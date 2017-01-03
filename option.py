from rustenum import RustEnum

Option = RustEnum("Object", Some=1, None_=0)

@Option.impl
def unwrap(self):
    def fail():
        raise ValueError("Called unwrap() on None_")

    return self.match(
        Some = lambda x: x,
        None_ = fail
    )

Some = Option.Some
None_ = Option.None_
