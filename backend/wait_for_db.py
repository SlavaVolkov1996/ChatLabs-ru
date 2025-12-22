import os
import sys
import time
import psycopg2
from django.db import connections
from django.db.utils import OperationalError

# проверку готовности все падало без него
def wait_for_db():
    max_retries = 30
    retry_delay = 2

    print("Waiting for database...")
    # попытки подключения, обработка
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                dbname=os.environ.get('POSTGRES_DB'),
                user=os.environ.get('POSTGRES_USER'),
                password=os.environ.get('POSTGRES_PASSWORD'),
                host=os.environ.get('POSTGRES_HOST', 'postgres'),
                port=os.environ.get('POSTGRES_PORT', '5432')
            )
            conn.close()
            print("Database is ready!")
            return True
        except Exception as e:
            print(f"Attempt {i + 1}/{max_retries}: Database not ready - {e}")
            time.sleep(retry_delay)

    print("Database connection failed after all retries")
    return False


if __name__ == "__main__":
    if wait_for_db():
        sys.exit(0)
    else:
        sys.exit(1)
