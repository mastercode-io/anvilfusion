import anvil.server


def init_user_session():
    anvil.server.call('check_session', 'a')
    logged_user = anvil.server.call('init_user_session')
    if not logged_user:
        anvil.users.login_with_form()
        logged_user = anvil.server.call('init_user_session')
    print('USER: ', logged_user)
    anvil.server.call('check_session', 'b')
    return logged_user
