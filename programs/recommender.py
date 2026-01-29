# Shim for backward compatibility: import the class from services
from .services.recommender import WorkoutService

# Optionally keep a default instance
default_workout_service = WorkoutService()