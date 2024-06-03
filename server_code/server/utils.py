# Server module for utility functions
import anvil.server
import anvil.users
from importlib import import_module
from anvil.tables import app_tables
import anvil.secrets
import uuid
import datetime


@anvil.server.callable
def init_user_session(user_email=None, password=None):
    print('init_user_session', anvil.server.context)
    if user_email and password:
        user = anvil.users.login_with_email(user_email, password)
    else:
        user = anvil.users.get_user()

    if user is None:
        return None

    user_dict = dict(user)
    anvil.server.session['user_uid'] = user_dict['uid']
    anvil.server.session['user_timezone'] = user_dict['timezone']
    user_name = (user_dict.get('first_name') or 'User') + ' ' + (user_dict.get('last_name') or 'Name')
    anvil.server.session['user_name'] = user_name.strip()
    anvil.server.session['user_email'] = user_dict['email']
    anvil.server.session['user_permissions'] = user_dict.get('permissions') or {}
    locked_tenant = anvil.server.session['user_permissions'].get('locked_tenant', False)
    tenant_row = app_tables.tenants.get(uid=user_dict['tenant_uid'])
    tenant_uid = ''
    tenant_name = ''
    app_mode = ''
    if anvil.server.session['user_permissions'].get('super_admin', False):
        tenant_uid = '00000000-0000-0000-0000-000000000000'
        tenant_name = ''
        app_mode = 'Super Admin Mode'
        # anvil.server.session['tenant_uid'] = '00000000-0000-0000-0000-000000000000'
        # anvil.server.session['tenant_name'] = ''
    elif anvil.server.session['user_permissions'].get('developer', False):
        tenant_uid = '00000000-0000-0000-0000-000000000000'
        tenant_name = ''
        app_mode = 'Developer Mode'
    if app_mode == '' or locked_tenant:
        tenant_uid = tenant_row['uid']
        tenant_name = tenant_row['name']
    # if (not anvil.server.session['user_permissions'].get('super_admin', False)
    #         or anvil.server.session['user_permissions'].get('locked_tenant', False)):
    #     tenant_uid = tenant_row['uid']
    #     tenant_name += f": {tenant_row['name']}" if tenant_name else tenant_row['name']
    #     tenant_row = app_tables.tenants.get(uid=user_dict['tenant_uid'])
    anvil.server.session['tenant_uid'] = tenant_uid
    anvil.server.session['tenant_name'] = tenant_name
    anvil.server.session['account_name'] = tenant_name
    anvil.server.session['data_files'] = [{'uid': tenant_uid, 'name': tenant_row['name']}]
    anvil.server.session['app_mode'] = app_mode
    anvil.server.session['locked_tenant'] = locked_tenant

    save_logged_user()
    logged_user = get_logged_user()
    return logged_user


def save_logged_user(current_user=None):
    if current_user is None:
        logged_user = {
            'tenant_uid': anvil.server.session['tenant_uid'],
            'tenant_name': anvil.server.session['tenant_name'],
            'user_uid': anvil.server.session['user_uid'],
            'user_name': anvil.server.session['user_name'],
            'email': anvil.server.session['user_email'],
            'timezone': anvil.server.session['user_timezone'],
            'permissions': anvil.server.session['user_permissions'],
            'account_name': anvil.server.session['account_name'],
            'data_files': anvil.server.session['data_files'],
            'app_mode': anvil.server.session['app_mode'],
            'locked_tenant': anvil.server.session['locked_tenant'],
        }
    else:
        logged_user = current_user.copy()
        anvil.server.session['tenant_uid'] = logged_user['tenant_uid']
        anvil.server.session['tenant_name'] = logged_user['tenant_name']
        anvil.server.session['user_uid'] = logged_user['user_uid']
        anvil.server.session['user_name'] = logged_user['user_name']
        anvil.server.session['user_email'] = logged_user['email']
        anvil.server.session['user_timezone'] = logged_user['timezone']
        anvil.server.session['user_permissions'] = logged_user['permissions']
        anvil.server.session['account_name'] = logged_user['account_name']
        anvil.server.session['data_files'] = logged_user['data_files']
        anvil.server.session['app_mode'] = logged_user['app_mode'],
        anvil.server.session['locked_tenant'] = logged_user['locked_tenant']
    anvil.server.session['logged_user'] = logged_user
    try:
        anvil.server.cookies.local['logged_user'] = logged_user
    except anvil.server.CookieError:
        pass
    # print('save_logged_user', anvil.server.session['logged_user'])


@anvil.server.callable
def check_session(tag=None):
    print(f'session check {tag}', anvil.server.session)


@anvil.server.callable
def get_logged_user(background_task_id=None):
    # print('get_logged_user bg_task', background_task_id)
    if background_task_id:
        background_task_row = app_tables.app_background_tasks.get(task_id=background_task_id)
        if background_task_row:
            logged_user = background_task_row['logged_user']
        else:
            logged_user = {}
    else:
        logged_user = anvil.server.session.get('logged_user', None)
        if logged_user is None:
            try:
                logged_user = anvil.server.cookies.local.get('logged_user', {})
            except anvil.server.CookieError:
                logged_user = {}
    return logged_user.copy()


@anvil.server.callable
def set_current_tenant(tenant_uid=None):
    user = anvil.users.get_user()
    user_row = app_tables.users.get(uid=user['uid'])
    user_row.update(tenant_uid=tenant_uid)
    anvil.server.session['tenant_uid'] = tenant_uid
    init_user_session()
    return get_logged_user()


@anvil.server.callable
def set_tenant_admin(tenant_uid=None, tenant_name=None):
    user = anvil.users.get_user()
    user_row = app_tables.users.get(uid=user['uid'])
    user_permissions = user['permissions'] or {}
    if tenant_uid is None and tenant_name is None:
        tenant_uid = '00000000-0000-0000-0000-000000000000'
        tenant_name = 'Super Admin'
        anvil.server.session['tenant_uid'] = tenant_uid
        anvil.server.session['tenant_name'] = 'Super Admin'
        user_permissions.pop('locked_tenant', None)
        user_row.update(tenant_uid='00000000-0000-0000-0000-000000000000', permissions=user_permissions)
    else:
        if tenant_uid is None:
            tenant_row = app_tables.tenants.get(name=tenant_name)
        else:
            tenant_row = app_tables.tenants.get(uid=tenant_uid)
        user_permissions['locked_tenant'] = True
        user_row.update(tenant_uid=tenant_row['uid'], permissions=user_permissions)
        tenant_uid = tenant_row['uid']
        tenant_name = 'Super Admin: ' + tenant_row['name']
    anvil.server.session['tenant_uid'] = tenant_uid
    anvil.server.session['tenant_name'] = tenant_name
    anvil.server.session['user_permissions'] = user_permissions
    save_logged_user()
    return get_logged_user()


@anvil.server.callable
def set_tenant_system_user(tenant_uid):
    anvil.server.session['tenant_uid'] = tenant_uid
    anvil.server.session['user_uid'] = 'system'
    anvil.server.session['user_permissions'] = {}
    save_logged_user()
    print('set_tenant_system_user', anvil.server.session)


@anvil.server.callable
def signup_user(email, password, tenant_uid):
    try:
        user_row = anvil.users.signup_with_email(email, password)
        user_row['tenant_uid'] = tenant_uid
        user_row['uid'] = str(uuid.uuid4())
        # user_row['first_name'] = user_instance['first_name']
        # user_row['last_name'] = user_instance['last_name']
        # user_row['enabled'] = user_instance['enabled']
        return {
            'status': 'success',
            'error': None,
            'uid': user_row['uid'],
        }
    except Exception as e:
        print('error', e)
        return {
            'status': 'error',
            'error': str(e),
            'uid': None,
        }


@anvil.server.callable
def init_model_enumerations(module, model_list):
    models = import_module(module)
    for model, props in model_list.items():
        # print(model, props)
        view_config = {
            'model': props['model'],
            'columns': [{'name': props['text_field']}],
        }
        cls = getattr(models, view_config['model'], None)
        if cls:
            search_queries = props['search_queries'] if 'search_queries' in props else []
            filters = props['filters'] if 'filters' in props else {}
            model_list[model]['options'] = cls.get_grid_view(view_config, search_queries, filters)
            if props['text_field'] != 'name':
                # name_field = props['name_field'].split('.', 1)[0]
                for option in model_list[model]['options']:
                    option['name'] = option[props['text_field'].replace('.', '__')]
    return model_list


@anvil.server.callable
def init_enum_constants(module, enum_model):
    models = import_module(module)
    app_enum = getattr(models, enum_model)
    enum_list = {enum.name: enum.options for enum in app_enum.search()}
    return enum_list


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


@anvil.server.callable
def set_cookie(name, value):
    anvil.server.cookies.local[name] = value


@anvil.server.callable
def set_cookies(cookies):
    for name, value in cookies.items():
        anvil.server.cookies.local[name] = value


@anvil.server.callable
def get_cookie(name):
    print(anvil.server.cookies.local)
    return anvil.server.cookies.local.get(name, None)


@anvil.server.callable
def get_cookies():
    return anvil.server.cookies.local


@anvil.server.callable
def set_session_prop(name, value):
    anvil.server.session[name] = value


@anvil.server.callable
def get_session_prop(name):
    return anvil.server.session.get(name, None)
