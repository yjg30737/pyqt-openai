import sqlite3, json, shutil


class SqliteDatabase:
    """
    functions which only meant to be used frequently are defined.

    if there is no functions you want to use, use ``getCursor`` instead
    """
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initDb()
        self.__createConv()

    def __initVal(self):
        # db names
        self.__db_filename = 'conv.db'
        self.__info_tb_nm = 'info_tb'
        self.__conv_tb_nm = 'conv_tb'
        self.__conv_tb_tr_nm = 'conv_tr'
        self.__conv_unit_tb_nm = 'conv_unit_tb'

        # field default value
        self.__attr_default_value = {
            'engine': "gpt-3.5-turbo",
            'temperature': 0.0,
            'max_tokens': 256,
            'top_p': 1.0,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0,
            'stream': True
        }

    def __initDb(self):
        try:
            # Connect to the database (create a new file if it doesn't exist)
            self.__conn = sqlite3.connect(self.__db_filename)
            self.__conn.execute('PRAGMA foreign_keys = ON;')
            self.__conn.commit()

            self.__c = self.__conn.cursor()
            self.__createInfo()
        except sqlite3.Error as e:
            print(f"An error occurred while connecting to the database: {e}")
            raise

    def __createInfo(self):
        try:
            # Check if the table exists
            self.__c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__info_tb_nm}'")
            if self.__c.fetchone()[0] == 1:
                # each conv table already exists
                pass
            else:
                # Create a table with update_dt and insert_dt columns
                self.__c.execute(f'''CREATE TABLE {self.__info_tb_nm}
                             (id INTEGER PRIMARY KEY,
                              engine VARCHAR(50) DEFAULT '{self.__attr_default_value['engine']}',
                              temperature INTEGER DEFAULT {self.__attr_default_value['temperature']},
                              max_tokens INTEGER DEFAULT {self.__attr_default_value['max_tokens']},
                              top_p INTEGER DEFAULT {self.__attr_default_value['top_p']},
                              frequency_penalty INTEGER DEFAULT {self.__attr_default_value['frequency_penalty']},
                              presence_penalty INTEGER DEFAULT {self.__attr_default_value['presence_penalty']},
                              stream BOOL DEFAULT {self.__attr_default_value['stream']},
                              update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                              insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')

                # Commit the transaction
                self.__conn.commit()

                # insert default record
                self.__c.execute(f'''INSERT INTO {self.__info_tb_nm}
                                    (
                                        engine,
                                        temperature,
                                        max_tokens,
                                        top_p,
                                        frequency_penalty,
                                        presence_penalty,
                                        stream
                                    ) VALUES
                                    (
                                        {','.join(['?' for _ in range(len(self.__attr_default_value))])}
                                    )
                                 ''', tuple(self.__attr_default_value.values()))
                # Commit the transaction
                self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")
            raise

    def __createConv(self):
        try:
            # Check if the table exists
            self.__c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__conv_tb_nm}'")
            if self.__c.fetchone()[0] == 1:
                # each conv table already exists
                pass
            else:
                # Create a table with update_dt and insert_dt columns
                self.__c.execute(f'''CREATE TABLE {self.__conv_tb_nm}
                             (id INTEGER PRIMARY KEY,
                              name TEXT,
                              update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                              insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                # Create a trigger to update the update_dt column with the current timestamp
                self.__c.execute(f'''CREATE TRIGGER {self.__conv_tb_tr_nm}
                             AFTER UPDATE ON {self.__conv_tb_nm}
                             FOR EACH ROW
                             BEGIN
                               UPDATE {self.__conv_tb_nm}
                               SET update_dt=CURRENT_TIMESTAMP
                               WHERE id=OLD.id;
                             END;''')
                # Commit the transaction
                self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")
            raise

    def selectAllInfo(self):
        """
        select all info
        """
        try:
            # filter bool type fields
            bool_type_column = [row[1] for row in self.__c.execute(f'PRAGMA table_info({self.__info_tb_nm})').fetchall() if row[2] == 'BOOL']

            # Execute the SELECT statement
            self.__c.execute(f'SELECT {",".join(list(self.__attr_default_value.keys()))} FROM {self.__info_tb_nm}')

            # Get the column names
            column_names = [description[0] for description in self.__c.description]

            rows = self.__c.fetchall()

            info_dict_arr = []

            # Get the rows with field names and values
            for row in rows:
                info_dict = {}
                for i, value in enumerate(row):
                    if column_names[i] in bool_type_column:
                        value = True if value == 1 else False
                    info_dict[column_names[i]] = value
                info_dict_arr.append(info_dict)

            return info_dict_arr
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")
            raise

    def selectInfo(self, id):
        """
        select specific info
        """
        try:
            # filter bool type fields
            bool_type_column = [row[1] for row in self.__c.execute(f'PRAGMA table_info({self.__info_tb_nm})').fetchall() if row[2] == 'BOOL']

            # Execute the SELECT statement
            self.__c.execute(f'SELECT {",".join(list(self.__attr_default_value.keys()))} FROM {self.__info_tb_nm} WHERE id={id}')

            # Get the column names
            column_names = [description[0] for description in self.__c.description]

            row = self.__c.fetchone()

            info_dict = {}
            for i, value in enumerate(row):
                if column_names[i] in bool_type_column:
                    value = True if value == 1 else False
                info_dict[column_names[i]] = value

            return info_dict
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")
            raise

    def selectAllConv(self):
        """
        select all conv
        """
        try:
            self.__c.execute(f'SELECT * FROM {self.__conv_tb_nm}')
            return self.__c.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectConv(self, id):
        """
        select specific conv
        """
        try:
            self.__c.execute(f'SELECT * FROM {self.__conv_tb_nm} WHERE id={id}')
            return self.__c.fetchone()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def insertConv(self, name):
        try:
            # Insert a row into the table
            self.__c.execute(f'INSERT INTO {self.__conv_tb_nm} (name) VALUES (?)', (name,))
            new_id = self.__c.lastrowid
            # Commit the transaction
            self.__conn.commit()
            self.__createConvUnit(new_id)
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def updateConv(self, id, name):
        try:
            self.__c.execute(f'UPDATE {self.__conv_tb_nm} SET name=(?) WHERE id={id}', (name,))
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def deleteConv(self, id):
        try:
            self.__c.execute(f'DELETE FROM {self.__conv_tb_nm} WHERE id={id}')
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def __createConvUnit(self, id_fk):
        try:
            # Check if the table exists
            self.__c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__conv_unit_tb_nm}{id_fk}'")
            if self.__c.fetchone()[0] == 1:
                # each conv table already exists
                pass
            else:
                self.__c.execute(f'''CREATE TABLE {self.__conv_unit_tb_nm}{id_fk}
                                         (id INTEGER PRIMARY KEY,
                                          id_fk INTEGER,
                                          is_user INTEGER,
                                          conv TEXT,
                                          update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                          insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                          FOREIGN KEY (id_fk) REFERENCES {self.__conv_tb_nm}(id) ON DELETE CASCADE)''')

                # insert trigger
                self.__c.execute(f'''
                    CREATE TRIGGER conv_tb_updated_by_unit_inserted_tr{id_fk}
                    AFTER INSERT ON {self.__conv_unit_tb_nm}{id_fk}
                    BEGIN
                      UPDATE {self.__conv_tb_nm} SET update_dt = CURRENT_TIMESTAMP WHERE id = NEW.id_fk;
                    END
                ''')

                # update trigger
                self.__c.execute(f'''
                    CREATE TRIGGER conv_tb_updated_by_unit_updated_tr{id_fk}
                    AFTER UPDATE ON {self.__conv_unit_tb_nm}{id_fk}
                    BEGIN
                      UPDATE {self.__conv_tb_nm} SET update_dt = CURRENT_TIMESTAMP WHERE id = NEW.id_fk;
                    END
                ''')

                # delete trigger
                self.__c.execute(f'''
                    CREATE TRIGGER conv_tb_updated_by_unit_deleted_tr{id_fk}
                    AFTER DELETE ON {self.__conv_unit_tb_nm}{id_fk}
                    BEGIN
                      UPDATE {self.__conv_tb_nm} SET update_dt = CURRENT_TIMESTAMP WHERE id = OLD.id_fk;
                    END
                ''')
                # Commit the transaction
                self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectConvUnit(self, id):
        self.__c.execute(f'SELECT * FROM {self.getConvUnitTableName()}{id}')
        return [elem[3] for elem in self.__c.fetchall()]

    def insertConvUnit(self, id, user_f, conv):
        try:
            # Insert a row into the table
            self.__c.execute(
                f'INSERT INTO {self.__conv_unit_tb_nm}{id} (id_fk, is_user, conv) VALUES (?, ?, ?)',
                (id, user_f, conv,))
            # Commit the transaction
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def export(self, ids, saved_filename):
        shutil.copy2(self.__db_filename, saved_filename)
        conn = sqlite3.connect(saved_filename)

        placeholders = ','.join('?' for _ in ids)
        cursor = conn.cursor()
        for i in range(len(ids)):
            delete_conv_q = f"DELETE FROM {self.__conv_tb_nm} WHERE id in ({placeholders})"
            cursor.execute(delete_conv_q, ids)
            drop_conv_unit_tb_q = f"DROP TABLE {self.__conv_unit_tb_nm}{ids[i]}"
            cursor.execute(drop_conv_unit_tb_q)
            conn.commit()

        conn.close()

    def convertJsonIntoSql(self):
        try:
            # Read data from json
            with open('test/conv_history.json', 'r') as f:
                data = json.load(f)
                for obj in list(data.values())[0]:
                    id, title, conv_data = obj.values()
                    # start from 1 in sql unlike json which starts from 0
                    id += 1
                    self.insertConv(title)
                    for i in range(len(conv_data)):
                        # Insert a row into the table
                        self.__c.execute(
                            f'INSERT INTO {self.__conv_unit_tb_nm}{id} (id_fk, is_user, conv) VALUES (?, ?, ?)',
                            (id, i % 2 == 0, conv_data[i],))
                        # Commit the transaction
                        self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def getCursor(self):
        return self.__c

    def getConvTableName(self):
        return self.__conv_tb_nm

    def getConvUnitTableName(self):
        return self.__conv_unit_tb_nm

    def close(self):
        self.__conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the connection
        self.__conn.close()