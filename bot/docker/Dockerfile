# Use a lightweight Python image instead of Ubuntu
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the bot code into the container
COPY . .

# Set environment variables from the .env file
COPY .env .env

# Expose port 80 for the application
EXPOSE 80

# Command to run the bot
CMD ["python", "main.py"]