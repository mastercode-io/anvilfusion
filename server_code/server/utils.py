# Server module for utility functions
import anvil
from importlib import import_module
from ..tools.utils import DotDict


@anvil.server.callable
def init_user_session():
    
    user_row = anvil.users.get_user()
    
    if user_row is None:
        return None

    anvil.server.session['user_uid'] = user_row['uid']
    anvil.server.session['tenant_uid'] = user_row['tenant_uid']
    anvil.server.session['timezone'] = user_row['timezone']
    anvil.server.session['email'] = user_row['email']
    logged_user = {
        'user_uid': anvil.server.session['user_uid'],
        'tenant_uid': anvil.server.session['tenant_uid'],
        'email': anvil.server.session['email'],
        'timezone': anvil.server.session['timezone']
    }
    return logged_user


@anvil.server.callable
def check_session(tag):
    print(f'seesion check {tag}', anvil.server.session)
    

@anvil.server.callable
def get_logged_user():
    logged_user = {
        'user_uid': anvil.server.session['user_uid'],
        'tenant_uid': anvil.server.session['tenant_uid'],
        'email': anvil.server.session['email'],
        'timezone': anvil.server.session['timezone']
    }
    return logged_user


@anvil.server.callable
def init_model_enumerations(model_list):
    model_module = import_module(anvil.server.session['dependency']['data_models'].split(".", 1)[1])
    for model, props in model_list.items():
        view_config = {
            'model': props['model'],
            'columns': [{'name': props['name_field']}],
        }
        cls = getattr(model_module, view_config['model'], None)
        if cls:
            search_queries = props['search_queries'] if 'search_queries' in props else []
            filters = props['filters'] if 'filters' in props else {}
            model_list[model]['options'] = cls.get_grid_view(view_config, search_queries, filters)
            if props['name_field'] != 'name':
                name_field = props['name_field'].split('.', 1)[0]
                for option in model_list[model]['options']:
                    option['name'] = option[name_field]

    model_enums = DotDict(model_list)
    print('model_enums', isinstance(model_enums, DotDict))
    return DotDict({'key': 'value'})
    # return DotDict(model_list)
