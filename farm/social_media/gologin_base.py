import os
import socket
import random
from decouple import config
try:
    from ..spygologin.gologin import GoLogin
except ImportError:
    from farm.spygologin.gologin import GoLogin


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _, port = s.getsockname()
    return port


class GoLoginBase:
    def __init__(self, profile_id):
        self.gl = GoLogin({
            'token': os.getenv('GOLOGIN_API_TOKEN'),
            'profile_id': profile_id,
            'port': get_free_port(),
            "uploadCookiesToServer": True,
            "extra_params": ["--disable-notifications", "--no-sandbox", "--start-maximized"],
        })

    def __call__(self, *args, **kwargs):
        return self.gl

    def _create_profile(self):
        pass


if __name__ == '__main__':
    pass
