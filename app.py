from flask import Flask, request, jsonify
from flask_cors import CORS
import replicate
import tempfile
import os

app = Flask(__name__)
CORS(app)

# Initialize Replicate client
rep_client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

@app.route("/")
def home():
    return "AI Kissing Backend is running!"

@app.route("/generate", methods=["POST"])
def generate():
    try:
        image1 = request.files.get("image1")
        image2 = request.files.get("image2")

        if not image1 or not image2:
            return jsonify({"error": "Both images are required."}), 400

        # Save temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f1, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f2:
            image1.save(f1.name)
            image2.save(f2.name)

            # Run Replicate model
            output = rep_client.run(
                "codeplugtech/face-swap:278a81e7ebb22db98bcba54de985d22cc1abeead2754eb1f2af717247be69b34",
                input={
                    "source_image": open(f1.name, "rb"),
                    "target_image": open(f2.name, "rb")
                }
            )

        # Clean up temp files
        os.remove(f1.name)
        os.remove(f2.name)

        # Return response
        if isinstance(output, list) and len(output) > 0:
            return jsonify({"result": output[0]})
        elif isinstance(output, str):
            return jsonify({"result": output})
        else:
            return jsonify({"error": "Invalid model response.", "raw_output": str(output)}), 500

    except Exception as e:
        print("Error in /generate:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
