# Python Executor Server

## Overview
This is a Flask-based server that securely executes Python code in isolated environments. It supports:
- **Persistent execution sessions**.
- **Resource limits**.
- **Sandboxing**.
- **Testing suite**.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/python-executor-server.git
cd python-executor-server
```

### 2. Set up a virtual environment (optional but recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
or
```bash
pip3 install -r requirements.txt
```

## Running the Server

Start the Flask server:
```bash
python3 server.py
```
The server will run on `http://localhost:5000`.

## API Usage

### **Execute Python Code**

### **Persistent Session Execution**
#### Request:
```http
POST /execute
Content-Type: application/json
{
  "id": "SESSION_ID",
  "code": "x = 123"
}
```
#### Response:
```json
{
  "id": "SESSION_ID"
}
```

### **Session-Based Code Execution**
```http
POST /execute
Content-Type: application/json
{
  "id": "SESSION_ID",
  "code": "print(x)"
}
```
Response:
```json
{
  "id": "SESSION_ID",
  "stdout": "123\n"
}
```

## Running Tests
To verify everything is working correctly, run:
```bash
python3 test_executor.py
```
Before running the tests, place any Python code that you want to execute with the server in the file "code.py".

