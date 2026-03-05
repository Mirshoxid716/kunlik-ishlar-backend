from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'jobs', views.JobViewSet)
router.register(r'workers', views.WorkerViewSet)
router.register(r'applications', views.ApplicationViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
