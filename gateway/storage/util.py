import pika, json

import pika.spec

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as e:
        return "internal server error", 500
    
    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "user_id": access["sub"] 
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )

    except:
        fs.delete(fid)
        return "internal server error", 500