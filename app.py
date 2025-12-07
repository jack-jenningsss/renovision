import os
import replicate
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "TradeVision AI (Replicate Edition) is Running!"

@app.route('/visualize', methods=['POST'])
def visualize_renovation():
    try:
        data = request.json
        image_url = data.get('image')
        user_prompt = data.get('prompt')

        if not image_url or not user_prompt:
            return jsonify({"status": "error", "message": "Missing image or prompt"}), 400

        print(f"Processing prompt: {user_prompt}")

        # 1. Get the model dynamically (so we don't need a hardcoded Version ID)
        model = replicate.models.get("timothybrooks/instruct-pix2pix")
        version = model.latest_version  # <--- This automatically grabs the correct ID

        # 2. Run the prediction using the version object
        output = version.predict(
            image=image_url,
            prompt=user_prompt,
            num_inference_steps=20,
            image_guidance_scale=1.5,
        )
        
        # Replicate usually returns a list of URLs or a single URL
        if output:
            # If it's a list, grab the first item. If it's a string, use it directly.
            result_url = output[0] if isinstance(output, list) else output
            return jsonify({
                "status": "success", 
                "image": result_url
            })
        else:
            return jsonify({"status": "error", "message": "Replicate returned no image."})

    except replicate.exceptions.ReplicateError as e:
        # This catches specific account errors (like missing billing)
        print(f"Replicate Error: {e}")
        return jsonify({"status": "error", "message": "Billing/Account Error: Check Replicate dashboard."})
    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
