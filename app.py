from flask import Flask, render_template, request
import PyPDF2
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database creation
conn = sqlite3.connect('database.db')

conn.execute("""
CREATE TABLE IF NOT EXISTS candidates(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
score INTEGER,
skills TEXT
)
""")

conn.close()

required_skills = [
    'python',
    'sql',
    'machine learning',
    'ai',
    'flask',
    'pandas'
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():

    file = request.files['resume']

    if file:

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        file.save(filepath)

        pdf_file = open(filepath, 'rb')

        reader = PyPDF2.PdfReader(pdf_file)

        text = ''

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        text = text.lower()

        found_skills = []

        score = 0

        for skill in required_skills:

            if skill in text:
                found_skills.append(skill)
                score += 1

        final_score = int((score / len(required_skills)) * 100)

        candidate_name = file.filename.split('.')[0]

        conn = sqlite3.connect('database.db')

        conn.execute(
            'INSERT INTO candidates(name, score, skills) VALUES (?, ?, ?)',
            (candidate_name, final_score, ', '.join(found_skills))
        )

        conn.commit()

        conn.close()

        return render_template(
            'result.html',
            name=candidate_name,
            score=final_score,
            skills=found_skills
        )

if __name__ == '__main__':
    app.run(debug=True)
