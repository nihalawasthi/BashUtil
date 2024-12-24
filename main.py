#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTabWidget, QWidget
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
        window_color = "#212121"
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setStyleSheet("""
    QTabWidget::pane {
        background: #1c1c1c; /* Match the window background */
        border: none;
    }

    QTabBar {
        background: #000; /* Tab bar background */
        border: none;
        padding: 0px;
    }

    QTabBar::tab {
        background: #000; /* Blend with tab bar */
        color: gray;
        border: none;
        padding: 10px;
        margin: 4px 0; /* Keep them aligned */
        border-radius: 16px;
    }

    QTabBar::tab:selected {
        background: #1c1c1c; /* Match window */
        color: white;
        margin-left: -10px; /* Extend outward from the tab bar */
        margin-right: -10px;
        border-top-left-radius: 24px; /* Smooth curve for the bump effect */
        border-top-right-radius: 24px;
        border-bottom-left-radius: 0px; /* No curve for bottom edge */
        border-bottom-right-radius: 0px;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.6); /* Subtle shadow for depth */
    }

    QTabBar::tab:hover {
        background: #333; /* Subtle hover effect */
        color: white;
    }
""")
        main_layout.addWidget(self.tabs)
        self.add_new_tab(label="Home")

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
    app.setWindowIcon(QIcon("src/xyz.png"))
    window = Browser(custom_html)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    html_path = os.path.join(os.path.dirname(__file__), "src/index.html")
    load(html_path)