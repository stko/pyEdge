from multiprocessing.connection import wait
from operator import mod
import os
import sys
import pika
import time
import json
import uuid

class PyEdgeConnectException(Exception):
    pass


class PyEdge:
    '''
    Helper Class to cover the communication work inside a pyEdge rabbitMQ architecture network
    '''
    connections = {}

    def __init__(self,
                 module_queue,
                 host="exchange",
                 port=5672,
                 user="guest",
                 password="guest",
                 nr_of_trials=30,
                 wait_delay=1,
                 purge=False

                 ) -> None:
        self.module_queue = module_queue
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.nr_of_trials = nr_of_trials
        self.wait_delay = wait_delay
        self.handlers = {}
        self.responses={}
        if not host in self.connections:  # do we have already connected to that host before?
            connection = None
            while connection == None and nr_of_trials > 0:
                try:
                    print("host", host, nr_of_trials)
                    connection = pika.BlockingConnection(
                        pika.ConnectionParameters(host=host, port=port,  credentials=pika.PlainCredentials(user, password)))
                except Exception as ex:
                    print("catched connect exception", str(ex))
                    if nr_of_trials < 2:
                        raise PyEdgeConnectException
                    time.sleep(wait_delay)
                nr_of_trials -= 1
            channel = connection.channel()
        connection, channel = self.get_connection(
            host, port, user, password, nr_of_trials, wait_delay)

        channel.queue_declare(queue=module_queue)  # receiving queue
        channel.queue_declare("exchange")  # exchange communication
        if purge:
            channel.queue_purge(queue=module_queue)
            channel.queue_purge("exchange")
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=module_queue,
                              on_message_callback=self.message_handler)

        print(" [x] Awaiting RPC requests on ", module_queue)
        channel.basic_publish(exchange='',
                              routing_key='exchange',
                              body='Hello World!')

    def get_connection(self, host, port, user, password, nr_of_trials, wait_delay):
        if not host in self.connections:  # do we have already connected to that host before?
            connection = None
            while connection == None and nr_of_trials > 0:
                try:
                    print("host", host, nr_of_trials)
                    connection = pika.BlockingConnection(
                        pika.ConnectionParameters(host=host, port=port,  credentials=pika.PlainCredentials(user, password)))
                except Exception as ex:
                    print("catched connect exception", str(ex))
                    if nr_of_trials < 1:
                        raise PyEdgeConnectException
                    time.sleep(wait_delay)
                nr_of_trials -= 1
            channel = connection.channel()
            self.connections[host] = {
                "connection": connection, "channel": channel}
        return self.connections[host]["connection"], self.connections[host]["channel"]

    def close(self,host=None):
        for actual_host in self.connections:
            if host == None or host == actual_host:
                self.connections[actual_host]["connection"].close()
        if host == None: #remove all
            self.connections={}
        else:
            del self.connections[host]

    def send_status(self):
        self.event("", 'exchange', {"module": self.module_queue})

    def event(self, duni, module, type, data,
              port=None,
              user=None,
              password=None,
              nr_of_trials=None,
              wait_delay=None
              ):
        if not port:
            port=self.port
        if not user:
                user=self.user
        if not password:
                password=self.password
        if not nr_of_trials:
                nr_of_trials=self.nr_of_trials
        if not wait_delay:
                wait_delay=self.wait_delay
        self._send_message(duni, module, {"type": type, "data": data},port=port,user=user,password=password,nr_of_trials=nr_of_trials,wait_delay=wait_delay)

    def request(self, module, type, data, 
              host=None,
              port=None,
              user=None,
              password=None,
              nr_of_trials=None,
              wait_delay=None
              ):
        if not host:
            host=self.host
        if not port:
            port=self.port
        if not user:
                user=self.user
        if not password:
                password=self.password
        if not nr_of_trials:
                nr_of_trials=self.nr_of_trials
        if not wait_delay:
                wait_delay=self.wait_delay
        connection, channel = self.get_connection(
            host, port, user, password, nr_of_trials, wait_delay)
        channel=connection.channel() # create a temporary channel

        result = channel.queue_declare(queue='', exclusive=True)
        callback_queue = result.method.queue

        channel.basic_consume(
            queue=callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        corr_id = str(uuid.uuid4())
        channel.basic_publish(
            exchange="",
            routing_key=module,
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=corr_id,
            ),
            body=json.dumps({"type":type,"rpc":True,"data":data})
        )
        self.responses[corr_id]=""
        connection.process_data_events(time_limit=None)
        result="Nöö"
        if corr_id in self.responses:
            result=self.responses[corr_id]
            del self.responses[corr_id]
        return result


    
    def on_response(self, ch, method, props, body):
        corr_id=props.correlation_id
        if corr_id in self.responses:
            self.responses[corr_id]=body



    def _send_message(self, exchange, module, message,host, port, user, password, nr_of_trials, wait_delay):
        connection, channel = self.get_connection(
            host, port, user, password, nr_of_trials, wait_delay)
        channel.basic_publish(exchange=exchange,
                                   routing_key=module,
                                   body=json.dumps(message))

    def runforever(self):
        connection, channel = self.get_connection(
            self.host, self.port, self.user, self.password, self.nr_of_trials, self.wait_delay)
        channel.start_consuming()

    def add_handler(self, msg_type, handler):
        if not msg_type:
            self.handlers = {}  # if msg_type is None or "", clear all handlers
        if msg_type == None:
            return  # nothing else to do
        if msg_type != "":
            # if we have a named type, then we can't use the unique handler anymore, so we remove him
            del self.handlers[""]
        self.handlers[msg_type] = handler  # store the handler

    def message_handler(self, ch, method, props, body):
        try:
            message = json.loads(body)
            msg_type = message["type"]
            if "" in self.handlers:
                result = self.handlers[""](message["data"])
            else:
                result = self.handlers[msg_type](message["data"])
            # if rpc is set then it is a remote call and not just an event
            if "rpc" in message and message["rpc"]:

                ch.basic_publish(exchange='',
                                 routing_key=props.reply_to,
                                 properties=pika.BasicProperties(
                                     correlation_id=props.correlation_id),
                                 body=json.dumps(result))
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as ex:
            print("malformed message structure received:", body, str(ex))
            if "rpc" in message and message["rpc"]:
                ch.basic_publish(exchange='',
                                 routing_key=props.reply_to,
                                 properties=pika.BasicProperties(
                                     correlation_id=props.correlation_id),
                                 body=json.dumps({"type":"exception", "msg":str(ex)}))
                ch.basic_ack(delivery_tag=method.delivery_tag)
