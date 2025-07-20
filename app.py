from flask import Flask, request, jsonify
import replicate
import tempfile, os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

@app.route("/generate", methods=["POST"])
def generate():
    image1 = request.files.get("image1")
    image2 = request.files.get("image2")
    if not image1 or not image2:
        return jsonify({"error": "Both images are required."}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f1, \
         tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f2:
        image1.save(f1.name)
        image2.save(f2.name)

        output = replicate.run(
    "lucataco/face-swap:84cd53b5588f89e5c579e6d35cc3b5dfd6c2a8f1d7a92480b6b5b40b19922712",
    input={
        "source_image": open(f1.name, "rb"),
        "target_image": open(f2.name, "rb")
    }
)
    return jsonify({"result": output[0]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
