import sys
import pika
import time
import subprocess
import os
import re
import datetime
#from src.Common.Settings import LogProceso




#sys.path.append('C:\\Dimatica\\offLine')

from src.layers.MessageMachine import MessageJson
from src.layers.MessageMachine import ErrorProcess
from src.layers.MessageMachine import SussesProcess
from src.layers.MessageMachine import WorkerStates
from src.layers.MessageMachine import Variables
from src.layers.RabbitMQ import Mensage
from src.layers.TCPClient import TCPDataAdapter
from flask import  Flask,jsonify,abort,make_response,request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

import logging
#region Variables generales



#endregion
#region Comand Machine
def monedero_callback(message):
    if 'PING' in message:
        return ''
    print(f"New monedero message >{message}<")
    print(f'Estado: {_Variables.current_state}')
    if ('CCM_Valor_Introducido' in message and (_Variables.current_state == WorkerStates.LOCAL)):
        matches = re.search("CCM_Valor_Introducido_(\d+\.\d+)CCM_Valor_Restante_(\d+\.\d+)", message)
        _Variables.importeIngresado =_Variables.importeIngresado + float(matches.groups()[0])
        print('**************************************')
        print('Lectura comandos ')
        print(f'Importe Introducido: {_Variables.importeIngresado}')
        print(f'Mensaje Machine: {message}')
        print('**************************************')
        return 'Status: APP'

    if (_Variables.current_state == WorkerStates.WAIT_PRODUCT_OUT and 'CCM_Producto_OUT' in message):
        print('Valida CCM_Producto_OUT Y WAIT_PRODUCT_OUT_LOCAL')
        _Variables.current_state=WorkerStates.APP
        _Variables.importeIngresado=0

        return 'OK'

def messageJsonOutput(Mensaje: MessageJson, MultiDat: str = None):
    return messageJsonOutput_Encoding(Mensaje.Accion, Mensaje.Phone, Mensaje.Success, Mensaje.Status,
                                           Mensaje.Mensaje, Mensaje.TimeBloq, MultiDat)

def messageJsonOutput_Encoding(Accion, Phone, Success, Status, Mensaje,TimeBloq,MultiDat):
    jsonData = '{"Accion":"'+str(Accion)+'","Phone":"'+str(Phone)+'","Success":'+str(Success)+',"Status":"'+str(Status)+'","Mensaje":"'+str(Mensaje)+'","TimeBloq":"'+str(TimeBloq)+'"}'
    if MultiDat!=None:
        jsonData = '{"Accion":"' + str(Accion) + '","Phone":"' + str(Phone) + '","Success":' + str(
            Success) + ',"Status":"' + str(Status) + '","Mensaje":' + str(Mensaje) + '}'
    jsonToPython =jsonData# json.loads(jsonData)
    print(f'Mensaje >>>> : {jsonToPython}')
    return jsonToPython

def GetStockStar():
    reply =ccm_adapter.transact_message("CCM_stockfull")
    print(f'Full Stock: {reply}')
    return reply

def MessageJsonDispacher(_Carril:str=None,_User:str=None,_Camp:str=None):
    _CarrilesFormat: str = None
    _Machine: str = "LOCALHOS"
    Comando = '{"Accion":"DISPACHER","Machine":"' + _Machine + '","Fecha":"' + FechaActual().strftime('%d/%m/%Y') + '","User":"'+_User+'","Camp":"'+_Camp+'" ,"Carril":"' + _Carril.replace(',','') + '"}'
    return Comando
def FechaActual():
    _FechaActual = datetime.datetime.now()
    #_x = _FechaActual.strftime('%H:%M:%S')
    return _FechaActual
#endregion


tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


@app.route('/api/v1.0/tasks',methods=['GET'])
def get_tasks():
    return jsonify({'tasks':tasks})

@app.route('/api/getstatus',methods=['GET'])
def getstatus():
    _Result = ccm_adapter.transact_message('CCM_Getstatus')
    print(f"Respuesta: {_Result}")
    ccm_adapter.close()
    if 'OK' in _Result:
        print('OK')
        return jsonify({'tasks': tasks})
    else:
        print('error')
        return jsonify({'tasks': tasks})

@app.route('/api/Start',methods=['GET'])
def ApiStart():
    print('Dimatica >>> Iniando start')
    _Result =MessageJson()
    _Result.Accion = "START"

    try:
        print(f'Dimatica >>> verificando status')
        if (CCM_Getstatus() == False):
            _Result.Status = "KO"
            _Result.Mensaje = ErrorProcess.CCM_STATUS
            return
        print(f'Dimatica >>> 2 *********************************************************')
        print('Dimatica >>> solicitando Stock full')
        _CarrilesFormat: str = str(GetStockStar())
        print(f'Dimatica >>> Carriles:{_CarrilesFormat}')
        print(f'Dimatica >>> 3 *************************************************')

        if (_Variables.current_state == WorkerStates.WAIT_PRODUCT_OUT):
            _Result.Status = 'KO'
            _Result.Mensaje = ErrorProcess.CCM_OUT_PRODUC
            msg = messageJsonOutput(_Result, None)
            return msg

        _Result.Status = 'OK'
        _Result.Phone = ''
        #_Result.Mensaje = SussesProcess.START  # 'Communicacion Aceptada'
        _Result.Mensaje = _CarrilesFormat
        _Result.TimeBloq = str("2000")
        _Variables.current_state=WorkerStates.LOCAL
        print('********************************************')
        print(f'Estado Machine{_Variables.current_state}')
        print('********************************************')
    except Exception as e:
        _Result.Phone=''
        _Result.Status='KO'
        print(f'Dimatica >>>{e}')
        _Result.Mensaje=ErrorProcess.DESCONOCIDO# 'ERR-1000: Error no controlado. '
    finally:
        print("Dimatica >>>Enviando Mensaje server")
        msg= messageJsonOutput(_Result,None)
        return msg

@app.route('/api/Prepare',methods=['GET'])
def ApiPrepare():
    _Result = MessageJson()
    _Result.Accion = "PREPARE"
    try:
        if (_Variables.current_state == WorkerStates.WAIT_PRODUCT_OUT):
            _Result.Status = 'KO'
            _Result.Mensaje = ErrorProcess.CCM_OUT_PRODUC
            msg = messageJsonOutput(_Result, None)
            return msg

        _carril:str= request.args.get('Carril')

        print(f'Dimatica >>>Carril: {_carril}')
        if(CCM_Getstatus()==True):
            Devolucion()
            if (CCM_Select(_carril) == True):
                _Variables.importeIngresado = 0
                _Result.Status = "OK"
                _Result.Mensaje = SussesProcess.PREPARE
            else:
                _Result.Status = "KO"
                _Result.Mensaje = ErrorProcess.CCM_SELECT
        else:
            _Result.Status="KO"
            _Result.Mensaje=ErrorProcess.CCM_STATUS

        print('********************************************')
        print(f'Estado Machine{_Variables.current_state}')
        print('********************************************')

    except Exception as e:
        _Result.Phone = ''
        _Result.Status = 'KO'
        _Result.Mensaje = ErrorProcess.DESCONOCIDO  # 'ERR-1000: Error no controlado.
    finally:
        print("Dimatica >>>Enviando Mensaje server")
        msg = messageJsonOutput(_Result, None)
        return msg
        #  '


@app.route('/api/Dispacher',methods=['GET'])
def ApiDispacher():
    print('********************************************')
    print(f'Estado Machine{_Variables.current_state}')
    print('********************************************')
    _Result = MessageJson()
    _Result.Accion = "DISPACHER"
    _Result.TimeBloq = 0
    try:
        _carril: str = request.args.get('Carril')
        _precio:float=float(request.args.get('Precio'))
        if (_Variables.current_state==WorkerStates.LOCAL):
            if(_Variables.importeIngresado>= _precio):
                if(CCM_Getstatus()==True):
                    time.sleep(0.25)
                    if(CCM_Select(_carril)==True):
                        time.sleep(0.25)
                        if(CCM_Write(_carril)==True):
                            _Variables.current_state=WorkerStates.WAIT_PRODUCT_OUT
                            _Result.Mensaje = SussesProcess.CCM_WRITE
                            _Result.Status="OK"
                            msgNew = MessageJsonDispacher(_carril, _User="", _Camp="")
                            _Variables.importeIngresado=0
                            #TODO: Mensaje a la Rabbit local
                            oMensaje=Mensage()
                            oMensaje.SendMessage(msgNew)
                            #oQueueDestroid.newMessageServer(msgNew, props=None, queue_name=NameQueueServer())

                        else:
                            _Result.Status = "KO"
                            _Result.Mensaje = ErrorProcess.CCM_WRITE

                    else:
                        _Result.Status = "KO"
                        _Result.Mensaje = ErrorProcess.CCM_SELECT
                else:
                    _Result.Status = "KO"
                    _Result.Mensaje = ErrorProcess.CCM_STATUS
            else:
                _Result.Status = "KO"
                _Result.Mensaje = ErrorProcess.PRICE_LACK

        else:
            _Result.Status="KO"
            _Result.Mensaje=ErrorProcess.PROCESS
    except Exception as e:
        _Result.Phone = ''
        _Result.Status = 'KO'
        print(e)
        _Result.Mensaje = ErrorProcess.DESCONOCIDO  # 'ERR-1000: Error no controlado.
    finally:
        print("Enviando Mensaje server")
        msg = messageJsonOutput(_Result, None)
        return msg

@app.route('/api/Finish',methods=['GET'])
def ApiFinish():
    print('********************************************')
    print(f'Estado Machine: {_Variables.current_state}')
    print('********************************************')
    try:
        _Variables.current_state = WorkerStates.APP
        _Variables.importeIngresado = 0
        print('********************************************')
        print(f' Cambiando estado.......')
        print(f'Estado Machine: {_Variables.current_state}')
        print('********************************************')
        return "OK"
    except Exception as e:
        return "Error........ Finish"


def CCM_Getstatus()-> bool:
    _Result = ccm_adapter.transact_message('CCM_Getstatus')
    print(f"Dimatica >>> Respuesta Status: {_Result}")

    if 'OK' in _Result:
        return True
    else:
        return False

def CCM_Select(_Carril:str)->bool:
    _Result = ccm_adapter.transact_message('CCM_Select('+_Carril+')')
    print(f"Dimatica >>> Respuesta Select: {_Result}")
    if 'OK' in _Result:
        return True
    else:
        return False


def CCM_Write(_Carril: str) -> bool:
    _Result = ccm_adapter.transact_message('CCM_Write(' + _Carril + ')')
    print(f"Respuesta Write: {_Result}")
    if 'OK' in _Result:
        return True
    else:
        return False

def Devolucion() -> bool:
    reply1 = ccm_adapter.transact_message("CCM_Devolucion")
    print(f'Dimatica devolucion >>>{reply1}')
    if 'OK' in reply1 or 'CCM_Devolucion' in reply1:
        return True
    else:
        return False



if __name__=='__main__':

    #print(f' Dimatica >>> {os.getcwd()}')
    #config_path = r"C:\Dimatica\offLine\Config\Configuracion.config"
    #oLog=LogProceso()
    #oLog.StartLogging(config_path)

    _Variables =  Variables()
    _Variables.current_state=WorkerStates.APP
    ccm_adapter = TCPDataAdapter()
    ccm_adapter.open()
    mon_adapter = TCPDataAdapter()
    mon_adapter.bind_and_setup_listening()
    mon_adapter.incoming_msg_handler = monedero_callback

    port = int(os.environ.get('PORT', 5000))

    app.run(host='127.0.0.1', port=port)
    #app.run(debug=False)

