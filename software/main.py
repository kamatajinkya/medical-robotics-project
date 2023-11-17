import numpy as np
from ui_qt import UI
from setup import PhysicalSetup, RNGBasedSetup, FileBasedSetup, SineWaveBasedSetup, ZeroSetup
import argparse
from algorithms import algorithms

def main():

    setup_map = {
        'phy' : PhysicalSetup,
        'rng' : RNGBasedSetup,
        'file' : FileBasedSetup,
        'sin' : SineWaveBasedSetup,
        'zero' : ZeroSetup
    }

    parser = argparse.ArgumentParser(
        prog='Surgial Robots Project',
        description='Recieves data from setup plots the results and saves them',
        epilog='For more info contact Ajinkya Kamat (ajinkyak@andrew.cmu.edu)'
    )

    parser.add_argument('-s', '--setup', choices=setup_map.keys(), default='phy')
    parser.add_argument('-a', '--azimuth', required=True, type=float)
    parser.add_argument('-e', '--elevation', required=True, type=float)
    args = parser.parse_args()

    setup = setup_map[args.setup]()
    force_orientation = (np.deg2rad(args.azimuth), np.deg2rad(args.elevation))

    timestamps = np.ndarray((1, 0))
    raw_readings = np.ndarray((3, 0))
    measured_forces = np.ndarray((3, 0))

    ui = UI(setup.set_force)

    while True:
        
        timestamp, raw_reading, measured_force_reading = setup.get_readings()

        measured_force = np.array([
            [measured_force_reading * np.cos(force_orientation[0]) * np.cos(force_orientation[1])],
            [measured_force_reading * np.sin(force_orientation[0]) * np.cos(force_orientation[1])],
            [measured_force_reading * np.sin(force_orientation[1])]
        ])
        
        timestamps = np.append(timestamps, timestamp)
        raw_readings = np.hstack([raw_readings, raw_reading])
        measured_forces = np.hstack([measured_forces, measured_force])

        infered_forces = {name : algorithm(timestamps, raw_readings) for (name, algorithm) in algorithms.items()}
        ui.update(timestamps, raw_readings, infered_forces, measured_forces, force_orientation)


if __name__ == '__main__':
    main()