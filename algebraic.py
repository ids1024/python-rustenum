class AlgebraicVariantBase(tuple):
    def __new__(cls, *args):
        if len(args) != cls._num:
            name = type(cls).__name__ + '.' + cls.__name__
            raise TypeError("Wrong number of arguments to " + name)
        return super().__new__(cls, args)

    def __repr__(self):
        name = type(type(self)).__name__ + '.' + type(self).__name__
        return "{}({})".format(name, ', '.join(repr(i) for i in self))


class AlgebraicBase(type):
    def __repr__(self):
        name = type(self).__name__ + '.' + self.__name__
        return "<{}>".format(name)
   

class Algebraic(type):
    def __new__(cls, name, **kwargs):
        return super().__new__(cls, name, (AlgebraicBase,), {"_name": name})

    def __init__(self, name, **kwargs):
        super().__init__(name, (type,), {})
        self._variants = []
        for k, v in kwargs.items():
            instance = self(k, (AlgebraicVariantBase,), {"_num": v})
            self._variants.append(instance)
            setattr(self, k, instance)

    def __repr__(self):
        return "<algebraic '" + self.__name__ + "'>"

    def __iter__(self):
        return iter(self._variants)
