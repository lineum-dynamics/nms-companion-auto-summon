// Portable UI and integrity gate. This executable contains the trusted manifest digest.
// It does not inject, stage mods, write saves, install packages, or require elevation.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using System.Web.Script.Serialization;
using System.Windows.Forms;

namespace CompanionAutoSummon.Portable
{
    internal static class Package
    {
        internal const string ManifestDigest = "@@MANIFEST_SHA256@@";
        private const int MaximumFiles = 30000;
        internal static string Hash(string path)
        {
            using (var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
            using (var hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
        }
        private static void Ordinary(string path)
        {
            if ((File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0)
                throw new InvalidDataException("Reparse point in package");
        }
        internal static string Resolve(string root, string relative)
        {
            if (String.IsNullOrWhiteSpace(relative) || relative.Length > 1024 ||
                relative.Contains("\\") || relative.Contains(":") || relative.StartsWith("/") ||
                Path.IsPathRooted(relative))
                throw new InvalidDataException("Invalid manifest path");
            string[] parts = relative.Split('/');
            string path = root;
            foreach (string part in parts)
            {
                if (part.Length == 0 || part == "." || part == ".." || part.EndsWith(".") ||
                    part.EndsWith(" ") || part.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 ||
                    Regex.IsMatch(part, @"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", RegexOptions.IgnoreCase))
                    throw new InvalidDataException("Unsafe manifest path segment");
                path = Path.Combine(path, part);
                Ordinary(path);
            }
            path = Path.GetFullPath(path);
            if (!path.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("Manifest path escaped package");
            return path;
        }
        internal static void Verify(string root, string entrypoint)
        {
            root = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar);
            Ordinary(root);
            string manifest = Path.Combine(root, "portable-manifest.json");
            Ordinary(manifest);
            if (new FileInfo(manifest).Length > 8 * 1024 * 1024)
                throw new InvalidDataException("Portable manifest digest mismatch");
            byte[] manifestBytes = File.ReadAllBytes(manifest);
            using (var sha = SHA256.Create())
                if (BitConverter.ToString(sha.ComputeHash(manifestBytes)).Replace("-", "").ToLowerInvariant() != ManifestDigest)
                    throw new InvalidDataException("Portable manifest digest mismatch");
            var parser = new JavaScriptSerializer { MaxJsonLength = 8 * 1024 * 1024 };
            var data = parser.Deserialize<Dictionary<string, object>>(new UTF8Encoding(false, true).GetString(manifestBytes));
            if (data == null || !data.ContainsKey("schema_version") || !(data["schema_version"] is int) ||
                (int)data["schema_version"] != 1 || !data.ContainsKey("version") ||
                !(data["version"] is string) || String.IsNullOrWhiteSpace((string)data["version"]) ||
                !data.ContainsKey("files") || !(data["files"] is ArrayList))
                throw new InvalidDataException("Unsupported manifest schema");
            var entries = (ArrayList)data["files"];
            if (entries.Count == 0 || entries.Count > MaximumFiles)
                throw new InvalidDataException("Manifest file count outside bounds");
            var paths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (object item in entries)
            {
                var record = item as Dictionary<string, object>;
                if (record == null || !record.ContainsKey("path") || !(record["path"] is string) ||
                    !record.ContainsKey("sha256") || !(record["sha256"] is string))
                    throw new InvalidDataException("Invalid manifest file record");
                string relative = (string)record["path"];
                string digest = (string)record["sha256"];
                if (!Regex.IsMatch(digest, "^[a-f0-9]{64}$") || !paths.Add(relative))
                    throw new InvalidDataException("Duplicate file or invalid digest");
                string path = Resolve(root, relative);
                if (!File.Exists(path) || Hash(path) != digest)
                    throw new InvalidDataException("Payload digest mismatch");
            }
            foreach (string required in new string[] { "runtime/pythonw.exe", "runtime/python.exe", "app/portable_launcher.py", "mod/locales/en.json" })
                if (!paths.Contains(required)) throw new InvalidDataException("Required payload missing");
            // Reject unlisted executable dependencies and reparse points, even in unused directories.
            var pending = new Stack<string>();
            pending.Push(root);
            int count = 0;
            while (pending.Count > 0)
            {
                foreach (string child in Directory.EnumerateFileSystemEntries(pending.Pop()))
                {
                    if (++count > MaximumFiles * 2) throw new InvalidDataException("Package tree too large");
                    Ordinary(child);
                    if (Directory.Exists(child)) { pending.Push(child); continue; }
                    if (String.Equals(child, manifest, StringComparison.OrdinalIgnoreCase) ||
                        String.Equals(child, entrypoint, StringComparison.OrdinalIgnoreCase)) continue;
                    string relative = child.Substring(root.Length + 1).Replace('\\', '/');
                    if (!paths.Contains(relative)) throw new InvalidDataException("Unlisted package file");
                }
            }
        }
        internal static string Quote(string value)
        {
            // Windows CommandLineToArgvW quoting, including terminal backslashes.
            var result = new StringBuilder("\"");
            int slashes = 0;
            foreach (char character in value)
            {
                if (character == '\\') { slashes++; continue; }
                if (character == '"') result.Append('\\', slashes * 2 + 1).Append('"');
                else result.Append('\\', slashes).Append(character);
                slashes = 0;
            }
            return result.Append('\\', slashes * 2).Append('"').ToString();
        }
    }

    internal static class Texts
    {
        private static Dictionary<string, Dictionary<string, string>> catalogs;
        private static string locale;
        internal static void Load()
        {
            using (var reader = new StreamReader(Assembly.GetExecutingAssembly().GetManifestResourceStream("PortableLocales"), Encoding.UTF8))
                catalogs = new JavaScriptSerializer().Deserialize<Dictionary<string, Dictionary<string, string>>>(reader.ReadToEnd());
            string culture = CultureInfo.CurrentUICulture.Name;
            locale = culture;
            if (culture.StartsWith("zh", StringComparison.OrdinalIgnoreCase))
                locale = culture.Contains("TW") || culture.Contains("HK") || culture.Contains("Hant") ? "zh-Hant" : "zh-Hans";
            else if (culture.StartsWith("es", StringComparison.OrdinalIgnoreCase)) locale = "es-ES";
            else if (culture.StartsWith("pt", StringComparison.OrdinalIgnoreCase)) locale = culture == "pt-BR" ? "pt-BR" : "pt-PT";
            else if (!catalogs.ContainsKey(locale)) locale = CultureInfo.CurrentUICulture.TwoLetterISOLanguageName;
            if (!catalogs.ContainsKey(locale)) locale = "en";
        }
        internal static string Get(string key) { return catalogs[locale][key]; }
    }

    internal sealed class LauncherWindow : Form
    {
        private readonly string root;
        private readonly Label status;
        private readonly Button start;
        private readonly Button check;
        private readonly Button choose;
        private string gameDirectory;
        private bool busy;
        internal LauncherWindow(string directory)
        {
            root = directory;
            Text = Texts.Get("product.full_name");
            StartPosition = FormStartPosition.CenterScreen;
            ClientSize = new Size(640, 290);
            MinimumSize = new Size(560, 330);
            Font = SystemFonts.MessageBoxFont;
            AutoScaleMode = AutoScaleMode.Dpi;
            var layout = new TableLayoutPanel { Dock = DockStyle.Fill, Padding = new Padding(18), ColumnCount = 1, RowCount = 5 };
            layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 38));
            layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 28));
            layout.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
            layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 48));
            layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 40));
            layout.Controls.Add(new Label { Text = Texts.Get("product.full_name"), AutoSize = true, Font = new Font(Font, FontStyle.Bold) });
            layout.Controls.Add(new Label { Text = Texts.Get("product.author_credit"), AutoSize = true });
            status = new Label { Text = Texts.Get("portable.ready"), Dock = DockStyle.Fill, AutoEllipsis = true };
            layout.Controls.Add(status);
            var actions = new FlowLayoutPanel { Dock = DockStyle.Fill, WrapContents = false };
            start = new Button { Text = Texts.Get("portable.start"), AutoSize = true, MinimumSize = new Size(130, 34) };
            check = new Button { Text = Texts.Get("portable.check"), AutoSize = true, MinimumSize = new Size(130, 34) };
            actions.Controls.Add(start); actions.Controls.Add(check);
            layout.Controls.Add(actions);
            var secondary = new FlowLayoutPanel { Dock = DockStyle.Fill, WrapContents = false };
            choose = new Button { Text = Texts.Get("portable.choose_game"), AutoSize = true, MinimumSize = new Size(130, 28) };
            var close = new Button { Text = Texts.Get("portable.close"), AutoSize = true, MinimumSize = new Size(90, 28) };
            secondary.Controls.Add(choose); secondary.Controls.Add(close);
            layout.Controls.Add(secondary);
            Controls.Add(layout);
            start.Click += async delegate { await Dispatch(false); };
            check.Click += async delegate { await Dispatch(true); };
            close.Click += delegate { Close(); };
            choose.Click += delegate {
                using (var picker = new FolderBrowserDialog { Description = Texts.Get("portable.game_choice_required"), ShowNewFolderButton = false })
                    if (picker.ShowDialog(this) == DialogResult.OK) { gameDirectory = picker.SelectedPath; status.Text = gameDirectory; }
            };
        }
        private void SetBusy(bool value)
        {
            busy = value; start.Enabled = !value; check.Enabled = !value; choose.Enabled = !value;
        }
        private async Task Dispatch(bool checkOnly)
        {
            if (busy) return;
            SetBusy(true);
            status.Text = Texts.Get(checkOnly ? "portable.checking" : "portable.starting");
            try
            {
                await Task.Run(delegate { Package.Verify(root, Assembly.GetExecutingAssembly().Location); });
                if (IsDisposed) return;
                string arguments = "-I -B " + Package.Quote(Path.Combine(root, "app", "portable_launcher.py"));
                if (gameDirectory != null) arguments += " --game-directory " + Package.Quote(gameDirectory);
                var settings = new ProcessStartInfo {
                    FileName = Path.Combine(root, "runtime", checkOnly ? "python.exe" : "pythonw.exe"),
                    Arguments = arguments + (checkOnly ? " --check-only --no-dialog" : ""),
                    WorkingDirectory = root, UseShellExecute = false, CreateNoWindow = true,
                    WindowStyle = ProcessWindowStyle.Hidden,
                    RedirectStandardOutput = checkOnly, RedirectStandardError = checkOnly
                };
                if (checkOnly)
                {
                    settings.StandardOutputEncoding = new UTF8Encoding(false);
                    settings.StandardErrorEncoding = new UTF8Encoding(false);
                }
                if (!checkOnly)
                {
                    using (Process process = Process.Start(settings))
                        if (process == null) throw new InvalidOperationException("No child process created");
                    status.Text = Texts.Get("portable.started");
                    return;
                }
                var outcome = await Task.Run(delegate { return RunCheck(settings); });
                if (IsDisposed) return;
                status.Text = Texts.Get(outcome.Item1 == 0 ? "portable.check_passed" : outcome.Item1 == -1 ? "portable.check_timeout" : "portable.check_failed").Replace("{details}", outcome.Item2);
                if (outcome.Item1 != 0) MessageBox.Show(this, status.Text, Texts.Get("launcher.blocked_title"), MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
            catch (Exception)
            {
                if (!IsDisposed) { status.Text = Texts.Get("portable.runtime_invalid"); MessageBox.Show(this, status.Text, Texts.Get("launcher.blocked_title"), MessageBoxButtons.OK, MessageBoxIcon.Error); }
            }
            finally { if (!IsDisposed) SetBusy(false); }
        }
        private static Tuple<int, string> RunCheck(ProcessStartInfo settings)
        {
            using (var process = new Process { StartInfo = settings })
            {
                var output = new StringBuilder();
                object gate = new object();
                process.Start();
                Task stdout = Drain(process.StandardOutput, output, gate);
                Task stderr = Drain(process.StandardError, output, gate);
                if (!process.WaitForExit(120000))
                {
                    // Only this read-only check process is bounded; never a game or mod host.
                    process.Kill();
                    return Tuple.Create(-1, "");
                }
                // A check must not wait forever for a mistakenly inherited pipe.
                Task.WaitAll(new Task[] { stdout, stderr }, 2000);
                lock (gate) return Tuple.Create(process.ExitCode, output.ToString().Trim());
            }
        }
        private static Task Drain(StreamReader reader, StringBuilder output, object gate)
        {
            return Task.Run(delegate {
                try
                {
                    char[] buffer = new char[1024];
                    int read;
                    while ((read = reader.Read(buffer, 0, buffer.Length)) > 0)
                        lock (gate)
                        {
                            int left = 8192 - output.Length;
                            if (left > 0) output.Append(buffer, 0, Math.Min(left, read));
                        }
                }
                catch (IOException) { }
                catch (ObjectDisposedException) { }
            });
        }
    }

    internal static class Program
    {
        [STAThread]
        private static int Main(string[] args)
        {
            string entrypoint = Assembly.GetExecutingAssembly().Location;
            string root = Path.GetDirectoryName(entrypoint);
            // Offline integrity verification only; never runs Python or constructs a window.
            if (args.Length == 1 && args[0] == "--verify-only")
            {
                try { Package.Verify(root, entrypoint); return 0; }
                catch (Exception) { return 2; }
            }
            if (args.Length != 0) return 2;
            Texts.Load();
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new LauncherWindow(root));
            return 0;
        }
    }
}
