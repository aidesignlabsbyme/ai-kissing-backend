from flask import Flask, request, jsonify
import replicate
import tempfile
import os
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Replicate client with your API token
replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

@app.route("/generate", methods=["POST"])
def generate():
    try:
        # Get uploaded files
        image1 = request.files.get("image1")
        image2 = request.files.get("image2")

        if not image1 or not image2:
            return jsonify({"error": "Both images are required"}), 400

        # Save the images temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f1, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f2:
            image1.save(f1.name)
            image2.save(f2.name)

            # Run the Replicate model
            output = replicate.run(
                "codeplugtech/face-swap:278a81e7ebb22db98bcba54de985d22cc1abeead2754eb1f2af717247be69b34",
                input={
                    "source_image": open(f1.name, "rb"),
                    "target_image": open(f2.name, "rb")
                }
            )

        # Return the model output
        return jsonify({"result": output})

    except Exception as e:
        print("🔥 Error in /generate:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
