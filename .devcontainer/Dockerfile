# Stable tag, easy updates
FROM ubuntu:22.04

# Optionally document the last verified digest
# Verified digest as of 2025-10-08:
# sha256:cfb8c7c1da3ec3cb5560fbd0b7a29f92d8f7f1f2e45b02c97b3c6069c7e4c9b4

# --------------------------------------------------------------------
# 🛠 System setup
# --------------------------------------------------------------------
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    git && \
    rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------
# 📦 Node.js + npm 
# --------------------------------------------------------------------
# Add NodeSource repo (pinned at 20.x release line)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g npm@10.7.0 && \
    rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------
# 🧰 Python packages
# --------------------------------------------------------------------
## Copy your requirements to pip dependencies
##COPY requirements.txt /tmp/requirements.txt
##RUN pip install --no-cache-dir -r /tmp/requirements.txt

# --------------------------------------------------------------------
# ⚙️ Node dependencies
# --------------------------------------------------------------------
# Copy package.json to leverage caching
COPY package*.json /tmp/
WORKDIR /workspace
RUN cd /tmp && npm install --omit=dev && rm -rf ~/.npm

# --------------------------------------------------------------------
# 👤 Non-root user (matches VSCode defaults)
# --------------------------------------------------------------------
RUN useradd -ms /bin/bash vscode
USER vscode
WORKDIR /workspace
