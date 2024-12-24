from PyQt5.QtWidgets import (
    QMainWindow, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget, QApplication, QGraphicsView, QGraphicsScene
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class CustomNavBar(QWidget):
    back_signal = pyqtSignal()
    forward_signal = pyqtSignal()
    reload_signal = pyqtSignal()
    new_tab_signal = pyqtSignal()
    navigate_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        nav_bar_layout = QHBoxLayout()
        nav_bar_layout.setContentsMargins(0, 0, 0, 0)
        nav_bar_layout.setSpacing(5)

        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setFixedSize(30, 30)
        self.new_tab_button.setStyleSheet(self.button_style())
        self.new_tab_button.clicked.connect(self.new_tab_signal.emit)

        self.back_button = QPushButton("<")
        self.back_button.setFixedSize(30, 30)
        self.back_button.setStyleSheet(self.button_style())
        self.back_button.clicked.connect(self.back_signal.emit)

        self.forward_button = QPushButton(">")
        self.forward_button.setFixedSize(30, 30)
        self.forward_button.setStyleSheet(self.button_style())
        self.forward_button.clicked.connect(self.forward_signal.emit)

        self.reload_button = QPushButton("⟳")
        self.reload_button.setFixedSize(30, 30)
        self.reload_button.setStyleSheet(self.button_style())
        self.reload_button.clicked.connect(self.reload_signal.emit)

        self.home_btn = QPushButton("🏠︎", self)
        self.home_btn.setFixedSize(30, 30)
        self.home_btn.setStyleSheet(self.button_style())

        url_bar_layout = QHBoxLayout()
        url_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Surf the web or enter the URL")
        self.url_bar.setFixedHeight(30)
        self.url_bar.setStyleSheet(
            "border: 1px solid lightblue; border-radius: 5px; padding-left: 10px;"
        )
        self.url_bar.returnPressed.connect(self.emit_url)

        self.bookmark_button = QPushButton("⛉")
        self.bookmark_button.setFixedSize(30, 30)
        self.bookmark_button.setStyleSheet(self.button_style())

        # Replacing QProgressBar with Matplotlib Bar Graph
        self.network_speed_graph = FigureCanvas(plt.Figure(figsize=(2, 1)))
        ax = self.network_speed_graph.figure.add_subplot(111)
        ax.barh([0], [0], color='#4CAF50')  # Initial bar
        ax.set_xlim(0, 100)
        ax.set_yticks([])  # Hide y-axis ticks
        ax.set_xticks([0, 50, 100])  # X-axis ticks for scale
        ax.set_xticklabels([0, 50, 100])

        url_bar_layout.addWidget(self.url_bar)
        url_bar_layout.addWidget(self.bookmark_button)
        url_bar_layout.addWidget(self.network_speed_graph)
        self.tools_button = QPushButton("🛠️")
        self.tools_button.setFixedSize(30, 30)
        self.tools_button.setStyleSheet(self.button_style())

        self.menu_button = QPushButton("☰")
        self.menu_button.setFixedSize(30, 30)
        self.menu_button.setStyleSheet(self.button_style())

        nav_bar_layout.addWidget(self.new_tab_button)
        nav_bar_layout.addWidget(self.back_button)
        nav_bar_layout.addWidget(self.forward_button)
        nav_bar_layout.addWidget(self.reload_button)
        nav_bar_layout.addWidget(self.home_btn)
        nav_bar_layout.addLayout(url_bar_layout)
        nav_bar_layout.addWidget(self.tools_button)
        nav_bar_layout.addWidget(self.menu_button)

        main_layout.addLayout(nav_bar_layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_network_speed)
        self.timer.start(1000)
        self.prev_net = psutil.net_io_counters()

    def emit_url(self):
        """Emit the text from the URL bar."""
        self.navigate_signal.emit(self.url_bar.text())

    def update_network_speed(self):
        """Update the network speed graph based on actual network usage."""
        net = psutil.net_io_counters()
        bytes_sent = net.bytes_sent - self.prev_net.bytes_sent
        bytes_recv = net.bytes_recv - self.prev_net.bytes_recv
        total_speed = (bytes_sent + bytes_recv) / 1024
        # Update bar graph
        self.network_speed_graph.figure.gca().clear()  # Clear previous graph
        ax = self.network_speed_graph.figure.add_subplot(111)
        ax.barh([0], [min(int(total_speed), 100)], color='#4CAF50')
        ax.set_xlim(0, 100)
        ax.set_yticks([])  # Hide y-axis ticks
        ax.set_xticks([0, 50, 100])  # X-axis ticks for scale
        ax.set_xticklabels([0, 50, 100])
        self.network_speed_graph.draw()
        self.prev_net = net

    @staticmethod
    def button_style():
        return """
            QPushButton {
                border: 1px solid lightblue;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """


if __name__ == "__main__":
    app = QApplication([])
    window = CustomNavBar()
    window.show()
    app.exec()
