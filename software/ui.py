import csv
from datetime import datetime
from matplotlib.gridspec import GridSpec
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import numpy as np
import matplotlib
matplotlib.use('TKAgg') 

class UI:

    def __init__(self, set_force):

        self.__buffer_size = 20
        self.__set_force = set_force

        self.__fig = plt.figure()

        grid_spec = GridSpec(nrows=3, ncols=2, figure=self.__fig)
        self.__raw_readings_axes = self.__fig.add_subplot(grid_spec[5])
        self.__force_3d_axes = self.__fig.add_subplot(grid_spec[0:2, 1], projection='3d')
        self.__force_x_axes = self.__fig.add_subplot(grid_spec[0])
        self.__force_y_axes = self.__fig.add_subplot(grid_spec[2])
        self.__force_z_axes = self.__fig.add_subplot(grid_spec[4])

        self.__fig.subplots_adjust(bottom=0.1)
        
        self.__applied_force_slider_axes = self.__fig.add_axes([0.2, 0.03, 0.2, 0.03])
        self.__applied_force_slider = Slider(
            ax=self.__applied_force_slider_axes,
            label='Applied force [%]',
            valmin=0,
            valmax=100,
            valinit=1,
        )
        self.__applied_force_slider.on_changed(self.__update_force_slider)

        self.__save_data_button = self.__fig.add_axes([0.55, 0.03, 0.4, 0.03])
        self.__text_box = Button(self.__save_data_button, "Save Data")
        self.__text_box.on_clicked(self.__save_data)
        
        self.__animation = animation.FuncAnimation(self.__fig, self.__animate, interval=1000, cache_frame_data=False)
        self.__should_show = True

    def __update_force_slider(self, force):
        self.__set_force(int(force))

    def __save_data(self, i):
        filename = f'{datetime.now():%Y%m%d%H%M%S}.txt'
        
        data = np.vstack(
            [self.__timestamps, self.__raw_readings, self.__measured_forces] \
            + [value for value in self.__infered_forces.values()]
        ).T
        
        alogrithms_used = ",".join([key for key in self.__infered_forces.keys()])

        np.savetxt(filename, data, header=f'Algos : {alogrithms_used}; Orientation : {self.__force_orientation}')

    def __animate(self, i):
        
        self.__raw_readings_axes.clear()
        for i, raw_reading in enumerate(self.__raw_readings):
            
            self.__raw_readings_axes.plot(
                self.__timestamps[-self.__buffer_size:],
                raw_reading[-self.__buffer_size:],
                label=f'Sensor {i} Raw'
            )
        self.__raw_readings_axes.legend()

        
        self.__force_x_axes.clear()
        self.__force_y_axes.clear()
        self.__force_z_axes.clear()
        self.__force_3d_axes.clear()

        self.__force_x_axes.plot(
            self.__timestamps[-self.__buffer_size:],
            self.__measured_forces[0, -self.__buffer_size:],
            label='Measured'
        )
        self.__force_y_axes.plot(
            self.__timestamps[-self.__buffer_size:],
            self.__measured_forces[1, -self.__buffer_size:],
            label='Measured'
        )
        self.__force_z_axes.plot(
            self.__timestamps[-self.__buffer_size:],
            self.__measured_forces[2, -self.__buffer_size:],
            label='Measured'
        )
        self.__force_3d_axes.plot(
                [0.0, self.__measured_forces[0, -1]],
                [0.0, self.__measured_forces[1, -1]],
                [0.0, self.__measured_forces[2, -1]],
            label='Measured'
        )

        for algorithm, force in self.__infered_forces.items():

            self.__force_x_axes.plot(
                self.__timestamps[-self.__buffer_size:],
                force[0, -self.__buffer_size:],
                label=algorithm
            )
            self.__force_y_axes.plot(
                self.__timestamps[-self.__buffer_size:],
                force[1, -self.__buffer_size:],
                label=algorithm
            )
            self.__force_z_axes.plot(
                self.__timestamps[-self.__buffer_size:],
                force[2, -self.__buffer_size:],
                label=algorithm
            )
            
            self.__force_3d_axes.plot(
                [0.0, force[0, -1]],
                [0.0, force[1, -1]],
                [0.0, force[2, -1]],
                label=algorithm
            )

        self.__force_x_axes.legend()
        self.__force_y_axes.legend()
        self.__force_z_axes.legend()
        self.__force_3d_axes.legend()

        self.__raw_readings_axes.set_title('Raw Readings')
        self.__force_3d_axes.set_title('Forces in 3D')
        self.__force_x_axes.set_title('Forces along x axis')
        self.__force_y_axes.set_title('Forces along y axis')
        self.__force_z_axes.set_title('Forces along z axis')

        plt.draw()
        

    def update(self, timestamps, raw_readings, infered_forces, measured_forces, force_orientation):
        
        self.__timestamps = timestamps
        self.__raw_readings = raw_readings
        self.__infered_forces = infered_forces
        self.__measured_forces = measured_forces
        self.__force_orientation = force_orientation
        
        plt.pause(0.001)

        if self.__should_show:
            plt.show(block=False)
            
            self.__should_show = False