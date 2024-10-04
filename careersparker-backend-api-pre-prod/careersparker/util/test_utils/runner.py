from types import MethodType

from django.db import connections
from django.test.runner import DiscoverRunner


def prepare_database(self):
    self.connect()
    self.connection.cursor().execute("""
               CREATE SCHEMA "cvr-db-test_schema" AUTHORIZATION max;
               GRANT ALL ON SCHEMA "cvr-db-test_schema" TO max;
           """)


class PostgresSchemaTestRunner(DiscoverRunner):

    def setup_databases(self, **kwargs):
        for connection_name in connections:
            connection = connections[connection_name]
            connection.prepare_database = MethodType(prepare_database, connection)
        return super().setup_databases(**kwargs)
