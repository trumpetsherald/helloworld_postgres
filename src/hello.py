import datetime
import json
import os
from src import hello_logger
from src import hello_database

from src.data_generator import generate_nginx_log_data

LOGGER: hello_logger.LOGGER = hello_logger.LOGGER
DATABASE: hello_database.HiPGDatabase


def connect_to_db():
    global DATABASE
    LOGGER.info("Connecting to Database.")

    db_host, db_name, db_username, db_password = None, None, None, None

    try:
        db_host = os.environ.get('HIPG_DB_HOST', "localhost")
        db_name = os.environ.get('HIPG_DB_NAME', "hello_postgres")
        db_username = os.environ.get('HIPG_DB_USERNAME', "mstonebreaker")
        db_password = os.environ.get('HIPG_DB_PASSWORD', "berkeley")
    except KeyError as ke:
        print("Key not found %s", ke)
        exit(42)

    DATABASE = hello_database.HiPGDatabase(db_host, db_name, db_username,
                                        db_password)
    # noinspection PyBroadException
    try:
        DATABASE.connect_to_db()
    except Exception:
        LOGGER.error("Could not connect to database after 10 retries. "
                     "Make sure the database is running and your credentials "
                     "are correct.")
        LOGGER.error("Export failed.")
        exit(42)


def create_data():
    LOGGER.info("Generating data.")
    frame = generate_nginx_log_data()

    return json.loads(frame.to_json(orient="records"))


def convert_tuples(requests):
    result = []
    for request in requests:
        result.append(
            (
                request['request_time'],
                request['status_code'],
                request['request_duration'],
                request['method'],
                request['response_size'],
                request['uri'],
                request['user_agent']
            )
        )

    return result


if __name__ == "__main__":
    start = datetime.datetime.now()
    LOGGER.info("Starting Hello Postgres.")
    fake_requests = create_data()
    request_records = convert_tuples(fake_requests)
    connect_to_db()

    LOGGER.info("Inserting %d records." % len(request_records))
    DATABASE.insert_request_records(request_records)
    end = datetime.datetime.now()
    LOGGER.info("Exiting, everything took %s seconds." % (end - start))
