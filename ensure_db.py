import os
import pymysql
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def ensure_mysql_database():
    """
    Ensure the MySQL database specified by DB_NAME exists.
    Creates it if it does not exist yet.
    """
    use_sqlite = os.environ.get('USE_SQLITE', 'False').lower() in ['true', '1', 'yes']
    if use_sqlite:
        return True

    db_name = os.environ.get('DB_NAME', 'expense_tracker')
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', '127.0.0.1')
    db_port = int(os.environ.get('DB_PORT', '3306'))

    try:
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.close()
        print(f"MySQL database '{db_name}' ensured on {db_host}:{db_port}.")
        return True
    except Exception as e:
        print(f"MySQL database setup check: {e}")
        return False

if __name__ == '__main__':
    ensure_mysql_database()
