"""
General utility functions
"""
import os
import platform


def format_path(path: str) -> str:
    if path.startswith('..'):
        path = os.path.dirname(__file__) + '/' + path

    if platform.system() == "Windows":
        return path.replace('/', '\\')
    else:
        return path

def get_client_secret(method: str = 'file'):
    """
    :return: the Spotify client secret, using the specified method
    """
    if method == 'file':
        with open(format_path('../confs/client_secret.conf'), 'r') as f:
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
        with open(format_path('../confs/client_id.conf'), 'r') as f:
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
        with open(format_path('../confs/wled.conf'), 'r') as f:
            return f.read()
    else:
        raise ValueError(f"Invalid method {method}")