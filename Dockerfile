# Use an official lightweight Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 (required by Render)
EXPOSE 8080

# Run both the bot and a dummy web server
CMD ["sh", "-c", "python main.py & python server.py"]
