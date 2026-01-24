function switchTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

function clearMessage(elementId) {
    const msg = document.getElementById(elementId);
    msg.classList.remove('success', 'error');
    msg.textContent = '';
}

function showMessage(elementId, message, type) {
    const msg = document.getElementById(elementId);
    msg.textContent = message;
    msg.className = `message ${type}`;
}

async function saveRecord() {
    const name = document.getElementById('save-name').value.trim();
    const course = document.getElementById('save-course').value.trim();
    const score = document.getElementById('save-score').value.trim();
    
    if (!name || !course || !score) {
        showMessage('save-message', '⚠️ All fields are required!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/save-record', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                course: course,
                score: score
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('save-message', '✅ ' + data.message, 'success');
            document.getElementById('save-name').value = '';
            document.getElementById('save-course').value = '';
            document.getElementById('save-score').value = '';
        } else {
            showMessage('save-message', '❌ ' + data.message, 'error');
        }
    } catch (error) {
        showMessage('save-message', '❌ Error: ' + error.message, 'error');
    }
}

async function calculateGPA() {
    const name = document.getElementById('gpa-name').value.trim();
    
    if (!name) {
        alert('⚠️ Please enter a student name!');
        return;
    }
    
    const resultBox = document.getElementById('gpa-result');
    resultBox.classList.remove('show');
    
    try {
        const response = await fetch('/api/calculate-gpa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultBox.innerHTML = `
                <h3>📊 GPA Calculation Result</h3>
                <p><strong>Student:</strong> ${name}</p>
                <div class="gpa-value">${data.gpa}</div>
                <p><strong>Total Scores Recorded:</strong> ${data.score_count}</p>
            `;
            resultBox.classList.add('show');
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

async function showChart() {
    const name = document.getElementById('chart-name').value.trim();
    
    if (!name) {
        alert('⚠️ Please enter a student name!');
        return;
    }
    
    const chartContainer = document.getElementById('chart-container');
    chartContainer.classList.remove('show');
    chartContainer.innerHTML = '<p style="text-align: center; color: #666;">Loading chart...</p>';
    chartContainer.classList.add('show');
    
    try {
        const response = await fetch('/api/get-chart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            let coursesList = data.courses.map((course, idx) => 
                `<li>${course}: ${data.scores[idx]}/100</li>`
            ).join('');
            
            chartContainer.innerHTML = `
                <img src="${data.chart}" alt="Grade Chart">
                <div class="chart-info">
                    <p><strong>📈 Grade Summary for ${name}</strong></p>
                    <ul style="list-style-position: inside; text-align: left;">
                        ${coursesList}
                    </ul>
                </div>
            `;
        } else {
            chartContainer.innerHTML = `<p style="color: #721c24;">❌ ${data.message}</p>`;
        }
    } catch (error) {
        chartContainer.innerHTML = `<p style="color: #721c24;">❌ Error: ${error.message}</p>`;
    }
}
