#!/bin/env python
"""This file has the code to connect a green client to the green apple server.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

from listener import GreenClient
from settings import GreenClientConstants as consts

GreenClient(
    host=consts.green_server_host,
    port=consts.green_server_port,
    client_namespace=consts.green_client_nmsp,
    server_namespace=consts.green_server_nmsp
).run()
