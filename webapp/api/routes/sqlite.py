import sqlite3

class sql3:
    def __init__(self,db_name='piglet.db'):
        self.db_name = db_name
        self.conn = None


    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise HTTPException(status_code=503, detail="Service Unavailable {e}")
        
    def disconnect(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        if not self.conn:
            self.connect()
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return None
    def create_table(self, table_name, columns):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.execute_query(query)
        self.conn.commit()

    def insert_data(self, table_name, data):
        placeholders = ', '.join(['?'] * len(data))
        columns = ', '.join(data.keys())
        values = tuple(data.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor = self.execute_query(query, values)
        self.conn.commit()
        return cursor.lastrowid
        
    def fetch_all(self, table_name):
        query = f"SELECT * FROM {table_name}"
        cursor = self.execute_query(query)
        return cursor.fetchall()

    def fetch_by_id(self, table_name, id):
        query = f"SELECT id FROM {table_name} WHERE id = {id}"
        cursor = self.execute_query(query)
        return cursor.fetchone()