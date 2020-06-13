__version__ = "1.0.9"

import importlib

api_key=None

# auth module shortcut
auth_module = importlib.import_module('.auth', package='tightai')
auth = auth_module.Auth()
login = auth.login
logout = auth.logout


# project module shortcut
projects = importlib.import_module('.projects', package='tightai')


