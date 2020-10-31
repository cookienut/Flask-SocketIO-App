#!/bin/env python
"""This file has the code for running the green apple server.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

from server import GreenAppleServer
from settings import GreenServerConstants as consts


GreenAppleServer(
    host=consts.grn_server_host,
    port=consts.grn_server_port,
    producer_namespace=consts.grn_client_nmsp,
    consumer_namespace=consts.red_server_nmsp
).run()
