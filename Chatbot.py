from flask import Flask, render_template, request, jsonify
import os
import aiml
import re
from threading import Thread

app = Flask(__name__)
BRAIN_FILE = "./pretrained_model/aiml_pretrained_model.brn"
LEARNING_FILE_LIST = "./pretrained_model/learningFileList.aiml"
k = aiml.Kernel()

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

    # Dictionary to store replacements and their priorities
    replacements = {
        r'\b(?:\w+\s+)*(hello|hi|hey|helo)(?:\s+\w+)*\b': ('hello', 25),

        r'\b(?:\w+\s+)*(faculty|faculties|staff|staffs)\b(?:(?!\b(?:\w+\s+)*(computer|COMP|COM|CSE|CS|f)\b|\b(?:\w+\s+)*department\b).)*\b(?:\w+\s+)*(computer|COMP|COM|CSE|CS|f)\b': ('FCOMPUTER', 8),
        r'\b(?:\w+\s+)*?(faculty|faculties|CIVIL)\b.*?\b(?:faculty|faculties|CIVIL)\b(?:\s+\w+)*?\b': ('FCIVIL', 3),
        #r'\b(?:\w+\s+)*?(faculty|faculties|staff|staffs|CIVIL)\b.*?\b(?:faculty|faculties|staff|staffs|CIVIL)\b(?:\s+\w+)*?\b': ('FCIVIL', 3),
        #r'\b(?:\w+\s+)*?(faculty|faculties|staff|staffs|MECHANICAL|mech)\b.*?\b(?:faculty|faculties|staff|staffs|MECHANICAL|mech)\b(?:\s+\w+)*?\b': ('FMECHANICAL', 4),
        #r'\b(?:\w+\s+)*?(faculty|faculties|staff|staffs|E&TC|ENTC|ELECTRONICS|TELECOMMUNICATION)\b.*?\b(?:faculty|faculties|staff|staffs|E&TC|ENTC|ELECTRONICS|TELECOMMUNICATION)\b(?:\s+\w+)*?\b': ('FELECTRONICS AND TELECOMMUNICATION ENGINEERING', 5),
        #r'\b(?:\w+\s+)*?(faculty|faculties|staff|staffs|ELE|electrical)\b.*?\b(?:faculty|faculties|staff|staffs|Ele|electrical)\b(?:\s+\w+)*?\b': ('FELECTRICAL', 6),
        #r'\b(?:\w+\s+)*?(faculty|faculties|staff|staffs|FIRST|FE)\b.*?\b(?:faculty|faculties|staff|staffs|FIRST|FE)\b(?:\s+\w+)*?\b': ('FFirst Year B.Tech', 31),

        #r'\b(?:\w+\s+)*?(FACULTY|F)(?:\s+\w+)\s+(?:\w+\s+)*(FIRST|FE)(?:\s+\w+)\s+(?:\w+\s+)*(FACULTY|F)(?:\s+\w+)*\b': ('FFirst Year B.Tech', 6),

        r'\b(?:\w+\s+)*(fee|fees|A)(?:\s+\w+)*\b': ('FEES', 7),
        r'\b(?:\w+\s+)*(fees|fee)(?:\s+\w+)\s+(?:\w+\s+)*(computer|COMP|com|fees|fee|civil|MECHANICAL|mech|E&TC|ENTC|ELECTRONICS|TELECOMMUNICATION|Electrical department|electrical)(?:\s+\w+)\s+(?:\w+\s+)*(fees|fee)(?:\s+\w+)\b': ('fees', 2),

        #r'\b(?:FEES|FEE|FIRST|ONE|FE|1)\b.*\b(?:FEES|FEE|FIRST|ONE|FE|1)\b': ('FE', 9),
        r'\b(?:FEES|FEE|FIRST|ONE|FE|1)\b.*\b(?:FEES|FEE|FIRST|ONE|FE|1)\b': ('FE', 9),

        r'\b(?:\w+\s+)*(FEES|FEE|SECOND|TWO|SE|2)\b.*\b(?:FEES|FEE|SECOND|TWO|SE|2)\s+(?:\w+\s+)*\b': ('SE', 10),
        r'\b(?:FEES|FEE|THREE|THIRD|TE|3)\b.*\b(?:FEES|FEE|THREE|THIRD|TE|3)\b': ('TE', 11),
        r'\b(?:FEES|FEE|FOUR|fourth|BE|ENGINEERING|4)\b.*\b(?:FEES|FEE|FOUR|fourth|BE|ENGINEERING|4)\b': ('FBTECH', 12),
        r'\b(?:FEES|FEE|MTECH|MASTER)\b.*\b(?:FEES|FEE|MTECH|MASTER)\b': ('FMTECH', 13),

        #r'\b(?:\w+\s+)*(fees|fee)(?:\s+\w+)\s+(?:\w+\s+)*(first|one|fe|1)(?:\s+\w+)\s+(?:\w+\s+)*(fees|fee)(?:\s+\w+)\b': ('FE', 9),
        #r'\b(?:\w+\s+)*(fees|fee)(?:\s+\w+)\s+(?:\w+\s+)*(SECOND|TWO|SE|2)(?:\s+\w+)\s+(?:\w+\s+)*(fees|fee)(?:\s+\w+)\b': ('SE', 10),
        #r'\b(?:\w+\s+)*(fees|fee)(?:\s+\w+)\s+(?:\w+\s+)*(THREE|THIRD|TE|3)(?:\s+\w+)\s+(?:\w+\s+)*(fees|fee)(?:\s+\w+)\b': ('TE', 11),
        #r'\b(?:\w+\s+)*(fees|fee)(?:\s+\w+)\s+(?:\w+\s+)*(FOUR|fourth|BE|ENGINEERING|4)(?:\s+\w+)\s+(?:\w+\s+)*(fees|fee)(?:\s+\w+)\b': ('FBTECH', 12),
        #r'\b(?:\w+\s+)*(fees|fee)(?:\s+\w+)\s+(?:\w+\s+)*(MTECH|MASTER|ME)(?:\s+\w+)\s+(?:\w+\s+)*(fees|fee)(?:\s+\w+)\b': ('FMTECH', 13),

        r'\b(?:\w+\s+)*(events|B)(?:\s+\w+)*\b': ('EVENTS', 14),
        r'\b(?:\w+\s+)*(carnival)(?:\s+\w+)*\b': ('CARNIVAL', 15),
        r'\b(?:\w+\s+)*(HACKATHON)(?:\s+\w+)*\b': ('HACKATHON', 16),

        r'\b(?:\w+\s+)*(INFRASTRUCTURE|ENVIRONMENT|C)(?:\s+\w+)*\b': ('INFRASTRUCTURE', 17),
        r'\b(?:\w+\s+)*(DEPARTMENTS|DEP|DEPARTMENT)(?:\s+\w+)*\b': ('DEPARTMENTS', 18),
        r'\b(?:\w+\s+)*(CAMPUS)(?:\s+\w+)*\b': ('CAMPUS TOUR', 19),
        r'\b(?:\w+\s+)*(HOSTEL)(?:\s+\w+)*\b': ('HOSTEL FACILITY', 20),
        r'\b(?:\w+\s+)*(CANTEEN|CANTEN)(?:\s+\w+)*\b': ('CANTEEN', 21),

        r'\b(?:\w+\s+)*(PRINCIPAL)(?:\s+\w+)*\b': ('PRINCIPAL', 22),

        r'\b(?:\w+\s+)*(ACADEMIC|D)(?:\s+\w+)*\b': ('ACADEMIC', 23),
        r'\b(?:\w+\s+)*(ADMISSIONS|ADMISSION)(?:\s+\w+)*\b': ('ADMISSIONS', 24),
        r'\b(?:\w+\s+)*(BACHELOR|BACHELORS|BE|BTECH)(?:\s+\w+)*\b': ('BACHELORS PROGRAMMES', 1),
        r'\b(?:\w+\s+)*(BACHELOR|BACHELORS|BE|BTECH)(?:\s+\w+)\s+(?:\w+\s+)*(ELIGIBILITY|ELIGIBLE)(?:\s+\w+)*\s+(?:\w+\s+)*(BACHELOR|BACHELORS|BE|BTECH)(?:\s+\w+)*\b': ('ELIGIBILITY BACHELORS', 26),
        r'\b(?:\w+\s+)*(SYLLABUS)(?:\s+\w+)*\b': ('SYLLABUS', 27),
        r'\b(?:\w+\s+)*(QUESTION|PAPERS|PAPER|QUESTION PAPER|QUESTION PAPERS)(?:\s+\w+)*\b': ('QUESTION PAPERS', 29),
        r'\b(?:\w+\s+)*(ENQUIRY FORM|ENQUIRY)(?:\s+\w+)*\b': ('ENQUIRY FORM', 30),
        r'\b(?:\w+\s+)*(PLACEMENTS|PLACEMENT|E)(?:\s+\w+)*\b': ('PLACEMENTS', 31),
        r'\b(?:\w+\s+)*(RECRUITERS|RECRUITER)(?:\s+\w+)*\b': ('RECRUITERS', 32),
        r'\b(?:\w+\s+)*(COMPANY|LOGOS|LOGO|COMPANIES)(?:\s+\w+)*\b': ('COMPANY LOGOS', 33),
        r'\b(?:\w+\s+)*(INTERNSHIPS|INTERNSHIP)(?:\s+\w+)*\b': ('INTERNSHIPS', 28),
        r'\b(?:\w+\s+)*(MTECH|MASTER|M TECH|M.TECH)(?:\s+\w+)*\b': ('MASTERS PROGRAMMES', 29),
        r'\b(?:\w+\s+)*(faculty|faculties|staff|staffs|F)(?:\s+\w+)*\b': ('FACULTY', 30),
        # Add more replacements as needed
    }

    # Sort replacements by priority
    sorted_replacements = sorted(replacements.items(), key=lambda x: x[1][1])

    # Apply replacements in order of priority
    for pattern, (replacement, priority) in sorted_replacements:
        query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)

    response = process_input(query)
    response_with_line_breaks = response.replace("ln", "<br/>")

    return str(response_with_line_breaks) if response_with_line_breaks else "Information not found. Please check the website: https://sknscoe.ac.in/"

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
