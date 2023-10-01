import psycopg2

def command_decorator(cursor):
    cursor = cursor
    def inner(func):
        def wrapper(**kwargs):
            try:
                return func(**kwargs)
            except psycopg2.Error as error:
                cursor.connection.rollback()
                print(error)
        return wrapper

    return inner