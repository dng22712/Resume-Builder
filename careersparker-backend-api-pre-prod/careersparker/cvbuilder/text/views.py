from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.models import TextSection, CvBuilder
from cvbuilder.text.serializers import TextSerializer
from util.payments.user_payment_checks import premium_required


# -------------Text by CV ID View----------------
@extend_schema(tags=['CV: Text'])
class TextByCvId(APIView):
    """
    Retrieve text by CV ID.
    """

    serializer_class = TextSerializer
    queryset = TextSection.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve text by CV ID.
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
        post text by CV ID.
        :param request:
        :param pk:
        :return:
        """

        cv = get_object_or_404(CvBuilder, pk=pk)

        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(cv=cv)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """
        delete text by CV ID.
        :param request:
        :param pk:
        :return:
        """

        cv = get_object_or_404(CvBuilder, pk=pk)

        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        queryset = get_object_or_404(self.queryset, cv=pk)
        queryset.delete()
        return Response({'message': 'Text deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# -------------Text by Text ID View----------------
@extend_schema(tags=['CV: Text'])
class TextById(APIView):
    """
    Retrieve text by text ID.
    """

    serializer_class = TextSerializer
    queryset = TextSection.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve text by text ID.
        :param request:
        :param pk:
        :return:
        """

        text = get_object_or_404(TextSection, pk=pk)
        serializer = self.serializer_class(text)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update text by text ID.
        :param request:
        :param pk:
        :return:
        """

        text = get_object_or_404(TextSection, pk=pk)

        # check if the user is the owner of the text
        if text.cv.user != request.user:
            return Response({'message': 'You are not authorized to update this text'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(text, data=request.data, partial=True)

        text.text_section_header_title = request.data.get('text_section_header_title', text.text_section_header_title)
        text.text_section_description = request.data.get('text_section_description', text.text_section_description)

        if serializer.is_valid():
            text.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        delete text by text ID.
        :param request:
        :param pk:
        :return:
        """

        text = get_object_or_404(TextSection, pk=pk)

        # check if the user is the owner of the text
        if text.cv.user != request.user:
            return Response({'message': 'You are not authorized to delete this text'},
                            status=status.HTTP_400_BAD_REQUEST)

        text.delete()
        return Response({'message': 'Text deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
