import types


class RustEnumVariant:
    def __init__(self, enum_class, name, num):
        self._enum_class = enum_class
        self._name = name
        self._num = num

    def __call__(self, *args):
        if len(args) != self._num:
            name = self._enum_class.__name__ + '.' + self._name
            raise TypeError("Wrong number of arguments to " + name)
        return self._enum_class(self._name, args)

    def __repr__(self):
        return self._enum_class.__name__ + '.' + self._name


class RustEnumMeta(type):
    def __new__(metacls, cls, bases, classdict):
        variants = {}
        impls = {}

        for k in list(classdict):
            if not k.startswith("_") and not k == "match":
                if callable(classdict[k]):
                    impls[k] = (classdict[k])
                else:
                    variants[k] = classdict[k]
                del classdict[k]

        classdict["_variants"] = variants;
        classdict["_impls"] = impls;

        instance = super().__new__(metacls, cls, bases, classdict)

        for k, v in variants.items():
            variant = RustEnumVariant(instance, k, v)
            setattr(instance, k, variant)

        return instance

    def __repr__(self):
        return "<rustenum '" + self.__name__ + "'>"

    def impl(self, function):
        self._impls[function.__name__] = function
        return function


class RustEnum(tuple, metaclass=RustEnumMeta):
    def __new__(cls, variant, values):
        instance = super().__new__(cls, values)
        instance._variant = variant
        return instance

    def __repr__(self):
        name = type(self).__name__ + '.' + self._variant
        return "{}({})".format(name, ', '.join(repr(i) for i in self))

    def __getattr__(self, name):
        if name in type(self)._impls:
            return types.MethodType(type(self)._impls[name], self)
        raise AttributeError

    def match(self, **kwargs):
        variants = type(self)._variants

        for k in kwargs:
            if k not in variants and k != '_':
                raise ValueError("'" + k + "' is not a variant of '" +
                                 type(type(self)).__name__ + "'.")

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
