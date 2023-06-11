import os
import sys
import re
import zipfile

from jinja2 import Template

from pyqt_openai.sqlite import SqliteDatabase


def get_generic_ext_out_of_qt_ext(text):
    pattern = r'\((\*\.(.+))\)'
    match = re.search(pattern, text)
    extension = '' if match else '.' + match.group(2)
    return extension


def open_directory(path):
    if sys.platform.startswith('darwin'):  # macOS
        os.system('open "{}"'.format(path))
    elif sys.platform.startswith('win'):  # Windows
        os.system('start "" "{}"'.format(path))
    elif sys.platform.startswith('linux'):  # Linux
        os.system('xdg-open "{}"'.format(path))
    else:
        print("Unsupported operating system.")


def conv_unit_to_txt(db, ids, filename, username='User', ai_name='AI'):
    content = ''
    for id in ids:
        certain_conv_filename = db.selectConv(id)[1]
        certain_conv_filename_content = db.selectCertainConv(id)
        content += f'== {certain_conv_filename} ==' + '\n'*2
        for unit in certain_conv_filename_content:
            unit_prefix = username if unit[2] == 1 else ai_name
            unit_content = unit[3]
            content += f'{unit_prefix}: {unit_content}' + '\n'*2
        content += '\n' * 2
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


def conv_unit_to_html(db, id, title):
    certain_conv_filename_content = db.selectCertainConv(id)
    chat_history = [unit[3] for unit in certain_conv_filename_content]
    template = Template('''
    <html>
<head>
    <title>pyqt-openai html file - {{ title }}</title>
    <style>
        .chat {
            background-color: #f2f2f2;
            border-radius: 5px;
            padding: 10px;
        }
        .message {
            padding: 2rem;
        }
        .message:nth-child(even) {
            background-color: #ddd; /* Color for even messages */
        }
        
        .message:nth-child(odd) {
            background-color: #fff; /* Color for odd messages */
        }
    </style>
</head>
<body>
    <header>
        <h1>{{ title }}</h1>
    </header>
    <div class="chat">
        {% for message in chat_history %}
            <div class="message">{{ message }}</div>
        {% endfor %}
    </div>
</body>
</html>

    ''')
    html = template.render(title=title, chat_history=chat_history)
    return html


def add_file_to_zip(file_content, file_name, output_zip_file):
    with zipfile.ZipFile(output_zip_file, 'a') as zipf:
        zipf.writestr(file_name, file_content)

db = SqliteDatabase('../conv.db')
ids = [1,2]
zip_file = 'b.zip'
for id in ids:
    html_filename = f'{id}.html'
    title = db.selectConv(id)[1]
    html_content = conv_unit_to_html(db, id, title)
    add_file_to_zip(html_content, html_filename, zip_file)