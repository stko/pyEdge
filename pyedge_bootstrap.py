#!/usr/bin/env python
import pika
import uuid
import json
import argparse


class PyeBootstrap:

    def __init__(self,host,port,user,password):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(user, password)))

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

    def get_config(self,duni_id):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='bootstrap',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                content_type="application/json"
            ),
            body=json.dumps({
                "duni_id":duni_id
            }))
        self.connection.process_data_events(time_limit=None)
        return self.response.decode()
    def close(self):
        if self.connection:
             self.connection.close()


parser=argparse.ArgumentParser()
parser.add_argument("--host",help="the RabbitMQ Exchange Server", default="localhost")
parser.add_argument("--port",help="the Server Port", default=5672, type=int)
parser.add_argument("--user",help="the Server User Name", default="guest")
parser.add_argument("--password",help="the Server Password", default="guest")
parser.add_argument("--duniid",help="the Duni ID (for debugging only)", default=hex(uuid.getnode()).upper())
args=parser.parse_args()



bootstrap = PyeBootstrap(args.host,args.port,args.user,args.password)

print(" try to get initial config")
response = bootstrap.get_config(args.duniid)
print(" [.] Got %s" % response)
bootstrap.close()
