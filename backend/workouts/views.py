from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Device, Exercise, Routine, WorkoutSession, WorkoutSet
from .serializers import (
    DeviceSerializer, ExerciseSerializer, RoutineSerializer, 
    WorkoutSessionSerializer, WorkoutSetSerializer
)

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    # Flutter uygulamasının açılışta cihazı kaydetmesini sağlayan fonksiyon
    @action(detail=False, methods=['post'], url_path='init')
    def initialize_device(self, request):
        device_id = request.data.get('device_id') or request.query_params.get('device_id')
        if device_id:
            device, created = Device.objects.get_or_create(id=device_id)
            serializer = self.get_serializer(device)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Device ID required"}, status=status.HTTP_400_BAD_REQUEST)

class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

class RoutineViewSet(viewsets.ModelViewSet):
    queryset = Routine.objects.all() # ROUTER'IN ÇÖKMESİNİ ENGELLEYEN SABİT
    serializer_class = RoutineSerializer

    def get_queryset(self):
        device_id = self.request.query_params.get('device_id') or self.request.headers.get('Device-Id')
        if device_id:
            return Routine.objects.filter(device_id=device_id).order_by('-created_at')
        return Routine.objects.none()

class WorkoutSessionViewSet(viewsets.ModelViewSet):
    queryset = WorkoutSession.objects.all() # ROUTER'IN ÇÖKMESİNİ ENGELLEYEN SABİT
    serializer_class = WorkoutSessionSerializer

    def get_queryset(self):
        device_id = self.request.query_params.get('device_id') or self.request.headers.get('Device-Id')
        if device_id:
            return WorkoutSession.objects.filter(device_id=device_id).order_by('-start_time')
        return WorkoutSession.objects.none()

class WorkoutSetViewSet(viewsets.ModelViewSet):
    queryset = WorkoutSet.objects.all()
    serializer_class = WorkoutSetSerializer