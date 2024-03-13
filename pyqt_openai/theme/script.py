from qtpy.QtGui import QFont
from qt_material import apply_stylesheet

THEME_DATA = {'Normal': '', 'Dark Amber': 'dark_amber.xml', 'Dark Blue': 'dark_blue.xml', 'Dark Cyan': 'dark_cyan.xml', 'Dark Lightgreen': 'dark_lightgreen.xml', 'Dark Pink': 'dark_pink.xml', 'Dark Purple': 'dark_purple.xml', 'Dark Red': 'dark_red.xml', 'Dark Teal': 'dark_teal.xml', 'Dark Yellow': 'dark_yellow.xml', 'Light Amber': 'light_amber.xml', 'Light Blue': 'light_blue.xml', 'Light Cyan': 'light_cyan.xml', 'Light Cyan 500': 'light_cyan_500.xml', 'Light Lightgreen': 'light_lightgreen.xml', 'Light Pink': 'light_pink.xml', 'Light Purple': 'light_purple.xml', 'Light Red': 'light_red.xml', 'Light Teal': 'light_teal.xml', 'Light Yellow': 'light_yellow.xml'}

def apply_theme_in_runtime(value, instance, font_size=12):
    value = THEME_DATA[value]
    font_size = font_size
    extra = {
        'font_size': f'{font_size}px',
    }
    if value:
        apply_stylesheet(instance, theme=value, invert_secondary=True, extra=extra)
    else:
        instance.setStyleSheet('')
    instance.setFont(QFont('Arial', font_size))