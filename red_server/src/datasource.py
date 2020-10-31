#!/bin/env python
"""This file holds data resources shared between red apple server components.

This file has the class in which saves the the information that needs to be
exchanged between various red apple server components.

Author: sagarbhat94@gmail.com (Sagar Bhat)
"""

from collections import defaultdict


class SharedResource:
    """Class to hold shared data for the `server` and `listener` components.

    This class has class variables to hold data which is shared between the
    `server` and `listener` components of red apple server i.e.  this class
    has variables updated and accessed during the `RedClient-RedAppleServer`
    connection and also during `RedAppleServer-GreenAppleServer` connection.

    Note: This should later be replaced by a database or similar.
    """
    active_green_ids = []
    green_server_connected = False
    new_published_data = defaultdict(list)
