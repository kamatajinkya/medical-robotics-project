
def identity(timestamps, raw_readings):
    return raw_readings

def times_2(timestamps, raw_readings):
    return raw_readings * 2

class TimesN:

    def __init__(self, n):
        self.__n = n

    def __call__(self, timestamps, raw_readings):
        return raw_readings * self.__n

algorithms = {
    "idenity" : identity,
    "times_2" : times_2,
    "times_n_3" : TimesN(3)
}
