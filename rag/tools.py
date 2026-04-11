# tools.py
from langchain.tools import tool
from rag_module import get_injection_explanation, get_target_url
from detector import detect_sql
import webbrowser


@tool
def detect_sql_injection(sql_statement: str) -> str:
    """检测SQL语句是否存在注入风险"""
    result = detect_sql(sql_statement)
    if result["result"] == 1:
        return f"⚠️ 检测到 {result['reason']}\n\n{result['explanation']}\n\n是否需要打开对应的靶场进行实战验证？请回复「打开靶场」或「不用了」。"
    else:
        return "✅ 安全：语句无注入风险"


@tool
def get_sql_knowledge(injection_type: str) -> str:
    """获取SQL注入类型的原理解释和修复建议"""
    return get_injection_explanation(injection_type)


@tool
def open_sqli_target(injection_type: str) -> str:
    """
    打开SQL注入靶场对应关卡。
    注意：调用前应先询问用户是否需要。
    """
    url = get_target_url(injection_type)
    if url:
        webbrowser.open(url)
        return f"✅ 已为你打开靶场：{url}\n\n请确保 Docker 容器已启动（docker start sqli-labs-8scenes）"
    else:
        return f"❌ 未找到 {injection_type} 对应的靶场"