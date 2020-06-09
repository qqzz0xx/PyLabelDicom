from PyQt5 import QtCore, QtGui, QtWidgets


class Dispatcher:
    listenerDict = dict()

    @staticmethod
    def dispatch(obj, event, *args):
        listenerDict = Dispatcher.listenerDict
        if event in listenerDict.keys():
            for listener in Dispatcher.listenerDict[event]:
                listener(obj, args)

    @staticmethod
    def hasListener(event, listener):
        listenerDict = Dispatcher.listenerDict
        if event in listenerDict.keys():
            return listener in listenerDict[event]
        return False

    @staticmethod
    def addListener(event, listener):
        if not Dispatcher.hasListener(event, listener):
            linsteners = Dispatcher.listenerDict.get(event, [])
            linsteners.append(listener)
            Dispatcher.listenerDict[event] = linsteners

    @staticmethod
    def removeListener(event, listener):
        if Dispatcher.hasListener(event, listener):
            linsteners = Dispatcher.listenerDict.get(event)
            if len(linsteners) == 1:
                del Dispatcher.listenerDict[event]
            else:
                linsteners.remove(listener)
                Dispatcher.listenerDict[event] = linsteners


class a:
    def __init__(self):
        Dispatcher.addListener('1', self.foo)

    def foo(self, a, b, c):
        print(self)
        print(a, b, c)


if __name__ == "__main__":
    a()
    # Dispatcher.addListener('1', foo)
    Dispatcher.dispatch(None, '1', 1, 2)
