###
# based on: https://github.com/ayush-sharma/infra_helpers
#
#  Removed the need for a specific auto increment column
#  set localTZ below to the timezone the MYSQL Database has
#       stored the timestamp for a conversion to UTC in InfluxDB
#
import datetime
from pytz import timezone

import MySQLdb
from influxdb import InfluxDBClient

localTZ = timezone('Europe/Berlin')


def file_read(path: str):
    """ Read a file and return content. """

    try:
        handler = open(path, "r")
        data = handler.read()
        handler.close()
        return data

    except Exception as e:
        print("Exception: %s" % str(e))
        return None


def file_write(path: str, mode: str, content: str):
    """ Write content to a file. """

    handler = open(path, mode)

    handler.write(content)

    handler.close()


def get_data_from_mysql(
    host: str, username: str, password: str, db: str, sql: str
):
    """ Run SQL query and get data from MySQL table. """

    db = MySQLdb.connect(host, username, password, db)

    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(sql)
        data = cursor.fetchall()
    except Exception as e:
        print("MySQL error %s: %s" % (e.args[0], e.args[1]))
        data = None

    db.close()

    return data


main_config = {
    "state_file_path": "/tmp/migrate_mysql_to_influxdb_state_file_",
    "mysql_host": "localhost",
    "mysql_username": "",
    "mysql_password": "",
    "mysql_database": "",
    "influxdb_host": "",
    "influxdb_port": "8086",
    "influxdb_user": "",
    "influxdb_password": "",
    "influxdb_database": "",
    "tables": [
        {
            "table_name": "light_log",
            "measurement_name": "Helligkeit",
            "columns": [
                {"column_name": "room", "is_tag": True, "type": "string"},
                {"column_name": "light", "is_tag": False, "type": "int"},
            ],
            "unix_timestamp_column": "time",
        },
        {
            "table_name": "temperature_log",
            "measurement_name": "Temperatur",
            "columns": [
                {"column_name": "room", "is_tag": True, "type": "string"},
                {
                    "column_name": "temperatur",
                    "is_tag": False,
                    "type": "float",
                },
            ],
            "unix_timestamp_column": "time",
        },
    ],
}

if __name__ == "__main__":

    mysql_tables = main_config["tables"]
    state_file_prefix = main_config["state_file_path"]

    for table in mysql_tables:
        first_dataset = True

        table_name = table["table_name"]
        measurement = table["measurement_name"]
        state_file = state_file_prefix + table_name

        last_state_value = (
            file_read(state_file) if file_read(state_file) else "0"
        )

        columns_list = [table["unix_timestamp_column"]]
        default_values = {}
        tags_list = []
        for item in table["columns"]:

            columns_list.append(item["column_name"])

            if item["type"] == "string":
                default_values[item["column_name"]] = ""

            if item["type"] == "int":
                default_values[item["column_name"]] = 0

            if item["type"] == "float":
                default_values[item["column_name"]] = 0.0

            if item["is_tag"]:
                tags_list.append(item["column_name"])

        columns_list = ",".join(columns_list)

        sql = (
            "SELECT "
            + columns_list
            + " FROM "
            + table_name
            + " LIMIT 10000"
            + " OFFSET "
            + last_state_value
        )

        data = get_data_from_mysql(
            host=main_config["mysql_host"],
            username=main_config["mysql_username"],
            password=main_config["mysql_password"],
            db=main_config["mysql_database"],
            sql=sql,
        )

        influxdb_data = []

        if len(data) > 0:

            influxdb_client = InfluxDBClient(
                main_config["influxdb_host"],
                main_config["influxdb_port"],
                main_config["influxdb_user"],
                main_config["influxdb_password"],
                main_config["influxdb_database"],
            )

            for item in data:
                timestamp = 0
                fields = {}
                tags = {}
                for key, value in item.items():

                    if key == table["unix_timestamp_column"]:
                        nativets = datetime.datetime.fromtimestamp(value)
                        timestampL = localTZ.localize(nativets)
                        timestampN = localTZ.normalize(timestampL)
                        timestamp = timestampN.isoformat()
                    else:
                        if key in tags_list:
                            tags[key] = value
                        else:
                            fields[key] = (
                                value if value else default_values[key]
                            )

                data_point = {
                    "measurement": measurement,
                    "tags": tags,
                    "time": timestamp,
                    "fields": fields,
                }

                influxdb_data.append(data_point)

                if first_dataset:
                    first_dataset = False
                    print(
                        "First Datapoint at: ", str(int(last_state_value) + 1)
                    )
                    print(data_point)

            file_write(state_file, "w", str(int(last_state_value) + len(data)))
            influxdb_client.write_points(influxdb_data)

            print(
                "Last Datapoint at: ", str(int(last_state_value) + len(data))
            )
            print(data_point)

            print(
                "Written "
                + str(len(data))
                + " points for table "
                + table_name
                + "."
            )

        else:
            print("No data retrieved from MySQL for table " + table_name + ".")
