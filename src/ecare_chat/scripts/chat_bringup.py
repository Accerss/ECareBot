#!/usr/bin/env python3

import rospy
from std_msgs.msg import Int32
from std_msgs.msg import String
import requests
import json

# 唤醒标志，默认为False
is_awake = True
url = "http://192.168.3.6:5000/api/send"
# 倒计时函数，倒计时结束后重置唤醒标志
def countdown():
    global is_awake
    rospy.sleep(20)  # 倒计时10秒
    is_awake = True


# 订阅到语音转换为文字的结果后的回调函数
def asr_result_callback(data):
    print("[ASR Result]:", data.data)
    # 在这里调用NLU模块进行自然语言处理的逻辑处理
    msg = data.data
    payload = json.dumps({
        "msg": msg,
        "sendto": 2
    })
    headers = {
     'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    rospy.loginfo("[LLM Result]: %s", response.text)
    publish_tts_result(response.text)
    countdown()

# 发布语音合成的结果
def publish_tts_result(text):
    rospy.loginfo("[TTS Result]: %s", text)
    tts_pub.publish(text)


if __name__ == '__main__':
    rospy.init_node('voice_dialogue_node', anonymous=True)

    # 创建订阅者和发布者
    asr_pub = rospy.Publisher('/voice_system/asr_topic', Int32, queue_size=10)
    asr_result_sub = rospy.Subscriber('/voice_system/asr_result_topic', String, asr_result_callback)
    tts_pub = rospy.Publisher('/voice_system/tts_topic', String, queue_size=10)
    rospy.sleep(1)  # 等待节点初始化完成
    # 循环等待唤醒信号
    while not rospy.is_shutdown():
        if is_awake:
            # 在这里调用麦克风模块获取连续语音输入
            msg = Int32()
            msg.data = 1
            asr_pub.publish(msg)
            # 将语音输入转换为文字
            # asr_result = "Hello"  # 假设这里获取到了语音转换为的文字结果
            # publish_tts_result(asr_result)  # 发布语音合成的结果
            is_awake = False  # 重置唤醒标志
            

        rospy.sleep(0.1)
