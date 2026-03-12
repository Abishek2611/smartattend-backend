from rest_framework import serializers
from django.utils import timezone
from .models import Attendance
from apps.accounts.serializers import UserSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id_code = serializers.CharField(source='employee.employee_id', read_only=True)
    department = serializers.CharField(source='employee.department.name', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'employee_id_code', 'department',
            'date', 'check_in_time', 'check_in_latitude', 'check_in_longitude',
            'check_in_selfie', 'check_in_distance', 'check_out_time',
            'check_out_latitude', 'check_out_longitude', 'total_hours',
            'status', 'notes', 'created_at'
        ]
        read_only_fields = ['employee', 'total_hours', 'check_in_distance']


class CheckInSerializer(serializers.Serializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    selfie = serializers.ImageField(required=True)

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError('Invalid latitude value')
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError('Invalid longitude value')
        return value


class CheckOutSerializer(serializers.Serializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError('Invalid latitude value')
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError('Invalid longitude value')
        return value


class AttendanceSummarySerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    present_today = serializers.IntegerField()
    absent_today = serializers.IntegerField()
    on_leave_today = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()
