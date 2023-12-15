# Use an official Python runtime as a parent docker ps -aimage
FROM python:3.10.4

# Set the working directory to /app2
WORKDIR /app2

# Copy the current directory contents into the container at /app2
COPY requirements.txt /app2

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install
RUN playwright install-deps

COPY . /app2

# Run app.py when the container launches
CMD ["python", "main.py"]
