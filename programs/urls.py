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
    LoginAndGetJWT,
    MyWorkoutOptionsAPI,
    ForgetPasswordRequestAPI,
    PasswordResetConfirmAPI,
    VerifyEmailAndSendOTP,
    VerifyResetLinkAndSendOTP,
    FinalPasswordResetAPI,
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
    path("my-options/", MyWorkoutOptionsAPI.as_view()),
    path("reset-password-confirm/<uidb64>/<token>/", PasswordResetConfirmAPI.as_view()),
    path('verify-email/<uidb64>/<token>/', VerifyEmailAndSendOTP.as_view(), name='verify-email'),
    path('forget-password/', ForgetPasswordRequestAPI.as_view(), name='forget_password'),
path('verify-reset-link/<uidb64>/<token>/', VerifyResetLinkAndSendOTP.as_view(), name='verify_reset_link'),
path('reset-password-final/<uidb64>/<token>/', FinalPasswordResetAPI.as_view(), name='reset_password_final'),
]