"""This file containts the server side code for the RED APPLE SERVER.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

import os
import sys

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, send

RED_CLIENT_NS = "/red"
RED_SERVER_HOST = "localhost"
RED_SERVER_PORT = "6000"

GRN_SERVER_NS = "/red"
GRN_SERVER_HOST = "localhost"
GRN_SERVER_PORT = "7000"

from collections import defaultdict
from socketio import Client, ClientNamespace


class SharedInfo:
    """
        Class which holds data shared between client and server sections of
        Red Apple Server.
    """
    new_supplied_data = defaultdict(list)
    active_green_ids = []

class SocketClient(ClientNamespace):
    """
        Client class for Red Apple Server to connect with Green Apple Server.
    """

    sio_client = Client(reconnection=False)

    def __init__(self, *args, **kwargs):
        super(SocketClient, self).__init__(*args, **kwargs)
        self.server_host = GRN_SERVER_HOST or "localhost"
        self.server_port = GRN_SERVER_PORT or 5000
        self.connect_url = f"http://{self.server_host}:{self.server_port}"

    def connect_server(self):
        """ """
        try:
            SocketClient.sio_client.connect(
                self.connect_url, namespaces=[GRN_SERVER_NS]
            )
        except (BadNamespaceError, ConnectionError) as ex:
            print(f"ERROR: {ex} (server unreachable or not running)")
            sys.exit(1)

    def disconnect_server(self):
        """ """
        print("Disconnecting...")
        SocketClient.sio_client.disconnect()

    def on_connect(self):
        print("Connected to Green Apple Server...")
        self.on_listening()

    def on_disconnect(self):
        print("on_disconnect called")

    def parse_new_data(self, received_data):
        """ """
        SharedInfo.active_green_ids = received_data["active"]
        if not received_data["data"]:
            return
        for (room_id, new_data) in received_data["data"]:
            SharedInfo.new_supplied_data[room_id].append(new_data)

    def on_listening(self):
        """ """
        print("Listening for new data...")
        while SocketClient.sio_client.connected:
            SocketClient.sio_client.emit(
                "listen_to_client",
                callback=self.parse_new_data,
                namespace=GRN_SERVER_NS
            )
            SocketClient.sio_client.sleep(0.5)


class RedAppleServer:
    """ Class for Red Apple Server """

    def __init__(self):

        self.active_red_sid_room = {}

        self.app = Flask(__name__)
        self.sio_server = SocketIO(self.app)

        self.sio_server.on_event(
            "disconnect", self.on_disconnect, namespace=RED_CLIENT_NS
        )
        self.sio_server.on_event(
            "join", self.on_join, namespace=RED_CLIENT_NS
        )
        self.sio_server.on_event(
            "leave", self.on_leave, namespace=RED_CLIENT_NS
        )
        self.sio_server.on_event(
            "send_new_data", self.on_send_new_data, namespace=RED_CLIENT_NS
        )

    def on_disconnect(self):
        """
        """
        print("On_disconnect on server called")
        self.on_leave()

    def on_send_new_data(self):
        """ """
        print("On supply callled")
        room_id = self.active_red_sid_room[request.sid]
        # While atleast one red client belonging to room exists
        while room_id in self.active_red_sid_room.values():
            self.sio_server.sleep(0.5)
            new_data = SharedInfo.new_supplied_data.get(room_id, None)
            if not new_data:
                continue
            new_data = new_data.copy()
            SharedInfo.new_supplied_data[room_id] = []
            emit("broadcast_message", new_data, room=room_id, namespace=RED_CLIENT_NS)

    def on_join(self, data):
        """ """
        print("on_join called by req.sid=", request.sid)
        room_id = data["id"]
        self.active_red_sid_room[request.sid] = room_id
        print("sid_red_client map: ", self.active_red_sid_room)
        print("Active Green", SharedInfo.active_green_ids)
        if room_id not in SharedInfo.active_green_ids:
            emit("abort_connection", f"Client 'GRN{room_id}' is unavailable.", namespace=RED_CLIENT_NS)
        else:
            join_room(room_id)

    def on_leave(self):
        """ """
        room_id = self.active_red_sid_room.pop(request.sid)
        leave_room(room_id)

    def run(self):
        """ """
        self.sio_server.run(
            self.app, host=RED_SERVER_HOST, port=RED_SERVER_PORT
        )


if __name__ == '__main__':
    green_server_conn = SocketClient(namespace=GRN_SERVER_NS)
    SocketClient.sio_client.register_namespace(green_server_conn)
    green_server_conn.connect_server()
    RedAppleServer().run()
