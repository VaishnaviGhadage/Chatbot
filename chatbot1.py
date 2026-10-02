from flask import Flask, render_template, request, jsonify
import os
import aiml
import re
from threading import Thread
from spellchecker import SpellChecker
from googletrans import Translator

app = Flask(__name__)
BRAIN_FILE = "./pretrained_model/aiml_pretrained_model.brn"
LEARNING_FILE_LIST = "./pretrained_model/learningFileList.aiml"
k = aiml.Kernel()
spell = SpellChecker()
translator = Translator()

def load_or_reload_brain():
    global k
    try:
        if os.path.exists(BRAIN_FILE):
            os.remove(BRAIN_FILE)
            print("Removed existing brain file: " + BRAIN_FILE)
        print("Parsing AIML files")
        k.bootstrap(learnFiles=LEARNING_FILE_LIST)
        print("Saving brain file: " + BRAIN_FILE)
        k.saveBrain(BRAIN_FILE)

        print("Loaded AIML files:")
        for file in k.getSessionData("activefiles"):
            print(file)
    except Exception as e:
        print(f"Error loading or reloading brain: {str(e)}")

def run_flask():
    try:
        app.run(host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Flask app failed to run: {str(e)}")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/get")
def get_bot_response():
    query = request.args.get('msg')

    # Translate query to Marathi if requested
    language = request.args.get('lang')  # Assuming language code sent by the user
    if language and language.lower() == 'marathi':
        translation = translator.translate(query, src='en', dest='mr')
        query = translation.text

    # Dictionary to store replacements and their priorities
    replacements = {
        r'\b(?:\w+\s+)*(hello|hi|hey|helo)(?:\s+\w+)*\b': ('hello', 1),
        r'\b(?:\w+\s+)*(computer|COMP|com)(?:\s+\w+)*\b': ('COMPUTER', 8),
        r'\b(?:\w+\s+)*civil(?:\s+\w+)*\b': ('civil', 3),
        r'\b(?:\w+\s+)*(MECHANICAL|mech)(?:\s+\w+)*\b': ('MECHANICAL', 4),
        r'\b(?:\w+\s+)*(E&TC|ENTC|ELECTRONICS|TELECOMMUNICATION)(?:\s+\w+)*\b': ('ELECTRONICS AND TELECOMMUNICATION ENGINEERING', 5),
        r'\b(?:\w+\s+)*(Electrical department|electrical)(?:\s+\w+)*\b': ('ELECTRICAL ENGINEERING', 6),
        r'\b(?:\w+\s+)*(fees|fee)(?:\s+\w+)\s+(?:\w+\s+)*(computer|COMP|com|civil|MECHANICAL|mech|E&TC|ENTC|ELECTRONICS|TELECOMMUNICATION|Electrical department|electrical)(?:\s+\w+)\s+(?:\w+\s+)*(fees|fee)(?:\s+\w+)\b': ('fees', 2),

        r'\b(?:\w+\s+)*(?:\d+|"first"|one|fe)(?:\s+\w+)*\b': ('FE', 9),
        r'\b(?:\w+\s+)*(SECOND|2|TWO|option SECOND)(?:\s+\w+)*\b': ('SE', 10),
        r'\b(?:\w+\s+)*(THIRD|3|THREE|option THIRD)(?:\s+\w+)*\b': ('TE', 11),
        r'\b(?:\w+\s+)*(BTECH|4|FOUR|option FOUR|BE|ENGINEERING)(?:\s+\w+)*\b': ('BTECH', 12),
        r'\b(?:\w+\s+)*(MTECH|5|FIVE|option FIFTH|MASTER)(?:\s+\w+)*\b': ('MTECH', 13),

        r'\b(?:\w+\s+)*(events)(?:\s+\w+)*\b': ('EVENTS', 14),
        r'\b(?:\w+\s+)*(INFRASTRUCTURE|ENVIRONMENT)(?:\s+\w+)*\b': ('INFRASTRUCTURE', 15),
        r'\b(?:\w+\s+)*(DEPARTMENTS|DEP|DEPARTMENT)(?:\s+\w+)*\b': ('DEPARTMENTS', 16),
        r'\b(?:\w+\s+)*(CAMPUS)(?:\s+\w+)*\b': ('CAMPUS TOUR', 17),
        r'\b(?:\w+\s+)*(HOSTEL)(?:\s+\w+)*\b': ('HOSTEL FACILITY', 18),
        r'\b(?:\w+\s+)*(CANTEEN|CANTEN)(?:\s+\w+)*\b': ('CANTEEN', 4),
        # Add more replacements as needed
    }

    # Sort replacements by priority
    sorted_replacements = sorted(replacements.items(), key=lambda x: x[1][1])

    # Apply replacements in order of priority
    for pattern, (replacement, priority) in sorted_replacements:
        query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)

    # Correct spelling mistakes
    corrected_query = correct_spelling(query)
    if corrected_query is None:
        corrected_query = query

    response = process_input(corrected_query)
    response_with_line_breaks = response.replace("ln", "<br/>")

    return str(response_with_line_breaks) if response_with_line_breaks else "Information not found. Please check the website: https://sknscoe.ac.in/"

def correct_spelling(query):
    if not query:
        return None
    # Split the query into words and correct each word
    corrected_words = [spell.correction(word) for word in query.split() if word]
    # Join the corrected words back into a sentence
    corrected_query = ' '.join(corrected_words)
    return corrected_query

def process_input(query):
    response = k.respond(query)
    return response

@app.route("/reload_brain", methods=["POST"])
def reload_brain():
    try:
        Thread(target=load_or_reload_brain).start()
        return jsonify({"status": "Brain reload initiated."})
    except Exception as e:
        return jsonify({"status": f"Error: {str(e)}"})

if __name__ == "__main__":
    load_or_reload_brain()
    Thread(target=run_flask).start()

''' <aiml version="1.0">
    <category>
        <pattern>LOAD AIML</pattern>
        <template>
            <!-- Load standard AIML set -->
            <learn>data/*.aiml</learn>
        </template>
    </category>
</aiml>

<aiml version="1.0">
    <category>
        <pattern>*</pattern>
        <template>
            I don't have a specific response for that.
        </template>
    </category>
</aiml>'''