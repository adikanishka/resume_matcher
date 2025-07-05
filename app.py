from flask import Flask, render_template, request, redirect, url_for
import os
import PyPDF2 
import json
from utils import generate_tips 

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # ensure folder exists

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return "No file part", 400

    file = request.files['resume']

    if file.filename == '':
        return "No selected file", 400

    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        # Extract text from PDF
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            resume_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    resume_text += text

        #  Check if we got any text at all
        if not resume_text.strip():
            return "<h2>Could not extract text from the resume. Try another PDF.</h2>"

        resume_text = resume_text.lower()

        # ✅ Load job roles
        with open("jobs_data.json", "r") as jf:
            jobs = json.load(jf)

        matched_roles = []
        for role, keywords in jobs.items():
            match_count = sum(1 for kw in keywords if kw.lower() in resume_text)
            if match_count > 0:
                matched_roles.append((role, match_count))

        matched_roles.sort(key=lambda x: x[1], reverse=True)

        with open("jobs_data.json", "r") as sf:
            role_skills = json.load(sf)

        suggested_skills = {}

        for role, _ in matched_roles:
            expected_skills = role_skills.get(role, [])
            missing_skills = []
            for skill in expected_skills:
                if skill.lower() not in resume_text:
                    missing_skills.append(skill)
            if missing_skills:
                suggested_skills[role] = missing_skills
        # Prepare data for chart
        chart_data = matched_roles[:10]
        chart_labels = [role for role, score in chart_data]
        chart_values = [score for role, score in chart_data]


        # ✅ Smart Tip Generator — NLP + rules
        tips, orgs, detected_degrees = generate_tips(resume_text)

        return render_template(
            "result.html",
            roles=matched_roles,
            tips=tips,
            orgs=orgs,
            degrees=detected_degrees,
            chart_labels=chart_labels,
            chart_values=chart_values,
            suggestions=suggested_skills
        )

    else:
        return "Invalid file type. Only PDF allowed.", 400

if __name__ == '__main__':
    app.run(debug=True)

