'use strict';
// Instrument only the owned CI child. No replacement of application functions.
const targetName = 'companionautosummon.asi';
const hostName = 'cas-behavior-host.exe';
const attached = new Set();
let eventCount = 0;
let overflow = false;
const hooks = [];
const failures = [];
const modules = new Map();
function owner(address) {
  for (const m of modules.values()) {
    if (address.compare(m.base) >= 0 && address.compare(m.end) < 0)
      return { module: m.name, rva: address.sub(m.base).toString() };
  }
  return { module: 'unknown', rva: null };
}
function observe(module, api, details) {
  const address = module.findExportByName(api);
  if (address === null) return;
  const key = module.name.toLowerCase() + '!' + api;
  // Forwarded exports can point to the same implementation. Keep one hook.
  if (attached.has(address.toString())) return;
  try {
    Interceptor.attach(address, {
      onEnter(args) {
        if (eventCount >= 4000) {
          if (!overflow) { overflow = true; send({ kind: 'overflow' }); }
          this.entry = null; return;
        }
        const caller = owner(this.returnAddress);
        // Avoid stack walking and live module enumeration inside loader/thread APIs.
        // Full-stack mode remains a separate prior experiment, not this capture.
        const frames = [];
        const extra = {};
        try {
          if (details === 'sleep') extra.milliseconds = args[0].toUInt32();
          if (details === 'thread') extra.creation_flags = args[4].toUInt32();
          if (details === 'process') extra.creation_flags = args[5].toUInt32();
          if (details === 'memory') extra.current_process_pseudo_handle = args[0].toInt32() === -1;
          if (details === 'delay') extra.interval_100ns = args[1].readS64().toString();
        } catch (_) { extra.argument_read_failed = true; }
        this.entry = { kind: 'api', api, provider: module.name.toLowerCase(), caller,
          frames, backtrace_requested: false, backtrace_error: false, details: extra,
          target_in_frames: frames.some(f => f.module === targetName),
          direct_target_caller: caller.module === targetName,
          direct_host_caller: caller.module === hostName,
          thread: Process.getCurrentThreadId(), call_id: eventCount + 1 };
        eventCount++;
        send({ ...this.entry, kind: 'api-enter' });
      },
      onLeave(value) {
        if (this.entry === null || this.entry === undefined) return;
        if (details === 'thread' || details === 'process') this.entry.succeeded = !value.isNull();
        if (details === 'memory') this.entry.succeeded = value.toInt32() !== 0;
        send(this.entry);
      }
    });
    attached.add(address.toString()); hooks.push({ provider: module.name.toLowerCase(), api });
  } catch (_) { failures.push({ provider: module.name.toLowerCase(), api }); }
}
const spec = {
  'kernelbase.dll': [ ['Sleep', 'sleep'], ['CreateThread', 'thread'], ['CreateProcessW', 'process'],
    ['CreateProcessA', 'process'], ['ReadProcessMemory', 'memory'], ['WriteProcessMemory', 'memory'],
    ['SuspendThread', ''], ['ResumeThread', ''], ['GetThreadContext', ''], ['SetThreadContext', ''] ],
  'ntdll.dll': [ ['NtDelayExecution', 'delay'], ['NtCreateUserProcess', ''], ['NtCreateThreadEx', ''] ],
  'ws2_32.dll': [ ['connect', ''], ['WSAConnect', ''], ['sendto', ''], ['WSASendTo', ''] ],
  'dnsapi.dll': [ ['DnsQuery_W', ''], ['DnsQueryEx', ''] ],
  'winhttp.dll': [ ['WinHttpConnect', ''], ['WinHttpSendRequest', ''] ],
  'wininet.dll': [ ['InternetConnectW', ''], ['HttpSendRequestW', ''] ]
};
spec['kernel32.dll'] = spec['kernelbase.dll'];
const observer = Process.attachModuleObserver({
  onAdded(module) {
    const name = module.name.toLowerCase();
    modules.set(module.base.toString(), { name, base: module.base, end: module.base.add(module.size) });
    if (name === targetName) send({ kind: 'target-module', bytes: module.size });
    const definitions = spec[name];
    if (definitions !== undefined) for (const [api, details] of definitions) observe(module, api, details);
  },
  onRemoved(module) { modules.delete(module.base.toString()); }
});
rpc.exports = {
  readiness() { return { hooks, failures, event_count: eventCount, overflow }; }
};
