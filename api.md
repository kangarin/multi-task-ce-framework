## 单个应用配置文件结构

当用户提交一个high-level的应用时，应用管理平台会根据用户提交的参数（若有些字段用户未指定，则使用缺省参数，如MQTT、Redis地址等，可设定有些字段为必须，如topic等），以默认冷启动的方式自动生成一个应用配置文件，该文件包含了应用的所有信息，包括应用名、服务名、实例序号、节点ip、容器名、镜像名、环境变量、端口映射、挂载目录、网络等。后续调度器会根据系统运行状况动态修改这个配置文件，以供各个微服务定期拉取并更新自己的执行参数。该文件的格式为json，包括了:
1. 管理节点视角下管理应用各部分微服务的必需参数
2. 执行节点视角下启动一个容器的必需参数
3. 应用相关情境参数（通过执行参数中的REDIS_KEY指定应用相关情境参数的存取位置，以供微服务与调度器交互，该REDIS_KEY对应一个应用相关的KV列表，如对于视频流应用的帧率分辨率等，也包括了微服务优先级等通用参数）

配置文件如下所示：

```json
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
                        "DATA_SOURCE": "rtsp://localhost/test",
                        "MQTT_BROKER_IP": "localhost",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_TOPIC": "headup_detection/video_generator",
                        "REDIS_IP": "localhost",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_generator_1"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_generator_1",
                    "ports": {
                        "1883": "1883"
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
                        "DATA_SOURCE": "rtsp://localhost/test",
                        "MQTT_BROKER_IP": "localhost",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_TOPIC": "headup_detection/video_generator",
                        "REDIS_IP": "localhost",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_generator_2"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_generator_2",
                    "ports": {
                        "1883": "1883"
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
                                "MQTT_BROKER_IP": "localhost",
                                "MQTT_BROKER_PORT": "1883",
                                "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_generator",
                                "MQTT_OUTGOING_TOPIC": "headup_detection/video_processor_stage_1",
                                "REDIS_IP": "localhost",
                                "REDIS_PORT": "6379",
                                "REDIS_DB": "0",
                                "REDIS_KEY": "headup_detection/video_processor_stage_1_instance_1"
                            },
                            "network": "headup_detection",
                            "container_name": "headup_detection_video_processor_stage_1_instance_1",
                            "ports": {
                                "1883": "1883"
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
                                "MQTT_BROKER_IP": "localhost",
                                "MQTT_BROKER_PORT": "1883",
                                "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_generator",
                                "MQTT_OUTGOING_TOPIC": "headup_detection/video_processor_stage_1",
                                "REDIS_IP": "localhost",
                                "REDIS_PORT": "6379",
                                "REDIS_DB": "0",
                                "REDIS_KEY": "headup_detection/video_processor_stage_1_instance_2"
                            },
                            "network": "headup_detection",
                            "container_name": "headup_detection_video_processor_stage_1_instance_2",
                            "ports": {
                                "1883": "1883"
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
                                "MQTT_BROKER_IP": "localhost",
                                "MQTT_BROKER_PORT": "1883",
                                "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_processor_stage_1",
                                "MQTT_OUTGOING_TOPIC": "headup_detection/video_processor_stage_2",
                                "REDIS_IP": "localhost",
                                "REDIS_PORT": "6379",
                                "REDIS_DB": "0",
                                "REDIS_KEY": "headup_detection/video_processor_stage_2_instance_1"
                            },
                            "network": "headup_detection",
                            "container_name": "headup_detection_video_processor_stage_2_instance_1",
                            "ports": {
                                "1883": "1883"
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
                                "MQTT_BROKER_IP": "localhost",
                                "MQTT_BROKER_PORT": "1883",
                                "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_processor_stage_1",
                                "MQTT_OUTGOING_TOPIC": "headup_detection/video_processor_stage_2",
                                "REDIS_IP": "localhost",
                                "REDIS_PORT": "6379",
                                "REDIS_DB": "0",
                                "REDIS_KEY": "headup_detection/video_processor_stage_2_instance_2"
                            },
                            "network": "headup_detection",
                            "container_name": "headup_detection_video_processor_stage_2_instance_2",
                            "ports": {
                                "1883": "1883"
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
                        "MQTT_BROKER_IP": "localhost",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_processor_stage_2",
                        "MQTT_OUTGOING_TOPIC": [
                            "headup_detection/video_aggregator_1",
                            "headup_detection/video_aggregator_2"
                        ],
                        "REDIS_IP": "localhost",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_distributor_1"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_distributor_1",
                    "ports": {
                        "1883": "1883"
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
                        "MQTT_BROKER_IP": "localhost",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_INCOMING_TOPIC": "$share/python/headup_detection/video_processor_stage_2",
                        "MQTT_OUTGOING_TOPIC": [
                            "headup_detection/video_aggregator_1",
                            "headup_detection/video_aggregator_2"
                        ],
                        "REDIS_IP": "localhost",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_distributor_2"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_distributor_2",
                    "ports": {
                        "1883": "1883"
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
                        "MQTT_BROKER_IP": "localhost",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_INCOMING_TOPIC": "headup_detection/video_distributor_1",
                        "REDIS_IP": "localhost",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_aggregator_1"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_aggregator_1",
                    "ports": {
                        "1883": "1883"
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
                        "MQTT_BROKER_IP": "localhost",
                        "MQTT_BROKER_PORT": "1883",
                        "MQTT_INCOMING_TOPIC": "headup_detection/video_distributor_2",
                        "REDIS_IP": "localhost",
                        "REDIS_PORT": "6379",
                        "REDIS_DB": "0",
                        "REDIS_KEY": "headup_detection/video_aggregator_2"
                    },
                    "network": "headup_detection",
                    "container_name": "headup_detection_video_aggregator_2",
                    "ports": {
                        "1883": "1883"
                    },
                    "volumes": {
                        "/home/edge/": "/home/edge/"
                    }
                }
            }
        ]
    }
}
```