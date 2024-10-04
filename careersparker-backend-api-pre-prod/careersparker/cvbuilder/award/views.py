from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.award.serializers import AwardSerializer
from cvbuilder.models import Award, CvBuilder
from util.payments.user_payment_checks import premium_required


# ------------------Award by CV ID------------------
@extend_schema(tags=['CV: Award'])
class AwardByCvId(APIView):
    """
    Retrieve, create, or delete an award by CV ID.

    """

    serializer_class = AwardSerializer
    queryset = Award.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve all award entries associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - Award entries associated with the CV ID.
        """
        queryset = self.queryset.filter(cv=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'awards': serializer.data}, status=status.HTTP_200_OK)

    @premium_required
    def post(self, request, pk=None):
        """
        Create a new award entry associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 201 CREATED if the award entry is created successfully.
        """

        cv = get_object_or_404(CvBuilder, pk=pk)
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)


        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(cv=cv)
        return Response({'message': 'Award created successfully'}, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete all award entries associated with a CV by providing the CV ID.
        :param request:
        :param pk:
        :return:
        """

        cv = get_object_or_404(CvBuilder, pk=pk)
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)

        try:
            Award.objects.filter(cv=pk).delete()
            return Response({'message': 'Award deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ------------------Award by award ID------------------
@extend_schema(tags=['CV: Award'])
class AwardById(APIView):
    """
    Retrieve, update, or delete an award entry by its award ID.

    """

    serializer_class = AwardSerializer
    queryset = Award.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve an award entry by providing its ID.

        Parameters:
        - request: Request object.
        - pk: Award ID.

        Returns:
        - Award entry associated with the ID.
        """
        award = get_object_or_404(Award, pk=pk)
        serializer = self.serializer_class(award)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @premium_required
    def patch(self, request, pk=None):
        """
        Update an award entry by providing its ID.

        Parameters:
        - request: Request object.
        - pk: Award ID.

        Returns:
        - HTTP 200 OK if the award entry is updated successfully.
        - HTTP 404 NOT FOUND if the specified award does not exist.
        - HTTP 400 BAD REQUEST if the user attempts to update another user's award.
        """
        user = request.user

        # get the award by id
        try:
            award = get_object_or_404(Award, pk=pk)

        except Award.DoesNotExist:
            return Response({'message': 'Award does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # prevents user from updating other users award
        if user != award.cv.user:
            return Response({'message': 'You are not authorized to update this award'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(award, data=request.data)

        award.award_title = request.data.get('award_title', award.award_title)
        award.award_description = request.data.get('award_description', award.award_description)
        award.award_date = request.data.get('award_date', award.award_date)
        award.award_url = request.data.get('award_url', award.award_url)
        award.award_issuer = request.data.get('award_issuer', award.award_issuer)
        serializer.is_valid(raise_exception=True)
        award.save()
        return Response({'message': 'Award updated successfully'}, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete an award entry by providing its ID.

        Parameters:
        - request: Request object.
        - pk: Award ID.

        Returns:
        - HTTP 200 OK if the award entry is deleted successfully.
        - HTTP 404 NOT FOUND if the specified award does not exist.
        - HTTP 400 BAD REQUEST if the user attempts to delete another user's award.
        """
        user = request.user

        award = get_object_or_404(Award, pk=pk)

        # prevents user from deleting other users award
        if user != award.cv.user:
            return Response({'message': 'You are not authorized to delete this award'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            award.delete()
            return Response({'message': 'Award deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

