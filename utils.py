import numpy as np
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def find_best_fitting_plane(points):
    """Find the best fitting plane for given points"""
    centroid = np.mean(points, axis=0)
    centered = points - centroid
    _, _, vh = np.linalg.svd(centered)
    normal = vh[2]  # The third row is the normal to the best-fit plane
    return centroid, normal

def is_internet_connected():
    """Checks if there is an active internet connection."""
    import socket
    try:
        # Host: Google Public DNS (8.8.8.8)
        # Port: 53 (DNS)
        # Timeout: 3 seconds
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except socket.error:
        return False