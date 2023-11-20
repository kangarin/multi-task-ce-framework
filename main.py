# general:
#   mqtt_host: "localhost"
#   mqtt_port: 1883
#   mqtt_username: "mqtt_user"
#   mqtt_password: "mqtt_password"
#   mqtt_application_name: "car_detection_app"

# services:
#   generators:
#     id_prefix: "generator"
#     outgoing_topic: "testapp/generator"
#     instances:
#     - id: "1"
#       data_source: 0
#       priority: 1
#       tuned_parameters:
#         resolution: 800
#         fps: 10
#         encoding: "h264"
#         frames_per_task: 10
#         skipping_frame_interval: 10

#     - id: "2"
#       data_source: 0
#       priority: 2
#       tuned_parameters:
#         resolution: 800
#         fps: 10
#         encoding: "h264"
#         frames_per_task: 5
#         skipping_frame_interval: 20

#   processors:
#     - order: 1
#       id_prefix: "processor_stage_1"
#       incoming_topic: "$share/python/testapp/generator"
#       outgoing_topic: "testapp/processor_stage_1"
#       instances:
#         - id: "1"
#           priority: 1
#           tuned_parameters:
#             model: "yolov3"
#             confidence: 0.5
#             threshold: 0.3
#         - id: "2"
#           priority: 2
#           tuned_parameters:
#             model: "yolov3"
#             confidence: 0.5
#             threshold: 0.3

#     - order: 2
#       id_prefix: "processor_stage_2"
#       incoming_topic: "$share/python/testapp/processor_stage_1"
#       outgoing_topic: "testapp/processor_stage_2"
#       instances:
#         - id: "1"
#           priority: 1
#           tuned_parameters:
#             param1: "test"
#             param2: 0.5
#         - id: "2"
#           priority: 2
#           tuned_parameters:
#             param1: "test2"
#             param2: 0.8

#   distributors:
#     id_prefix: "distributor"
#     incoming_topic: "$share/python/testapp/processor_stage_2"
#     instances:
#       - id: "1"
#       - id: "2"

#   aggregators:
#     id_prefix: "aggregator"
#     instances:
#       - id: "1"
#         incoming_topic: "$share/python/testapp/aggregator_1"
#       - id: "2"
#         incoming_topic: "$share/python/testapp/aggregator_2"








if __name__ == '__main__':
    from video_example_with_mqtt.video_generator import VideoGenerator
    from video_example_with_mqtt.video_processor_stage_1 import VideoProcessor1
    from video_example_with_mqtt.video_processor_stage_2 import VideoProcessor2
    from video_example_with_mqtt.video_distributor import VideoDistributor
    from video_example_with_mqtt.video_aggregator import VideoAggregator

    import cv2
    # parse yaml file "app_config_template.yaml"
    import yaml
    import argparse
    parser = argparse.ArgumentParser(description='Video generator')
    parser.add_argument('--config', type=str, help='app config file')
    config_file = parser.parse_args().config
    config_file = "app_config_template.yaml"
    with open(config_file) as f:
        config = yaml.safe_load(f)

import multiprocessing

mqtt_host = config['general']['mqtt_host']
mqtt_port = config['general']['mqtt_port']
mqtt_username = config['general']['mqtt_username']
mqtt_password = config['general']['mqtt_password']
mqtt_application_name = config['general']['mqtt_application_name']

# create generators
generators = []
for generator_config in config['services']['generators']['instances']:
    generator_id = config['services']['generators']['id_prefix'] + '_' + generator_config['id']
    generator = VideoGenerator(generator_config['data_source'], generator_id,
                                config['services']['generators']['outgoing_topic'], generator_config['priority'], generator_config['tuned_parameters'])
    # generator.run()
    generators.append(generator)

# create processors
processors_1 = []
processors_2 = []
for processor_config in config['services']['processors']:
    order = processor_config['order']
    if order == 1:
        for instance in processor_config['instances']:
            processor_id = processor_config['id_prefix'] + '_' + instance['id']
            processor = VideoProcessor1(processor_id, processor_config['incoming_topic'], processor_config['outgoing_topic'], instance['priority'], instance['tuned_parameters'])
            # processor.run()
            processors_1.append(processor)

    elif order == 2:
        for instance in processor_config['instances']:
            processor_id = processor_config['id_prefix'] + '_' + instance['id']
            processor = VideoProcessor2(processor_id, processor_config['incoming_topic'], processor_config['outgoing_topic'], instance['priority'], instance['tuned_parameters'])
            # processor.run()
            processors_2.append(processor)

# create distributors
distributors = []
for distributor_config in config['services']['distributors']['instances']:
    distributor_id = config['services']['distributors']['id_prefix'] + '_' + distributor_config['id']
    distributor = VideoDistributor(distributor_id, config['services']['distributors']['incoming_topic'])
    # distributor.run()
    distributors.append(distributor)

# create aggregators
aggregators = []
for aggregator_config in config['services']['aggregators']['instances']:
    aggregator_id = config['services']['aggregators']['id_prefix'] + '_' + aggregator_config['id']
    aggregator = VideoAggregator(aggregator_id, aggregator_config['incoming_topic'])
    # aggregator.run()
    aggregators.append(aggregator)