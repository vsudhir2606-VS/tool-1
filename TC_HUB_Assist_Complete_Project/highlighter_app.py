
from flask import Flask, render_template, request, jsonify
import re
import json
import os

app = Flask(__name__)

# File to store highlight configurations
HIGHLIGHT_CONFIG_FILE = 'highlight_config.json'

def load_highlight_config():
    """Load highlight configuration from JSON file"""
    if os.path.exists(HIGHLIGHT_CONFIG_FILE):
        try:
            with open(HIGHLIGHT_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_highlight_config(config):
    """Save highlight configuration to JSON file"""
    with open(HIGHLIGHT_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def highlight_text(text, keywords, colors):
    """Highlight keywords in text with specified colors"""
    if not text or not keywords:
        return text
    
    highlighted_text = text
    
    # Sort keywords by length (longest first) to avoid partial replacements
    sorted_keywords = sorted(keywords, key=len, reverse=True)
    
    for i, keyword in enumerate(sorted_keywords):
        if keyword.strip():
            color = colors[i % len(colors)] if colors else '#ffff00'
            # Use word boundaries for exact word matching
            pattern = r'\b' + re.escape(keyword.strip()) + r'\b'
            replacement = f'<mark style="background-color: {color}; padding: 2px 4px; border-radius: 3px;">{keyword.strip()}</mark>'
            highlighted_text = re.sub(pattern, replacement, highlighted_text, flags=re.IGNORECASE)
    
    return highlighted_text

@app.route('/')
def index():
    return render_template('highlighter.html')

@app.route('/api/highlight', methods=['POST'])
def api_highlight():
    data = request.get_json()
    text = data.get('text', '')
    keywords = data.get('keywords', [])
    colors = data.get('colors', ['#ffff00', '#90EE90', '#FFB6C1', '#87CEEB', '#DDA0DD'])
    
    # Filter out empty keywords
    keywords = [k.strip() for k in keywords if k.strip()]
    
    highlighted_text = highlight_text(text, keywords, colors)
    
    return jsonify({
        'highlighted_text': highlighted_text,
        'keyword_count': len(keywords),
        'total_matches': sum(len(re.findall(r'\b' + re.escape(k) + r'\b', text, re.IGNORECASE)) for k in keywords)
    })

@app.route('/api/save-config', methods=['POST'])
def save_config():
    data = request.get_json()
    config_name = data.get('config_name', '')
    keywords = data.get('keywords', [])
    colors = data.get('colors', [])
    
    if not config_name:
        return jsonify({'error': 'Config name is required'}), 400
    
    config = load_highlight_config()
    config[config_name] = {
        'keywords': keywords,
        'colors': colors
    }
    save_highlight_config(config)
    
    return jsonify({'message': 'Configuration saved successfully'})

@app.route('/api/load-config/<config_name>')
def load_config(config_name):
    config = load_highlight_config()
    if config_name in config:
        return jsonify(config[config_name])
    return jsonify({'error': 'Configuration not found'}), 404

@app.route('/api/configs')
def get_configs():
    config = load_highlight_config()
    return jsonify(list(config.keys()))

@app.route('/api/delete-config/<config_name>', methods=['DELETE'])
def delete_config(config_name):
    config = load_highlight_config()
    if config_name in config:
        del config[config_name]
        save_highlight_config(config)
        return jsonify({'message': 'Configuration deleted successfully'})
    return jsonify({'error': 'Configuration not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
