# Helper classes and functions
from anvil import app
import anvil.server
import anvil.users
import sys
import re
import uuid
import datetime
from .._version import __version__, __environment__


# name string conversions
def print_exception(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_no = exc_tb.tb_lineno
    print(f"Exception occurred: {e}, in file: {file_name}, at line: {line_no}")


def get_plural_name(name):
    if name.endswith('y'):
        return name[:-1] + 'ies'
    elif name[-1] in 'sx' or name[-2:] in ['sh', 'ch']:
        return name + 'es'
    else:
        return name + 's'


def get_singular_name(name):
    if name.endswith('ies'):
        return name[:-3] + 'y'
    elif name.endswith('es'):
        return name[:-2]
    elif name.endswith('s'):
        return name[:-1]
    else:
        return name


def get_table_name(name):
    return camel_to_snake(name)


def camel_to_snake(string):
    """Convert a CamelCase string to snake_case"""
    return '_'.join(re.findall('[A-Z][^A-Z]*', string)).lower()


def camel_to_title(string):
    """Convert a CamelCase string to Title Case"""
    return ' '.join(re.findall('[A-Z][^A-Z]*', string))


def snake_to_camel(string):
    """Convert a snakle_case string to CamelCase"""
    first, *rest = string.split('_')
    return ''.join([first.title(), *map(str.title, rest)])


def label_to_id(label):
    return label.lower().replace(' ', '_')


# compose ui element id
def get_form_field_id(form_id, field_name):
    return f"{form_id}_{field_name}"


def new_el_id():
    return f"q{str(uuid.uuid4()).replace('-', '')}"


# get python module attribute by string name
def str_to_attr(module_name, attr_name):
    attr = getattr(sys.modules[module_name], attr_name) if hasattr(sys.modules[module_name], attr_name) else None
    return attr


def datetime_py_to_js(dt):
    return anvil.js.window.Date(int(dt.strftime('%s')) * 1000)


def datetime_js_to_py(dt):
    return datetime.datetime.fromtimestamp(dt.getTime() / 1000)


def time_js_to_py(time):
    return datetime.datetime(1970, 1, 1, time.getHours(), time.getMinutes())


def set_cookie(name, value):
    anvil.server.call('set_cookie', name, value)


def set_cookies(cookies):
    anvil.server.call('set_cookies', cookies)


def get_cookie(name):
    return anvil.server.call('get_cookie', name)


def get_cookies():
    return anvil.server.call('get_cookies')


# Application environment cache
# Initialise user session and store user info app session
def init_user_session(login_form=None, after_login=None, user_email=None, password=None):
    print('--- App Info ---')
    print(f'AnvilFusion version: {__version__} ({__environment__})')
    print(f'git branch: {app.branch}')
    print(f'environment: {app.environment.name} ({app.environment.tags})')
    print(f'id: {app.id}')
    stim0 = datetime.datetime.now()
    # anvil.users.get_user()
    stim1 = datetime.datetime.now()
    print(f'get_user: {stim1 - stim0}')
    # anvil.server.call('check_session', 'a')
    stime2 = datetime.datetime.now()
    print(f'check_session: {stime2 - stim1}')
    logged_user = anvil.server.call('init_user_session', user_email=user_email, password=password)
    stime3 = datetime.datetime.now()
    print(f'init_user_session: {stime3 - stime2}')
    if not logged_user:
        if login_form:
            login_form = login_form(after_login=after_login)
            login_form.form_show()
        else:
            anvil.users.login_with_form()
        logged_user = anvil.server.call('init_user_session')
    print('USER: ', logged_user)
    anvil.server.call('check_session', 'b')
    stime4 = datetime.datetime.now()
    print(f'check_session 2: {stime4 - stime3}')
    return DotDict(logged_user) if logged_user else None


# Dictionary extension that allows dot notation access to keys
@anvil.server.portable_class
@anvil.server.serializable_type
class DotDict(dict):
    def __getattr__(self, item):
        return self[item] if item in self else None

    def __setattr__(self, key, value):
        if key in self:
            self[key] = value if not isinstance(value, dict) else DotDict(value)
        else:
            super(DotDict, self).__setattr__(key, value)

    def __delattr__(self, item):
        if item in self:
            del self[item]
        else:
            super(DotDict, self).__delattr__(item)

    def __getitem__(self, key):
        item = super().__getitem__(key)
        if isinstance(item, dict):
            return DotDict(item)
        elif isinstance(item, list):
            return [DotDict(i) if isinstance(i, dict) else i for i in item]
        else:
            return item


# Basic enumeration class for ORM client
class Enumeration:
    def __init__(self, values, upper_case=True):
        self._values = {}
        self._upper_case = upper_case
        for key, value in values.items():
            attr_name = key.upper() if upper_case is True else key
            self._values[attr_name] = self.Member(attr_name, value)

    def __setattr__(self, name, value):
        if name in ('_values', '_upper_case'):
            return object.__setattr__(self, name, value)
        attr_name = name.upper() if self.upper_case is True else name
        if attr_name in self._values:
            raise AttributeError(f"attribute '{attr_name}' is read-only")
        else:
            super().__setattr__(attr_name, value)

    def __getattr__(self, name):
        if name == '_values':
            return object.__getattribute__(self, '_values')
        if name in self._values:
            return self._values[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __delattr__(self, name):
        if '_values' not in self.__dict__:
            return super().__delattr__(name)
        if name in self._values:
            raise AttributeError(f"attribute '{name}' is read-only")
        else:
            super().__delattr__(name)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {', '.join(self._values.keys())}>"

    def __iter__(self):
        yield from self._values.keys()

    def __len__(self):
        return len(self._values)

    def __contains__(self, item):
        attr_name = item.upper() if self._upper_case is True else item
        return attr_name in self._values

    def __getitem__(self, name):
        attr_name = name.upper() if self._upper_case is True else name
        if attr_name in self._values:
            member = self._values[attr_name]
            return member.value if not isinstance(member.value, dict) else DotDict(member.value)
        return None

    class Member:
        def __init__(self, name, value):
            self.name = name
            self.value = value
            if isinstance(value, dict):
                for key, value in value.items():
                    setattr(self, key, value)


class AppEnv:
    APP_ID = None
    ANVIL_FUSION_VERSION = '0.0.1'
    content_container_id = None
    data_models = None
    forms = None
    views = None
    pages = None
    enum_models = None
    enum_constants = None
    grid_settings = {}
    theme = {}
    start_menu = None
    aws_config = {
        'region': None,
        'cognito_identity_pool_id': None,
        's3_bucket': None,
    }
    aws_access = None
    aws_s3 = None
    logged_user = DotDict({})
    login_user = None
    after_login = None
    navigation = None

    @staticmethod
    def init_enumerations(model_list=None):
        if model_list is None:
            model_list = {}
        AppEnv.enum_models = DotDict(
            anvil.server.call('init_model_enumerations', AppEnv.data_models.__name__, model_list)
        )

    @staticmethod
    def init_enum_constants():
        AppEnv.enum_constants = Enumeration(anvil.server.call(
            'init_enum_constants',
            AppEnv.data_models.__name__,
            'AppEnum',
        ))

    @staticmethod
    def set_tenant_admin(tenant_uid=None, tenant_name=None, reload_func=None):
        print(AppEnv, AppEnv.logged_user)
        if AppEnv.logged_user.permissions.super_admin or AppEnv.logged_user.permissions.developer:
            logged_user = anvil.server.call('set_tenant_admin',
                                            tenant_uid=tenant_uid,
                                            tenant_name=tenant_name)
            AppEnv.logged_user = DotDict(logged_user)
        if callable(reload_func):
            reload_func()

    @staticmethod
    def reset_tenant_admin(reload_func=None):
        if AppEnv.logged_user.permissions.super_admin or AppEnv.logged_user.permissions.developer:
            logged_user = anvil.server.call('set_tenant_admin')
            AppEnv.logged_user = DotDict(logged_user)
        if callable(reload_func):
            reload_func()
