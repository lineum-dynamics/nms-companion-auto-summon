"""CI-only differential tracing of frozen modules in an owned foreign host.

No game process, player deployment, antivirus reconfiguration or binary upload.
Frida changes the controlled process environment and timings; results are
bounded API observations, not malware classification or NMS acceptance.
"""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import time


PINS = {
    '6474247c07e7659efc6e4fc698a1e7cdf9471c3ec471656675a251ff5fe96652',
    '765cdbdf0e99aea433fd977048b38f0cd28ccbe6c26902c511310a3ee9523ffa',
}
REPO = 'lineum-dynamics/nms-companion-auto-summon'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--host', type=Path, required=True)
    parser.add_argument('--expected-host-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if (os.name != 'nt' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != REPO
            or os.environ.get('RUNNER_OS') != 'Windows'):
        raise RuntimeError('Refuse execution outside the authorized Windows CI context')
    module = args.module.resolve(strict=True)
    host = args.host.resolve(strict=True)
    if (args.expected_sha256 not in PINS or digest(module) != args.expected_sha256
            or host.name.lower() != 'cas-behavior-host.exe'
            or digest(host) != args.expected_host_sha256):
        raise RuntimeError('Refuse unrecognized module/host bytes')
    import frida
    import ctypes
    from ctypes import wintypes
    if frida.__version__ != '17.24.3':
        raise RuntimeError('Unexpected instrumentation version')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetExitCodeProcess.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    agent_path = Path(__file__).with_name('native_behavior_agent.js')
    agent = agent_path.read_text(encoding='utf-8')
    allowed_environment = {'SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP', 'SYSTEMDRIVE',
                           'COMSPEC', 'GITHUB_ACTIONS', 'GITHUB_REPOSITORY', 'RUNNER_OS'}
    child_environment = {name: value for name, value in os.environ.items()
                         if name.upper() in allowed_environment}
    result = {'schema': 1, 'kind': 'owned-ci-differential-native-api-trace',
              'source_revision': os.environ.get('GITHUB_SHA'),
              'module_sha256': args.expected_sha256, 'host_sha256': args.expected_host_sha256,
              'agent_sha256': digest(agent_path), 'frida': frida.__version__,
              'game_access': False, 'security_settings_changed': False, 'binary_uploaded': False,
              'cases': [], 'status': 'TOOL_ERROR',
              'limits': ['Owned unsupported host only; no active game hooks are exercised.',
                         'Instrumentation affects process state and timing; plain controls are separate.',
                         'Accurate backtrace failures/unknown frames remain unknown.',
                         'Watched APIs are not complete syscall or packet coverage.',
                         'No antivirus detection cause or safety classification follows from a zero.']}
    try:
        device = frida.get_local_device()
        for mode in ('baseline', 'load', 'inspect', 'initialize'):
            if digest(module) != args.expected_sha256 or digest(host) != args.expected_host_sha256:
                raise RuntimeError('Input identity changed')
            argv = [str(host), mode, str(module)]
            plain = subprocess.run(argv, text=True, capture_output=True, timeout=30,
                                   env=child_environment)
            plain_records = [json.loads(line) for line in plain.stdout.splitlines() if line.startswith('{')]
            case = {'mode': mode, 'plain_exit': plain.returncode, 'plain_phases': plain_records,
                    'events': [], 'agent_errors': [], 'output_records': [], 'status': 'TOOL_ERROR'}
            result['cases'].append(case)
            if plain.returncode != 0 or not any(x.get('phase') == 'complete' for x in plain_records):
                raise RuntimeError('Uninstrumented owned-host control failed; no benign result inferred')
            detached = threading.Event()
            output = bytearray()
            pid = None
            session = None
            process_handle = None

            def on_output(process, descriptor, data):
                if process == pid and descriptor == 1 and data:
                    output.extend(data)

            def on_detached(reason, crash=None):
                case['detach'] = {'reason': str(reason), 'crash_reported': crash is not None}
                detached.set()

            def on_message(message, data):
                if message.get('type') == 'send':
                    case['events'].append(message['payload'])
                elif message.get('type') == 'error':
                    case['agent_errors'].append({'kind': 'agent_error'})

            device.on('output', on_output)
            try:
                pid = device.spawn(argv, stdio='pipe', envp=child_environment)
                # Hold an independent read/synchronize handle to this owned child.
                process_handle = kernel.OpenProcess(0x1000 | 0x100000, False, pid)
                if not process_handle:
                    raise RuntimeError('Owned process exit-observation handle unavailable')
                session = device.attach(pid)
                session.on('detached', on_detached)
                script = session.create_script(agent)
                script.on('message', on_message)
                script.load()
                ready = script.exports_sync.readiness()
                case['readiness'] = ready
                watched = {x['api'] for x in ready['hooks']}
                required = {'Sleep', 'CreateThread', 'CreateProcessW', 'ReadProcessMemory',
                            'WriteProcessMemory', 'SuspendThread', 'SetThreadContext',
                            'NtDelayExecution', 'NtCreateUserProcess'}
                if ready['failures'] or not required <= watched:
                    raise RuntimeError('Required instrumentation points are unavailable')
                device.resume(pid)
                if not detached.wait(30):
                    device.kill(pid)
                    raise RuntimeError('Owned instrumented host timed out; possible instrumentation interference')
                if kernel.WaitForSingleObject(process_handle, 5000) != 0:
                    raise RuntimeError('Owned process termination was not signaled')
                exit_code = wintypes.DWORD()
                if not kernel.GetExitCodeProcess(process_handle, ctypes.byref(exit_code)):
                    raise RuntimeError('Owned process exit code unavailable')
                case['observed_exit_code'] = exit_code.value
                time.sleep(0.25)
            finally:
                device.off('output', on_output)
                if pid is not None and not detached.is_set():
                    try: device.kill(pid)
                    except frida.ProcessNotFoundError: pass
                if session is not None and not detached.is_set():
                    try: session.detach()
                    except frida.InvalidOperationError: pass
                if process_handle:
                    kernel.CloseHandle(process_handle)
            case['output_records'] = [json.loads(line) for line in output.decode('utf-8').splitlines()
                                      if line.startswith('{')]
            api_events = [x for x in case['events'] if x.get('kind') == 'api']
            controls = {x['api'] for x in api_events if x.get('direct_host_caller')}
            case['positive_control_apis'] = sorted(controls)
            if not {'Sleep', 'CreateThread', 'WriteProcessMemory'} <= controls:
                raise RuntimeError('Known host API controls were not observed')
            if (case['agent_errors'] or any(x.get('kind') == 'overflow' for x in case['events'])
                    or case['output_records'] != plain_records
                    or case.get('detach') != {'reason': 'process-terminated', 'crash_reported': False}
                    or case.get('observed_exit_code') != 0):
                raise RuntimeError('Incomplete instrumented capture')
            case['direct_target_counts'] = dict(collections.Counter(
                x['api'] for x in api_events if x.get('direct_target_caller')))
            case['target_in_stack_counts'] = dict(collections.Counter(
                x['api'] for x in api_events if x.get('target_in_frames')))
            module_events = [x for x in case['events'] if x.get('kind') == 'target-module']
            if mode == 'baseline' and module_events:
                raise RuntimeError('Baseline unexpectedly loaded the target')
            if mode != 'baseline' and not any(x.get('bytes') == 2031616 for x in module_events):
                raise RuntimeError('Target module was not observed with its exact image size')
            if mode == 'initialize' and not (case['direct_target_counts'].get('CreateThread', 0)
                                             or case['target_in_stack_counts'].get('CreateThread', 0)):
                raise RuntimeError('Known target initialization call was not attributed')
            case['status'] = 'CAPTURE_COMPLETED'
        result['status'] = 'CAPTURES_COMPLETED'
    except Exception as error:
        controlled_prefixes = ('Input identity', 'Uninstrumented owned-host', 'Required instrumentation',
                               'Owned instrumented', 'Owned process', 'Known host', 'Incomplete instrumented',
                               'Baseline unexpectedly', 'Target module', 'Known target')
        reason = str(error) if type(error) is RuntimeError and str(error).startswith(controlled_prefixes) else 'External tool failure'
        result['tool_error'] = {'type': type(error).__name__, 'reason': reason}
    finally:
        result['post_module_sha256'] = digest(module)
        result['post_host_sha256'] = digest(host)
        if result['post_module_sha256'] != args.expected_sha256 or result['post_host_sha256'] != args.expected_host_sha256:
            result['status'] = 'TOOL_ERROR'
            result['tool_error'] = {'type': 'IdentityChanged'}
        args.output.write_bytes((json.dumps(result, indent=2, ensure_ascii=True) + '\n').encode())
    print(json.dumps({'status': result['status'], 'cases': [
        {'mode': x['mode'], 'status': x['status'], 'direct_target_counts': x.get('direct_target_counts')}
        for x in result['cases']], 'tool_error': result.get('tool_error')}, indent=2))
    return 0 if result['status'] == 'CAPTURES_COMPLETED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
