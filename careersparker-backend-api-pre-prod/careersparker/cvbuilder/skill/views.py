from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.models import Skill, CvBuilder
from cvbuilder.skill.serializers import CvSkillSerializer


# ----------------------------------------------------------------
# Skill by CV ID
# ----------------------------------------------------------------

@extend_schema(tags=['CV: Skill'])
class SkillByCvId(APIView):
    """
    Retrieve, update, or delete skill entries by CV ID.

    GET:
    Retrieve all skill entries associated with a CV by providing the CV ID.

    POST:
    Create a new skill entry associated with a CV by providing the CV ID.

    DELETE:
    Delete all skill entries associated with a CV by providing the CV ID.
    """

    serializer_class = CvSkillSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = Skill.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk=None):
        """
        Retrieve all skill entries associated with a CV by providing the CV ID.

        Parameters:
        - request: Request object.
        - pk: CV ID.

        Returns:
        - Skill entries associated with the CV ID.
        """
        queryset = self.queryset.filter(cv=pk).order_by('-skill_name')
        serializer = self.serializer_class(queryset, many=True)
        return Response({'skills': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, pk):
        """
        Create a new skill by CV builder ID.
        :param request:
        :param pk:
        :return:
        """

        user = request.user
        cv = get_object_or_404(CvBuilder, pk=pk)

        # check if the user is the owner of the CV
        if user != cv.user:
            return Response({'message': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)

        # check if the cv is already published
        try:
            skill = Skill.objects.get(cv=cv, skill_name=request.data.get('skill_name'))
            if skill:
                return Response({'message': 'Skill already exists'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(cv=cv)
            return Response({'message': 'Skill created successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)

        except Skill.DoesNotExist:
            return Response({'message': 'Skill not found'}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete all skill entries associated with a CV by providing the CV ID.
        :param request:
        :param pk:
        :return:
        """

        cv = get_object_or_404(CvBuilder, pk=pk)

        user = request.user

        # check the user is the owner of the CV
        if cv.user != user:
            return Response({'message': 'You are not authorized to perform this action'},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            Skill.objects.filter(cv=pk).delete()
            return Response({'message': 'Skill entries deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------------
# Skill by ID
# ----------------------------------------------------------------

@extend_schema(tags=['CV: Skill'])
class SkillById(APIView):
    """
    Manage CV skills in the database.
    Authentication:
       - Requires JWT authentication.
    Permissions:
        - Allows read-only access to authenticated users.
    """

    serializer_class = CvSkillSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = Skill.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        """
        Retrieve a skill by ID.
        :param request:
        :param pk:
        :return:
        """

        queryset = self.queryset.filter(pk=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'skills': serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """
        Update a skill by ID.
        :param request:
        :param pk:
        :return:
        """

        skill = get_object_or_404(Skill, pk=pk)

        # check if the user is the owner of the CV
        if skill.cv.user != request.user:
            return Response({'message': 'You are not authorized to delete this skill'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(skill, data=request.data, partial=True)
        skill.skill_level = request.data.get('skill_level', skill.skill_level)

        serializer.is_valid(raise_exception=True)
        serializer.save(skill_level=skill.skill_level)
        return Response({'message': 'Skill updated successfully'}, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request, pk):
        """
        Delete a skill by ID.
        :param request:
        :param pk:
        :return:
        """

        user = request.user

        skill = get_object_or_404(Skill, pk=pk)
        cv = get_object_or_404(CvBuilder, pk=skill.cv.id)

        # prevents user from deleting other users skills
        if user != cv.user:
            return Response({'message': 'You are not authorized to delete this skill'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            skill.delete()
            return Response({'message': 'Skill deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
