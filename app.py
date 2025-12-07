import os
import replicate
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "TradeVision AI (Stable ID) is Running!"

@app.route('/visualize', methods=['POST'])
def visualize_renovation():
    try:
        data = request.json
        image_url = data.get('image')
        user_prompt = data.get('prompt')

        if not image_url or not user_prompt:
            return jsonify({"status": "error", "message": "Missing image or prompt"}), 400

        print(f"Processing prompt: {user_prompt}")

        # WE USE THE SPECIFIC, STABLE PUBLIC ID HERE
        # + The modern 'replicate.run' command
        output = replicate.run(
            "timothybrooks/instruct-pix2pix:30c1d0b916a6f8efce20493f5d61ee27491ab2a60437c13c588468b9810ec23f",
            input={
                "image": image_url,
                "prompt": user_prompt,
                "num_inference_steps": 20,
                "image_guidance_scale": 1.5,
            },
            use_file_output=False # Forces it to give us a web link, not a raw file
        )
        
        if output:
            # Replicate returns a list of URLs, we take the first one
            return jsonify({
                "status": "success", 
                "image": output[0]
            })
        else:
            return jsonify({"status": "error", "message": "Replicate returned no image."})

    except replicate.exceptions.ReplicateError as e:
        # This will show us the EXACT error if it fails again
        print(f"Replicate API Error: {e}")
        return jsonify({"status": "error", "message": str(e)})
    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
