document.getElementById('resume-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    var formData = new FormData(this);
    
    fetch('/evaluate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('evaluation-text').innerText = data.evaluation;
        document.getElementById('evaluation-audio').src = 'data:audio/mp3;base64,' + data.audio;
        document.getElementById('result').classList.remove('hidden');
    })
    .catch(error => console.error('Error:', error));
});