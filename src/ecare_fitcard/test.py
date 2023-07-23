import pygatt
import time
import requests
import os
# 蓝牙设备名称
DEVICE_NAME_PREFIX = "WL ECG"

# 特征值的UUID
CHARACTERISTIC_UUID = "974CBE31-3E83-465E-ACDE-6F92FE712134"

# 创建一个BLE设备管理器
adapter = pygatt.GATTToolBackend()

file_path = "received_data.txt"
# 检查文件是否存在
if os.path.exists(file_path):
    # 删除文件
    os.remove(file_path)

blu_data = []

try:
    # 启动BLE设备管理器
    adapter.start()

    # 开始搜索设备
    devices = adapter.scan()
    print(devices)
    for device in devices:
        if device["name"] is not None and device["name"].startswith(DEVICE_NAME_PREFIX):
            # 连接设备
            device_mac = device["address"]
            print("正在连接，蓝牙地址"+device_mac)
            device = adapter.connect(device_mac, address_type=pygatt.BLEAddressType.random, timeout=10)
            print("设备已连接！")

            def handle_data(sender, data):
                # 处理接收到的数据
                # print("Received data: ", data.hex())
                blu_data.append(data.hex())
                
            device.subscribe(CHARACTERISTIC_UUID, callback=handle_data)
            break
    
    # 持续监听数据，直到按下Ctrl+C停止程序
    start_time = time.time()
    while True:
        # 检查是否已经达到5秒
        if time.time() - start_time >= 60:
            break  # 跳出循环体
        print(time.time() - start_time)
        pass

finally:
    # 断开连接并停止BLE设备管理器
    adapter.stop()
    # 保存数据到本地文件
    with open(file_path, 'a') as f:
        for data in blu_data:
            for i in range(0, len(data), 2):
                byte = data[i:i+2]
                f.write(byte + '\n')

    print('数据保存成功')

# 获取token
url = "https://api.waveletech.com/v1/gettoken?key=20005&secret=2d70g9e799660df661ef16e2827c0bh9"
payload={}
headers = {
  'Cookie': 'connect.sid=s%3ADwKQK5tJHtM_18FaDs6dB9U1TYrdc4JK.kQpK%2FXx1zzaP8DOQihltfp49mDEC1Pa%2BtSoJr2pktxw'
}
response = requests.request("GET", url, headers=headers, data=payload)
# 判断是否获取成功
if response.status_code >= 200 and response.status_code <= 299:
    print("token request Successful！")
    response_json = response.json()
    token = response_json['data']['accessToken']
else:
    print("token request fail!")



# 上传文件
url = "https://api.waveletech.com/v1/files"
payload={}
files=[
  ('',('received_data.txt',open('received_data.txt','rb'),'text/plain'))
]
headers = {
  'Authorization': 'Bearer ' + token,
  'Cookie': 'connect.sid=s%3ADwKQK5tJHtM_18FaDs6dB9U1TYrdc4JK.kQpK%2FXx1zzaP8DOQihltfp49mDEC1Pa%2BtSoJr2pktxw'
}
response = requests.request("POST", url, headers=headers, data=payload, files=files)
# 判断文件上传是否成功
if response.status_code >= 200 and response.status_code <= 299:
    print("File upload successful.")
    response_json = response.json()
    file_id = response_json['data']['files'][0]['_id']
else:
    print("File upload fail!")



# 数据计算

url = "https://api.waveletech.com/v1/compute"

payload='fileId=' + file_id + '&type=1'
headers = {
  'Authorization': 'Bearer ' + token,
  'Content-Type': 'application/x-www-form-urlencoded',
  'Cookie': 'connect.sid=s%3ADwKQK5tJHtM_18FaDs6dB9U1TYrdc4JK.kQpK%2FXx1zzaP8DOQihltfp49mDEC1Pa%2BtSoJr2pktxw'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)



