import json
import sqlite3
from datetime import datetime
from typing import List
from qtpy.QtCore import QSettings

from pyqt_openai import THREAD_TABLE_NAME, THREAD_TRIGGER_NAME, \
    THREAD_TABLE_NAME_OLD, \
    THREAD_TRIGGER_NAME_OLD, MESSAGE_TABLE_NAME_OLD, MESSAGE_TABLE_NAME, THREAD_MESSAGE_INSERTED_TR_NAME, \
    THREAD_MESSAGE_UPDATED_TR_NAME, THREAD_MESSAGE_DELETED_TR_NAME, THREAD_MESSAGE_INSERTED_TR_NAME_OLD, \
    THREAD_MESSAGE_UPDATED_TR_NAME_OLD, THREAD_MESSAGE_DELETED_TR_NAME_OLD, IMAGE_TABLE_NAME, \
    PROPERTY_PROMPT_UNIT_TABLE_NAME_OLD, PROPERTY_PROMPT_GROUP_TABLE_NAME_OLD, TEMPLATE_PROMPT_GROUP_TABLE_NAME_OLD, \
    TEMPLATE_PROMPT_TABLE_NAME_OLD, PROMPT_GROUP_TABLE_NAME, PROMPT_ENTRY_TABLE_NAME, INI_FILE_NAME, DB_FILE_NAME
from pyqt_openai.models import ImagePromptContainer, ChatMessageContainer, PromptEntryContainer, PromptGroupContainer


def get_db_filename():
    """
    Get the database file's name from the settings.
    """
    settings = QSettings(INI_FILE_NAME, QSettings.Format.IniFormat)
    db_path = settings.value("db", DB_FILE_NAME) + ".db"
    return db_path


class SqliteDatabase:
    """
    Functions which only meant to be used frequently are defined.
    If there is no functions you want to use, use ``getCursor`` instead.
    """
    def __init__(self, db_filename=get_db_filename()):
        super().__init__()
        self.__initVal(db_filename)
        self.__initDb()

    def __initVal(self, db_filename):
        # DB file name
        self.__db_filename = db_filename or get_db_filename()

    def __initDb(self):
        try:
            # Connect to the database (create a new file if it doesn't exist)
            self.__conn = sqlite3.connect(self.__db_filename)
            self.__conn.row_factory = sqlite3.Row
            self.__conn.execute('PRAGMA foreign_keys = ON;')
            self.__conn.commit()

            # create cursor
            self.__c = self.__conn.cursor()

            # create conversation tables
            self.__createThread()

            # create prompt tables
            self.__createPromptGroup()

            # create image tables
            self.__createImage()
        except sqlite3.Error as e:
            print(f"An error occurred while connecting to the database: {e}")
            raise

    def __createPromptGroup(self):
        try:
            self.__c.execute(
                f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{PROMPT_GROUP_TABLE_NAME}'")
            if self.__c.fetchone()[0] == 1:
                pass
            else:
                self.__c.execute(f'''CREATE TABLE {PROMPT_GROUP_TABLE_NAME}
                                     (id INTEGER PRIMARY KEY,
                                      name VARCHAR(255),
                                      prompt_type VARCHAR(255),
                                      update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                      insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                # Create prompt entry
                self.__createPromptEntry()

                # Will remove after v1.0.0
                # Alter old prompt group table to new one
                self.__alterOldPromptGroup()

                # Will remove after v1.0.0
                # Remove old prompt group
                self.__removeOldPromptGroup()

                # Will remove after v1.0.0
                # Remove old prompt entry
                self.__removeOldPromptEntry()

                # Commit the transaction
                self.__conn.commit()

                # self.insertPropPromptGroup('Default')
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")
            raise

    def __alterOldPromptGroup(self):
        try:
            # Move to new prompt group table if the old prop table exists
            table_name_old_exists = self.__c.execute(
                f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{PROPERTY_PROMPT_GROUP_TABLE_NAME_OLD}'").fetchone()[
                                        0] == 1
            if table_name_old_exists:
                prop_prompt_groups = self.selectPropPromptGroup()
                for group in prop_prompt_groups:
                    group_id = self.insertPromptGroup(group['name'], prompt_type='form')
                    prompt_entries = self.selectPropPromptAttribute(group['id'])
                    for prompt_entry in prompt_entries:
                        self.insertPromptEntry(group_id, prompt_entry['name'], prompt_entry['text'])

            # Move to new prompt group table if the old template table exists
            table_name_old_exists = self.__c.execute(
                f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{TEMPLATE_PROMPT_GROUP_TABLE_NAME_OLD}'").fetchone()[
                                        0] == 1
            if table_name_old_exists:
                template_prompt_group = self.selectTemplatePromptGroup()
                for group in template_prompt_group:
                    group_id = self.insertPromptGroup(group['name'], prompt_type='sentence')
                    prompt_entries = self.selectTemplatePromptUnit(group['id'])
                    for prompt_entry in prompt_entries:
                        self.insertPromptEntry(group_id, prompt_entry['name'], prompt_entry['text'])
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def __removeOldPromptGroup(self):
        if self.__c.execute(
                f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{PROPERTY_PROMPT_GROUP_TABLE_NAME_OLD}'").fetchone()[0] == 1:
            self.__c.execute(f'DROP TABLE {PROPERTY_PROMPT_GROUP_TABLE_NAME_OLD}')
        if self.__c.execute(
                f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{TEMPLATE_PROMPT_GROUP_TABLE_NAME_OLD}'").fetchone()[0] == 1:
            self.__c.execute(f'DROP TABLE {TEMPLATE_PROMPT_GROUP_TABLE_NAME_OLD}')

    def __removeOldPromptEntry(self):
        self.__c.execute(f'''
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
                AND name LIKE '%{PROPERTY_PROMPT_UNIT_TABLE_NAME_OLD}%' OR name LIKE '%{TEMPLATE_PROMPT_TABLE_NAME_OLD}%'
            ''')
        for name in self.__c.fetchall():
            self.__c.execute(f'DROP TABLE {name[0]}')

    def insertPromptGroup(self, name, prompt_type):
        try:
            # Insert a row into the table
            self.__c.execute(f'INSERT INTO {PROMPT_GROUP_TABLE_NAME} (name, prompt_type) VALUES (?, ?)', (name,
                                                                                                          prompt_type))
            new_id = self.__c.lastrowid
            # Commit the transaction
            self.__conn.commit()
            return new_id
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectPromptGroup(self, prompt_type=None):
        try:
            query = f'SELECT * FROM {PROMPT_GROUP_TABLE_NAME}'
            if prompt_type == 'form':
                query += f' WHERE prompt_type="form"'
            elif prompt_type == 'sentence':
                query += f' WHERE prompt_type="sentence"'
            self.__c.execute(query)
            return [PromptGroupContainer(**elem) for elem in self.__c.fetchall()]
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectCertainPromptGroup(self, id=None, name=None):
        """
        Select specific prompt group by id or name
        """
        try:
            query = f'SELECT * FROM {PROMPT_GROUP_TABLE_NAME}'
            if id or name:
                query += ' WHERE'
                if id:
                    query += f' id={id}'
                    if name:
                        query += ' AND'
                if name:
                    query += f' name="{name}"'
            result = self.__c.execute(query).fetchone()
            if result:
                return PromptGroupContainer(**result)
            else:
                return None
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def updatePromptGroup(self, id, name):
        try:
            self.__c.execute(f'UPDATE {PROMPT_GROUP_TABLE_NAME} SET name=? WHERE id={id}', (name))
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def deletePromptGroup(self, id=None):
        try:
            query = f'DELETE FROM {PROMPT_GROUP_TABLE_NAME}'
            if id:
                query += f' WHERE id = {id}'
            self.__c.execute(query)
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def __createPromptEntry(self):
        try:
            self.__c.execute(
                f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{PROMPT_ENTRY_TABLE_NAME}'")
            if self.__c.fetchone()[0] == 1:
                # Let it pass if the table already exists
                pass
            else:
                self.__c.execute(f'''CREATE TABLE {PROMPT_ENTRY_TABLE_NAME} (
                                    id INTEGER PRIMARY KEY,
                                    group_id INTEGER NOT NULL,
                                    name VARCHAR(255) NOT NULL,
                                    content TEXT NOT NULL,
                                    insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (group_id) REFERENCES {PROMPT_GROUP_TABLE_NAME}
                                    ON DELETE CASCADE)
                ''')
                self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def insertPromptEntry(self, group_id, name, content=''):
        try:
            # Insert a row into the table
            self.__c.execute(f'INSERT INTO {PROMPT_ENTRY_TABLE_NAME} (group_id, name, content) VALUES (?, ?, ?)',
                             (group_id, name, content))
            new_id = self.__c.lastrowid
            # Commit the transaction
            self.__conn.commit()
            return new_id
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectPromptEntry(self, group_id, id=None, name=None) -> List[PromptEntryContainer]:
        try:
            query = f'SELECT * FROM {PROMPT_ENTRY_TABLE_NAME} WHERE group_id={group_id}'
            if id:
                query += f' AND id={id}'
            if name:
                query += f' AND name="{name}"'
            return [PromptEntryContainer(**elem) for elem in self.__c.execute(query).fetchall()]
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def updatePromptEntry(self, id, name, content):
        try:
            self.__c.execute(f'UPDATE {PROMPT_ENTRY_TABLE_NAME} SET name=?, content=? WHERE id={id}', (name, content))
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def deletePromptEntry(self, group_id, id=None):
        try:
            query = f'DELETE FROM {PROMPT_ENTRY_TABLE_NAME} WHERE group_id={group_id}'
            if id:
                query += f' AND id={id}'
            self.__c.execute(query)
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectPropPromptGroup(self):
        try:
            self.__c.execute(f'SELECT * FROM {PROPERTY_PROMPT_GROUP_TABLE_NAME_OLD}')
            return self.__c.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectPropPromptAttribute(self, id):
        try:
            self.__c.execute(f'SELECT * FROM {PROPERTY_PROMPT_UNIT_TABLE_NAME_OLD}{id}')
            return self.__c.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectTemplatePromptGroup(self):
        try:
            self.__c.execute(f'SELECT * FROM {TEMPLATE_PROMPT_GROUP_TABLE_NAME_OLD}')
            return self.__c.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectTemplatePromptUnit(self, id):
        try:
            # TODO make every select statement check if it exists
            self.__c.execute(
                f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{TEMPLATE_PROMPT_TABLE_NAME_OLD}{id}'")
            if self.__c.fetchone()[0] == 1:
                self.__c.execute(f'SELECT * FROM {TEMPLATE_PROMPT_TABLE_NAME_OLD}{id}')
                return self.__c.fetchall()
            else:
                return []
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def __alterOldThread(self):
        # Check if the old thread table exists for v0.6.5 and below for migration purpose
        table_name_old_exists = self.__c.execute(
            f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{THREAD_TABLE_NAME_OLD}'").fetchone()[
                                    0] == 1
        if table_name_old_exists:
            # Rename the table (will remove this later)
            self.__c.execute(f'ALTER TABLE {THREAD_TABLE_NAME_OLD} RENAME TO {THREAD_TABLE_NAME}')
            # Alter message tables for migration purpose
            self.__alterThreadUnit()

        # Check if the old trigger table exists for v0.6.5 and below for migration purpose
        trigger_name_old_exists = self.__c.execute(
            f"SELECT count(*) FROM sqlite_master WHERE type='trigger' AND name='{THREAD_TRIGGER_NAME_OLD}'").fetchone()[0] == 1
        if trigger_name_old_exists:
            self.__c.execute(f'DROP TRIGGER {THREAD_TRIGGER_NAME_OLD}')

    def __createThread(self):
        try:
            # Will remove after v1.0.0
            # Check if the old thread table exists for v0.6.5 and below for migration purpose
            self.__alterOldThread()

            # Create new thread table if not exists
            table_name_new_exists = self.__c.execute(
                    f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{THREAD_TABLE_NAME}'").fetchone()[
                                            0] == 1
            if table_name_new_exists:
                pass
            else:
                # If user uses app for the first time, create a table
                # Create a table with update_dt and insert_dt columns
                self.__c.execute(f'''CREATE TABLE {THREAD_TABLE_NAME}
                             (id INTEGER PRIMARY KEY,
                              name TEXT,
                              update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                              insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                # Create message table
                self.__createMessage()
            # Create new thread trigger if not exists
            trigger_name_new_exists = self.__c.execute(
                f"SELECT count(*) FROM sqlite_master WHERE type='trigger' AND name='{THREAD_TRIGGER_NAME}'").fetchone()[
                                        0] == 1
            if trigger_name_new_exists:
                pass
            else:
                # Create a trigger to update the update_dt column with the current timestamp
                self.__c.execute(f'''CREATE TRIGGER {THREAD_TRIGGER_NAME}
                             AFTER UPDATE ON {THREAD_TABLE_NAME}
                             FOR EACH ROW
                             BEGIN
                               UPDATE {THREAD_TABLE_NAME}
                               SET update_dt=CURRENT_TIMESTAMP
                               WHERE id=OLD.id;
                             END;''')
            # Commit the transaction
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")
            raise

    def selectAllThread(self, id_arr=None):
        """
        Select all thread
        id_arr: list of thread id
        """
        try:
            query = f'SELECT * FROM {THREAD_TABLE_NAME}'
            if id_arr:
                query += f' WHERE id IN ({",".join(map(str, id_arr))})'
            self.__c.execute(query)
            return self.__c.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectThread(self, id):
        """
        Select specific thread
        """
        try:
            self.__c.execute(f'SELECT * FROM {THREAD_TABLE_NAME} WHERE id={id}')
            return self.__c.fetchone()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def insertThread(self, name):
        try:
            # Insert a row into the table
            self.__c.execute(f'INSERT INTO {THREAD_TABLE_NAME} (name) VALUES (?)', (name,))
            new_id = self.__c.lastrowid
            # Commit the transaction
            self.__conn.commit()
            return new_id
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def updateThread(self, id, name):
        try:
            self.__c.execute(f'UPDATE {THREAD_TABLE_NAME} SET name=(?) WHERE id={id}', (name,))
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def deleteThread(self, id=None):
        try:
            query = f'DELETE FROM {THREAD_TABLE_NAME}'
            if id:
                query += f' WHERE id = {id}'
            self.__c.execute(query)
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def __alterThreadUnit(self):
        # Make message table
        self.__createMessage()

        # search the conv unit tables
        res = self.__c.execute(f'''
                        SELECT name
                        FROM sqlite_master
                        WHERE type = 'table' AND name LIKE '{MESSAGE_TABLE_NAME_OLD}%';
                    ''')
        # UNION all old message tables to new one
        union_query = ''
        for name in res.fetchall():
            union_query += f'SELECT * FROM {name[0]}\n'
        union_query = ' UNION '.join(union_query.split('\n')[:-1]) + ' order by id_fk'

        # Insert all old message tables to new one
        res = self.__c.execute(union_query)

        arg = ChatMessageContainer()
        insert_query = arg.create_insert_query(table_name=MESSAGE_TABLE_NAME, excludes=['id'])

        for row in res.fetchall():
            row_dict = dict(row)
            row_dict['role'] = 'user' if row_dict['is_user'] == 1 else 'assistant'
            row_dict['thread_id'] = row_dict['id_fk']
            row_dict['content'] = row_dict['conv']
            del row_dict['is_user']
            del row_dict['conv']
            del row_dict['id_fk']
            arg = ChatMessageContainer(**row_dict)
            self.__c.execute(insert_query, arg.get_values_for_insert(excludes=['id']))
            self.__conn.commit()

        # Remove old message tables
        self.__removeOldMessage()

    def __removeOldMessage(self):
        # remove old message tables
        self.__c.execute(f'''
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name LIKE '%{MESSAGE_TABLE_NAME_OLD}%'
            ''')
        for name in self.__c.fetchall():
            self.__c.execute(f'DROP TABLE {name[0]}')
        self.__conn.commit()

    def __removeOldTrigger(self):
        # remove old trigger
        self.__c.execute(f'''
            SELECT name
            FROM sqlite_master
            WHERE type = 'trigger'
              AND name LIKE '%{THREAD_MESSAGE_INSERTED_TR_NAME_OLD}%'
            ''')
        for name in self.__c.fetchall():
            self.__c.execute(f'DROP TRIGGER {name[0]}')

        self.__c.execute(f'''
            SELECT name
            FROM sqlite_master
            WHERE type = 'trigger'
              AND name LIKE '%{THREAD_MESSAGE_UPDATED_TR_NAME_OLD}%'
            ''')
        for name in self.__c.fetchall():
            self.__c.execute(f'DROP TRIGGER {name[0]}')

        self.__c.execute(f'''
            SELECT name
            FROM sqlite_master
            WHERE type = 'trigger'
              AND name LIKE '%{THREAD_MESSAGE_DELETED_TR_NAME_OLD}%'
            ''')
        for name in self.__c.fetchall():
            self.__c.execute(f'DROP TRIGGER {name[0]}')
        self.__conn.commit()

    def __createMessageTrigger(self):
        """
        Create message trigger
        """
        # Create insert trigger
        self.__c.execute(f'''
            CREATE TRIGGER {THREAD_MESSAGE_INSERTED_TR_NAME}
            AFTER INSERT ON {MESSAGE_TABLE_NAME}
            BEGIN
              UPDATE {THREAD_TABLE_NAME} SET update_dt = CURRENT_TIMESTAMP WHERE id = NEW.thread_id;
            END
        ''')

        # Create update trigger
        self.__c.execute(f'''
            CREATE TRIGGER {THREAD_MESSAGE_UPDATED_TR_NAME}
            AFTER UPDATE ON {MESSAGE_TABLE_NAME}
            BEGIN
              UPDATE {THREAD_TABLE_NAME} SET update_dt = CURRENT_TIMESTAMP WHERE id = NEW.thread_id;
            END
        ''')

        # Create delete trigger
        self.__c.execute(f'''
            CREATE TRIGGER {THREAD_MESSAGE_DELETED_TR_NAME}
            AFTER DELETE ON {MESSAGE_TABLE_NAME}
            BEGIN
              UPDATE {THREAD_TABLE_NAME} SET update_dt = CURRENT_TIMESTAMP WHERE id = OLD.thread_id;
            END
        ''')
        # Commit the transaction
        self.__conn.commit()

    def __createMessage(self):
        """
        Create message table
        """
        try:
            # Check if the table exists
            self.__c.execute(
                f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{MESSAGE_TABLE_NAME}'")
            if self.__c.fetchone()[0] == 1:
                # Let it pass if the table already exists
                pass
            else:
                # Create message table and triggers
                self.__c.execute(f'''CREATE TABLE {MESSAGE_TABLE_NAME}
                             (id INTEGER PRIMARY KEY,
                              thread_id INTEGER,
                              role VARCHAR(255),
                              content TEXT,
                              finish_reason VARCHAR(255),
                              model VARCHAR(255),
                              prompt_tokens INTEGER,
                              completion_tokens INTEGER,
                              total_tokens INTEGER,
                              favorite INTEGER DEFAULT 0,
                              update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                              insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                              favorite_set_date DATETIME,
                              FOREIGN KEY (thread_id) REFERENCES {THREAD_TABLE_NAME}
                              ON DELETE CASCADE)''')

                # Will remove after v1.0.0
                self.__removeOldTrigger()

                self.__createMessageTrigger()
                self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")
            raise

    def selectCertainThreadMessagesRaw(self, thread_id, content_to_select=None):
        """
        This is for selecting all messages in a thread with a specific thread_id.
        The format of the result is a list of sqlite Rows.
        """
        query = f'SELECT * FROM {MESSAGE_TABLE_NAME} WHERE thread_id = {thread_id}'
        if content_to_select:
            query += f' AND content LIKE "%{content_to_select}%"'
        self.__c.execute(query)
        return self.__c.fetchall()

    def selectCertainThreadMessages(self, thread_id, content_to_select=None) -> List[ChatMessageContainer]:
        """
        This is for selecting all messages in a thread with a specific thread_id.
        The format of the result is a list of ChatMessageContainer.
        """
        result = [ChatMessageContainer(**elem) for elem in self.selectCertainThreadMessagesRaw(thread_id, content_to_select=content_to_select)]
        return result

    def selectAllContentOfThread(self, content_to_select=None):
        """
        This is for selecting all messages in all threads which include the content_to_select.
        """
        arr = []
        for _id in [conv[0] for conv in self.selectAllThread()]:
            result = self.selectCertainThreadMessages(_id, content_to_select)
            if result:
                arr.append((_id, result))
        return arr

    def insertMessage(self, arg: ChatMessageContainer):
        try:
            excludes = ['id', 'update_dt', 'insert_dt']
            insert_query = arg.create_insert_query(table_name=MESSAGE_TABLE_NAME, excludes=excludes)
            self.__c.execute(insert_query, arg.get_values_for_insert(excludes=excludes))
            new_id = self.__c.lastrowid
            # Commit the transaction
            self.__conn.commit()
            return new_id
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def updateMessage(self, id, favorite):
        """
        Update message favorite
        """
        try:
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.__c.execute(f'''
                            UPDATE {MESSAGE_TABLE_NAME} 
                            SET favorite = ?,
                                favorite_set_date = CASE 
                                                      WHEN ? = 1 THEN ? 
                                                      ELSE NULL 
                                                    END 
                            WHERE id = ?
                        ''', (favorite, favorite, current_date, id))
            self.__conn.commit()
            return current_date
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def __createImage(self):
        try:
            # Check if the table exists
            self.__c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{IMAGE_TABLE_NAME}'")
            # Will remove after v1.0.0
            if self.__c.fetchone()[0] == 1:
                # To not make table every time to change column's name and type
                self.__c.execute(f'PRAGMA table_info({IMAGE_TABLE_NAME})')
                existing_columns = set([column[1] for column in self.__c.fetchall()])
                required_columns = set(ImagePromptContainer.get_keys(['id', 'update_dt', 'insert_dt']))

                # Find missing columns
                missing_columns = required_columns - existing_columns
                for column in missing_columns:
                    # Add missing columns to the table
                    column_type = 'TEXT'  # Default type
                    if column in ['n', 'width', 'height']:
                        column_type = 'INT'
                    elif column == 'data':
                        column_type = 'BLOB'
                    elif column in ['model', 'quality', 'style']:
                        column_type = 'VARCHAR(255)'
                    self.__c.execute(f'ALTER TABLE {IMAGE_TABLE_NAME} ADD COLUMN {column} {column_type}')

                self.__conn.commit()
            else:
                self.__c.execute(f'''CREATE TABLE {IMAGE_TABLE_NAME}
                             (id INTEGER PRIMARY KEY,
                              model VARCHAR(255),
                              prompt TEXT,
                              n INT,
                              quality VARCHAR(255),
                              data BLOB,
                              style VARCHAR(255),
                              revised_prompt TEXT,
                              width INT,
                              height INT,
                              negative_prompt TEXT,
                              update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
                              insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                # Commit the transaction
                self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")
            raise

    def insertImage(self, arg: ImagePromptContainer):
        try:
            excludes = ['id', 'insert_dt', 'update_dt']
            query = arg.create_insert_query(IMAGE_TABLE_NAME, excludes)
            values = arg.get_values_for_insert(excludes)
            self.__c.execute(query, values)
            new_id = self.__c.lastrowid
            self.__conn.commit()
            return new_id
        except sqlite3.Error as e:
            print(f"An error occurred..")
            raise

    def selectImage(self):
        try:
            self.__c.execute(f'SELECT * FROM {IMAGE_TABLE_NAME}')
            return self.__c.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectCertainImage(self, id):
        try:
            self.__c.execute(f'SELECT * FROM {IMAGE_TABLE_NAME} WHERE id={id}')
            return self.__c.fetchone()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def removeImage(self, id=None):
        try:
            query = f'DELETE FROM {IMAGE_TABLE_NAME}'
            if id:
                query += f' WHERE id = {id}'
            self.__c.execute(query)
            self.__conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def selectFavorite(self):
        try:
            self.__c.execute(f'SELECT * FROM {MESSAGE_TABLE_NAME} WHERE favorite=1 order by favorite_set_date')
            return self.__c.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            raise

    def export(self, ids, filename):
        # Get the records of the threads of the given ids
        thread_records = self.selectAllThread(ids)
        data = [dict(record) for record in thread_records]
        # Convert it into dictionary
        for d in data:
            d['messages'] = list(map(lambda x: x.__dict__, self.selectCertainThreadMessages(d['id'])))

        # Save the JSON
        with open(filename, 'w') as f:
            json.dump(data, f)

    def getCursor(self):
        return self.__c

    def close(self):
        self.__conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the connection
        self.__conn.close()

#
# db = SqliteDatabase()
# command_obj_lst = []
# for group in db.selectPromptGroup():
#     entries = [attr for attr in db.selectPromptEntry(group_id=group.id)]
#     if group.prompt_type == 'form':
#         command_obj = {'name': group.name, 'value': ''}
#         for entry in entries:
#             content = entry.content
#             if content and content.strip():
#                 command_obj['value'] += f'{entry.name}: {content}\n'
#         command_obj_lst.append(command_obj)
#     elif group.prompt_type == 'sentence':
#         command_obj = {'name': '', 'value': ''}
#         for entry in entries:
#             command_obj_lst.append({
#                 'name': f'{entry.name}({group.name})',
#                 'value': entry.content
#             })
#
# print([obj['name'] for obj in command_obj_lst])
