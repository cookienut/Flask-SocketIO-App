#!/bin/env python
"""This file has code for listening to data published by green apple server.

This file has a class derived from SocketIO's `ClientNamespace` and consists
of instance methods to listen to data published by the green apple server.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

import sys

from socketio import Client, ClientNamespace
from socketio import exceptions as sio_exceptions

from datasource import SharedResource as shared_db


class Listener(ClientNamespace):
    """Class for listening to data publised by green apple server.
    """

    sio_client = Client(reconnection=False)

    def __init__(self, host=None, port=None, *args, **kwargs):
        self.host = host or "0.0.0.0"
        self.port = port or "5000"
        self.connect_url = f"http://{self.host}:{self.port}"
        self.client_namespace = kwargs.pop("client_namespace", "/")
        self.server_namespace = kwargs.pop("server_namespace", "/")
        super(Listener, self).__init__(namespace=self.client_namespace)

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
            Listener.sio_client.connect(
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
        print("< Disconnecting >")
        Listener.sio_client.disconnect()

    def on_connect(self):
        """Prints connection acknowledgement and starts listening for new data.

        This method gets invoked right before establishing a connection with
        the green apple server. It prints acknowledment and starts listening
        for any new published data till server or client disconnects.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        print("< Connected to Green Apple Server >")
        shared_db.green_server_connected = True
        self.on_listening()

    def on_disconnect(self):
        """Prints disconnect acknowledgement.

        This method gets invoked right before disconnecting a client from the
        server. It updates the boolean flag of shared data resource to notify
        that it cannot listen to the server anymore due to closed connection.

        :param self: The reference to class instance.

        :return: None
        """
        shared_db.green_server_connected = False
        print("< Disconnected from Green Apple Server >")

    def parse_new_data(self, data):
        """Updates the shared data resource with the published data.

        This method gets invoked as a callback right after detecting new data
        published by green apple server. It updates  the shared data resource
        with the green client id and its corresponding data.

        :param self: The reference to class instance.
        :param data: The dict of all active green client ids and new published
                     data as a list of tuple. For example:
                        {
                            "data": [("123", "data1"), ("456", "data2")],
                            "active": ["123", "456", "789"]
                        }

        :return: None
        """
        shared_db.active_green_ids = data["active"]
        if not data["data"]:
            return
        for (room_id, new_data) in data["data"]:
            shared_db.new_published_data[room_id].append(new_data)

    def on_listening(self):
        """Listens for any new published data forwarded by green apple server.

        This method gets invoked right after connecting with the green apple
        server and listens for published data continuously till connection is
        alive.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        while Listener.sio_client.connected:
            Listener.sio_client.emit(
                "listen",
                callback=self.parse_new_data,
                namespace=self.server_namespace
            )
            Listener.sio_client.sleep(0.5)

    def run(self):
        """Runs instance of SocketIO client to connect to green apple server.

        This method registers the instance variable  `client_namespace` as the
        official namespace of thr class object and then establishes connection
        with the green apple server.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        Listener.sio_client.register_namespace(self)
        self.connect_to_server()
