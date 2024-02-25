import os, math, colorsys, posixpath

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel

from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRect


class ColorSquareWidget(QWidget):
    colorChanged = pyqtSignal(float, float, float)

    def __init__(self, color):
        super().__init__()
        self.__initVal()
        self.__initUi(color)

    def __initVal(self):
        # default width and height
        self.__width = 300
        self.__height = 300

    def __initUi(self, color):
        self.setFixedSize(self.__width, self.__height)

        self.__h, \
        self.__s, \
        self.__l = colorsys.rgb_to_hsv(color.redF(), color.greenF(), color.blueF())

        # Multiply 100 for insert into stylesheet code
        self.__h *= 100


        self.__colorView = QWidget()
        self.__colorView.setStyleSheet(f'''
            background-color: qlineargradient(x1:1, x2:0, 
            stop:0 hsl({self.__h}%,100%,50%), 
            stop:1 #fff);
            border-radius: 5px;
        ''')

        self.__blackOverlay = QWidget()

        with open(os.path.join(os.path.dirname(__file__), 'style/black_overlay.css').replace(os.path.sep, posixpath.sep), 'r') as f:
            self.__blackOverlay.setStyleSheet(f.read())

        self.__blackOverlay.mouseMoveEvent = self.__moveSelectorByCursor
        self.__blackOverlay.mousePressEvent = self.__moveSelectorByCursor

        self.__selector_diameter = 12

        self.__selector = QWidget(self.__blackOverlay)
        self.__selector.setGeometry(math.floor(self.__selector_diameter / 2) * -1,
                                    math.floor(self.__selector_diameter / 2) * -1,
                                    self.__selector_diameter,
                                    self.__selector_diameter)

        with open(os.path.join(os.path.dirname(__file__), 'style/color_selector.css').replace(os.path.sep, posixpath.sep), 'r') as f:
            self.__selector.setStyleSheet(f.read())

        self.__blackRingInsideSelector = QLabel(self.__selector)
        self.__blackRingInsideSelector_diameter = self.__selector_diameter - 2
        self.__blackRingInsideSelector.setGeometry(QRect(1, 1, self.__blackRingInsideSelector_diameter,
                                                         self.__blackRingInsideSelector_diameter))
        with open(os.path.join(os.path.dirname(__file__), 'style/black_ring_of_color_selector.css').replace(os.path.sep, posixpath.sep), 'r') as f:
            self.__blackRingInsideSelector.setStyleSheet(f.read())

        lay = QGridLayout()
        lay.addWidget(self.__colorView, 0, 0, 1, 1)
        lay.addWidget(self.__blackOverlay, 0, 0, 1, 1)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

        self.__initSelector()

    def __moveSelectorNotByCursor(self, s, l):
        geo = self.__selector.geometry()
        x = self.minimumWidth() * s
        y = self.minimumHeight() - self.minimumHeight() * l
        geo.moveCenter(QPoint(int(x), int(y)))
        self.__selector.setGeometry(geo)

    def __initSelector(self):
        self.__moveSelectorNotByCursor(self.__s, self.__l)

    def __moveSelectorByCursor(self, e):
        if e.buttons() == Qt.LeftButton:
            pos = e.pos()
            if pos.x() < 0:
                pos.setX(0)
            if pos.y() < 0:
                pos.setY(0)
            if pos.x() > self.__width:
                pos.setX(int(self.__width))
            if pos.y() > self.__height:
                pos.setY(int(self.__height))

            self.__selector.move(pos - QPoint(math.floor(self.__selector_diameter / 2),
                                              math.floor(self.__selector_diameter / 2)))

            self.__setSaturation()
            self.__setLightness()

            self.colorChanged.emit(self.__h, self.__s, self.__l)

    def changeHue(self, h):
        self.__h = h
        self.__colorView.setStyleSheet(f'''
            border-radius: 5px;
            background-color: qlineargradient(x1:1, x2:0,
            stop:0 hsl({self.__h}%,100%,50%),
            stop:1 #fff);
        ''')

        self.colorChanged.emit(self.__h, self.__s, self.__l)

    def changeHueByEditor(self, h):
        # Prevent hue from becoming larger than 100
        # if hue becomes larger than 100, hue of square will turn into dark.
        self.__h = min(100, h)
        self.__colorView.setStyleSheet(f'''
            border-radius: 5px;
            background-color: qlineargradient(x1:1, x2:0,
            stop:0 hsl({self.__h}%,100%,50%),
            stop:1 #fff);
        ''')

    def __setSaturation(self):
        self.__s = (self.__selector.pos().x() + math.floor(self.__selector_diameter / 2)) / self.minimumWidth()

    def getSaturatation(self):
        return self.__s

    def __setLightness(self):
        self.__l = abs(
            ((self.__selector.pos().y() + math.floor(self.__selector_diameter / 2)) / self.minimumHeight()) - 1)

    def getLightness(self):
        return self.__l

    def moveSelectorByEditor(self, s, l):
        self.__moveSelectorNotByCursor(s, l)