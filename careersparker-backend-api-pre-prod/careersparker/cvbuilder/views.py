import uuid

from autoslug.utils import slugify
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, generics, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder import serializers
from cvbuilder.models import CvBuilder
from cvbuilder.serializers import CvBuilderSerializer
from util.payments.user_payment_checks import can_create_cv, can_download_worddoc, can_download_cv_pdf

COMMON_ERROR_MESSAGE = 'You are not the owner of this cv'


@extend_schema(tags=['CV'])
class CvBuilderViewset(mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
                       generics.CreateAPIView):
    """

    """

    authentication_classes = [JWTAuthentication]  # JWT Authentication
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = CvBuilder.objects.all()
    serializer_class = serializers.CvBuilderSerializer

    def get_queryset(self):  # get the cv builder for the authenticated user
        """

        """
        return CvBuilder.objects.order_by('-created_at').filter(user=self.request.user)

    # create cv builder
    def create(self, request, *args, **kwargs):
        """

        """
        user = self.request.user
        serializer = self.get_serializer(data=request.data)

        # get cv builder payment status, if the user has paid for cv builder
        # then allow user to create cv builder from the cv builder model

        check_user_has_paid = can_create_cv(user)
        if not check_user_has_paid:
            return Response({'error': 'Insufficient credits to create a CV.'}, status=status.HTTP_400_BAD_REQUEST)

        # create cv builder
        if serializer.is_valid():
            serializer.save(user=user)

            # check if cv builder is created successfully
            if serializer.instance:
                user.deduct_cv_create_count()  # deduct cv create count
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # delete cv builder
    def destroy(self, request, *args, **kwargs):
        """

        """
        print("HERE")
        cv_builder = self.get_object()
        print("rtrfggf", cv_builder)
        cv_builder.delete()
        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=['CV'])
class CvBuilderUpdate(APIView):
    """

    """

    queryset = CvBuilder.objects.all()
    serializer_class = serializers.CvBuilderSerializer
    authentication_classes = [JWTAuthentication]  # JWT Authentication
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @staticmethod
    def get(pk):
        """

        """
        cvbuilder = CvBuilder.objects.get(id=pk)
        serializer = CvBuilderSerializer(cvbuilder)
        return Response(serializer.data)

    def patch(self, request, pk):
        """

        """
        try:
            user = self.request.user
            cvbuilder = get_object_or_404(CvBuilder.objects.filter(user=user, id=pk))
        except CvBuilder.DoesNotExist:
            return Response({'error': 'CV not found'}, status=status.HTTP_404_NOT_FOUND)

        if cvbuilder.user != user:
            return Response({'error': 'You are not the owner of this cv'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CvBuilderSerializer(cvbuilder, data=request.data, partial=True)
        cvbuilder.cv_title = request.data.get('cv_title', cvbuilder.cv_title)

        # make sure the cv_slug is unique

        if cvbuilder.cv_title is None:
            return Response({'error': 'Please enter a CV title'}, status=status.HTTP_400_BAD_REQUEST)
        counter = 1
        new_slug = slugify(cvbuilder.cv_title)
        while CvBuilder.objects.filter(cv_slug=new_slug).exists():
            new_slug = f"{slugify(cvbuilder.cv_title)}-{counter}"
            counter += 1
        cvbuilder.cv_slug = new_slug

        if serializer.is_valid():
            serializer.save(cv_slug=cvbuilder.cv_slug)

            return Response(status=status.HTTP_200_OK, data={'success': 'CV updated successfully'})

        print(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------------------------
# Change cv template
# ---------------------------------------------------------------------------------------------
@extend_schema(tags=['CV'])
class CvTemplateChange(APIView):
    """

    """

    queryset = CvBuilder.objects.all()
    serializer_class = serializers.CvBuilderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @staticmethod
    def get_object(pk):
        """

        """
        cvbuilder = CvBuilder.objects.get(id=pk)
        serializer = CvBuilderSerializer(cvbuilder)
        return Response(serializer.data)

    def patch(self, request, pk):
        """

        """
        user = self.request.user
        cvbuilder = get_object_or_404(CvBuilder.objects.filter(user=user, id=pk))

        # check if user is the owner of the cv builder
        if cvbuilder.user != user:
            return Response({'error': COMMON_ERROR_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

        # check if user has paid for cv template
        can_create_template = can_create_cv(user)
        if not can_create_template:
            return Response({'error': 'Insufficient credits to change CV template'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = CvBuilderSerializer(cvbuilder, data=request.data, partial=True)

        cvbuilder.cv_template_selected = request.data('cv_template_selected', cvbuilder.cv_template_selected)

        # set the cv template to default if user.is_free = True
        if user.is_free:
            cvbuilder.cv_template_selected = 'default'

        if serializer.is_valid():
            serializer.save()

            # update the cv_template_count if cv template is changed successfully
            if serializer.instance:
                # call deduct_cv_template_count method to deduct the cv template count
                user.deduct_cv_template_count()
            return Response(status=status.HTTP_200_OK, data={'success': 'CV template changed successfully'})


# ---------------------------------------------------------------------------------------------
# Download cv as word document
# ---------------------------------------------------------------------------------------------

@extend_schema(tags=['CV'])
class CvWordDownload(APIView):
    """

    """

    queryset = CvBuilder.objects.all()
    serializer_class = serializers.CvBuilderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @staticmethod
    def get_object(pk):
        """

        """
        cvbuilder = CvBuilder.objects.get(id=pk)
        serializer = CvBuilderSerializer(cvbuilder)
        return Response(serializer.data)

    def get(self, request, pk):
        """

        """
        user = self.request.user
        cvbuilder = get_object_or_404(CvBuilder.objects.filter(user=user, id=pk))
        # check if user is the owner of the cv builder
        if cvbuilder.user != user:
            return Response({'error': 'You are not the owner of this cv builder'}, status=status.HTTP_400_BAD_REQUEST)

        # check if user can download the cv using can_download_cv method
        can_download_word = can_download_worddoc(user)
        if not can_download_word:
            return Response({'error': 'You have reached your limit of cv Word download'},
                            status=status.HTTP_400_BAD_REQUEST)

        # UPDATE  WORD DOWNLOAD COUNT
        user.deduct_word_download_count()
        return Response(status=status.HTTP_200_OK, data={'success': 'CV Word Document downloaded successfully'})


# ---------------------------------------------------------------------------------------------
# Download cv as pdf document
# ---------------------------------------------------------------------------------------------

@extend_schema(tags=['CV'])
class CvPdfDownload(APIView):
    """

    """

    queryset = CvBuilder.objects.all()
    serializer_class = serializers.CvBuilderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @staticmethod
    def get_object(pk):
        """

        """
        cvbuilder = CvBuilder.objects.get(id=pk)
        serializer = CvBuilderSerializer(cvbuilder)
        return Response(serializer.data)

    def get(self, request, pk):
        """

        """
        user = self.request.user
        cvbuilder = get_object_or_404(CvBuilder.objects.filter(user=user, id=pk))

        # check if user is the owner of the cv builder
        if cvbuilder.user != user:
            return Response({'error': 'You are not the owner of this cv builder'}, status=status.HTTP_400_BAD_REQUEST)

        # check if user can download the cv using can_download_cv method
        can_download_pdf = can_download_cv_pdf(user)
        if not can_download_pdf:
            return Response({'error': 'You have reached your limit of cv download'}, status=status.HTTP_400_BAD_REQUEST)

        # UPDATE THE PDF DOWNLOAD COUNT
        user.deduct_pdf_download_count()
        return Response(status=status.HTTP_200_OK, data={'success': 'CV PDF Document downloaded successfully'})
