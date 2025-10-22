# middleware_core.py
import json
import os
from abc import ABCMeta, abstractmethod
import datetime

# 抽象观察者：定义消息接收接口
class AbstractObserver(metaclass=ABCMeta):
    def __init__(self, observer_id):
        self.observer_id = observer_id  # 观察者唯一ID（用于网页标识）
        self.subscribed_topics = []     # 订阅的主题列表
        self.received_messages = []     # 接收的消息列表（用于网页展示）
    
    @abstractmethod
    def update(self, message, topic_name):
        """接收被观察者（主题）的消息并处理"""
        pass

# 抽象被观察者：定义观察者管理与通知接口
class AbstractSubject(metaclass=ABCMeta):
    def __init__(self, topic_name):
        self.topic_name = topic_name          # 主题名称（唯一）
        self.observers = []                   # 订阅当前主题的观察者列表
    
    @abstractmethod
    def register_observer(self, observer):
        """注册观察者（观察者订阅主题）"""
        pass
    
    @abstractmethod
    def remove_observer(self, observer):
        """移除观察者（观察者取消订阅）"""
        pass
    
    @abstractmethod
    def notify_observers(self, message):
        """通知所有观察者接收消息"""
        pass
    
    @abstractmethod
    def receive_message(self, message):
        """接收生产者的消息，触发通知逻辑"""
        pass

# 具体被观察者：消息主题
class TopicSubject(AbstractSubject):
    def register_observer(self, observer):
        """注册观察者：若观察者未订阅该主题，则添加到列表"""
        if observer not in self.observers and self.topic_name not in observer.subscribed_topics:
            self.observers.append(observer)
            observer.subscribed_topics.append(self.topic_name)
    
    def remove_observer(self, observer):
        """移除观察者：若观察者已订阅该主题，则从列表中删除"""
        if observer in self.observers and self.topic_name in observer.subscribed_topics:
            self.observers.remove(observer)
            observer.subscribed_topics.remove(self.topic_name)
    
    def notify_observers(self, message):
        """通知所有观察者：调用每个观察者的update()方法传递消息"""
        for observer in self.observers:
            observer.update(message, self.topic_name)
    
    def receive_message(self, message):
        """接收生产者消息后，触发通知逻辑"""
        self.notify_observers(message)

# 具体观察者：消息消费者
class ConsumerObserver(AbstractObserver):
    def update(self, message, topic_name):
        """处理消息：将消息添加到个人消息列表（用于网页展示）"""
        message_info = f"[主题：{topic_name}] {message}"
        self.received_messages.append(message_info)

# 生产者：消息发布者
class MessageProducer:
    def __init__(self, producer_id):
        self.producer_id = producer_id  # 生产者唯一ID（用于网页标识）
    
    def publish_message(self, middleware_core, topic_name, message_content):
        """发布消息：通过中间件协调器找到主题，传递消息"""
        # 1. 从中间件协调器获取主题
        topic = middleware_core.get_topic(topic_name)
        if not topic:
            return False, f"主题「{topic_name}」不存在，请先创建主题"
        # 2. 构造完整消息（包含生产者ID和时间）
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        full_message = f"[生产者{self.producer_id}][{current_time}] {message_content}"
        # 3. 向主题发送消息
        topic.receive_message(full_message)
        # 4. 记录消息日志到中间件协调器
        middleware_core.add_message_log(f"生产者{self.producer_id}向主题「{topic_name}」发布消息：{message_content}")
        return True, f"消息发布成功：{full_message}"

class MiddlewareCore:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file    # 配置文件路径
        self.topics = {}                  # 主题字典：key=主题名称，value=TopicSubject实例
        self.producers = {}               # 生产者字典：key=生产者ID，value=MessageProducer实例
        self.observers = {}               # 观察者字典：key=观察者ID，value=ConsumerObserver实例
        self.message_logs = []            # 消息日志列表（用于网页展示全流程）
        # 注意：不再自动加载配置文件，需要用户手动点击加载按钮
        
    # 主题管理
    def create_topic(self, topic_name):
        """创建主题：若主题不存在则新建"""
        if topic_name not in self.topics:
            self.topics[topic_name] = TopicSubject(topic_name)
            self.add_message_log(f"创建主题：「{topic_name}」")
            return True, f"主题「{topic_name}」创建成功"
        return False, f"主题「{topic_name}」已存在"
    
    def delete_topic(self, topic_name):
        """删除主题：若主题存在则删除，同时取消所有观察者的订阅"""
        if topic_name in self.topics:
            topic = self.topics.pop(topic_name)
            # 取消该主题的所有观察者订阅
            for observer in list(topic.observers):  # 使用list()避免在迭代时修改列表
                topic.remove_observer(observer)
            self.add_message_log(f"删除主题：「{topic_name}」")
            return True, f"主题「{topic_name}」删除成功"
        return False, f"主题「{topic_name}」不存在"
    
    def get_topic(self, topic_name):
        """获取主题实例"""
        return self.topics.get(topic_name)
    
    # 生产者管理
    def create_producer(self, producer_id):
        """创建生产者：若生产者ID不存在则新建"""
        if producer_id not in self.producers:
            self.producers[producer_id] = MessageProducer(producer_id)
            self.add_message_log(f"创建生产者：生产者{producer_id}")
            return True, f"生产者{producer_id}创建成功"
        return False, f"生产者{producer_id}已存在"
    
    # 观察者管理
    def create_observer(self, observer_id):
        """创建观察者：若观察者ID不存在则新建"""
        if observer_id not in self.observers:
            self.observers[observer_id] = ConsumerObserver(observer_id)
            self.add_message_log(f"创建观察者：观察者{observer_id}")
            return True, f"观察者{observer_id}创建成功"
        return False, f"观察者{observer_id}已存在"
    
    def observer_subscribe_topic(self, observer_id, topic_name):
        """观察者订阅主题：找到观察者和主题，调用主题的注册方法"""
        observer = self.observers.get(observer_id)
        topic = self.topics.get(topic_name)
        if not observer:
            return False, f"观察者{observer_id}不存在，请先创建观察者"
        if not topic:
            return False, f"主题「{topic_name}」不存在，请先创建主题"
        # 调用主题的注册方法
        topic.register_observer(observer)
        self.add_message_log(f"观察者{observer_id}订阅主题「{topic_name}」")
        return True, f"观察者{observer_id}订阅主题「{topic_name}」成功"
    
    def observer_unsubscribe_topic(self, observer_id, topic_name):
        """观察者取消订阅主题：找到观察者和主题，调用主题的移除方法"""
        observer = self.observers.get(observer_id)
        topic = self.topics.get(topic_name)
        if not observer or not topic:
            return False, "观察者或主题不存在"
        # 调用主题的移除方法
        topic.remove_observer(observer)
        self.add_message_log(f"观察者{observer_id}取消订阅主题「{topic_name}」")
        return True, f"观察者{observer_id}取消订阅主题「{topic_name}」成功"
    
    # 消息日志管理
    def add_message_log(self, log_content):
        """添加消息日志（包含时间）"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        full_log = f"[{current_time}] {log_content}"
        self.message_logs.append(full_log)
        # 限制日志数量（仅保留最近100条，避免内存溢出）
        if len(self.message_logs) > 100:
            self.message_logs.pop(0)
    
    def get_message_logs(self):
        """获取所有消息日志（用于网页展示）"""
        return self.message_logs
    
    # 观察者消息获取（用于网页展示）
    def get_observer_messages(self, observer_id):
        """获取指定观察者接收的消息"""
        observer = self.observers.get(observer_id)
        if not observer:
            return []
        return observer.received_messages
    
    # 配置文件管理
    def save_config(self):
        """保存当前状态到配置文件"""
        # 构建订阅关系
        subscriptions = {}
        for observer_id, observer in self.observers.items():
            if observer.subscribed_topics:
                subscriptions[observer_id] = observer.subscribed_topics
        
        config = {
            'topics': list(self.topics.keys()),
            'producers': list(self.producers.keys()),
            'observers': list(self.observers.keys()),
            'subscriptions': subscriptions
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.add_message_log("配置已保存到文件")
            return True, "配置保存成功"
        except Exception as e:
            error_msg = f"保存配置文件失败：{str(e)}"
            self.add_message_log(error_msg)
            return False, error_msg
    
    def load_config(self):
        """从配置文件加载预设配置"""
        if not os.path.exists(self.config_file):
            msg = "配置文件不存在"
            self.add_message_log(msg)
            return False, msg
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 清除现有数据
            self._clear_all_entities()
            
            # 加载预设主题
            topics = config.get('topics', [])
            for topic_name in topics:
                if topic_name not in self.topics:
                    self.topics[topic_name] = TopicSubject(topic_name)
                    self.add_message_log(f"从配置文件加载主题：「{topic_name}」")
            
            # 加载预设生产者
            producers = config.get('producers', [])
            for producer_id in producers:
                if producer_id not in self.producers:
                    self.producers[producer_id] = MessageProducer(producer_id)
                    self.add_message_log(f"从配置文件加载生产者：生产者{producer_id}")
            
            # 加载预设观察者
            observers = config.get('observers', [])
            for observer_id in observers:
                if observer_id not in self.observers:
                    self.observers[observer_id] = ConsumerObserver(observer_id)
                    self.add_message_log(f"从配置文件加载观察者：观察者{observer_id}")
            
            # 加载订阅关系
            subscriptions = config.get('subscriptions', {})
            for observer_id, topic_list in subscriptions.items():
                if observer_id in self.observers:
                    observer = self.observers[observer_id]
                    for topic_name in topic_list:
                        if topic_name in self.topics:
                            topic = self.topics[topic_name]
                            # 检查是否已经订阅
                            if topic_name not in observer.subscribed_topics:
                                topic.register_observer(observer)
                                self.add_message_log(f"从配置文件加载订阅关系：观察者{observer_id}订阅主题「{topic_name}」")
            
            msg = "配置加载成功"
            self.add_message_log(msg)
            return True, msg
        except Exception as e:
            error_msg = f"加载配置文件失败：{str(e)}"
            self.add_message_log(error_msg)
            return False, error_msg
    
    def _clear_all_entities(self):
        """清除所有实体"""
        # 清除主题（需要先取消所有订阅关系）
        for topic_name, topic in self.topics.items():
            # 取消所有观察者的订阅
            for observer in list(topic.observers):
                topic.remove_observer(observer)
        
        # 清空所有字典
        self.topics.clear()
        self.producers.clear()
        self.observers.clear()
        
        self.add_message_log("已清除所有现有实体")
    
    def get_all_entities(self):
        """获取所有实体信息用于前端下拉选择"""
        # 获取订阅关系
        subscriptions = {}
        for observer_id, observer in self.observers.items():
            subscriptions[observer_id] = observer.subscribed_topics
        
        return {
            'topics': list(self.topics.keys()),
            'producers': list(self.producers.keys()),
            'observers': list(self.observers.keys()),
            'subscriptions': subscriptions
        }