from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.cv_template_list.serializers import CvTemplateListSerializer
from cvbuilder.models import CvTemplateList
from util.Storage.process_image import convert_image_webp, check_image_size
from util.Storage.s3_function import delete_s3_file


@extend_schema(tags=['CV Template List'])
class CVTemplateListViewSet(APIView):
    """Manage CV Template List in the database"""

    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = CvTemplateListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = CvTemplateList.objects.all()

    @staticmethod
    def get(request):
        """
        Retrieve all CV Templates
        """

        cv_templates = CvTemplateList.objects.all()
        serializer = CvTemplateListSerializer(cv_templates, many=True)
        return Response({'cv_templates': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new CV Template
        """

        user = self.request.user
        self.serializer_class(data=request.data)

        if user.is_superuser:
            if CvTemplateList.objects.filter(template_name=request.data.get('template_name')).exists():
                return Response({'error': 'Template already exists'}, status=status.HTTP_400_BAD_REQUEST)

        cv_template_thumbnail = request.data.get('cv_template_thumbnail')

        # check if cv_template_thumbnail is less than 1240x1754, if yes return error
        if cv_template_thumbnail.width > 1240 or cv_template_thumbnail.height > 1754:
            return Response({'error': 'Image must be less than 1240x1754'}, status=status.HTTP_400_BAD_REQUEST)

        # process thumbnail to webp
        cv_template_thumbnail = convert_image_webp(cv_template_thumbnail)

        # check the filesize
        cv_template_thumbnail = check_image_size(cv_template_thumbnail)

        CvTemplateList.objects.create(
            user=user,
            cv_template_name=request.data.get('cv_template_name'),
            cv_template_profession=request.data.get('cv_template_profession'),
            cv_template_thumbnail=cv_template_thumbnail,
            cv_template_thumbnail_small=request.data.get('cv_template_small_thumbnail'),
        )

        return Response({'message': 'Template created successfully'}, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        """

        """

        user = self.request.user
        if user.is_superuser:
            if CvTemplateList.objects.filter(template_name=request.data.get('template_name')).exists():
                return Response({'error': 'Template already exists'}, status=status.HTTP_400_BAD_REQUEST)

            cv_template = CvTemplateList.objects.get(pk=pk)

            # check if cv template already exists
            if CvTemplateList.objects.filter(cv_template_name=request.data.get('cv_template_name')).exists():
                delete_s3_file(cv_template.cv_template_thumbnail)
                delete_s3_file(cv_template.cv_template_thumbnail_small)

                cv_template.cv_template_thumbnail = None
                cv_template.cv_template_thumbnail_small = None
                cv_template.save()

            cv_template_thumbnail = request.data.get('cv_template_thumbnail')

            # check if cv_template_thumbnail is less than 1240x1754, if yes return error
            if cv_template_thumbnail.width > 1240 or cv_template_thumbnail.height > 1754:
                return Response({'error': 'Image must be less than 1240x1754'}, status=status.HTTP_400_BAD_REQUEST)

            # process thumbnail to webp
            cv_template_thumbnail = convert_image_webp(cv_template_thumbnail)

            # check the filesize
            cv_template_thumbnail = check_image_size(cv_template_thumbnail)

            serializer = self.serializer_class(cv_template, data=request.data, partial=True)

            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'message': 'Template updated successfully'}, status=status.HTTP_200_OK)

            except ValidationError as e:
                return Response({'error': 'Template not updated. Reason: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'error': 'You are not allowed to update cv template'}, status=status.HTTP_403_FORBIDDEN)

    @transaction.atomic
    def delete(self, request, pk):
        """
        Delete a CV Template

        """

        user = self.request.user

        if user.is_superuser:
            cv_template = CvTemplateList.objects.get(pk=pk)
            delete_s3_file(cv_template.cv_template_thumbnail)
            delete_s3_file(cv_template.cv_template_thumbnail_small)
            cv_template.delete()
            return Response({'message': 'Template deleted successfully'}, status=status.HTTP_200_OK)

        else:
            return Response({'error': 'You are not allowed to delete cv template'}, status=status.HTTP_403_FORBIDDEN)
