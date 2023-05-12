from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QCheckBox


class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Add a checkbox to the view
        checkbox = QCheckBox()
        proxy = QGraphicsProxyWidget()
        proxy.setWidget(checkbox)
        proxy.setPos(0, 0)
        self.scene.addItem(proxy)


if __name__ == "__main__":
    app = QApplication([])
    view = CustomGraphicsView()
    view.show()
    app.exec_()
