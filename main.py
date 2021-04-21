from configs import get_app_and_login_manager

app, login_manager = get_app_and_login_manager()

from views import *

if __name__ == '__main__':
    app.run()
