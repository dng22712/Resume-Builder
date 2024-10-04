from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.custom_section.serializers import CustomSectionSerializer
from cvbuilder.models import CustomSection
from util.payments.user_payment_checks import prevent_free_user, premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'  # error message


# ------------Custom Section by CV ID----------------
@extend_schema(tags=['CV: Custom Section'])
class CustomSectionyCvId(APIView):
    """

    """

    queryset = CustomSection.objects.all()
    serializer_class = CustomSectionSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve custom section by CV ID.
        :param request:
        :param pk:
        :return:
        """
        queryset = get_object_or_404(self.queryset, cv=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @premium_required
    def post(self, request, pk=None):
        """
        post custom section by CV ID.
        :param request:
        :param pk:
        :return:
        """
        cv = get_object_or_404(CustomSection, pk=pk)  # get the CV object
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
        Delete custom section by CV ID.
        :param request:
        :param pk:
        :return:
        """
        cv = get_object_or_404(CustomSection, pk=pk)
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            CustomSection.objects.filter(cv=pk).delete()
            return Response({'message': 'Custom section deleted successfully'}, status=status.HTTP_200_OK)
        except CustomSection.DoesNotExist:
            return Response({'message': 'Custom section not found'}, status=status.HTTP_404_NOT_FOUND)


# ----------------Custom Section by Section ID----------------
@extend_schema(tags=['CV: Custom Section'])
class CustomSectionById(APIView):
    """

    """

    serializer_class = CustomSectionSerializer
    queryset = CustomSection.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve custom section by section ID.
        :param request:
        :param pk:
        :return:
        """
        queryset = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update custom section by section ID.
        :param request:
        :param pk:
        :return:
        """
        custom_section = get_object_or_404(CustomSection, pk=pk)
        user = request.user

        # check if the user is the owner of the CV
        if custom_section.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(custom_section, data=request.data)
        custom_section.custom_section_header_title = request.data.get('custom_section_header_title',
                                                                      custom_section.custom_section_header_title)
        custom_section.title = request.data.get('title', custom_section.title)
        custom_section.description = request.data.get('description', custom_section.description)
        custom_section.city = request.data.get('city', custom_section.city)
        custom_section.country = request.data.get('country', custom_section.country)
        custom_section.start_date = request.data.get('start_date', custom_section.start_date)
        custom_section.end_date = request.data.get('end_date', custom_section.end_date)
        custom_section.currently_here = request.data.get('is_current', custom_section.currently_here)

        if serializer.is_valid():
            custom_section.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete custom section by section ID.
        :param request:
        :param pk:
        :return:
        """
        custom_section = get_object_or_404(CustomSection, pk=pk)
        user = request.user

        # check if the user is the owner of the CV
        if custom_section.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            custom_section.delete()
            return Response({'message': 'Custom section deleted successfully'}, status=status.HTTP_200_OK)
        except CustomSection.DoesNotExist:
            return Response({'message': 'Custom section not found'}, status=status.HTTP_404_NOT_FOUND)
