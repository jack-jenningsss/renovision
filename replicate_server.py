from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import replicate
import tempfile
import traceback
import requests

app = Flask(__name__, static_folder='.')
CORS(app)

# Ensure token is set in env or exit
REPLICATE_TOKEN = os.environ.get('REPLICATE_API_TOKEN')
if not REPLICATE_TOKEN:
    print('WARNING: REPLICATE_API_TOKEN not found in environment. Set it before running the server.')
else:
    os.environ.setdefault('REPLICATE_API_TOKEN', REPLICATE_TOKEN)


def resolve_output_to_url(output):
    # output may be a string, list, or Replicate FileOutput object
    if isinstance(output, list):
        output = output[0]

    if isinstance(output, str):
        return output

    # Try common URL attributes/methods
    for attr in ('url', 'download_url', 'get_url', 'public_url'):
        if hasattr(output, attr):
            try:
                val = getattr(output, attr)
                val = val() if callable(val) else val
                if isinstance(val, str):
                    return val
            except Exception:
                continue

    # Fallback to str()
    return str(output)


@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        email = request.form.get('email')
        prompt = request.form.get('prompt') or 'Make this roof black'
        image = request.files.get('image')

        if not email:
            return jsonify({'error': 'Missing email'}), 400
        if not image:
            return jsonify({'error': 'Missing image file'}), 400

        # Save uploaded file to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[1]) as tf:
            image.save(tf.name)
            temp_path = tf.name

        # Call replicate using file handle
        with open(temp_path, 'rb') as f:
            input_data = {
                'prompt': prompt,
                'image_input': [f]
            }
            try:
                output = replicate.run('google/nano-banana', input=input_data)
            except Exception:
                traceback.print_exc()
                os.unlink(temp_path)
                return jsonify({'error': 'Replicate call failed'}), 500

        os.unlink(temp_path)

        image_url = resolve_output_to_url(output)

        return jsonify({'imageUrl': image_url})

    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'Server error'}), 500


@app.route('/widget.html')
def widget():
    return send_from_directory('.', 'widget.html')


if __name__ == '__main__':
    # Run on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)