# Use an official lightweight Python image
FROM python:3.9-slim  

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app 

# Copy project files into the container
COPY . /app  

RUN pip install -r requirements.txt  

EXPOSE 3000

# Command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "4", "--preload", "app:app"]