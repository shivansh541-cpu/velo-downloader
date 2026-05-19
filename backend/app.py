from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
import threading
import time

from downloader import get_video_info, download_video
from utils.platform_detector import is_valid_url, is_supported
from utils.file_cleaner import clean_old_files

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def start_cleaner():
    while True:
        clean_old_files(DOWNLOAD_FOLDER)
        time.sleep(3600)

thread = threading.Thread(target=start_cleaner, daemon=True)
thread.start()


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running", "message": "Velo Downloader API is live!"})


@app.route("/api/info", methods=["POST"])
def get_info():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "URL nahi diya"}), 400

    if not is_valid_url(url):
        return jsonify({"error": "URL sahi nahi hai"}), 400

    if not is_supported(url):
        return jsonify({"error": "Yeh platform supported nahi hai"}), 400

    result = get_video_info(url)

    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    return jsonify(result)


@app.route("/api/download", methods=["GET"])
def download():
    url = request.args.get("url", "").strip()
    format_type = request.args.get("format", "mp4")
    quality = request.args.get("quality", "720")

    if not url:
        return jsonify({"error": "URL nahi diya"}), 400

    if not is_valid_url(url):
        return jsonify({"error": "URL sahi nahi hai"}), 400

    if not is_supported(url):
        return jsonify({"error": "Yeh platform supported nahi hai"}), 400

    result = download_video(url, format_type, quality, DOWNLOAD_FOLDER)

    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    filepath = result.get("filepath")
    filename = result.get("filename")

    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "File nahi mili, download fail hua"}), 404

    # File ko response ke baad background mein delete karo
    def remove_file():
        time.sleep(10)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass

    threading.Thread(target=remove_file, daemon=True).start()

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )


@app.route("/api/platforms", methods=["GET"])
def platforms():
    return jsonify({
        "supported": [
            "YouTube", "Instagram", "Facebook",
            "Twitter/X", "TikTok", "Dailymotion",
            "Vimeo", "Reddit", "Pinterest"
        ]
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route nahi mila"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server mein kuch gadbad hai"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)