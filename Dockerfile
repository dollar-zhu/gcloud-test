# # Use an official Python runtime as a parent image
# FROM python:3.10-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the requirements file
# COPY requirements.txt .

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the application code
# COPY . .

# # Make port 8080 available to the world outside this container
# EXPOSE 8080

# # Define environment variable
# ENV PORT 8080

# # For Scrapy, you might need to run a command like this instead:
# # CMD ["scrapy", "crawl", "omni"]

# # Run main.py when the container launches
# CMD ["python", "main.py"]

###########
# Stage 1: Build Stage
###########
FROM python:3.10-slim as build-stage

# Set working directory for the build stage
WORKDIR /workdir

# Copy the requirements file and install dependencies along with scrapyd-client
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt scrapyd-client

# Copy the entire project
COPY . .

# Build the deployable egg for your Scrapy project (adjust the egg name as needed)
RUN scrapyd-deploy --build-egg=omni.egg

###########
# Stage 2: Final Image
###########
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements and install only runtime dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# (Optional) If you need the built egg for later use (for example, for scrapyd deployments),
# uncomment the next line.
# COPY --from=build-stage /workdir/omni.egg /app/

# Copy the rest of the application code
COPY . .

# Expose port 8080 (as you require)
EXPOSE 8080

# Define environment variable for the port
ENV PORT=8080

# Run main.py when the container launches
CMD ["python", "main.py"]