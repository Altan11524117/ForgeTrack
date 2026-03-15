from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, ExerciseViewSet, RoutineViewSet, WorkoutSessionViewSet, WorkoutSetViewSet

# Django'nun otomatik adres yönlendiricisi (Postane)
router = DefaultRouter()

# Mahalledeki mevcut sokaklarımız
router.register(r'devices', DeviceViewSet)
router.register(r'exercises', ExerciseViewSet)
router.register(r'routines', RoutineViewSet)

# İŞTE EKSİK OLAN YENİ SOKAĞIMIZ BURASI!
router.register(r'workout-sessions', WorkoutSessionViewSet)
router.register(r'workout-sets', WorkoutSetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]