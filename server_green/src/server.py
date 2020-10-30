#!/bin/env python
"""This file has the code for running the green apple server.

This file additionally has the code for invoking a SocketIO client to listen to
the data published by the Green-Apple server. The socket client and the running
Red-Apple server exchange data using shared class variables.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room

from datasource import SharedResource as shared_db


class GreenAppleServer:
    """Class, attributes and methods for the green apple server.
    """

    def __init__(self, host=None, port=None, *args, **kwargs):
        self.host = host or "localhost"
        self.port = port or "5000"
        self.namespace = kwargs.pop("namespace", "/")
        self.consumer_namespace = kwargs.pop("consumer_namespace", "/")
        self.producer_namespace = kwargs.pop("producer_namespace", "/")
        self.sid_to_rooms_map = {}
        self.active_green_ids = []
        self.new_published_data = []
        self.app = Flask(__name__)
        self.sio_server = SocketIO(self.app)
        super(GreenAppleServer, self).__init__(*args, **kwargs)

        # For server-to-server interaction (RedServer-GreenServer)
        self.sio_server.on_event(
            "connect", self.on_server_connect, namespace=RED_SERVER_NS
        )
        self.sio_server.on_event(
            "disconnect", self.on_server_disconnect, namespace=RED_SERVER_NS
        )
        self.sio_server.on_event(
            "listen_to_client", self.listen_for_data, namespace=RED_SERVER_NS
        )
        # For server-to-client interaction (GreenServer-GreenClient)
        self.sio_server.on_event(
            "connect", self.on_client_connect, namespace=GRN_CLIENT_NS
        )
        self.sio_server.on_event(
            "disconnect", self.on_client_disconnect, namespace=GRN_CLIENT_NS
        )
        self.sio_server.on_event(
            "incoming_data", self.on_incoming_data, namespace=GRN_CLIENT_NS
        )
        self.sio_server.on_event(
            "join", self.on_client_join, namespace=GRN_CLIENT_NS
        )
        self.sio_server.on_event(
            "leave", self.on_client_leave, namespace=GRN_CLIENT_NS
        )

    def on_disconnect(self):
        """Removes the connected client from its corresponding room.

        This method gets called right before disconnecting a client from the
        red apple server.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        client = "RED" + self.sid_to_rooms_map.get(request.sid, "XXX")
        print(f"< One instance of '{client}' disconnected >")
        self.on_leave()

    def on_new_data(self):
        """Listens to new incoming data received from Green-Apple Server.

        This method reads the shared data resource which is shared between the
        redServer-greenServer and redClient-redServer connections. It new data
        is found, it broadcasts the data to all the corresponding red clients.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        room_id = self.sid_to_rooms_map[request.sid]
        # While atleast one red client belonging to room exists
        while room_id in self.sid_to_rooms_map.values():
            self.sio_server.sleep(0.2)
            new_data = shared_db.new_published_data.get(room_id, None)
            if not new_data:
                continue
            new_data = new_data.copy()
            shared_db.new_published_data[room_id] = []
            emit(
                "broadcast_message",
                new_data,
                room=room_id,
                namespace=self.client_namespace
            )

    def on_join(self, data):
        """Adds or registers a new connected red client to corresponding room.

        This method should be called as soon as a red client connects to the
        server so as to register it to some room based on its client id.  It
        aborts the connection if a green client with the same three digit id
        isn't connected to the green server at that point of time.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.
        :param data: The dict data which holds the three digit ``id`` of the
                     new client. For example:
                        {"id": "123"}

        :return: None
        """
        room_id = data["id"]
        self.sid_to_rooms_map[request.sid] = room_id
        if room_id not in shared_db.active_green_ids:
            emit(
                "abort_connection",
                f"Client 'GRN{room_id}' is unavailable.",
                namespace=self.client_namespace
            )
            return
        join_room(room_id)
        print(f"< One new instance of 'RED{room_id}' connected >")

    def on_leave(self):
        """Removes a red client from its registered room.

        This method should be called before any registered  client disconnects
        from the server so as to unregister it from corresponding room. The id
        of the client (or room) is retrieved using its session id.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        room_id = self.sid_to_rooms_map.pop(request.sid)
        leave_room(room_id)

    def run(self):
        """Runs an instance of Red-Apple server.

        This method runs a Flask-SocketIO server and servers as the source of
        incoming data for all the connected red clients.

        :param self: The reference to class instance. This will be used to call
                     the instance methods and to access the instance variables.

        :return: None
        """
        print(f"Starting server on '{self.host}:{self.port}'...")
        self.sio_server.run(self.app, host=self.host, port=self.port)
        print("Server closed.")






def __init__(self):

    self.sid_to_rooms_map = {}
    self.active_green_ids = []
    self.new_supplied_data = []

    self.app = Flask(__name__)
    self.sio_server = SocketIO(self.app)

    # For server-to-server interaction (RedServer-GreenServer)
    self.sio_server.on_event(
        "connect", self.on_server_connect, namespace=RED_SERVER_NS
    )
    self.sio_server.on_event(
        "disconnect", self.on_server_disconnect, namespace=RED_SERVER_NS
    )
    self.sio_server.on_event(
        "listen_to_client", self.listen_for_data, namespace=RED_SERVER_NS
    )
    # For server-to-client interaction (GreenServer-GreenClient)
    self.sio_server.on_event(
        "connect", self.on_client_connect, namespace=GRN_CLIENT_NS
    )
    self.sio_server.on_event(
        "disconnect", self.on_client_disconnect, namespace=GRN_CLIENT_NS
    )
    self.sio_server.on_event(
        "incoming_data", self.on_incoming_data, namespace=GRN_CLIENT_NS
    )
    self.sio_server.on_event(
        "join", self.on_client_join, namespace=GRN_CLIENT_NS
    )
    self.sio_server.on_event(
        "leave", self.on_client_leave, namespace=GRN_CLIENT_NS
    )

def on_server_connect(self):
    """Somethinfg
    """
    print("< Red Apple Server is Live >")
    self.new_supplied_data = []

def on_server_disconnect(self):
    """Somethinfg
    """
    print("< Red Apple Server disconnected >")

def listen_for_data(self):
    """Somethinfg
    """
    if self.new_supplied_data:
        data = self.new_supplied_data.copy()
        self.new_supplied_data = []
        return {"data": data, "active": self.active_green_ids}
    return {"data": None, "active": self.active_green_ids}

#HERE
def on_client_connect(self):
    print("On connect called")

def on_client_disconnect(self):
    print("On disconnect called")
    print(self.active_green_ids)
    try:
        room_id = self.sid_to_rooms_map.pop(request.sid)
        self.active_green_ids.remove(room_id)
    except (KeyError, ValueError):
        pass
    print(self.active_green_ids)
    print("Left")

def on_incoming_data(self, data):
    """ """
    self.new_supplied_data.append((data["id"], data["data"]))

def on_client_join(self, data):
    """ """
    if data["id"] in self.active_green_ids:
        emit("duplicate_connection", namespace=GRN_CLIENT_NS)
        return
    self.sid_to_rooms_map[request.sid] = data["id"]
    self.active_green_ids.append(data["id"])

def on_client_leave(self):
    """ """
    print("Left the Room")
