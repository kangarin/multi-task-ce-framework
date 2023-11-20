# 使用基础镜像（例如Python官方镜像）
FROM jjanzic/docker-python3-opencv:latest

# 设置工作目录
WORKDIR /app

# 安装所需的依赖项
# RUN pip install opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install paho-mqtt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 将本地文件夹复制到容器中
COPY examples /app/examples
COPY framework /app/framework

# 启动脚本
# CMD ["python3", "generator.py"]
CMD ["bash"]