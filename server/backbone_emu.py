#!/usr/bin/env python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port= 5673,credentials=pika.PlainCredentials("myuser", "mypassword")))

channel = connection.channel()

channel.queue_declare(queue='bootstrap')


def on_request(ch, method, props, body):
    try:
        data=json.loads(body)
        duni_id=data["duni_id"]

        print("duni_id",duni_id)
        response = {
            "repositories" : [
                {
            "docker_rep_url" : "localhost",
            "docker_rep_user" : "user",
            "docker_rep_password" : "password",
                }
            ],
            "docker-compose":'''
version: "3.9"
services:
  pythonbuilder:
    container_name: "pythonbuilder"
    image: "pythonbuilder"
    build: ./pythonbuilder
  exchange:
    container_name: "exchange"
    # image: rabbitmq-management-with-federation
    image: rabbitmq-management
    build: ./exchange
    #build:
    #  context: .
    #  dockerfile: ./Dockerfile
    ports:
      # HTTP management UI
      - '8080:15672'
      # AMQP protocol port
      - '5672:5672'
    environment:
    - RABBITMQ_DEFAULT_USER=myuser
    - RABBITMQ_DEFAULT_PASS=mypassword
  demo:
    container_name: demo
    build: ./demo
    environment:
    - RABBITMQ_DEFAULT_USER=myuser
    - RABBITMQ_DEFAULT_PASS=mypassword
    #- DUNI_HOST=192.168.1.116
 
    depends_on:
    - "exchange"
    - "pythonbuilder"
  can_demo:
    container_name: can_demo
    build: ./can_demo
    environment:
    - RABBITMQ_DEFAULT_USER=myuser
    - RABBITMQ_DEFAULT_PASS=mypassword
    #- DUNI_HOST=192.168.1.116
 
    depends_on:
    - "exchange"
    - "pythonbuilder"
        '''}

        ch.basic_publish(exchange='',
                        routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id = \
                                                            props.correlation_id),
                        body=json.dumps(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as ex:
        print(str(ex))


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='bootstrap', on_message_callback=on_request)

print(" Awaiting RPC requests")
channel.start_consuming()

