from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
#from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import check_password, make_password

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


# This view is used to register a new user
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Check that email does not already exist
        if User.objects.filter(email=email).exists():
            return Response({
                "message": "Email already exists"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check that username does not already exist
        if User.objects.filter(username=username).exists():
            return Response({
                "message": "Username already exists"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check password requirements are met
        # Password must be at least 8 characters long
        if len(password) < 8:
            return Response({
                "message": "Password must be at least 8 characters long"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Password must contain at least one uppercase letter
        if not any(char.isupper() for char in password):
            return Response({
                "message": "Password must contain at least one uppercase letter"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Password must contain at least one number
        if not any(char.isdigit() for char in password):
            return Response({
                "message": "Password must contain at least one number"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Password must contain at least one special character
        special_characters = "!@#$%^&*()-+"
        if not any(char in special_characters for char in password):
            return Response({
                "message": "Password must contain at least one special character"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create a User instance
        user = User.objects.create_user(username=username, email=email, password=password)

        # Generate token for user
        token = Token.objects.create(user=user)

        # Return the response with the user and token
        return Response({
            "message": "User registered successfully",
        }, status=status.HTTP_201_CREATED)
    

# This view is used to authenticate user login
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Check that username and password are not empty
        if not username or not password:
            return Response({
                "message": "Username and/or password required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user login credentials
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response({
                "message": "User logged in successfully",
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                "message": "Invalid Credentials"
            }, status=status.HTTP_400_BAD_REQUEST)

