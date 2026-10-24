"""Read-only metadata audit of write/delete handles matching the C: root.

No file contents, process memory or unrelated path names are read or reported.
Do not run during an owner restriction to repository-only work.
Only this process's duplicates are closed; source handles are never closed.
Extended handle layout reference: winsiderss/phnt 53fbbdc5b5d2b08761db1c7b26bfa8c820924356.
"""
import argparse
import ctypes as c
from ctypes import wintypes as w
import hashlib
import json
import os
from pathlib import Path
import time


class HandleEntry(c.Structure):
    _fields_ = [("object", c.c_void_p), ("pid", c.c_size_t), ("handle", c.c_size_t),
                ("access", w.DWORD), ("creator", w.USHORT), ("kind", w.USHORT),
                ("attributes", w.DWORD), ("reserved", w.DWORD)]


class FileInfo(c.Structure):
    _fields_ = [("attributes", w.DWORD), ("created", w.FILETIME), ("accessed", w.FILETIME),
                ("written", w.FILETIME), ("volume", w.DWORD), ("size_high", w.DWORD),
                ("size_low", w.DWORD), ("links", w.DWORD), ("index_high", w.DWORD),
                ("index_low", w.DWORD)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if args.report.exists():
        raise ValueError("Refuse an existing audit receipt")
    if c.sizeof(c.c_void_p) != 8 or c.sizeof(HandleEntry) != 40 or c.sizeof(FileInfo) != 52:
        raise ValueError("Unsupported metadata layout")
    k = c.WinDLL("kernel32", use_last_error=True)
    nt = c.WinDLL("ntdll")
    k.CreateFileW.argtypes = [w.LPCWSTR,w.DWORD,w.DWORD,c.c_void_p,w.DWORD,w.DWORD,c.c_void_p]
    k.CreateFileW.restype = w.HANDLE
    k.CloseHandle.argtypes = [w.HANDLE]
    k.GetCurrentProcess.restype = w.HANDLE
    k.OpenProcess.argtypes = [w.DWORD,w.BOOL,w.DWORD]
    k.OpenProcess.restype = w.HANDLE
    k.GetFileType.argtypes = [w.HANDLE]
    k.GetFileType.restype = w.DWORD
    k.GetFileInformationByHandle.argtypes = [w.HANDLE,c.POINTER(FileInfo)]
    k.GetFileInformationByHandle.restype = w.BOOL
    k.DuplicateHandle.argtypes = [w.HANDLE,w.HANDLE,w.HANDLE,c.POINTER(w.HANDLE),w.DWORD,w.BOOL,w.DWORD]
    k.DuplicateHandle.restype = w.BOOL
    k.QueryFullProcessImageNameW.argtypes = [w.HANDLE,w.DWORD,w.LPWSTR,c.POINTER(w.DWORD)]
    k.QueryFullProcessImageNameW.restype = w.BOOL
    nt.NtQuerySystemInformation.argtypes = [w.ULONG,c.c_void_p,w.ULONG,c.POINTER(w.ULONG)]
    nt.NtQuerySystemInformation.restype = c.c_long
    root = k.CreateFileW("C:/", 0x81, 7, None, 3, 0x02200000, None)
    if root == w.HANDLE(-1).value:
        raise OSError("Cannot inspect root metadata: " + str(c.get_last_error()))
    processes = {}
    report = {"scope":"write/delete metadata handles matching the existing C: root",
              "target_file_contents_read":False,"process_memory_access":False,
              "source_handles_closed":False,"game_access":False,"matches":[],
              "tool_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    try:
        target = FileInfo()
        if not k.GetFileInformationByHandle(root,c.byref(target)):
            raise OSError("Cannot identify root metadata")
        capacity = 4*1024*1024
        for _ in range(8):
            buffer = c.create_string_buffer(capacity)
            required = w.ULONG()
            status = nt.NtQuerySystemInformation(64,buffer,capacity,c.byref(required)) & 0xffffffff
            if status == 0:
                break
            if status != 0xC0000004:
                raise OSError("System handle query failed: " + hex(status))
            capacity = max(capacity*2,required.value+65536)
            if capacity > 128*1024*1024:
                raise ValueError("System handle metadata exceeds bound")
        else:
            raise OSError("System handle metadata did not stabilize")
        count = c.c_size_t.from_buffer(buffer).value
        if count > (capacity-16)//c.sizeof(HandleEntry):
            raise ValueError("System handle count exceeds buffer")
        entries = (HandleEntry*count).from_buffer(buffer,16)
        self_entry = next((e for e in entries if e.pid == os.getpid() and e.handle == root),None)
        if self_entry is None:
            raise ValueError("Cannot independently confirm File object type")
        candidates = [e for e in entries if e.kind == self_entry.kind and e.access & 0x10006 and e.pid]
        report.update(handle_records=count,write_delete_candidates=len(candidates),inspected=0,
                      duplicate_failures=0,metadata_failures=0,denied_processes=0)
        deadline = time.monotonic()+20
        for item in candidates:
            if time.monotonic() > deadline:
                report["bounded_stop"] = True
                break
            if item.pid not in processes:
                processes[item.pid] = k.OpenProcess(0x1040,False,item.pid)
                if not processes[item.pid]:
                    report["denied_processes"] += 1
            process = processes[item.pid]
            if not process:
                continue
            duplicate = w.HANDLE()
            # DUPLICATE_SAME_ACCESS only. Never use DUPLICATE_CLOSE_SOURCE.
            if not k.DuplicateHandle(process,item.handle,k.GetCurrentProcess(),c.byref(duplicate),0,False,2):
                report["duplicate_failures"] += 1
                continue
            try:
                if k.GetFileType(duplicate) != 1:
                    continue
                report["inspected"] += 1
                info = FileInfo()
                if not k.GetFileInformationByHandle(duplicate,c.byref(info)):
                    report["metadata_failures"] += 1
                    continue
                if ((info.volume,info.index_high,info.index_low) !=
                    (target.volume,target.index_high,target.index_low)):
                    continue
                name = c.create_unicode_buffer(32768)
                size = w.DWORD(len(name))
                image = Path(name.value).name if k.QueryFullProcessImageNameW(process,0,name,c.byref(size)) else "unavailable"
                report["matches"].append({"pid":item.pid,"image_basename":image,
                    "access_mask":hex(item.access),"write_data":bool(item.access&2),
                    "append_data":bool(item.access&4),"delete":bool(item.access&0x10000)})
            finally:
                k.CloseHandle(duplicate)
    finally:
        for process in processes.values():
            if process:
                k.CloseHandle(process)
        k.CloseHandle(root)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_bytes((json.dumps(report,indent=2)+"\n").encode())
    print(json.dumps(report,sort_keys=True))


if __name__ == "__main__":
    main()
