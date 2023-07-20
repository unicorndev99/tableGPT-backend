from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import json
import time
import os

#chatAI module

from langchain.agents import create_pandas_dataframe_agent
from langchain.llms import OpenAI
import pandas as pd

app = Flask(__name__)
CORS(app)

os.environ["OPENAI_API_KEY"] = "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"

# generate upload folder
folder_name = "upload_dir"
current_directory = os.getcwd()

# Create the new folder path
new_folder_path = os.path.join(current_directory, folder_name)

# Create the new folder
if not os.path.exists(new_folder_path):
    os.mkdir(new_folder_path)
    print("Folder created successfully")

@app.route('/getAnswer', methods=['POST'])
def getAnswer_fromfile():
    json_data = request.get_json()
    
    df = pd.read_csv(os.path.join(new_folder_path, json_data.get('file')), encoding = "utf-8")
    df = df.fillna(0)

    df.info()
    df.head()

    agent = create_pandas_dataframe_agent(OpenAI(temperature=0, model_name='text-davinci-003'), df, verbose=True)

    answer = agent.run(json_data.get('message'))
    print("answer", answer)

    data = {'message': answer}
    return jsonify(data)

@app.route('/upload', methods=['POST', "OPTIONS"])
def upload_file():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    elif request.method == "POST": # The actual request following the preflight
        file = request.files['file']
        if file:
            filename  = file.filename.rsplit(".", 1)[0]
            extension  = file.filename.rsplit(".", 1)[1]
            current_timestamp = int(time.time())
            saved_filename = filename + "_" + str(current_timestamp) + "." + extension
            file.save(os.path.join(new_folder_path, saved_filename))
            return saved_filename
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))


    # return 'Hello, World!'
    
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# @app.route('/redirect')
# def redirect_to_hello():
#     return redirect('/hello')

if __name__ == '__main__':
    app.run()