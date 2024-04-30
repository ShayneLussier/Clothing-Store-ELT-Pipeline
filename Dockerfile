FROM apache/airflow:2.8.1

# Install additional Python packages
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Create a new user named "airflow" with UID and GID specified by the AIRFLOW_UID environment variable regardless of if it already exists
USER root
RUN id -u airflow &>/dev/null || adduser --uid $AIRFLOW_UID --disabled-password --gecos '' airflow

# Set the working directory
WORKDIR /opt/airflow

# Switch to the "airflow" user
USER airflow