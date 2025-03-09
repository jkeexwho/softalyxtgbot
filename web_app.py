from flask import Flask, request, jsonify
from bot import handle_website_request
from config import FLASK_SECRET_KEY
import secrets
import asyncio

app = Flask(__name__)
# Generate a secure random secret key
app.secret_key = FLASK_SECRET_KEY or secrets.token_hex(32)

@app.route('/api/send-request', methods=['POST'])
def send_request():
    """Endpoint for receiving requests from the website"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'message', 'contact_preference', 'privacy_accepted']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False, 
                'error': f'Missing required fields. Required: {", ".join(required_fields)}'
            }), 400
        
        # Validate contact preference
        if data['contact_preference'] not in ['Telegram', 'Email']:
            return jsonify({
                'success': False,
                'error': 'Contact preference must be either "Telegram" or "Email"'
            }), 400
            
        # Validate privacy policy acceptance
        if not data['privacy_accepted']:
            return jsonify({
                'success': False,
                'error': 'Privacy policy must be accepted to process the request'
            }), 400
        
        # Send message to Telegram
        success = asyncio.run(handle_website_request(data))
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Request sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send message'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 