# Local MinHook patch in Companion Auto Summon 0.10.4

Upstream: MinHook 1.3.4, commit
`c3fcafdc10146beb5919319d0683e44e3c30d537`.
Only `src/buffer.c`, `IsExecutableAddress`, differs. The helper now requires
VirtualQuery to return the full MEMORY_BASIC_INFORMATION size before reading
State or Protect. Failed/incomplete queries return FALSE. Successful page
classification is unchanged. This handles a reproduced injected-fault defect;
no corresponding NMS failure or antivirus rule has been established.

- Original: 9,814 bytes, SHA-256
  `0ab484d7870c3a8e7a3a1ee61e2070072cf445ed85b619d4c4207fed34356d99`.
- Patched: 9,854 bytes, SHA-256
  `3a9b2f7a1fb084e72897acd8095d4325ab03545669b5b43d89d13ea71d113035`.

`tools/validate_native_dependencies.py` verifies all retained dependency and
notice bytes. It also reverses this exact two-line guard and requires the
original upstream digest, preventing unrelated edits from being described as
this patch. The original BSD/HDE notices remain unchanged and are packaged.
The packaged notice README explicitly describes the local change.

`native/tests/minhook_query_host.c` compiles the actual patched C source into
an owned host with a query substitute. It covers failed/incomplete results and
successful page classifications. `hook_host.exe` separately tests real hooks
and callback forwarding inside its own executable. Neither host accesses NMS.
The earlier unmodified baseline remains in the dated scan investigation.
