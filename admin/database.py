from database.database import CURSOR


class AdminDB:
    per_page = 15

    def __init__(self, table_name: str) -> None:
        self.table_name = table_name

    def get_list_of_objects(self, page: int) -> list:
        CURSOR.execute(f'''
        SELECT * FROM "{self.table_name}" LIMIT {AdminDB.per_page * page} OFFSET {AdminDB.per_page * (page - 1)}
        ''')

        return list(CURSOR.fetchall())
