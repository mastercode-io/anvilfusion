# Server module for utility functions
import anvil.server
import anvil.users
from importlib import import_module
from anvil.tables import app_tables
import anvil.secrets
# from ..tools.utils import DotDict


@anvil.server.portable_class
@anvil.server.serializable_type
class DotDictServer(dict):
    def __getattr__(self, item):
        return self[item] if item in self else None

    def __setattr__(self, key, value):
        if key in self:
            self[key] = value if not isinstance(value, dict) else DotDictServer(value)
        else:
            super(DotDictServer, self).__setattr__(key, value)

    def __delattr__(self, item):
        if item in self:
            del self[item]
        else:
            super(DotDictServer, self).__delattr__(item)

    def __getitem__(self, key):
        item = super().__getitem__(key)
        if isinstance(item, dict):
            return DotDictServer(item)
        elif isinstance(item, list):
            return [DotDictServer(i) if isinstance(i, dict) else i for i in item]
        else:
            return item

    def __setitem__(self, key, value):
        self.__setattr__(key, value)


@anvil.server.callable
def init_user_session():
    
    user_row = anvil.users.get_user()
    
    if user_row is None:
        return None

    anvil.server.session['user_uid'] = user_row['uid']
    anvil.server.session['tenant_uid'] = user_row['tenant_uid']
    anvil.server.session['timezone'] = user_row['timezone']
    anvil.server.session['email'] = user_row['email']
    anvil.server.session['permissions'] = user_row['permissions']
    return get_logged_user()


@anvil.server.callable
def check_session(tag=None):
    print(f'session check {tag}', anvil.server.session)
    

@anvil.server.callable
def get_logged_user():
    logged_user = {
        'user_uid': anvil.server.session['user_uid'],
        'tenant_uid': anvil.server.session['tenant_uid'],
        'email': anvil.server.session['email'],
        'timezone': anvil.server.session['timezone'],
        'permissions': anvil.server.session['permissions'],
        # 'permissions': DotDictServer(anvil.server.session['permissions'])
    }
    return logged_user


@anvil.server.callable
def init_model_enumerations(module, model_list):
    models = import_module(module)
    for model, props in model_list.items():
        view_config = {
            'model': props['model'],
            'columns': [{'name': props['name_field']}],
        }
        cls = getattr(models, view_config['model'], None)
        if cls:
            search_queries = props['search_queries'] if 'search_queries' in props else []
            filters = props['filters'] if 'filters' in props else {}
            model_list[model]['options'] = cls.get_grid_view(view_config, search_queries, filters)
            if props['name_field'] != 'name':
                name_field = props['name_field'].split('.', 1)[0]
                for option in model_list[model]['options']:
                    option['name'] = option[name_field]
    return model_list


@anvil.server.callable
def check_table(table_name=None):
    try:
        table = getattr(app_tables, table_name)
        return table.list_columns()
    except Exception as e:
        return None


@anvil.server.callable
def get_secrets(*secret_names):
    return {secret: anvil.secrets.get_secret(secret) for secret in secret_names}
