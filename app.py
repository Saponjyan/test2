
# docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
from fastapi import FastAPI
import pika
from pika import channel
from fastapi import HTTPException
from pydantic import BaseModel
from cs50 import SQL
from datetime import datetime
from typing import List

app = FastAPI()

# Настройки подключения RabbitMQ
rabbitmq_host = 'localhost'
rabbitmq_port = 5672
rabbitmq_user = 'guest'
rabbitmq_password = 'guest'
rabbitmq_queue = 'my_queue'

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///mydb.db")

class Client(BaseModel):
    id: str
    phone_number: str
    operator_code: str
    tag: str
    timezone: str


# Модель данных для рассылки
class Newsletter(BaseModel):
    id: str
    client_id:str
    message: str
    client_filter: dict
    start_time: datetime
    end_time: datetime
    status:bool

# Модель данных для статистики рассылки
class NewsletterStats(BaseModel):
    sent: int
    failed: int
    pending: int
    
    
class Mailing(BaseModel):
    id: str  
    start_time: str
    message: str
    filter_property: str
    end_time: str
    
    
class Messages(BaseModel):
    id: str
    creat_data: datetime
    status:str
    mailing_id: str
    client_id: str
####################################################################
def send_message(message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, 
                                    credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password))
    )
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_queue)
    channel.basic_publish(exchange='', routing_key=rabbitmq_queue, body=message)
    connection.close()

def receive_message():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port,
                                    credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password))
    )
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_queue)
    method_frame, _, body = channel.basic_get(queue=rabbitmq_queue, auto_ack=True)
    connection.close()
    return body


@app.get("/")
async def root():
    return { "message": "Hello world" }


@app.post('/send/')
async def send(request_body: str):
    send_message(request_body)
    return {'message': 'Message sent'}

@app.get('/receive/')
async def receive():
    message = receive_message()
    return {'message': message.decode()}
###########################################################################################
@app.post("/clients")
async def create_client(client: Client):
    # Логика создания клиента
    # client - данные клиента, полученные через запрос
    db.execute("INSERT INTO clients (id, phone_number, operator_code,tag, timezone) VALUES ( :id, :phone_number, :operator_code, :tag,:timezone)",
                    id=client.id,
                    phone_number=client.phone_number,
                    operator_code=client.operator_code,
                    tag=client.tag,
                    timezone=str(datetime.now())
                    )
    

    return {"message": f"Client {client.id} created successfully"}


@app.put("/clients/{client_id}")
async def update_client(client_id: str, client: Client):
    '''Логика обновления данных клиента
    client_id - идентификатор клиента
    client - данные клиента, полученные через запрос
    db.execute(f"UPDATE clients SET id = {client.id} WHERE id={client_id}")'''
    
    db.execute(f"DELETE FROM clients WHERE id = '{client_id}'")
    db.execute("INSERT INTO clients (id, phone_number, operator_code,tag, timezone) VALUES ( :id, :phone_number, :operator_code, :tag,:timezone)",
                    id = client.id,
                    phone_number=client.phone_number,
                    operator_code=client.operator_code,
                    tag=client.tag,
                    timezone=str(datetime.now())
                    )

    return {"message": f"Client {client_id} updated successfully"}

@app.delete("/clients/{client_id}")
async def delete_client(client_id: str):
    # Логика удаления клиента
    # client_id - идентификатор клиента
    db.execute(f"DELETE FROM clients WHERE id = '{client_id}'")

    return {"message": "Client deleted successfully"}

@app.post("/mailings")
async def create_mailing(mailing: Mailing):
    # Логика создания новой рассылки
    # mailing - данные рассылки, полученные через запрос
    db.execute("INSERT INTO mailings (id, start_time, message,filter_property, end_time) VALUES ( :id, :start_time, :message, :filter_property,:end_time)",
                    id=mailing.id,
                    start_time= mailing.start_time,
                    message=mailing.message,
                    filter_property=mailing.filter_property,
                    end_time=mailing.end_time)

    # # Отправка сообщения в RabbitMQ для обработки активных рассылок
    # channel.basic_publish(exchange='',
    #                     routing_key='mailings_queue',
    #                     body=f"New Mailing: {mailing.id}")

    return {"message": "Mailing created successfully"}

@app.get("/statistics/mailings")
async def get_mailings_statistics(message):
    '''Логика получения общей статистики по рассылкам'''
    # all = db.execute(f"SELECT * from newsletterStats")

    return {"message": f"{message} Mailings statistics"}

# mailing_id - идентификатор рассылки
@app.get("/statistics/mailings/{mailing_id}")
async def get_mailing_statistics(mailing_id: str):
    '''Логика получения детальной статистики по рассылке'''
    pass

    return {"message": f"Statistics for Mailing: {mailing_id}"}


# @app.delete("/newsletterStats")
# async def delete_client(client_id: str):
#     # Логика удаления клиента
#     # client_id - идентификатор клиента
#     db.execute(f"DELETE FROM clients WHERE id = '{client_id}'")

#     return {"message": "Client deleted successfully"}
###########################################################################################
# Обработка активных рассылок и отправка сообщений клиентам через RabbitMQ
# def process_active_mailings(message):
#     '''Логика обработки активных рассылок'''
#     connection = pika.BlockingConnection(
#     pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, 
#                                     credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password))
#     )
#     channel = connection.channel()
#     channel.queue_declare(queue=rabbitmq_queue)
#     channel.basic_publish(exchange='', routing_key=rabbitmq_queue, body=message)
#     connection.close()



# Обработка сообщений из RabbitMQ
# def callback(ch, method, properties, body):
#     ''' Логика обработки сообщений из RabbitMQ body - содержимое сообщения'''

#     connection = pika.BlockingConnection(
#         pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port,
#                                     credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password))
#     )
#     channel = connection.channel()
#     channel.queue_declare(queue=rabbitmq_queue)
#     method_frame, _, body = channel.basic_get(queue=rabbitmq_queue, auto_ack=True)
#     connection.close()
#     return body


# Запуск обработки активных рассылок
# process_active_mailings("hi!!!!!!!!!!!111")
# send_message("hiiiii!!!!!!")


#############################################################################################
# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app, host='0.0.0.0', port=8000)



#  CREATE TABLE IF NOT EXISTS clients (
#                         id varchar(45) NOT NULL,
#                         phone_number varchar(45) NOT NULL,
#                         operator_code varchar(45) NOT NULL,
#                         tag varchar(45),
#                         timezone varchar(45));



# CREATE TABLE IF NOT EXISTS mailings (
#         id VARCHAR NOT NULL,
#         start_time VARCHAR,
#         message VARCHAR,
#         filter_property VARCHAR,
#         end_time VARCHAR
# );

    
#     CREATE TABLE IF NOT EXISTS messages (
#         id VARCHAR NOT NULL,
#         creat_data VARCHAR,
#         status VARCHAR,
#         mailing_id VARCHAR,
#         client_id VARCHAR
# );

# Модель данных для статистики рассылки

    
#     CREATE TABLE IF NOT EXISTS newsletterStats (
#         sent integer NOT NULL,
#         failed integer,
#         pending integer
# );