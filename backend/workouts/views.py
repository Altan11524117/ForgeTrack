from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Device, Exercise, Routine, WorkoutSession, WorkoutSet
from .serializers import (
    DeviceSerializer, ExerciseSerializer, RoutineSerializer,
    WorkoutSessionSerializer, WorkoutSetSerializer
)


def get_device_id(request):
    """
    Extract device_id from any of the three possible locations:
      1. Query parameter:  ?device_id=...
      2. Header:           Device-Id: ... (case-insensitive via Django)
      3. Request body:     {"device_id": "..."}  (POST/PUT/PATCH only)
    """
    # Check query params first
    device_id = request.query_params.get('device_id')
    if device_id:
        return device_id

    # Check headers (Django normalises header names to HTTP_*)
    device_id = request.headers.get('Device-Id') or request.headers.get('device-id')
    if device_id:
        return device_id

    # Check request body (available for POST/PUT/PATCH)
    if hasattr(request, 'data') and isinstance(request.data, dict):
        device_id = request.data.get('device_id')
        if device_id:
            return device_id

    return None


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    @action(detail=False, methods=['post'], url_path='init')
    def initialize_device(self, request):
        device_id = get_device_id(request)
        if device_id:
            device, created = Device.objects.get_or_create(id=device_id)
            serializer = self.get_serializer(device)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Device ID required"}, status=status.HTTP_400_BAD_REQUEST)


class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer


class RoutineViewSet(viewsets.ModelViewSet):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer

    def get_queryset(self):
        device_id = get_device_id(self.request)
        if device_id:
            return Routine.objects.filter(device_id=device_id).order_by('-created_at')
        return Routine.objects.none()

    def perform_create(self, serializer):
        device_id = get_device_id(self.request)
        if device_id:
            device, _ = Device.objects.get_or_create(id=device_id)
            serializer.save(device=device)
        else:
            raise ValidationError({"device_id": "This field is required."})


class WorkoutSessionViewSet(viewsets.ModelViewSet):
    queryset = WorkoutSession.objects.all()
    serializer_class = WorkoutSessionSerializer

    def get_queryset(self):
        device_id = get_device_id(self.request)
        if device_id:
            return WorkoutSession.objects.filter(device_id=device_id).order_by('-start_time')
        return WorkoutSession.objects.none()

    def perform_create(self, serializer):
        device_id = get_device_id(self.request)
        if device_id:
            device, _ = Device.objects.get_or_create(id=device_id)
            serializer.save(device=device)
        else:
            raise ValidationError({"device_id": "This field is required."})


class WorkoutSetViewSet(viewsets.ModelViewSet):
    queryset = WorkoutSet.objects.all()
    serializer_class = WorkoutSetSerializer