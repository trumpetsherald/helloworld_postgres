import psycopg2
import psycopg2.extras as extras
from retry import retry
from src import hello_logger


class HiPGDatabaseException(Exception):
    pass


class HiPGDatabase(object):
    def __init__(self, host, name, user, password):
        self.logger = hello_logger.LOGGER
        self.host = host
        self.name = name
        self.username = user
        self.password = password
        self.connection = None

    #  Wait up to 17 mins attempting to reconnect
    @retry((Exception, psycopg2.DatabaseError), tries=10, delay=1, backoff=2)
    def connect_to_db(self):
        result = True
        conn_params = {
            "host": self.host,
            "database": self.name,
            "user": self.username,
            "password": self.password
        }

        if not self.connection:
            try:
                self.connection = psycopg2.connect(**conn_params)

                # create a cursor
                cur = self.connection.cursor()

                # execute a statement
                self.logger.debug('PostgreSQL database version:')
                cur.execute('SELECT version()')

                # display the PostgreSQL database server version
                db_version = cur.fetchone()
                self.logger.debug(db_version)

                # close communication with the PostgreSQL DB
                cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                self.logger.error("Error connecting to database:")
                self.logger.error(error)
                raise error

        return result

    def close(self):
        self.connection.close()

    def insert_values(self, records, sql):
        result = True
        cursor = self.connection.cursor()
        try:
            extras.execute_values(cursor, sql, records)
        except (Exception, psycopg2.Error) as error_ex:
            self.logger.error("Error executing the following sql: %s" % sql)
            self.logger.error("Error: " + str(error_ex))
            result = False
        else:
            try:
                self.connection.commit()
            except (Exception, psycopg2.Error) as error_ex:
                self.logger.error("Error on commit.")
                self.logger.error("Error: " + str(error_ex))
                self.connection.rollback()
                result = False
        finally:
            cursor.close()

        return result

    def get_values(self, sql, data=None):
        cursor = self.connection.cursor()
        try:
            if data:
                cursor.execute(sql, data)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
        except (Exception, psycopg2.Error) as error_ex:
            self.logger.error("Error executing the following sql: %s" % sql)
            self.logger.error("Error: " + str(error_ex))
            result = False
        finally:
            cursor.close()

        return result

    def insert_request_records(self, request_records):
        upsert_sql = "INSERT INTO public.request(" \
                     "request_time, " \
                     "status_code, " \
                     "request_duration, " \
                     "method, " \
                     "response_size, " \
                     "uri, " \
                     "user_agent) " \
                     "VALUES %s " \
                     "ON CONFLICT ON CONSTRAINT" \
                     "  request_pkey " \
                     "DO NOTHING;"

        return self.insert_values(request_records, upsert_sql)

    # def insert_category_records(self, health_records):
    #     upsert_sql = "INSERT INTO public.hk_category_record(" \
    #                  "person_id, " \
    #                  "hk_type, " \
    #                  "hk_source, " \
    #                  "source_version, " \
    #                  "device, " \
    #                  "creation_date, " \
    #                  "start_date, " \
    #                  "end_date, " \
    #                  "unit, " \
    #                  "hk_value) " \
    #                  "VALUES %s " \
    #                  "ON CONFLICT ON CONSTRAINT" \
    #                  "  hk_category_record_unique " \
    #                  "DO UPDATE " \
    #                  "SET (source_version, device, " \
    #                  "creation_date, unit, hk_value) = " \
    #                  "(EXCLUDED.source_version, " \
    #                  "EXCLUDED.device, EXCLUDED.creation_date, " \
    #                  "EXCLUDED.unit, EXCLUDED.hk_value);"
    #
    #     return self.insert_values(health_records, upsert_sql)
