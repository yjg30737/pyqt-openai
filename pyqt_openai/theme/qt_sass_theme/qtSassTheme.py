from qtpy.QtGui import QColor, QFont, qGray
from qtpy.QtWidgets import QWidget, QAbstractButton

from lxml import etree
import os, tempfile, posixpath, re
import shutil

import qtsass


class QtSassTheme:

    def __init__(self):
        # set the icons
        cur_dir = os.path.dirname(__file__)
        icon_path = cur_dir.replace(os.path.sep, posixpath.sep)
        ico_filename = os.path.join(icon_path, 'ico/_icons.scss').replace(os.path.sep, posixpath.sep)
        self.__setIcoPath(ico_filename, icon_path)
        self.__initVal()

    def __initVal(self):
        self.__font = ''
        # maybe use this later
        self.__widgetToChange = ''
        self.__color = ''

    def __setIcoPath(self, ico_filename: str, icon_path: str):
        import_abspath_str = f'$icopath: \'{icon_path}/\';'
        with open(ico_filename, 'r+') as f:
            fdata = f.read()
            # if the path is still same
            if fdata.find(import_abspath_str) != -1:
                pass
            else:
                m = re.search(r'\$icopath:\s(\"|\')(.+)(\"|\')', fdata)
                # if the path was changed
                if m:
                    f.truncate(0)
                    f.seek(0, 0)
                    f.write(import_abspath_str + '\n' + '\n'.join(fdata.splitlines(True)[1:]))

                # if the path is nowhere (which means it is the first time to set the path)
                else:
                    f.seek(0, 0)
                    f.write(import_abspath_str + '\n' + fdata)

    def __setCustomThemeColor(self, var_filename: str, theme_color: str):
        with open(var_filename, 'r+') as f:
            fdata = f.read()
            m = re.search(r'\$bgcolor:(.+\n)', fdata)
            if m:
                custom_theme_code = f'$bgcolor: {theme_color};\n'
                f.truncate(0)
                f.seek(0, 0)
                f.write(custom_theme_code + ''.join(fdata.splitlines(True)[1:]))

    def __setFont(self, var_filename: str, font):
        bold = 'bold' if font.bold() else ''
        italic = 'italic' if font.italic() else ''
        size = f"{font.pointSize()}pt"
        family = f'"{font.family()}"'
        fontattr = ' '.join([bold, italic, size, family]).strip()
        with open(var_filename, 'r+') as f:
            fdata = f.read()
            regex = re.compile(r'\$fontattr:(.+)')
            custom_theme_code = f'$fontattr: {fontattr};\n'
            idx = 0
            lines = fdata.split('\n')
            for i, line in enumerate(lines):
                if regex.search(line):
                    idx = i
                    break
            lines[idx] = custom_theme_code
            new_text = '\n'.join(lines)
            f.write(new_text)

    def __setIcon(self, ico_dirname: str, new_width: str, new_height: str, new_color: str) -> None:
        '''
        :param ico_dirname: the directory containing SVG icons
        :param width: the new width of the SVG icons
        :param height: the new height of the SVG icons
        :param new_color: the new fill color of the SVG icons
        :return: None
        '''

        # loop through all the SVG files in the directory
        for filename in os.listdir(ico_dirname):
            if filename.endswith('.svg'):
                # load the SVG file as an etree object
                svg = etree.parse(os.path.join(ico_dirname, filename))

                # modify the root element to change the width, height, and fill attributes
                root = svg.getroot()
                root.set('width', new_width)
                root.set('height', new_height)
                for elem in root.iter():
                    if len(elem):
                        if 'fill' in elem.attrib:
                            elem.set('fill', new_color)
                        else:
                            elem.attrib['fill'] = new_color

                # save the modified SVG object back to the original file
                svg.write(os.path.join(ico_dirname, filename), pretty_print=True)

    def __setBackgroundPolicy(self, var_filename: str, background_darker=False):
        if background_darker:
             with open(var_filename, 'r+') as f:
                fdata = f.read()
                m1 = re.search(r'\$bgcolor:(.+\n)', fdata)
                m2 = re.search(r'\$widgetcolor:(.+\n)', fdata)
                if m1 and m2:
                    w_color_v = m1.group(1)
                    bg_color_v = m2.group(1).replace('bgcolor', 'widgetcolor')
                    background_darker_code = f'$widgetcolor:{w_color_v}' \
                                             f'$bgcolor:{bg_color_v}'
                    background_darker_code += ''.join(fdata.splitlines(True)[2:])
                    f.truncate(0)
                    f.seek(0, 0)
                    f.write(background_darker_code)
        else:
            pass

    def __getStyle(self, filename):
        cur_dir = os.path.dirname(__file__)
        sass_dirname = os.path.join(cur_dir, 'sass')
        # make temporary file
        temp_file = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        css = qtsass.compile_filename(os.path.join(sass_dirname, filename), temp_file)
        return css

    def getThemeFiles(self, theme: str = 'dark_gray', font=QFont('Arial', 9), icon_size=9, background_darker=False, output_path=os.getcwd()):
        official_theme_dict = {'dark_gray': '#555555', 'dark_blue': '#2c3949', 'light_gray': '#D4D4D4', 'light_blue': '#c7dffb'}
        cur_dir = os.path.dirname(__file__)
        official_theme_flag = theme in official_theme_dict.keys()
        theme_color = ''
        ico_dirname = ''
        var_dirname = ''
        if official_theme_flag:
            theme_color = official_theme_dict[theme]
            theme_prefix = theme.split('_')[0]
            ico_dirname = os.path.join(cur_dir, 'ico')
            var_dirname = os.path.join(cur_dir, os.path.join(os.path.join('var', theme_prefix), theme))

        # check whether theme value is 6-digit hex color
        else:
            m = re.match(r'#[a-fA-F0-9]{6}', theme)
            if m:
                theme_color = m.group(0)
                theme_color = QColor(theme_color)

                # 'if it is, check 6-digit hex color is lighter than usual or darker')
                r, g, b = theme_color.red(), theme_color.green(), theme_color.blue()
                theme_lightness = ''
                # use this to var
                if qGray(r, g, b) > 255 // 2:
                    theme_lightness = 'light'
                else:
                    theme_lightness = 'dark'

                # get the ico_dirname
                ico_dirname = os.path.join(cur_dir, os.path.join('ico'))

                # get the dark_gray/light_gray theme
                var_dirname = os.path.join(cur_dir, os.path.join(os.path.join('var', theme_lightness),
                                                                 theme_lightness+'_gray'))
            else:
                raise Exception('Invalid theme')

        sass_dirname = os.path.join(cur_dir, 'sass')
        os.chdir(output_path)
        output_dirname = 'res'
        if os.path.exists(output_dirname):
            pass
        else:
            os.mkdir(output_dirname)
        os.chdir(output_dirname)
        if os.path.exists('ico'):
            shutil.rmtree('ico')
        if os.path.exists('sass'):
            shutil.rmtree('sass')
        if os.path.exists('var'):
            shutil.rmtree('var')
        shutil.copytree(ico_dirname, 'ico')
        shutil.copytree(sass_dirname, 'sass')
        shutil.copytree(var_dirname, 'var')

        # assume we have an existing QColor variable named 'old_color'
        old_color = QColor(theme_color)  # example color, you can replace with your own QColor variable

        # get the hue, saturation, and lightness values of the old color
        h, s, l = old_color.hue(), old_color.saturation(), old_color.lightness()

        # desaturate the color by setting the saturation value to 0
        s = 0

        # invert the lightness value by subtracting it from 255
        l = 255 - l

        # create a new color with the modified values
        new_color = QColor.fromHsl(h, s, l)

        # set svg icon attribute
        self.__setIcon('ico', str(font.pointSize()), str(font.pointSize()), new_color.name())

        # set icon scss
        ico_filename = 'ico/_icons.scss'
        self.__setIcoPath(ico_filename, output_dirname)

        var_filename = 'var/_variables.scss'
        if official_theme_flag:
            pass
        else:
            self.__setCustomThemeColor(var_filename, theme)
        self.__setBackgroundPolicy(var_filename, background_darker)

        self.__setFont(var_filename, font)

        # TODO set the font
        # TODO set the size of the icon

    def setThemeFiles(self, main_window: QWidget, input_path='res'):
        if os.path.basename(os.getcwd()) != input_path:
            input_path = os.path.join(os.getcwd(), input_path)
            os.chdir(input_path)
        qtsass.compile_dirname('sass', '.')
        ico_filename = 'ico/_icons.scss'
        sass_dirname = 'sass'
        var_dirname = 'var'
        if os.path.exists(ico_filename):
            os.remove(ico_filename)
        if os.path.exists(sass_dirname):
            shutil.rmtree(sass_dirname)
        if os.path.exists(var_dirname):
            shutil.rmtree(var_dirname)

        os.chdir('../')
        if os.path.isdir(input_path):
            f_lst = ['theme.css', 'custom_widget.css', 'icon_button.css', 'icon_text_button.css', 'menu_bar.css']
            f_lst = [os.path.join(input_path, f) for f in f_lst]

            with open(f_lst[0], 'r') as f:
                theme_style = f.read()
            with open(f_lst[1], 'r') as f:
                custom_widget_style = f.read()
            with open(f_lst[2], 'r') as f:
                icon_button_style = f.read()
            with open(f_lst[3], 'r') as f:
                icon_text_button_style = f.read()
            with open(f_lst[4], 'r') as f:
                menu_bar_style = f.read()

            main_window.setStyleSheet(theme_style +
                                      custom_widget_style +
                                      menu_bar_style)

            # button
            def setButtonStyle(main_window):
                btns = main_window.findChildren(QAbstractButton)
                for btn in btns:
                    # check if text exists
                    if btn.text().strip() == '':
                        btn.setStyleSheet(icon_button_style)  # no text - icon button style
                    else:
                        btn.setStyleSheet(icon_text_button_style)  # text - icon-text button style

            setButtonStyle(main_window)

    def getThemeStyle(self):
        css = self.__getStyle('theme.scss')
        return css

    def getCustomWidgetStyle(self):
        css = self.__getStyle('custom_widget.scss')
        return css

    def getIconButtonStyle(self):
        css = self.__getStyle('icon_button.scss')
        return css

    def getIconTextButtonStyle(self):
        css = self.__getStyle('icon_text_button.scss')
        return css

    def getMenuBarStyle(self):
        css = self.__getStyle('menu_bar.scss')
        return css

