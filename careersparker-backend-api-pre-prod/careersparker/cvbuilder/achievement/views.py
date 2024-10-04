from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.achievement.serializers import AchievementSerializer
from cvbuilder.models import Achievement, CvBuilder
from util.payments.user_payment_checks import premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'


@extend_schema(tags=['CV: Achievement'])
class AchievementByCvId(APIView):
    """
    Retrieve, create, or delete an achievement by CV ID.

    """

    serializer_class = AchievementSerializer
    queryset = Achievement.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve all achievement entries associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - Achievement entries associated with the CV ID.
        """
        queryset = self.queryset.filter(cv=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'achievements': serializer.data}, status=status.HTTP_200_OK)

    @premium_required
    def post(self, request, pk=None):
        """
        Create a new achievement entry associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - HTTP 201 CREATED if the achievement entry is created successfully.
        """

        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object
        user = request.user
        print('user', user)

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        # disallow free users from creating achievements
        # if prevent_free_user(user):
        #     return Response(
        #         {'message': 'This is a premium feature. Please upgrade your account to access it.'},
        #         status=status.HTTP_403_FORBIDDEN
        #     )

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(cv=cv)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk):
        """
        Delete all achievement entries associated with a CV by providing the CV ID.
        """

        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            Achievement.objects.filter(cv=pk).delete()
            return Response({'message': 'Achievements deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ------------------Achievement by achievement ID------------------

@extend_schema(tags=['CV: Achievement'])
class AchievementById(APIView):
    """
    Retrieve, update, or delete an achievement by achievement ID.
    """

    serializer_class = AchievementSerializer
    queryset = Achievement.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve an achievement by its achievement ID.
        :param request:
        :param pk:
        :return:
        """

        achievement = get_object_or_404(Achievement, pk=pk)
        serializer = self.serializer_class(achievement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @premium_required
    def patch(self, request, pk=None):
        """
        Update an achievement by its achievement ID.
        :param request:
        :param pk:
        :return:
        """

        achievement = get_object_or_404(Achievement, pk=pk)  # get the achievement object
        user = request.user

        # check if the user is the owner of the achievement
        if achievement.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

            # disallow free users from creating achievements
        # if prevent_free_user(user):
        #     return Response(
        #         {'message': 'This is a premium feature. Please upgrade your account to access it.'},
        #         status=status.HTTP_403_FORBIDDEN
        #     )

        serializer = self.serializer_class(achievement, data=request.data, partial=True)
        Achievement.achievement_description = request.data.get('achievement_description', Achievement.achievement_description)

        if serializer.is_valid():
            achievement.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete an achievement by its achievement ID.
        :param request:
        :param pk:
        :return:
        """

        achievement = get_object_or_404(Achievement, pk=pk)  # get the achievement object
        user = request.user

        # check if the user is the owner of the achievement
        if achievement.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            achievement.delete()
            return Response({'message': 'Achievement deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)
