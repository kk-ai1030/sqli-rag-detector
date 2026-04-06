# SQL注入智能检测平台

基于随机森林 + RAG + 通义千问 Qwen3-Max的 SQL 注入检测系统。检测到注入后，自动通过 RAG 检索知识库，生成原理解释和修复建议，并支持一键跳转 Docker 靶场实战验证。

## 功能特点

- ⚡ 双重检测架构：随机森林快速筛查（毫秒级）+ RAG 深度解释
- 🧠 RAG 增强问答：基于 LangChain + Chroma，检索注入原理与修复方案
- 🔗 靶场联动：检测出注入类型后，自动返回对应 sql-labs 关卡链接
- 📦 工程化设计：向量库持久化、Prompt 模板化、LLM 单例模式

## 🛠️ 技术栈

| 模块 | 技术 |
| :--- | :--- |
| Web 框架 | Flask |
| 机器学习 | scikit-learn（随机森林） |
| RAG 框架 | LangChain |
| 大模型 | 通义千问 Qwen3-Max（ChatTongyi） |
| 向量数据库 | Chroma（持久化） |
| Embedding | DashScope（text-embedding-v3） |
| 容器化 | Docker |

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

## 项目结构
```
rag/
├── app.py # Flask Web 服务
├── rag_module.py # RAG 检索与 LLM 调用（核心）
├── sql_rf_model.pkl # 随机森林模型
├── sql_tfidf.pkl # TF-IDF 向量器
├── knowledge.txt # 知识库源文件
├── chroma_db/ # 向量库持久化目录（自动生成）
├── requirements.txt # Python 依赖
└── docker_start.bat # Docker 靶场启动脚本
.gitignore
README.md
```
