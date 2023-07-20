# Init and maintain user session variables
import anvil
import sys
from ..orm_client.utils import DotDict


# @anvil.server.callable
# def create_tenant(tenant_name=None):
#     if tenant_name is not None:
#         tenant = Tenant('name', tenant_name).save(audit=False)
#         return tenant


# @anvil.server.callable
# def signup_user(email=None, password=None, tenant_name=None):
#     if not email or not password or not tenant_name:
#         return None
#     tenant = Tenant.get_by('name', tenant_name)
#     user = anvil.users.signup_with_email(email, password)
#     user['uid'] = str(uuid.uuid4())
#     user['tenant_uid'] = tenant.uid


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
def init_model_enumerations(model_module, model_list):
    for model, props in model_list.items():
        view_config = {
            'model': props['model'],
            'columns': [{'name': props['name_field']}],
        }
        cls = getattr(sys.modules[model_module], view_config['model'])
        search_queries = props['search_queries'] if 'search_queries' in props else []
        filters = props['filters'] if 'filters' in props else {}
        model_list[model]['options'] = cls.get_grid_view(view_config, search_queries, filters)
        if props['name_field'] != 'name':
            name_field = props['name_field'].split('.', 1)[0]
            for option in model_list[model]['options']:
                option['name'] = option[name_field]

    return DotDict(model_list)
