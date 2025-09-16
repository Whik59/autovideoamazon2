#!/usr/bin/env python3
"""
Dialog Components Module
Contains all dialog windows for the anti-detect browser
"""

import re
import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLineEdit, QLabel, QFormLayout, QCheckBox, QSpinBox,
                           QMessageBox, QListWidget, QTextEdit, QApplication, QDialog, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui_styles import DIALOG_STYLE


class ProfileSelectionDialog(QDialog):
    """Dialog for selecting a profile for new tabs"""
    # ... (This dialog can be improved later if needed, focusing on the main one first)
    def __init__(self, parent=None, profile_names=None):
        super().__init__(parent)
        self.profile_names = profile_names or []
        self.selected_profile = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Select Browser Profile")
        self.setFixedSize(400, 300)
        self.setWindowModality(Qt.ApplicationModal)
        layout = QVBoxLayout(self)
        title = QLabel("Choose a profile for the new browser tab:")
        title.setFont(QFont("Arial", 11))
        layout.addWidget(title)
        self.profile_list = QListWidget()
        self.profile_list.addItems(self.profile_names)
        if self.profile_names:
            self.profile_list.setCurrentRow(0)
        self.profile_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.profile_list)
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Open Tab")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.setDefault(True)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)
    
    def get_selected_profile(self):
        return self.selected_profile
    
    def accept(self):
        current_item = self.profile_list.currentItem()
        if current_item:
            self.selected_profile = current_item.text()
        super().accept()
    
    def reject(self):
        super().reject()
    
    @staticmethod
    def get_profile(parent, profile_names):
        dialog = ProfileSelectionDialog(parent, profile_names)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_selected_profile()
        return None


class ProfileDialog(QDialog):
    """Dialog for creating/editing browser profiles"""
    
    def __init__(self, parent=None, profile=None):
        super().__init__(parent)
        self.profile = profile
        self.setup_ui()
        
        if profile:
            self.load_profile_data()
    
    def setup_ui(self):
        """Setup the profile dialog UI"""
        self.setWindowTitle("Browser Profile Configuration")
        self.setObjectName("dialogWidget")
        self.setStyleSheet(DIALOG_STYLE)
        
        self.setMinimumSize(700, 650)
        self.setWindowModality(Qt.ApplicationModal)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header ---
        header_widget = QWidget()
        header_widget.setObjectName("headerWidget")
        header_layout = QVBoxLayout(header_widget)
        header_label = QLabel("Create / Edit Browser Profile")
        header_label.setObjectName("headerLabel")
        header_subtitle = QLabel("Configure your isolated browsing environment and proxy settings.")
        header_subtitle.setObjectName("headerSubtitle")
        header_layout.addWidget(header_label)
        header_layout.addWidget(header_subtitle)
        main_layout.addWidget(header_widget)
        
        # --- Content ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 10, 20, 20)
        
        # Profile name
        profile_section = QLabel("Profile Information")
        profile_section.setObjectName("dialogSectionHeader")
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Business_Profile_1")
        form_layout.addRow("Profile Name:", self.name_input)
        
        # Country selector for YouTube targeting
        self.country_combo = QComboBox()
        self.country_combo.addItems([
            "USA", "Germany", "France", "Spain", "Italy", 
            "Netherlands", "Poland", "Sweden"
        ])
        self.country_combo.setToolTip("Select the country to match your YouTube channel's target audience")
        form_layout.addRow("Target Country:", self.country_combo)
        
        content_layout.addWidget(profile_section)
        content_layout.addLayout(form_layout)
        
        # Proxy config
        proxy_section = QLabel("Proxy Configuration")
        proxy_section.setObjectName("dialogSectionHeader")
        content_layout.addWidget(proxy_section)

        # Proxy import
        import_layout = QHBoxLayout()
        self.proxy_import_input = QLineEdit()
        self.proxy_import_input.setPlaceholderText("Import from host:port:user:pass")
        self.import_proxy_button = QPushButton("Import")
        self.import_proxy_button.setObjectName("importButton")
        self.import_proxy_button.clicked.connect(self.import_proxy_from_string)
        import_layout.addWidget(self.proxy_import_input, 1)
        import_layout.addWidget(self.import_proxy_button)
        content_layout.addLayout(import_layout)
        
        self.proxy_enabled = QCheckBox("Enable Proxy for this profile")
        self.proxy_enabled.toggled.connect(self.toggle_proxy_fields)
        content_layout.addWidget(self.proxy_enabled)
        
        proxy_form_layout = QFormLayout()
        proxy_form_layout.setSpacing(10)
        self.proxy_host_input = QLineEdit()
        self.proxy_port_input = QSpinBox()
        self.proxy_port_input.setRange(1, 65535)
        self.proxy_username_input = QLineEdit()
        self.proxy_password_input = QLineEdit()
        self.proxy_password_input.setEchoMode(QLineEdit.Password)
        proxy_form_layout.addRow("Host:", self.proxy_host_input)
        proxy_form_layout.addRow("Port:", self.proxy_port_input)
        proxy_form_layout.addRow("Username:", self.proxy_username_input)
        proxy_form_layout.addRow("Password:", self.proxy_password_input)
        content_layout.addLayout(proxy_form_layout)
        
        # Test results
        test_section = QLabel("Connection Test")
        test_section.setObjectName("dialogSectionHeader")
        self.status_text = QTextEdit()
        self.status_text.setPlaceholderText("Proxy test results will appear here...")
        self.status_text.setMaximumHeight(80)
        content_layout.addWidget(test_section)
        content_layout.addWidget(self.status_text)
        
        main_layout.addWidget(content_widget)
        main_layout.addStretch()

        # --- Buttons ---
        button_widget = QWidget()
        button_widget.setObjectName("dialogButtons")
        button_layout = QHBoxLayout(button_widget)
        self.test_proxy_button = QPushButton("Test Proxy")
        self.test_proxy_button.setObjectName("testButton")
        self.test_proxy_button.clicked.connect(self.test_proxy)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = QPushButton("Save Profile")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.accept)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.test_proxy_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        main_layout.addWidget(button_widget)
        
        # Initial state
        self.toggle_proxy_fields(False)
    
    def toggle_proxy_fields(self, enabled):
        """Enable/disable proxy input fields"""
        self.proxy_host_input.setEnabled(enabled)
        self.proxy_port_input.setEnabled(enabled)
        self.proxy_username_input.setEnabled(enabled)
        self.proxy_password_input.setEnabled(enabled)
        self.test_proxy_button.setEnabled(enabled)
    
    def import_proxy_from_string(self):
        # (Same logic as before)
        proxy_string = self.proxy_import_input.text().strip()
        if not proxy_string: return
        parts = proxy_string.split(':')
        if len(parts) != 4:
            QMessageBox.warning(self, "Format Error", "Invalid proxy format. Please use host:port:username:password.")
            return
        host, port_str, username, password = parts
        try:
            port = int(port_str)
            if not (1 <= port <= 65535): raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Format Error", "Invalid port number.")
            return
        self.proxy_host_input.setText(host)
        self.proxy_port_input.setValue(port)
        self.proxy_username_input.setText(username)
        self.proxy_password_input.setText(password)
        self.proxy_enabled.setChecked(True)
        self.proxy_import_input.clear()
        self.status_text.setText("Proxy details imported successfully!")

    def load_profile_data(self):
        """Load existing profile data into form"""
        self.name_input.setText(self.profile.profile_name)
        # --- FIXED: Allow profile name editing ---
        # self.name_input.setEnabled(False)
        
        # --- FIXED: Load target country when editing ---
        if hasattr(self.profile, 'target_country') and self.profile.target_country:
            # Find and set the country in the combo box
            country_index = self.country_combo.findText(self.profile.target_country)
            if country_index >= 0:
                self.country_combo.setCurrentIndex(country_index)
        
        if self.profile.proxy_config:
            self.proxy_enabled.setChecked(True)
            self.proxy_host_input.setText(self.profile.proxy_config.get('host', ''))
            self.proxy_port_input.setValue(self.profile.proxy_config.get('port', 5959))
            self.proxy_username_input.setText(self.profile.proxy_config.get('username', ''))
            self.proxy_password_input.setText(self.profile.proxy_config.get('password', ''))
    
    def test_proxy(self):
        """Test proxy connection"""
        proxy_config = self.get_proxy_config()
        if not proxy_config or not proxy_config['host']:
            self.status_text.setHtml("<font color='red'>Please enter a proxy host.</font>")
            return
        
        self.status_text.setText("Testing proxy connection...")
        QApplication.processEvents()
        
        # List of reliable URLs to test against
        test_urls = ['http://httpbin.org/ip', 'https://api.ipify.org?format=json']
        success = False
        
        for url in test_urls:
            try:
                proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['host']}:{proxy_config['port']}"
                proxies = {'http': proxy_url, 'https': proxy_url}
                response = requests.get(url, proxies=proxies, timeout=15)
                
                if response.status_code == 200:
                    ip = response.json().get('origin') or response.json().get('ip')
                    self.status_text.setHtml(f"<font color='green'>✅ Proxy working! Your IP: {ip}</font>")
                    success = True
                    break # Stop on first success
                elif response.status_code == 503:
                    self.status_text.setHtml(f"<font color='orange'>⚠️ Proxy test failed (503 Service Unavailable). This is a temporary server-side issue. Trying fallback...</font>")
                    continue # Try next URL
                else:
                    self.status_text.setHtml(f"<font color='red'>❌ Test failed with status: {response.status_code} on {url}</font>")
            
            except Exception as e:
                self.status_text.setHtml(f"<font color='red'>❌ Proxy test failed: {e}</font>")

        if not success:
             self.status_text.append("<br><font color='red'>❌ All proxy tests failed. Please check credentials and proxy status.</font>")

    def get_proxy_config(self):
        """Get proxy configuration from form"""
        if not self.proxy_enabled.isChecked():
            return None
        return {
            'host': self.proxy_host_input.text().strip(),
            'port': self.proxy_port_input.value(),
            'username': self.proxy_username_input.text().strip(),
            'password': self.proxy_password_input.text().strip()
        }
    
    def get_profile_data(self):
        """Get all profile data from form"""
        return {
            'name': self.name_input.text().strip(),
            'target_country': self.country_combo.currentText(),
            'proxy_config': self.get_proxy_config()
        }
    
    def accept(self):
        """Validate input and accept dialog"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Please enter a profile name.")
            return
        
        super().accept()
    
    def reject(self):
        super().reject()
    
    @staticmethod
    def get_profile_data_from_dialog(parent, profile=None):
        dialog = ProfileDialog(parent, profile)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_profile_data()
        return None 