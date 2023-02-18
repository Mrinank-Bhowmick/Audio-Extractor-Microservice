import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3


def main():
    username=os.environ.get("MONGO_USERNAME")
    password=os.environ.get("MONGO_PASSWORD")
    client = MongoClient(f"mongodb+srv://{username}:{password}@mongodb-cluster.hhz7bbb.mongodb.net/?retryWrites=true&w=majority")
    
    db_videos = client.videos
    db_mp3s = client.mp3s
    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # rabbitmq connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        error = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if error:
            ch.basic_nack(delivery_tag=method.delivery_tag) # negative Aknowledgement
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)