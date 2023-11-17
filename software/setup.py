import numpy as np
from serial import Serial
from typing import Protocol
import time

class Setup(Protocol):

    def get_readings(self):
        pass

    def set_force(self):
        pass


class ZeroSetup(Setup):

    def __init__(self):
        self.__i = 0

    def get_readings(self):
        time.sleep(0.002)
        self.__i = self.__i + 1
        return self.__i, np.array([[0.0], [0.0], [0.0]]), 0.0
    
    def set_force(self, force):
        print(f'Force set to {force} %')

class PhysicalSetup(Setup):

    def __init__(self, device):
        self.__serial = Serial(device)

    def get_readings(self):
        bytes = self.__serial.readline()
        
        if bytes is None:
            return None
        
        values = [float(value) for value in bytes.decode().split(',')]

        return values[0], np.array([[values[1]], [values[2]], [values[3]]]), values[4]

    def set_force(self, force):
        self.__serial.write(f'{force}')

class RNGBasedSetup(Setup):

    def __init__(self):
        self.__i = 0

    def get_readings(self):
        time.sleep(0.002)
        self.__i = self.__i + 1
        return self.__i, np.array([[np.random.rand()], [np.random.rand()], [np.random.rand()]]), np.random.rand()

    def set_force(self, force):
        print(f'Force set to {force} %')

class SineWaveBasedSetup(Setup):

    def __init__(self):
        self.__i = 0.0
        self.__sample_rate = 0.002

    def get_readings(self):
        time.sleep(self.__sample_rate)
        self.__i = self.__i + 1.0
        theta = 2.0 * np.pi * self.__sample_rate * self.__i
        return \
            self.__i, \
            np.array([
                [np.sin(theta)],
                [np.sin(theta + 2.0*np.pi/3.0)],
                [np.sin(theta - 2.0*np.pi/3.0)]
            ]), \
            np.cos(theta)

    def set_force(self, force):
        print(f'Force set to {force} %')


class FileBasedSetup(Setup):

    def __init__(self):
        ...

    def get_readings(self):
        ...

    def set_force(self, force):
        ...


