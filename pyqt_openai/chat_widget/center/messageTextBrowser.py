import json

# from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtGui import QPalette, QColor, QDesktopServices
from PySide6.QtWidgets import QTextBrowser

from pyqt_openai import MESSAGE_MAXIMUM_HEIGHT, MESSAGE_PADDING, INDENT_SIZE


class MessageTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Make the remote links clickable
        self.anchorClicked.connect(self.on_anchor_clicked)
        self.setOpenExternalLinks(True)
        self.__initUi()

    def on_anchor_clicked(self, url):
        QDesktopServices.openUrl(url)

    def __initUi(self):
        # Transparent background
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor(0, 0, 0, 0))
        self.setPalette(palette)

        # Remove edge
        self.setFrameShape(QTextBrowser.NoFrame)

        # Padding
        self.document().setDocumentMargin(MESSAGE_PADDING)

        self.setContentsMargins(0, 0, 0, 0)

    def setJson(self, json_str):
        try:
            json_data = json.loads(json_str)
            pretty_json = json.dumps(json_data, indent=INDENT_SIZE)
            self.setPlainText(pretty_json)
        except json.JSONDecodeError as e:
            self.setPlainText(f"Error decoding JSON: {e}")

    def adjustBrowserHeight(self):
        document_height = self.document().size().height()
        max_height = MESSAGE_MAXIMUM_HEIGHT

        if document_height < max_height:
            self.setMinimumHeight(int(document_height))
        else:
            self.setMinimumHeight(int(max_height))
        self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().maximum())

    def setMarkdown(self, markdown: str) -> None:
        super().setMarkdown(markdown)
        # Convert markdown to HTML using QTextDocument

    #     document = QTextDocument()
    #     document.setMarkdown(markdown)
    #     html_text = document.toHtml()
    #     with open("test.html", "w") as f:
    #         f.write(html_text)
    # #
    # #     # Customize the converted HTML (e.g., add style tags)
    #     custom_html = f"""
    #     <style>
    #     h1 {{
    #         color: red;
    #         font-size: 24px;
    #     }}
    #     h2 {{
    #         color: darkgreen;
    #         font-size: 20px;
    #     }}
    #     ul {{
    #         margin-left: 20px;
    #         color: blue;
    #     }}
    #     a {{
    #         color: red;
    #         text-decoration: none;
    #     }}
    #     a:hover {{
    #         text-decoration: underline;
    #     }}
    #     </style>{html_text}
    #     """
    #     self.setHtml(custom_html)
    #
    # def eventFilter(self, obj, event):
    #     print(obj, int(event.type()))
    #     return super().eventFilter(obj, event)


#
# def main():
#     app = QApplication([])
#
#     window = QWidget()
#     layout = QVBoxLayout()
#
#     text_browser = MessageTextBrowser()
#
#     markdown_text = """
# https://www.google.com
#     """
#     text_browser.setMarkdown(markdown_text)
#
#     layout.addWidget(text_browser)
#     window.setLayout(layout)
#     window.show()
#
#     app.exec()
#
#
# if __name__ == "__main__":
#     main()
