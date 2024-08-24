import os
from urllib.parse import urlparse

from flask import Flask, request, jsonify
from extract_text import extract_text_from_pdf, extract_text_from_docx, extract_text_from_pptx

import requests
import subprocess

app = Flask(__name__)


def download_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


@app.route('/run_code', methods=['POST'])
def run_code():
    data = request.get_json()
    file_path = data.get('file_path')

    # if not file_path or not os.path.exists(file_path):
    #     return jsonify({'response': 'File not found'}), 400

    if not file_path:
        return jsonify({'response': 'File not found'}), 400

    # Check if the file path is a URL
    parsed_url = urlparse(file_path)
    if parsed_url.scheme in ['http', 'https']:
        try:
            file_path = download_file(file_path)
        except Exception as e:
            return jsonify({'response': f'Error downloading file: {str(e)}'}), 400
    else:
        if not os.path.exists(file_path):
            return jsonify({'response': 'File not found'}), 400

    _, file_extension = os.path.splitext(file_path)

    try:
        if file_extension == '.docx':
            result = extract_text_from_docx(file_path)
        elif file_extension == '.pptx':
            result = extract_text_from_pptx(file_path)
        elif file_extension == '.pdf':
            result = extract_text_from_pdf(file_path)
        else:
            return jsonify({'response': 'Unsupported file type'}), 400
    except Exception as e:
        result = str(e)

    return jsonify({'response': result})


if __name__ == '__main__':
    app.run(debug=True)
