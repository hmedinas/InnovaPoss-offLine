from src.Common import Util
import logging
import logging.handlers
import os
from pathlib import Path
from src.layers.MessageMachine import Constantes

class Settings():
    def __init__(self):

        self.logging_logger_name: str = None
        self.logging_level: int = None
        self.logging_filename: str = None
        self.logging_format: str = None
        self.port3000: int = Constantes.port3000
        self.port3001: int = Constantes.port3001
        self.Host: str = Constantes.Host
        self.RabbitAMQP: str = Constantes.RabbitAMQP# 'amqp://guest:guest@innova.vservers.es:5672'
        self.QueueServer: str = Constantes.QueueServer

    @staticmethod
    def StartConfiguration(path:str):

        if not path:
            raise ValueError('No existe el archivo de configuraciones')
        else:
            from pathlib import Path
            print(f'path{path}')
            oArchivo=Path(path)
            if not oArchivo.is_file():
                raise FileExistsError("El archivo de configuraciones no es un archivo")
            from configparser import ConfigParser
            oConfiguracion=ConfigParser()
            oConfiguracion.read(path)

            oResult=Settings()#para setar las variables

            oResult.logging_level=Util.get_with_default(oConfiguracion, "logging", "level", "DEBUG")
            oResult.logging_filename = Util.get_with_default(oConfiguracion, "logging", "filename", 'innovapos_no_config.log')
            oResult.logging_format = Util.get_with_default(oConfiguracion, "logging", "format","%%(asctime)s %%(name)s %%(levelname)s %%(message)s")

            return oResult
'''
class LogProceso():
    def __init__(self):
        self.Settting:Settings=None
    def StartLogging(self,path:str):
        self.Settting=Settings.StartConfiguration(path)
        self.logger=logging.getLogger(self.Settting.logging_filename)
        print(f'Dimatica >>> Level: {self.Settting.logging_level}')
        self.logger.setLevel(self.Settting.logging_level)

        log_stream_handler = logging.StreamHandler()
        log_stream_handler.setLevel(self.Settting.logging_level)
        log_stream_formatter = logging.Formatter(self.Settting.logging_format)
        log_stream_handler.setFormatter(log_stream_formatter)

        if self.Settting.logging_filename.startswith("~"):
            self.Settting.logging_filename = self.Settting.logging_filename.replace("~", os.path.expanduser("~"))
        dir_path = Path(self.Settting.logging_filename).parent
        os.makedirs(dir_path, exist_ok=True)

        log_file_handler = logging.handlers.TimedRotatingFileHandler(filename=self.Settting.logging_filename,when='D', interval=1, backupCount=0)
        log_file_formatter = logging.Formatter(self.Settting.logging_format)
        log_file_handler.setFormatter(log_file_formatter)
        self.logger.addHandler(log_stream_handler)
        self.logger.addHandler(log_file_handler)
        self.logger.info(" = = = = = = Inicio de Log OffLine = = = = = = ")
        self.logger.debug("Configuracion de level")
        
'''