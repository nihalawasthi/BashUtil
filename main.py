#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTabWidget, QWidget, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QTimer
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

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(5, 5, 5, 0)

        # Apply styles to the parent widget
        self.setStyleSheet("""
            #customNavBar {
                border-left: 4px solid #3c3b3b;
                border-top: 4px solid #3c3b3b;
            }
        """)

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
        self.network_speed_graph.figure.gca().clear()
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
/*              border: 1px solid lightblue;*/
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """

class Browser(QMainWindow):
    def __init__(self, custom_html_path):
        super().__init__()
        self.custom_html_path = custom_html_path
        self.setWindowTitle("PhantomSurf")
        self.setGeometry(100, 100, 1200, 800)
        #self.setStyleSheet("background-color: lightblue;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.nav_bar = CustomNavBar()
        self.nav_bar.back_signal.connect(self.navigate_back)
        self.nav_bar.forward_signal.connect(self.navigate_forward)
        self.nav_bar.reload_signal.connect(self.reload_page)
        self.nav_bar.new_tab_signal.connect(self.add_new_tab)
        self.nav_bar.navigate_signal.connect(self.navigate_to_url)
        main_layout.addWidget(self.nav_bar)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.currentChanged.connect(self.update_close_buttons)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.add_new_tab(label="Home")
        main_layout.addWidget(self.tabs)
        self.tabs.setStyleSheet("""
    QTabBar {
        padding-left: 8px;
        border-left: 4px solid #3c3b3b;
    }

    QTabBar::tab {
        background: white;
        color: gray;
        margin: 4px;
        margin-left: 8px;
        padding: 20px 8px;
        border: none;
    }

    QTabBar::tab:hover {
        background-color:rgb(154, 154, 154);
        color: white;
    }

    QTabBar::tab:selected {
        background-color: #3c3b3b;
        color: white;
        margin-right: 0;
        margin-left: 4px;
        border-right: 4px solid rgb(115, 0, 255);
    }
""")

    def update_close_buttons(self):
        """Update close buttons to only show on the active tab."""
        for i in range(self.tabs.count()):
            close_button = self.tabs.tabBar().tabButton(i, self.tabs.tabBar().RightSide)
            if close_button:
                close_button.setVisible(i == self.tabs.currentIndex())  # Show only for the active tab

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl.fromLocalFile(self.custom_html_path)

        browser = QWebEngineView()
        browser.setUrl(qurl)

        tab_index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentWidget(browser)

        # Add a close button to the tab
        close_button = QPushButton("x")
        close_button.setStyleSheet("""
        QPushButton {
            border: none;
            background: black;
            color: white;
            font-size: 12px;
        }
        QPushButton:hover {
            color: white;
        }
    """)
        close_button.clicked.connect(lambda: self.close_current_tab(tab_index))
        self.tabs.tabBar().setTabButton(tab_index, self.tabs.tabBar().RightSide, close_button)
        self.update_close_buttons()


    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl.fromLocalFile(self.custom_html_path)

        browser = QWebEngineView()
        browser.setUrl(qurl)
        browser.urlChanged.connect(self.update_url_bar)
        
        # Connect favicon and title update signals
        browser.iconChanged.connect(lambda icon, browser=browser: self.update_tab_icon(browser))
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(browser, title))

        tab_index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentWidget(browser)

    def update_tab_icon(self, browser):
        """Update the favicon of the current tab."""
        icon = browser.icon()
        if icon and not icon.isNull():
            index = self.tabs.indexOf(browser)
            if index != -1:
                self.tabs.setTabIcon(index, icon)

    def update_tab_title(self, browser, title):
        """Update the title of the current tab."""
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title)

    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_back(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().back()

    def navigate_forward(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().forward()

    def reload_page(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().reload()

    def navigate_to_url(self, url_text):
        if not url_text.strip():
            return
        qurl = QUrl(url_text if "://" in url_text else "http://" + url_text)
        if self.tabs.currentWidget():
            self.tabs.currentWidget().setUrl(qurl)

    def update_url_bar(self, qurl=None):
        current_widget = self.tabs.currentWidget()
        if current_widget is None:
            self.nav_bar.url_bar.clear()
            return

        if isinstance(current_widget, QWebEngineView):
            qurl = current_widget.url()
            self.nav_bar.url_bar.setText(qurl.toString())
            self.nav_bar.url_bar.setCursorPosition(0)


def load(custom_html):
    app = QApplication(sys.argv)
    QApplication.setApplicationName("PhantomSurf")
    app.setWindowIcon(QIcon("src/icons/xyz.png"))
    window = Browser(custom_html)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    html_path = os.path.join(os.path.dirname(__file__), "templates/index.html")
    load(html_path)