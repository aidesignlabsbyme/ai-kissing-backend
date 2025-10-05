from flask import Flask, request, jsonify
import replicate
import tempfile, os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize Replicate client using your API key
replicate_client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

@app.route("/")
def home():
    return "AI Kissing Backend is running!"

@app.route("/generate", methods=["POST"])
def generate():
    try:
        # Get the uploaded images
        image1 = request.files.get("image1")
        image2 = request.files.get("image2")

        if not image1 or not image2:
            return jsonify({"error": "Both images are required"}), 400

        # Save to temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp1, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp2:
            image1.save(temp1.name)
            image2.save(temp2.name)

        print("Uploading images to Replicate model...")

        # Run Replicate model
        output = replicate.run(
            "fofr/face-swap:8e37b3fda37dc9085cb02b84b5a76221f64f8dbb27d38a33a9a0c8b8b23a6e5b",
            input={
                "source_image": open(temp1.name, "rb"),
                "target_image": open(temp2.name, "rb")
            }
        )

        print("Model output:", output)

        # Clean up temp files
        os.remove(temp1.name)
        os.remove(temp2.name)

        # Return output
        return jsonify({"output": output})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
