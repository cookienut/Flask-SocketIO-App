#!/bin/env python
"""This file has the code for running the Red-Apple Server.

The red apple server is primarily connected to red clients only and also reads
from shared resources to propogate any supplied information to the clients.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room

from datasource import SharedResource as shared_db


class RedAppleServer:
    """Class, attributes and methods for the Red Apple Server.
    """

    def __init__(self, host=None, port=None, *args, **kwargs):
        self.sid_to_rooms_map = {}
        self.host = host or "0.0.0.0"
        self.port = port or "5000"
        self.client_namespace = kwargs.pop("client_namespace", "/")
        self.server_namespace = kwargs.pop("server_namespace", "/")
        self.app = Flask(__name__)
        self.sio_server = SocketIO(self.app)
        super(RedAppleServer, self).__init__(*args, **kwargs)

        self.sio_server.on_event(
            "disconnect", self.on_disconnect, namespace=self.server_namespace
        )
        self.sio_server.on_event(
            "join", self.on_join, namespace=self.server_namespace
        )
        self.sio_server.on_event(
            "leave", self.on_leave, namespace=self.server_namespace
        )
        self.sio_server.on_event(
            "new_data", self.on_new_data, namespace=self.server_namespace
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
        self.sio_server.run(self.app, host=self.host, port=self.port)
