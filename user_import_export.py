import csv
import logging
import threading

from models import User
from serializers import UserSerializer, ValidationError

from app import app

logging.basicConfig(filename='importer.log', level=logging.ERROR)


USER_INPUT_FILE_PATH = "/tmp/users_input.csv"
USER_OUTPUT_FILE_PATH = "/tmp/users_output.csv"

COL_USERNAME = 0
COL_NAME = 1
COL_HOME_TOWN = 2
COL_HOME_UF = 3
COL_WORK_CITY = 4
COL_WORK_UF = 5
COL_WORK_ENTERING_HOUR = 6
COL_WORK_LEAVING_HOUR = 7


def process_row_async(row_number, row_data):
    serializer = UserSerializer(data=row_data)

    try:
        with app.app_context():
            serializer.validate(row_data)
            serializer.create()
    except ValidationError as e:
        logging.error("Error row %d: %s" % (row_number, str(e)))


def process_row(row_number, row_data):
    threading.Thread(target=process_row_async, args=(row_number, row_data)).start()


def import_users():
    input_file_path = USER_INPUT_FILE_PATH

    def get_column(row, index):
        try:
            return row[index]
        except IndexError:
            return None

    with open(input_file_path, "r") as csvfile:
        data_reader = csv.reader(csvfile, delimiter=';', quotechar='"')

        for index, row in enumerate(data_reader):
            data = {
                "username": get_column(row, COL_USERNAME),
                "name": get_column(row, COL_NAME),
                "home_city_name": get_column(row, COL_HOME_TOWN),
                "home_city_uf": get_column(row, COL_HOME_UF),
                "work_city_name": get_column(row, COL_WORK_CITY),
                "work_city_uf": get_column(row, COL_WORK_UF),
                "work_entering_hour": get_column(row, COL_WORK_ENTERING_HOUR),
                "work_leaving_hour": get_column(row, COL_WORK_LEAVING_HOUR),
            }
            process_row(index, data)


def export_users():
    export_data = []

    with app.app_context():
        users = User.query.all()

        for user in users:
            user_data = [
                user.username,
                user.name,
                user.home_location.city_name,
                user.home_location.uf,
                user.work_location.city_name if user.work_location else "",
                user.work_location.uf if user.work_location else "",
                user.work_entering_hour or "",
                user.work_leaving_hour or "",
            ]
            export_data.append(user_data)
    with open(USER_OUTPUT_FILE_PATH, "w") as csvfile:
        wr = csv.writer(csvfile, delimiter=';', quotechar='"')
        wr.writerows(export_data)
