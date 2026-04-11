# 🛡️ AI SQL注入智能检测平台

基于**随机森林 + RAG + Agent** 的 SQL 注入检测系统。支持注入检测、AI 原理解释、多轮对话、靶场联动。

## ✨ 核心特性

| 模块 | 能力 |
| :--- | :--- |
| **🔍 注入检测** | 随机森林模型快速判断（毫秒级），准确率 85% |
| **🧠 RAG 解释** | 检索知识库 + 通义千问生成原理与修复建议 |
| **🤖 Agent 智能体** | ReAct 框架多轮对话，自主调用检测/知识库/靶场工具 |
| **🎯 靶场联动** | 一键跳转 sql-labs 对应关卡，实战验证 |
| **💾 持久化** | 向量库持久化，重启无需重建 |
| **📝 历史会话** | 前端支持多会话管理，对话自动保存 |

## 🛠️ 技术栈

| 模块 | 技术 |
| :--- | :--- |
| Web 框架 | Flask |
| 机器学习 | scikit-learn（随机森林） |
| 向量数据库 | Chroma（持久化） |
| 大模型 | 通义千问 Qwen3-Max |
| Agent 框架 | LangChain ReAct |
| 容器 | Docker |


## 🚀 快速开始

### 安装依赖
pip install -r requirements.txt

### 配置API Key
设置环境变量 DASHSCOPE_API_KEY

### 启动靶场
docker start sqli-labs-8scenes

靶场地址访问 http://localhost:8000

### 运行服务
python app.py

访问 http://localhost:5001

## 📁 项目结构
```
rag/
├── app.py # Flask 主入口
├── agent.py # Agent 创建与对话
├── tools.py # Agent 工具（检测/知识库/靶场）
├── detector.py # SQL 检测模型
├── rag_module.py # RAG 检索模块
├── templates/
│ └── index.html # 前端页面
├── knowledge.txt # 知识库源文件
├── chroma_db/ # 向量库（自动生成，已忽略）
├── requirements.txt
└── .gitignore
README.md
```
