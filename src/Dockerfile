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

# Command to run the app with detailed logging
# --log-level debug: Enable debug logging
# --access-logfile -: Log access logs to stdout
# --error-logfile -: Log error logs to stdout
# --access-logformat: Custom format showing method, path, status, response time
# --capture-output: Capture stdout/stderr from the app
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "4", "--preload", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "--access-logformat", "%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\" %(D)s", \
     "app:app"]