def get_top_parent(obj):
    return obj.__class__.mro()[-2]
