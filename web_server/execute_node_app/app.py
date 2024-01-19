from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'



from module1 import module1_blue
from module2 import module2_blue

app.register_blueprint(module1_blue)
app.register_blueprint(module2_blue)



if __name__ == '__main__':
    app.run(port=8798)