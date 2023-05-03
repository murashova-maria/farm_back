import os
try:
    from ..spygologin.gologin import GoLogin
except ImportError:
    from farm.spygologin.gologin import GoLogin


class GoLoginBase:
    def __init__(self, profile_id):
        self.gl = GoLogin({
            'token': os.getenv('GOLOGIN_API_TOKEN'),
            'profile_id': profile_id,
            "uploadCookiesToServer": True,
            "extra_params": ["--disable-notifications", "--no-sandbox", "--start-maximized"],
        })

    def __call__(self, *args, **kwargs):
        return self.gl

    def _create_profile(self):
        pass


if __name__ == '__main__':
    pass
