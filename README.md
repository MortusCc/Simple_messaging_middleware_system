# 简易消息中间件系统

一个基于Flask和Python实现的简易消息中间件系统，采用发布-订阅（Publish-Subscribe）模式，支持主题管理、消息发布和订阅功能。

[![Stargazers over time](https://starchart.cc/MortusCc/Simple_messaging_middleware_system.svg?variant=adaptive)](https://starchart.cc/MortusCc/Simple_messaging_middleware_system)

[![GitHub issues](https://img.shields.io/github/issues/MortusCc/Simple_messaging_middleware_system.svg)](https://github.com/MortusCc/Simple_messaging_middleware_system/issues)
[![GitHub forks](https://img.shields.io/github/forks/MortusCc/Simple_messaging_middleware_system.svg)](https://github.com/MortusCc/Simple_messaging_middleware_system/network)
[![GitHub stars](https://img.shields.io/github/stars/MortusCc/Simple_messaging_middleware_system.svg)](https://github.com/MortusCc/Simple_messaging_middleware_system/stargazers)

## 项目简介

本项目实现了一个简易的消息中间件系统，模拟了真实世界中消息队列的工作原理。系统提供Web界面，用户可以通过图形界面创建主题、生产者和观察者（消费者），并实现消息的发布和订阅功能。

主要特性：
- 主题管理：创建和删除消息主题
- 生产者管理：创建消息生产者并发布消息到指定主题
- 观察者管理：创建观察者并订阅/取消订阅主题
- 实时消息传递：观察者可以实时接收订阅主题的消息
- 可视化界面：提供友好的Web界面进行操作和监控
- 配置文件支持：支持通过配置文件预设系统实体

## 项目结构

```
simple_mq/
├── app.py                 # Flask应用主文件，提供REST API接口
├── middleware_core.py     # 核心业务逻辑，实现发布-订阅模式
├── config.json           # 系统配置文件，包含预设的主题、生产者和观察者
├── templates/
│   └── index.html        # 前端界面文件
```

## 系统架构

系统基于观察者模式设计，包含以下核心组件：

1. **AbstractObserver（抽象观察者）**：定义观察者的基本接口
2. **AbstractSubject（抽象被观察者）**：定义主题的基本接口
3. **TopicSubject（具体主题）**：实现具体的消息主题逻辑
4. **MiddlewareCore（中间件核心）**：协调管理所有实体和消息传递

## 功能模块

### 1. 主题管理
- 创建主题
- 删除主题

### 2. 生产者管理
- 创建生产者
- 发布消息到指定主题

### 3. 观察者管理
- 创建观察者（消费者）
- 订阅/取消订阅主题
- 查看接收到的消息

### 4. 系统监控
- 实时查看消息日志
- 查看观察者接收到的消息

## 快速开始

### 环境要求
- Python 3.x
- Flask
- 其他依赖（根据实际需求安装）

### 安装和运行

1. 克隆或下载项目代码

2. 安装依赖（如果需要）
   ```
   pip install flask
   ```

3. 运行应用
   ```
   cd simple_mq
   python app.py
   ```
   
4. 在浏览器中访问
   ```
   http://127.0.0.1:5000 # 具体端口和网络接口可根据实际情况在app.py最后一行修改
   ```

### 使用说明

1. 打开浏览器访问 `http://127.0.0.1:5000`
2. 在界面中可以：
   - 创建主题（Topic）
   - 创建生产者（Producer）
   - 创建观察者（Observer）
   - 让观察者订阅或取消订阅主题
   - 通过生产者向主题发布消息
   - 实时查看消息传递日志和观察者接收到的消息

### 配置文件

系统提供 `config.json` 文件用于预设系统实体：
- `topics`: 预定义的主题列表
- `producers`: 预定义的生产者列表
- `observers`: 预定义的观察者列表
- `subscriptions`: 预定义的订阅关系

可以通过界面中的"加载配置"功能将这些预设实体加载到系统中。

## API接口

系统提供以下REST API接口：

- `POST /create_topic` - 创建主题
- `POST /delete_topic` - 删除主题
- `POST /create_producer` - 创建生产者
- `POST /publish_message` - 发布消息
- `POST /create_observer` - 创建观察者
- `POST /subscribe_topic` - 订阅主题
- `POST /unsubscribe_topic` - 取消订阅主题
- `POST /get_observer_messages` - 获取观察者消息
- `GET /get_message_logs` - 获取消息日志
- `GET /get_entities` - 获取所有实体信息
- `POST /load_config` - 加载配置文件

## 设计模式

项目采用了多种设计模式：

1. **观察者模式（Observer Pattern）**：实现消息的发布和订阅机制
2. **单例模式（Singleton Pattern）**：`MiddlewareCore`确保全局唯一实例
3. **抽象工厂模式**：通过抽象类定义接口规范

## 扩展建议

1. 添加消息持久化功能
2. 实现消息确认机制
3. 增加用户权限管理
4. 添加消息过滤和路由功能
5. 实现集群部署支持
