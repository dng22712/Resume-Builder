# set the Python version
FROM python:3.12

# update pip
RUN pip install --upgrade pip

# set the working directory in the container
WORKDIR /career_sparker
ADD . /career_sparker

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies from requirements.txt
COPY /requirements.txt /career_sparker
RUN pip install -r requirements.txt
#RUN apt-get update
#RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev


RUN apt-get update \
    && apt-get -y install build-essential libpq-dev \
    && apt-get clean

# copy project file
COPY . /career_sparker

# expose port 8000 to the Docker host, so we can access it from the outside
EXPOSE 8000

# run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
