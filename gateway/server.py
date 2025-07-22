import os
import json
import pika
import gridfs
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from auth import validate
from auth_svc import access
from storage import util

app = Flask(__name__)

# Use proper env variable escaping inside f-strings
root_user = os.environ.get("MONGODB_ROOT_USER")
root_pass = os.environ.get("MONGODB_ROOT_PASS")

app.config["MONGO_URI_VIDEOS"] = f"mongodb://{root_user}:{root_pass}@mongodb-service:27017/videos"
app.config["MONGO_URI_MP3"] = f"mongodb://{root_user}:{root_pass}@mongodb-service:27017/mp3s"

mongo_videos = PyMongo(app, uri=app.config["MONGO_URI_VIDEOS"])
fs_videos = gridfs.GridFS(mongo_videos.db)

mongo_mp3 = PyMongo(app, uri=app.config["MONGO_URI_MP3"])
fs_mp3 = gridfs.GridFS(mongo_mp3.db)

# RabbitMQ setup
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@app.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    return token if not err else err

@app.route("/upload", methods=["POST"])
def upload():
    user_access, err = validate.token(request)
    if err:
        return err

    access_json = json.loads(user_access)

    if len(request.files) != 1:
        return jsonify({"error": "Exactly one file must be uploaded."}), 403

    try:
        file = next(iter(request.files.values()))
        upload_err = util.upload(file, fs_videos, channel, access_json)
        if upload_err:
            return upload_err
        return jsonify({"success": True}), 200
    except Exception as e:
        app.logger.error(f"Upload failed: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/download", methods=["GET"])
def download():
    try:
        user_access, err = validate.token(request)
        if err:
            return err

        access_json = json.loads(user_access)

        fid_string = request.args.get('fid')
        if not fid_string:
            return jsonify({"error": "fid is required"}), 400

        try:
            fid = ObjectId(fid_string)
        except Exception:
            return jsonify({"error": "Invalid fid"}), 400

        grid_out = fs_mp3.find_one({"_id": fid})
        if not grid_out:
            return jsonify({"error": "File not found"}), 404

        return send_file(
            grid_out,
            as_attachment=True,
            download_name=f"{secure_filename(fid_string)}.mp3",
            mimetype="audio/mpeg"
        )

    except Exception as e:
        app.logger.error(f"Download failed: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
