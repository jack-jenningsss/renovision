import os
import replicate
import httpx # Required for the timeout fix
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# SETUP: Create a client with a LONG timeout (5 minutes instead of 1)
# This prevents the "Connection Error" during the Cold Boot
client = replicate.Client(
    api_token=os.environ.get("REPLICATE_API_TOKEN"),
    timeout=httpx.Timeout(300.0, connect=60.0) # Wait 300 seconds (5 mins)
)

@app.route('/')
def home():
    return "TradeVision AI (Long Timeout Edition) is Running!"

@app.route('/visualize', methods=['POST'])
def visualize_renovation():
    try:
        data = request.json
        image_url = data.get('image')
        user_prompt = data.get('prompt')

        if not image_url or not user_prompt:
            return jsonify({"status": "error", "message": "Missing image or prompt"}), 400

        print(f"Processing prompt: {user_prompt}")

        # Run with the stable ID
        output = client.run(
            "timothybrooks/instruct-pix2pix:30c1d0b916a6f8efce20493f5d61ee27491ab2a60437c13c588468b9810ec23f",
            input={
                "image": image_url,
                "prompt": user_prompt,
                "num_inference_steps": 20,
                "image_guidance_scale": 1.5,
            },
            use_file_output=False
        )
        
        if output:
            return jsonify({
                "status": "success", 
                "image": output[0]
            })
        else:
            return jsonify({"status": "error", "message": "Replicate returned no image."})

    except replicate.exceptions.ReplicateError as e:
        print(f"Replicate Error: {e}")
        return jsonify({"status": "error", "message": str(e)})
    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
