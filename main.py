if __name__ == '__main__':
    from examples.video_generator import VideoGenerator
    from examples.video_processor_stage_1 import VideoProcessor1
    from examples.video_processor_stage_2 import VideoProcessor2
    from examples.video_distributor import VideoDistributor
    from examples.video_aggregator import VideoAggregator

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

# # use multiprocessing to run generators in parallel
# generator_processes = []
# for generator in generators:
#     generator_process = multiprocessing.Process(target=generator.run)
#     generator_processes.append(generator_process)
#     generator_process.start()

# input("Press Enter to continue...")
# for generator_process in generator_processes:
#     generator_process.join()
