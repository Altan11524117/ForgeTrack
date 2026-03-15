from rest_framework import serializers
from .models import Device, Exercise, Routine, RoutineItem, WorkoutSession, WorkoutSet

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'created_at']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'muscle_group', 'is_compound']

class RoutineItemSerializer(serializers.ModelSerializer):
    exercise_details = ExerciseSerializer(source='exercise', read_only=True)
    
    class Meta:
        model = RoutineItem
        fields = ['id', 'exercise', 'exercise_details', 'day_name', 'order', 'target_sets', 'target_reps']

class RoutineSerializer(serializers.ModelSerializer):
    days = serializers.JSONField(write_only=True)
    items = RoutineItemSerializer(many=True, read_only=True)
    device = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Routine
        fields = ['id', 'device', 'name', 'days', 'items', 'created_at']

    def create(self, validated_data):
        days_data = validated_data.pop('days', [])
        request = self.context.get('request')
        
        device_id = None
        if request:
            device_id = (
                request.query_params.get('device_id') or
                request.headers.get('Device-Id') or
                request.headers.get('device-id') or
                request.data.get('device_id')
            )

        if device_id:
            device, _ = Device.objects.get_or_create(id=device_id)
        else:
            device, _ = Device.objects.get_or_create(id='00000000-0000-0000-0000-000000000000')

        routine = Routine.objects.create(device=device, **validated_data)

        order_counter = 0
        for day in days_data:
            day_name = day.get('day_name')
            for ex in day.get('exercises', []):
                RoutineItem.objects.create(
                    routine=routine,
                    day_name=day_name,
                    exercise_id=ex.get('exercise_id'),
                    target_sets=ex.get('sets'),
                    target_reps=ex.get('reps'),
                    order=order_counter
                )
                order_counter += 1

        return routine

class WorkoutSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSet
        fields = ['id', 'exercise', 'weight', 'reps', 'rpe', 'created_at']

# İŞTE BİZİM YENİ AKILLI KAYIT SİSTEMİMİZ
class WorkoutSessionSerializer(serializers.ModelSerializer):
    sets_data = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    sets = WorkoutSetSerializer(many=True, read_only=True)
    device = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WorkoutSession
        fields = ['id', 'device', 'routine', 'start_time', 'end_time', 'notes', 'is_active', 'sets', 'sets_data']

    def create(self, validated_data):
        sets_data = validated_data.pop('sets_data', [])
        request = self.context.get('request')
        
        device_id = None
        if request:
            device_id = (
                request.query_params.get('device_id') or
                request.headers.get('Device-Id') or
                request.headers.get('device-id') or
                request.data.get('device_id')
            )

        if device_id:
            device, _ = Device.objects.get_or_create(id=device_id)
        else:
            device, _ = Device.objects.get_or_create(id='00000000-0000-0000-0000-000000000000')

        session = WorkoutSession.objects.create(device=device, **validated_data)

        for set_item in sets_data:
            WorkoutSet.objects.create(
                session=session, 
                exercise_id=set_item.get('exercise'),
                weight=set_item.get('weight', 0),
                reps=set_item.get('reps', 0),
                rpe=set_item.get('rpe', 8)
            )

        return session