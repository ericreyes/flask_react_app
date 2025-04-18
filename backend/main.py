from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configuration
app.config['DEBUG'] = True

# In production, static files will be served from the React build folder
REACT_BUILD_FOLDER = os.path.abspath('../frontend/build')

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint that returns a simple JSON response"""
    return jsonify({
        'message': 'Flask API is working!',
        'status': 'success'
    })

# Route to serve React app - for production use
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React app in production"""
    if path != "" and os.path.exists(os.path.join(REACT_BUILD_FOLDER, path)):
        return send_from_directory(REACT_BUILD_FOLDER, path)
    else:
        return send_from_directory(REACT_BUILD_FOLDER, 'index.html')

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'message': 'Resource not found',
        'status': 'error',
        'error': str(e)
    }), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({
        'message': 'Internal server error',
        'status': 'error',
        'error': str(e)
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

