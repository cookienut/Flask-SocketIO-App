#!/bin/env python
"""
This file holds the constant settings to be used for running Red-Apple server.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""


class RedServerConstants:
    """Class for constants used in Red Apple Server.
    """

    red_client_nmsp = "/red"        # Namespace for connecting to red clients
    red_server_port = "8000"        # Port for running red server
    red_server_host = "localhost"   # Host for running red server

    grn_client_nmsp = "/red"        # Namespace for connecting to green server
    grn_server_port = "9000"        # Port for connecting to green server
    grn_server_host = "localhost"   # Host for connecting to green server
