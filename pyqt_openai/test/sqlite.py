import sqlite3


class SqliteDatabase:
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initDb()
        self.__createTables()

    def __initVal(self):
        self.__table_name = 'example_table'
        self.__child_table_name = 'child_table_name'

    def __initDb(self):
        try:
            # Connect to the database (create a new file if it doesn't exist)
            self.__conn = sqlite3.connect('example.db')
        except sqlite3.Error as e:
            print(f"An error occurred while connecting to the database: {e}")
            raise

    def __createTables(self):
        try:
            # Create a cursor object
            self.__c = self.__conn.cursor()

            # Check if the table exists
            self.__c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__table_name}'")
            if self.__c.fetchone()[0] == 1:
                print(f"The table '{self.__table_name}' exists.")
            else:
                # Create a table with update_dt and insert_dt columns
                self.__c.execute('''CREATE TABLE example_table
                             (id INTEGER PRIMARY KEY,
                              name TEXT,
                              update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                              insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                # Create a trigger to update the update_dt column with the current timestamp
                self.__c.execute('''CREATE TRIGGER update_example_table
                             AFTER UPDATE ON example_table
                             FOR EACH ROW
                             BEGIN
                               UPDATE example_table
                               SET update_dt=CURRENT_TIMESTAMP
                               WHERE id=OLD.id;
                             END;''')
                # Commit the transaction
                self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")
            raise

    def insert(self, name):
        try:
            # Insert a row into the table
            self.__c.execute(f'INSERT INTO {self.__table_name} (name) VALUES (?)', (name,))
            new_id = self.__c.lastrowid
            # Commit the transaction
            self.__conn.commit()
            self.__createChild(new_id)
        except sqlite3.Error as e:
            print(f"An error occurred while inserting into the table: {e}")
            raise

    def isExists(self, id):
        try:
            # Insert a row into the table
            query = f"SELECT * FROM {self.__table_name} WHERE id=?"
            self.__c.execute(query, (id,))
            result = self.__c.fetchone()
            return result[0] == id if result else False
        except sqlite3.Error as e:
            print(f"An error occurred while inserting into the table: {e}")
            raise

    def __createChild(self, example_table_id):
        try:
            # Check if the child_table exists
            self.__c.execute(f"SELECT count(*) FROM {self.__table_name} WHERE id='{example_table_id}'")
            # if self.__c.fetchone()[0] == 0:
            #     # Create the child_table with a foreign key constraint referencing the example_table
            #     self.__c.execute(f'''CREATE TABLE child_table
            #                              (id INTEGER PRIMARY KEY,
            #                               example_table_id INTEGER,
            #                               child_name TEXT,
            #                               FOREIGN KEY({example_table_id}) REFERENCES {self.__table_name}(id))''')
            # # Commit the transaction
            # self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while inserting into the table: {e}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the connection
        self.__conn.close()


with SqliteDatabase() as db:
    db.insert('Jack')
    db.insert('Carl')
    id = 1
    if db.isExists(id):
        print('good')
    else:
        print('not exists')
