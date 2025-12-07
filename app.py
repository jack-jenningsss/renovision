import os
import replicate
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "TradeVision AI (Updated) is Running!"

@app.route('/visualize', methods=['POST'])
def visualize_renovation():
    try:
        data = request.json
        image_url = data.get('image')
        user_prompt = data.get('prompt')

        if not image_url or not user_prompt:
            return jsonify({"status": "error", "message": "Missing image or prompt"}), 400

        print(f"Processing prompt: {user_prompt}")

        # 1. Get the latest version ID dynamically
        model = replicate.models.get("timothybrooks/instruct-pix2pix")
        version = model.latest_version
        
        # 2. Run using the modern "replicate.run" command
        # We construct the ID manually: "owner/model:version_id"
        model_id = f"timothybrooks/instruct-pix2pix:{version.id}"
        
        output = replicate.run(
            model_id,
            input={
                "image": image_url,
                "prompt": user_prompt,
                "num_inference_steps": 20,
                "image_guidance_scale": 1.5,
            },
            # CRITICAL FIX: This forces Replicate to give us a URL string
            # instead of a file stream (which would crash your JSON)
            use_file_output=False 
        )
        
        # Replicate returns a list of URLs
        if output:
            return jsonify({
                "status": "success", 
                "image": output[0] # Grab the first URL
            })
        else:
            return jsonify({"status": "error", "message": "Replicate returned no image."})

    except replicate.exceptions.ReplicateError as e:
        print(f"Replicate API Error: {e}")
        return jsonify({"status": "error", "message": "Replicate Billing or API Error."})
    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
