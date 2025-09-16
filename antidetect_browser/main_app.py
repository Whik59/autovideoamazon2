#!/usr/bin/env python3
"""
Anti-Detect Browser Main Application
Profile manager that launches sandboxed Chrome instances.
"""

import sys
import shutil
import threading
from pathlib import Path

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QPushButton, QLabel, QListWidget, 
                           QMessageBox, QListWidgetItem)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

import undetected_chromedriver as uc

from browser_profile import BrowserProfile
from dialogs import ProfileDialog
from ui_styles import MAIN_STYLESHEET, ICON_PROXY, ICON_NO_PROXY, ICON_ADD, ICON_EDIT, ICON_DELETE
from proxy_util import create_proxy_extension


class AntiDetectBrowser(QMainWindow):
    """Main profile manager window"""
    
    def __init__(self):
        super().__init__()
        self.profiles = {}
        self.running_browsers = {}
        self.setup_ui()
        self.load_existing_profiles()
    
    def setup_ui(self):
        """Setup the main manager UI"""
        self.setWindowTitle("Anti-Detect Browser Pro")
        self.setGeometry(100, 100, 400, 600)
        self.setMinimumSize(350, 500)
        self.setStyleSheet(MAIN_STYLESHEET)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main content area (replacing splitter)
        content_widget = QWidget()
        content_widget.setObjectName("sidebar") # Use sidebar style for consistency
        main_layout.addWidget(content_widget)
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(10)
        
        # App header
        app_header = QLabel("Anti-Detect Browser")
        app_header.setObjectName("appHeader")
        app_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_header)
        
        # Profile management
        profile_label = QLabel("Browser Profiles")
        profile_label.setObjectName("sectionHeader")
        layout.addWidget(profile_label)
        
        self.profile_list = QListWidget()
        self.profile_list.setIconSize(QSize(20, 20))
        self.profile_list.itemDoubleClicked.connect(self.launch_selected_browser)
        layout.addWidget(self.profile_list)
        
        # Profile buttons
        buttons_layout = QHBoxLayout()
        self.new_profile_btn = QPushButton(" New")
        self.new_profile_btn.setObjectName("successButton")
        self.new_profile_btn.setIcon(QIcon(ICON_ADD))
        self.new_profile_btn.setIconSize(QSize(20, 20))
        
        self.edit_profile_btn = QPushButton(" Edit")
        self.edit_profile_btn.setObjectName("primaryButton")
        self.edit_profile_btn.setIcon(QIcon(ICON_EDIT))
        self.edit_profile_btn.setIconSize(QSize(20, 20))
        
        self.delete_profile_btn = QPushButton(" Delete")
        self.delete_profile_btn.setObjectName("dangerButton")
        self.delete_profile_btn.setIcon(QIcon(ICON_DELETE))
        self.delete_profile_btn.setIconSize(QSize(20, 20))

        buttons_layout.addWidget(self.new_profile_btn)
        buttons_layout.addWidget(self.edit_profile_btn)
        buttons_layout.addWidget(self.delete_profile_btn)
        layout.addLayout(buttons_layout)
        
        # Launch button
        self.launch_btn = QPushButton("🚀 Launch Browser")
        self.launch_btn.setObjectName("successButton")
        self.launch_btn.setStyleSheet("text-align: center; font-size: 16px; padding: 12px;")
        layout.addWidget(self.launch_btn)

        # Connect signals
        self.new_profile_btn.clicked.connect(self.show_new_profile_dialog)
        self.edit_profile_btn.clicked.connect(self.edit_selected_profile)
        self.delete_profile_btn.clicked.connect(self.delete_selected_profile)
        self.launch_btn.clicked.connect(self.launch_selected_browser)
    
    def launch_selected_browser(self):
        """Launch Chrome for the currently selected profile"""
        current_item = self.profile_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a profile to launch.")
            return
        
        profile_name = current_item.data(Qt.UserRole)
        
        if profile_name in self.running_browsers:
            QMessageBox.information(self, "Already Running", f"A browser for '{profile_name}' is already running.")
            return

        # Run in a separate thread to keep the UI responsive
        thread = threading.Thread(target=self.run_browser, args=(profile_name,))
        thread.daemon = True
        thread.start()

    def run_browser(self, profile_name):
        """The core browser launching logic"""
        profile = self.profiles[profile_name]
        options = uc.ChromeOptions()
        
        # Set user agent
        options.add_argument(f"--user-agent={profile.fingerprint['user_agent']}")
        
        # Set language and locale based on profile country
        print(f"Setting language for country: {profile.target_country}")
        if profile.target_country == "Germany":
            print("Adding German language arguments...")
            options.add_argument("--lang=de-DE")
            options.add_argument("--accept-lang=de-DE,de;q=0.9")
        elif profile.target_country == "France":
            print("Adding French language arguments...")
            options.add_argument("--lang=fr-FR")
            options.add_argument("--accept-lang=fr-FR,fr;q=0.9")
        elif profile.target_country == "Spain":
            print("Adding Spanish language arguments...")
            options.add_argument("--lang=es-ES")
            options.add_argument("--accept-lang=es-ES,es;q=0.9")
        elif profile.target_country == "Italy":
            print("Adding Italian language arguments...")
            options.add_argument("--lang=it-IT")
            options.add_argument("--accept-lang=it-IT,it;q=0.9")
        elif profile.target_country == "Netherlands":
            print("Adding Dutch language arguments...")
            options.add_argument("--lang=nl-NL")
            options.add_argument("--accept-lang=nl-NL,nl;q=0.9")
        elif profile.target_country == "Poland":
            print("Adding Polish language arguments...")
            options.add_argument("--lang=pl-PL")
            options.add_argument("--accept-lang=pl-PL,pl;q=0.9")
        elif profile.target_country == "Sweden":
            print("Adding Swedish language arguments...")
            options.add_argument("--lang=sv-SE")
            options.add_argument("--accept-lang=sv-SE,sv;q=0.9")
        else:  # Default to English
            print("Adding English language arguments...")
            options.add_argument("--lang=en-US")
            options.add_argument("--accept-lang=en-US,en;q=0.9")
        
        # Set isolated profile path
        options.add_argument(f"--user-data-dir={profile.chrome_data_dir.resolve()}")
        
        proxy_extension_path = None
        # Handle proxy settings
        if profile.proxy_config:
            proxy = profile.proxy_config
            if proxy.get('host') and proxy.get('port'):
                # Always use host:port format for --proxy-server (Chrome doesn't support embedded auth)
                proxy_server = f"{proxy['host']}:{proxy['port']}"
                print(f"Configuring Chrome proxy: {proxy_server}")
                options.add_argument(f"--proxy-server={proxy_server}")
                
                # For authenticated proxies, create extension for auth
                if proxy.get('username') and proxy.get('password'):
                    print(f"Creating auth extension for {proxy['host']}:{proxy['port']}")
                    proxy_extension_path = create_proxy_extension(
                        proxy['host'], proxy['port'], proxy['username'], proxy['password'], profile_name
                    )
                    print(f"Proxy extension created at: {proxy_extension_path}")
                    options.add_argument(f"--load-extension={proxy_extension_path}")
        
        # Add some additional Chrome arguments for better proxy handling
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--allow-running-insecure-content")
        
        # Maximum WebRTC leak protection
        options.add_argument("--disable-webrtc")
        options.add_argument("--disable-features=WebRTC")
        options.add_argument("--disable-features=RTCPeerConnection")
        options.add_argument("--disable-features=GetUserMedia")
        options.add_argument("--disable-webrtc-multiple-routes")
        options.add_argument("--disable-webrtc-hw-decoding")
        options.add_argument("--disable-webrtc-hw-encoding")
        options.add_argument("--force-webrtc-ip-handling-policy=disable_non_proxied_udp")
        options.add_argument("--disable-webrtc-apm-in-audio-service")
        options.add_argument("--disable-rtc-smoothness-algorithm")
        options.add_argument("--disable-webrtc-stun-origin")
        
        # Block WebRTC at network level
        options.add_argument("--host-rules=MAP *.stun.* 127.0.0.1")
        options.add_argument("--host-rules=MAP *.turn.* 127.0.0.1")
        options.add_argument("--host-rules=MAP stun.* 127.0.0.1")
        options.add_argument("--host-rules=MAP turn.* 127.0.0.1")
        
        # Additional network isolation
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-sync")
        
        # Enhanced anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions-except=" + (proxy_extension_path if proxy_extension_path else ""))
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu-sandbox")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        
        # Make browser appear more human
        options.add_argument("--enable-features=NetworkService,NetworkServiceLogging")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        # --- FIX: This option is no longer supported and causes crashes ---
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # --- FIX: This option is also no longer supported and causes crashes ---
        # options.add_experimental_option('useAutomationExtension', False)
        
        # Set Chrome preferences to disable WebRTC
        prefs = {
            "profile.default_content_setting_values.media_stream_camera": 2,
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1,
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False
        }
        options.add_experimental_option("prefs", prefs)

        try:
            # Force the driver to match the user's installed Chrome version
            print("Launching Chrome with options:")
            for arg in options.arguments:
                print(f"  {arg}")
            
            # Simplified Chrome launch to avoid conflicts
            driver = uc.Chrome(
                version_main=139, 
                options=options
            )
            self.running_browsers[profile_name] = driver
            
            # Give the extension time to load and configure the proxy
            if proxy_extension_path:
                print("Waiting for proxy extension to initialize...")
                import time
                time.sleep(3)
            
            # Inject fingerprint script for proper profile isolation
            print("Injecting fingerprint script...")
            injection_success = self.inject_fingerprint_script(driver, profile)
            
            if not injection_success:
                print("⚠️  WARNING: Fingerprint injection failed - browser may not have proper German locale!")
            
            # Give the browser a moment to fully initialize before testing
            import time
            time.sleep(1)
            
            # Test if fingerprint injection worked
            print("Testing fingerprint injection...")
            try:
                # Test language setting
                print("Checking navigator.language...")
                injected_language = driver.execute_script("return navigator.language;")
                print("Checking navigator.languages...")
                injected_languages = driver.execute_script("return navigator.languages;")
                print("Checking timezone...")
                injected_timezone = driver.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone;")
                
                print(f"Injected language: {injected_language}")
                print(f"Injected languages: {injected_languages}")
                print(f"Injected timezone: {injected_timezone}")
                print(f"Expected language: {profile.fingerprint.get('language', 'N/A')}")
                print(f"Expected timezone: {profile.fingerprint.get('timezone', 'N/A')}")
                
                # Verify if injection worked
                expected_lang = profile.fingerprint.get('language', '').split(',')[0]
                if injected_language != expected_lang:
                    print(f"WARNING: Language injection failed! Got {injected_language}, expected {expected_lang}")
                else:
                    print("✓ Language injection successful!")
                    
                if injected_timezone != profile.fingerprint.get('timezone'):
                    print(f"WARNING: Timezone injection failed! Got {injected_timezone}, expected {profile.fingerprint.get('timezone')}")
                else:
                    print("✓ Timezone injection successful!")
                    
            except Exception as e:
                print(f"Error testing fingerprint injection: {e}")
                import traceback
                traceback.print_exc()
            
            print("Navigating to Google to test localization...")
            driver.get("https://www.google.com")
            
            # Inject WebRTC blocking script directly
            print("Injecting WebRTC blocking script...")
            webrtc_block_script = """
            // Completely disable WebRTC to prevent IP leaks
            (function() {
                'use strict';
                
                console.log('Blocking WebRTC APIs to prevent IP leaks');
                
                // Override RTCPeerConnection
                if (window.RTCPeerConnection) {
                    window.RTCPeerConnection = function() {
                        throw new Error('RTCPeerConnection blocked');
                    };
                }
                if (window.webkitRTCPeerConnection) {
                    window.webkitRTCPeerConnection = function() {
                        throw new Error('webkitRTCPeerConnection blocked');
                    };
                }
                if (window.mozRTCPeerConnection) {
                    window.mozRTCPeerConnection = function() {
                        throw new Error('mozRTCPeerConnection blocked');
                    };
                }
                
                // Override getUserMedia
                if (navigator.getUserMedia) {
                    navigator.getUserMedia = function() {
                        throw new Error('getUserMedia blocked');
                    };
                }
                if (navigator.webkitGetUserMedia) {
                    navigator.webkitGetUserMedia = function() {
                        throw new Error('webkitGetUserMedia blocked');
                    };
                }
                if (navigator.mozGetUserMedia) {
                    navigator.mozGetUserMedia = function() {
                        throw new Error('mozGetUserMedia blocked');
                    };
                }
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    navigator.mediaDevices.getUserMedia = function() {
                        return Promise.reject(new Error('getUserMedia blocked'));
                    };
                }
                
                console.log('WebRTC APIs successfully blocked');
            })();
            """
            
            try:
                driver.execute_script(webrtc_block_script)
                print("WebRTC blocking script injected successfully")
            except Exception as e:
                print(f"Failed to inject WebRTC blocking script: {e}")
            
            # Refresh the page to ensure the script takes effect
            print("Refreshing page to apply WebRTC blocking...")
            driver.refresh()
            
            # This loop will block until the browser window is closed by the user
            while True:
                try:
                    # Check if the window is still open
                    _ = driver.window_handles
                    import time
                    time.sleep(1)  # Prevent busy waiting
                except Exception:
                    # Browser has been closed
                    break
        finally:
            # Clean up after browser is closed
            try:
                if profile_name in self.running_browsers:
                    driver = self.running_browsers[profile_name]
                    driver.quit()  # Ensure proper cleanup
                    del self.running_browsers[profile_name]
                    print(f"Browser for profile '{profile_name}' cleaned up successfully")
            except Exception as e:
                print(f"Error during browser cleanup: {e}")
                # Still remove from tracking even if cleanup failed
            if profile_name in self.running_browsers:
                del self.running_browsers[profile_name]

    def show_new_profile_dialog(self):
        profile_data = ProfileDialog.get_profile_data_from_dialog(self)
        if profile_data:
            self.create_new_profile(profile_data)
    
    def create_new_profile(self, profile_data):
        profile_name = profile_data['name']
        if profile_name in self.profiles:
            QMessageBox.warning(self, "Error", f"Profile '{profile_name}' already exists!")
            return
        
        profile = BrowserProfile(
            profile_name, 
            profile_data.get('proxy_config'), 
            profile_data.get('target_country', 'USA')
        )
        profile.save_profile()
        self.profiles[profile_name] = profile
        self.refresh_profile_list()
        QMessageBox.information(self, "Success", f"Profile '{profile_name}' created for {profile_data.get('target_country', 'USA')} audience.")
    
    def edit_selected_profile(self):
        current_item = self.profile_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a profile to edit.")
            return
        
        old_profile_name = current_item.data(Qt.UserRole)
        profile = self.profiles[old_profile_name]
        
        profile_data = ProfileDialog.get_profile_data_from_dialog(self, profile)
        if profile_data:
            new_profile_name = profile_data.get('name', old_profile_name)
            
            # --- FIXED: Handle profile name changes ---
            if new_profile_name != old_profile_name:
                # Remove old profile from dictionary
                del self.profiles[old_profile_name]
                
                # Rename profile directory if name changed
                old_profile_dir = Path("profiles") / old_profile_name
                new_profile_dir = Path("profiles") / new_profile_name
                
                if old_profile_dir.exists() and not new_profile_dir.exists():
                    old_profile_dir.rename(new_profile_dir)
                
                # Update profile name
                profile.profile_name = new_profile_name
                profile.profile_dir = new_profile_dir
                profile.chrome_data_dir = new_profile_dir / "chrome_data"
                
                # Add profile back with new name
                self.profiles[new_profile_name] = profile
            
            # --- FIXED: Update all profile data including country ---
            old_country = profile.target_country
            profile.proxy_config = profile_data.get('proxy_config')
            profile.target_country = profile_data.get('target_country', 'USA')
            
            # Regenerate fingerprint if country changed to match new locale
            if old_country != profile.target_country:
                profile.fingerprint = profile.generate_fingerprint()
            
            profile.save_profile()
            self.refresh_profile_list()
            
            QMessageBox.information(self, "Success", f"Profile '{new_profile_name}' updated successfully!")
    
    def delete_selected_profile(self):
        current_item = self.profile_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a profile to delete.")
            return
        
        profile_name = current_item.data(Qt.UserRole)
        
        # Check if browser is currently running for this profile
        if profile_name in self.running_browsers:
            reply = QMessageBox.question(self, "Browser Running", 
                f"Profile '{profile_name}' has a browser currently running.\n\n"
                f"Do you want to:\n"
                f"• Keep the browser open and just delete the profile data\n"
                f"• Cancel deletion\n\n"
                f"Note: The browser will continue running but won't be tracked by this app.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.No:
                return
            else:
                # Remove from tracking but don't close the browser
                print(f"Removing profile '{profile_name}' from tracking but keeping browser open")
                del self.running_browsers[profile_name]
        
        reply = QMessageBox.question(self, "Confirm Delete", 
            f"Are you sure you want to permanently delete profile '{profile_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Remove from memory first
                if profile_name in self.profiles:
                    del self.profiles[profile_name]
                
                # Get the directory where this script is located
                script_dir = Path(__file__).parent
                profile_dir = script_dir / "profiles" / profile_name
                
                if profile_dir.exists():
                    # Simple deletion attempt - user will close Chrome manually
                    try:
                        shutil.rmtree(profile_dir)
                    except PermissionError:
                        # Show user-friendly message without any automatic cleanup attempts
                        QMessageBox.warning(self, "Profile In Use", 
                            f"Cannot delete profile '{profile_name}' - files are in use.\n\n"
                            f"Please:\n"
                            f"1. Close the Chrome window for this profile\n"
                            f"2. Wait a few seconds for Chrome to fully close\n"
                            f"3. Try deleting the profile again\n\n"
                            f"Chrome will handle cleanup automatically when closed.")
                        return
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to delete profile directory: {str(e)}")
                        return
                
                self.refresh_profile_list()
                QMessageBox.information(self, "Success", f"Profile '{profile_name}' deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete profile: {str(e)}")
                # Try to restore the profile in memory if directory deletion failed
                try:
                    profile = BrowserProfile.load_profile(profile_name)
                    if profile:
                        self.profiles[profile_name] = profile
                        self.refresh_profile_list()
                except Exception:
                    pass

    def load_existing_profiles(self):
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        profiles_dir = script_dir / "profiles"
        
        if profiles_dir.exists():
            for profile_dir in profiles_dir.iterdir():
                if profile_dir.is_dir():
                    profile = BrowserProfile.load_profile(profile_dir.name)
                    if profile:
                        self.profiles[profile.profile_name] = profile
        self.refresh_profile_list()
    
    def refresh_profile_list(self):
        self.profile_list.clear()
        for profile_name in sorted(self.profiles.keys()):
            profile = self.profiles[profile_name]
            # Show profile name with country flag emoji
            country_flags = {
                "USA": "🇺🇸", "Germany": "🇩🇪", "France": "🇫🇷", "Spain": "🇪🇸", 
                "Italy": "🇮🇹", "Netherlands": "🇳🇱", "Poland": "🇵🇱", "Sweden": "🇸🇪"
            }
            flag = country_flags.get(profile.target_country, "🌍")
            display_name = f"{flag} {profile_name} ({profile.target_country})"
            
            item = QListWidgetItem(display_name)
            icon = QIcon(ICON_PROXY if profile.proxy_config else ICON_NO_PROXY)
            item.setIcon(icon)
            item.setData(Qt.UserRole, profile_name)
            self.profile_list.addItem(item)
    
    def inject_fingerprint_script(self, driver, profile):
        """Inject comprehensive fingerprinting script into the browser"""
        import json
        
        # Read the fingerprint injection template
        script_path = Path(__file__).parent / "fingerprint_injector.js"
        if not script_path.exists():
            print("Warning: Fingerprint injector script not found")
            return
            
        with open(script_path, 'r') as f:
            script_template = f.read()
        
        # Replace the placeholder with actual fingerprint data
        fingerprint_json = json.dumps(profile.fingerprint, indent=2)
        script = script_template.replace('{fingerprint_data}', fingerprint_json)
        
        # Execute the script using multiple methods for better compatibility
        injection_success = False
        
        # Method 1: Try CDP command first
        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': script
            })
            print("✓ Fingerprint script injected via CDP")
            injection_success = True
        except Exception as e:
            print(f"CDP injection failed: {e}")
        
        # Method 2: Try direct script execution as immediate fallback
        try:
            driver.execute_script(script)
            print("✓ Fingerprint script executed directly")
            injection_success = True
        except Exception as e:
            print(f"Direct script execution failed: {e}")
        
        # Method 3: Try injecting with a simple test first
        if not injection_success:
            try:
                # Test if we can execute any script at all
                test_result = driver.execute_script("return 'test successful';")
                if test_result == 'test successful':
                    print("✓ Basic script execution works, trying fingerprint injection again...")
                    driver.execute_script(script)
                    injection_success = True
                    print("✓ Fingerprint script injected on retry")
            except Exception as e:
                print(f"Final fingerprint injection attempt failed: {e}")
        
        if not injection_success:
            print("❌ All fingerprint injection methods failed!")
        
        return injection_success
    
    def closeEvent(self, event):
        """Ensure all running browsers are closed when the app exits"""
        if self.running_browsers:
            reply = QMessageBox.question(self, "Confirm Exit",
                "Closing this window will also close all running browser sessions. Are you sure?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                for driver in self.running_browsers.values():
                    try:
                        driver.quit()
                    except Exception as e:
                        print(f"Error closing a browser: {e}")
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Anti-Detect Browser Pro")
    parser.add_argument('--profile', type=str, help='Automatically launch a specific profile')
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Anti-Detect Browser Pro")
    app.setOrganizationName("AntiDetect Solutions")
    
    browser = AntiDetectBrowser()
    
    # Always load existing profiles first
    browser.load_existing_profiles()
    
    # If a profile is specified, try to launch it automatically
    if args.profile:
        print(f"Auto-launching profile: {args.profile}")
        
        # Check if the profile exists
        if args.profile in browser.profiles:
            print(f"Found profile '{args.profile}', launching browser...")
            # Launch the browser in a separate thread to avoid blocking the UI
            import threading
            thread = threading.Thread(target=browser.run_browser, args=(args.profile,))
            thread.daemon = True
            thread.start()
            print(f"Profile '{args.profile}' launched successfully!")
        else:
            print(f"ERROR: Profile '{args.profile}' not found!")
            print(f"Available profiles: {list(browser.profiles.keys())}")
            print("Opening main interface to create the profile...")
    
    browser.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 