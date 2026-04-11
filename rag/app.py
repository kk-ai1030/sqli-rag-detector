# app.py
from flask import Flask, request, jsonify, render_template
from agent import chat_with_agent
from detector import detect_sql
import time

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():
    data = request.get_json()
    sql = data.get("sql", "")
    return jsonify(detect_sql(sql))


@app.route("/agent", methods=["POST"])
def agent_chat():
    """普通对话接口（非流式）"""
    start = time.time()

    data = request.get_json()
    user_input = data.get("message", "")
    session_id = data.get("session_id", "default")
    response = chat_with_agent(user_input, session_id)

    elapsed = time.time() - start
    print(f"⏱️ 总耗时: {elapsed:.2f} 秒")

    return jsonify({"response": response})
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)