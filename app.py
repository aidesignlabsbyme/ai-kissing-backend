from flask import Flask, request, jsonify
import replicate
import tempfile, os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize Replicate with your API token
replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

@app.route("/generate", methods=["POST"])
def generate():
    image1 = request.files.get("image1")
    image2 = request.files.get("image2")

    if not image1 or not image2:
        return jsonify({"error": "Both images are required"}), 400

    # Save images temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f1, \
         tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f2:
        image1.save(f1.name)
        image2.save(f2.name)

        try:
            # Run the faceswap model
            output = replicate.run(
    "fofr/face-swap:8e37b3fda37dc9085cb02b84b5a76221f64f8dbb27d38a33a9a0c8b8b23a6e5b",
                input={
                    "face_image": open(f1.name, "rb"),
                    "target_image": open(f2.name, "rb")
                }
            )

            return jsonify({"result": output}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
