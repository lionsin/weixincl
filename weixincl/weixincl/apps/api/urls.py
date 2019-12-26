from django.conf.urls import url

from api import views
# 提供接口给爬虫
urlpatterns = [
    # Articles/search?
    url(r"^param/pass$", views.PassParamsAPIView.as_view()),
    url(r"^pc/addlist$", views.SavePcCreateView.as_view()),
]