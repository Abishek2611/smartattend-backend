from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('employees/', views.UserListCreateView.as_view(), name='employee_list'),
    path('employees/<int:pk>/', views.UserDetailView.as_view(), name='employee_detail'),
    path('departments/', views.DepartmentListCreateView.as_view(), name='department_list'),
]
