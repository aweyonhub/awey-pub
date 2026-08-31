#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#define WIN32_LEAN_AND_MEAN

#include <windows.h>

#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr wchar_t kVersion[] = L"0.1.0";

class UniqueHandle {
 public:
  UniqueHandle() = default;
  explicit UniqueHandle(HANDLE handle) : handle_(handle) {}

  UniqueHandle(const UniqueHandle&) = delete;
  UniqueHandle& operator=(const UniqueHandle&) = delete;

  UniqueHandle(UniqueHandle&& other) noexcept
      : handle_(std::exchange(other.handle_, nullptr)) {}

  UniqueHandle& operator=(UniqueHandle&& other) noexcept {
    if (this != &other) {
      Reset(std::exchange(other.handle_, nullptr));
    }
    return *this;
  }

  ~UniqueHandle() { Reset(); }

  HANDLE Get() const { return handle_; }

  explicit operator bool() const {
    return handle_ != nullptr && handle_ != INVALID_HANDLE_VALUE;
  }

  void Reset(HANDLE handle = nullptr) {
    if (*this) {
      CloseHandle(handle_);
    }
    handle_ = handle;
  }

 private:
  HANDLE handle_ = nullptr;
};

void WriteAll(HANDLE output, const void* data, DWORD size) {
  if (output == nullptr || output == INVALID_HANDLE_VALUE) {
    return;
  }

  const auto* bytes = static_cast<const std::uint8_t*>(data);
  DWORD written_total = 0;
  while (written_total < size) {
    DWORD written = 0;
    if (!WriteFile(output, bytes + written_total, size - written_total, &written,
                   nullptr) ||
        written == 0) {
      return;
    }
    written_total += written;
  }
}

std::string Utf8(const std::wstring& value) {
  if (value.empty()) {
    return {};
  }

  const int required = WideCharToMultiByte(
      CP_UTF8, 0, value.data(), static_cast<int>(value.size()), nullptr, 0,
      nullptr, nullptr);
  if (required <= 0) {
    return {};
  }

  std::string result(static_cast<std::size_t>(required), '\0');
  WideCharToMultiByte(CP_UTF8, 0, value.data(),
                      static_cast<int>(value.size()), result.data(), required,
                      nullptr, nullptr);
  return result;
}

void WriteText(HANDLE output, const std::wstring& text) {
  const std::string utf8 = Utf8(text);
  WriteAll(output, utf8.data(), static_cast<DWORD>(utf8.size()));
}

std::wstring Win32Message(DWORD error) {
  wchar_t* buffer = nullptr;
  const DWORD size = FormatMessageW(
      FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM |
          FORMAT_MESSAGE_IGNORE_INSERTS,
      nullptr, error, 0, reinterpret_cast<wchar_t*>(&buffer), 0, nullptr);
  if (size == 0 || buffer == nullptr) {
    return L"unknown Windows error";
  }

  std::wstring message(buffer, size);
  LocalFree(buffer);
  while (!message.empty() &&
         (message.back() == L'\r' || message.back() == L'\n' ||
          message.back() == L' ')) {
    message.pop_back();
  }
  return message;
}

void ReportError(const std::wstring& operation, DWORD error = GetLastError()) {
  WriteText(GetStdHandle(STD_ERROR_HANDLE),
            L"wsl1-pm2-bridge: " + operation + L" failed (" +
                std::to_wstring(error) + L"): " + Win32Message(error) +
                L"\n");
}

std::wstring QuoteArgument(const std::wstring& argument) {
  if (!argument.empty() &&
      argument.find_first_of(L" \t\n\v\"") == std::wstring::npos) {
    return argument;
  }

  std::wstring result = L"\"";
  std::size_t backslashes = 0;
  for (const wchar_t character : argument) {
    if (character == L'\\') {
      ++backslashes;
      continue;
    }

    if (character == L'\"') {
      result.append(backslashes * 2 + 1, L'\\');
      result.push_back(L'\"');
    } else {
      result.append(backslashes, L'\\');
      result.push_back(character);
    }
    backslashes = 0;
  }

  result.append(backslashes * 2, L'\\');
  result.push_back(L'\"');
  return result;
}

std::wstring BuildDirectCommandLine(const std::vector<std::wstring>& args) {
  std::wstring command_line;
  for (const auto& argument : args) {
    if (!command_line.empty()) {
      command_line.push_back(L' ');
    }
    command_line += QuoteArgument(argument);
  }
  return command_line;
}

std::wstring ComSpec() {
  const DWORD required = GetEnvironmentVariableW(L"COMSPEC", nullptr, 0);
  if (required == 0) {
    return L"C:\\Windows\\System32\\cmd.exe";
  }

  std::wstring value(required, L'\0');
  const DWORD written =
      GetEnvironmentVariableW(L"COMSPEC", value.data(), required);
  if (written == 0 || written >= required) {
    return L"C:\\Windows\\System32\\cmd.exe";
  }
  value.resize(written);
  return value;
}

struct PumpContext {
  HANDLE input;
  HANDLE output;
};

DWORD WINAPI PumpPipe(void* opaque) {
  auto* context = static_cast<PumpContext*>(opaque);
  std::uint8_t buffer[16 * 1024];

  for (;;) {
    DWORD read = 0;
    if (!ReadFile(context->input, buffer, sizeof(buffer), &read, nullptr) ||
        read == 0) {
      return 0;
    }
    WriteAll(context->output, buffer, read);
  }
}

struct Options {
  enum class Mode { kNone, kCmd, kExe } mode = Mode::kNone;
  std::wstring working_directory;
  std::wstring shell_command;
  std::vector<std::wstring> direct_args;
};

void PrintUsage(HANDLE output) {
  WriteText(
      output,
      L"wsl1-pm2-bridge " + std::wstring(kVersion) +
          L"\n\n"
          L"Usage:\n"
          L"  wsl1-pm2-bridge.exe [--cwd WINDOWS_DIR] --cmd COMMAND\n"
          L"  wsl1-pm2-bridge.exe [--cwd WINDOWS_DIR] --exe PROGRAM [ARG ...]\n\n"
          L"Options:\n"
          L"  --cmd COMMAND  Run a CMD/BAT command through cmd.exe /d /s /c.\n"
          L"  --exe PROGRAM  Start a Windows executable directly.\n"
          L"  --cwd DIR      Set the Windows working directory for the child.\n"
          L"  --help         Show this help.\n"
          L"  --version      Show the version.\n");
}

bool ParseOptions(int argc, wchar_t** argv, Options* options, int* exit_code) {
  for (int index = 1; index < argc; ++index) {
    const std::wstring argument = argv[index];

    if (argument == L"--help" || argument == L"-h") {
      PrintUsage(GetStdHandle(STD_OUTPUT_HANDLE));
      *exit_code = 0;
      return false;
    }
    if (argument == L"--version") {
      WriteText(GetStdHandle(STD_OUTPUT_HANDLE),
                L"wsl1-pm2-bridge " + std::wstring(kVersion) + L"\n");
      *exit_code = 0;
      return false;
    }
    if (argument == L"--cwd") {
      if (++index >= argc) {
        WriteText(GetStdHandle(STD_ERROR_HANDLE),
                  L"wsl1-pm2-bridge: --cwd requires a directory\n");
        *exit_code = 2;
        return false;
      }
      options->working_directory = argv[index];
      continue;
    }
    if (argument == L"--cmd") {
      if (options->mode != Options::Mode::kNone || ++index >= argc) {
        WriteText(GetStdHandle(STD_ERROR_HANDLE),
                  L"wsl1-pm2-bridge: --cmd requires exactly one command\n");
        *exit_code = 2;
        return false;
      }
      options->mode = Options::Mode::kCmd;
      options->shell_command = argv[index];
      if (index + 1 != argc) {
        WriteText(GetStdHandle(STD_ERROR_HANDLE),
                  L"wsl1-pm2-bridge: unexpected argument after --cmd command\n");
        *exit_code = 2;
        return false;
      }
      break;
    }
    if (argument == L"--exe") {
      if (options->mode != Options::Mode::kNone || ++index >= argc) {
        WriteText(GetStdHandle(STD_ERROR_HANDLE),
                  L"wsl1-pm2-bridge: --exe requires a program\n");
        *exit_code = 2;
        return false;
      }
      options->mode = Options::Mode::kExe;
      for (; index < argc; ++index) {
        options->direct_args.emplace_back(argv[index]);
      }
      break;
    }

    WriteText(GetStdHandle(STD_ERROR_HANDLE),
              L"wsl1-pm2-bridge: unknown argument: " + argument + L"\n");
    *exit_code = 2;
    return false;
  }

  if (options->mode == Options::Mode::kNone) {
    PrintUsage(GetStdHandle(STD_ERROR_HANDLE));
    *exit_code = 2;
    return false;
  }
  return true;
}

bool MakePipe(UniqueHandle* read_handle, UniqueHandle* write_handle) {
  SECURITY_ATTRIBUTES attributes{};
  attributes.nLength = sizeof(attributes);
  attributes.bInheritHandle = TRUE;

  HANDLE read_raw = nullptr;
  HANDLE write_raw = nullptr;
  if (!CreatePipe(&read_raw, &write_raw, &attributes, 0)) {
    return false;
  }

  read_handle->Reset(read_raw);
  write_handle->Reset(write_raw);
  if (!SetHandleInformation(read_handle->Get(), HANDLE_FLAG_INHERIT, 0)) {
    return false;
  }
  return true;
}

int Run(const Options& options) {
  UniqueHandle job(CreateJobObjectW(nullptr, nullptr));
  if (!job) {
    ReportError(L"CreateJobObjectW");
    return 3;
  }

  JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits{};
  limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
  if (!SetInformationJobObject(job.Get(), JobObjectExtendedLimitInformation,
                               &limits, sizeof(limits))) {
    ReportError(L"SetInformationJobObject");
    return 3;
  }

  UniqueHandle stdout_read;
  UniqueHandle stdout_write;
  UniqueHandle stderr_read;
  UniqueHandle stderr_write;
  if (!MakePipe(&stdout_read, &stdout_write) ||
      !MakePipe(&stderr_read, &stderr_write)) {
    ReportError(L"CreatePipe");
    return 3;
  }

  SECURITY_ATTRIBUTES inheritable{};
  inheritable.nLength = sizeof(inheritable);
  inheritable.bInheritHandle = TRUE;
  UniqueHandle null_input(CreateFileW(
      L"NUL", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, &inheritable,
      OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr));
  if (!null_input) {
    ReportError(L"CreateFileW(NUL)");
    return 3;
  }

  SIZE_T attribute_size = 0;
  InitializeProcThreadAttributeList(nullptr, 1, 0, &attribute_size);
  std::vector<std::uint8_t> attribute_storage(attribute_size);
  auto* attribute_list = reinterpret_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(
      attribute_storage.data());
  if (!InitializeProcThreadAttributeList(attribute_list, 1, 0,
                                         &attribute_size)) {
    ReportError(L"InitializeProcThreadAttributeList");
    return 3;
  }

  HANDLE inherited_handles[] = {null_input.Get(), stdout_write.Get(),
                                stderr_write.Get()};
  if (!UpdateProcThreadAttribute(
          attribute_list, 0, PROC_THREAD_ATTRIBUTE_HANDLE_LIST,
          inherited_handles, sizeof(inherited_handles), nullptr, nullptr)) {
    const DWORD error = GetLastError();
    DeleteProcThreadAttributeList(attribute_list);
    ReportError(L"UpdateProcThreadAttribute", error);
    return 3;
  }

  STARTUPINFOEXW startup{};
  startup.StartupInfo.cb = sizeof(startup);
  startup.StartupInfo.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;
  startup.StartupInfo.wShowWindow = SW_HIDE;
  startup.StartupInfo.hStdInput = null_input.Get();
  startup.StartupInfo.hStdOutput = stdout_write.Get();
  startup.StartupInfo.hStdError = stderr_write.Get();
  startup.lpAttributeList = attribute_list;

  std::wstring application;
  std::wstring command_line;
  if (options.mode == Options::Mode::kCmd) {
    application = ComSpec();
    command_line = QuoteArgument(application) + L" /d /s /c \"" +
                   options.shell_command + L"\"";
  } else {
    command_line = BuildDirectCommandLine(options.direct_args);
  }

  std::vector<wchar_t> mutable_command(command_line.begin(), command_line.end());
  mutable_command.push_back(L'\0');

  PROCESS_INFORMATION process{};
  const DWORD creation_flags = CREATE_NO_WINDOW | CREATE_SUSPENDED |
                               CREATE_UNICODE_ENVIRONMENT |
                               EXTENDED_STARTUPINFO_PRESENT;
  const BOOL created = CreateProcessW(
      application.empty() ? nullptr : application.c_str(), mutable_command.data(),
      nullptr, nullptr, TRUE, creation_flags, nullptr,
      options.working_directory.empty() ? nullptr
                                        : options.working_directory.c_str(),
      &startup.StartupInfo, &process);
  const DWORD create_error = created ? ERROR_SUCCESS : GetLastError();
  DeleteProcThreadAttributeList(attribute_list);

  if (!created) {
    ReportError(L"CreateProcessW", create_error);
    return 4;
  }

  UniqueHandle child_process(process.hProcess);
  UniqueHandle child_thread(process.hThread);
  stdout_write.Reset();
  stderr_write.Reset();
  null_input.Reset();

  if (!AssignProcessToJobObject(job.Get(), child_process.Get())) {
    const DWORD error = GetLastError();
    TerminateProcess(child_process.Get(), 4);
    WaitForSingleObject(child_process.Get(), INFINITE);
    ReportError(L"AssignProcessToJobObject", error);
    return 4;
  }

  PumpContext stdout_context{stdout_read.Get(),
                             GetStdHandle(STD_OUTPUT_HANDLE)};
  PumpContext stderr_context{stderr_read.Get(),
                             GetStdHandle(STD_ERROR_HANDLE)};
  UniqueHandle stdout_thread(
      CreateThread(nullptr, 0, PumpPipe, &stdout_context, 0, nullptr));
  UniqueHandle stderr_thread(
      CreateThread(nullptr, 0, PumpPipe, &stderr_context, 0, nullptr));
  if (!stdout_thread || !stderr_thread) {
    const DWORD error = GetLastError();
    job.Reset();
    if (stdout_thread) {
      WaitForSingleObject(stdout_thread.Get(), INFINITE);
    }
    if (stderr_thread) {
      WaitForSingleObject(stderr_thread.Get(), INFINITE);
    }
    ReportError(L"CreateThread", error);
    return 3;
  }

  if (ResumeThread(child_thread.Get()) == static_cast<DWORD>(-1)) {
    const DWORD error = GetLastError();
    job.Reset();
    WaitForSingleObject(stdout_thread.Get(), INFINITE);
    WaitForSingleObject(stderr_thread.Get(), INFINITE);
    ReportError(L"ResumeThread", error);
    return 4;
  }

  child_thread.Reset();
  WaitForSingleObject(child_process.Get(), INFINITE);

  DWORD exit_code = 1;
  if (!GetExitCodeProcess(child_process.Get(), &exit_code)) {
    ReportError(L"GetExitCodeProcess");
    exit_code = 4;
  }

  // Closing the job kills any descendants that survived the root process.
  job.Reset();
  WaitForSingleObject(stdout_thread.Get(), INFINITE);
  WaitForSingleObject(stderr_thread.Get(), INFINITE);
  return static_cast<int>(exit_code);
}

}  // namespace

int wmain(int argc, wchar_t** argv) {
  Options options;
  int exit_code = 0;
  if (!ParseOptions(argc, argv, &options, &exit_code)) {
    return exit_code;
  }
  return Run(options);
}
