from module1 import module1_blue

@module1_blue.route('/hello')
def hello1():
    return 'hello'

@module1_blue.route('/register')
def register():
    return 'register'

@module1_blue.route('/login')
def login():
    return 'login'

@module1_blue.route('/modify_password')
def modify_password():
    return 'modify_password'