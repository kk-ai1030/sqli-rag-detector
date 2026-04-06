# rag_module.py（优化版 - 使用 ChatTongyi）
import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi  # 改用 ChatTongyi
from langchain_core.prompts import ChatPromptTemplate

# 阿里云百炼配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
if not DASHSCOPE_API_KEY:
    print("⚠️ 警告：未设置 DASHSCOPE_API_KEY 环境变量")

_retriever = None
_llm = None
KNOWLEDGE_FILE = "knowledge.txt"


def _ensure_knowledge_file():
    """确保知识库文件存在"""
    if not os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
            f.write("""SQL注入原理与防御...
联合查询注入：使用 UNION SELECT 获取额外数据，防御：参数化查询。
报错注入：利用数据库报错提取数据，防御：关闭错误回显。
布尔盲注：根据页面真假判断，防御：统一错误处理。
时间盲注：利用延时函数判断，防御：禁用延时函数。
堆叠查询注入：多语句执行，防御：限制单条语句。
宽字节注入：利用编码漏洞绕过转义，防御：统一 UTF-8 编码。
二次注入：先存储后触发，防御：所有查询都参数化。
""")


def get_llm():
    """获取 LLM 实例（单例模式）"""
    global _llm
    if _llm is None:
        _llm = ChatTongyi(
            model="qwen3-max",  # 你用的是 Qwen3-Max
            temperature=0.7,
            api_key=DASHSCOPE_API_KEY,  # 直接传入 API Key
        )
        print("✅ LLM 初始化完成（Qwen3-Max）")
    return _llm


def init_rag():
    """初始化 RAG 检索器（带持久化）"""
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
        model="text-embedding-v3",  # 升级到 v3
        dashscope_api_key=DASHSCOPE_API_KEY
    )

    PERSIST_DIR = "./chroma_db"
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
        collection_name="sql_injection_kb"
    )

    _retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 4,  "score_threshold": 0.5}
    )
    print("✅ RAG 检索器初始化完成（已持久化）")


def get_injection_explanation(injection_type: str) -> str:
    """根据注入类型获取解释和修复建议"""
    global _retriever
    if _retriever is None:
        init_rag()

    query_map = {
            "时间盲注": "解释时间盲注的原理和修复建议",
            "联合查询注入": "解释联合查询注入的原理和修复建议",
            "报错注入": "解释报错注入的原理和修复建议",
            "布尔盲注": "解释布尔盲注的原理和修复建议",
            "堆叠查询注入": "解释堆叠查询注入的原理和修复建议",
            "宽字节注入": "解释宽字节注入的原理和修复建议",
            "二次注入": "解释二次注入的原理和修复建议"
    }
    query = query_map.get(injection_type, "解释 SQL 注入的原理和通用修复建议")

    try:
        docs = _retriever.invoke(query)
        if docs:
            context = "\n\n".join([doc.page_content for doc in docs[:3]])
        else:
            context = "知识库中暂无相关信息"

        # 使用 ChatPromptTemplate
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个SQL注入安全专家。请严格基于以下知识库内容回答，不要编造信息。\n\n知识库内容：\n{context}"),
            ("human", "{query}")
        ])

        formatted_prompt = prompt_template.invoke({
            "context": context,
            "query": query
        })

        llm = get_llm()
        response = llm.invoke(formatted_prompt)
        return response.content
    except Exception as e:
        return f"知识库检索失败：{e}"


# 注入类型对应的靶场 URL 映射（保持不变）
INJECTION_URL_MAP = {
    "联合查询注入": "http://127.0.0.1:8080/Less-1/",
    "报错注入": "http://127.0.0.1:8080/Less-5/",
    "布尔盲注": "http://127.0.0.1:8080/Less-8/",
    "时间盲注": "http://127.0.0.1:8080/Less-9/",
}


def get_target_url(injection_type: str) -> str:
    """根据注入类型返回对应的靶场 URL"""
    return INJECTION_URL_MAP.get(injection_type, None)


if __name__ == "__main__":
    init_rag()
    # result = get_injection_explanation("联合查询注入")
    # print("测试结果：", result)