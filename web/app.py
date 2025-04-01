from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

def load_memes():
    try:
        meme_file = os.path.join(os.path.dirname(__file__), '..', 'memes', 'meme_metadata.json')
        with open(meme_file, 'r') as f:
            data = json.load(f)
            # Sort memes by timestamp in descending order
            data['memes'].sort(key=lambda x: x['timestamp'], reverse=True)
            return data['memes']
    except Exception as e:
        print(f"Error loading memes: {e}")
        return []

def load_presentation():
    try:
        presentation_file = os.path.join(os.path.dirname(__file__), 'content', 'presentation.json')
        with open(presentation_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading presentation: {e}")
        return {}

@app.route('/')
def gallery():
    memes = load_memes()
    return render_template('gallery.html', memes=memes)

@app.route('/api/memes')
def get_memes():
    return jsonify(load_memes())

@app.route('/presentation/<int:slide_id>')
def presentation(slide_id):
    content = load_presentation()
    max_slides = len(content['slides'])
    current_slide = content['slides'][min(slide_id - 1, max_slides - 1)]
    return render_template('presentation.html', 
                         slide=current_slide, 
                         current_id=slide_id,
                         max_slides=max_slides)

@app.route('/team')
def team():
    return render_template('team.html')

# Vercel requires this
app.debug = True

# This is only used when running locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000) 