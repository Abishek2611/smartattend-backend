from rest_framework import serializers, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import LeaveRequest, LeaveType
from apps.accounts.permissions import IsAdminUser


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'max_days_per_year', 'description']


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id_code = serializers.CharField(source='employee.employee_id', read_only=True)
    department = serializers.CharField(source='employee.department.name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'employee_id_code', 'department',
            'leave_type', 'leave_type_name', 'start_date', 'end_date', 'total_days',
            'reason', 'status', 'reviewed_by', 'reviewed_by_name',
            'review_note', 'reviewed_at', 'created_at'
        ]
        read_only_fields = ['employee', 'status', 'reviewed_by', 'reviewed_at', 'total_days']


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']

    def validate(self, attrs):
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError('Start date must be before end date')
        if attrs['start_date'] < timezone.localdate():
            raise serializers.ValidationError('Cannot apply leave for past dates')
        return attrs


class LeaveReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approved', 'rejected'])
    review_note = serializers.CharField(required=False, allow_blank=True)
