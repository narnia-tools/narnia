from abc import abstractmethod
from functools import wraps
import roslibpy
import inspect
import asyncio

import time

# Help
# https://stackoverflow.com/questions/3589311/get-defining-class-of-unbound-method-object-in-python-3/25959545#25959545

ROS_CLIENT = None
ROS_TOPICS = None
ROS_SERVICES = None

__ROS_LINKS__ = {
    'top_subs': {},
    'top_pubs': {},
    'services': {}
}

import atexit

loop = asyncio.get_event_loop()


def get_fn_name(fn):
    return fn.__name__


def get_fn_class_name(fn):
    module_name = inspect.getmodule(fn).__name__
    class_name = fn.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
    return module_name + '.' + class_name


def print_ros_topics():
    c_length = 60
    line = '+' + ''.join(['-' for _ in range(c_length * 2)]) + '+'
    print(line)
    print('|' + 'TOPICS:'.ljust(c_length) + 'MSG TYPE:'.ljust(c_length) + '|')
    print(line)

    for i in range(len(ROS_TOPICS['topics'])):
        print('|' + ROS_TOPICS['topics'][i].ljust(c_length) + ROS_TOPICS['types'][i].ljust(c_length) + '|')

    print(line)


def init_ros_client():
    global ROS_CLIENT, ROS_TOPICS, ROS_SERVICES
    if ROS_CLIENT is None:
        ROS_CLIENT = roslibpy.Ros(host='mani.local', port=9090)
        ROS_CLIENT.run()

        pull_topics_n_services()
    return ROS_CLIENT


def pull_topics_n_services():
    global ROS_TOPICS, ROS_SERVICES
    service_topics = roslibpy.Service(ROS_CLIENT, '/rosapi/topics', 'roscpp/GetLoggers')
    service_services = roslibpy.Service(ROS_CLIENT, '/rosapi/services', 'roscpp/GetLoggers')

    ROS_TOPICS = service_topics.call(roslibpy.ServiceRequest())
    ROS_SERVICES = service_services.call(roslibpy.ServiceRequest())


def register_topic_subscriber(obj, topic, msg_type, method_name):


    def fn(data):
        loop.call_soon_threadsafe(getattr(obj, method_name), data)
    roslibpy.Topic(obj.ros_client, topic, msg_type, queue_size=1).subscribe(fn)


def register_topic_publisher(obj, topic_name, msg_type, method_name):
    topic = roslibpy.Topic(obj.ros_client, topic_name, msg_type)

    pre_fn = getattr(obj, method_name)
    def fn(msg):
        new_msg = pre_fn(msg)
        new_msg = msg if new_msg is None else new_msg
        topic.publish(roslibpy.Message(new_msg))
        return new_msg
    setattr(obj, method_name, fn)


def register_service(obj, topic, msg_type, method_name):
    service = roslibpy.Service(obj.ros_client, topic, msg_type)

    def fn():
        request = roslibpy.ServiceRequest()
        return service.call(request)

    setattr(obj, method_name, fn)


def register_ros_links(obj):
    class_name = obj.__class__.__name__
    module_name = obj.__module__
    class_hash = module_name + '.' + class_name

    for kind in __ROS_LINKS__:
        if class_hash not in __ROS_LINKS__[kind]:
            continue

        methods = __ROS_LINKS__[kind][class_hash]

        for method_name in methods:
            params = methods[method_name]
            topic = params['topic']
            topic_idx = ROS_TOPICS['topics'].index(topic)
            msg_type = ROS_TOPICS['types'][topic_idx]


            if kind == 'top_subs':
                register_topic_subscriber(obj, topic, msg_type, method_name)
            elif kind == 'top_pubs':
                register_topic_publisher(obj, topic, msg_type, method_name)
            elif kind == 'services':
                register_service(obj, topic, msg_type, method_name)


class ROSActuator:

    def __init__(self):
        self.ros_client = init_ros_client()

        register_ros_links(self)







class ROSDecorator:
    def __init__(self, idx, topic, **kwargs):
        self.params = dict({'topic': topic}, **kwargs)
        self.idx = idx

    def __call__(self, fn):
        fn_name = get_fn_name(fn)
        class_name = get_fn_class_name(fn)
        if class_name not in self.idx:
            self.idx[class_name] = {}
        self.idx[class_name][fn_name] = self.params
        return fn


class ROSTopicSubscriber(ROSDecorator):
    def __init__(self, topic, **kwargs):
        super().__init__(__ROS_LINKS__['top_subs'], topic, **kwargs)


class ROSTopicPublisher(ROSDecorator):
    def __init__(self, topic, **kwargs):
        super().__init__(__ROS_LINKS__['top_pubs'], topic, **kwargs)


class ROSServiceSubscriber(ROSDecorator):
    def __init__(self, topic, **kwargs):
        super().__init__(__ROS_LINKS__['services'], topic, **kwargs)


init_ros_client()
