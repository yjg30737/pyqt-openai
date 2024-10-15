# TODO WILL_BE_IMPLEMENTED AFTER v2.x.0

# from PySide6.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QLabel, QComboBox,
#                             QPushButton, QColorDialog, QFormLayout, QScrollArea)
#
# from pyqt_openai.lang.translations import LangClass
# from pyqt_openai.models import SettingsParamsContainer
# from pyqt_openai.util.script import getSeparator
#
#
# class MarkdownSettingsWidget(QWidget):
#     def __init__(self, args: SettingsParamsContainer, parent=None):
#         super().__init__(parent)
#         self.__initVal(args)
#         self.__initUi()
#
#     def __initVal(self, args):
#         self.__show_as_markdown = args.show_as_markdown
#         self.__apply_user_defined_styles = args.apply_user_defined_styles
#         self.__span_font = args.span_font
#         self.__span_color = args.span_color
#         self.__ul_color = args.ul_color
#         self.__h1_color = args.h1_color
#         self.__h2_color = args.h2_color
#         self.__h3_color = args.h3_color
#         self.__h4_color = args.h4_color
#         self.__h5_color = args.h5_color
#         self.__h6_color = args.h6_color
#         self.__a_color = args.a_color
#
#     def __initUi(self):
#         self.__showAsMarkdownCheckBox = QCheckBox(LangClass.TRANSLATIONS['Show as Markdown'])
#
#         self.__applyUserDefinedStylesCheckBox = QCheckBox(LangClass.TRANSLATIONS['Apply User-Defined HTML Styles'])
#
#         markdownLbl = QLabel(LangClass.TRANSLATIONS['Details'])
#         markdownWidget = QWidget()
#
#         form_layout = QFormLayout()
#
#         # Helper function to create color picker buttons
#         def create_color_picker(label_text):
#             color_button = QPushButton('Choose Color')
#             color_button.setObjectName(label_text)
#             color_button.clicked.connect(self.open_color_dialog)
#             combo_box_font = None
#             if label_text == 'span':
#                 combo_box_font = QComboBox()
#                 # Add frequently used font families to the combo box
#                 font_families = ["Arial", "Courier New", "Times New Roman", "Verdana", "Helvetica"]
#                 combo_box_font.addItems(font_families)
#                 form_layout.addRow(QLabel(label_text + ' Font:'), combo_box_font)
#             form_layout.addRow(QLabel(label_text + ' Color:'), color_button)
#             form_layout.addRow(getSeparator())
#             return combo_box_font, color_button
#
#         # Adding form fields for each tag and attribute
#         self.font_editors = {}
#         self.color_buttons = {}
#         self.__tags_attributes = [
#             ('span', 'Font, Color'),
#             ('ol', 'Color'),
#             ('li', 'Color'),
#             ('ul', 'Color'),
#             ('h1', 'Color'),
#             ('h2', 'Color'),
#             ('h3', 'Color'),
#             ('h4', 'Color'),
#             ('h5', 'Color'),
#             ('h6', 'Color'),
#             ('a', 'Color')
#         ]
#
#         for tag, attributes in self.__tags_attributes:
#             if 'Font' in attributes:
#                 self.font_editors[tag], self.color_buttons[tag] = create_color_picker(tag)
#             else:
#                 _, self.color_buttons[tag] = create_color_picker(tag)
#
#         # Set the form layout to the widget
#         markdownWidget.setLayout(form_layout)
#
#         # Create a QScrollArea and set markdownWidget as its widget
#         scroll_area = QScrollArea()
#         scroll_area.setWidget(markdownWidget)
#         scroll_area.setWidgetResizable(True)
#
#         layout = QVBoxLayout()
#         layout.addWidget(self.__showAsMarkdownCheckBox)
#         layout.addWidget(self.__applyUserDefinedStylesCheckBox)
#         layout.addWidget(markdownLbl)
#         layout.addWidget(scroll_area)
#
#         self.setLayout(layout)
#
#         self.__showAsMarkdownCheckBox.toggled.connect(
#             lambda: self.__applyUserDefinedStylesCheckBox.setEnabled(self.__showAsMarkdownCheckBox.isChecked()))
#         self.__applyUserDefinedStylesCheckBox.toggled.connect(
#             lambda: markdownWidget.setEnabled(self.__applyUserDefinedStylesCheckBox.isChecked() and self.__showAsMarkdownCheckBox.isChecked()))
#
#         self.__showAsMarkdownCheckBox.setChecked(self.__show_as_markdown)
#         self.__applyUserDefinedStylesCheckBox.setChecked(self.__apply_user_defined_styles)
#
#         self.__applyUserDefinedStylesCheckBox.setEnabled(self.__showAsMarkdownCheckBox.isChecked())
#         markdownWidget.setEnabled(self.__applyUserDefinedStylesCheckBox.isChecked() and self.__showAsMarkdownCheckBox.isChecked())
#
#     def open_color_dialog(self):
#         sender = self.sender()
#         color = QColorDialog.getColor()
#         if color.isValid():
#             sender.setStyleSheet(f'background-color: {color.name()};')
#
#     def getParam(self):
#         params = {
#             'show_as_markdown': self.__showAsMarkdownCheckBox.isChecked(),
#             'apply_user_defined_styles': self.__applyUserDefinedStylesCheckBox.isChecked(),
#         }
#         for tag, editor in self.font_editors.items():
#             if editor:  # editor will be None for tags without a font combo box
#                 params[f'{tag}_font'] = editor.currentText()
#         for tag, button in self.color_buttons.items():
#             color_name = button.palette().button().color().name()
#             params[f'{tag}_color'] = color_name
#         return params
