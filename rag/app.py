from flask import Flask, render_template_string, request, jsonify
import joblib
import re
from rag_module import init_rag, get_injection_explanation, get_target_url

app = Flask(__name__)

# 加载模型
print("加载模型...")
model = joblib.load("sql_rf_model.pkl")
tfidf = joblib.load("sql_tfidf.pkl")
print("✅ 模型加载成功")

# 初始化 RAG
print("初始化 RAG...")
init_rag()
print("✅ RAG初始化成功")


def preprocess_sql(sql):
    if not sql:
        return ""
    sql = re.sub(r'\s+', ' ', sql.strip())
    return sql.lower()


def get_injection_type(sql):
    sql_lower = sql.lower()
    if any(k in sql_lower for k in ["sleep", "benchmark", "waitfor"]):
        return "时间盲注"
    if "union select" in sql_lower:
        return "联合查询注入"
    if any(k in sql_lower for k in ["updatexml", "extractvalue"]):
        return "报错注入"
    if any(k in sql_lower for k in ["and 1=1", "or 1=1"]):
        return "布尔盲注"
    if ";" in sql and any(k in sql_lower for k in ["drop", "insert", "delete"]):
        return "堆叠查询注入"
    if any(k in sql_lower for k in ["%df", "%27"]):
        return "宽字节注入"
    return "SQL注入"


def clean_markdown(text):
    if not text:
        return ""
    text = re.sub(r'###\s*', '', text)
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'`', '', text)
    text = re.sub(r'```', '', text)
    text = re.sub(r'\|', ' ', text)
    text = re.sub(r'\-{3,}', '', text)
    return text.strip()


def detect_sql(sql):
    if not sql:
        return {"result": 0, "reason": "空输入", "explanation": "", "target_url": None}

    processed = preprocess_sql(sql)
    vec = tfidf.transform([processed])
    result = model.predict(vec)[0]

    if result == 1:
        injection_type = get_injection_type(sql)
        explanation = get_injection_explanation(injection_type)
        explanation = clean_markdown(explanation)
        target_url = get_target_url(injection_type)
        return {
            "result": 1,
            "reason": injection_type,
            "explanation": explanation,
            "target_url": target_url
        }
    else:
        return {
            "result": 0,
            "reason": "正常SQL",
            "explanation": "语句安全，无注入风险",
            "target_url": None
        }


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI SQL注入检测平台</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            min-height: 100vh;
            background: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card { 
            background: white; 
            border-radius: 24px; 
            padding: 32px; 
            max-width: 800px;
            width: 100%;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 { color: #333; margin-bottom: 8px; font-size: 28px; }
        .badge { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 6px 16px; 
            border-radius: 20px; 
            font-size: 12px; 
            display: inline-block; 
            margin-bottom: 24px;
        }
        textarea { 
            width: 100%; 
            height: 150px; 
            padding: 16px; 
            font-family: 'Monaco', 'Menlo', monospace; 
            font-size: 13px; 
            border: 2px solid #e0e4e8; 
            border-radius: 16px; 
            resize: vertical;
            outline: none;
        }
        textarea:focus { border-color: #667eea; }
        button { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none; 
            padding: 14px 28px; 
            border-radius: 40px; 
            cursor: pointer; 
            margin-top: 20px; 
            width: 100%; 
            font-size: 16px; 
            font-weight: 600;
        }
        button:hover { opacity: 0.9; }
        .result { margin-top: 24px; padding: 20px; border-radius: 16px; line-height: 1.6; }
        .danger { background: #fff5f5; border-left: 4px solid #dc3545; }
        .safe { background: #e8f5e9; border-left: 4px solid #28a745; }
        .explanation-box { 
            background: #f8f9fa; 
            padding: 16px; 
            border-radius: 12px; 
            margin-top: 12px; 
            max-height: 400px; 
            overflow-y: auto; 
            font-size: 14px; 
            line-height: 1.7;
            white-space: pre-wrap;
        }
        hr { margin: 16px 0; border: none; border-top: 1px solid #e0e4e8; }
        .loading { text-align: center; padding: 20px; color: #667eea; }
        .target-btn {
            background: #28a745 !important;
            margin-top: 15px;
            width: auto !important;
            padding: 8px 20px !important;
            font-size: 14px !important;
            display: inline-block !important;
        }
        .target-btn:hover { background: #218838 !important; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🛡️ AI SQL注入检测平台</h1>
        <div class="badge">RAG增强版 | 随机森林 + 通义千问</div>

        <textarea id="sqlInput" placeholder="输入SQL语句进行检测，例如：&#10;1&#39; OR &#39;1&#39;=&#39;1"></textarea>

        <button onclick="doDetect()">🔍 执行AI检测</button>

        <div id="result" style="display: none;"></div>
    </div>

    <script>
        async function doDetect() {
            const sql = document.getElementById('sqlInput').value;
            const resultDiv = document.getElementById('result');

            if (!sql.trim()) {
                resultDiv.style.display = 'block';
                resultDiv.className = 'result danger';
                resultDiv.innerHTML = '请输入SQL语句';
                return;
            }

            resultDiv.style.display = 'block';
            resultDiv.className = 'result';
            resultDiv.innerHTML = '<div class="loading">🔄 AI 分析中，请稍候...</div>';

            try {
                const res = await fetch('/detect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({sql: sql})
                });
                const data = await res.json();

                if (data.result === 1) {
                    resultDiv.className = 'result danger';
                    let explanation = data.explanation || '暂无解释';
                    let targetUrl = data.target_url;
                    let buttonHtml = '';
                    if (targetUrl) {
                        buttonHtml = `<button class="target-btn" onclick="window.open('${targetUrl}', '_blank')">🎯 打开手工靶场验证（${data.reason}）</button>`;
                    }
                    resultDiv.innerHTML = `
                        <div style="font-weight:600; font-size:16px;">❌ 存在SQL注入风险</div>
                        <div style="margin-top:8px;">📌 注入类型：<strong>${data.reason}</strong></div>
                        <hr>
                        <div><strong>📖 专家解释：</strong></div>
                        <div class="explanation-box">${explanation.replace(/\\n/g, '<br>')}</div>
                        ${buttonHtml}
                    `;
                } else {
                    resultDiv.className = 'result safe';
                    resultDiv.innerHTML = `
                        <div style="font-weight:600; font-size:16px;">✅ 安全</div>
                        <div style="margin-top:8px;">${data.explanation}</div>
                    `;
                }
            } catch (err) {
                resultDiv.className = 'result danger';
                resultDiv.innerHTML = `请求失败：${err.message}`;
            }
        }
    </script>
</body>
</html>
'''


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/detect", methods=["POST"])
def detect():
    data = request.get_json()
    sql = data.get("sql", "")
    return jsonify(detect_sql(sql))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)