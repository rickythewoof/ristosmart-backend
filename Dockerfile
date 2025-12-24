    # Use an official lightweight Python image
    FROM python:3.9-slim  

    # Set the working directory
    WORKDIR /app 

    # Copy project files into the container
    COPY . /app  
    RUN pip install -r requirements.txt  

    EXPOSE 3000

    # Command to run the app
    CMD ["python", "src/app.py"]