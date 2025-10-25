FROM python:3.11-slim

# Install Vale
RUN apt-get update && \
    apt-get install -y curl && \
    VALE_VERSION=$(curl -s https://api.github.com/repos/errata-ai/vale/releases/latest | grep '"tag_name"' | sed -E 's/.*"v([^"]+)".*/\1/') && \
    curl -sfL https://github.com/errata-ai/vale/releases/download/v${VALE_VERSION}/vale_${VALE_VERSION}_Linux_64-bit.tar.gz | tar -xz -C /usr/local/bin vale && \
    chmod +x /usr/local/bin/vale && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Set up Python environment
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir fastmcp httpx

# Set Vale path
ENV VALE_PATH=/usr/local/bin/vale

# Default command (fastmcp.cloud will override this)
CMD ["python", "vale_mcp.py"]
