import json
import pickle

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from liebes.CiObjects import DBCheckout, Checkout
<<<<<<< HEAD
=======
from liebes.analysis import CIAnalysis, load_cia
>>>>>>> d7b5f734f3ede5c39a083a63321c112632e496d2
from liebes.GitHelper import GitHelper
from sqlalchemy import and_, or_
from sqlalchemy import text


class SQLHelper:
<<<<<<< HEAD
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
=======
    def __init__(self, database_path, debug=False):
        engine = create_engine(f"mysql+mysqlconnector://root:linux%40133@localhost:3306/lkft", echo=debug)
        # engine = create_engine(f'sqlite:///{database_path}', echo=debug)
        self.session = sessionmaker(bind=engine)()
>>>>>>> d7b5f734f3ede5c39a083a63321c112632e496d2
