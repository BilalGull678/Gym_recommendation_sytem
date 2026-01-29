from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login  # Django's built-in functions
from rest_framework_simplejwt.tokens import RefreshToken # Needed for JWT
from .models import Exercise
from .serializers import (
    ExerciseSerializer,
    WorkoutResultSerializer,
    SignupSerializer,
    UserProfileSerializer,
)
from .services.recommender import WorkoutService
from .services.scheduler import SchedulerService

workout_service = WorkoutService()
scheduler_service = SchedulerService()


class CategoryOptionsAPI(APIView):
    def get(self, request, category):
        options = workout_service.get_category_options(category)
        serializer = ExerciseSerializer(options, many=True)
        return Response(serializer.data)


class ExerciseDetailAPI(APIView):
    def post(self, request):
        exercise_id = request.data.get("exercise_id")
        training_age = request.data.get("training_age")

        if exercise_id is None or training_age is None:
            return Response(
                {"detail": "Both 'exercise_id' and 'training_age' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            training_age = int(training_age)
        except (ValueError, TypeError):
            return Response(
                {"detail": "'training_age' must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = workout_service.get_exercise_plan(
                exercise_id,
                training_age
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WorkoutResultSerializer(data)
        return Response(serializer.data)

    def get(self, request):
        exercise_id = request.query_params.get("exercise_id")
        training_age = request.query_params.get("training_age")

        if exercise_id is None or training_age is None:
            return Response(
                {"detail": "Query params 'exercise_id' and 'training_age' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            training_age = int(training_age)
        except (ValueError, TypeError):
            return Response(
                {"detail": "'training_age' must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = workout_service.get_exercise_plan(
                exercise_id,
                training_age
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WorkoutResultSerializer(data)
        return Response(serializer.data)
    
# Login_jwt
class LoginAndGetJWT(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Optional: if you still want to support session-based auth alongside JWT
            user = User.objects.get(username=serializer.validated_data['username'])
            login(request, user) 
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class FullWorkoutAPI(APIView):
    def post(self, request):
        categories = request.data.get("categories")
        training_age = request.data.get("training_age")

        if not isinstance(categories, list) or training_age is None:
            return Response(
                {"detail": "'categories' (list) and 'training_age' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            training_age = int(training_age)
        except (ValueError, TypeError):
            return Response(
                {"detail": "'training_age' must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            workout = workout_service.daily_workout(
                categories,
                training_age
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WorkoutResultSerializer(workout, many=True)
        return Response(serializer.data)

    def get(self, request):
        categories_param = request.query_params.get("categories")
        training_age = request.query_params.get("training_age")

        if not categories_param or training_age is None:
            return Response(
                {"detail": "Query params 'categories' and 'training_age' are required. Use categories=cardio,strength"},
                status=status.HTTP_400_BAD_REQUEST
            )

        categories = [c.strip() for c in categories_param.split(",") if c.strip()]

        try:
            training_age = int(training_age)
        except (ValueError, TypeError):
            return Response(
                {"detail": "'training_age' must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            workout = workout_service.daily_workout(
                categories,
                training_age
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WorkoutResultSerializer(workout, many=True)
        return Response(serializer.data)


class AllCategoriesWithExercisesAPI(APIView):
    def get(self, request):
        categories = Exercise.objects.values_list(
            "category", flat=True
        ).distinct()

        data = []

        for cat in categories:
            exercises = Exercise.objects.filter(category=cat)
            data.append({
                "category": cat,
                "subcategories": [
                    {"id": e.id, "name": e.name} for e in exercises
                ]
            })

        return Response(data)


# Signup endpoint — public
class SignupAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response({"detail": "User created", "username": user.username}, status=status.HTTP_201_CREATED)
    
#Sign-in
# add to programs/views.py

class LoginAndGetJWT(APIView):
    """
    Authenticates, creates a Django session (login), and returns JWT refresh & access.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"detail": "username and password required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Create a session cookie
        login(request, user)

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)


# Admin-only: update training_age for a user
class AdminUpdateTrainingAgeAPI(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        new_age = request.data.get("training_age")
        if new_age is None:
            return Response({"detail": "'training_age' is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_age = int(new_age)
        except (ValueError, TypeError):
            return Response({"detail": "'training_age' must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        profile = user.profile
        profile.training_age = new_age
        profile.save()
        return Response({"detail": "training_age updated", "username": username, "training_age": profile.training_age})


# User schedule endpoint — returns 4-day plan for the user's training_age
class UserScheduleAPI(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = request.user.profile
        plan = scheduler_service.build_4_day_plan(profile.training_age)
        serializer = UserProfileSerializer(profile)
        return Response({"profile": serializer.data, "plan": plan})