from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.education.serializers import CvEducationSerializer
from cvbuilder.models import Education, CvBuilder


# ----------------------Education History by CV ID----------------------
@extend_schema(tags=['CV: Education'])
class EducationByCvId(APIView):
    """
    Retrieve, update, or delete education entries by CV ID.

    GET:
    Retrieve all education entries associated with a CV by providing the CV ID.

    POST:
    Create a new education entry associated with a CV by providing the CV ID.

    DELETE:
    Delete all education entries associated with a CV by providing the CV ID.
    """

    serializer_class = CvEducationSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = Education.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk=None):
        """
        Retrieve all education entries associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - Education entries associated with the CV ID.
        """
        queryset = self.queryset.filter(cv=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'education': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, pk=None):
        """
        Create a new education entry associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 201 CREATED if the education entry is created successfully.
        """
        cv = get_object_or_404(CvBuilder, pk=pk)
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(cv=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete all education entries associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 204 NO CONTENT if the education entries are deleted successfully.
        """
        cv = get_object_or_404(CvBuilder, pk=pk)
        user = request.user

        # check the user is the owner of the CV
        if cv.user != user:
            return Response({'message': 'You are not authorized to perform this action'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            Education.objects.filter(cv=pk).delete()
            return Response({'message': 'Education entries deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------------
# Education by education ID
# -------------------------------------------------------------------

@extend_schema(tags=['CV: Education'])
class EducationById(APIView):
    """
    Retrieve, update, or delete an education entry by its education ID.

    GET:
    Retrieve an education entry by providing its ID.

    PUT:
    Update an education entry by providing its ID.

    DELETE:
    Delete an education entry by providing its ID.
    """

    serializer_class = CvEducationSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = Education.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk=None):
        """
        Retrieve an education entry by providing its ID.

        Parameters:
        - request: Request object.
        - pk: Education ID.

        Returns:
        - Education entry associated with the ID.
        """
        education = get_object_or_404(Education, pk=pk)
        serializer = self.serializer_class(education)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update an education entry by providing its ID.

        Parameters:
        - request: Request object.
        - pk: Education ID.

        Returns:
        - HTTP 200 OK if the education entry is updated successfully.
        """

        education = get_object_or_404(Education, pk=pk)
        user = request.user

        # check if the user is the owner of the education
        if education.cv.user != user:
            return Response({'message': 'You are not authorized to update this education'},
                            status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(education, data=request.data, partial=True)
        education.school_name = request.data.get('school_name', education.school_name)
        education.school_city = request.data.get('school_city', education.school_city)
        education.school_country = request.data.get('school_country', education.school_country)
        education.degree = request.data.get('degree', education.degree)
        education.field_of_study = request.data.get('field_of_study', education.field_of_study)
        education.start_date = request.data.get('start_date', education.start_date)
        education.end_date = request.data.get('end_date', education.end_date)
        education.currently_studying_here = request.data.get('currently_studying_here',
                                                             education.currently_studying_here)

        serializer.is_valid(raise_exception=True)
        education.save()
        return Response({'message': 'Education updated successfully'}, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete an education entry by providing its ID.

        Parameters:
        - request: Request object.
        - pk: Education ID.

        Returns:
        - HTTP 204 NO CONTENT if the education entry is deleted successfully.
        """
        education = get_object_or_404(Education, pk=pk)
        user = request.user

        # check if the user is the owner of the education
        if education.cv.user != user:
            return Response({'message': 'You are not authorized to delete this education'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            education.delete()
            return Response({'message': 'Education deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
