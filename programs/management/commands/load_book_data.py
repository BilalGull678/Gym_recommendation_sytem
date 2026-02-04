from django.core.management.base import BaseCommand
from django.utils.text import slugify
from programs.models import Exercise, WorkoutSlotLogic

class Command(BaseCommand):
    help = "Load gym exercise logic (16 slots) directly from the book data."

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning old logic data...")
        WorkoutSlotLogic.objects.all().delete() # Fresh start for slots

        # 0-1 AGE TRAINING LOGIC (As per your Excel sheet)
        # Phase 1: Months 1-4
        phase_1_0_1 = [
            {"slot": 1, "pattern": "UPPER PUSH HOR", "base": "DB BENCH 1 ARM", "easy": "DB/KB BENCH 2 ARM", "hard": "DB/KB BENCH 1 ARM 1/2 OFF"},
            {"slot": 2, "pattern": "UPPER PULL HOR", "base": "DB/KB BENCH 1 ARM 3PT ROW", "easy": "BODYWEIGHT ROW- BARBELL", "hard": "BODYWEIGHT ROW- STRAP"},
            {"slot": 3, "pattern": "UPPER PUSH VERT", "base": "DB/KB INCLINE BENCH- 2 ARM", "easy": "DB/KB INCLINE BENCH- 1 ARM", "hard": "PUSHUP- INCLINE"},
            {"slot": 4, "pattern": "UPPER PULL VERT", "base": "PULLUP- NEUTRAL- ISO HOLD", "easy": "SELECTORIZED- ASSISTED PULLUP", "hard": "SELECTORIZED LAT PULLDOWN"},
            {"slot": 5, "pattern": "LOWER PUSH", "base": "DB/KB GOBLET SQUAT", "easy": "DB/KB SQUAT- 2 ARM", "hard": "DB/KB GOBLET SQUAT- STAGGERED"},
            {"slot": 6, "pattern": "LOWER PULL (HIP)", "base": "DB/KB RDL-STAGGERED STANCE- 2 ARM", "easy": "DB/KB RDL-1 LEG- 2 ARM", "hard": "CABLE PULL THROUGH"},
            {"slot": 7, "pattern": "LOWER PULL KNEE", "base": "SLIDE ECCENTRIC LOWER", "easy": "PHYSIOBALL HAMSTRING CURL", "hard": "SELECTORIZED HAMSTRING CURL"},
            {"slot": 8, "pattern": "CORE", "base": "SIDE PLANK- ELBOWS-KNEE TUCK", "easy": "SIDE PLANK- ELBOWS-LEG LIFT", "hard": "FRONT PLANK W DIAGNOL ARM LIFT"},
            {"slot": 9, "pattern": "OLYMPIC", "base": "KETTLEBELL SWING- 2 ARM", "easy": "DB/KB SNATCH - 1 ARM", "hard": "BARBELL CLEAN PULL"},
            {"slot": 10, "pattern": "MEDICINE BALL", "base": "SQUAT TO THROW- VERTICAL", "easy": "GRANNY TOSS", "hard": "OVERHEAD SLAM- STANDING"},
            # Adding placeholders for slots 11-16 (Warmups/Finisher)
            {"slot": 11, "pattern": "WARMUP 1", "base": "FORWARD ELBOW TO IN-STEP x 3ea", "easy": "None", "hard": "None"},
            {"slot": 12, "pattern": "WARMUP 2", "base": "LATERAL LUNGE x 3ea", "easy": "None", "hard": "None"},
            {"slot": 13, "pattern": "WARMUP 3", "base": "REVERSE LUNGE x 3ea", "easy": "None", "hard": "None"},
            {"slot": 14, "pattern": "WARMUP 4", "base": "PUSHUP x 3ea", "easy": "None", "hard": "None"},
            {"slot": 15, "pattern": "SPEED", "base": "A-SKIP 2 x 10 yds", "easy": "None", "hard": "None"},
            {"slot": 16, "pattern": "FINISHER", "base": "RHYTHM- LINEAR ACCEL", "easy": "None", "hard": "None"},
        ]

        # Brackets and Phases
        brackets = [
            ("0-1", 1, 4, phase_1_0_1), # Bracket, Start Month, End Month, Data List
        ]

        self.stdout.write("Loading 16 Exercise Slots with Options...")

        for bracket, start, end, slots in brackets:
            for s in slots:
                # Create Exercise Objects first to maintain consistency
                slug = slugify(s["base"])
                Exercise.objects.get_or_create(
                    slug=slug,
                    defaults={"name": s["base"], "category": s["pattern"], "kind": s["pattern"]}
                )

                # Save the logic to the new model
                WorkoutSlotLogic.objects.update_or_create(
                    training_bracket=bracket,
                    phase=start,  # 'month_range_start' ki jagah 'phase' use karein
                    slot_number=s["slot"],
                    defaults={
                        # 'month_range_end' ko hata dein kyunki aapke model mein nahi hai
                        "movement_pattern": s["pattern"], # Model mein jo naam hai wahi yahan likhein
                        "base_exercise": s["base"],
                        "progression_exercise": s["easy"],
                        "regression_exercise": s["hard"],
                    }
                )

        self.stdout.write(self.style.SUCCESS("Master gym logic loaded successfully."))