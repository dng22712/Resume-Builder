from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.language.serializers import LanguageSerializer
from cvbuilder.models import Language, CvBuilder
from util.payments.user_payment_checks import premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'


# ---------------Language by CV ID----------------
@extend_schema(tags=['CV Builder: Language'])
class LanguageByCvId(APIView):
    """
    Retrieve, update, or delete a language by CV ID.
    """

    serializer_class = LanguageSerializer
    queryset = Language.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve a language by CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - Language entry associated with the CV ID.
        """

        cv = get_object_or_404(CvBuilder, pk=pk)
        serializer = self.serializer_class(cv)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @premium_required
    def post(self, request, pk=None):
        """
        Update a language by CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 200 OK if the language is updated successfully.
        """

        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(cv, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete a language by CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 204 NO CONTENT if the language is deleted successfully.
        """

        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            Language.objects.filter(cv=pk).delete()
            return Response({'message': 'Language deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)


# ---------------Language by Language ID----------------
@extend_schema(tags=['CV Builder: Language'])
class LanguageById(APIView):
    """
    Retrieve, update, or delete a language by language ID.
    """

    serializer_class = LanguageSerializer
    queryset = Language.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve a language by language ID.

        Parameters:
        - request: Request object.
        - pk: Language ID.

        Returns:
        - Language entry associated with the language ID.
        """

        language = get_object_or_404(Language, pk=pk) # get the language object
        serializer = self.serializer_class(language)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update a language by providing its ID.

        Parameters:
        - request: Request object.
        - pk: Language ID.

        Returns:
        - HTTP 200 OK if the language is updated successfully.
        """

        language = get_object_or_404(Language, pk=pk) # get the language object
        user = request.user

        # check if the user is the owner of the language
        if language.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(language, data=request.data)

        language.language_name = request.data.get('language_name', language.language_name)
        language.proficiency = request.data.get('proficiency', language.proficiency)

        if serializer.is_valid():
            language.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete a language by providing its ID.

        Parameters:
        - request: Request object.
        - pk: Language ID.

        Returns:
        - HTTP 204 NO CONTENT if the language is deleted successfully.
        """

        language = get_object_or_404(Language, pk=pk) # get the language object

        # check if the user is the owner of the language
        if language.cv.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            language.delete()
            return Response({'message': 'Language deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)

