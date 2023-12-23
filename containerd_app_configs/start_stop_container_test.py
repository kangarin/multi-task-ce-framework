
import json
def parse_json_for_generators(json_file):
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    generators = json_data['services']['generators']
    return generators

def parse_json_for_processors(json_file):
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    processors = json_data['services']['processors']
    return processors

def parse_json_for_distributors(json_file):
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    distributors = json_data['services']['distributors']
    return distributors

def parse_json_for_aggregators(json_file):
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    aggregators = json_data['services']['aggregators']
    return aggregators

def start_generators(generators):
    for generator in generators:
        generator_id = generator['id']
        image = generator['execution_params']['image']
        env = generator['execution_params']['env']
        network = generator['execution_params']['network']
        container_name = generator['execution_params']['container_name']
        ports = generator['execution_params']['ports']
        volumes = generator['execution_params']['volumes']
        # print(generator_id, image, env, network, container_name, ports, volumes)
        client.containers.run(image, detach=True, environment=env, network=network, name=container_name, ports=ports)

def start_processors_of_stage(processors, stage):
    for processor in processors:
        if processor['stage'] == stage:
            for processor_instance in processor['instances']:
                processor_id = processor_instance['id']
                image = processor_instance['execution_params']['image']
                env = processor_instance['execution_params']['env']
                network = processor_instance['execution_params']['network']
                container_name = processor_instance['execution_params']['container_name']
                ports = processor_instance['execution_params']['ports']
                volumes = processor_instance['execution_params']['volumes']
                # print(processor_id, image, env, network, container_name, ports, volumes)
                client.containers.run(image, detach=True, environment=env, network=network, name=container_name, ports=ports)

def start_distributors(distributors):
    for distributor in distributors:
        distributor_id = distributor['id']
        image = distributor['execution_params']['image']
        env = distributor['execution_params']['env']
        network = distributor['execution_params']['network']
        container_name = distributor['execution_params']['container_name']
        ports = distributor['execution_params']['ports']
        volumes = distributor['execution_params']['volumes']
        # print(distributor_id, image, env, network, container_name, ports, volumes)
        client.containers.run(image, detach=True, environment=env, network=network, name=container_name, ports=ports)

def start_aggregators(aggregators):
    for aggregator in aggregators:
        aggregator_id = aggregator['id']
        image = aggregator['execution_params']['image']
        env = aggregator['execution_params']['env']
        network = aggregator['execution_params']['network']
        container_name = aggregator['execution_params']['container_name']
        ports = aggregator['execution_params']['ports']
        volumes = aggregator['execution_params']['volumes']
        # print(aggregator_id, image, env, network, container_name, ports, volumes)
        client.containers.run(image, detach=True, environment=env, network=network, name=container_name, ports=ports)

if __name__ == '__main__':

    import docker
    client = docker.from_env()

    import argparse
    parser = argparse.ArgumentParser(description='Video generator')
    parser.add_argument('--config', type=str, help='app config file')
    config_file = parser.parse_args().config
    config_file = "containerd_app_configs/test_config.json"
    generators = parse_json_for_generators(config_file)
    start_generators(generators)
    processors = parse_json_for_processors(config_file)
    start_processors_of_stage(processors, '1')
    start_processors_of_stage(processors, '2')
    distributors = parse_json_for_distributors(config_file)
    start_distributors(distributors)
    aggregators = parse_json_for_aggregators(config_file)
    start_aggregators(aggregators)
