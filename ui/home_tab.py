from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QPushButton,
                             QLabel, QFileDialog, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from workers.apk_worker import APKWorker


class HomeTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.worker = None
        self.default_dir = Path.home() / "Android"
        self.default_dir.mkdir(exist_ok=True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🔒 Android APK Pentesting Tool")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Select an operation to get started")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #808080; margin-bottom: 15px;")
        layout.addWidget(subtitle)
        
        # Operation buttons grid
        grid = QGridLayout()
        grid.setSpacing(12)
        
        operations = [
            ("🔧 Install Tools", 0, 0, self.install_tools),
            ("📱 Extract APK", 0, 1, self.extract_apk),
            ("🔗 Merge Split APKs", 1, 0, self.merge_split_apks),
            ("📦 Decompile APK", 1, 1, self.decompile_apk),
            ("🔓 Remove SSL Pinning", 2, 0, self.remove_ssl_pinning),
            ("✍️ Resign APK", 2, 1, self.resign_apk),
            ("📲 AAB → APK", 3, 0, self.convert_aab_to_apk),
        ]
        
        for text, row, col, action in operations:
            btn = QPushButton(text)
            btn.clicked.connect(action)
            btn.setMinimumHeight(70)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0e639c;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 6px;
                }
                QPushButton:hover { background-color: #1177bb; }
                QPushButton:pressed { background-color: #0d5289; }
            """)
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        # Info
        info = QLabel(f"📁 Working directory: {self.default_dir}")
        info.setStyleSheet("background-color: #2d2d2d; padding: 10px; border-radius: 4px;")
        info.setWordWrap(True)
        layout.addWidget(info)
    
    def install_tools(self):
        """Switch to install tools tab"""
        self.parent.switch_to_install_tab()
    
    def extract_apk(self):
        self.parent.switch_to_extract_tab()
    
    def merge_split_apks(self):
        """Merge split APKs"""
        directory = QFileDialog.getExistingDirectory(self, "Select Split APK Directory", str(self.default_dir))
        if not directory:
            return
        
        apk_files = list(Path(directory).glob("*.apk"))
        if not apk_files:
            QMessageBox.warning(self, "No APKs", f"No APK files found in:\n{directory}")
            return
        
        self._run_operation("merge_split_apks", directory, directory, "Merging split APKs...")
    
    def decompile_apk(self):
        """Decompile APK"""
        apk_file, _ = QFileDialog.getOpenFileName(self, "Select APK", str(self.default_dir), "APK Files (*.apk)")
        if not apk_file:
            return
        
        output = str(Path(apk_file).parent / "decompiled")
        self._run_operation("decompile_apk", apk_file, output, "Decompiling APK...")
    
    def remove_ssl_pinning(self):
        """Remove SSL pinning"""
        apk_file, _ = QFileDialog.getOpenFileName(self, "Select APK", str(self.default_dir), "APK Files (*.apk)")
        if not apk_file:
            return
        
        output = str(Path(apk_file).parent / "patched_apk")
        self._run_operation("remove_ssl_pinning", apk_file, output, "Removing SSL pinning...")
    
    def resign_apk(self):
        """Resign APK"""
        apk_file, _ = QFileDialog.getOpenFileName(self, "Select APK", str(self.default_dir), "APK Files (*.apk)")
        if not apk_file:
            return
        
        output = str(Path(apk_file).parent / "signed_apk")
        self._run_operation("resign_apk", apk_file, output, "Signing APK...")
    
    def convert_aab_to_apk(self):
        """Convert AAB to APK"""
        aab_file, _ = QFileDialog.getOpenFileName(self, "Select AAB", str(self.default_dir), "AAB Files (*.aab)")
        if not aab_file:
            return
        
        output = str(Path(aab_file).parent)
        self._run_operation("convert_aab_to_apk", aab_file, output, "Converting AAB to APK...")
    
    def _run_operation(self, operation, input_path, output_path, status_msg):
        """Common method to run APK operations"""
        self.parent.log(f"Input: {input_path}")
        self.parent.log(f"Output: {output_path}")
        self.parent.statusBar().showMessage(status_msg)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.worker = APKWorker(operation, input_path, output_path)
        self.worker.finished.connect(self._on_complete)
        self.worker.error.connect(self._on_error)
        self.worker.progress.connect(self.parent.log)
        self.worker.command.connect(lambda cmd: self.parent.log(f"$ {cmd}"))
        self.worker.start()
    
    def _on_complete(self, result):
        """Handle operation completion"""
        self.progress_bar.setVisible(False)
        self.parent.statusBar().showMessage("Complete!")
        self.parent.log(f"✓ {result.get('operation', 'Operation')} completed!", "success")
        self.parent.log(f"Output: {result.get('output', 'N/A')}", "success")
        
        QMessageBox.information(self, "Success",
            f"Operation: {result.get('operation', '').replace('_', ' ').title()}\n"
            f"Output: {result.get('output', 'N/A')}")
    
    def _on_error(self, error_msg):
        """Handle errors"""
        self.progress_bar.setVisible(False)
        self.parent.statusBar().showMessage("Error")
        self.parent.log(error_msg, "error")
        QMessageBox.critical(self, "Error", error_msg)