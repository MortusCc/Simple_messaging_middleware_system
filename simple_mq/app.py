# app.py
from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS
from middleware_core import MiddlewareCore
import time
import threading

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
# 初始化中间件协调器（全局唯一，确保所有请求共享同一中间件实例）
middleware = MiddlewareCore()

# 1. 首页：渲染网页界面
@app.route('/')
def index():
    return render_template('index.html')  # index.html放在templates文件夹下

# 2. 主题管理接口
@app.route('/create_topic', methods=['POST'])
def create_topic():
    data = request.json
    topic_name = data.get('topic_name')
    success, msg = middleware.create_topic(topic_name)
    return jsonify({"success": success, "msg": msg})

@app.route('/delete_topic', methods=['POST'])
def delete_topic():
    data = request.json
    topic_name = data.get('topic_name')
    success, msg = middleware.delete_topic(topic_name)
    return jsonify({"success": success, "msg": msg})

# 3. 生产者接口
@app.route('/create_producer', methods=['POST'])
def create_producer():
    data = request.json
    producer_id = data.get('producer_id')
    success, msg = middleware.create_producer(producer_id)
    return jsonify({"success": success, "msg": msg})

@app.route('/publish_message', methods=['POST'])
def publish_message():
    data = request.json
    producer_id = data.get('producer_id')
    topic_name = data.get('topic_name')
    message_content = data.get('message_content')
    # 检查生产者是否存在
    if producer_id not in middleware.producers:
        return jsonify({"success": False, "msg": f"生产者{producer_id}不存在，请先创建"})
    # 调用生产者的发布方法
    producer = middleware.producers[producer_id]
    success, msg = producer.publish_message(middleware, topic_name, message_content)
    return jsonify({"success": success, "msg": msg})

# 4. 观察者接口
@app.route('/create_observer', methods=['POST'])
def create_observer():
    data = request.json
    observer_id = data.get('observer_id')
    success, msg = middleware.create_observer(observer_id)
    return jsonify({"success": success, "msg": msg})

@app.route('/subscribe_topic', methods=['POST'])
def subscribe_topic():
    data = request.json
    observer_id = data.get('observer_id')
    topic_name = data.get('topic_name')
    success, msg = middleware.observer_subscribe_topic(observer_id, topic_name)
    return jsonify({"success": success, "msg": msg})

@app.route('/unsubscribe_topic', methods=['POST'])
def unsubscribe_topic():
    data = request.json
    observer_id = data.get('observer_id')
    topic_name = data.get('topic_name')
    success, msg = middleware.observer_unsubscribe_topic(observer_id, topic_name)
    return jsonify({"success": success, "msg": msg})

# 5. 数据展示接口（供前端实时刷新）
@app.route('/get_observer_messages', methods=['POST'])
def get_observer_messages():
    data = request.json
    observer_id = data.get('observer_id')
    messages = middleware.get_observer_messages(observer_id)
    return jsonify({"messages": messages})

@app.route('/get_message_logs', methods=['GET'])
def get_message_logs():
    logs = middleware.get_message_logs()
    return jsonify({"logs": logs})

# 6. 吞吐率测试接口
@app.route('/test_throughput', methods=['GET'])
def test_throughput():
    # 准备：创建主题、生产者、观察者
    topic_name = "test_topic"
    middleware.create_topic(topic_name)
    producer_id = "test_producer"
    middleware.create_producer(producer_id)
    observer_id = "test_observer"
    middleware.create_observer(observer_id)
    middleware.observer_subscribe_topic(observer_id, topic_name)
    
    producer = middleware.producers[producer_id]
    message_count = 0  # 消息计数器
    start_time = time.time()
    end_time = start_time + 60  # 测试时长：60秒
    
    # 定义生产者线程函数：持续发布消息
    def produce_messages():
        nonlocal message_count
        while time.time() < end_time:
            # 发布1KB消息（约1024个字符）
            message_content = "a" * 1024
            success, _ = producer.publish_message(middleware, topic_name, message_content)
            if success:
                message_count += 1
            # 避免CPU占用过高，轻微延时
            time.sleep(0.001)
    
    # 启动5个生产者线程（模拟并发）
    threads = []
    for _ in range(5):
        t = threading.Thread(target=produce_messages)
        t.start()
        threads.append(t)
    
    # 等待所有线程结束
    for t in threads:
        t.join()
    
    # 计算吞吐率
    throughput = message_count / 60 # 60秒内的总消息数
    # 清理测试数据
    middleware.delete_topic(topic_name)
    del middleware.producers[producer_id]
    del middleware.observers[observer_id]
    
    return jsonify({
        "test_duration": 60,  # 测试时长（秒）
        "total_messages": message_count,
        "throughput": f"{throughput:.2f}条/分钟"
    })

if __name__ == '__main__':
    app.run(debug=True)
