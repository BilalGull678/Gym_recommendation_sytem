# Source "book" data: exercises and prescriptions.
# You can extend each exercise dict with an optional "kind" key (plyo/strength/cardio/etc).
BOOK_EXERCISES = {
    "cardio": [
        {"name": "Walking", "kind": "cardio"},
        {"name": "Running", "kind": "cardio"},
        {"name": "Jump Rope", "kind": "plyo"},
    ],
    "strength": [
        {"name": "Push-ups", "kind": "strength"},
        {"name": "Squats", "kind": "strength"},
        {"name": "Plank", "kind": "strength"},
    ],
    "flexibility": [
        {"name": "Yoga", "kind": "flexibility"},
        {"name": "Stretching", "kind": "mobility"},
        {"name": "Pilates", "kind": "flexibility"},
    ],
}

# Keys in BOOK_PRESCRIPTIONS must match exercise names (case-insensitive matching is handled by loader).
BOOK_PRESCRIPTIONS = {
    "baby": {
        "Walking": {"sets": 1, "reps": 10, "rest": 30},
    },
    "kid": {
        "Walking": {"sets": 2, "reps": 15, "rest": 40},
        "Push-ups": {"sets": 2, "reps": 8, "rest": 60},
    },
    "adult": {
        "Running": {"sets": 3, "reps": 20, "rest": 60},
        "Push-ups": {"sets": 4, "reps": 12, "rest": 90},
        "Squats": {"sets": 4, "reps": 15, "rest": 90},
    },
}