#!/usr/bin/env python

import os, sys
import pika
import uuid
import json
from pyedge import PyEdge


class FibonacciRpcClient(object):

    def __init__(self):
        user =os.getenv("RABBITMQ_DEFAULT_USER") or "myuser"
        password= os.getenv("RABBITMQ_DEFAULT_PASS") or "mypassword"
        # helpful for debugging to set another exchange
        host = sys.argv[1]
        pe=PyEdge(
            "rpcclient.1",
            host=host,
            user=user,
            password=password
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host,  credentials=pika.PlainCredentials(user, password)))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='demo.1',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps({"type":"egal","rpc":True,"data":str(n)})
        )
        self.connection.process_data_events(time_limit=None)
        return int(self.response)


fibonacci_rpc = FibonacciRpcClient()

print(" [x] Requesting fib(5)")
response = fibonacci_rpc.call(5)
print(" [.] Got %r" % response)

