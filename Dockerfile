# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8888 for the Flask app
EXPOSE 8888

# Run the Flask app
CMD ["gunicorn", "-b", ":8888", "main:app"]
