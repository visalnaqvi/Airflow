FROM apache/airflow:2.10.2

# Switch to root for installing system packages
USER root

# Install Node.js and npm
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy Node.js dependencies first (better caching)
COPY scripts/package*.json /opt/airflow/scripts/
RUN cd /opt/airflow/scripts && npm install

# Copy the rest of your project
COPY . /opt/airflow

# Switch back to airflow user
USER airflow
