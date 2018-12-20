

class MetaA(type):
    def __new__(cls, name, bases, attrs):
        print(name, bases, attrs, cls)
        return super(MetaA, cls).__new__(cls, name, bases, attrs)

    def __init__(self, name, bases, attrs):
        print(name, bases, attrs, self)


class A(metaclass=MetaA):
    def __init__(self):
        self.name = "name"

    @classmethod
    def test(cls):
        pass

    @staticmethod
    def run():
        pass

a =A()
print(a.__dict__)
print(A.__dict__)
