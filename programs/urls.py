from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    CategoryOptionsAPI,
    ExerciseDetailAPI,
    FullWorkoutAPI,
    AllCategoriesWithExercisesAPI,
    SignupAPI,
    AdminUpdateTrainingAgeAPI,
    UserScheduleAPI,
    LoginAndGetJWT
)

urlpatterns = [
    path("options/<str:category>/", CategoryOptionsAPI.as_view()),
    path("exercise-detail/", ExerciseDetailAPI.as_view()),
    path("full-workout/", FullWorkoutAPI.as_view()),
    path("all-categories/", AllCategoriesWithExercisesAPI.as_view()),
    path("signup/", SignupAPI.as_view()),
    path("admin/update-training-age/<str:username>/", AdminUpdateTrainingAgeAPI.as_view()),
    path("my-schedule/", UserScheduleAPI.as_view()),
    path('api-token-auth/', obtain_auth_token),  # POST username & password -> {"token": "..."},
    path("login/", LoginAndGetJWT.as_view(), name="login_and_get_jwt"),
]