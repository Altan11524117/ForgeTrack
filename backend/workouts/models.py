import uuid
from django.db import models

class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.id)

class Exercise(models.Model):
    MUSCLE_GROUPS = [
        ('CHEST', 'Chest'),
        ('BACK', 'Back'),
        ('LEGS', 'Legs'),
        ('SHOULDERS', 'Shoulders'),
        ('ARMS', 'Arms'),
        ('CORE', 'Core'),
    ]
    name = models.CharField(max_length=100)
    muscle_group = models.CharField(max_length=20, choices=MUSCLE_GROUPS)
    is_compound = models.BooleanField(default=False, help_text="Is this a base/compound move?")
    
    def __str__(self):
        return self.name

class Routine(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='routines')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.device.id}"

class RoutineItem(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='items')
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True)
    

    day_name = models.CharField(max_length=20, default="Monday") 
    
    order = models.PositiveIntegerField(default=0)
    target_sets = models.PositiveIntegerField(default=3)
    target_reps = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f"{self.day_name}: {self.exercise.name} ({self.target_sets}x{self.target_reps})"

class WorkoutSession(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sessions')
    routine = models.ForeignKey(Routine, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    @property
    def is_active(self):
        return self.end_time is None
        
    def __str__(self):
        return f"Session {self.id} - {self.device.id}"

class WorkoutSet(models.Model):
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='sets')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=2) 
    reps = models.PositiveIntegerField()
    rpe = models.PositiveIntegerField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exercise.name} - {self.weight}kg x {self.reps}"