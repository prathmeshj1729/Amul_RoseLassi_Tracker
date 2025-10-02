FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application file
COPY tracker.py .

# Run the tracker
CMD ["python", "-u", "tracker.py"]
