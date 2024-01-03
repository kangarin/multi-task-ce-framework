# 如果镜像存在，删除镜像
docker rmi ixpe_gen
docker rmi ixpe_stg1
docker rmi ixpe_stg2
docker rmi ixpe_stg3

docker build -t ixpe_gen -f k8s_ixpe/dockerfile/Dockerfile.generator .
docker build -t ixpe_stg1 -f k8s_ixpe/dockerfile/Dockerfile.processor_stage_1 .
docker build -t ixpe_stg2 -f k8s_ixpe/dockerfile/Dockerfile.processor_stage_2 .
docker build -t ixpe_stg3 -f k8s_ixpe/dockerfile/Dockerfile.processor_stage_3 .