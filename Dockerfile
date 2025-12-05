FROM kalilinux/kali-rolling:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nmap \
    nikto \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install RustScan
RUN wget https://github.com/RustScan/RustScan/releases/download/2.0.1/rustscan_2.0.1_amd64.deb \
    && dpkg -i rustscan_2.0.1_amd64.deb \
    && rm rustscan_2.0.1_amd64.deb

# Install Python packages
RUN pip3 install --no-cache-dir flask flask-socketio python-socketio eventlet

# Create directories
RUN mkdir -p /app/templates /output

# Copy application files
COPY app.py /app/
COPY templates/index.html /app/templates/

WORKDIR /app

EXPOSE 5000

CMD ["python3", "app.py"]