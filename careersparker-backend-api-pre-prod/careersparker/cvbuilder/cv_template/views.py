from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.cv_template import serializers
from cvbuilder.cv_template.serializers import CvTemplateSerializer
from cvbuilder.models import CvTemplate, CvBuilder, CvTemplateList

from util.payments.user_payment_checks import can_create_template


@extend_schema(tags=['CV: Template'])
class TemplateByCvId(APIView):
    """
    Retrieve, create, or delete a template by CV ID.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = CvTemplate.objects.all()
    serializer_class = serializers.CvTemplateSerializer

    def get(self, request, pk):
        """
        Retrieve a template by CV ID.
        """
        try:
            queryset = self.queryset.get(cv=pk).order_by('-template_name')
            serializer = self.serializer_class(queryset)
            return Response({'template': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': 'Template not found. Reason: ' + str(e)})

    def post(self, request, pk):
        """
        Create a template by CV ID.

        """

        user = self.request.user

        cv = get_object_or_404(CvBuilder, pk=pk)

        # get cv builder fixed payment permission

        check_user_has_paid = can_create_template(user)
        if not check_user_has_paid:
            return Response({'error': 'You do not have permission to create a template'},
                            status=status.HTTP_403_FORBIDDEN)

        cv_template_name = request.data.get("cv_template_name")

        # set template to default if user is free
        if user.is_free and user.cv_template_count <= 0:
            cv_template_name = 'default'
            # TODO: Add a message to notify the user that the template is set to default

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save(cv=cv, cv_template_name=cv_template_name)

            # check if template is created successfully
            if serializer.instance:
                user.deduct_cv_template_count()
                # user.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['CV: Template'])
class TemplateById(APIView):
    """

    """
    serializer_class = CvTemplateSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    @staticmethod
    def get(self, request, pk):
        """
        Retrieve a template by ID.
        """
        queryset = self.queryset.filter(cv=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'cv-template': serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """

        :param request:
        :param pk:
        :return:
        """

        cv_template = get_object_or_404(CvTemplate, pk=pk)
        user = request.user

        # check the user is the owner of the template
        if cv_template.user != user:
            return Response({'message': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        check_user_has_paid = can_create_template(user)
        if not check_user_has_paid:
            return Response({'error': 'Insufficient credits to create a template.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(cv_template, data=request.data, partial=True)

        cv_template_name = request.data.get("cv_template_name")

        # set template to default if user is free
        if user.is_free:
            cv_template_name = 'default'

        if serializer.is_valid(raise_exception=True):
            serializer.save(cv_template_name=cv_template_name)
            return Response({'message': 'CV Template updated successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
