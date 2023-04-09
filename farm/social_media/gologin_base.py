import requests
try:
    from ..drivers.pygologin.gologin import GoLogin
except ImportError:
    from farm.drivers.pygologin.gologin import GoLogin


class GoLoginBase:
    def __init__(self, api_token):
        self.gl = GoLogin({
            'token': '',
            'profile_id': ''
        })

    def _create_profile(self):
        pass


if __name__ == '__main__':
    pass
