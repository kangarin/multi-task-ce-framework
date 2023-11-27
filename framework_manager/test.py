from flask import Flask, request, jsonify
import docker

app = Flask(__name__)
client = docker.from_env()

@app.route('/start_containers', methods=['POST'])
def start_containers():
    data = request.get_json()
    image_name = data['image_name']
    instance_count = data['instance_count']

    for _ in range(instance_count):
        container = client.containers.run(image_name, detach=True)
        # 这里你可以记录容器的信息，例如容器ID、IP和端口等

    return jsonify({'message': f'Started {instance_count} containers for {image_name}'})

@app.route('/stop_container/<container_id>', methods=['POST'])
def stop_container(container_id):
    container = client.containers.get(container_id)
    container.stop()
    return jsonify({'message': f'Container {container_id} stopped'})

@app.route('/get_containers_info', methods=['GET'])
def get_containers_info():
    containers_info = []

    for container in client.containers.list():
        container_info = {
            'id': container.id,
            'ip': container.attrs['NetworkSettings']['IPAddress'],
            'port': container.attrs['NetworkSettings']['Ports']
        }
        containers_info.append(container_info)

    return jsonify({'containers': containers_info})

@app.route('/send_command/<container_id>', methods=['POST'])
def send_command(container_id):
    data = request.get_json()
    command = data['command']

    container = client.containers.get(container_id)
    # 在这里执行发送命令的逻辑

    return jsonify({'message': f'Command "{command}" sent to Container {container_id}'})

if __name__ == '__main__':
    app.run(debug=True)
