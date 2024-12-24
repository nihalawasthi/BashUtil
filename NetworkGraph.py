#!/usr/bin/env python3
import sys
import psutil
from collections import deque
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
import pyqtgraph as pg


class NetworkMonitorGraph(QWidget):
    def __init__(self, parent=None, max_points=60):
        super().__init__(parent)
        self.setWindowTitle("Network Speed Monitor (Graph)")
        self.max_points = max_points  # Allow dynamic max_points
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Graph widget setup
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("transparent")
        self.graph_widget.setLabel("left", "Speed (KB/s)", color="white", size="12pt")
        self.graph_widget.setLabel("bottom", "Time (s)", color="white", size="12pt")
        self.graph_widget.addLegend()

        # Remove grid
        self.graph_widget.showGrid(x=False, y=False)

        # Data queues
        self.download_speeds = deque([0] * self.max_points, maxlen=self.max_points)
        self.upload_speeds = deque([0] * self.max_points, maxlen=self.max_points)
        self.time_ticks = deque(range(-self.max_points + 1, 1), maxlen=self.max_points)

        # Plot lines
        self.download_plot = self.graph_widget.plot(
            pen=pg.mkPen("cyan", width=2), name="Download Speed"
        )
        self.upload_plot = self.graph_widget.plot(
            pen=pg.mkPen("magenta", width=2), name="Upload Speed"
        )

        layout.addWidget(self.graph_widget)

        # Initial network stats
        self.previous_stats = psutil.net_io_counters()

        # Timer to update data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(1000)

    def update_graph(self):
        # Get current network stats
        current_stats = psutil.net_io_counters()

        # Calculate download and upload speeds
        download_speed = (current_stats.bytes_recv - self.previous_stats.bytes_recv) / 1024
        upload_speed = (current_stats.bytes_sent - self.previous_stats.bytes_sent) / 1024

        # Append data to queues
        self.download_speeds.append(download_speed)
        self.upload_speeds.append(upload_speed)
        self.time_ticks.append(self.time_ticks[-1] + 1)

        # Update previous stats
        self.previous_stats = current_stats

        # Update the graph lines
        self.download_plot.setData(self.time_ticks, list(self.download_speeds))
        self.upload_plot.setData(self.time_ticks, list(self.upload_speeds))

'''
if __name__ == "__main__":
    app = QApplication(sys.argv)
    monitor = NetworkMonitorGraph()
    monitor.resize(800, 400)  # Initial size of the widget
    monitor.show()
    sys.exit(app.exec_())'''
