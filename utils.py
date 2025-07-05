import re
import spacy
import json

nlp = spacy.load("en_core_web_sm")

import spacy
import json
import re

import spacy
from spacy.cli import download

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def generate_tips(resume_text: str, tips_file='tips.json'):
    tips = []
    resume_text = resume_text.lower()

    # Load tips from JSON file
    with open(tips_file, 'r') as f:
        tip_rules = json.load(f)

    # Rule-based tips from JSON
    for rule in tip_rules:
        tip = rule["tip"]
        ttype = rule["type"]

        if ttype == "keyword_absence":
            if all(kw.lower() not in resume_text for kw in rule["keywords"]):
                tips.append(tip)

        elif ttype == "section_absence":
            if rule["keyword"].lower() not in resume_text:
                tips.append(tip)

        elif ttype == "soft_skills_absence":
            if all(skill not in resume_text for skill in rule["keywords"]):
                tips.append(tip)

        elif ttype == "formatting_check":
            lines = resume_text.splitlines()
            if all(re.match(rule["regex"], line) for line in lines if line.strip()):
                tips.append(tip)

    # 🔍 NLP: Extract ORG entities
    doc = nlp(resume_text)
    orgs = []
    for ent in doc.ents:
        if ent.label_ == "ORG":
            org_name = ent.text.strip().lower()
            # Filter out obvious false positives
            if (
                "gmail" not in org_name
                and len(org_name.split()) > 1  # Must be more than 1 word
                and not org_name.startswith("•")
            ):
                orgs.append(org_name)

    if not orgs:
        tips.append("Mention organizations (e.g., companies or colleges) you’ve worked or studied at.")

    # ✅ Manual degree detection via keyword matching
    degree_keywords = [
        'b.tech', 'm.tech', 'b.e', 'bsc', 'msc', 'mba', 'phd',
        'bachelor of science', 'bachelor of technology',
        'master of science', 'master of technology',
        'diploma', 'degree','graduate', 'postgraduate','undergraduate','high school', 'secondary school',
        'higher education', 'minor', 'major', 'associate degree', 'junior college',
        ]

    # If no degrees found → add tip
    if all(degree not in resume_text for degree in degree_keywords):
        tips.append("Include degrees or certifications to showcase your educational background.")

    # Extract which degrees we *did* find
    detected_degrees = []
    for keyword in degree_keywords:
    # Match as full word using regex (avoids partial word matches)
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, resume_text):
            detected_degrees.append(keyword)


    orgs = sorted(set([org.title() for org in orgs]))
    detected_degrees = sorted(set([deg.title() for deg in detected_degrees]))

    # Return smart tips + detected orgs + degrees
    return tips, orgs, detected_degrees
