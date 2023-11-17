import numpy as np
from datetime import datetime
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QSlider, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

class UI:

    def __init__(self, set_force):

        self.__buffer_size = 200
        self.__set_force = set_force

        self.__app = pg.mkQApp("Surgical")
        self.__windows = QWidget()
        
        self.__main_layout = QHBoxLayout(self.__windows)
        self.__left_panel_layout = QVBoxLayout()

        self.__save_button = QPushButton("Save Data")
        self.__left_panel_layout.addWidget(self.__save_button)

        self.__force_layout = QHBoxLayout()
        self.__force_slider = QSlider(Qt.Orientation.Horizontal)
        self.__force_slider.setMaximum(100)
        self.__force_text_box = QLineEdit()
        self.__force_text_box.setMaximumWidth(40)
        self.__force_text_validator = QIntValidator(0, 100)
        self.__force_text_box.setValidator(self.__force_text_validator)
        self.__force_layout.addWidget(self.__force_slider)
        self.__force_layout.addWidget(self.__force_text_box)
        self.__left_panel_layout.addLayout(self.__force_layout)

        self.__force_3d_widget = gl.GLViewWidget()
        self.__force_3d_grid = gl.GLGridItem()
        self.__left_panel_layout.addWidget(self.__force_3d_widget)
        self.__force_3d_widget.addItem(self.__force_3d_grid)
        self.__main_layout.addLayout(self.__left_panel_layout, 2)
        self.__force_3d_lines = {}
        self.__force_3d_text = {}

        self.__plot_widget = pg.GraphicsLayoutWidget()
        self.__main_layout.addWidget(self.__plot_widget)

        pg.setConfigOptions(antialias=True)

        self.__colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']

        self.__raw_readings_plot = self.__plot_widget.addPlot(title="Raw Sensor Readings")
        self.____raw_readings_curves = []
        self.__raw_readings_plot.addLegend()

        self.__plot_widget.nextRow()
        
        self.__force_x_plot = self.__plot_widget.addPlot(title="Force along X axis")
        self.__force_x_curves = {}
        self.__force_x_plot.addLegend()

        self.__plot_widget.nextRow()

        self.__force_y_plot = self.__plot_widget.addPlot(title="Force along Y axis")
        self.__force_y_curves = {}
        self.__force_y_plot.addLegend()

        self.__plot_widget.nextRow()

        self.__force_z_plot = self.__plot_widget.addPlot(title="Force along Z axis")
        self.__force_z_curves = {}
        self.__force_z_plot.addLegend()
        
        self.__windows.show()

        self.__force_slider.sliderReleased.connect(self.__force_slider_released)
        self.__force_slider.valueChanged.connect(self.__force_slider_changed)
        self.__force_text_box.editingFinished.connect(self.__force_text_box_edited)
        self.__save_button.clicked.connect(self.__save_data)

        self.__timer = QtCore.QTimer()
        self.__timer.timeout.connect(self.__redraw_data)
        self.__timer.start(50)

    def __save_data(self, i):
        filename = f'{datetime.now():%Y%m%d%H%M%S}.txt'
        
        data = np.vstack(
            [self.__timestamps, self.__raw_readings] \
            + [value for value in self.__forces.values()]
        ).T
        
        alogrithms_used = ",".join([key for key in self.__forces.keys()])

        np.savetxt(filename, data, header=f'Timestamp,Raw,{alogrithms_used}; Orientation : {self.__force_orientation}')

    def __force_text_box_edited(self):
        force = int(self.__force_text_box.text())
        self.__force_slider.setValue(force)
        self.__set_force(force)

    def __force_slider_released(self):
        self.__set_force(int(self.__force_text_box.text()))

    def __force_slider_changed(self):
        self.__force_text_box.setText(f'{self.__force_slider.value()}')
        
    def __redraw_data(self):

        for i, raw_reading in enumerate(self.__raw_readings):

            if len(self.____raw_readings_curves) <= i:
                self.____raw_readings_curves.append(self.__raw_readings_plot.plot(pen=self.__colors[i], name=f'Sensor {i} Raw'))
            
            self.____raw_readings_curves[i].setData(
                self.__timestamps[-self.__buffer_size:],
                raw_reading[-self.__buffer_size:]
            )

        for key, force in self.__forces.items():
            
            if key not in self.__force_x_curves.keys():
                color = self.__colors[len(self.__force_x_curves.keys())]
                self.__force_x_curves[key] = self.__force_x_plot.plot(pen=color, name=key)

            self.__force_x_curves[key].setData(
                self.__timestamps[-self.__buffer_size:],
                force[0, -self.__buffer_size:]
            )

            if key not in self.__force_y_curves.keys():
                color = self.__colors[len(self.__force_y_curves.keys())]
                self.__force_y_curves[key] = self.__force_y_plot.plot(pen=color, name=key)

            self.__force_y_curves[key].setData(
                self.__timestamps[-self.__buffer_size:],
                force[1, -self.__buffer_size:]
            )

            if key not in self.__force_z_curves.keys():
                color = self.__colors[len(self.__force_z_curves.keys())]
                self.__force_z_curves[key] = self.__force_z_plot.plot(pen=color, name=key)

            self.__force_z_curves[key].setData(
                self.__timestamps[-self.__buffer_size:],
                force[2, -self.__buffer_size:]
            )

            if key not in self.__force_3d_lines.keys():
                color = self.__colors[len(self.__force_x_curves.keys())]
                self.__force_3d_lines[key] = gl.GLLinePlotItem(color=color, antialias=True)
                self.__force_3d_widget.addItem(self.__force_3d_lines[key])

                self.__force_3d_text[key] = gl.GLTextItem(color=color, text=key)
                self.__force_3d_widget.addItem(self.__force_3d_text[key])

            self.__force_3d_lines[key].setData(pos=np.array([[0, 0, 0], force[:, -1]]))
            self.__force_3d_text[key].setData(pos=force[:, -1])



    def update(self, timestamps, raw_readings, infered_forces, measured_forces, force_orientation):
        
        self.__timestamps = timestamps
        self.__raw_readings = raw_readings
        self.__forces = infered_forces
        self.__forces['Measured'] = measured_forces
        self.__force_orientation = force_orientation

        self.__app.processEvents()