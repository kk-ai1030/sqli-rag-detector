import joblib
import re
import os
from rag_module import init_rag, get_injection_explanation, get_target_url

# 获取当前文件所在目录（rag/）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 模型文件就在当前目录下
model_path = os.path.join(BASE_DIR, "sql_rf_model.pkl")
tfidf_path = os.path.join(BASE_DIR, "sql_tfidf.pkl")

print("加载模型...")
model = joblib.load(model_path)
tfidf = joblib.load(tfidf_path)
print("✅ 模型加载成功")

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