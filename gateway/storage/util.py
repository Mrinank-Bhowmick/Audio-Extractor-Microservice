import pika, json


def upload(file, gridfs_instance, rabbitmq_channel, access):
    try:
        file_id = gridfs_instance.put(file)
    except Exception as error:
        return f"Internal Server Error line 8 and {error}", 500

    message = {
        "video_fid": str(file_id),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        rabbitmq_channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            # We need to make sure that the message is persistent
            # that means it will be stored in the queue even if the server crashes
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as error:
        gridfs_instance.delete(file_id)
        # We need to delete the file from the database because it is not being processed
        return f"Internal Server Error util.py line 31 and {error}", 500
