# SQL注入智能检测平台

基于机器学习和RAG的SQL注入检测与教学平台，集成随机森林检测模型、RAG知识库检索、sqli-labs靶场联动。

## 功能特点

- 随机森林模型识别SQL注入，准确率85%+
- RAG检索知识库，生成注入原理与修复建议
- 检测到注入时一键跳转sqli-labs对应关卡
- 优雅降级、环境变量保护API Key、Docker一键部署

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python, Flask |
| 机器学习 | scikit-learn (TF-IDF, RandomForest) |
| RAG | LangChain, Chroma, 阿里云百炼 |
| 部署 | Docker |

## 快速开始

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

sqli-rag-detector/        
├── README.md              
├── .gitignore
└── rag/          
    ├── app.py
    ├── rag_module.py
    ├── knowledge.txt
    ├── requirements.txt
    └── docker_start.bat
