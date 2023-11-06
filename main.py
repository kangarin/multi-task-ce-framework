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

    # create generators
    generators = []
    id_prefix_g = config['services']['generators']['id_prefix']
    for generator_config in config['services']['generators']['instances']:
        generator = VideoGenerator(generator_config['data_source'],
                                    id_prefix_g + "_" + generator_config['id'],
                                    config['services']['generators']['outgoing_topic'],
                                    generator_config['priority'],
                                    generator_config['tuned_parameters'],
                                    # config['general']['mqtt_host'],
                                    # config['general']['mqtt_port'],
                                    # config['general']['mqtt_username'],
                                    # config['general']['mqtt_password']
                                    )
        generators.append(generator)
    
    # create processors
    processors_1 = []
    id_prefix_p1 = config['services']['processors'][0]['id_prefix']
    processors_2 = []
    id_prefix_p2 = config['services']['processors'][1]['id_prefix']
    for processor_config in config['services']['processors']:
        if processor_config['order'] == 1:
            for processor_instance_config in processor_config['instances']:
                processor = VideoProcessor1(id_prefix_p1 + "_" + processor_instance_config['id'],
                                            processor_config['incoming_topic'],
                                            processor_config['outgoing_topic'],
                                            processor_instance_config['priority'],
                                            processor_instance_config['tuned_parameters'],
                                            # config['general']['mqtt_host'],
                                            # config['general']['mqtt_port'],
                                            # config['general']['mqtt_username'],
                                            # config['general']['mqtt_password']
                                            )
                processors_1.append(processor)
        elif processor_config['order'] == 2:
            for processor_instance_config in processor_config['instances']:
                processor = VideoProcessor2(id_prefix_p2 + "_" + processor_instance_config['id'],
                                            processor_config['incoming_topic'],
                                            processor_config['outgoing_topic'],
                                            processor_instance_config['priority'],
                                            processor_instance_config['tuned_parameters'],
                                            # config['general']['mqtt_host'],
                                            # config['general']['mqtt_port'],
                                            # config['general']['mqtt_username'],
                                            # config['general']['mqtt_password']
                                            )
                processors_2.append(processor)
    
    # create distributors

    distributors = []
    id_prefix_d = config['services']['distributors']['id_prefix']
    for distributor_config in config['services']['distributors']['instances']:
        distributor = VideoDistributor(id_prefix_d + "_" + distributor_config['id'],
                                        config['services']['distributors']['incoming_topic'],
                                        # config['general']['mqtt_host'],
                                        # config['general']['mqtt_port'],
                                        # config['general']['mqtt_username'],
                                        # config['general']['mqtt_password']
                                        )
        distributors.append(distributor)
    
    # create aggregators
    aggregators = []
    id_prefix_a = config['services']['aggregators']['id_prefix']
    for aggregator_config in config['services']['aggregators']['instances']:
        aggregator = VideoAggregator(id_prefix_a + "_" + aggregator_config['id'],
                                        aggregator_config['incoming_topic'],
                                        # config['general']['mqtt_host'],
                                        # config['general']['mqtt_port'],
                                        # config['general']['mqtt_username'],
                                        # config['general']['mqtt_password']
                                        )
        aggregators.append(aggregator)

    # start all services with multiprocessing
    from multiprocessing import Process
    processes = []
    for generator in generators:
        processes.append(Process(target=generator.run))
    for processor in processors_1:
        processes.append(Process(target=processor.run))
    for processor in processors_2:
        processes.append(Process(target=processor.run))
    for distributor in distributors:
        processes.append(Process(target=distributor.run))
    for aggregator in aggregators:
        processes.append(Process(target=aggregator.run))
    for process in processes:
        process.start()
    for process in processes:
        process.join()

