import os
from flask import request, jsonify
from controller.smry import smry_function

def summarize():
    """Endpoint to summarize the content of a text file."""
    data = request.json
    file_path = data.get('file_path')

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File path is invalid or file does not exist'}), 400

    try:
        summary = smry_function(file_path)
        return jsonify({
            'summary': summary
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
