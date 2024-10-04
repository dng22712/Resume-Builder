from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cvbuilder.graph.serializers import GraphSerializer
from cvbuilder.models import Graph, CvBuilder
from util.payments.user_payment_checks import premium_required

ERROR_MESSAGE = 'You are not authorized to perform this action'


# -------------Graphs by CV ID----------------
@extend_schema(tags=['CV: Graph'])
class GraphByCvId(APIView):
    """
    Retrieve graphs by CV ID.
    """

    serializer_class = GraphSerializer
    queryset = Graph.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve graphs by CV ID.
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
        post graphs by CV ID.
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
        Delete graphs by CV ID.
        :param request:
        :param pk:
        :return:
        """

        cv = get_object_or_404(CvBuilder, pk=pk)
        user = request.user

        # check if the user is the owner of the CV
        if cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            Graph.objects.filter(cv=pk).delete()
            return Response({'message': 'Graphs deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# -----------Graph by Graph ID------------------#
@extend_schema(tags=['CV: Graph'])
class GraphById(APIView):
    """
    Retrieve, update, or delete a graph by graph ID.
    """

    serializer_class = GraphSerializer
    queryset = Graph.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, pk=None):
        """
        Retrieve graph by graph ID.
        :param request:
        :param pk:
        :return:
        """

        queryset = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        """
        Update graph by graph ID.
        :param request:
        :param pk:
        :return:
        """

        graph = get_object_or_404(Graph, pk=pk)
        user = request.user

        # check if the user is the owner of the graph
        if graph.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(graph, data=request.data)
        graph.graph_header_title = request.data.get('graph_header_title', graph.graph_header_title)
        graph.graph_name = request.data.get('graph_name', graph.graph_name)
        graph.graph_value = request.data.get('graph_value', graph.graph_value)

        if serializer.is_valid():
            graph.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, pk=None):
        """
        Delete graph by graph ID.
        :param request:
        :param pk:
        :return:
        """

        graph = get_object_or_404(Graph, pk=pk)
        user = request.user

        # check if the user is the owner of the graph
        if graph.cv.user != user:
            return Response({'message': ERROR_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        try:
            graph.delete()
            return Response({'message': 'Graph deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
