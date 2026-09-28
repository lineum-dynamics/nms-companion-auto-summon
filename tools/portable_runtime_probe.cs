// Test-owned child only. Loads the pinned DLL locally; never opens another
// process, injects, hooks, loads a mod, or selects a game.
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

internal static class PortableRuntimeProbe
{
    [DllImport("kernel32", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr LoadLibraryExW(string path, IntPtr file, uint flags);
    [DllImport("kernel32", CharSet = CharSet.Ansi, SetLastError = true)]
    private static extern IntPtr GetProcAddress(IntPtr module, string name);
    [DllImport("kernel32", SetLastError = true)]
    private static extern bool SetDefaultDllDirectories(uint flags);
    [DllImport("kernel32", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr AddDllDirectory(string path);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate int RunDataFunction(IntPtr data);
    [StructLayout(LayoutKind.Sequential)]
    private struct StringData { public IntPtr value; public byte isFile; }
    [StructLayout(LayoutKind.Sequential)]
    private struct ErrorData { public IntPtr text; public UIntPtr length; public UInt32 index; }
    [StructLayout(LayoutKind.Sequential)]
    private struct RunData { public UInt32 count; public IntPtr strings; public IntPtr error; }

    private static int Main(string[] args)
    {
        if (args.Length != 3 || (args[1] != "source" && args[1] != "file")) return 64;
        string runtime = Path.GetFullPath(args[0]);
        string input = Path.GetFullPath(args[2]);
        if (!SetDefaultDllDirectories(0x1000) || AddDllDirectory(runtime) == IntPtr.Zero) return 65;
        IntPtr python = LoadLibraryExW(Path.Combine(runtime, "python311.dll"), IntPtr.Zero, 0x1100);
        if (python == IntPtr.Zero) return 66;
        IntPtr library = LoadLibraryExW(Path.Combine(runtime, @"Lib\site-packages\pyrun_injected\dll.cp311-win_amd64.pyd"), IntPtr.Zero, 0x1100);
        if (library == IntPtr.Zero) return 67;
        IntPtr address = GetProcAddress(library, "run_data");
        if (address == IntPtr.Zero) return 68;
        string code = args[1] == "file" ? input : File.ReadAllText(input, Encoding.UTF8);
        byte[] bytes = Encoding.UTF8.GetBytes(code + "\0");
        IntPtr text = Marshal.AllocHGlobal(bytes.Length);
        IntPtr strings = Marshal.AllocHGlobal(Marshal.SizeOf(typeof(StringData)));
        IntPtr error = Marshal.AllocHGlobal(Marshal.SizeOf(typeof(ErrorData)));
        IntPtr data = Marshal.AllocHGlobal(Marshal.SizeOf(typeof(RunData)));
        try
        {
            Marshal.Copy(bytes, 0, text, bytes.Length);
            Marshal.StructureToPtr(new StringData { value = text, isFile = (byte)(args[1] == "file" ? 1 : 0) }, strings, false);
            Marshal.StructureToPtr(new ErrorData(), error, false);
            Marshal.StructureToPtr(new RunData { count = 1, strings = strings, error = error }, data, false);
            var run = (RunDataFunction)Marshal.GetDelegateForFunctionPointer(address, typeof(RunDataFunction));
            int result = run(data);
            Console.WriteLine("{\"native_return\":" + result + "}");
            return result;
        }
        finally
        {
            Marshal.FreeHGlobal(data);
            Marshal.FreeHGlobal(error);
            Marshal.FreeHGlobal(strings);
            Marshal.FreeHGlobal(text);
        }
    }
}
