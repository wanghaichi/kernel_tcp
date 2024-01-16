import json
import pickle

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from liebes.CiObjects import DBCheckout, Checkout
from liebes.GitHelper import GitHelper
from sqlalchemy import and_, or_
from sqlalchemy import text


class SQLHelper:
    def __init__(self, debug=False):
        # engine = create_engine(f'sqlite:///{database_path}', echo=debug)
        engine = create_engine(f"mysql+mysqlconnector://root:linux%40133@localhost:3306/lkft", echo=debug)
        self.session = sessionmaker(bind=engine)()

    # file_path is not null
    def update_instances(self, instances):
        for instance in tqdm(instances):
            self.session.merge(instance)
        self.session.commit()


if __name__ == "__main__":
    pass
