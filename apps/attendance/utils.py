import math
from django.conf import settings


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two GPS points using Haversine formula.
    Returns distance in meters.
    """
    R = 6371000  # Earth's radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return round(distance, 2)


def verify_office_location(employee_lat: float, employee_lon: float) -> dict:
    """
    Verify if employee is within allowed radius of office.
    Returns dict with is_valid, distance, and message.
    """
    office_lat = settings.OFFICE_LATITUDE
    office_lon = settings.OFFICE_LONGITUDE
    allowed_radius = settings.OFFICE_RADIUS_METERS

    distance = haversine_distance(
        float(employee_lat), float(employee_lon),
        office_lat, office_lon
    )

    is_within_radius = distance <= allowed_radius

    return {
        'is_valid': is_within_radius,
        'distance': distance,
        'allowed_radius': allowed_radius,
        'office_lat': office_lat,
        'office_lon': office_lon,
        'message': (
            f'Check-in approved. You are {distance:.0f}m from the office.'
            if is_within_radius
            else f'Check-in denied. You are {distance:.0f}m from the office. Must be within {allowed_radius}m.'
        )
    }
