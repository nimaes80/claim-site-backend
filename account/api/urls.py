from django.urls import path
from account.api import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()

urlpatterns = [
    path("login/admin/", views.AdminDecoratedTokenObtainPairView.as_view()),
    path("login/", views.DecoratedTokenObtainPairView.as_view()),
    path("refresh/", views.DecoratedTokenRefreshView.as_view()),
]

router.register("user", views.UserViewSet, "user")
router.register("system_setting", views.SystemSettingViewSet, "system_setting")
urlpatterns += router.urls
