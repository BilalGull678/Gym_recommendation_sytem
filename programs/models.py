from django.db import models
from django.contrib.auth.models import User

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    dob = models.DateField(null=True, blank=True)
    # training_age is program-level training age (1, 2, 3, 4, 5, ...)
    # Default to 1 on signup as you requested
    training_age = models.IntegerField(default=1)

    def __str__(self):
        return f"Profile for {self.user.username} (training_age={self.training_age})"