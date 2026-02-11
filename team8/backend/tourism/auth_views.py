import bcrypt
import jwt
from datetime import timedelta, timezone, datetime
from django.conf import settings
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User
from .utils import log_activity


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def generate_jwt(user_id: int, email: str, username: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'username': username,
        'exp': datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXP_DAYS),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register new user"""
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    
    if not username or not email or not password:
        return Response(
            {'error': 'username, email, and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(password) < 8:
        return Response(
            {'error': 'password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.create(
            username=username,
            email=email,
            password_hash=hash_password(password)
        )
        
        token = generate_jwt(user.user_id, user.email, user.username)
        
        log_activity(user, 'USER_LOGIN', metadata={'via': 'register'})
        
        response = Response({
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'created_at': user.created_at,
            },
            'token': token,
        }, status=status.HTTP_201_CREATED)
        
        response.set_cookie(
            'access_token', token,
            max_age=settings.JWT_EXP_DAYS * 86400,
            httponly=True, samesite='Lax',
        )
        
        return response
        
    except IntegrityError as e:
        if 'username' in str(e):
            return Response({'error': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        elif 'email' in str(e):
            return Response({'error': 'email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'registration failed'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user"""
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    
    if not username or not password:
        return Response(
            {'error': 'username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(username=username)
        
        if not verify_password(password, user.password_hash):
            return Response(
                {'error': 'invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token = generate_jwt(user.user_id, user.email, user.username)
        
        log_activity(user, 'USER_LOGIN')
        
        response = Response({
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
            },
            'token': token
        })
        
        response.set_cookie(
            'access_token', token,
            max_age=settings.JWT_EXP_DAYS * 86400,
            httponly=True, samesite='Lax',
        )
        
        return response
        
    except User.DoesNotExist:
        return Response(
            {'error': 'invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    """Logout user"""
    response = Response({'message': 'logged out successfully'})
    response.delete_cookie('access_token')
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_token(request):
    """Verify JWT token from cookie"""
    token = request.COOKIES.get('access_token')
    
    if not token:
        return Response({'error': 'not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    payload = decode_jwt(token)
    
    if not payload:
        return Response({'error': 'invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        user = User.objects.get(user_id=payload['user_id'])
        return Response({
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
            }
        })
    except User.DoesNotExist:
        return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_profile(request):
    """Get current user profile"""
    return Response({
        'user': {
            'user_id': request.user.user_id,
            'username': request.user.username,
            'email': request.user.email,
            'is_admin': request.user.is_admin,
            'created_at': request.user.created_at,
            'updated_at': request.user.updated_at
        }
    })
