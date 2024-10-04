from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.models import Publication, CvBuilder
from cvbuilder.publication.serializers import PublicationSerializer
from util.payments.user_payment_checks import premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'


# --------------------Publication by CV ID--------------------
@extend_schema(tags=['CV: Publication'])
class PublicationByCvId(APIView):
    """
    Retrieve, create, or delete a publication by CV ID.

    """

    serializer_class = PublicationSerializer
    queryset = Publication.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve all publication entries associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - Publication entries associated with the CV ID.
        """
        queryset = self.queryset.filter(cv=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'publications': serializer.data}, status=status.HTTP_200_OK)

    @premium_required
    def post(self, request, pk=None):
        """
        Create a new publication entry associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 201 CREATED if the publication entry is created successfully.
        """

        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object
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
        Delete all publication entries associated with a CV by providing the CV ID.
        :param request:
        :param pk:
        :return:
        """
        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        Publication.objects.filter(cv=pk).delete()
        return Response({'message': 'Publications deleted successfully'}, status=status.HTTP_200_OK)


# --------------------Publication by ID--------------------
@extend_schema(tags=['CV: Publication'])
class PublicationById(APIView):
    """
    Retrieve, update, or delete a publication by ID.
    """

    serializer_class = PublicationSerializer
    queryset = Publication.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve a publication by providing its ID.

        Parameters:
        - request: Request object.
        - pk: Publication ID.

        Returns:
        - Publication entry associated with the ID.
        """
        publication = get_object_or_404(Publication, pk=pk)
        serializer = self.serializer_class(publication)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update a publication by providing its ID.

        Parameters:
        - request: Request object.
        - pk: Publication ID.

        Returns:
        - HTTP 200 OK if the publication is updated successfully.
        """
        publication = get_object_or_404(Publication, pk=pk)  # get the publication object
        user = request.user

        # check if the user is the owner of the publication
        if publication.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(publication, data=request.data)

        publication.publication_title = request.data.get('publication_title', publication.publication_title)
        publication.publication_description = request.data.get('publication_description',
                                                               publication.publication_description)
        publication.publication_publisher = request.data.get('publication_publisher', publication.publication_publisher)
        publication.publication_url = request.data.get('publication_url', publication.publication_url)
        publication.publication_date = request.data.get('publication_date', publication.publication_date)

        if serializer.is_valid():
            publication.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete a publication by providing its ID.

        Parameters:
        - request: Request object.
        - pk: Publication ID.

        Returns:
        - HTTP 204 NO CONTENT if the publication is deleted successfully.
        """
        publication = get_object_or_404(Publication, pk=pk)

        # check if the user is the owner of the publication
        if publication.cv.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            publication.delete()
            return Response({'message': 'Publication deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)
