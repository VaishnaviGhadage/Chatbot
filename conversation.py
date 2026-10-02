from flask import Flask, render_template, request, jsonify
import aiml
import os

app = Flask(__name__)

BRAIN_FILE = "aiml_brain.brn"
LEARNING_FILE_LIST = "learningFileList.aiml"

k = aiml.Kernel()


def load_or_reload_brain():
    global k
    k.resetBrain()  # Clear existing brain

    print("Parsing AIML files")
    k.bootstrap(learnFiles=[LEARNING_FILE_LIST], commands="load aiml")
    print("Saving brain file: " + BRAIN_FILE)
    k.saveBrain(BRAIN_FILE)


# Load or reload the brain when the application starts
load_or_reload_brain()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/get")
def get_bot_response():
    query = request.args.get('msg')
    response_obj = k.respond(query)

    print("User Input:", query)
    print("AIML Response Object:", response_obj)

    # Extract text from the response_obj
    response_text = extract_text_from_response(response_obj)

    print("AIML Response Text:", response_text)

    return jsonify({"response": response_text})


def extract_text_from_response(response_obj):
    # Modify this function based on the actual structure of your response objects
    # This is just a placeholder; replace it with the correct logic for your use case
    if isinstance(response_obj, dict) and 'text' in response_obj:
        return response_obj['text']
    else:
        # If the response object is not in the expected format, return a placeholder or handle it accordingly
        return str(response_obj)

