import os
import replicate
import httpx
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Setup Replicate Client with a long timeout
client = replicate.Client(
    api_token=os.environ.get("REPLICATE_API_TOKEN"),
    timeout=httpx.Timeout(300.0, connect=60.0)
)

@app.route('/')
def home():
    return "TradeVision AI (Flux Edition) is Running!"

@app.route('/visualize', methods=['POST'])
def visualize_renovation():
    try:
        data = request.json
        image_url = data.get('image')
        user_prompt = data.get('prompt')

        if not image_url or not user_prompt:
            return jsonify({"status": "error", "message": "Missing image or prompt"}), 400

        print(f"Processing with Flux: {user_prompt}")

        # FLUX.1 [Fill] - The Best "Structure Aware" Editor
        # We use a lower 'guidance' to keep the house shape, but high enough to change materials.
        output = client.run(
            "black-forest-labs/flux-fill-dev",
            input={
                "image": image_url,
                "prompt": f"High resolution photo of a house. {user_prompt}. Photorealistic, architectural photography, 8k.",
                "guidance": 30,         # Controls how strictly it follows the prompt
                "output_format": "jpg"
            }
        )
        
        # Flux usually returns a generic file object or URL
        if output:
            # Handle list vs string output
            result = output[0] if isinstance(output, list) else output
            return jsonify({
                "status": "success", 
                "image": str(result)
            })
        else:
            return jsonify({"status": "error", "message": "Flux returned no image."})

    except replicate.exceptions.ReplicateError as e:
        print(f"Replicate Error: {e}")
        return jsonify({"status": "error", "message": str(e)})
    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
