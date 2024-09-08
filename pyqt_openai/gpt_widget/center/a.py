class A:
    def __init__(self):
        pass

    def _print(self):
        print('A')


class B(A):
    def __init__(self):
        super().__init__()

    def _print(self):
        print('B')


a = A()
b = B()
a._print()