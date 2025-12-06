// Network Scanner - Client-side JavaScript
const socket = io();
let currentScanId = null;

// Socket.IO Event Handlers
socket.on('connect', () => {
    console.log('Connected to scanner');
});

socket.on('scan_progress', (data) => {
    if (data.scan_id === currentScanId) {
        updateProgress(data.progress, data.status);
    }
});

socket.on('scan_log', (data) => {
    if (data.scan_id === currentScanId) {
        addLog(data.log);
    }
});

socket.on('port_found', (data) => {
    if (data.scan_id === currentScanId) {
        addPort(data.port);
    }
});

socket.on('vulnerability_found', (data) => {
    if (data.scan_id === currentScanId) {
        addVulnerability(data.vulnerability);
    }
});

// Form Submission Handler
document.getElementById('scanForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const target = document.getElementById('target').value;
    const startBtn = document.getElementById('startBtn');
    
    startBtn.disabled = true;
    startBtn.textContent = 'Starting Scan...';
    
    try {
        const response = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target })
        });
        
        const data = await response.json();
        currentScanId = data.scan_id;
        
        document.getElementById('results').classList.add('active');
        document.getElementById('scanInfo').innerHTML = `
            <h3>Target: ${data.target}</h3>
            <span class="status-badge status-${data.status}">Status: ${data.status}</span>
            <p>Scan ID: ${data.scan_id}</p>
        `;
        
        document.getElementById('portList').innerHTML = '';
        document.getElementById('vulnList').innerHTML = '';
        document.getElementById('logConsole').innerHTML = '';
        
        socket.emit('subscribe', { scan_id: currentScanId });
        
    } catch (error) {
        alert('Failed to start scan: ' + error.message);
    } finally {
        startBtn.disabled = false;
        startBtn.textContent = 'Start Vulnerability Scan';
    }
});

// Update Progress Bar and Status
function updateProgress(progress, status) {
    const progressBar = document.getElementById('progressBar');
    progressBar.style.width = progress + '%';
    progressBar.textContent = progress + '%';
    
    const statusBadge = document.querySelector('.status-badge');
    if (statusBadge) {
        statusBadge.className = `status-badge status-${status}`;
        statusBadge.textContent = 'Status: ' + status.replace('_', ' ');
    }
    
    // Show/hide cancel button
    const cancelBtn = document.getElementById('cancelBtn');
    if (status === 'queued' || status === 'initializing' || status.includes('scanning')) {
        cancelBtn.style.display = 'block';
    } else {
        cancelBtn.style.display = 'none';
    }
    
    if (progress === 100 || status === 'completed') {
        document.getElementById('downloadButtons').style.display = 'flex';
    }
}

// Add Log Entry
function addLog(log) {
    const logConsole = document.getElementById('logConsole');
    const entry = document.createElement('div');
    entry.className = `log-entry log-${log.level}`;
    entry.textContent = `[${log.timestamp}] ${log.message}`;
    logConsole.appendChild(entry);
    logConsole.scrollTop = logConsole.scrollHeight;
}

// Add Port to List
function addPort(port) {
    const portList = document.getElementById('portList');
    if (portList.children.length === 1 && portList.children[0].textContent === 'Scanning...') {
        portList.innerHTML = '';
    }
    
    const li = document.createElement('li');
    li.className = 'port-item';
    li.textContent = `Port ${port}/tcp`;
    portList.appendChild(li);
}

// Add Vulnerability to List
function addVulnerability(vuln) {
    const vulnList = document.getElementById('vulnList');
    if (vulnList.children.length === 1 && vulnList.children[0].textContent === 'Scanning...') {
        vulnList.innerHTML = '';
    }
    
    const li = document.createElement('li');
    li.className = 'vuln-item';
    li.textContent = `Port ${vuln.port}: ${vuln.finding}`;
    vulnList.appendChild(li);
}

// Download Report
function downloadReport() {
    window.location.href = `/api/scan/${currentScanId}/report`;
}
