count = 0
for i in ''.__class__.__mro__[1].__subclasses__():
    #if isinstance(i, wrapper_descriptor):
    print('index %s: %s' % (count,i))
    count += 1

