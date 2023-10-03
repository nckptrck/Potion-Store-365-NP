import os
import dotenv
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()

    uri = os.environ.get("POSTGRES_URI")
    print('AAAAA: ', uri)

    for key, value in os.environ.items():
        print(f"{key}: {value}")

    return(uri)


engine = create_engine(database_connection_url(), pool_pre_ping=True)