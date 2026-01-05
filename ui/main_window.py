from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                             QTextEdit, QPushButton)
from PyQt6.QtCore import Qt
from ui.home_tab import HomeTab
from ui.install_tab import InstallTab
from ui.extract_tab import ExtractTab


class AndroidPentestTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Android APK Pentesting Tool")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        
        # Home Tab
        self.home_tab = HomeTab(self)
        self.tabs.addTab(self.home_tab, "🏠 Home")
        
        # Install Tab
        self.install_tab = InstallTab(self)
        self.tabs.addTab(self.install_tab, "🔧 Install Tools")
        
        # Extract APK Tab
        self.extract_tab = ExtractTab(self)
        self.tabs.addTab(self.extract_tab, "📱 Extract APK")
        
        # Console Tab
        console_tab = QWidget()
        console_layout = QVBoxLayout(console_tab)
        console_layout.addWidget(self.console)
        clear_btn = QPushButton("Clear Console")
        clear_btn.clicked.connect(self.console.clear)
        console_layout.addWidget(clear_btn)
        self.tabs.addTab(console_tab, "📋 Console")
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Clean dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-size: 13px;
            }
            
            QTabWidget::pane {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #808080;
                padding: 10px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #252526;
                color: #ffffff;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #3c3c3c;
            }
            
            QLineEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                padding: 8px 12px;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #1084d8;
            }
            
            QPushButton:pressed {
                background-color: #006cbd;
            }
            
            QPushButton:disabled {
                background-color: #3c3c3c;
                color: #808080;
            }
            
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 4px;
            }
            
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 2px;
            }
            
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            
            QListWidget::item:hover:!selected {
                background-color: #3c3c3c;
            }
            
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px;
            }
            
            QProgressBar {
                background-color: #2d2d2d;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
            
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 10px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #5a5a5a;
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #787878;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QGroupBox {
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            QCheckBox {
                spacing: 8px;
                padding: 5px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid #3c3c3c;
                background-color: #2d2d2d;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
            }
        """)
    
    def log(self, message, level="info"):
        """Add message to console"""
        colors = {"info": "#00ff00", "warning": "#ffaa00", "error": "#ff5555", "success": "#00ffff"}
        color = colors.get(level, "#00ff00")
        self.console.append(f'<span style="color: {color};">[{level.upper()}] {message}</span>')
    
    def switch_to_extract_tab(self):
        """Switch to extract APK tab"""
        self.tabs.setCurrentWidget(self.extract_tab)
    
    def switch_to_install_tab(self):
        """Switch to install tools tab"""
        self.tabs.setCurrentWidget(self.install_tab)