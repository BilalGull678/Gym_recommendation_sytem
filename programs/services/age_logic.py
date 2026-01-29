# def get_level(training_age):
#     if training_age <= 1:
#         return "beginner"
#     elif training_age <=4:
#         return "intermediate"
#     return "advanced"
class AgeLogic:
    """
    Encapsulates training-age -> level mapping in a class so callers use an instance.
    """

    def get_level(self, training_age: int) -> str:
        """
        Map numeric training_age to level strings used by Prescription.level.

        Rules:
        - training_age <= 1  => "baby"
        - 2 <= training_age <= 4 => "kid"
        - training_age >= 5 => "adult"
        """
        try:
            ta = int(training_age)
        except (TypeError, ValueError):
            # If invalid input is given, default to baby (you can change this behavior).
            ta = 1

        if ta <= 1:
            return "baby"
        if 2 <= ta <= 4:
            return "kid"
        return "adult"
