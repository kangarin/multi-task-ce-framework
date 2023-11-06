# multi-task-ce-framework

## Introduction
This is a multimodal multitask cloud-edge collaborative framework on the application layer for stateless stream analysis. 


There are four kinds of services: 

1. **Generator**. This is a service that is bound to a dataflow source, and generate starting tasks.

2. **Processor**. This is a service that is stateless, and process the tasks. There can be multiple processors forming a pipeline, and there can be multiple instances of the same processor for load balancing.

3. **Distributor**. This is a service that send the tasks to the proper aggregator. Only one distributor is needed for each application.

4. **Aggregator**. This is a service that aggregate the results from processors. One aggregator is bound to one generator to aggragate the results from the same dataflow source.

## Usage
### MQTT topics
The generator publisher's topic should be in the format of `application_name/generator`.

The corresbonding processor subscriber's incoming topic should be in the format of `$share/python/application_name/generator` for load balancing of several instances of the same processor.

The corresbonding processor subscriber's outgoing topic should be in the format of `application_name/processor_stage`.

If multiple processors(forming a pipeline) are used, the outgoing topic of the first processor should be in the format of `application_name/processor_stage_1`, and the outgoing topic of the second processor should be in the format of `application_name/processor_stage_2`, and so on.

The distributor subscriber's topic should be in the format of `application_name/processor_stage_of_the_last_processor`.

The distributor publisher's topics should be in the format of `[application_name/aggregator_dataflow_name]`.

The aggregator subscriber's topic should be in the format of `application_name/aggregator_dataflow_name`.

### Services
The 'id' should be unique for each service instance. Naming convention should
follow the rules:
1. The generator should be named as `generator_dataflow_name_id`. For example, `generator_traffic_mainstreet_1`.
2. The processor should be named as `processor_stage_id_instance_id`. For example, `processor_stage_1_instance_1`.