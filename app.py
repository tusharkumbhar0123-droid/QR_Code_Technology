
from flask import Flask, render_template, request, jsonify, send_file
import qrcode
import io
import cv2
import numpy as np

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate_qr():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Please enter some text or a URL."}), 400

    qr = qrcode.make(text)
    image_buffer = io.BytesIO()
    qr.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    return send_file(
        image_buffer,
        mimetype="image/png",
        download_name="qr-code.png"
    )


@app.route("/api/scan", methods=["POST"])
def scan_qr():
    if "image" not in request.files:
        return jsonify({"error": "Please upload a QR code image."}), 400

    file = request.files["image"]

    if not file.filename:
        return jsonify({"error": "Please select an image."}), 400

    image_bytes = file.read()

    if not image_bytes:
        return jsonify({"error": "The uploaded file is empty."}), 400

    image_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({"error": "Please upload a valid image."}), 400

    detector = cv2.QRCodeDetector()
    decoded_text, points, _ = detector.detectAndDecode(image)

    if not decoded_text:
        return jsonify({
            "error": "No readable QR code found in this image."
        }), 400

    return jsonify({"text": decoded_text})


if __name__ == "__main__":
    app.run(debug=False)
