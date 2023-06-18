import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

MYSQL_USER = os.environ.get("username", "root")
MYSQL_PASSWORD = os.environ.get("password", "")
MYSQL_HOST = os.environ.get("host", "localhost:3306")
MYSQL_DB = os.environ.get("name", "log")


class Database(object):
    def __init__(self):
        self._engine = create_engine(
            "mysql://{0}:{1}@{2}/{3}".format(
                MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB
            ),
            pool_recycle=3600,
            pool_size=10,
            echo=False,
        )

    def get_engine(self):
        return self._engine

    @classmethod
    def instance(cls):
        """Singleton like accessor to instantiate backend object"""
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def get_session_factory(self):
        self._session_factory = scoped_session(sessionmaker(bind=self._engine))
        return self._session_factory

    def get_session(self):
        self.get_session_factory()
        self._session = self._session_factory()
        return self._session
