from enum import Enum
import datetime

class Constantes():
    port3000:int=4000
    port3001:int=4001
    Host:str='127.0.0.1'
    RabbitAMQP:str='amqp://guest:guest@innova.vservers.es:5672'
    QueueServer:str='OUT_ServerREAD'


class WorkerStates(Enum):
    NONE = "NONE"  # --si
    DEBUGGING = "DEBUGGING"
    ANY = "ANY"  # --si
    BOOTING = "BOOTING"
    IDLE = "IDLE"
    BUYING_CASH = "BUYING_CASH"
    BUYING_CASH_NO_APP = "BUYING_CASH_NO_APP"
    WAITING_CASH = "WAITING_CASH"
    RETURN_CASH = "RETURN_CASH"
    DISPENSING = "DISPENSING"
    WAIT_COLLECTION = "WAIT_COLLECTION"
    MANUAL = "MANUAL"  # --si
    APP = "APP"  # --si
    WAIT_PRODUCT_OUT="WAIT_PRODUCT_OUT" #--si
    WAIT_PRODUCT_OUT_LOCAL="WAIT_PRODUCT_OUT_LOCAL"
    LOCAL="LOCAL"

class MessageJson():
    Accion=''
    Phone=''
    Success='true'
    Status=''
    Mensaje=''
    TimeBloq=''


class ErrorProcess():
    DESCONOCIDO = "ERR-1000: ERROR DESCONOCIDO"  # --si
    CONEXION_USO= "ERR-1001: La conexion esta en uso"
    USO_APP = "ERR-1002: Maquina usada por APP"
    CCM_STATUS = "ERR-2001: Maquina No disponible"
    CCM_SELECT = "ERR-2002: No se puede Seleccionar el producto"
    CCM_OUT_PRODUC="ERR-2003: Existe un Producto en el Dispensador, Retirelo para continuar"
    CCM_WRITE = "ERR-2004: No se puede Despachar el producto"
    TIME_OUT="ERR-2004: Su compra ha exedido el tiempo Establecido."
    PRICE_LACK="ERR-3001: Precio Insuficente "
    PROCESS="ERR-9999: Error en el flujo del proceso"

    SET_STOCK="ERR-3002: no se puede Actualizar el Stock"
    SET_STOCK_FULL="ERR-3003: No se puede actualizar el Stock Full"
    GET_STOCK="ERR-3004: No se puede obtener el Stock"
    GET_STOCK_FULL="ERR-3005:  No se puede obtener el Stock Full"
    SET_PRICE="ERR-3006: Error Actualizando el Precio"

class SussesProcess():
    START='Proceso Iniciado con Exito'
    PREPARE='Equipo Preparado Para Compra'
    CANCEL='Operaciones Canceladas'
    CCM_STATUS = "Maquina disponible"
    CCM_SELECT = "Producto Seleccionado"
    CCM_WRITE = "Producto Despachado"

    SET_STOCK = "Stock Agregado con Exito"
    SET_STOCK_FULL = "Stock Agregado con Exito"
    SET_PRICE = "Actiualizacion de Precio Correcto"

class ConstantesProcess():
    TimeMessageExpire='12000'
    QueueServer='SERVER'

class Variables:
    _instance_ = None
    def __init__(self):
        """
        Main coordinator of the interaction with the dispenser
        Uses innovapos.dispenser.adapters.HardwareClient in order to interact with the data; \
        the pika library is used in order to be able to read and write from RabbitMQ

        """
        self.current_state = WorkerStates.BOOTING
        # TODO: Variables de Uso local
        self.importeIngresado = 0
        self.precioProducto = 0
        self.KeyApi:str=None
        self.KeyTime:int=0
        self.new_inc_queue:str=None
        self.new_out_queue:str=None
        self.Fecha:datetime=None
        self.isFinish:bool=False

def metodo():
    _Variables=Variables();
