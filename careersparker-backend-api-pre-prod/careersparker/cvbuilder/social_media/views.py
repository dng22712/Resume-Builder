from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.models import social_media
from cvbuilder.social_media.serializers import SocialMediaSerializer
from util.payments.user_payment_checks import premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'  # error message`


# -----------Social Media by CV ID------------------#
@extend_schema(tags=['CV: Social Media'])
class SocialMediaByCvId(APIView):
    """
    Retrieve, update, or delete social media by CV ID.
    """

    serializer_class = SocialMediaSerializer
    queryset = social_media.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve social media by CV ID.
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
        post social media by CV ID.
        :param request:
        :param pk:
        :return:
        """

        cv = get_object_or_404(social_media, pk=pk)  # get the CV object
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
        delete social media by CV ID.
        :param request:
        :param pk:
        :return:
        """

        cv = get_object_or_404(social_media, pk=pk)  # get the CV object

        # check if the user is the owner of the CV
        if cv.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            # delete the social media object from the cv object
            cv.delete()
            return Response({'message': 'Social Media deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# -----------Social Media by Social Media ID------------------#
@extend_schema(tags=['CV: Social Media'])
class SocialMediaById(APIView):
    """
    Retrieve, update, or delete social media by Social Media ID.
    """

    serializer_class = SocialMediaSerializer
    queryset = social_media.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve social media by Social Media ID.
        :param request:
        :param pk:
        :return:
        """

        queryset = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update social media by Social Media ID.
        :param request:
        :param pk:
        :return:
        """

        social_medias = get_object_or_404(self.queryset, pk=pk)

        # check if the user is the owner of the CV
        if social_medias.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(social_media, data=request.data, partial=True)
        social_media.social_media_name = request.data.get('social_media_name', social_media.social_media_name)
        social_media.social_media_url = request.data.get('social_media_url', social_media.social_media_url)

        if serializer.is_valid():
            social_medias.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """
        Delete social media by Social Media ID.
        :param request:
        :param pk:
        :return:
        """

        social_medias = get_object_or_404(self.queryset, pk=pk)

        # check if the user is the owner of the CV
        if social_medias.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            # delete the social media object from the cv object
            social_medias.delete()
            return Response({'message': 'Social Media deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
