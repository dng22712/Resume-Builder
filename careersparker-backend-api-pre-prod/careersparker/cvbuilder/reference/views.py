from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.models import Reference, CvBuilder
from cvbuilder.reference.serializers import ReferenceSerializer
from util.payments.user_payment_checks import premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'


# ----------Reference by CV ID----------
@extend_schema(tags=['CV: Reference'])
class ReferenceByCvId(APIView):
    """
    Retrieve all references associated with a CV ID.
    """

    serializer_class = ReferenceSerializer
    queryset = Reference.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve all reference entries associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - Reference entries associated with the CV ID.
        """
        queryset = self.queryset.filter(cv=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'references': serializer.data}, status=status.HTTP_200_OK)

    @premium_required
    def post(self, request, pk=None):
        """
        Create a new reference entry associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 201 CREATED if the reference entry is created successfully.
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

    @staticmethod
    def delete(request, pk=None):
        """
        Delete a reference entry by providing the reference ID.

        Parameters:
        - request: Request object.
        - pk: Reference ID.

        Returns:
        - HTTP 204 NO CONTENT if the reference entry is deleted successfully.
        """
        reference = get_object_or_404(Reference, pk=pk)  # get the reference object
        user = request.user

        # check if the user is the owner of the reference
        if reference.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            reference.delete()
            return Response({'message': 'Reference deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ----------Reference by reference ID----------

@extend_schema(tags=['CV: Reference'])
class ReferenceById(APIView):
    """
    Retrieve a reference entry by providing the reference ID.

    """

    serializer_class = ReferenceSerializer
    queryset = Reference.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve a reference entry by providing the reference ID.

        Parameters:
        - request: Request object.
        - pk: Reference ID.

        Returns:
        - Reference entry associated with the reference ID.
        """
        reference = get_object_or_404(Reference, pk=pk)
        serializer = self.serializer_class(reference)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update a reference entry by providing the reference ID.

        Parameters:
        - request: Request object.
        - pk: Reference ID.

        Returns:
        - HTTP 200 OK if the reference entry is updated successfully.
        """
        reference = get_object_or_404(Reference, pk=pk)
        user = request.user

        # check if the user is the owner of the reference
        if reference.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(reference, data=request.data)

        reference.reference_name = request.data.get('reference_name', reference.reference_name)
        reference.reference_position = request.data.get('reference_position', reference.reference_position)
        reference.reference_company = request.data.get('reference_company', reference.reference_company)
        reference.reference_email = request.data.get('reference_email', reference.reference_email)
        reference.reference_phone = request.data.get('reference_phone', reference.reference_phone)
        reference.reference_relationship = request.data.get('reference_relationship', reference.reference_relationship)

        if serializer.is_valid():
            reference.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete a reference entry by providing the reference ID.

        Parameters:
        - request: Request object.
        - pk: Reference ID.

        Returns:
        - HTTP 204 NO CONTENT if the reference entry is deleted successfully.
        """
        reference = get_object_or_404(Reference, pk=pk) # get the reference object

        # check if user is the owner of the reference
        if reference.cv.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            reference.delete()
            return Response({'message': 'Reference deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)



