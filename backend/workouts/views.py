from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Device, Exercise, Routine, WorkoutSession, WorkoutSet
from .serializers import (
    DeviceSerializer, ExerciseSerializer, RoutineSerializer,
    WorkoutSessionSerializer, WorkoutSetSerializer,
)


def get_device_id(request):
    """
    Extract device_id from any of three possible locations (in priority order):
      1. Query parameter : ?device_id=<uuid>
      2. Request header  : Device-Id: <uuid>
      3. Request body    : {"device_id": "<uuid>"}  (POST / PUT / PATCH)
    Returns the UUID string, or None if not found anywhere.
    """
    # 1. Query param — always sent by the Dio interceptor
    value = request.query_params.get('device_id')
    if value:
        return value

    # 2. Header (Django normalises header names; both casings covered)
    value = (
        request.headers.get('Device-Id') or
        request.headers.get('device-id')
    )
    if value:
        return value

    # 3. JSON body (POST / PUT / PATCH only)
    if hasattr(request, 'data') and isinstance(request.data, dict):
        value = request.data.get('device_id')
        if value:
            return value

    return None


def _get_or_create_device(device_id):
    """Return a Device instance, creating it if needed."""
    device, _ = Device.objects.get_or_create(id=device_id)
    return device


# ---------------------------------------------------------------------------
# Apply @csrf_exempt at the class level so every action is exempt.
# These are device-keyed public endpoints — no user session / cookie auth.
# ---------------------------------------------------------------------------
@method_decorator(csrf_exempt, name='dispatch')
class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    authentication_classes = []
    permission_classes = []

    @action(detail=False, methods=['post'], url_path='init')
    def initialize_device(self, request):
        device_id = get_device_id(request)
        if not device_id:
            return Response(
                {'error': 'device_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        device = _get_or_create_device(device_id)
        return Response(DeviceSerializer(device).data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    authentication_classes = []
    permission_classes = []


@method_decorator(csrf_exempt, name='dispatch')
class RoutineViewSet(viewsets.ModelViewSet):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        device_id = get_device_id(self.request)
        if device_id:
            return Routine.objects.filter(device_id=device_id).order_by('-created_at')
        return Routine.objects.none()

    def perform_create(self, serializer):
        device_id = get_device_id(self.request)
        if not device_id:
            raise ValidationError({'device_id': 'This field is required.'})
        device = _get_or_create_device(device_id)
        serializer.save(device=device)


@method_decorator(csrf_exempt, name='dispatch')
class WorkoutSessionViewSet(viewsets.ModelViewSet):
    queryset = WorkoutSession.objects.all()
    serializer_class = WorkoutSessionSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        device_id = get_device_id(self.request)
        if device_id:
            return WorkoutSession.objects.filter(
                device_id=device_id,
            ).order_by('-start_time')
        return WorkoutSession.objects.none()

    def perform_create(self, serializer):
        device_id = get_device_id(self.request)
        if not device_id:
            raise ValidationError({'device_id': 'This field is required.'})
        device = _get_or_create_device(device_id)
        serializer.save(device=device)


@method_decorator(csrf_exempt, name='dispatch')
class WorkoutSetViewSet(viewsets.ModelViewSet):
    queryset = WorkoutSet.objects.all()
    serializer_class = WorkoutSetSerializer
    authentication_classes = []
    permission_classes = []