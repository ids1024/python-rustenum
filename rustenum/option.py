from rustenum import RustEnum

class Option(RustEnum):
    Some = 1
    None_ = 0

@Option.impl
def unwrap(self):
    def fail():
        raise ValueError("Called unwrap() on None_")

    return self.match(
        Some = lambda x: x,
        None_ = fail
    )
    
@Option.impl
def map(self, callback):
    return self.match(
        Some = lambda x: Some(callback(x)),
        None_ = lambda: None_
    )

Some = Option.Some
None_ = Option.None_
