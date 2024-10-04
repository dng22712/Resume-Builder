from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.internship.serializers import InternshipSerializer
from cvbuilder.models import Internship, CvBuilder
from util.payments.user_payment_checks import premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'


# ----------Internship By CV ID----------------
@extend_schema(tags=['CV: Internship'])
class InternshipByCvId(APIView):
    """
    Retrieve, create, or delete an internship by CV ID.

    """

    serializer_class = InternshipSerializer
    queryset = Internship.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve all internship entries associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - Internship entries associated with the CV ID.
        """
        queryset = self.queryset.filter(cv=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'internships': serializer.data}, status=status.HTTP_200_OK)

    @premium_required
    def post(self, request, pk=None):
        """
        Create a new internship entry associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 201 CREATED if the internship entry is created successfully.
        """

        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'error': ERROR_MESSAGE}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(cv=cv)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete an internship entry by providing the internship ID.

        Parameters:
        - request: Request object.
        - pk: Internship ID.

        Returns:
        - HTTP 204 NO CONTENT if the internship entry is deleted successfully.
        """
        internship = get_object_or_404(Internship, pk=pk)
        internship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------Internship By Internship ID----------------
@extend_schema(tags=['CV: Internship'])
class InternshipById(APIView):
    """
    Retrieve, update, or delete an internship by internship ID.

    """

    serializer_class = InternshipSerializer
    queryset = Internship.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve an internship entry by providing the internship ID.

        Parameters:
        - request: Request object.
        - pk: Internship ID.

        Returns:
        - Internship entry by the internship ID.
        """
        internship = get_object_or_404(Internship, pk=pk)
        serializer = self.serializer_class(internship)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update an internship entry by providing the internship ID.

        Parameters:
        - request: Request object.
        - pk: Internship ID.

        Returns:
        - HTTP 200 OK if the internship entry is updated successfully.
        """
        internship = get_object_or_404(Internship, pk=pk)  # get the internship object
        user = request.user

        # check if the user is the owner of the internship
        if internship.cv.user != user:
            return Response({'error': ERROR_MESSAGE}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(internship, data=request.data)

        internship.internship_name = request.data.get('internship_name', internship.internship_name)
        internship.internship_company = request.data.get('internship_company', internship.internship_company)
        internship.internship_city = request.data.get('internship_city', internship.internship_city)
        internship.internship_country = request.data.get('internship_country', internship.internship_country)
        internship.internship_start_date = request.data.get('internship_start_date', internship.internship_start_date)
        internship.internship_end_date = request.data.get('internship_end_date', internship.internship_end_date)
        internship.internship_description = request.data.get('internship_description',
                                                             internship.internship_description)
        internship.currently_interning_here = request.data.get('currently_interning_here',
                                                               internship.currently_interning_here)

        if serializer.is_valid():
            internship.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete an internship entry by providing the internship ID.

        Parameters:
        - request: Request object.
        - pk: Internship ID.

        Returns:
        - HTTP 204 NO CONTENT if the internship entry is deleted successfully.
        """
        internship = get_object_or_404(Internship, pk=pk)  # get the internship object

        # check if the user is the owner of the internship
        if internship.cv.user != request.user:
            return Response({'error': ERROR_MESSAGE}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            internship.delete()
            return Response({'message': 'Internship deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
