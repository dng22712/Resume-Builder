from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.hobby.serializers import HobbySerializer
from cvbuilder.models import Hobby, CvBuilder
from util.payments.user_payment_checks import premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'


# --------------Hobby By CV ID----------------
@extend_schema(tags=['CV: Hobby'])
class HobbyByCvId(APIView):
    """
    Retrieve, create, or delete a hobby by CV ID.

    """

    serializer_class = HobbySerializer
    queryset = Hobby.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve all hobby entries associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - Hobby entries associated with the CV ID.
        """
        queryset = self.queryset.filter(cv=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'hobbies': serializer.data}, status=status.HTTP_200_OK)

    @premium_required
    def post(self, request, pk=None):
        """
        Create a new hobby entry associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 201 CREATED if the hobby entry is created successfully.
        """

        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(cv=cv)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete all hobby entries associated with a CV by providing the CV ID.
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
            Hobby.objects.filter(cv=pk).delete()
            return Response({'message': 'Hobbies deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ------------------Hobby by hobby ID------------------
@extend_schema(tags=['CV: Hobby'])
class HobbyById(APIView):
    """
    Retrieve, update, or delete a hobby by hobby ID.
    """

    serializer_class = HobbySerializer
    queryset = Hobby.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve a hobby entry by its hobby ID.

        Parameters:
        - request: Request object.
        - pk: Hobby ID.

        Returns:
        - Hobby entry associated with the hobby ID.
        """
        queryset = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update a hobby entry by its hobby ID.

        Parameters:
        - request: Request object.
        - pk: Hobby ID.

        Returns:
        - HTTP 200 OK if the hobby entry is updated successfully.
        """
        hobby = get_object_or_404(Hobby, pk=pk)  # get the hobby object
        user = request.user

        # check if the user is the owner of the hobby
        if hobby.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(hobby, data=request.data)

        hobby.hobby_name = request.data.get('hobby_name', hobby.hobby_name)
        hobby.hobby_icon_value = request.data.get('hobby_icon_value', hobby.hobby_icon_value)

        if serializer.is_valid():
            hobby.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete a hobby entry by its hobby ID.

        Parameters:
        - request: Request object.
        - pk: Hobby ID.

        Returns:
        - HTTP 204 NO CONTENT if the hobby entry is deleted successfully.
        """
        hobby = get_object_or_404(Hobby, pk=pk)  # get the hobby object

        # check if user is the owner of the hobby
        if hobby.cv.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            hobby.delete()
            return Response({'message': 'Hobby deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
