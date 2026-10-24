# Parked backup volume-root prototype

Date: 24 October 2026. Branch: `fix/native-backup-volume-root`.
Status: source-only research, parked at the owner's request to prioritize
antivirus/Nexus publication. It is not included in the frozen 0.10.4 package.
The owner forbids desktop/app control; repository and owned offline work only.

The prototype anchors filesystem operations to the physical volume GUID and
permits root write sharing on NTFS only with a strictly held first child.
Other ancestor/source/destination write/delete refusal, private ACLs, inventory
and hashing checks remain in its code. Empty/absent first-child cases stay strict.
This needs dedicated race/error/binding tests and independent review before
integration. Passing the existing suite does not establish those new contracts.

Existing owned backup validation: 16 checks, passed=True.
No game or actual save data was accessed. No player archive was rebuilt.
Prototype source SHA-256: `e3931f9aec6908ed093f4a391d0dfa2ef1f09b19802c0aab9331fc58a8da6abf`.
Validation receipt SHA-256: `d025d60068547c0e724b7d96285f0956792bc0cdd8bcc9ae1f01927b008d2896`.
Compiler: pinned LLVM-MinGW 20260922, clang23.1.2; CPython3.11.9.
Reproduction: compile backup.cpp and native/tests/backup_driver.cpp with
`-std=c++17 -O2 -Wall -Wextra -Werror -static -I native/include -I native/third_party
-lbcrypt -ladvapi32`, then run tools/validate_native_backup.py with that owned
driver and a fresh receipt path. No deployment/launch step is part of this test.

Microsoft reference contracts:
- https://learn.microsoft.com/en-us/windows/win32/fileio/reparse-points
- https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-volume
- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumenameforvolumemountpointw
- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew

This branch does not address the antivirus labels or clear Nexus quarantine.
Return to the frozen query-guard source for the requested detection investigation.
