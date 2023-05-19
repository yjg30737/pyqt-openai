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

        # conv table names
        self.__conv_tb_nm = 'conv_tb'
        self.__conv_tb_tr_nm = 'conv_tr'
        self.__conv_unit_tb_nm = 'conv_unit_tb'

        # info table names
        self.__info_tb_nm = 'info_tb'
        self.__completion_info_tb_nm = 'info_completion_tb'

        # prompt table
        self.__prop_prompt_group_tb_nm = 'prop_prompt_grp_tb'
        self.__prop_prompt_unit_tb_nm = 'prop_prompt_unit_tb'

        self.__template_prompt_tb_nm = 'template_prompt_tb'

        # model type (chat, etc.)
        self.__model_type = 1

        # default value of each properties based on https://platform.openai.com/docs/api-reference/chat/create
        # GPT-3.5(ChatGPT), GPT-4
        self.__chat_default_value = {
            'engine': "gpt-3.5-turbo",
            'system': "You are a helpful assistant.",
            'temperature': 0.7,
            # -1 means infinite, not currently used in this application
            'max_tokens': -1,
            'top_p': 1,
            'frequency_penalty': 0,
            'presence_penalty': 0,
            'stream': True
        }

        # GPT-3, etc.
        self.__completion_default_value = {
            'engine': "text-davinci-003",
            'temperature': 0.7,
            'max_tokens': 4096,
            'top_p': 1,
            'frequency_penalty': 0,
            'presence_penalty': 0,
        }

        # DALL-E
        self.__image_default_value = {
            'engine': "DALL-E",
            'n': 1,
            'width': 1024,
            'height': 1024,
            # 'response_format':
        }

        self.__each_info_dict = {1: [self.__info_tb_nm, self.__chat_default_value],
                                 2: [self.__completion_info_tb_nm, self.__completion_default_value], }

        self.__prop_prompt_unit_default_value = [{'name': 'Task', 'text': ''},
                                                 {'name': 'Topic', 'text': ''},
                                                 {'name': 'Style', 'text': ''},
                                                 {'name': 'Tone', 'text': ''},
                                                 {'name': 'Audience', 'text': ''},
                                                 {'name': 'Length', 'text': ''},
                                                 {'name': 'Form', 'text': ''}]

        # based on Alex Brogan's prompt example
        self.__template_prompt_default_value = [
            {'name': 'Sample 1',
             'text': 'Identify the 20% of [topic or skill] that will yield 80% of the desired results and provide a focused learning plan to master it.'},
             {'name': 'Sample 2',
              'text': 'Explain [topic or skill] in the simplest terms possible as if teaching it to a complete beginner. Identify gaps in my understanding and suggest resources to fill them.'},
              {'name': 'Sample 3',
               'text': 'Create a study plan that mixes different topics or skills within [subject area] to help me develop a more robust understanding and facilitate connections between them.'},
               {'name': 'Sample 4',
                'text': 'Design a spaced repetition schedule for me to effectively review [topic or skill] over time, ensuring better retention and recall.'},
                {'name': 'Sample 5',
                 'text': 'Help me create mental models or analogies to better understand and remember key concepts in [topic or skill].'},
                 {'name': 'Sample 6',
                  'text': 'Suggest various learning resources (e.g., videos, books, podcasts, interactive exercises) for [topic or skill] that cater to different learning styles.'},
                  {'name': 'Sample 7',
                   'text': 'Provide me with a series of challenging questions or problems related to [topic or skill] to test my understanding and improve long-term retention.'},
                   {'name': 'Sample 8',
                    'text': 'Transform key concepts or lessons from [topic or skill] into engaging stories or narratives to help me better remember and understand the material.'},
                    {'name': 'Sample 9',
                     'text': 'Design a deliberate practice routine for [topic or skill], focusing on my weaknesses and providing regular feedback for improvement.'},
                     {'name': 'Sample 10',
                      'text': 'Guide me through a visualization exercise to help me internalize [topic or skill] and imagine myself succesfully applying it in real-life situations.'}
        ]

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

    def __createChat(self):
        # Check if the table exists
        self.__c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__info_tb_nm}'")
        if self.__c.fetchone()[0] == 1:
            # Check if each column already exists in the table
            existing_columns = [row[1] for row in self.__c.execute(f"PRAGMA table_info({self.__info_tb_nm});")]
            new_columns = [col for col in self.__chat_default_value.keys() if col not in existing_columns]
            # Add the new columns if they don't already exist
            # TODO specify the type
            for col in new_columns:
                d_value = self.__chat_default_value[col]
                if isinstance(self.__chat_default_value[col], str):
                    d_value = f'"{d_value}"' if len(self.__chat_default_value[col].split()) > 0 else d_value
                self.__c.execute(f"ALTER TABLE {self.__info_tb_nm} ADD COLUMN {col} DEFAULT {d_value}")
        else:
            self.__c.execute(f'''CREATE TABLE {self.__info_tb_nm}
                                     (id INTEGER PRIMARY KEY,
                                      engine VARCHAR(50) DEFAULT '{self.__chat_default_value['engine']}',
                                      system TEXT DEFAULT '{self.__chat_default_value['system']}',
                                      temperature INTEGER DEFAULT {self.__chat_default_value['temperature']},
                                      max_tokens INTEGER DEFAULT {self.__chat_default_value['max_tokens']},
                                      top_p INTEGER DEFAULT {self.__chat_default_value['top_p']},
                                      frequency_penalty INTEGER DEFAULT {self.__chat_default_value['frequency_penalty']},
                                      presence_penalty INTEGER DEFAULT {self.__chat_default_value['presence_penalty']},
                                      stream BOOL DEFAULT {self.__chat_default_value['stream']},

                                      update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                      insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')

            # Commit the transaction
            self.__conn.commit()

            # insert default record
            self.__c.execute(f'''INSERT INTO {self.__info_tb_nm}
                                            (
                                                engine,
                                                system,
                                                temperature,
                                                max_tokens,
                                                top_p,
                                                frequency_penalty,
                                                presence_penalty,
                                                stream
                                            ) VALUES
                                            (
                                                {','.join(['?' for _ in range(len(self.__chat_default_value))])}
                                            )
                                         ''', tuple(self.__chat_default_value.values()))

    def __createCompletion(self):
        # Check if the table exists
        self.__c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__completion_info_tb_nm}'")
        if self.__c.fetchone()[0] == 1:
            pass
        else:
            self.__c.execute(f'''CREATE TABLE {self.__completion_info_tb_nm}
                                             (id INTEGER PRIMARY KEY,
                                              engine VARCHAR(50) DEFAULT '{self.__completion_default_value['engine']}',
                                              temperature INTEGER DEFAULT {self.__completion_default_value['temperature']},
                                              max_tokens INTEGER DEFAULT {self.__completion_default_value['max_tokens']},
                                              top_p INTEGER DEFAULT {self.__completion_default_value['top_p']},
                                              frequency_penalty INTEGER DEFAULT {self.__completion_default_value['frequency_penalty']},
                                              presence_penalty INTEGER DEFAULT {self.__completion_default_value['presence_penalty']},

                                              update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                              insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')

            # Commit the transaction
            self.__conn.commit()

            # insert default record
            self.__c.execute(f'''INSERT INTO {self.__completion_info_tb_nm}
                                                    (
                                                        engine,
                                                        temperature,
                                                        max_tokens,
                                                        top_p,
                                                        frequency_penalty,
                                                        presence_penalty
                                                    ) VALUES
                                                    (
                                                        {','.join(['?' for _ in range(len(self.__completion_default_value))])}
                                                    )
                                                 ''', tuple(self.__completion_default_value.values()))

    def __createPropPromptGroup(self):
        self.__c.execute(
            f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__prop_prompt_group_tb_nm}'")
        if self.__c.fetchone()[0] == 1:
            pass
        else:
            self.__c.execute(f'''CREATE TABLE {self.__prop_prompt_group_tb_nm}
                                                 (id INTEGER PRIMARY KEY,
                                                  name VARCHAR(50),
                                                  
                                                  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                                  insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')

            # Commit the transaction
            self.__conn.commit()

            self.insertPropPromptGroup('Default')

    def createDefaultPropPromptAttributes(self, id_fk):
        self.__c.execute(
            f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__prop_prompt_unit_tb_nm}{id_fk}'")
        if self.__c.fetchone()[0] == 1:
            pass
        else:
            self.__c.execute(f'''CREATE TABLE {self.__prop_prompt_unit_tb_nm}{id_fk}
                                                             (id INTEGER PRIMARY KEY,
                                                              id_fk INTEGER,
                                                              name VARCHAR(50),
                                                              text TEXT,
                                                              update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                                              insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                                              FOREIGN KEY (id_fk) REFERENCES {self.__prop_prompt_group_tb_nm}(id)
                                                              ON DELETE CASCADE)''')

        # insert default property group
        for obj in self.__prop_prompt_unit_default_value:
            lst = [id_fk] + list(tuple(obj.values()))
            self.__c.execute(f"INSERT INTO {self.__prop_prompt_unit_tb_nm}{id_fk} (id_fk, name, text) VALUES (?, ?, ?)", tuple(lst))

        # Commit the transaction
        self.__conn.commit()

    def selectPropPromptAttribute(self, id):
        try:
            self.__c.execute(f'SELECT * FROM {self.__prop_prompt_unit_tb_nm}{id}')
            return self.__c.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def insertPropPromptAttribute(self, id, name):
        try:
            # Insert a row into the table
            self.__c.execute(f'INSERT INTO {self.__prop_prompt_unit_tb_nm}{id} (id_fk, name) VALUES (?, ?)', (id, name,))
            new_id = self.__c.lastrowid
            # Commit the transaction
            self.__conn.commit()
            return new_id
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def updatePropPromptAttribute(self, p_id, id, name, text):
        try:
            self.__c.execute(f'UPDATE {self.__prop_prompt_unit_tb_nm}{p_id} SET name=?, text=? WHERE id={id}', (name, text))
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def deletePropPromptAttribute(self, p_id, id):
        try:
            self.__c.execute(f'DELETE FROM {self.__prop_prompt_unit_tb_nm}{p_id} WHERE id={id}')
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectPropPromptGroup(self):
        try:
            self.__c.execute(f'SELECT * FROM {self.__prop_prompt_group_tb_nm}')
            return self.__c.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectPropPromptGroupId(self, id):
        try:
            self.__c.execute(f'SELECT * FROM {self.__prop_prompt_group_tb_nm} WHERE id={id}')
            return self.__c.fetchone()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def insertPropPromptGroup(self, name):
        try:
            # Insert a row into the table
            self.__c.execute(f'INSERT INTO {self.__prop_prompt_group_tb_nm} (name) VALUES (?)', (name,))
            new_id = self.__c.lastrowid
            # Commit the transaction
            self.__conn.commit()
            # insert default attributes
            self.createDefaultPropPromptAttributes(new_id)
            # TODO abcd make others insert statement return like this
            return new_id
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def updatePropPromptGroup(self, id, name):
        try:
            self.__c.execute(f'UPDATE {self.__prop_prompt_group_tb_nm} SET name=(?) WHERE id={id}', (name,))
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def deletePropPromptGroup(self, id):
        try:
            self.__c.execute(f'DELETE FROM {self.__prop_prompt_group_tb_nm} WHERE id={id}')
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def __createTemplatePrompt(self):
        self.__c.execute(
            f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{self.__template_prompt_tb_nm}'")
        if self.__c.fetchone()[0] == 1:
            pass
        else:
            self.__c.execute(f'''CREATE TABLE {self.__template_prompt_tb_nm}
                                                 (id INTEGER PRIMARY KEY,
                                                  name VARCHAR(50),
                                                  text TEXT,
                                                  update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                                  insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')

            # Commit the transaction
            self.__conn.commit()

            # insert default template set
            for obj in self.__template_prompt_default_value:
                self.__c.execute(f"INSERT INTO {self.__template_prompt_tb_nm} (name, text) VALUES (?, ?)", tuple(obj.values()))

    def selectTemplatePrompt(self):
        try:
            self.__c.execute(f'SELECT * FROM {self.__template_prompt_tb_nm}')
            return self.__c.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def insertTemplatePrompt(self, name):
        try:
            # Insert a row into the table
            self.__c.execute(f"INSERT INTO {self.__template_prompt_tb_nm} (name, text) VALUES (?, ?)",
                             (name, ''))
            new_id = self.__c.lastrowid
            # Commit the transaction
            self.__conn.commit()
            return new_id
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def updateTemplatePrompt(self, id, name, text):
        try:
            self.__c.execute(f'UPDATE {self.__template_prompt_tb_nm} SET name=(?), text=(?) WHERE id={id}', (name, text))
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def deleteTemplatePrompt(self, id):
        try:
            self.__c.execute(f'DELETE FROM {self.__template_prompt_tb_nm} WHERE id={id}')
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def __createInfo(self):
        try:
            # chat and completion information
            self.__createChat()
            self.__createCompletion()

            # prompt information
            self.__createPropPromptGroup()
            self.__createTemplatePrompt()

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
        FIXME
        """
        try:
            # filter bool type fields
            bool_type_column = [row[1] for row in self.__c.execute(f'PRAGMA table_info({self.__info_tb_nm})').fetchall() if row[2] == 'BOOL']

            # Execute the SELECT statement
            self.__c.execute(f'SELECT {",".join(list(self.__chat_default_value.keys()))} FROM {self.__info_tb_nm}')

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
        """
        select specific info
        default value is 1 (chat - gpt3.5, gpt4, etc.)
        """
        try:
            # default value is 1 (chat - gpt3.5, gpt4, etc.)
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