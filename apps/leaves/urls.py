from django.urls import path
from . import views

urlpatterns = [
    path('types/', views.LeaveTypeListView.as_view(), name='leave_types'),
    path('requests/', views.LeaveRequestListCreateView.as_view(), name='leave_requests'),
    path('requests/<int:pk>/', views.LeaveRequestDetailView.as_view(), name='leave_detail'),
    path('requests/<int:pk>/review/', views.LeaveReviewView.as_view(), name='leave_review'),
]
