import requests
import shutil

# 发送 GET 请求
response = requests.get('http://localhost:5000', stream=True)

# 检查响应状态码
if response.status_code == 200:
    # 从响应头中获取文件名
    content_disposition = response.headers.get('content-disposition')
    file_name = content_disposition.split('filename=')[1]

    # 将响应的内容写入文件
    with open(file_name, 'wb') as f:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, f)
else:
    print(f'请求失败，状态码：{response.status_code}')