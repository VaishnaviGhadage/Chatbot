import csv
import os
import pandas as pd
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from threading import Thread

app = Flask(__name__)
BRAIN_FILE = "./pretrained_model/aiml_pretrained_model.brn"
LEARNING_FILE_LIST = "./pretrained_model/learningFileList.aiml"
AIML_CSV_FILE = "./pretrained_model/aiml_data.csv"
model = None
vectorizer = None

def load_or_reload_brain():
    try:
        if os.path.exists(BRAIN_FILE):
            os.remove(BRAIN_FILE)
            print("Removed existing brain file:", BRAIN_FILE)
        print("Parsing AIML files")
        parse_aiml_files(LEARNING_FILE_LIST, AIML_CSV_FILE)
        print("AIML files parsed and CSV file created:", AIML_CSV_FILE)
    except Exception as e:
        print("Error loading or reloading brain:", str(e))

def parse_aiml_files(aiml_file, csv_file):
    aiml_data = []
    tree = ET.parse(aiml_file)
    root = tree.getroot()
    for category in root.findall('.//category'):
        pattern = category.find('.//pattern').text.strip()
        template = category.find('.//template').text.strip()
        aiml_data.append({'Pattern': pattern, 'Response': template})
    write_to_csv(aiml_data, csv_file)

def write_to_csv(data, csv_file):
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Pattern', 'Response'])
        writer.writeheader()
        writer.writerows(data)

def load_dataset_and_train_model():
    global model, vectorizer
    try:
        if not os.path.exists(AIML_CSV_FILE):
            print("Error: AIML CSV file does not exist.")
            return

        aiml_data = pd.read_csv(AIML_CSV_FILE)
        print("Loaded AIML data from CSV file:")
        print(aiml_data.head())

        if aiml_data.empty:
            print("Error: AIML CSV file is empty.")
            return

        # Drop rows with NaN values in 'Response' column
        aiml_data.dropna(subset=['Response'], inplace=True)

        if 'Pattern' not in aiml_data.columns or 'Response' not in aiml_data.columns:
            print("Error: Columns 'Pattern' and 'Response' not found in the CSV file.")
            return

        if aiml_data.empty:
            print("Error: No valid data after removing rows with NaN values.")
            return

        X = aiml_data['Pattern']
        y = aiml_data['Response']
        vectorizer = CountVectorizer()
        X_vectorized = vectorizer.fit_transform(X)
        model = MultinomialNB()
        model.fit(X_vectorized, y)
    except Exception as e:
        print("Error loading dataset and training model:", str(e))

def predict_response(user_input):
    global model, vectorizer
    try:
        if model is None:
            load_dataset_and_train_model()

        aiml_data = pd.read_csv(AIML_CSV_FILE)
        if aiml_data.empty:
            print("Error: AIML CSV file is empty.")
            return "Error: AIML CSV file is empty."

        if 'Pattern' not in aiml_data.columns or 'Response' not in aiml_data.columns:
            print("Error: Columns 'Pattern' and 'Response' not found in the CSV file.")
            return "Error: Columns 'Pattern' and 'Response' not found in the CSV file."

        input_vectorized = vectorizer.transform([user_input])
        prediction = model.predict(input_vectorized)
        print("Prediction:", prediction)
        matching_row = aiml_data.loc[aiml_data['Pattern'] == user_input]
        print("Matching row:", matching_row)
        predicted_response = matching_row['Response'].values[0] if not matching_row.empty else "Information not found."
        print("Predicted response:", predicted_response)
        return predicted_response
    except Exception as e:
        print("Error predicting response:", str(e))
        return "Error predicting response: " + str(e)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/get")
def get_bot_response():
    try:
        query = request.args.get('msg')
        response = predict_response(query)
        print("Response:", response)  # Debugging print
        return jsonify({"response": response})
    except Exception as e:
        print("Error in get_bot_response:", str(e))
        return jsonify({"response": "Error: " + str(e)})

@app.route("/reload_brain", methods=["POST"])
def reload_brain():
    try:
        Thread(target=load_or_reload_brain).start()
        return jsonify({"status": "Brain reload initiated."})
    except Exception as e:
        return jsonify({"status": f"Error: {str(e)}"})

if __name__ == "__main__":
    load_or_reload_brain()
    Thread(target=app.run, kwargs={'host': '127.0.0.1', 'port': 5000}).start()
