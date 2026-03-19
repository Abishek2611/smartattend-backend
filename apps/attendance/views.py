from rest_framework import generics, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from django_filters.rest_framework import DjangoFilterBackend
import datetime

from .models import Attendance
from .serializers import (
    AttendanceSerializer, CheckInSerializer,
    CheckOutSerializer, AttendanceSummarySerializer
)
from .utils import verify_office_location
from apps.accounts.permissions import IsAdminUser

User = get_user_model()


class CheckInView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        today = timezone.localdate()
        employee = request.user

        # Prevent duplicate check-in
        if Attendance.objects.filter(employee=employee, date=today).exists():
            return Response(
                {'error': 'You have already checked in today'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # GPS Verification
        lat = serializer.validated_data['latitude']
        lon = serializer.validated_data['longitude']
        gps_result = verify_office_location(lat, lon)

        if not gps_result['is_valid']:
            return Response(
                {
                    'error': 'GPS verification failed',
                    'message': gps_result['message'],
                    'distance': gps_result['distance'],
                    'allowed_radius': gps_result['allowed_radius'],
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Create attendance record
        attendance = Attendance.objects.create(
            employee=employee,
            date=today,
            check_in_time=timezone.now(),
            check_in_latitude=lat,
            check_in_longitude=lon,
            check_in_selfie=serializer.validated_data.get('selfie', None),
            check_in_distance=gps_result['distance'],
            status='present'
        )

        return Response({
            'message': gps_result['message'],
            'attendance': AttendanceSerializer(attendance).data,
        }, status=status.HTTP_201_CREATED)


class CheckOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        today = timezone.localdate()
        employee = request.user

        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return Response(
                {'error': 'No check-in found for today. Please check in first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if attendance.check_out_time:
            return Response(
                {'error': 'You have already checked out today'},
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance.check_out_time = timezone.now()
        attendance.check_out_latitude = serializer.validated_data['latitude']
        attendance.check_out_longitude = serializer.validated_data['longitude']
        attendance.save()
        attendance.calculate_total_hours()

        # Classify half day
        if attendance.total_hours and float(attendance.total_hours) < 4:
            attendance.status = 'half_day'
            attendance.save(update_fields=['status'])

        return Response({
            'message': f'Checked out successfully. Total hours: {attendance.total_hours}',
            'attendance': AttendanceSerializer(attendance).data,
        })


class TodayAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        try:
            attendance = Attendance.objects.get(employee=request.user, date=today)
            data = AttendanceSerializer(attendance).data
            data['is_checked_in'] = True
            return Response(data)
        except Attendance.DoesNotExist:
            return Response(None)


class AttendanceHistoryView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date', 'status']
    ordering = ['-date']

    def get_queryset(self):
        user = self.request.user
        queryset = Attendance.objects.filter(employee=user)

        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month and year:
            queryset = queryset.filter(date__month=month, date__year=year)

        return queryset


class AdminAttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['date', 'status', 'employee']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering = ['-date']

    def get_queryset(self):
        queryset = Attendance.objects.select_related('employee', 'employee__department')

        date = self.request.query_params.get('date')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        if date:
            queryset = queryset.filter(date=date)
        elif month and year:
            queryset = queryset.filter(date__month=month, date__year=year)

        return queryset


class DashboardSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.localdate()
        total_employees = User.objects.filter(is_active=True, role='employee').count()

        today_attendance = Attendance.objects.filter(date=today)
        present_today = today_attendance.filter(status__in=['present', 'half_day']).count()
        on_leave = today_attendance.filter(status='on_leave').count()
        absent_today = total_employees - present_today - on_leave

        # Last 7 days trend
        trend = []
        for i in range(6, -1, -1):
            d = today - datetime.timedelta(days=i)
            count = Attendance.objects.filter(date=d, status__in=['present', 'half_day']).count()
            trend.append({'date': str(d), 'present': count})

        # Department-wise today
        from apps.accounts.models import Department
        dept_data = []
        for dept in Department.objects.all():
            dept_employees = User.objects.filter(department=dept, is_active=True, role='employee').count()
            dept_present = Attendance.objects.filter(
                date=today,
                employee__department=dept,
                status__in=['present', 'half_day']
            ).count()
            dept_data.append({
                'department': dept.name,
                'total': dept_employees,
                'present': dept_present,
            })

        from apps.leaves.models import LeaveRequest
        pending_leaves = LeaveRequest.objects.filter(status='pending').select_related('employee', 'leave_type')[:5]
        pending_leaves_data = [
            {
                'id': l.id,
                'employee_name': l.employee.get_full_name(),
                'leave_type': l.leave_type.name,
            }
            for l in pending_leaves
        ]

        return Response({
            'total_employees': total_employees,
            'present_today': present_today,
            'absent_today': max(absent_today, 0),
            'on_leave_today': on_leave,
            'attendance_percentage': round((present_today / total_employees * 100) if total_employees else 0, 1),
            'weekly_trend': trend,
            'department_summary': dept_data,
            'pending_leaves': pending_leaves_data,
        })
