import os
try:
    from ..pygologin.gologin import GoLogin
except ImportError:
    from farm.pygologin.gologin import GoLogin


class GoLoginBase:
    def __init__(self, profile_id):
        self.gl = GoLogin({
            'token': os.getenv('GOLOGIN_API_TOKEN'),
            'profile_id': profile_id
        })

    def __call__(self, *args, **kwargs):
        return self.gl.start()

    def _create_profile(self):
        pass


if __name__ == '__main__':
    pass
