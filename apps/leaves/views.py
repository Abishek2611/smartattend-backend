from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import LeaveRequest, LeaveType
from .serializers import (
    LeaveRequestSerializer, LeaveRequestCreateSerializer,
    LeaveReviewSerializer, LeaveTypeSerializer
)
from apps.accounts.permissions import IsAdminUser


class LeaveTypeListView(generics.ListCreateAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]


class LeaveRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LeaveRequestCreateSerializer
        return LeaveRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            queryset = LeaveRequest.objects.select_related('employee', 'leave_type')
            status_filter = self.request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            return queryset
        return LeaveRequest.objects.filter(employee=user).select_related('leave_type')

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)


class LeaveRequestDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(employee=self.request.user)

    def destroy(self, request, *args, **kwargs):
        leave = self.get_object()
        if leave.status != 'pending':
            return Response(
                {'error': 'Can only cancel pending requests'},
                status=status.HTTP_400_BAD_REQUEST
            )
        leave.status = 'cancelled'
        leave.save()
        return Response({'message': 'Leave request cancelled'})


class LeaveReviewView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            leave = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)

        if leave.status != 'pending':
            return Response({'error': 'Leave request already reviewed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LeaveReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        leave.status = serializer.validated_data['action']
        leave.reviewed_by = request.user
        leave.review_note = serializer.validated_data.get('review_note', '')
        leave.reviewed_at = timezone.now()
        leave.save()

        return Response({
            'message': f'Leave request {leave.status}',
            'leave': LeaveRequestSerializer(leave).data
        })
