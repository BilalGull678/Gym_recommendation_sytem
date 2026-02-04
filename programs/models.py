from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from dateutil.relativedelta import relativedelta
# load_book_data.py ki line 3


class Exercise(models.Model):
    CATEGORY_CHOICES = [
        ("cardio", "Cardio"),
        ("strength", "Strength"),
        ("flexibility", "Flexibility"),
    ]

    KIND_CHOICES = [
        ("plyo", "Plyometric"),
        ("cardio", "Cardio"),
        ("strength", "Strength"),
        ("flexibility", "Flexibility"),
        ("mobility", "Mobility"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="other")
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def __str__(self):
        return self.name


class Prescription(models.Model):
    LEVEL_CHOICES = [
        ("baby", "0-1"),
        ("kid", "2-4"),
        ("adult", "5+"),
    ]

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    sets = models.IntegerField()
    reps = models.IntegerField()
    rest = models.IntegerField(help_text="Rest in seconds")

    class Meta:
        unique_together = ("exercise", "level")

    def __str__(self):
        return f"{self.exercise.name} ({self.level})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    training_start_date = models.DateField(default=timezone.now)
    training_age = models.IntegerField(default=1) # <--- Yeh line add karein
    training_age = models.IntegerField(default=1)  # <--- Yeh line add karein
    dob = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)

    @property
    def current_training_month(self):
        # Aaj ki date aur join date ka farq nikaal kar month calculate karna
        delta = relativedelta(timezone.now().date(), self.training_start_date)
        return (delta.years * 12) + delta.months + 1

# programs/models.py mein
class WorkoutSlotLogic(models.Model):
    training_bracket = models.CharField(max_length=10)
    phase = models.IntegerField()
    slot_number = models.IntegerField()
    movement_pattern = models.CharField(max_length=100)
    base_exercise = models.TextField()
    progression_exercise = models.TextField(null=True, blank=True)
    regression_exercise = models.TextField(null=True, blank=True)  # regression_exercise (as per script)

    class Meta:
        unique_together = ('training_bracket', 'phase', 'slot_number')