import sys

import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import Constants
import Modeling
import Parser
from Constants import FLOAT_SHIFT, GRAPH_LEFT_BORDER, POINTS_COUNT


def slider_update(slider: QtWidgets.QSlider, line_edit: QtWidgets.QLineEdit):
    line_edit.setText(str(slider.value() / FLOAT_SHIFT))


def lineEdit_update(slider: QtWidgets.QSlider, line_edit: QtWidgets.QLineEdit):
    if line_edit.text().replace('.', '', 1).isdigit():
        slider.setValue(min(int(float(line_edit.text()) * FLOAT_SHIFT), slider.maximum() + 12345))
    else:
        line_edit.setText("0")


def load_points(file_path: str):
    with open(file_path, 'r') as file:
        match (file_path.split('.')[-1]):
            case 'txt':
                return Parser.parse_txt_file(file)
            case 'csv':
                return Parser.parse_csv_file(file)


def S1(x: np.array, a, eps, lt):
    if eps == 0:
        return np.array([0.0] * x.size)
    y = (1 + a * x / eps * (1 - np.exp(-lt))) ** eps / np.exp(a * x)
    y[y < 1e-6] = np.NAN
    return y


class ModelingApp(QtWidgets.QMainWindow, Modeling.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.A_arr = []
        self.E_arr = []
        self.T_arr = []

        slider_update(self.sliderA, self.lineEditA)
        slider_update(self.sliderE, self.lineEditE)
        slider_update(self.sliderT, self.lineEditT)

        self.sliderA.valueChanged.connect(lambda: slider_update(self.sliderA, self.lineEditA))
        self.sliderE.valueChanged.connect(lambda: slider_update(self.sliderE, self.lineEditE))
        self.sliderT.valueChanged.connect(lambda: slider_update(self.sliderT, self.lineEditT))

        self.lineEditA.editingFinished.connect(lambda: lineEdit_update(self.sliderA, self.lineEditA))
        self.lineEditE.editingFinished.connect(lambda: lineEdit_update(self.sliderE, self.lineEditE))
        self.lineEditT.editingFinished.connect(lambda: lineEdit_update(self.sliderT, self.lineEditT))

        self.pointsX, self.pointsY = Constants.X_POINTS, Constants.Y_POINTS

        self.rightBorder = max(self.pointsX) * Constants.GRAPH_RIGHT_BORDER_COEFFICIENT
        self.mpl_canvas.canvas.axes.set_xlim(GRAPH_LEFT_BORDER, self.rightBorder)
        self.mpl_canvas.canvas.axes.set_xlabel('доза, Гр')
        self.mpl_canvas.canvas.axes.set_ylabel('SF')
        self.mpl_canvas.canvas.axes.semilogy(self.pointsX, self.pointsY, 'o', label='данные')

        self.buttonGraphPrint.clicked.connect(self.draw_graph)
        self.buttonAddGraph.clicked.connect(self.draw_data_graphs)
        self.buttonImport.clicked.connect(self.import_points)
        self.buttonExport.clicked.connect(self.export_points)

    def draw_graph(self):
        self.update_canvas(False)
        self.update_data(True)

    def draw_data_graphs(self):
        self.update_canvas(True)
        self.update_data(False)

    def import_points(self):
        file_name = QFileDialog.getOpenFileName(self, "Open File", filter="*.txt *.csv")[0]
        if file_name == '':
            return
        self.pointsX, self.pointsY = load_points(file_name)
        self.rightBorder = max(self.pointsX) * Constants.GRAPH_RIGHT_BORDER_COEFFICIENT
        self.update_canvas(False)

    def export_points(self):
        with open('points.txt', 'w', encoding='utf') as file:
            x = np.linspace(GRAPH_LEFT_BORDER, self.rightBorder, 250)
            mvars = self.get_all_variables()
            y = S1(x, mvars[0], mvars[1], mvars[2])
            for i in range(x.size):
                file.write(f'{x[i]} {y[i]}\n')

            message_box = QMessageBox(self)
            message_box.setWindowTitle("Points export")
            message_box.setText("Export complete")
            message_box.setIcon(QMessageBox.Information)
            message_box.exec_()

    def get_lineEdit_num(self, line_edit: QtWidgets.QLineEdit):
        return float(line_edit.text())

    def get_all_variables(self):
        """
        :return: [a, e, t]
        """
        return [self.get_lineEdit_num(self.lineEditA),
                self.get_lineEdit_num(self.lineEditE),
                self.get_lineEdit_num(self.lineEditT)]

    def update_canvas(self, add_old_graphs: bool):
        x = np.linspace(GRAPH_LEFT_BORDER, self.rightBorder, POINTS_COUNT)
        mvars = self.get_all_variables()
        if mvars[1] == 0:
            x = np.array([0.0])
        y = S1(x, mvars[0], mvars[1], mvars[2])

        self.mpl_canvas.canvas.axes.cla()
        self.mpl_canvas.canvas.axes.set_xlabel('доза, Гр')
        self.mpl_canvas.canvas.axes.set_ylabel('SF')

        self.mpl_canvas.canvas.axes.semilogy(x, y, 'r', label=f'{mvars[0]} {mvars[1]} {mvars[2]}')
        self.mpl_canvas.canvas.axes.semilogy(self.pointsX, self.pointsY, 'o', label='данные')

        if add_old_graphs:
            self.add_graphs()

        self.mpl_canvas.canvas.axes.legend(loc='best')
        self.mpl_canvas.canvas.axes.set_xlim(GRAPH_LEFT_BORDER, self.rightBorder)
        self.mpl_canvas.canvas.draw()

    def add_graphs(self):
        for i in range(len(self.A_arr)):
            x = np.linspace(GRAPH_LEFT_BORDER, self.rightBorder, POINTS_COUNT)
            y = S1(x, self.A_arr[i], self.E_arr[i], self.T_arr[i])
            self.mpl_canvas.canvas.axes.semilogy(x, y, label=f'{self.A_arr[i]} {self.E_arr[i]} {self.T_arr[i]}')

    def update_data(self, delete_old_data: bool):
        if delete_old_data:
            self.A_arr.clear()
            self.E_arr.clear()
            self.T_arr.clear()
        mvars = self.get_all_variables()
        self.A_arr.append(mvars[0])
        self.E_arr.append(mvars[1])
        self.T_arr.append(mvars[2])


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ModelingApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
