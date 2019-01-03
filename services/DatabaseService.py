# -*- coding: UTF-8 -*-
"""
module with a service providing all database related connections and functions
"""

from GeologicalToolbox.DBHandler import DBHandler

from GeologicalDataProcessing.miscellaneous.ExceptionHandling import ExceptionHandling
from GeologicalDataProcessing.miscellaneous.QGISDebugLog import QGISDebugLog


class DatabaseService:
    """
    Singleton class controlling all database related processes
    """
    __instance = None

    logger = QGISDebugLog()

    @staticmethod
    def get_instance() -> "DatabaseService":
        """
        Creates a new object instance if no object exists or updates the existing one.
        :return: The single instance of this class
        """
        if DatabaseService.__instance is None:
            DatabaseService.logger.debug(DatabaseService.__class__.__name__, "Create new DatabaseService instance")
            DatabaseService()
        else:
            DatabaseService.logger.debug(DatabaseService.__name__, "Returning existing DatabaseService instance")

        return DatabaseService.__instance

    def __init__(self):
        """ Virtually private constructor. """
        super().__init__()
        if DatabaseService.__instance is not None:
            raise BaseException("The DatabaseService-class is a singleton and can't be called directly. " +
                                "Use DatabaseService.get_instance() instead!")
        else:
            DatabaseService.__instance = self

        self.__connection = ""
        self.__db_type = ""
        self.__password = ""
        self.__username = ""

        self.__handler = None
        self.__session = None

    #
    # setter and getter
    #

    @property
    def connection(self) -> str:
        """
        Getter for the current connection string
        :return: returns the current connection string
        """
        return self.__connection

    @connection.setter
    def connection(self, value: str) -> None:
        """
        setter for the current connection string
        :return: Nothing
        """
        self.__connection = str(value)

    @property
    def db_type(self) -> str:
        """
        Getter for the database type
        :return: returns the current database type
        """
        return self.__db_type

    @db_type.setter
    def db_type(self, value: str) -> None:
        """
        setter for the database type
        :return: Nothing
        :raises ValueError: if value is not "SQLite" or "PostgreSQL"
        """
        value = str(value)

        if value.lower() not in ("sqlite", "postgresql"):
            raise ValueError("Unknown database format: {}".format(value))

        self.__db_type = value.lower()

    @property
    def password(self) -> str:
        """
        Getter for the current password
        :return: returns the current password
        """
        return self.__password

    @password.setter
    def password(self, value: str) -> None:
        """
        setter for the current password
        :return: Nothing
        """
        self.__password = str(value)

    @property
    def username(self) -> str:
        """
        Getter for the current username
        :return: returns the current username
        """
        return self.__username

    @username.setter
    def username(self, value: str) -> None:
        """
        setter for the current username
        :return: Nothing
        """
        self.__username = str(value)

    #
    # public functions
    #

    def check_connection(self) -> str:
        """
        Check database connection
        :return: Error message if test fails, else empty string
        :raises ValueError: if database type is unknown
        """
        self.logger.debug("check_connection called")

        try:
            # noinspection SpellCheckingInspection
            if self.db_type == "postgresql":
                self.logger.debug("\tPostgreSQL connection")
                # connection string: postgresql+psycopg2://user:password@host:port/dbname[?key=value&key=value...]
                connection = "postgresql+psycopg2://{}:{}@{}".format(self.username, self.password, self.connection)
            elif self.db_type == "sqlite":
                self.logger.debug("\tSQLite connection")
                connection = "sqlite:///{}".format(self.connection)
            else:
                raise ValueError("Unknown DB Format: {}".format(self.db_type))

            self.logger.debug("\tconnecting to handler")
            self.__handler = DBHandler(connection=connection, echo=False)
            self.__session = self.__handler.get_session()
            self.logger.debug("\tclosing connection")
            self.__handler.close_last_session()
            return ""

        except Exception as e:
            ExceptionHandling(e).log(True)
            return str(e)
