FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
# Copy the requirements.txt file
COPY ./requirements.txt /requirements.txt
# Run the pip command to install the requirements
RUN pip install -r requirements.txt
# Create app directory
RUN mkdir /app
# Set the work directory
WORKDIR /app
# Copy the app folder from local machine to folder in the docker image
COPY ./app /app
# Add the user, -D means applications only, username
RUN adduser -D user
# Set the user to be used
USER user

