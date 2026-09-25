"""Own the verification process tree, including on restricted Windows hosts."""
import os
import signal


class ProcessTree:
    def __init__(self):
        self.process = None
        self.job = None
        if os.name != 'nt':
            return
        import ctypes
        from ctypes import wintypes as w
        self.ctypes = ctypes
        kernel = self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateJobObjectW.argtypes = [w.LPVOID, w.LPCWSTR]
        kernel.CreateJobObjectW.restype = w.HANDLE
        kernel.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, w.LPVOID, w.DWORD]
        kernel.SetInformationJobObject.restype = w.BOOL
        kernel.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        kernel.AssignProcessToJobObject.restype = w.BOOL
        kernel.TerminateJobObject.argtypes = [w.HANDLE, w.UINT]
        kernel.TerminateJobObject.restype = w.BOOL
        kernel.CloseHandle.argtypes = [w.HANDLE]
        kernel.CloseHandle.restype = w.BOOL
        class Limits(ctypes.Structure):
            _fields_ = [('process_time', ctypes.c_int64), ('job_time', ctypes.c_int64),
                        ('flags', w.DWORD), ('min_working', ctypes.c_size_t), ('max_working', ctypes.c_size_t),
                        ('active_processes', w.DWORD), ('affinity', ctypes.c_size_t),
                        ('priority', w.DWORD), ('scheduling', w.DWORD)]
        class Extended(ctypes.Structure):
            _fields_ = [('basic', Limits), ('io', ctypes.c_uint64 * 6),
                        ('process_memory', ctypes.c_size_t), ('job_memory', ctypes.c_size_t),
                        ('peak_process', ctypes.c_size_t), ('peak_job', ctypes.c_size_t)]
        self.job = kernel.CreateJobObjectW(None, None)
        if not self.job:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not kernel.SetInformationJobObject(self.job, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def attach(self, process):
        self.process = process
        if self.job and not self.kernel.AssignProcessToJobObject(self.job, int(process._handle)):
            error = self.ctypes.WinError(self.ctypes.get_last_error())
            process.kill()
            process.wait(timeout=10)
            self.close()
            raise error

    def stop(self):
        if self.job:
            if not self.kernel.TerminateJobObject(self.job, 1):
                raise self.ctypes.WinError(self.ctypes.get_last_error())
        elif self.process:
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if self.process:
            self.process.wait(timeout=10)

    def close(self):
        if self.job:
            self.kernel.CloseHandle(self.job)
            self.job = None
        elif self.process and os.name != 'nt':
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
