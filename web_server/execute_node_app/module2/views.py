from module2 import module2_blue

@module2_blue.route('/hello')
def hello2():
    return 'hello'

@module2_blue.route('/alluser')
def alluser():
    return 'alluser'


@module2_blue.route('/deluser')
def deluser():
    return 'deluser'