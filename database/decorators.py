import psycopg2

def command_decorator(func):
    def wrapper(**kwargs):
        try:
            return func(**kwargs)
        except psycopg2.Error as error:
            print(error)

    return wrapper