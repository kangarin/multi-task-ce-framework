from flask import Flask, jsonify
from flask_restful import Api, Resource
import docker

app = Flask(__name__)
api = Api(app)
client = docker.from_env()

class GetContainersList(Resource):
    def get(self):
        containers_info = []

        for container in client.containers.list():
            container_info = {
                'id': container.id,
                'name': container.name,
                'ip': container.attrs['NetworkSettings']['IPAddress'],
                'port': container.attrs['NetworkSettings']['Ports'],
                'status': container.status,
                'image': container.attrs['Config']['Image']
            }
            containers_info.append(container_info)

        return jsonify({'containers': containers_info})

class GetContainerInfo(Resource):
    def get(self, container_id):
        container = client.containers.get(container_id)
        container_info = {
            'id': container.id,
            'name': container.name,
            'ip': container.attrs['NetworkSettings']['IPAddress'],
            'port': container.attrs['NetworkSettings']['Ports'],
            'status': container.status,
            'image': container.attrs['Config']['Image']
        }
        return jsonify({'container': container_info})


api.add_resource(GetContainersList, '/containers/info')
api.add_resource(GetContainerInfo, '/containers/<string:container_id>/info')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
