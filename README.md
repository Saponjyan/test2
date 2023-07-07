docker build -t fastdockerimage77 .
docker run -d --name fastdockercontainer77 -p 80:80 fastdockerimage77
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management

# Настройки подключения RabbitMQ
rabbitmq_host = 'localhost'
rabbitmq_port = 5672
rabbitmq_user = 'guest'
rabbitmq_password = 'guest'
rabbitmq_queue = 'my_queue'


http://localhost:15672/#/ rebbitmq
http://localhost/docs    fastapi