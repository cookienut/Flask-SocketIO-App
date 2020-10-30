"""
This file containts the server side code for the RED APPLE SERVER.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

import os
import sys

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, send


RED_SERVER_NS = "/red"
GRN_CLIENT_NS = "/green"

GRN_SERVER_HOST = "localhost"
GRN_SERVER_PORT = "9000"

global shared_var
shared_var = []

from collections import defaultdict
from socketio import Client, ClientNamespace


class GreenAppleServer:
    """Class for Green Apple Server
    """


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


    def run(self):
        """ """
        print(f"Starting server on '{GRN_SERVER_HOST}:{GRN_SERVER_PORT}'")
        self.sio_server.run(
            self.app, host=GRN_SERVER_HOST, port=GRN_SERVER_PORT
        )
        print("Server closed.")


if __name__ == '__main__':
    GreenAppleServer().run()
