# https://www.docker.com/blog/how-to-dockerize-django-app/
# https://learn.microsoft.com/en-us/azure/app-service/tutorial-custom-container?tabs=azure-portal&pivots=container-linux

# Use the official Python runtime image
FROM python:3.14-slim  

# Create the app directory
RUN mkdir /app
# Set the working directory inside the container
WORKDIR /app

# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 

# Upgrade pip
RUN pip install --upgrade pip 

# Copy the Django project  and install dependencies
COPY requirements.txt  /app/
# run this command to install all dependencies 
RUN pip install --no-cache-dir -r requirements.txt

# update data from apt-get repositories and install curl
RUN apt-get update && apt-get -y install curl 
# Download the package to configure the Microsoft repo
RUN curl -sSL -O https://packages.microsoft.com/config/debian/$(grep VERSION_ID /etc/os-release | cut -d '"' -f 2 | cut -d '.' -f 1)/packages-microsoft-prod.deb
# Install the package
RUN dpkg -i packages-microsoft-prod.deb
# Delete the file
RUN rm packages-microsoft-prod.deb
# Install ODBC drivers from Microsoft repo
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18
RUN apt-get install -y unixodbc-dev

# Copy the Django project to the container
COPY . /app/

# Expose the Django port
EXPOSE 8000

# # Run Django’s development server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "LASER.wsgi:application"]
