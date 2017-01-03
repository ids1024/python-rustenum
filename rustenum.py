import types


class RustEnumVariantBase(tuple):
    def __new__(cls, *args):
        if len(args) != cls._num:
            name = type(cls).__name__ + '.' + cls.__name__
            raise TypeError("Wrong number of arguments to " + name)
        return super().__new__(cls, args)

    def __repr__(self):
        name = type(type(self)).__name__ + '.' + type(self).__name__
        return "{}({})".format(name, ', '.join(repr(i) for i in self))

    def __getattr__(self, name):
        if name in type(type(self))._impls:
            return types.MethodType(type(type(self))._impls[name], self)
        raise AttributeError

    def match(self, **kwargs):
        variants = [i.__name__ for i in type(type(self))]

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

        if type(self).__name__ in kwargs:
            return kwargs[type(self).__name__](*self)
        else:
            return kwargs['_']()


class RustEnumMeta(type):
    def __new__(metacls, cls, bases, classdict):
        variants = {}
        impls = {}

        for k in list(classdict):
            if not k.startswith("_"):
                if callable(classdict[k]):
                    impls[k] = (classdict[k])
                else:
                    variants[k] = classdict[k]
                del classdict[k]

        classdict["_variants"] = [];
        classdict["_impls"] = impls;

        instance = super().__new__(metacls, cls, bases, classdict)

        for k, v in variants.items():
            subinstance = instance(k, (RustEnumVariantBase,), {"_num": v})
            instance._variants.append(subinstance)
            setattr(instance, k, subinstance)

        return instance

    def __repr__(self):
        return "<rustenum '" + self.__name__ + "'>"

    def __iter__(self):
        return iter(self._variants)

    def impl(self, function):
        self._impls[function.__name__] = function
        return function


class RustEnum(type, metaclass=RustEnumMeta):
    def __repr__(self):
        name = type(self).__name__ + '.' + self.__name__
        return "<{}>".format(name)
