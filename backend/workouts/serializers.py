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
        fields = ['id', 'exercise', 'exercise_details', 'day_name', 'order',
                  'target_sets', 'target_reps']


class RoutineSerializer(serializers.ModelSerializer):
    # Write-only: Flutter sends [{day_name, exercises:[{exercise_id,sets,reps}]}]
    days = serializers.JSONField(write_only=True, required=False, default=list)
    items = RoutineItemSerializer(many=True, read_only=True)
    device = serializers.PrimaryKeyRelatedField(read_only=True)

    # device_id is injected by the view's perform_create; ignore it if it
    # arrives in the body so DRF doesn't try to validate it as a model field.
    device_id = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Routine
        fields = ['id', 'device', 'device_id', 'name', 'days', 'items', 'created_at']

    def create(self, validated_data):
        days_data = validated_data.pop('days', [])
        validated_data.pop('device_id', None)   # handled by perform_create
        routine = Routine.objects.create(**validated_data)

        order_counter = 0
        for day in days_data:
            day_name = day.get('day_name')
            for ex in day.get('exercises', []):
                RoutineItem.objects.create(
                    routine=routine,
                    day_name=day_name,
                    exercise_id=ex.get('exercise_id'),
                    target_sets=ex.get('sets', 3),
                    target_reps=ex.get('reps', 10),
                    order=order_counter,
                )
                order_counter += 1

        return routine


class WorkoutSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSet
        fields = ['id', 'exercise', 'weight', 'reps', 'rpe', 'created_at']


class WorkoutSessionSerializer(serializers.ModelSerializer):
    sets_data = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False,
    )
    sets = WorkoutSetSerializer(many=True, read_only=True)
    device = serializers.PrimaryKeyRelatedField(read_only=True)
    device_id = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = WorkoutSession
        fields = [
            'id', 'device', 'device_id', 'routine', 'start_time', 'end_time',
            'notes', 'is_active', 'sets', 'sets_data',
        ]

    def create(self, validated_data):
        sets_data = validated_data.pop('sets_data', [])
        validated_data.pop('device_id', None)   # handled by perform_create
        session = WorkoutSession.objects.create(**validated_data)

        for set_item in sets_data:
            WorkoutSet.objects.create(
                session=session,
                exercise_id=set_item.get('exercise'),
                weight=set_item.get('weight', 0),
                reps=set_item.get('reps', 0),
                rpe=set_item.get('rpe', 8),
            )

        return session