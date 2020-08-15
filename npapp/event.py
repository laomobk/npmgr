
class DestroyEvent:
    def __init__(self, widget):
        self.__widget = widget

    @property
    def widget(self):
        return self.__widget


class SetVisibleEvent:
    def __init__(self, v :bool):
        self.__v = v

    @property
    def value(self) -> b:
        return self.__v
