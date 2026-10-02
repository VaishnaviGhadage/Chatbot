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
            print("Removed existing brain file:", BRAIN_FILE)
        print("Parsing AIML files")
        k.bootstrap(learnFiles=LEARNING_FILE_LIST)
        print("Saving brain file:", BRAIN_FILE)
        k.saveBrain(BRAIN_FILE)

        print("Loaded AIML files:")
        for file in k.getSessionData("activefiles"):
            print(file)
    except Exception as e:
        print("Error loading or reloading brain:", str(e))

def run_flask():
    try:
        app.run(host='127.0.0.1', port=5000)
    except Exception as e:
        print("Flask app failed to run:", str(e))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/get")
def get_bot_response():
    query = request.args.get('msg')

    # Dictionary to store replacements and their priorities
    replacements = {
        r'\b(?:\w+\s+)*(BACHELOR|BACHELORS|BE|BTECH)(?:\s+\w+)*\b': ('BACHELORS PROGRAMMES', 12),

        r'\b(?:\w+\s+)*(hello|hi|hey|helo|hei|hie)(?:\s+\w+)*\b': ('hello', 25),
        r'\b(?:\w+\s+)*(thanku|thank|thanks|tx)(?:\s+\w+)*\b': ('THANKYOU', 41),

        r'\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|computer|COMP|COM|CSE|CS|f|science)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|computer|COMP|COM|CSE|CS|f|science)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(science|computer|COMP|COM|CSE|CS|f|teacher|teachers|faculty|faculties|staff|staffs)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|computer|COMP|COM|CSE|CS|f|science)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('FCOMPUTER', 13),
        r'\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|CIVIL)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|CIVIL)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(CIVIL|teacher|teachers|faculty|faculties|staff|staffs)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|CIVIL)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('FCIVIL', 7),
        r'\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|MECHANICAL|mech)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|MECHANICAL|mech)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(MECHANICAL|mech|teacher|teachers|faculty|faculties|staff|staffs)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|MECHANICAL|mech)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('FMECHANICAL', 4),
        r'\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|E&TC|ENTC|ELECTRONICS|TELECOMMUNICATION)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|E&TC|ENTC|ELECTRONICS|TELECOMMUNICATION)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(E&TC|ENTC|ELECTRONICS|TELECOMMUNICATION|teacher|teachers|faculty|faculties|staff|staffs)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|E&TC|ENTC|ELECTRONICS|TELECOMMUNICATION)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('FELECTRONICS', 5),
        r'\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|ELE|electrical)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|ELE|electrical)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(ELE|electrical|teacher|teachers|faculty|faculties|staff|staffs)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|ELE|electrical)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('FELECTRICAL', 6),
        r'\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|FIRST|FE)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|FIRST|FE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(FIRST|FE|teacher|teachers|faculty|faculties|staff|staffs)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|FIRST|FE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('FFirst Year B.Tech', 3),
        r'\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|LBRY|LIBRARY)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|LBRY|LIBRARY)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(LBRY|LIBRARY|teacher|teachers|faculty|faculties|staff|staffs)\b(?:(?!\b(?:\w+\s+)*(teacher|teachers|faculty|faculties|staff|staffs|LBRY|LIBRARY)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('FLIBRARY', 8),
        r'\b(?:\w+\s+)*(faculty|faculties|staff|staffs|non)\b(?:(?!\b(?:\w+\s+)*(faculty|faculties|staff|staffs|non)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(non|f|faculty|faculties|staff|staffs)\b(?:(?!\b(?:\w+\s+)*(faculty|faculties|staff|staffs|non)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('non teaching', 15),
        r'\b(?:\w+\s+)*(faculty|faculties|staff|staffs|F)(?:\s+\w+)*\b': ('FACULTY', 30),

        r'\b(?:\w+\s+)*(fee|fees|A)(?:\s+\w+)*\b': ('FEES', 39),
        r'\b(?:\w+\s+)*(FEES|FEE|FIRST|ONE|FE|1)\b(?:(?!\b(?:\w+\s+)*(FEES|FEE|FIRST|ONE|FE|1)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(FIRST|ONE|FE|1|FEES|FEE)\b(?:(?!\b(?:\w+\s+)*(FEES|FEE|FIRST|ONE|FE|1)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('FE', 9),
        r'\b(?:\w+\s+)*(FEES|FEE|SECOND|TWO|SE|2)\b(?:(?!\b(?:\w+\s+)*(FEES|FEE|SECOND|TWO|SE|2)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(SECOND|TWO|SE|2|FEES|FEE)\b(?:(?!\b(?:\w+\s+)*(FEES|FEE|SECOND|TWO|SE|2)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('SE', 10),
        r'\b(?:\w+\s+)*(FEES|FEE|THREE|THIRD|TE|3)\b(?:(?!\b(?:\w+\s+)*(FEES|FEE|THREE|THIRD|TE|3)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(THREE|THIRD|TE|3|FEES|FEE)\b(?:(?!\b(?:\w+\s+)*(FEES|FEE|THREE|THIRD|TE|3)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('TE', 11),
        r'\b(?:\w+\s+)*(FEES|FEE|FOUR|fourth|BE|BTECH|ENGINEERING|4|final)\b(?:(?!\b(?:\w+\s+)*(FEES|FEE|FOUR|fourth|BE|BTECH|ENGINEERING|4|final)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(final|FOUR|fourth|BE|BTECH|ENGINEERING|4|FEES|FEE)\b(?:(?!\b(?:\w+\s+)*(FEES|FEE|FOUR|fourth|BE|BTECH|ENGINEERING|4|final)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('FBTECH', 1),
        r'\b(?:\w+\s+)*(FEES|FEE|MTECH|MASTER)\b(?:(?!\b(?:\w+\s+)*(FEES|FEE|MTECH|MASTER)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(MTECH|MASTER|FEES|FEE)\b(?:(?!\b(?:\w+\s+)*(FEES|FEE|MTECH|MASTER)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('FMTECH', 29),

        r'\b(?:\w+\s+)*(events|B|festival)(?:\s+\w+)*\b': ('EVENTS', 44),
        r'\b(?:\w+\s+)*(carnival)(?:\s+\w+)*\b': ('CARNIVAL', 50),
        r'\b(?:\w+\s+)*(HACKATHON)(?:\s+\w+)*\b': ('HACKATHON', 16),
        r'\b(?:\w+\s+)*(INFRASTRUCTURE|ENVIRONMENT|C)(?:\s+\w+)*\b': ('INFRASTRUCTURE', 17),

        r'\b(?:\w+\s+)*(CAMPUS)(?:\s+\w+)*\b': ('CAMPUS TOUR', 19),
        r'\b(?:\w+\s+)*(HOSTEL)(?:\s+\w+)*\b': ('HOSTEL FACILITY', 20),
        r'\b(?:\w+\s+)*(CANTEEN|CANTEN)(?:\s+\w+)*\b': ('CANTEEN', 21),
        r'\b(?:\w+\s+)*(PRINCIPAL)(?:\s+\w+)*\b': ('PRINCIPAL', 22),
        r'\b(?:\w+\s+)*(ACADEMIC|D)(?:\s+\w+)*\b': ('ACADEMIC', 23),
        r'\b(?:\w+\s+)*(ADMISSIONS|ADMISSION)(?:\s+\w+)*\b': ('ADMISSIONS', 24),
        r'\b(?:\w+\s+)*(BACHELOR|BACHELORS|BE|BTECH)(?:\s+\w+)\s+(?:\w+\s+)*(ELIGIBILITY|ELIGIBLE)(?:\s+\w+)*\s+(?:\w+\s+)*(BACHELOR|BACHELORS|BE|BTECH)(?:\s+\w+)*\b': ('ELIGIBILITY BACHELORS', 26),
        r'\b(?:\w+\s+)*(SYLLABUS)(?:\s+\w+)*\b': ('SYLLABUS', 27),
        r'\b(?:\w+\s+)*(QUESTION|PAPERS|PAPER|QUESTION PAPER|QUESTION PAPERS)(?:\s+\w+)*\b': ('QUESTION PAPERS', 29),
        r'\b(?:\w+\s+)*(ENQUIRY FORM|ENQUIRY)(?:\s+\w+)*\b': ('ENQUIRY FORM', 34),

        r'\b(?:\w+\s+)*(RECRUITERS|RECRUITER)(?:\s+\w+)*\b': ('RECRUITERS', 32),
        r'\b(?:\w+\s+)*(COMPANY|LOGOS|LOGO|COMPANIES)(?:\s+\w+)*\b': ('COMPANY LOGOS', 18),
        r'\b(?:\w+\s+)*(INTERNSHIPS|INTERNSHIP)(?:\s+\w+)*\b': ('INTERNSHIPS', 28),
        r'\b(?:\w+\s+)*(MTECH|MASTER|M TECH|M.TECH)(?:\s+\w+)*\b': ('MASTERS PROGRAMMES', 31),


        r'\b(?:\w+\s+)*(skn|long|full)\b(?:(?!\b(?:\w+\s+)*(skn|long|full)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(long|full|skn)\b(?:(?!\b(?:\w+\s+)*(skn|long|full)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('SKN', 42),
        r'\b(?:\w+\s+)*(computer|COMP|COM|CSE|CS|SCIENCE)(?:\s+\w+)*\b': ('COMPUTER SCIENCE', 35),
        r'\b(?:\w+\s+)*(CIVIL)(?:\s+\w+)*\b': ('CIVIL', 36),
        r'\b(?:\w+\s+)*(MECHANICAL|mech)(?:\s+\w+)*\b': ('Mechanical', 37),
        r'\b(?:\w+\s+)*(E&TC|ENTC|ELECTRONICS|TELECOMMUNICATION)(?:\s+\w+)*\b': ('ELECTRONICS', 38),
        r'\b(?:\w+\s+)*(ELE|electrical)(?:\s+\w+)*\b': ('ELECTRICAL', 39),
        r'\b(?:\w+\s+)*(DEPARTMENTS|DEP|DEPARTMENT)(?:\s+\w+)*\b': ('DEPARTMENTS', 40),


        r'\b(?:\w+\s+)*(LBRY|LIBRARY)(?:\s+\w+)*\b': ('LIBRARY', 45),
        r'\b(?:\w+\s+)*(WEENGS|wing|wings|weeng)(?:\s+\w+)*\b': ('WEENGS', 46),
        r'\b(?:\w+\s+)*(SPECTRUM)(?:\s+\w+)*\b': ('SPECTRUM', 14),
        r'\b(?:\w+\s+)*(mess)(?:\s+\w+)*\b': ('mess', 57),
        r'\b(?:\w+\s+)*(branches|branch|branchs)(?:\s+\w+)*\b': ('branch', 48),
        r'\b(?:\w+\s+)*(intake|places|vacancy)(?:\s+\w+)*\b': ('INTAKE', 47),
        r'\b(?:\w+\s+)*(ESTABLISHMENT|Established|opened|open|Sinhgad|SKNSCOE)\b(?:(?!\b(?:\w+\s+)*(ESTABLISHMENT|Established|opened|open|Sinhgad|SKNSCOE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(Sinhgad|SKNSCOE|ESTABLISHMENT|Established|opened|open)\b(?:(?!\b(?:\w+\s+)*(ESTABLISHMENT|Established|opened|open|Sinhgad|SKNSCOE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('ESTABLISHMENT DATE', 33),

        r'\b(?:\w+\s+)*(vision|Sinhgad|SKNSCOE)\b(?:(?!\b(?:\w+\s+)*(vision|Sinhgad|SKNSCOE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(Sinhgad|SKNSCOE|vision)\b(?:(?!\b(?:\w+\s+)*(vision|Sinhgad|SKNSCOE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('vision', 51),
        r'\b(?:\w+\s+)*(Mission|Mision|Sinhgad|SKNSCOE)\b(?:(?!\b(?:\w+\s+)*(Mission|Mision|Sinhgad|SKNSCOE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(Sinhgad|SKNSCOE|Mission|Mision)\b(?:(?!\b(?:\w+\s+)*(Mission|Mision|Sinhgad|SKNSCOE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('mission', 52),
        r'\b(?:\w+\s+)*(Quality|Policy|Sinhgad|SKNSCOE)\b(?:(?!\b(?:\w+\s+)*(Quality|Policy|Sinhgad|SKNSCOE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(Sinhgad|SKNSCOE|Quality|Policy)\b(?:(?!\b(?:\w+\s+)*(Quality|Policy|Sinhgad|SKNSCOE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('Quality Policy', 53),
        r'\b(?:\w+\s+)*(pos|Outcomes|Sinhgad|SKNSCOE)\b(?:(?!\b(?:\w+\s+)*(pos|Outcomes|Sinhgad|SKNSCOE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?(Sinhgad|SKNSCOE|pos|Outcomes)\b(?:(?!\b(?:\w+\s+)*(pos|Outcomes|Sinhgad|SKNSCOE)\b)(?!.*\bengineering\b).)*(?:\w+\s+)*?\b': ('pos', 54),
        r'\b(?:\w+\s+)*(outcomes|outcome)(?:\s+\w+)*\b': ('pos', 54),

        r'\b(?:\w+\s+)*(Sinhgad|SKNSCOE)(?:\s+\w+)*\b': ('SKN Sinhgad', 58),

        r'\b(?:\w+\s+)*(cell)(?:\s+\w+)*\b': ('cell', 49),

        r'\b(?:\w+\s+)*(PLACEMENTS|PLACEMENT|E)(?:\s+\w+)*\b': ('PLACEMENTS', 57),
        r'\b(?:\w+\s+)*(founder|owner)(?:\s+\w+)*\b': ('founder', 55),
        r'\b(?:\w+\s+)*(training and placement officer|tpo)(?:\s+\w+)*\b': ('TPO', 56),
        r'\b(?:\w+\s+)*(placed)(?:\s+\w+)*\b': ('placed', 59),

    }

    # Apply replacements in order of priority
    for pattern, (replacement, priority) in sorted(replacements.items(), key=lambda x: x[1][1]):
        query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)

    response = process_input(query)
    response_with_line_breaks = response.replace("ln", "<br/>")

    return response_with_line_breaks if response_with_line_breaks else "Information not found. Please check the Spelling or check on this website: https://sknscoe.ac.in/"

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
