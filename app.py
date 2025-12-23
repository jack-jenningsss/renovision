import os
import replicate
import base64
import io  # Required to create "virtual files"
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all routes and origins (important for local testing)
CORS(app, resources={r"/*": {"origins": "*"}})

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

@app.route('/api/preview', methods=['POST'])
def api_preview():
    try:
        # 1. Check if image and prompt exist
        if 'image' not in request.files or 'prompt' not in request.form:
            return jsonify({'error': 'Missing image or prompt'}), 400

        image_file = request.files['image']
        prompt_text = request.form['prompt']
        
        # 2. Save the image temporarily so Replicate can read it
        temp_filename = f"temp_{image_file.filename}"
        image_file.save(temp_filename)

        # 3. Call Replicate (The AI)
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "image": open(temp_filename, "rb"),
                "prompt": prompt_text,
                "strength": 0.5,  # How much to change the original photo
                "guidance_scale": 7.5
            }
        )

        # 4. Clean up temp file
        os.remove(temp_filename)

        # 5. Return the result to the widget
        # Replicate returns a list; we want the first image URL
        return jsonify({'imageUrl': str(output[0])})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/widget.js')
def serve_widget():
    # This tells Flask: "Look in the current folder for widget.js and send it"
    return send_from_directory('.', 'widget.js')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)