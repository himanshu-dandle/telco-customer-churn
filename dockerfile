# Use an official Python runtime as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy app files to container
COPY . /app

# Ensure model directory exists
RUN mkdir -p /app/data/output

# Copy the trained model to the correct location
COPY data/output/xgboost_model_v5.json /app/data/output/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose API port
EXPOSE 8000

# Set the correct startup command
##CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]

