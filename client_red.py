"""
This file containts the server side code for the RED APPLE SERVER.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

import sys

from socketio import Client, ClientNamespace
from socketio.exceptions import BadNamespaceError, ConnectionError

# Red Apple server configuration
RED_SERVER_NS = "/red"
RED_SERVER_HOST = "localhost"
RED_SERVER_PORT = "6000"

CONSOLE_BANNER = "\n============== RED CLIENT CONSOLE =============="


class RedClient(ClientNamespace):
    """ Consumer class for Red clients. """

    def __init__(self, *args, **kwargs):
        super(RedClient, self).__init__(*args, **kwargs)
        # Color config
        self.color = "RED"
        self.numID = input("Hello RED, enter three digit ID: ")
        self.colID = self.color + self.numID
        # Connection Config
        self.sio = Client(reconnection=False)
        self.server_host = RED_SERVER_HOST or "localhost"
        self.server_port = RED_SERVER_PORT or 5000
        self.connect_url = f"http://{self.server_host}:{self.server_port}"

    def connect_server(self):
        """ """
        try:
            self.connect_url = f"http://{RED_SERVER_HOST}:{RED_SERVER_PORT}"
            self.sio.connect(self.connect_url)
        except ConnectionError as ex:
            print(f"ERROR: {ex} (server unreachable or not running)")
            sys.exit(1)

    def disconnect_server(self):
        """ """
        print("Disconnecting...")
        self.sio.disconnect()

    def pull_data(self):
        """ """
        print("Pulling data")
        self.sio.emit("new_data", namespace=RED_SERVER_NS)

    def on_connect(self):
        print("<Connected to Red-Apple Server >")
        join_data = {
            "id": self.numID
        }
        self.sio.emit(
            "join",
            join_data,
            callback=self.pull_data,
            namespace=RED_SERVER_NS
        )

    def on_disconnect(self):
        print("on_disconnect called")

    def on_abort_connection(self, data):
        print(f"ERROR: {data}")
        self.disconnect_server()

    def on_broadcast_message(self, data):
        for _data_ in data:
            print("Received: ", _data_)


if __name__ == "__main__":
    # Initiate connection
    print(CONSOLE_BANNER)
    try:
        red_client = RedClient(namespace=RED_SERVER_NS)
        red_client.sio.register_namespace(red_client)
        red_client.connect_server()
    except Exception as ex:
        print(f"ERROR: {ex}")
        red_client.disconnect_server()
