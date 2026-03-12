from django.urls import path
from . import views

urlpatterns = [
    path('check-in/', views.CheckInView.as_view(), name='check_in'),
    path('check-out/', views.CheckOutView.as_view(), name='check_out'),
    path('today/', views.TodayAttendanceView.as_view(), name='today_attendance'),
    path('history/', views.AttendanceHistoryView.as_view(), name='attendance_history'),
    path('admin/all/', views.AdminAttendanceListView.as_view(), name='admin_attendance'),
    path('admin/dashboard/', views.DashboardSummaryView.as_view(), name='dashboard_summary'),
]
