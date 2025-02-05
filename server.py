import uuid, multiprocessing
from flask import Flask, request, jsonify
from worker import worker_loop
import time

app = Flask(__name__)

sessions = {}
session_timestamps = {}

def create_session():
    session_id = str(uuid.uuid4())
    parent_conn, child_conn = multiprocessing.Pipe()
    p = multiprocessing.Process(target=worker_loop, args=(child_conn,))
    p.daemon = True
    p.start()
    sessions[session_id] = (p, parent_conn)
    session_timestamps[session_id] = time.time()
    return session_id

def cleanup_sessions():
    now = time.time()
    expired_sessions = [sid for sid, timestamp in session_timestamps.items() if now - timestamp > 300]  # 5 min
    for sid in expired_sessions:
        p, _ = sessions.pop(sid, (None, None))
        if p:
            p.terminate()
        session_timestamps.pop(sid, None)

@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json(force=True)
    code = data.get("code")
    session_id = data.get("id")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    if not session_id or session_id not in sessions:
        session_id = create_session()

    p, conn = sessions[session_id]

    try:
        conn.send({"code": code})
        if conn.poll(3):  # 3 seconds timeout on response
            result = conn.recv()
        else:
            result = {"error": "execution timeout"}
    except Exception as e:
        result = {"error": str(e)}

    response = {}
    if "error" in result:
        response["error"] = result["error"]
    else:
        response["id"] = session_id
        if result.get("stdout"):
            response["stdout"] = result["stdout"]
        if result.get("stderr"):
            response["stderr"] = result["stderr"]

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)