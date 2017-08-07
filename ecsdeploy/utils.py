def dict_map(f):
    def wrapper(t):
        map_tuple = t
        if isinstance(t, dict):
            map_tuple = t.items()
        return list(map(lambda x: f(x), map_tuple))
    return wrapper


def dict_add(c, k, v):
    if v or v == 0:
        c[k] = v

def int_or_none(i):
    return int(i) if i else None
