# agent.py
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain_community.chat_models import ChatTongyi
from dotenv import load_dotenv
import os

from tools import detect_sql_injection, get_sql_knowledge, open_sqli_target

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

model = ChatTongyi(
    model="qwen3-max",
    temperature=0.7,
    api_key=DASHSCOPE_API_KEY,
    timeout=10,  # 10秒超时
    max_retries=1,  # 只重试1次
)

system_prompt = """你是一个 SQL 注入安全分析专家。你必须严格按照以下规则执行：

## 规则1：检测 SQL 语句
当用户输入任何 SQL 语句时，你**必须**首先调用 `detect_sql_injection` 工具。
- 输入：用户提供的完整 SQL 语句
- 输出：检测结果

例如：
用户输入：1' OR '1'='1
你应该调用：detect_sql_injection(sql_statement="1' OR '1'='1")

## 规则2：解释注入原理
检测到注入后，调用 `get_sql_knowledge` 获取详细解释。

## 规则3：打开靶场
只有当用户明确说「打开靶场」、「需要」、「是的」时，才调用 `open_sqli_target`。

## 规则4：禁止直接回答
在没有调用工具之前，禁止直接回答用户的问题。

## 规则5：禁止编造
调用工具后，工具返回的结果就是最终答案。不要自己编造工具没有返回的信息。

现在开始执行。"""

tools_list = [detect_sql_injection, get_sql_knowledge, open_sqli_target]
checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=tools_list,
    system_prompt=system_prompt,
    checkpointer=checkpointer,
)


def chat_with_agent(user_input: str, session_id: str = "default") -> str:
    config = {"configurable": {"thread_id": session_id}}
    response = agent.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )
    return response["messages"][-1].content