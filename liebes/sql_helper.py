from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from liebes.CiObjects import DBCheckout, Checkout
from liebes.analysis import CIAnalysis, load_cia
from liebes.GitHelper import GitHelper
from sqlalchemy import and_, or_
from sqlalchemy import text
from liebes.ci_logger import settings


class SQLHelper:
    def __init__(self, debug=False):
        engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(
            settings.MYSQL.USERNAME, settings.MYSQL.PASSWORD, settings.MYSQL.HOST, settings.MYSQL.PORT,
            settings.MYSQL.DATABASE
        ), echo=debug)

        # engine = create_engine(f'sqlite:///{database_path}', echo=debug)
        self.session = sessionmaker(bind=engine)()


# if __name__ == "__main__":
    # def __init__(self, database_path, debug=False):
        # engine = create_engine(f"mysql+mysqlconnector://root:linux%40133@localhost:3306/lkft", echo=debug)
        # engine = create_engine(f'sqlite:///{database_path}', echo=debug)
        # self.session = sessionmaker(bind=engine)()

