# Use the python:alpine image as the base image and name it "builder"
FROM python:alpine AS builder

# Set the working directory inside the container to /usr/src/app
WORKDIR /usr/src/app

# Copy the requirements.txt file from the host to the container's working directory
COPY requirements.txt .

# Update the package index and install nmap and nmap-scripts using apk package manager
RUN apk update && apk add --no-cache nmap nmap-scripts

# Install the Python dependencies listed in requirements.txt using pip
RUN pip install --no-cache-dir -r requirements.txt --root-user-action=ignore

# Copy the rest of the application code from the host to the container's working directory
COPY . .

# Set the command to run when the container starts
CMD ["waitress-serve", "--port=8080", "main:app"]
