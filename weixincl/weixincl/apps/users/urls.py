from django.conf.urls import url


from users import views

urlpatterns = [


    url(r"^mobiles/(?P<mobile>1[3456789]\d{9})/count/$", views.MobileCountAPIView.as_view()),
    url(r"^users/$", views.UserAPIView.as_view()),





    # url(r"^browse_histories/$", views.UserBrowsingHistoryView.as_view())

]

