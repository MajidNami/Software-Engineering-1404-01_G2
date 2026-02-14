from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Func, Value
import math


class Point:
    """Simple Point class to hold longitude and latitude"""
    def __init__(self, longitude, latitude):
        self.longitude = float(longitude)
        self.latitude = float(latitude)
    
    def __repr__(self):
        return f"Point({self.longitude}, {self.latitude})"
    
    def __str__(self):
        return f"({self.longitude}, {self.latitude})"
    
    def __iter__(self):
        return iter([self.longitude, self.latitude])
    
    def distance(self, other):
        """
        Calculate distance between two points using Haversine formula.
        Returns distance in kilometers.
        
        Args:
            other: Another Point object
        
        Returns:
            float: Distance in kilometers
        """
        if not isinstance(other, Point):
            raise TypeError("other must be a Point object")
        
        # Convert to radians
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        lon1 = math.radians(self.longitude)
        lon2 = math.radians(other.longitude)
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in kilometers
        r = 6371
        
        return c * r


class PointField(models.Field):
    """
    Custom field that stores data as MySQL POINT type.
    In Python: Point(longitude, latitude)
    In MySQL: POINT(longitude latitude)
    """
    
    description = "A geographic point (longitude, latitude)"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def db_type(self, connection):
        return 'POINT'
    
    def from_db_value(self, value, expression, connection):
        """Convert from MySQL POINT to Python Point object"""
        if value is None:
            return None
        
        # With ST_AsText, MySQL returns as string "POINT(lon lat)"
        if isinstance(value, str):
            if value.startswith('POINT('):
                coords = value.replace('POINT(', '').replace(')', '').split()
                return Point(float(coords[0]), float(coords[1]))
        
        # If it's bytes, parse WKB format
        if isinstance(value, bytes):
            import struct
            lon, lat = struct.unpack('<dd', value[5:])
            return Point(lon, lat)
        
        return value
    
    def to_python(self, value):
        """Convert to Python Point object"""
        if value is None:
            return None
        
        if isinstance(value, Point):
            return value
        
        if isinstance(value, (tuple, list)) and len(value) == 2:
            return Point(value[0], value[1])
        
        if isinstance(value, dict):
            return Point(value['longitude'], value['latitude'])
        
        if isinstance(value, str):
            # Parse WKT: "POINT(lon lat)"
            if value.startswith('POINT('):
                coords = value.replace('POINT(', '').replace(')', '').split()
                return Point(float(coords[0]), float(coords[1]))
        
        return value
    
    def get_prep_value(self, value):
        """Prepare value for database (convert to WKT format)"""
        if value is None:
            return None
        
        if isinstance(value, Point):
            lon, lat = value.longitude, value.latitude
        elif isinstance(value, (tuple, list)) and len(value) == 2:
            lon, lat = value
        elif isinstance(value, dict):
            lon, lat = value['longitude'], value['latitude']
        else:
            raise ValidationError("Invalid point value")
        
        # Validate
        if not (-180 <= lon <= 180):
            raise ValidationError(f"Longitude must be between -180 and 180, got {lon}")
        if not (-90 <= lat <= 90):
            raise ValidationError(f"Latitude must be between -90 and 90, got {lat}")
        
        return value
    
    def get_db_prep_save(self, value, connection):
        """Prepare value for saving to database - return raw SQL expression"""
        if value is None:
            return None
            
        # Prepare the value first
        value = self.get_prep_value(value)
        
        if isinstance(value, Point):
            lon, lat = value.longitude, value.latitude
        elif isinstance(value, (tuple, list)) and len(value) == 2:
            lon, lat = value
        else:
            return None
        
        # For MySQL/MariaDB, return WKT string
        # Django will pass this as parameter to ST_GeomFromText
        return f"POINT({lon} {lat})"
    
    def get_db_prep_value(self, value, connection, prepared=False):
        """This is called by get_db_prep_save"""
        if prepared:
            return value
        return self.get_db_prep_save(value, connection)
    
    def get_placeholder(self, value, compiler, connection):
        """Return placeholder for SQL query"""
        # For MySQL/MariaDB POINT type, use ST_GeomFromText
        return "ST_GeomFromText(%s)"
    
    def select_format(self, compiler, sql, params):
        """Format SELECT to return location as binary data that can be parsed"""
        # Return as-is, MySQL will return as WKB binary
        # Or use ST_AsText for text format
        return f"ST_AsText({sql})", params
    
    def value_to_string(self, obj):
        """Serialize for fixtures"""
        value = self.value_from_object(obj)
        if value is None:
            return None
        if isinstance(value, Point):
            return f"{value.longitude},{value.latitude}"
        return str(value)
