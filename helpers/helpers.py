def my_propagator(value):
    return value

class OpaqueWrapper:
    def do_something(self, data):
        return data

def id1(x):
    return x

def id2(x):
    return id1(x)

def id3(x):
    return id2(x)
