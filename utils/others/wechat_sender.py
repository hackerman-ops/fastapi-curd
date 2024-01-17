# This file is used to send wechat message to users.

import requests


def send_wechat_message(message, access_token, user_id):
    url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
    data = {
        "touser": user_id,
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    response = requests.post(url, json=data)
    return response.json()