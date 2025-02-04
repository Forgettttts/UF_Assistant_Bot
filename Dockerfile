# Use an official lightweight Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Install locales and set es_CL.UTF-8
RUN apt-get update && apt-get install -y locales \
    && locale-gen es_CL.UTF-8 \
    && update-locale LANG=es_CL.UTF-8

# Set environment variables for locale
ENV LANG es_CL.UTF-8
ENV LANGUAGE es_CL:es
ENV LC_ALL es_CL.UTF-8

# Copy project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "main.py"]
