import os
import replicate
import httpx
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Setup Replicate Client with a long timeout (Gemini can take 10-20s)
client = replicate.Client(
    api_token=os.environ.get("REPLICATE_API_TOKEN"),
    timeout=httpx.Timeout(300.0, connect=60.0)
)

@app.route('/')
def home():
    return "TradeVision AI (Nano Banana Edition) is Running!"

@app.route('/visualize', methods=['POST'])
def visualize_renovation():
    try:
        data = request.json
        image_url = data.get('image')
        user_prompt = data.get('prompt')

        if not image_url or not user_prompt:
            return jsonify({"status": "error", "message": "Missing image or prompt"}), 400

        print(f"Processing with Nano Banana: {user_prompt}")

        # NANO BANANA (Gemini 2.5 Flash Image)
        # It works best with a clear, conversational instruction.
        output = client.run(
            "google/nano-banana",
            input={
                "image": image_url,
                "prompt": f"Edit this image of a house. {user_prompt}. Maintain photorealism and keeping the original structure exactly the same.",
                "output_format": "jpg"
            }
        )
        
        # Google models on Replicate typically return a single string URL (not a list)
        # But we check both just in case.
        if output:
            result_url = output[0] if isinstance(output, list) else output
            return jsonify({
                "status": "success", 
                "image": result_url
            })
        else:
            return jsonify({"status": "error", "message": "AI returned no image."})

    except replicate.exceptions.ReplicateError as e:
        print(f"Replicate Error: {e}")
        # This catches the 422 error if the input schema is slightly different
        return jsonify({"status": "error", "message": str(e)})
    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
