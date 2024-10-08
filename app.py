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
import shutil

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

def text_to_speech_mixed(hr_feedback, output_file="hr_feedback_combined.mp3"):
    # Split the feedback into lines
    lines = hr_feedback.split('\n')

    # Initialize an empty AudioSegment to store the combined audio
    combined_audio = AudioSegment.empty()

    # Loop through each line, generate audio based on HR1 or HR2, and concatenate
    for line in lines:
        if line.startswith("HR1:"):
            hr1_text = line.replace("HR1:", "").strip()
            if hr1_text:
                hr1_tts = gTTS(hr1_text, lang='en', slow=False)  # Default TTS for HR1
                # Use BytesIO to save audio in memory
                hr1_audio_buffer = BytesIO()
                hr1_tts.save(hr1_audio_buffer)
                hr1_audio_buffer.seek(0)  # Move to the start of the BytesIO buffer
                hr1_audio = AudioSegment.from_mp3(hr1_audio_buffer)  # Load the temporary audio
                combined_audio += hr1_audio  # Concatenate HR1 audio
        elif line.startswith("HR2:"):
            hr2_text = line.replace("HR2:", "").strip()
            if hr2_text:
                hr2_tts = gTTS(hr2_text, lang='en', tld='co.in', slow=False)  # Indian accent TTS for HR2
                # Use BytesIO to save audio in memory
                hr2_audio_buffer = BytesIO()
                hr2_tts.save(hr2_audio_buffer)
                hr2_audio_buffer.seek(0)  # Move to the start of the BytesIO buffer
                hr2_audio = AudioSegment.from_mp3(hr2_audio_buffer)  # Load the temporary audio
                combined_audio += hr2_audio  # Concatenate HR2 audio

    # Save the combined audio as a single output file
    combined_audio.export(output_file, format="mp3")  # Export combined audio
    print(f"Combined audio feedback saved as {output_file}")

    return output_file  # Return the output file path or handle it as needed


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
    audio_file_path = text_to_speech_mixed(evaluation)

    # Check if audio_file_path is None
    if audio_file_path is None:
        return jsonify({'error': 'Audio file could not be created'})

    # Read the audio file as bytes
    with open(audio_file_path, 'rb') as audio_file:
        audio_data = audio_file.read()

    # Ensure audio_data is bytes
    if isinstance(audio_data, str):
        return jsonify({'error': 'Audio data is not in bytes format'})

    # Encode audio data to base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    return jsonify({
        'evaluation': evaluation,
        'audio': audio_base64
    })

#if __name__ == '__main__':
 #   app.run(debug=True)

