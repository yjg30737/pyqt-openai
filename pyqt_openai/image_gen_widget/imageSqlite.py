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
        self.__createImage()

    def __initVal(self):
        # db names
        self.__db_filename = 'image.db'

        # image table names
        self.__image_tb_nm = 'image_tb'
        self.__image_tb_tr_nm = 'image_tr'
        self.__image_unit_tb_nm = 'image_unit_tb'

        # info table names
        self.__dall_e_info_tb_nm = 'dall_e_info_tb'
        self.__stable_diffusion_info_tb_nm = 'stable_diffusion_tb'

        # model type (chat, etc.)
        self.__model_type = 1

        # DALL-E
        self.__image_dall_e_default_value = {
            'engine': "DALL-E",
            'n': 1,
            'width': 1024,
            'height': 1024,
            # 'response_format':
        }
        
        # SD
        self.__image_sd_default_value = {
            'height': 512,
            'width': 512,
            'steps': 30,
            'samples': 1,
            'cfg_scale': 7,
            'engine': 'stable-diffusion-xl-beta-v2-2-2',
            'sampler': 'k_dpmpp_2m',
            'seed': 0, # random
        }
        
        self.__each_info_dict = {1: [self.__dall_e_info_tb_nm, self.__image_dall_e_default_value],
                                 2: [self.__stable_diffusion_info_tb_nm, self.__image_sd_default_value], }

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

    def __createDallE(self):
        # Check if the table exists
        self.__c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__dall_e_info_tb_nm}'")
        if self.__c.fetchone()[0] == 1:
            # Check if each column already exists in the table
            existing_columns = [row[1] for row in self.__c.execute(f"PRAGMA table_info({self.__dall_e_info_tb_nm});")]
            new_columns = [col for col in self.__image_dall_e_default_value.keys() if col not in existing_columns]
            # Add the new columns if they don't already exist
            # TODO specify the type
            for col in new_columns:
                d_value = self.__image_dall_e_default_value[col]
                if isinstance(self.__image_dall_e_default_value[col], str):
                    d_value = f'"{d_value}"' if len(self.__image_dall_e_default_value[col].split()) > 0 else d_value
                self.__c.execute(f"ALTER TABLE {self.__dall_e_info_tb_nm} ADD COLUMN {col} DEFAULT {d_value}")
        else:
            self.__c.execute(f'''CREATE TABLE {self.__dall_e_info_tb_nm}
                                     (id INTEGER PRIMARY KEY,
                                      n TEXT DEFAULT '{self.__image_dall_e_default_value['n']}',
                                      width INTEGER DEFAULT {self.__image_dall_e_default_value['width']},
                                      height INTEGER DEFAULT {self.__image_dall_e_default_value['height']},
                                      update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                      insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')

            # Commit the transaction
            self.__conn.commit()

            # insert default record
            self.__c.execute(f'''INSERT INTO {self.__dall_e_info_tb_nm}
                                            (
                                                n,
                                                width,
                                                height
                                            ) VALUES
                                            (
                                                {','.join(['?' for _ in range(len(self.__image_dall_e_default_value))])}
                                            )
                                         ''', tuple(self.__image_dall_e_default_value.values()))

    def __createStableDiffusion(self):
        # Check if the table exists
        self.__c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__stable_diffusion_info_tb_nm}'")
        if self.__c.fetchone()[0] == 1:
            pass
        else:
            self.__c.execute(f'''CREATE TABLE {self.__stable_diffusion_info_tb_nm}
                                             (
                                                id INTEGER PRIMARY KEY,
                                                height INTEGER DEFAULT '{self.__image_sd_default_value['height']},
                                                width INTEGER DEFAULT '{self.__image_sd_default_value['width']},
                                                steps INTEGER DEFAULT '{self.__image_sd_default_value['steps']},
                                                samples INTEGER DEFAULT '{self.__image_sd_default_value['samples']},
                                                cfg_scale INTEGER DEFAULT '{self.__image_sd_default_value['cfg_scale']},
                                                engine VARCHAR(50) DEFAULT '{self.__image_sd_default_value['engine']},
                                                sampler VARCHAR(50) DEFAULT '{self.__image_sd_default_value['sampler']},
                                                seed INTEGER DEFAULT '{self.__image_sd_default_value['seed']},
                                              update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                              insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')

            # Commit the transaction
            self.__conn.commit()

            # insert default record
            self.__c.execute(f'''INSERT INTO {self.__stable_diffusion_info_tb_nm}
                                                    (
                                                        height,
                                                        width,
                                                        steps,
                                                        samples,
                                                        cfg_scale,
                                                        engine,
                                                        sampler,
                                                        seed
                                                    ) VALUES
                                                    (
                                                        {','.join(['?' for _ in range(len(self.__image_sd_default_value))])}
                                                    )
                                                 ''', tuple(self.__image_sd_default_value.values()))

    def __createInfo(self):
        try:
            self.__createDallE()
            self.__createStableDiffusion()
            # Commit the transaction
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")
            raise

    def __createImage(self):
        try:
            # Check if the table exists
            self.__c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__image_tb_nm}'")
            if self.__c.fetchone()[0] == 1:
                # each image table already exists
                pass
            else:
                # Create a table with update_dt and insert_dt columns
                self.__c.execute(f'''CREATE TABLE {self.__image_tb_nm}
                             (id INTEGER PRIMARY KEY,
                              name TEXT,
                              update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                              insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                # Create a trigger to update the update_dt column with the current timestamp
                self.__c.execute(f'''CREATE TRIGGER {self.__image_tb_tr_nm}
                             AFTER UPDATE ON {self.__image_tb_nm}
                             FOR EACH ROW
                             BEGIN
                               UPDATE {self.__image_tb_nm}
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
        FIXME
        """
        try:
            # filter bool type fields
            bool_type_column = [row[1] for row in self.__c.execute(f'PRAGMA table_info({self.__dall_e_info_tb_nm})').fetchall() if row[2] == 'BOOL']

            # Execute the SELECT statement
            self.__c.execute(f'SELECT {",".join(list(self.__image_dall_e_default_value.keys()))} FROM {self.__dall_e_info_tb_nm}')

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

    def selectInfo(self, id=None):
        try:
            id = id if id else self.__model_type

            # filter bool type fields
            bool_type_column = [row[1] for row in self.__c.execute(f'PRAGMA table_info({self.__each_info_dict[id][0]})').fetchall() if row[2] == 'BOOL']

            # Execute the SELECT statement
            self.__c.execute(f'SELECT {",".join(list(self.__each_info_dict[id][1].keys()))} FROM {self.__each_info_dict[id][0]}')

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

    def updateInfo(self, id, field, value):
        try:
            self.__c.execute(f'UPDATE {self.__each_info_dict[id][0]} SET {field}=(?) WHERE id=1', (value,))
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectAllImage(self):
        """
        select all image
        """
        try:
            self.__c.execute(f'SELECT * FROM {self.__image_tb_nm}')
            return self.__c.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectImage(self, id):
        """
        select specific image
        """
        try:
            self.__c.execute(f'SELECT * FROM {self.__image_tb_nm} WHERE id={id}')
            return self.__c.fetchone()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def insertImage(self, name):
        try:
            # Insert a row into the table
            self.__c.execute(f'INSERT INTO {self.__image_tb_nm} (name) VALUES (?)', (name,))
            new_id = self.__c.lastrowid
            # Commit the transaction
            self.__conn.commit()
            self.__createImageUnit(new_id)
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def updateImage(self, id, name):
        try:
            self.__c.execute(f'UPDATE {self.__image_tb_nm} SET name=(?) WHERE id={id}', (name,))
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def deleteImage(self, id):
        try:
            self.__c.execute(f'DELETE FROM {self.__image_tb_nm} WHERE id={id}')
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def __createImageUnit(self, id_fk):
        try:
            # Check if the table exists
            self.__c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__image_unit_tb_nm}{id_fk}'")
            if self.__c.fetchone()[0] == 1:
                # each image table already exists
                pass
            else:
                self.__c.execute(f'''CREATE TABLE {self.__image_unit_tb_nm}{id_fk}
                                         (id INTEGER PRIMARY KEY,
                                          id_fk INTEGER,
                                          is_user INTEGER,
                                          image TEXT,
                                          update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                          insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                          FOREIGN KEY (id_fk) REFERENCES {self.__image_tb_nm}(id) ON DELETE CASCADE)''')

                # insert trigger
                self.__c.execute(f'''
                    CREATE TRIGGER image_tb_updated_by_unit_inserted_tr{id_fk}
                    AFTER INSERT ON {self.__image_unit_tb_nm}{id_fk}
                    BEGIN
                      UPDATE {self.__image_tb_nm} SET update_dt = CURRENT_TIMESTAMP WHERE id = NEW.id_fk;
                    END
                ''')

                # update trigger
                self.__c.execute(f'''
                    CREATE TRIGGER image_tb_updated_by_unit_updated_tr{id_fk}
                    AFTER UPDATE ON {self.__image_unit_tb_nm}{id_fk}
                    BEGIN
                      UPDATE {self.__image_tb_nm} SET update_dt = CURRENT_TIMESTAMP WHERE id = NEW.id_fk;
                    END
                ''')

                # delete trigger
                self.__c.execute(f'''
                    CREATE TRIGGER image_tb_updated_by_unit_deleted_tr{id_fk}
                    AFTER DELETE ON {self.__image_unit_tb_nm}{id_fk}
                    BEGIN
                      UPDATE {self.__image_tb_nm} SET update_dt = CURRENT_TIMESTAMP WHERE id = OLD.id_fk;
                    END
                ''')
                # Commit the transaction
                self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectImageUnit(self, id):
        self.__c.execute(f'SELECT * FROM {self.getImageUnitTableName()}{id}')
        return [elem[3] for elem in self.__c.fetchall()]

    def insertImageUnit(self, id, user_f, image):
        try:
            # Insert a row into the table
            self.__c.execute(
                f'INSERT INTO {self.__image_unit_tb_nm}{id} (id_fk, is_user, image) VALUES (?, ?, ?)',
                (id, user_f, image,))
            # Commit the transaction
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def setModelType(self, model_type: int):
        """
        :param model_type: it starts from 1
        :return:
        """
        self.__model_type = model_type

    def export(self, ids, saved_filename):
        shutil.copy2(self.__db_filename, saved_filename)
        conn = sqlite3.connect(saved_filename)

        placeholders = ','.join('?' for _ in ids)
        cursor = conn.cursor()
        for i in range(len(ids)):
            delete_image_q = f"DELETE FROM {self.__image_tb_nm} WHERE id in ({placeholders})"
            cursor.execute(delete_image_q, ids)
            drop_image_unit_tb_q = f"DROP TABLE {self.__image_unit_tb_nm}{ids[i]}"
            cursor.execute(drop_image_unit_tb_q)
            conn.commit()

        conn.close()

    def imageertJsonIntoSql(self):
        try:
            # Read data from json
            with open('test/image_history.json', 'r') as f:
                data = json.load(f)
                for obj in list(data.values())[0]:
                    id, title, image_data = obj.values()
                    # start from 1 in sql unlike json which starts from 0
                    id += 1
                    self.insertImage(title)
                    for i in range(len(image_data)):
                        # Insert a row into the table
                        self.__c.execute(
                            f'INSERT INTO {self.__image_unit_tb_nm}{id} (id_fk, is_user, image) VALUES (?, ?, ?)',
                            (id, i % 2 == 0, image_data[i],))
                        # Commit the transaction
                        self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def getCursor(self):
        return self.__c

    def getImageTableName(self):
        return self.__image_tb_nm

    def getImageUnitTableName(self):
        return self.__image_unit_tb_nm

    def close(self):
        self.__conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the connection
        self.__conn.close()