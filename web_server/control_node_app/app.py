from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'



from application_management import application_management_blue
from node_management import node_management_blue

app.register_blueprint(application_management_blue)
app.register_blueprint(node_management_blue)



if __name__ == '__main__':
    app.run(port=8798)