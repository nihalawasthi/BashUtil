#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTabWidget, QWidget, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from Navbar import CustomNavBar
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
        background: black;
        padding-left: 8px;
        border-left: 4px solid #3c3b3b;
    }

    QTabBar::tab {
        background: black;
        color: gray;
        margin: 4px;
        margin-left: 8px;
        padding: 20px 8px;
        max-height: 150px;
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
        margin-left: 0px;
        border-right: 4px solid #6BEC75;
    }
""")

    def update_close_buttons(self):
        """Update close buttons to only show on the active tab."""
        for i in range(self.tabs.count()):
            close_button = self.tabs.tabBar().tabButton(i, self.tabs.tabBar().RightSide)
            if close_button:
                close_button.setVisible(i == self.tabs.currentIndex())
                
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