#!/bin/env python
"""
This file holds the constant settings to connect green clients to green server.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""


class GreenClientConstants:
    """Class for constants used for green client connections.
    """

    green_client_nmsp = "/green"    # Namespace for connecting to green clients
    green_server_nmsp = "/green"    # Namespace for connecting to green server
    green_server_port = "7000"      # Port for running green server
    green_server_host = "0.0.0.0"   # Host for running green server
