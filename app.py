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
        image_url = data.get('image') # The widget sends a data URI
        user_prompt = data.get('prompt')

        if not image_url or not user_prompt:
            return jsonify({"status": "error", "message": "Missing image or prompt"}), 400

        print("Sending to Replicate...")

        # Run the "Instruct-Pix2Pix" model
        # This model is famous for: "Turn the apples into oranges" style edits
        # Run the "Instruct-Pix2Pix" model (Updated Version ID)
        output = replicate.run(
            "timothybrooks/instruct-pix2pix:30c1d0b916a6f8efce20493f5d61ee27491ab2a60437c13c588468b9810ec23f",
            input={
                "image": image_url,
                "prompt": user_prompt,
                "num_inference_steps": 20,
                "image_guidance_scale": 1.5,
            }
        )
        
        # Replicate returns a list of URL(s)
        if output and len(output) > 0:
            return jsonify({
                "status": "success", 
                "image": output[0] # The URL of the new image
            })
        else:
            return jsonify({"status": "error", "message": "Replicate returned no image."})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
