#!/usr/bin/env python3
"""
UI Styles Module
Contains all styling definitions for the anti-detect browser interface
"""

# --- Color Palette ---
COLOR_DARK_PRIMARY = "#1e2124"
COLOR_DARK_SECONDARY = "#282b30"
COLOR_DARK_TERTIARY = "#36393f"
COLOR_LIGHT_PRIMARY = "#ffffff"
COLOR_LIGHT_SECONDARY = "#f8f9fa"
COLOR_LIGHT_TERTIARY = "#e9ecef"
COLOR_ACCENT_PRIMARY = "#5865f2"  # A modern purple/blue
COLOR_ACCENT_HOVER = "#4f5bda"
COLOR_ACCENT_DANGER = "#ed4245"
COLOR_ACCENT_SUCCESS = "#3ba55d"
COLOR_ACCENT_WARNING = "#faa61a"
COLOR_TEXT_PRIMARY = "#dcddde"  # Light text for dark backgrounds
COLOR_TEXT_SECONDARY = "#b9bbbe"
COLOR_TEXT_HEADER = "#ffffff"
COLOR_TEXT_DARK = "#2e3338"     # Dark text for light backgrounds

# --- SVG Icons (encoded for CSS) ---
# Using https://yoksel.github.io/url-encoder/
ICON_ADD = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23dcddde' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='12' y1='5' x2='12' y2='19'%3E%3C/line%3E%3Cline x1='5' y1='12' x2='19' y2='12'%3E%3C/line%3E%3C/svg%3E"
ICON_EDIT = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23dcddde' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7'%3E%3C/path%3E%3Cpath d='M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z'%3E%3C/path%3E%3C/svg%3E"
ICON_DELETE = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23dcddde' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='3 6 5 6 21 6'%3E%3C/polyline%3E%3Cpath d='M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2'%3E%3C/path%3E%3Cline x1='10' y1='11' x2='10' y2='17'%3E%3C/line%3E%3Cline x1='14' y1='11' x2='14' y2='17'%3E%3C/line%3E%3C/svg%3E"
ICON_PROXY = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%233ba55d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 17a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2'%3E%3C/path%3E%3Cpath d='M12 15V7'%3E%3C/path%3E%3Cpath d='M12 5a2 2 0 1 0 0-4 2 2 0 0 0 0 4z'%3E%3C/path%3E%3Cpath d='M5 15a2 2 0 1 0 0-4 2 2 0 0 0 0 4z'%3E%3C/path%3E%3Cpath d='M19 15a2 2 0 1 0 0-4 2 2 0 0 0 0 4z'%3E%3C/path%3E%3C/svg%3E"
ICON_NO_PROXY = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23b9bbbe' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M1 1l22 22'%3E%3C/path%3E%3Cpath d='M20 17a2 2 0 0 0-2-2H7.83a2 2 0 0 0-1.42.59'%3E%3C/path%3E%3Cpath d='M12 15V7'%3E%3C/path%3E%3Cpath d='M12 5a2 2 0 1 0 0-4 2 2 0 0 0 0 4z'%3E%3C/path%3E%3Cpath d='M5 15a2 2 0 1 0 0-4 2 2 0 0 0 0 4z'%3E%3C/path%3E%3Cpath d='M19 15a2 2 0 0 0 .59-3.41'%3E%3C/path%3E%3C/svg%3E"


# --- Main Application Stylesheet ---
MAIN_STYLESHEET = f"""
/* --- General --- */
QMainWindow, QWidget {{
    background-color: {COLOR_LIGHT_PRIMARY};
    color: {COLOR_TEXT_DARK};
    font-family: 'Segoe UI', 'Arial', sans-serif;
}}

/* --- Sidebar --- */
QWidget#sidebar {{
    background-color: {COLOR_DARK_SECONDARY};
    border-right: 1px solid {COLOR_DARK_TERTIARY};
}}

/* --- Headers --- */
QLabel#appHeader {{
    color: {COLOR_TEXT_HEADER};
    font-size: 16px;
    font-weight: 600;
    padding: 5px;
}}
QLabel#sectionHeader {{
    color: {COLOR_TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 600;
    padding: 5px 8px;
    margin: 8px 0 4px 0;
    text-transform: uppercase;
}}

/* --- Profile List --- */
QListWidget {{
    background-color: {COLOR_LIGHT_PRIMARY};
    border: 2px solid {COLOR_LIGHT_TERTIARY};
    border-radius: 8px;
    padding: 8px;
    font-size: 15px;
    font-weight: 600;
}}
QListWidget::item {{
    color: {COLOR_TEXT_DARK};
    background-color: {COLOR_LIGHT_SECONDARY};
    padding: 14px 16px;
    margin: 4px 0;
    border-radius: 6px;
    border: 1px solid {COLOR_LIGHT_TERTIARY};
    font-size: 15px;
    font-weight: 600;
    min-height: 24px;
}}
QListWidget::item:selected {{
    background-color: {COLOR_ACCENT_PRIMARY};
    color: {COLOR_TEXT_HEADER};
    font-weight: 700;
    border: 2px solid {COLOR_ACCENT_HOVER};
    font-size: 16px;
}}
QListWidget::item:hover:!selected {{
    background-color: {COLOR_LIGHT_TERTIARY};
    border: 1px solid {COLOR_ACCENT_PRIMARY};
    color: {COLOR_TEXT_DARK};
    font-weight: 700;
}}

/* --- Buttons --- */
QPushButton {{
    color: {COLOR_TEXT_HEADER};
    border: none;
    padding: 10px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 14px;
    text-align: left;
    padding-left: 15px;
}}
QPushButton:hover {{
    background-color: {COLOR_DARK_TERTIARY};
}}
QPushButton:pressed {{
    background-color: {COLOR_DARK_PRIMARY};
}}

QPushButton#successButton {{
    background-color: {COLOR_ACCENT_SUCCESS};
}}
QPushButton#successButton:hover {{
    background-color: #339154;
}}

QPushButton#primaryButton {{
    background-color: {COLOR_DARK_TERTIARY};
}}
QPushButton#primaryButton:hover {{
    background-color: {COLOR_ACCENT_PRIMARY};
}}

QPushButton#dangerButton {{
    background-color: {COLOR_ACCENT_DANGER};
}}
QPushButton#dangerButton:hover {{
    background-color: #d83c3e;
}}

/* --- Tab Widget --- */
QTabWidget::pane {{
    border: none;
    background-color: {COLOR_LIGHT_PRIMARY};
}}
QTabBar::tab {{
    background-color: {COLOR_LIGHT_TERTIARY};
    color: {COLOR_TEXT_DARK};
    border: 1px solid {COLOR_LIGHT_TERTIARY};
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
}}
QTabBar::tab:selected {{
    background: {COLOR_LIGHT_PRIMARY};
    border-color: {COLOR_LIGHT_TERTIARY};
}}
QTabBar::tab:hover:!selected {{
    background: #e1e3e5;
}}
QTabBar::close-button {{
    image: url(data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%2336393f' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='18' y1='6' x2='6' y2='18'%3E%3C/line%3E%3Cline x1='6' y1='6' x2='18' y2='18'%3E%3C/line%3E%3C/svg%3E);
    subcontrol-position: right;
    padding: 2px;
}}

/* --- Scrollbars --- */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {COLOR_DARK_TERTIARY};
    min-height: 20px;
    border-radius: 5px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
"""

# --- Dialog Styles ---
DIALOG_STYLE = f"""
/* --- Dialog Base --- */
QWidget#dialogWidget {{
    background-color: {COLOR_LIGHT_PRIMARY};
}}

/* --- Header --- */
QWidget#headerWidget {{
    background-color: {COLOR_LIGHT_SECONDARY};
    border-bottom: 1px solid {COLOR_LIGHT_TERTIARY};
}}
QLabel#headerLabel {{
    color: {COLOR_TEXT_DARK};
    font-size: 18px;
    font-weight: 600;
}}
QLabel#headerSubtitle {{
    color: #6b7280; /* Gray-500 */
    font-size: 14px;
}}

/* --- Section Headers --- */
QLabel#dialogSectionHeader {{
    color: {COLOR_TEXT_DARK};
    font-size: 14px;
    font-weight: 600;
    margin-top: 10px;
    padding-bottom: 5px;
    border-bottom: 2px solid {COLOR_LIGHT_TERTIARY};
}}

/* --- Input Fields --- */
QLineEdit, QSpinBox {{
    background-color: {COLOR_LIGHT_SECONDARY};
    color: {COLOR_TEXT_DARK};
    border: 1px solid {COLOR_LIGHT_TERTIARY};
    border-radius: 6px;
    padding: 10px;
    font-size: 14px;
}}
QLineEdit:focus, QSpinBox:focus {{
    border-color: {COLOR_ACCENT_PRIMARY};
    background-color: {COLOR_LIGHT_PRIMARY};
}}
QLineEdit:disabled, QSpinBox:disabled {{
    background-color: {COLOR_LIGHT_TERTIARY};
    color: #9ca3af; /* Gray-400 */
}}

/* --- Checkbox --- */
QCheckBox {{
    color: {COLOR_TEXT_DARK};
    spacing: 8px;
    font-size: 14px;
    font-weight: 600;
}}
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {COLOR_LIGHT_TERTIARY};
    border-radius: 6px;
}}
QCheckBox::indicator:checked {{
    background-color: {COLOR_ACCENT_PRIMARY};
    border-color: {COLOR_ACCENT_PRIMARY};
}}

/* --- Text Area --- */
QTextEdit {{
    background-color: {COLOR_LIGHT_SECONDARY};
    border: 1px solid {COLOR_LIGHT_TERTIARY};
    border-radius: 6px;
    font-family: 'Consolas', 'Monaco', monospace;
}}

/* --- Dialog Buttons --- */
#dialogButtons QWidget {{
    background-color: {COLOR_LIGHT_SECONDARY};
    border-top: 1px solid {COLOR_LIGHT_TERTIARY};
}}

#dialogButtons QPushButton {{
    font-size: 14px;
    font-weight: 600;
    padding: 12px 20px;
    text-align: center;
}}
#dialogButtons #saveButton {{
    background-color: {COLOR_ACCENT_SUCCESS};
    color: white;
}}
#dialogButtons #saveButton:hover {{
    background-color: #339154;
}}
#dialogButtons #cancelButton {{
    background-color: {COLOR_LIGHT_TERTIARY};
    color: {COLOR_TEXT_DARK};
}}
#dialogButtons #cancelButton:hover {{
    background-color: #d1d5db; /* Gray-300 */
}}
#dialogButtons #testButton {{
    background-color: {COLOR_ACCENT_WARNING};
    color: {COLOR_TEXT_DARK};
}}
#dialogButtons #testButton:hover {{
    background-color: #e1940a;
}}
#dialogButtons #importButton {{
    background-color: {COLOR_ACCENT_PRIMARY};
    color: white;
}}
#dialogButtons #importButton:hover {{
    background-color: {COLOR_ACCENT_HOVER};
}}
"""

# Status colors for different message types, designed to fit the new theme
STATUS_COLORS = {
    # Text Color, Background Color, Border Color
    "info":    ("#3c366b", "#e0e7ff", "#c7d2fe"),  # Indigo
    "success": ("#166534", "#dcfce7", "#bbf7d0"),  # Green
    "warning": ("#b45309", "#fef3c7", "#fde68a"),  # Amber
    "error":   ("#991b1b", "#fee2e2", "#fecaca")   # Red
} 