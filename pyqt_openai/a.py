from pyqt_openai.constants import MESSAGE_TABLE_NAME_OLD, MESSAGE_TABLE_NAME, THREAD_TABLE_NAME
import sqlite3

# Connect to the database (create a new file if it doesn't exist)
from pyqt_openai.models import ChatMessageContainer

conn = sqlite3.connect('old_one/conv.db')
conn.row_factory = sqlite3.Row
conn.execute('PRAGMA foreign_keys = ON;')
conn.commit()

# create cursor
c = conn.cursor()

res = c.execute(f'''
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name LIKE '{MESSAGE_TABLE_NAME_OLD}%';
            ''')

# UNION all old message tables to new one
union_query = ''
for name in res.fetchall():
    union_query += f'SELECT * FROM {name[0]}\n'
union_query = ' UNION '.join(union_query.split('\n')[:-1]) + ' order by id_fk'

res = c.execute(union_query)

# c.execute(f'''CREATE TABLE {MESSAGE_TABLE_NAME}
#                              (id INTEGER PRIMARY KEY,
#                               thread_id INTEGER,
#                               role VARCHAR(255),
#                               content TEXT,
#                               finish_reason VARCHAR(255),
#                               model_name VARCHAR(255),
#                               prompt_tokens INTEGER,
#                               completion_tokens INTEGER,
#                               total_tokens INTEGER,
#                               update_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
#                               insert_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
#                               FOREIGN KEY (thread_id) REFERENCES {THREAD_TABLE_NAME}
#                               ON DELETE CASCADE)''')

arg = ChatMessageContainer()
insert_query = arg.create_insert_query(table_name=MESSAGE_TABLE_NAME, excludes=['id'])

for row in res.fetchall():
    row_dict = dict(row)
    row_dict['role'] = 'user' if row_dict['is_user'] == 1 else 'assistant'
    row_dict['thread_id'] = row_dict['id_fk']
    row_dict['content'] = row_dict['conv']
    del row_dict['is_user']
    arg = ChatMessageContainer(**row_dict)
    c.execute(insert_query, arg.get_values_for_insert(excludes=['id']))
    conn.commit()