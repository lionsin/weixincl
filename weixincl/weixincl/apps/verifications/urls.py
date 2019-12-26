from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'sms_codes/(?P<mobile>1[345678]\d{9})/$', views.SMSCodeView.as_view()),
]
