# syntax=docker/dockerfile:1

FROM python:3.10

# Set the working directory
WORKDIR /giftai

# Copy the requirements.txt file
COPY requirements.txt ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Run the application
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]