from django.test import TestCase

# Create your tests here

import requests
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}
data = requests.get("https://weixin.sogou.com/weixin?type=1&s_"
                    "from=input&query=广州&ie=utf8&_sug_=n&_sug_type_=",headers=headers)
print(data.content.decode())