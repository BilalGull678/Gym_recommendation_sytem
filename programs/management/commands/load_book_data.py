from django.core.management.base import BaseCommand
from django.utils.text import slugify
from programs.models import Exercise, Prescription
from programs.book_data import BOOK_EXERCISES, BOOK_PRESCRIPTIONS

class Command(BaseCommand):
    help = "Load gym exercise and prescription data from the book source."

    def handle(self, *args, **kwargs):
        self.stdout.write("Loading exercise data...")

        exercise_map = {}

        # Normalize keys by lowercasing names to avoid mismatches
        for category, exercises in BOOK_EXERCISES.items():
            for e in exercises:
                name = e["name"].strip()
                kind = e.get("kind", "other")
                slug = slugify(name)
                obj, created = Exercise.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "category": category,
                        "kind": kind,
                    }
                )
                if not created:
                    # update fields if they changed in book data
                    updated = False
                    if obj.name != name:
                        obj.name = name
                        updated = True
                    if obj.category != category:
                        obj.category = category
                        updated = True
                    if obj.kind != kind:
                        obj.kind = kind
                        updated = True
                    if updated:
                        obj.save()
                exercise_map[name.lower()] = obj

        self.stdout.write("Loading prescription data...")

        for level, exercises in BOOK_PRESCRIPTIONS.items():
            for name, data in exercises.items():
                key = name.strip().lower()
                exercise_obj = exercise_map.get(key)
                if not exercise_obj:
                    self.stdout.write(self.style.WARNING(
                        f"Skipping prescription for '{name}' (not found in BOOK_EXERCISES)."
                    ))
                    continue

                Prescription.objects.get_or_create(
                    exercise=exercise_obj,
                    level=level,
                    defaults={
                        "sets": data["sets"],
                        "reps": data["reps"],
                        "rest": data["rest"],
                    }
                )

        self.stdout.write(self.style.SUCCESS("Data loading complete."))