from django.conf.urls import url

from weixin import views
urlpatterns = [
    # Articles/search?
    url(r"^pcnum/search$", views.PcSearchListView.as_view()),
    url(r"^collect_list$", views.AddCollectList.as_view()),
    url(r"^collect_list/clear$", views.ClearCollectList.as_view()),
    url(r"^collect_list/delete$", views.ClearCollectList.as_view()),

    url(r"^tasks/add$", views.TaskaddAPIView.as_view()),
    url(r"^tasks/list$", views.TasklistAPIView.as_view()),
    url(r"^tasks/detail$", views.TaskShowDetailAPIView.as_view()),
    url(r"^tasks/delete$", views.TaskdeleteAPIView.as_view()),
    # 查看任务文章列表
    url(r"^task_arts/list$", views.ArticleShowDetailAPIView.as_view()),
    url(r"^history/add$", views.PcSearchHistoryView.as_view()),
    url(r"^history$", views.PcSearchHistoryView.as_view()),
    # 清空采集列表页
    url(r"^history/clear$", views.HistoryClearAPIView.as_view()),

]
