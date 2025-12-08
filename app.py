import os
import replicate
import base64
import io  # Required to create "virtual files"
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "TradeVision AI (Nano Banana Edition) is Running!"

@app.route('/visualize', methods=['POST'])
def visualize_renovation():
    try:
        data = request.json
        image_data = data.get('image') # This is the base64 string from the widget
        user_prompt = data.get('prompt')

        if not image_data or not user_prompt:
            return jsonify({"status": "error", "message": "Missing image or prompt"}), 400

        print(f"Processing with Nano Banana: {user_prompt}")

        # 1. CLEAN & DECODE THE IMAGE
        # The widget sends "data:image/jpeg;base64,..." - we need to strip the header
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]
        
        # Decode the string into raw bytes
        image_bytes = base64.b64decode(image_data)
        
        # Create a "Virtual File" in memory (The AI thinks this is a real file on disk)
        virtual_file = io.BytesIO(image_bytes)

        # 2. RUN THE MODEL (Exact logic from your working script)
        # Note: We use 'use_file_output=False' to fix the "JSON Serializable" crash
        output = replicate.run(
            "google/nano-banana",
            input={
                "prompt": f"Edit this image: {user_prompt}",
                "image_input": [virtual_file] # Passing it as a list, just like your script
            },
            use_file_output=False # CRITICAL: Forces Replicate to give us a URL string
        )
        
        # 3. HANDLE THE OUTPUT
        if output:
            # Replicate returns a list of URLs (e.g. ['https://...'])
            result_url = output[0] if isinstance(output, list) else output
            return jsonify({
                "status": "success", 
                "image": result_url
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
