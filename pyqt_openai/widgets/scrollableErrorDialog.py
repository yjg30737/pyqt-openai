from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QScrollArea, QPushButton, QHBoxLayout

from pyqt_openai import REPORT_ERROR_URL
from pyqt_openai.lang.translations import LangClass
from pyqt_openai.widgets.linkLabel import LinkLabel


class ScrollableErrorDialog(QDialog):
    def __init__(self, error_msg, parent=None):
        super().__init__(parent)
        self.__initUi(error_msg)

    def __initUi(self, error_msg):
        # TODO LANGUAGE
        self.setWindowTitle(LangClass.TRANSLATIONS["Error"])

        # Main layout
        main_layout = QVBoxLayout(self)

        # Add a label to display the critical error title
        label = QLabel("<b>An unexpected error occurred.</b>")
        main_layout.addWidget(label)

        # Scroll Area to hold the error message
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Error message label inside the scroll area
        error_label = QLabel(error_msg)
        error_label.setWordWrap(True)

        # Set the error message into the scroll area
        scroll_area.setWidget(error_label)

        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)

        # Button layout for the "OK" button
        button_layout = QHBoxLayout()
        report_error_lbl = LinkLabel()
        report_error_lbl.setUrl(REPORT_ERROR_URL)
        # TODO LANGUAGE
        report_error_lbl.setText('Report Error')

        ok_button = QPushButton(LangClass.TRANSLATIONS['OK'])
        ok_button.clicked.connect(self.accept)  # Close the dialog when OK is clicked
        button_layout.addWidget(report_error_lbl)
        button_layout.addStretch(1)  # To push the button to the right
        button_layout.addWidget(ok_button)

        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)