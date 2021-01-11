import math

def to_real(x):
    """
    Convert Z3 Fractional numbers into floating points
    """
    return float(x.numerator_as_long()/x.denominator_as_long())

def Hellinger_distance(P, Q):
        """
        Hellinger_distance between two probability distribution.
        """
        dist = 0.0
        for p, q in zip(P, Q):
            dist += (math.sqrt(p) - math.sqrt(q)) ** 2

        dist = math.sqrt(dist)
        dist /= math.sqrt(2)

        return dist
    
XES_NES = { 'xes': 'rttp://www.w3.org/2001/XMLSchema' }

def node_from_key(root, key):
    for atr in root:
        if 'key' in atr.attrib and atr.attrib['key'] == key:
            return atr
    return None

