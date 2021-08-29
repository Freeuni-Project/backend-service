import json
import pika


def publish(method, body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='stat_queue', durable=True)
    properties = pika.BasicProperties(method, delivery_mode=2)

    channel.basic_publish(exchange='', routing_key='stat_queue', body=json.dumps(body), properties=properties)
    connection.close()
