import random
from ..models import Prescription, Exercise
from .age_logic import AgeLogic


class WorkoutService:
    """
    Class-based workout service that uses AgeLogic class for mapping training_age -> level.
    """

    def __init__(self, age_logic: AgeLogic | None = None):
        # Accept an AgeLogic instance (useful for testing); create default if not provided.
        self.age_logic = age_logic or AgeLogic()

    def get_category_options(self, category):
        return Exercise.objects.filter(category=category)

    def get_exercise_plan(self, exercise_id, training_age):
        level = self.age_logic.get_level(training_age)

        try:
            prescription = Prescription.objects.get(
                exercise_id=exercise_id,
                level=level
            )
        except Prescription.DoesNotExist:
            raise ValueError(
                f"No prescription found for exercise id={exercise_id} and level={level}"
            )

        return {
            "exercise": prescription.exercise.name,
            "sets": prescription.sets,
            "reps": prescription.reps,
            "rest": prescription.rest,
        }

    def daily_workout(self, categories, training_age):
        workout = []

        for category in categories:
            options = self.get_category_options(category)

            if not options.exists():
                continue

            exercise = random.choice(list(options))

            workout.append(
                self.get_exercise_plan(
                    exercise.id,
                    training_age
                )
            )

        return workout