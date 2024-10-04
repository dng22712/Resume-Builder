from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.models import Strength, CvBuilder
from cvbuilder.strength.serializers import StrengthSerializer
from util.payments.user_payment_checks import premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'  # error message`


# -------------------------- Strength by CV ID --------------------------
@extend_schema(tags=['CV: Strength'])
class StrengthByCvId(APIView):
    """
    Retrieve, update, or delete strength by CV ID.
    """

    serializer_class = StrengthSerializer
    queryset = Strength.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve strength by CV ID.
        :param request:
        :param pk:
        :return:
        """

        queryset = self.queryset.filter(cv=pk).order_by('-strength_name')
        serializer = self.serializer_class(queryset, many=True)
        return Response({'strengths': serializer.data}, status=status.HTTP_200_OK)

    @premium_required
    def post(self, request, pk=None):
        """
        post strength by CV ID.
        :param request:
        :param pk:
        :return:
        """

        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            strength = Strength.objects.get(cv=cv, strength_name=request.data['strength_name'])
            if strength:
                return Response({'message': 'Strength already exists'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(cv=cv)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Strength.DoesNotExist:
            return Response({'message': 'Strength does not exist'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        delete strength by CV ID.
        :param request:
        :param pk:
        :return:
        """

        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object

        # check if the user is the owner of the CV
        if cv.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            # delete the strength object from the cv object
            Strength.objects.filter(cv=pk).delete()
            return Response({'message': 'Strength deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------- Strength by Strength ID --------------------------

@extend_schema(tags=['CV: Strength'])
class StrengthById(APIView):
    """
    Retrieve, update, or delete strength by Strength ID.
    """

    serializer_class = StrengthSerializer
    queryset = Strength.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve strength by Strength ID.
        :param request:
        :param pk:
        :return:
        """

        queryset = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update strength by Strength ID.
        :param request:
        :param pk:
        :return:
        """

        strength = get_object_or_404(Strength, pk=pk)

        # check if the user is the owner of the CV
        if strength.cv.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(strength, data=request.data, partial=True)
        strength.strength_name = request.data.get('strength_name', strength.strength_name)

        if serializer.is_valid():
            strength.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete strength by Strength ID.
        :param request: ,nb
        :param pk:
        :return:
        """

        strength = get_object_or_404(Strength, pk=pk)

        # check if the user is the owner of the CV
        if strength.cv.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            # delete the strength object from the cv object
            strength.delete()
            return Response({'message': 'Strength deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
