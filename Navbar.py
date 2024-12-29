from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QPainter, QColor
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
        self.setObjectName("customNavBar")
        self.init_ui()
        self.network_speeds = [0] * 50 

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(5, 5, 5, 0)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(palette)

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
            "border: 1px solid #6BEC75; border-radius: 5px; padding-left: 10px;"
        )
        self.url_bar.returnPressed.connect(self.emit_url)

        self.bookmark_button = QPushButton("⛉")
        self.bookmark_button.setFixedSize(30, 30)
        self.bookmark_button.setStyleSheet(self.button_style())

        self.network_speed_graph = FigureCanvas(plt.Figure(figsize=(2, 1)))
        self.network_speed_graph.setToolTip('Hover to see network speed')
        ax = self.network_speed_graph.figure.add_subplot(111)
        ax.barh([0], [0], color='#4CAF50')  # Initial bar
        ax.set_xlim(0, 100)
        ax.set_yticks([])  # Hide y-axis ticks
        ax.set_xticks([])  # Hide x-axis ticks

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
        """Update the network speed graph with scrolling effect."""
        net = psutil.net_io_counters()
        bytes_sent = net.bytes_sent - self.prev_net.bytes_sent
        bytes_recv = net.bytes_recv - self.prev_net.bytes_recv
        total_speed = (bytes_sent + bytes_recv) / 1024
        self.network_speeds.append(min(int(total_speed), 100))
        if len(self.network_speeds) > 50:
            self.network_speeds.pop(0)

        ax = self.network_speed_graph.figure.gca()
        ax.clear()
        ax.bar(range(len(self.network_speeds)), self.network_speeds, color='#6BEC75', width=1.0)
        ax.axis('off')
        if total_speed >= 1024:
            speed_display = f"{total_speed / 1024:.2f} MB/s"
        else:
            speed_display = f"{total_speed:.2f} KB/s"
        self.network_speed_graph.setToolTip(f"Packet Transfer Speed: {speed_display}")
        self.network_speed_graph.draw()
        self.prev_net = net

    def paintEvent(self, event):
        """Custom painting to add a left border."""
        super().paintEvent(event)
        painter = QPainter(self)
        border_color = QColor("#3c3b3b")
        border_width = 4
        painter.setPen(border_color)
        painter.setBrush(border_color)
        painter.drawRect(0, 0, border_width, self.height())
        painter.end()

    @staticmethod
    def button_style():
        return """
            QPushButton {
                color: white;
                border-radius: 5px;
                background-color: black;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """