from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.models import Volunteering, CvBuilder
from cvbuilder.volunteering.serializers import VolunteeringSerializer
from util.payments.user_payment_checks import premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'


# -------------Volunteering By CV ID----------------
@extend_schema(tags=['CV: Volunteering'])
class VolunteeringByCvId(APIView):
    """
    Retrieve all volunteering entries associated with a CV.
    """

    serializer_class = VolunteeringSerializer
    queryset = Volunteering.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve all volunteering entries associated with a CV by providing the CV ID.
        :param request:
        :param pk:
        :return:
        """

        queryset = self.queryset.filter(cv=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @premium_required
    def post(self, request, pk=None):
        """
        Create a new volunteering entry associated with a CV by providing the CV ID.
        :param request:
        :param pk:
        :return:
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
        Delete a volunteering entry by providing the CV ID and the volunteering ID.
        :param request:
        :param pk:
        :return:
        """

        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object

        # check if the user is the owner of the CV
        if cv.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            Volunteering.objects.get(cv_id=pk, id=request.data['id']).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Volunteering.DoesNotExist:
            return Response({'message': 'Volunteering entry not found'}, status=status.HTTP_404_NOT_FOUND)


# -------------Volunteering By Volunteering ID----------------
@extend_schema(tags=['CV: Volunteering'])
class VolunteeringById(APIView):
    """
    Retrieve a volunteering entry by providing the CV ID and the volunteering ID.
    """

    serializer_class = VolunteeringSerializer
    queryset = Volunteering.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve a volunteering entry by providing the CV ID and the volunteering ID.
        :param request:
        :param pk:
        :return:
        """

        queryset = get_object_or_404(self.queryset, cv=pk, id=request.data['id'])
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update a volunteering entry by providing the CV ID and the volunteering ID.
        :param request:
        :param pk:
        :return:
        """

        volunteering = get_object_or_404(self.queryset, cv=pk, id=request.data['id'])
        user = request.user

        # check if the user is the owner of the CV
        if volunteering.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(volunteering, data=request.data, partial=True)

        volunteering.role = request.data.get('role', volunteering.role)
        volunteering.organization_name = request.data.get('organization', volunteering.organization)
        volunteering.city = request.data.get('city', volunteering.city)
        volunteering.country = request.data.get('country', volunteering.country)
        volunteering.start_date = request.data.get('start_date', volunteering.start_date)
        volunteering.end_date = request.data.get('end_date', volunteering.end_date)
        volunteering.currently_volunteering = request.data.get('currently_volunteering',
                                                               volunteering.currently_volunteering)
        volunteering.description = request.data.get('description', volunteering.description)

        if serializer.is_valid():
            volunteering.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """
        Delete a volunteering entry by providing the CV ID and the volunteering ID.
        :param request:
        :param pk:
        :return:
        """

        volunteering = get_object_or_404(self.queryset, cv=pk, id=request.data['id'])
        user = request.user

        # check if the user is the owner of the CV
        if volunteering.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        volunteering.delete()
        return Response({'message': 'Volunteering entry deleted successfully'}, status=status.HTTP_200_OK)
