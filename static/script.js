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

    })
    .catch(error => console.error('Error:', error));
});
