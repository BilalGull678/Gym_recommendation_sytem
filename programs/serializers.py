from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Exercise, Prescription, UserProfile
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ["id", "name", "category", "kind"]

class PrescriptionSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    class Meta:
        model = Prescription
        fields = ["id", "exercise", "level", "sets", "reps", "rest"]

class WorkoutResultSerializer(serializers.Serializer):
    exercise = serializers.CharField()
    sets = serializers.IntegerField()
    reps = serializers.IntegerField()
    rest = serializers.IntegerField()
    kind = serializers.CharField(required=False)

# Signup serializer
class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField() # <--- Yeh line lazmi add karein
    dob = serializers.DateField(required=False, allow_null=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"], # <--- Yeh line bhi add karein
            password=validated_data["password"]
        )
        profile = user.profile
        profile.dob = validated_data.get("dob")
        profile.save()
        return user
    
# Login-user-flow
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid username or password.")
        else:
            raise serializers.ValidationError("Both username and password are required.")

        # If authentication succeeds, generate tokens
        refresh = RefreshToken.for_user(user)
        
        return {
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = UserProfile
        fields = ["user", "dob", "training_age"]