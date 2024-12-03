# Use the official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy local files to the container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Command to run your script
CMD ["python", "avant_2_go_scrapper.py"]
