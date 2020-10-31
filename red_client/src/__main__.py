#!/bin/env python
"""This file has the code which connects the red client to red apple server.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

from listener import RedClient
from settings import RedClientConstants as consts

RedClient(
    host=consts.red_server_host,
    port=consts.red_server_port,
    client_namespace=consts.red_client_nmsp,
    server_namespace=consts.red_server_nmsp
).run()
