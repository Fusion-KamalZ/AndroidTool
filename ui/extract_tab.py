from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QListWidget, QLabel, QMessageBox,
                             QProgressBar, QFileDialog)
from workers.adb_worker import ADBWorker


class ExtractTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.worker = None
        self.default_dir = Path.home() / "Android"
        self.default_dir.mkdir(exist_ok=True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter package name (e.g., com.example)")
        self.search_input.returnPressed.connect(self.search_packages)
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.clicked.connect(self.search_packages)
        search_layout.addWidget(QLabel("Package:"))
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)
        
        # Command display
        self.cmd_display = QLineEdit()
        self.cmd_display.setReadOnly(True)
        self.cmd_display.setPlaceholderText("No command running...")
        self.cmd_display.setStyleSheet("""
            background-color: #1e1e1e; color: #00ff00;
            font-family: 'Consolas', monospace; padding: 8px;
        """)
        layout.addWidget(self.cmd_display)
        
        # Package list
        layout.addWidget(QLabel("Packages Found:"))
        self.package_list = QListWidget()
        self.package_list.itemClicked.connect(self._on_package_click)
        self.package_list.itemDoubleClicked.connect(self.extract_apk)
        layout.addWidget(self.package_list)
        
        # Selected package
        selected_layout = QHBoxLayout()
        selected_layout.addWidget(QLabel("Selected:"))
        self.selected_label = QLabel("None")
        self.selected_label.setStyleSheet("color: #0078d4; font-weight: bold;")
        selected_layout.addWidget(self.selected_label, 1)
        layout.addLayout(selected_layout)
        
        # Output directory
        output_layout = QHBoxLayout()
        self.output_input = QLineEdit(str(self.default_dir))
        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(QLabel("Output:"))
        output_layout.addWidget(self.output_input, 1)
        output_layout.addWidget(browse_btn)
        layout.addLayout(output_layout)
        
        # Extract button
        self.extract_btn = QPushButton("📦 Extract Selected APK")
        self.extract_btn.clicked.connect(self.extract_apk)
        self.extract_btn.setEnabled(False)
        self.extract_btn.setMinimumHeight(40)
        layout.addWidget(self.extract_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Tip
        tip = QLabel(f"💡 APKs saved to: {self.default_dir}/[package_name]/")
        tip.setStyleSheet("background-color: #2d2d2d; padding: 8px; border-radius: 4px; color: #cccccc;")
        tip.setWordWrap(True)
        layout.addWidget(tip)
    
    def _browse_output(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output", self.output_input.text())
        if directory:
            self.output_input.setText(directory)
    
    def _on_package_click(self, item):
        self.selected_label.setText(item.text())
        self.extract_btn.setEnabled(True)
    
    def search_packages(self):
        """Search for packages on device"""
        self.package_list.clear()
        self.selected_label.setText("None")
        self.extract_btn.setEnabled(False)
        self._set_loading(True)
        
        self.worker = ADBWorker("list_packages", self.search_input.text().strip())
        self.worker.finished.connect(self._on_search_done)
        self.worker.error.connect(self._on_error)
        self.worker.command.connect(self.cmd_display.setText)
        self.worker.start()
    
    def _on_search_done(self, packages):
        self._set_loading(False)
        if not packages:
            QMessageBox.information(self, "No Results", "No packages found matching your search.")
            return
        self.package_list.addItems(packages)
        self.parent.log(f"Found {len(packages)} packages", "success")
    
    def extract_apk(self):
        """Extract APK for selected package"""
        item = self.package_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Select a package first.")
            return
        
        output_dir = self.output_input.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "No Output", "Specify an output directory.")
            return
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self._set_loading(True)
        
        self.worker = ADBWorker("extract_apk", item.text(), output_dir)
        self.worker.finished.connect(self._on_extract_done)
        self.worker.error.connect(self._on_error)
        self.worker.command.connect(self.cmd_display.setText)
        self.worker.start()
    
    def _on_extract_done(self, result):
        self._set_loading(False)
        self.parent.log(f"✓ Extracted {result['count']} files", "success")
        QMessageBox.information(self, "Success",
            f"Package: {result['package']}\n"
            f"Files: {result['count']}\n"
            f"Location: {result['directory']}")
    
    def _on_error(self, msg):
        self._set_loading(False)
        self.parent.log(msg, "error")
        QMessageBox.critical(self, "Error", msg)
    
    def _set_loading(self, loading):
        self.progress_bar.setVisible(loading)
        self.progress_bar.setRange(0, 0 if loading else 100)
        self.search_btn.setEnabled(not loading)
        self.extract_btn.setEnabled(not loading and self.package_list.currentItem() is not None)