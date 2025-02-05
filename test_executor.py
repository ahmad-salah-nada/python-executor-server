import requests
import sys

BASE_URL = "http://localhost:5000/execute"

def test_basic_execution():
    payload = {"code": "print('Hello, World!')"}
    response = requests.post(BASE_URL, json=payload)
    data = response.json()
    assert "stdout" in data, f"stdout missing: {data}"
    assert data["stdout"] == "Hello, World!\n", f"Unexpected output: {data['stdout']}"
    print("Basic execution passed:", data, '\n')

def test_timeout():
    payload = {"code": "while True: pass"}
    response = requests.post(BASE_URL, json=payload)
    data = response.json()
    assert "error" in data, f"Error not returned: {data}"
    assert data["error"] == "execution timeout", f"Unexpected error message: {data['error']}"
    print("Timeout test passed:", data, '\n')

def test_persistent_session():
    payload1 = {"code": "x = 123"}
    response1 = requests.post(BASE_URL, json=payload1)
    data1 = response1.json()
    assert "id" in data1, f"Session id not returned: {data1}"
    session_id = data1["id"]
    print("Session created:", session_id, '\n')
    
    payload2 = {"id": session_id, "code": "print(x)"}
    response2 = requests.post(BASE_URL, json=payload2)
    data2 = response2.json()
    assert "stdout" in data2, f"stdout missing in persistent session test: {data2}"
    assert data2["stdout"] == "123\n", f"Persistent state not retained: {data2['stdout']}"
    print("Persistent session test passed:", data2, '\n')

def test_security_enforcement():
    payload = {"code": "import os; os.remove('file.txt')"}
    response = requests.post(BASE_URL, json=payload)
    data = response.json()
    assert "error" in data, f"Security error not raised: {data}"
    assert "Permission denied" in data["error"] or "not allowed" in data["error"], f"Unexpected security error: {data['error']}"
    print("Security enforcement test passed:", data, '\n')

def test_memory_limit():
    if sys.platform == "darwin":
        print("Memory limit test skipped on macOS.\n")
        return

    payload = {"code": "a = [0] * (10**8)"}
    response = requests.post(BASE_URL, json=payload)
    data = response.json()
    assert "error" in data or "stderr" in data, f"Memory limit test failed, expected error: {data}"
    print("Memory limit test passed:", data, '\n')

def test_builtin_print():
    payload = {"code": "print('Testing builtins')"}
    response = requests.post(BASE_URL, json=payload)
    data = response.json()
    assert "stdout" in data, f"stdout missing in builtins test: {data}"
    assert data["stdout"] == "Testing builtins\n", f"Builtins not working as expected: {data['stdout']}"
    print("Builtins test passed:", data, '\n')

def execute_script_from_file(filename):
    try:
        with open(filename, 'r') as file:
            code = file.read()
        payload = {"code": code}
        response = requests.post(BASE_URL, json=payload)
        data = response.json()
        print(f"Execution result for {filename}:", data, '\n')
    except Exception as e:
        print(f"Error reading or executing {filename}: {e}", '\n')

def test_malicious_code():
    payload = {"code": "import os; os.system('rm -rf /')"}
    response = requests.post(BASE_URL, json=payload)
    data = response.json()
    assert "error" in data, "Expected error on dangerous code execution"
    print("Malicious code test passed:", data, '\n')

if __name__ == '__main__':
    print("Running intensive tests on the code execution server...\n")
    test_basic_execution()
    test_timeout()
    test_persistent_session()
    test_security_enforcement()
    test_memory_limit()
    test_builtin_print()
    test_malicious_code()

    print("\nAll tests passed successfully!\n")
    
    
    script_filename = "code.py"
    execute_script_from_file(script_filename)
    
