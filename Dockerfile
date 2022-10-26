FROM python

#This is directory with files for container
WORKDIR /app

#This will copy requirements.txt and install dependencies and necessary files to workdir
COPY requirements.txt .
RUN pip install -r requirements.txt

# We can copy all app files by COPY . . or we can use .dockerignore file in order to ignore some of them

COPY . .
