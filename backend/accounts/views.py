from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response({"detail": "Invalid username or password."}, status=400)

        login(request, user)

        return Response({
            "username": user.username,
            "message": "Logged in successfully."
        })


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."})