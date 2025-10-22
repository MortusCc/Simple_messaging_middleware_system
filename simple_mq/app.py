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

# 6. 新增：获取所有实体信息接口（用于前端下拉选择）
@app.route('/get_entities', methods=['GET'])
def get_entities():
    entities = middleware.get_all_entities()
    return jsonify(entities)

# 7. 新增：加载配置文件接口
@app.route('/load_config', methods=['POST'])
def load_config():
    success, msg = middleware.load_config()
    # 重新加载实体信息
    entities = middleware.get_all_entities()
    return jsonify({"success": success, "msg": msg, "entities": entities})

# 8. 新增：保存配置文件接口
@app.route('/save_config', methods=['POST'])
def save_config():
    success, msg = middleware.save_config()
    return jsonify({"success": success, "msg": msg})

# 9. 新增：获取观察者的订阅信息
@app.route('/get_observer_subscriptions', methods=['POST'])
def get_observer_subscriptions():
    data = request.json
    observer_id = data.get('observer_id')
    observer = middleware.observers.get(observer_id)
    if not observer:
        return jsonify({"subscriptions": []})
    return jsonify({"subscriptions": observer.subscribed_topics})

# 10. 吞吐率测试接口（改进版）
@app.route('/test_throughput', methods=['GET'])
def test_throughput():
    # 获取测试参数
    test_duration = int(request.args.get('duration', 60))  # 测试时长，默认60秒
    message_size = int(request.args.get('size', 1024))     # 消息大小，默认1KB
    producer_count = int(request.args.get('producers', 5)) # 生产者数量，默认5个
    
    # 准备：创建主题、生产者、观察者
    topic_name = "throughput_test_topic"
    middleware.create_topic(topic_name)
    observers = []
    
    # 创建多个观察者以避免成为瓶颈
    for i in range(3):
        observer_id = f"test_observer_{i}"
        middleware.create_observer(observer_id)
        middleware.observer_subscribe_topic(observer_id, topic_name)
        observers.append(observer_id)
    
    producers = []
    for i in range(producer_count):
        producer_id = f"test_producer_{i}"
        middleware.create_producer(producer_id)
        producers.append(producer_id)
    
    message_count = 0  # 消息计数器
    start_time = time.time()
    end_time = start_time + test_duration
    
    # 定义生产者线程函数：持续发布消息
    def produce_messages(producer_id):
        nonlocal message_count
        producer = middleware.producers[producer_id]
        while time.time() < end_time:
            # 发布指定大小的消息
            message_content = "a" * message_size
            success, _ = producer.publish_message(middleware, topic_name, message_content)
            if success:
                message_count += 1
            # 短暂休眠以控制发送速率
            time.sleep(0.0001)
    
    # 启动生产者线程（模拟并发）
    threads = []
    for producer_id in producers:
        t = threading.Thread(target=produce_messages, args=(producer_id,))
        t.start()
        threads.append(t)
    
    # 等待所有线程结束
    for t in threads:
        t.join()
    
    # 计算吞吐率
    actual_duration = time.time() - start_time
    throughput = message_count / actual_duration  # 消息/秒
    
    # 清理测试数据
    middleware.delete_topic(topic_name)
    for producer_id in producers:
        if producer_id in middleware.producers:
            del middleware.producers[producer_id]
    for observer_id in observers:
        if observer_id in middleware.observers:
            del middleware.observers[observer_id]
    
    return jsonify({
        "test_duration": actual_duration,  # 实际测试时长（秒）
        "total_messages": message_count,
        "message_size": message_size,      # 消息大小（字节）
        "producer_count": producer_count,  # 生产者数量
        "throughput_msg_per_sec": f"{throughput:.2f} 条/秒",
        "throughput_kb_per_sec": f"{throughput * message_size / 1024:.2f} KB/秒"
    })

# 11. 基准测试接口（多种消息大小）- 改进版
@app.route('/benchmark', methods=['GET'])
def benchmark():
    message_sizes = [100, 1024, 10240]  # 移除100KB测试，避免性能问题
    results = []
    
    for size in message_sizes:
        try:
            # 调用吞吐率测试接口
            test_duration = 15  # 缩短测试时间到15秒，避免长时间阻塞
            producer_count = 2  # 减少生产者数量
            
            # 准备测试
            topic_name = f"benchmark_topic_{size}"
            middleware.create_topic(topic_name)
            
            observers = []
            for i in range(2):
                observer_id = f"benchmark_observer_{i}_{size}"
                middleware.create_observer(observer_id)
                middleware.observer_subscribe_topic(observer_id, topic_name)
                observers.append(observer_id)
            
            producers = []
            for i in range(producer_count):
                producer_id = f"benchmark_producer_{i}_{size}"
                middleware.create_producer(producer_id)
                producers.append(producer_id)
            
            message_count = 0
            start_time = time.time()
            end_time = start_time + test_duration
            
            def produce_messages(producer_id):
                nonlocal message_count
                producer = middleware.producers[producer_id]
                while time.time() < end_time:
                    # 对于大消息，我们使用更有效的方式生成
                    if size <= 1000:
                        message_content = "b" * size
                    else:
                        # 对于大消息，我们使用更节省内存的方式
                        message_content = "b" * 1000 + "..." + "b" * (size - 1003) if size > 1003 else "b" * size
                    
                    success, _ = producer.publish_message(middleware, topic_name, message_content)
                    if success:
                        message_count += 1
                    # 根据消息大小调整休眠时间，避免系统过载
                    sleep_time = min(0.001 * (size / 1024), 0.1)  # 最大休眠0.1秒
                    time.sleep(sleep_time)
            
            threads = []
            for producer_id in producers:
                t = threading.Thread(target=produce_messages, args=(producer_id,))
                t.start()
                threads.append(t)
            
            # 等待所有线程结束，设置超时避免无限等待
            for t in threads:
                t.join(timeout=20)  # 20秒超时
            
            actual_duration = time.time() - start_time
            throughput = message_count / actual_duration if actual_duration > 0 else 0
            
            results.append({
                "message_size": size,
                "total_messages": message_count,
                "duration": actual_duration,
                "throughput_msg_per_sec": throughput,
                "throughput_kb_per_sec": throughput * size / 1024
            })
            
            # 清理
            middleware.delete_topic(topic_name)
            for producer_id in producers:
                if producer_id in middleware.producers:
                    del middleware.producers[producer_id]
            for observer_id in observers:
                if observer_id in middleware.observers:
                    del middleware.observers[observer_id]
                    
        except Exception as e:
            # 如果某个测试出现异常，记录错误并继续下一个测试
            results.append({
                "message_size": size,
                "error": str(e)
            })
            continue
    
    # 正确返回测试结果
    formatted_results = []
    for result in results:
        if "error" in result:
            formatted_results.append(result)
        else:
            formatted_results.append({
                "message_size": result["message_size"],
                "total_messages": result["total_messages"],
                "duration": round(result["duration"], 2),
                "throughput_msg_per_sec": round(result["throughput_msg_per_sec"], 2),
                "throughput_kb_per_sec": round(result["throughput_kb_per_sec"], 2)
            })
    
    return jsonify({
        "test_type": "benchmark",
        "results": formatted_results
    })

if __name__ == '__main__':
    app.run(debug=True)