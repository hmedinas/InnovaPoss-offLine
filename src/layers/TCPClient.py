import socket
import logging
import uuid
from _thread import start_new_thread
from time import sleep
from typing import Callable, Any


class TCPDataAdapter():
    def __init__(self):
        """
        TCPDataAdapter constructor

        """
        self.read_stop_byte = str.encode('\n')
        self.sock: socket.socket = None
        self.logger = logging.getLogger(__name__)
        print("Adapter instantiated")
        self.incoming_msg_handler: Callable[[Any, str], str] = None
        self._is_opened_ = False

    def open(self) -> None:
        """
        Initializes a new connection

        :return: None
        :rtype: None
        """
        print("Opening connection")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("localhost", 3000))
        self.sock.settimeout(1)
        print("Connection opened")
        self._is_opened_ = True

    def bind_and_setup_listening(self):
        try:
            """
            Binds the passed port for new connections

            :return: None
            :rtype: None
            """
            print("Binding port 3001")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(("localhost", 3001))
            self.sock.settimeout(1)
            print("Port binding done")
            self.sock.listen()
            self._is_opened_ = True
            start_new_thread(self.accept_new_connections_loop, ())
            print("Port bound and listener started")
        except Exception as exc:
            print('error')

    def set_message_handler(self, handler: Callable[[Any, str], str]):
        """
        Sets the handler function for messages received on the listened port

        :param handler: handler function for incoming messages on bound port. only required if you will be \
            listening on that specific port in order to be able to notify whoever it may interest. 

            The handler function may return a value. That value will be used to reply to the received message. \
            If the returned value is None, no message will be sent
        :type handler: Callable[[Any, str], str]
        :return: 
        :rtype: 
        """
        self.incoming_msg_handler = handler

    def send_message(self, message: str):
        print(f"Sending message '{message}'")
        self.sock.send(str.encode(f'{message}\n'))

    def receive_message_with_stop_byte(self) -> str:
        """
        Reads a message from the TCP stream until it encounters the stop byte
        :return: read message 
        :rtype: str
        """
        print(f"Starting to read reply")
        reply = self.__read_until_stop_byte_or_timeout__(self.sock)
        print(f"Reply length - {len(reply)}. Reply - '{reply}'")
        return reply

    def transact_message(self, message: str) -> str:
        """
        Sends a message and receives an answer until stopbyte is received
        :param message: message to send
        :type message: str
        :return: received answer
        :rtype: str
        """
        print(f"Transacting message {message}")
        self.send_message(message)
        sleep(2)
        reply = self.receive_message_with_stop_byte()
        return reply

    def accept_new_connections_loop(self):
        print('Nueva Conexion TCP')
        while self._is_opened_:
            try:
                conn, address = self.sock.accept()
                print(f"Accepted a new connection on. Starting handler thread")
                start_new_thread(self.handle_client_messages_loop, (conn, address))
            except  Exception:
                pass

    def handle_client_messages_loop(self, connection, address):
        while self._is_opened_:
            try:
                result = self.__read_until_stop_byte_or_timeout__(connection)
                if result and self.incoming_msg_handler is not None:
                    result=result.replace('\r','')
                    print(f"New message on port {address}: {result} ")
                    reply_to_send = ''
                    try:
                        reply_to_send = self.incoming_msg_handler(result)
                    except Exception as e:
                        print(e)
                    if reply_to_send:
                        print(f"Callback returned {reply_to_send}. Replying")
                        connection.send(str.encode(reply_to_send))
                else:
                    sleep(0.5)
            except Exception as e:
                print(f'Error en el LOOP del Monedero')

    def close(self) -> None:
        self._is_opened_ = False
        if self.sock is not None:
            self.sock.close()
        self.sock = None

    def __read_until_stop_byte_or_timeout__(self, connection: socket.socket) -> str:
        """
        Reads the TCP stream until the end char is met

        :return: full response
        :rtype: str
        """
        result: str = ""
        while True:
            try:
                current_char = connection.recv(1)
                if current_char == self.read_stop_byte:  # /n /r
                    break
                result += bytes.decode(current_char)
            except TimeoutError:
                break
            except OSError:
                break
        return result

