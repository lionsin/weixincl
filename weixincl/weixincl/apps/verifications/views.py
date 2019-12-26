from django.shortcuts import render

# Create your views here.
import random
from celery_tasks.sms.tasks import *
import logging



from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from verifications import constants
# 生成日志对象
logger = logging.getLogger("django")


class SMSCodeView(APIView):
    # 请求后端发送短信
    """
    访问路径：/sms_codes/(?P<mobile>\d{11})/

    """

    def get(self, request, mobile):
        # 1/生成短信验证码拿到手机号
        # ２.保存短信验证码
        print(222)
        # 发送短信前判断６０秒内是否发送过短信
        redis = get_redis_connection("verify")
        # print(redis)
        flag = None

        try:
            flag = redis.get("sms_flag_%s" % mobile)
        except Exception as e:
            print(e)
        print(11)
        if flag:
            return Response({"message": "发送短信过于频繁"}, status=404)
        # 生成短信验证码

        sms_code = '%06s' % random.randint(0, 999999)
        # 短信验证码存货时间
        expire = constants.SMS_CODE_REDIS_EXPIRES
        # print(flag)
        # 使用celery生成的必须用ｄｅｌａｙ调用
        print(22)

        send_sms_code.delay(mobile, sms_code, expire)

        # 记录日志
        logger.debug("%s:%s" % (mobile, sms_code))
        # 保存验证码到ｒｅｄｉｓ中
        pl = redis.pipeline()
        pl.setex("sms_%s" % mobile, expire, sms_code)
        pl.setex("sms_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()  # 统一提交ｒｅｄｉｓ操作，提高性能
        return Response({"message": "ok"})