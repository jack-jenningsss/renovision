import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# We get the key from the environment variable (safe storage)
api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

@app.route('/')
def home():
    return "TradeVision AI is Running!"

@app.route('/visualize', methods=['POST'])
def visualize_renovation():
    try:
        data = request.json
        image_data = data.get('image')
        user_prompt = data.get('prompt')

        if not image_data or not user_prompt:
            return jsonify({"status": "error", "message": "Missing image or prompt"}), 400

        # Clean up the base64 string
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]

        img_bytes = base64.b64decode(image_data)

        # Call Google Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                f"Edit this image: {user_prompt}. Keep the structure of the house exactly the same. Photorealistic, high quality."
            ]
        )

        if response.text:
            # Note: Sometimes Gemini returns text if it refuses the image.
            # But usually for valid edits, it returns inline_data.
            pass 

        # Extract Image
        # (Gemini 2.0 Flash usually returns the image in the response parts)
        # For simplicity in this snippet we assume success if we get here.
        # In a full production app, we would add more error checking.

        # Re-encode to send back to browser
        if hasattr(response, 'inline_data') and response.inline_data:
             generated_b64 = base64.b64encode(response.inline_data.data).decode('utf-8')
             return jsonify({
                "status": "success", 
                "image": f"data:image/jpeg;base64,{generated_b64}"
             })

        # Fallback if the model returns a link or other format
        return jsonify({"status": "error", "message": "AI finished but returned no image data."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)