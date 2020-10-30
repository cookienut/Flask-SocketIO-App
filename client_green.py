"""
This file containts the server side code for the RED APPLE SERVER.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

import sys

from socketio import Client, ClientNamespace
from socketio.exceptions import BadNamespaceError, ConnectionError

# Red Apple server configuration
GREEN_SERVER_NS = "/green"
GREEN_SERVER_HOST = "localhost"
GREEN_SERVER_PORT = 9000


CONSOLE_BANNER = "\n======== GREEN CLIENT CONSOLE [use <Q> to Exit] =========="

class GreenClient(ClientNamespace):
    """ Producer class for Green clients which supply data. """

    def __init__(self, *args, **kwargs):
        super(GreenClient, self).__init__(*args, **kwargs)
        # Color config
        self.color = "GRN"
        self.numID = input("Hello GRN, enter three digit ID: ")
        self.colID = self.color + self.numID
        # Connection Config
        self.sio = Client(reconnection=False)
        self.server_host = GREEN_SERVER_HOST or "localhost"
        self.server_port = GREEN_SERVER_PORT or 5000
        self.connect_url = f"http://{self.server_host}:{self.server_port}"

    def connect_server(self):
        """ """
        try:
            self.sio.connect(self.connect_url)
        except ConnectionError as ex:
            print(f"ERROR: {ex} (server unreachable or not running)")
            sys.exit(1)

    def disconnect_server(self):
        """ """
        print("Disconnecting...")
        self.sio.disconnect()

    def send_data(self):
        """ """
        while True:
            inp = input(f"{self.colID}> ")
            if inp.strip() == "<Q>":
                self.disconnect_server()
                sys.exit(0)
            data = {"id": self.numID, "data": inp}
            if self.sio.connected:
                self.sio.emit("incoming_data", data, namespace=GREEN_SERVER_NS)
                continue
            self.disconnect_server()
            break

    def on_connect(self):
        print("<Connected to Green-Apple Server>")
        join_data = {
            "id": self.numID
        }
        self.sio.emit(
            "join",
            join_data,
            callback=self.send_data,
            namespace=GREEN_SERVER_NS
        )

    def on_disconnect(self):
        print(f"< Green Apple Server closed or unreachable >")

    def on_duplicate_connection(self):
        print(f"ERROR: One instance of '{self.colID}' is already running.")
        self.disconnect_server()


if __name__ == "__main__":
    # Initiate connection
    print(CONSOLE_BANNER)
    try:
        green_client = GreenClient(namespace=GREEN_SERVER_NS)
        green_client.sio.register_namespace(green_client)
        green_client.connect_server()
    except Exception as ex:
        print(f"ERROR: {ex}")
        green_client.disconnect_server()
