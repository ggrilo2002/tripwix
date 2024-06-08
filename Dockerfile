# Pull official base image
FROM python:3.9-slim

# Install Nginx and other dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Set up the application
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080
EXPOSE 8080
EXPOSE 8501

# Start Nginx and your application
CMD streamlit run login.py --server.port=8501 --server.address=0.0.0.0 & python -m functions.credential_refresher
