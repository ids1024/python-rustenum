import types


class RustEnumVariant:
    def __init__(self, enum_class, name, num):
        self._enum_class = enum_class
        self._name = name
        self._num = num

    def __call__(self, *args):
        if len(args) != self._num:
            raise TypeError("Wrong number of arguments to " + repr(self))
        return self._enum_class(self._name, args)

    def __get__(self, instance, owner):
        if self._num == 0:
            return self()
        return self

    def __repr__(self):
        return self._enum_class.__name__ + '.' + self._name


class RustEnumMeta(type):
    def __new__(metacls, cls, bases, classdict):
        instance = super().__new__(metacls, cls, bases, classdict)
        instance._variants = {}

        for k, v in classdict.items():
            if not k.startswith("_") and isinstance(classdict[k], int):
                instance._variants[k] = classdict[k]
                variant = RustEnumVariant(instance, k, v)
                setattr(instance, k, variant)

        return instance

    def __repr__(self):
        return "<rustenum '" + self.__name__ + "'>"


class RustEnum(tuple, metaclass=RustEnumMeta):
    def __new__(cls, variant, values):
        instance = super().__new__(cls, values)
        instance._variant = variant
        return instance

    def __repr__(self):
        name = type(self).__name__ + '.' + self._variant
        if self:
            name += '('+ ', '.join(repr(i) for i in self) + ')'
        return name

    def __eq__(self, other):
        return (type(self) == type(other) and
                self._variant == other._variant and
                super().__eq__(other))

    def match(self, **kwargs):
        variants = type(self)._variants

        for k in kwargs:
            if k not in variants and k != '_':
                raise ValueError("'" + k + "' is not a variant of '" +
                                 type(self).__name__ + "'.")

        for v in kwargs.values():
            if not callable(v):
                raise ValueError("'" + repr(v) + "' is not callable.")

        if ('_' not in kwargs) and (set(kwargs) != set(variants)):
            not_handled = ', '.join(set(variants) - set(kwargs))
            raise ValueError("Match not cover all cases.\n"
                             "Not covered: " + not_handled)

        if self._variant in kwargs:
            return kwargs[self._variant](*self)
        else:
            return kwargs['_']()

    @classmethod
    def impl(cls, function):
        setattr(cls, function.__name__, function)
        return function
