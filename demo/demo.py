#!/usr/bin/env python
import os
import sys
import pika
import time

module_name = os.getenv("MODULE_NAME")
module_index = os.getenv("MODULE_INDEX")
module_queue = '.'.join([module_name, module_index])
duni_id = os.getenv("DUNI_ID")
# helpful for debugging to set another exchange
host = os.getenv("DUNI_HOST") or 'exchange'
# if not host:
#    host= 'exchange'
connection = None
nr_of_trials = 30
while connection == None and nr_of_trials > 0:
    try:
        print("host", host, nr_of_trials)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host,  credentials=pika.PlainCredentials(os.getenv("RABBITMQ_DEFAULT_USER"), os.getenv("RABBITMQ_DEFAULT_PASS"))))
    except Exception as ex:
        print("catched connect exception", str(ex))
        if nr_of_trials < 1:
            sys.exit(1)
        time.sleep(1)
    nr_of_trials -= 1

channel = connection.channel()

channel.queue_declare(queue=module_queue)  # receivinf queue
channel.queue_declare("exchange")  # exchange communication


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def on_request(ch, method, props, body):
    n = int(body)

    print(" [.] fib(%s)" % n)
    response = fib(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(
                         correlation_id=props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=module_queue, on_message_callback=on_request)

print(" [x] Awaiting RPC requests on ", module_queue)
channel.basic_publish(exchange='',
                      routing_key='exchange',
                      body='Hello World!')
channel.start_consuming()
