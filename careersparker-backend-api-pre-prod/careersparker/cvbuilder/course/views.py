from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.course.serializers import CourseSerializer
from cvbuilder.models import Course, CvBuilder
from util.payments.user_payment_checks import premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'


# ----------------Course by CV ID------------------

@extend_schema(tags=['CV: Course'])
class CourseByCvId(APIView):
    """
    Retrieve, update, or delete a course by CV ID.
    """

    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, pk=None):
        """
        Retrieve a course by its CV ID.
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
        Create a new course entry associated with a CV by providing the CV ID.
        :param request:
        :param pk:
        :return:
        """

        course = Course.objects.create(cv_id=pk, **request.data)  # create a new course
        user = request.user

        # check if the user is the owner of the CV
        if course.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(course)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete a course by its CV ID.
        :param request:
        :param pk:
        :return:
        """

        cv = get_object_or_404(CvBuilder, pk=pk)  # get the CV object
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            course = Course.objects.get(cv_id=pk)
            course.delete()
            return Response({'message': 'Course deleted successfully'}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'message': 'Course does not exist'}, status=status.HTTP_404_NOT_FOUND)


# ----------------Course by ID------------------
@extend_schema(tags=['CV: Course'])
class CourseById(APIView):
    """
    Retrieve, update, or delete a course by its ID.
    """

    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def get(self, request, pk=None):
        """
        Retrieve a course by its ID.
        :param request:
        :param pk:
        :return:
        """
        course = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update a course by its ID.
        :param request:
        :param pk:
        :return:
        """
        course = get_object_or_404(self.queryset, pk=pk)
        user = request.user

        # check if the user is the owner of the CV
        if course.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(course, data=request.data, partial=True)
        course.course_name = request.data.get('course_name', course.course_name)
        course.course_description = request.data.get('course_description', course.course_description)
        course.institution_name = request.data.get('institution', course.institution)
        course.institution_city = request.data.get('institution_city', course.institution_city)
        course.institution_country = request.data.get('institution_country', course.institution_country)
        course.start_date = request.data.get('start_date', course.start_date)
        course.end_date = request.data.get('end_date', course.end_date)
        course.currently_studying = request.data.get('currently_studying', course.currently_studying)

        if serializer.is_valid():
            course.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """
        Delete a course by its ID.
        :param request:
        :param pk:
        :return:
        """
        course = get_object_or_404(self.queryset, pk=pk)

        # check if the user is the owner of the CV
        if course.cv.user != request.user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        course.delete()
        return Response({'message': 'Course deleted successfully'}, status=status.HTTP_200_OK)
