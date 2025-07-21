import pika, os, sys
from send import email

def main():
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )

    channel = conn.channel()

    def callback(ch, methods, properties, body):
        err = email.notify(body)
        if err:
            ch.basic_nack(delivery_tag=methods.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=methods.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("MP3_QUEUE"),
        on_message_callback=callback
    )

    print("Waiting fro messages. Print Ctrl + c to exit")

    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interupted")
        try:
            sys.exit(0)
        except:
            os._exit(0)
