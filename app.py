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
from pydub import AudioSegment
#AudioSegment.converter = r"C:\Users\Hp840\OneDrive\Desktop\ffmpeg-7.1.tar.xz"

app = Flask(__name__)

# Set up Groq client

#client = groq.Groq(api_key=os.environ["GROQ_API_KEY"])
client = groq.Groq(api_key="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")

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
        You're two senior HR executives evaluating a candidate's resume for the role of {job_role}. It is a {experience_level} level job.
        Here is the candidate's resume:

        {resume_text}

        Now, start a humorous conversation between 2 HRs talking to each other where you provide critical feedback, roast the resume, and suggest improvements.
        -Make the conversations in a communicative tone
        -Do not use markdown, emojis, or other formatting in your responses. Respond in a way easily spoken by text-to-speech software
        -Do not write anything in braces
        -Do not use any emotions like (laughs) in your responses
        -The output should be like - "HR1: <text>\nHR2: <text>\n...."
        -Do not forget to suggest the improvements
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


# Comment out the text_to_speech_mixed function
"""
def text_to_speech_mixed(hr_feedback):
    lines = hr_feedback.split('\n')
    combined_audio = AudioSegment.empty()

    for line in lines:
        if line.startswith("HR1:") or line.startswith("HR2:"):
            hr_text = line.split(":", 1)[1].strip()
            if hr_text:
                tts = gTTS(hr_text, lang='en', tld='com' if line.startswith("HR1:") else 'co.in', slow=False)
                mp3_fp = BytesIO()
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)
                audio = AudioSegment.from_mp3(mp3_fp)
                combined_audio += audio

    output_buffer = BytesIO()
    combined_audio.export(output_buffer, format="mp3")
    return output_buffer.getvalue()
"""

@app.route('/')
def index():
    return render_template('index.html')

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
    #audio_data = text_to_speech_mixed(evaluation)

    # Encode audio data to base64
    #audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    return jsonify({
        'evaluation': evaluation,
        #'audio': audio_base64
    })

#if __name__ == '__main__':
 #   app.run(debug=True)

