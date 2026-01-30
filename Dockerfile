# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# (Assuming you have one, otherwise we install manually)
RUN pip install --no-cache-dir fastapi uvicorn pandas pandas-ta yfinance scikit-learn joblib matplotlib

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME SovereignBot

# Run dashboard_server.py when the container launches
# Note: In a real deployment, we'd use supervisord to run bot + server + guardian
CMD ["python", "dashboard_server.py"]
