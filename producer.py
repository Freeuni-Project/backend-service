import json
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='stat_queue', durable=True)


def publish(method, body):
    properties = pika.BasicProperties(method, delivery_mode=2)

    channel.basic_publish(exchange='', routing_key='stat_queue', body=json.dumps(body), properties=properties)

