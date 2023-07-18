"""
General utility functions
"""
import os


def get_client_secret(method: str = 'file'):
    """
    :return: the Spotify client secret, using the specified method
    """
    if method == 'file':
        with open('client_secret.conf', 'r') as f:
            return f.read()
    elif method == 'env':
        return os.environ['SPOTIFY_CLIENT_SECRET']
    else:
        raise ValueError(f"Invalid method {method}")

def get_client_id(method: str = 'file'):
    """
    :return: the Spotify client ID, using the specified method
    """
    if method == 'file':
        with open('client_id.conf', 'r') as f:
            return f.read()
    elif method == 'env':
        return os.environ['SPOTIFY_CLIENT_ID']
    else:
        raise ValueError(f"Invalid method {method}")

def get_target_address(method: str = 'file'):
    """
    :return: the Spotify client ID, using the specified method
    """
    if method == 'file':
        with open('wled.conf', 'r') as f:
            return f.read()
    else:
        raise ValueError(f"Invalid method {method}")