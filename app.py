from flask import Flask, render_template, request, jsonify
import PyPDF2
import docx
import groq
import os
from gtts import gTTS
import tempfile
import base64
import io
from io import BytesIO
#from pydub import AudioSegment
import shutil

app = Flask(__name__)

# Set up Groq client

client = groq.Groq(api_key=os.environ["GROQ_API_KEY"])


def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def evaluate_resume(resume_text, job_role, experience_level):
    prmpt = f"""
        You're two senior HR executives (both ladies) evaluating a candidate's resume for the role of {job_role}. It is a {experience_level} level job.
        Here is the candidate's resume:

        {resume_text}

        Now, start a humorous conversation between 2 HRs talking to each other where you provide critical feedback, roast the resume, and suggest improvements.
        -Make the conversations in a communicative tone
        -Do not use markdown any other formatting in your responses.
        -Do not write anything in braces
        -The output should be like - "HR1: <text>\nHR2: <text>\n...."
        -Do not forget to suggest the improvements to be made in the resume in a conversational way
        -This is not a conversation between HR and candidate, this is a conversation between two HR executives.
        """


    completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prmpt}],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )
    # Gather the output as chunks of text (streaming mode)
    hr_conversation = ""
    for chunk in completion:
        hr_conversation += chunk.choices[0].delta.content or ""

    return hr_conversation




@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    file = request.files['resume']
    job_role = request.form['job_role']
    experience_level = request.form['experience_level']

    # Create a BytesIO object to store the file content
    file_content = io.BytesIO(file.read())

    if file.filename.endswith('.pdf'):
        resume_text = extract_text_from_pdf(file_content)
    elif file.filename.endswith('.docx'):
        resume_text = extract_text_from_docx(file_content)
    else:
        return jsonify({'error': 'Invalid file format'})

    evaluation = evaluate_resume(resume_text, job_role, experience_level)
   
    return jsonify({
        'evaluation': evaluation,
        #'audio': audio_base64
    })

#if __name__ == '__main__':
 #   app.run(debug=True)

