from django.http import HttpResponse
from django.test import TestCase

# Create your tests here.
from django.views import View
from requests import Response
from rest_framework.views import APIView
# import json
#
# class test(View):
#     def get(self,request):
#         name = request.GET.get("name")
#         context = {
#             "name":name
#         }
#         context= json.dumps(context)
#         return HttpResponse(context)
#
#
# class Test(View):
#     def post(self, request):
#         image_url = request.POST.get("image_url")
#         weixin_num = request.POST.get("weixin_num")
#         name = request.POST.get("name")
#         _biz = request.POST.get("_biz")
#         introduction = request.POST.get("introduction")
#
#         context = {
#             "image_url":image_url,
#             "weixin_num":weixin_num,
#             "name": name,
#             "_biz":_biz,
#             "introduction":introduction
#
#         }
#         context=json.dumps(context)
#         return HttpResponse(context)


