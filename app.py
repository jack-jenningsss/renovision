import os
import replicate
import base64
import io 
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "TradeVision AI is Running!"

# --- THE MAIN GENERATION ROUTE ---
@app.route('/api/preview', methods=['POST'])
def api_preview():
    try:
        # 1. Check if image and prompt exist
        if 'image' not in request.files or 'prompt' not in request.form:
            return jsonify({'error': 'Missing image or prompt'}), 400

        image_file = request.files['image']
        prompt_text = request.form['prompt']
        
        # 2. Save the image temporarily
        temp_filename = f"temp_{image_file.filename}"
        image_file.save(temp_filename)

        print(f"Generatng with prompt: {prompt_text}")

        # 3. Call Replicate (SDXL)
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "image": open(temp_filename, "rb"),
                "prompt": prompt_text,
                "strength": 0.85,   # <--- CHANGED TO 0.85 FOR BETTER COVERAGE
                "guidance_scale": 7.5
            }
        )

        # 4. Clean up
        os.remove(temp_filename)

        # 5. Return Result
        return jsonify({'imageUrl': str(output[0])})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/widget.js')
def serve_widget():
    return send_from_directory('.', 'widget.js')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)