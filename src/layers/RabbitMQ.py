import pika
import pika.frame as frame
import pika.exceptions as exceptions
import pika.spec as spec
from pika.utils import is_callable
import time
from uuid import uuid4
from src.layers.MessageMachine import Constantes

class Mensage():
    def __init__(self):
        self.Credenciales:str=Constantes.RabbitAMQP
        self.NameQueue:str=Constantes.QueueServer
    def SendMessage(self, message: str, props: pika.spec.BasicProperties = None, queue_name: str = None):
        print('HMS: envioo mensaje server')
        try:
            QueueDest:str=None

            if props is None:
                props = pika.spec.BasicProperties()
            if props.message_id is None:
                props.message_id = str(uuid4())
            if props.delivery_mode is None:
                props.delivery_mode = 2  # 2 - persistent
            if props.timestamp is None:
                props.timestamp = int(time.time())

            if queue_name is None:
                QueueDest=self.NameQueue
            else:
                QueueDest=queue_name

            Conexion = pika.BlockingConnection(pika.URLParameters(self.Credenciales))
            Canal = Conexion.channel()
            Canal.queue_declare(queue=QueueDest,durable=True)
            body=message
            Canal.basic_publish(exchange='',
                                              routing_key=QueueDest,
                                              body=body,
                                              properties=props)
            Conexion.close()




        except Exception:
            pass



        pass