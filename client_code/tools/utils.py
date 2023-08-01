# Helper classes and functions
import anvil.server
import sys
import re
import uuid
import datetime


# name string conversions
def print_exception(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_no = exc_tb.tb_lineno
    print(f"Exception occurred: {e}, in file: {file_name}, at line: {line_no}")


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


# compose ui element id
def get_form_field_id(form_id, field_name):
    return f"{form_id}_{field_name}"


def new_el_id():
    return str(uuid.uuid4()).replace('-', '')


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


# Application environment cache
class AppEnv:
    APP_ID = None
    data_models = None
    forms = None
    views = None
    pages = None
    enum_models = None
    
    
    @staticmethod
    def init_enumerations(model_list=None):
        if model_list is None:
            model_list = {}
        AppEnv.enum_models = DotDict(anvil.server.call('init_model_enumerations', AppEnv.data_models.__name__, model_list))
        # print('ENUMERATIONS: ', AppEnv.enumerations)


# Initialise user session and store user info app session
def init_user_session():
    anvil.server.call('check_session', 'a')
    logged_user = anvil.server.call('init_user_session')
    if not logged_user:
        anvil.users.login_with_form()
        logged_user = anvil.server.call('init_user_session')
    print('USER: ', logged_user)
    anvil.server.call('check_session', 'b')
    return logged_user


# Dictionary extension that allows dot notation access to keys
@anvil.server.portable_class
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

    class Member:
        def __init__(self, name, value):
            self.name = name
            self.value = value
            if isinstance(value, dict):
                for key, value in value.items():
                    setattr(self, key, value)

    def __getitem__(self, name):
        if name in self._values:
            return self._values[name]
        raise KeyError(name)
