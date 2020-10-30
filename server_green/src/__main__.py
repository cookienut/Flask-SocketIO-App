#!/bin/env python
"""This file has the code for running the Red-Apple Server.

This file additionally has the code for invoking a SocketIO client to listen to
the data published by the Green-Apple server. The socket client and the running
Red-Apple server exchange data using shared class variables.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

from listener import Listener
from server import RedAppleServer
from settings import RedServerConstants as consts


# Listener(
#     host=consts.grn_server_host,
#     port=consts.grn_server_port,
#     client_namespace=consts.grn_client_nmsp,
#     server_namespace=consts.grn_client_nmsp
# ).run()

RedAppleServer(
    host=consts.red_server_host,
    port=consts.red_server_port,
    client_namespace=consts.red_client_nmsp,
    server_namespace=consts.red_client_nmsp
).run()
