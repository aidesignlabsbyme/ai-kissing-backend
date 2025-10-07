from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import tempfile
import os

app = Flask(__name__)
CORS(app)

# Free Hugging Face Space endpoint
HF_API_URL = "https://akhaliq-face-swap.hf.space/run/predict"


@app.route("/")
def home():
    return "AI Kissing Backend (free Hugging Face version) is running!"


@app.route("/generate", methods=["POST"])
def generate():
    try:
        image1 = request.files.get("image1")
        image2 = request.files.get("image2")
        if not image1 or not image2:
            return jsonify({"error": "Both images are required"}), 400

        # Save temp images
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f1, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f2:
            image1.save(f1.name)
            image2.save(f2.name)

        # ✅ Correct 'files' format for requests.post()
        files = [
            ("data", open(f1.name, "rb")),
            ("data", open(f2.name, "rb")),
        ]

        response = requests.post(HF_API_URL, files=files)

        print("🔍 HF status:", response.status_code)
        print("🔍 HF raw response:", response.text)

        try:
            result = response.json()
        except Exception:
            result = {"error": "Non-JSON response", "text": response.text}

        # Clean up
        os.remove(f1.name)
        os.remove(f2.name)

        if "data" in result and len(result["data"]) > 0:
            return jsonify({"result": result["data"][0]})
        else:
            return jsonify({"error": "Invalid response from Hugging Face", "raw": result}), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("🔥 Error in /generate:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
