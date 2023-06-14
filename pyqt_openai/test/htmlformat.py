from PyQt5.QtWidgets import QApplication, QTextEdit
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

code = """
const path = require('path');

require('dotenv').config();

module.exports = {
    // DB 설정
    ConfigDatabase: {
        host: process.env.DB_HOST,
        port: process.env.DB_PORT,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        database: process.env.DB_NAME,
        connectionLimit: 10,
        dateStrings: 'date',
    },
    // 파일 경로
    filePath: {
        root: path.normalize(process.env.PATH2 + process.env.DATA_PATH),
        excel: path.normalize(process.env.PATH2 + process.env.EXCEL_PATH),
    },
    // cors 설정
    corsOptions: {
        origin: true, // 접근 권한을 부여하는 도메인
        credentials: true, // 응답 헤더에 Access-Control-Allow-Credentials 추가
        optionsSuccessStatus: 200 // 응답 상태 200으로 설정
    },
    // mail 정보
    mailOptions: {
        mailuser: process.env.MAIL_USER,
        mailpass: process.env.MAIL_PASSWORD,
        mailtext: process.env.MAIL_TEXT
    },
    impPort: {
        imp_key: process.env.IMP_KEY,
        imp_secret: process.env.IMP_SECRET
    },
    // CBT 배포 대상 사용자 지칭 문자열
    customerName: {
        userName: process.env.USER_NAME,
    },
    // 문제 컬렉션에서 자주 사용되는 상수
    constInColl: {
        questionStemCnt: 5, // 문제줄기 최대 개수
        questionOptionCnt: 15, // 답가지 최대 개수
        questionStemFilePrefix: 'question_stem_file', // 문제줄기파일 접두어
        questionStemHelpPrefix: 'question_stem_help', // 문제줄기도움말 접두어
        questionOptionPrefix: 'question_option', // 답가지 접두어
        questionOptionFilePrefix: 'question_option_file', // 답가지파일 접두어
    },
};


"""

lexer = PythonLexer()
formatter = HtmlFormatter(style='colorful')

css_styles = formatter.get_style_defs('.highlight')

html_code = f"""
<html>
    <head>
        <style>
            {css_styles}
        </style>
    </head>
    <body>
        {highlight(code, lexer, formatter)}
    </body>
</html>
"""

print(html_code)


import sys

app = QApplication(sys.argv)
w = QTextEdit()
w.setText(html_code)
w.show()
sys.exit(app.exec())