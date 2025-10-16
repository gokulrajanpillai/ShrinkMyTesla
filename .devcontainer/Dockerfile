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
    git \
    openssh-client && \
    rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------
# 🚀 Install uv with pip and upper pin
# --------------------------------------------------------------------
# Ensure a modern pip, then install uv from PyPI with an upper pin for stability
RUN python3 -m pip install --no-cache-dir --upgrade "pip>=23.3,<25" && \
    python3 -m pip install --no-cache-dir "uv>=0.4.0,<0.5.0"

# --------------------------------------------------------------------
# 📦 Node.js and npm
# --------------------------------------------------------------------
# Add NodeSource repo pinned at 20.x release line
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g npm@10.7.0 && \
    rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------
# 🧰 Python packages via uv
# --------------------------------------------------------------------
# Copy only requirements first to leverage layer caching
COPY requirements.txt /tmp/requirements.txt

# Install into system site packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r /tmp/requirements.txt

# --------------------------------------------------------------------
# ⚙️ Node dependencies
# --------------------------------------------------------------------
# Copy package.json to leverage caching
COPY package*.json /tmp/
WORKDIR /workspace
RUN cd /tmp && npm install --omit=dev && rm -rf ~/.npm

# --------------------------------------------------------------------
# 👤 Non root user that matches VS Code defaults
# --------------------------------------------------------------------
RUN useradd -ms /bin/bash vscode
USER vscode
WORKDIR /workspace
