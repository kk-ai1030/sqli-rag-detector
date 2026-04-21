# app.py
from flask import Flask, request, jsonify, render_template
from agent import chat_with_agent
from detector import detect_sql
import time
import webbrowser
import threading

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


# ========== 注意：这个路由要放在 agent_chat 函数外面！ ==========
@app.route("/open_target", methods=["POST"])
def open_target():
    """直接打开靶场（绕过 Agent）"""
    data = request.get_json()
    injection_type = data.get("injection_type", "")

    from rag_module import get_target_url

    def open_browser(url):
        webbrowser.open(url)

    url = get_target_url(injection_type)
    if url:
        # 在后台线程打开浏览器，避免阻塞
        threading.Thread(target=open_browser, args=(url,)).start()
        return jsonify({"success": True, "url": url})
    else:
        return jsonify({"success": False, "error": f"未找到 {injection_type} 对应的靶场"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)