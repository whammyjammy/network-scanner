from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_socketio import SocketIO, emit
import subprocess
import json
import os
import threading
import queue
from datetime import datetime
from pathlib import Path
import re
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vuln-scanner-secret-key-change-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")

SCANS_DIR = Path("/output")
SCANS_DIR.mkdir(exist_ok=True)

# Store active scans
active_scans = {}
scan_queue = queue.Queue()

class ScanJob:
    def __init__(self, scan_id, target):
        self.scan_id = scan_id
        self.target = target
        self.status = "queued"
        self.progress = 0
        self.results = {
            "target": target,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "ports": [],
            "vulnerabilities": [],
            "logs": []
        }
        self.output_dir = SCANS_DIR / scan_id
        self.output_dir.mkdir(exist_ok=True)
    
    def log(self, message, level="info"):
        """Add log message and emit to client"""
        log_entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message
        }
        self.results["logs"].append(log_entry)
        socketio.emit('scan_log', {
            'scan_id': self.scan_id,
            'log': log_entry
        })
    
    def update_progress(self, progress, status):
        """Update scan progress"""
        self.progress = progress
        self.status = status
        socketio.emit('scan_progress', {
            'scan_id': self.scan_id,
            'progress': progress,
            'status': status
        })
    
    def run_rustscan(self):
        """Run RustScan for port discovery"""
        self.log("Starting RustScan - Fast Port Discovery", "info")
        self.update_progress(10, "scanning_ports")
        
        output_file = self.output_dir / f"rustscan_{self.results['timestamp']}.txt"
        
        try:
            cmd = [
                "rustscan",
                "-a", self.target,
                "--ulimit", "5000",
                "--", "-sV", "-sC", "-oN", str(output_file)
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            for line in process.stdout:
                self.log(line.strip(), "debug")
                if "Open" in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        port = match.group(1)
                        if port not in self.results["ports"]:
                            self.results["ports"].append(port)
                            self.log(f"Found open port: {port}", "success")
                            socketio.emit('port_found', {
                                'scan_id': self.scan_id,
                                'port': port
                            })
            
            process.wait()
            self.update_progress(40, "ports_scanned")
            self.log(f"RustScan completed. Found {len(self.results['ports'])} open ports", "success")
            
        except Exception as e:
            self.log(f"RustScan error: {str(e)}", "error")
    
    def run_nikto(self):
        """Run Nikto web vulnerability scanner"""
        web_ports = [p for p in self.results["ports"] if p in ["80", "443", "8080", "8443"]]
        
        if not web_ports:
            self.log("No web ports detected, skipping Nikto scan", "warning")
            self.update_progress(80, "completed_no_web")
            return
        
        self.log(f"Starting Nikto scan on {len(web_ports)} web port(s)", "info")
        self.update_progress(50, "scanning_web")
        
        for i, port in enumerate(web_ports):
            protocol = "https" if port in ["443", "8443"] else "http"
            url = f"{protocol}://{self.target}:{port}"
            
            self.log(f"Scanning {url}...", "info")
            output_file = self.output_dir / f"nikto_{port}_{self.results['timestamp']}.txt"
            
            try:
                cmd = [
                    "nikto",
                    "-h", url,
                    "-o", str(output_file),
                    "-Format", "txt"
                ]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                for line in process.stdout:
                    self.log(line.strip(), "debug")
                    if "OSVDB" in line or "CVE" in line or "+" in line:
                        vuln = {
                            "port": port,
                            "finding": line.strip()
                        }
                        self.results["vulnerabilities"].append(vuln)
                        socketio.emit('vulnerability_found', {
                            'scan_id': self.scan_id,
                            'vulnerability': vuln
                        })
                
                process.wait()
                progress = 50 + int((i + 1) / len(web_ports) * 30)
                self.update_progress(progress, "scanning_web")
                
            except Exception as e:
                self.log(f"Nikto scan error on port {port}: {str(e)}", "error")
        
        self.log(f"Nikto completed. Found {len(self.results['vulnerabilities'])} potential issues", "success")
    
    def generate_report(self):
        """Generate final report"""
        self.log("Generating vulnerability report...", "info")
        self.update_progress(90, "generating_report")
        
        report_file = self.output_dir / f"vulnerability_report_{self.results['timestamp']}.txt"
        json_file = self.output_dir / f"scan_results_{self.results['timestamp']}.json"
        
        # Generate text report
        with open(report_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("VULNERABILITY ASSESSMENT REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Target: {self.target}\n")
            f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Scan ID: {self.scan_id}\n\n")
            
            f.write("-"*70 + "\n")
            f.write("OPEN PORTS\n")
            f.write("-"*70 + "\n")
            if self.results["ports"]:
                for port in sorted(self.results["ports"], key=int):
                    f.write(f"  • Port {port}/tcp\n")
            else:
                f.write("  No open ports detected\n")
            
            f.write("\n" + "-"*70 + "\n")
            f.write("VULNERABILITY SUMMARY\n")
            f.write("-"*70 + "\n")
            if self.results["vulnerabilities"]:
                f.write(f"Total Findings: {len(self.results['vulnerabilities'])}\n\n")
                for i, vuln in enumerate(self.results["vulnerabilities"], 1):
                    f.write(f"{i}. Port {vuln['port']}\n")
                    f.write(f"   {vuln['finding']}\n\n")
            else:
                f.write("  No vulnerabilities detected by automated scan\n")
            
            f.write("\n" + "-"*70 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("-"*70 + "\n")
            f.write("1. Review all open ports and close unnecessary services\n")
            f.write("2. Apply security patches for identified vulnerabilities\n")
            f.write("3. Implement network segmentation and firewall rules\n")
            f.write("4. Conduct manual penetration testing for validation\n")
            f.write("5. Perform regular security assessments\n\n")
        
        # Save JSON
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log("Report generation completed", "success")
        self.update_progress(100, "completed")
    
    def run(self):
        """Execute full scan"""
        try:
            self.log(f"Starting vulnerability scan for {self.target}", "info")
            self.update_progress(5, "initializing")
            
            self.run_rustscan()
            self.run_nikto()
            self.generate_report()
            
            self.log("Vulnerability assessment completed successfully!", "success")
            self.status = "completed"
            
        except Exception as e:
            self.log(f"Scan failed: {str(e)}", "error")
            self.status = "failed"
            self.update_progress(0, "failed")

def scan_worker():
    """Background worker for processing scans"""
    while True:
        scan_job = scan_queue.get()
        if scan_job is None:
            break
        
        active_scans[scan_job.scan_id] = scan_job
        scan_job.run()
        scan_queue.task_done()

# Start background worker
worker_thread = threading.Thread(target=scan_worker, daemon=True)
worker_thread.start()

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def start_scan():
    """Start a new vulnerability scan"""
    data = request.get_json()
    target = data.get('target', '').strip()
    
    if not target:
        return jsonify({'error': 'Target is required'}), 400
    
    # Generate unique scan ID
    scan_id = str(uuid.uuid4())
    
    # Create and queue scan job
    scan_job = ScanJob(scan_id, target)
    active_scans[scan_id] = scan_job
    scan_queue.put(scan_job)
    
    return jsonify({
        'scan_id': scan_id,
        'target': target,
        'status': 'queued'
    })

@app.route('/api/scan/<scan_id>')
def get_scan_status(scan_id):
    """Get current status of a scan"""
    if scan_id not in active_scans:
        return jsonify({'error': 'Scan not found'}), 404
    
    scan = active_scans[scan_id]
    return jsonify({
        'scan_id': scan_id,
        'target': scan.target,
        'status': scan.status,
        'progress': scan.progress,
        'ports': scan.results['ports'],
        'vulnerabilities': len(scan.results['vulnerabilities']),
        'logs': scan.results['logs'][-50:]  # Last 50 logs
    })

@app.route('/api/scans')
def list_scans():
    """List all scans"""
    scans = []
    for scan_id, scan in active_scans.items():
        scans.append({
            'scan_id': scan_id,
            'target': scan.target,
            'status': scan.status,
            'progress': scan.progress,
            'timestamp': scan.results['timestamp']
        })
    return jsonify({'scans': scans})

@app.route('/api/scan/<scan_id>/report')
def download_report(scan_id):
    """Download scan report"""
    if scan_id not in active_scans:
        return jsonify({'error': 'Scan not found'}), 404
    
    scan = active_scans[scan_id]
    report_file = scan.output_dir / f"vulnerability_report_{scan.results['timestamp']}.txt"
    
    if not report_file.exists():
        return jsonify({'error': 'Report not available yet'}), 404
    
    return send_file(report_file, as_attachment=True)

@app.route('/api/scan/<scan_id>/json')
def download_json(scan_id):
    """Download scan results as JSON"""
    if scan_id not in active_scans:
        return jsonify({'error': 'Scan not found'}), 404
    
    scan = active_scans[scan_id]
    return jsonify(scan.results)

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'message': 'Connected to scanner'})

@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to scan updates"""
    scan_id = data.get('scan_id')
    if scan_id in active_scans:
        emit('subscribed', {'scan_id': scan_id})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)