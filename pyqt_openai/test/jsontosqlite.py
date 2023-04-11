import json
import sqlite3


def convertJsonIntoSql():
    # Read data from json
    with open('conv_history.json', 'r') as f:
        data = json.load(f)
        root_table = list(data.keys())[0]
        print('root_table: ', root_table)
        for obj in list(data.values())[0]:
            id, title, conv_data = obj


convertJsonIntoSql()




# try:
#     # Connect to the database (create a new file if it doesn't exist)
#     conn = sqlite3.connect('conv.db')
#     table_name = 'each_conv_lst'
#     trigger_name = 'update_each_conv_lst'
#     c = conn.cursor()
#     c.execute(f'SELECT count(*) FROM sqlite_master WHERE type=\'table\' AND name={table_name}')
#     if c.fetchone()[0] == 1:
#         print(f'the table {table_name} exists.')
#     else:
#         # Create a table with update_dt and insert_dt columns
#         c.execute(f'''CREATE TABLE {table_name}
#                                      (id INTEGER PRIMARY KEY,
#                                       name TEXT,
#                                       update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
#                                       insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP)''')
#         # Create a trigger to update the update_dt column with the current timestamp
#         c.execute(f'''CREATE TRIGGER {trigger_name}
#                                      AFTER UPDATE ON example_table
#                                      FOR EACH ROW
#                                      BEGIN
#                                        UPDATE {table_name}
#                                        SET update_dt=CURRENT_TIMESTAMP
#                                        WHERE id=OLD.id;
#                                      END;''')
#         # Commit the transaction
#         conn.commit()
#
#         c.execute(f'INSERT INTO {table_name} (name) VALUES (?)', (name,))
#         new_id = c.lastrowid
#         # Commit the transaction
#         conn.commit()
# except sqlite3.Error as e:
#     print(f"An error occurred while connecting to the database: {e}")
#     raise




