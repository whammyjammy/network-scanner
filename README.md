# 🔒 Network Scanner

A comprehensive, web-based security assessment tool that combines **RustScan**, **Nikto**, and **Nmap** for network reconnaissance and vulnerability detection. Run professional-grade security scans through a modern web interface on any platform with Docker.

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Kali](https://img.shields.io/badge/Kali-268BEE?style=for-the-badge&logo=kalilinux&logoColor=white)

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Web Interface](#web-interface)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Security & Legal](#security--legal)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🌐 Web-Based Interface
- **Modern, Responsive UI**: Beautiful gradient design that works on all devices
- **Real-Time Updates**: WebSocket integration for live scan progress
- **Interactive Dashboard**: Visual progress bars and status indicators
- **Multiple Concurrent Scans**: Queue system for scanning multiple targets

### ⚡ Powerful Scanning Capabilities
- **Fast Port Discovery**: RustScan for rapid scanning of all 65,535 ports
- **Web Vulnerability Assessment**: Nikto for comprehensive web application testing
- **Service Detection**: Nmap integration for detailed service fingerprinting
- **Intelligent Reporting**: Both JSON and human-readable text formats

### 🔄 Real-Time Features
- Live port discovery notifications
- Vulnerability alerts as they're found
- Streaming console logs
- Progress tracking with percentage completion

### 📊 Comprehensive Reporting
- Timestamped scan results
- Organized output directories
- Downloadable text reports
- JSON export for automation
- Color-coded log levels

### 🐳 Containerized & Portable
- Runs on any platform with Docker
- Isolated environment with all tools included
- No dependency conflicts
- Easy deployment and distribution

## 🔧 Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 1.29 or higher (optional but recommended)
- **Disk Space**: ~2GB for the Docker image
- **Network Access**: Connectivity to target systems
- **Permissions**: Authorization to scan target networks

### Installing Docker

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)

**Windows:**
Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

### Installing Docker Compose

```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

## 📦 Installation

### Method 1: Clone and Build

```bash
# Clone the repository
git clone https://github.com/yourusername/network-scanner.git
cd network-scanner

# Build the Docker image
docker-compose build

# Start the application
docker-compose up -d
```

### Method 2: Manual Build

```bash
# Build the image
docker build -t network-scanner-web:latest .

# Run the container
docker run -d --name network-scanner \
  --network host \
  -v $(pwd)/scans:/output \
  -p 5000:5000 \
  network-scanner-web:latest
```

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/network-scanner.git
cd network-scanner

# 2. Build and start the application
docker-compose up -d

# 3. Access the web interface
# Open your browser to: http://localhost:5000

# 4. View logs (optional)
docker-compose logs -f

# 5. Stop the application
docker-compose down
```

## 📁 Project Structure

```
network-scanner/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface HTML
├── Dockerfile            # Container definition
├── docker-compose.yml    # Docker Compose configuration
├── README.md            # This file
├── scans/               # Output directory (auto-created)
│   ├── <scan-id>/
│   │   ├── vulnerability_report_*.txt
│   │   ├── scan_results_*.json
│   │   ├── rustscan_*.txt
│   │   └── nikto_*_*.txt
└── .gitignore           # Git ignore file
```

### File Descriptions

- **app.py**: Flask web application with WebSocket support
- **templates/index.html**: Modern, responsive web interface
- **Dockerfile**: Multi-stage build for optimized image size
- **docker-compose.yml**: Orchestration configuration
- **scans/**: Persistent volume for scan results

## 📖 Usage

### Accessing the Web Interface

1. Start the application:
   ```bash
   docker-compose up -d
   ```

2. Open your browser to:
   ```
   http://localhost:5000
   ```

3. Enter a target (IP address or hostname)

4. Click "Start Vulnerability Scan"

5. Watch real-time progress and results

6. Download reports when complete

### Web Interface Features

- **Target Input**: Enter IP addresses, hostnames, or domains
- **Real-Time Progress**: Visual progress bar with percentage
- **Live Port Discovery**: Ports appear as they're found
- **Vulnerability Alerts**: Security issues displayed instantly
- **Console Logs**: Color-coded streaming logs
- **Download Options**: Text and JSON report formats

## 🔌 API Documentation

### REST API Endpoints

#### Start a New Scan
```http
POST /api/scan
Content-Type: application/json

{
  "target": "192.168.1.1"
}

Response:
{
  "scan_id": "uuid-string",
  "target": "192.168.1.1",
  "status": "queued"
}
```

#### Get Scan Status
```http
GET /api/scan/<scan_id>

Response:
{
  "scan_id": "uuid-string",
  "target": "192.168.1.1",
  "status": "scanning",
  "progress": 45,
  "ports": ["80", "443"],
  "vulnerabilities": 3,
  "logs": [...]
}
```

#### List All Scans
```http
GET /api/scans

Response:
{
  "scans": [
    {
      "scan_id": "uuid-string",
      "target": "192.168.1.1",
      "status": "completed",
      "progress": 100,
      "timestamp": "20231203_143022"
    }
  ]
}
```

#### Download Text Report
```http
GET /api/scan/<scan_id>/report

Response: File download (text/plain)
```

#### Download JSON Data
```http
GET /api/scan/<scan_id>/json

Response:
{
  "target": "192.168.1.1",
  "timestamp": "20231203_143022",
  "ports": ["80", "443", "8080"],
  "vulnerabilities": [...],
  "logs": [...]
}
```

### WebSocket Events

The application uses Socket.IO for real-time updates:

#### Client Events
```javascript
// Connect to server
socket.on('connect', () => {
  console.log('Connected');
});

// Subscribe to scan updates
socket.emit('subscribe', { scan_id: 'uuid-string' });
```

#### Server Events
```javascript
// Scan progress updates
socket.on('scan_progress', (data) => {
  // data: { scan_id, progress, status }
});

// New log entry
socket.on('scan_log', (data) => {
  // data: { scan_id, log: { timestamp, level, message } }
});

// Port discovered
socket.on('port_found', (data) => {
  // data: { scan_id, port }
});

// Vulnerability found
socket.on('vulnerability_found', (data) => {
  // data: { scan_id, vulnerability: { port, finding } }
});
```

## 🎨 Web Interface

### Main Features

1. **Header Section**
   - Application title and description
   - Gradient background design

2. **Scan Form**
   - Target input field
   - Start scan button
   - Form validation

3. **Results Dashboard**
   - Progress bar with percentage
   - Status badge (queued, scanning, completed, failed)
   - Target information

4. **Results Grid**
   - Open Ports card with live updates
   - Vulnerabilities card with findings
   - Color-coded items

5. **Log Console**
   - Real-time streaming logs
   - Color-coded by severity
   - Auto-scrolling

6. **Download Section**
   - Text report download
   - JSON export download

### UI Color Scheme

- **Primary Gradient**: Purple to violet (#667eea → #764ba2)
- **Success**: Green (#4CAF50)
- **Warning**: Orange (#ff9800)
- **Error**: Red (#f44336)
- **Info**: Blue (#2196F3)

## 🔬 Advanced Usage

### Using the API

#### Python Example
```python
import requests
import time

# Start a scan
response = requests.post('http://localhost:5000/api/scan', 
                        json={'target': '192.168.1.1'})
scan_id = response.json()['scan_id']

# Poll for status
while True:
    status = requests.get(f'http://localhost:5000/api/scan/{scan_id}')
    data = status.json()
    
    print(f"Progress: {data['progress']}%")
    
    if data['status'] == 'completed':
        break
    
    time.sleep(5)

# Download report
report = requests.get(f'http://localhost:5000/api/scan/{scan_id}/report')
with open('report.txt', 'wb') as f:
    f.write(report.content)
```

#### Bash Example
```bash
#!/bin/bash

# Start scan
SCAN_ID=$(curl -s -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.1"}' | jq -r '.scan_id')

echo "Scan ID: $SCAN_ID"

# Wait for completion
while true; do
  STATUS=$(curl -s http://localhost:5000/api/scan/$SCAN_ID | jq -r '.status')
  PROGRESS=$(curl -s http://localhost:5000/api/scan/$SCAN_ID | jq -r '.progress')
  
  echo "Status: $STATUS, Progress: $PROGRESS%"
  
  if [ "$STATUS" = "completed" ]; then
    break
  fi
  
  sleep 5
done

# Download report
curl -o report.txt http://localhost:5000/api/scan/$SCAN_ID/report
echo "Report saved to report.txt"
```

### Scanning Multiple Targets

```bash
# Create a targets file
cat > targets.txt << EOF
192.168.1.1
192.168.1.10
example.com
scanme.nmap.org
EOF

# Scan all targets
while read target; do
  curl -X POST http://localhost:5000/api/scan \
    -H "Content-Type: application/json" \
    -d "{\"target\":\"$target\"}"
done < targets.txt
```

### CI/CD Integration

```yaml
# .gitlab-ci.yml
security_scan:
  stage: test
  image: curlimages/curl:latest
  script:
    - |
      SCAN_ID=$(curl -s -X POST http://scanner:5000/api/scan \
        -H "Content-Type: application/json" \
        -d "{\"target\":\"$STAGING_SERVER\"}" | jq -r '.scan_id')
      
      while true; do
        STATUS=$(curl -s http://scanner:5000/api/scan/$SCAN_ID | jq -r '.status')
        if [ "$STATUS" = "completed" ]; then
          break
        fi
        sleep 10
      done
      
      curl -o security-report.txt http://scanner:5000/api/scan/$SCAN_ID/report
  artifacts:
    paths:
      - security-report.txt
```

### Docker Network Configuration

#### Host Network (Recommended for LAN scanning)
```yaml
# docker-compose.yml
services:
  network-scanner-web:
    network_mode: host
```

#### Bridge Network (Isolated)
```yaml
services:
  network-scanner-web:
    ports:
      - "5000:5000"
    networks:
      - scanner-net

networks:
  scanner-net:
    driver: bridge
```

#### Custom Network
```bash
# Create network
docker network create --driver bridge scanner-network

# Run with custom network
docker run -d --name network-scanner \
  --network scanner-network \
  -p 5000:5000 \
  -v $(pwd)/scans:/output \
  network-scanner-web:latest
```

### Environment Variables

```yaml
# docker-compose.yml
services:
  network-scanner-web:
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key-here
      - MAX_CONCURRENT_SCANS=5
      - SCAN_TIMEOUT=3600
```

### Persistent Data

```bash
# Use named volume
docker volume create scanner-data

docker run -d --name network-scanner \
  -v scanner-data:/output \
  -p 5000:5000 \
  network-scanner-web:latest

# Backup scans
docker run --rm \
  -v scanner-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/scans-backup.tar.gz /data
```

## 🐛 Troubleshooting

### Issue: Cannot Access Web Interface

**Symptoms**: Browser shows "Connection refused" or "Unable to connect"

**Solutions**:
```bash
# Check if container is running
docker ps

# Check container logs
docker-compose logs network-scanner-web

# Verify port binding
netstat -tulpn | grep 5000

# Try accessing from container
docker exec network-scanner-web curl http://localhost:5000

# Restart the service
docker-compose restart
```

### Issue: Scans Not Starting

**Symptoms**: Scan stuck in "queued" status

**Solutions**:
```bash
# Check container resources
docker stats network-scanner-web

# View detailed logs
docker-compose logs -f --tail=100

# Restart the container
docker-compose restart

# Check worker thread
docker exec network-scanner-web ps aux | grep python
```

### Issue: Permission Denied on Scans Directory

**Symptoms**: Cannot write to `/output` directory

**Solutions**:
```bash
# Fix directory permissions
sudo chmod 777 ./scans

# Or change ownership
sudo chown -R $USER:$USER ./scans

# Or run with user mapping
docker-compose run --user $(id -u):$(id -g) network-scanner-web
```

### Issue: Slow Network Scanning

**Symptoms**: RustScan taking too long

**Solutions**:
```bash
# Use host network mode
# Edit docker-compose.yml:
network_mode: host

# Increase ulimit
# Edit app.py rustscan command:
"--ulimit", "10000"

# Check network connectivity
docker exec network-scanner-web ping -c 4 8.8.8.8
```

### Issue: WebSocket Connection Failed

**Symptoms**: Real-time updates not working

**Solutions**:
```bash
# Check if Socket.IO is running
docker exec network-scanner-web netstat -tulpn

# Verify WebSocket support
# Open browser console and check for errors

# Try with polling transport
# Edit index.html socket connection:
const socket = io({transports: ['polling', 'websocket']});

# Check firewall rules
sudo ufw status
```

### Issue: Container Exits Immediately

**Symptoms**: Container stops right after starting

**Solutions**:
```bash
# Check build logs
docker-compose build --no-cache

# Run interactively to see errors
docker run -it --rm \
  -p 5000:5000 \
  network-scanner-web:latest

# Check Python dependencies
docker exec network-scanner-web pip3 list

# Verify all tools installed
docker exec network-scanner-web which rustscan
docker exec network-scanner-web which nikto
docker exec network-scanner-web which nmap
```

### Issue: Reports Not Downloading

**Symptoms**: Download buttons not working

**Solutions**:
```bash
# Check scan completion status
curl http://localhost:5000/api/scan/<scan_id>

# Verify file exists
docker exec network-scanner-web ls -la /output/<scan_id>/

# Check file permissions
docker exec network-scanner-web cat /output/<scan_id>/vulnerability_report_*.txt

# Try direct API access
curl -O http://localhost:5000/api/scan/<scan_id>/report
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "rustscan: command not found" | RustScan not installed | Rebuild image with `--no-cache` |
| "Permission denied: /output" | Volume permission issue | Run `chmod 777 scans` |
| "Port 5000 already in use" | Port conflict | Change port or stop conflicting service |
| "Connection refused" | Service not running | Run `docker-compose up -d` |
| "Scan timeout" | Network unreachable | Check network connectivity |

## 🔐 Security & Legal

### ⚠️ Important Legal Notice

**This tool is for authorized security testing only.**

- ✅ Only scan networks and systems you **own** or have **explicit written permission** to test
- ❌ Unauthorized scanning may be **illegal** in your jurisdiction
- ⚖️ Violators may face **civil and criminal penalties** including fines and imprisonment
- 📝 Always obtain proper **written authorization** before scanning
- 🎯 Stay within the **agreed-upon scope** of testing

### Responsible Use Guidelines

1. **Authorization**: Get written permission before scanning any network
2. **Scope**: Stay within the agreed-upon scope of testing
3. **Timing**: Schedule scans during approved maintenance windows
4. **Reporting**: Document and report findings responsibly
5. **Disclosure**: Follow responsible disclosure practices
6. **Privacy**: Respect user data and privacy
7. **Impact**: Minimize impact on production systems

### Security Best Practices

#### Change Default Secret Key
```python
# app.py
app.config['SECRET_KEY'] = 'your-secure-random-key-here'
```

#### Use HTTPS in Production
```bash
# Use reverse proxy with SSL
docker run -d nginx-proxy
```

#### Restrict Network Access
```yaml
# docker-compose.yml
services:
  network-scanner-web:
    networks:
      - internal
networks:
  internal:
    internal: true
```

#### Enable Authentication
Add authentication middleware to protect the web interface.

### Recommended Testing Targets

```bash
# Official test targets (safe to scan)
scanme.nmap.org
testphp.vulnweb.com
testaspnet.vulnweb.com

# Your own infrastructure
localhost
192.168.1.1 (your router)
your-domain.com (with permission)
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Getting Started

1. **Fork** the repository
2. **Clone** your fork
   ```bash
   git clone https://github.com/yourusername/network-scanner.git
   cd network-scanner
   ```
3. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Make** your changes
5. **Test** your changes
   ```bash
   docker-compose build
   docker-compose up -d
   ```
6. **Commit** your changes
   ```bash
   git commit -m 'Add amazing feature'
   ```
7. **Push** to your branch
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open** a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/network-scanner.git
cd network-scanner

# Create development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run locally (without Docker)
python3 app.py

# Build and test Docker image
docker-compose build
docker-compose up -d
docker-compose logs -f
```

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Write docstrings for functions
- Keep functions focused and small

### Testing

```bash
# Test API endpoints
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org"}'

# Test WebSocket connection
# Open browser console and check Socket.IO connection

# Test scan functionality
# Use the web interface to run a complete scan
```

## 📝 License

This project is provided as-is for **authorized security testing purposes only**. Use at your own risk and responsibility.

### Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## 🙏 Acknowledgments

This tool integrates the following excellent open-source projects:

- **[RustScan](https://github.com/RustScan/RustScan)** - The Modern Port Scanner
- **[Nikto](https://github.com/sullo/nikto)** - Web Server Scanner
- **[Nmap](https://nmap.org/)** - Network Exploration Tool
- **[Flask](https://flask.palletsprojects.com/)** - Python Web Framework
- **[Socket.IO](https://socket.io/)** - Real-time Communication
- **[Kali Linux](https://www.kali.org/)** - Security-focused Linux Distribution

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/network-scanner/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/network-scanner/discussions)
- 📧 **Email**: security@yourdomain.com
- 📖 **Documentation**: [Wiki](https://github.com/yourusername/network-scanner/wiki)

## 🔄 Version History

### v1.0.0 (Current)
- ✨ Initial release
- 🌐 Web-based interface with modern UI
- ⚡ Real-time updates via WebSocket
- 🔍 RustScan integration for fast port scanning
- 🌐 Nikto web vulnerability scanning
- 📊 Comprehensive reporting (TXT & JSON)
- 🐳 Fully containerized with Docker
- 🎨 Color-coded console output
- 📱 Responsive design for mobile devices
- 🔌 RESTful API for automation
- 🔄 Multiple concurrent scan support

## 🗺️ Roadmap

### v1.1.0 (Planned)
- [ ] User authentication system
- [ ] Scan scheduling and automation
- [ ] Email notifications
- [ ] Advanced filtering and search
- [ ] Export to PDF reports
- [ ] Scan history management
- [ ] Custom scan profiles

### v1.2.0 (Planned)
- [ ] Integration with additional security tools
- [ ] Vulnerability database integration
- [ ] Compliance reporting (PCI-DSS, HIPAA, etc.)
- [ ] Team collaboration features
- [ ] RBAC (Role-Based Access Control)

### v2.0.0 (Future)
- [ ] Machine learning for vulnerability prioritization
- [ ] Automated remediation suggestions
- [ ] Integration with ticketing systems
- [ ] Mobile application
- [ ] Cloud deployment options

---

**Made with ❤️ for the security community**

⭐ If you find this tool useful, please consider giving it a star on GitHub!

## 📊 Statistics

![GitHub stars](https://img.shields.io/github/stars/yourusername/network-scanner?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/network-scanner?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/network-scanner)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/network-scanner)
![GitHub license](https://img.shields.io/github/license/yourusername/network-scanner)