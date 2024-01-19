import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt

# 生成一些示例数据，每个样本有两个特征
data = np.random.rand(1000, 2).astype(np.float32)

# # 生成一些示例数据，均值为0.2，标准差为0.1的正态分布，
# data = np.random.normal(0.5, 0.5, (10000, 2)).astype(np.float32)

# 生成一些示例数据，均值为0.8，标准差为0.3的正态分布，
# data = np.random.normal(0.8, 0.3, (1000, 2)).astype(np.float32)

# # 生成一些示例数据
# data = np.concatenate((np.random.normal(3, 0.3, (500, 2)).astype(np.float32), 
#                        np.random.normal(2, 0.1, (500, 2)).astype(np.float32), 
#                        np.random.normal(0.5, 0.4, (500, 2)).astype(np.float32)))

# 生成一些示例数据
data1 = np.concatenate((np.random.normal(0.5, 0.1, (500, 1)).astype(np.float32),
                       np.random.normal(1.2, 0.5, (500, 1)).astype(np.float32)), axis=1)
data2 = np.concatenate((np.random.normal(0.9, 0.1, (500, 1)).astype(np.float32),
                          np.random.normal(0.3, 0.2, (500, 1)).astype(np.float32)), axis=1)
data3 = np.concatenate((np.random.normal(0.1, 0.1, (500, 1)).astype(np.float32),
                            np.random.normal(0.8, 0.2, (500, 1)).astype(np.float32)), axis=1)
data = np.concatenate((data1, data2, data3))

# # 生成一些示例数据，均值为20，标准差为10的正态分布，
# data = np.random.normal(20, 10, (1000, 2)).astype(np.float32)

# # 生成一些示例数据，alpha=0.5，beta=0.5的贝塔分布
# data = np.random.beta(0.5, 0.5, (10000, 2)).astype(np.float32)

# # 生成一些示例数据，卡方分布
# data = np.random.chisquare(0.5, (2000, 2)).astype(np.float32)

# 生成一些示例数据，拉普拉斯分布
# data = np.random.laplace(0.5, 0.5, (3000, 2)).astype(np.float32)

# 生成一些示例数据，指数分布
# data = np.random.exponential(0.5, (10000, 2)).astype(np.float32)

# 转换为 PyTorch 张量
data_tensor = torch.from_numpy(data)


# 定义神经网络模型
class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(2, 32)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(32, 16)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(16, 1)  # 输出一个标量，表示优先级分布的差异

    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x

# 创建模型、损失函数和优化器
model = NeuralNetwork()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 定义目标分布的统计量
target_mean = 8.0
target_std = 4.0

# 训练模型
num_epochs = 1200
for epoch in range(num_epochs):
    # Forward pass
    outputs = model(data_tensor)

    # 计算均值和标准差
    model_mean = torch.mean(outputs)
    model_std = torch.std(outputs)

    # 映射需要维护偏序关系，计算逆序对个数，由于不能改变data_tensor所以不能用排序，故采样，每隔n个取一个
    skipping = 100
    inverse_pairs = 0
    for i in range(0, len(data_tensor), skipping):
        for j in range(0, len(data_tensor), skipping):
            if(outputs[i] > outputs[j] and 
               (data_tensor[i][0] < data_tensor[j][0] and 
                data_tensor[i][1] < data_tensor[j][1])):
                inverse_pairs += 1
            if(outputs[i] < outputs[j] and 
               (data_tensor[i][0] > data_tensor[j][0] and 
                data_tensor[i][1] > data_tensor[j][1])):
                inverse_pairs += 1

    # 计算损失函数，输出分布与正态分布的差异 + 违背偏序关系的逆序对个数
    loss = (model_mean - target_mean)**2 + (model_std - target_std)**2 + inverse_pairs * 0.1

    # Backward pass and optimization
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # 打印训练过程中的损失
    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

# test_case = [
#     [1.0, 1.0],
#     [0.8, 0.8],
#     [0.5, 0.5],
#     [0.3, 0.3],
#     [0.1, 0.1],
#     [0.05, 0.05],
#     [0, 0],
#     [0.2, 0.2],
#     [0.2, 0.3],
#     [0.2, 0.1],
#     [0.3, 0.2],
#     [0.3, 0.1]
# ]


# 使用训练好的模型进行预测
with torch.no_grad():
    model.eval()
    predictions = model(torch.tensor(data_tensor))
    # clamp to [0,16] int
    predictions = torch.clamp(predictions, 0, 16)
    predictions = torch.round(predictions)
    # print(predictions)
    # draw graphs and save to file

    # draw 2d point scattering graph
    plt.scatter(data[:,0], data[:,1], c=predictions.numpy())
    # 指定横轴
    plt.xlabel('urgency')
    # 指定纵轴
    plt.ylabel('importance')
    # 指定标题
    plt.title('task distribution')
    plt.savefig("data.png")

    plt.clf()
    plt.hist(predictions.numpy(), bins=17, range=(0,16))
    plt.xlabel('priority')
    plt.ylabel('number of tasks')
    plt.title('priority distribution')
    plt.savefig("predictions.png")





# 输出训练后的模型在目标统计量上的偏差
print(f"Model Mean: {model_mean.item()}, Model Std: {model_std.item()}")
