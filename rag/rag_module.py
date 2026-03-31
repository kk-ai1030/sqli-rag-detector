# rag_module.py
import os
import requests
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

# 阿里云百炼配置（输入API_KEY）
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
if not DASHSCOPE_API_KEY:
    print("⚠️ 警告：未设置 DASHSCOPE_API_KEY 环境变量，请在环境变量中配置")

_retriever = None
KNOWLEDGE_FILE = "knowledge.txt"


def _ensure_knowledge_file():
    """确保知识库文件存在，不存在则创建默认内容"""
    if not os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
            f.write("""
SQL 注入是一种代码注入技术，攻击者通过插入恶意 SQL 语句欺骗数据库执行。

修复方法：使用参数化查询、输入过滤、最小权限原则。

联合查询注入：使用 UNION SELECT 获取额外数据，防御：参数化查询。
报错注入：利用数据库报错提取数据，防御：关闭错误回显。
布尔盲注：根据页面真假判断，防御：统一错误处理。
时间盲注：利用延时函数判断，防御：禁用延时函数。
堆叠查询注入：多语句执行，防御：限制单条语句。
宽字节注入：利用编码漏洞绕过转义，防御：统一 UTF-8 编码。
二次注入：先存储后触发，防御：所有查询都参数化。
""")
        print("✅ 已创建默认 knowledge.txt")


def init_rag():
    """初始化 RAG 检索器"""
    global _retriever
    if _retriever:
        return

    _ensure_knowledge_file()
    print("📖 加载知识库...")
    loader = TextLoader(KNOWLEDGE_FILE, encoding="utf-8")
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = text_splitter.split_documents(docs)
    print(f"   切分为 {len(documents)} 个文本块")

    print("📊 创建向量库...")
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v1",
        dashscope_api_key=DASHSCOPE_API_KEY
    )
    vectorstore = Chroma.from_documents(documents, embeddings)
    _retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    print("✅ RAG 检索器初始化完成")


def call_qwen(prompt: str) -> str:
    """直接调用通义千问 HTTP API"""
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen-turbo",
        "input": {
            "messages": [{"role": "user", "content": prompt}]
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()

        if response.status_code == 200:
            # 你的返回格式是 output.text
            if "output" in data and "text" in data["output"]:
                return data["output"]["text"]
            # 兼容其他格式
            elif "output" in data and "choices" in data["output"]:
                return data["output"]["choices"][0]["message"]["content"]
            else:
                return f"响应格式异常：{data}"
        else:
            return f"调用失败：{data.get('message', '未知错误')}"
    except Exception as e:
        return f"调用异常：{e}"


def get_injection_explanation(injection_type: str) -> str:
    """根据注入类型获取解释和修复建议"""
    global _retriever
    if _retriever is None:
        init_rag()

    query_map = {
        "时间盲注": "解释时间盲注的原理和修复建议",
        "布尔盲注": "解释布尔盲注的原理和修复建议",
        "联合查询注入": "解释联合查询注入的原理和修复建议",
        "报错注入": "解释报错注入的原理和修复建议",
        "堆叠查询注入": "解释堆叠查询注入的原理和修复建议",
        "宽字节注入": "解释宽字节注入的原理和修复建议",
        "二次注入": "解释二次注入的原理和修复建议",
        "混淆变形注入": "解释 SQL 注入混淆绕过技术的原理和防御",
    }
    query = query_map.get(injection_type, "解释 SQL 注入的原理和通用修复建议")

    try:
        # 1. 从向量库检索相关知识
        docs = _retriever.invoke(query)

        # 2. 提取文档内容
        if docs:
            context = "\n\n".join([doc.page_content for doc in docs[:3]])
        else:
            context = "知识库中暂无相关信息"

        # 3. 构建 prompt
        full_prompt = f"""你是一个 SQL 注入安全专家。根据以下知识库内容回答问题：

{context}

用户问题：{query}

请给出准确、有帮助的回答。"""

        # 4. 调用大模型
        answer = call_qwen(full_prompt)
        return answer
    except Exception as e:
        return f"知识库检索失败：{e}"

# 注入类型对应的靶场 URL 映射
INJECTION_URL_MAP = {
    "联合查询注入": "http://127.0.0.1:8080/Less-1/",
    "报错注入": "http://127.0.0.1:8080/Less-5/",
    "布尔盲注": "http://127.0.0.1:8080/Less-8/",
    "时间盲注": "http://127.0.0.1:8080/Less-9/",
    "堆叠查询注入": "http://127.0.0.1:8080/Less-3/",
    "宽字节注入": "http://127.0.0.1:8080/Less-32/",
    "二次注入": "http://127.0.0.1:8080/Less-24/",
    "POST注入": "http://127.0.0.1:8080/Less-11/",
}

def get_target_url(injection_type: str) -> str:
    """根据注入类型返回对应的靶场 URL"""
    return INJECTION_URL_MAP.get(injection_type, None)


if __name__ == "__main__":
    # 测试
    init_rag()
    result = get_injection_explanation("联合查询注入")
    print("测试结果：", result)