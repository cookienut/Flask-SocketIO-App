#!/bin/env python
"""This file has client code for retrieving data published by red apple server.

This file has a class derived from SocketIO's `ClientNamespace` and consists
of instance methods to listen to data published by the red apple server.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

import sys

from socketio import Client, ClientNamespace
from socketio import exceptions as sio_exceptions

class RedClient(ClientNamespace):
    """Class for listening to data publised by green apple server.
    """

    def __init__(self, host=None, port=None, *args, **kwargs):
        self.host = host or "0.0.0.0"
        self.port = port or "5000"
        self.connect_url = f"http://{self.host}:{self.port}"
        self.client_namespace = kwargs.pop("client_namespace", "/")
        self.server_namespace = kwargs.pop("server_namespace", "/")
        self.color = "RED"
        self.numID = input("Hello RED, enter three digit ID: ")
        self.colID = self.color + self.numID
        self.sio_client = Client(reconnection=False)
        super(RedClient, self).__init__(namespace=self.client_namespace)

    def connect_to_server(self):
        """Creates a connection with the red apple server.

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
            print(f"ERROR: {ex} (red server unreachable or not running)")
            sys.exit(1)

    def disconnect_from_server(self):
        """Closes client connection to the red apple server.

        This method is to be used to voluntarily disconnect client from server.
        It internally calls the `disconnect()` method of SocketIO client.

        :param self: The reference to class instance.

        :return: None
        """
        self.sio_client.disconnect()

    def pull_data(self):
        """Pulls new data ready to be published by red apple server.

        This method gets invoked as a callback right after establishing new
        connection with apple server. It makes call to server methods so as
        to retrieve published data.

        :param self: The reference to class instance.

        :return: None
        """
        self.sio_client.emit("new_data", namespace=self.server_namespace)

    def on_connect(self):
        """Prints connection acknowledgement and starts listening for new data.

        This method gets invoked right before establishing a connection with
        the red apple server. It prints acknowledment and starts listening
        for any new published data till server or client disconnects.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        print("<Connected to Red Apple Server >")
        join_data = {
            "id": self.numID
        }
        self.sio_client.emit(
            "join",
            join_data,
            callback=self.pull_data,
            namespace=self.server_namespace
        )

    def on_disconnect(self):
        """Prints disconnect acknowledgement.

        :param self: The reference to class instance.

        :return: None
        """
        print("< Disconnected from Red Apple Server >")

    def on_abort_connection(self, error):
        """Aborts connection and disconnects client from server.

        This method gets invoked if a corresponding green client doesn't exist
        or isn't connected to it's green apple server yet.

        :param self: The reference to class instance.
        :param error: Error string

        :return: None
        """
        print(f"ERROR: {error}")
        self.disconnect_from_server()

    def on_broadcast_message(self, data):
        """Broadcasted message received by red apple server.

        This method gets invoked when red apple server brodcasts data to
        all the red clients which are connected to the same room. For e.g.
        if server broadcasts message for id RED123, then all the clients
        with id as RED123, which are currently active will get invoked
        through this method call.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.
        :param data: The list of string messages from green clients which have
                     been forwarded by red apple server.

        :return: None
        """
        for _data in data:
            print("Received: ", _data)

    def run(self):
        """Runs instance of SocketIO client to connect to red apple server.

        This method registers the instance variable  `client_namespace` as the
        official namespace of thr class object and then establishes connection
        with the red apple server.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        print("============== RED CLIENT CONSOLE ==============")
        self.sio_client.register_namespace(self)
        self.connect_to_server()
