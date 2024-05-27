import json
import uuid
from datetime import datetime
from bson import json_util
from data_flow.mq import RabbitMQConnection


client = RabbitMQConnection()
client.connect()

def send_queue_message() -> None:
    mq_connection = RabbitMQConnection()
    mq_connection.connect()

    full_document = {
        "type": "articles",
        "entry_id": str(uuid.uuid4()),
        "source": "medium",
        "title": "moon soon",
        "summary": "no lambo yet",
        "content": "wait pantiently",
        "published_at": datetime.now().strftime(format="%Y-%m-%d")
    }

    data = json.dumps(full_document, default=json_util.default)
    mq_connection.publish_message(data=data, queue="articles_queue")

def clean_queue() -> None:
    channel = client.get_channel()
    channel.queue_purge("articles_queue")
    print("Collection cleaned")


if __name__ == "__main__":
    FORCE_CLEAN = True

    if FORCE_CLEAN:
        clean_queue()

    send_queue_message()
