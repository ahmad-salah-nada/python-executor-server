import io, signal, resource, traceback, builtins
from contextlib import redirect_stdout, redirect_stderr

DISALLOWED_MODULES = {'os', 'sys', 'socket', 'subprocess'}

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name in DISALLOWED_MODULES:
        raise ImportError("Permission denied")
    return __import__(name, globals, locals, fromlist, level)

def set_sandbox():
    safe_builtins = builtins.__dict__.copy()
    safe_builtins['__import__'] = safe_import
    safe_builtins['eval'] = lambda x: "Eval is disabled"
    safe_builtins['exec'] = lambda x: "Exec is disabled"
    return {"__builtins__": safe_builtins}
def alarm_handler(signum, frame):
    raise TimeoutError("execution timeout")

def run_code(code, globals_dict):
    mem_limit = 100 * 1024 * 1024 
    current_soft, current_hard = resource.getrlimit(resource.RLIMIT_AS)
    if current_hard != resource.RLIM_INFINITY and mem_limit > current_hard:
        mem_limit = current_hard

    try:
        resource.setrlimit(resource.RLIMIT_AS, (mem_limit, mem_limit))
    except ValueError:
        print("Warning: Unable to set memory limit; proceeding without a custom limit.")
    
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(2)
    
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, globals_dict)
        result = {"stdout": stdout_capture.getvalue(), "stderr": stderr_capture.getvalue()}
    except TimeoutError:
        result = {"error": "execution timeout"}
    except ImportError as e:
        result = {"error": str(e)}
    except Exception:
        tb = traceback.format_exc()
        result = {"stderr": tb}
    finally:
        signal.alarm(0)
    
    return result

def worker_loop(pipe):
    globals_dict = set_sandbox()
    while True:
        try:
            data = pipe.recv()
        except EOFError:
            break
        result = run_code(data.get("code", ""), globals_dict)
        pipe.send(result)
