# Use multi-platform base image and specify linux/amd64 for HPC compatibility
FROM --platform=linux/amd64 python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the BIDS App
COPY volume_counter_bidsapp.py /app/

# Set the entrypoint
ENTRYPOINT ["python", "/app/volume_counter_bidsapp.py"]

# Add labels for BIDS App
LABEL org.label-schema.schema-version="1.0.0" \
      org.label-schema.name="T1 Volume Counter BIDS App" \
      org.label-schema.description="BIDS App to count volumes in T1-weighted images" \
      org.label-schema.url="https://github.com/ReproNim/babs-demo-ohbm2025" \
      org.label-schema.vcs-url="https://github.com/ReproNim/babs-demo-ohbm2025" \
      org.label-schema.version="0.1.0" \
      org.label-schema.vendor="ReproNim"