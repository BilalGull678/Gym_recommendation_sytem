import random
from ..models import Prescription, Exercise
from .recommender import WorkoutService
from .age_logic import AgeLogic


class SchedulerService:
    """
    Class-based scheduler that uses AgeLogic and WorkoutService.
    Produces a 4-day plan composed from up to 16 exercises for a training_age.
    """

    def __init__(self, age_logic: AgeLogic | None = None, workout_service: WorkoutService | None = None):
        self.age_logic = age_logic or AgeLogic()
        self.workout_service = workout_service or WorkoutService(self.age_logic)

    def get_candidates_for_level(self, training_age):
        level = self.age_logic.get_level(training_age)
        prescriptions = Prescription.objects.filter(level=level).select_related("exercise")
        seen = set()
        exercises = []
        for p in prescriptions:
            e = p.exercise
            if e.id not in seen:
                seen.add(e.id)
                exercises.append((e, p))
        return exercises

    def select_16(self, exercises_with_pres):
        if len(exercises_with_pres) <= 16:
            return exercises_with_pres[:]
        return random.sample(exercises_with_pres, 16)

    def build_4_day_plan(self, training_age):
        candidates = self.get_candidates_for_level(training_age)
        if not candidates:
            return [{"day": i + 1, "exercises": []} for i in range(4)]

        selected = self.select_16(candidates)

        plyo = [item for item in selected if item[0].kind == "plyo"]
        non_plyo = [item for item in selected if item[0].kind != "plyo"]

        days = [[] for _ in range(4)]

        # Distribute plyo exercises first
        for idx, item in enumerate(plyo):
            day_idx = idx % 4
            e, p = item
            days[day_idx].append(self._plan_dict(e, p))

        # Fill remaining slots aiming for 4 per day when possible
        remaining_slots = [4 - len(d) for d in days]
        random.shuffle(non_plyo)
        ni = 0
        for day_idx, slots in enumerate(remaining_slots):
            while slots > 0 and ni < len(non_plyo):
                e, p = non_plyo[ni]
                days[day_idx].append(self._plan_dict(e, p))
                ni += 1
                slots -= 1

        # If any non_plyo left, append round-robin
        while ni < len(non_plyo):
            for day_idx in range(4):
                if ni >= len(non_plyo):
                    break
                e, p = non_plyo[ni]
                days[day_idx].append(self._plan_dict(e, p))
                ni += 1

        return [
            {"day": i + 1, "exercises": days[i]}
            for i in range(4)
        ]

    def _plan_dict(self, exercise, prescription):
        return {
            "exercise": exercise.name,
            "kind": exercise.kind,
            "sets": prescription.sets,
            "reps": prescription.reps,
            "rest": prescription.rest,
        }