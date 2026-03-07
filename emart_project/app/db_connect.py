import configparser
import os

import mysql.connector


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.ini')


def get_connection():
    """Create and return a MySQL connection using values from config.ini."""
    config = configparser.ConfigParser()

    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f'Config file not found: {CONFIG_PATH}')

    config.read(CONFIG_PATH)
    if 'mysql' not in config:
        raise KeyError("Missing 'mysql' section in config.ini")

    db_cfg = config['mysql']
    return mysql.connector.connect(
        host=db_cfg.get('host', 'localhost'),
        user=db_cfg.get('user', ''),
        password=db_cfg.get('password', ''),
        database=db_cfg.get('database', '')
    )


if __name__ == '__main__':
    connection = None
    try:
        connection = get_connection()
        if connection.is_connected():
            print('Database connection successful.')
        else:
            print('Database connection failed.')
    except mysql.connector.Error as err:
        print(f'MySQL Error: {err}')
    except Exception as err:
        print(f'Error: {err}')
    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            print('Connection closed.')
