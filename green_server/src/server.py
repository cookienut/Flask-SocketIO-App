#!/bin/env python
"""This file has the code for running the green apple server.

The green apple server can be connected to any number of green clients and one
red apple server. It forwards the information supplied by green clients to the
red apple server so that it may be further propogated to red clients.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room


class GreenAppleServer:
    """Class, attributes and methods for the green apple server.

    :param self: The reference to class instance. This will be used to call
                 the instance methods and to access the instance variables.
    :param host: The host for running the green apple server. Defaults to
                 the host value as `0.0.0.0`.
    :param port: The port for running the green apple server. Defaults to
                 the port value as `5000`.
    :param args: The optional tuple of extra arguments to be passed to the
                 parent class init method.
    :param kwargs: The optional dict of keyworded arguments to be used or
                   passed to the parent class init method. Keywords such
                   as `consumer_namespace` and `producer_namespace` are
                   used to define namespace in current class. If not found,
                   both default to `/`. Rest of the keyworded arguments
                   are passed to the parent init method.
    """

    def __init__(self, host=None, port=None, *args, **kwargs):
        self.host = host or "0.0.0.0"
        self.port = port or "5000"
        self.consumer_namespace = kwargs.pop("consumer_namespace", "/")
        self.producer_namespace = kwargs.pop("producer_namespace", "/")

        self.sid_to_rooms_map = {}
        self.active_green_ids = []
        self.new_published_data = []

        self.app = Flask(__name__)
        self.sio_server = SocketIO(self.app)
        super(GreenAppleServer, self).__init__(*args, **kwargs)

        # For server-to-server interaction (RedServer-GreenServer)
        namespace = self.consumer_namespace
        self.sio_server.on_event(
            "connect", self.on_connect_red_server, namespace=namespace
        )
        self.sio_server.on_event(
            "disconnect", self.on_disconnect_red_server, namespace=namespace
        )
        self.sio_server.on_event(
            "listen", self.on_listen_for_red_server, namespace=namespace
        )
        # For server-to-client interaction (GreenServer-GreenClient)
        namespace = self.producer_namespace
        self.sio_server.on_event(
            "disconnect", self.on_disconnect_green_client, namespace=namespace
        )
        self.sio_server.on_event(
            "incoming_data", self.on_incoming_client_data, namespace=namespace
        )
        self.sio_server.on_event(
            "join", self.on_join_green_client, namespace=namespace
        )

    def on_connect_red_server(self):
        """Connects red apple server to green apple server.

        This method gets called right before connecting red apple server to
        green apple server so as to forward the data published by the green
        clients, to the red clients. Upon collecting the data variable is
        reset to only publish fresh data after red server connected.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        print("< Red Apple Server connected >")
        self.new_published_data = []

    def on_disconnect_red_server(self):
        """Prints acknowledgement of disconnecting the red apple server.

        :param self: The reference to class instance.

        :return: None
        """
        print("< Red Apple Server disconnected >")

    def on_listen_for_red_server(self):
        """Listens to new incoming data published by any green clients.

        This method reads the class instance variable which holds the newly
        published data everytime it is called, parses the data and returns
        the active id of green clients and their published data.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: A dictionary with active green clients and the data. Example -
                    {
                        "data": [("123", data1), ("456", "data2")],
                        "active": ["123", "456", "789"]
                    }
        """
        data = {
            "data": None,
            "active": self.active_green_ids
        }
        if self.new_published_data:
            new_data = self.new_published_data.copy()
            self.new_published_data = []
            data["data"] = new_data
        return data

    def on_disconnect_green_client(self):
        """Removes the connected client and discards it as an inactive client.

        This method gets called right before disconnecting a client from the
        green apple server. It prints the acknowledgement and removes its id
        from the list of active green clients.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        room_id = self.sid_to_rooms_map.pop(request.sid, "XXX")
        try:
            self.active_green_ids.remove(room_id)
        except ValueError:
            pass
        print(f"< Client 'GRN{room_id}' disconnected >")

    def on_join_green_client(self, data):
        """Registers a new green client and validates duplicate connections.

        This method should be called as soon as a green client connects to the
        server to register its id as an active id.  If a green client with the
        same id is already connected, abort connection because duplicate id is
        not allowed.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.
        :param data: The dict data which holds the three digit ``id`` of the
                     new client. For example:
                        {"id": "123"}

        :return: None
        """
        if data["id"] in self.active_green_ids:
            emit("duplicate_connection", namespace=self.producer_namespace)
            return
        self.sid_to_rooms_map[request.sid] = data["id"]
        self.active_green_ids.append(data["id"])
        print(f"< Client 'GRN{data['id']}' connected >")

    def on_incoming_client_data(self, data):
        """Listens to new incoming data received from connected green clients.

        This method should get called everytime a green client publishes data.
        It appends the incoming data to class instance variable which is also
        shared by other connected clients.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.
        :param data: The dict which holds the three digit ``id`` of the sender
                     client and the published data. For example:
                        {"id": "123", "data": "some_data"}

        :return: None
        """
        self.new_published_data.append((data["id"], data["data"]))

    def run(self):
        """Runs an instance of green apple server.

        This method runs a Flask-SocketIO server and servers as the source of
        incoming data for the connected red apple server to propogate further.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        print(f"(Starting server on '{self.host}:{self.port}')")
        self.sio_server.run(self.app, host=self.host, port=self.port)
        print("Server closed.")
