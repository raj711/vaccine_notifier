import os

import sqlalchemy as db
from datetime import datetime
try:

    # print(os.environ.get("DB_USERNAME"))
    connection_string = 'mysql+mysqldb://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4&ssl=true'.format(
        db_user=os.environ.get("DB_USERNAME"), db_password=os.environ.get("DB_PASSWORD"), db_host=os.environ.get("DB_HOST"),
        db_port=int(os.environ.get("DB_PORT")), db_name=os.environ.get("DB_NAME"))

    # print(">>>>>>>>>>", connection_string)
    db_engine = db.create_engine(connection_string,
                                 pool_size=15,
                                 max_overflow=0, pool_recycle=3600, pool_pre_ping=True)

except Exception as e:
    print("Error to connect with  DB" + str(e))
    # print(traceback.print_exc())
    db_engine = None

def get_user_data(app):
    connection = db_engine.connect()
    try:

        db_table = "users"
        result = connection.execute(
            """SELECT * FROM {} where is_notified = 0""".format(db_table))
        if result != None:
            return [{column: value for column, value in result.items()} for result in result]
    except Exception as e:
        app.logger.error("Error to get user data " + str(e))
        return None
    finally:
        connection.close()


def create_user(email, district_code, district,  age, app):
    connection = db_engine.connect()
    try:
        db_table = "users"
        query = """INSERT INTO {} (`email`, `district_code`, `district`, `is_notified`, `created_at`, `updated_at`, `age`) VALUES (%s, %s, %s, %s, %s, %s, %s)""".format(db_table)
        result = connection.execute(query, (email, district_code, district, 0, datetime.now(), datetime.now(), age))
        return True
    except Exception as e:
        app.logger.error("Error to create user " + str(e))
        return False
    finally:
        connection.close()


def get_user_by_email(email, district_code, age, app):
    connection = db_engine.connect()
    try:
        db_table = "users"
        query = """SELECT * from {} where email=%s AND district_code=%s AND age=%s""".format(
            db_table)
        result = connection.execute(query, (email, district_code, age))
        if result != None:
            return [{column: value for column, value in result.items()} for result in result]
    except Exception as e:
        app.logger.error("Error to get user " + str(e))
        return None
    finally:
        connection.close()


def update_user_notified_status(email, district_code, age, is_notified, app):
    connection = db_engine.connect()
    try:
        db_table = "users"
        query = """UPDATE {} SET is_notified=%s, updated_at=%s where email=%s AND district_code=%s AND age=%s""".format(
            db_table)
        result = connection.execute(query, (int(not is_notified), datetime.now(), email, district_code, age))
        return True
    except Exception as e:
        app.logger.error("Error to update status {}".format(str(e)))
        return False
    finally:
        connection.close()

