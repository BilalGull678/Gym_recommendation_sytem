import token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework_simplejwt.tokens import RefreshToken

# Local Imports
from .models import Exercise, WorkoutSlotLogic
from .serializers import (
    ExerciseSerializer,
    WorkoutResultSerializer,
    SignupSerializer,
    UserProfileSerializer,
    LoginSerializer
)
from .services.recommender import WorkoutService
from .services.scheduler import SchedulerService
from .emails import send_brevo_email # Brevo email function
import random


# Global Instances
workout_service = WorkoutService()
scheduler_service = SchedulerService()

# --- AUTHENTICATION VIEWS ---

class SignupAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            if user.email:
                # Link generate karein jo email mein button par lagega
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # IMPORTANT: 'localhost' ya '127.0.0.1' ka poora path
                verify_link = f"http://127.0.0.1:8000/api/verify-email/{uid}/{token}/"
                
                subject = "Verify Your Email - Gym System"
                context = {
                    'username': user.username,
                    'verify_link': verify_link # <--- Signup email mein link chahiye
                }
                send_brevo_email(subject, 'emails/signup_welcome.html', context, user.email)
            
            return Response({"detail": "User created. Verification email sent!"}, status=201)
        return Response(serializer.errors, status=400)
    
class VerifyEmailAndSendOTP(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            # 1. Decode the User ID from the URL
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid verification link."}, status=400)

        # 2. Check if the token from the URL is valid for this user
        if user and default_token_generator.check_token(user, token):
            profile = user.profile
            
            # Update verification status
            profile.is_verified = True 
            
            # 3. Generate a 6-digit OTP
            otp_code = str(random.randint(100000, 999999))
            profile.otp = otp_code 
            profile.save()

            # 4. Prepare and send the OTP email via Brevo
            subject = "Your Gym System OTP Code"
            context = {
                'username': user.username,
                'otp': otp_code
            }
            
            email_status = send_brevo_email(subject, 'emails/otp_email.html', context, user.email)

            if email_status:
                return Response({
                    "detail": "Email verified! An OTP has been sent to your inbox.",
                    "username": user.username
                }, status=200)
            else:
                return Response({"detail": "Verified, but failed to send OTP email."}, status=500)
        
        return Response({"detail": "This link is invalid or has expired."}, status=400)

class LoginAndGetJWT(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            user = User.objects.get(username=username)
            login(request, user) 
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

# --- PASSWORD RESET VIEWS (BREVO) ---

# programs/views.py

class ForgetPasswordRequestAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_link = f"http://127.0.0.1:8000/api/verify-reset-link/{uid}/{token}/"
            
            # Send Email
            subject = "Password Reset Request"
            context = {'username': user.username, 'reset_link': reset_link}
            send_brevo_email(subject, 'emails/reset_password.html', context, email)
            
            # Yahan hum response mein uid aur token bhej rahe hain testing ke liye
            return Response({
                "detail": "Reset button sent to email.",
                "uid": uid,    # <--- Ab ye Postman mein nazar aayega
                "token": token  # <--- Ab ye Postman mein nazar aayega
            })
        
        return Response({"detail": "Email not found"}, status=404)
    
class VerifyResetLinkAndSendOTP(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid reset link."}, status=400)

        # Check if the URL token is valid
        if user and default_token_generator.check_token(user, token):
            # Generate 6-digit OTP
            otp_code = str(random.randint(100000, 999999))
            profile = user.profile
            profile.otp = otp_code
            profile.save()

            # Send the OTP Email (reset_otp.html)
            subject = "Your Security OTP Code"
            context = {
                'username': user.username,
                'otp': otp_code
            }
            send_brevo_email(subject, 'emails/reset_otp.html', context, user.email)

            # Redirect user to frontend OTP screen or show success
            return Response({
                "detail": "Link verified! A security OTP has been sent to your email.",
                "uid": uidb64,
                "token": token
            })
        
        return Response({"detail": "This reset link has expired."}, status=400)
    
class FinalPasswordResetAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        otp_received = request.data.get("otp")
        new_password = request.data.get("password")

        if not otp_received or not new_password:
            return Response({"detail": "OTP and password are required."}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            profile = user.profile
        except:
            return Response({"detail": "User not found."}, status=404)

        # Check OTP match
        if profile.otp == otp_received:
            user.set_password(new_password)
            user.save()
            profile.otp = None # Clear OTP after use
            profile.save()
            return Response({"detail": "Password updated successfully!"})
        
        return Response({"detail": "Invalid OTP."}, status=400)
    
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
            workout = workout_service.daily_workout(categories, int(training_age))
            serializer = WorkoutResultSerializer(workout, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class AllCategoriesWithExercisesAPI(APIView):
    permission_classes = [AllowAny] # Sab dekh sakte hain

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
    
class AdminUpdateTrainingAgeAPI(APIView):
    permission_classes = [IsAdminUser] # Sirf admin change kar sakta hai

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
        
        return Response({
            "detail": "training_age updated", 
            "username": username, 
            "new_training_age": profile.training_age
        })

class PasswordResetConfirmAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            new_password = request.data.get("password")
            if not new_password:
                return Response({"detail": "New password is required"}, status=400)
            
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password changed successfully!"})
        
        return Response({"detail": "Invalid link or token"}, status=400)

# --- GYM LOGIC VIEWS ---

class UserScheduleAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        user_month = profile.current_training_month
        
        if profile.training_age <= 1:
            bracket = "0-1"
        elif profile.training_age <= 4:
            bracket = "2-4"
        else:
            bracket = "5+"

        current_phase = 1 if user_month <= 4 else 2

        slots = WorkoutSlotLogic.objects.filter(
            training_bracket=bracket,
            phase=current_phase
        ).order_by('slot_number')

        if not slots.exists():
            return Response({"detail": "No workout plan found for your level."}, status=404)

        plan_data = []
        for s in slots:
            plan_data.append({
                "slot_id": s.slot_number,
                "pattern": s.movement_pattern,
                "options": {
                    "starting_exercise": s.base_exercise,
                    "if_too_easy": s.progression_exercise,
                    "if_too_hard": s.regression_exercise
                }
            })

        serializer = UserProfileSerializer(profile)
        return Response({
            "profile": serializer.data,
            "current_month": user_month,
            "bracket": bracket,
            "phase": current_phase,
            "16_slot_plan": plan_data
        })

class MyWorkoutOptionsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_month = request.user.profile.current_training_month
        training_age = request.user.profile.training_age
        
        bracket = "0-1" if training_age <= 1 else ("2-4" if training_age <= 4 else "5+")
        phase = 1 if user_month <= 4 else 2 

        slots = WorkoutSlotLogic.objects.filter(training_bracket=bracket, phase=phase).order_by('slot_number')
        
        results = [{"slot_id": s.slot_number, "pattern": s.movement_pattern, "options": {"base": s.base_exercise, "progression": s.progression_exercise, "regression": s.regression_exercise}} for s in slots]

        return Response({"month": user_month, "bracket": bracket, "phase": phase, "workout": results})

# --- UTILITY VIEWS (CATEGORIES & DETAILS) ---

class CategoryOptionsAPI(APIView):
    def get(self, request, category):
        options = workout_service.get_category_options(category)
        serializer = ExerciseSerializer(options, many=True)
        return Response(serializer.data)

class ExerciseDetailAPI(APIView):
    def post(self, request):
        exercise_id, training_age = request.data.get("exercise_id"), request.data.get("training_age")
        if exercise_id is None or training_age is None:
            return Response({"detail": "Missing fields"}, status=400)
        try:
            data = workout_service.get_exercise_plan(exercise_id, int(training_age))
            return Response(WorkoutResultSerializer(data).data)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)