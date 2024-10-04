from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.certificate.serializers import CertificateSerializer
from cvbuilder.models import Certificate, CvBuilder
from util.payments.user_payment_checks import premium_required


# ------------Certificate by CV ID----------------
@extend_schema(tags=['CV: Certificate'])
class CertificateByCvId(APIView):
    """
    Retrieve, create, or delete a certificate by CV ID.

    """

    serializer_class = CertificateSerializer
    queryset = Certificate.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve all certificate entries associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - Certificate entries associated with the CV ID.
        """
        queryset = self.queryset.filter(cv=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'certificates': serializer.data}, status=status.HTTP_200_OK)

    @premium_required
    def post(self, request, pk=None):
        """
        Create a new certificate entry associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 201 CREATED if the certificate entry is created successfully.
        """

        cv = get_object_or_404(CvBuilder, pk=pk) # get the CV object
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

    @staticmethod
    def delete(request, pk=None):
        """
        Delete all certificate entries associated with a CV.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 204 NO CONTENT if the certificate entries are deleted successfully.
        - HTTP 404 NOT FOUND if the specified CV does not exist.
        - HTTP 403 FORBIDDEN if the user is unauthorized to delete the certificate entries.
        """
        user = request.user

        # get the CV by ID
        try:
            cv = get_object_or_404(CvBuilder, pk=pk)

        except CvBuilder.DoesNotExist:
            return Response({'message': 'CV does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # prevent user from deleting other users certificates
        if user != cv.user:
            return Response({'message': 'You are not authorized to delete this certificate'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            Certificate.objects.filter(cv=pk).delete()
            return Response({'message': 'Certificates deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ------------------Certificate by certificate ID------------------
@extend_schema(tags=['CV: Certificate'])
class CertificateById(APIView):
    """
    Retrieve, update, or delete a certificate by certificate ID.

    """

    serializer_class = CertificateSerializer
    queryset = Certificate.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve a certificate entry by providing the certificate ID.

        Parameters:
        - request: Request object.
        - pk: Certificate ID.

        Returns:
        - Certificate entry associated with the certificate ID.
        """
        certificate = get_object_or_404(Certificate, pk=pk)
        serializer = self.serializer_class(certificate)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @premium_required
    def patch(self, request, pk=None):
        """
        Update a certificate entry by providing the certificate ID.

        Parameters:
        - request: Request object.
        - pk: Certificate ID.

        Returns:
        - HTTP 200 OK if the certificate entry is updated successfully.
        - HTTP 404 NOT FOUND if the specified certificate does not exist.
        - HTTP 403 FORBIDDEN if the user is unauthorized to update the certificate entry.
        """
        certificate = get_object_or_404(Certificate, pk=pk)
        user = request.user

        # check if the user is the owner of the certificate
        if certificate.cv.user != user:
            return Response({'message': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(certificate, data=request.data)

        certificate.certificate_title = request.data.get('certificate_title', certificate.certificate_title)
        certificate.certificate_description = request.data.get('institution', certificate.certificate_description)
        certificate.certificate_authority = request.data.get('certificate_authority', certificate.certificate_authority)
        certificate.certificate_url = request.data.get('certificate_url', certificate.certificate_url)
        certificate.certificate_date = request.data.get('date_received', certificate.certificate_date)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete a certificate entry by providing the certificate ID.

        Parameters:
        - request: Request object.
        - pk: Certificate ID.

        Returns:
        - HTTP 204 NO CONTENT if the certificate entry is deleted successfully.
        - HTTP 404 NOT FOUND if the specified certificate does not exist.
        - HTTP 403 FORBIDDEN if the user is unauthorized to delete the certificate entry.
        """
        certificate = get_object_or_404(Certificate, pk=pk)
        user = request.user

        # check if the user is the owner of the certificate
        if certificate.cv.user != user:
            return Response({'message': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            certificate.delete()
            return Response({'message': 'Certificate deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
