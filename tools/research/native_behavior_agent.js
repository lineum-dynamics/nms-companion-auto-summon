'use strict';
// Instrument only the owned CI child. No replacement of application functions.
const targetName = 'companionautosummon.asi';
const hostName = 'cas-behavior-host.exe';
const attached = new Set();
let eventCount = 0;
let overflow = false;
const hooks = [];
const failures = [];
function owner(address) {
  const m = Process.findModuleByAddress(address);
  return m === null ? { module: 'unknown', rva: null } :
    { module: m.name.toLowerCase(), rva: address.sub(m.base).toString() };
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
        let frames = [], backtraceError = false;
        try { frames = Thread.backtrace(this.context, Backtracer.ACCURATE).slice(0, 12).map(owner); }
        catch (_) { backtraceError = true; }
        const extra = {};
        try {
          if (details === 'sleep') extra.milliseconds = args[0].toUInt32();
          if (details === 'thread') extra.creation_flags = args[4].toUInt32();
          if (details === 'process') extra.creation_flags = args[5].toUInt32();
          if (details === 'memory') extra.current_process_pseudo_handle = args[0].toInt32() === -1;
          if (details === 'delay') extra.interval_100ns = args[1].readS64().toString();
          if (details === 'exit') extra.exit_status = args[0].toUInt32();
        } catch (_) { extra.argument_read_failed = true; }
        this.entry = { kind: 'api', api, provider: module.name.toLowerCase(), caller,
          frames, backtrace_error: backtraceError, details: extra,
          target_in_frames: frames.some(f => f.module === targetName),
          direct_target_caller: caller.module === targetName,
          direct_host_caller: caller.module === hostName,
          thread: Process.getCurrentThreadId() };
        eventCount++;
        if (details === 'exit') { send(this.entry); this.entry = null; }
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
  'ntdll.dll': [ ['NtDelayExecution', 'delay'], ['NtCreateUserProcess', ''], ['NtCreateThreadEx', ''],
    ['RtlExitUserProcess', 'exit'] ],
  'ws2_32.dll': [ ['connect', ''], ['WSAConnect', ''], ['sendto', ''], ['WSASendTo', ''] ],
  'dnsapi.dll': [ ['DnsQuery_W', ''], ['DnsQueryEx', ''] ],
  'winhttp.dll': [ ['WinHttpConnect', ''], ['WinHttpSendRequest', ''] ],
  'wininet.dll': [ ['InternetConnectW', ''], ['HttpSendRequestW', ''] ]
};
spec['kernel32.dll'] = spec['kernelbase.dll'];
const observer = Process.attachModuleObserver({
  onAdded(module) {
    const name = module.name.toLowerCase();
    if (name === targetName) send({ kind: 'target-module', bytes: module.size });
    const definitions = spec[name];
    if (definitions !== undefined) for (const [api, details] of definitions) observe(module, api, details);
  }
});
rpc.exports = {
  readiness() { return { hooks, failures, event_count: eventCount, overflow }; }
};
