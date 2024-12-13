import sys
import os
import socket
import ssl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QLineEdit,
    QToolBar, QAction, QStatusBar, QSplitter, QPushButton, QHBoxLayout, QTabBar
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt

class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        self.port = 80 if self.scheme == "http" else 443
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        request = f"GET {self.path} HTTP/1.0\r\nHost: {self.host}\r\n\r\n"
        s.send(request.encode("utf8"))
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        content = response.read()
        s.close()
        return content
    
class Browser(QMainWindow):
    def __init__(self, custom_html_path):
        super().__init__()
        self.custom_html_path = custom_html_path
        self.theme = "dark"
        self.setStyleSheet(self.get_stylesheet())

        main_layout = QSplitter(Qt.Horizontal)
        main_layout.setSizes([200, 800])
        self.setCentralWidget(main_layout)

        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        sidebar_layout.addWidget(self.tabs)

        # Bottom Tab Bar Buttons
        bottom_bar = QHBoxLayout()
        self.tools_btn = QPushButton("🛠️")
        self.settings_btn = QPushButton("⚙️")
        self.theme_toggle_btn = QPushButton("🌙")
        self.menu_btn = QPushButton("☰")

        for btn in [self.tools_btn, self.settings_btn, self.theme_toggle_btn, self.menu_btn]:
            btn.setFixedSize(40, 40)
            bottom_bar.addWidget(btn)

        bottom_bar.setSpacing(5)
        bottom_bar.addStretch()
        sidebar_layout.addLayout(bottom_bar)

        sidebar_widget.setLayout(sidebar_layout)

        # Browser Layout
        browser_widget = QWidget()
        self.browser_layout = QVBoxLayout()
        browser_widget.setLayout(self.browser_layout)

        # Navigation Toolbar
        nav_toolbar = QToolBar("Navigation")
        self.addToolBar(nav_toolbar)

        # New Tab Button
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setFixedSize(25, 25)
        self.new_tab_button.clicked.connect(lambda: self.add_new_tab(label="New Tab"))
        nav_toolbar.addWidget(self.new_tab_button)

        # Navigation Buttons
        back_btn = QAction("<", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        nav_toolbar.addAction(back_btn)

        forward_btn = QAction(">", self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        nav_toolbar.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        nav_toolbar.addAction(reload_btn)

        home_btn = QAction("🏠︎", self)
        home_btn.triggered.connect(self.navigate_home)
        nav_toolbar.addAction(home_btn)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search Surf or enter the URL")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.focusInEvent = self.clear_placeholder_on_focus
        nav_toolbar.addWidget(self.url_bar)

        # Bookmark Button
      # bookmark_btn = QPushButton("⛉")
        bookmark_btn = QPushButton("⚐")
        bookmark_btn.setFixedSize(30, 30)
        nav_toolbar.addWidget(bookmark_btn)

        # Status Bar
        self.setStatusBar(QStatusBar())

        # Adding Layouts
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(browser_widget)
        main_layout.setStretchFactor(1, 1)

        # Load Default Tab
        self.add_new_tab(label="Home")

        # Theme Toggle
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)

    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_home(self):
        home_url = QUrl.fromLocalFile(self.custom_html_path)
        self.tabs.currentWidget().setUrl(home_url)
        self.url_bar.setText("Search Surf or enter the URL")
        self.url_bar.setCursorPosition(0)

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl.fromLocalFile(self.custom_html_path)

        browser = QWebEngineView()
        browser.setUrl(qurl)

        tab_index = self.tabs.addTab(browser, label)
        close_btn = QPushButton("x")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(lambda: self.tabs.removeTab(tab_index))
        self.tabs.tabBar().setTabButton(tab_index, QTabBar.RightSide, close_btn)

        browser.urlChanged.connect(self.update_url_bar)
        self.tabs.setCurrentWidget(browser)

        self.url_bar.setText("Search Surf or enter the URL")
        self.url_bar.setCursorPosition(0)

    def navigate_to_url(self):
        url_text = self.url_bar.text()
        if not url_text.strip():
            return  # Do nothing if the URL bar is empty
        qurl = QUrl(url_text if "://" in url_text else "http://" + url_text)
        self.tabs.currentWidget().setUrl(qurl)

    def update_url_bar(self, qurl=None):
        current_widget = self.tabs.currentWidget()
        if current_widget is None:
            self.url_bar.clear()
            return
        if qurl is None:
            qurl = current_widget.url()
        elif not isinstance(qurl, QUrl):
            qurl = QUrl(str(qurl))
        self.url_bar.setText(qurl.toString())
        self.url_bar.setCursorPosition(0)

        # Update placeholder only if the URL is empty (indicating home or new tab)
        if not qurl.toString():
            self.url_bar.setPlaceholderText("Search Surf or enter the URL")

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.setStyleSheet(self.get_stylesheet())
        self.theme_toggle_btn.setText("☀️" if self.theme == "light" else "🌙")

    def get_stylesheet(self):
        if self.theme == "dark":
            return """
                QMainWindow { background-color: #000000; }
                QLineEdit { color: #fff; background: #333; }
                QPushButton { color: #fff; background-color: #444; }
                QPushButton:hover { background-color: #555; }
            """
        return """
            QMainWindow { background-color: #ffffff; }
            QLineEdit { color: #000; background: #ccc; }
            QPushButton { color: #000; background-color: #ddd; }
            QPushButton:hover { background-color: #bbb; }
        """

    def clear_placeholder_on_focus(self, event):
        if self.url_bar.text() == "Search Surf or enter the URL":
            self.url_bar.clear()
        super().focusInEvent(event)

def load(custom_html):
    app = QApplication(sys.argv)
    window = Browser(custom_html)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    load(html_path)