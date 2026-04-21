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
    model="qwen-turbo",
    temperature=0.7,
    api_key=DASHSCOPE_API_KEY,
    timeout=10,  # 10秒超时
    max_retries=1,  # 只重试1次
)

system_prompt = """你是一个 SQL 注入安全分析专家。

## 工具
- detect_sql_injection: 检测SQL注入，返回注入类型
- get_sql_knowledge: 返回注入原理和修复建议
- open_sqli_target: 打开靶场

## 规则（必须遵守）

当用户输入SQL语句时，你的回复必须包含以下内容：

1. 调用 detect_sql_injection 得到的结果
2. 调用 get_sql_knowledge 得到的**完整内容**（一字不改）
3. 最后问用户是否需要打开靶场

## 回复格式（必须按这个格式）

检测结果：[detect_sql_injection 返回的内容]

原理与修复：[get_sql_knowledge 返回的内容]

是否需要打开靶场验证？

## 示例

用户：1' OR '1'='1

你的回复必须是：
检测结果：联合查询注入

原理与修复：联合查询注入的原理是攻击者使用UNION SELECT... 修复方法是使用参数化查询...

是否需要打开靶场验证？

## 重要
- 绝对不要省略 get_sql_knowledge 的内容
- 绝对不要自己编造解释
- 在用户说「打开靶场」之前，不要调用 open_sqli_target

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