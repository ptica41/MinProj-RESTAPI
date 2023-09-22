from django.shortcuts import redirect
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegistrationSerializer
from Minapp.views import user_response


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = RegistrationSerializer
    # renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        if serializer.is_valid():
            serializer.save()
            return Response(user_response(True, "User was create successful", 201, serializer.data),
                            status=status.HTTP_201_CREATED)
        else:
            return Response(user_response(False, "Incorrect data", 400, serializer.errors,
                                          exception="RegistrationFailed"), status=status.HTTP_400_BAD_REQUEST)
