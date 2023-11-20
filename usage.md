### Starting a demo pipeline with independent python scripts

`python3 video_example_with_mqtt/video_generator.py --id=1 --data_source=/Users/wenyidai/Downloads/demo.mp4`
`python3 video_example_with_mqtt/video_generator.py --id=2`

`python3 video_example_with_mqtt/video_processor_stage_1.py --id=1`
`python3 video_example_with_mqtt/video_processor_stage_1.py --id=2`
`python3 video_example_with_mqtt/video_processor_stage_1.py --id=3`
`python3 video_example_with_mqtt/video_processor_stage_1.py --id=4`

`python3 video_example_with_mqtt/video_processor_stage_2.py --id=1`
`python3 video_example_with_mqtt/video_processor_stage_2.py --id=2`
`python3 video_example_with_mqtt/video_processor_stage_2.py --id=3`

`python3 video_example_with_mqtt/video_distributor.py --id=1`

`python3 video_example_with_mqtt/video_aggregator.py --id=1`
`python3 video_example_with_mqtt/video_aggregator.py --id=2`

### TODO:Starting a demo pipeline with one python script (unfinished)

`python3 main.py`

