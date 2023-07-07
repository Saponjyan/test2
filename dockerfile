# FROM python:3.10

# WORKDIR /code

# COPY ./requirements.txt /code/requirements.txt
# COPY ./mydb.db /code/mydb.db

# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# # RUN docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
# # 
# COPY ./main.py /code/

# #run["docker", "run", "-it", "--rm", "--name", "rabbitmq", "-p", "5672:5672", "-p", "15672:15672", "rabbitmq:3.12-management"]
# # CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
# CMD ["uvicorn", "main:app", "--reload"]
# # docker run -d -p 80:8000 mytest
# Using Python 3.9 
FROM python:3.10

# Setup working directory
RUN mkdir code
WORKDIR /code

# Copy requirements file to our working directory
COPY ./requirements.txt /code/requirements.txt
COPY ./mydb.db /code/mydb.db

# Install packages - Use cache dependencies 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
#docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management

# Copy our code over to our working directory
COPY ./ /code/app

# Run our project exposed on port 80
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]
# docker stop $(docker ps -a -q)
# docker rm $(docker ps -a -q)
# docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
# docker run -d --name fastdockercontainer77 -p 80:80 fastdockerimage77