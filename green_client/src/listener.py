#!/bin/env python
"""This file has client code for publishing data to green apple server.

This file has a class derived from SocketIO's `ClientNamespace` and consists
of instance methods to supply data to green apple server which forwards it
further to red apple server and then eventually to red clients.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

import sys

from socketio import Client, ClientNamespace
from socketio import exceptions as sio_exceptions

class GreenClient(ClientNamespace):
    """Class for publishing data to green apple server.
    """

    def __init__(self, host=None, port=None, *args, **kwargs):
        self.host = host or "0.0.0.0"
        self.port = port or "5000"
        self.connect_url = f"http://{self.host}:{self.port}"
        self.client_namespace = kwargs.pop("client_namespace", "/")
        self.server_namespace = kwargs.pop("server_namespace", "/")
        self.color = "GRN"
        self.numID = input("Hello GRN, enter three digit ID: ")
        self.colID = self.color + self.numID
        self.sio_client = Client(reconnection=False)
        super(GreenClient, self).__init__(namespace=self.client_namespace)

    def connect_to_server(self):
        """Creates a connection with the green apple server.

        This method is to be used for initiating a connection with a server.
        It uses the `host`, `port` and `namespaces` defined during the class
        instantiation or their corresponding defaults, to create a websocket
        connection using SocketIO client.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        try:
            self.sio_client.connect(
                self.connect_url, namespaces=[self.server_namespace]
            )
        except sio_exceptions.BadNamespaceError as ex:
            print(f"ERROR: {ex} (possibly wrong namespace, check again)")
            sys.exit(1)
        except sio_exceptions.ConnectionError as ex:
            print(f"ERROR: {ex} (green server unreachable or not running)")
            sys.exit(1)

    def disconnect_from_server(self):
        """Closes client connection to the green apple server.

        This method is to be used to voluntarily disconnect client from server.
        It internally calls the `disconnect()` method of SocketIO client.

        :param self: The reference to class instance.

        :return: None
        """
        try:
            self.sio_client.disconnect()
        except:
            pass

    def send_data(self):
        """Sends new data to be received by green apple server.

        This method continuously supplies data to connected green apple server
        till connection is alive. If input data is put as `<q>`, it breaks the
        loop and disconnects the client from server. Otherwise, emits the data
        to be further forwarded till it reaches the appropriate red clients.

        :param self: The reference to class instance.

        :return: None
        """
        while True:
            inp = input(f"{self.colID}> ")
            if inp.strip() == "<q>":
                self.disconnect_from_server()
                sys.exit(0)
            data = {
                "id": self.numID,
                "data": inp
            }
            if self.sio_client.connected:
                self.sio_client.emit(
                    "incoming_data", data, namespace=self.server_namespace
                )
                continue
            self.disconnect_server()
            break

    def on_connect(self):
        """Prints connection acknowledgement and starts publishing new data.

        This method gets invoked right before establishing a connection with
        green apple server. It prints acknowledment and calls the `on_join`
        method of green apple server, which as a callback calls the method
        `send_data` of the client.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        print("<Connected to Green Apple Server >")
        join_data = {
            "id": self.numID
        }
        self.sio_client.emit(
            "join",
            join_data,
            callback=self.send_data,
            namespace=self.server_namespace
        )

    def on_disconnect(self):
        """Prints disconnect acknowledgement.

        :param self: The reference to class instance.

        :return: None
        """
        print("< Disconnected from Green Apple Server >")

    def on_duplicate_connection(self):
        """Closes duplicate connection by disconnecting client from server.

        This method gets invoked if a green client with the same three digit id
        is already connected to the green apple server.

        :param self: The reference to class instance.

        :return: None
        """
        print(f"ERROR: One instance of '{self.colID}' is already running.")
        self.disconnect_from_server()

    def run(self):
        """Runs instance of SocketIO client to connect to green apple server.

        This method registers the instance variable  `client_namespace` as the
        official namespace of thr class object and then establishes connection
        with the green apple server.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        print("======== GREEN CLIENT CONSOLE [use <q> to Exit] ==========")
        self.sio_client.register_namespace(self)
        self.connect_to_server()
