from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from cvbuilder.employment_history import serializers
from cvbuilder.models import EmploymentHistory, CvBuilder


# ----------------------Employment History by CV ID----------------------
@extend_schema(tags=['CV: Employment History'])
class EmploymentHistoryByCvId(APIView):
    """`
    **This module provides views to manage CV employment history in the database.**

    *Endpoints:*

    - GET: Retrieve employment history by CV builder ID
    - POST: Create a new employment history by CV builder ID

    *Endpoint details:*

        - GET:
            - Parameters:

                - request: Request object containing metadata about the request
                - pk: CV builder ID for which employment history needs to be retrieved
            - Returns:

                - Returns employment history by CV builder ID
            - Raises:

                - Returns HTTP 400 BAD REQUEST if an exception occurs during retrieval

        - POST:

            - Parameters:

                - request: Request object containing employment history data
                - pk: CV builder ID for which employment history needs to be created
            - Returns:

                - Creates a new employment history by CV builder ID
            - Raises:

                - Returns HTTP 404 NOT FOUND if the specified user or CV builder does not exist
                - Returns HTTP 400 BAD REQUEST if the user is unauthorized or if the serializer data is invalid
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.EmploymentHistorySerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = EmploymentHistory.objects.all()

    def get(self, request, pk=None):
        """
        Retrieve employment history by CV ID.
        """
        queryset = EmploymentHistory.objects.filter(cv=pk).order_by('-employer_name')
        serializer = self.serializer_class(queryset, many=True)
        try:
            return Response({'employment history': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk=None):
        """
        Create a new employment history entry associated with a CV.
        """
        cv = get_object_or_404(CvBuilder, pk=pk)
        user = request.user

        # check the user is the owner of the CV
        if cv.user != user:
            return Response({'message': 'You are not authorized to perform this action'},
                            status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(cv=cv)
        return Response({'message': 'Employment history created successfully'}, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete employment history by CV ID.
        """
        cv = get_object_or_404(CvBuilder, pk=pk)
        user = request.user

        # check the user is the owner of the CV
        if cv.user != user:
            return Response({'message': 'You are not authorized to perform this action'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            EmploymentHistory.objects.filter(cv=pk).delete()
            return Response({'message': 'Employment history deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------------
# Employment History by employment history ID
# -------------------------------------------------------------------

@extend_schema(tags=['CV: Employment History'])
class EmploymentHistoryById(APIView):
    """
    Retrieve, update, or delete an employment history entry by its employment history id.

    GET:
    Retrieve an employment history entry by providing its id.

    PATCH:
    Update an employment history entry by providing its id. Only the authorized user can update their own employment history.

    DELETE:
    Delete an employment history entry by providing its id. Only the authorized user can delete their own employment history.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.EmploymentHistorySerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve an employment history entry by its employment history id.
        """
        employment_history = get_object_or_404(EmploymentHistory, pk=pk)
        serializer = self.serializer_class(employment_history)
        return Response({'employment history': serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update an employment history entry by its employment history id.
        """
        employment_history = get_object_or_404(EmploymentHistory, pk=pk)
        user = request.user

        # check if the user is the owner of the employment history
        if employment_history.user != user:
            return Response({'message': 'You are not authorized to update this employment history'},
                            status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(employment_history, data=request.data, partial=True)
        employment_history.job_title = request.data.get('job_title', employment_history.job_title)
        employment_history.employer_name = request.data.get('employer_name', employment_history.employer_name)
        employment_history.employer_city = request.data.get('employer_city', employment_history.employer_city)
        employment_history.employer_country = request.data.get('employer_country', employment_history.employer_country)
        employment_history.start_date = request.data.get('start_date', employment_history.start_date)
        employment_history.end_date = request.data.get('end_date', employment_history.end_date)
        employment_history.currently_working_here = request.data.get('currently_working_here',
                                                                     employment_history.currently_working_here)
        employment_history.job_description = request.data.get('job_description', employment_history.job_description)

        serializer.is_valid(raise_exception=True)
        employment_history.save()
        return Response({'message': 'Employment history updated successfully'}, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete an employment history entry by its employment history id.
        """
        employment_history = get_object_or_404(EmploymentHistory, pk=pk)
        user = request.user

        # check if the user is the owner of the employment history
        if employment_history.user != user:
            return Response({'message': 'You are not authorized to delete this employment history'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            employment_history.delete()
            return Response({'message': 'Employment history deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
