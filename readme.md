# AI 智能客服系统

基于 Python + LangChain + LangGraph + RAG 技术构建的智能客服问答系统，专为床垫产品场景打造，支持自动问答、知识库检索、多轮对话与上下文理解。

## 项目简介

本项目旨在解决传统客服重复问答多、响应慢、人工成本高等问题，通过大模型 + 本地知识库的方式，实现：

- 床垫产品相关问题智能回答
- 自定义知识库问答，支持文档批量导入
- 多轮对话与上下文记忆
- 流式响应，接近真实客服交互体验
- 可快速部署为 Web 服务接入小程序 / 官网

## 技术栈

- 后端：Python + FastAPI
- 大模型框架：LangChain、LangGraph
- 向量数据库：Milvus
- 持久化数据库：Mysql
- 中间件：Redis缓存 ， Nacos配置中心
- 前端：Vue3 + Element Plus
- 部署：Docker、Gunicorn
- 日志：Loki

## 核心功能

1. **智能问答**

   基于用户问题自动匹配知识库内容，结合大模型生成精准、自然的回答。

   

2. **RAG 检索增强**

   对产品手册、常见问题进行向量化存储，提升回答专业性与准确性。

   

3. **多轮对话管理**

   支持上下文理解，可连续追问，对话历史自动记忆。

   

4. **问题路由与意图识别**

   自动识别用户意图（咨询、售后、投诉、预约等）并分流处理。

   

5. **流式输出**

   打字机式回复，提升用户体验。

   

## 项目结构

```
ai_customer_service/
├── api/          	 	 # 后端服务（api）
├── cache/        		 # 缓存工具
├── constants/            # 常量
├── core/       		 # 核心配置（数据库、异常、middleware）
├── dao/          		 # dao层
├── models/ 			#表模型 
├── rag/ 				#rag相关
├── schemas/ 
├── service/ 			#service层 
├── utils/ 				#工具类
└── main.py              # 项目入口
```

## 快速启动

### 1. 克隆项目

bash

运行

```
git clone https://github.com/old-jiang-ghb/ai_customer_service.git
cd ai_customer_service
```

### 2. 安装依赖

bash

运行

```
pip install -r requirements.txt
```

### 3. 配置模型与知识库

embedding模型：rag/embeddings/embedding.py

向量库：rag/vector_store/milvus_store.py

### 4. 启动服务

bash

运行

```
python main.py
```

## 使用场景

- 床垫品牌官网智能客服
- 电商店铺自动问答机器人
- 线下门店导购辅助系统
- 企业内部产品知识问答库

## 扩展能力

- 支持对接微信公众号、小程序
- 支持人工客服转接
- 支持用户评价、问题统计、数据分析

## 关于作者

GitHub：old-jiang-ghb

项目：AI 应用开发、大模型落地、RAG 企业级解决方案

## 页面展示

登录页面：

![image-20260401221116250](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20260401221116250.png)

首页：

![image-20260401221250467](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20260401221250467.png)

聊天界面：

![image-20260401221314570](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20260401221314570.png)

![image-20260401221554307](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20260401221554307.png)