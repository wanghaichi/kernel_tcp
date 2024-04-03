from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from liebes.ci_logger import settings


class SQLHelper:
    # _instance = None
    #
    # def __new__(cls, *args, **kwargs):
    #     if not isinstance(cls._instance, cls):
    #         cls._instance = super(SQLHelper, cls).__new__(cls, *args, **kwargs)
    #     return cls._instance

    def __init__(self, debug=False):
        self.debug = debug
        pass

    _session = None

    @property
    def session(self):
        if self._session is None:
            engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(
                settings.MYSQL.USERNAME, settings.MYSQL.PASSWORD, settings.MYSQL.HOST, settings.MYSQL.PORT,
                settings.MYSQL.DATABASE
            ), echo=self.debug, pool_size=20)

            # engine = create_engine(f'sqlite:///{database_path}', echo=debug)
            self._session = sessionmaker(bind=engine)()
        return self._session

# if __name__ == "__main__":
# def __init__(self, database_path, debug=False):
# engine = create_engine(f"mysql+mysqlconnector://root:linux%40133@localhost:3306/lkft", echo=debug)
# engine = create_engine(f'sqlite:///{database_path}', echo=debug)
# self.session = sessionmaker(bind=engine)()
