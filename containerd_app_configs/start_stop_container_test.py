{
    "application_name": "headup_detection",
    "description": "application for detecting students' heads up rate in class",
    "services": {
        "generators": [
            {
                "id": "1",
                "management_params":{
                    "service_name": "video_generator_1",
                    "description": "class A surveillance camera"
                },
                "execution_params":{
                    "image": "video_generator",
                    "env": {
                        "DATA_SOURCE": "rtsp://172.27.155.106:8554/mystream",
                        "MQTT_BROKER_IP": "172.27.155.106",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_TOPIC": "headup_detection/video_generator",
                        "REDIS_IP": "172.27.155.106",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_generator_1"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_generator_1",
                    "ports": {
                       "12345": "12345"
                    },
                    "volumes": {
                        "/home/edge/": "/home/edge/"
                    }
                }
            },
            {
                "id": "2",
                "management_params":{
                    "service_name": "video_generator_2",
                    "description": "class B surveillance camera"
                },
                "execution_params":{
                    "image": "video_generator",
                    "env": {
                        "DATA_SOURCE": "rtsp://172.27.155.106:8554/mystream",
                        "MQTT_BROKER_IP": "172.27.155.106",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_TOPIC": "headup_detection/video_generator",
                        "REDIS_IP": "172.27.155.106",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_generator_2"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_generator_2",
                    "ports": {
                        "12346": "12346"
                    },
                    "volumes": {
                        "/home/edge/": "/home/edge/"
                    }
                }
            }
        ],
        "processors": [
            {
                "stage": "1",
                "instances": [
                    {
                        "id": "1",
                        "management_params":{
                            "service_name": "video_processor_stage_1_instance_1",
                            "description": "video processor stage 1 instance 1"
                        },
                        "execution_params":{
                            "image": "video_processor_stage_1",
                            "env": {
                                "MQTT_BROKER_IP": "172.27.155.106",
                                "MQTT_BROKER_PORT": "1883",
                                "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_generator",
                                "MQTT_OUTGOING_TOPIC": "headup_detection/video_processor_stage_1",
                                "REDIS_IP": "172.27.155.106",
                                "REDIS_PORT": "6379",
                                "REDIS_DB": "0",
                                "REDIS_KEY": "headup_detection/video_processor_stage_1_instance_1"
                            },
                            "network": "headup_detection",
                            "container_name": "headup_detection_video_processor_stage_1_instance_1",
                            "ports": {

                            },
                            "volumes": {
                                "/home/edge/": "/home/edge/"
                            }
                        }
                    },
                    {
                        "id": "2",
                        "management_params":{
                            "service_name": "video_processor_stage_1_instance_2",
                            "description": "video processor stage 1 instance 2"
                        },
                        "execution_params":{
                            "image": "video_processor_stage_1",
                            "env": {
                                "MQTT_BROKER_IP": "172.27.155.106",
                                "MQTT_BROKER_PORT": "1883",
                                "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_generator",
                                "MQTT_OUTGOING_TOPIC": "headup_detection/video_processor_stage_1",
                                "REDIS_IP": "172.27.155.106",
                                "REDIS_PORT": "6379",
                                "REDIS_DB": "0",
                                "REDIS_KEY": "headup_detection/video_processor_stage_1_instance_2"
                            },
                            "network": "headup_detection",
                            "container_name": "headup_detection_video_processor_stage_1_instance_2",
                            "ports": {

                            },
                            "volumes": {
                                "/home/edge/": "/home/edge/"
                            }
                        }
                    }
                ]
            },
            {
                "stage": "2",
                "instances": [
                    {
                        "id": "1",
                        "management_params":{
                            "service_name": "video_processor_stage_2_instance_1",
                            "description": "video processor stage 2 instance 1"
                        },
                        "execution_params":{
                            "image": "video_processor_stage_2",
                            "env": {
                                "MQTT_BROKER_IP": "172.27.155.106",
                                "MQTT_BROKER_PORT": "1883",
                                "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_processor_stage_1",
                                "MQTT_OUTGOING_TOPIC": "headup_detection/video_processor_stage_2",
                                "REDIS_IP": "172.27.155.106",
                                "REDIS_PORT": "6379",
                                "REDIS_DB": "0",
                                "REDIS_KEY": "headup_detection/video_processor_stage_2_instance_1"
                            },
                            "network": "headup_detection",
                            "container_name": "headup_detection_video_processor_stage_2_instance_1",
                            "ports": {

                            },
                            "volumes": {
                                "/home/edge/": "/home/edge/"
                            }
                        }
                    },
                    {
                        "id": "2",
                        "management_params":{
                            "service_name": "video_processor_stage_2_instance_2",
                            "description": "video processor stage 2 instance 2"
                        },
                        "execution_params":{
                            "image": "video_processor_stage_2",
                            "env": {
                                "MQTT_BROKER_IP": "172.27.155.106",
                                "MQTT_BROKER_PORT": "1883",
                                "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_processor_stage_1",
                                "MQTT_OUTGOING_TOPIC": "headup_detection/video_processor_stage_2",
                                "REDIS_IP": "172.27.155.106",
                                "REDIS_PORT": "6379",
                                "REDIS_DB": "0",
                                "REDIS_KEY": "headup_detection/video_processor_stage_2_instance_2"
                            },
                            "network": "headup_detection",
                            "container_name": "headup_detection_video_processor_stage_2_instance_2",
                            "ports": {

                            },
                            "volumes": {
                                "/home/edge/": "/home/edge/"
                            }
                        }
                    }
                ]
            }
        ],
        "distributors": [
            {
                "id": "1",
                "management_params":{
                    "service_name": "video_distributor_1",
                    "description": "video distributor 1"
                },
                "execution_params":{
                    "image": "video_distributor",
                    "env": {
                        "MQTT_BROKER_IP": "172.27.155.106",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_processor_stage_2",
                        "MQTT_OUTGOING_TOPIC": [
                            "headup_detection/video_aggregator_1",
                            "headup_detection/video_aggregator_2"
                        ],
                        "REDIS_IP": "172.27.155.106",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_distributor_1"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_distributor_1",
                    "ports": {

                    },
                    "volumes": {
                        "/home/edge/": "/home/edge/"
                    }
                }
            },
            {
                "id": "2",
                "management_params":{
                    "service_name": "video_distributor_2",
                    "description": "video distributor 2"
                },
                "execution_params":{
                    "image": "video_distributor",
                    "env": {
                        "MQTT_BROKER_IP": "172.27.155.106",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_processor_stage_2",
                        "MQTT_OUTGOING_TOPIC": [
                            "headup_detection/video_aggregator_1",
                            "headup_detection/video_aggregator_2"
                        ],
                        "REDIS_IP": "172.27.155.106",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_distributor_2"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_distributor_2",
                    "ports": {

                    },
                    "volumes": {
                        "/home/edge/": "/home/edge/"
                    }
                }
            }
        ],
        "aggregators": [
            {
                "id": "1",
                "management_params":{
                    "service_name": "video_aggregator_1",
                    "description": "video aggregator 1"
                },
                "execution_params":{
                    "image": "video_aggregator",
                    "env": {
                        "MQTT_BROKER_IP": "172.27.155.106",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_INCOMING_TOPIC": "headup_detection/video_distributor_1",
                        "REDIS_IP": "172.27.155.106",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_aggregator_1",
                        "FLASK_PORT": "9753"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_aggregator_1",
                    "ports": {
                        "9753" : "9753"
                    },
                    "volumes": {
                        "/home/edge/": "/home/edge/"
                    }
                }
            },
            {
                "id": "2",
                "management_params":{
                    "service_name": "video_aggregator_2",
                    "description": "video aggregator 2"
                },
                "execution_params":{
                    "image": "video_aggregator",
                    "env": {
                        "MQTT_BROKER_IP": "172.27.155.106",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_INCOMING_TOPIC": "headup_detection/video_distributor_2",
                        "REDIS_IP": "172.27.155.106",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_aggregator_2",
                        "FLASK_PORT": "9754"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_aggregator_2",
                    "ports": {
                        "9754" : "9754"
                    },
                    "volumes": {
                        "/home/edge/": "/home/edge/"
                    }
                }
            }
        ]
    }
}
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
    config_file = "/Users/wenyidai/GitHub/multi-task-ce-framework/containerd_app_configs/test_config.json"
    generators = parse_json_for_generators(config_file)
    start_generators(generators)
    processors = parse_json_for_processors(config_file)
    start_processors_of_stage(processors, '1')
    start_processors_of_stage(processors, '2')
    distributors = parse_json_for_distributors(config_file)
    start_distributors(distributors)
    aggregators = parse_json_for_aggregators(config_file)
    start_aggregators(aggregators)
