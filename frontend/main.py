
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGroupBox, QCheckBox, QPushButton, QGridLayout,
                             QRadioButton, QMainWindow, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
import pyqtgraph as pg

class EntropyMaxWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EntropyMax")
        self.setFixedSize(900, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QGridLayout()
        self.central_widget.setLayout(main_layout)

        # Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        # chart_menu = menubar.addMenu("&ChartOptions")
        # help_menu = menubar.addMenu("&Help")

        exit_action = file_menu.addAction("&Exit")
        exit_action.triggered.connect(self.close)
        
        # copy_action = chart_menu.addAction("&Copy")
        
        # contents_action = help_menu.addAction("&Contents")
        # about_action = help_menu.addAction("&About")


        # Input Group
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout()
        input_group.setLayout(input_layout)
        select_input_button = QPushButton("Select Input File")
        select_input_button.clicked.connect(self.select_input_file)
        input_layout.addWidget(select_input_button)
        main_layout.addWidget(input_group, 0, 0)

        # Output Group
        output_group = QGroupBox("Output")
        output_layout = QGridLayout()
        output_group.setLayout(output_layout)
        define_output_button = QPushButton("Define Output Filename")
        define_output_button.clicked.connect(self.define_output_file)
        output_layout.addWidget(define_output_button, 0, 0, 2, 1)
        
        composite_radio = QRadioButton("Composite")
        composite_radio.setChecked(True)
        individual_radio = QRadioButton("Individual")
        both_radio = QRadioButton("Both")
        
        output_layout.addWidget(composite_radio, 0, 1)
        output_layout.addWidget(individual_radio, 0, 2)
        output_layout.addWidget(both_radio, 0, 3)

        main_layout.addWidget(output_group, 0, 1, 1, 3)

        # Processing Options Group
        processing_group = QGroupBox("Processing Options")
        processing_layout = QHBoxLayout()
        processing_group.setLayout(processing_layout)
        
        perm_check = QCheckBox("Do Permutations")
        perm_check.setChecked(True)
        prop_check = QCheckBox("Take row proportions")
        groups_check = QCheckBox("Do 2 to 20 Groups")
        groups_check.setChecked(True)

        processing_layout.addWidget(perm_check)
        processing_layout.addWidget(prop_check)
        processing_layout.addWidget(groups_check)
        main_layout.addWidget(processing_group, 1, 0, 1, 2)

        # Buttons
        proceed_button = QPushButton("Proceed")
        proceed_button.clicked.connect(self.plot_data)
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)

        main_layout.addWidget(proceed_button, 1, 2)
        main_layout.addWidget(exit_button, 1, 3)


        # Chart Group
        chart_group = QGroupBox("Chart")
        chart_layout = QVBoxLayout()
        chart_group.setLayout(chart_layout)
        
        self.plot_widget = pg.PlotWidget()
        chart_layout.addWidget(self.plot_widget)
        
        main_layout.addWidget(chart_group, 2, 0, 1, 4)

    def select_input_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select Input File")
        if file_path:
            QMessageBox.information(self, "File Selected", f"Selected: {file_path}")
    def define_output_file(self):
        file_dialog = QFileDialog(self)
        # _ is a file filter        
        file_path, _ = file_dialog.getSaveFileName(self, "Define Output Filename")
        if file_path:
            QMessageBox.information(self, "Output File", f"Output: {file_path}")

    def plot_data(self):
        # Sample data
        x = [i for i in range(2, 21)]
        y_ch = [i**2 for i in x] # Sample C-H data
        y_rs = [i*10 for i in x] # Sample Rs data

        self.plot_widget.clear()
        self.plot_widget.plot(x, y_ch, pen='b', name='C-H')
        self.plot_widget.plot(x, y_rs, pen='r', name='Rs')
        self.plot_widget.addLegend()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EntropyMaxWindow()
    window.show()
    sys.exit(app.exec())
