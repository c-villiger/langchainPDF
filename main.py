"""
Imports
"""
import os
from flask import Flask, request, render_template
import tempfile
import openai

# Import functions
from langchain_pdf_bot.functions import qa

# Import API Key
from apikey import API_KEY
openai.api_key = API_KEY

# Start App
app = Flask(__name__)


"""
Routes
"""


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/qa', methods=['POST'])
def qa_route():
    # Process the uploaded files
    file_paths = []
    for file in request.files.getlist("file_input"):
        if file.filename != '':
            file_path = os.path.join("cache", file.filename)
            file.save(file_path)
            file_paths.append(file_path)

    prompt_text = request.form['prompt']
    select_chain_type = request.form['select_chain_type']
    select_k = request.form['select_k']

    result = qa(files=file_paths, query=prompt_text,
                chain_type=select_chain_type, k=select_k)

    return render_template('result.html', result=result["result"], source_documents=result["source_documents"])


if __name__ == '__main__':
    app.run(debug=True)
