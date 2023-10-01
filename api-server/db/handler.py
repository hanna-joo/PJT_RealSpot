import pymysql
from fastapi import HTTPException
from typing import List, Dict

connection = None

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "mysql",
    "database": "study_db",
}


def _create_db_connection():
    return pymysql.connect(**db_config)


def fetch_all(sql) -> List[Dict]:
    """

    :param sql:
        query script (select)
    :return:
        query result
    """
    conn = _create_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute(sql)
        result = cursor.fetchall()

        if result is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return result

    finally:
        cursor.close()
        conn.close()
