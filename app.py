import os
import replicate
import httpx
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Setup Replicate Client with a timeout that matches Render's limit
client = replicate.Client(
    api_token=os.environ.get("REPLICATE_API_TOKEN"),
    timeout=httpx.Timeout(100.0, connect=60.0) 
)

@app.route('/')
def home():
    return "TradeVision AI (SDXL Edition) is Running!"

@app.route('/visualize', methods=['POST'])
def visualize_renovation():
    try:
        data = request.json
        image_url = data.get('image')
        user_prompt = data.get('prompt')

        if not image_url or not user_prompt:
            return jsonify({"status": "error", "message": "Missing image or prompt"}), 400

        print(f"Processing with SDXL: {user_prompt}")

        # STABLE DIFFUSION XL (SDXL)
        # We use 'prompt_strength' to balance structure vs. creativity.
        output = client.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "image": image_url,
                "prompt": f"Professional architectural photography of a house, {user_prompt}. 8k, photorealistic, high detail.",
                "prompt_strength": 0.7, # <--- KEY SETTING (0.1 = subtle, 1.0 = wild)
                "num_inference_steps": 40,
                "refine": "expert_ensemble_refiner" # Adds that crisp "expensive" look
            }
        )
        
        # SDXL returns a list of URLs
        if output:
            result = output[0] if isinstance(output, list) else output
            return jsonify({
                "status": "success", 
                "image": str(result)
            })
        else:
            return jsonify({"status": "error", "message": "AI returned no image."})

    except replicate.exceptions.ReplicateError as e:
        print(f"Replicate Error: {e}")
        return jsonify({"status": "error", "message": str(e)})
    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
