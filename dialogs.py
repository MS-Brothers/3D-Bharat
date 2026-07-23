import copy
import numpy as np
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QGridLayout, QGroupBox, QCheckBox, 
    QTextEdit, QComboBox, QDoubleSpinBox, QRadioButton, QButtonGroup, QWidget, QFileDialog, QInputDialog, QMessageBox,
    QScrollArea, QMenu, QAction, QListWidget, QMainWindow, QSizePolicy, QFrame, QStackedWidget, QTableWidget, QHeaderView, QTableWidgetItem,
    ### Mayur Wakhare 16-06-2026 Upadate code for 3D workshet selection tree View
    QProgressBar, QColorDialog, QProgressDialog, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QApplication,
    QTreeWidget, QTreeWidgetItem
    ###############################################################
)

from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper, vtkRenderer, vtkProperty
from vtkmodules.vtkFiltersSources import vtkPlaneSource, vtkCubeSource
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QColor, QPixmap, QFont

import os
import json
import shutil
from API import WorksheetAPI
from json_manager import DesignConstructionManager

from datetime import datetime
import glob

# ===========================================================================================================================
# ** ZERO LINE DIALOG **
# ===========================================================================================================================
class ZeroLineDialog(QDialog):
    def __init__(self, point1=None, point2=None, km1=None, chain1=None, km2=None, chain2=None, interval=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zero Line Configuration")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #e6e6fa, stop:1 #e6e6fa);
                border-radius: 20px;
            }
            QLabel {
                color: black;
                font-weight: 500;
            }
            QGroupBox {
                border: 2px solid #7B1FA2;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 10px;
                font-weight: bold;
                color: #4A148C;
                background-color: rgba(255,255,255,0.3);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 3px 8px;
                font-size: 12px;
            }
            QLineEdit {
                border: 2px solid #9C27B0;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                selection-background-color: #CE93D8;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 2px solid #7B1FA2;
                background-color: #F3E5F5;
            }
            QPushButton {
                border-radius: 20px;
                padding: 10px;
                font-weight: bold;
                min-width: 120px;
                border: none;
            }
            QPushButton#saveBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #9C27B0, stop:1 #6A1B9A);
                color: white;
            }
            QPushButton#saveBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #AB47BC, stop:1 #4A148C);
            }
            QPushButton#saveBtn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #6A1B9A, stop:1 #4A148C);
                padding: 12px 10px 8px 10px;
            }
            QPushButton#cancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333333;
            }
            QPushButton#cancelBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #D1C4E9, stop:1 #BA68C8);
            }
            QPushButton#cancelBtn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #CE93D8, stop:1 #8E24AA);
                padding: 12px 10px 8px 10px;
            }
        """)

        layout = QVBoxLayout(self)

        # Point 1 KM and Chainage
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("FROM KM:"))
        self.km1_edit = QLineEdit(str(km1) if km1 is not None else "")
        self.km1_edit.setPlaceholderText("e.g. 101")
        row1.addWidget(self.km1_edit)
        row1.addWidget(QLabel("FROM Chainage:"))
        self.chain1_edit = QLineEdit(str(chain1) if chain1 is not None else "")
        self.chain1_edit.setPlaceholderText("Optional")
        row1.addWidget(self.chain1_edit)
        layout.addLayout(row1)

        # Point 1 coordinates
        group_p1 = QGroupBox("Point 1 Coordinates")
        layout_p1 = QGridLayout(group_p1)
        layout_p1.addWidget(QLabel("X:"), 0, 0)
        self.x1_edit = QLineEdit(f"{point1[0]:.3f}" if point1 is not None else "0.000")
        layout_p1.addWidget(self.x1_edit, 0, 1)
        layout_p1.addWidget(QLabel("Y:"), 0, 2)
        self.y1_edit = QLineEdit(f"{point1[1]:.3f}" if point1 is not None else "0.000")
        layout_p1.addWidget(self.y1_edit, 0, 3)
        layout_p1.addWidget(QLabel("Z:"), 1, 0)
        self.z1_edit = QLineEdit(f"{point1[2]:.3f}" if point1 is not None else "0.000")
        layout_p1.addWidget(self.z1_edit, 1, 1)
        layout.addWidget(group_p1)

        # Point 2 KM and Chainage
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("TO KM:"))
        self.km2_edit = QLineEdit(str(km2) if km2 is not None else "")
        self.km2_edit.setPlaceholderText("e.g. 102")
        row2.addWidget(self.km2_edit)
        row2.addWidget(QLabel("TO Chainage:"))
        self.chain2_edit = QLineEdit(str(chain2) if chain2 is not None else "")
        self.chain2_edit.setPlaceholderText("Optional")
        row2.addWidget(self.chain2_edit)
        layout.addLayout(row2)

        # Point 2 coordinates
        group_p2 = QGroupBox("Point 2 Coordinates")
        layout_p2 = QGridLayout(group_p2)
        layout_p2.addWidget(QLabel("X:"), 0, 0)
        self.x2_edit = QLineEdit(f"{point2[0]:.3f}" if point2 is not None else "0.000")
        layout_p2.addWidget(self.x2_edit, 0, 1)
        layout_p2.addWidget(QLabel("Y:"), 0, 2)
        self.y2_edit = QLineEdit(f"{point2[1]:.3f}" if point2 is not None else "0.000")
        layout_p2.addWidget(self.y2_edit, 0, 3)
        layout_p2.addWidget(QLabel("Z:"), 1, 0)
        self.z2_edit = QLineEdit(f"{point2[2]:.3f}" if point2 is not None else "0.000")
        layout_p2.addWidget(self.z2_edit, 1, 1)
        layout.addWidget(group_p2)


        # Interval
        from PyQt5.QtGui import QIntValidator

        # Replace the interval line with this:
        row_int = QHBoxLayout()
        row_int.addWidget(QLabel("Interval (m):"))
        self.interval_edit = QLineEdit(str(int(interval)) if interval is not None else "20")
        self.interval_edit.setValidator(QIntValidator(1, 10000))  # Only positive integers
        self.interval_edit.setPlaceholderText("e.g. 20")
        row_int.addWidget(self.interval_edit)
        layout.addLayout(row_int)

        # Connect signals for automatic calculation
        self.x1_edit.textChanged.connect(self.update_auto_chainage)
        self.y1_edit.textChanged.connect(self.update_auto_chainage)
        self.z1_edit.textChanged.connect(self.update_auto_chainage)
        self.x2_edit.textChanged.connect(self.update_auto_chainage)
        self.y2_edit.textChanged.connect(self.update_auto_chainage)
        self.z2_edit.textChanged.connect(self.update_auto_chainage)
        self.km1_edit.textEdited.connect(self.update_auto_chainage)
        self.chain1_edit.textEdited.connect(self.update_auto_chainage)
        self.interval_edit.textEdited.connect(self.update_auto_chainage)

        # Connect signals for manual TO chainage changes
        self.km2_edit.textEdited.connect(self.update_p2_from_chainage)
        self.chain2_edit.textEdited.connect(self.update_p2_from_chainage)

        # Base properties to track original differences
        try:
            self._base_km1 = int(km1) if km1 is not None else 0
            self._base_ch1 = float(chain1) if chain1 is not None else 0.0
            self._base_km2 = int(km2) if km2 is not None else 0
            self._base_ch2 = float(chain2) if chain2 is not None else 0.0
            
            self._base_x1 = point1[0] if point1 else 0.0
            self._base_y1 = point1[1] if point1 else 0.0
            self._base_x2 = point2[0] if point2 else 0.0
            self._base_y2 = point2[1] if point2 else 0.0
        except:
            pass
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Zero Line")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self.on_save_clicked)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    # -------------------------------------------------
    # Automatic chainage calculation
    # -------------------------------------------------
    def update_auto_chainage(self):
        """
        Automatically update TO KM + Chainage when FROM fields or coordinates or interval change.
        Snaps distance DOWN to nearest interval multiple (typical road/alignment practice).
        """
        try:
            # ── Coordinates ───────────────────────────────────────
            x1 = float(self.x1_edit.text() or "0")
            y1 = float(self.y1_edit.text() or "0")
            z1 = float(self.z1_edit.text() or "0")
            x2 = float(self.x2_edit.text() or "0")
            y2 = float(self.y2_edit.text() or "0")
            z2 = float(self.z2_edit.text() or "0")

            # Actual 3D distance
            dist = ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2) ** 0.5

            # ── Starting chainage info ────────────────────────────
            km1_str   = self.km1_edit.text().strip()
            ch1_str   = self.chain1_edit.text().strip()
            interv_str = self.interval_edit.text().strip()

            km1 = int(km1_str) if km1_str.isdigit() else 0
            ch1 = float(ch1_str) if ch1_str.replace(".", "").isdigit() else 0.0

            interval = 20.0
            if interv_str.replace(".", "").isdigit():
                interval = float(interv_str)
                if interval <= 0:
                    interval = 20.0

            # Snap DOWN to nearest interval (most common in chainage stationing)
            snapped_dist = (int(dist // interval)) * interval

            # Total chainage from project zero point
            total_start_m = km1 * 1000 + ch1
            total_end_m   = total_start_m + snapped_dist

            # Compute end station
            km2 = int(total_end_m // 1000)
            ch2 = total_end_m % 1000

            # Update TO fields without triggering recursion
            self.km2_edit.blockSignals(True)
            self.chain2_edit.blockSignals(True)

            self.km2_edit.setText(str(km2))
            self.chain2_edit.setText(f"{ch2:.3f}")

            self.km2_edit.blockSignals(False)
            self.chain2_edit.blockSignals(False)

        except (ValueError, TypeError):
            # partial / invalid input → silent ignore (user is still typing)
            pass

    # -------------------------------------------------
    # Manual chainage calculation (Update P2 based on Chainage input)
    # -------------------------------------------------
    def update_p2_from_chainage(self):
        """
        Update Point 2 coordinates when the user manually changes 'TO KM' or 'TO Chainage'.
        Calculates the delta chainage and applies it to the axis with the largest difference.
        """
        try:
            km1 = int(self.km1_edit.text() or "0")
            ch1 = float(self.chain1_edit.text() or "0")
            km2 = int(self.km2_edit.text() or "0")
            ch2 = float(self.chain2_edit.text() or "0")

            total_start_m = km1 * 1000 + ch1
            total_end_m   = km2 * 1000 + ch2

            # Calculate expected new distance from P1
            desired_dist = total_end_m - total_start_m

            x1 = float(self.x1_edit.text() or "0")
            y1 = float(self.y1_edit.text() or "0")
            z1 = float(self.z1_edit.text() or "0")
            old_x2 = float(self.x2_edit.text() or "0")
            old_y2 = float(self.y2_edit.text() or "0")
            old_z2 = float(self.z2_edit.text() or "0")

            diff_x = old_x2 - x1
            diff_y = old_y2 - y1
            diff_z = old_z2 - z1

            current_dist = (diff_x**2 + diff_y**2 + diff_z**2) ** 0.5

            if current_dist > 0:
                scale = desired_dist / current_dist
                new_x2 = x1 + diff_x * scale
                new_y2 = y1 + diff_y * scale
                # We can also update Z if desired, or keep it as is. Usually it scales too.
                new_z2 = z1 + diff_z * scale

                self.x2_edit.blockSignals(True)
                self.y2_edit.blockSignals(True)
                self.z2_edit.blockSignals(True)

                self.x2_edit.setText(f"{new_x2:.3f}")
                self.y2_edit.setText(f"{new_y2:.3f}")
                self.z2_edit.setText(f"{new_z2:.3f}")

                self.x2_edit.blockSignals(False)
                self.y2_edit.blockSignals(False)
                self.z2_edit.blockSignals(False)

        except (ValueError, TypeError):
            # Error ignored if typing incomplete string
            pass

    # -------------------------------------------------
    # Custom save button handler with full validation
    # -------------------------------------------------
    def on_save_clicked(self):
        if self.validate_all_inputs():
            self.accept()  # Only accept if everything is valid

    # -------------------------------------------------
    # Full input validation
    # -------------------------------------------------
    def validate_all_inputs(self):
        errors = []

        # Validate coordinates (must be valid floats and not empty)
        coord_fields = [
            ("Point 1 X", self.x1_edit),
            ("Point 1 Y", self.y1_edit),
            ("Point 1 Z", self.z1_edit),
            ("Point 2 X", self.x2_edit),
            ("Point 2 Y", self.y2_edit),
            ("Point 2 Z", self.z2_edit),
        ]

        for label, edit in coord_fields:
            text = edit.text().strip()
            if not text:
                errors.append(f"{label} cannot be empty.")
                continue
            try:
                float(text)
            except ValueError:
                errors.append(f"{label} must be a valid number (e.g., 387211.438).")

        # Validate KM fields (optional, but must be integer if filled)
        for label, edit in [("Point 1 KM", self.km1_edit), ("Point 2 KM", self.km2_edit)]:
            text = edit.text().strip()
            if text:
                if not text.isdigit():
                    errors.append(f"{label} must be a whole number (e.g., 101).")

        # Validate interval
        interval_text = self.interval_edit.text().strip()
        if not interval_text:
            errors.append("Interval cannot be empty.")
        else:
            try:
                interval_val = float(interval_text)
                if interval_val <= 0:
                    errors.append("Interval must be greater than 0.")
            except ValueError:
                errors.append("Interval must be a valid number (e.g., 20 or 20.5).")

        if errors:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please correct the following errors:\n\n" + "\n".join(f"• {e}" for e in errors)
            )
            return False

        return True

    # -------------------------------------------------
    # Safe extraction of coordinates
    # -------------------------------------------------
    def get_points(self):
        """Returns (p1, p2) as numpy arrays. Guaranteed valid due to validation."""
        try:
            p1 = np.array([
                float(self.x1_edit.text().strip()),
                float(self.y1_edit.text().strip()),
                float(self.z1_edit.text().strip())
            ])
            p2 = np.array([
                float(self.x2_edit.text().strip()),
                float(self.y2_edit.text().strip()),
                float(self.z2_edit.text().strip())
            ])
            return p1, p2
        except Exception:
            return None, None  # Should never reach here due to validation

    # -------------------------------------------------
    # Optional: Helper to get KM and interval safely
    # -------------------------------------------------
    def get_configuration(self):
        def to_int(s):
            s = s.strip()
            return int(s) if s.isdigit() else None

        def to_float(s, default=0.0):
            s = s.strip()
            try:
                return float(s)
            except:
                return default

        return {
            'km1':        to_int(self.km1_edit.text()),
            'chainage1':  to_float(self.chain1_edit.text()),
            'km2':        to_int(self.km2_edit.text()),
            'chainage2':  to_float(self.chain2_edit.text()),
            'interval':   to_float(self.interval_edit.text(), 20.0)
        }
# ===========================================================================================================================
# ** CURVE DIALOG **
# ===========================================================================================================================
class CurveDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Curve Configuration")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #e6e6fa, stop:1 #e6e6fa);
                border-radius: 20px;
            }
            QLabel {
                color: black;
                font-weight: 500;
            }
            QCheckBox {
                color: black;
                font-weight: 500;
                spacing: 10px;
            }
            QLineEdit {
                border: 2px solid #9C27B0;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                selection-background-color: #CE93D8;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 2px solid #7B1FA2;
                background-color: #F3E5F5;
            }
            QPushButton {
                border-radius: 20px;
                padding: 10px;
                font-weight: bold;
                min-width: 80px;
                border: none;
            }
            QPushButton#okBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #9C27B0, stop:1 #6A1B9A);
                color: white;
            }
            QPushButton#okBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #AB47BC, stop:1 #4A148C);
            }
            QPushButton#okBtn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #6A1B9A, stop:1 #4A148C);
                padding: 12px 10px 8px 10px;
            }
            QPushButton#cancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333333;
            }
            QPushButton#cancelBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #D1C4E9, stop:1 #BA68C8);
            }
            QPushButton#cancelBtn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #CE93D8, stop:1 #8E24AA);
                padding: 12px 10px 8px 10px;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Inner & Outer Curve checkboxes in one row
        checkbox_layout = QHBoxLayout()
        self.outer_checkbox = QCheckBox("Outer Curve")
        self.inner_checkbox = QCheckBox("Inner Curve")
        checkbox_layout.addWidget(self.outer_checkbox)
        checkbox_layout.addWidget(self.inner_checkbox)
        checkbox_layout.addStretch()
        layout.addLayout(checkbox_layout)
        
        # Single angle input below the checkboxes
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("Angle:"))
        self.angle_edit = QLineEdit("0.0")
        self.angle_edit.setFixedWidth(80)
        angle_layout.addWidget(self.angle_edit)
        angle_layout.addStretch()
        layout.addLayout(angle_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setObjectName("okBtn")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def get_configuration(self):
        return {
            'outer_curve': self.outer_checkbox.isChecked(),
            'inner_curve': self.inner_checkbox.isChecked(),
            'angle': float(self.angle_edit.text() or 0.0)
        }

# ===========================================================================================================================
# ** CONSTRUCTION CONFIG DIALOG **
# ===========================================================================================================================
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QRadioButton,
    QButtonGroup, QLineEdit, QComboBox, QPushButton, QCheckBox, QFrame,
    QStackedWidget, QGridLayout, QFormLayout, QScrollArea
)
from PyQt5.QtCore import Qt

class ConstructionConfigDialog(QDialog):
    def __init__(self, chainage_label="", parent=None, loaded_data=None):
        super().__init__(parent)

        self.setWindowTitle(f"Construction Configuration - {chainage_label}")
        self.setModal(True)
        self.setMinimumSize(860, 740)          # Slightly taller to feel more comfortable

        self.chainage_label = chainage_label.strip()
        self.parent_widget = parent
        self.loaded_data = loaded_data

        # ───────────────────────────────────────────────────────────────
        #                      Stylesheet (unchanged)
        # ───────────────────────────────────────────────────────────────
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f0f4ff, stop:1 #e6e6fa);
                border-radius: 16px;
            }
            QLabel {
                color: #1a1a3d;
                font-weight: 500;
            }
            QFrame {
                background: rgba(255,255,255,0.35);
                border-radius: 12px;
            }
            QGroupBox {
                border: 2px solid #6a1b9a;
                border-radius: 10px;
                margin-top: 18px;
                padding-top: 12px;
                font-weight: bold;
                color: #4a148c;
                background: rgba(255,255,255,0.4);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                font-size: 13px;
            }
            QCheckBox, QRadioButton {
                color: #1a1a3d;
                font-weight: 500;
                spacing: 12px;
            }
            QLineEdit {
                border: 1.5px solid #b19cd9;
                border-radius: 8px;
                padding: 8px 10px;
                background: white;
                font-weight: 500;
                selection-background-color: #d7c3e6;
            }
            QLineEdit:focus {
                border: 2px solid #7b1fa2;
                background: #f8f5ff;
                selection-background-color: #ce93d8;
            }
            QLineEdit:hover:!focus {
                border: 1.5px solid #9c27b0;
            }
            QComboBox {
                border: 1.5px solid #b19cd9;
                border-radius: 8px;
                padding: 6px 10px;
                background: white;
                font-weight: 500;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox:focus {
                border: 2px solid #7b1fa2;
                background: #f8f5ff;
            }
            QPushButton {
                border-radius: 18px;
                padding: 10px 18px;
                font-weight: 600;
                min-width: 100px;
                border: none;
            }
            QPushButton#saveBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #8e24aa, stop:1 #6a1b9a);
                color: white;
            }
            QPushButton#saveBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #ab47bc, stop:1 #7b1fa2);
            }
            QPushButton#nextBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #f57c00, stop:1 #ef6c00);
                color: white;
            }
            QPushButton#cancelBtn, QPushButton#backBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #d1c4e9, stop:1 #b39ddb);
                color: #333;
            }
            QPushButton#cancelBtn:hover, QPushButton#backBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #ba68c8, stop:1 #8e24aa);
                color: white;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(12)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # ───────────────────────────────
        #           PAGE 1 – Bridge Type (unchanged)
        # ───────────────────────────────
        self.page1 = QWidget()
        p1 = QVBoxLayout(self.page1)
        p1.setSpacing(12)

        title1 = QLabel(f"BRIDGE DESIGN CONFIGURATION\nChainage: {self.chainage_label}")
        title1.setAlignment(Qt.AlignCenter)
        title1.setStyleSheet("""
            font-size: 15px; font-weight: bold; color: #4a148c;
            padding: 12px; background: rgba(232,245,233,0.65);
            border-radius: 8px; border: 1px solid #81c784;
        """)
        p1.addWidget(title1)


        # ─── Pillar Name Input + Yellow Sticker (real bridge style) ───────────────────────────
        pillar_name_container = QHBoxLayout()
        pillar_name_container.setContentsMargins(0, 10, 0, 10)

        # Label + Input field
        input_hbox = QHBoxLayout()
        input_hbox.addWidget(QLabel("Pillar / Pier ID:"))
        self.le_pillar_name = QLineEdit()
        self.le_pillar_name.setPlaceholderText("e.g. P12, Pier-45, Abutment-A, P380")
        self.le_pillar_name.setMaximumWidth(280)
        self.le_pillar_name.setMinimumWidth(220)
        input_hbox.addWidget(self.le_pillar_name)
        input_hbox.addStretch()
        pillar_name_container.addLayout(input_hbox)

        # Yellow circular sticker (updates live when user types)
        sticker_vbox = QVBoxLayout()
        sticker_vbox.setAlignment(Qt.AlignCenter)
        sticker_vbox.setSpacing(4)

        self.pillar_sticker = QLabel("P ?")
        self.pillar_sticker.setAlignment(Qt.AlignCenter)
        self.pillar_sticker.setFixedSize(120, 120)
        self.pillar_sticker.setStyleSheet("""
            QLabel {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, 
                                            fx:0.5, fy:0.5, 
                                            stop:0 #fff176, stop:0.5 #ffee58, stop:1 #fdd835);
                color: #000000;
                font-size: 32px;
                font-weight: bold;
                border: 4px solid #c62828;
                border-radius: 60px;
                padding: 12px;
                box-shadow: 4px 5px 10px rgba(0,0,0,0.4);
            }
        """)

        sub_label = QLabel("PIER ID")
        sub_label.setStyleSheet("color: #b71c1c; font-size: 12px; font-weight: bold;")
        sub_label.setAlignment(Qt.AlignCenter)

        sticker_vbox.addWidget(self.pillar_sticker)
        sticker_vbox.addWidget(sub_label)

        pillar_name_container.addStretch()
        pillar_name_container.addLayout(sticker_vbox)
        pillar_name_container.addStretch()

        p1.addLayout(pillar_name_container)

        # Small note
        note = QLabel("This name will appear as a yellow label on the 3D pillar")
        note.setStyleSheet("font-size: 10px; color: #666666; font-style: italic;")
        note.setAlignment(Qt.AlignCenter)
        p1.addWidget(note)

        p1.addSpacing(12)

        # ─── Live update sticker when user types ────────────────────────────────
        self.le_pillar_name.textChanged.connect(self._update_pillar_sticker)


        if self.parent_widget and hasattr(self.parent_widget, 'current_worksheet_data'):
            data = self.parent_widget.current_worksheet_data
            layer_name = data.get("initial_layer_name") or data.get("initial_layer", "").strip()
            if layer_name and layer_name.lower() != "none":
                layer_h = QHBoxLayout()
                layer_h.addWidget(QLabel("Layer:"))
                le = QLineEdit(layer_name)
                le.setReadOnly(True)
                le.setStyleSheet("background:#f5f5f5; color:#555; border:1px solid #ccc;")
                layer_h.addWidget(le)
                p1.addLayout(layer_h)

        gb_type = QGroupBox("Bridge Type")
        vb = QVBoxLayout(gb_type)
        self.rb_group = QButtonGroup(self)

        self.rb_under = QRadioButton("Under Pass")
        self.rb_mini  = QRadioButton("Mini Bridge")
        self.rb_long  = QRadioButton("Long Bridge")

        for rb in [self.rb_under, self.rb_mini, self.rb_long]:
            self.rb_group.addButton(rb)
            vb.addWidget(rb)

        for rb in [self.rb_under, self.rb_mini, self.rb_long]:
            rb.toggled.connect(self._update_page1_visibility)

        p1.addWidget(gb_type)

        self.frame_bridge = QFrame()
        self.frame_bridge.setVisible(False)
        fbl = QVBoxLayout(self.frame_bridge)

        fbl.addWidget(QLabel("Configuration").setStyleSheet("font-weight:bold; color:#4a148c; font-size:13px;"))

        self.w_mini = QWidget()
        hl = QHBoxLayout(self.w_mini)
        hl.addWidget(QLabel("Type:"))
        self.combo_mini = QComboBox()
        self.combo_mini.addItems(["", "Pillar Base", "Box Base", "Circular Pipe"])
        hl.addWidget(self.combo_mini)
        fbl.addWidget(self.w_mini)
        self.w_mini.setVisible(False)

        self.w_long = QWidget()
        hl = QHBoxLayout(self.w_long)
        hl.addWidget(QLabel("Type:"))
        self.combo_long = QComboBox()
        self.combo_long.addItems(["", "Normal", "U Shape Pillar", "L Shape Pillar"])
        hl.addWidget(self.combo_long)
        fbl.addWidget(self.w_long)
        self.w_long.setVisible(False)

        hl = QHBoxLayout()
        hl.addWidget(QLabel("Number of supports:"))
        self.le_supports = QLineEdit()
        self.le_supports.setPlaceholderText("e.g. 3 or 5")
        hl.addWidget(self.le_supports)
        fbl.addLayout(hl)

        p1.addWidget(self.frame_bridge)

        self.frame_under = QFrame()
        self.frame_under.setVisible(False)
        ful = QVBoxLayout(self.frame_under)
        ful.addWidget(QLabel("Underpass Dimensions (m)").setStyleSheet("font-weight:bold; color:#4a148c;"))

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.addWidget(QLabel("Width:"), 0, 0)
        self.le_under_w = QLineEdit()
        grid.addWidget(self.le_under_w, 0, 1)
        grid.addWidget(QLabel("Height:"), 1, 0)
        self.le_under_h = QLineEdit()
        grid.addWidget(self.le_under_h, 1, 1)
        grid.addWidget(QLabel("Length:"), 2, 0)
        self.le_under_l = QLineEdit()
        grid.addWidget(self.le_under_l, 2, 1)
        ful.addLayout(grid)
        p1.addWidget(self.frame_under)

        btn1 = QHBoxLayout()
        btn1.addStretch()

        self.btn_cancel = QPushButton("Cancel", objectName="cancelBtn")
        self.btn_cancel.clicked.connect(self.reject)
        btn1.addWidget(self.btn_cancel)

        self.btn_next = QPushButton("Next →", objectName="nextBtn")
        self.btn_next.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.btn_next.setVisible(False)
        btn1.addWidget(self.btn_next)

        p1.addLayout(btn1)

        self.stacked_widget.addWidget(self.page1)

        # ───────────────────────────────
        #           PAGE 2 – Construction Configuration with Scroll
        # ───────────────────────────────
        self.page2 = QWidget()
        p2_outer = QVBoxLayout(self.page2)
        p2_outer.setContentsMargins(0, 0, 0, 0)
        p2_outer.setSpacing(0)

        title2 = QLabel(f"CONSTRUCTION CONFIGURATION\nChainage: {self.chainage_label}")
        title2.setAlignment(Qt.AlignCenter)
        title2.setStyleSheet(title1.styleSheet())
        p2_outer.addWidget(title2)

        # ─── Scroll Area ────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_content = QWidget()
        p2 = QVBoxLayout(scroll_content)
        p2.setContentsMargins(20, 16, 20, 20)
        p2.setSpacing(14)

        # Location
        pos_h = QHBoxLayout()
        pos_h.addWidget(QLabel("Location: ").setStyleSheet("font-weight:bold;"))
        self.cb_over   = QCheckBox("Over the water")
        self.cb_under  = QCheckBox("Under the water")
        self.cb_land   = QCheckBox("On land")
        pos_h.addWidget(self.cb_over)
        pos_h.addWidget(self.cb_under)
        pos_h.addWidget(self.cb_land)
        pos_h.addStretch()
        p2.addLayout(pos_h)

        self._make_exclusive_checkboxes([self.cb_over, self.cb_under, self.cb_land])

        # Shapes
        shapes_h = QHBoxLayout()

        def add_shape_group(title, options):
            gb = QGroupBox(title)
            vb = QVBoxLayout(gb)
            cbs = []
            for opt in options:
                cb = QCheckBox(opt)
                vb.addWidget(cb)
                cbs.append(cb)
            self._make_exclusive_checkboxes(cbs)
            shapes_h.addWidget(gb)
            return cbs

        self.base_cbs   = add_shape_group("Base (shape)",   ["Rectangle", "Square", "Circular", "Other"])
        self.pillar_cbs = add_shape_group("Pillar (shape)", ["Circular", "Rectangular", "Tapered", "Other"])
        self.span_cbs   = add_shape_group("Span (shape)",   ["Vert. shape", "Flat shape", "Arched", "Slab", "T_Beam", "Box girder", "Other"])
        self.deck_cbs   = add_shape_group("Deck Support (shape)", ["Rectangular Box (Cuboid)", "Square Box", "Other"])

        p2.addLayout(shapes_h)

        # Dimensions
        dims_h = QHBoxLayout()

        def add_dim_group(title, labels_defaults):
            gb = QGroupBox(title)
            grid = QGridLayout(gb)
            grid.setVerticalSpacing(8)
            for i, (lbl, ph) in enumerate(labels_defaults):
                grid.addWidget(QLabel(f"{lbl}:"), i, 0)
                le = QLineEdit()
                le.setPlaceholderText(ph or "—")
                grid.addWidget(le, i, 1)
            dims_h.addWidget(gb)
            return [gb.layout().itemAt(j*2+1).widget() for j in range(len(labels_defaults))]

        self.base_dims   = add_dim_group("Base dimension (m)",   [("Width", ""), ("Length", ""), ("Height", ""), ("Depth", "")])
        self.pillar_dims = add_dim_group("Pillar Dimension (m)", [("Diameter/Width", ""), ("Height", ""), ("Length", "")])
        self.span_dims   = add_dim_group("Span Dimension (m)",   [("Height", ""), ("Width", ""), ("Length", ""), ("Thickness", "")])
        self.deck_dims   = add_dim_group("Deck Support Dimension (m)", [("Width", ""), ("Height", ""), ("Length", "")])

        p2.addLayout(dims_h)

        # Steel Configuration checkbox
        steel_check_h = QHBoxLayout()
        steel_check_h.addStretch()
        self.cb_steel_config = QCheckBox("Steel Configuration")
        self.cb_steel_config.setStyleSheet("font-weight: bold; color: #4a148c; font-size: 13px;")
        steel_check_h.addWidget(self.cb_steel_config)
        steel_check_h.addStretch()
        p2.addLayout(steel_check_h)

        # Steel configuration content
        self.frame_steel = QFrame()
        self.frame_steel.setVisible(False)
        steel_vl = QVBoxLayout(self.frame_steel)
        steel_vl.setSpacing(14)

        self.steel_types = [
            "TMT Bars",
            "Reinforcement steel - Epoxy Coated Rebar",
            "Reinforcement steel - Galvanized Rebar",
            "Reinforcement steel - Stainless Steel",
            "Structural Steel",
            "Weathering Steel",
            "Prestressing Steel",
            "High Strength Steel",
            "Other"
        ]

        self.steel_combos = {}
        self.grade_lines = {}

        for comp in ["Base", "Pillar", "Span", "Deck Support"]:
            gb = QGroupBox(f"{comp} Steel")
            form = QFormLayout(gb)
            form.setLabelAlignment(Qt.AlignRight)

            combo = QComboBox()
            combo.addItems(["(select)"] + self.steel_types)
            form.addRow("Steel Type:", combo)

            grade = QLineEdit()
            grade.setPlaceholderText("e.g. Fe 500, ASTM A615 Gr.60, E350, etc.")
            form.addRow("Grade / Instruction:", grade)

            steel_vl.addWidget(gb)

            key = comp.lower().replace(" ", "_")
            self.steel_combos[key] = combo
            self.grade_lines[key] = grade

        p2.addWidget(self.frame_steel)

        self.cb_steel_config.stateChanged.connect(self._on_steel_config_toggled)

        p2.addStretch()   # ← keeps content from stretching weirdly

        scroll.setWidget(scroll_content)
        p2_outer.addWidget(scroll)

        # Buttons – always visible at bottom
        btn2 = QHBoxLayout()
        btn2.addStretch()

        btn_back = QPushButton("Back", objectName="backBtn")
        btn_back.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        btn2.addWidget(btn_back)

        btn_save = QPushButton("Save", objectName="saveBtn")
        btn_save.clicked.connect(self.accept)
        btn2.addWidget(btn_save)

        p2_outer.addLayout(btn2)

        self.stacked_widget.addWidget(self.page2)

        self.stacked_widget.setCurrentIndex(0)

        if self.loaded_data:
            self._populate_from_loaded_data()

    def _on_steel_config_toggled(self, state):
        self.frame_steel.setVisible(state == Qt.Checked)

    # ───────────────────────────────────────────────────────────────
    #               Original methods – unchanged below
    # ───────────────────────────────────────────────────────────────

    def _update_page1_visibility(self, checked):
        if not checked:
            return
        sender = self.sender()

        self.frame_bridge.setVisible(False)
        self.frame_under.setVisible(False)
        self.btn_next.setVisible(False)

        if sender == self.rb_under:
            self.frame_under.setVisible(True)
            self.btn_next.setVisible(True)
        elif sender in (self.rb_mini, self.rb_long):
            self.frame_bridge.setVisible(True)
            self.w_mini.setVisible(sender == self.rb_mini)
            self.w_long.setVisible(sender == self.rb_long)
            self.btn_next.setVisible(True)

    def _make_exclusive_checkboxes(self, checkboxes):
        def handler(checked_cb):
            if checked_cb.isChecked():
                for cb in checkboxes:
                    if cb is not checked_cb:
                        cb.blockSignals(True)
                        cb.setChecked(False)
                        cb.blockSignals(False)

        for cb in checkboxes:
            cb.stateChanged.connect(lambda state, c=cb: handler(c) if state == Qt.Checked else None)

    def _populate_from_loaded_data(self):
        if not self.loaded_data:
            return
        try:
            bridge_type = self.loaded_data.get('bridge_type', '')
            if bridge_type == 'Under Pass':
                self.rb_under.setChecked(True)
                self.le_under_w.setText(str(self.loaded_data.get('underpass_width', '')))
                self.le_under_h.setText(str(self.loaded_data.get('underpass_height', '')))
                self.le_under_l.setText(str(self.loaded_data.get('underpass_length', '')))
            elif bridge_type == 'Mini Bridge':
                self.rb_mini.setChecked(True)
                mini_type = self.loaded_data.get('mini_type', '')
                if mini_type:
                    idx = self.combo_mini.findText(mini_type)
                    if idx >= 0:
                        self.combo_mini.setCurrentIndex(idx)
                self.le_supports.setText(str(self.loaded_data.get('support_count', '')))
            elif bridge_type == 'Long Bridge':
                self.rb_long.setChecked(True)
                long_type = self.loaded_data.get('long_type', '')
                if long_type:
                    idx = self.combo_long.findText(long_type)
                    if idx >= 0:
                        self.combo_long.setCurrentIndex(idx)
                self.le_supports.setText(str(self.loaded_data.get('support_count', '')))

            location = self.loaded_data.get('location', '')
            for cb in [self.cb_over, self.cb_under, self.cb_land]:
                if cb.text() == location:
                    cb.setChecked(True)
                    break

            base_shape = self.loaded_data.get('base_shape', '')
            for cb in self.base_cbs:
                if cb.text() == base_shape:
                    cb.setChecked(True)
                    break

            pillar_shape = self.loaded_data.get('pillar_shape', '')
            for cb in self.pillar_cbs:
                if cb.text() == pillar_shape:
                    cb.setChecked(True)
                    break

            span_shape = self.loaded_data.get('span_shape', '')
            for cb in self.span_cbs:
                if cb.text() == span_shape:
                    cb.setChecked(True)
                    break

            deck_shape = self.loaded_data.get('deck_support_shape', '')
            for cb in self.deck_cbs:
                if cb.text() == deck_shape:
                    cb.setChecked(True)
                    break

            base_dim_keys = ['base_width', 'base_length', 'base_height', 'base_depth']
            for key, widget in zip(base_dim_keys, self.base_dims):
                val = self.loaded_data.get(key, '')
                if val:
                    widget.setText(str(val))

            pillar_dim_keys = ['pillar_diameter_width', 'pillar_height', 'pillar_length']
            for key, widget in zip(pillar_dim_keys, self.pillar_dims):
                val = self.loaded_data.get(key, '')
                if val:
                    widget.setText(str(val))

            span_dim_keys = ['span_height', 'span_width', 'span_length', 'span_thickness']
            for key, widget in zip(span_dim_keys, self.span_dims):
                val = self.loaded_data.get(key, '')
                if val:
                    widget.setText(str(val))

            deck_dim_keys = ['deck_support_width', 'deck_support_height', 'deck_support_length']
            for key, widget in zip(deck_dim_keys, self.deck_dims):
                val = self.loaded_data.get(key, '')
                if val:
                    widget.setText(str(val))

            # Steel config population
            use_steel = self.loaded_data.get('use_steel_config', False)
            if use_steel:
                self.cb_steel_config.setChecked(True)
                self._on_steel_config_toggled(Qt.Checked)

                for comp_key in ["base", "pillar", "span", "deck_support"]:
                    steel_type = self.loaded_data.get(f"{comp_key}_steel_type", "")
                    grade = self.loaded_data.get(f"{comp_key}_steel_grade", "")

                    if steel_type and comp_key in self.steel_combos:
                        idx = self.steel_combos[comp_key].findText(steel_type)
                        if idx >= 0:
                            self.steel_combos[comp_key].setCurrentIndex(idx)

                    if grade and comp_key in self.grade_lines:
                        self.grade_lines[comp_key].setText(grade)

        except Exception as e:
            print(f"Error populating loaded data: {e}")


    def _update_pillar_sticker(self, text):
        """Update yellow sticker live as user types pillar name"""
        display_text = text.strip() or "P ?"
        self.pillar_sticker.setText(display_text)
        
        # Auto-adjust font size for longer names
        if len(display_text) > 6:
            self.pillar_sticker.setStyleSheet(
                self.pillar_sticker.styleSheet().replace("font-size: 32px", "font-size: 26px")
            )
        else:
            self.pillar_sticker.setStyleSheet(
                self.pillar_sticker.styleSheet().replace("font-size: 26px", "font-size: 32px")
            )

    def get_configuration(self):
        data = {"chainage": self.chainage_label}

        if self.rb_under.isChecked():
            data["bridge_type"] = "Under Pass"
            data.update({
                "underpass_width":  self.le_under_w.text().strip(),
                "underpass_height": self.le_under_h.text().strip(),
                "underpass_length": self.le_under_l.text().strip(),
            })
        elif self.rb_mini.isChecked():
            data["bridge_type"] = "Mini Bridge"
            data["mini_type"] = self.combo_mini.currentText().strip()
            data["support_count"] = self.le_supports.text().strip()
        elif self.rb_long.isChecked():
            data["bridge_type"] = "Long Bridge"
            data["long_type"] = self.combo_long.currentText().strip()
            data["support_count"] = self.le_supports.text().strip()

        for cb in [self.cb_over, self.cb_under, self.cb_land]:
            if cb.isChecked():
                data["location"] = cb.text()
                break

        shape_keys = ["base_shape", "pillar_shape", "span_shape", "deck_support_shape"]
        shape_groups = [self.base_cbs, self.pillar_cbs, self.span_cbs, self.deck_cbs]
        for key, group in zip(shape_keys, shape_groups):
            for cb in group:
                if cb.isChecked():
                    data[key] = cb.text()
                    break

        dim_keys = [
            ("base_width", "base_length", "base_height", "base_depth"),
            ("pillar_diameter_width", "pillar_height", "pillar_length"),
            ("span_height", "span_width", "span_length", "span_thickness"),
            ("deck_support_width", "deck_support_height", "deck_support_length")
        ]
        dim_groups = [self.base_dims, self.pillar_dims, self.span_dims, self.deck_dims]
        for keys, widgets in zip(dim_keys, dim_groups):
            for k, w in zip(keys, widgets):
                txt = w.text().strip()
                if txt:
                    data[k] = txt

        data["pillar_name"] = self.le_pillar_name.text().strip() or "P?"

        data["use_steel_config"] = self.cb_steel_config.isChecked()
        if self.cb_steel_config.isChecked():
            for comp_key in ["base", "pillar", "span", "deck_support"]:
                if comp_key in self.steel_combos:
                    data[f"{comp_key}_steel_type"] = self.steel_combos[comp_key].currentText().strip()
                if comp_key in self.grade_lines:
                    data[f"{comp_key}_steel_grade"] = self.grade_lines[comp_key].text().strip()

        return data
    

# ===========================================================================================================================
# ** MATERIAL LINE DIALOG ** (FINAL CORRECTED VERSION – ONLY SHOWS SELECTED BASELINES)
# ===========================================================================================================================
class MaterialLineDialog(QDialog):
    def __init__(self, material_data=None, construction_layer_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Material Line")
        self.setModal(True)
        self.setFixedSize(500, 500)

        self.construction_layer_path = construction_layer_path
        self.parent_app = parent
        self.material_data = material_data if material_data else {
            'name': '',
            'description': '',
            'material_type': '',  # Will hold the name
            'rmh_id': None,       # New field
            'ref_layer': 'None'
        }

        # Fetch materials from API
        try:
            from API import WorksheetAPI
            self.available_materials = WorksheetAPI.get_road_materials()
        except Exception as e:
            print(f"Error importing API or fetching materials: {e}")
            self.available_materials = []

        self.setup_ui()
        self.load_material_data()
        self.load_available_baselines()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Title
        title_label = QLabel("Material Line Configuration")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000; padding-bottom: 15px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Material Line Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Material Layer Name:")
        name_label.setFixedWidth(150)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Material Layer Name")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input, 1)
        layout.addLayout(name_layout)

        
        # =============== Aniket Pund - Added on 01-05-2025 (For the Road Resurfacing Functionality) =================
        # Road Resurfacing checkbox (initially unchecked)
        self.road_resurfacing_checkbox = QCheckBox("Road Resurfacing")
        self.road_resurfacing_checkbox.setStyleSheet("QCheckBox { font-weight: 500; font-size: 14px; font: bold; }")
        self.road_surfacing_checkbox = self.road_resurfacing_checkbox
        self.road_resurfacing_checkbox.setChecked(False)
        layout.addWidget(self.road_resurfacing_checkbox)
        # =========================================================================================================

    
        # Material Type
        # Material Type (Dropdown)
        type_layout = QHBoxLayout()
        type_label = QLabel("Material Name:")
        type_label.setFixedWidth(150)
        
        self.material_combo = QComboBox()
        self.material_combo.addItem("Select Material", None)
        
        # Populate dropdown
        if self.available_materials:
            for mat in self.available_materials:
                name = 'Unknown'
                rmh_id = None
                
                if isinstance(mat, dict):
                    name = mat.get('material_name', 'Unknown')
                    rmh_id = mat.get('rmh_id')
                    if rmh_id is None: rmh_id = mat.get('id')
                elif isinstance(mat, str):
                    name = mat
                    rmh_id = None  # Or try to look it up if possible, but string implies just name
                
                self.material_combo.addItem(name, rmh_id)
        else:
            self.material_combo.addItem("No materials found (check connection)", None)

        type_layout.addWidget(type_label)
        type_layout.addWidget(self.material_combo, 1)
        layout.addLayout(type_layout)

        layout.addSpacing(20)

        # Reference Baseline Section
        ref_label = QLabel("Reference Baseline")
        ref_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(ref_label)

        ref_layer_layout = QHBoxLayout()
        ref_layer_label = QLabel("Select Reference Baseline:")
        ref_layer_label.setFixedWidth(150)
        self.ref_layer_combo = QComboBox()
        self.ref_layer_combo.addItem("None")
        ref_layer_layout.addWidget(ref_layer_label)
        ref_layer_layout.addWidget(self.ref_layer_combo, 1)
        layout.addLayout(ref_layer_layout)

        layout.addStretch()

        # Save Button
        save_button = QPushButton("Save")
        save_button.setFixedSize(100, 35)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #005A9E; }
            QPushButton:pressed { background-color: #004578; }
        """)
        save_button.clicked.connect(self.on_save)
        layout.addWidget(save_button, alignment=Qt.AlignCenter)

    def on_save(self):
        material_name = self.name_input.text().strip()
        if not material_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a valid material line name.")
            return

        selected_material_idx = self.material_combo.currentIndex()
        if selected_material_idx <= 0: # 0 is "Select Material"
             QMessageBox.warning(self, "No Material", "Please select a material from the list.")
             return

        selected_baseline = self.ref_layer_combo.currentText()
        if selected_baseline == "None":
            QMessageBox.warning(self, "No Baseline", "Please select a reference baseline.")
            return

        # No folder creation, no file writing — just accept the dialog
        QMessageBox.information(self, "Success", f"Material line '{material_name}' configured successfully!")
        self.accept()  # This will make dialog.exec_() return QDialog.Accepted

    def load_available_baselines(self):
        """Load baselines from the unified design_construction_config.json file"""
        from json_manager import DesignConstructionManager
        
        self.ref_layer_combo.clear()
        self.ref_layer_combo.addItem("None")

        if not self.construction_layer_path or not os.path.exists(self.construction_layer_path):
            self.ref_layer_combo.addItem("Construction layer path not available")
            return

        config_path = os.path.join(self.construction_layer_path, "Construction_Layer_config.txt")
        if not os.path.exists(config_path):
            self.ref_layer_combo.addItem("Construction_Layer_config.txt not found")
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            reference_layer_2d = config.get("reference_layer_2d")

            if not reference_layer_2d:
                self.ref_layer_combo.addItem("No reference design layer defined")
                return

            worksheet_root = os.path.abspath(os.path.join(self.construction_layer_path, "..", ".."))
            designs_folder = os.path.join(worksheet_root, "designs")
            design_layer_path = os.path.join(designs_folder, reference_layer_2d)

            if not os.path.exists(design_layer_path):
                self.ref_layer_combo.addItem(f"Design layer folder not found: {reference_layer_2d}")
                return

            # Load ALL baselines from unified file
            all_baselines = DesignConstructionManager.load_all_baselines_from_unified(design_layer_path)
            
            # Map baseline keys to display names
            baseline_mapping = {
                'surface_baseline': 'Surface',
                'construction_baseline': 'Construction',
                'road_surface_baseline': 'Road Surface',
                'deck_line': 'Deck Line',
                'projection_line': 'Projection Line'
            }
            
            found_count = 0
            for baseline_key, display_name in baseline_mapping.items():
                if baseline_key in all_baselines and all_baselines[baseline_key]:
                    self.ref_layer_combo.addItem(display_name)
                    found_count += 1

            if found_count == 0:
                self.ref_layer_combo.addItem("Selected baselines not found in design layer")

        except Exception as e:
            self.ref_layer_combo.addItem(f"Error loading config: {str(e)}")

    def load_material_data(self):
        if not self.material_data:
            return
        self.name_input.setText(self.material_data.get('name', ''))
        
        # Set combo box based on existing material type or ID
        target_name = self.material_data.get('material_type', '')
        if target_name:
            index = self.material_combo.findText(target_name)
            if index >= 0:
                self.material_combo.setCurrentIndex(index)
        
        ref_layer = self.material_data.get('ref_layer', 'None')
        index = self.ref_layer_combo.findText(ref_layer)
        if index >= 0:
            self.ref_layer_combo.setCurrentIndex(index)

    def get_material_data(self):
        return {
            'name': self.name_input.text().strip(),
            'material_type': self.material_combo.currentText(),
            'rmh_id': self.material_combo.currentData(),
            'ref_layer': self.ref_layer_combo.currentText() if self.ref_layer_combo.currentText() != "None" else '',
            'road_resurfacing': self.road_resurfacing_checkbox.isChecked()
        }
# ==========================================================================================================================================
#                                                    ** MEASUREMENT DIALOG **
# ==========================================================================================================================================

class MeasurementNewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New Measurement Layer")
        self.setModal(True)
        self.setFixedWidth(500)  # Fixed width
        self.initial_height = 350  # Initial height without reference section
        self.expanded_height = 500  # Height with reference section
        
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f0e6fa, stop:1 #e6e6fa);
                border-radius: 18px;
            }
            QLabel {
                color: #2d1b3d;
                font-weight: 600;
                font-size: 13px;
            }
            QLineEdit {
                border: 2px solid #BA68C8;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #8E24AA;
                background-color: #F8E8FF;
            }
            QComboBox {
                border: 2px solid #BA68C8;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 2px solid #8E24AA;
                background-color: #F8E8FF;
            }
            QCheckBox {
                font-weight: 500;
                spacing: 8px;
                font-size: 13px;
            }
            QGroupBox {
                border: 2px solid #9C27B0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 8px;
                font-weight: bold;
                color: #4A148C;
                background-color: rgba(255, 255, 255, 0.4);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 10px;
                background-color: #E1BEE7;
                border-radius: 6px;
            }
            QPushButton {
                border-radius: 20px;
                padding: 11px;
                font-weight: bold;
                min-width: 100px;
                border: none;
            }
            QPushButton#saveBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #AB47BC, stop:1 #8E24AA);
                color: white;
            }
            QPushButton#saveBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #9C27B0, stop:1 #7B1FA2);
            }
            QPushButton#cancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333;
            }
            QPushButton#cancelBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #D1C4E9, stop:1 #BA68C8);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)  # Reduced spacing

        # Title - Simple centered label
        title = QLabel("Create New Measurement Layer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #4A148C; 
            padding: 8px 0;
        """)
        layout.addWidget(title)

        # Layer Name
        layer_name_label = QLabel("Enter Layer Name:")
        layer_name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(layer_name_label)
        
        self.layer_name_edit = QLineEdit()
        self.layer_name_edit.setPlaceholderText("Enter measurement layer name...")
        layout.addWidget(self.layer_name_edit)
        
        # Add some spacing
        layout.addSpacing(8)

        # Use Reference Layer Checkbox
        self.use_reference_checkbox = QCheckBox("Use Reference Layer")
        self.use_reference_checkbox.setChecked(False)
        layout.addWidget(self.use_reference_checkbox)

        # Reference Layer Configuration
        self.reference_widget = QDialog()  # Using QDialog as container
        reference_layout = QVBoxLayout(self.reference_widget)
        reference_layout.setContentsMargins(0, 0, 0, 0)
        reference_layout.setSpacing(8)
        
        # Design Layer Dropdown
        design_label = QLabel("Select Design Layer:")
        design_label.setStyleSheet("font-weight: bold;")
        reference_layout.addWidget(design_label)
        
        self.design_layer_combo = QComboBox()
        self.populate_design_layers()
        reference_layout.addWidget(self.design_layer_combo)
        
        # Reference Line Dropdown
        reference_line_label = QLabel("Select Reference Line:")
        reference_line_label.setStyleSheet("font-weight: bold;")
        reference_layout.addWidget(reference_line_label)
        
        self.reference_line_combo = QComboBox()
        self.reference_line_combo.addItems(["Road Surface Line", "Construction Line"])
        reference_layout.addWidget(self.reference_line_combo)
        
        # Add the reference widget to main layout
        layout.addWidget(self.reference_widget)
        self.reference_widget.setVisible(False)

        # Add some spacing
        layout.addSpacing(8)

        # === Point Cloud Selection ===
        pc_group = QGroupBox("Select Point Cloud File (optional)")
        pc_layout = QHBoxLayout(pc_group)
        self.pc_combo = QComboBox()
        self.pc_combo.addItem("No file selected")
        pc_layout.addWidget(QLabel("File:"))
        pc_layout.addWidget(self.pc_combo, 1)
        layout.addWidget(pc_group)
        self.load_files_from_project()

        # Add stretch to push buttons to bottom
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_save = QPushButton("Save")
        self.btn_save.setObjectName("saveBtn")
        self.btn_save.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("cancelBtn")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)

        # Set initial height
        self.setFixedHeight(self.initial_height)

        # Connect checkbox to show/hide reference widget
        self.use_reference_checkbox.stateChanged.connect(self.on_reference_checkbox_changed)

    def populate_design_layers(self):
        """Fetch all design layer folders from the current worksheet and populate the dropdown"""
        # Get the parent application to access the current worksheet path
        parent_app = self.parent()
        
        # Build the path dynamically based on the current worksheet
        if parent_app and hasattr(parent_app, 'current_worksheet_name') and hasattr(parent_app, 'WORKSHEETS_BASE_DIR'):
            designs_path = os.path.join(
                parent_app.WORKSHEETS_BASE_DIR, 
                parent_app.current_worksheet_name, 
                "designs"
            )
        else:
            # Fallback to the hardcoded path if parent info is not available
            designs_path = r"C:\3D_Tool\user\worksheets\Worksheet1\designs"
            print("Warning: Using fallback design path. Ensure a worksheet is active.")
        
        self.design_layer_combo.clear()
        self.design_layer_combo.addItem("-- Select a Design Layer --", None)
        
        try:
            if os.path.exists(designs_path):
                # Get all directories (design layer folders) in the designs folder
                for item in sorted(os.listdir(designs_path)):
                    item_path = os.path.join(designs_path, item)
                    if os.path.isdir(item_path):  # Only process folders, not files
                        # Look for a config file to get the proper layer name
                        config_path = os.path.join(item_path, "design_layer_config.txt")
                        display_name = item  # Default to folder name
                        
                        if os.path.exists(config_path):
                            try:
                                with open(config_path, 'r', encoding='utf-8') as f:
                                    config_data = json.load(f)
                                    # Use the 'layer_name' from config if available
                                    display_name = config_data.get('layer_name', item)
                            except:
                                pass  # Keep folder name if config read fails
                        
                        self.design_layer_combo.addItem(display_name, item_path)
                
                if self.design_layer_combo.count() <= 1:  # Only has the default "Select" item
                    self.design_layer_combo.addItem("No design layers found")
                    self.design_layer_combo.setEnabled(False)
            else:
                self.design_layer_combo.addItem(f"Designs path not found: {designs_path}")
                self.design_layer_combo.setEnabled(False)
        except Exception as e:
            print(f"Error loading design layers: {e}")
            self.design_layer_combo.addItem("Error loading design layers")
            self.design_layer_combo.setEnabled(False)

    def on_reference_checkbox_changed(self, state):
        """Handle checkbox state change to show/hide reference layer configuration"""
        if state == Qt.Checked:
            self.reference_widget.setVisible(True)
            self.setFixedHeight(self.expanded_height)
        else:
            self.reference_widget.setVisible(False)
            self.setFixedHeight(self.initial_height)
        
        # Update the layout
        self.layout().invalidate()
        self.updateGeometry()

    def load_files_from_project(self):
        """Load point cloud files from the selected project into the dropdown"""
        
        self.pc_combo.clear()
        self.pc_combo.addItem("No file selected")
        parent_app = self.parent()
        project_name = getattr(parent_app, 'current_project_name', "None")

        project_folder = os.path.join(r"C:\3D_Tool\projects", project_name)
        config_path = os.path.join(project_folder, "project_config.txt")

        if not os.path.exists(config_path):
            self.pc_combo.clear()
            self.pc_combo.addItem("Project not found")
            self.pc_combo.setEnabled(False)
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            files = data.get("pointcloud_files", [])
            if not files:
                self.pc_combo.clear()
                self.pc_combo.addItem("No point cloud files linked to the Project")
                self.pc_combo.setEnabled(False)
            else:
                for f in files:
                    self.pc_combo.addItem(os.path.basename(f), f)
                self.pc_combo.setEnabled(True)
        except Exception as e:
            self.pc_combo.addItem(f"Error reading config: {e}")
            self.pc_combo.setEnabled(False)
    def get_data(self):
        """Return all measurement layer data as a dict"""
        data = {
            "layer_name": self.layer_name_edit.text(),
            "use_reference": self.use_reference_checkbox.isChecked(),
        }
        
        if self.use_reference_checkbox.isChecked():
            data.update({
                "design_layer": self.design_layer_combo.currentText(),
                "design_layer_file": self.design_layer_combo.currentData(),
                "reference_line": self.reference_line_combo.currentText()
            })
        else:
            data.update({
                "design_layer": None,
                "design_layer_file": None,
                "reference_line": None
            })

        return data
    

# ===========================================================================================================================
# DESIGN NEW LAYER DIALOG – With Dynamic Dropdown Based on Road/Bridge Selection + NO OVERWRITE
# ===========================================================================================================================
class DesignNewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Design Layer")
        self.setModal(True)
        self.setMinimumWidth(440)
        self.parent = parent  # To access base directories and current worksheet
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f0e6fa, stop:1 #e6e6fa);
                border-radius: 18px;
            }
            QLabel {
                color: #2d1b3d;
                font-weight: 600;
                font-size: 13px;
            }
            QGroupBox {
                border: 2px solid #9C27B0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 8px;
                font-weight: bold;
                color: #4A148C;
                background-color: rgba(255, 255, 255, 0.4);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 10px;
                background-color: #E1BEE7;
                border-radius: 6px;
            }
            QRadioButton, QCheckBox {
                font-weight: 500;
                spacing: 8px;
                font-size: 13px;
            }
            QComboBox {
                border: 2px solid #BA68C8;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 2px solid #8E24AA;
                background-color: #F8E8FF;
            }
            QLineEdit {
                border: 2px solid #BA68C8;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #8E24AA;
                background-color: #F8E8FF;
            }
            QPushButton {
                border-radius: 20px;
                padding: 11px;
                font-weight: bold;
                min-width: 100px;
                border: none;
            }
            QPushButton#okBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #AB47BC, stop:1 #8E24AA);
                color: white;
            }
            QPushButton#okBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #9C27B0, stop:1 #7B1FA2);
            }
            QPushButton#cancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333;
            }
            QPushButton#cancelBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #D1C4E9, stop:1 #BA68C8);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        # Title
        title = QLabel("Create New Design Layer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A148C; padding: 10px;")
        layout.addWidget(title)

        # ------------------ Layer Name -----------------
        layer_name_label = QLabel("Layer Name:")
        layer_name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(layer_name_label)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter unique layer name (required)")
        layout.addWidget(self.name_edit)
    
    # ==== Aniket Added for the simulation purpose ===========
        # === Master Layer Checkbox ===
        self.cb_master = QCheckBox("Master layer")
        self.cb_master.setStyleSheet("margin-top: 5px;")
        layout.addWidget(self.cb_master)
    # ==========================================================
    
        # === Layer Dimension (3D / 2D) ===
        dim_group = QGroupBox("Layer Type")
        dim_layout = QVBoxLayout(dim_group)
        self.radio_3d = QRadioButton("3D")
        self.radio_2d = QRadioButton("2D")
        # Default to 2D and hide/disable 3D option
        self.radio_2d.setChecked(True)
        self.radio_3d.setVisible(False)
        dim_layout.addWidget(self.radio_3d)
        dim_layout.addWidget(self.radio_2d)
        layout.addWidget(dim_group)

        # === Road checkbox (application is road-only) ===
        self.cb_road = QCheckBox("Road")
        self.cb_road.setChecked(True)
        self.cb_road.stateChanged.connect(lambda s: self.update_reference_dropdown())
        layout.addWidget(self.cb_road)
        
        # === Create mode ===
        mode_group = QGroupBox("Create Mode")
        mode_layout = QVBoxLayout(mode_group)
        self.mode_design_radio = QRadioButton("Design")
        self.mode_design_with_material_radio = QRadioButton("Design with Material")
        self.mode_design_radio.setChecked(True)
        mode_layout.addWidget(self.mode_design_radio)
        mode_layout.addWidget(self.mode_design_with_material_radio)
        layout.addWidget(mode_group)

        # === Reference Layer Dropdown (Dynamic) ===
        # Commented out per request — hide reference-type dropdown
        # self.ref_layer_group = QGroupBox("Reference Layer")
        # ref_layer_layout = QVBoxLayout(self.ref_layer_group)
        # self.combo_reference = QComboBox()
        # self.combo_reference.setEnabled(False)
        # ref_layer_layout.addWidget(QLabel("Select reference Layer 2D:"))
        # ref_layer_layout.addWidget(self.combo_reference)
        # layout.addWidget(self.ref_layer_group)
        # self.ref_layer_group.setVisible(True)
        # self.update_reference_dropdown()

        # Connect dimension change
        self.radio_3d.toggled.connect(self.on_dimension_changed)
        self.radio_2d.toggled.connect(self.on_dimension_changed)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("okBtn")
        ok_btn.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(ok_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    # def on_dimension_changed(self, checked):
    #     if not checked:
    #         return
    #     self.ref_layer_group.setVisible(self.radio_3d.isChecked())
    #     self.update_reference_dropdown()


    def on_dimension_changed(self, checked):
        if not checked:
            return
        
        if self.radio_3d.isChecked():
            self.ref_layer_group.setVisible(True)
            self.ref_layer_group.setMaximumHeight(16777215)
            # Restore normal spacing
            self.layout().setSpacing(18)
        else:
            self.ref_layer_group.setVisible(False)
            self.ref_layer_group.setMaximumHeight(0)
            # Reduce spacing since we're hiding a section
            self.layout().setSpacing(12)  # Reduced spacing
        
        self.update_reference_dropdown()
        self.adjustSize()


    def update_reference_dropdown(self):
        # Reference dropdown is commented out; no-op
        return

    def validate_and_accept(self):
        layer_name = self.name_edit.text().strip()
        if not layer_name:
            QMessageBox.warning(self, "Input Required", "Layer name is required!")
            return

        # === Check if layer already exists in current worksheet ===
        if not hasattr(self.parent, 'current_worksheet_name') or not self.parent.current_worksheet_name:
            QMessageBox.warning(self, "No Worksheet", "No active worksheet found.")
            return

        base_designs_path = os.path.join(self.parent.WORKSHEETS_BASE_DIR, self.parent.current_worksheet_name, "designs")
        layer_folder = os.path.join(base_designs_path, layer_name)

        if os.path.exists(layer_folder):
            QMessageBox.warning(self, "Name Exists",
                                "A design layer with this name already exists.\n"
                                "Please enter a different name.")
            return  # Do NOT accept — user must change name

        # If all good, call Mode 2 API to create design layer on server, then accept
        try:
            from API import WorksheetAPI
            import json as _json

            parent = getattr(self, 'parent', None)
            user_id = None
            worksheet_id = None
            if parent:
                user_id = getattr(parent, 'current_user_id', None) or getattr(parent, 'current_user', None) or getattr(parent, 'api_user_id', None)
                worksheet_id = getattr(parent, 'current_worksheet_id', None) or (getattr(parent, 'current_worksheet_data', {}) or {}).get('id') or getattr(parent, 'created_worksheet_id', None)

            dimension = "3D" if self.radio_3d.isChecked() else "2D"
            reference_type = "Road" if self.cb_road.isChecked() else None
            project_name = getattr(parent, 'current_project_name', "None") if parent else "None"
            worksheet_name = getattr(parent, 'current_worksheet_name', "Unknown") if parent else "Unknown"
            
            point_cloud_file = ""
            if parent and hasattr(parent, 'current_worksheet_data') and isinstance(parent.current_worksheet_data, dict):
                config = parent.current_worksheet_data.get("worksheet_config_data", {})
                if isinstance(config, str):
                    try:
                        import json as _j
                        config = _j.loads(config)
                    except:
                        config = {}
                point_cloud_file = config.get("point_cloud_file", "")

            layer_config_data = {
                "layer_name": layer_name,
                "dimension": dimension,
                "reference_type": reference_type or "Road",
                "reference_line": "",
                "master_layer": bool(self.cb_master.isChecked()), # ========= Aniket added 02-05-2026
                "project_name": project_name,
                "worksheet_name": worksheet_name,
                "point_cloud_file": point_cloud_file,
                "created_by": getattr(parent, 'current_user_full_name', getattr(parent, 'current_user', "Unknown")) if parent else "Unknown",
                "created_at": datetime.now().isoformat()
            }

            payload = {
                "mode": 2,
                "user_id": int(user_id) if user_id is not None and str(user_id).isdigit() else user_id,
                "worksheet_id": str(worksheet_id) if worksheet_id is not None else worksheet_id,
                "layer_name": layer_name,
                "construction_type": 1,
                "is_2d": 1,
                "type_2d": 1,
                "is_3d": 0,
                "type_3d": 0,
                "file_path": "",
                "layer_config_data": layer_config_data,
                "layer_json_data": {}
            }

            # Debug: print payload to stdout
            try:
                print('\n=== MODE 2 PAYLOAD ===')
                print(_json.dumps(payload, indent=2, default=str))
            except Exception:
                print('MODE2 PAYLOAD:', payload)

            # Append payload to UI message area if available
            if parent and hasattr(parent, 'message_text'):
                try:
                    parent.message_text.append('MODE2 PAYLOAD: ' + _json.dumps(payload, ensure_ascii=False))
                except Exception:
                    try:
                        parent.message_text.append('MODE2 PAYLOAD: ' + str(payload))
                    except:
                        pass

            resp = WorksheetAPI.create_worksheet(payload)

            # Debug: print full response to stdout
            try:
                print('\n=== MODE 2 RESPONSE ===')
                print(_json.dumps(resp, indent=2, default=str))
            except Exception:
                print('MODE2 RESPONSE:', resp)

            # Log into parent message area if available
            if parent and hasattr(parent, 'message_text'):
                try:
                    parent.message_text.append('MODE2 RESPONSE: ' + (_json.dumps(resp, ensure_ascii=False) if isinstance(resp, dict) else str(resp)))
                except Exception:
                    try:
                        parent.message_text.append('MODE2 RESPONSE: ' + str(resp))
                    except:
                        pass

            # Evaluate success and show user-facing dialog
            success = False
            resp_text = ''
            status_code = None
            if isinstance(resp, dict):
                success = bool(resp.get('success'))
                status_code = resp.get('status_code') or resp.get('status')
                resp_text = resp.get('text') or resp.get('message') or str(resp.get('data') or '')
            else:
                success = bool(resp)
                resp_text = str(resp)

            if success:
                msg = f"Mode 2 request completed. status={status_code or ''}"
                try:
                    if parent and hasattr(parent, 'message_text'):
                        parent.message_text.append(msg)
                except:
                    pass
                QMessageBox.information(self, 'Server', msg)
            else:
                msg = resp_text or 'Unknown error'
                try:
                    if parent and hasattr(parent, 'message_text'):
                        parent.message_text.append('Mode2 error: ' + str(msg))
                except:
                    pass
                QMessageBox.warning(self, 'Server Error', f'Failed to create design layer on server:\n{msg}')

        except Exception as e:
            try:
                print('Mode 2 API call exception:', e)
            except:
                pass
            if getattr(self, 'parent', None) and hasattr(self.parent, 'message_text'):
                try:
                    self.parent.message_text.append(f'Mode 2 API call failed: {e}')
                except:
                    pass
            QMessageBox.warning(self, 'API Error', f'Mode 2 API call failed: {e}')

        # Accept dialog after API call
        self.accept()

    def get_configuration(self):
        layer_name = self.name_edit.text().strip()
        reference_type = None
        reference_line = None
        if self.radio_3d.isChecked():
            if self.cb_road.isChecked():
                reference_type = "Road"
                reference_line = None
        else:
            if self.cb_road.isChecked():
                reference_type = "Road"

        return {
            "layer_name": layer_name,
            "dimension": "3D" if self.radio_3d.isChecked() else "2D",
            "reference_type": reference_type,
            "reference_line": reference_line,
            "master_layer": bool(self.cb_master.isChecked()),
            "creation_mode": "design_with_material" if self.mode_design_with_material_radio.isChecked() else "design"
        }

# ===========================================================================================================================
#                                                ** HELP Dialog Box **
# ===========================================================================================================================
class DownloadThread(QThread):
    finished_signal = pyqtSignal(bool, str)
    progress_signal = pyqtSignal(int)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        def progress_clbk(percent):
            self.progress_signal.emit(percent)
            
        result = WorksheetAPI.download_file_by_url(self.url, self.save_path, progress_callback=progress_clbk)
        self.finished_signal.emit(result["success"], result["message"])

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help")
        self.setModal(True)
        self.resize(600, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>Point Cloud Viewer - Help</h2>
        <p>Welcome to the Point Cloud Viewer application. This tool allows you to visualize and analyze 3D point cloud data.</p>
        <h3>Features:</h3>
        <ul>
            <li>Load and display point cloud files in various formats.</li>
            <li>Measure distances, areas, and volumes within the point cloud.</li>
            <li>Create and manage design layers for construction projects.</li>
            <li>Generate worksheets to document measurements and designs.</li>
        </ul>
        <h3>Getting Started:</h3>
        <ol>
            <li>Use the 'File' menu to load a point cloud file.</li>
            <li>Navigate the 3D view using mouse controls (rotate, pan, zoom).</li>
            <li>Select measurement tools from the toolbar to start measuring.</li>
            <li>Create new design layers using the 'Design' menu.</li>
            <li>Generate worksheets from the 'Worksheet' menu.</li>
        </ol>
        <h3>Support:</h3>
        <p>If you encounter any issues or have questions, please contact our support team at
        <a href="mailto:
                          """)
        #help_text.setOpenExternalLinks(True)
        layout.addWidget(help_text)
        support_email = "info@microintegrated.in"
        help_text.append("{}.".format(support_email))

        # Close Button
        close_button = QPushButton("Close")
        close_button.setFixedSize(100, 35)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #005A9E; }
            QPushButton:pressed { background-color: #004578; }
        """)
        close_button.clicked.connect(self.accept)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)


# ===========================================================================================================================
# FINAL UPDATED: Construction Layer Creation Dialog (Multiple Baseline Selection + Preview)
# ===========================================================================================================================
class ConstructionNewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Material Layer")
        self.setFixedSize(380, 500)
        self.parent = parent
       
        self.current_worksheet_path = None

        # Initialize preview-related attributes EARLY to avoid AttributeError
        self.preview_artists = []  # Temporary artists for live preview
        self.selected_baseline_data = []  # List of (data_dict, color, baseline_key, filename)
        self.preview_colors = ["gray", "blue", "green", "orange", "purple", "brown", "pink", "olive", "cyan"]

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; }
            QLineEdit {
                padding: 8px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
            }
            QRadioButton { font-size: 13px; spacing: 8px; }
            QPushButton {
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 90px;
            }
            QListWidget {
                border: 2px solid #BBB;
                border-radius: 6px;
                padding: 5px;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Create New Material Layer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A148C;")
        layout.addWidget(title)
        
        # Layer Name
        layout.addWidget(QLabel("Layer Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter layer name")
        layout.addWidget(self.name_edit)
        
        # Type Selection
        type_group = QGroupBox("Type")
        type_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        type_layout = QHBoxLayout()
        self.road_radio = QRadioButton("Road")
        # self.bridge_radio = QRadioButton("Bridge")
        self.road_radio.setChecked(True)
        type_layout.addWidget(self.road_radio)
        # type_layout.addWidget(self.bridge_radio)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Reference Layer Dropdown
        layout.addWidget(QLabel("Reference Layer of 2D design Layer:"))
        self.ref_layer_combo = QComboBox()
        self.ref_layer_combo.setEditable(False)
        layout.addWidget(self.ref_layer_combo)
        
        # Base Lines - Multi-Select List
        layout.addWidget(QLabel("2D Layer refer to Base lines (select one or more):"))
        self.base_lines_list = QListWidget()
        self.base_lines_list.setSelectionMode(QListWidget.MultiSelection)
        self.base_lines_list.setMinimumHeight(120)
        layout.addWidget(self.base_lines_list)
        
        # Initial load
        self.load_design_layers()
        
        # Connect signals
        self.ref_layer_combo.currentIndexChanged.connect(self.on_reference_layer_changed)
        self.base_lines_list.itemSelectionChanged.connect(self.on_baseline_selection_changed)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet("background-color:#7B1FA2;color:white;")
        self.ok_button.clicked.connect(self.validate_and_accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("background-color:#B0BEC5;color:#333;")
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)

    def set_current_worksheet_path(self, path):
        self.current_worksheet_path = path
        self.load_design_layers()

    def get_designs_path(self):
        if not self.current_worksheet_path:
            return None
        return os.path.join(self.current_worksheet_path, "designs")
    
    def load_design_layers(self):
        self.ref_layer_combo.clear()
        self.ref_layer_combo.addItem("None")
        designs_path = self.get_designs_path()
        if not designs_path or not os.path.exists(designs_path):
            self.ref_layer_combo.addItem("(No designs folder)")
            self.on_reference_layer_changed()
            return
        try:
            folders = [name for name in os.listdir(designs_path)
                       if os.path.isdir(os.path.join(designs_path, name))]
            folders.sort()
            if folders:
                self.ref_layer_combo.addItems(folders)
            else:
                self.ref_layer_combo.addItem("(No design layers found)")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load design layers:\n{e}")
        self.on_reference_layer_changed()
    
    def get_json_baselines_in_layer(self, design_layer_name):
        """Load baseline names from the unified design_construction_config.json file."""
        from json_manager import DesignConstructionManager
        
        if not design_layer_name or design_layer_name in ("None", "(No designs folder)", "(No design layers found)"):
            return []
        designs_path = self.get_designs_path()
        if not designs_path:
            return []
        layer_path = os.path.join(designs_path, design_layer_name)
        if not os.path.exists(layer_path):
            return []
        try:
            # Load all baselines from unified file
            all_baselines = DesignConstructionManager.load_all_baselines_from_unified(layer_path)
            
            # Extract baseline names
            baseline_keys = ['surface_baseline', 'construction_baseline', 'road_surface_baseline', 'deck_line', 'projection_line']
            baseline_names = []
            
            for key in baseline_keys:
                if key in all_baselines and all_baselines[key]:
                    # Convert to display name (e.g., 'surface_baseline' -> 'Surface')
                    display_name = key.replace('_baseline', '').replace('_', ' ').title()
                    baseline_names.append((key, display_name, all_baselines[key]))
            
            return baseline_names
        except Exception as e:
            print(f"Error loading baselines from unified file: {e}")
            return []

    def on_reference_layer_changed(self):
        ref_layer = self.ref_layer_combo.currentText()
        baselines = self.get_json_baselines_in_layer(ref_layer)
        
        self.base_lines_list.clear()
        self.baseline_lookup = {}  # Store lookup for selected baselines
        
        if baselines:
            for key, display_name, data in baselines:
                self.base_lines_list.addItem(display_name)
                self.baseline_lookup[display_name] = (key, data)
        else:
            self.base_lines_list.addItem("(No baselines found)")

        # Clear any existing preview
        self.clear_preview_lines()
        self.selected_baseline_data.clear()

    def clear_preview_lines(self):
        for artist in self.preview_artists:
            try:
                artist.remove()
            except:
                pass
        self.preview_artists.clear()
        if hasattr(self.parent, 'canvas'):
            self.parent.canvas.draw_idle()

    def on_baseline_selection_changed(self):
        self.clear_preview_lines()
        self.selected_baseline_data.clear()

        selected_items = self.base_lines_list.selectedItems()
        if not selected_items:
            self.parent.message_text.append("No baselines selected for preview.")
            return

        color_idx = 0
        for item in selected_items:
            display_name = item.text()
            if display_name.startswith("("):  # Skip placeholder items
                continue
            
            # Get baseline data from lookup
            if not hasattr(self, 'baseline_lookup'):
                continue
            
            if display_name not in self.baseline_lookup:
                continue
            
            baseline_key, data = self.baseline_lookup[display_name]
            
            if not data:
                continue

            try:
                color = data.get("color", self.preview_colors[color_idx % len(self.preview_colors)])
                baseline_type = data.get("baseline_type", display_name)

                # Store for later use (on OK)
                self.selected_baseline_data.append((data, color, baseline_key, display_name))

                # Plot dotted preview
                all_x = []
                all_y = []
                for poly in data.get("polylines", []):
                    poly_x = [pt["chainage_m"] for pt in poly.get("points", [])]
                    poly_y = [pt["relative_elevation_m"] for pt in poly.get("points", [])]
                    if poly_x:
                        all_x.extend(poly_x)
                        all_y.extend(poly_y)

                if all_x:
                    artist, = self.parent.ax.plot(
                        all_x, all_y,
                        color=color,
                        linestyle=':',
                        linewidth=3,
                        alpha=0.8,
                        label=f"Ref: {baseline_type}",
                        zorder=5
                    )
                    self.preview_artists.append(artist)

                color_idx += 1

            except Exception as e:
                QMessageBox.warning(self, "Load Error", f"Failed to load {display_name}:\n{str(e)}")

        self.parent.canvas.draw_idle()
        self.parent.message_text.append(f"Preview: {len(selected_items)} baseline(s) selected (dotted lines)")

    def validate_and_accept(self):
        from json_manager import DesignConstructionManager
        
        layer_name = self.name_edit.text().strip()
        if not layer_name:
            QMessageBox.warning(self, "Input Required", "Please enter a layer name.")
            return

        construction_base = os.path.join(r"C:\3D_Tool\user\worksheets", self.parent.current_worksheet_name, "construction")
        if os.path.exists(os.path.join(construction_base, layer_name)):
            QMessageBox.warning(self, "Name Exists",
                                "A construction layer with this name already exists.\nPlease enter another name.")
            return

        # Clear standard baseline types
        baseline_types_to_clear = [
            'surface', 'construction', 'road_surface',
            'deck_line', 'projection_line', 'material'
        ]
        for ltype in baseline_types_to_clear:
            if ltype in self.parent.line_types:
                for artist in self.parent.line_types[ltype]['artists']:
                    try:
                        artist.remove()
                    except:
                        pass
                self.parent.line_types[ltype]['artists'].clear()
                self.parent.line_types[ltype]['polylines'].clear()

        # Re-plot ALL selected reference baselines permanently (dotted)
        self.clear_preview_lines()  # Remove temporary ones
        for data, color, baseline_key, display_name in self.selected_baseline_data:
            if baseline_key not in self.parent.line_types:
                self.parent.line_types[baseline_key] = {'color': color, 'polylines': [], 'artists': []}

            # Clear any old
            for artist in self.parent.line_types[baseline_key]['artists']:
                try:
                    artist.remove()
                except:
                    pass
            self.parent.line_types[baseline_key]['artists'].clear()
            self.parent.line_types[baseline_key]['polylines'].clear()

            all_x = []
            all_y = []
            for poly in data.get("polylines", []):
                poly_x = [pt["chainage_m"] for pt in poly.get("points", [])]
                poly_y = [pt["relative_elevation_m"] for pt in poly.get("points", [])]
                if poly_x:
                    all_x.extend(poly_x)
                    all_y.extend(poly_y)
                    self.parent.line_types[baseline_key]['polylines'].append(list(zip(poly_x, poly_y)))

            if all_x:
                ref_artist, = self.parent.ax.plot(
                    all_x, all_y,
                    color=color,
                    linestyle=':',
                    linewidth=3,
                    alpha=0.8,
                    zorder=5
                )
                self.parent.line_types[baseline_key]['artists'].append(ref_artist)

        self.parent.canvas.draw_idle()

        # Create 3D base plane from FIRST selected baseline (if any)
        if self.selected_baseline_data:
            first_data = self.selected_baseline_data[0][0]
            width = float(first_data.get("width_meters", 10.0))
            half_width = width / 2.0

            if not hasattr(self.parent, 'construction_base_actors'):
                self.parent.construction_base_actors = []
            for actor in self.parent.construction_base_actors:
                self.parent.renderer.RemoveActor(actor)
            self.parent.construction_base_actors.clear()

            # Load zero line data from the unified file
            ref_layer = self.ref_layer_combo.currentText()
            designs_path = self.get_designs_path()
            if designs_path:
                layer_path = os.path.join(designs_path, ref_layer)
                try:
                    # Load all baselines from unified file to get zero_line_config
                    all_baselines = DesignConstructionManager.load_all_baselines_from_unified(layer_path)
                    zero_config = all_baselines.get("zero_line_config", {})
                    
                    # Extract zero line points
                    point1 = zero_config.get("point1", {})
                    point2 = zero_config.get("point2", {})
                    zero_start = np.array(point1.get("coordinates", [0, 0, 0]), dtype=float)
                    zero_end = np.array(point2.get("coordinates", [0, 0, 0]), dtype=float)
                    ref_z = float(zero_config.get("reference_elevation_z", 0.0))
                except Exception as e:
                    self.parent.message_text.append(f"Warning: Could not load zero line config: {e}")
                    # Fallback to defaults
                    zero_start = np.array([0, 0, 0], dtype=float)
                    zero_end = np.array([100, 0, 0], dtype=float)
                    ref_z = 0.0
            else:
                zero_start = np.array([0, 0, 0], dtype=float)
                zero_end = np.array([100, 0, 0], dtype=float)
                ref_z = 0.0

            zero_dir_vec = zero_end - zero_start
            zero_length = np.linalg.norm(zero_dir_vec)
            if zero_length < 1e-6:
                zero_length = 100.0  # Fallback

            ltype = self.selected_baseline_data[0][2]
            plane_colors = {
                'surface': (0.0, 0.8, 0.0, 0.4),
                'construction': (1.0, 0.0, 0.0, 0.4),
                'road_surface': (0.0, 0.6, 1.0, 0.45),
                'deck_line': (1.0, 0.5, 0.0, 0.4),
                'projection_line': (0.5, 0.0, 0.5, 0.4),
                'material': (1.0, 1.0, 0.0, 0.4),
            }
            rgba = plane_colors.get(ltype, (0.5, 0.5, 0.5, 0.4))
            color_rgb = rgba[:3]
            opacity = rgba[3]

            for poly in first_data.get("polylines", []):
                points_2d = poly.get("points", [])
                if len(points_2d) < 2:
                    continue

                for i in range(len(points_2d) - 1):
                    pt1 = points_2d[i]
                    pt2 = points_2d[i + 1]

                    dist1 = pt1["chainage_m"]
                    dist2 = pt2["chainage_m"]
                    rel_z1 = pt1["relative_elevation_m"]
                    rel_z2 = pt2["relative_elevation_m"]

                    pos1 = zero_start + (dist1 / zero_length) * zero_dir_vec
                    pos2 = zero_start + (dist2 / zero_length) * zero_dir_vec

                    center1 = np.array([pos1[0], pos1[1], ref_z + rel_z1])
                    center2 = np.array([pos2[0], pos2[1], ref_z + rel_z2])

                    seg_dir = center2 - center1
                    seg_len = np.linalg.norm(seg_dir)
                    if seg_len < 1e-6:
                        continue
                    seg_unit = seg_dir / seg_len

                    horiz = np.array([seg_unit[0], seg_unit[1], 0.0])
                    hlen = np.linalg.norm(horiz)
                    if hlen < 1e-6:
                        zero_unit = zero_dir_vec / zero_length
                        perp = np.array([-zero_unit[1], zero_unit[0], 0.0])
                    else:
                        horiz /= hlen
                        perp = np.array([-horiz[1], horiz[0], 0.0])

                    perp_len = np.linalg.norm(perp)
                    if perp_len > 0:
                        perp /= perp_len

                    c1 = center1 + perp * half_width
                    c2 = center1 - perp * half_width
                    c3 = center2 - perp * half_width
                    c4 = center2 + perp * half_width

                    plane = vtkPlaneSource()
                    plane.SetOrigin(c1[0], c1[1], c1[2])
                    plane.SetPoint1(c4[0], c4[1], c4[2])
                    plane.SetPoint2(c2[0], c2[1], c2[2])
                    plane.SetXResolution(12)
                    plane.SetYResolution(2)
                    plane.Update()

                    mapper = vtkPolyDataMapper()
                    mapper.SetInputConnection(plane.GetOutputPort())

                    actor = vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(*color_rgb)
                    actor.GetProperty().SetOpacity(opacity)
                    actor.GetProperty().EdgeVisibilityOn()
                    actor.GetProperty().SetEdgeColor(*color_rgb)
                    actor.GetProperty().SetLineWidth(1.5)

                    self.parent.renderer.AddActor(actor)
                    self.parent.construction_base_actors.append(actor)

            self.parent.vtk_widget.GetRenderWindow().Render()
            self.parent.message_text.append(f"Base plane created from first selected baseline (width: {width:.2f}m)")

    # =============================== API Payload of Material Layer Creation (Mode 3) ===============================
        # Send Mode 3 API call to create a material layer on server using this dialog's layer name
        try:
            from API import WorksheetAPI
            import json

            parent = getattr(self, 'parent', None)
            user_id = None
            worksheet_id = None
            design_layer_id = None
            if parent:
                user_id = getattr(parent, 'current_user_id', None) or getattr(parent, 'current_user', None) or getattr(parent, 'api_user_id', None)
                worksheet_id = getattr(parent, 'current_worksheet_id', None) or (getattr(parent, 'current_worksheet_data', {}) or {}).get('id') or getattr(parent, 'created_worksheet_id', None)
                design_layer_id = getattr(parent, 'current_layer_id', None)

            reference_layer_2d = self.ref_layer_combo.currentText()
            if reference_layer_2d in ("None", "(No designs folder)", "(No design layers found)"):
                reference_layer_2d = None

            selected_baselines = [
                item.text() for item in self.base_lines_list.selectedItems()
                if not item.text().startswith("(")
            ]

            layer_config_data = {
                "construction_layer_name": layer_name,
                "worksheet_name": getattr(parent, 'current_worksheet_name', "Unknown") if parent else "Unknown",
                "project_name": getattr(parent, 'current_project_name', "None") if parent else "None",
                "worksheet_type": "Design",
                "worksheet_category": "Road",
                "construction_type": "Road" if self.road_radio.isChecked() else "Bridge",
                "reference_layer_2d": reference_layer_2d,
                "design_layer_name": reference_layer_2d,
                "base_lines_reference": selected_baselines,
                "created_at": datetime.now().isoformat(),
                "created_by": getattr(parent, 'current_user_full_name', getattr(parent, 'current_user', "Unknown")) if parent else "Unknown",
                "material_lines": []
            }

            payload = {
                "mode": 3,
                "user_id": int(user_id) if user_id is not None and str(user_id).isdigit() else user_id,
                "worksheet_id": str(worksheet_id) if worksheet_id is not None else worksheet_id,
                "design_layer_id": str(design_layer_id) if design_layer_id is not None else design_layer_id,
                "material_layer_name": layer_name,
                "layer_config_data": layer_config_data,
                "layer_json_data": {}
            }

            resp = WorksheetAPI.create_worksheet(payload)
            
            if resp.get('success'):
                # Print payload
                print("\n=== MODE 3 PAYLOAD (SUCCESSFUL) ===")
                print(json.dumps(payload, indent=4, default=str))
                print("===================================\n")
                
                # Print API response
                print("\n=== MODE 3 API RESPONSE (SUCCESSFUL) ===")
                print(json.dumps(resp, indent=4, default=str))
                print("========================================\n")
                
                # ✅ Extract and store the material layer ID
                material_layer_id = None
                if 'data' in resp and 'layer_id' in resp['data']:
                    material_layer_id = resp['data']['layer_id']
                elif 'layer_id' in resp:
                    material_layer_id = resp['layer_id']
                
                if material_layer_id:
                    # Store in parent (main window) for later use in upload
                    parent.current_material_layer_id = material_layer_id
                    self.parent.message_text.append(f"Mode 3: Material layer created with ID {material_layer_id}")
                else:
                    self.parent.message_text.append("Mode 3: Success but no layer_id in response")
                
                self.parent.message_text.append("Mode 3: material layer creation request sent to server")
            else:
                msg = resp.get('message') or resp.get('text') or str(resp)
                QMessageBox.warning(self, "Server Error", f"Failed to create material layer on server:\n{msg}")
        except Exception as e:
            self.parent.message_text.append(f"Mode 3 API call failed: {e}")
    
    # ===========================================================================================================================================================================================================
        self.accept()
    
    def get_data(self):
        ref_layer = self.ref_layer_combo.currentText()
        selected_baselines = [
            item.text() for item in self.base_lines_list.selectedItems()
            if not item.text().startswith("(")
        ]
        
        return {
            'layer_name': self.name_edit.text().strip(),
            'is_road': self.road_radio.isChecked(),
            # 'is_bridge': self.bridge_radio.isChecked(),
            'reference_layer': None if ref_layer in ("None", "(No designs folder)", "(No design layers found)") else ref_layer,
            'base_lines_layer': selected_baselines  # List of selected JSON files
        }

# ===========================================================================================================================
# ** CREATE PROJECT DIALOG - IMPROVED VERSION (Supports File + Folder Selection) **
# ===========================================================================================================================

class CreateProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setFixedWidth(500)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #E8DAF8, stop:1 #D7B8F3);
                border: 1px solid #BB86FC;
                border-radius: 12px;
            }
            QLabel {
                color: #4A148C;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
            }
            QLabel[accessibleName="title"] {
                font-size: 20px;
                font-weight: bold;
                color: #4A148C;
                margin: 10px;
            }
            QLineEdit, QComboBox {
                padding: 10px;
                border: 2px solid #CF9FFF;
                border-radius: 10px;
                background-color: white;
                font-size: 14px;
                color: #333;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #9C27B0;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QTextEdit {
                padding: 12px;
                border: 2px solid #CF9FFF;
                border-radius: 10px;
                background-color: white;
                font-size: 13px;
                color: #555;
            }
            QPushButton {
                padding: 12px 20px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton#okBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #AB47BC, stop:1 #8E24AA);
                color: white;
                border: none;
            }
            QPushButton#okBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #9C27B0, stop:1 #7B1FA2);
            }
            QPushButton#cancelBtn {
                background-color: #E0C3FC;
                color: #4A148C;
                border: 2px solid #CF9FFF;
            }
            QPushButton#cancelBtn:hover {
                background-color: #D8B8F8;
            }
            QPushButton#browseFileBtn {
                background-color: #7C4DFF;
                color: white;
            }
            QPushButton#browseFileBtn:hover {
                background-color: #651FFF;
            }
            QPushButton#browseFolderBtn {
                background-color: #9C27B0;
                color: white;
            }
            QPushButton#browseFolderBtn:hover {
                background-color: #7B1FA2;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(5)
        # Title
        title = QLabel("Create New Project")
        title.setAccessibleName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        # Project Name
        layout.addWidget(QLabel("Project Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter project name")
        layout.addWidget(self.name_edit)
        # Point Cloud Files Section
        layout.addWidget(QLabel("Link 3D Point Cloud Data:"))
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        self.browse_file_btn = QPushButton("Choose File(s)")
        self.browse_file_btn.setObjectName("browseFileBtn")
        self.browse_file_btn.clicked.connect(self.browse_files)
        self.browse_folder_btn = QPushButton("Choose Folder")
        self.browse_folder_btn.setObjectName("browseFolderBtn")
        self.browse_folder_btn.clicked.connect(self.browse_folder)
        btn_layout.addWidget(self.browse_file_btn)
        btn_layout.addWidget(self.browse_folder_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        # File Display
        self.files_display = QTextEdit()
        self.files_display.setReadOnly(True)
        self.files_display.setFixedHeight(140)
        self.files_display.setPlaceholderText("No files selected yet...")
        layout.addWidget(self.files_display)
        # File counter
        self.file_count_label = QLabel("0 files selected")
        self.file_count_label.setStyleSheet("color: #6A1B9A; font-style: italic;")
        layout.addWidget(self.file_count_label)
        # Project Category
        layout.addWidget(QLabel("Project Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["None", "Design", "Construction", "Measurement", "Other"])
        layout.addWidget(self.category_combo)
        # OK / Cancel Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("okBtn")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)
        self.selected_files = []

    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Point Cloud Files",
            "",
            "Point Cloud Files (*.las *.laz *.ply *.pts *.xyz *.pcd *.bin);;All Files (*)"
        )
        if files:
            self.selected_files = files
            self.update_file_display()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder Containing Point Cloud Files")
        if folder:
            supported_exts = {'.las', '.laz', '.ply', '.pts', '.xyz', '.pcd', '.bin'}
            found = []
            for root, _, fs in os.walk(folder):
                for f in fs:
                    if os.path.splitext(f)[1].lower() in supported_exts:
                        found.append(os.path.join(root, f))
            if not found:
                QMessageBox.information(self, "No Files", "No supported point cloud files found.")
                return
            self.selected_files = found
            self.update_file_display()

    def update_file_display(self):
        count = len(self.selected_files)
        self.file_count_label.setText(f"{count} file{'s' if count != 1 else ''} selected")
        if count == 0:
            self.files_display.setPlainText("No files selected yet...")
        elif count <= 12:
            self.files_display.setPlainText("\n".join(os.path.basename(f) for f in self.selected_files))
        else:
            sample = "\n".join(os.path.basename(f) for f in self.selected_files[:10])
            self.files_display.setPlainText(f"{sample}\n... and {count - 10} more files")

    def validate_and_accept(self):
        project_name = self.name_edit.text().strip()
        if not project_name:
            QMessageBox.warning(self, "Input Required", "Please enter a project name.")
            return

        projects_base = r"C:\3D_Tool\projects"
        project_folder = os.path.join(projects_base, project_name)
        if os.path.exists(project_folder):
            QMessageBox.warning(self, "Name Exists", "A project with this name already exists.\nPlease enter another name.")
            return

        self.accept()

    def get_data(self):
        return {
            "project_name": self.name_edit.text().strip(),
            "pointcloud_files": self.selected_files.copy(),
            "category": self.category_combo.currentText(),
            "file_count": len(self.selected_files)
        }
#### Mayur Wakhare 16-06-2026 New Code Added 
class WorksheetCategoryDialog(QDialog):
    def __init__(self, worksheet_folder, worksheet_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Layer")
        self.setModal(True)
        self.resize(500, 400)
        
        self.worksheet_folder = worksheet_folder
        self.worksheet_data = worksheet_data
        
        self.selected_category_folder = None
        self.selected_layer = None
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel(f"Worksheet: {self.worksheet_data.get('worksheet_name', 'Unknown')}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4A148C; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeWidget { border: 2px solid #BA68C8; border-radius: 8px; font-size: 14px; padding: 5px; }
            QTreeWidget::item { padding: 8px; }
            QTreeWidget::item:selected { background-color: #E1BEE7; color: #4A148C; }
        """)
        layout.addWidget(self.tree)
        
        # Categories mapping
        categories = [
            ("Design Layers", "designs"),
            ("Measurement", "measurements"),
            ("Material Layers", "construction"),
            ("Mergers", "merger")
        ]
        
        for display_name, folder_name in categories:
            cat_item = QTreeWidgetItem(self.tree)
            cat_item.setData(0, Qt.UserRole, folder_name)
            
            cat_path = os.path.join(self.worksheet_folder, folder_name)
            layer_count = 0
            if os.path.exists(cat_path) and os.path.isdir(cat_path):
                layers = [d for d in os.listdir(cat_path) if os.path.isdir(os.path.join(cat_path, d))]
                layers.sort()
                layer_count = len(layers)
                for layer in layers:
                    layer_item = QTreeWidgetItem(cat_item)
                    layer_item.setText(0, layer)
                    layer_item.setData(0, Qt.UserRole, layer)
                    
            cat_item.setText(0, f"{display_name} ({layer_count})")
        
        self.tree.itemDoubleClicked.connect(self.on_double_click)
        self.tree.itemClicked.connect(self.on_item_clicked)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton { background-color: #E0C3FC; color: #4A148C; border-radius: 10px; padding: 8px 16px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #D8B8F8; }
        """)
        
        self.open_btn = QPushButton("Open Selected")
        self.open_btn.clicked.connect(self.accept_selection)
        self.open_btn.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #AB47BC, stop:1 #8E24AA); color: white; border-radius: 10px; padding: 8px 16px; font-weight: bold; border: none; }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9C27B0, stop:1 #7B1FA2); }
        """)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.open_btn)
        layout.addLayout(btn_layout)

    def accept_selection(self):
        item = self.tree.currentItem()
        if not item:
            QMessageBox.information(self, "No Selection", "Please select a layer.")
            return
            
        parent_item = item.parent()
        if not parent_item:
            QMessageBox.information(self, "Invalid Selection", "Please select a specific layer inside a category.")
            return
            
        self.selected_category_folder = parent_item.data(0, Qt.UserRole)
        self.selected_layer = item.data(0, Qt.UserRole)
        self.accept()
        
    def on_double_click(self, item, column):
        if item.parent():
            self.accept_selection()

    def on_item_clicked(self, item, column):
        # If it's a top-level item (category), toggle its expansion
        if not item.parent():
            item.setExpanded(not item.isExpanded())
##########################################################################
# ===========================================================================================================================
# ** EXISTING WORKSHEET DIALOG - MULTI-PAGE VERSION **
# ===========================================================================================================================
class ExistingWorksheetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open Existing Worksheet")
        self.setModal(True)
        self.resize(800, 600)

        self.parent = parent  # PointCloudViewer instance
        if parent and hasattr(parent, 'WORKSHEETS_BASE_DIR'):
            self.base_dir = parent.WORKSHEETS_BASE_DIR
        else:
            self.base_dir = r"C:\3D_Tool\user\worksheets"

        # Final selected data
        self.selected_worksheet_data = None
        self.selected_worksheet_folder = None
        self.selected_subfolder_type = None   # "designs", "measurements", "construction"
        self.selected_layer_name = None

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Dynamic title
        self.title_label = QLabel("Select an Existing Worksheet")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: #4A148C;
            padding: 10px; background-color: #E8EAF6; border-radius: 8px;
        """)
        main_layout.addWidget(self.title_label)

        # Checkbox for Buddies
        self.buddy_checkbox = QCheckBox("View Buddies Worksheet")
        self.buddy_checkbox.setStyleSheet("font-size: 14px; font-weight: bold; color: #4A148C; margin-left: 5px;")
        self.buddy_checkbox.toggled.connect(self.toggle_buddy_mode)
        main_layout.addWidget(self.buddy_checkbox)

        # Pages
        self.page0 = self.create_page0() # Buddies list
        self.page1 = self.create_page1() # Worksheets list
        self.page2 = self.create_page2()
        self.page3 = self.create_page3()

        main_layout.addWidget(self.page0)
        main_layout.addWidget(self.page1)
        main_layout.addWidget(self.page2)
        main_layout.addWidget(self.page3)

        self.page0.hide()
        self.page2.hide()
        self.page3.hide()

        # Buttons
        btn_layout = QHBoxLayout()

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setFixedWidth(100)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545; color: white; border: none; padding: 12px;
                border-radius: 20px; font-weight: bold;
            }
            QPushButton:hover { background-color: #C82333; }
        """)
        self.delete_btn.clicked.connect(self.delete_worksheet)

        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()

        self.back_btn = QPushButton("Back")
        self.back_btn.setFixedWidth(100)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.hide()

        self.open_ws_btn = QPushButton("Open Worksheet")
        self.open_ws_btn.setFixedWidth(160)
        self.open_ws_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #007BFF, stop:1 #0056B3);
                color: white; border: none; padding: 12px;
                border-radius: 20px; font-weight: bold;
            }
        """)
        self.open_ws_btn.clicked.connect(self.open_worksheet_directly)

        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedWidth(120)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #AB47BC, stop:1 #8E24AA);
                color: white; border: none; padding: 12px;
                border-radius: 20px; font-weight: bold;
            }
        """)
        self.next_btn.clicked.connect(self.go_next)

        self.open_btn = QPushButton("Open Selected")
        self.open_btn.setFixedWidth(160)
        self.open_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #AB47BC, stop:1 #8E24AA);
                color: white; border: none; padding: 12px;
                border-radius: 20px; font-weight: bold;
            }
        """)
        self.open_btn.clicked.connect(self.final_open)
        self.open_btn.hide()  # Only shown on page 3

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.open_ws_btn)
        btn_layout.addWidget(self.next_btn)
        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(cancel_btn)

        main_layout.addLayout(btn_layout)

    # ------------------------------------------------------------------
    # Page 0: List of Buddies
    # ------------------------------------------------------------------
    def create_page0(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.buddies_list = QListWidget()
        self.buddies_list.setStyleSheet("""
            QListWidget::item { padding: 14px; border-bottom: 1px solid #E0E0E0; font-size: 14px; }
            QListWidget::item:selected { background: #BBDEFB; color: black; }
        """)
        layout.addWidget(QLabel("Select a Buddy (User):"))
        layout.addWidget(self.buddies_list)
        return widget

    def toggle_buddy_mode(self, checked):
        if checked:
            self.load_buddies()
            self.page1.hide()
            self.page2.hide()
            self.page3.hide()
            self.page0.show()
            self.delete_btn.hide()
            self.open_ws_btn.hide()
            self.back_btn.hide()
            self.next_btn.show()
            self.open_btn.hide()
            self.title_label.setText("Select Buddy")
        else:
            self.base_dir = self.parent.WORKSHEETS_BASE_DIR if hasattr(self.parent, 'WORKSHEETS_BASE_DIR') else r"C:\3D_Tool\user\worksheets"
            self.load_worksheets()
            self.page0.hide()
            self.page2.hide()
            self.page3.hide()
            self.page1.show()
            self.delete_btn.show()
            self.open_ws_btn.show()
            self.back_btn.hide()
            self.next_btn.show()
            self.open_btn.hide()
            self.title_label.setText("Select an Existing Worksheet")

    def load_buddies(self):
        self.buddies_list.clear()
        users_dir = r"C:\3D_Tool\user"
        if not os.path.exists(users_dir):
            self.buddies_list.addItem("Directory not found: " + users_dir)
            return

        current_uid = str(self.parent.current_user_id) if hasattr(self.parent, 'current_user_id') else ""
        
        found = False
        for u_dir in os.listdir(users_dir):
            if u_dir == current_uid:
                continue
                
            u_path = os.path.join(users_dir, u_dir)
            if not os.path.isdir(u_path):
                continue
                
            config_path = os.path.join(u_path, "user_config.txt")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    name = data.get("user_name") or data.get("full_name") or u_dir
                except:
                    name = u_dir
            else:
                name = u_dir
                
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, u_dir)
            self.buddies_list.addItem(item)
            found = True
            
        if not found:
            self.buddies_list.addItem("(No buddies found)")

    # ------------------------------------------------------------------
    # Page 1: List of worksheets
    # ------------------------------------------------------------------
    def create_page1(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: 2px solid #BA68C8; border-radius: 10px; background:white; }")

        self.ws_content = QWidget()
        self.ws_content_layout = QVBoxLayout(self.ws_content)
        self.ws_content_layout.setAlignment(Qt.AlignTop)
        self.ws_content_layout.setSpacing(12)

        self.ws_items = []  # (checkbox, data, folder_name, item_widget)

        self.load_worksheets()

        scroll.setWidget(self.ws_content)
        layout.addWidget(scroll)
        return widget

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

    def load_worksheets(self):
        self.clear_layout(self.ws_content_layout)
        
        self.ws_items.clear()

        if not os.path.exists(self.base_dir):
            lbl = QLabel(f"Directory not found:\n{self.base_dir}")
            lbl.setStyleSheet("color:red;")
            self.ws_content_layout.addWidget(lbl)
        else:
            found = False
            for folder_name in sorted(os.listdir(self.base_dir)):
                folder_path = os.path.join(self.base_dir, folder_name)
                if not os.path.isdir(folder_path):
                    continue
                config_path = os.path.join(folder_path, "worksheet_config.txt")
                if not os.path.exists(config_path):
                    continue
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    found = True

                    name = data.get("worksheet_name", folder_name)
                    proj = data.get("project_name", "None")
                    if proj in ("None", ""):
                        proj = "No Project"
                    date_str = data.get("created_at", "")
                    if date_str:
                        try:
                            date_str = date_str.replace("Z", "+00:00")
                            date = datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M")
                        except:
                            date = date_str[:19] if len(date_str) >= 19 else date_str
                    else:
                        date = "Unknown"

                    checkbox = QCheckBox()
                    text = f"<b>{name}</b><br>"
                    text += f"<small>Project: <i>{proj}</i> | Created: {date}<br>Folder: {folder_name}</small>"
                    label = QLabel(text)
                    label.setWordWrap(True)
                    label.setStyleSheet("""
                        QLabel { background:#F8E8FF; padding:14px; border-radius:10px;
                                 border:1px solid #E1BEE7; }
                    """)

                    item_widget = QWidget()
                    item_layout = QHBoxLayout(item_widget)
                    item_layout.setContentsMargins(0,0,0,0)
                    item_layout.addWidget(checkbox)
                    item_layout.addWidget(label, 1)

                    self.ws_content_layout.addWidget(item_widget)
                    
                    self.ws_items.append((checkbox, data, folder_name, item_widget))
                except Exception as e:
                    err_lbl = QLabel(f"Warning: Error loading {folder_name}: {e}")
                    err_lbl.setStyleSheet("color:orange;")
                    self.ws_content_layout.addWidget(err_lbl)

            if not found:
                self.ws_content_layout.addWidget(QLabel("No worksheets found in the directory."))

    # ------------------------------------------------------------------
    # Page 2: Actual existing subfolders
    # ------------------------------------------------------------------
    def create_page2(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.subfolder_list = QListWidget()
        self.subfolder_list.setStyleSheet("""
            QListWidget::item { padding: 12px; border-bottom: 1px solid #E0E0E0; }
            QListWidget::item:selected { background: #BBDEFB; color: black; }
        """)
        layout.addWidget(QLabel("Select a section folder:"))
        layout.addWidget(self.subfolder_list)
        return widget

    # ------------------------------------------------------------------
    # Page 3: Layer folders inside selected subfolder
    # ------------------------------------------------------------------
    def create_page3(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.layer_list = QListWidget()
        self.layer_list.setStyleSheet("""
            QListWidget::item { padding: 14px; border-bottom: 1px solid #E0E0E0; font-size: 14px; }
            QListWidget::item:selected { background: #BBDEFB; color: black; }
        """)
        self.layer_list.itemDoubleClicked.connect(self.final_open)  # Double-click to open
        layout.addWidget(QLabel("Select a layer folder:"))
        layout.addWidget(self.layer_list)
        return widget

    # ------------------------------------------------------------------
    # Navigation: Next button logic
    # ------------------------------------------------------------------
    def go_next(self):
        if self.page0.isVisible():
            item = self.buddies_list.currentItem()
            if not item or item.text().startswith("("):
                QMessageBox.information(self, "No Selection", "Please select a valid buddy.")
                return
            buddy_id = str(item.data(Qt.UserRole))
            self.base_dir = os.path.join(r"C:\3D_Tool\user", buddy_id, "road")
            self.load_worksheets()
            self.page0.hide()
            self.page1.show()
            self.delete_btn.hide()
            self.open_ws_btn.hide()
            self.back_btn.show()
            self.next_btn.hide()
            self.open_btn.show()
            title_text = f"{item.text().split('(')[0].strip()}'s Worksheets"
            self.title_label.setText(title_text)
            return

        elif self.page1.isVisible():
           ################################################################### Mayur Wakhare 16-06-2026 New code added
            # Find the selected worksheet first
            selected_any = False
            for cb, data, folder_name, _ in self.ws_items:
                if cb.isChecked():
                    self.selected_worksheet_data = data
                    self.selected_worksheet_folder = os.path.join(self.base_dir, folder_name)
                    selected_any = True
                    break
            
            if not selected_any:
                QMessageBox.information(self, "No Selection", "Please select at least one worksheet.")
                return

            cat_dialog = WorksheetCategoryDialog(self.selected_worksheet_folder, self.selected_worksheet_data, self)
            if cat_dialog.exec_() == QDialog.Accepted:
                self.selected_subfolder_type = cat_dialog.selected_category_folder
                self.selected_layer_name = cat_dialog.selected_layer
                
                # Save config and accept the main dialog
                config_data = {
                    "worksheet": self.selected_worksheet_data.get("worksheet_name",
                                                                os.path.basename(self.selected_worksheet_folder)),
                    "folder": self.selected_subfolder_type,
                    "layer": self.selected_layer_name,
                    "last_selected": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                config_path = os.path.join(self.selected_worksheet_folder, "selected_config.txt")

                try:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=4)
                    print(f"Updated {config_path}")
                except Exception as e:
                    print(f"Failed to save {config_path}: {e}")

                self.accept()
            return

        elif self.page2.isVisible():
            # From Page 2 → Page 3
            item = self.subfolder_list.currentItem()
            if not item or item.text().startswith("("):
                QMessageBox.information(self, "No Selection", "Please select a valid section folder.")
                return

            self.selected_subfolder_type = item.text()
            sub_path = os.path.join(self.selected_worksheet_folder, self.selected_subfolder_type)

            self.layer_list.clear()
            try:
                layers = [d for d in os.listdir(sub_path)
                          if os.path.isdir(os.path.join(sub_path, d))]
                layers.sort()
                if layers:
                    for layer in layers:
                        self.layer_list.addItem(layer)
                else:
                    self.layer_list.addItem("(No layers in this section)")
            except Exception as e:
                self.layer_list.addItem(f"Error reading folder: {e}")

            self.page2.hide()
            self.page3.show()
            self.next_btn.hide()
            self.open_btn.show()
            self.title_label.setText(f"Select Layer in '{self.selected_subfolder_type}'")

    # ------------------------------------------------------------------
    # Back button
    # ------------------------------------------------------------------
    def go_back(self):
        if self.page3.isVisible():
            self.page3.hide()
            self.page2.show()
            self.next_btn.show()
            self.open_btn.hide()
            self.title_label.setText(f"{self.selected_worksheet_data.get('worksheet_name', '')} → Select Section")
        elif self.page2.isVisible():
            self.page2.hide()
            self.page1.show()
            
            if not self.buddy_checkbox.isChecked():
                self.delete_btn.show()
                self.back_btn.hide()
                self.title_label.setText("Select an Existing Worksheet")
            else:
                self.delete_btn.hide()
                self.back_btn.show()
                item = self.buddies_list.currentItem()
                title = f"{item.text().split('(')[0].strip()}'s Worksheets" if item else "Select Buddy Worksheet"
                self.title_label.setText(title)
                
            self.open_ws_btn.show()
            self.next_btn.show()
            self.open_btn.hide()
            
        elif self.page1.isVisible() and hasattr(self, 'buddy_checkbox') and self.buddy_checkbox.isChecked():
            self.page1.hide()
            self.page0.show()
            self.delete_btn.hide()
            self.open_ws_btn.hide()
            self.back_btn.hide()
            self.next_btn.show()
            self.open_btn.hide()
            self.title_label.setText("Select Buddy")

    # ------------------------------------------------------------------
    # Final open - THIS IS WHERE WE SAVE THE selected_config.txt
    # ------------------------------------------------------------------
    def final_open(self):
        if self.page1.isVisible():
            selected_any = False
            for cb, data, folder_name, _ in self.ws_items:
                if cb.isChecked():
                    selected_any = True
                    break
            
            if not selected_any:
                QMessageBox.information(self, "No Selection", "Please select at least one worksheet.")
                return
                
            self.accept()
            return
            
        if not self.page3.isVisible():
            self.go_next()
            return

        item = self.layer_list.currentItem()
        if not item or item.text().startswith("("):
            QMessageBox.information(self, "No Layer", "Please select a valid layer folder.")
            return

        self.selected_layer_name = item.text()

        # Save selected config in worksheet root folder (overwrites existing)
        config_data = {
            "worksheet": self.selected_worksheet_data.get("worksheet_name",
                                                        os.path.basename(self.selected_worksheet_folder)),
            "folder": self.selected_subfolder_type,
            "layer": self.selected_layer_name,
            "last_selected": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        config_path = os.path.join(self.selected_worksheet_folder, "selected_config.txt")

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
            print(f"Updated {config_path}")
        except Exception as e:
            print(f"Failed to save {config_path}: {e}")

        self.accept()

    # ------------------------------------------------------------------
    # Delete a worksheet (only for own worksheets)
    # ------------------------------------------------------------------
    def delete_worksheet(self):
        if not self.page1.isVisible():
            return
            
        if hasattr(self, 'buddy_checkbox') and self.buddy_checkbox.isChecked():
            QMessageBox.warning(self, "Action Denied", "You cannot delete a buddy's worksheet!")
            return
            
        selected_folder = None
        selected_item_widget = None
        for radio, data, folder_name, widget in self.ws_items:
            if radio.isChecked():
                selected_folder = os.path.join(self.base_dir, folder_name)
                selected_item_widget = widget
                break
                
        if not selected_folder:
            QMessageBox.warning(self, "No Selection", "Please select a worksheet to delete.")
            return
            
        name = os.path.basename(selected_folder)
        reply = QMessageBox.question(self, "Delete Worksheet", f"Are you sure you want to permanently delete this worksheet?\n({name})", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            import shutil
            try:
                shutil.rmtree(selected_folder)
                QMessageBox.information(self, "Success", "Worksheet deleted successfully.")
                if selected_item_widget:
                    selected_item_widget.hide()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")

    # ------------------------------------------------------------------
    # Open a worksheet directly from the list (only for own worksheets)
    # ------------------------------------------------------------------
    def open_worksheet_directly(self):
        if not self.page1.isVisible():
            return
            
        selected = None
        for radio, data, folder_name, widget in self.ws_items:
            if radio.isChecked():
                selected = (data, folder_name)
                break

        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a worksheet before opening.")
            return

        self.selected_worksheet_data = selected[0]
        self.selected_worksheet_folder = os.path.join(self.base_dir, selected[1])
        
        # New logic: Auto-select the latest design layer instead of relying on selected_config.txt
        designs_path = os.path.join(self.selected_worksheet_folder, "designs")
        if os.path.exists(designs_path):
            try:
                # Get all directories in the designs folder
                layers = [d for d in os.listdir(designs_path) if os.path.isdir(os.path.join(designs_path, d))]
                if layers:
                    # Sort by modification time to get the latest worked-on layer
                    layers.sort(key=lambda x: os.path.getmtime(os.path.join(designs_path, x)), reverse=True)
                    
                    self.selected_subfolder_type = "designs"
                    self.selected_layer_name = layers[0] # Latest layer
                    
                    self.accept()
                    return
            except Exception as e:
                print(f"Error auto-resolving latest layer: {e}")
                
        QMessageBox.warning(self, "No Design Layer", "No design layers found for this worksheet. Please click 'Next' to manually select a layer.")

    # ------------------------------------------------------------------
    # Return selected data to main window
    # ------------------------------------------------------------------
    def get_selected_data(self):
        """
        Returns a list of data for all selected worksheets.
        Each element is a dict with worksheet_data and folder_path.
        """
        selected_worksheets = []
        for cb, data, folder_name, _ in self.ws_items:
            if cb.isChecked():
                folder_path = os.path.join(self.base_dir, folder_name)
                selected_worksheets.append({
                    "worksheet_data": data,
                    "folder_path": folder_path
                })
        return selected_worksheets


# =================================================================================================================================================================
#                                                   ** Updated WorksheetNewDialog (Layer Name - No Fallback) **
# =================================================================================================================================================================
class WorksheetNewDialog(QDialog):
    """Multi-page dialog for creating a new worksheet with conditional Baseline Type selection (only for 2D)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Worksheet")
        self.setModal(True)
        self.resize(560, 400)

        self.parent = parent  # Reference to main window

        # Data storage
        self.reference_type = None
        self.allocation_data = {}
        self.allocated_project_id = None
        self.allocated_project_name = None
        self.allocated_from_km = 0
        self.allocated_to_km = 1000  # Default wide range if no allocation
        self.user_config_path = ""

        # Load allocation
        self.load_user_allocation()
        
        # ------------------------------------------------------------------
        # Style (consistent with DesignNewDialog)
        # ------------------------------------------------------------------
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f0e6fa, stop:1 #e6e6fa);
                border-radius: 18px;
            }
            QLabel {
                color: #2d1b3d;
                font-weight: 600;
                font-size: 13px;
            }
            QLineEdit, QComboBox {
                border: 2px solid #BA68C8;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #8E24AA;
                background-color: #F8E8FF;
            }
            QGroupBox {
                border: 2px solid #9C27B0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 8px;
                font-weight: bold;
                color: #4A148C;
                background-color: rgba(255, 255, 255, 0.4);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 10px;
                background-color: #E1BEE7;
                border-radius: 6px;
            }
            QCheckBox {
                font-weight: 500;
                spacing: 8px;
                font-size: 13px;
            }
            QRadioButton {
                padding: 6px;
                color: #2d1b3d;
                font-weight: normal;
            }
            QPushButton {
                border-radius: 20px;
                padding: 11px;
                font-weight: bold;
                min-width: 110px;
                border: none;
            }
            QPushButton#nextBtn, QPushButton#okBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #AB47BC, stop:1 #8E24AA);
                color: white;
            }
            QPushButton#nextBtn:hover, QPushButton#okBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #9C27B0, stop:1 #7B1FA2);
            }
            QPushButton#backBtn, QPushButton#cancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333;
            }
            QPushButton#backBtn:hover, QPushButton#cancelBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #D1C4E9, stop:1 #BA68C8);
            }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # Stacked pages
        self.page1 = QWidget()
        self.page2 = QWidget()
        self.setup_page1()
        self.setup_page2()

        self.main_layout.addWidget(self.page1)
        self.main_layout.addWidget(self.page2)
        self.page2.setVisible(False)

    def load_user_allocation(self):
        """Load allocation data from user_config.txt"""
        if not self.parent or not hasattr(self.parent, 'current_user_id'):
            return

        user_id = str(self.parent.current_user_id)
        self.user_config_path = os.path.join(r"C:\3D_Tool\user", user_id, "user_config.txt")
        
        if os.path.exists(self.user_config_path):
            try:
                with open(self.user_config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Keys must match what is written in login.py (user_config_data)
                    self.allocation_data = data.get("allocation_data", {})
                    project_data = data.get("project_data", {})
                    # Set default project id since project logic isn't strictly needed for file fetch but might be needed elsewhere in backend
                    self.allocated_project_id = project_data.get("ph_id")
                    self.allocated_project_name = project_data.get("ph_name")
                    
                    # Parse allocation KMs
                    try:
                        self.allocated_from_km = int(self.allocation_data.get("from_km", 0))
                        self.allocated_to_km = int(self.allocation_data.get("to_km", 1000))
                    except:
                        self.allocated_from_km = 0
                        self.allocated_to_km = 1000
            except Exception as e:
                print(f"Error loading user allocation: {e}")

    # Page 1: Basic worksheet info
    # ------------------------------------------------------------------
    def setup_page1(self):
        layout = QVBoxLayout(self.page1)
        layout.setSpacing(15)

        title = QLabel("Create New Worksheet")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 19px; font-weight: bold; color: #4A148C; padding: 8px;")
        layout.addWidget(title)

        form = QVBoxLayout()
        form.setSpacing(12)

        # Worksheet Name
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Worksheet Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter worksheet name")
        row1.addWidget(self.name_edit)
        form.addLayout(row1)

        # =========================================================
        # File Selection (C:\3D_Tool\road)
        # =========================================================
        file_group = QGroupBox("Point Cloud File Selection")
        file_layout = QVBoxLayout(file_group)

        row_file = QHBoxLayout()
        row_file.addWidget(QLabel("Select File:"))
        self.file_combo = QComboBox()
        self.file_combo.currentTextChanged.connect(self.check_file_availability)
        row_file.addWidget(self.file_combo)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setStyleSheet("background-color: #E1BEE7; border-radius: 4px; padding: 6px;")
        self.btn_refresh.clicked.connect(self.refresh_files)
        row_file.addWidget(self.btn_refresh)
        
        file_layout.addLayout(row_file)
        
        # Download new file section (Hidden as we now use API dropdown)
        self.dl_km_group = QWidget()
        self.dl_km_layout = QHBoxLayout(self.dl_km_group)
        self.dl_km_layout.addWidget(QLabel("Download KM File:"))
        self.dl_km_edit = QLineEdit()
        self.dl_km_edit.setPlaceholderText("Enter KM to download")
        self.dl_km_layout.addWidget(self.dl_km_edit)
        self.dl_km_group.setVisible(False)
        file_layout.addWidget(self.dl_km_group)

        form.addWidget(file_group)

        # Validation Label
        self.lbl_validation = QLabel("")
        self.lbl_validation.setStyleSheet("color: red; font-size: 11px;")
        form.addWidget(self.lbl_validation)

        # === File Status Section ===
        self.file_status_group = QWidget()
        self.file_status_layout = QVBoxLayout(self.file_status_group)
        self.file_status_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_file_status = QLabel("")
        self.lbl_file_status.setStyleSheet("font-size: 11px;")
        self.file_status_layout.addWidget(self.lbl_file_status)

        self.btn_download = QPushButton("Download from Server")
        self.btn_download.clicked.connect(self.start_download)
        self.btn_download.setVisible(False)  # Hiding download button as requested
        self.btn_download.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 6px; 
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.file_status_layout.addWidget(self.btn_download)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        # self.file_status_layout.addWidget(self.progress_bar) # Removing from layout

        form.addWidget(self.file_status_group)

        # Validate and check status based on input text change
        self.dl_km_edit.textChanged.connect(self.validate_km_and_check_file)


        layout.addLayout(form)
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("nextBtn")
        self.next_btn.clicked.connect(self.go_to_page2)
        btn_layout.addWidget(self.next_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # Initialize the files dropdown at the end so it has access to status labels
        self.refresh_files()

    # ------------------------------------------------------------------
    # Page 2: Layer & Baseline Configuration
    # ------------------------------------------------------------------
    def setup_page2(self):
        layout = QVBoxLayout(self.page2)
        layout.setSpacing(12)

        title = QLabel("Worksheet Configuration")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 19px; font-weight: bold; color: #4A148C; padding: 8px;")
        layout.addWidget(title)

        # === Enter Layer Name ===
        layer_name_row = QHBoxLayout()
        layer_name_row.addWidget(QLabel("Enter Layer Name:"))
        self.layer_name_edit = QLineEdit()
        self.layer_name_edit.setPlaceholderText("e.g. Base Layer, Design Layer 1")
        layer_name_row.addWidget(self.layer_name_edit)
        layout.addLayout(layer_name_row)

    # ==== Aniket added on 02-05-2026 for the Simulation purpose ===== 
        # === Master Layer Checkbox ===
        self.cb_master_layer = QCheckBox("Master layer")
        self.cb_master_layer.setStyleSheet("margin-left: 5px;")
        layout.addWidget(self.cb_master_layer)

        layout.addStretch(1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        back_btn = QPushButton("Back")
        back_btn.setObjectName("backBtn")
        back_btn.clicked.connect(self.go_to_page1)
        btn_layout.addWidget(back_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("okBtn")
        ok_btn.clicked.connect(self.final_accept)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------
    def refresh_files(self):
        self.file_combo.clear()

        # 1. Load ONLY Local Files from C:\3D_Tool\road
        road_dir = r"C:\3D_Tool\road"
        local_files = []
        import os
        import glob
        if os.path.exists(road_dir):
            local_files = [os.path.basename(f) for f in glob.glob(os.path.join(road_dir, "*.ply"))]
        print(f"DEBUG: Local files in {road_dir}: {local_files}")

        for f in local_files:
            self.file_combo.addItem(f, {
                "url": None,
                "name": f,
                "is_local": True,
                "local_path": os.path.join(road_dir, f)
            })

        self.check_file_availability()

    def go_to_page2(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Input Required", "Please enter a worksheet name.")
            return

        # Check if file needs to be downloaded before proceeding
        data = self.file_combo.currentData()
        if data and not data.get("is_local"):
            # If not local, start download and proceed only after success
            self.start_download(auto_proceed=True)
            return

    # =================================== Create Worksheet API Payload Mode 1 ====================================
        # At this point the worksheet name exists and selected file is local (or None).
        # Call server API for mode 1 to create worksheet entry.
        try:
            import requests
        except Exception:
            requests = None

        worksheet_name = self.name_edit.text().strip()
        # Determine user id from parent (ehu_id / current_user_id)
        user_id = None
        if self.parent:
            user_id = getattr(self.parent, 'current_user_id', None) or getattr(self.parent, 'current_user', None)

        # Determine file_id from combo data if available. If local file selected,
        # try to resolve a matching server file and use its ID so server doesn't receive null.
        file_id = None
        file_name = None
        if data:
            # Support common keys used by server-side data
            file_id = data.get('file_id') or data.get('id') or data.get('fileId')
            file_name = data.get('name') or data.get('file_name') or data.get('local_path')
            if file_name and file_name.endswith('.ply') and os.path.exists(file_name):
                # if local_path provided, extract basename
                file_name = os.path.basename(file_name)

        # If file_id is still None, try to match the selected filename with server files
        if not file_id and file_name:
            try:
                from API import WorksheetAPI
                api_user_id = None
                if self.parent:
                    api_user_id = getattr(self.parent, 'api_user_id', None) or getattr(self.parent, 'current_user_id', None)
                if api_user_id:
                    files_resp = WorksheetAPI.get_edu_3d_files(api_user_id)
                    if files_resp.get('success'):
                        for f in files_resp.get('data', []):
                            # match by filename or by cleaned name
                            server_name = f.get('file_name') or f.get('name') or ''
                            if server_name == file_name or os.path.basename(server_name) == file_name:
                                file_id = f.get('id') or f.get('file_id')
                                break
            except Exception:
                pass

        payload = {
            "mode": 1,
            "user_id": int(user_id) if user_id is not None and str(user_id).isdigit() else user_id,
            "worksheet_name": worksheet_name,
            "file_id": file_id,
            "worksheet_config_data": {
                "worksheet_name": worksheet_name,
                "project_name": "None",
                "created_at": datetime.now().isoformat(),
                "created_by": getattr(self.parent, 'current_user_full_name', getattr(self.parent, 'current_user', "Unknown")) if self.parent else "Unknown",
                "worksheet_type": "Design",
                "initial_layer": self.design_layer_edit.text() if hasattr(self, 'design_layer_edit') else "",
                "worksheet_category": "Road",
                "data_category": "Design",
                "dimension": "2D",
                "point_cloud_file": file_name if file_name else ""
            }
        }


        # Make the API call if requests is available; otherwise proceed locally but warn user
        api_ok = False
        api_resp_text = ""
        created_ws_id = None
        print("\n=== CREATE WORKSHEET PAYLOAD ===")
        try:
            import json as _json
            print(_json.dumps(payload, indent=2))
        except Exception:
            print(payload)

        # Use central API helper
        try:
            from API import WorksheetAPI
            resp = WorksheetAPI.create_worksheet(payload)
        except Exception as e:
            resp = {"success": False, "message": str(e)}

        # Print response debug
        try:
            print("=== CREATE WORKSHEET RESPONSE (via API helper) ===")
            import json as _json
            print(_json.dumps(resp, indent=2))
        except Exception:
            print(resp)

        if not resp.get('success'):
            api_resp_text = resp.get('text') or resp.get('message') or str(resp)
            QMessageBox.warning(self, "API Error", f"Failed to create worksheet on server.\n{api_resp_text}")
            return

        # Save created worksheet id for later use (if returned)
        created_ws_id = None
        if isinstance(resp.get('data'), dict):
            created_ws_id = resp['data'].get('worksheet_id') or resp['data'].get('worksheetId') or resp.get('worksheet_id')
        if not created_ws_id:
            # older servers might return id at top level
            created_ws_id = resp.get('worksheet_id') or resp.get('data')

        if created_ws_id:
            try:
                self.created_worksheet_id = int(created_ws_id)
            except Exception:
                self.created_worksheet_id = created_ws_id
            # Propagate created id to parent (main window) so callers can use it
            try:
                if hasattr(self, 'parent') and self.parent:
                    setattr(self.parent, 'created_worksheet_id', self.created_worksheet_id)
                    # also set current_worksheet_id for callers that expect it
                    try:
                        setattr(self.parent, 'current_worksheet_id', self.created_worksheet_id)
                    except Exception:
                        pass
            except Exception:
                pass
    # ===============================================================================================================

        # Proceed to page 2 only if API call succeeded
        self.page1.setVisible(False)
        self.page2.setVisible(True)
        self.on_project_changed()


    def _get_selected_data_category(self):
        # Hardcoded to Design
        return "Design"

    def check_file_availability(self):
        """Check if local file is selected."""
        if self.file_combo.count() == 0:
            self.lbl_file_status.setText("⚠ No local files found. Please download from Buy 3D Files.")
            self.lbl_file_status.setStyleSheet("color: red; font-weight: bold;")
            self.btn_download.setVisible(False)
            self.next_btn.setEnabled(False)
            return

        data = self.file_combo.currentData()
        if not data:
            self.next_btn.setEnabled(False)
            return

        if data.get("is_local"):
            self.lbl_file_status.setText(f"✅ Selected local file: {data.get('name')}")
            self.lbl_file_status.setStyleSheet("color: green; font-weight: bold;")
            self.btn_download.setVisible(False)
            self.next_btn.setEnabled(True)

    def start_download(self, auto_proceed=False):
        """Start background download of selected file to C:\\3D_Tool\\road"""
        data = self.file_combo.currentData()
        if not data or not data.get("url"):
            QMessageBox.warning(self, "Error", "No download URL available for this file.")
            return

        file_url = data.get("url")
        file_name = data.get("name")
        
        # Setup destination: C:\3D_Tool\road
        road_folder = r"C:\3D_Tool\road"
        if not os.path.exists(road_folder):
            os.makedirs(road_folder, exist_ok=True)
        
        save_path = os.path.join(road_folder, file_name)
        self.auto_proceed_after_dl = auto_proceed
        
        # Disable button and update text
        self.btn_download.setEnabled(False)
        self.btn_download.setText(f"Downloading {file_name} (0%)...")
        
        # User request: "Don't add the another dialog box to the download ok. show downoad process in the same New Worksheet dialog box"
        # We will use the button itself as a progress bar
        
        self.download_thread = DownloadThread(file_url, save_path)
        self.download_thread.progress_signal.connect(self.update_download_progress)
        self.download_thread.finished_signal.connect(self.on_download_finished)
        self.download_thread.start()

    def update_download_progress(self, percent):
        """Update the button styling to act as a progress bar (Green part vs Red part)"""
        data = self.file_combo.currentData()
        file_name = data.get("name") if data else "File"
        self.btn_download.setText(f"Downloading {file_name} ({percent}%)...")
        
        # Explicit stops for sharp transition: Green (#4CAF50), Red (#f44336)
        p = percent / 100.0
        self.btn_download.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                            stop:0 #4CAF50, stop:{p} #4CAF50, 
                                            stop:{p} #f44336, stop:1 #f44336);
                color: white; 
                border-radius: 5px; 
                padding: 8px; 
                font-weight: bold;
                min-height: 25px;
            }}
        """)

    def on_download_finished(self, success, message):
        self.btn_download.setEnabled(True)
        self.btn_download.setText("Download & Proceed")
        
        if success:
            self.btn_download.setText("Download Complete ✅")
            self.btn_download.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border-radius: 5px; font-weight: bold; }")
            
            # Update data
            idx = self.file_combo.currentIndex()
            data = self.file_combo.itemData(idx)
            if data:
                data["is_local"] = True
                data["local_path"] = os.path.join(r"C:\3D_Tool\road", data.get("name"))
                self.file_combo.setItemData(idx, data)
                # Update display text to (Local)
                self.file_combo.setItemText(idx, f"{data.get('name')} (Local)")
            
            self.check_file_availability()
            
            # Auto proceed to next page if triggered from 'Next' button
            if hasattr(self, 'auto_proceed_after_dl') and self.auto_proceed_after_dl:
                self.auto_proceed_after_dl = False
                self.go_to_page2()
        else:
            QMessageBox.critical(self, "Download Failed", f"Failed to download file: {message}")
            self.check_file_availability() # Reset button style

    def validate_km_and_check_file(self):
        """Validate KM range for downloading"""
        if self.validate_km_range():
            self.btn_download.setEnabled(True)
        else:
            self.btn_download.setEnabled(False)

    def validate_km_range(self):
        """Validate if entered KM is within allocation for downloading"""
        text = self.dl_km_edit.text().strip()
        
        self.lbl_validation.setText("")
        
        # If empty, disable next
        if not text:
            return False

        try:
            val_km = int(text)
        except ValueError:
            self.lbl_validation.setText("KM must be an integer number.")
            return False

        # Allocation Check
        if val_km < self.allocated_from_km or val_km > self.allocated_to_km:
            self.lbl_validation.setText(f"KM {val_km} is outside allocation [{self.allocated_from_km}-{self.allocated_to_km}].")
            return False
            
        return True

    def go_to_page1(self):
        self.page2.setVisible(False)
        self.page1.setVisible(True)

    def on_dimension_changed(self):
        is_2d = self.radio_2d.isChecked()
        
        # Show/hide the baseline group
        self.baseline_group.setVisible(is_2d)
        
        # Adjust the size policy
        if is_2d:
            self.baseline_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        else:
            # When hidden, minimize space usage
            self.baseline_group.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        
        # Force layout recalculation
        self.page2.layout().invalidate()
        self.page2.layout().activate()
        
        # Update the dialog size
        self.adjustSize()

    def on_project_changed(self):
        # No longer needed to load point cloud files, as we now auto-determine path per KM
        pass


    # ------------------------------------------------------------------
    # Final accept
    # ------------------------------------------------------------------
    def final_accept(self):
        worksheet_name = self.name_edit.text().strip()
        if not worksheet_name:
            QMessageBox.warning(self, "Error", "Worksheet name is required.")
            return
        worksheets_base = r"C:\3D_Tool\user\worksheets"
        worksheet_folder = os.path.join(worksheets_base, worksheet_name)
        if os.path.exists(worksheet_folder):
            QMessageBox.warning(self, "Name Exists", "A worksheet with this name already exists.\nPlease enter another name.")
            return

        # Build payload for mode 2
        layer_name = self.layer_name_edit.text().strip()
        if not layer_name:
            QMessageBox.warning(self, "Error", "Layer name is required.")
            return
    
    # ================================ Create Layer API Payload Mode 2 =================================
        # Worksheet id should have been set by the mode 1 response earlier
        worksheet_id = getattr(self, 'created_worksheet_id', None)
        if not worksheet_id and self.parent:
            worksheet_id = getattr(self.parent, 'current_worksheet_id', None) or getattr(self.parent, 'created_worksheet_id', None)

        if not worksheet_id:
            QMessageBox.warning(self, "Error", "Worksheet ID not found. Please complete the first step (Next) to create the worksheet on server.")
            return

        user_id = None
        if self.parent:
            user_id = getattr(self.parent, 'current_user_id', None) or getattr(self.parent, 'current_user', None)

        data = self.file_combo.currentData()
        point_cloud_file = data.get("local_path") if data else ""

        layer_config_data = {
            "layer_name": layer_name,
            "dimension": "2D",
            "reference_type": self.reference_type or "Road",
            "reference_line": "",
            "master_layer": bool(self.cb_master_layer.isChecked()),
            "project_name": self.allocated_project_name or "None",
            "worksheet_name": self.name_edit.text().strip(),
            "point_cloud_file": point_cloud_file,
            "created_by": getattr(self.parent, 'current_user_full_name', getattr(self.parent, 'current_user', "Unknown")) if self.parent else "Unknown",
            "created_at": datetime.now().isoformat()
        }

        payload = {
            "mode": 2,
            "user_id": int(user_id) if user_id is not None and str(user_id).isdigit() else user_id,
            "worksheet_id": str(worksheet_id),
            "layer_name": layer_name,
            "construction_type": 1,
            "is_2d": 1,
            "type_2d": 1,
            "is_3d": 0,
            "type_3d": 0,
            "file_path": "",
            "layer_config_data": layer_config_data,
            "layer_json_data": {}
        }


        # Print debug payload
        try:
            import json as _json
            print("\n=== MODE 2 (CREATE LAYER) PAYLOAD ===")
            print(_json.dumps(payload, indent=2))
        except Exception:
            print(payload)

        # Use central API helper for mode 2
        try:
            from API import WorksheetAPI
            resp = WorksheetAPI.create_worksheet(payload)
        except Exception as e:
            resp = {"success": False, "message": str(e)}

        try:
            print("=== MODE 2 RESPONSE (via API helper) ===")
            import json as _json2
            print(_json2.dumps(resp, indent=2))
        except Exception:
            print(resp)

        if not resp.get('success'):
            api_resp_text = resp.get('text') or resp.get('message') or str(resp)
            QMessageBox.critical(self, "API Error", f"Failed to create layer on server.\n{api_resp_text}")
            return

        # Save created layer id if returned
        created_layer_id = None
        if isinstance(resp.get('data'), dict):
            created_layer_id = resp['data'].get('layer_id') or resp['data'].get('layerId') or resp['data'].get('id')
        if not created_layer_id:
            created_layer_id = resp.get('layer_id') or resp.get('data')

        if created_layer_id:
            self.created_layer_id = created_layer_id
            # propagate to parent if present
            if self.parent:
                try:
                    setattr(self.parent, 'current_layer_id', created_layer_id)
                except Exception:
                    pass

        self.reference_type = "Road"
        self.accept()

    # ------------------------------------------------------------------
    # get_data() – returns all needed info
    # ------------------------------------------------------------------
    def get_data(self):
        worksheet_name = self.name_edit.text().strip()
        project_name = self.allocated_project_name or ""
        ph_id = self.allocated_project_id
        dimension = "2D"
        worksheet_type = "Design"
        data_category = "Design"

        # Use exactly what user entered — no fallback
        layer_name = self.layer_name_edit.text().strip()

        # Selected drop down point cloud file
        data = self.file_combo.currentData()
        point_cloud_file = data.get("local_path") if data else None
        file_name = data.get("name") if data else ""
        
        # Parse km from selected file name if possible
        km_final = "0"
        if file_name:
            try:
                # Try to extract numbers from filename like "123.ply" or "KM_456.ply"
                import re
                nums = re.findall(r'\d+', file_name)
                if nums:
                    km_final = nums[0]
            except:
                km_final = str(self.allocated_from_km)

        return {
            "worksheet_name": worksheet_name,
            "project_name": project_name,
            "ph_id": ph_id,
            "worksheet_type": worksheet_type,
            "worksheet_category": self.reference_type or "Road",
            "data_category": data_category,
            "dimension": dimension,
            "initial_layer_name": layer_name,
            "reference_type": self.reference_type or "Road",
            "reference_line": None,
            "point_cloud_file": point_cloud_file,
            "from_km": km_final,
            "to_km": km_final,
            "master_layer": bool(self.cb_master_layer.isChecked())
        }
    


# ===========================================================================================================================
# ** ROAD PLANE WIDTH DIALOG **  For the road baseline map on 3D Point Cloud Data
# ===========================================================================================================================

class RoadPlaneWidthDialog(QDialog):
    def __init__(self, current_width=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Road Plane Width Configuration")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f0e6fa, stop:1 #e6e6fa);
                border-radius: 15px;
            }
            QLabel { 
                color: #2d1b3d; 
                font-weight: bold; 
                font-size: 13px; 
            }
            QLineEdit {
                border: 2px solid #BA68C8;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #9C27B0;
            }
            QLineEdit:read-only {
                background-color: #f0f0f0;
                color: #666;
            }
            QGroupBox {
                border: 2px solid #BA68C8;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 10px;
                font-weight: bold;
                color: #4A148C;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
            }
            QPushButton {
                border-radius: 18px;
                padding: 8px 15px;
                font-weight: bold;
                border: none;
            }
            QPushButton#okBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #AB47BC, stop:1 #8E24AA);
                color: white;
            }
            QPushButton#cancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333;
            }
            QPushButton#addBtn {
                background-color: #4A148C;
                color: white;
                border-radius: 5px;
                font-size: 12px;
                min-width: 150px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QRadioButton {
                font-weight: bold;
                color: #2d1b3d;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Mode Selection
        mode_group = QGroupBox("Configuration Mode")
        mode_layout = QHBoxLayout(mode_group)
        self.radio_normal = QRadioButton("Normal (Straight)")
        self.radio_lane_drop = QRadioButton("Lane Drop / Expand")
        self.radio_normal.setChecked(True)
        mode_layout.addWidget(self.radio_normal)
        mode_layout.addWidget(self.radio_lane_drop)
        main_layout.addWidget(mode_group)

        # Stacked Widget for modes
        self.stacked_widget = QStackedWidget()
        
        # --- Normal Mode Page ---
        self.page_normal = QWidget()
        normal_layout = QVBoxLayout(self.page_normal)
        self.normal_title = QLabel("Enter Road Plane Width (meters)")
        self.normal_title.setAlignment(Qt.AlignCenter)
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("e.g. 10.0")
        self.width_input.setAlignment(Qt.AlignCenter)
        if current_width:
            self.width_input.setText(str(current_width))
        validator = QDoubleValidator(0.1, 1000.0, 2)
        self.width_input.setValidator(validator)
        normal_layout.addWidget(self.normal_title)
        normal_layout.addWidget(self.width_input)
        # normal_layout.addStretch() # Removed to prevent weird layout in stack
        self.stacked_widget.addWidget(self.page_normal)

        # --- Lane Drop Mode Page ---
        self.page_lane_drop = QWidget()
        lane_drop_layout = QVBoxLayout(self.page_lane_drop)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.sections_layout = QVBoxLayout(self.scroll_content)
        self.sections_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.scroll_content)
        lane_drop_layout.addWidget(scroll)

        self.add_section_btn = QPushButton("+ Add lane drop/Expand")
        self.add_section_btn.setObjectName("addBtn")
        self.add_section_btn.clicked.connect(self.add_section_row)
        lane_drop_layout.addWidget(self.add_section_btn, 0, Qt.AlignCenter)
        
        self.stacked_widget.addWidget(self.page_lane_drop)
        main_layout.addWidget(self.stacked_widget)

        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setObjectName("okBtn")
        self.ok_btn.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        main_layout.addLayout(btn_layout)

        # Initialize sections
        self.section_rows = []
        self.radio_normal.toggled.connect(self.toggle_mode)
        
        # Add default 2 sections for Lane Drop
        self.add_section_row()
        self.add_section_row()

    def toggle_mode(self):
        if self.radio_normal.isChecked():
            self.stacked_widget.setCurrentIndex(0)
        else:
            self.stacked_widget.setCurrentIndex(1)

    def add_section_row(self):
        index = len(self.section_rows) + 1
        group = QGroupBox(f"Section {index}")
        row_layout = QGridLayout(group)
        
        lbl_from = QLabel("From Ch:")
        edit_from = QLineEdit()
        edit_from.setPlaceholderText("100+000")
        
        lbl_to = QLabel("To Ch:")
        edit_to = QLineEdit()
        edit_to.setPlaceholderText("100+200")
        
        lbl_width = QLabel("Width:")
        edit_width = QLineEdit()
        edit_width.setPlaceholderText("30")
        edit_width.setValidator(QDoubleValidator(0.0, 1000.0, 2))
        
        lbl_angle = QLabel("Angle:")
        edit_angle = QLineEdit()
        edit_angle.setReadOnly(True)
        edit_angle.setPlaceholderText("Calculated")
        
        # Grid positioning
        row_layout.addWidget(lbl_from, 0, 0)
        row_layout.addWidget(edit_from, 0, 1)
        row_layout.addWidget(lbl_to, 0, 2)
        row_layout.addWidget(edit_to, 0, 3)
        row_layout.addWidget(lbl_width, 1, 0)
        row_layout.addWidget(edit_width, 1, 1)
        
        # Show Angle A, B... starting from Section 2
        if index > 1:
            lbl_angle.setText(f"Angle {chr(64+index-1)}:") # Angle A, Angle B...
            row_layout.addWidget(lbl_angle, 1, 2)
            row_layout.addWidget(edit_angle, 1, 3)

        # Delete button for sections > 2
        if index > 2:
            del_btn = QPushButton("X")
            del_btn.setFixedSize(30, 30)
            del_btn.setStyleSheet("background-color: #ff4d4d; color: white; border-radius: 5px;")
            del_btn.clicked.connect(lambda: self.remove_section_row(group))
            row_layout.addWidget(del_btn, 1, 4)

        self.sections_layout.addWidget(group)
        
        row_data = {
            'group': group,
            'from': edit_from,
            'to': edit_to,
            'width': edit_width,
            'angle': edit_angle
        }
        self.section_rows.append(row_data)
        
        # Connect signals for auto-calculation
        edit_from.textChanged.connect(self.calculate_angles)
        edit_to.textChanged.connect(self.calculate_angles)
        edit_width.textChanged.connect(self.calculate_angles)

    def remove_section_row(self, group):
        for i, row in enumerate(self.section_rows):
            if row['group'] == group:
                self.section_rows.pop(i)
                group.setParent(None)
                break
        self.calculate_angles()

    def parse_chainage(self, ch_str):
        """Convert '100+000' to 100000.0 or similar float"""
        try:
            ch_str = ch_str.strip()
            if not ch_str: return None
            if '+' in ch_str:
                parts = ch_str.split('+')
                return float(parts[0]) * 1000 + float(parts[1])
            return float(ch_str)
        except:
            return None

    def calculate_angles(self):
        """Calculate Angle A, B, etc. between sections"""
        import math
        for i in range(1, len(self.section_rows)):
            prev_row = self.section_rows[i-1]
            curr_row = self.section_rows[i]
            
            end_ch_prev = self.parse_chainage(prev_row['to'].text())
            start_ch_curr = self.parse_chainage(curr_row['from'].text())
            
            w_prev = 0.0
            try: w_prev = float(prev_row['width'].text())
            except: pass
            
            w_curr = 0.0
            try: w_curr = float(curr_row['width'].text())
            except: pass
            
            if end_ch_prev is not None and start_ch_curr is not None:
                dist = start_ch_curr - end_ch_prev
                if dist > 0:
                    delta_w = abs(w_curr - w_prev)
                    # Symmetrical drop assumed? Or total drop? User drawing shows total width.
                    # Angle A usually defined as the deviation angle.
                    angle_rad = math.atan(delta_w / dist)
                    angle_deg = math.degrees(angle_rad)
                    curr_row['angle'].setText(f"{angle_deg:.2f}°")
                else:
                    curr_row['angle'].setText("N/A (Overlap)")
            else:
                curr_row['angle'].setText("")

    def validate_and_accept(self):
        if self.radio_normal.isChecked():
            if not self.width_input.text().strip():
                QMessageBox.warning(self, "Input Error", "Please enter a valid width.")
                return
            self.accept()
        else:
            # Validate Lane Drop Sections
            if not self.section_rows:
                QMessageBox.warning(self, "Input Error", "Please add at least one section.")
                return
            
            last_to = -float('inf')
            for i, row in enumerate(self.section_rows):
                f_ch = self.parse_chainage(row['from'].text())
                t_ch = self.parse_chainage(row['to'].text())
                w = 0.0
                try: w = float(row['width'].text())
                except: pass
                
                if f_ch is None or t_ch is None:
                    QMessageBox.warning(self, "Input Error", f"Section {i+1}: Invalid chainage format.")
                    return
                if f_ch >= t_ch:
                    QMessageBox.warning(self, "Input Error", f"Section {i+1}: 'From' must be less than 'To'.")
                    return
                if f_ch < last_to:
                    QMessageBox.warning(self, "Input Error", f"Section {i+1} overlaps with previous section.")
                    return
                if w <= 0:
                    QMessageBox.warning(self, "Input Error", f"Section {i+1}: Width must be > 0.")
                    return
                
                last_to = t_ch
            
            self.accept()

    def get_width(self):
        """Retained for compatibility, returns single width if in normal mode"""
        if self.radio_normal.isChecked():
            text = self.width_input.text().strip()
            try: return float(text)
            except: return None
        return None

    def get_configuration(self):
        """Returns the full configuration as a dict"""
        if self.radio_normal.isChecked():
            width = self.get_width()
            return {
                'mode': 'normal',
                'width': width,
                'sections': []
            }
        else:
            sections = []
            for row in self.section_rows:
                sections.append({
                    'from_ch': self.parse_chainage(row['from'].text()),
                    'to_ch': self.parse_chainage(row['to'].text()),
                    'width': float(row['width'].text() or 0),
                    'from_ch_str': row['from'].text(),
                    'to_ch_str': row['to'].text()
                })
            return {
                'mode': 'lane_drop',
                'sections': sections
            }


# =======================================================================================================================================
# ADD THIS NEW DIALOG CLASS TO dialogs.py (or inline if preferred)
# =======================================================================================================================================
class MaterialSegmentDialog(QDialog):
    """Simplified Material Segment Dialog - Only user input fields, no API calls"""
    def __init__(self, material_thickness=None, width=None, after_rolling=None, material_description=None, from_chainage=None, to_chainage=None, from_chainage_m=None, to_chainage_m=None, parent=None, auto_save=False, **kwargs):
        super().__init__(parent)
        self.setWindowTitle("Material Segment Configuration")
        self.setModal(True)
        self.setMinimumWidth(550)
        self.setMinimumHeight(550)
        self.parent = parent
        self.auto_save = auto_save
        # aniket added these lines on 02-05-2026 to store material index and road surfacing permission for later use in processing
        self.material_index = kwargs.get('material_index', None)
        self.road_surfacing_allowed = self._resolve_road_surfacing_permission()
        # -----------------------------------------------------------
        # Store numeric chainage values (in meters)
        # Priority: numeric params > formatted string params
        if from_chainage_m is not None:
            self.from_chainage_m = from_chainage_m
        elif isinstance(from_chainage, (int, float)):
            self.from_chainage_m = from_chainage
        else:
            self.from_chainage_m = None
            
        if to_chainage_m is not None:
            self.to_chainage_m = to_chainage_m
        elif isinstance(to_chainage, (int, float)):
            self.to_chainage_m = to_chainage
        else:
            self.to_chainage_m = None
        
        # Store display strings for UI purposes
        self.from_chainage_display = from_chainage if isinstance(from_chainage, str) else None
        self.to_chainage_display = to_chainage if isinstance(to_chainage, str) else None

        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #e6e6fa, stop:1 #e6e6fa);
                border-radius: 20px;
            }
            QLabel {
                color: black;
                font-weight: 500;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                border: 2px solid #9C27B0;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                selection-background-color: #CE93D8;
                font-weight: 500;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #7B1FA2;
                background-color: #F3E5F5;
            }
            QPushButton {
                border-radius: 20px;
                padding: 10px;
                font-weight: bold;
                min-width: 100px;
                border: none;
            }
            QPushButton#okBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #9C27B0, stop:1 #6A1B9A);
                color: white;
            }
            QPushButton#okBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #AB47BC, stop:1 #4A148C);
            }
            QPushButton#cancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333333;
            }
            QPushButton#cancelBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #D1C4E9, stop:1 #BA68C8);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Title
        title_label = QLabel("Material Layer Configuration")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4A148C;")
        layout.addWidget(title_label)

        # Chainage Range (if provided)
        display_from = self.from_chainage_display or (f"{self.from_chainage_m:.3f}m" if self.from_chainage_m is not None else "N/A")
        display_to = self.to_chainage_display or (f"{self.to_chainage_m:.3f}m" if self.to_chainage_m is not None else "N/A")
        
        if self.from_chainage_m is not None or self.to_chainage_m is not None:
            chainage_layout = QHBoxLayout()
            chainage_label = QLabel("Chainage Range:")
            chainage_label.setFixedWidth(120)
            chainage_value = QLabel(f"{display_from} - {display_to}")
            chainage_value.setStyleSheet("font-weight: bold; color: #6A1B9A;")
            chainage_layout.addWidget(chainage_label)
            chainage_layout.addWidget(chainage_value, 1)
            layout.addLayout(chainage_layout)

        # 1. Material Description
        desc_layout = QHBoxLayout()
        desc_label = QLabel("Description:")
        desc_label.setFixedWidth(120)
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter material description...")
        self.description_edit.setMaximumHeight(80)
        if material_description:
            self.description_edit.setText(str(material_description))
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.description_edit, 1)
        layout.addLayout(desc_layout)

    # ====== Aniket Added on 01-05-2026: Chainage display fields with auto-calculation from numeric values and parsing ======
        # Chainage display fields (auto-calculated from numeric chainage values)
        def _format_chainage_from_meters(val):
            try:
                if val is None:
                    return "", ""
                m = float(val)
                km = int(m // 1000)
                ch = m - (km * 1000)
                # Round chainage to nearest meter for display
                ch_int = int(round(ch))
                km_str = str(km)
                ch_str = f"{km}+{ch_int:03d}"
                return km_str, ch_str
            except Exception:
                return "", ""

        def _parse_chainage_display(s):
            # Accept formats like '101+060' or '101+060.000' or simple numeric
            if not s:
                return "", ""
            try:
                if isinstance(s, (int, float)):
                    return _format_chainage_from_meters(float(s))
                if "+" in s:
                    parts = s.split("+")
                    km = parts[0].strip()
                    ch = parts[1].strip()
                    # normalize chainage part to integer meters when possible
                    try:
                        ch_val = float(ch)
                        ch_int = int(round(ch_val))
                        return km, f"{km}+{ch_int:03d}"
                    except:
                        return km, s
                # fallback: try numeric meters
                m = float(s)
                return _format_chainage_from_meters(m)
            except Exception:
                return "", ""

        # Simple chainage row: only From Ch and To Ch (integer meters)
        from_ch_label = QLabel("From Ch:")
        self.from_chain_edit = QLineEdit()
        self.from_chain_edit.setReadOnly(True)
        self.from_chain_edit.setFixedWidth(150)

        to_ch_label = QLabel("To Ch:")
        self.to_chain_edit = QLineEdit()
        self.to_chain_edit.setReadOnly(True)
        self.to_chain_edit.setFixedWidth(150)

        def _chainage_to_meters(val):
            # Accept numeric meters or formats like '101+060'
            if val is None:
                return None
            try:
                if isinstance(val, (int, float)):
                    return int(round(float(val)))
                s = str(val).strip()
                if not s:
                    return None
                if "+" in s:
                    parts = s.split("+")
                    km = float(parts[0].strip())
                    ch = float(parts[1].strip())
                    meters = int(round(km * 1000 + ch))
                    return meters
                # fallback: plain numeric meters
                return int(round(float(s)))
            except Exception:
                return None

        # Prefer numeric meter inputs, then parse display strings
        from_m = _chainage_to_meters(self.from_chainage_m) if self.from_chainage_m is not None else _chainage_to_meters(self.from_chainage_display)
        to_m = _chainage_to_meters(self.to_chainage_m) if self.to_chainage_m is not None else _chainage_to_meters(self.to_chainage_display)

        self.from_chain_edit.setText(str(from_m) if from_m is not None else "")
        self.to_chain_edit.setText(str(to_m) if to_m is not None else "")

        chainage_row = QHBoxLayout()
        chainage_row.addWidget(from_ch_label)
        chainage_row.addWidget(self.from_chain_edit)
        chainage_row.addSpacing(30)
        chainage_row.addWidget(to_ch_label)
        chainage_row.addWidget(self.to_chain_edit)

        layout.addLayout(chainage_row)
    # ==========================================================================================

        # 2. Material Thickness (Before)
        thick_layout = QHBoxLayout()
        thick_label = QLabel("Before Thickness (m):")
        thick_label.setFixedWidth(120)
        self.thickness_edit = QLineEdit()
        self.thickness_edit.setPlaceholderText("Enter thickness value")
        if material_thickness:
            self.thickness_edit.setText(str(material_thickness))
        thick_layout.addWidget(thick_label)
        thick_layout.addWidget(self.thickness_edit, 1)
        layout.addLayout(thick_layout)

        # 3. After Rolling Thickness
        rolling_layout = QHBoxLayout()
        rolling_label = QLabel("After Rolling (mm):")
        rolling_label.setFixedWidth(120)
        self.after_rolling_edit = QLineEdit()
        self.after_rolling_edit.setPlaceholderText("Enter thickness after rolling")
        if after_rolling:
            self.after_rolling_edit.setText(str(after_rolling))
        rolling_layout.addWidget(rolling_label)
        rolling_layout.addWidget(self.after_rolling_edit, 1)
        layout.addLayout(rolling_layout)

        # 4. Material Width
        width_layout = QHBoxLayout()
        width_label = QLabel("Material Width (m):")
        width_label.setFixedWidth(120)
        self.width_edit = QLineEdit()
        self.width_edit.setPlaceholderText("Enter width in meters")
        if width:
            self.width_edit.setText(str(width))
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_edit, 1)
        layout.addLayout(width_layout)

        # 5. Position Type
        position_group = QGroupBox("Filling Position")
        position_group.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; margin-top: 10px; }")
        position_layout = QHBoxLayout(position_group)
        self.above_ground_radio = QRadioButton("Above Ground Surface")
        self.below_ground_radio = QRadioButton("Below Ground Surface")
        self.above_ground_radio.setChecked(False) # default is above (trapezoidal)

        # --- Aniket added on 02-05-2026: If road surfacing is not allowed for this material line, force below ground selection and disable above ground option ---

        # If Road Surfacing/Resurfacing is not enabled for this material line,
        # only below-ground filling is allowed.
        if not self.road_surfacing_allowed:
            self.below_ground_radio.setChecked(False)
        # ----------------------------------------------------------------------

        position_layout.addWidget(self.above_ground_radio)
        position_layout.addWidget(self.below_ground_radio)
        layout.addWidget(position_group)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("okBtn")
        ok_btn.clicked.connect(self.on_ok_clicked)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    # ----------------- Aniket added on 02-05-2026: Method to determine if above-ground filling is allowed based on material line config -----------------
    def _resolve_road_surfacing_permission(self):
        """Return True if active material line allows above-road-surface filling."""
        try:
            if not self.parent or not hasattr(self.parent, 'material_configs'):
                return True

            idx = self.material_index
            if idx is None:
                idx = getattr(self.parent, 'active_material_index', None)

            if idx is None:
                return True

            idx = int(idx)
            if idx < 0 or idx >= len(self.parent.material_configs):
                return True

            cfg = self.parent.material_configs[idx] or {}
            return bool(cfg.get('road_surfacing', cfg.get('road_resurfacing', False)))
        except Exception:
            return True

    # -----------------------------------------------------------------------------
    def on_ok_clicked(self):
        """Validate input and save material data"""
        description = self.description_edit.toPlainText().strip()
        
        try:
            thickness = float(self.thickness_edit.text().strip() or 0)
            after_rolling = float(self.after_rolling_edit.text().strip() or 0)
            width = float(self.width_edit.text().strip() or 0)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric values for thickness, rolling thickness, and width.")
            return

        if not description:
            QMessageBox.warning(self, "Input Required", "Please enter material description.")
            return

        if width <= 0:
            QMessageBox.warning(self, "Input Error", "Material width must be greater than 0.")
            return
        # ------------- Aniket added on 02-05-2026: If road surfacing is not allowed for this material line, BLOCK above-ground filling selection -------------
        if self.above_ground_radio.isChecked() and not self.road_surfacing_allowed:
            QMessageBox.warning(self, "Road Surfacing Required", "You can not fill the material above the Road Surface")
            return  # Hard block: prevent dialog acceptance and data save

        # ---------------------------------------------------------------------------------
        # Fill material in graph with hatching (delegate to parent if available)
        if self.parent and hasattr(self.parent, 'draw_material_hatching'):
            try:
                self.parent.draw_material_hatching(description, width)
            except Exception as e:
                print(f"Warning: Could not draw material hatching: {e}")

        # Save material data to unified JSON file (optional for edit flows)
        if self.auto_save:
            self.save_material_data(description, thickness, after_rolling, width)

        self.accept()

    def get_is_below_ground(self):
        return self.below_ground_radio.isChecked()

    def save_material_data(self, description, thickness, after_rolling, width):
        """Save material data to material_construction_config.json"""
        from json_manager import DesignConstructionManager
        
        try:
            if not self.parent or not hasattr(self.parent, 'current_construction_layer_path'):
                print("Warning: Construction layer path not available")
                return

            construction_path = self.parent.current_construction_layer_path
            
            # Build material entry
            material_entry = {
                'name': description,
                'description': description,
                'before_thickness_mm': thickness * 1000,
                'after_rolling_thickness_mm': after_rolling,
                'width_m': width,
                'is_below_ground': self.get_is_below_ground(),
                'timestamp': datetime.now().isoformat(),
                'saved_by': getattr(self.parent, 'current_user', 'user')
            }

            # Load existing materials from unified file
            unified_file_path = os.path.join(construction_path, 'material_construction_config.json')
            materials_list = []

            if os.path.exists(unified_file_path):
                try:
                    with open(unified_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        materials_list = data.get('materials', [])
                except Exception as e:
                    print(f"Warning: Could not load existing materials: {e}")
                    materials_list = []

            # Add new material
            materials_list.append(material_entry)

            # Save updated materials to unified file
            unified_data = {
                'materials': materials_list,
                'last_updated': datetime.now().isoformat(),
                'updated_by': getattr(self.parent, 'current_user', 'user')
            }

            # Keep material line config as a separate object in the same unified JSON.
            # Source of truth is material_lines_config.txt in construction root.
            material_lines_config_path = os.path.join(construction_path, 'material_lines_config.txt')
            if os.path.exists(material_lines_config_path):
                try:
                    with open(material_lines_config_path, 'r', encoding='utf-8') as f:
                        unified_data['material_lines_config'] = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load material_lines_config.txt: {e}")
            elif os.path.exists(unified_file_path):
                # Preserve existing object if file not found right now.
                try:
                    with open(unified_file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                    if isinstance(existing_data, dict) and 'material_lines_config' in existing_data:
                        unified_data['material_lines_config'] = existing_data['material_lines_config']
                except Exception as e:
                    print(f"Warning: Could not preserve existing material_lines_config: {e}")

            os.makedirs(construction_path, exist_ok=True)
            with open(unified_file_path, 'w', encoding='utf-8') as f:
                json.dump(unified_data, f, indent=2, ensure_ascii=False)

            print(f"✓ Material '{description}' saved to {unified_file_path}")
            
            if self.parent and hasattr(self.parent, 'message_text'):
                self.parent.message_text.append(f"✓ Material saved: {description} (Width: {width}m, Before: {thickness}mm, After: {after_rolling}mm)")

        except Exception as e:
            print(f"Error saving material data: {e}")
            if self.parent and hasattr(self.parent, 'message_text'):
                self.parent.message_text.append(f"✗ Error saving material: {str(e)}")

    def get_data(self):
        """Return material configuration data with numeric chainage values"""
        try:
            thickness_val = float(self.thickness_edit.text() or 0)
        except:
            thickness_val = 0.0

        try:
            after_roll_val = float(self.after_rolling_edit.text() or 0) / 1000.0
        except:
            after_roll_val = 0.0

        try:
            width_val = float(self.width_edit.text() or 0)
        except:
            width_val = 0.0

        data = {
            'description': self.description_edit.toPlainText().strip(),
            'material_thickness_m': thickness_val,  # Already in meters
            'after_rolling_thickness_m': after_roll_val,  # Convert mm to m
            'width_m': width_val,
            'is_below_ground': self.get_is_below_ground()
        }
        # Add numeric chainage values (MUST be floats, not strings)
        if self.from_chainage_m is not None:
            data['from_chainage_m'] = float(self.from_chainage_m)
        if self.to_chainage_m is not None:
            data['to_chainage_m'] = float(self.to_chainage_m)
        
        return data


# ======================================================================================================================================================================
#                                                     ** NEW MATERIAL LINE DIALOG CLASS **
# ======================================================================================================================================================================
class NewMaterialLineDialog(QDialog):
    """Dialog for creating a new material line."""
    def __init__(self, material_config=None, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.material_config = material_config or {}
        self.is_edit_mode = bool(material_config)
        
        # Ensure available_materials exists by checking parent first
        self.available_materials = getattr(self.parent, 'available_materials', [])
        
        # If parent didn't have materials, try fetching from API
        if not self.available_materials:
            try:
                from API import WorksheetAPI
                fetched_materials = WorksheetAPI.get_road_materials()
                if fetched_materials:
                    self.available_materials = fetched_materials
            except Exception as e:
                print(f"Error importing API or fetching materials: {e}")
        
        title = "Create New Material Line" if self.is_edit_mode else "Create New Material Line"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f0e6fa, stop:1 #e6e6fa);
                border-radius: 20px;
            }
            QLabel { color: black; font-weight: 500; font-size: 14px; }
            QLineEdit {
                border: 2px solid #9C27B0; border-radius: 8px; padding: 8px;
                background-color: white;
            }
            QLineEdit:focus { border: 2px solid #7B1FA2; background-color: #F3E5F5; }
            QLineEdit[readOnly="true"] { background-color: #f0f0f0; color: #555555; }
            QPushButton { border-radius: 20px; padding: 10px; font-weight: bold; min-width: 120px; border: none; }
            QPushButton#saveBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9C27B0, stop:1 #6A1B9A);
                color: white;
            }
            QPushButton#saveBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #AB47BC, stop:1 #4A148C);
            }
            QPushButton#cancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333333;
            }
            QPushButton#cancelBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D1C4E9, stop:1 #BA68C8);
            }
        """)

        self.load_table_data()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000; padding-bottom: 15px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Material Line Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Material Layer Name:")
        name_label.setFixedWidth(150)
        self.name_input = QLineEdit()
        
        # Always start empty — user types whatever they want
        self.name_input.clear()
        self.name_input.setPlaceholderText("Enter any name: e.g. Material 1, Material 2, etc.")
        
        # Optional: helpful tooltip
        self.name_input.setToolTip("Type the exact name for this material layer (fully customizable)")

        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input, 1)
        layout.addLayout(name_layout)

        # Material Type (Dropdown)
        type_layout = QHBoxLayout()
        type_label = QLabel("Material Name:")
        type_label.setFixedWidth(150)
        
        self.material_combo = QComboBox()
        self.material_combo.addItem("Select Material", None)
        
        # Populate dropdown
        if self.available_materials:
            for mat in self.available_materials:
                name = 'Unknown'
                rmh_id = None
                
                if isinstance(mat, dict):
                    name = mat.get('material_name', 'Unknown')
                    rmh_id = mat.get('rmh_id')
                    if rmh_id is None: rmh_id = mat.get('id')
                elif isinstance(mat, str):
                    name = mat
                    rmh_id = None

                self.material_combo.addItem(name, rmh_id)
        else:
            self.material_combo.addItem("No materials found", None)
        
        if self.is_edit_mode:
            target_name = self.material_config.get('material_type', '')
            if target_name:
                idx = self.material_combo.findText(target_name)
                if idx >= 0:
                    self.material_combo.setCurrentIndex(idx)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.material_combo, 1)
        layout.addLayout(type_layout)

        # =============== Aniket Pund - Added on 01-05-2025 (For the Road Resurfacing Functionality) =================
        # Road Surfacing checkbox (above the table)
        self.road_surfacing_checkbox = QCheckBox("Road Surfacing")
        self.road_surfacing_checkbox.setStyleSheet("QCheckBox { font-weight: 500; font-size: 14px; font: bold; }")
        self.road_surfacing_checkbox.setChecked(False)
        layout.addWidget(self.road_surfacing_checkbox)
        # ============================================================================================================

        # Table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setSpacing(15)

        header = QHBoxLayout()
        headers = ["From", "→", "To", "Reference Name"]
        for i, text in enumerate(headers):
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)

            # *** Changes made by Aniket Pund on 01-05-2025 for better alignment of header labels with input fields in the rows below ***
            if i in (0, 2):
                label.setFixedWidth(130)
            elif i == 1:
                label.setFixedWidth(20)
            elif i == 3:
                label.setFixedWidth(200)
            # ============================================================================================================
            header.addWidget(label)
            if i == 0: header.addSpacing(5)
            elif i == 1: header.addSpacing(5)
            elif i == 2: header.addSpacing(5)
            elif i == 3: header.addSpacing(40)

        table_layout.addLayout(header)

        self.segment_rows = []

        if self.table_data:
            for idx, item in enumerate(self.table_data):
                row = self.create_row(idx, item, is_edit_mode=self.is_edit_mode)
                table_layout.addLayout(row['layout'])
                self.segment_rows.append(row)
        else:
            for i in range(3):
                row = self.create_row(i, None, is_edit_mode=False)
                table_layout.addLayout(row['layout'])
                self.segment_rows.append(row)

        layout.addWidget(table_widget)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)


    def load_table_data(self):
        """Load and split references using EXACT chainage strings from JSON files."""
        self.table_data = []

        if not self.parent or not hasattr(self.parent, 'current_construction_layer_path'):
            return

        construction_path = self.parent.current_construction_layer_path
        worksheet_root = os.path.abspath(os.path.join(construction_path, "..", ".."))
        designs_path = os.path.join(worksheet_root, "designs")

        # === Step 1: Get Construction baseline full range (with exact strings) ===
        overall_start_str = overall_end_str = ""
        overall_start_m = overall_end_m = None

        ref_design_layer = ""
        
        # Check Construction_Layer_config.txt
        const_config_path = os.path.join(construction_path, "Construction_Layer_config.txt")
        if os.path.exists(const_config_path):
            try:
                with open(const_config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                ref_design_layer = data.get("reference_layer_2d", "")
            except: pass

        reference_name = "Construction"
        # User mentioned material_lines_config.txt for reference name
        mat_line_config_path = os.path.join(construction_path, "material_lines_config.txt")
        if os.path.exists(mat_line_config_path):
            try:
                with open(mat_line_config_path, 'r', encoding='utf-8') as f:
                    mat_data = json.load(f)
                
                mat_lines = mat_data.get("material_line", [])
                if isinstance(mat_lines, list) and len(mat_lines) > 0:
                    first_line = mat_lines[0] # The base reference is what the FIRST material was built on
                    if first_line.get("ref_layer"):
                        reference_name = first_line.get("ref_layer")
            except: pass

        from json_manager import DesignConstructionManager
        
        baseline_data = None
        if ref_design_layer:
            layer_root = os.path.join(designs_path, ref_design_layer)
            if os.path.exists(layer_root):
                baseline_data = DesignConstructionManager.get_design_construction_baseline(layer_root)
            
        # VERY IMPORTANT FALLBACK: If not found, scan all design layers!
        if not baseline_data and os.path.exists(designs_path):
            for d in os.listdir(designs_path):
                d_path = os.path.join(designs_path, d)
                if os.path.isdir(d_path):
                    b_data = DesignConstructionManager.get_design_construction_baseline(d_path)
                    if b_data and b_data.get("polylines"):
                        baseline_data = b_data
                        break

        if baseline_data:
            try:
                polylines = baseline_data.get("polylines", [])
                all_pts = []
                for poly in polylines:
                    all_pts.extend(poly.get("points", []))
                if all_pts:
                    all_pts.sort(key=lambda p: float(p.get("chainage_m", 0)))
                    first = all_pts[0]
                    last = all_pts[-1]
                    overall_start_m = float(first.get("chainage_m"))
                    overall_end_m = float(last.get("chainage_m"))
                    overall_start_str = first.get("chainage_str", f"{overall_start_m:.3f}" if overall_start_m else "")
                    overall_end_str = last.get("chainage_str", f"{overall_end_m:.3f}" if overall_end_m else "")
            except Exception as e:
                print(f"Error loading construction baseline: {e}")

        if not overall_start_str or not overall_end_str:
            return

        # === Step 2: Collect all existing material lines from material_construction_config.json ===
        material_coverages = []  # List of (start_m, end_m, name, from_str, to_str, json_data)

        unified_file_path = os.path.join(construction_path, 'material_construction_config.json')
        if os.path.exists(unified_file_path):
            try:
                with open(unified_file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                materials_list = config_data.get("materials", [])
                for data in materials_list:
                    material_name = (
                        data.get("material_line_name") or
                        data.get("material_line_id") or
                        data.get("name") or 
                        data.get("material_line_folder") or
                        "Unknown Material"
                    )

                    from_info = data.get("overall_from_chainage", {})
                    to_info = data.get("overall_to_chainage", {})

                    start_m = from_info.get("chainage_m")
                    end_m = to_info.get("chainage_m")
                    from_str = from_info.get("chainage_str", f"{start_m:.3f}" if start_m is not None else "")
                    to_str = to_info.get("chainage_str", f"{end_m:.3f}" if end_m is not None else "")

                    if start_m is not None and end_m is not None and from_str and to_str and end_m > start_m:
                        material_coverages.append((start_m, end_m, material_name, from_str, to_str, data))
            except Exception as e:
                print(f"Error loading material_construction_config.json: {e}")

        # Sort by start chainage
        material_coverages.sort(key=lambda x: x[0])

        # === Step 3: Build segmented rows using exact strings ===
        segments = []
        current_pos_m = overall_start_m

        for start_m, end_m, mat_name, from_str, to_str, mat_data in material_coverages:
            # Add segment before this material (if gap exists)
            if current_pos_m is not None and start_m > current_pos_m + 0.001:  # tolerance for float
                segments.append({
                    'from': overall_start_str if len(segments) == 0 else segments[-1]['to'],
                    'to': from_str,
                    'name': reference_name,
                    'width': "",
                    'initial': 0,
                    'final': 0
                })

            # Add the material segment with exact strings
            width = initial = final = ""
            segs = mat_data.get("segments", [])
            if segs:
                s = segs[0]
                width = s.get("width_m", "")
                initial = s.get("material_thickness_m", 0)
                final = s.get("after_rolling_thickness_m", 0)

            segments.append({
                'from': from_str,
                'to': to_str,
                'name': mat_name,
                'width': width,
                'initial': initial,
                'final': final
            })

            current_pos_m = end_m

        # Add final segment
        if current_pos_m is not None and overall_end_m > current_pos_m + 0.001:
            last_to = overall_end_str
            from_for_last = material_coverages[-1][4] if material_coverages else overall_start_str
            segments.append({
                'from': from_for_last,
                'to': last_to,
                'name': reference_name,
                'width': "",
                'initial': 0,
                'final': 0
            })

        # If no materials, just full range
        if not segments:
            segments.append({
                'from': overall_start_str,
                'to': overall_end_str,
                'name': reference_name,
                'width': "",
                'initial': 0,
                'final': 0
            })

        self.table_data = segments

    def create_row(self, index, item_data, is_edit_mode=False):
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)

        checkbox = QCheckBox()
        if is_edit_mode and item_data:
            ref_layer = self.material_config.get('ref_layer')
            if isinstance(ref_layer, list):
                checkbox.setChecked(item_data['name'] in ref_layer)
            else:
                checkbox.setChecked(str(item_data['name']).lower() == str(ref_layer).lower())
        else:
            checkbox.setChecked(True)

        row_layout.addWidget(checkbox)

        from_edit = QLineEdit(str(item_data['from']) if item_data else "")
        from_edit.setReadOnly(True)
        from_edit.setFixedWidth(130)
        row_layout.addWidget(from_edit)

        row_layout.addWidget(QLabel("→"), alignment=Qt.AlignCenter)

        to_edit = QLineEdit(str(item_data['to']) if item_data else "")
        to_edit.setReadOnly(True)
        to_edit.setFixedWidth(130)
        row_layout.addWidget(to_edit)

        name_label = QLineEdit(item_data['name'] if item_data else "Unknown")
        name_label.setReadOnly(True)
        name_label.setFixedWidth(200)
        row_layout.addWidget(name_label, alignment=Qt.AlignCenter)

        row_layout.addStretch()

        return {
            'layout': row_layout,
            'checkbox': checkbox,
            'from': from_edit,
            'to': to_edit,
            'material_name': name_label
        }


    def on_save(self):
        updated_segments = []
        checked_refs = []

        for row in self.segment_rows:
            if not row['checkbox'].isChecked():
                continue
            ref_name = row['material_name'].text().strip()
            checked_refs.append(ref_name)

            updated_segments.append({
                'from_chainage': row['from'].text().strip(),
                'to_chainage': row['to'].text().strip(),
                'ref_layer': ref_name
            })

        if not updated_segments:
            QMessageBox.warning(self, "Error", "At least one reference must be selected")
            return

        # === SECURITY: Force user to enter a name ===
        material_name = self.name_input.text().strip()
        if not material_name:
            QMessageBox.warning(self, "Required Field", "Please enter a Material line name.")
            return

        # Use the validated name
        proposed_name = material_name

        # === ENFORCE UNIQUE NAME (your existing logic preserved) ===
        existing_names = [cfg['name'] for cfg in getattr(self.parent, 'material_configs', [])]

        if self.is_edit_mode:
            current_original_name = self.material_config.get('name', '')
            if proposed_name != current_original_name and proposed_name in existing_names:
                QMessageBox.warning(self, "Duplicate Name",
                                    f"A material named '{proposed_name}' already exists.\n"
                                    "Please choose a unique name.")
                return
        else:
            if proposed_name in existing_names:
                counter = 1
                base_name = proposed_name
                while f"{base_name} ({counter})" in existing_names:
                    counter += 1
                unique_name = f"{base_name} ({counter})"
                reply = QMessageBox.question(self, "Name Conflict",
                                             f"'{proposed_name}' already exists.\n"
                                             f"Use '{unique_name}' instead?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    proposed_name = unique_name
                else:
                    return

        material_type = self.material_combo.currentText()
        rmh_id = self.material_combo.currentData()

        unique_refs = list(dict.fromkeys(checked_refs))
        ref_layer_value = unique_refs[0] if len(unique_refs) == 1 else unique_refs

        self.result_data = {
            'name': proposed_name,
            'material_type': material_type,
            'rmh_id': rmh_id,
            'ref_layer': ref_layer_value,
            'segments': updated_segments,
            'road_surfacing': bool(self.road_surfacing_checkbox.isChecked())
        }

        self.accept()

    def get_material_data(self):
        return getattr(self, 'result_data', None)

# ===========================================================================================================================
#                                  ** Merger Layer Configuration **
# ===========================================================================================================================
class MergerLayerConfigDialog(QDialog):
    def __init__(self, parent=None, worksheet_root=None):
        super().__init__(parent)
        self.setWindowTitle("Merger Layer Configuration")
        self.setModal(True)
        self.setMinimumSize(900, 600)

        self.worksheet_selection_widgets = {}   # moved from create_merger_point_widget
        
        # Store dynamic widgets
        self.worksheet_root = worksheet_root
        self.merger_points_widgets = []

        # Add dictionary to store verified world coordinates
        self.verified_coordinates = {}
        
        # Tolerance for coordinate matching (in meters)
        self.coordinate_tolerance = 100.0

        # Add dictionary to store loaded baseline data for each layer
        self.loaded_baseline_data = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Merger Layer Configuration")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #4A148C; 
            padding: 10px;
        """)
        layout.addWidget(title)
        
        # Layer Name
        layer_name_layout = QHBoxLayout()
        layer_name_label = QLabel("Layer Name:")
        layer_name_label.setStyleSheet("font-weight: bold;")
        layer_name_layout.addWidget(layer_name_label)
        self.layer_name_input = QLineEdit()
        self.layer_name_input.setPlaceholderText("Enter Merger Layer Name")
        layer_name_layout.addWidget(self.layer_name_input)
        layout.addLayout(layer_name_layout)
        
        # Merger Points - Remove space between label and input
        merger_points_layout = QHBoxLayout()        
        merger_points_label = QLabel("Merger Points:")
        merger_points_label.setStyleSheet("font-weight: bold;")
        merger_points_layout.addWidget(merger_points_label)
        
        self.merger_points_input = QLineEdit()
        self.merger_points_input.setPlaceholderText("Enter no. of merger points")
        self.merger_points_input.setFixedWidth(200)
        merger_points_layout.addWidget(self.merger_points_input)
        
        # Add some spacing before the button
        merger_points_layout.addSpacing(10)
        merger_points_layout.addStretch(1)
        
        self.create_merger_points_btn = QPushButton("Create Merger Points")
        self.create_merger_points_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #388E3C;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
        """)
        self.create_merger_points_btn.clicked.connect(self.create_merger_points)
        merger_points_layout.addWidget(self.create_merger_points_btn)
        merger_points_layout.addStretch()
        
        layout.addLayout(merger_points_layout)
        
        # Scroll area for dynamic merger points
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.merger_points_container = QWidget()
        self.merger_points_layout = QVBoxLayout(self.merger_points_container)
        self.merger_points_layout.setSpacing(15)
        
        # Create placeholder label
        self.placeholder_label = QLabel("No merge points created yet.\nEnter number of merge points above and click 'Create Merge Points'.")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                color: #757575;
                font-style: italic;
                padding: 20px;
                border: 1px dashed #BDBDBD;
                border-radius: 5px;
                background-color: #FAFAFA;
            }
        """)
        self.merger_points_layout.addWidget(self.placeholder_label)
        
        scroll_area.setWidget(self.merger_points_container)
        layout.addWidget(scroll_area)
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #388E3C;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
        """)
        self.save_btn.clicked.connect(self.save_config)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")  # Add object name for specific styling
        self.cancel_btn.setStyleSheet("""
            QPushButton#cancelBtn {
                background-color: #F44336;
                color: white;
                border: 2px solid #D32F2F;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton#cancelBtn:hover {
                background-color: #FFCDD2;
            }
            QPushButton#cancelBtn:pressed {
                background-color: #D32F2F;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Apply main dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                border: 2px solid #9C27B0;
                border-radius: 10px;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit {
                border: 1px solid #9C27B0;
                border-radius: 4px;
                padding: 6px;
            }
            QGroupBox {
                border: 1px solid #7B1FA2;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: #4A148C;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QScrollArea {
                border: 1px solid #BA68C8;
                border-radius: 6px;
                background-color: white;
            }
        """)
        
    def create_merger_points(self):
        """Create merger points based on user input"""
        try:
            num_points = int(self.merger_points_input.text().strip())
            if num_points <= 0:
                QMessageBox.warning(self, "Invalid Input", "Please enter a positive number for merger points")
                return
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for merger points")
            return
        
        # Clear existing merger points
        self.clear_merger_points()
        
        # Hide placeholder label
        self.placeholder_label.hide()
        
        # Create new merger points
        for i in range(1, num_points + 1):
            merger_point_widget = self.create_merger_point_widget(i)
            self.merger_points_widgets.append(merger_point_widget)
            self.merger_points_layout.addWidget(merger_point_widget)
            
    def create_merger_point_widget(self, point_number):
        group_box = QGroupBox(f"Merger Point {point_number}")
        layout = QVBoxLayout(group_box)

        # --- Layer count input ---
        layer_input_layout = QHBoxLayout()
        layer_input_label = QLabel("Enter no. of layers:")
        layer_input_label.setStyleSheet("font-weight: bold;")
        layer_input_layout.addWidget(layer_input_label)
        layer_input_layout.setSpacing(15)

        layer_count_input = QLineEdit()
        layer_count_input.setPlaceholderText("___________")
        layer_count_input.setFixedWidth(100)
        layer_count_input.textChanged.connect(lambda: self.check_selection_count(point_number))
        layer_input_layout.addWidget(layer_count_input)

        layer_input_layout.addStretch(1)

        merger_type_label = QLabel("Merger Type:")
        merger_type_label.setStyleSheet("font-weight: bold;")
        layer_input_layout.addWidget(merger_type_label)

        layer_input_layout.addSpacing(15)
        merger_type_dropdown = QComboBox()
        merger_type_dropdown.setFixedWidth(250)
        merger_type_dropdown.addItem("Road & Road")  # Default option
        merger_type_dropdown.addItem("Road & Bridge")  # New option for bridge+road merging
        merger_type_dropdown.setStyleSheet("""
            QComboBox {
                border: 1px solid #9C27B0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QComboBox::drop-down {
                border-left: 1px solid #9C27B0;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        layer_input_layout.addWidget(merger_type_dropdown)
        layer_input_layout.addStretch()
        layout.addLayout(layer_input_layout)

        # --- Multi-user selection ---
        user_selection_layout = QHBoxLayout()
        user_label = QLabel("Select Users:")
        user_label.setStyleSheet("font-weight: bold;")
        user_selection_layout.addWidget(user_label)

        user_combo = QComboBox()
        user_combo.setFixedWidth(150)
        self.populate_users_combo(user_combo)
        user_selection_layout.addWidget(user_combo)

        add_user_btn = QPushButton("Add User")
        add_user_btn.clicked.connect(lambda: self.add_user_to_list(point_number))
        user_selection_layout.addWidget(add_user_btn)

        remove_user_btn = QPushButton("Remove User")
        remove_user_btn.clicked.connect(lambda: self.remove_user_from_list(point_number))
        user_selection_layout.addWidget(remove_user_btn)
        user_selection_layout.addStretch()
        layout.addLayout(user_selection_layout)

        users_list = QListWidget()
        users_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        users_list.setMaximumHeight(80)
        layout.addWidget(QLabel("Selected Users:"))
        layout.addWidget(users_list)

        # --- Worksheet selection area (initially hidden) ---
        selection_widget = QWidget()
        selection_layout = QVBoxLayout(selection_widget)
        selection_layout.setContentsMargins(0, 5, 0, 5)

        worksheet_combo = QComboBox()
        worksheet_combo.setEnabled(False)
        selection_layout.addWidget(QLabel("Select a worksheet and click Add:"))
        selection_layout.addWidget(worksheet_combo)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Worksheet")
        remove_btn = QPushButton("Remove Selected")
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        selection_layout.addLayout(btn_layout)

        selected_list = QListWidget()
        selected_list.setSelectionMode(QAbstractItemView.SingleSelection)
        selection_layout.addWidget(QLabel("Selected worksheets:"))
        selection_layout.addWidget(selected_list)

        selection_info_label = QLabel("Select worksheets (must match number of layers)")
        selection_layout.addWidget(selection_info_label)

        confirm_btn = QPushButton("Confirm Worksheets and Create Layers")
        confirm_btn.setEnabled(False)
        selection_layout.addWidget(confirm_btn)

        layout.addWidget(selection_widget)
        selection_widget.setVisible(False)  # hidden until at least one user added

        # Store references - CRITICAL: assign all widgets to group_box
        group_box.layer_count_input = layer_count_input
        group_box.user_combo = user_combo
        group_box.users_list = users_list          # <-- ADD THIS LINE
        group_box.selection_widget = selection_widget
        group_box.worksheet_combo = worksheet_combo
        group_box.selected_list = selected_list
        group_box.confirm_btn = confirm_btn
        group_box.selection_info_label = selection_info_label
        group_box.expected_layers = 0

        # Connect signals
        add_btn.clicked.connect(lambda: self.add_worksheet_to_list(point_number))
        remove_btn.clicked.connect(lambda: self.remove_worksheet_from_list(point_number))
        confirm_btn.clicked.connect(lambda: self.create_layers_for_point(point_number))
                
        # Primary Layer selection
        primary_layer_layout = QHBoxLayout()
        
        primary_layer_label = QLabel("Select Primary Layer:")
        primary_layer_label.setStyleSheet("font-weight: bold;")
        primary_layer_layout.addWidget(primary_layer_label)

        primary_layer_layout.addSpacing(15)
        
        primary_layer_dropdown = QComboBox()
        primary_layer_dropdown.setFixedWidth(400)
        primary_layer_dropdown.setStyleSheet("""
            QComboBox {
                border: 1px solid #9C27B0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QComboBox::drop-down {
                border-left: 1px solid #9C27B0;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        primary_layer_layout.addWidget(primary_layer_dropdown)
        
        primary_layer_layout.addStretch()
        layout.addLayout(primary_layer_layout)

        layout.addSpacing(10)
            
        # Container for layers
        layers_container = QWidget()
        layers_container.layers_layout = QVBoxLayout(layers_container)
        layers_container.layers_layout.setSpacing(5)
        layout.addWidget(layers_container)

        # Connect Layers button (initially hidden)
        connect_layers_layout = QHBoxLayout()
        connect_layers_layout.addStretch()
        
        connect_layers_btn = QPushButton("Connect Layers")
        connect_layers_btn.setFixedWidth(150)
        connect_layers_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 2px solid #1976D2;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                border: 2px solid #9E9E9E;
                color: #757575;
            }
        """)
        connect_layers_btn.setVisible(False)  # Initially hidden
        connect_layers_btn.clicked.connect(lambda: self.connect_layers_for_point(point_number))
        
        connect_layers_layout.addWidget(connect_layers_btn)
        connect_layers_layout.addStretch()
        layout.addLayout(connect_layers_layout)
        
        # Store references for later use
        group_box.layers_container = layers_container
        group_box.layer_count_input = layer_count_input
        group_box.primary_layer_dropdown = primary_layer_dropdown  # Store the primary layer dropdown reference
        group_box.merger_type_dropdown = merger_type_dropdown  # Store the merger type dropdown reference (Road/Road & Bridge)
        group_box.connect_layers_btn = connect_layers_btn  # Store the connect layers button reference
        
        return group_box
    
    def connect_layers_for_point(self, point_number):
        """Handle Connect Layers button click for a specific merger point"""
        merger_point_widget = None
        for widget in self.merger_points_widgets:
            if widget.title() == f"Merger Point {point_number}":
                merger_point_widget = widget
                break

        if not merger_point_widget:
            return

        layers_info = []
        layer_paths = []
        layout = merger_point_widget.layers_container.layers_layout

        for i in range(layout.count()):
            child = layout.itemAt(i)
            if child and child.widget():
                widget = child.widget()

                selected_data = widget.layer_dropdown.currentData() if hasattr(widget, 'layer_dropdown') else None
                subfolder_type = ""
                if selected_data and isinstance(selected_data, tuple):
                    # Support both 3‑tuple (old) and 4‑tuple (new with subfolder)
                    if len(selected_data) == 4:
                        user_id, worksheet_name, actual_layer_name, subfolder_type = selected_data
                    elif len(selected_data) == 3:
                        user_id, worksheet_name, actual_layer_name = selected_data
                    else:
                        user_id = worksheet_name = actual_layer_name = ""
                else:
                    user_id = worksheet_name = ""
                    actual_layer_name = widget.layer_dropdown.currentText() if hasattr(widget, 'layer_dropdown') else ""

                chainage_value = widget.chainage_input.text().strip() if hasattr(widget, 'chainage_input') else ""
                verification_status = widget.verify_btn.text() if hasattr(widget, 'verify_btn') else "Not Verified"
                is_verified = widget.verify_btn.text() == "✓" if hasattr(widget, 'verify_btn') else False

                # Build correct filesystem path using subfolder_type if available
                if user_id and worksheet_name and actual_layer_name:
                    if subfolder_type:
                        layer_path = os.path.join(r"C:\3D_Tool\user", user_id, subfolder_type, worksheet_name, "designs", actual_layer_name)
                    else:
                        # Fallback for older data without road/bridge subfolder
                        layer_path = os.path.join(r"C:\3D_Tool\user", user_id, worksheet_name, "designs", actual_layer_name)
                else:
                    layer_path = os.path.join(self.worksheet_root, "designs", actual_layer_name)

                layer_paths.append(layer_path)

                layers_info.append({
                    "layer_number": i + 1,
                    "layer_name": actual_layer_name,
                    "display_name": widget.layer_dropdown.currentText() if hasattr(widget, 'layer_dropdown') else "",
                    "chainage": chainage_value,
                    "verified": is_verified,
                    "verification_status": verification_status,
                    "world_coordinates": getattr(widget.verify_btn, 'world_coordinates', None),
                    "json_path": getattr(widget.verify_btn, 'json_file_path', ''),
                    "user_id": user_id,
                    "worksheet_name": worksheet_name,
                    "subfolder_type": subfolder_type
                })

        primary_layer = merger_point_widget.primary_layer_dropdown.currentText()

        # Build confirmation message (unchanged)
        info_message = f"Merger Point {point_number} - Connect Layers\n\n"
        info_message += f"Primary Layer: {primary_layer}\n\nLayers to connect:\n"
        for layer in layers_info:
            status_icon = "✓" if layer["verified"] else "✗"
            if layer["world_coordinates"]:
                coords = layer["world_coordinates"]
                info_message += f"{layer['layer_number']}. {layer['layer_name']} (from worksheet {layer['worksheet_name']}) at {layer['chainage']} (X={coords[0]:.2f}, Y={coords[1]:.2f}, Z={coords[2]:.2f}) {status_icon}\n"
            else:
                info_message += f"{layer['layer_number']}. {layer['layer_name']} (from worksheet {layer['worksheet_name']}) at {layer['chainage']} {status_icon}\n"

        reply = QMessageBox.question(
            self,
            f"Connect Layers - Merger Point {point_number}",
            info_message + "\nDo you want to proceed with connecting these layers?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.load_layers_for_point(point_number, layer_paths, layers_info)
        
    def load_layers_for_point(self, point_number, layer_paths, layers_info):
        try:
            merger_point_widget = None
            for widget in self.merger_points_widgets:
                if widget.title() == f"Merger Point {point_number}":
                    merger_point_widget = widget
                    break

            if not merger_point_widget:
                QMessageBox.warning(self, "Error", f"Merger Point {point_number} not found.")
                return False

            loaded_layers = []
            loaded_data_for_3d = {}

            merger_type = "Road & Road"
            for widget in self.merger_points_widgets:
                if widget.title() == f"Merger Point {point_number}":
                    if hasattr(widget, 'merger_type_dropdown'):
                        merger_type = widget.merger_type_dropdown.currentText()
                    break
            print(f"✓ Merger type for Point {point_number}: {merger_type}")

            bridge_layer_paths = []   # layers containing Bridge_components
            deck_layer_paths = []     # layers containing decks

            for i, layer_path in enumerate(layer_paths):
                layer_name = layers_info[i]["layer_name"]
                try:
                    success = self.load_baselines_from_json(layer_path)
                    if success:
                        loaded_layers.append(layer_name)
                        if layer_path in self.loaded_baseline_data:
                            layer_data = self.loaded_baseline_data[layer_path]
                            for json_file, baseline_json in layer_data["baseline_files"].items():
                                if json_file == "bridge_components.json":
                                    continue
                                # Map the key to a layer type
                                if json_file == "road_surface_baseline.json":
                                    ltype = "road_surface"
                                elif json_file == "surface_baseline.json":
                                    ltype = "surface"
                                elif json_file == "construction_baseline.json":
                                    ltype = "construction"
                                elif json_file == "deck_baseline.json":
                                    ltype = "deck_line"
                                else:
                                    ltype = baseline_json.get("baseline_key", f"type_{len(loaded_data_for_3d)}")

                                if ltype not in loaded_data_for_3d:
                                    loaded_data_for_3d[ltype] = {"polylines": []}
                                for polyline in baseline_json.get("polylines", []):
                                    poly_data = {
                                        "points": polyline.get("points", []),
                                        "layer_folder": layer_path
                                    }
                                    loaded_data_for_3d[ltype]["polylines"].append(poly_data)

                        # For Road & Bridge, read unified config for bridge components and decks
                        if merger_type == "Road & Bridge":
                            unified_path = os.path.join(layer_path, "design_construction_config.json")
                            if os.path.exists(unified_path):
                                try:
                                    with open(unified_path, 'r') as f:
                                        config = json.load(f)
                                    if config.get("Bridge_components") or config.get("bridge_components"):
                                        bridge_layer_paths.append(layer_path)
                                        print(f"  → Found bridge components in unified config: {layer_name}")
                                    if config.get("decks"):
                                        deck_layer_paths.append(layer_path)
                                        print(f"  → Found decks in unified config: {layer_name}")
                                except Exception as e:
                                    print(f"  ⚠ Error reading unified config for {layer_name}: {e}")

                        print(f"✓ Loaded layer: {layer_name}")
                    else:
                        print(f"✗ Failed to load layer: {layer_name}")
                except Exception as e:
                    print(f"✗ Error loading layer {layer_name}: {str(e)}")

            if loaded_layers:
                QMessageBox.information(self, "Success", f"Successfully loaded {len(loaded_layers)} layers for Merger Point {point_number}")

                # --- Load zero line from primary layer (unchanged) ---
                users_base_dir = r"C:\3D_Tool\user"
                primary_layer_data = merger_point_widget.primary_layer_dropdown.currentData()
                if primary_layer_data and isinstance(primary_layer_data, tuple):
                    if len(primary_layer_data) == 4:
                        user_id, ws_name, layer_name, sub = primary_layer_data
                        primary_layer_path = os.path.join(users_base_dir, user_id, sub, ws_name, "designs", layer_name)
                    elif len(primary_layer_data) == 3:
                        user_id, ws_name, layer_name = primary_layer_data
                        primary_layer_path = os.path.join(users_base_dir, user_id, ws_name, "designs", layer_name)
                    else:
                        primary_layer_path = ""
                    if primary_layer_path and hasattr(self.parent(), 'load_zero_line_from_layer'):
                        zero_loaded = self.parent().load_zero_line_from_layer(primary_layer_path)
                        self.parent().scale_section.setVisible(True)
                        print("✓ Zero line loaded from primary layer" if zero_loaded else "⚠ Failed to load zero line")
                else:
                    print("⚠ No valid primary layer selected – cannot load zero line")

                # --- Map to 3D planes (unchanged) ---
              ## Mayur Wakhare 13-07-2026 tunnel
                if loaded_data_for_3d and hasattr(self.parent(), 'map_baselines_to_3d_planes_from_data'):
                ##################################################################################
                    width = 10.0
                    for ltype, data in loaded_data_for_3d.items():
                        if data["polylines"]:
                            for layer_path in self.loaded_baseline_data:
                                layer_metadata = self.loaded_baseline_data[layer_path].get("metadata", {})
                                for json_file in layer_metadata:
                                    if "width_meters" in layer_metadata[json_file]:
                                        width = layer_metadata[json_file]["width_meters"]
                                        break
                                if width != 10.0:
                                    break
                        if width != 10.0:
                            break
                 ## Mayur Wakhare 13-07-2026
                  
                    self.parent().map_baselines_to_3d_planes_from_data(loaded_data_for_3d, width)
                    ##########################################################################
                    print("3D planes generation attempted")
                else:
                    print("Cannot map: no 3D data or parent method missing")

                # --- Load bridge components and decks from unified config (Road & Bridge) ---
                if merger_type == "Road & Bridge":
                    # The parent methods (load_bridge_components_from_json, load_decks_from_json)
                    # must be updated to read from design_construction_config.json.
                    # If they already read the unified file, just call them with the layer path.
                    if hasattr(self.parent(), 'load_bridge_components_from_json'):
                        for bridge_path in bridge_layer_paths:
                            try:
                                self.parent().load_bridge_components_from_json(bridge_path)
                                print(f"    ✓ Loaded bridge components from unified config in: {os.path.basename(bridge_path)}")
                            except Exception as e:
                                print(f"    ✗ Error loading bridge components: {str(e)}")
                    if hasattr(self.parent(), 'load_decks_from_json'):
                        for deck_path in deck_layer_paths:
                            try:
                                self.parent().load_decks_from_json(deck_path)
                                print(f"    ✓ Loaded decks from unified config in: {os.path.basename(deck_path)}")
                            except Exception as e:
                                print(f"    ✗ Error loading decks: {str(e)}")

                merger_point_widget.connect_layers_btn.setText("Layers Connected")
                merger_point_widget.connect_layers_btn.setEnabled(False)
            else:
                QMessageBox.warning(self, "Warning", f"No layers were loaded for Merger Point {point_number}")

            return len(loaded_layers) > 0
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading layers: {str(e)}")
            return False

    def create_layers_for_point(self, point_number):
        merger_point_widget = self.find_merger_point_widget(point_number)
        if not merger_point_widget:
            return

        try:
            expected_layers = int(merger_point_widget.layer_count_input.text().strip())
            if expected_layers <= 0:
                QMessageBox.warning(self, "Invalid Input", "Please enter a positive number of layers.")
                return
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number of layers.")
            return

        # Get all selected worksheets (now with subfolder info)
        selected_worksheets = []
        for i in range(merger_point_widget.selected_list.count()):
            data = merger_point_widget.selected_list.item(i).data(Qt.UserRole)
            if data and len(data) == 3:
                selected_worksheets.append(data)   # (user_id, ws_name, subfolder_type)

        if not selected_worksheets:
            QMessageBox.warning(self, "Selection Error", "Please select at least one worksheet.")
            return

        # Collect all available layers from selected worksheets
        all_layers = []  # (user_id, ws_name, layer_name, subfolder_type)
        for user_id, ws_name, sub in selected_worksheets:
            designs_path = os.path.join(r"C:\3D_Tool\user", user_id, sub, ws_name, "designs")
            if os.path.exists(designs_path):
                for layer_name in os.listdir(designs_path):
                    layer_path = os.path.join(designs_path, layer_name)
                    if os.path.isdir(layer_path):
                        all_layers.append((user_id, ws_name, layer_name, sub))

        if not all_layers:
            QMessageBox.warning(self, "No Layers Found", "No layer folders found in the selected worksheets.")
            return

        # Store the combined layer list for later use
        merger_point_widget.all_available_layers = all_layers

        # Clear existing layers
        self.clear_layers_for_point(merger_point_widget)

        # Create exactly 'expected_layers' layer widgets
        for i in range(1, expected_layers + 1):
            layer_widget = self.create_layer_widget(i, all_layers)
            merger_point_widget.layers_container.layers_layout.addWidget(layer_widget)

        # Populate primary layer dropdown
        self.populate_primary_layer_dropdown(merger_point_widget)

        merger_point_widget.confirm_btn.setEnabled(False)
        merger_point_widget.selection_info_label.setText(f"Created {expected_layers} layer(s). Add/remove worksheets and confirm again to regenerate.")
        merger_point_widget.connect_layers_btn.setVisible(False)
            
    def create_layer_widget(self, layer_number, all_layers):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        layer_label = QLabel(f"layer {layer_number}:")
        layer_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(layer_label)

        layer_dropdown = QComboBox()
        layer_dropdown.setFixedWidth(350)
        layer_dropdown.setStyleSheet("""...""")  # (keep existing styling)
        layout.addWidget(layer_dropdown)

        layer_dropdown.clear()
        layer_dropdown.addItem("Select Layer", None)
        for user_id, ws_name, layer_name, sub in all_layers:
            prefix = "Road" if sub == "road" else "Bridge"
            display_text = f"{layer_name} ({prefix}_{ws_name} - {user_id})"
            layer_dropdown.addItem(display_text, (user_id, ws_name, layer_name, sub))

        if layer_dropdown.count() == 1:
            layer_dropdown.addItem("No layers found", None)
            layer_dropdown.setEnabled(False)

        # Chainage label and input (unchanged)
        chainage_label = QLabel("Chainage =")
        chainage_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(chainage_label)

        chainage_input = QLineEdit()
        chainage_input.setPlaceholderText("eg. 101+000")
        chainage_input.setFixedWidth(150)
        chainage_input.setStyleSheet("""...""")
        layout.addWidget(chainage_input)

        verify_btn = QPushButton("Verify")
        verify_btn.setFixedWidth(80)
        verify_btn.setStyleSheet("""...""")
        verify_btn.point_number = getattr(self, 'current_point_number', 1)
        verify_btn.layer_number = layer_number
        verify_btn.clicked.connect(lambda: self.verify_layer_chainage(
            layer_number, layer_dropdown, chainage_input, verify_btn
        ))

        layout.addWidget(verify_btn)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        container.layer_dropdown = layer_dropdown
        container.chainage_input = chainage_input
        container.verify_btn = verify_btn
        return container
    
    def verify_layer_chainage(self, layer_number, layer_dropdown, chainage_input, verify_btn):
        selected_data = layer_dropdown.currentData()
        if not selected_data or len(selected_data) != 4:
            QMessageBox.warning(self, "Verification Failed",
                                f"Please select a valid layer for layer {layer_number}")
            return

        user_id, worksheet_name, selected_layer, subfolder_type = selected_data
        chainage_value = chainage_input.text().strip()

        if not chainage_value:
            QMessageBox.warning(self, "Verification Failed",
                                f"Please enter a chainage value for layer {layer_number}")
            return

        if not self.validate_chainage_format(chainage_value):
            QMessageBox.warning(self, "Verification Failed",
                                f"Please enter a valid chainage format for layer {layer_number}\nExample: 101+000")
            return

        # Build path using subfolder_type
        layer_folder_path = os.path.join(r"C:\3D_Tool\user", user_id, subfolder_type, worksheet_name, "designs", selected_layer)
        if not os.path.exists(layer_folder_path):
            QMessageBox.warning(self, "Verification Failed",
                                f"Layer folder not found: {layer_folder_path}")
            return

        # Define config path once (used for both bridge and road baselines)
        config_json_path = os.path.join(layer_folder_path, "design_construction_config.json")

        # Get merger type for this point
        merger_type = "Road & Road"
        for widget in self.merger_points_widgets:
            if hasattr(widget, 'merger_type_dropdown'):
                if widget.title() == f"Merger Point {verify_btn.point_number}":
                    merger_type = widget.merger_type_dropdown.currentText()
                    break

        found_chainage = False
        world_coordinates = None
        found_json_path = None
        found_json_file = None
        is_bridge_components = False
        data_used = None

        # 1. For Road & Bridge, check the unified config for bridge components
        if merger_type == "Road & Bridge" and os.path.exists(config_json_path):
            try:
                with open(config_json_path, 'r') as f:
                    config_data = json.load(f)
                # Try both possible keys: "Bridge_components" (as in provided example) and "bridge_components"
                bridge_components = config_data.get("Bridge_components")
                if bridge_components and isinstance(bridge_components, list):
                    coords = self.find_chainage_in_bridge_components(bridge_components, chainage_value)
                    if coords:
                        found_chainage = True
                        world_coordinates = coords
                        found_json_path = config_json_path
                        found_json_file = "design_construction_config.json (Bridge_components)"
                        is_bridge_components = True
                        data_used = bridge_components
            except Exception as e:
                print(f"Error reading bridge components from unified config: {e}")

        # 2. Always check design_construction_config.json for road surface baseline
        if not found_chainage and os.path.exists(config_json_path):
            try:
                with open(config_json_path, 'r') as f:
                    config_data = json.load(f)
                # Extract the road_surface_baseline object
                road_baseline = config_data.get("design", {}).get("road_surface_baseline")
                if road_baseline:
                    coords = self.find_chainage_coordinates(road_baseline, chainage_value)
                    if coords:
                        found_chainage = True
                        world_coordinates = coords
                        found_json_path = config_json_path
                        found_json_file = "design_construction_config.json (road_surface_baseline)"
                        is_bridge_components = False
                        data_used = road_baseline
            except Exception as e:
                print(f"Error reading design_construction_config.json for road baseline: {e}")

        # 3. Fallback to old separate JSON files (optional, for backward compatibility)
        if not found_chainage:
            json_files_to_check = ["road_surface_baseline.json", "deck_baseline.json"]
            if merger_type == "Road & Bridge":
                json_files_to_check = ["road_surface_baseline.json", "deck_baseline.json"]
            for json_file in json_files_to_check:
                json_path = os.path.join(layer_folder_path, json_file)
                if not os.path.exists(json_path):
                    continue
                try:
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                    coords = self.find_chainage_coordinates(data, chainage_value)
                    if coords:
                        found_chainage = True
                        world_coordinates = coords
                        found_json_path = json_path
                        found_json_file = json_file
                        is_bridge_components = False
                        data_used = data
                        break
                except Exception as e:
                    print(f"Error reading {json_file}: {e}")

        if not found_chainage:
            QMessageBox.warning(self, "Verification Failed",
                                f"Chainage {chainage_value} not found in {selected_layer}")
            chainage_input.clear()
            return

        # Store verification data (including subfolder_type)
        key = f"point_{verify_btn.point_number}_layer_{layer_number}"
        baseline_type = "Bridge Component" if is_bridge_components else data_used.get("baseline_type", "Unknown")

        self.verified_coordinates[key] = {
            "layer_name": selected_layer,
            "chainage": chainage_value,
            "world_coordinates": world_coordinates,
            "baseline_type": baseline_type,
            "json_file_name": found_json_file,
            "json_file_path": found_json_path,
            "layer_folder_path": layer_folder_path,
            "user_id": user_id,
            "worksheet_name": worksheet_name,
            "subfolder_type": subfolder_type
        }

        # Attach data to button
        verify_btn.world_coordinates = world_coordinates
        verify_btn.layer_name = selected_layer
        verify_btn.chainage_value = chainage_value
        verify_btn.verification_key = key
        verify_btn.json_file_path = found_json_path
        verify_btn.baseline_type = baseline_type
        verify_btn.user_id = user_id
        verify_btn.worksheet_name = worksheet_name
        verify_btn.subfolder_type = subfolder_type

        self.mark_as_verified(verify_btn)

        QMessageBox.information(self, "Verification Successful",
                                f"Layer {selected_layer} verified!\n"
                                f"Chainage {chainage_value} found in {found_json_file}\n"
                                f"Coordinates: X={world_coordinates[0]:.2f}, Y={world_coordinates[1]:.2f}, Z={world_coordinates[2]:.2f}")

        self.check_coordinate_matching(verify_btn.point_number)

    def check_coordinate_matching(self, point_number):
        """Check if all verified layers have matching coordinates within tolerance"""
        # Find the merger point widget
        merger_point_widget = None
        for widget in self.merger_points_widgets:
            if widget.title() == f"Merger Point {point_number}":
                merger_point_widget = widget
                break

        if not merger_point_widget:
            return

        # Get all layer widgets for this point
        layout = merger_point_widget.layers_container.layers_layout
        layer_widgets = []
        for i in range(layout.count()):
            child = layout.itemAt(i)
            if child.widget():
                layer_widgets.append(child.widget())

        # Check if all layers are verified
        all_verified = True
        verified_coordinates = []
        verified_layers_info = []          # NEW: store (widget, coords, layer_name) for later

        for widget in layer_widgets:
            if hasattr(widget.verify_btn, 'world_coordinates') and widget.verify_btn.text() == "✓":
                coords = widget.verify_btn.world_coordinates
                verified_coordinates.append(coords)
                layer_name = widget.layer_dropdown.currentText()
                verified_layers_info.append((widget, coords, layer_name))   # NEW
            else:
                all_verified = False
                break

        if not all_verified or len(verified_coordinates) < 2:
            # Not all layers are verified or only one layer is verified
            return

        # Check if all coordinates match within tolerance
        reference_coords = verified_coordinates[0]
        coordinates_match = True

        for i, coords in enumerate(verified_coordinates[1:], 1):
            if (abs(coords[0] - reference_coords[0]) > self.coordinate_tolerance or
                abs(coords[1] - reference_coords[1]) > self.coordinate_tolerance or
                abs(coords[2] - reference_coords[2]) > self.coordinate_tolerance):
                coordinates_match = False
                break

        # Show/Hide Connect Layers button based on matching
        if coordinates_match:
            merger_point_widget.connect_layers_btn.setVisible(True)

            # Show success message (original)
            QMessageBox.information(
                self,
                "Coordinates Matched",
                f"All verified layers for Merger Point {point_number} have matching coordinates!\n\n" +
                f"Reference coordinates: X={reference_coords[0]:.2f}, Y={reference_coords[1]:.2f}, Z={reference_coords[2]:.2f}\n" +
                f"Tolerance: {self.coordinate_tolerance} meters"
            )

            # ========== NEW: Primary layer identification and Z‑difference storage ==========
            primary_layer_name = merger_point_widget.primary_layer_dropdown.currentText()
            if primary_layer_name in ["Select Primary Layer", "No primary layers found", "Error loading layers"]:
                # Should not happen because all layers are verified, but just in case
                return

            # Find the primary layer among the verified ones
            primary_coords = None
            for widget, coords, layer_name in verified_layers_info:
                if layer_name == primary_layer_name:
                    primary_coords = coords
                    break

            if primary_coords is None:
                # Primary layer is not verified – also shouldn't happen because all are verified
                return

            # Store the primary layer name on the widget for later use
            merger_point_widget.primary_layer_name = primary_layer_name

            # Compute Z differences relative to primary layer (keyed by actual layer name)
            z_differences = {}
            for widget, coords, layer_name in verified_layers_info:
                if layer_name == primary_layer_name:
                    continue
                z_diff = primary_coords[2] - coords[2]   # primary Z minus other Z
                z_differences[layer_name] = z_diff

            # Store the differences on the merger point widget
            merger_point_widget.z_differences = z_differences
            # ============================================================================

        else:
            merger_point_widget.connect_layers_btn.setVisible(False)

            # Show warning message (original)
            coordinate_details = "\n".join([f"Layer {i+1}: X={coords[0]:.2f}, Y={coords[1]:.2f}, Z={coords[2]:.2f}" 
                                        for i, coords in enumerate(verified_coordinates)])

            QMessageBox.warning(
                self,
                "Coordinates Mismatch",
                f"Coordinates for verified layers in Merger Point {point_number} do not match within tolerance!\n\n" +
                f"Coordinate details:\n{coordinate_details}\n\n" +
                f"Tolerance: {self.coordinate_tolerance} meters" 
            )
            
    def find_chainage_coordinates(self, baseline_data, chainage_value):
        """Search for chainage in the baseline data and return world coordinates"""
        try:
            # Check if the data has polylines
            if "polylines" not in baseline_data:
                return None
            
            def parse_chainage(ch_str):
                # safely parse something like "101+20.000" to (101, 20.0)
                if not ch_str: return None
                parts = str(ch_str).split('+')
                if len(parts) == 2:
                    try:
                        return int(parts[0]), float(parts[1])
                    except ValueError:
                        pass
                return None
                
            target_ch = parse_chainage(chainage_value)
            
            # Search through all polylines and their points
            for polyline in baseline_data["polylines"]:
                if "points" not in polyline:
                    continue
                
                for point in polyline["points"]:
                    point_ch_str = point.get("chainage_str")
                    
                    # 1. Exact string match
                    if point_ch_str == chainage_value:
                        return point.get("world_coordinates")
                        
                    # 2. Semantic math match (handles "101+000" vs "101+000.000")
                    if target_ch:
                        pt_ch = parse_chainage(point_ch_str)
                        if pt_ch and pt_ch[0] == target_ch[0] and abs(pt_ch[1] - target_ch[1]) < 0.001:
                            return point.get("world_coordinates")
            
            # 3. If not found by string, try to find by chainage_m if chainage_value can be converted to float
            try:
                chainage_m = float(chainage_value)
                for polyline in baseline_data["polylines"]:
                    if "points" not in polyline:
                        continue
                    
                    for point in polyline["points"]:
                        # Find the closest chainage (within a small tolerance)
                        if abs(point.get("chainage_m", 0) - chainage_m) < 0.001:
                            return point.get("world_coordinates")
            except ValueError:
                pass  # chainage_value cannot be converted to float
            
            return None
        except Exception as e:
            print(f"Error finding chainage coordinates: {e}")
            return None
    
    def find_chainage_in_bridge_components(self, components_data, chainage_value):
        """
        Search for chainage in bridge_components.json format.
        bridge_components.json contains a list of bridge component objects with:
        - chainage_str: "111+019"
        - coordinates_3d: {"x": ..., "y": ..., "z": ...}
        """
        try:
            if not isinstance(components_data, list):
                print("Bridge components data is not a list")
                return None

            def parse_chainage(ch_str):
                if not ch_str:
                    return None
                parts = str(ch_str).split('+')
                if len(parts) == 2:
                    try:
                        return int(parts[0]), float(parts[1])
                    except ValueError:
                        pass
                return None

            target_ch = parse_chainage(chainage_value)

            for component in components_data:
                comp_chainage = component.get("chainage_str")
                if not comp_chainage:
                    continue

                # 1. Exact string match
                if comp_chainage == chainage_value:
                    coords = component.get("coordinates_3d", {})
                    x, y, z = coords.get("x"), coords.get("y"), coords.get("z")
                    if x is not None and y is not None and z is not None:
                        return [x, y, z]

                # 2. Semantic math match (handles formatting differences)
                if target_ch:
                    pt_ch = parse_chainage(comp_chainage)
                    if pt_ch and pt_ch[0] == target_ch[0] and abs(pt_ch[1] - target_ch[1]) < 0.001:
                        coords = component.get("coordinates_3d", {})
                        x, y, z = coords.get("x"), coords.get("y"), coords.get("z")
                        if x is not None and y is not None and z is not None:
                            return [x, y, z]

            # 3. Fallback: try by numeric chainage_m if provided
            try:
                chainage_m = float(chainage_value)
                for component in components_data:
                    comp_m = component.get("chainage_m")
                    if comp_m is not None and abs(comp_m - chainage_m) < 0.001:
                        coords = component.get("coordinates_3d", {})
                        x, y, z = coords.get("x"), coords.get("y"), coords.get("z")
                        if x is not None and y is not None and z is not None:
                            return [x, y, z]
            except ValueError:
                pass

            return None

        except Exception as e:
            print(f"Error finding chainage in bridge components: {e}")
            return None

    # Update the mark_as_verified to store verification data
    def mark_as_verified(self, verify_btn):
        """Mark the verify button as verified with green background and checkmark"""
        verify_btn.setText("✓")
        verify_btn.setEnabled(False)  # Disable button to prevent re-verification
        verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #388E3C;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 16px;
            }
        """)

    def validate_chainage_format(self, chainage_value):
        """Validate chainage format like '101+000' or '101+00.000' or '101+0.000'"""
        if not chainage_value:
            return False
        import re
        # Pattern: digits, plus, digits, then optional decimal point and digits
        pattern = r'^\d+\+\d+(?:\.\d+)?$'
        return bool(re.match(pattern, chainage_value))

    def populate_primary_layer_dropdown(self, merger_point_widget):
        dropdown = merger_point_widget.primary_layer_dropdown
        dropdown.clear()
        dropdown.addItem("Select Primary Layer", None)

        all_layers = getattr(merger_point_widget, 'all_available_layers', [])
        for user_id, ws_name, layer_name, sub in all_layers:
            prefix = "Road" if sub == "road" else "Bridge"
            display_text = f"{layer_name} ({prefix}_{ws_name} - {user_id})"
            dropdown.addItem(display_text, (user_id, ws_name, layer_name, sub))

        if dropdown.count() == 1:
            dropdown.addItem("No primary layers found", None)
            dropdown.setEnabled(False)
        else:
            dropdown.setEnabled(True)
            
    def clear_merger_points(self):
        """Clear all merger points"""
        for widget in self.merger_points_widgets:
            widget.deleteLater()
        self.merger_points_widgets.clear()
        
        # Show placeholder when no merger points exist
        self.placeholder_label.show()
        
    def clear_layers_for_point(self, merger_point_widget):
        """Clear all layers for a specific merger point"""
        layout = merger_point_widget.layers_container.layers_layout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Hide the Connect Layers button when layers are cleared
        merger_point_widget.connect_layers_btn.setVisible(False)
                
    def save_config(self):
        layer_name = self.layer_name_input.text().strip()
        if not layer_name:
            QMessageBox.warning(self, "Missing Information", "Please enter a Layer Name")
            return

        # ========== Enhanced warning for height differences ==========
        z_threshold = 0.05   # meters, adjust as needed
        mismatch_details = []
        for merger_point_widget in self.merger_points_widgets:
            point_num = merger_point_widget.title().split()[-1]   # extract number from "Merger Point X"
            if hasattr(merger_point_widget, 'z_differences') and hasattr(merger_point_widget, 'primary_layer_name'):
                primary = merger_point_widget.primary_layer_name
                for layer, diff in merger_point_widget.z_differences.items():
                    if abs(diff) > z_threshold:
                        mismatch_details.append(
                            f"In Merger Point {point_num} layer '{layer}' has a height elevation difference of {diff:.3f} m compared with the primary layer '{primary}'."
                        )

        if mismatch_details:
            # Create a custom QMessageBox with rich text formatting
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("⚠ Height Differences Detected")
            msg_box.setTextFormat(Qt.RichText)

            # Build HTML content with updated styles
            html = """
            <html>
            <head>
            <style>
                body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt; }
                .header { color: #c04000; font-size: 14pt; font-weight: bold; margin-bottom: 10px; }
                .list { margin-left: 20px; }
                .item { color: #b22222; font-weight: bold; }
                .footer { margin-top: 15px; color: #333; font-style: italic; }
                .question { font-size: 12pt; font-weight: bold; color: #c04000; margin-top: 15px; }
            </style>
            </head>
            <body>
            <div class="header">⚠ Height Differences Detected</div>
            <p>The following layers have a vertical offset from their respective primary layers:</p>
            <ul class="list">
            """
            for detail in mismatch_details:
                html += f"<li class='item'>{detail}</li>"
            html += """
            </ul>
            <p class="footer"><b>These layers may need to be redrawn to match the primary layer height.</b></p>
            <p class="question">What would you like to do?</p>
            </body>
            </html>
            """

            msg_box.setText(html)

            # Add custom buttons
            send_btn = msg_box.addButton("Send back to design person", QMessageBox.AcceptRole)
            edit_btn = msg_box.addButton("Edit by myself", QMessageBox.RejectRole)
            msg_box.setDefaultButton(edit_btn)   # "Edit" is the default

            msg_box.setMinimumSize(500, 300)

            reply = msg_box.exec_()
            if msg_box.clickedButton() == send_btn:
                return   # User wants to edit → stay in dialog
            # If "Send back to design person" is clicked, we proceed to save (maybe with a flag later)
            # You could optionally show a confirmation that the configuration will be saved as a draft.
            # For now, we just continue.
        # ==============================================================
               
        # Collect configuration data
        config_data = {
            "layer_name": layer_name,
            "merger_points_count": len(self.merger_points_widgets),
            "merger_points": []
        }
        
        # Collect data from each merger point
        for i, merger_point_widget in enumerate(self.merger_points_widgets, 1):
            # Get primary layer selection
            primary_layer = merger_point_widget.primary_layer_dropdown.currentText()
            # Get merger type selection (Road / Road & Bridge)
            merger_type = merger_point_widget.merger_type_dropdown.currentText() if hasattr(merger_point_widget, 'merger_type_dropdown') else " Road & Road"
            
            merger_point_data = {
                "point_number": i,
                "primary_layer": primary_layer,
                "merger_type": merger_type,  # NEW: Include merger type selection
                "layers_count": merger_point_widget.layers_container.layers_layout.count(),
                "layers": []
            }
            
            # Get layer information
            layout = merger_point_widget.layers_container.layers_layout
            for j in range(layout.count()):
                child = layout.itemAt(j)
                if child.widget():
                    # Extract layer information from the widget
                    widget = child.widget()
                    # Get the selected layer from dropdown
                    selected_layer = widget.layer_dropdown.currentText() if hasattr(widget, 'layer_dropdown') else ""
                    # Get the chainage input value
                    chainage_value = widget.chainage_input.text().strip() if hasattr(widget, 'chainage_input') else ""
                    
                    layer_info = {
                        "layer_number": j + 1,
                        "selected_layer": selected_layer,
                        "chainage": chainage_value
                    }
                    merger_point_data["layers"].append(layer_info)
                
            config_data["merger_points"].append(merger_point_data)
        
        # You can now use config_data as needed
        print("Merger Layer Configuration saved:")
        print(json.dumps(config_data, indent=2))
        
        # Show success message
        QMessageBox.information(self, "Success", "Merger Layer Configuration saved successfully! You can edit layers from merger Hierarchy.")
        
        # Close dialog
        self.accept()

    def get_configuration(self):
        """Return the current configuration"""
        config_data = {
            "layer_name": self.layer_name_input.text().strip(),
            "merger_points_count": len(self.merger_points_widgets),
            "merger_points": []
        }
        
        # Base directory for users (no "worksheets" subfolder)
        users_base_dir = r"C:\3D_Tool\user"
        
        for i, merger_point_widget in enumerate(self.merger_points_widgets, 1):
            merger_type = merger_point_widget.merger_type_dropdown.currentText() if hasattr(merger_point_widget, 'merger_type_dropdown') else "Road & Road"
            
            # Get primary layer selection and its stored data
            primary_layer_data = merger_point_widget.primary_layer_dropdown.currentData()
            primary_layer = merger_point_widget.primary_layer_dropdown.currentText()
            primary_layer_user = None
            primary_layer_worksheet = None
            primary_layer_path = ""
            primary_json_path = ""

            if primary_layer_data and primary_layer not in ["Select Primary Layer", "No primary layers found", "Error loading layers"]:
                if isinstance(primary_layer_data, tuple) and len(primary_layer_data) == 3:
                    primary_layer_user, primary_layer_worksheet, primary_layer_name = primary_layer_data
                    # Correct path: user/<user_id>/<worksheet_name>/designs/<layer_name>
                    primary_layer_path = os.path.join(users_base_dir, primary_layer_user, primary_layer_worksheet, "designs", primary_layer_name)
                else:
                    # Fallback for older data (should not happen)
                    primary_layer_path = os.path.join(self.worksheet_root, "designs", primary_layer)
                
                for json_file in ["road_surface_baseline.json", "deck_baseline.json"]:
                    json_path = os.path.join(primary_layer_path, json_file)
                    if os.path.exists(json_path):
                        primary_json_path = json_path
                        break

            merger_point_data = {
                "point_number": i,
                "primary_layer": primary_layer,
                "primary_layer_user": primary_layer_user,
                "primary_layer_worksheet": primary_layer_worksheet,
                "merger_type": merger_type,
                "primary_layer_path": primary_layer_path,
                "primary_json_path": primary_json_path,
                "layers_count": merger_point_widget.layers_container.layers_layout.count(),
                "layers": []
            }
            
            # Process each layer widget
            layout = merger_point_widget.layers_container.layers_layout
            for j in range(layout.count()):
                child = layout.itemAt(j)
                if child and child.widget():
                    widget = child.widget()
                    selected_layer = widget.layer_dropdown.currentText() if hasattr(widget, 'layer_dropdown') else ""
                    chainage_value = widget.chainage_input.text().strip() if hasattr(widget, 'chainage_input') else ""
                    user_id = getattr(widget, 'user_id', '')
                    worksheet_name = getattr(widget, 'worksheet_name', '')
                    
                    layer_path = ""
                    json_path = ""
                    verification_status = "not_verified"
                    world_coordinates = None
                    baseline_type = "Unknown"
                    
                    if selected_layer and selected_layer not in ["Select Layer", "No layers found", "Error loading layers"]:
                        # Correct path: user/<user_id>/<worksheet_name>/designs/<selected_layer>
                        if user_id and worksheet_name:
                            layer_path = os.path.join(users_base_dir, user_id, worksheet_name, "designs", selected_layer)
                        else:
                            # Fallback to current worksheet root
                            layer_path = os.path.join(self.worksheet_root, "designs", selected_layer)
                        
                        if hasattr(widget.verify_btn, 'json_file_path'):
                            json_path = widget.verify_btn.json_file_path
                            verification_status = "verified"
                            world_coordinates = getattr(widget.verify_btn, 'world_coordinates', None)
                            baseline_type = getattr(widget.verify_btn, 'baseline_type', "Unknown")
                        else:
                            for json_file in ["road_surface_baseline.json", "deck_baseline.json"]:
                                possible_path = os.path.join(layer_path, json_file)
                                if os.path.exists(possible_path):
                                    json_path = possible_path
                                    break
                    
                    layer_info = {
                        "user_id": user_id,
                        "worksheet_name": worksheet_name,
                        "layer_number": j + 1,
                        "selected_layer": selected_layer,
                        "subfolder_type": getattr(widget, 'subfolder_type', ''),
                        "layer_path": layer_path,
                        "json_path": json_path,
                        "chainage": chainage_value,
                        "verification_status": verification_status
                    }
                    
                    if world_coordinates:
                        layer_info["world_coordinates"] = world_coordinates
                        layer_info["baseline_type"] = baseline_type
                    
                    # =========================================================
                    # For Road & Bridge and Bridge & Bridge mode: Add deck and bridge components paths
                    # =========================================================
                    if merger_type =="Road & Bridge" and layer_path:
                        # Add decks.json path if it exists (for deck slabs visualization)
                        decks_json_path = os.path.join(layer_path, "decks.json")
                        if os.path.exists(decks_json_path):
                            layer_info["decks_json_path"] = decks_json_path
                        
                        # Add bridge_components.json path if it exists
                        bridge_components_path = os.path.join(layer_path, "bridge_components.json")
                        if os.path.exists(bridge_components_path):
                            layer_info["bridge_components_path"] = bridge_components_path
                        
                    merger_point_data["layers"].append(layer_info)
            
            config_data["merger_points"].append(merger_point_data)
        
        return config_data

    def load_baselines_from_json(self, layer_path):
        """
        Load baseline data from JSON files in the layer directory.
        Now supports design_construction_config.json as the primary source.
        """
        try:
            print(f"Attempting to load from: {layer_path}")
            if not os.path.exists(layer_path):
                print(f"  ✗ Path does not exist")
                return False

            loaded_data = {
                "layer_path": layer_path,
                "baseline_files": {},
                "polylines": [],
                "points": [],
                "metadata": {},
                "has_bridge_components": False
            }

            files_loaded = 0

            # Check for design_construction_config.json first
            config_path = os.path.join(layer_path, "design_construction_config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    design = config.get("design", {})
                    # Extract each baseline type
                    baseline_mapping = {
                        "road_surface_baseline": "road_surface",
                        "surface_baseline": "surface",
                        "construction_baseline": "construction"
                    }
                    for key, ltype in baseline_mapping.items():
                        baseline_obj = design.get(key)
                        if baseline_obj:
                            # Store as if it came from a separate file
                            loaded_data["baseline_files"][f"{key}.json"] = baseline_obj
                            files_loaded += 1
                            # Process polylines
                            if "polylines" in baseline_obj:
                                for polyline in baseline_obj["polylines"]:
                                    polyline_info = {
                                        "baseline_file": key,
                                        "start_chainage_m": polyline.get("start_chainage_m"),
                                        "start_chainage_str": polyline.get("start_chainage_str"),
                                        "end_chainage_m": polyline.get("end_chainage_m"),
                                        "end_chainage_str": polyline.get("end_chainage_str"),
                                        "points": []
                                    }
                                    for point in polyline.get("points", []):
                                        point_info = {
                                            "chainage_m": point.get("chainage_m"),
                                            "chainage_str": point.get("chainage_str"),
                                            "relative_elevation_m": point.get("relative_elevation_m"),
                                            "world_coordinates": point.get("world_coordinates")
                                        }
                                        polyline_info["points"].append(point_info)
                                        loaded_data["points"].append(point_info)
                                    loaded_data["polylines"].append(polyline_info)
                            # Metadata
                            loaded_data["metadata"][key] = {
                                "baseline_type": baseline_obj.get("baseline_type", "Unknown"),
                                "baseline_key": baseline_obj.get("baseline_key", ""),
                                "color": baseline_obj.get("color", ""),
                                "width_meters": baseline_obj.get("width_meters", 0.0),
                                "total_chainage_length": baseline_obj.get("total_chainage_length", 0.0)
                            }
                            print(f"✓ Loaded {key} from design_construction_config.json")
                except Exception as e:
                    print(f"✗ Error reading design_construction_config.json: {e}")

            # Also check for bridge_components.json (if exists)
            bridge_path = os.path.join(layer_path, "bridge_components.json")
            if os.path.exists(bridge_path):
                try:
                    with open(bridge_path, 'r') as f:
                        bridge_data = json.load(f)
                    if isinstance(bridge_data, list):
                        loaded_data["baseline_files"]["bridge_components.json"] = bridge_data
                        loaded_data["has_bridge_components"] = True
                        loaded_data["bridge_components_path"] = bridge_path
                        files_loaded += 1
                        print(f"✓ Loaded bridge_components.json from {layer_path}")
                        print(f"  - Bridge components: {len(bridge_data)}")
                except Exception as e:
                    print(f"✗ Error reading bridge_components.json: {e}")

            # Fallback: if no design_construction_config.json, try old separate JSON files
            if files_loaded == 0:
                old_files = ["road_surface_baseline.json", "deck_baseline.json"]
                for json_file in old_files:
                    json_path = os.path.join(layer_path, json_file)
                    if os.path.exists(json_path):
                        try:
                            with open(json_path, 'r') as f:
                                data = json.load(f)
                            loaded_data["baseline_files"][json_file] = data
                            files_loaded += 1
                            # Process polylines (same as before)
                            if "polylines" in data:
                                for polyline in data["polylines"]:
                                    polyline_info = {
                                        "baseline_file": json_file,
                                        "start_chainage_m": polyline.get("start_chainage_m"),
                                        "start_chainage_str": polyline.get("start_chainage_str"),
                                        "end_chainage_m": polyline.get("end_chainage_m"),
                                        "end_chainage_str": polyline.get("end_chainage_str"),
                                        "points": []
                                    }
                                    for point in polyline.get("points", []):
                                        point_info = {
                                            "chainage_m": point.get("chainage_m"),
                                            "chainage_str": point.get("chainage_str"),
                                            "relative_elevation_m": point.get("relative_elevation_m"),
                                            "world_coordinates": point.get("world_coordinates")
                                        }
                                        polyline_info["points"].append(point_info)
                                        loaded_data["points"].append(point_info)
                                    loaded_data["polylines"].append(polyline_info)
                            # Metadata
                            loaded_data["metadata"][json_file] = {
                                "baseline_type": data.get("baseline_type", "Unknown"),
                                "baseline_key": data.get("baseline_key", ""),
                                "color": data.get("color", ""),
                                "width_meters": data.get("width_meters", 0.0),
                                "total_chainage_length": data.get("total_chainage_length", 0.0)
                            }
                            print(f"✓ Loaded {json_file} from {layer_path}")
                        except Exception as e:
                            print(f"✗ Error reading {json_file}: {e}")

            if files_loaded == 0:
                print(f"✗ No valid baseline data found in {layer_path}")
                return False

            # Summary
            loaded_data["summary"] = {
                "files_loaded": files_loaded,
                "total_polylines": len(loaded_data["polylines"]),
                "total_points": len(loaded_data["points"]),
                "loaded_files": list(loaded_data["baseline_files"].keys())
            }

            self.loaded_baseline_data[layer_path] = loaded_data
            print(f"✓ Successfully loaded {files_loaded} baseline source(s) with {len(loaded_data['polylines'])} polylines and {len(loaded_data['points'])} points")
            return True

        except Exception as e:
            print(f"✗ Unexpected error loading baselines from {layer_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def get_loaded_baseline_data(self, layer_path=None):
        if layer_path:
            return self.loaded_baseline_data.get(layer_path)
        else:
            return self.loaded_baseline_data
    
    def clear_loaded_data(self):
        """Clear all loaded baseline data"""
        self.loaded_baseline_data.clear()
        print("Cleared all loaded baseline data")

    def add_worksheet_to_list(self, point_number):
        widget = self.find_merger_point_widget(point_number)
        if not widget:
            return
        data = widget.worksheet_combo.currentData()
        if data:
            user_id, ws_name, sub = data
            existing = []
            for i in range(widget.selected_list.count()):
                item_data = widget.selected_list.item(i).data(Qt.UserRole)
                existing.append(item_data)
            if (user_id, ws_name, sub) not in existing:
                prefix = "Road" if sub == "road" else "Bridge"
                display = f"{prefix}_{ws_name} (user: {user_id})"
                widget.selected_list.addItem(display)
                widget.selected_list.item(widget.selected_list.count()-1).setData(Qt.UserRole, (user_id, ws_name, sub))
        self.check_selection_count(point_number)

    def remove_worksheet_from_list(self, point_number):
        widget = self.find_merger_point_widget(point_number)
        if not widget:
            return
        row = widget.selected_list.currentRow()
        if row >= 0:
            widget.selected_list.takeItem(row)
        self.check_selection_count(point_number)

    def check_selection_count(self, point_number):
        widget = self.find_merger_point_widget(point_number)
        if not widget:
            return
        selected = widget.selected_list.count()
        # Enable confirm button if at least one worksheet is selected
        widget.confirm_btn.setEnabled(selected > 0)
        if selected == 0:
            widget.selection_info_label.setText("Select at least one worksheet to create layers.")
        else:
            widget.selection_info_label.setText(f"✓ {selected} worksheet(s) selected. Ready to create layers.")

    def find_merger_point_widget(self, point_number):
        for w in self.merger_points_widgets:
            if w.title() == f"Merger Point {point_number}":
                return w
        return None
              
    def populate_users_combo(self, combo):
        users_dir = r"C:\3D_Tool\user"
        combo.clear()
        combo.addItem("Select User", None)
        if os.path.exists(users_dir):
            for user_id in os.listdir(users_dir):
                user_path = os.path.join(users_dir, user_id)
                if os.path.isdir(user_path):
                    combo.addItem(user_id, user_id)

    def add_user_to_list(self, point_number):
        widget = self.find_merger_point_widget(point_number)
        if not widget:
            return
        user_id = widget.user_combo.currentData()
        if user_id:
            existing = [widget.users_list.item(i).data(Qt.UserRole) for i in range(widget.users_list.count())]
            if user_id not in existing:
                widget.users_list.addItem(user_id)
                widget.users_list.item(widget.users_list.count()-1).setData(Qt.UserRole, user_id)
        self.refresh_worksheets_for_point(point_number)

    def remove_user_from_list(self, point_number):
        widget = self.find_merger_point_widget(point_number)
        if not widget:
            return
        for item in widget.users_list.selectedItems():
            row = widget.users_list.row(item)
            widget.users_list.takeItem(row)
        self.refresh_worksheets_for_point(point_number)

    def refresh_worksheets_for_point(self, point_number):
        widget = self.find_merger_point_widget(point_number)
        if not widget:
            return

        merger_type = widget.merger_type_dropdown.currentText() if hasattr(widget, 'merger_type_dropdown') else "Road & Road"
        # Determine which subfolders to scan
        if merger_type == "Road & Road":
            subfolders = ["road"]
        else:  # "Road & Bridge"
            subfolders = ["road", "bridge"]

        worksheet_set = set()  # (user_id, worksheet_name, subfolder_type)
        for i in range(widget.users_list.count()):
            user_id = widget.users_list.item(i).data(Qt.UserRole)
            if not user_id:
                continue
            user_path = os.path.join(r"C:\3D_Tool\user", user_id)
            if not os.path.exists(user_path):
                continue
            for sub in subfolders:
                sub_path = os.path.join(user_path, sub)
                if not os.path.exists(sub_path):
                    continue
                # Each item inside sub_path is a worksheet folder
                for ws_name in os.listdir(sub_path):
                    ws_full = os.path.join(sub_path, ws_name)
                    if os.path.isdir(ws_full) and os.path.exists(os.path.join(ws_full, "designs")):
                        worksheet_set.add((user_id, ws_name, sub))  # sub = 'road' or 'bridge'

        widget.worksheet_combo.clear()
        if worksheet_set:
            for user_id, ws_name, sub in sorted(worksheet_set, key=lambda x: (x[2], x[1])):
                # Display with prefix "Road_" or "Bridge_"
                prefix = "Road" if sub == "road" else "Bridge"
                display = f"{prefix}_{ws_name} (user: {user_id})"
                widget.worksheet_combo.addItem(display, (user_id, ws_name, sub))
            widget.worksheet_combo.setEnabled(True)
            widget.selection_widget.setVisible(True)
            widget.selection_info_label.setText("Select worksheets (must match number of layers)")
        else:
            widget.worksheet_combo.addItem("No worksheets found for selected users")
            widget.worksheet_combo.setEnabled(False)
            widget.selection_widget.setVisible(True)
            widget.selection_info_label.setText("No worksheets available. Please add a worksheet folder with a 'designs' subfolder under 'road' or 'bridge'.")
        widget.selected_list.clear()
        widget.confirm_btn.setEnabled(False)

# ===========================================================================================================================
# ** ELEVATION ANGLE DIALOG FOR APPROACH ROAD **
# ===========================================================================================================================
class ElevationAngleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Elevation Angle Configuration")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #e6e6fa, stop:1 #e6e6fa);
                border-radius: 20px;
            }
            QLabel {
                color: black;
                font-weight: 500;
            }
            QCheckBox {
                color: black;
                font-weight: 500;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #9C27B0;
                border: 2px solid #6A1B9A;
                border-radius: 4px;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 2px solid #9C27B0;
                border-radius: 4px;
            }
            QLineEdit {
                border: 2px solid #9C27B0;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                selection-background-color: #CE93D8;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 2px solid #7B1FA2;
                background-color: #F3E5F5;
            }
            QPushButton {
                border-radius: 20px;
                padding: 10px;
                font-weight: bold;
                min-width: 80px;
                border: none;
            }
            QPushButton#okBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #9C27B0, stop:1 #6A1B9A);
                color: white;
            }
            QPushButton#okBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #AB47BC, stop:1 #4A148C);
            }
            QPushButton#okBtn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #6A1B9A, stop:1 #4A148C);
                padding: 12px 10px 8px 10px;
            }
            QPushButton#cancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333333;
            }
            QPushButton#cancelBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #D1C4E9, stop:1 #BA68C8);
            }
            QPushButton#cancelBtn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #CE93D8, stop:1 #8E24AA);
                padding: 12px 10px 8px 10px;
            }
            /* Style for the bracket labels */
            .bracket {
                font-size: 16px;
                font-weight: bold;
                color: #6A1B9A;
                padding: 0 2px;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Heading
        angle_heading_label = QLabel("Approach Road Angle Configuration")
        angle_heading_label.setStyleSheet("font-weight: bold; color: #4A148C;")
        layout.addWidget(angle_heading_label)

        # ----- ORIGINAL ANGLE CONFIGURATION (unchanged) -----
        # Direction checkboxes (Upward & Downward) - mutually exclusive
        direction_layout = QHBoxLayout()
        self.upward_checkbox = QCheckBox("Upward")
        self.downward_checkbox = QCheckBox("Downward")
        
        # Set upward as default
        self.upward_checkbox.setChecked(True)
        
        # Make checkboxes mutually exclusive
        self.upward_checkbox.stateChanged.connect(self._on_upward_changed)
        self.downward_checkbox.stateChanged.connect(self._on_downward_changed)
        
        direction_layout.addWidget(self.upward_checkbox)
        direction_layout.addWidget(self.downward_checkbox)
        direction_layout.addStretch()
        layout.addLayout(direction_layout)

        # Elevation angle input
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("Elevation Angle (°):"))
        self.angle_edit = QLineEdit("0.0")
        self.angle_edit.setFixedWidth(80)
        self.angle_edit.setPlaceholderText("e.g., 10")
        angle_layout.addWidget(self.angle_edit)
        angle_layout.addStretch()
        layout.addLayout(angle_layout)

        # ----- NEW: APPROACH ROAD SIDE WALLS CONFIGURATION (simple) -----
        # Heading
        wall_heading_label = QLabel("Approach Road Side Walls Configuration")
        wall_heading_label.setStyleSheet("font-weight: bold; color: #4A148C;")
        layout.addWidget(wall_heading_label)

        # Width field with brackets
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("width:"))

        self.width_edit = QLineEdit()
        self.width_edit.setFixedWidth(80)
        self.width_edit.setPlaceholderText("width")

        width_layout.addWidget(self.width_edit)
        width_layout.addStretch()

        layout.addLayout(width_layout)
        # ----- END OF NEW SECTION -----

        # Buttons (original, unchanged)
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setObjectName("okBtn")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def _on_upward_changed(self, state):
        """Make upward and downward checkboxes mutually exclusive"""
        if state == Qt.Checked:
            self.downward_checkbox.blockSignals(True)
            self.downward_checkbox.setChecked(False)
            self.downward_checkbox.blockSignals(False)
    
    def _on_downward_changed(self, state):
        """Make upward and downward checkboxes mutually exclusive"""
        if state == Qt.Checked:
            self.upward_checkbox.blockSignals(True)
            self.upward_checkbox.setChecked(False)
            self.upward_checkbox.blockSignals(False)

    def get_configuration(self):
        """Return elevation angle and side walls configuration"""
        try:
            angle = float(self.angle_edit.text() or 0.0)
        except ValueError:
            angle = 0.0
        
        # Determine direction
        if self.upward_checkbox.isChecked():
            direction = 'upward'
        elif self.downward_checkbox.isChecked():
            direction = 'downward'
        else:
            direction = 'upward'  # Default to upward if neither is checked

        # Side walls width
        try:
            side_wall_width = float(self.width_edit.text() or 0.0)
        except ValueError:
            side_wall_width = 0.0
        
        return {
            'angle': angle,
            'direction': direction,
            'wall_width': side_wall_width
        }
    
# ===========================================================================================================================
# ** DECK CONFIGURATION DIALOG **
# ===========================================================================================================================
class DeckConfigDialog(QDialog):
    """Dialog for configuring deck parameters between two construction points"""
    
    def __init__(self, deck_label="", p1_chainage="", p2_chainage="", distance=0.0, parent=None, loaded_data=None):
        super().__init__(parent)
        
        self.setWindowTitle(f"Deck Configuration - {deck_label}")
        self.setModal(True)
        self.setFixedSize(700, 800)
        
        self.deck_label = deck_label
        self.p1_chainage = p1_chainage
        self.p2_chainage = p2_chainage
        self.distance = distance
        self.loaded_data = loaded_data
        
        # Set improved stylesheet
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #e3f2fd, stop:1 #f3e5f5);
                border-radius: 12px;
            }
            QLabel {
                color: #1a237e;
                font-weight: 500;
            }
            QGroupBox {
                border: 2px solid #1976d2;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: bold;
                color: #0d47a1;
                background: rgba(255,255,255,0.5);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                font-size: 12px;
            }
            QLineEdit {
                border: 1.5px solid #90caf9;
                border-radius: 6px;
                padding: 8px 10px;
                background: white;
                font-weight: 500;
                selection-background-color: #bbdefb;
            }
            QLineEdit:focus {
                border: 2px solid #1976d2;
                background: #f5f5f5;
            }
            QCheckBox {
                color: #1a237e;
                font-weight: 500;
                spacing: 8px;
            }
            QPushButton {
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                color: white;
            }
            QPushButton#saveBtn {
                background: #4caf50;
                border: none;
            }
            QPushButton#saveBtn:hover {
                background: #45a049;
            }
            QPushButton#cancelBtn {
                background: #f44336;
                border: none;
            }
            QPushButton#cancelBtn:hover {
                background: #da190b;
            }
        """)
        
        self.setup_ui()
        
        # Populate with loaded data if provided
        if self.loaded_data:
            self._populate_from_loaded_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title with chainage info
        title_layout = QVBoxLayout()
        title_label = QLabel(f"DECK CONFIGURATION\n{self.deck_label}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 14px; font-weight: bold; color: #0d47a1;
            padding: 12px; background: rgba(144, 202, 249, 0.3);
            border-radius: 6px; border: 1px solid #1976d2;
        """)
        title_layout.addWidget(title_label)
        main_layout.addLayout(title_layout)
        
        # Chainage display
        chainage_layout = QHBoxLayout()
        chainage_layout.addWidget(QLabel("Chainage:"))
        self.chainage_display = QLineEdit()
        self.chainage_display.setText(f"{self.p1_chainage} → {self.p2_chainage}")
        self.chainage_display.setReadOnly(True)
        self.chainage_display.setStyleSheet("background: #f0f0f0; color: #555;")
        chainage_layout.addWidget(self.chainage_display)
        main_layout.addLayout(chainage_layout)
        
        # Distance display
        distance_layout = QHBoxLayout()
        distance_layout.addWidget(QLabel("Distance (m):"))
        self.distance_display = QLineEdit()
        self.distance_display.setText(f"{self.distance:.2f}")
        self.distance_display.setReadOnly(True)
        self.distance_display.setStyleSheet("background: #f0f0f0; color: #555;")
        distance_layout.addWidget(self.distance_display)
        main_layout.addLayout(distance_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #1976d2;")
        main_layout.addWidget(separator)
        
        # Deck parameters group
        params_group = QGroupBox("Deck Parameters")
        params_layout = QGridLayout(params_group)
        params_layout.setSpacing(10)
        
        # Deck Width
        params_layout.addWidget(QLabel("Deck Width (m):"), 0, 0)
        self.deck_width_input = QLineEdit()
        self.deck_width_input.setPlaceholderText("e.g., 8.5")
        params_layout.addWidget(self.deck_width_input, 0, 1)
        
        # Deck Thickness
        params_layout.addWidget(QLabel("Deck Thickness (m):"), 1, 0)
        self.deck_thickness_input = QLineEdit()
        self.deck_thickness_input.setPlaceholderText("e.g., 0.75")
        params_layout.addWidget(self.deck_thickness_input, 1, 1)
        
        # Deck Length (read-only, auto-calculated)
        params_layout.addWidget(QLabel("Deck Length (m):"), 2, 0)
        self.deck_length_display = QLineEdit()
        self.deck_length_display.setText(f"{self.distance:.2f}")
        self.deck_length_display.setReadOnly(True)
        self.deck_length_display.setStyleSheet("background: #f0f0f0; color: #555;")
        params_layout.addWidget(self.deck_length_display, 2, 1)
        
        # Deck Support Gap
        params_layout.addWidget(QLabel("Deck Support Gap (m):"), 3, 0)
        self.deck_support_gap_input = QLineEdit()
        self.deck_support_gap_input.setPlaceholderText("e.g., 0.5 (clearance from pillar center)")
        params_layout.addWidget(self.deck_support_gap_input, 3, 1)
        
        # Deck Support Gap description
        gap_desc = QLabel("(Clearance from the center of pillar supports on both ends)")
        gap_desc.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        params_layout.addWidget(gap_desc, 4, 0, 1, 2)
        
        # Start Deck Offset
        params_layout.addWidget(QLabel("Start Deck Offset (m):"), 5, 0)
        self.start_deck_offset_input = QLineEdit()
        self.start_deck_offset_input.setPlaceholderText("e.g., 5.0 (extra deck before first pillar)")
        params_layout.addWidget(self.start_deck_offset_input, 5, 1)
        
        # End Deck Offset
        params_layout.addWidget(QLabel("End Deck Offset (m):"), 6, 0)
        self.end_deck_offset_input = QLineEdit()
        self.end_deck_offset_input.setPlaceholderText("e.g., 5.0 (extra deck after last pillar)")
        params_layout.addWidget(self.end_deck_offset_input, 6, 1)
        
        # Offset description
        offset_desc = QLabel("(Creates small deck extensions beyond the pillars with offset length)")
        offset_desc.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        params_layout.addWidget(offset_desc, 7, 0, 1, 2)
        
        main_layout.addWidget(params_group)
        
        # FootPath checkbox
        self.footpath_checkbox = QCheckBox("Include FootPath")
        self.footpath_checkbox.setStyleSheet("margin: 10px 0px;")
        main_layout.addWidget(self.footpath_checkbox)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel", objectName="cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save", objectName="saveBtn")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)
    
    def _populate_from_loaded_data(self):
        """Populate form fields with previously loaded deck data"""
        if not self.loaded_data:
            return
        
        try:
            width = self.loaded_data.get('deck_width', '')
            if width:
                self.deck_width_input.setText(str(width))
            
            thickness = self.loaded_data.get('deck_thickness', '')
            if thickness:
                self.deck_thickness_input.setText(str(thickness))
            
            support_gap = self.loaded_data.get('deck_support_gap', '')
            if support_gap:
                self.deck_support_gap_input.setText(str(support_gap))
            
            start_offset = self.loaded_data.get('start_deck_offset', '')
            if start_offset:
                self.start_deck_offset_input.setText(str(start_offset))
            
            end_offset = self.loaded_data.get('end_deck_offset', '')
            if end_offset:
                self.end_deck_offset_input.setText(str(end_offset))
            
            has_footpath = self.loaded_data.get('has_footpath', False)
            self.footpath_checkbox.setChecked(has_footpath)
        
        except Exception as e:
            print(f"Error populating deck data: {e}")
    
    def get_configuration(self):
        """Return deck configuration from dialog"""
        try:
            width = float(self.deck_width_input.text().strip() or 0.0)
            thickness = float(self.deck_thickness_input.text().strip() or 0.0)
            support_gap = float(self.deck_support_gap_input.text().strip() or 0.0)
            start_offset = float(self.start_deck_offset_input.text().strip() or 0.0)
            end_offset = float(self.end_deck_offset_input.text().strip() or 0.0)
        except ValueError:
            width = thickness = support_gap = start_offset = end_offset = 0.0
        
        return {
            'deck_label': self.deck_label,
            'p1_chainage': self.p1_chainage,
            'p2_chainage': self.p2_chainage,
            'deck_width': width,
            'deck_thickness': thickness,
            'deck_length': self.distance,
            'deck_support_gap': support_gap,
            'start_deck_offset': start_offset,
            'end_deck_offset': end_offset,
            'has_footpath': self.footpath_checkbox.isChecked()
        }



# ===========================================================================================================================
# ** STREET LIGHT CONFIG DIALOG **
# ===========================================================================================================================
class StreetLightDialog(QDialog):
    def __init__(self, road_surface_data=None, is_edit_mode=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Street Light Configuration")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.is_edit_mode = is_edit_mode
        
        # Handle the road surface data structure (dict vs list)
        self.points = []
        self.global_width = 7.0 # Default
        
        if isinstance(road_surface_data, dict):
            self.global_width = float(road_surface_data.get("width_meters", 7.0))
            if "polylines" in road_surface_data:
                for poly in road_surface_data["polylines"]:
                    self.points.extend(poly.get("points", []))
            elif "points" in road_surface_data:
                self.points = road_surface_data["points"]
        elif isinstance(road_surface_data, list):
            self.points = road_surface_data
            
        self.verified_point = None  # Will store the found point data

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f4ff, stop:1 #e6e6fa);
                border-radius: 12px;
            }
            QLabel { font-weight: bold; color: #333; }
            QLineEdit {
                padding: 6px; border: 1px solid #ccc; border-radius: 4px;
            }
            QPushButton {
                padding: 6px 12px; border-radius: 4px; font-weight: bold;
                background-color: #007bff; color: white; border: none;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton:disabled { background-color: #cccccc; color: #666; }
            QGroupBox {
                border: 1px solid #aaa; border-radius: 6px; margin-top: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
            QRadioButton {
                font-weight: bold;
                color: #333;
            }
        """)

        layout = QVBoxLayout(self)
        
        # ── Mode Selection (Edit vs Drop) - Always create, but visibility controlled ──
        self.mode_group = QWidget()
        mode_layout = QHBoxLayout(self.mode_group)
        mode_layout.setContentsMargins(0, 0, 0, 10)
        
        self.radio_edit = QRadioButton("Edit")
        self.radio_edit.setChecked(True)
        self.radio_edit.setStyleSheet("font-weight: bold; color: #333;")
        self.radio_drop = QRadioButton("Drop")
        self.radio_drop.setStyleSheet("font-weight: bold; color: #333;")
        
        mode_layout.addWidget(QLabel("Mode:"))
        mode_layout.addWidget(self.radio_edit)
        mode_layout.addWidget(self.radio_drop)
        mode_layout.addStretch()
        
        layout.addWidget(self.mode_group)
        
        self.radio_edit.toggled.connect(self._toggle_mode)
        self.radio_drop.toggled.connect(self._toggle_mode)
        
        # Only show mode group when in edit mode
        if not is_edit_mode:
            self.mode_group.setVisible(False)

        # --- Chainage Input ---
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Chainage:"))
        self.chainage_input = QLineEdit()
        self.chainage_input.setPlaceholderText("Enter chainage (e.g. 50+100 or 100)")
        h_layout.addWidget(self.chainage_input)
        
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.clicked.connect(self.verify_chainage)
        h_layout.addWidget(self.verify_btn)
        layout.addLayout(h_layout)

        # --- Status Label ---
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red; font-weight: normal;")
        layout.addWidget(self.status_label)

        # --- Pole Position Selection ---
        self.position_group = QGroupBox("Pole Position")
        self.position_group.setEnabled(False)  # Disabled until verified
        position_layout = QHBoxLayout(self.position_group)
        
        self.check_left_shoulder = QCheckBox("Left Shoulder")
        self.check_right_shoulder = QCheckBox("Right Shoulder")
        self.check_center = QCheckBox("Center")
        
        position_layout.addWidget(self.check_left_shoulder)
        position_layout.addWidget(self.check_center)
        position_layout.addWidget(self.check_right_shoulder)
        layout.addWidget(self.position_group)

        # --- Orientation Selection (Inner / Outer) ---
        self.orient_group = QGroupBox("Pole Direction")
        self.orient_group.setEnabled(False)
        orient_layout = QHBoxLayout(self.orient_group)
        
        self.check_inner = QCheckBox("Inner (Towards Road)")
        self.check_outer = QCheckBox("Outer (Away from Road)")
        self.check_inner.setChecked(True) # Default
        
        # Exclusive check logic
        self.check_inner.toggled.connect(lambda: self.check_outer.setChecked(not self.check_inner.isChecked()))
        self.check_outer.toggled.connect(lambda: self.check_inner.setChecked(not self.check_outer.isChecked()))
        
        orient_layout.addWidget(self.check_inner)
        orient_layout.addWidget(self.check_outer)
        layout.addWidget(self.orient_group)

        # Connect position checkboxes to toggle center config visibility (REMOVED)
        # self.check_center.toggled.connect(self.toggle_center_config)
        
        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False) # Enabled after verification
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("background-color: #6c757d;")
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _toggle_mode(self):
        """Toggle UI elements based on Edit vs Drop mode selection."""
        is_drop = self.radio_drop.isChecked()
        
        if is_drop:
            # In drop mode, adjust the UI if needed
            pass
        else:
            # In edit mode, show normal configuration
            pass

    def verify_chainage(self):
        txt = self.chainage_input.text().strip()
        if not txt:
            self.status_label.setText("Please enter a chainage.")
            return
        
        found = None
        
        # Helper to parse "50+100" -> (50, 100)
        def parse_ch(s):
            s = str(s).replace(" ", "")
            if "+" in s:
                parts = s.split("+")
                if len(parts) == 2:
                    try:
                        return float(parts[0]), float(parts[1])
                    except:
                        return None, None
            else:
                try:
                    return 0.0, float(s)
                except:
                    return None, None
            return None, None

        target_km, target_m = parse_ch(txt)
        
        # Iterate and search
        for item in self.points:
            # Check match against chainage_str
            c_str = item.get("chainage_str", "")
            c_m_val = float(item.get("chainage_m", -9999))
            
            # 1. Try matching string parts (KM + M)
            ckm, cm = parse_ch(c_str)
            if target_km is not None and ckm is not None:
                # Compare KM (exact) and M (tolerance)
                if ckm == target_km and abs(cm - target_m) < 0.1:
                    found = item
                    break
            
            # 2. Try matching raw float input against chainage_m
            # Only if user input didn't look like KM+M (target_km is 0 or user just typed number)
            # But the user might type "100" meaning 100m.
            if "+" not in txt:
                try:
                    val = float(txt)
                    if abs(val - c_m_val) < 0.1:
                        found = item
                        break
                except:
                    pass

        if found:
            # Prepare verified data enriched with global width and standardized point
            self.verified_point = found.copy()
            
            # Ensure 'width' is available for the backend
            if 'width' not in self.verified_point:
                self.verified_point['width'] = self.global_width
                
            # Ensure 'point' key exists for backend (it uses 'point' or 'x,y,z')
            if 'point' not in self.verified_point and 'world_coordinates' in self.verified_point:
                self.verified_point['point'] = self.verified_point['world_coordinates']
            
            self.status_label.setText(f"Verified: {found.get('chainage_str', 'Found')}")
            self.status_label.setStyleSheet("color: green;")
            self.position_group.setEnabled(True)
            self.orient_group.setEnabled(True)
            self.ok_btn.setEnabled(True)
        else:
            self.verified_point = None
            self.status_label.setText("Not Found: Chainage verification failed.")
            self.status_label.setStyleSheet("color: red;")
            self.position_group.setEnabled(False)
            self.orient_group.setEnabled(False)
            self.ok_btn.setEnabled(False)

    def get_data(self):
        return {
            "chainage": self.chainage_input.text(), # Return the string input or the verified chainage
            "left_shoulder": self.check_left_shoulder.isChecked(),
            "right_shoulder": self.check_right_shoulder.isChecked(),
            "center": self.check_center.isChecked(),
            "inner": self.check_inner.isChecked(),
            "outer": self.check_outer.isChecked(),
            "one_direction": True, # Base is one direction
            "two_direction": False,
            "four_direction": False,
            "point_data": self.verified_point,
            "is_drop_mode": self.radio_drop.isChecked()  # Safe now - always created
        }

# ** SIGNAL POLE CONFIG DIALOG **
# ===========================================================================================================================
class SignalPoleDialog(StreetLightDialog):
    def __init__(self, road_surface_data=None, is_edit_mode=False, parent=None):
        super().__init__(road_surface_data, is_edit_mode, parent)
        self.setWindowTitle("Signal Pole Configuration")

# --- Specialized Street Light Dialogs ---
class OneDirectionStreetLightDialog(StreetLightDialog):
    def __init__(self, road_surface_data=None, is_edit_mode=False, parent=None):
        super().__init__(road_surface_data, is_edit_mode, parent)
        self.setWindowTitle("One Direction Street Light Configuration")

class TwoDirectionStreetLightDialog(StreetLightDialog):
    def __init__(self, road_surface_data=None, is_edit_mode=False, parent=None):
        super().__init__(road_surface_data, is_edit_mode, parent)
        self.setWindowTitle("Two Direction Street Light Configuration")
    
    def get_data(self):
        data = super().get_data()
        data["one_direction"] = False
        data["two_direction"] = True
        return data

class FourDirectionStreetLightDialog(StreetLightDialog):
    def __init__(self, road_surface_data=None, is_edit_mode=False, parent=None):
        super().__init__(road_surface_data, is_edit_mode, parent)
        self.setWindowTitle("Four Direction Street Light Configuration")
    
    def get_data(self):
        data = super().get_data()
        data["one_direction"] = False
        data["four_direction"] = True
        return data

# ====================================================================================================
# --- Specialized Signal Pole Dialogs ---
class OneDirectionSignalPoleDialog(SignalPoleDialog):
    def __init__(self, road_surface_data=None, is_edit_mode=False, parent=None):
        super().__init__(road_surface_data, is_edit_mode, parent)
        self.setWindowTitle("One Direction Signal Pole Configuration")

class TwoDirectionSignalPoleDialog(SignalPoleDialog):
    def __init__(self, road_surface_data=None, is_edit_mode=False, parent=None):
        super().__init__(road_surface_data, is_edit_mode, parent)
        self.setWindowTitle("Two Direction Signal Pole Configuration")
    
    def get_data(self):
        data = super().get_data()
        data["one_direction"] = False
        data["two_direction"] = True
        return data

class FourDirectionSignalPoleDialog(SignalPoleDialog):
    def __init__(self, road_surface_data=None, parent=None):
        super().__init__(road_surface_data, parent)
        self.setWindowTitle("Four Direction Signal Pole Configuration")
    
    def get_data(self):
        data = super().get_data()
        data["one_direction"] = False
        data["four_direction"] = True
        return data

# ===========================================================================================================================
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QDoubleSpinBox, QSpinBox,
    QCheckBox, QPushButton, QScrollArea, QLineEdit, QStackedWidget, QWidget
)
from PyQt5.QtCore import Qt

class LaneMarkingDialog(QDialog):
    def __init__(self, road_surface_data=None, existing_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lane Configuration")
        self.setModal(True)
        self.resize(700, 800)
        
        self.road_surface_data = road_surface_data
        self.existing_data = existing_data
        self.from_drop_dialog = False # Flag to indicate if data comes from page 2

        # Main layout for the dialog
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Create Stacked Widget
        self.stacked_widget = QStackedWidget()
        outer_layout.addWidget(self.stacked_widget)
        
        # Configure Pages
        self.setup_page1()
        self.setup_page2()
        
        if self.existing_data:
            self._populate_from_existing_data()

    def _populate_from_existing_data(self):
        """Pre-fill the dialog fields using existing configuration Data."""
        try:
            # Look at either single config or pick first if it's a list
            data = self.existing_data[0] if isinstance(self.existing_data, list) else self.existing_data
            if not data: return
            
            # Chainages
            from_str = data.get('from_chainage_str', str(data.get('from_chainage', '')))
            to_str = data.get('to_chainage_str', str(data.get('to_chainage', '')))
            if from_str: self.from_chainage.setText(str(from_str))
            if to_str: self.to_chainage.setText(str(to_str))
            
            # Center Lane
            if 'center_lane_name' in data: self.center_lane_name.setText(str(data['center_lane_name']))
            if 'center_lane_width' in data: self.center_lane_width.setValue(float(data['center_lane_width']))
            
            # Lane counts
            left_count = int(data.get('lanes_left', 2))
            right_count = int(data.get('lanes_right', 2))
            
            self.lanes_left.setValue(left_count)
            self.lanes_right.setValue(right_count)
            
            self.update_lane_names()
            
            # Populate generated LineEdits for Left Lanes
            for i in range(min(left_count, len(self.left_name_edits))):
                name_key = f"Left Lane {i+1} Name"
                width_key = f"Left Lane {i+1} width"
                if name_key in data: self.left_name_edits[i].setText(str(data[name_key]))
                if width_key in data: self.left_width_edits[i].setValue(float(data[width_key]))
                
            # Populate generated LineEdits for Right Lanes
            for i in range(min(right_count, len(self.right_name_edits))):
                # Using lower case 'name' to match get_data output
                name_key = f"Right Lane {i+1} name"
                width_key = f"Right Lane {i+1} width"
                if name_key in data: self.right_name_edits[i].setText(str(data[name_key]))
                if width_key in data: self.right_width_edits[i].setValue(float(data[width_key]))
                
            # Shoulders
            self.shoulder_left_check.setChecked(bool(data.get('hard_shoulder_left', True)))
            self.shoulder_right_check.setChecked(bool(data.get('hard_shoulder_right', True)))
            
            if 'Left Shoulder lane name' in data: self.left_shoulder_name.setText(str(data['Left Shoulder lane name']))
            if 'Left shoulder lane width' in data: self.left_shoulder_width.setValue(float(data['Left shoulder lane width']))
            
            if 'Right shoulder lane name' in data: self.right_shoulder_name.setText(str(data['Right shoulder lane name']))
            if 'Right shoulder lane width' in data: self.right_shoulder_width.setValue(float(data['Right shoulder lane width']))
                
        except Exception as e:
            print(f"Error populating Lane Marking edit dialog: {str(e)}")
        
    def setup_page1(self):
        page1 = QWidget()
        self.stacked_widget.addWidget(page1)
        self.verified_range = None # Stores (start_m, end_m) if verified

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f4ff, stop:1 #e6e6fa);
                border-radius: 12px;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QDoubleSpinBox, QSpinBox {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-width: 140px;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                background-color: #007bff;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
            QGroupBox {
                border: 1px solid #aaa;
                border-radius: 8px;
                margin-top: 14px;
                padding: 14px 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                color: #444;
            }
            .note {
                font-weight: normal;
                font-size: 11px;
                color: #555;
            }
        """)

        main_layout = QVBoxLayout(page1)
        main_layout.setSpacing(14)

        # ── Chainage Configuration ───────────────────────────
        chainage_group = QGroupBox("Chainage Range (Optional)")
        chainage_layout = QVBoxLayout(chainage_group)
        
        c_grid = QGridLayout()
        c_grid.addWidget(QLabel("From Chainage:"), 0, 0)
        self.from_chainage = QLineEdit()
        self.from_chainage.setPlaceholderText("e.g. 100+020")
        c_grid.addWidget(self.from_chainage, 0, 1)

        c_grid.addWidget(QLabel("To Chainage:"), 0, 2)
        self.to_chainage = QLineEdit()
        self.to_chainage.setPlaceholderText("e.g. 100+100")
        c_grid.addWidget(self.to_chainage, 0, 3)
        
        self.verify_btn = QPushButton("Verify Button") # Mockup says "Verify Button"
        self.verify_btn.clicked.connect(self.verify_chainage)
        c_grid.addWidget(self.verify_btn, 1, 0, 1, 4)

        chainage_layout.addLayout(c_grid)
        
        self.chainage_status = QLabel("")
        self.chainage_status.setStyleSheet("color: red; font-weight: normal;")
        chainage_layout.addWidget(self.chainage_status)
        
        main_layout.addWidget(chainage_group)

        # ── Main group ───────────────────────────────────────
        group = QGroupBox("Lane Configuration")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignLeft)
        form.setSpacing(12)

        # 1. Center Lane Name & Width
        center_hbox = QHBoxLayout()
        self.center_lane_name = QLineEdit()
        self.center_lane_name.setPlaceholderText("Name")
        self.center_lane_width = QDoubleSpinBox()
        self.center_lane_width.setRange(0.0, 50.0)
        self.center_lane_width.setSingleStep(0.1)
        self.center_lane_width.setValue(0.0)
        self.center_lane_width.setSuffix(" m")
        
        center_hbox.addWidget(QLabel("Name:"))
        center_hbox.addWidget(self.center_lane_name)
        center_hbox.addWidget(QLabel("Width:"))
        center_hbox.addWidget(self.center_lane_width)

        form.addRow("Center Lane:", center_hbox)

        # 2. Number of lanes
        self.lanes_left = QSpinBox()
        self.lanes_left.setRange(0, 8)
        self.lanes_left.setValue(2)

        self.lanes_right = QSpinBox()
        self.lanes_right.setRange(0, 8)
        self.lanes_right.setValue(2)

        hbox_lanes = QHBoxLayout()
        hbox_lanes.addWidget(QLabel("No. of Left Lanes:"))
        hbox_lanes.addWidget(self.lanes_left)
        hbox_lanes.addStretch(1)
        hbox_lanes.addWidget(QLabel("No. of Right Lanes:"))
        hbox_lanes.addWidget(self.lanes_right)

        form.addRow("", hbox_lanes)

        # ── Lane Names & Widths Input ────────────────────────
        self.lane_names_container = QWidget()
        self.lane_names_layout = QHBoxLayout(self.lane_names_container)
        self.lane_names_layout.setContentsMargins(0, 0, 0, 0)
        
        self.left_names_layout = QVBoxLayout()
        self.left_names_layout.setAlignment(Qt.AlignTop)
        
        self.right_names_layout = QVBoxLayout()
        self.right_names_layout.setAlignment(Qt.AlignTop)
        
        self.lane_names_layout.addLayout(self.left_names_layout)
        self.lane_names_layout.addSpacing(20)
        self.lane_names_layout.addLayout(self.right_names_layout)
        
        form.addRow(self.lane_names_container)

        self.left_name_edits = []
        self.left_width_edits = []
        self.right_name_edits = []
        self.right_width_edits = []

        self.lanes_left.valueChanged.connect(self.update_lane_names)
        self.lanes_right.valueChanged.connect(self.update_lane_names)
        
        # 3. Hard Shoulder
        shoulder_title_hbox = QHBoxLayout()
        self.shoulder_left_check = QCheckBox("Left")
        self.shoulder_right_check = QCheckBox("Right")
        shoulder_title_hbox.addWidget(QLabel("Hard Shoulder :"))
        shoulder_title_hbox.addWidget(self.shoulder_left_check)
        shoulder_title_hbox.addSpacing(20)
        shoulder_title_hbox.addWidget(self.shoulder_right_check)
        shoulder_title_hbox.addStretch(1)
        form.addRow("", shoulder_title_hbox)

        shoulder_grid = QGridLayout()
        # Left Shoulder
        shoulder_grid.addWidget(QLabel("Left Shoulder Name:"), 0, 0)
        self.left_shoulder_name = QLineEdit()
        shoulder_grid.addWidget(self.left_shoulder_name, 0, 1)
        
        shoulder_grid.addWidget(QLabel("Left Shoulder width:"), 1, 0)
        self.left_shoulder_width = QDoubleSpinBox()
        self.left_shoulder_width.setRange(0.0, 10.0)
        self.left_shoulder_width.setValue(2.5)
        self.left_shoulder_width.setSuffix(" m")
        shoulder_grid.addWidget(self.left_shoulder_width, 1, 1)

        # Right Shoulder
        shoulder_grid.addWidget(QLabel("Right Shoulder Name:"), 0, 2)
        self.right_shoulder_name = QLineEdit()
        shoulder_grid.addWidget(self.right_shoulder_name, 0, 3)
        
        shoulder_grid.addWidget(QLabel("Right Shoulder width:"), 1, 2)
        self.right_shoulder_width = QDoubleSpinBox()
        self.right_shoulder_width.setRange(0.0, 10.0)
        self.right_shoulder_width.setValue(2.5)
        self.right_shoulder_width.setSuffix(" m")
        shoulder_grid.addWidget(self.right_shoulder_width, 1, 3)

        form.addRow("", shoulder_grid)

        # Initial population of lane list
        self.update_lane_names()

        main_layout.addWidget(group)

        # ── Buttons ──────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        self.drop_lane_btn = QPushButton("Drop / Extrude Lane Configuration")
        self.drop_lane_btn.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
        self.drop_lane_btn.clicked.connect(self.switch_to_page2)

        self.ok_btn = QPushButton("OK / Apply")
        self.ok_btn.setMinimumWidth(130)
        self.ok_btn.clicked.connect(self.accept_page1)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(130)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("background-color: #6c757d; color: white;")

        btn_layout.addStretch()
        btn_layout.addWidget(self.drop_lane_btn)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(cancel_btn)

        main_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

    def setup_page2(self):
        self.page2 = QWidget()
        self.stacked_widget.addWidget(self.page2)
        
        main_layout = QVBoxLayout(self.page2)
        
        # Scroll area setup
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        
        main_layout.addWidget(self.scroll_area, 1) # stretch 1
        
        self.sections = [] # List to hold individual section data objects (widgets/inputs)
        
        # Add default 2 sections
        self.add_section()
        self.add_section()
        
        # Add Section Button
        self.add_btn_layout = QHBoxLayout()
        self.add_sec_btn = QPushButton("+ Add Section")
        self.add_sec_btn.clicked.connect(self.add_section)
        self.add_btn_layout.addStretch()
        self.add_btn_layout.addWidget(self.add_sec_btn)
        self.add_btn_layout.addStretch()
        main_layout.addLayout(self.add_btn_layout)
        
        # Buttons Bottom
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        back_btn = QPushButton("Back")
        back_btn.setMinimumWidth(130)
        back_btn.clicked.connect(self.switch_to_page1)

        self.ok_btn_p2 = QPushButton("OK / Apply")
        self.ok_btn_p2.setMinimumWidth(130)
        self.ok_btn_p2.clicked.connect(self.accept_page2)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(130)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("background-color: #6c757d; color: white;")

        btn_layout.addStretch()
        btn_layout.addWidget(back_btn)
        btn_layout.addWidget(self.ok_btn_p2)
        btn_layout.addWidget(cancel_btn)

        main_layout.addLayout(btn_layout)

    def switch_to_page1(self):
        self.stacked_widget.setCurrentIndex(0)
        
    def switch_to_page2(self):
        self.stacked_widget.setCurrentIndex(1)
        
    def remove_section(self, widgets, group):
        self.sections.remove(widgets)
        self.scroll_layout.removeWidget(group)
        group.deleteLater()
        
        # Renumber remaining sections
        for idx, w in enumerate(self.sections):
            w['group'].setTitle(f"Section {idx + 1}")

    def add_section(self):
        section_num = len(self.sections) + 1
        group = QGroupBox(f"Section {section_num}")
        form = QFormLayout(group)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignLeft)
        
        # Dictionary to store references to widgets for this section
        widgets = {'group': group}
        
        # Top bar with Remove Button
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        rem_btn = QPushButton("Remove Section")
        rem_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        rem_btn.clicked.connect(lambda _, w=widgets, g=group: self.remove_section(w, g))
        top_bar.addWidget(rem_btn)
        form.addRow(top_bar)
        
        # Chainage Range
        hbox_f = QHBoxLayout()
        widgets['from_ch'] = QLineEdit()
        widgets['from_ch'].setPlaceholderText("e.g. 100+000")
        hbox_f.addWidget(widgets['from_ch'])
        form.addRow("From Chainage:", hbox_f)
        
        hbox_t = QHBoxLayout()
        widgets['to_ch'] = QLineEdit()
        widgets['to_ch'].setPlaceholderText("e.g. 100+260")
        hbox_t.addWidget(widgets['to_ch'])
        form.addRow("To Chainage:", hbox_t)
        
        # Section Verification
        verify_btn = QPushButton("Verify Range")
        verify_btn.clicked.connect(lambda _, w=widgets: self.verify_section_chainage(w))
        
        widgets['status_label'] = QLabel("")
        widgets['status_label'].setStyleSheet("color: red; font-weight: normal;")
        
        form.addRow("", verify_btn)
        form.addRow("", widgets['status_label'])
        
        widgets['verified_range'] = None # Store verification result
        
        # Center Lane Name & Width
        center_hbox = QHBoxLayout()
        widgets['center_lane_name'] = QLineEdit()
        widgets['center_lane_name'].setPlaceholderText("Name")
        widgets['center_lane'] = QDoubleSpinBox()
        widgets['center_lane'].setRange(0.0, 10.0)
        widgets['center_lane'].setValue(3.0)
        widgets['center_lane'].setSuffix(" m")
        
        center_hbox.addWidget(QLabel("Name:"))
        center_hbox.addWidget(widgets['center_lane_name'])
        center_hbox.addWidget(QLabel("Width:"))
        center_hbox.addWidget(widgets['center_lane'])
        form.addRow("1. Center Lane:", center_hbox)
        
        # Lanes Left/Right
        hbox_count = QHBoxLayout()
        widgets['lanes_left'] = QSpinBox()
        widgets['lanes_left'].setRange(0, 10)
        widgets['lanes_left'].setValue(2)
        hbox_count.addWidget(QLabel("No. of Left Lanes:"))
        hbox_count.addWidget(widgets['lanes_left'])
        
        hbox_count.addStretch(1)
        
        widgets['lanes_right'] = QSpinBox()
        widgets['lanes_right'].setRange(0, 10)
        widgets['lanes_right'].setValue(2)
        hbox_count.addWidget(QLabel("No. of Right Lanes:"))
        hbox_count.addWidget(widgets['lanes_right'])
        
        form.addRow("2. Number of lanes:", hbox_count)
        
        widgets['left_layout'] = QVBoxLayout()
        widgets['right_layout'] = QVBoxLayout()
        
        name_container = QHBoxLayout()
        name_container.addLayout(widgets['left_layout'])
        name_container.addSpacing(20)
        name_container.addLayout(widgets['right_layout'])
        form.addRow(name_container)
        
        widgets['left_name_edits'] = []
        widgets['left_width_edits'] = []
        widgets['right_name_edits'] = []
        widgets['right_width_edits'] = []
        
        def update_names():
            def clear_inner(layout):
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget(): item.widget().deleteLater()
                    elif item.layout(): clear_inner(item.layout())

            clear_inner(widgets['left_layout'])
            clear_inner(widgets['right_layout'])
            widgets['left_name_edits'].clear()
            widgets['left_width_edits'].clear()
            widgets['right_name_edits'].clear()
            widgets['right_width_edits'].clear()
            
            nl = widgets['lanes_left'].value()
            for i in range(nl):
                row = QGridLayout()
                row.addWidget(QLabel(f"Left lane {i+1} Name:"), 0, 0)
                le_name = QLineEdit()
                le_name.setText(f"L{i+1}")
                row.addWidget(le_name, 0, 1)
                
                row.addWidget(QLabel(f"Left lane {i+1} width:"), 1, 0)
                le_width = QDoubleSpinBox()
                le_width.setRange(0.0, 10.0)
                le_width.setValue(3.5)
                le_width.setSuffix(" m")
                row.addWidget(le_width, 1, 1)
                
                widgets['left_layout'].addLayout(row)
                widgets['left_name_edits'].append(le_name)
                widgets['left_width_edits'].append(le_width)
            
            nr = widgets['lanes_right'].value()
            for i in range(nr):
                row = QGridLayout()
                row.addWidget(QLabel(f"Right lane {i+1} Name:"), 0, 0)
                le_name = QLineEdit()
                le_name.setText(f"R{i+1}")
                row.addWidget(le_name, 0, 1)
                
                row.addWidget(QLabel(f"Right lane {i+1} width:"), 1, 0)
                le_width = QDoubleSpinBox()
                le_width.setRange(0.0, 10.0)
                le_width.setValue(3.5)
                le_width.setSuffix(" m")
                row.addWidget(le_width, 1, 1)
                
                widgets['right_layout'].addLayout(row)
                widgets['right_name_edits'].append(le_name)
                widgets['right_width_edits'].append(le_width)
                    
        widgets['lanes_left'].valueChanged.connect(update_names)
        widgets['lanes_right'].valueChanged.connect(update_names)
        update_names()

        # Shoulders
        hbox_sh_title = QHBoxLayout()
        widgets['shoulder_left_check'] = QCheckBox("Left")
        widgets['shoulder_left_check'].setChecked(True)
        widgets['shoulder_right_check'] = QCheckBox("Right")
        widgets['shoulder_right_check'].setChecked(True)
        hbox_sh_title.addWidget(QLabel("3. Hard Shoulder :"))
        hbox_sh_title.addWidget(widgets['shoulder_left_check'])
        hbox_sh_title.addSpacing(20)
        hbox_sh_title.addWidget(widgets['shoulder_right_check'])
        hbox_sh_title.addStretch(1)
        form.addRow("", hbox_sh_title)

        shoulder_grid = QGridLayout()
        # Left
        shoulder_grid.addWidget(QLabel("Left Shoulder Name:"), 0, 0)
        widgets['left_shoulder_name'] = QLineEdit()
        shoulder_grid.addWidget(widgets['left_shoulder_name'], 0, 1)
        shoulder_grid.addWidget(QLabel("Left Shoulder width:"), 1, 0)
        widgets['left_shoulder_width'] = QDoubleSpinBox()
        widgets['left_shoulder_width'].setRange(0.0, 10.0)
        widgets['left_shoulder_width'].setValue(2.5)
        widgets['left_shoulder_width'].setSuffix(" m")
        shoulder_grid.addWidget(widgets['left_shoulder_width'], 1, 1)

        # Right
        shoulder_grid.addWidget(QLabel("Right Shoulder Name:"), 0, 2)
        widgets['right_shoulder_name'] = QLineEdit()
        shoulder_grid.addWidget(widgets['right_shoulder_name'], 0, 3)
        shoulder_grid.addWidget(QLabel("Right Shoulder width:"), 1, 2)
        widgets['right_shoulder_width'] = QDoubleSpinBox()
        widgets['right_shoulder_width'].setRange(0.0, 10.0)
        widgets['right_shoulder_width'].setValue(2.5)
        widgets['right_shoulder_width'].setSuffix(" m")
        shoulder_grid.addWidget(widgets['right_shoulder_width'], 1, 3)
        
        form.addRow("", shoulder_grid)
        
        self.sections.append(widgets)
        self.scroll_layout.addWidget(group)

    def parse_chainage(self, s):
        s = s.replace(" ", "")
        try:
            if "+" in s:
                parts = s.split("+")
                if len(parts) == 2:
                    return float(parts[0]) * 1000 + float(parts[1])
            return float(s)
        except:
            return None

    def verify_section_chainage(self, widgets):
        """Verifies a single section's chainage against the road surface data"""
        status_label = widgets['status_label']
        if not self.road_surface_data:
            status_label.setText("No road surface data loaded to verify against.")
            status_label.setStyleSheet("color: orange;")
            return

        from_str = widgets['from_ch'].text().strip()
        to_str = widgets['to_ch'].text().strip()
        
        if not from_str or not to_str:
            status_label.setText("Please enter both chainages.")
            status_label.setStyleSheet("color: red;")
            return
            
        global_start_offset = 0.0
        polylines = []
        if isinstance(self.road_surface_data, dict):
            polylines = self.road_surface_data.get("polylines", [])
        elif isinstance(self.road_surface_data, list) and len(self.road_surface_data) > 0:
             polylines = self.road_surface_data

        if polylines and len(polylines) > 0:
             start_str = polylines[0].get("start_chainage_str")
             if start_str:
                 parsed_start = self.parse_chainage(start_str)
                 if parsed_start is not None:
                     global_start_offset = parsed_start
                     
        min_c = float('inf')
        max_c = float('-inf')
        valid_points_count = 0
        
        for poly in polylines:
            for pt in poly.get("points", []):
                c = pt.get("chainage_m")
                if c is not None:
                    c = float(c)
                    if c < min_c: min_c = c
                    if c > max_c: max_c = c
                    valid_points_count += 1
                    
        if valid_points_count == 0:
             status_label.setText("Could not determine road range.")
             return
             
        user_start_abs = self.parse_chainage(from_str)
        user_end_abs = self.parse_chainage(to_str)
        
        if user_start_abs is None or user_end_abs is None:
             status_label.setText("Invalid chainage format.")
             return
             
        if user_start_abs > user_end_abs:
            user_start_abs, user_end_abs = user_end_abs, user_start_abs

        rel_start = user_start_abs - global_start_offset
        rel_end = user_end_abs - global_start_offset
        
        if rel_end < (min_c - 0.1) or rel_start > (max_c + 0.1):
             status_label.setText(f"Out of bounds. Road: {min_c:.1f} to {max_c:.1f} (Offset: {global_start_offset:.1f})")
             status_label.setStyleSheet("color: red;")
             widgets['verified_range'] = None
        else:
             widgets['verified_range'] = (rel_start, rel_end)
             status_label.setText(f"Verified! Valid segment: {rel_start:.1f}m to {rel_end:.1f}m")
             status_label.setStyleSheet("color: green; font-weight: bold;")

    def accept_page2(self):
        from PyQt5.QtWidgets import QMessageBox
        
        # 1. Validation hook
        for i, widgets in enumerate(self.sections):
            f_str = widgets['from_ch'].text().strip()
            t_str = widgets['to_ch'].text().strip()
            if not f_str or not t_str:
                QMessageBox.warning(self, "Missing Values", f"Please enter both chainages in Section {i+1}.")
                return
                
            f_val = self.parse_chainage(f_str)
            t_val = self.parse_chainage(t_str)
            if f_val is None or t_val is None:
                QMessageBox.warning(self, "Invalid Chainage", f"Invalid chainage format in Section {i+1}.")
                return
                
            if widgets['verified_range'] is None:
                QMessageBox.warning(self, "Unverified Chainage", f"Please explicitly verify Section {i+1}'s chainage range before applying.")
                return
                
        # 2. Extract Data perfectly mirroring Page 1's format
        global_start_offset = 0.0
        polylines = []
        if isinstance(self.road_surface_data, dict):
            polylines = self.road_surface_data.get("polylines", [])
        elif isinstance(self.road_surface_data, list):
            if len(self.road_surface_data) > 0 and 'points' in self.road_surface_data[0]:
                polylines = self.road_surface_data
        if polylines:
             start_str = polylines[0].get("start_chainage_str")
             if start_str:
                 try:
                     if "+" in start_str:
                         p = start_str.split("+")
                         global_start_offset = float(p[0])*1000 + float(p[1])
                     else:
                         global_start_offset = float(start_str)
                 except: pass

        def get_xyz_at_relative(target_rel):
            closest_p = None
            min_dist = float('inf')
            for poly in polylines:
                for pt in poly.get("points", []):
                    c = pt.get("chainage_m")
                    if c is not None:
                        dist = abs(float(c) - target_rel)
                        if dist < min_dist:
                            min_dist = dist
                            closest_p = pt
            if closest_p:
                if 'point' in closest_p: return closest_p['point']
                if 'world_coordinates' in closest_p: return closest_p['world_coordinates']
                if 'x' in closest_p: return [closest_p['x'], closest_p['y'], closest_p['z']]
            return [0.0, 0.0, 0.0]

        data_list = []
        for widgets in self.sections:
             from_str = widgets['from_ch'].text().strip()
             to_str = widgets['to_ch'].text().strip()
             v_start, v_end = widgets['verified_range']
             
             def parse_km_m(s):
                 s = s.replace(" ", "")
                 try:
                     if "+" in s:
                         parts = s.split("+")
                         return int(parts[0]), float(parts[1])
                     return int(float(s) // 1000), float(s) % 1000
                 except: pass
                 return 0, 0.0
                  
             f_km, f_m = parse_km_m(from_str)
             t_km, t_m = parse_km_m(to_str)
             f_xyz = get_xyz_at_relative(v_start)
             t_xyz = get_xyz_at_relative(v_end)
             
             data = {
                 "from_km": f_km,
                 "from_chainage": int(f_m),
                 "to_km": t_km,
                 "to_chainage": int(t_m),
                 "from_chainage_str": from_str,
                 "to_chainage_str": to_str,
                 f"from chainage coordinates : ({from_str})": {
                    "x": f_xyz[0],
                    "y": f_xyz[1],
                    "z": f_xyz[2]
                 },
                 f"to chainage coordinates : ({to_str})": {
                    "x": t_xyz[0],
                    "y": t_xyz[1],
                    "z": t_xyz[2]
                 },
                 "center_lane_name": widgets['center_lane_name'].text(),
                 "center_lane_width": widgets['center_lane'].value(),
             }

             # Left Lanes
             for i, (edit_n, edit_w) in enumerate(zip(widgets['left_name_edits'], widgets['left_width_edits'])):
                 data[f"Left Lane {i+1} Name"] = edit_n.text()
                 data[f"Left Lane {i+1} width"] = edit_w.value()

             # Right Lanes
             for i, (edit_n, edit_w) in enumerate(zip(widgets['right_name_edits'], widgets['right_width_edits'])):
                 data[f"Right Lane {i+1} name"] = edit_n.text()
                 data[f"Right Lane {i+1} width"] = edit_w.value()

             # Shoulders
             data["Left Shoulder lane name"] = widgets['left_shoulder_name'].text()
             data["Left shoulder lane width"] = widgets['left_shoulder_width'].value()
             data["Right shoulder lane name"] = widgets['right_shoulder_name'].text()
             data["Right shoulder lane width"] = widgets['right_shoulder_width'].value()

             # Internal properties
             data['from_chainage_rel'] = v_start
             data['to_chainage_rel'] = v_end
             data["from_xyz"] = f_xyz
             data["to_xyz"] = t_xyz
             data["lanes_left"] = widgets['lanes_left'].value()
             data["lanes_right"] = widgets['lanes_right'].value()
             data["hard_shoulder_left"] = widgets['shoulder_left_check'].isChecked()
             data["hard_shoulder_right"] = widgets['shoulder_right_check'].isChecked()

             data_list.append(data)
             
        self.drop_lane_data = data_list
        self.from_drop_dialog = True
        QDialog.accept(self)

    def verify_chainage(self):
        """Parse and verify the entered chainage range against road_surface_data"""
        if not self.road_surface_data:
            self.chainage_status.setText("No road surface data loaded to verify against.")
            self.chainage_status.setStyleSheet("color: orange;")
            return

        from_str = self.from_chainage.text().strip()
        to_str = self.to_chainage.text().strip()
        
        if not from_str or not to_str:
            self.chainage_status.setText("Please enter both From and To chainages.")
            self.chainage_status.setStyleSheet("color: red;")
            return
        
        # ============================================================================================================================
        # Helper function to parse chainage strings into absolute meters
        def parse_chainage(s):
            # Formats: "100+020" -> 100020.0, "100.020" -> 100.020, "100" -> 100.0
            s = s.replace(" ", "")
            try:
                if "+" in s:
                    parts = s.split("+")
                    if len(parts) == 2:
                         return float(parts[0]) * 1000 + float(parts[1])
                return float(s)
            except:
                return None

        # 1. Determine Global Start Offset from Data
        global_start_offset = 0.0
        
        polylines = []
        if isinstance(self.road_surface_data, dict):
            polylines = self.road_surface_data.get("polylines", [])
        elif isinstance(self.road_surface_data, list):
             if len(self.road_surface_data) > 0:
                 if 'points' in self.road_surface_data[0]:
                     polylines = self.road_surface_data
                 else:
                     pass

        if polylines and len(polylines) > 0:
             start_str = polylines[0].get("start_chainage_str")
             if start_str:
                 parsed_start = parse_chainage(start_str)
                 if parsed_start is not None:
                     global_start_offset = parsed_start
        
        # 2. Collect Min/Max RELATIVE Chainage
        min_c = float('inf')
        max_c = float('-inf')
        valid_points_count = 0
        
        for poly in polylines:
            for pt in poly.get("points", []):
                c = pt.get("chainage_m")
                if c is not None:
                    c = float(c)
                    if c < min_c: min_c = c
                    if c > max_c: max_c = c
                    valid_points_count += 1
        
        if valid_points_count == 0:
             self.chainage_status.setText("Could not determine road chainage range.")
             return

        # 3. Parse Inputs
        user_start_abs = parse_chainage(from_str)
        user_end_abs = parse_chainage(to_str)
        
        if user_start_abs is None or user_end_abs is None:
             self.chainage_status.setText("Invalid chainage format.")
             return
             
        if user_start_abs > user_end_abs:
            user_start_abs, user_end_abs = user_end_abs, user_start_abs

        # 4. Convert to Relative
        rel_start = user_start_abs - global_start_offset
        rel_end = user_end_abs - global_start_offset
        
        # 5. Verify against Relative Limits [min_c, max_c]
        if rel_end < (min_c - 0.1) or rel_start > (max_c + 0.1):
             self.chainage_status.setText(f"Range out of bounds. Road Relative: {min_c:.1f} to {max_c:.1f} (Offset: {global_start_offset:.1f})")
             self.chainage_status.setStyleSheet("color: red;")
             self.verified_range = None
        else:
             self.verified_range = (rel_start, rel_end)
             self.chainage_status.setText(f"Verified! Valid segment: {rel_start:.1f}m to {rel_end:.1f}m")
             self.chainage_status.setStyleSheet("color: green; font-weight: bold;")

    # =======================================================================================================================================
    # This method is called after the user clicks OK/Apply. It returns all the configuration data, including the verified chainage range and also attempts to find the corresponding 3D coordinates for the start and end chainages based on the road surface data.         

    def get_data(self):
        """Returns either the normal data dictionary OR a list of dictionaries if drop lane config is used."""
        if getattr(self, 'from_drop_dialog', False) and hasattr(self, 'drop_lane_data'):
            return self.drop_lane_data
        
        print("DEBUG: Executing updated LaneMarkingDialog.get_data with KM parsing and per-lane data")
        
        def parse_km_m(s):
            s = s.strip().replace(" ", "")
            try:
                if "+" in s:
                    parts = s.split("+")
                    if len(parts) == 2:
                        km = int(parts[0])
                        m = float(parts[1])
                        return km, m, km * 1000 + m
                else:
                    val = float(s)
                    km = int(val // 1000)
                    m = val % 1000
                    return km, m, val
            except:
                return 0, 0.0, 0.0

        f_txt = self.from_chainage.text()
        t_txt = self.to_chainage.text()

        f_km, f_m, f_abs = parse_km_m(f_txt)
        t_km, t_m, t_abs = parse_km_m(t_txt)

        global_start_offset = 0.0
        polylines = []
        if isinstance(self.road_surface_data, dict):
            polylines = self.road_surface_data.get("polylines", [])
        elif isinstance(self.road_surface_data, list):
            if len(self.road_surface_data) > 0 and 'points' in self.road_surface_data[0]:
                polylines = self.road_surface_data
        
        if polylines:
             start_str = polylines[0].get("start_chainage_str")
             if start_str:
                 try:
                     if "+" in start_str:
                         p = start_str.split("+")
                         global_start_offset = float(p[0])*1000 + float(p[1])
                     else:
                         global_start_offset = float(start_str)
                 except: pass

        rel_start = f_abs - global_start_offset
        rel_end = t_abs - global_start_offset

        def get_xyz_at_relative(target_rel):
            closest_p = None
            min_dist = float('inf')
            for poly in polylines:
                for pt in poly.get("points", []):
                    c = pt.get("chainage_m")
                    if c is not None:
                        dist = abs(float(c) - target_rel)
                        if dist < min_dist:
                            min_dist = dist
                            closest_p = pt
            if closest_p:
                if 'point' in closest_p: return closest_p['point']
                if 'world_coordinates' in closest_p: return closest_p['world_coordinates']
                if 'x' in closest_p: return [closest_p['x'], closest_p['y'], closest_p['z']]
            return [0.0, 0.0, 0.0]

        f_xyz = get_xyz_at_relative(rel_start)
        t_xyz = get_xyz_at_relative(rel_end)

        result = {
            "from_km": f_km,
            "from_chainage": int(f_m),
            "to_km": t_km,
            "to_chainage": int(t_m),
            "from_chainage_str": f_txt,
            "to_chainage_str": t_txt,
            f"from chainage coordinates : ({f_txt})": {
                "x": f_xyz[0],
                "y": f_xyz[1],
                "z": f_xyz[2]
            },
            f"to chainage coordinates : ({t_txt})": {
                "x": t_xyz[0],
                "y": t_xyz[1],
                "z": t_xyz[2]
            },
            "center_lane_name": self.center_lane_name.text(),
            "center_lane_width": self.center_lane_width.value(),
        }

        # Left Lanes
        for i, (edit_n, edit_w) in enumerate(zip(self.left_name_edits, self.left_width_edits)):
            result[f"Left Lane {i+1} Name"] = edit_n.text()
            result[f"Left Lane {i+1} width"] = edit_w.value()

        # Right Lanes
        for i, (edit_n, edit_w) in enumerate(zip(self.right_name_edits, self.right_width_edits)):
            result[f"Right Lane {i+1} name"] = edit_n.text()
            result[f"Right Lane {i+1} width"] = edit_w.value()

        # Shoulders
        result["Left Shoulder lane name"] = self.left_shoulder_name.text()
        result["Left shoulder lane width"] = self.left_shoulder_width.value()
        result["Right shoulder lane name"] = self.right_shoulder_name.text()
        result["Right shoulder lane width"] = self.right_shoulder_width.value()

        # Add internal properties for rendering/backward compatibility if needed by the app
        result["from_chainage_rel"] = rel_start
        result["to_chainage_rel"] = rel_end
        result["from_xyz"] = f_xyz
        result["to_xyz"] = t_xyz
        result["lanes_left"] = self.lanes_left.value()
        result["lanes_right"] = self.lanes_right.value()
        result["hard_shoulder_left"] = self.shoulder_left_check.isChecked()
        result["hard_shoulder_right"] = self.shoulder_right_check.isChecked()

        return result

    # =======================================================================================================================================
    """This method dynamically updates the lane name input fields based on the current number of lanes specified for left and right. 
       It clears existing inputs and regenerates them with appropriate placeholders."""
    def update_lane_names(self):
        """Re-generate lane name and width inputs based on current lane counts"""
        def clear_layout(layout):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget: widget.deleteLater()
                elif item.layout(): clear_layout(item.layout())
        
        clear_layout(self.left_names_layout)
        clear_layout(self.right_names_layout)
        self.left_name_edits.clear()
        self.left_width_edits.clear()
        self.right_name_edits.clear()
        self.right_width_edits.clear()
        
        # Generate Left Inputs
        count_left = self.lanes_left.value()
        for i in range(count_left):
            row = QGridLayout()
            row.addWidget(QLabel(f"Left lane {i+1} Name:"), 0, 0)
            le_name = QLineEdit()
            le_name.setPlaceholderText(f"L{i+1}")
            row.addWidget(le_name, 0, 1)
            
            row.addWidget(QLabel(f"Left lane {i+1} width:"), 1, 0)
            le_width = QDoubleSpinBox()
            le_width.setRange(0.0, 10.0)
            le_width.setValue(3.5)
            le_width.setSuffix(" m")
            row.addWidget(le_width, 1, 1)
            
            self.left_names_layout.addLayout(row)
            self.left_name_edits.append(le_name)
            self.left_width_edits.append(le_width)
        
        # Generate Right Inputs
        count_right = self.lanes_right.value()
        for i in range(count_right):
            row = QGridLayout()
            row.addWidget(QLabel(f"Right lane {i+1} Name:"), 0, 0)
            le_name = QLineEdit()
            le_name.setPlaceholderText(f"R{i+1}")
            row.addWidget(le_name, 0, 1)
            
            row.addWidget(QLabel(f"Right lane {i+1} width:"), 1, 0)
            le_width = QDoubleSpinBox()
            le_width.setRange(0.0, 10.0)
            le_width.setValue(3.5)
            le_width.setSuffix(" m")
            row.addWidget(le_width, 1, 1)
            
            self.right_names_layout.addLayout(row)
            self.right_name_edits.append(le_name)
            self.right_width_edits.append(le_width)

    def accept_page1(self):
        """
        Validate inputs for page-1 and close dialog.
        This must call accept so caller can save lane_marking.json locally.
        """
        from PyQt5.QtWidgets import QMessageBox

        from_str = self.from_chainage.text().strip()
        to_str = self.to_chainage.text().strip()

        # Chainage range is optional. If user enters any value, require full verified range.
        if from_str or to_str:
            if not from_str or not to_str:
                QMessageBox.warning(self, "Missing Chainage", "Please enter both From and To chainages.")
                return

            self.verify_chainage()
            if getattr(self, 'verified_range', None) is None:
                QMessageBox.warning(self, "Invalid Chainage", "Please verify a valid chainage range before applying.")
                return

        # Basic width sanity check to avoid saving an empty/invalid lane configuration.
        center_w = self.center_lane_width.value()
        left_lanes_w = sum(edit.value() for edit in self.left_width_edits)
        right_lanes_w = sum(edit.value() for edit in self.right_width_edits)
        shoulder_l_w = self.left_shoulder_width.value() if self.shoulder_left_check.isChecked() else 0.0
        shoulder_r_w = self.right_shoulder_width.value() if self.shoulder_right_check.isChecked() else 0.0

        total_configured_width = center_w + left_lanes_w + right_lanes_w + shoulder_l_w + shoulder_r_w
        if total_configured_width <= 0:
            QMessageBox.warning(self, "Invalid Width", "Total configured lane width must be greater than 0.")
            return

        QDialog.accept(self)


# ===========================================================================================================================
# ** BUY 3D FILES DIALOG **
# ===========================================================================================================================

from PyQt5.QtCore import QThread, pyqtSignal

class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        import requests
        import os
        try:
            response = requests.get(self.url, stream=True, timeout=30)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 8
            wrote = 0
            with open(self.save_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    if self._is_cancelled:
                        break
                    if data:
                        f.write(data)
                        wrote += len(data)
                        if total_size > 0:
                            self.progress.emit(int((wrote / total_size) * 100))
            
            if self._is_cancelled:
                if os.path.exists(self.save_path):
                    os.remove(self.save_path)
                self.error.emit("Download cancelled by user.")
            else:
                self.progress.emit(100)
                self.finished.emit(self.save_path)
        except Exception as e:
            self.error.emit(str(e))

class Buy3DFilesDialog(QDialog):
    def __init__(self, user_id, euh_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buy 3D Files")
        self.setModal(True)
        self.setMinimumSize(1200, 700)
        self.user_id = user_id        # API user ID (e.g., 7) — used for fetching files
        self.euh_id = euh_id or user_id  # EUH ID (e.g., 126002) — used in the buy URL
        self.all_files = []
        self.purchased_files = []
        self.cart_items = []
        print(f"DEBUG: Buy3DFilesDialog initialized with API user_id={self.user_id}, euh_id={self.euh_id}")
        
        self.setStyleSheet("""
            QDialog {
                background: #f0f0f0;
            }
            QGroupBox {
                border: 2px solid #007BFF;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
                font-weight: bold;
                color: #004085;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #ddd;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #007BFF;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
                cursor: pointer;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """)
        
        self.init_ui()
        self.fetch_files()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # ===== FILTER SECTION =====
        filter_group = QGroupBox("Filters")
        filter_layout = QVBoxLayout(filter_group)
        
        # Category Filters
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("File Category:"))
        
        self.category_checkboxes = {}
        for category in ["Road", "Bridge", "Metro", "Railway"]:
            checkbox = QCheckBox(category)
            checkbox.setChecked(category == "Road")  # Only Roads checked by default
            checkbox.stateChanged.connect(self.apply_filters)
            self.category_checkboxes[category] = checkbox
            category_layout.addWidget(checkbox)
        
        category_layout.addStretch()
        filter_layout.addLayout(category_layout)
        
        main_layout.addWidget(filter_group)
        
        # ===== FILES TABLE SECTION =====
        table_group = QGroupBox("Available 3D Files")
        table_layout = QVBoxLayout(table_group)
        
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(7)
        self.files_table.setHorizontalHeaderLabels([
            "Sr.No", "File Name", "Category", "Type", "Add to Cart", "Price", "Action"
        ])
        self.files_table.horizontalHeader().setStretchLastSection(False)
        self.files_table.setColumnWidth(0, 50)
        self.files_table.setColumnWidth(1, 250)
        self.files_table.setColumnWidth(2, 100)
        self.files_table.setColumnWidth(3, 100)
        self.files_table.setColumnWidth(4, 120)
        self.files_table.setColumnWidth(5, 100)
        self.files_table.setColumnWidth(6, 120)
        
        table_layout.addWidget(self.files_table)
        main_layout.addWidget(table_group)
        
        # ===== CART SECTION =====
        cart_group = QGroupBox("Shopping Cart")
        cart_layout = QHBoxLayout(cart_group)
        
        self.cart_label = QLabel("Cart Items: 0")
        self.cart_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        cart_layout.addWidget(self.cart_label)
        
        cart_layout.addStretch()
        
        clear_cart_btn = QPushButton("Clear Cart")
        clear_cart_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        clear_cart_btn.clicked.connect(self.clear_cart)
        cart_layout.addWidget(clear_cart_btn)
        
        self.total_price_label = QLabel("Total: ₹0.00")
        self.total_price_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #28a745;")
        cart_layout.addWidget(self.total_price_label)
        
        buy_btn = QPushButton("Buy Now")
        buy_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        buy_btn.clicked.connect(self.proceed_to_buy)
        cart_layout.addWidget(buy_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        close_btn.clicked.connect(self.close)
        cart_layout.addWidget(close_btn)
        
        main_layout.addWidget(cart_group)
    
    def fetch_files(self):
        """Fetch all files and purchased files from API for the current user"""
        try:
            # Fetch all available files for this user
            result_all = WorksheetAPI.get_edu_3d_files(self.user_id)
            if result_all.get("success"):
                self.all_files = result_all.get("data", [])
            
            # Fetch purchased files for this user
            result_purchased = WorksheetAPI.get_edu_3d_files(self.user_id)
            if result_purchased.get("success"):
                self.purchased_files = result_purchased.get("data", [])
            
            self.populate_table()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch files: {str(e)}")
    
    def populate_table(self):
        """Populate the table with files from API response"""
        self.files_table.setRowCount(0)
        
        # Filter files based on selection
        filtered_files = self.filter_files()
        print(f"DEBUG: populate_table() - Found {len(filtered_files)} filtered files from {len(self.all_files)} total files")
        
        # Type mapping: 1=Raw, 2=Design, 3=Measurement
        type_map = {1: "Raw", 2: "Design", 3: "Measurement"}
        
        row = 0
        for idx, file_data in enumerate(filtered_files):
            # Extract data from API response
            file_id = file_data.get("id")
            file_name = file_data.get("file_name", "Unknown")
            category_name = file_data.get("category_name", "")
            file_type_code = file_data.get("type", 0)
            file_type_name = type_map.get(file_type_code, "Unknown")
            price = file_data.get("price", 0)
            is_purchased = file_data.get("purchased", False)
            purchase_status = file_data.get("purchase_status", 1)
            purchase_type = file_data.get("purchase_type", "Paid")
            
            can_download = is_purchased or purchase_status == 2 or str(purchase_type).lower() == 'free'
            
            # Insert row
            self.files_table.insertRow(row)
            
            # Sr.No
            self.files_table.setItem(row, 0, QTableWidgetItem(str(idx + 1)))
            
            # File Name
            self.files_table.setItem(row, 1, QTableWidgetItem(file_name))
            
            # Category
            self.files_table.setItem(row, 2, QTableWidgetItem(category_name))
            
            # Type (Raw, Design, Measurement)
            self.files_table.setItem(row, 3, QTableWidgetItem(file_type_name))
            
            # Status column - Download or Add to Cart
            if can_download:
                item = QTableWidgetItem("-")
                item.setTextAlignment(Qt.AlignCenter)
                self.files_table.setItem(row, 4, item)
            else:
                status_widget = QWidget()
                status_layout = QHBoxLayout(status_widget)
                status_layout.setContentsMargins(0, 0, 0, 0)
                
                # Show Add to Cart button for non-purchased files
                add_btn = QPushButton("Add to Cart")
                add_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFA500;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #FF8C00;
                    }
                """)
                add_btn.clicked.connect(lambda checked, f=file_data, r=row: self.add_to_cart(f, r))
                status_layout.addWidget(add_btn)
                self.files_table.setCellWidget(row, 4, status_widget)
            
            # Price
            if is_purchased:
                self.files_table.setItem(row, 5, QTableWidgetItem("-"))
            elif purchase_status == 2 or str(purchase_type).lower() == 'free':
                self.files_table.setItem(row, 5, QTableWidgetItem("Free"))
            else:
                self.files_table.setItem(row, 5, QTableWidgetItem(f"₹{price}"))
            
            # Action Button (Remove from table if needed, or keep for future use)
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            if can_download:
                action_btn = QPushButton("Download")
                action_btn.setEnabled(True)
                action_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 3px;
                    }
                """)
                action_btn.clicked.connect(lambda checked, f=file_data: self.download_file(f))
            else:
                action_btn = QPushButton("Buy")
                action_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #007BFF;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #0056b3;
                    }
                """)
                action_btn.clicked.connect(lambda checked, f=file_data, r=row: self.add_to_cart(f, r))
            
            action_layout.addWidget(action_btn)
            self.files_table.setCellWidget(row, 6, action_widget)
            
            row += 1
    
    def filter_files(self):
        """Filter files based on selected categories only"""
        # Get selected categories
        selected_categories = [cat.lower() for cat, cb in self.category_checkboxes.items() if cb.isChecked()]
        
        filtered = self.all_files
        
        print(f"DEBUG: All categories in API data: {set(f.get('category_name', 'Unknown') for f in self.all_files)}")
        print(f"DEBUG: Selected categories in Filter: {selected_categories}")
        
        # Filter by category using category_name
        if selected_categories:
            filtered = [f for f in filtered if str(f.get("category_name", "")).lower() in selected_categories]
        else:
            filtered = []  # If no categories selected, show no files
        
        return filtered
    
    def apply_filters(self):
        """Apply filters and refresh table"""
        self.populate_table()
    
    def is_file_purchased(self, file_data):
        """Check if a file is already purchased using the purchased field from API"""
        # The API response has a "purchased" boolean field
        is_purchased = file_data.get("purchased", False)
        return is_purchased
    
    def on_checkbox_changed(self, row, state):
        """Handle checkbox change"""
        if state == Qt.Checked:
            # Get file data from table
            file_name_item = self.files_table.item(row, 1)
            price_item = self.files_table.item(row, 5)
            
            if file_name_item and price_item:
                file_name = file_name_item.text()
                try:
                    price = float(price_item.text().replace("₹", ""))
                except:
                    price = 0
                
                # Add to cart
                self.cart_items.append({"file_name": file_name, "price": price})
                self.update_cart()
        else:
            # Remove from cart
            file_name_item = self.files_table.item(row, 1)
            if file_name_item:
                file_name = file_name_item.text()
                self.cart_items = [item for item in self.cart_items if item["file_name"] != file_name]
                self.update_cart()
    
    def add_to_cart(self, file_data, row):
        """Add file to cart"""
        file_name = file_data.get("file_name", "")
        file_id = file_data.get("id", "")        # Internal record ID (used for duplicate check)
        tfd_id = file_data.get("tfd_id") or file_data.get("id", "")  # tfd_id for the buy URL
        price = file_data.get("price", 0)
        
        # Check if already in cart (use file_id so same-named files with different IDs can both be added)
        if file_id and any(item.get("file_id") == file_id for item in self.cart_items):
            QMessageBox.info(self, "Info", "This file is already in your cart!")
            return
        
        self.cart_items.append({"file_id": file_id, "tfd_id": tfd_id, "file_name": file_name, "price": price})
        self.update_cart()
        
        QMessageBox.info(self, "Success", f"'{file_name}' added to cart!")
    
    def update_cart(self):
        """Update cart display"""
        total_price = sum(item["price"] for item in self.cart_items)
        self.cart_label.setText(f"Cart Items: {len(self.cart_items)}")
        self.cart_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #007BFF;")
        self.total_price_label.setText(f"Total: ₹{total_price:.2f}")
    
    def clear_cart(self):
        """Clear shopping cart"""
        if len(self.cart_items) == 0:
            QMessageBox.info(self, "Empty Cart", "Your cart is already empty!")
            return
        
        reply = QMessageBox.question(self, "Clear Cart", "Are you sure you want to clear your cart?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cart_items = []
            self.update_cart()
            self.populate_table()  # Refresh table
    
    def download_file(self, file_data):
        """Download a purchased file"""
        file_name = file_data.get('file_name', 'Unknown')
        file_category = file_data.get('category_name', 'Unknown')
        file_url = file_data.get('folder_location', '')

        # Category mapping restriction checks
        app_category = "Road"
        if str(file_category).lower() != app_category.lower():
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Category Mismatch")
            msg_box.setText(f"You are logged in the {app_category} Application. If you want to download the {file_category} file, "
                            f"then you should download the {file_category} Design application.")
            
            download_btn = msg_box.addButton(f"Download {file_category} Application", QMessageBox.ActionRole)
            msg_box.addButton("Cancel", QMessageBox.RejectRole)
            
            msg_box.exec_()
            
            if msg_box.clickedButton() == download_btn:
                from PyQt5.QtGui import QDesktopServices
                from PyQt5.QtCore import QUrl
                url = f"https://3dbharat.miscos.in/trial-info?category={file_category.lower()}"
                QDesktopServices.openUrl(QUrl(url))
            return

        if not file_url:
            QMessageBox.warning(self, "Error", "Download URL not found for this file.")
            return

        import os
        save_dir = os.path.join(r"D:\3D_Tool", file_category.lower())
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, file_name)

        from PyQt5.QtWidgets import QProgressDialog
        from PyQt5.QtCore import Qt

        self.progress_dialog = QProgressDialog(f"Downloading: {file_name}\nTo: {save_dir}", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle("Download in Progress")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumWidth(450)
        self.progress_dialog.setStyleSheet("""
            QProgressDialog {
                background-color: #ffffff;
            }
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                background-color: #ecf0f1;
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #5cb85c, stop:1 #4cae4c);
                border-radius: 7px;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 6px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)

        self.download_worker = DownloadWorker(file_url, save_path)
        self.download_worker.progress.connect(self.progress_dialog.setValue)
        self.download_worker.finished.connect(self._on_download_success)
        self.download_worker.error.connect(self._on_download_error)
        
        self.progress_dialog.canceled.connect(self.download_worker.cancel)
        self.download_worker.start()
        self.progress_dialog.show()

    def _on_download_success(self, save_path):
        QMessageBox.information(self, "Success", f"File downloaded successfully to:\n{save_path}")

    def _on_download_error(self, err_msg):
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.critical(self, "Download Failed", f"An error occurred while downloading:\n{err_msg}")
    
    def proceed_to_buy(self):
        """Proceed to purchase — opens the payment page in the default browser."""
        if len(self.cart_items) == 0:
            QMessageBox.warning(self, "Empty Cart", "Please add files to your cart before purchasing!")
            return

        # Collect the tfd_id for every cart item (fallback to file_id if tfd_id missing)
        file_ids = [str(item.get("tfd_id") or item.get("file_id", "")) for item in self.cart_items]
        file_ids = [fid for fid in file_ids if fid]  # drop empties

        if not file_ids:
            QMessageBox.warning(self, "Error", "Could not determine file IDs. Please try again.")
            return

        files_param = ",".join(file_ids)
        buy_url = f"https://3dbharat.com/edu-login/{self.euh_id}/{files_param}"

        print(f"DEBUG: proceed_to_buy URL = {buy_url}")

        # Show summary before opening browser
        total_price = sum(item["price"] for item in self.cart_items)
        items_list = "\n".join([f"  • {item['file_name']}" for item in self.cart_items])
        msg = (
            f"Purchase Summary:\n\n{items_list}\n\n"
            f"Total Amount: ₹{total_price:.2f}\n\n"
            f"Click 'Yes' to open the payment page in your browser."
        )
        reply = QMessageBox.question(self, "Confirm Purchase", msg, QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            from PyQt5.QtCore import QUrl
            from PyQt5.QtGui import QDesktopServices
            opened = QDesktopServices.openUrl(QUrl(buy_url))
            if not opened:
                QMessageBox.warning(
                    self, "Browser Error",
                    f"Could not open the browser automatically.\n\nPlease visit:\n{buy_url}"
                )


# ===========================================================================================================================
# ** ROAD ASSETS DIALOGS (SIDE WALL, FOOTPATH, DIVIDER) **
# ===========================================================================================================================

class RoadAssetBaseDialog(QDialog):
    def __init__(self, title, asset_name, asset_id, road_surface_data=None, project_id=None, is_edit_mode=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.asset_name = asset_name
        self.asset_id = asset_id
        self.road_surface_data = road_surface_data
        self.project_id = project_id
        self.is_edit_mode = is_edit_mode
        self.setModal(True)
        self.setMinimumWidth(450)
        
        self.verified_range = None
        
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f4ff, stop:1 #e6e6fa);
                border-radius: 12px;
            }
            QLabel { font-weight: bold; color: #333; }
            QLineEdit, QDoubleSpinBox {
                padding: 6px; border: 1px solid #ccc; border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 15px; border-radius: 6px; font-weight: bold;
                background-color: #007bff; color: white; border: none;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton#getLaneBtn { background-color: #28a745; }
            QPushButton#getLaneBtn:hover { background-color: #218838; }
            QComboBox {
                padding: 6px; border: 1px solid #ccc; border-radius: 4px;
                background-color: white;
            }
            QGroupBox {
                border: 1px solid #aaa; border-radius: 8px; margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
        """)

        self.layout_main = QVBoxLayout(self)
        self.layout_main.setSizeConstraint(QVBoxLayout.SetFixedSize)
        
        # --- Mode Selection (Edit vs Drop) ---
        self.mode_group = QWidget()
        mode_layout = QHBoxLayout(self.mode_group)
        mode_layout.setContentsMargins(0, 0, 0, 10)
        self.radio_edit = QRadioButton("Edit")
        self.radio_edit.setChecked(True)
        self.radio_edit.setStyleSheet("font-weight: bold; color: #333;")
        self.radio_drop = QRadioButton("Drop")
        self.radio_drop.setStyleSheet("font-weight: bold; color: #333;")
        mode_layout.addWidget(self.radio_edit)
        mode_layout.addWidget(self.radio_drop)
        mode_layout.addStretch()
        self.layout_main.addWidget(self.mode_group)
        
        self.radio_edit.toggled.connect(self._toggle_mode)
        self.radio_drop.toggled.connect(self._toggle_mode)
        
        if not self.is_edit_mode:
            self.mode_group.setVisible(False)
        
        # --- Chainage Group ---
        self.ch_group = QGroupBox("Chainage Configuration")
        ch_layout = QGridLayout(self.ch_group)
        
        ch_layout.addWidget(QLabel("From KM:"), 0, 0)
        self.from_km = QLineEdit()
        self.from_km.setPlaceholderText("e.g. 100")
        ch_layout.addWidget(self.from_km, 0, 1)
        
        ch_layout.addWidget(QLabel("From Chainage:"), 0, 2)
        self.from_ch = QLineEdit()
        self.from_ch.setPlaceholderText("e.g. 050")
        ch_layout.addWidget(self.from_ch, 0, 3)
        
        ch_layout.addWidget(QLabel("To KM:"), 1, 0)
        self.to_km = QLineEdit()
        self.to_km.setPlaceholderText("e.g. 101")
        ch_layout.addWidget(self.to_km, 1, 1)
        
        ch_layout.addWidget(QLabel("To Chainage:"), 1, 2)
        self.to_ch = QLineEdit()
        self.to_ch.setPlaceholderText("e.g. 150")
        ch_layout.addWidget(self.to_ch, 1, 3)
        
        # Auto-calculate length when chainage changes
        self.from_km.textChanged.connect(self._update_length)
        self.from_ch.textChanged.connect(self._update_length)
        self.to_km.textChanged.connect(self._update_length)
        self.to_ch.textChanged.connect(self._update_length)
        
        self.get_lane_btn = QPushButton("Get Lane")
        self.get_lane_btn.setObjectName("getLaneBtn")
        self.get_lane_btn.clicked.connect(self.fetch_lanes)
        ch_layout.addWidget(self.get_lane_btn, 2, 0, 1, 4)
        
        self.layout_main.addWidget(self.ch_group)
        
        # --- Lane Selection ---
        self.lane_container = QWidget()
        lane_layout = QHBoxLayout(self.lane_container)
        lane_layout.setContentsMargins(0, 0, 0, 0)
        self.lane_label = QLabel("Select Lane:")
        lane_layout.addWidget(self.lane_label)
        self.lane_combo = QComboBox()
        self.lane_combo.setMinimumWidth(200)
        lane_layout.addWidget(self.lane_combo)
        self.layout_main.addWidget(self.lane_container)
        
        # --- Dimensions Group ---
        self.dim_group = QGroupBox(f"{asset_name} Dimensions")
        dim_layout = QGridLayout(self.dim_group)
        
        dim_layout.addWidget(QLabel("Width (m):"), 0, 0)
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.0, 50.0)
        self.width_spin.setValue(0.5)
        dim_layout.addWidget(self.width_spin, 0, 1)
        
        dim_layout.addWidget(QLabel("Height (m):"), 1, 0)
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.0, 50.0)
        self.height_spin.setValue(1.0)
        dim_layout.addWidget(self.height_spin, 1, 1)
        
        dim_layout.addWidget(QLabel("Length (m):"), 2, 0)
        self.length_spin = QDoubleSpinBox()
        self.length_spin.setRange(0.0, 500000.0)
        self.length_spin.setValue(0.0)
        self.length_spin.setReadOnly(True)
        self.length_spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.length_spin.setStyleSheet("background-color: #e9ecef;")  # grey-out to show read-only
        dim_layout.addWidget(self.length_spin, 2, 1)
        
        self.asset_color = "#808080"
        dim_layout.addWidget(QLabel("Color:"), 3, 0)
        self.color_btn = QPushButton("Select Color")
        self.color_btn.setStyleSheet(f"background-color: {self.asset_color}; color: white; border: 1px solid #333;")
        self.color_btn.clicked.connect(self._choose_color)
        dim_layout.addWidget(self.color_btn, 3, 1)
        
        self.layout_main.addWidget(self.dim_group)
        
        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept_validation)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("background-color: #6c757d;")
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        self.layout_main.addLayout(btn_layout)

    def _toggle_mode(self):
        """Toggle UI elements based on Edit vs Drop mode selection."""
        is_drop = self.radio_drop.isChecked()
        
        if is_drop:
            # Change label text
            self.lane_label.setText(f"Select {self.asset_name}:")
            self.ch_group.setTitle("Chainage Configuration:-")
            
            # Reorder lane selection above chainage configuration
            idx_ch = self.layout_main.indexOf(self.ch_group)
            idx_lane = self.layout_main.indexOf(self.lane_container)
            if idx_lane > idx_ch:
                self.layout_main.removeWidget(self.lane_container)
                self.layout_main.insertWidget(idx_ch, self.lane_container)
                
            # Hide Get Lane button and dimensions in Drop mode
            self.get_lane_btn.setVisible(False)
            self.dim_group.setVisible(False)
            
            # Load available assets from reference_assets
            self._load_reference_assets()
            
        else:
            # Revert to standard Edit mode
            self.lane_label.setText("Select Lane:")
            self.ch_group.setTitle("Chainage Configuration")
            
            # Reorder lane selection back below chainage
            idx_ch = self.layout_main.indexOf(self.ch_group)
            idx_lane = self.layout_main.indexOf(self.lane_container)
            if idx_lane < idx_ch:
                self.layout_main.removeWidget(self.lane_container)
                # Re-insert at the original place below ch_group
                self.layout_main.insertWidget(self.layout_main.indexOf(self.ch_group) + 1, self.lane_container)
                
            # Show Get Lane button and dimensions again in Edit mode
            self.get_lane_btn.setVisible(True)
            self.dim_group.setVisible(True)
            
        self.adjustSize()

    def _load_reference_assets(self):
        """Load available reference assets (side walls, dividers, footpaths) for drop mode."""
        try:
            layer_folder = self._resolve_current_layer_folder()
            if not layer_folder:
                return
            
            from json_manager import DesignConstructionManager
            ref_assets = DesignConstructionManager.get_reference_asset(layer_folder, self.asset_id)
            
            # Clear existing items
            self.lane_combo.clear()
            
            if ref_assets and isinstance(ref_assets, dict):
                # ref_assets is dict like {"L1": {...}, "L2": {...}}
                for asset_name in sorted(ref_assets.keys()):
                    self.lane_combo.addItem(asset_name, asset_name)
            elif ref_assets and isinstance(ref_assets, list):
                # Handle case where it's a list
                for item in ref_assets:
                    if isinstance(item, dict):
                        asset_name = item.get('asset_name', 'Unknown')
                        self.lane_combo.addItem(asset_name, asset_name)
                    else:
                        self.lane_combo.addItem(str(item), str(item))
        except Exception as e:
            print(f"Error loading reference assets: {e}")

    def _update_length(self):
        """Auto-calculate length from chainage difference."""
        try:
            f_km = float(self.from_km.text().strip()) if self.from_km.text().strip() else 0.0
            f_ch = float(self.from_ch.text().strip()) if self.from_ch.text().strip() else 0.0
            t_km = float(self.to_km.text().strip()) if self.to_km.text().strip() else 0.0
            t_ch = float(self.to_ch.text().strip()) if self.to_ch.text().strip() else 0.0
            
            from_abs = f_km * 1000 + f_ch
            to_abs = t_km * 1000 + t_ch
            length = abs(to_abs - from_abs)
            self.length_spin.setValue(length)
        except (ValueError, TypeError):
            self.length_spin.setValue(0.0)

    def _resolve_current_layer_folder(self):
        """Resolve current layer folder from parent viewer context."""
        parent = self.parent()
        if not parent:
            return None

        base_dir = getattr(parent, 'WORKSHEETS_BASE_DIR', None)
        worksheet = getattr(parent, 'current_worksheet_name', None)
        subfolder = getattr(parent, 'current_subfolder_type', 'designs')
        layer = getattr(parent, 'current_layer_name', None)

        if not base_dir or not worksheet or not layer:
            return None

        return os.path.join(base_dir, worksheet, subfolder, layer)

    def _extract_lane_names_from_config(self, config):
        """Extract all lane/shoulder names from one lane configuration object."""
        names = []

        center_name = str(config.get('center_lane_name', '')).strip()
        center_width = float(config.get('center_lane_width', 0.0) or 0.0)
        if center_name and center_width > 0:
            names.append(center_name)

        n_left = int(config.get('lanes_left', 0) or 0)
        for i in range(1, n_left + 1):
            l_name = config.get(f"Left Lane {i} Name", config.get(f"Left Lane {i} name", f"Left Lane {i}"))
            l_width = float(config.get(f"Left Lane {i} Width", config.get(f"Left Lane {i} width", 0.0)) or 0.0)
            if str(l_name).strip() and l_width > 0:
                names.append(str(l_name).strip())

        n_right = int(config.get('lanes_right', 0) or 0)
        for i in range(1, n_right + 1):
            r_name = config.get(f"Right Lane {i} Name", config.get(f"Right Lane {i} name", f"Right Lane {i}"))
            r_width = float(config.get(f"Right Lane {i} Width", config.get(f"Right Lane {i} width", 0.0)) or 0.0)
            if str(r_name).strip() and r_width > 0:
                names.append(str(r_name).strip())

        if config.get('hard_shoulder_left', False):
            sh_l_name = str(config.get('Left Shoulder lane name', config.get('Left Shoulder lane Name', 'Left Shoulder'))).strip()
            sh_l_width = float(config.get('Left shoulder lane width', config.get('Left shoulder lane Width', 0.0)) or 0.0)
            if sh_l_name and sh_l_width > 0:
                names.append(sh_l_name)

        if config.get('hard_shoulder_right', False):
            sh_r_name = str(config.get('Right shoulder lane name', config.get('Right shoulder lane Name', 'Right Shoulder'))).strip()
            sh_r_width = float(config.get('Right shoulder lane width', config.get('Right shoulder lane Width', 0.0)) or 0.0)
            if sh_r_name and sh_r_width > 0:
                names.append(sh_r_name)

        return names

    def _load_lanes_from_local_json(self):
        """Load lane names from design_construction_config.json in current layer folder."""
        layer_folder = self._resolve_current_layer_folder()
        if not layer_folder:
            return None, "Current worksheet/layer context is missing."

        try:
            from json_manager import DesignConstructionManager
            lane_data = DesignConstructionManager.get_lane_marking(layer_folder)
        except Exception as e:
            return None, f"Failed to read design configuration: {str(e)}"
            
        if not lane_data:
            return None, "lane_marking configuration not found in current layer."

        configs = lane_data if isinstance(lane_data, list) else [lane_data]
        lane_names = []
        seen = set()
        for cfg in configs:
            if not isinstance(cfg, dict):
                continue
            for lane_name in self._extract_lane_names_from_config(cfg):
                key = lane_name.lower()
                if key not in seen:
                    seen.add(key)
                    lane_names.append(lane_name)

        return lane_names, None

    def fetch_lanes(self):
        f_km = self.from_km.text().strip()
        f_ch = self.from_ch.text().strip()
        t_km = self.to_km.text().strip()
        t_ch = self.to_ch.text().strip()
        
        if not all([f_km, f_ch, t_km, t_ch]):
            QMessageBox.warning(self, "Invalid Input", "Please fill all KM and Chainage fields.")
            return

        # Keep the same input behavior; just validate numbers and use local JSON as lane source.
        try:
            int(f_km)
            int(f_ch)
            int(t_km)
            int(t_ch)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "KM and Chainage must be valid integers.")
            return

        lane_names, err = self._load_lanes_from_local_json()
        if err:
            QMessageBox.critical(self, "Lane Data Error", err)
            return

        self.lane_combo.clear()
        if lane_names:
            for lane_name in lane_names:
                # Use lane name as local identifier (no server lane id in local mode).
                self.lane_combo.addItem(lane_name, lane_name)
            QMessageBox.information(self, "Success", f"Found {len(lane_names)} lanes from local lane_marking.json.")
        else:
            QMessageBox.warning(self, "No Lanes", "No lanes found in local lane_marking.json.")

    def _choose_color(self):
        color = QColorDialog.getColor(QColor(self.asset_color), self, "Select Asset Color")
        if color.isValid():
            self.asset_color = color.name()
            text_color = "black" if color.lightness() > 128 else "white"
            self.color_btn.setStyleSheet(f"background-color: {self.asset_color}; color: {text_color}; border: 1px solid #333;")

    def accept_validation(self):
        if self.lane_combo.currentIndex() == -1 or not self.lane_combo.currentText().strip():
            QMessageBox.warning(self, "Validation Error", f"Please select a {self.asset_name} lane first.")
            return
        
        # For drop mode, additional validation
        if self.radio_drop.isChecked():
            try:
                from_km = float(self.from_km.text().strip())
                from_ch = float(self.from_ch.text().strip())
                to_km = float(self.to_km.text().strip())
                to_ch = float(self.to_ch.text().strip())
                
                # Validate chainage ranges
                from_abs = from_km * 1000 + from_ch
                to_abs = to_km * 1000 + to_ch
                
                if from_abs >= to_abs:
                    QMessageBox.warning(self, "Validation Error", "From chainage must be less than To chainage.")
                    return
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Please enter valid numeric values for KM and Chainage.")
                return
        
        self.accept()

    def get_data(self):
        lane_name = self.lane_combo.currentText().strip()
        
        if not lane_name:
            raise ValueError("Lane name cannot be empty")
        
        data = {
            "asset_id": self.asset_id,
            "asset_name": self.asset_name,
            "lane_id": self.lane_combo.currentData(),
            "lane_name": lane_name,  # Use selected lane name as-is (e.g., "Left Side Wall", "Right Side Wall")
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "length": self.length_spin.value(),
            "from_km": self.from_km.text().strip(),
            "from_chainage": self.from_ch.text().strip(),
            "to_km": self.to_km.text().strip(),
            "to_chainage": self.to_ch.text().strip(),
            "color": self.asset_color,
            "is_drop_mode": self.radio_drop.isChecked() if hasattr(self, 'radio_drop') else False
        }
        return data

class SideWallDialog(RoadAssetBaseDialog):
    def __init__(self, road_surface_data=None, is_edit_mode=False, parent=None):
        super().__init__(
            "Side Wall Configuration",
            "Side Wall",
            "side_wall",
            road_surface_data=road_surface_data,
            is_edit_mode=is_edit_mode,
            parent=parent,
        )

class FootPathDialog(RoadAssetBaseDialog):
    def __init__(self, road_surface_data=None, is_edit_mode=False, parent=None):
        super().__init__(
            "Footpath Configuration",
            "Footpath",
            "footpath",
            road_surface_data=road_surface_data,
            is_edit_mode=is_edit_mode,
            parent=parent,
        )

class DividerDialog(RoadAssetBaseDialog):
    def __init__(self, road_surface_data=None, is_edit_mode=False, parent=None):
        super().__init__(
            "Divider Configuration",
            "Divider",
            "divider",
            road_surface_data=road_surface_data,
            is_edit_mode=is_edit_mode,
            parent=parent,
        )


# ===========================================================================================================================
# ** POLE ASSET DIALOG (Street Light & Signal Pole) **
# ===========================================================================================================================

class PoleAssetDialog(QDialog):
    """Dialog for placing street light / signal pole at intervals on a lane's road asset."""

    @staticmethod
    def _default_pole_config(pole_type):
        """Fallback config used when asset JSON files are not present."""
        base_cfg = {
            "pole": {
                "height": 12.0,
                "diameter": 0.12,
            },
            "cantilever": {
                "diameter": 0.07,
                "length": 2.0,
                "angle_from_vertical_deg": 90.0,
            },
        }

        if pole_type == "signal_pole":
            base_cfg["traffic_light"] = {
                "plate_height": 3.0,
                "plate_width": 0.5,
                "plate_thickness": 0.2,
                "light_radius": 0.15,
            }

        return base_cfg

    def __init__(self, title, pole_type, config_path, layer_folder, road_surface_data=None, project_id=None, is_edit_mode=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.pole_type = pole_type          # "street_light" or "signal_pole"
        self.config_path = config_path      # path to street_light.json or signal_pole.json
        self.layer_folder = layer_folder    # current design layer folder
        self.road_surface_data = road_surface_data
        self.project_id = project_id
        self.is_edit_mode = is_edit_mode
        self.setModal(True)
        self.setMinimumWidth(520)

        self.pole_config = {}
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.pole_config = json.load(f)
            except Exception as e:
                print(f"Error loading pole config: {e}")

        if not isinstance(self.pole_config, dict) or not self.pole_config:
            self.pole_config = self._default_pole_config(self.pole_type)

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f4ff, stop:1 #e6e6fa);
                border-radius: 12px;
            }
            QLabel { font-weight: bold; color: #333; }
            QLineEdit, QDoubleSpinBox, QSpinBox {
                padding: 6px; border: 1px solid #ccc; border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 15px; border-radius: 6px; font-weight: bold;
                background-color: #007bff; color: white; border: none;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton#getLaneBtn { background-color: #28a745; }
            QPushButton#getLaneBtn:hover { background-color: #218838; }
            QComboBox {
                padding: 6px; border: 1px solid #ccc; border-radius: 4px;
                background-color: white;
            }
            QGroupBox {
                border: 1px solid #aaa; border-radius: 8px; margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
        """)

        layout = QVBoxLayout(self)
        
        # ── Mode Selection (Edit vs Drop) - Always create, visibility controlled by is_edit_mode ──
        self.mode_group = QWidget()
        mode_layout = QHBoxLayout(self.mode_group)
        mode_layout.setContentsMargins(0, 0, 0, 10)
        
        self.radio_edit = QRadioButton("Edit")
        self.radio_edit.setChecked(True)
        self.radio_edit.setStyleSheet("font-weight: bold; color: #333;")
        self.radio_drop = QRadioButton("Drop")
        self.radio_drop.setStyleSheet("font-weight: bold; color: #333;")
        
        mode_layout.addWidget(self.radio_edit)
        mode_layout.addWidget(self.radio_drop)
        mode_layout.addStretch()
        layout.addWidget(self.mode_group)
        
        self.radio_edit.toggled.connect(self._toggle_mode)
        self.radio_drop.toggled.connect(self._toggle_mode)
        
        if not is_edit_mode:
            self.mode_group.setVisible(False)

        # ── Chainage Group ──
        self.ch_group = QGroupBox("Chainage Configuration")
        ch_layout = QGridLayout(self.ch_group)

        self.chainage_mode = "multiple"

        self.single_chainage_checkbox = QCheckBox("One Chainage")
        self.multiple_chainage_checkbox = QCheckBox("Multiple Chainage")
        self.multiple_chainage_checkbox.setChecked(True)

        self.single_chainage_checkbox.toggled.connect(self._on_single_chainage_toggled)
        self.multiple_chainage_checkbox.toggled.connect(self._on_multiple_chainage_toggled)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.single_chainage_checkbox)
        mode_layout.addWidget(self.multiple_chainage_checkbox)
        mode_layout.addStretch()
        ch_layout.addLayout(mode_layout, 0, 0, 1, 4)

        self.single_km_label = QLabel("KM:")
        self.single_km = QLineEdit()
        self.single_km.setPlaceholderText("e.g. 100")
        ch_layout.addWidget(self.single_km_label, 1, 0)
        ch_layout.addWidget(self.single_km, 1, 1)

        self.single_ch_label = QLabel("Chainage:")
        self.single_ch = QLineEdit()
        self.single_ch.setPlaceholderText("e.g. 0")
        ch_layout.addWidget(self.single_ch_label, 1, 2)
        ch_layout.addWidget(self.single_ch, 1, 3)

        self.from_km_label = QLabel("From KM:")
        self.from_km = QLineEdit()
        self.from_km.setPlaceholderText("e.g. 100")
        ch_layout.addWidget(self.from_km_label, 2, 0)
        ch_layout.addWidget(self.from_km, 2, 1)

        self.from_ch_label = QLabel("From Chainage:")
        self.from_ch = QLineEdit()
        self.from_ch.setPlaceholderText("e.g. 0")
        ch_layout.addWidget(self.from_ch_label, 2, 2)
        ch_layout.addWidget(self.from_ch, 2, 3)

        self.to_km_label = QLabel("To KM:")
        self.to_km = QLineEdit()
        self.to_km.setPlaceholderText("e.g. 100")
        ch_layout.addWidget(self.to_km_label, 3, 0)
        ch_layout.addWidget(self.to_km, 3, 1)

        self.to_ch_label = QLabel("To Chainage:")
        self.to_ch = QLineEdit()
        self.to_ch.setPlaceholderText("e.g. 120")
        ch_layout.addWidget(self.to_ch_label, 3, 2)
        ch_layout.addWidget(self.to_ch, 3, 3)

        self.interval_label = QLabel("Chainage Interval (m):")
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(1.0, 5000.0)
        self.interval_spin.setValue(20.0)
        self.interval_spin.setSuffix(" m")
        ch_layout.addWidget(self.interval_label, 4, 0, 1, 2)
        ch_layout.addWidget(self.interval_spin, 4, 2, 1, 2)

        self.get_lane_btn = QPushButton("Get Lanes")
        self.get_lane_btn.setObjectName("getLaneBtn")
        self.get_lane_btn.clicked.connect(self.fetch_lanes)
        ch_layout.addWidget(self.get_lane_btn, 5, 0, 1, 4)

        layout.addWidget(self.ch_group)

        # ── Lane & Reference Asset ──
        self.sel_group = QGroupBox("Lane & Asset Selection")
        sel_layout = QGridLayout(self.sel_group)

        sel_layout.addWidget(QLabel("Select Lane:"), 0, 0)
        self.lane_combo = QComboBox()
        self.lane_combo.setMinimumWidth(200)
        sel_layout.addWidget(self.lane_combo, 0, 1)

        sel_layout.addWidget(QLabel("Reference Asset:"), 1, 0)
        self.ref_asset_combo = QComboBox()
        self.ref_asset_combo.setMinimumWidth(200)
        self._populate_ref_assets()
        sel_layout.addWidget(self.ref_asset_combo, 1, 1)

        layout.addWidget(self.sel_group)

        # ── Pole Parameters (from config JSON) ──
        self.param_group = QGroupBox(f"{title} Parameters")
        param_layout = QGridLayout(self.param_group)
        self.param_edits = {}
        row = 0
        self._add_params_recursive(param_layout, self.pole_config, prefix="", row_ref=[row])
        layout.addWidget(self.param_group)

        # ── Colors ──
        self.pole_color = "#808080"
        self.cantilever_color = "#808080"
        
        self.color_group = QGroupBox("Colors")
        color_layout = QGridLayout(self.color_group)
        
        color_layout.addWidget(QLabel("Pole Color:"), 0, 0)
        self.pole_color_btn = QPushButton("Select Color")
        self.pole_color_btn.setStyleSheet(f"background-color: {self.pole_color}; color: white; border: 1px solid #333;")
        self.pole_color_btn.clicked.connect(self._choose_pole_color)
        color_layout.addWidget(self.pole_color_btn, 0, 1)

        color_layout.addWidget(QLabel("Cantilever Color:"), 1, 0)
        self.cant_color_btn = QPushButton("Select Color")
        self.cant_color_btn.setStyleSheet(f"background-color: {self.cantilever_color}; color: white; border: 1px solid #333;")
        self.cant_color_btn.clicked.connect(self._choose_cant_color)
        color_layout.addWidget(self.cant_color_btn, 1, 1)

        layout.addWidget(self.color_group)

        # ── Buttons ──
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self._accept_validation)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("background-color: #6c757d;")
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self._set_chainage_mode(False)

    def _set_chainage_mode(self, single_mode):
        self.chainage_mode = "single" if single_mode else "multiple"

        self.single_km_label.setVisible(single_mode)
        self.single_km.setVisible(single_mode)
        self.single_ch_label.setVisible(single_mode)
        self.single_ch.setVisible(single_mode)

        self.from_km_label.setVisible(not single_mode)
        self.from_km.setVisible(not single_mode)
        self.from_ch_label.setVisible(not single_mode)
        self.from_ch.setVisible(not single_mode)
        self.to_km_label.setVisible(not single_mode)
        self.to_km.setVisible(not single_mode)
        self.to_ch_label.setVisible(not single_mode)
        self.to_ch.setVisible(not single_mode)
        self.interval_label.setVisible(not single_mode)
        self.interval_spin.setVisible(not single_mode)

    def _on_single_chainage_toggled(self, checked):
        if checked:
            if self.multiple_chainage_checkbox.isChecked():
                self.multiple_chainage_checkbox.blockSignals(True)
                self.multiple_chainage_checkbox.setChecked(False)
                self.multiple_chainage_checkbox.blockSignals(False)
            self._set_chainage_mode(True)
        elif not self.multiple_chainage_checkbox.isChecked():
            self.multiple_chainage_checkbox.blockSignals(True)
            self.multiple_chainage_checkbox.setChecked(True)
            self.multiple_chainage_checkbox.blockSignals(False)
            self._set_chainage_mode(False)

    def _on_multiple_chainage_toggled(self, checked):
        if checked:
            if self.single_chainage_checkbox.isChecked():
                self.single_chainage_checkbox.blockSignals(True)
                self.single_chainage_checkbox.setChecked(False)
                self.single_chainage_checkbox.blockSignals(False)
            self._set_chainage_mode(False)
        elif not self.single_chainage_checkbox.isChecked():
            self.single_chainage_checkbox.blockSignals(True)
            self.single_chainage_checkbox.setChecked(True)
            self.single_chainage_checkbox.blockSignals(False)
            self._set_chainage_mode(True)

    def _parse_chainage_number(self, text, field_name):
        text = str(text).strip()
        if text == "":
            raise ValueError(f"Please enter {field_name}.")
        try:
            return float(text)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid number.") from exc

    def _collect_chainage_data(self):
        if self.chainage_mode == "single":
            km_text = self.single_km.text().strip()
            ch_text = self.single_ch.text().strip()
            if not km_text or not ch_text:
                return None, "Please enter KM and Chainage for one-chainage mode."

            try:
                km = self._parse_chainage_number(km_text, "KM")
                chainage = self._parse_chainage_number(ch_text, "Chainage")
            except ValueError as exc:
                return None, str(exc)

            abs_chainage = km * 1000.0 + chainage
            return {
                "chainage_mode": "single",
                "from_km": km_text,
                "from_chainage": ch_text,
                "to_km": km_text,
                "to_chainage": ch_text,
                "chainage_interval": 0.0,
                "total_length": 0.0,
                "pole_positions_abs": [abs_chainage],
                "num_poles": 1,
            }, None

        f_km = self.from_km.text().strip()
        f_ch = self.from_ch.text().strip()
        t_km = self.to_km.text().strip()
        t_ch = self.to_ch.text().strip()

        if not all([f_km, f_ch, t_km, t_ch]):
            return None, "Please fill all KM and Chainage fields."

        try:
            from_km = self._parse_chainage_number(f_km, "From KM")
            from_ch = self._parse_chainage_number(f_ch, "From Chainage")
            to_km = self._parse_chainage_number(t_km, "To KM")
            to_ch = self._parse_chainage_number(t_ch, "To Chainage")
        except ValueError as exc:
            return None, str(exc)

        from_abs = from_km * 1000.0 + from_ch
        to_abs = to_km * 1000.0 + to_ch
        interval = float(self.interval_spin.value())
        total_length = abs(to_abs - from_abs)

        pole_positions = []
        if total_length == 0:
            pole_positions = [from_abs]
        elif interval > 0:
            direction = 1.0 if to_abs >= from_abs else -1.0
            num_poles = int(total_length / interval) + 1
            for i in range(num_poles):
                ch = from_abs + direction * i * interval
                if direction > 0:
                    if ch <= to_abs + 0.01:
                        pole_positions.append(ch)
                else:
                    if ch >= to_abs - 0.01:
                        pole_positions.append(ch)

            if not pole_positions:
                pole_positions = [from_abs]

        return {
            "chainage_mode": "multiple",
            "from_km": f_km,
            "from_chainage": f_ch,
            "to_km": t_km,
            "to_chainage": t_ch,
            "chainage_interval": interval,
            "total_length": total_length,
            "pole_positions_abs": pole_positions,
            "num_poles": len(pole_positions),
        }, None

    def _add_params_recursive(self, grid, data, prefix, row_ref):
        """Recursively add config parameters as labeled input fields."""
        for key, value in data.items():
            if key == "type":
                continue
            if isinstance(value, dict):
                label = QLabel(f"── {key.replace('_', ' ').title()} ──")
                label.setStyleSheet("color: #007bff; font-size: 13px;")
                grid.addWidget(label, row_ref[0], 0, 1, 2)
                row_ref[0] += 1
                self._add_params_recursive(grid, value, prefix=f"{prefix}{key}.", row_ref=row_ref)
            elif isinstance(value, list):
                full_key = f"{prefix}{key}"
                grid.addWidget(QLabel(f"{key.replace('_', ' ').title()}:"), row_ref[0], 0)
                le = QLineEdit(", ".join(str(v) for v in value))
                le.setReadOnly(True)
                le.setStyleSheet("background-color: #e9ecef;")
                grid.addWidget(le, row_ref[0], 1)
                self.param_edits[full_key] = le
                row_ref[0] += 1
            else:
                full_key = f"{prefix}{key}"
                grid.addWidget(QLabel(f"{key.replace('_', ' ').title()}:"), row_ref[0], 0)
                spin = QDoubleSpinBox()
                spin.setRange(0.0, 10000.0)
                spin.setDecimals(3)
                spin.setValue(float(value))
                grid.addWidget(spin, row_ref[0], 1)
                self.param_edits[full_key] = spin
                row_ref[0] += 1

    def _populate_ref_assets(self):
        """Scan unified master configuration for road assets (footpath, side_wall, divider)."""
        self.ref_asset_combo.clear()
        found = False
        if self.layer_folder and os.path.isdir(self.layer_folder):
            try:
                from json_manager import DesignConstructionManager
                ref_assets = DesignConstructionManager.get_all_reference_assets(self.layer_folder)
                
                for asset_key, data in ref_assets.items():
                    if data:
                        asset_name = data.get("lane_name") or data.get("asset_name") or asset_key.replace('_', ' ').title()
                        self.ref_asset_combo.addItem(asset_name, asset_key)
                        found = True
            except Exception as e:
                print(f"Error loading reference assets for poles: {e}")

        if not found:
            self.ref_asset_combo.addItem("(No road assets found)", "")

    def _extract_lane_names_from_config(self, config):
        """Extract all lane/shoulder names from one lane configuration object."""
        names = []

        center_name = str(config.get('center_lane_name', '')).strip()
        center_width = float(config.get('center_lane_width', 0.0) or 0.0)
        if center_name and center_width > 0:
            names.append(center_name)

        n_left = int(config.get('lanes_left', 0) or 0)
        for i in range(1, n_left + 1):
            l_name = config.get(f"Left Lane {i} Name", config.get(f"Left Lane {i} name", f"Left Lane {i}"))
            l_width = float(config.get(f"Left Lane {i} Width", config.get(f"Left Lane {i} width", 0.0)) or 0.0)
            if str(l_name).strip() and l_width > 0:
                names.append(str(l_name).strip())

        n_right = int(config.get('lanes_right', 0) or 0)
        for i in range(1, n_right + 1):
            r_name = config.get(f"Right Lane {i} Name", config.get(f"Right Lane {i} name", f"Right Lane {i}"))
            r_width = float(config.get(f"Right Lane {i} Width", config.get(f"Right Lane {i} width", 0.0)) or 0.0)
            if str(r_name).strip() and r_width > 0:
                names.append(str(r_name).strip())

        if config.get('hard_shoulder_left', False):
            sh_l_name = str(config.get('Left Shoulder lane name', config.get('Left Shoulder lane Name', 'Left Shoulder'))).strip()
            sh_l_width = float(config.get('Left shoulder lane width', config.get('Left shoulder lane Width', 0.0)) or 0.0)
            if sh_l_name and sh_l_width > 0:
                names.append(sh_l_name)

        if config.get('hard_shoulder_right', False):
            sh_r_name = str(config.get('Right shoulder lane name', config.get('Right shoulder lane Name', 'Right Shoulder'))).strip()
            sh_r_width = float(config.get('Right shoulder lane width', config.get('Right shoulder lane Width', 0.0)) or 0.0)
            if sh_r_name and sh_r_width > 0:
                names.append(sh_r_name)

        return names

    def _load_lanes_from_local_json(self):
        """Load lane names from design_construction_config.json in current layer folder."""
        if not self.layer_folder:
            return None, "Current layer folder is not available."

        try:
            from json_manager import DesignConstructionManager
            lane_data = DesignConstructionManager.get_lane_marking(self.layer_folder)
        except Exception as e:
            return None, f"Failed to read design configuration: {str(e)}"
            
        if not lane_data:
            return None, "lane_marking configuration not found in current layer."

        configs = lane_data if isinstance(lane_data, list) else [lane_data]
        lane_names = []
        seen = set()
        for cfg in configs:
            if not isinstance(cfg, dict):
                continue
            for lane_name in self._extract_lane_names_from_config(cfg):
                key = lane_name.lower()
                if key not in seen:
                    seen.add(key)
                    lane_names.append(lane_name)

        return lane_names, None

    def fetch_lanes(self):
        _, err = self._collect_chainage_data()
        if err:
            QMessageBox.warning(self, "Invalid Input", err)
            return

        lane_names, err = self._load_lanes_from_local_json()
        if err:
            QMessageBox.critical(self, "Lane Data Error", err)
            return

        self.lane_combo.clear()
        if lane_names:
            for lane_name in lane_names:
                # Use lane name as local ID in offline mode.
                self.lane_combo.addItem(lane_name, lane_name)
            QMessageBox.information(self, "Success", f"Found {len(lane_names)} lanes from local lane_marking.json.")
        else:
            QMessageBox.warning(self, "No Lanes", "No lanes found in local lane_marking.json.")

    def _choose_pole_color(self):
        color = QColorDialog.getColor(QColor(self.pole_color), self, "Select Pole Color")
        if color.isValid():
            self.pole_color = color.name()
            text_color = "black" if color.lightness() > 128 else "white"
            self.pole_color_btn.setStyleSheet(f"background-color: {self.pole_color}; color: {text_color}; border: 1px solid #333;")

    def _toggle_mode(self):
        """Toggle UI elements based on Edit vs Drop mode selection."""
        is_drop = self.radio_drop.isChecked()
        
        if is_drop:
            # In drop mode, show chainage configuration for trimming
            self.ch_group.setTitle("Chainage Configuration (Drop Range)")
            self.param_group.setVisible(False)
            self.color_group.setVisible(False)
            self.ok_btn.setText("Drop")
            self.ok_btn.setStyleSheet("background-color: #dc3545; color: white;")
        else:
            # In edit mode, show normal chainage configuration
            self.ch_group.setTitle("Chainage Configuration")
            self.param_group.setVisible(True)
            self.color_group.setVisible(True)
            self.ok_btn.setText("OK")
            self.ok_btn.setStyleSheet("background-color: #007bff; color: white;")

    def _choose_cant_color(self):
        color = QColorDialog.getColor(QColor(self.cantilever_color), self, "Select Cantilever Color")
        if color.isValid():
            self.cantilever_color = color.name()
            text_color = "black" if color.lightness() > 128 else "white"
            self.cant_color_btn.setStyleSheet(f"background-color: {self.cantilever_color}; color: {text_color}; border: 1px solid #333;")

    def _accept_validation(self):
        _, err = self._collect_chainage_data()
        if err:
            QMessageBox.warning(self, "Validation", err)
            return
        if self.lane_combo.currentIndex() == -1 or not self.lane_combo.currentData():
            QMessageBox.warning(self, "Validation", "Please select a lane first.")
            return
        ref_path = self.ref_asset_combo.currentData()
        if not ref_path or ref_path == "":
            QMessageBox.warning(self, "Validation", "No reference road asset found. Create a Footpath/Side Wall/Divider first.")
            return
        self.accept()

    def get_data(self):
        """Return all dialog data for pole creation."""
        chainage_data, err = self._collect_chainage_data()
        if err:
            return {}

        pole_positions = chainage_data.get("pole_positions_abs", [])
        interval = chainage_data.get("chainage_interval", self.interval_spin.value())
        total_length = chainage_data.get("total_length", 0.0)

        # Read current parameter values
        params = {}
        for key, widget in self.param_edits.items():
            if isinstance(widget, QDoubleSpinBox):
                params[key] = widget.value()
            elif isinstance(widget, QLineEdit):
                params[key] = widget.text()

        # Load reference asset data
        ref_asset_data = {}
        ref_path = self.ref_asset_combo.currentData()
        if ref_path and os.path.exists(ref_path):
            try:
                with open(ref_path, 'r', encoding='utf-8') as f:
                    ref_asset_data = json.load(f)
            except:
                pass

        return {
            "pole_type": self.pole_type,
            "chainage_mode": chainage_data.get("chainage_mode", "multiple"),
            "from_km": chainage_data.get("from_km", self.from_km.text().strip()),
            "from_chainage": chainage_data.get("from_chainage", self.from_ch.text().strip()),
            "to_km": chainage_data.get("to_km", self.to_km.text().strip()),
            "to_chainage": chainage_data.get("to_chainage", self.to_ch.text().strip()),
            "chainage_interval": interval,
            "total_length": total_length,
            "lane_id": self.lane_combo.currentData(),
            "lane_name": self.lane_combo.currentText(),
            "ref_asset_name": self.ref_asset_combo.currentText(),
            "ref_asset_file": ref_path,
            "ref_asset_data": ref_asset_data,
            "pole_config": params,
            "pole_positions_abs": pole_positions,
            "num_poles": len(pole_positions),
            "pole_color": self.pole_color,
            "cantilever_color": self.cantilever_color,
            "is_drop_mode": self.radio_drop.isChecked() if hasattr(self, 'radio_drop') else False
        }
# ===========================================================================================================================
# ** FEEDBACK DIALOG **
# ===========================================================================================================================
class FeedbackDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Feedback")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #e3f2fd, stop:1 #bbdefb);
                border-radius: 15px;
            }
            QLabel {
                color: #0d47a1;
                font-weight: bold;
                font-size: 14px;
            }
            QTextEdit {
                border: 2px solid #2196f3;
                border-radius: 10px;
                padding: 10px;
                background-color: white;
                font-size: 13px;
                color: #333;
            }
            QPushButton {
                border-radius: 20px;
                padding: 10px;
                font-weight: bold;
                min-width: 120px;
                font-size: 14px;
            }
            QPushButton#sendBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #2196f3, stop:1 #1976d2);
                color: white;
                border: none;
            }
            QPushButton#sendBtn:hover {
                background: #1976d2;
            }
            QPushButton#cancelBtn {
                background: #e0e0e0;
                color: #424242;
                border: none;
            }
            QPushButton#cancelBtn:hover {
                background: #bdbdbd;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("Please provide your feedback / input:"))
        
        self.feedback_text = QTextEdit()
        self.feedback_text.setPlaceholderText("Enter your feedback here...")
        layout.addWidget(self.feedback_text)

        btn_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.send_btn)
        layout.addLayout(btn_layout)


# ===========================================================================================================================
# ** IMAGE VIEWER DIALOG **
# ===========================================================================================================================
class ZoomPanGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        from PyQt5.QtGui import QPainter
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.setFrameShape(QFrame.NoFrame)
        self._zoom = 0
    
    def setPixmap(self, pixmap):
        if not pixmap or pixmap.isNull():
            return
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self._zoom = 0
        
    def wheelEvent(self, event):
        if self.pixmap_item.pixmap().isNull():
            return
        
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
            self._zoom += 1
        else:
            # Allow zooming out to a point, but mostly normal Qt scrolling
            self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)
            self._zoom -= 1

class ImageViewerDialog(QDialog):
    """Full-screen image viewer dialog with maximize and full-screen options"""

    def __init__(self, image_path, file_name=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"View Image - {file_name if file_name else 'System Design'}")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)

        self.image_path = image_path
        self.file_name = file_name
        self.is_fullscreen = False
        self.original_geometry = None

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1a1a1a, stop:1 #2a2a2a);
            }
            QLabel {
                background: transparent;
                color: white;
            }
            QPushButton {
                background: #9C27B0;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 80px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #7B1FA2;
            }
            QPushButton:pressed {
                background: #6A1B9A;
            }
        """)

        self.setup_ui(image_path)

    def setup_ui(self, image_path):
        """Setup image viewer UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Image viewer with zoom and pan
        self.image_view = ZoomPanGraphicsView(self)
        self.image_view.setStyleSheet("""
            QGraphicsView {
                background-color: #000;
                border: 2px solid #9C27B0;
                border-radius: 8px;
            }
        """)

        if os.path.exists(image_path):
            self.pixmap = QPixmap(image_path)
            if not self.pixmap.isNull():
                self.image_view.setPixmap(self.pixmap)
            else:
                # Fallback label for error inside a layout or just blank
                pass
        else:
            pass

        main_layout.addWidget(self.image_view, 1)

        # Bottom buttons layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.maximize_btn = QPushButton("Maximize")
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        btn_layout.addWidget(self.maximize_btn)

        self.fullscreen_btn = QPushButton("Full Screen")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        btn_layout.addWidget(self.fullscreen_btn)

        btn_layout.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        main_layout.addLayout(btn_layout)

    def update_image_display(self):
        """Update image display based on current window size"""
        if hasattr(self, 'image_view') and hasattr(self, 'pixmap') and not self.pixmap.isNull():
            if self.image_view._zoom == 0:
                self.image_view.fitInView(self.image_view.scene.sceneRect(), Qt.KeepAspectRatio)

    def toggle_maximize(self):
        """Toggle between normal and maximized window"""
        if self.isMaximized():
            self.showNormal()
            if hasattr(self, 'maximize_btn'):
                self.maximize_btn.setText("Maximize")
        else:
            self.showMaximized()
            if hasattr(self, 'maximize_btn'):
                self.maximize_btn.setText("Restore")

    def toggle_fullscreen(self):
        """Toggle full-screen mode"""
        if self.is_fullscreen:
            # Exit full-screen
            self.is_fullscreen = False
            self.showNormal()
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
            self.show()
            if hasattr(self, 'fullscreen_btn'):
                self.fullscreen_btn.setText("Full Screen")
        else:
            # Enter full-screen
            self.is_fullscreen = True
            self.original_geometry = self.geometry()
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
            self.showFullScreen()
            if hasattr(self, 'fullscreen_btn'):
                self.fullscreen_btn.setText("Exit Full Screen")

    def resizeEvent(self, event):
        """Update image when window is resized"""
        super().resizeEvent(event)
        self.update_image_display()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape:
            if self.is_fullscreen:
                self.toggle_fullscreen()
            else:
                self.accept()
        else:
            super().keyPressEvent(event)


# ===========================================================================================================================
# ** VIEW SYSTEM DESIGN DIALOG **
# ===========================================================================================================================
class ViewSystemDesignDialog(QDialog):
    """Dialog to browse and load 3D system designs from road directory"""

    def __init__(self, user_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("View System Design")
        self.setModal(True)
        self.setMinimumWidth(900)
        self.setMinimumHeight(500)
        self.user_id = user_id
        self.selected_file_name = None
        self.selected_item_widget = None

        # Base paths
        self.ROAD_FILES_DIR = r"C:\3D_Tool\road"
        self.USER_BASE_DIR = r"C:\3D_Tool\user"

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #e6e6fa, stop:1 #e6e6fa);
                border-radius: 20px;
            }
            QLabel {
                color: black;
                font-weight: 500;
            }
            QGroupBox {
                border: 2px solid #7B1FA2;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 10px;
                font-weight: bold;
                color: #4A148C;
                background-color: rgba(255,255,255,0.3);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 3px 8px;
                font-size: 12px;
            }
            QScrollArea {
                border: 1px solid #9C27B0;
                border-radius: 8px;
                background-color: white;
            }
            QPushButton {
                border-radius: 20px;
                padding: 10px;
                font-weight: bold;
                min-width: 100px;
                border: none;
            }
            QPushButton#viewBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #9C27B0, stop:1 #6A1B9A);
                color: white;
            }
            QPushButton#viewBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #AB47BC, stop:1 #4A148C);
            }
            QPushButton#viewBtn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #6A1B9A, stop:1 #4A148C);
                padding: 12px 10px 8px 10px;
            }
            QPushButton#cancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333333;
            }
            QPushButton#cancelBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #D1C4E9, stop:1 #BA68C8);
            }
        """)

        self.setup_ui()
        self.load_system_designs()

    def setup_ui(self):
        """Setup the dialog UI - WITHOUT preview section"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Available System Designs")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Main content area
        content_group = QGroupBox("Select Design")
        content_layout = QVBoxLayout(content_group)

        # Scroll area for design items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.designs_container = QWidget()
        self.designs_layout = QVBoxLayout(self.designs_container)
        self.designs_layout.setSpacing(10)

        scroll_area.setWidget(self.designs_container)
        content_layout.addWidget(scroll_area)

        layout.addWidget(content_group, 1)

        # Buttons layout
        btn_layout = QHBoxLayout()

        self.view_btn = QPushButton("View")
        self.view_btn.setObjectName("viewBtn")
        self.view_btn.clicked.connect(self.on_view_clicked)
        self.view_btn.setEnabled(False)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.view_btn)
        layout.addLayout(btn_layout)

    def load_system_designs(self):
        """Load all .ply files from road directory and display them"""
        try:
            if not os.path.exists(self.ROAD_FILES_DIR):
                QMessageBox.warning(self, "Error", f"Road files directory not found: {self.ROAD_FILES_DIR}")
                return

            # Get all .ply files
            ply_files = glob.glob(os.path.join(self.ROAD_FILES_DIR, "*.ply"))
            ply_files.sort()

            if not ply_files:
                QMessageBox.information(self, "No Designs", "No .ply files found in the road directory.")
                return

            # Create design items
            for ply_file in ply_files:
                file_name = os.path.splitext(os.path.basename(ply_file))[0]
                png_file = os.path.join(self.ROAD_FILES_DIR, f"{file_name}.png")

                # Create design item (file name + thumbnail + select button)
                item_widget = self.create_design_item(file_name, png_file)
                self.designs_layout.addWidget(item_widget)

            self.designs_layout.addStretch()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load system designs: {str(e)}")

    def create_design_item(self, file_name, png_file):
        """Create a design item widget with file name and thumbnail - clickable to select"""
        item_widget = QFrame()
        item_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #d0d0d0;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                background-color: #f5f5f5;
                border: 2px solid #9C27B0;
            }
        """)
        item_widget.setCursor(Qt.PointingHandCursor)

        item_layout = QHBoxLayout(item_widget)
        item_layout.setSpacing(15)

        # Thumbnail
        thumbnail_label = QLabel()
        thumbnail_label.setFixedSize(120, 120)
        thumbnail_label.setAlignment(Qt.AlignCenter)
        thumbnail_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd; border-radius: 4px;")

        if os.path.exists(png_file):
            pixmap = QPixmap(png_file)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaledToWidth(100, Qt.SmoothTransformation)
                thumbnail_label.setPixmap(scaled_pixmap)
            thumbnail_label.setCursor(Qt.PointingHandCursor)
            # Open image viewer window when thumbnail clicked
            thumbnail_label.mousePressEvent = lambda e: self.open_image_viewer(png_file, file_name)
        else:
            thumbnail_label.setText("No Image")
            thumbnail_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd; color: #999;")

        item_layout.addWidget(thumbnail_label)

        # File name (clickable to select)
        right_layout = QVBoxLayout()

        name_label = QLabel(file_name)
        name_font = name_label.font()
        name_font.setPointSize(11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
        name_label.setCursor(Qt.PointingHandCursor)
        right_layout.addWidget(name_label)

        right_layout.addStretch()

        item_layout.addLayout(right_layout, 1)

        # Store reference for styling
        item_widget.design_name = file_name
        item_widget.png_file = png_file
        item_widget.name_label = name_label

        # Make item clickable by connecting mouse press event
        def on_item_clicked(event):
            self.on_design_selected(file_name, png_file, item_widget)

        item_widget.mousePressEvent = on_item_clicked

        return item_widget

    def open_image_viewer(self, png_file, file_name):
        """Open a separate dialog to view the full image"""
        if os.path.exists(png_file):
            viewer_dialog = ImageViewerDialog(png_file, file_name, parent=self)
            viewer_dialog.exec_()

    def on_design_selected(self, file_name, png_file, item_widget):
        """Handle design selection - update styling and enable View button"""
        # Remove previous selection styling
        if self.selected_item_widget:
            self.selected_item_widget.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 2px solid #d0d0d0;
                    border-radius: 8px;
                    padding: 10px;
                }
                QFrame:hover {
                    background-color: #f5f5f5;
                    border: 2px solid #9C27B0;
                }
            """)

        # Apply selection styling to clicked item
        item_widget.setStyleSheet("""
            QFrame {
                background-color: #F3E5F5;
                border: 3px solid #9C27B0;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        # Update selected file
        self.selected_file_name = file_name
        self.selected_item_widget = item_widget

        # Enable View button
        self.view_btn.setEnabled(True)

    def on_view_clicked(self):
        """Handle View button click - create folder structure and copy files, then directly open design layer"""
        if not self.selected_file_name:
            QMessageBox.warning(self, "Error", "Please select a design first.")
            return

        try:
            # Create folder structure and copy files
            if self.create_worksheet_structure(self.selected_file_name):
                # Store the selected design info for opening - then accept without message
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to create worksheet structure.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def create_worksheet_structure(self, file_name):
        r"""
        Create the worksheet folder structure and copy files
        Structure:
        C:\3D_Tool\user\{user_id}\road\{file_name}_worksheet\
            ├── designs\{file_name}_design_layer\
            │   ├── design_construction_config.json
            │   └── design_layer_config.txt
            └── construction\{file_name}_material_layer\
                ├── material_construction_config.json
                └── Construction_Layer_config.txt
        """
        try:
            if not self.user_id:
                QMessageBox.warning(self, "Error", "User ID not available.")
                return False

            # Create base worksheet directory under default application bucket: road
            user_dir = os.path.join(self.USER_BASE_DIR, str(self.user_id))
            road_dir = os.path.join(user_dir, "road")
            worksheet_dir = os.path.join(road_dir, f"{file_name}_worksheet")
            os.makedirs(worksheet_dir, exist_ok=True)

            # Create designs folder structure
            design_layer_dir = os.path.join(worksheet_dir, "designs", f"{file_name}_design_layer")
            os.makedirs(design_layer_dir, exist_ok=True)

            # Create construction (material) folder structure
            material_layer_dir = os.path.join(worksheet_dir, "construction", f"{file_name}_material_layer")
            os.makedirs(material_layer_dir, exist_ok=True)

            # Save worksheet-level configuration so it appears in Existing Worksheet flow
            parent_app = self.parent()
            created_by = getattr(parent_app, 'current_user', None) or str(self.user_id or "guest")
            worksheet_config = {
                "worksheet_name": f"{file_name}_worksheet",
                "project_name": "None",
                "created_at": datetime.now().isoformat(),
                "created_by": created_by,
                "worksheet_type": "Design",
                "initial_layer": f"{file_name}_design_layer",
                "worksheet_category": "Road",
                "data_category": "Design",
                "dimension": "2D",
                "point_cloud_file": os.path.join(self.ROAD_FILES_DIR, f"{file_name}.ply")
            }
            worksheet_config_path = os.path.join(worksheet_dir, "worksheet_config.txt")
            with open(worksheet_config_path, 'w', encoding='utf-8') as f:
                json.dump(worksheet_config, f, indent=4)

            # Save design-layer-level configuration inside the generated design layer folder
            design_layer_config = {
                "layer_name": f"{file_name}_design_layer",
                "dimension": "2D",
                "reference_type": "Road",
                "reference_line": "",
                "project_name": "None",
                "worksheet_name": f"{file_name}_worksheet",
                "point_cloud_file": os.path.join(self.ROAD_FILES_DIR, f"{file_name}.ply"),
                "created_by": created_by,
                "created_at": datetime.now().isoformat()
            }
            design_layer_config_path = os.path.join(design_layer_dir, "design_layer_config.txt")
            with open(design_layer_config_path, 'w', encoding='utf-8') as f:
                json.dump(design_layer_config, f, indent=4)

            # Copy design config file - REMOVE @ PREFIX from filename
            design_config_src = os.path.join(self.ROAD_FILES_DIR, f"{file_name}@design_construction_config.json")
            design_config_dst = os.path.join(design_layer_dir, "design_construction_config.json")

            if os.path.exists(design_config_src):
                import shutil
                shutil.copy2(design_config_src, design_config_dst)
                print(f"Copied design config: {design_config_src} -> {design_config_dst}")
            else:
                print(f"Warning: Design config file not found: {design_config_src}")

            # Copy all JSON files from road directory to design layer (baselines, design elements, etc.)
            import shutil
            import glob

            # First, list all JSON files in road directory for this file_name
            json_files = glob.glob(os.path.join(self.ROAD_FILES_DIR, f"{file_name}*.json"))
            print(f"DEBUG: Found {len(json_files)} JSON files for '{file_name}'")
            for f in json_files:
                print(f"  - {os.path.basename(f)}")

            copied_count = 0
            for json_file in json_files:
                # Skip the @design_construction_config.json and @material_construction_config.json files
                basename = os.path.basename(json_file)
                if "@design_construction_config.json" not in basename and "@material_construction_config.json" not in basename:
                    try:
                        dst_file = os.path.join(design_layer_dir, basename)
                        shutil.copy2(json_file, dst_file)
                        print(f"✓ Copied design JSON file: {basename}")
                        copied_count += 1
                    except Exception as e:
                        print(f"✗ Warning: Could not copy {basename}: {str(e)}")

            print(f"DEBUG: Total JSON files copied: {copied_count}")

            # Verify files exist in design_layer_dir
            copied_files = glob.glob(os.path.join(design_layer_dir, "*.json"))
            print(f"DEBUG: Files now in design_layer_dir: {len(copied_files)}")
            for f in copied_files:
                print(f"  - {os.path.basename(f)}")

            # Copy material config file - REMOVE @ PREFIX from filename
            material_config_src = os.path.join(self.ROAD_FILES_DIR, f"{file_name}@material_construction_config.json")
            material_config_dst = os.path.join(material_layer_dir, "material_construction_config.json")

            material_lines_config = None

            if os.path.exists(material_config_src):
                import shutil
                shutil.copy2(material_config_src, material_config_dst)
                print(f"Copied material config: {material_config_src} -> {material_config_dst}")

                # Read the source material config file to extract material_lines_config
                try:
                    with open(material_config_src, 'r', encoding='utf-8') as f:
                        source_material_config_data = json.load(f)

                    # Extract material_lines_config object from source file
                    if "material_lines_config" in source_material_config_data:
                        # Extract existing material_lines_config from source file
                        material_lines_config = source_material_config_data.get("material_lines_config")
                        print(f"Extracted material_lines_config from source file")
                    else:
                        # If material_lines_config doesn't exist, create one from material_line array
                        material_line_array = source_material_config_data.get("material_line", [])
                        material_lines_config = {
                            "worksheet_name": f"{file_name}_worksheet",
                            "project_name": "None",
                            "created_by": created_by,
                            "created_at": datetime.now().isoformat(),
                            "material_line": material_line_array
                        }
                        print(f"Created material_lines_config from material_line array")

                except Exception as e:
                    print(f"Warning: Could not process material config data: {str(e)}")
                    material_lines_config = {
                        "worksheet_name": f"{file_name}_worksheet",
                        "project_name": "None",
                        "created_by": created_by,
                        "created_at": datetime.now().isoformat(),
                        "material_line": []
                    }
            else:
                print(f"Warning: Material config file not found: {material_config_src}")
                # Create default material_lines_config if source file not found
                material_lines_config = {
                    "worksheet_name": f"{file_name}_worksheet",
                    "project_name": "None",
                    "created_by": created_by,
                    "created_at": datetime.now().isoformat(),
                    "material_line": []
                }

            # Save material_lines_config.txt in material layer directory
            if material_lines_config:
                material_lines_config_path = os.path.join(material_layer_dir, "material_lines_config.txt")
                with open(material_lines_config_path, 'w', encoding='utf-8') as f:
                    json.dump(material_lines_config, f, indent=4)
                print(f"Created material_lines_config.txt: {material_lines_config_path}")

            # Create Construction_Layer_config.txt in material layer directory
            construction_layer_config = {
                "construction_layer_name": f"{file_name}_material_layer",
                "worksheet_name": f"{file_name}_worksheet",
                "project_name": "None",
                "worksheet_type": "Design",
                "worksheet_category": "Road",
                "construction_type": "Road",
                "reference_layer_2d": f"{file_name}_design_layer",
                "design_layer_name": f"{file_name}_design_layer",
                "base_lines_reference": [
                    "Construction",
                    "Road Surface"
                ],
                "created_at": datetime.now().isoformat(),
                "created_by": created_by,
                "material_lines": []
            }
            construction_layer_config_path = os.path.join(material_layer_dir, "Construction_Layer_config.txt")
            with open(construction_layer_config_path, 'w', encoding='utf-8') as f:
                json.dump(construction_layer_config, f, indent=4)
            print(f"Created Construction_Layer_config.txt: {construction_layer_config_path}")

            # Store the selected design info for opening
            self.worksheet_dir = worksheet_dir
            self.design_layer_dir = design_layer_dir
            self.material_layer_dir = material_layer_dir
            self.file_name = file_name

            return True

        except Exception as e:
            print(f"Error creating worksheet structure: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
# ===========================================================================================================================
# ** BUDDY DIALOG **
# ===========================================================================================================================
class BuddyDialog(QDialog):
    """
    Dialog for creating a new buddy.
    Features:
    - Name, Mobile no, email_id fields
    - Search Buddy button: searches buddy via API by email or mobile
    - If found, shows a popup with "Buddy Data Available in server" and a "Make Buddy" button
    - After clicking "Make Buddy", creates buddy via API
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Buddy")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)

        # Get user IDs from parent
        # current_user_id = euh_id for folder structure (e.g., 100007)
        # current_api_user_id = id for API calls
        self.current_user_id = getattr(parent, 'current_user_id', None) if parent else None
        self.current_api_user_id = getattr(parent, 'current_api_user_id', None) if parent else None
        
        # Local storage for created buddies
        self.created_buddies = []   # list of dicts
        self.found_buddy_data = None  # Store found buddy data for make_buddy call

        # Setup UI
        self.init_ui()

    def init_ui(self):
        """Create and arrange all widgets."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Apply consistent gradient background (same as other dialogs)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #e6e6fa, stop:1 #e6e6fa);
                border-radius: 20px;
            }
            QLabel {
                color: black;
                font-weight: 500;
            }
            QLineEdit {
                border: 2px solid #9C27B0;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                selection-background-color: #CE93D8;
                font-weight: 500;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #7B1FA2;
                background-color: #F3E5F5;
            }
            QPushButton {
                border-radius: 20px;
                padding: 10px;
                font-weight: bold;
                min-width: 120px;
                border: none;
            }
            QPushButton#searchBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #9C27B0, stop:1 #6A1B9A);
                color: white;
            }
            QPushButton#searchBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #AB47BC, stop:1 #4A148C);
            }
            QPushButton#searchBtn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #6A1B9A, stop:1 #4A148C);
                padding: 12px 10px 8px 10px;
            }
            QPushButton#cancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333333;
            }
            QPushButton#cancelBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #D1C4E9, stop:1 #BA68C8);
            }
            QPushButton#cancelBtn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #CE93D8, stop:1 #8E24AA);
                padding: 12px 10px 8px 10px;
            }
        """)

        # ----- Form fields -----
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter full name")
        name_layout.addWidget(self.name_edit)
        form_layout.addLayout(name_layout)

        # Mobile no
        mobile_layout = QHBoxLayout()
        mobile_layout.addWidget(QLabel("Mobile no:"))
        self.mobile_edit = QLineEdit()
        self.mobile_edit.setPlaceholderText("Enter mobile number")
        mobile_layout.addWidget(self.mobile_edit)
        form_layout.addLayout(mobile_layout)

        # email_id
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("email_id:"))
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Enter email address")
        email_layout.addWidget(self.email_edit)
        form_layout.addLayout(email_layout)

        main_layout.addLayout(form_layout)

        # ----- Buttons -----
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.search_btn = QPushButton("Search Buddy")
        self.search_btn.setObjectName("searchBtn")
        self.search_btn.clicked.connect(self.search_buddy)
        button_layout.addWidget(self.search_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

    def search_buddy(self):
        """
        Search for buddy via API using email or mobile.
        If found, show a custom popup with 'Make Buddy' option.
        """
        if not self.current_api_user_id:
            QMessageBox.warning(self, "Error", "User not logged in. Please log in first.")
            return
            
        email = self.email_edit.text().strip()
        mobile = self.mobile_edit.text().strip()

        if not email and not mobile:
            QMessageBox.warning(self, "Search Error", "Please enter either email or mobile number to search.")
            return

        # Show loading message
        QMessageBox.information(self, "Searching", "Searching for buddy on server...")

        # Call API to search buddy
        from API import WorksheetAPI
        result = WorksheetAPI.search_buddy(
            user_id=self.current_user_id,
            buddy_email=email,
            buddy_mobile=mobile
        )

        if result["success"]:
            api_data = result["data"]
            
            # Handle both single buddy and multiple buddies
            # Check if response contains multiple buddy IDs
            if isinstance(api_data, list):
                # Multiple buddies found - store all
                buddy_info_list = []
                for buddy in api_data:
                    # Extract user_id from registered_apps for make_buddy call
                    registered_apps = buddy.get("registered_apps", [])
                    app_user_id = None
                    if registered_apps:
                        # Get the first user_id from registered_apps
                        app_user_id = registered_apps[0].get("user_id")
                    
                    buddy_info = {
                        "buddy_id": buddy.get("buddy_id"),
                        "app_user_id": app_user_id,  # user_id from registered_apps for make_buddy
                        "name": buddy.get("buddy_name", ""),
                        "first_name": buddy.get("buddy_first_name", ""),
                        "last_name": buddy.get("buddy_last_name", ""),
                        "email": buddy.get("buddy_email", ""),
                        "mobile": buddy.get("buddy_mobile", "")
                    }
                    buddy_info_list.append(buddy_info)
                
                # Store all found buddies
                self.found_buddy_data = buddy_info_list
                
                # Show confirmation dialog for multiple buddies
                self.show_make_buddy_popup(buddy_info_list)
            else:
                # Single buddy found (original behavior)
                # Extract user_id from registered_apps for make_buddy call
                registered_apps = api_data.get("registered_apps", [])
                app_user_id = None
                if registered_apps:
                    # Get the first user_id from registered_apps
                    app_user_id = registered_apps[0].get("user_id")
                
                buddy_info = {
                    "buddy_id": api_data.get("buddy_id"),
                    "app_user_id": app_user_id,  # user_id from registered_apps for make_buddy
                    "name": api_data.get("buddy_name", ""),
                    "first_name": api_data.get("buddy_first_name", ""),
                    "last_name": api_data.get("buddy_last_name", ""),
                    "email": api_data.get("buddy_email", ""),
                    "mobile": api_data.get("buddy_mobile", "")
                }
                
                # Pre-fill the name field
                self.name_edit.setText(buddy_info["name"])
                
                # Store buddy data for make_buddy call
                self.found_buddy_data = buddy_info
                
                # Show confirmation dialog
                self.show_make_buddy_popup(buddy_info)
        else:
            QMessageBox.information(self, "Not Found", f"No buddy found: {result['message']}")

    def show_make_buddy_popup(self, buddy_data):
        """
        Display a popup with 'Buddy Data Available in server' message and a 'Make Buddy' button.
        When 'Make Buddy' is clicked, sends buddy request via API.
        
        Args:
            buddy_data: Can be a single buddy dict or a list of buddy dicts
        """
        popup = QDialog(self)
        popup.setModal(True)
        popup.setStyleSheet(self.styleSheet())  # inherit same style

        layout = QVBoxLayout(popup)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Check if we have multiple buddies
        is_multiple = isinstance(buddy_data, list) and len(buddy_data) > 1
        
        if is_multiple:
            popup.setWindowTitle("Multiple Buddies Found")
            popup.setMinimumWidth(500)
            
            # Message for multiple buddies
            msg_label = QLabel(f"{len(buddy_data)} Buddies Found in Server")
            msg_label.setAlignment(Qt.AlignCenter)
            msg_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4A148C;")
            layout.addWidget(msg_label)
            
            # Create scroll area for multiple buddies
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setMinimumHeight(200)
            
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(10)
            
            # Add each buddy details
            for idx, buddy in enumerate(buddy_data, 1):
                buddy_label = QLabel(f"<b>{idx}. Name:</b> {buddy.get('name', 'N/A')}<br>"
                                     f"<b>Mobile:</b> {buddy.get('mobile', 'N/A')}<br>"
                                     f"<b>Email:</b> {buddy.get('email', 'N/A')}")
                buddy_label.setStyleSheet("font-size: 12px; color: #333; background: rgba(255,255,255,0.6); padding: 10px; border-radius: 8px;")
                scroll_layout.addWidget(buddy_label)
            
            scroll.setWidget(scroll_widget)
            layout.addWidget(scroll)
            
        else:
            # Single buddy (original behavior)
            buddy = buddy_data[0] if isinstance(buddy_data, list) else buddy_data
            
            popup.setWindowTitle("Buddy Found")
            popup.setMinimumWidth(400)
            
            # Message
            msg_label = QLabel("Buddy Data Available in Server")
            msg_label.setAlignment(Qt.AlignCenter)
            msg_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4A148C;")
            layout.addWidget(msg_label)

            # Show buddy details
            details_text = f"""<b>Name:</b> {buddy.get('name', 'N/A')}<br>
<b>Mobile:</b> {buddy.get('mobile', 'N/A')}<br>
<b>Email:</b> {buddy.get('email', 'N/A')}"""
            
            details = QLabel(details_text)
            details.setAlignment(Qt.AlignCenter)
            details.setStyleSheet("font-size: 12px; color: #333; background: rgba(255,255,255,0.6); padding: 10px; border-radius: 8px;")
            layout.addWidget(details)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        make_btn = QPushButton("Make Buddy")
        make_btn.setObjectName("searchBtn")  # reuse purple gradient
        make_btn.clicked.connect(lambda: self.create_buddy(buddy_data, popup))
        btn_layout.addWidget(make_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(popup.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        popup.exec_()

    def create_buddy(self, buddy_data, popup):
        """
        Send buddy request via API (Mode 2) and handle the response.
        Closes the popup and the main dialog on success.
        
        Args:
            buddy_data: Can be a single buddy dict or a list of buddy dicts
            popup: The popup dialog to close
        """
        if not self.current_user_id:
            QMessageBox.warning(self, "Error", "User not logged in.")
            return

        # Handle both single buddy and multiple buddies
        if isinstance(buddy_data, list):
            # Multiple buddies - extract all app_user_ids from registered_apps
            buddy_ids = []
            for buddy in buddy_data:
                # Get app_user_id from registered_apps (not buddy_id)
                app_user_id = buddy.get("app_user_id")
                if app_user_id:
                    buddy_ids.append(app_user_id)
            
            if not buddy_ids:
                QMessageBox.warning(self, "Error", "No valid user IDs found. Cannot create buddies.")
                return
            
            # Show loading message with count
            QMessageBox.information(self, "Creating Buddies", f"Sending buddy request for {len(buddy_ids)} buddies...")
            
            # Call API to make buddies with array of IDs
            from API import WorksheetAPI
            result = WorksheetAPI.make_buddy(
                user_id=self.current_user_id,
                buddy_id=buddy_ids
            )
            
            if result["success"]:
                api_data = result["data"]
                
                # Store all buddies locally
                self.created_buddies.extend(buddy_data)
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"{len(buddy_ids)} Buddies created successfully!"
                )
                popup.accept()   # close the popup
                self.accept()    # close the main dialog
            else:
                QMessageBox.warning(
                    self, 
                    "Error", 
                    f"Failed to create buddies: {result['message']}"
                )
        else:
            # Single buddy (original behavior)
            # Get app_user_id from registered_apps (not buddy_id)
            app_user_id = buddy_data.get("app_user_id")
            
            if not app_user_id:
                QMessageBox.warning(self, "Error", "Invalid user ID. Cannot create buddy.")
                return

            # Show loading message
            QMessageBox.information(self, "Creating Buddy", "Sending buddy request...")

            # Call API to make buddy (Mode 2)
            from API import WorksheetAPI
            result = WorksheetAPI.make_buddy(
                user_id=self.current_user_id,
                buddy_id=app_user_id
            )

            if result["success"]:
                api_data = result["data"]
                buddy_name = api_data.get("buddy_name", buddy_data.get("name", "Buddy"))
                
                # Store locally
                self.created_buddies.append(buddy_data)
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Buddy '{buddy_name}' created successfully!"
                )
                popup.accept()   # close the popup
                self.accept()    # close the main dialog
            else:
                QMessageBox.warning(
                    self, 
                    "Error", 
                    f"Failed to create buddy: {result['message']}"
                )

# ===========================================================================================================================
# ** BUDDIES & WORKSHEETS DIALOG (Fixed seen/unseen + hover border only) **
# ===========================================================================================================================
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QCheckBox,
    QScrollArea, QWidget, QButtonGroup, QFrame, QMessageBox, QStackedWidget
)
from PyQt5.QtCore import Qt

# ------------------------------------------------------------------
# Custom frame for buddy row – applies style based on 'seen'
# ------------------------------------------------------------------
class BuddyFrame(QFrame):
    def __init__(self, seen=False, parent=None):
        super().__init__(parent)
        self.set_seen(seen)
        self.setObjectName("BuddyFrame")
        self.setFixedHeight(50)

    def set_seen(self, seen):
        self.seen = seen
        if seen:
            # Seen: normal black text for both name and time
            self.setStyleSheet("""
                QFrame#BuddyFrame {
                    background-color: #e8eaf6;
                    border-radius: 10px;
                    margin: 2px;
                    padding: 5px;
                }
                QFrame#BuddyFrame:hover {
                    border: 1px solid #9C27B0;
                }
                QLabel#nameLabel, QLabel#dateLabel {
                    font-weight: normal;
                    color: black;
                }
            """)
        else:
            # Unseen: bold black text for both name and time
            self.setStyleSheet("""
                QFrame#BuddyFrame {
                    background-color: white;
                    border-radius: 10px;
                    margin: 2px;
                    padding: 5px;
                }
                QFrame#BuddyFrame:hover {
                    border: 1px solid #9C27B0;
                }
                QLabel#nameLabel, QLabel#dateLabel {
                    font-weight: bold;
                    color: black;
                }
            """)
        # Force immediate style refresh
        self.style().unpolish(self)
        self.style().polish(self)

# =========================================================================================================================================
#                                               ** BUDDIES & WORKSHEETS DIALOG **
# ========================================================================================================================================
class BuddiesWorksheetsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buddies & Worksheets")
        self.setModal(True)
        self.setMinimumSize(700, 500)
        self.setStyleSheet(self._get_base_stylesheet())

        # Get user ID from parent
        self.current_user_id = getattr(parent, 'current_user_id', None) if parent else None

        self.buddies_data = []

        if self.current_user_id is not None:
            res = WorksheetAPI.get_buddies(self.current_user_id)
            if res.get("success"):
                api_data = res.get("data", {})
                # The buddies list is under the 'buddies' key in the response
                buddies_list = api_data.get("buddies", []) if isinstance(api_data, dict) else []
                
                self.buddies_data = []
                for buddy in buddies_list:
                    # Extract buddy_euh_id from the apps list
                    buddy_id = None
                    if buddy.get("apps") and len(buddy["apps"]) > 0:
                        buddy_id = buddy["apps"][0].get("buddy_euh_id")
                    
                    if not buddy_id:
                        continue
                        
                    # Try to get user_name from local user_config.txt first
                    local_name = None
                    config_path = os.path.join(r"C:\3D_Tool\user", str(buddy_id), "user_config.txt")
                    if os.path.exists(config_path):
                        try:
                            with open(config_path, 'r', encoding='utf-8') as f:
                                cfg = json.load(f)
                                local_name = cfg.get("user_name")
                        except:
                            pass
                    
                    buddy_name = local_name or buddy.get("buddy_name") or "Buddy"
                    
                    self.buddies_data.append({
                        "id": buddy_id,
                        "name": buddy_name,
                        "last_activity": "", # get_buddies doesn't provide this; will be empty for sorting
                        "seen": False,
                        "worksheets": []
                    })

        self.sort_buddies()

        # Dummy worksheet data no longer needed
        self.worksheets_data = []

        self.selected_buddy = None
        self.page2_title = None
        self.selected_worksheets = []

        self.stacked_widget = QStackedWidget(self)
        self.init_page1()
        self.init_page2()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        self.stacked_widget.setCurrentIndex(0)


        # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def sort_buddies(self):
        self.buddies_data.sort(key=lambda b: b["last_activity"], reverse=True)

    def format_activity_display(self, datetime_str):
        try:
            if not datetime_str:
                return ""
            if 'T' in datetime_str:
                dt = datetime.strptime(datetime_str.split('.')[0], "%Y-%m-%dT%H:%M:%S")
            elif 'AM' in datetime_str or 'PM' in datetime_str:
                dt = datetime.strptime(datetime_str, "%I:%M %p %d-%m-%Y")
            else:
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if dt.date() == today.date():
                return dt.strftime("%H:%M")
            else:
                return dt.strftime("%d %B")
        except:
            return datetime_str

    def _get_base_stylesheet(self):
        return """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #e6e6fa, stop:1 #e6e6fa);
                border-radius: 20px;
            }
            QRadioButton, QCheckBox {
                color: black;
                font-weight: 500;
                spacing: 8px;
            }
            QPushButton {
                border-radius: 20px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
                border: none;
            }
            QPushButton#nextBtn, QPushButton#buyBtn, QPushButton#downloadBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #9C27B0, stop:1 #6A1B9A);
                color: white;
            }
            QPushButton#nextBtn:hover, QPushButton#buyBtn:hover, QPushButton#downloadBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #AB47BC, stop:1 #4A148C);
            }
            QPushButton#cancelBtn, QPushButton#backBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333333;
            }
            QPushButton#cancelBtn:hover, QPushButton#backBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #D1C4E9, stop:1 #BA68C8);
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QPushButton:disabled {
                background: #b0a0c0;
                color: #555;
            }
        """

    # ------------------------------------------------------------------
    # Page 1 – Buddies
    # ------------------------------------------------------------------
    def init_page1(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Buddies")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A148C; margin-bottom: 10px;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        self.buddies_layout = QVBoxLayout(scroll_content)
        self.buddies_layout.setSpacing(8)
        self.buddies_layout.setContentsMargins(10, 10, 10, 10)
        self.buddies_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.buddy_group = QButtonGroup(self)
        self.buddy_group.buttonToggled.connect(self.on_buddy_selected)

        self.refresh_buddies_list()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("nextBtn")
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.on_next_clicked)
        btn_layout.addWidget(self.next_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.stacked_widget.addWidget(page)

    def refresh_buddies_list(self):
        # Clear existing rows
        while self.buddies_layout.count() > 1:
            item = self.buddies_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for btn in self.buddy_group.buttons():
            self.buddy_group.removeButton(btn)

        self.sort_buddies()

        for buddy in self.buddies_data:
            frame = BuddyFrame(seen=buddy["seen"])
            row_layout = QHBoxLayout(frame)
            row_layout.setContentsMargins(10, 8, 10, 8)

            radio = QRadioButton()
            radio.setProperty("buddy_data", buddy)

            name_label = QLabel(buddy["name"])
            name_label.setObjectName("nameLabel")

            display_text = self.format_activity_display(buddy["last_activity"])
            date_label = QLabel(display_text)
            date_label.setObjectName("dateLabel")
            date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            row_layout.addWidget(radio)
            row_layout.addWidget(name_label)
            row_layout.addStretch()
            row_layout.addWidget(date_label)

            self.buddies_layout.insertWidget(self.buddies_layout.count() - 1, frame)
            self.buddy_group.addButton(radio)

    def on_buddy_selected(self, button, checked):
        if checked:
            self.selected_buddy = button.property("buddy_data")
            self.next_btn.setEnabled(True)
        else:
            if not any(r.isChecked() for r in self.buddy_group.buttons()):
                self.selected_buddy = None
                self.next_btn.setEnabled(False)

    def on_next_clicked(self):
        if not self.selected_buddy:
            return

        # Mark as seen
        self.selected_buddy["seen"] = True
        
        # Show a simple message or cursor to indicate loading if needed
        # For now we'll just call the API synchronously
        
        # Fetch shared files for this specific buddy
        # Pass current_user_id (receiver) and selected_buddy["id"] (sender)
        res = WorksheetAPI.get_shared_files(self.current_user_id, self.selected_buddy["id"])
        
        if res.get("success"):
            data = res.get("data", [])
            # Parse the worksheets from the response
            self.selected_buddy["worksheets"] = self._parse_worksheets_data(data)
        else:
            QMessageBox.warning(self, "Error", f"Failed to fetch worksheets for this buddy: {res.get('message')}")
            return

        self.refresh_buddies_list()
        self.update_page2_title()
        self.refresh_worksheets_list()
        self.stacked_widget.setCurrentIndex(1)

    def _parse_worksheets_data(self, data):
        """Helper to parse the shared files data into the format Page 2 expects."""
        parsed_worksheets = []
        for sf in data:
            ws_data = sf.get("worksheet", {})
            ws_name = sf.get("worksheet_name") or ws_data.get("worksheet_name")
            if not ws_name:
                ws_id = ws_data.get('worksheet_id', sf.get('worksheet_id', 'Unknown'))
                ws_name = f"Worksheet {ws_id}"
            
            parsed_worksheets.append({
                "id": ws_data.get("worksheet_id", sf.get("worksheet_id")),
                "name": ws_name,
                "purchased": (sf.get("can_download", False) is True) and (sf.get("purchased_status") == "Purchased"),
                "button_text": sf.get("button_text", "Download"),
                "file_id": sf.get("file_id"),
                "raw_data": sf
            })
        return parsed_worksheets

    # ------------------------------------------------------------------
    # Page 2 – Worksheets
    # ------------------------------------------------------------------
    def init_page2(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        self.page2_title = QLabel()
        self.page2_title.setAlignment(Qt.AlignCenter)
        self.page2_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A148C; margin-bottom: 10px;")
        layout.addWidget(self.page2_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        self.worksheets_layout = QVBoxLayout(scroll_content)
        self.worksheets_layout.setSpacing(15)
        self.worksheets_layout.setContentsMargins(10, 10, 10, 10)
        self.worksheets_layout.addStretch()

        self.worksheet_checkboxes = []

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.addStretch()
        back_btn = QPushButton("Go Back")
        back_btn.setObjectName("backBtn")
        back_btn.clicked.connect(self.on_go_back)
        bottom_btn_layout.addWidget(back_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        bottom_btn_layout.addWidget(cancel_btn)

        layout.addLayout(bottom_btn_layout)
        self.stacked_widget.addWidget(page)

    def on_go_back(self):
        self.refresh_buddies_list()   # ensures seen buddies show normal style
        self.stacked_widget.setCurrentIndex(0)

    def refresh_worksheets_list(self):
        # Clear existing rows
        while self.worksheets_layout.count() > 1:
            item = self.worksheets_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.worksheet_checkboxes = []
        
        if not self.selected_buddy:
            return
            
        worksheets = self.selected_buddy.get("worksheets", [])
        
        for ws in worksheets:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(10, 5, 10, 5)

            # Checkbox
            cb = QCheckBox()
            cb.setProperty("worksheet_data", ws)
            cb.stateChanged.connect(self.on_worksheet_checkbox_toggled)
            row_layout.addWidget(cb)

            # Worksheet name
            name_label = QLabel(ws["name"])
            name_label.setStyleSheet("font-weight: bold; font-size: 13px;")
            name_label.setMinimumWidth(150)
            row_layout.addWidget(name_label)

            row_layout.addStretch()

            btn = QPushButton(ws.get("button_text", "Download"))
            if ws.get("purchased", False):
                btn.setObjectName("downloadBtn")
                btn.clicked.connect(lambda checked, w=ws: self.on_download_worksheet(w))
            else:
                btn.setObjectName("buyBtn")
                btn.clicked.connect(lambda checked, w=ws: self.on_buy_worksheet(w))

            btn.setFixedWidth(100)
            row_layout.addWidget(btn)

            self.worksheets_layout.insertWidget(self.worksheets_layout.count() - 1, row_widget)
            self.worksheet_checkboxes.append((cb, ws))

    # -------------------------------------------------------------------
    # 
    # -------------------------------------------------------------------
    def on_worksheet_checkbox_toggled(self, state):
        cb = self.sender()
        ws = cb.property("worksheet_data")
        if state == Qt.Checked:
            if ws not in self.selected_worksheets:
                self.selected_worksheets.append(ws)
        else:
            if ws in self.selected_worksheets:
                self.selected_worksheets.remove(ws)
    
    # -------------------------------------------------------------------
    # 
    # -------------------------------------------------------------------
    def update_page2_title(self):
        if self.selected_buddy:
            buddy_name = self.selected_buddy["name"]
            self.page2_title.setText(f"{buddy_name}'s Worksheets")
        else:
            self.page2_title.setText("Worksheets")

    def on_buy_worksheet(self, worksheet):
        QMessageBox.information(self, "Purchase", f"You have bought {worksheet['name']}.\n(API integration pending)")

    # -----------------------------------------------------------------------
    # This is the main function to handle worksheet download. It extracts all necessary information from the worksheet object,
    # creates the required folder structure, and saves the layer JSON files and config files as specified in the API response.
    # -----------------------------------------------------------------------
    def on_download_worksheet(self, worksheet):
        try:
            import os
            import json
            
            sf = worksheet.get("raw_data", {})
            shared_by_user = sf.get("shared_by_user", {})
            shared_by = sf.get("shared_by") or shared_by_user.get("user_id") or "unknown_user"
            shared_from_app = sf.get("shared_from_app")
            
            # Map application to folder name
            if shared_from_app == 2:
                app_folder = "bridge"
            else:
                app_folder = "road"
                
            ws_data = sf.get("worksheet", {})
            ws_name = sf.get("worksheet_name") or ws_data.get("worksheet_name", "Unknown_Worksheet")
            layers = sf.get("layers", [])
            
            if not layers:
                if sf.get("design_layer_json"):
                    layers.append({
                        "parse_type": "design", 
                        "parse_name": sf.get("design_layer_name", "Unknown_Design"), 
                        "data_to_save": sf
                    })
                if sf.get("material_layer_json"):
                    layers.append({
                        "parse_type": "material", 
                        "parse_name": sf.get("material_layer_name", "Unknown_Material"), 
                        "data_to_save": sf
                    })
                if not layers and sf.get("layer_type"):
                    layers.append({
                        "parse_type": sf.get("layer_type"), 
                        "parse_name": sf.get("layer_name", "Unknown_Layer"), 
                        "data_to_save": sf
                    })
                
                # Support new structured format in worksheet object
                if not layers:
                    dl = ws_data.get("design_layers") or ws_data.get("design_layer", [])
                    for d in dl:
                         layers.append({
                             "parse_type": d.get("layer_type", "design"),
                             "parse_name": d.get("layer_name", "Unknown_Design"),
                             "data_to_save": d.get("layer_json_data", d),
                             "config_data": d.get("layer_config_data", {})
                         })
                    ml = ws_data.get("material_layers") or ws_data.get("material_layer", [])
                    for m in ml:
                         layers.append({
                             "parse_type": m.get("layer_type", "material"),
                             "parse_name": m.get("layer_name", "Unknown_Material"),
                             "data_to_save": m.get("layer_json_data", m),
                             "config_data": m.get("layer_config_data", {})
                         })

            if not layers:
                QMessageBox.warning(self, "Download Warn", "No layers found to download for this worksheet.")
                return

            saved_paths = []
            base_path = r"C:\3D_Tool\user"
            
            # Create user folder and check/create user_config.txt
            user_folder_path = os.path.join(base_path, str(shared_by))
            os.makedirs(user_folder_path, exist_ok=True)
            
            user_config_path = os.path.join(user_folder_path, "user_config.txt")
            if not os.path.exists(user_config_path) and shared_by_user:
                with open(user_config_path, 'w', encoding='utf-8') as f:
                    json.dump(shared_by_user, f, indent=4, sort_keys=False, ensure_ascii=False)
                saved_paths.append(user_config_path)
            
            # Create worksheet folder
            ws_folder_path = os.path.join(user_folder_path, app_folder, ws_name)
            os.makedirs(ws_folder_path, exist_ok=True)
            
            # Extract and save worksheet_config_data
            ws_config = ws_data.get("worksheet_config")
            if ws_config:
                ws_config_path = os.path.join(ws_folder_path, "worksheet_config.txt")
                with open(ws_config_path, 'w', encoding='utf-8') as f:
                    json.dump(ws_config, f, indent=4, sort_keys=False, ensure_ascii=False)
                saved_paths.append(ws_config_path)

            for layer in layers:
                if "parse_type" in layer:
                    layer_type = layer["parse_type"]
                    layer_name = layer["parse_name"]
                    layer_to_save = layer["data_to_save"]
                    layer_config = layer.get("config_data")
                else:
                    layer_type = layer.get("layer_type", "")
                    layer_name = layer.get("layer_name", "Unknown_Layer")
                    layer_to_save = layer
                    layer_config = layer.get("layer_config_data")
                
                # Map layer type to folder name and file name
                if str(layer_type).lower() == "design" or layer_type == 1:
                    layer_folder = "designs"
                    json_filename = "design_construction_config.json"
                    config_filename = "design_layer_config.txt"
                else:
                    # Default "Material" -> "construction"
                    layer_folder = "construction"
                    json_filename = "material_construction_config.json"
                    config_filename = "Construction_Layer_config.txt"
                    
                # Base path: C:\3D_Tool\user\{shared_by}\{app_folder}\{ws_name}\{layer_folder}\{layer_name}
                full_path = os.path.join(base_path, str(shared_by), app_folder, ws_name, layer_folder, layer_name)
                
                # Create directories
                os.makedirs(full_path, exist_ok=True)
                
                # File path
                file_path = os.path.join(full_path, json_filename)
                
                # Save the complete layer object exactly as it appears in the API response
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(layer_to_save, f, indent=4, sort_keys=False, ensure_ascii=False)
                    
                saved_paths.append(file_path)
                
                # Save layer config
                if layer_config:
                    config_file_path = os.path.join(full_path, config_filename)
                    with open(config_file_path, 'w', encoding='utf-8') as f:
                        json.dump(layer_config, f, indent=4, sort_keys=False, ensure_ascii=False)
                    saved_paths.append(config_file_path)
                    
                # Extract and save material_line_config if present
                if layer_folder == "construction":
                    material_line_config = None
                    if isinstance(layer_to_save, dict):
                        material_line_config = layer_to_save.get("material_line_config")
                    if material_line_config is not None:
                        material_config_file_path = os.path.join(full_path, "material_layer_config.txt")
                        with open(material_config_file_path, 'w', encoding='utf-8') as f:
                            json.dump(material_line_config, f, indent=4, sort_keys=False, ensure_ascii=False)
                        saved_paths.append(material_config_file_path)
                
            msg = "\n".join(saved_paths)
            QMessageBox.information(self, "Download Successful", f"Successfully downloaded layers for '{ws_name}'.\n\nSaved to:\n{msg}")
        except Exception as e:
            QMessageBox.critical(self, "Download Error", f"Failed to download: {str(e)}")

    def get_selected_buddy(self):
        return self.selected_buddy

    def get_selected_worksheets(self):
        return self.selected_worksheets

# ===========================================================================================================================
# ** UPLOAD DIALOG (Three‑page: Worksheets → Buddies → Uploading) **
# ===========================================================================================================================
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QScrollArea, QWidget, QProgressBar, QMessageBox, QListWidget, 
    QListWidgetItem, QAbstractItemView, QGroupBox, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer

class ShareWithBuddiesDialog(QDialog):
    """
    Three‑page share dialog:
    - Page 1: Select worksheets (folders) with checkboxes. When selected, shows Design and Material layers.
    - Page 2: Select buddies (multiple selection with checkboxes) from server/dummy data.
    - Page 3: Upload progress bar and status.
    """
    def __init__(self, worksheets_path, parent=None):
        super().__init__(parent)
        self.worksheets_path = worksheets_path
        self.setWindowTitle("Share with my Buddies")
        self.setModal(True)
        self.setMinimumSize(700, 600)
        self.setStyleSheet(self._get_stylesheet())

        # Data containers
        self.worksheets_folders = []        # list of folder names
        self.selected_worksheets_data = {}  # dict: {worksheet_name: {"designs": [], "materials": []}}

        # Get user ID from parent
        self.current_user_id = getattr(parent, 'current_user_id', None) if parent else None

        # Fetch buddies from API
        self.buddies_data = self._fetch_buddies_from_api()
        self.sort_buddies()

        self.selected_buddies = []          # list of selected buddy dicts

        # Load worksheets from the given path
        self.load_worksheets()

        # Stacked widget for pages
        self.stacked_widget = QStackedWidget(self)
        self.init_page1()
        self.init_page2()
        self.init_page3()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        self.stacked_widget.setCurrentIndex(0)
    
        # Center the dialog on screen
        self.center_on_screen()

    def _get_stylesheet(self):
        return """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #e6e6fa, stop:1 #e6e6fa);
                border-radius: 20px;
            }
            QLabel {
                color: black;
                font-weight: 500;
            }
            QCheckBox {
                color: black;
                font-weight: 500;
                spacing: 8px;
            }
            QPushButton {
                border-radius: 20px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
                border: none;
            }
            QPushButton#nextBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #9C27B0, stop:1 #6A1B9A);
                color: white;
            }
            QPushButton#nextBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #AB47BC, stop:1 #4A148C);
            }
            QPushButton#backBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333333;
            }
            QPushButton#backBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #D1C4E9, stop:1 #BA68C8);
            }
            QPushButton#cancelBtn, QPushButton#doneBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #E1BEE7, stop:1 #CE93D8);
                color: #333333;
            }
            QPushButton#cancelBtn:hover, QPushButton#doneBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #D1C4E9, stop:1 #BA68C8);
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QGroupBox {
                border: 2px solid #9C27B0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #4A148C;
            }
            QListWidget {
                border: 2px solid #9C27B0;
                border-radius: 8px;
                padding: 5px;
                background-color: white;
                selection-background-color: #CE93D8;
                selection-color: black;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #CE93D8;
                color: black;
            }
            QPushButton:disabled {
                background: #b0a0c0;
                color: #555;
            }
            QProgressBar {
                border: 2px solid #9C27B0;
                border-radius: 10px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #9C27B0, stop:1 #6A1B9A);
                border-radius: 8px;
            }
        """

    def sort_buddies(self):
        self.buddies_data.sort(key=lambda b: b["last_activity"], reverse=True)

    def _fetch_buddies_from_api(self):
        """Fetch buddies from API using user_id and show only buddy_name from the buddies list."""
        if not self.current_user_id:
            return []
        try:
            from API import WorksheetAPI
            result = WorksheetAPI.get_buddies(user_id=self.current_user_id)
            if result["success"]:
                api_data = result["data"]
                # The buddies list is under the 'buddies' key in the response
                buddies_list = api_data.get("buddies", []) if isinstance(api_data, dict) else []
                buddies = []
                for buddy in buddies_list:
                    buddy_euh_id = None
                    if buddy.get("apps") and len(buddy["apps"]) > 0:
                        buddy_euh_id = buddy["apps"][0].get("buddy_euh_id")
                        
                    buddies.append({
                        "name": buddy.get("buddy_name", "Unknown"),
                        "buddy_euh_id": buddy_euh_id,
                        # Optionally, you can add more fields if you want to display more info
                        "last_activity": "",  # Not available in response, so leave blank or add if needed
                        "seen": True  # Default to True or handle as needed
                    })
                return buddies
            else:
                print(f"Failed to fetch buddies: {result.get('message')}")
                return []
        except Exception as e:
            print(f"Error fetching buddies: {str(e)}")
            return []
        
    # ------------------------------------------------------------------
    # Load worksheets from directory (list SUBFOLDERS only)
    # ------------------------------------------------------------------
    def load_worksheets(self):
        """
        Fetch worksheets from the API (mode 1) and populate self.worksheets_folders and self.worksheet_data_map.
        """
        self.worksheets_folders = []
        self.worksheet_data_map = {}
        self.worksheet_file_id_map = {}
        self.worksheet_full_data_map = getattr(self, 'worksheet_full_data_map', {})
        
        if not self.current_user_id:
            return
            
        try:
            from API import WorksheetAPI
            result = WorksheetAPI.get_worksheet_layer_data(self.current_user_id, mode=1)
            if result.get("success"):
                data = result.get("data", {})
                items = data.get("worksheets", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                if isinstance(data, dict) and "data" in data:
                    items = data["data"]
                    
                for item in items:
                    if isinstance(item, dict):
                        ws_id = item.get("worksheet_id", item.get("id"))
                        ws_name = item.get("worksheet_name", item.get("name", f"Worksheet {ws_id}"))
                        file_id = item.get("file_id")
                        
                        if ws_name and ws_name not in self.worksheets_folders:
                            self.worksheets_folders.append(ws_name)
                            self.worksheet_data_map[ws_name] = ws_id
                            self.worksheet_full_data_map[ws_name] = item
                            if file_id is not None:
                                self.worksheet_file_id_map[ws_name] = file_id
            else:
                print(f"Failed to load worksheets from API: {result.get('message')}")
        except Exception as e:
            print(f"Error loading worksheets from API: {e}")
            
        self.worksheets_folders.sort()

    # ------------------------------------------------------------------
    # Load design and material layers for a worksheet
    # ------------------------------------------------------------------
    def load_worksheet_layers(self, worksheet_name):
        """Load design and material layers from cached API data."""
        design_layers = []
        material_layers = []
        
        ws_id = getattr(self, 'worksheet_data_map', {}).get(worksheet_name)
        print(f"DEBUG load_worksheet_layers: worksheet_name='{worksheet_name}', ws_id={ws_id}")
        if ws_id is None or not self.current_user_id:
            print("DEBUG: ws_id is None or current_user_id is not set. Returning early.")
            return design_layers, material_layers
            
        self.design_id_map = getattr(self, 'design_id_map', {})
        self.material_id_map = getattr(self, 'material_id_map', {})
        self.design_id_map[worksheet_name] = {}
        self.material_id_map[worksheet_name] = {}
            
        ws = getattr(self, 'worksheet_full_data_map', {}).get(worksheet_name, {})
        
        if ws:
            # Parse design layers
            d_items = ws.get("design_layers", [])
            print(f"DEBUG: Found {len(d_items)} design layers")
            for item in d_items:
                if isinstance(item, dict):
                    name = item.get("layer_name", item.get("design_layer_name", item.get("name")))
                    layer_id = item.get("layer_id", item.get("id"))
                    if name:
                        design_layers.append(name)
                        if layer_id is not None:
                            self.design_id_map[worksheet_name][name] = layer_id
                elif isinstance(item, str):
                    design_layers.append(item)
                    
            # Parse material layers
            m_items = ws.get("material_layers", [])
            print(f"DEBUG: Found {len(m_items)} material layers")
            for item in m_items:
                if isinstance(item, dict):
                    name = item.get("layer_name", item.get("material_layer_name", item.get("name")))
                    layer_id = item.get("layer_id", item.get("id"))
                    if name:
                        material_layers.append(name)
                        if layer_id is not None:
                            self.material_id_map[worksheet_name][name] = layer_id
                elif isinstance(item, str):
                    material_layers.append(item)
        else:
            print(f"DEBUG: No cached worksheet data found for '{worksheet_name}'")
            
        return design_layers, material_layers

    # ------------------------------------------------------------------
    # Page 1: Select Worksheets with Design and Material layer selection
    # ------------------------------------------------------------------
    def init_page1(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Select Worksheets")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A148C; margin-bottom: 20px;")
        layout.addWidget(title)

        # Split into two sections: Worksheets list (left) and Layers selection (right)
        split_layout = QHBoxLayout()
        
        # Left side: Worksheets list with checkboxes
        worksheets_group = QGroupBox("Available Worksheets")
        worksheets_layout = QVBoxLayout(worksheets_group)
        
        scroll_worksheets = QScrollArea()
        scroll_worksheets.setWidgetResizable(True)
        scroll_worksheets.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_worksheets.setMaximumWidth(300)
        
        scroll_content = QWidget()
        self.worksheets_list_layout = QVBoxLayout(scroll_content)
        self.worksheets_list_layout.setSpacing(8)
        self.worksheets_list_layout.setContentsMargins(10, 10, 10, 10)
        self.worksheets_list_layout.addStretch()
        
        self.worksheet_checkboxes = {}
        for folder_name in self.worksheets_folders:
            cb = QCheckBox(folder_name)
            cb.setStyleSheet("""
                QCheckBox {
                    spacing: 15px;  /* Adds space between checkbox indicator and text */
                    margin-bottom: 10px;
                }
            """)
            cb.stateChanged.connect(lambda state, name=folder_name: self.on_worksheet_toggled(state, name))
            self.worksheets_list_layout.insertWidget(self.worksheets_list_layout.count() - 1, cb)
            self.worksheet_checkboxes[folder_name] = cb
        
        scroll_worksheets.setWidget(scroll_content)
        worksheets_layout.addWidget(scroll_worksheets)
        split_layout.addWidget(worksheets_group)
        
        # Right side: Layers selection container (initially empty)
        self.layers_container = QGroupBox("Select Files to Upload")
        self.layers_layout = QVBoxLayout(self.layers_container)
        self.layers_container.setVisible(False)
        split_layout.addWidget(self.layers_container)
        
        layout.addLayout(split_layout)
        
        # Buttons: Next and Cancel
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.next_btn1 = QPushButton("Next")
        self.next_btn1.setObjectName("nextBtn")
        self.next_btn1.setEnabled(False)
        self.next_btn1.clicked.connect(lambda: self.go_to_page(1))
        btn_layout.addWidget(self.next_btn1)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.stacked_widget.addWidget(page)

    def on_worksheet_toggled(self, state, worksheet_name):
        """Handle worksheet checkbox toggling and update layers container."""
        if state == Qt.Checked:
            # Initialize empty layers for this worksheet
            self.selected_worksheets_data[worksheet_name] = {
                "designs": [],
                "materials": []
            }
            self.layers_container.setVisible(True)
            # Refresh the layers display for all selected worksheets
            self.refresh_layers_display()
        else:
            # Remove worksheet from selection
            if worksheet_name in self.selected_worksheets_data:
                del self.selected_worksheets_data[worksheet_name]
            # If no worksheets selected, hide layers container
            if not self.selected_worksheets_data:
                self.layers_container.setVisible(False)
            else:
                # Refresh the layers display for remaining worksheets
                self.refresh_layers_display()
        
        self.next_btn1.setEnabled(len(self.selected_worksheets_data) > 0)

    def refresh_layers_display(self):
        """Refresh the layers display for all selected worksheets."""
        # Clear existing widgets
        while self.layers_layout.count():
            item = self.layers_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.selected_worksheets_data:
            return
        
        # Show all selected worksheets
        selected_worksheets_label = QLabel("<b>Selected Worksheets:</b>")
        selected_worksheets_label.setStyleSheet("color: #4A148C; margin-top: 10px;")
        self.layers_layout.addWidget(selected_worksheets_label)
        
        # Create tabs for each selected worksheet
        self.worksheet_tabs = QTabWidget()
        self.worksheet_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #9C27B0;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.5);
            }
            QTabBar::tab {
                background-color: #E1BEE7;
                border-radius: 8px;
                padding: 5px 15px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #9C27B0;
                color: white;
            }
        """)
        
        # Store references to list widgets for each worksheet
        self.worksheet_layers_widgets = {}
        
        # Add a tab for each selected worksheet
        for ws_name in self.selected_worksheets_data.keys():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            # Design Layer selection
            design_label = QLabel("Select Design Layer(s):")
            design_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            tab_layout.addWidget(design_label)
            
            design_list = QListWidget()
            design_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
            design_list.setMaximumHeight(150)
            
            # Get layers for this worksheet
            ws_design_layers, ws_material_layers = self.load_worksheet_layers(ws_name)
            
            if not ws_design_layers:
                design_list.addItem("No Design Layers Found")
                design_list.setEnabled(False)
            else:
                for layer in ws_design_layers:
                    design_list.addItem(layer)
                all_item = QListWidgetItem("All of the above")
                all_item.setForeground(Qt.darkBlue)
                design_list.addItem(all_item)
            
            # Restore previously selected layers
            previously_selected = self.selected_worksheets_data[ws_name].get("designs", [])
            for i in range(design_list.count()):
                item = design_list.item(i)
                if item.text() in previously_selected:
                    item.setSelected(True)
            
            # Connect with proper capture using default arguments
            design_list.itemSelectionChanged.connect(
                lambda checked=False, name=ws_name, lst=design_list, layers=ws_design_layers: 
                self.on_design_selection_changed(name, lst, layers)
            )
            tab_layout.addWidget(design_list)
            
            # Material Layer selection
            material_label = QLabel("Select Material Layer(s):")
            material_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            tab_layout.addWidget(material_label)
            
            material_list = QListWidget()
            material_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
            material_list.setMaximumHeight(150)
            
            if not ws_material_layers:
                material_list.addItem("No Material Layers Found")
                material_list.setEnabled(False)
            else:
                for layer in ws_material_layers:
                    material_list.addItem(layer)
                all_item = QListWidgetItem("All of the above")
                all_item.setForeground(Qt.darkBlue)
                material_list.addItem(all_item)
            
            # Restore previously selected layers
            previously_selected_materials = self.selected_worksheets_data[ws_name].get("materials", [])
            for i in range(material_list.count()):
                item = material_list.item(i)
                if item.text() in previously_selected_materials:
                    item.setSelected(True)
            
            material_list.itemSelectionChanged.connect(
                lambda checked=False, name=ws_name, lst=material_list, layers=ws_material_layers: 
                self.on_material_selection_changed(name, lst, layers)
            )
            tab_layout.addWidget(material_list)
            
            tab_layout.addStretch()
            self.worksheet_tabs.addTab(tab, ws_name)
            
            # Store references
            self.worksheet_layers_widgets[ws_name] = {
                "design_list": design_list,
                "material_list": material_list,
                "design_layers": ws_design_layers,
                "material_layers": ws_material_layers
            }
        
        self.layers_layout.addWidget(self.worksheet_tabs)

    def on_design_selection_changed(self, worksheet_name, design_list, all_design_layers):
        """Handle design layer selection with 'All' option logic."""
        if worksheet_name not in self.selected_worksheets_data:
            return
        
        selected_items = design_list.selectedItems()
        selected_texts = [item.text() for item in selected_items]
        
        # Check if "All of the above" is selected
        if "All of the above" in selected_texts:
            # Select all design layers
            for i in range(design_list.count()):
                item = design_list.item(i)
                if item.text() != "All of the above" and item.text() != "No Design Layers Found":
                    item.setSelected(True)
            # Store all layers
            self.selected_worksheets_data[worksheet_name]["designs"] = all_design_layers.copy()
        else:
            # Store only selected layers (excluding the "All" option)
            selected_layers = [text for text in selected_texts if text != "All of the above"]
            self.selected_worksheets_data[worksheet_name]["designs"] = selected_layers

    def on_material_selection_changed(self, worksheet_name, material_list, all_material_layers):
        """Handle material layer selection with 'All' option logic."""
        if worksheet_name not in self.selected_worksheets_data:
            return
        
        selected_items = material_list.selectedItems()
        selected_texts = [item.text() for item in selected_items]
        
        # Check if "All of the above" is selected
        if "All of the above" in selected_texts:
            # Select all material layers
            for i in range(material_list.count()):
                item = material_list.item(i)
                if item.text() != "All of the above" and item.text() != "No Material Layers Found":
                    item.setSelected(True)
            # Store all layers
            self.selected_worksheets_data[worksheet_name]["materials"] = all_material_layers.copy()
        else:
            # Store only selected layers (excluding the "All" option)
            selected_layers = [text for text in selected_texts if text != "All of the above"]
            self.selected_worksheets_data[worksheet_name]["materials"] = selected_layers
                
    def on_layer_selection_changed(self, worksheet_name, layer_type):
        """Update selected layers data when user selects/deselects items."""
        if worksheet_name not in self.selected_worksheets_data:
            return
        
        if layer_type == "designs":
            selected_items = self.design_list.selectedItems()
            selected_layers = [item.text() for item in selected_items]
            self.selected_worksheets_data[worksheet_name]["designs"] = selected_layers
        elif layer_type == "materials":
            selected_items = self.material_list.selectedItems()
            selected_layers = [item.text() for item in selected_items]
            self.selected_worksheets_data[worksheet_name]["materials"] = selected_layers

    # ------------------------------------------------------------------
    # Page 2: Select Buddies (Multiple selection with checkboxes)
    # ------------------------------------------------------------------
    def init_page2(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 10, 20, 10)   # top margin = 0
        layout.setSpacing(10)                      # minimal spacing

        # Title
        title = QLabel("Select Buddies")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A148C; margin-bottom: 10px;")  # no margins
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setMaximumHeight(250)

        scroll_content = QWidget()
        buddies_layout = QVBoxLayout(scroll_content)
        buddies_layout.setSpacing(2)
        buddies_layout.setContentsMargins(10, 5, 10, 5)  # reduce vertical padding
        # No stretch added

        self.buddy_checkboxes = []
        for buddy in self.buddies_data:
            cb = QCheckBox(buddy["name"])
            cb.setStyleSheet("""
                QCheckBox {
                    spacing: 15px;
                    margin: 2px 0px;
                }
            """)
            cb.setProperty("buddy_data", buddy)
            cb.stateChanged.connect(self.on_buddy_toggled)
            buddies_layout.addWidget(cb)   # directly add, no insertWidget
            self.buddy_checkboxes.append(cb)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        back_btn = QPushButton("Back")
        back_btn.setObjectName("backBtn")
        back_btn.clicked.connect(lambda: self.go_to_page(0))
        btn_layout.addWidget(back_btn)

        self.next_btn2 = QPushButton("Next")
        self.next_btn2.setObjectName("nextBtn")
        self.next_btn2.setEnabled(False)
        self.next_btn2.clicked.connect(self.on_start_upload)
        btn_layout.addWidget(self.next_btn2)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.stacked_widget.addWidget(page)

    def on_buddy_toggled(self):
        selected = [cb.property("buddy_data") for cb in self.buddy_checkboxes if cb.isChecked()]
        self.selected_buddies = selected
        self.next_btn2.setEnabled(len(selected) > 0)

    # ------------------------------------------------------------------
    # Page 3: Uploading (with progress simulation)
    # ------------------------------------------------------------------
    def init_page3(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Uploading")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A148C; margin-bottom: 20px;")
        layout.addWidget(title)

        self.status_label = QLabel("Uploading...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #333; margin-top: 15px; margin-bottom: 20px;")
        layout.addWidget(self.status_label)

        # Remove the stretch and adjust button spacing
        self.done_btn = QPushButton("Done")
        self.done_btn.setObjectName("doneBtn")
        self.done_btn.clicked.connect(self.accept)
        self.done_btn.hide()
        layout.addWidget(self.done_btn, alignment=Qt.AlignCenter)

        self.stacked_widget.addWidget(page)

    def go_to_page(self, page_index):
        """Switch to specified page and resize dialog."""
        self.stacked_widget.setCurrentIndex(page_index)
        self.resize_for_page(page_index)
        # Re-center after resize
        self.center_on_screen()

    def center_on_screen(self):
        """Center the dialog on the screen."""
        # Get the screen geometry
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        
        # Calculate center position
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        
        # Move dialog to center
        self.move(x, y)

    def resize_for_page(self, page_index):
        """Auto-adjust dialog height based on page content."""
        current_width = self.width()
        if page_index == 2:  # Uploading page
            self.setMinimumSize(400, 250)
            self.resize(current_width, 300)
        elif page_index == 1:  # Buddies page
            self.setMinimumSize(600, 350)   # lower height
            self.resize(current_width, 350) # match content
        else:  # Worksheets page
            self.setMinimumSize(700, 600)
            self.resize(current_width, 600)
        self.center_on_screen()

    def on_start_upload(self):
        """Switch to page 3 and start upload via API."""
        self.stacked_widget.setCurrentIndex(2)
        self.resize_for_page(2)  # Auto-resize for uploading page
        
        self.status_label.setText("Preparing to share...")
        QApplication.processEvents()

        # Build shared_to payload
        shared_to_ids = []
        for buddy in self.selected_buddies:
            euh_id = buddy.get("buddy_euh_id")
            if euh_id:
                shared_to_ids.append(euh_id)

        from API import WorksheetAPI
        
        all_success = True
        
        # Process each selected worksheet
        for ws_name, ws_data in self.selected_worksheets_data.items():
            ws_id = getattr(self, 'worksheet_data_map', {}).get(ws_name)
            file_id = getattr(self, 'worksheet_file_id_map', {}).get(ws_name, 1)
            
            design_ids = []
            for d_name in ws_data.get("designs", []):
                d_id = getattr(self, 'design_id_map', {}).get(ws_name, {}).get(d_name)
                if d_id is not None: design_ids.append(d_id)
                
            material_ids = []
            for m_name in ws_data.get("materials", []):
                m_id = getattr(self, 'material_id_map', {}).get(ws_name, {}).get(m_name)
                if m_id is not None: material_ids.append(m_id)
                
            # If the user selects multiple, the API might only accept one, or an array.
            # Given the payload in the prompt has a single integer, we will pass the first one,
            # but if there are multiple, maybe comma-separated string? We will use the first integer to be safe as per prompt example.
            d_id_to_send = design_ids[0] if design_ids else None
            m_id_to_send = material_ids[0] if material_ids else None
            
            payload = {
              "shared_by": self.current_user_id,
              "shared_to": shared_to_ids,
              "worksheet_id": ws_id,
              "design_layer_id": d_id_to_send,
              "material_layer_id": m_id_to_send,
              "file_id": file_id,
              "shared_from_app": 1
            }
            
            self.status_label.setText(f"Sharing {ws_name}...")
            QApplication.processEvents()
            
            res = WorksheetAPI.share_file_to_buddy(payload)
            if res.get("success"):
                print("Successfully pushed:", payload)
            else:
                print("Failed to push:", payload, res)
                all_success = False

        if all_success:
            self.status_label.setText("Successfully uploaded!")
        else:
            self.status_label.setText("Upload finished with some errors.")
        self.done_btn.show()

    def get_selected_data(self):
        """Return the complete selected data for upload."""
        return {
            "worksheets": self.selected_worksheets_data,
            "buddies": self.selected_buddies
        }

# ========= Aniket Added on 03-05-2026 : For the simualtion satge configuration =======
# ===========================================================================================================================
# ** SIMULATION CONFIG DIALOG **
# ===========================================================================================================================
class SimulationConfigDialog(QDialog):
    def __init__(self, design_layers, material_layers, current_config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simulation Flow Process Configuration")
        self.setModal(True)
        self.setMinimumSize(650, 500)
        
        self.design_layers = ["None"] + design_layers
        self.material_layers = ["None"] + material_layers
        
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #f8f9ff, stop:1 #e8eaf6);
                border-radius: 12px;
            }
            QLabel#headerText {
                font-size: 16px;
                font-weight: bold;
                color: #1a237e;
                padding: 10px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QGroupBox {
                border: 2px solid #3f51b5;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #1a237e;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                background-color: #3f51b5;
                color: white;
                border-radius: 4px;
            }
            QComboBox {
                border: 1.5px solid #c5cae9;
                border-radius: 6px;
                padding: 6px;
                min-width: 140px;
                background: white;
            }
            QComboBox:focus {
                border: 2px solid #3f51b5;
            }
            QPushButton#addBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #4caf50, stop:1 #388e3c);
                color: white;
                padding: 8px 15px;
                border-radius: 18px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton#addBtn:hover {
                background: #43a047;
            }
            QPushButton#deleteBtn {
                background-color: #ffebee;
                color: #d32f2f;
                border: 1px solid #ffcdd2;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                min-width: 32px;
                min-height: 32px;
            }
            QPushButton#deleteBtn:hover {
                background-color: #d32f2f;
                color: white;
            }
            QPushButton#okBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #3f51b5, stop:1 #283593);
                color: white;
                padding: 10px 25px;
                border-radius: 20px;
                font-weight: bold;
                border: none;
            }
            QPushButton#cancelBtn {
                background-color: #eeeeee;
                color: #424242;
                padding: 10px 25px;
                border-radius: 20px;
                font-weight: bold;
                border: 1px solid #bdbdbd;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header Row
        header_layout = QHBoxLayout()
        header_label = QLabel("Simulation Stage Designer")
        header_label.setObjectName("headerText")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        self.add_btn = QPushButton("➕ Add New Stage")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(lambda: self.add_stage_row())
        header_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(header_layout)
        
        # --- Simulation Header Section ---
        name_layout = QHBoxLayout()
        name_label = QLabel("Name of the Simulation:")
        name_label.setStyleSheet("color: #1a237e; font-weight: bold;")
        self.simulation_name_input = QLineEdit()
        self.simulation_name_input.setPlaceholderText("Enter simulation name...")
        self.simulation_name_input.setStyleSheet("border: 1.5px solid #c5cae9; border-radius: 6px; padding: 6px; background: white;")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.simulation_name_input)
        main_layout.addLayout(name_layout)

        # --- Auto Simulation UI ---
        auto_sim_group = QGroupBox("Auto Simulation Control")
        auto_sim_group.setStyleSheet("""
            QGroupBox {
                border: 1.5px solid #c5cae9;
                border-radius: 8px;
                margin-top: 5px;
                padding-top: 10px;
                background-color: #f0f4ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                background-color: #3f51b5;
                color: white;
                border-radius: 3px;
            }
        """)
        auto_sim_layout = QHBoxLayout(auto_sim_group)
        self.auto_sim_checkbox = QCheckBox("Auto Simulation")
        self.auto_sim_checkbox.setStyleSheet("font-weight: bold; color: #1a237e;")
        
        self.timestamp_label = QLabel("Enter the Timestamp (sec):")
        self.timestamp_label.setStyleSheet("color: #1a237e; font-weight: 500;")
        self.timestamp_input = QLineEdit()
        self.timestamp_input.setPlaceholderText("e.g. 5")
        self.timestamp_input.setFixedWidth(80)
        self.timestamp_input.setStyleSheet("border: 1.5px solid #c5cae9; border-radius: 6px; padding: 4px; background: white;")
        
        auto_sim_layout.addWidget(self.auto_sim_checkbox)
        auto_sim_layout.addSpacing(20)
        auto_sim_layout.addWidget(self.timestamp_label)
        auto_sim_layout.addWidget(self.timestamp_input)
        auto_sim_layout.addStretch()
        
        # Hide timestamp fields initially
        self.timestamp_label.setVisible(False)
        self.timestamp_input.setVisible(False)
        
        # Connect toggle
        self.auto_sim_checkbox.toggled.connect(lambda checked: self.timestamp_label.setVisible(checked))
        self.auto_sim_checkbox.toggled.connect(lambda checked: self.timestamp_input.setVisible(checked))
        
        main_layout.addWidget(auto_sim_group)
        
        # Scroll Area for Stages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.stages_layout = QVBoxLayout(self.container)
        self.stages_layout.setAlignment(Qt.AlignTop)
        self.stages_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)
        
        self.stage_rows = []
        
        # Initial Load
        if current_config:
            # Load metadata
            metadata = current_config.get("metadata", {})
            self.simulation_name_input.setText(metadata.get("simulation_name", ""))
            is_auto = metadata.get("auto_simulation", False)
            self.auto_sim_checkbox.setChecked(is_auto)
            self.timestamp_input.setText(str(metadata.get("timestamp", "")))
            self.timestamp_label.setVisible(is_auto)
            self.timestamp_input.setVisible(is_auto)
            # Report checkbox will be handled below where it's created

            # Sort keys to maintain order, exclude metadata
            sorted_stages = sorted([(k, v) for k, v in current_config.items() if k != "metadata"], key=lambda x: int(x[0]))
            for stage_id, data in sorted_stages:
                self.add_stage_row(data)
        else:
            # Add one default stage if new
            self.add_stage_row()
            
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        
        # Report Checkbox on the left
        self.report_checkbox = QCheckBox("Report")
        self.report_checkbox.setStyleSheet("font-weight: bold; color: #1a237e;")
        if current_config:
            self.report_checkbox.setChecked(current_config.get("metadata", {}).get("report", False))
        btn_layout.addWidget(self.report_checkbox)
        
        btn_layout.addStretch()

        self.ok_btn = QPushButton("Save Configuration")
        self.ok_btn.setObjectName("okBtn")
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        main_layout.addLayout(btn_layout)

    def add_stage_row(self, data=None):
        stage_num = len(self.stage_rows) + 1
        
        group = QGroupBox(f"Stage {stage_num}")
        row_layout = QHBoxLayout(group)
        row_layout.setContentsMargins(15, 10, 15, 10)
        row_layout.setSpacing(15)
        
        name_vbox = QVBoxLayout()
        name_vbox.addWidget(QLabel("Stage Name:"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("e.g. Excavation")
        name_input.setStyleSheet("border: 1.5px solid #c5cae9; border-radius: 6px; padding: 6px; background: white;")
        name_vbox.addWidget(name_input)
        row_layout.addLayout(name_vbox)

        design_vbox = QVBoxLayout()
        design_vbox.addWidget(QLabel("Design Layer:"))
        design_combo = QComboBox()
        design_combo.addItems(self.design_layers)
        design_vbox.addWidget(design_combo)
        row_layout.addLayout(design_vbox)
        
        mat_vbox = QVBoxLayout()
        mat_vbox.addWidget(QLabel("Material Layer:"))
        mat_combo = QComboBox()
        mat_combo.addItems(self.material_layers)
        mat_vbox.addWidget(mat_combo)
        row_layout.addLayout(mat_vbox)

        # Excavation Checkbox
        excavation_check = QCheckBox("Excavation")
        excavation_check.setStyleSheet("font-weight: bold; color: #1a237e;")
        row_layout.addWidget(excavation_check)

        # Stage Timestamp
        time_vbox = QVBoxLayout()
        time_vbox.addWidget(QLabel("Time (sec):"))
        time_input = QLineEdit()
        time_input.setPlaceholderText("e.g. 5")
        time_input.setFixedWidth(60)
        time_input.setStyleSheet("border: 1.5px solid #c5cae9; border-radius: 6px; padding: 6px; background: white;")
        time_vbox.addWidget(time_input)
        row_layout.addLayout(time_vbox)

        # Delete Button
        del_btn = QPushButton("🗑")
        del_btn.setObjectName("deleteBtn")
        del_btn.setToolTip("Remove this stage")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda: self.remove_stage_row(group))
        
        row_layout.addStretch()
        row_layout.addWidget(del_btn)
        
        # Set values if provided
        if data:
            name_input.setText(data.get("stage_name", ""))
            d_idx = design_combo.findText(data.get("design_layer", "None"))
            if d_idx >= 0: design_combo.setCurrentIndex(d_idx)
            
            m_idx = mat_combo.findText(data.get("material_layer", "None"))
            if m_idx >= 0: mat_combo.setCurrentIndex(m_idx)
            
            excavation_check.setChecked(data.get("excavation", False))
            time_input.setText(str(data.get("timestamp", "")))
            
        self.stages_layout.addWidget(group)
        self.stage_rows.append((group, name_input, design_combo, mat_combo, excavation_check, time_input))
        
    def remove_stage_row(self, group):
        # Find and remove from list
        for i, (g, n, d, m, e_chk, t_in) in enumerate(self.stage_rows):
            if g == group:
                self.stage_rows.pop(i)
                break
        
        # Remove from UI
        group.setParent(None)
        group.deleteLater()
        
        # Renumber remaining stages
        for i, (g, n, d, m, e_chk, t_in) in enumerate(self.stage_rows, 1):
            g.setTitle(f"Stage {i}")

    def get_config(self):
        config = {
            "metadata": {
                "simulation_name": self.simulation_name_input.text(),
                "auto_simulation": self.auto_sim_checkbox.isChecked(),
                "timestamp": self.timestamp_input.text(),
                "report": self.report_checkbox.isChecked()
            }
        }
        for i, (group, n_input, d_combo, m_combo, e_chk, t_in) in enumerate(self.stage_rows, 1):
            config[str(i)] = {
                "stage_name": n_input.text(),
                "design_layer": d_combo.currentText(),
                "material_layer": m_combo.currentText(),
                "excavation": e_chk.isChecked(),
                "timestamp": t_in.text()
            }
        return config
    
# ===========================================================================================================================
#                 ** ClearLayerDialog for Erasing Data based on Layer and Chainage Range **
# ===========================================================================================================================
class ClearLayersDialog(QDialog):
    def __init__(self, material_layers, design_layers, parent=None, json_path=None):
        super().__init__(parent)

        self.setWindowTitle("Clear")
        # self.setMinimumWidth(520)

        self.material_layers = material_layers
        self.design_layers = design_layers
        self.selected_layers = []
        self.json_path = json_path
        self.design_base_path = r"C:\3D_Tool\user\100007\road\work - 1\designs"

        # ================= FONT =================
        self.setFont(QFont("Segoe UI", 10))

        # ================= MAIN LAYOUT =================
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        # ================= TITLE =================
        title = QLabel("Erase Data")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #4A148C;")
        main_layout.addWidget(title)

        # ================= LAYER TYPE =================
        type_box = QGroupBox("Layer Type")
        type_box.setStyleSheet(self.group_style())

        type_layout = QHBoxLayout()

        self.design_cb = QCheckBox("Design")
        self.material_cb = QCheckBox("Material")
        self.all_cb = QCheckBox("All")

        type_layout.addWidget(self.design_cb)
        type_layout.addWidget(self.material_cb)
        type_layout.addWidget(self.all_cb)

        type_box.setLayout(type_layout)
        main_layout.addWidget(type_box)

        # ================= CHAINAGE =================
        chainage_box = QGroupBox("Chainage Range")
        chainage_box.setStyleSheet(self.group_style())

        grid = QGridLayout()
        grid.setSpacing(10)

        self.from_km = QLineEdit()
        self.to_km = QLineEdit()
        self.from_chainage = QLineEdit()
        self.to_chainage = QLineEdit()

        for field in [self.from_km, self.to_km, self.from_chainage, self.to_chainage]:
            field.setMinimumHeight(32)
            field.setStyleSheet(self.input_style())

        grid.addWidget(QLabel("From KM"), 0, 0)
        grid.addWidget(self.from_km, 0, 1)

        grid.addWidget(QLabel("To KM"), 1, 0)
        grid.addWidget(self.to_km, 1, 1)

        grid.addWidget(QLabel("From Chainage"), 0, 2)
        grid.addWidget(self.from_chainage, 0, 3)

        grid.addWidget(QLabel("To Chainage"), 1, 2)
        grid.addWidget(self.to_chainage, 1, 3)

        chainage_box.setLayout(grid)
        main_layout.addWidget(chainage_box)

        # ================= VERIFY =================
        verify_layout = QHBoxLayout()
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet(self.button_style())

        verify_layout.addStretch()
        verify_layout.addWidget(self.verify_btn)
        verify_layout.addStretch()

        main_layout.addLayout(verify_layout)

        # ================= LAYER BOX =================
        self.layer_box = QGroupBox("Select Layer")
        self.layer_box.setStyleSheet(self.group_style())

        self.layer_layout = QVBoxLayout()
        self.layer_layout.setSpacing(6)

        self.layer_box.setLayout(self.layer_layout)
        main_layout.addWidget(self.layer_box)

        # ================= FOOTER =================
        footer = QHBoxLayout()

        self.erase_btn = QPushButton("Erase")
        self.erase_btn.clicked.connect(self.erase_selected_data)
        self.cancel_btn = QPushButton("Cancel")

        self.erase_btn.setStyleSheet(self.button_style())
        self.cancel_btn.setStyleSheet(self.cancel_style())

        footer.addStretch()
        footer.addWidget(self.erase_btn)
        footer.addWidget(self.cancel_btn)

        main_layout.addLayout(footer)

        self.setLayout(main_layout)

        # DESIGN
        self.design_cb.toggled.connect(lambda checked: (
            self.material_cb.blockSignals(True),
            self.all_cb.blockSignals(True),

            self.material_cb.setChecked(False),
            self.all_cb.setChecked(False),

            self.material_cb.blockSignals(False),
            self.all_cb.blockSignals(False),

            # self.reset_verify_button(),

            # setattr(self, "loaded_json", None),
            self.clear_layout(),

            self.show_design_layers()
        ) if checked else None)


        # MATERIAL
        self.material_cb.toggled.connect(lambda checked: (
            self.design_cb.blockSignals(True),
            self.all_cb.blockSignals(True),

            self.design_cb.setChecked(False),
            self.all_cb.setChecked(False),

            self.design_cb.blockSignals(False),
            self.all_cb.blockSignals(False),

            self.reset_verify_button(),

            self.clear_layout(),

            self.show_material_layers()
        ) if checked else None)


        # ALL
        self.all_cb.toggled.connect(lambda checked: (
            self.design_cb.blockSignals(True),
            self.material_cb.blockSignals(True),

            self.design_cb.setChecked(checked),
            self.material_cb.setChecked(checked),

            self.design_cb.blockSignals(False),
            self.material_cb.blockSignals(False),

            self.reset_verify_button(),
            self.clear_layout(),
        ) if True else None)

        self.erase_btn.clicked.connect(self.collect_selection)
        self.cancel_btn.clicked.connect(self.reject)

        self.verify_btn.clicked.connect(self.verify_range)

    # ================= STYLES =================
    def group_style(self):
        return """
        QGroupBox {
            border: 2px solid #9C27B0;
            border-radius: 10px;
            padding: 10px;
            font-weight: bold;
            color: #6A1B9A;
        }
        """

    def input_style(self):
        return """
        QLineEdit {
            background-color: #F3E5F5;
            border: 2px solid #9C27B0;
            border-radius: 8px;
            padding: 6px;
        }
        """

    def button_style(self):
        return """
        QPushButton {
            background-color: #9C27B0;
            color: white;
            border-radius: 8px;
            padding: 6px 15px;
        }
        QPushButton:hover {
            background-color: #7B1FA2;
        }
        """

    def cancel_style(self):
        return """
        QPushButton {
            background-color: #CE93D8;
            color: black;
            border-radius: 8px;
            padding: 6px 15px;
        }
        """
    # ================= HELPERS =================

    def clear_layout(self):
        while self.layer_layout.count():
            item = self.layer_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # ================= SHOW DESIGN =================
    def show_design_layers(self):

        if not hasattr(self, "loaded_json"):
            return

        self.clear_layout()

        design = self.loaded_json.get("design", {})

        self.layer_box.setTitle("Select Baseline")

        # FIXED CHECK (None check, not truthy check)
        if design.get("surface_baseline") is not None:
            self.layer_layout.addWidget(QCheckBox("Surface Baseline"))

        if design.get("construction_baseline") is not None:
            self.layer_layout.addWidget(QCheckBox("Construction Baseline"))

        if design.get("road_surface_baseline") is not None:
            self.layer_layout.addWidget(QCheckBox("Road Surface Baseline"))

        if design.get("deck_line") is not None:
            self.layer_layout.addWidget(QCheckBox("Deck Line"))

        if design.get("projection_line") is not None:
            self.layer_layout.addWidget(QCheckBox("Projection Line"))

    # ================= SHOW MATERIAL =================
    def show_material_layers(self):
        if not hasattr(self, "loaded_json"):
            return

        self.clear_layout()
        self.layer_box.setTitle("Select Material Layers")

        materials = self.loaded_json.get("materials", [])

        if not materials:
            return

        # Add checkboxes
        for mat in materials:
            name = mat.get("material_line_folder")
            if name:
                checkbox = QCheckBox(name)
                self.layer_layout.addWidget(checkbox)


    def _show_all_layers_split_view(self, from_chainage, to_chainage):
        self.clear_layout()
        self.layer_box.setTitle("All Layers — Select to Erase")

        # ── DESIGN SECTION ──
        design_header = QLabel("📐  Design Layers")
        design_header.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #4A148C;
                background-color: #E1BEE7;
                padding: 4px 8px;
                border-radius: 6px;
            }
        """)
        self.layer_layout.addWidget(design_header)

        if hasattr(self, "loaded_json"):
            design = self.loaded_json.get("design", {})

            design_map = {
                "surface_baseline":      "Surface Baseline",
                "construction_baseline": "Construction Baseline",
                "road_surface_baseline": "Road Surface Baseline",
                "deck_line":             "Deck Line",
                "projection_line":       "Projection Line",
            }

            design_found = False
            for key, label in design_map.items():
                if design.get(key) is not None:
                    cb = QCheckBox(label)
                    cb.setChecked(True)
                    cb.setStyleSheet("padding-left: 10px;")
                    self.layer_layout.addWidget(cb)
                    design_found = True

            if not design_found:
                lbl = QLabel("  (No design layers found)")
                lbl.setStyleSheet("color: gray; padding-left: 10px;")
                self.layer_layout.addWidget(lbl)

        # ── SEPARATOR ──
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #9C27B0; margin: 6px 0;")
        self.layer_layout.addWidget(separator)

        # ── MATERIAL SECTION ──
        material_header = QLabel("🧱  Material Layers")
        material_header.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #4A148C;
                background-color: #E1BEE7;
                padding: 4px 8px;
                border-radius: 6px;
            }
        """)
        self.layer_layout.addWidget(material_header)

        parent = self.parent()
        worksheet_path = os.path.join(
            parent.WORKSHEETS_BASE_DIR,
            parent.current_worksheet_name
        )
        material_json_path = os.path.join(
            worksheet_path, "construction", "Material",
            "material_construction_config.json"
        )

        material_found = False

        if os.path.exists(material_json_path):
            with open(material_json_path, "r") as f:
                mat_data = json.load(f)

            for mat in mat_data.get("materials", []):
                name     = mat.get("material_line_folder")
                mat_from = float(mat.get("overall_from_chainage", {}).get("chainage_m", 0))
                mat_to   = float(mat.get("overall_to_chainage",   {}).get("chainage_m", 0))

                if not (from_chainage >= mat_from and to_chainage <= mat_to):
                    continue

                cb = QCheckBox(name)
                cb.setChecked(True)
                cb.setStyleSheet("padding-left: 10px;")
                self.layer_layout.addWidget(cb)
                material_found = True

        if not material_found:
            lbl = QLabel("  (No material layers found in this range)")
            lbl.setStyleSheet("color: gray; padding-left: 10px;")
            self.layer_layout.addWidget(lbl)

# ================================================================================================
    def load_material_layers_with_filter(self, json_file, from_chainage, to_chainage):
        import json, os

        print("===== MATERIAL VERIFY START =====")

        # user_chainage = float(user_chainage)
        from_chainage = float(from_chainage)
        to_chainage = float(to_chainage)

        # print("User Chainage:", user_chainage)

        if not os.path.exists(json_file):
            print("JSON NOT FOUND:", json_file)
            return

        print("Opening JSON:", json_file)

        with open(json_file, "r") as f:
            data = json.load(f)

        materials = data.get("materials", [])

        # UI clear
        self.clear_layout()
        self.layer_box.setTitle("Select Material Layers")

        valid_found = False

        for mat in materials:

            name = mat.get("material_line_folder")
            from_ch = mat["overall_from_chainage"]["chainage_m"]
            to_ch = mat["overall_to_chainage"]["chainage_m"]

            print("Checking:", name, "Range:", from_ch, to_ch)

            if not (from_chainage >= from_ch and to_chainage <= to_ch):
                print("Skipped:", name)
                continue

            print("Added:", name)

            checkbox = QCheckBox(name)
            self.layer_layout.addWidget(checkbox)

            valid_found = True   

        return valid_found

    # ================= ALL =================
    def select_all_layers(self):
        if not self.all_cb.isChecked():
            self.clear_layout()
    # ================= COLLECT =================

    def collect_selection(self):
        self.selected_layers = []

        for i in range(self.layer_layout.count()):
            cb = self.layer_layout.itemAt(i).widget()
            if isinstance(cb, QCheckBox) and cb.isChecked():
                self.selected_layers.append(cb.text())

        self.accept()

# =============================Verify Range Function ========================================
    def verify_range(self):

        if not (self.design_cb.isChecked() or self.material_cb.isChecked() or self.all_cb.isChecked()):
            QMessageBox.warning(self, "Warning", "Please Select Layer")
            return

        try:
            # ================= INPUT =================
            from_km = float(self.from_km.text())
            to_km = float(self.to_km.text())
            from_chainage = float(self.from_chainage.text())
            to_chainage = float(self.to_chainage.text())

            # ================= GET WORKSHEET PATH =================
            parent = self.parent()

            if not parent or not hasattr(parent, "current_worksheet_name"):
                QMessageBox.warning(self, "Error", "Worksheet not active")
                return

            worksheet_path = os.path.join(
                parent.WORKSHEETS_BASE_DIR,
                parent.current_worksheet_name
            )

            designs_path = os.path.join(worksheet_path, "designs")
            material_path = os.path.join(worksheet_path, "construction")

            # is_material = self.material_cb.isChecked()
            is_material = self.material_cb.isChecked() and not self.all_cb.isChecked()

            #  FIX: dynamic base_path (no hardcoding)
            if is_material:
                if not os.path.exists(material_path):
                    QMessageBox.warning(self, "Error", "Material folder not found")
                    return
                base_path = material_path
            else:
                if not os.path.exists(designs_path):
                    QMessageBox.warning(self, "Error", "Design folder not found")
                    return
                base_path = designs_path

            found = False

            # ================= LOOP ALL LAYERS =================
            for layer in os.listdir(base_path):
                layer_path = os.path.join(base_path, layer)

                if not os.path.isdir(layer_path):
                    continue

                # ================= MATERIAL =================
                if is_material:

                    #  FIX: removed wrong re-join of path
                    json_file = os.path.join(layer_path, "material_construction_config.json")

                    if not os.path.exists(json_file):
                        continue

                    print("MATERIAL JSON FOUND:", json_file)
                    self.current_json_path = json_file

                    is_valid = self.load_material_layers_with_filter(
                        json_file,
                        from_chainage,
                        to_chainage
                    )

                    found = is_valid
                    break

                # ================= DESIGN =================
                else:
                    json_file = os.path.join(layer_path, "design_construction_config.json")

                if not os.path.exists(json_file):
                    continue

                try:
                    with open(json_file, "r") as f:
                        content = f.read().strip()

                        if not content:
                            continue

                        data = json.loads(content)
                        self.current_json_path = json_file

                        if not isinstance(data, dict):
                            continue

                except Exception as e:
                    print("JSON ERROR:", json_file, str(e))
                    continue

                # ================= GET BASELINES =================
                surface = data.get("design", {}).get("surface_baseline", {})
                construction = data.get("design", {}).get("construction_baseline", {})
                road_surface = data.get("design", {}).get("road_surface_baseline", {})

                baselines = [surface, construction, road_surface]

                for base in baselines:

                    polylines = base.get("polylines")
                    if not isinstance(polylines, list):
                        continue

                    for poly in polylines:

                        points = poly.get("points")
                        if not isinstance(points, list):
                            continue

                        all_kms = set()

                        for temp_pt in points:
                            try:
                                chainage_str = temp_pt.get("chainage_str", "")
                                if "+" not in chainage_str:
                                    continue

                                km_part, _ = chainage_str.split("+")
                                km_val = float(km_part)

                                all_kms.add(km_val)

                            except:
                                continue

                        if from_km not in all_kms or to_km not in all_kms:
                            continue

                        for pt in points:

                            try:
                                chainage_str = pt.get("chainage_str", "")

                                if "+" not in chainage_str:
                                    continue

                                km_part, ch_part = chainage_str.split("+")
                                km_val = float(km_part)
                                ch_val = float(ch_part)

                                chainages = []

                                for pt in points:
                                    try:
                                        chainage_str = pt.get("chainage_str", "")
                                        if "+" not in chainage_str:
                                            continue

                                        km_part, ch_part = chainage_str.split("+")
                                        km_val = float(km_part)
                                        ch_val = float(ch_part)

                                        if km_val == from_km:
                                            chainages.append(ch_val)

                                    except:
                                        continue

                                if chainages:
                                    min_ch = min(chainages)
                                    max_ch = max(chainages)

                                    if (
                                        from_chainage >= min_ch and
                                        to_chainage <= max_ch
                                    ):
                                        found = True
                                        self.loaded_json = data
                                        print("JSON LOADED ")
                                        break

                            except:
                                continue

                        if found:
                            self.loaded_json = data
                            break
                    if found:
                        break
                if found:
                    break

            # ================= RESULT =================
            if found:
                self.verify_btn.setText("Verified")
                self.verify_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border-radius: 8px;
                        padding: 6px 15px;
                    font-weight: bold;
                }
            """)

                if self.all_cb.isChecked():
                    # self.select_all_layers()
                    self._show_all_layers_split_view(from_chainage, to_chainage)

                elif self.design_cb.isChecked():
                    self.show_design_layers()
                    

                elif self.material_cb.isChecked():
                    pass

                # elif self.all_cb.isChecked():
                #     # self.select_all_layers()
                #     self._show_all_layers_split_view(from_chainage, to_chainage)

            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Data not found. Please enter a valid range."
                )

        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def reset_verify_button(self):
        self.verify_btn.setText("Verify")
        self.verify_btn.setStyleSheet("""
        QPushButton {
            background-color: #9C27B0;
            color: white;
            border-radius: 8px;
            padding: 6px 15px;
        }
        QPushButton:hover {
            background-color: #7B1FA2;
        }
        """)

        if hasattr(self, "loaded_json"):
            del self.loaded_json
# ================================== Original Erase Function ===============================
    def erase_selected_data(self):

        try:
            if not self.material_cb.isChecked():    
                if not hasattr(self, "loaded_json"):
                    QMessageBox.warning(self, "Error", "Please verify first")
                    return
            

            from_km = float(self.from_km.text())
            to_km = float(self.to_km.text())
            from_chainage = float(self.from_chainage.text())
            to_chainage = float(self.to_chainage.text())

            #  selected baselines
            selected = []
            for i in range(self.layer_layout.count()):
                cb = self.layer_layout.itemAt(i).widget()
                if isinstance(cb, QCheckBox) and cb.isChecked():
                    selected.append(cb.text())

            if not selected:
                QMessageBox.warning(self, "Error", "Select at least one baseline")
                return
            
        # ======================================= All =========================================
            if self.all_cb.isChecked():

                design_labels = [
                    "Surface Baseline", "Construction Baseline",
                    "Road Surface Baseline", "Deck Line", "Projection Line"
                ]

                design_selected  = [s for s in selected if s in design_labels]
                material_selected = [s for s in selected if s not in design_labels]

                print("ALL MODE → Design:", design_selected)
                print("ALL MODE → Material:", material_selected)

                # ── DESIGN ERASE ──
                # ── DESIGN ERASE ──
                if design_selected:
                    data = self.loaded_json
                    design = data.get("design", {})

                    key_map = {
                        "Surface Baseline":      "surface_baseline",
                        "Construction Baseline": "construction_baseline",
                        "Road Surface Baseline": "road_surface_baseline",
                    }

                    for name in design_selected:
                        key = key_map.get(name)
                        if not key:
                            continue

                        base = design.get(key)
                        if base is None:
                            continue

                        new_polylines = []

                        for poly in base.get("polylines", []):
                            points = poly.get("points", [])
                            current_segment = []

        # =================================== Only Erase 20 Interval ================================
                            for pt in points:
                                try:
                                    ch_str = pt.get("chainage_str", "")
                                    if "+" not in ch_str:
                                        current_segment.append(pt)
                                        continue

                                    km, ch = ch_str.split("+")
                                    val_local = float(ch)

                                    if from_chainage <= val_local <= to_chainage:


                                        if current_segment and current_segment[-1].get("chainage_m") != to_chainage:

                                            last_pt = current_segment[-1]
                                            last_ch = float(last_pt.get("chainage_m", 0))
                                            curr_ch = float(pt.get("chainage_m", val_local))

                                            if abs(curr_ch - last_ch) > 0.001:
                                                t = (from_chainage - last_ch) / (curr_ch - last_ch)
                                            else:
                                                t = 0.0

                                            last_wc = last_pt.get("world_coordinates", [0, 0, 0])
                                            curr_wc = pt.get("world_coordinates", [0, 0, 0])

                                            interp_wc = [
                                                last_wc[0] + t * (curr_wc[0] - last_wc[0]),
                                                last_wc[1] + t * (curr_wc[1] - last_wc[1]),
                                                last_wc[2] + t * (curr_wc[2] - last_wc[2]),
                                            ]

                                            interp_rel_elev = (
                                                last_pt.get("relative_elevation_m", 0)
                                                + t * (pt.get("relative_elevation_m", 0) - last_pt.get("relative_elevation_m", 0))
                                            )

                                            cut_point = dict(last_pt)
                                            cut_point["chainage_m"] = from_chainage
                                            cut_point["chainage_str"] = f"{int(from_km)}+{from_chainage:.3f}"
                                            cut_point["world_coordinates"] = interp_wc
                                            cut_point["relative_elevation_m"] = interp_rel_elev

                                            current_segment.append(cut_point)

                                            if len(current_segment) >= 2:
                                                new_polylines.append({"points": current_segment})

                                        cut_point2 = dict(pt)
                                        cut_point2["chainage_m"] = to_chainage
                                        cut_point2["chainage_str"] = f"{int(to_km)}+{to_chainage:.3f}"

                                        current_segment = [cut_point2]
                                        continue

                                    current_segment.append(pt)

                                except:
                                    current_segment.append(pt)

                            if len(current_segment) >= 2:
                                new_polylines.append({"points": current_segment})

                        base["polylines"] = new_polylines

                        if not any(p.get("points") for p in base.get("polylines", [])):
                            design[key] = None

                    # ── DESIGN JSON SAVE ──
                    parent = self.parent()
                    worksheet_path = os.path.join(
                        parent.WORKSHEETS_BASE_DIR,
                        parent.current_worksheet_name
                    )
                    designs_path = os.path.join(worksheet_path, "designs")

                    for layer_folder in os.listdir(designs_path):
                        layer_path = os.path.join(designs_path, layer_folder)
                        json_file = os.path.join(layer_path, "design_construction_config.json")
                        if os.path.exists(json_file):
                            with open(json_file, "w") as f:
                                json.dump(data, f, indent=4)

                # ── MATERIAL ERASE ──
                if material_selected:
                    parent = self.parent()
                    worksheet_path = os.path.join(
                        parent.WORKSHEETS_BASE_DIR,
                        parent.current_worksheet_name
                    )
                    material_base_path = os.path.join(worksheet_path, "construction")

                    for layer_folder in os.listdir(material_base_path):
                        layer_path = os.path.join(material_base_path, layer_folder)
                        json_file = os.path.join(layer_path, "material_construction_config.json")

                        if not os.path.exists(json_file):
                            continue

                        with open(json_file, "r") as f:
                            mat_data = json.load(f)

                        changed = False

                        for mat in mat_data.get("materials", []):
                            mat_name = mat.get("material_line_folder")

                            if mat_name not in material_selected:
                                continue


                            new_segments = []
                            erase_from = from_chainage
                            erase_to = to_chainage

                            for seg in mat.get("segments", []):
                                seg_from = float(seg.get("from_chainage_m", 0))
                                seg_to   = float(seg.get("to_chainage_m", 0))

                                print(f"Segment: {seg_from} → {seg_to}")
                                print(f"Erase range: {erase_from} → {erase_to}")

                                # Check for overlap (ANY PART of segment inside erase range)
                                if not (seg_to <= erase_from or seg_from >= erase_to):
                                    # Overlap detected - remove the segment
                                    print(f"REMOVED → {mat_name}: {seg_from}→{seg_to}")
                                    changed = True
                                    continue
                                else:
                                    # No overlap - keep the segment
                                    print(f"KEPT → {mat_name}: {seg_from}→{seg_to}")
                                    new_segments.append(seg)

                            mat["segments"] = new_segments
                            mat["total_segments"] = len(new_segments)

                        if changed:
                            with open(json_file, "w") as f:
                                json.dump(mat_data, f, indent=4)

            #     # ── REFRESH VIEW ──
                parent = self.parent()
                renderer = parent.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()

                for attr in ["surface_actor", "road_surface_actor", "construction_surface_actor"]:
                    if hasattr(parent, attr):
                        renderer.RemoveActor(getattr(parent, attr))
                        delattr(parent, attr)

                if hasattr(parent, "material_actors_by_name"):
                    for actors in parent.material_actors_by_name.values():
                        for actor in actors:
                            renderer.RemoveActor(actor)
                    parent.material_actors_by_name.clear()

                parent.vtk_widget.GetRenderWindow().Render()

                QMessageBox.information(self, "Success", "All selected layers erased successfully")
                return

        # ======================================================================================
            #  CHECK IF CONSTRUCTION BASELINE IS SELECTED
            if "Construction Baseline" in selected:

                reply = QMessageBox.question(
                    self,
                    "Confirm Deletion",
                    "It may affect material lines. Are you sure you want to erase construction line data?",
                    QMessageBox.Yes | QMessageBox.Cancel,
                    QMessageBox.Cancel
                )

                if reply != QMessageBox.Yes:
                    return  #  User cancelled → stop execution
                
            # ================= MATERIAL DELETE LOGIC =================
            if self.material_cb.isChecked():

                json_file = self.current_json_path

                with open(json_file, "r") as f:
                    data = json.load(f)

                materials = data.get("materials", [])

                selected_layer = selected[0]
                # ================== Dependency function Calls ==================
                #  GET FULL DEPENDENCY CHAIN
                dependent_layers = self.get_full_dependency_chain(selected_layer, materials)

                print("Selected:", selected_layer)
                print("Affected:", dependent_layers)
                # ==================================================================
                # FIND DEPENDENTS
                dependents = []

                for mat in materials:
                    ref = mat.get("reference_baseline")

                    if isinstance(ref, list):
                        if selected_layer in ref:
                            dependents.append(mat.get("material_line_folder"))

                    elif isinstance(ref, str):
                        if ref == selected_layer:
                            dependents.append(mat.get("material_line_folder"))
                # --------------------------------------------------------------------
                # FIND DEPENDENTS (keep this as is)
                # dependents = []

                # for mat in materials:
                #     ref = mat.get("reference_baseline")

                #     if isinstance(ref, list):
                #         if selected_layer in ref:
                #             dependents.append(mat.get("material_line_folder"))

                #     elif isinstance(ref, str):
                #         if ref == selected_layer:
                #             dependents.append(mat.get("material_line_folder"))
                # =====================================================================
                # MESSAGE
                if dependents:
                    msg = f"It may affect the {', '.join(dependents)} material layer. Are you sure you want to erase the {selected_layer} Layer?"
                else:
                    msg = f"Are you sure you want to erase the {selected_layer} Layer?"

                reply = QMessageBox.question(
                    self,
                    "Confirm Delete",
                    msg,
                    QMessageBox.Yes | QMessageBox.Cancel
                )

                if reply != QMessageBox.Yes:
                    return

                # ================= PARTIAL SEGMENT DELETE =================
                erase_from = from_chainage
                erase_to = to_chainage

                print("\n===== PARTIAL ERASE START =====")
                print("Selected:", selected_layer)
                print("Range:", erase_from, "→", erase_to)

                #CREATE FULL ERASE LIST (PARENT + DEPENDENCIES)
                layers_to_erase = [selected_layer] + dependent_layers

                print("DEBUG → Full erase chain:", layers_to_erase)

                for mat in materials:

                    mat_name = mat.get("material_line_folder")

                    # ✔ APPLY ONLY TO REQUIRED LAYERS
                    if mat_name not in layers_to_erase:
                        continue
                # ======================================================================
                    new_segments = []

                    for seg in mat.get("segments", []):

                        seg_from = float(seg.get("from_chainage_m", 0))
                        seg_to = float(seg.get("to_chainage_m", 0))

                        print(f"Segment: {seg_from} → {seg_to}")

                        # REMOVE ONLY MATCHING SEGMENT
                        # if abs(seg_from - erase_from) < 0.001 and abs(seg_to - erase_to) < 0.001:
                        #     print("REMOVED ✔")
                        #     continue

                        # if seg_from >= erase_from and seg_to <= erase_to:
                        #     print("REMOVED ✔")
                        #     continue

                        # print("KEPT ✔")
                        # new_segments.append(seg)

                        # Check if segment overlaps with erase range
                        if not (seg_to <= erase_from or seg_from >= erase_to):
                            # Overlap detected - remove the segment
                            print(f"REMOVED ✔ (overlaps {erase_from}→{erase_to})")
                            continue
                        else:
                            # No overlap - keep the segment
                            print(f"KEPT ✔ (no overlap)")
                            new_segments.append(seg)

                # ================================================================================
                    mat["segments"] = new_segments

                    #  FIX COUNT
                    mat["total_segments"] = len(new_segments)

                print("===== PARTIAL ERASE END =====\n")

                with open(json_file, "w") as f:
                    json.dump(data, f, indent=4)

                print(f"{selected_layer} deleted")

                # REFRESH VIEW
                parent = self.parent()

                renderer = parent.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()
                #  REMOVE OLD MATERIAL ACTORS PROPERLY
                if hasattr(parent, "material_actors_by_name"):
                    for actors in parent.material_actors_by_name.values():
                        for actor in actors:
                            renderer.RemoveActor(actor)

                    parent.material_actors_by_name.clear()

                # renderer.Render()
                renderer.GetRenderWindow().Render()
                # renderer.Modified()
                parent.vtk_widget.update()

                print("Old material actors removed")

                #  NOW RELOAD FROM UPDATED JSON
                parent.load_json_files_to_3d_pointcloud(
                    os.path.dirname(json_file)
                )
                parent.vtk_widget.GetRenderWindow().Render()
                QMessageBox.information(self, "Success", "Material deleted successfully")

                return
# =======================================================================================

            data = self.loaded_json
            design = data.get("design", {})

            for name in selected:

                if name == "Surface Baseline":
                    key = "surface_baseline"

                elif name == "Construction Baseline":
                    key = "construction_baseline"

                elif name == "Road Surface Baseline":
                    key = "road_surface_baseline"

                else:
                    continue

                base = design.get(key)

                if base is None:
                    continue


                new_polylines = []

                for poly in base.get("polylines", []):
                    points = poly.get("points", [])

                    current_segment = []

                    for pt in points:
                        try:
                            ch_str = pt.get("chainage_str", "")
                            if "+" not in ch_str:
                                current_segment.append(pt)
                                continue

                            km, ch = ch_str.split("+")
                            val = float(km) * 1000 + float(ch)
                            val_local = float(ch)                                                   #  chainage part (40, 60)

                            from_val = from_km * 1000 + from_chainage
                            to_val = to_km * 1000 + to_chainage


                            if from_chainage <= val_local <= to_chainage:

                                if current_segment and current_segment[-1].get("chainage_m") != to_chainage:

                                    last_pt = current_segment[-1]
                                    last_ch = float(last_pt.get("chainage_m", 0))
                                    curr_ch = float(pt.get("chainage_m", val_local))

                                    # ── Interpolate world_coordinates at exact from_chainage ──
                                    if abs(curr_ch - last_ch) > 0.001:
                                        t = (from_chainage - last_ch) / (curr_ch - last_ch)
                                    else:
                                        t = 0.0

                                    last_wc = last_pt.get("world_coordinates", [0, 0, 0])
                                    curr_wc = pt.get("world_coordinates", [0, 0, 0])

                                    interp_wc = [
                                        last_wc[0] + t * (curr_wc[0] - last_wc[0]),
                                        last_wc[1] + t * (curr_wc[1] - last_wc[1]),
                                        last_wc[2] + t * (curr_wc[2] - last_wc[2]),
                                    ]

                                    interp_rel_elev = (
                                        last_pt.get("relative_elevation_m", 0)
                                        + t * (pt.get("relative_elevation_m", 0) - last_pt.get("relative_elevation_m", 0))
                                    )

                                    cut_point = dict(last_pt)
                                    cut_point["chainage_m"] = from_chainage
                                    cut_point["chainage_str"] = f"{int(from_km)}+{from_chainage:.3f}"
                                    cut_point["world_coordinates"] = interp_wc
                                    cut_point["relative_elevation_m"] = interp_rel_elev

                                    current_segment.append(cut_point)

                                    if len(current_segment) >= 2:
                                        new_polylines.append({"points": current_segment})

                                # Resume segment after the erase zone ends
                                cut_point2 = dict(pt)
                                cut_point2["chainage_m"] = to_chainage
                                cut_point2["chainage_str"] = f"{int(to_km)}+{to_chainage:.3f}"


                                current_segment = [cut_point2]
                                continue
                            # ==================================================

                            #  NORMAL POINT ADD
                            current_segment.append(pt)

                        except:
                            current_segment.append(pt)

                    #LAST SEGMENT ADD
                    if len(current_segment) >= 2:
                        new_polylines.append({
                            "points": current_segment
                        })

                
                base["polylines"] = new_polylines

                QMessageBox.information(
                    self,
                    "Success",
                    f"{name} erased successfully"
                )

                all_empty = True
                for poly in base.get("polylines", []):
                    if poly.get("points"):
                        all_empty = False
                        break

                if all_empty:
                    design[key] = None
            # ================= SAVE FILE =================
            parent = self.parent()

            worksheet_path = os.path.join(
                parent.WORKSHEETS_BASE_DIR,
                parent.current_worksheet_name
            )

            designs_path = os.path.join(worksheet_path, "designs")

            for layer in os.listdir(designs_path):
                layer_path = os.path.join(designs_path, layer)
                json_file = os.path.join(layer_path, "design_construction_config.json")

                if os.path.exists(json_file):
                    with open(json_file, "w") as f:
                        json.dump(data, f, indent=4)

            with open(self.current_json_path, "w") as f:
                json.dump(data, f, indent=4)


            if "Construction Baseline" in selected:                                                     #Depnedency check for construction baseline erase
                self._erase_construction_dependents(from_chainage, to_chainage)

            parent = self.parent()
            renderer = parent.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()

            # REMOVE OLD SURFACE ACTORS
            for attr in ["surface_actor", "road_surface_actor", "construction_surface_actor"]:
                if hasattr(parent, attr):
                    renderer.RemoveActor(getattr(parent, attr))
                    delattr(parent, attr)

            print("DEBUG → Reloading JSON after erase")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))



# ============================== Design Layer as well as Material Layer =========================

    def get_full_dependency_chain(self, selected_layer, materials):

        mapping = {
            "Construction Baseline": "Construction",
            "Surface Baseline": "Surface",
            "Road Surface Baseline": "Road Surface"
        }

        base_layer = mapping.get(selected_layer, selected_layer)

        chain = []

        def find_children(layer):
            for mat in materials:
                ref = mat.get("reference_baseline")

                if isinstance(ref, list):
                    if layer in ref:
                        name = mat.get("material_line_folder")
                        if name not in chain:
                            chain.append(name)
                            find_children(name)

                elif isinstance(ref, str):
                    if ref == layer:
                        name = mat.get("material_line_folder")
                        if name not in chain:
                            chain.append(name)
                            find_children(name)

        find_children(base_layer)
        return chain


    def _erase_construction_dependents(self, from_chainage, to_chainage):

        parent = self.parent()

        worksheet_path = os.path.join(
            parent.WORKSHEETS_BASE_DIR,
            parent.current_worksheet_name
        )

        # ── SAHI PATH ──
        material_json_path = os.path.join(
            worksheet_path,
            "construction",
            "Material",
            "material_construction_config.json"
        )

        print(f"[Chain] Material JSON path: {material_json_path}")
        print(f"[Chain] Exists: {os.path.exists(material_json_path)}")

        if not os.path.exists(material_json_path):
            print("[Chain] File nahi mili")
            return

        with open(material_json_path, "r") as f:
            data = json.load(f)

        materials = data.get("materials", [])

        print(f"[Chain] Materials found: {[m.get('material_line_folder') for m in materials]}")

        # ── CHAIN BUILD ──
        chain = self.get_full_dependency_chain("Construction Baseline", materials)
        print(f"[Chain] Dependency chain: {chain}")

        if not chain:
            print("[Chain] Koi dependent nahi mila")
            return

        # ── ERASE ──
        self._erase_material_segments_range(materials, chain, from_chainage, to_chainage)

        with open(material_json_path, "w") as f:
            json.dump(data, f, indent=4)

        print("[Chain] Material JSON saved")

        # ── VIEWPORT REFRESH ──
        # self._refresh_material_actors(material_json_path)


# =======================================================================================================
    def _erase_material_segments_range(self, materials, affected_layers, from_chainage, to_chainage):
        """
        Sirf us range ke segments remove karta hai jo [from_chainage, to_chainage] ke andar hain.
        Partial overlap bhi handle karta hai — trim karta hai, poora nahi hatata.
        """
        for mat in materials:

            mat_name = mat.get("material_line_folder")

            if mat_name not in affected_layers:
                continue

            new_segments = []

            for seg in mat.get("segments", []):

                seg_from = float(seg.get("from_chainage_m", 0))
                seg_to   = float(seg.get("to_chainage_m",   0))

                # ── Case 1: Segment poora erase range ke bahar (keep) ──
                if seg_to <= from_chainage or seg_from >= to_chainage:
                    new_segments.append(seg)
                    continue

                # ── Case 2: Segment poora andar (drop) ──
                if seg_from >= from_chainage and seg_to <= to_chainage:
                    print(f"  [Chain] {mat_name} | REMOVED {seg_from}→{seg_to}")
                    continue

                # ── Case 3: Partial left overlap — right side trim ──
                if seg_from < from_chainage < seg_to:
                    trimmed = dict(seg)
                    trimmed["to_chainage_m"] = from_chainage
                    new_segments.append(trimmed)
                    print(f"  [Chain] {mat_name} | TRIMMED RIGHT {seg_from}→{from_chainage}")

                # ── Case 4: Partial right overlap — left side trim ──
                if seg_from < to_chainage < seg_to:
                    trimmed = dict(seg)
                    trimmed["from_chainage_m"] = to_chainage
                    new_segments.append(trimmed)
                    print(f"  [Chain] {mat_name} | TRIMMED LEFT {to_chainage}→{seg_to}")

            mat["segments"]       = new_segments
            mat["total_segments"] = len(new_segments)

            print(f"  [Chain] {mat_name}: {len(new_segments)} segments bache")

# ======================================================================================================================================
#                                           **  Copy Dialog for Design and Material Data **
# ======================================================================================================================================
class CopyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Copy")
        self.selected_layers = []

        self.copy_buffer = {}

        # ================= FONT =================
        self.setFont(QFont("Segoe UI", 10))

        # ================= MAIN LAYOUT =================
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        # ================= TITLE =================
        title = QLabel("Copy Data")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #4A148C;")
        main_layout.addWidget(title)

        # ================= CHAINAGE =================
        chainage_box = QGroupBox("Chainage Range")
        chainage_box.setStyleSheet(self.group_style())

        grid = QGridLayout()
        grid.setSpacing(10)

        self.from_km = QLineEdit()
        self.to_km = QLineEdit()
        self.from_chainage = QLineEdit()
        self.to_chainage = QLineEdit()

        for field in [self.from_km, self.to_km, self.from_chainage, self.to_chainage]:
            field.setMinimumHeight(32)
            field.setStyleSheet(self.input_style())

        grid.addWidget(QLabel("From KM"), 0, 0)
        grid.addWidget(self.from_km, 0, 1)

        grid.addWidget(QLabel("To KM"), 1, 0)
        grid.addWidget(self.to_km, 1, 1)

        grid.addWidget(QLabel("From Chainage"), 0, 2)
        grid.addWidget(self.from_chainage, 0, 3)

        grid.addWidget(QLabel("To Chainage"), 1, 2)
        grid.addWidget(self.to_chainage, 1, 3)

        chainage_box.setLayout(grid)
        main_layout.addWidget(chainage_box)

        # ================= VERIFY =================
        verify_layout = QHBoxLayout()
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet(self.button_style())

        verify_layout.addStretch()
        verify_layout.addWidget(self.verify_btn)
        verify_layout.addStretch()

        main_layout.addLayout(verify_layout)

        # ================= LAYER BOX =================
        self.layer_box = QGroupBox("Select Layers")
        self.layer_box.setStyleSheet(self.group_style())
        self.layer_box.setVisible(False)

        self.layer_layout = QVBoxLayout()
        self.layer_layout.setSpacing(6)

        self.layer_box.setLayout(self.layer_layout)
        main_layout.addWidget(self.layer_box)

        # ================= FOOTER =================
        footer = QHBoxLayout()

        self.ok_btn = QPushButton("Copy")
        self.cancel_btn = QPushButton("Cancel")

        # self.ok_btn.clicked.connect(self.collect_selection)

        self.ok_btn.setStyleSheet(self.button_style())
        self.cancel_btn.setStyleSheet(self.cancel_style())

        footer.addStretch()
        footer.addWidget(self.ok_btn)
        footer.addWidget(self.cancel_btn)

        main_layout.addLayout(footer)

        self.setLayout(main_layout)

        # ================= CONNECTIONS =================
        self.verify_btn.clicked.connect(self.verify_range)
        self.ok_btn.clicked.connect(self.collect_selection)
        self.cancel_btn.clicked.connect(self.reject)

        # self.from_km.textChanged.connect(self.reset_verify_button)
        # self.to_km.textChanged.connect(self.reset_verify_button)
        # self.from_chainage.textChanged.connect(self.reset_verify_button)
        # self.to_chainage.textChanged.connect(self.reset_verify_button)

    # ================= STYLES =================

    def group_style(self):
        return """
        QGroupBox {
            border: 2px solid #9C27B0;
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 8px;
            font-weight: bold;
            color: #4A148C;
            background-color: rgba(255, 255, 255, 0.4);
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 4px 10px;
            background-color: #E1BEE7;
            border-radius: 6px;
        }
        """

    def input_style(self):
        return """
        QLineEdit {
            background-color: #F3E5F5;
            border: 2px solid #9C27B0;
            border-radius: 8px;
            padding: 6px;
        }
        """

    def button_style(self):
        return """
        QPushButton {
            background-color: #9C27B0;
            color: white;
            border-radius: 8px;
            padding: 6px 15px;
        }
        QPushButton:hover {
            background-color: #7B1FA2;
        }
        """

    def cancel_style(self):
        return """
        QPushButton {
            background-color: #CE93D8;
            color: black;
            border-radius: 8px;
            padding: 6px 15px;
        }
        """

    # ================= HELPERS =================

    def clear_layout(self):
        while self.layer_layout.count():
            item = self.layer_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def verify_range(self):
        try:
            from_km       = float(self.from_km.text())
            to_km         = float(self.to_km.text())
            from_chainage = float(self.from_chainage.text())
            to_chainage   = float(self.to_chainage.text())

        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values")
            return

        try:
            parent = self.parent()

            if not parent or not hasattr(parent, "current_worksheet_name"):
                QMessageBox.warning(self, "Error", "Worksheet not active")
                return

            worksheet_path = os.path.join(
                parent.WORKSHEETS_BASE_DIR,
                parent.current_worksheet_name
            )

            designs_path  = os.path.join(worksheet_path, "designs")
            material_path = os.path.join(worksheet_path, "construction")

            design_found   = False
            material_found = False

            self.loaded_design_json   = None
            self.loaded_material_json = None
            self.design_json_path     = None
            self.material_json_path   = None

            # ── DESIGN VERIFY ──
            if os.path.exists(designs_path):
                for layer in os.listdir(designs_path):
                    layer_path = os.path.join(designs_path, layer)
                    if not os.path.isdir(layer_path):
                        continue

                    json_file = os.path.join(layer_path, "design_construction_config.json")
                    if not os.path.exists(json_file):
                        continue

                    try:
                        with open(json_file, "r") as f:
                            content = f.read().strip()
                            if not content:
                                continue
                            data = json.loads(content)
                            if not isinstance(data, dict):
                                continue
                    except:
                        continue

                    surface      = data.get("design", {}).get("surface_baseline", {})
                    construction = data.get("design", {}).get("construction_baseline", {})
                    road_surface = data.get("design", {}).get("road_surface_baseline", {})

                    for base in [surface, construction, road_surface]:
                        polylines = base.get("polylines")
                        if not isinstance(polylines, list):
                            continue

                        for poly in polylines:
                            points = poly.get("points", [])
                            if not isinstance(points, list):
                                continue

                            start_found = False
                            end_found   = False

                            for pt in points:
                                try:
                                    ch_str = pt.get("chainage_str", "")
                                    if "+" not in ch_str:
                                        continue

                                    km_part, ch_part = ch_str.split("+", 1)
                                    km_val = float(km_part)
                                    ch_val = float(ch_part)

                                    if km_val == from_km and abs(ch_val - from_chainage) < 0.01:
                                        start_found = True

                                    if km_val == to_km and abs(ch_val - to_chainage) < 0.01:
                                        end_found = True

                                except:
                                    continue

                            if start_found and end_found:
                                design_found = True
                                self.loaded_design_json = data
                                self.design_json_path   = json_file
                                break

                        if design_found:
                            break
                    if design_found:
                        break

            # ── MATERIAL VERIFY ──
            # Fix: segment-level check karo, overall chainage pe depend mat karo
            if os.path.exists(material_path):
                for layer_folder in os.listdir(material_path):
                    layer_path = os.path.join(material_path, layer_folder)
                    if not os.path.isdir(layer_path):
                        continue

                    json_file = os.path.join(layer_path, "material_construction_config.json")
                    if not os.path.exists(json_file):
                        continue

                    try:
                        with open(json_file, "r") as f:
                            mat_data = json.load(f)
                    except:
                        continue

                    for mat in mat_data.get("materials", []):
                        try:
                            segments = mat.get("segments", [])
                            if not segments:
                                continue

                            # ── SEGMENT-LEVEL CHECK ──
                            # Koi bhi segment user range ko cover karta ho
                            # (segment range aur user range overlap ho)
                            has_data_in_range = False

                            for seg in segments:
                                seg_from = float(seg.get("from_chainage_m", 0))
                                seg_to   = float(seg.get("to_chainage_m",   0))

                                # Overlap condition: segment aur [from_chainage, to_chainage] overlap karte hain
                                if seg_to > from_chainage and seg_from < to_chainage:
                                    has_data_in_range = True
                                    break

                            if has_data_in_range:
                                material_found            = True
                                self.loaded_material_json = mat_data
                                self.material_json_path   = json_file
                                break

                        except Exception as e:
                            print(f"Material verify error: {e}")
                            continue

                    if material_found:
                        break

            # ── RESULT ──
            if not design_found and not material_found:
                QMessageBox.warning(self, "Error", "Data not found. Please enter a valid range.")
                return

            print(f"Verify result → design_found={design_found}, material_found={material_found}")

            # ── SHOW LAYERS ──
            self.verify_btn.setText("Verified")
            self.verify_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 8px;
                    padding: 6px 15px;
                    font-weight: bold;
                }
            """)

            self.clear_layout()

            if design_found:
                self.design_cb = QCheckBox("Design Layer")
                self.layer_layout.addWidget(self.design_cb)

            if material_found:
                self.material_cb = QCheckBox("Material Layer")
                self.layer_layout.addWidget(self.material_cb)

            self.layer_box.setVisible(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            import traceback
            traceback.print_exc()


    def collect_selection(self):
        self.selected_layers = []

        for i in range(self.layer_layout.count()):
            cb = self.layer_layout.itemAt(i).widget()
            if isinstance(cb, QCheckBox) and cb.isChecked():
                self.selected_layers.append(cb.text())

        if not self.selected_layers:
            QMessageBox.warning(self, "Warning", "Please select at least one layer")
            return

        try:
            from_km       = float(self.from_km.text())
            to_km         = float(self.to_km.text())
            from_chainage = float(self.from_chainage.text())
            to_chainage   = float(self.to_chainage.text())

        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values")
            return

        # ================= COPY BUFFER INITIALIZE =================
        self.copy_buffer = {}

        self.copy_buffer["range"] = {
            "from_km":       from_km,
            "to_km":         to_km,
            "from_chainage": from_chainage,
            "to_chainage":   to_chainage,
        }
        self.copy_buffer["design"]   = {}
        self.copy_buffer["material"] = []

        design_copied   = False
        material_copied = False

        design_labels = [
            "Surface Baseline",
            "Construction Baseline",
            "Road Surface Baseline",
            "Deck Line",
            "Projection Line",
        ]

        # ── Design Layer checkbox = saare baselines ──
        if "Design Layer" in self.selected_layers:
            design = (
                self.loaded_design_json.get("design", {})
                if hasattr(self, "loaded_design_json") and self.loaded_design_json
                else {}
            )
            design_selected = [
                label for label, key in {
                    "Surface Baseline":      "surface_baseline",
                    "Construction Baseline": "construction_baseline",
                    "Road Surface Baseline": "road_surface_baseline",
                    "Deck Line":             "deck_line",
                    "Projection Line":       "projection_line",
                }.items()
                if design.get(key) is not None
            ]
        else:
            design_selected = [s for s in self.selected_layers if s in design_labels]

        # ================= DESIGN COPY =================
        if design_selected and hasattr(self, "loaded_design_json") and self.loaded_design_json:

            design  = self.loaded_design_json.get("design", {})
            key_map = {
                "Surface Baseline":      "surface_baseline",
                "Construction Baseline": "construction_baseline",
                "Road Surface Baseline": "road_surface_baseline",
                "Deck Line":             "deck_line",
                "Projection Line":       "projection_line",
            }

            for label in design_selected:
                key  = key_map.get(label)
                if not key:
                    continue

                base = design.get(key)
                if base is None:
                    continue

                filtered_polylines = []

                for poly in base.get("polylines", []):
                    filtered_points = []

                    for pt in poly.get("points", []):
                        try:
                            ch_str = pt.get("chainage_str", "")
                            if "+" not in ch_str:
                                continue

                            km_part, ch_part = ch_str.split("+", 1)
                            km_val = float(km_part)
                            ch_val = float(ch_part)

                            if (
                                from_km <= km_val <= to_km and
                                from_chainage <= ch_val <= to_chainage
                            ):
                                filtered_points.append(pt)

                        except Exception as e:
                            print("Design point parse error:", e)
                            continue

                    if len(filtered_points) >= 2:
                        filtered_polylines.append({"points": filtered_points})

                # Fallback color
                design_color = self.parent().plane_colors.get(
                    key.replace("_baseline", ""),
                    (0.5, 0.5, 0.5, 0.4)
                )

                if filtered_polylines:
                    self.copy_buffer["design"][key] = {
                        "baseline_type":        base.get("baseline_type"),
                        "baseline_key":         base.get("baseline_key"),
                        "color":                design_color,
                        "width_meters":         base.get("width_meters", 20),
                        "zero_line_start":      base.get("zero_line_start"),
                        "zero_line_end":        base.get("zero_line_end"),
                        "zero_start_elevation": base.get("zero_start_elevation"),
                        "total_chainage_length": base.get("total_chainage_length"),
                        "reference_type":       base.get("reference_type"),
                        "polylines":            filtered_polylines,
                    }
                    design_copied = True
                    print(f"COPIED design → {key} | Polylines: {len(filtered_polylines)}")
                else:
                    print(f"SKIPPED design → {key} | No valid points in range")

        # ================= MATERIAL COPY =================
        material_selected = "Material Layer" in self.selected_layers

        print(f"material_selected={material_selected} | "
            f"loaded_material_json={hasattr(self, 'loaded_material_json') and self.loaded_material_json is not None}")

        if material_selected and hasattr(self, "loaded_material_json") and self.loaded_material_json:

            materials = self.loaded_material_json.get("materials", [])
            print(f"Total materials in JSON: {len(materials)}")

            for mat in materials:
                mat_name = mat.get("material_line_folder")

                # ── Filter segments that OVERLAP with user range ──
                # (seg_from < to_chainage AND seg_to > from_chainage)
                filtered_segments = []

                for seg in mat.get("segments", []):
                    seg_from = float(seg.get("from_chainage_m", 0))
                    seg_to   = float(seg.get("to_chainage_m",   0))

                    # Full overlap: segment jo user range ke andar aaye
                    # Either fully inside or partially overlapping
                    if seg_from >= from_chainage and seg_to <= to_chainage:
                        # Fully inside user range
                        filtered_segments.append(seg)
                        print(f"  MATCH (full) → {seg.get('segment_label')} | {seg_from}→{seg_to}")
                    elif seg_from < to_chainage and seg_to > from_chainage:
                        # Partially overlapping — include bhi karo
                        filtered_segments.append(seg)
                        print(f"  MATCH (partial) → {seg.get('segment_label')} | {seg_from}→{seg_to}")
                    else:
                        print(f"  SKIP → {seg.get('segment_label')} | {seg_from}→{seg_to}")

                if not filtered_segments:
                    print(f"SKIPPED material → {mat_name} | No segments in range {from_chainage}→{to_chainage}")
                    continue

                # Color
                material_color = [0.5, 0.5, 0.5, 1.0]
                if hasattr(self, "material_actors_dict"):
                    actor = self.material_actors_dict.get(mat_name)
                    if actor:
                        prop    = actor.GetProperty()
                        rgb     = prop.GetColor()
                        opacity = prop.GetOpacity()
                        material_color = [rgb[0], rgb[1], rgb[2], opacity]

                self.copy_buffer["material"].append({
                    "material_line_folder":  mat_name,
                    "material_line_name":    mat.get("material_line_name"),
                    "material_line_id":      mat.get("material_line_id"),
                    "rmh_id":                mat.get("rmh_id"),
                    "reference_baseline":    mat.get("reference_baseline"),
                    "is_below_ground":       mat.get("is_below_ground"),
                    "width_m":               filtered_segments[0].get("width_m", 20.0),
                    "color":                 material_color,
                    "overall_from_chainage": {
                        "chainage_m":   filtered_segments[0]["from_chainage_m"],
                        "chainage_str": f"{int(from_km)}+{int(filtered_segments[0]['from_chainage_m']):03d}",
                    },
                    "overall_to_chainage": {
                        "chainage_m":   filtered_segments[-1]["to_chainage_m"],
                        "chainage_str": f"{int(to_km)}+{int(filtered_segments[-1]['to_chainage_m']):03d}",
                    },
                    "segments":           filtered_segments,
                    "total_segments":     len(filtered_segments),
                    "worksheet":          mat.get("worksheet"),
                    "construction_layer": mat.get("construction_layer"),
                })

                material_copied = True
                print(f"COPIED material → {mat_name} | Segments: {len(filtered_segments)}")

        # ── FINAL MESSAGE ──
        if design_copied and material_copied:
            QMessageBox.information(self, "Success", "Both Layers copied successfully")
        elif design_copied:
            QMessageBox.information(self, "Success", "Design Layer copied successfully")
        elif material_copied:
            QMessageBox.information(self, "Success", "Material Layer copied successfully")
        else:
            QMessageBox.warning(self, "Warning", "No data found in selected range")
            return

        self.accept()

# ======================================================================================================================================
#                                   *** Expanding Road Dialog for Layer Cloning / Offset ***
# ======================================================================================================================================
class ExpandingRoadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Expanding Road")
        self.setModal(True)
        self.setMinimumWidth(760)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #eef4ff, stop:1 #f8fbff);
            }
            QLabel {
                color: #1f2937;
                font-weight: 600;
            }
            QGroupBox {
                border: 2px solid #2f80ed;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: bold;
                color: #174ea6;
                background-color: rgba(255, 255, 255, 0.5);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 10px;
                background-color: #dbeafe;
                border-radius: 6px;
            }
            QLineEdit, QComboBox {
                border: 2px solid #93c5fd;
                border-radius: 8px;
                padding: 7px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #2563eb;
                background-color: #eff6ff;
            }
            QPushButton {
                border-radius: 18px;
                padding: 10px 16px;
                font-weight: bold;
                min-width: 96px;
                border: none;
            }
            QPushButton#verifyBtn {
                background-color: #2563eb;
                color: white;
            }
            QPushButton#verifyBtn:disabled {
                background-color: #93c5fd;
                color: white;
            }
            QPushButton#okBtn {
                background-color: #16a34a;
                color: white;
            }
            QPushButton#cancelBtn {
                background-color: #e5e7eb;
                color: #111827;
            }
        """)

        self.source_layer_path = None
        self.source_layer_data = None
        self.source_design_data = None
        self.source_layer_name = None
        self.source_layer_width = 0.0
        self.verified = False
        self.created_layers = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        title = QLabel("Expanding Road")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #174ea6;")
        main_layout.addWidget(title)

        layer_group = QGroupBox("Source Design Layer")
        layer_layout = QVBoxLayout(layer_group)
        layer_layout.setSpacing(8)

        self.design_layer_combo = QComboBox()
        self.design_layer_combo.currentIndexChanged.connect(self._on_layer_changed)
        layer_layout.addWidget(QLabel("Select Design Layer:"))
        layer_layout.addWidget(self.design_layer_combo)
        main_layout.addWidget(layer_group)

        chainage_group = QGroupBox("Chainage Range")
        chainage_layout = QGridLayout(chainage_group)
        chainage_layout.setHorizontalSpacing(10)
        chainage_layout.setVerticalSpacing(10)

        self.from_km_edit = QLineEdit()
        self.from_chainage_edit = QLineEdit()
        self.to_km_edit = QLineEdit()
        self.to_chainage_edit = QLineEdit()

        for field in [self.from_km_edit, self.from_chainage_edit, self.to_km_edit, self.to_chainage_edit]:
            field.setValidator(QDoubleValidator(0.0, 1000000.0, 3))
            field.setMinimumHeight(32)
            field.textChanged.connect(self._on_range_changed)

        chainage_layout.addWidget(QLabel("From KM"), 0, 0)
        chainage_layout.addWidget(self.from_km_edit, 0, 1)
        chainage_layout.addWidget(QLabel("From Chainage"), 0, 2)
        chainage_layout.addWidget(self.from_chainage_edit, 0, 3)
        chainage_layout.addWidget(QLabel("To KM"), 1, 0)
        chainage_layout.addWidget(self.to_km_edit, 1, 1)
        chainage_layout.addWidget(QLabel("To Chainage"), 1, 2)
        chainage_layout.addWidget(self.to_chainage_edit, 1, 3)
        main_layout.addWidget(chainage_group)

        verify_row = QHBoxLayout()
        verify_row.addStretch()
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setObjectName("verifyBtn")
        self.verify_btn.clicked.connect(self.verify_selected_layer_range)
        verify_row.addWidget(self.verify_btn)
        verify_row.addStretch()
        main_layout.addLayout(verify_row)

        mode_group = QWidget()
        mode_row = QVBoxLayout(mode_group)
        mode_row.setContentsMargins(0, 0, 0, 0)
        mode_row.setSpacing(8)

        mode_checkbox_row = QHBoxLayout()
        mode_checkbox_row.setSpacing(14)
        self.design_mode_checkbox = QCheckBox("Design")
        self.design_with_material_checkbox = QCheckBox("Design with Material")
        self.offset_checkbox = QCheckBox("Offset")
        self.design_mode_checkbox.setChecked(True)
        self.design_mode_checkbox.stateChanged.connect(self._on_mode_changed)
        self.design_with_material_checkbox.stateChanged.connect(self._on_mode_changed)
        self.offset_checkbox.stateChanged.connect(self._on_mode_changed)
        mode_checkbox_row.addWidget(self.design_mode_checkbox)
        mode_checkbox_row.addWidget(self.design_with_material_checkbox)
        mode_checkbox_row.addWidget(self.offset_checkbox)
        mode_checkbox_row.addStretch()
        mode_row.addLayout(mode_checkbox_row)

        offset_row = QHBoxLayout()
        offset_row.setSpacing(8)
        self.offset_distance_label = QLabel("Gap Distance (m)")
        self.offset_distance_edit = QLineEdit()
        self.offset_distance_edit.setValidator(QDoubleValidator(0.01, 1000000.0, 3))
        self.offset_distance_edit.setPlaceholderText("Enter gap distance in meters")
        self.offset_distance_label.setEnabled(False)
        self.offset_distance_edit.setEnabled(False)
        offset_row.addWidget(self.offset_distance_label)
        offset_row.addWidget(self.offset_distance_edit, 1)
        mode_row.addLayout(offset_row)

        main_layout.addWidget(mode_group)

        self.status_label = QLabel("Select a layer and verify the range before continuing.")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #334155; font-style: italic;")
        main_layout.addWidget(self.status_label)

        side_group = QGroupBox("Offset Side")
        side_layout = QVBoxLayout(side_group)
        side_layout.setSpacing(8)

        self.left_radio = QRadioButton("Left")
        self.right_radio = QRadioButton("Right")
        self.both_radio = QRadioButton("Both side")
        self.left_radio.setChecked(True)

        self.left_radio.toggled.connect(self._update_width_ui)
        self.right_radio.toggled.connect(self._update_width_ui)
        self.both_radio.toggled.connect(self._update_width_ui)

        side_row = QHBoxLayout()
        side_row.addWidget(self.left_radio)
        side_row.addWidget(self.right_radio)
        side_row.addWidget(self.both_radio)
        side_row.addStretch()
        side_layout.addLayout(side_row)

        self.single_width_widget = QWidget()
        single_width_layout = QHBoxLayout(self.single_width_widget)
        single_width_layout.setContentsMargins(0, 0, 0, 0)
        single_width_layout.setSpacing(8)
        self.single_width_label = QLabel("Road Width (m)")
        self.single_width_edit = QLineEdit()
        self.single_width_edit.setValidator(QDoubleValidator(0.01, 100000.0, 3))
        self.single_width_edit.setPlaceholderText("Enter width in meters")
        single_width_layout.addWidget(self.single_width_label)
        single_width_layout.addWidget(self.single_width_edit, 1)

        self.both_width_widget = QWidget()
        both_width_layout = QGridLayout(self.both_width_widget)
        both_width_layout.setContentsMargins(0, 0, 0, 0)
        both_width_layout.setHorizontalSpacing(10)
        both_width_layout.setVerticalSpacing(8)
        self.left_width_edit = QLineEdit()
        self.right_width_edit = QLineEdit()
        self.left_width_edit.setValidator(QDoubleValidator(0.01, 100000.0, 3))
        self.right_width_edit.setValidator(QDoubleValidator(0.01, 100000.0, 3))
        self.left_width_edit.setPlaceholderText("Left width")
        self.right_width_edit.setPlaceholderText("Right width")
        both_width_layout.addWidget(QLabel("Left Width (m)"), 0, 0)
        both_width_layout.addWidget(self.left_width_edit, 0, 1)
        both_width_layout.addWidget(QLabel("Right Width (m)"), 1, 0)
        both_width_layout.addWidget(self.right_width_edit, 1, 1)

        side_layout.addWidget(self.single_width_widget)
        side_layout.addWidget(self.both_width_widget)
        main_layout.addWidget(side_group)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setObjectName("okBtn")
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self.on_ok_clicked)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.ok_btn)
        btn_row.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_row)

        self.populate_design_layers()
        self._update_width_ui()

    def _log_message(self, text):
        parent = self.parent()
        if parent and hasattr(parent, "message_text") and parent.message_text is not None:
            parent.message_text.append(str(text))

    def _on_mode_changed(self, state):
        sender = self.sender()
        if sender == self.offset_checkbox:
            is_enabled = self.offset_checkbox.isChecked()
            self.offset_distance_label.setEnabled(is_enabled)
            self.offset_distance_edit.setEnabled(is_enabled)

        if not self.design_mode_checkbox.isChecked() and not self.design_with_material_checkbox.isChecked():
            self.design_mode_checkbox.blockSignals(True)
            self.design_mode_checkbox.setChecked(True)
            self.design_mode_checkbox.blockSignals(False)

    def get_creation_mode(self):
        if self.offset_checkbox.isChecked():
            return "offset"
        return "design_with_material" if self.design_with_material_checkbox.isChecked() else "design"

    def _worksheet_root(self):
        parent = self.parent()
        worksheet_name = getattr(parent, "current_worksheet_name", None) if parent else None
        if not worksheet_name:
            return None

        base_dir = getattr(parent, "WORKSHEETS_BASE_DIR", None) if parent else None
        if base_dir:
            candidate = os.path.join(base_dir, worksheet_name)
            if os.path.exists(candidate):
                return candidate

        fallback_roots = [
            os.path.join(os.path.expanduser("~"), "3D_Tool", "user"),
            os.path.join("C:\\", "3D_Tool", "user"),
        ]
        for root in fallback_roots:
            if not os.path.exists(root):
                continue
            direct = os.path.join(root, worksheet_name)
            if os.path.exists(direct):
                return direct
            try:
                for current_root, dirs, _files in os.walk(root):
                    if os.path.basename(current_root) == worksheet_name:
                        designs_path = os.path.join(current_root, "designs")
                        if os.path.exists(designs_path):
                            return current_root
            except Exception:
                continue
        return None

    def populate_design_layers(self):
        self.design_layer_combo.clear()
        self.design_layer_combo.addItem("-- Select a Design Layer --", None)

        worksheet_root = self._worksheet_root()
        if not worksheet_root:
            self.design_layer_combo.addItem("No active worksheet found")
            self.design_layer_combo.setEnabled(False)
            return

        designs_path = os.path.join(worksheet_root, "designs")
        if not os.path.exists(designs_path):
            self.design_layer_combo.addItem("Designs folder not found")
            self.design_layer_combo.setEnabled(False)
            return

        try:
            layer_items = []
            for folder in sorted(os.listdir(designs_path)):
                layer_path = os.path.join(designs_path, folder)
                if not os.path.isdir(layer_path):
                    continue

                config_path = os.path.join(layer_path, "design_layer_config.txt")
                display_name = folder
                if os.path.exists(config_path):
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            config_data = json.load(f)
                        display_name = config_data.get("layer_name", folder) or folder
                    except Exception:
                        display_name = folder

                layer_items.append((display_name, layer_path))

            if not layer_items:
                self.design_layer_combo.addItem("No design layers found")
                self.design_layer_combo.setEnabled(False)
                return

            for display_name, layer_path in layer_items:
                self.design_layer_combo.addItem(display_name, layer_path)
        except Exception as e:
            self.design_layer_combo.addItem(f"Error loading layers: {e}")
            self.design_layer_combo.setEnabled(False)

    def _on_layer_changed(self, _index):
        self.verified = False
        self.ok_btn.setEnabled(False)
        self.verify_btn.setText("Verify")
        self.verify_btn.setEnabled(True)
        self.status_label.setText("Select a layer and verify the range before continuing.")
        self.status_label.setStyleSheet("color: #334155; font-style: italic;")

    def _on_range_changed(self, *args):
        if self.verified:
            self.verified = False
            self.ok_btn.setEnabled(False)
            self.verify_btn.setText("Verify")
            self.verify_btn.setEnabled(True)
            self.status_label.setText("Chainage range changed. Please verify again.")
            self.status_label.setStyleSheet("color: #b45309; font-style: italic;")

    def _update_width_ui(self, *args):
        both = self.both_radio.isChecked()
        self.single_width_widget.setVisible(not both)
        self.both_width_widget.setVisible(both)

    def _parse_chainage_pair(self):
        try:
            from_km = float(self.from_km_edit.text().strip())
            from_chainage = float(self.from_chainage_edit.text().strip())
            to_km = float(self.to_km_edit.text().strip())
            to_chainage = float(self.to_chainage_edit.text().strip())
        except ValueError:
            raise ValueError("Please enter valid numeric values for all chainage fields.")

        return from_km, from_chainage, to_km, to_chainage

    @staticmethod
    def _chainage_to_total_m(km_value, chainage_value):
        return float(km_value) * 1000.0 + float(chainage_value)

    def _collect_chainage_values(self, design_section):
        chainage_values = set()

        def add_point_value(point):
            if not isinstance(point, dict):
                return
            chainage_m = point.get("chainage_m")
            if chainage_m is not None:
                try:
                    chainage_values.add(round(float(chainage_m), 3))
                except Exception:
                    pass
            chainage_str = point.get("chainage_str")
            if chainage_str and "+" in str(chainage_str):
                try:
                    km_part, chain_part = str(chainage_str).split("+", 1)
                    chainage_values.add(round(self._chainage_to_total_m(km_part, chain_part), 3))
                except Exception:
                    pass

        if not isinstance(design_section, dict):
            return chainage_values

        zero_line = design_section.get("zero_line_config")
        if isinstance(zero_line, dict):
            p1 = zero_line.get("point1", {})
            p2 = zero_line.get("point2", {})
            for point in [p1, p2]:
                if isinstance(point, dict):
                    km_key = point.get("from_km") if "from_km" in point else point.get("to_km")
                    chain_key = point.get("from_chainage") if "from_chainage" in point else point.get("to_chainage")
                    if km_key is not None and chain_key is not None:
                        try:
                            chainage_values.add(round(self._chainage_to_total_m(km_key, chain_key), 3))
                        except Exception:
                            pass

        for baseline_key in ["surface_baseline", "construction_baseline", "road_surface_baseline", "deck_line", "projection_line"]:
            baseline = design_section.get(baseline_key)
            if not isinstance(baseline, dict):
                continue
            for poly in baseline.get("polylines", []):
                if not isinstance(poly, dict):
                    continue
                for point in poly.get("points", []):
                    add_point_value(point)

        return chainage_values

    def _load_source_layer(self):
        layer_path = self.design_layer_combo.currentData()
        if not layer_path or not os.path.isdir(layer_path):
            raise ValueError("Please select a valid design layer.")

        layer_config_path = os.path.join(layer_path, "design_layer_config.txt")
        layer_config = {}
        if os.path.exists(layer_config_path):
            try:
                with open(layer_config_path, "r", encoding="utf-8") as f:
                    layer_config = json.load(f)
            except Exception:
                layer_config = {}

        # Ensure DesignConstructionManager is available in this scope
        from json_manager import DesignConstructionManager

        layer_data = DesignConstructionManager.load_master(layer_path)
        if not isinstance(layer_data, dict):
            layer_data = DesignConstructionManager.get_default_structure()

        design_section = layer_data.get("design", {}) if isinstance(layer_data.get("design", {}), dict) else {}
        return layer_path, layer_config, layer_data, design_section

    def verify_selected_layer_range(self, *args):
        try:
            from_km, from_chainage, to_km, to_chainage = self._parse_chainage_pair()
        except ValueError as e:
            QMessageBox.warning(self, "Input Required", str(e))
            return

        if self.design_layer_combo.currentData() is None:
            QMessageBox.warning(self, "Input Required", "Please select a design layer.")
            return

        try:
            layer_path, layer_config, layer_data, design_section = self._load_source_layer()
        except Exception as e:
            QMessageBox.warning(self, "Verification Failed", str(e))
            return

        start_total = round(self._chainage_to_total_m(from_km, from_chainage), 3)
        end_total = round(self._chainage_to_total_m(to_km, to_chainage), 3)
        if end_total <= start_total:
            QMessageBox.warning(self, "Invalid Range", "To chainage must be greater than From chainage.")
            return

        available_chainages = self._collect_chainage_values(design_section)
        start_match = any(abs(start_total - value) <= 0.01 for value in available_chainages)
        end_match = any(abs(end_total - value) <= 0.01 for value in available_chainages)

        if not (start_match and end_match):
            QMessageBox.warning(
                self,
                "Verification Failed",
                "The entered KM/chainage range does not match the selected design layer."
            )
            return

        self.source_layer_path = layer_path
        self.source_layer_data = layer_data
        self.source_design_data = design_section
        self.source_layer_name = layer_config.get("layer_name") or os.path.basename(layer_path)
        self.source_layer_width = float(self._extract_source_width(layer_data))
        self.creation_mode = self.get_creation_mode()
        self.verified = True

        self.verify_btn.setText("Verified, OK")
        self.verify_btn.setEnabled(False)
        self.ok_btn.setEnabled(True)
        self.status_label.setText(
            f"Verified: {self.source_layer_name} | Source width: {self.source_layer_width:.3f} m"
        )
        self.status_label.setStyleSheet("color: #166534; font-weight: bold;")

    def _extract_source_width(self, layer_data):
        design_section = layer_data.get("design", {}) if isinstance(layer_data, dict) else {}
        if not isinstance(design_section, dict):
            return 0.0

        for key in ["road_surface_baseline", "surface_baseline", "construction_baseline", "deck_line", "projection_line"]:
            baseline = design_section.get(key)
            if isinstance(baseline, dict):
                for width_key in ["width_meters", "width_m"]:
                    value = baseline.get(width_key)
                    if value is not None:
                        try:
                            return float(value)
                        except Exception:
                            continue

        for width_key in ["width_meters", "width_m"]:
            value = design_section.get(width_key)
            if value is not None:
                try:
                    return float(value)
                except Exception:
                    continue

        return 0.0

    @staticmethod
    def _shift_coords(coords, offset_xy):
        if not isinstance(coords, (list, tuple)):
            return coords
        if len(coords) < 2:
            return list(coords)
        try:
            x = float(coords[0]) + float(offset_xy[0])
            y = float(coords[1]) + float(offset_xy[1])
            shifted = [x, y]
            for value in coords[2:]:
                shifted.append(float(value))
            return shifted
        except Exception:
            return list(coords)

    def _shift_geometry_recursive(self, value, offset_xy, new_width=None, parent_key=None):
        if isinstance(value, dict):
            shifted = {}
            for key, item in value.items():
                if key in ("coordinates", "world_coordinates", "from_coordinates", "to_coordinates", "zero_line_start", "zero_line_end", "absolute_coordinates"):
                    shifted[key] = self._shift_coords(item, offset_xy)
                elif new_width is not None and key in ("width_meters", "width_m"):
                    try:
                        shifted[key] = float(new_width)
                    except Exception:
                        shifted[key] = item
                else:
                    shifted[key] = self._shift_geometry_recursive(item, offset_xy, new_width, key)
            return shifted

        if isinstance(value, list):
            return [self._shift_geometry_recursive(item, offset_xy, new_width, parent_key) for item in value]

        return value

    def _compute_offset_vector(self, zero_line_config, side, source_width, new_width):
        point1 = zero_line_config.get("point1", {}) if isinstance(zero_line_config, dict) else {}
        point2 = zero_line_config.get("point2", {}) if isinstance(zero_line_config, dict) else {}

        p1 = np.array(point1.get("coordinates", [0.0, 0.0, 0.0]), dtype=float)
        p2 = np.array(point2.get("coordinates", [0.0, 0.0, 0.0]), dtype=float)
        direction = p2[:2] - p1[:2]
        norm = float(np.linalg.norm(direction))
        if norm <= 1e-9:
            direction = np.array([1.0, 0.0], dtype=float)
            norm = 1.0

        left_normal = np.array([-direction[1], direction[0]], dtype=float) / norm
        right_normal = -left_normal

        # Shift distance is the center-to-center expansion distance:
        # source half-width + new half-width.
        try:
            shift_distance = (float(source_width) / 2.0) + (float(new_width) / 2.0)
        except Exception:
            shift_distance = 0.0

        if abs(shift_distance) <= 1e-9:
            return np.array([0.0, 0.0], dtype=float)

        if side.lower() == "right":
            return right_normal * shift_distance
        return left_normal * shift_distance

    def _compute_total_offset_vector(self, zero_line_config, side, source_width, new_width, extra_offset_m=0.0):
        base_offset = self._compute_offset_vector(zero_line_config, side, source_width, new_width)
        try:
            extra_offset_m = float(extra_offset_m)
        except Exception:
            extra_offset_m = 0.0

        if abs(extra_offset_m) <= 1e-9:
            return base_offset

        point1 = zero_line_config.get("point1", {}) if isinstance(zero_line_config, dict) else {}
        point2 = zero_line_config.get("point2", {}) if isinstance(zero_line_config, dict) else {}

        p1 = np.array(point1.get("coordinates", [0.0, 0.0, 0.0]), dtype=float)
        p2 = np.array(point2.get("coordinates", [0.0, 0.0, 0.0]), dtype=float)
        direction = p2[:2] - p1[:2]
        norm = float(np.linalg.norm(direction))
        if norm <= 1e-9:
            direction = np.array([1.0, 0.0], dtype=float)
            norm = 1.0

        edge_normal = np.array([-direction[1], direction[0]], dtype=float) / norm
        if side.lower() == "right":
            edge_normal = -edge_normal

        return base_offset + (edge_normal * extra_offset_m)

    def _generate_unique_layer_name(self, designs_path, base_name):
        base_name = str(base_name or "Design Layer").strip() or "Design Layer"
        counter = 1
        while True:
            candidate = f"{base_name}-{counter}"
            candidate_path = os.path.join(designs_path, candidate)
            if not os.path.exists(candidate_path):
                return candidate
            counter += 1

    def _prepare_expanded_clone(self, source_layer_path, source_layer_data, side, new_width, output_layer_name, extra_offset_m=0.0):
        cloned_data = copy.deepcopy(source_layer_data)
        design_section = cloned_data.get("design", {}) if isinstance(cloned_data, dict) else {}

        zero_line_config = design_section.get("zero_line_config") if isinstance(design_section, dict) else None
        if not isinstance(zero_line_config, dict):
            raise ValueError("The selected layer does not contain a valid zero line configuration.")

        offset_xy = self._compute_total_offset_vector(
            zero_line_config,
            side,
            self.source_layer_width,
            new_width,
            extra_offset_m,
        )

        cloned_design = self._shift_geometry_recursive(design_section, offset_xy, new_width, "design")

        source_point1 = zero_line_config.get("point1", {}).get("coordinates", [0.0, 0.0, 0.0])
        shifted_point1 = (
            cloned_design.get("zero_line_config", {})
            .get("point1", {})
            .get("coordinates", [0.0, 0.0, 0.0])
        )
        try:
            source_point1_xy = np.array(source_point1[:2], dtype=float)
            shifted_point1_xy = np.array(shifted_point1[:2], dtype=float)
            actual_offset_xy = shifted_point1_xy - source_point1_xy
            residual_offset_xy = np.array(offset_xy, dtype=float) - actual_offset_xy
            if float(np.linalg.norm(residual_offset_xy)) > 1e-6:
                cloned_design = self._shift_geometry_recursive(cloned_design, residual_offset_xy, None, "design")
        except Exception:
            pass

        cloned_data["design"] = cloned_design

        cloned_data["layer_name"] = output_layer_name
        cloned_data["expanded_from_layer"] = self.source_layer_name
        cloned_data["expanded_side"] = side
        cloned_data["expanded_width_m"] = float(new_width)
        cloned_data["expanded_source_width_m"] = float(self.source_layer_width)
        cloned_data["expanded_offset_m"] = float((self.source_layer_width + float(new_width)) / 2.0)
        cloned_data["expanded_at"] = datetime.now().isoformat()

        return cloned_data, offset_xy

    def _copy_and_write_layer(self, source_layer_path, output_layer_name, clone_data, side, new_width, from_km, from_chainage, to_km, to_chainage):
        designs_path = os.path.dirname(source_layer_path)
        output_layer_path = os.path.join(designs_path, output_layer_name)

        if os.path.exists(output_layer_path):
            raise FileExistsError(f"Layer folder already exists: {output_layer_name}")

        shutil.copytree(source_layer_path, output_layer_path)

        master_path = os.path.join(output_layer_path, DesignConstructionManager.MASTER_FILENAME)
        with open(master_path, "w", encoding="utf-8") as f:
            json.dump(clone_data, f, indent=2, ensure_ascii=False)

        source_config_path = os.path.join(source_layer_path, "design_layer_config.txt")
        source_config = {}
        if os.path.exists(source_config_path):
            try:
                with open(source_config_path, "r", encoding="utf-8") as f:
                    source_config = json.load(f)
            except Exception:
                source_config = {}

        # Prepare config for the new layer and write into the new layer folder
        updated_config = dict(source_config)
        updated_config.update({
            "layer_name": output_layer_name,
            "expanded_from_layer": self.source_layer_name,
            "expanded_side": side,
            "expanded_width_m": float(new_width),
            "expanded_source_width_m": float(self.source_layer_width),
            "expanded_offset_m": float((self.source_layer_width + float(new_width)) / 2.0),
            "expanded_range": {
                "from_km": from_km,
                "from_chainage": from_chainage,
                "to_km": to_km,
                "to_chainage": to_chainage,
            },
            "created_at": datetime.now().isoformat(),
        })

        output_config_path = os.path.join(output_layer_path, "design_layer_config.txt")
        try:
            with open(output_config_path, "w", encoding="utf-8") as f:
                json.dump(updated_config, f, indent=4, ensure_ascii=False)
        except Exception:
            # fallback: write into source config if output path fails for any reason
            try:
                with open(source_config_path, "w", encoding="utf-8") as f:
                    json.dump(updated_config, f, indent=4, ensure_ascii=False)
            except Exception:
                pass

        return output_layer_path

    def _generate_unique_construction_layer_name(self, construction_root, base_name):
        base_name = str(base_name or "Material").strip() or "Material"
        candidate = base_name
        if not os.path.exists(os.path.join(construction_root, candidate)):
            return candidate

        counter = 1
        while True:
            candidate = f"{base_name}-{counter}"
            if not os.path.exists(os.path.join(construction_root, candidate)):
                return candidate
            counter += 1

    def _find_source_material_layer(self, construction_root, source_design_layer_name):
        source_design_layer_name = str(source_design_layer_name or "").strip()
        if not source_design_layer_name or not os.path.isdir(construction_root):
            return None, None, None

        for folder_name in sorted(os.listdir(construction_root)):
            folder_path = os.path.join(construction_root, folder_name)
            if not os.path.isdir(folder_path):
                continue

            config_path = os.path.join(folder_path, "Construction_Layer_config.txt")
            if not os.path.exists(config_path):
                continue

            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                continue

            design_layer_name = str(config_data.get("design_layer_name", "")).strip()
            reference_layer_2d = str(config_data.get("reference_layer_2d", "")).strip()
            if design_layer_name == source_design_layer_name or reference_layer_2d == source_design_layer_name:
                material_json_path = os.path.join(folder_path, "material_construction_config.json")
                material_data = {}
                if os.path.exists(material_json_path):
                    try:
                        with open(material_json_path, "r", encoding="utf-8") as f:
                            material_data = json.load(f)
                    except Exception:
                        material_data = {}
                return folder_path, config_data, material_data

        return None, None, None

    def _duplicate_material_layer_for_design(self, output_design_name, side, new_width, extra_offset_m=0.0):
        worksheet_root = self._worksheet_root()
        if not worksheet_root:
            self._log_message("Warning: Could not resolve worksheet root for material duplication.")
            return None

        construction_root = os.path.join(worksheet_root, "construction")
        os.makedirs(construction_root, exist_ok=True)

        source_design_name = getattr(self, "source_layer_name", None) or os.path.basename(getattr(self, "source_layer_path", ""))
        source_material_path, source_material_config, source_material_data = self._find_source_material_layer(construction_root, source_design_name)
        if not source_material_path:
            self._log_message(
                f"Warning: No matching construction layer found for source design '{source_design_name}'."
            )
            return None

        target_material_base = f"Material {output_design_name}"
        target_material_name = self._generate_unique_construction_layer_name(construction_root, target_material_base)
        target_material_path = os.path.join(construction_root, target_material_name)

        shutil.copytree(source_material_path, target_material_path)

        zero_line_config = {}
        if isinstance(self.source_design_data, dict):
            zero_line_config = self.source_design_data.get("zero_line_config", {}) or {}

        offset_xy = self._compute_total_offset_vector(
            zero_line_config,
            side,
            self.source_layer_width,
            new_width,
            extra_offset_m,
        )

        cloned_data = copy.deepcopy(source_material_data) if isinstance(source_material_data, dict) else {}
        if isinstance(cloned_data, dict):
            materials = cloned_data.get("materials", [])
            if isinstance(materials, list):
                shifted_materials = []
                for material_entry in materials:
                    if not isinstance(material_entry, dict):
                        shifted_materials.append(material_entry)
                        continue

                    shifted_entry = self._shift_geometry_recursive(material_entry, offset_xy, new_width, "material")
                    for key in ("material_line_folder", "material_line_name", "construction_layer"):
                        shifted_entry[key] = target_material_name
                    shifted_entry["updated_at"] = datetime.now().isoformat()
                    shifted_materials.append(shifted_entry)

                cloned_data["materials"] = shifted_materials

            cloned_data["construction_layer"] = target_material_name
            cloned_data["worksheet"] = getattr(self.parent(), "current_worksheet_name", "")
            cloned_data["last_updated"] = datetime.now().isoformat()
            cloned_data["updated_by"] = getattr(self.parent(), "current_user", "user")

            material_lines_config = cloned_data.get("material_lines_config")
            if material_lines_config is not None:
                material_lines_config = copy.deepcopy(material_lines_config)
                material_lines_config["worksheet_name"] = getattr(self.parent(), "current_worksheet_name", "")
                material_lines_config["project_name"] = getattr(self.parent(), "current_project_name", "None") or "None"
                material_lines_config["created_by"] = getattr(self.parent(), "current_user", "user")
                material_lines_config["created_at"] = datetime.now().isoformat()
                cloned_data["material_lines_config"] = material_lines_config
            else:
                cloned_data["material_lines_config"] = {
                    "worksheet_name": getattr(self.parent(), "current_worksheet_name", ""),
                    "project_name": getattr(self.parent(), "current_project_name", "None") or "None",
                    "created_by": getattr(self.parent(), "current_user", "user"),
                    "created_at": datetime.now().isoformat(),
                    "material_line": []
                }

        source_config = dict(source_material_config or {})
        updated_config = dict(source_config)
        updated_config.update({
            "construction_layer_name": target_material_name,
            "worksheet_name": getattr(self.parent(), "current_worksheet_name", ""),
            "project_name": getattr(self.parent(), "current_project_name", "None") or "None",
            "worksheet_type": source_config.get("worksheet_type", "Design"),
            "worksheet_category": source_config.get("worksheet_category", "Road"),
            "construction_type": source_config.get("construction_type", "Road"),
            "reference_layer_2d": output_design_name,
            "design_layer_name": output_design_name,
            "created_at": datetime.now().isoformat(),
            "created_by": getattr(self.parent(), "current_user", "user"),
        })

        with open(os.path.join(target_material_path, "material_construction_config.json"), "w", encoding="utf-8") as f:
            json.dump(cloned_data, f, indent=4, ensure_ascii=False)

        material_lines_config = cloned_data.get("material_lines_config") if isinstance(cloned_data, dict) else None
        if material_lines_config is not None:
            with open(os.path.join(target_material_path, "material_lines_config.txt"), "w", encoding="utf-8") as f:
                json.dump(material_lines_config, f, indent=4, ensure_ascii=False)

        with open(os.path.join(target_material_path, "Construction_Layer_config.txt"), "w", encoding="utf-8") as f:
            json.dump(updated_config, f, indent=4, ensure_ascii=False)

        self._log_message(f"Material layer duplicated: {target_material_name}")
        self._log_message(f"  Path: {target_material_path}")
        return target_material_path

    def _width_for_side(self, side):
        if side.lower() == "both":
            raise ValueError("Both side width is handled separately.")
        try:
            return float(self.single_width_edit.text().strip())
        except ValueError:
            raise ValueError("Please enter a valid road width.")

    def _widths_for_both_sides(self):
        try:
            left_width = float(self.left_width_edit.text().strip())
            right_width = float(self.right_width_edit.text().strip())
        except ValueError:
            raise ValueError("Please enter valid widths for both left and right sides.")
        return left_width, right_width

    def on_ok_clicked(self, *args):
        if not self.verified:
            QMessageBox.warning(self, "Verification Required", "Please verify the selected design layer first.")
            return

        try:
            from_km, from_chainage, to_km, to_chainage = self._parse_chainage_pair()
        except ValueError as e:
            QMessageBox.warning(self, "Input Required", str(e))
            return

        try:
            source_layer_path = self.source_layer_path
            source_layer_data = self.source_layer_data
            if not source_layer_path or not source_layer_data:
                raise ValueError("Source design layer could not be loaded.")

            worksheet_root = self._worksheet_root()
            if not worksheet_root:
                raise ValueError("Worksheet root could not be resolved.")

            designs_path = os.path.join(worksheet_root, "designs")
            if not os.path.exists(designs_path):
                raise ValueError("Designs folder not found for the active worksheet.")

            created_paths = []
            created_material_paths = []
            base_name = self.source_layer_name or os.path.basename(source_layer_path)

            if self.both_radio.isChecked():
                left_width, right_width = self._widths_for_both_sides()
                specs = [("Left", left_width), ("Right", right_width)]
            else:
                side = "Left" if self.left_radio.isChecked() else "Right"
                specs = [(side, self._width_for_side(side))]

            extra_offset_m = 0.0
            if self.offset_checkbox.isChecked():
                offset_text = self.offset_distance_edit.text().strip()
                if not offset_text:
                    raise ValueError("Please enter a gap distance for the Offset option.")
                try:
                    extra_offset_m = float(offset_text)
                except ValueError:
                    raise ValueError("Please enter a valid numeric gap distance.")
                if extra_offset_m <= 0:
                    raise ValueError("Gap distance must be greater than zero.")

            for side, width in specs:
                output_name = self._generate_unique_layer_name(designs_path, base_name)
                clone_data, _offset_xy = self._prepare_expanded_clone(
                    source_layer_path,
                    source_layer_data,
                    side,
                    width,
                    output_name,
                    extra_offset_m=extra_offset_m,
                )
                new_path = self._copy_and_write_layer(
                    source_layer_path,
                    output_name,
                    clone_data,
                    side,
                    width,
                    from_km,
                    from_chainage,
                    to_km,
                    to_chainage,
                )
                created_paths.append((output_name, new_path))

                material_path = None
                if self.design_with_material_checkbox.isChecked():
                    material_path = self._duplicate_material_layer_for_design(
                        output_name,
                        side,
                        width,
                        extra_offset_m=extra_offset_m,
                    )
                    if material_path:
                        created_material_paths.append((os.path.basename(material_path), material_path))

                parent = self.parent()
                if parent and hasattr(parent, "add_layer_to_panel"):
                    try:
                        parent.add_layer_to_panel(output_name, "2D", full_path=new_path, subfolder="designs")
                    except Exception:
                        pass
                    if material_path:
                        try:
                            parent.add_layer_to_panel(os.path.basename(material_path), "2D", full_path=material_path, subfolder="construction")
                        except Exception:
                            pass

            self.created_layers = created_paths
            self.created_material_layers = created_material_paths

            parent = self.parent()
            if parent and created_paths:
                first_layer_name, first_layer_path = created_paths[0]
                if hasattr(parent, "current_layer_name"):
                    parent.current_layer_name = first_layer_name
                if hasattr(parent, "current_design_layer_path"):
                    parent.current_design_layer_path = first_layer_path
                if hasattr(parent, "switch_to_layer_from_panel"):
                    try:
                        parent.switch_to_layer_from_panel(first_layer_name, first_layer_path, "designs")
                    except Exception:
                        pass
                if hasattr(parent, "set_layer_panel_highlight"):
                    try:
                        parent.set_layer_panel_highlight(
                            active_layer_name=first_layer_name,
                            active_subfolder="designs",
                            linked_design_layer_name=None,
                        )
                    except Exception:
                        pass

            if len(created_paths) == 2:
                success_message = f"Created two expanded design layers:\n{created_paths[0][0]}\n{created_paths[1][0]}"
                if created_material_paths:
                    success_message += "\n\nCreated material layers:\n" + "\n".join(name for name, _path in created_material_paths)
                QMessageBox.information(
                    self,
                    "Success",
                    success_message
                )
            else:
                success_message = f"Created expanded design layer:\n{created_paths[0][0]}"
                if created_material_paths:
                    success_message += "\n\nCreated material layer(s):\n" + "\n".join(name for name, _path in created_material_paths)
                QMessageBox.information(
                    self,
                    "Success",
                    success_message
                )

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Expansion Failed", str(e))

# ======================================================================================================================================
#                                    *** Paste Dialog for Design and Material Data with Dependency Handling ***
# =====================================================================================================================================
class PasteDialog(QDialog):
    def __init__(self, copy_buffer, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Paste")
        self.copy_buffer = copy_buffer

        has_design = bool(self.copy_buffer.get("design"))
        has_material = bool(self.copy_buffer.get("material"))

        self.setFont(QFont("Segoe UI", 10))

        # ================= MAIN LAYOUT =================
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)

        # ================= TITLE =================
        title = QLabel("Paste Data")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #4A148C;")
        main_layout.addWidget(title)

        # ================= COPY INFO =================
        rng = self.copy_buffer.get("range", {})

        self.copy_from_km = float(rng.get("from_km", 0))
        self.copy_to_km   = float(rng.get("to_km", 0))

        self.copy_from_ch = float(rng.get("from_chainage", 0))
        self.copy_to_ch   = float(rng.get("to_chainage", 0))

        self.km_length = self.copy_to_km - self.copy_from_km
        self.chainage_length = self.copy_to_ch - self.copy_from_ch

        info_label = QLabel(
            f"Copied Range: KM {int(self.copy_from_km)}  |  "
            f"Chainage {self.copy_from_ch} → {self.copy_to_ch}"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #4A148C;
                font-size: 12px;
                padding: 2px;
            }
        """)
        main_layout.addWidget(info_label)

        # ================= CHAINAGE BOX =================
        chainage_box = QGroupBox("Chainage Range")
        chainage_box.setStyleSheet(self.group_style())

        grid = QGridLayout()
        grid.setSpacing(6)

        self.from_km       = QLineEdit()
        self.to_km         = QLineEdit()
        self.from_chainage = QLineEdit()
        self.to_chainage   = QLineEdit()

        for field in [self.from_km, self.to_km, self.from_chainage, self.to_chainage]:
            field.setMinimumHeight(30)
            field.setStyleSheet(self.input_style())

        grid.addWidget(QLabel("From KM"),       0, 0)
        grid.addWidget(self.from_km,            0, 1)
        grid.addWidget(QLabel("From Chainage"), 0, 2)
        grid.addWidget(self.from_chainage,      0, 3)

        grid.addWidget(QLabel("To KM"),         1, 0)
        grid.addWidget(self.to_km,              1, 1)
        grid.addWidget(QLabel("To Chainage"),   1, 2)
        grid.addWidget(self.to_chainage,        1, 3)

        chainage_box.setLayout(grid)
        main_layout.addWidget(chainage_box)

        # ================= VERIFY =================
        verify_layout = QHBoxLayout()

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setFixedWidth(100)
        self.verify_btn.setStyleSheet(self.button_style())

        verify_layout.addStretch()
        verify_layout.addWidget(self.verify_btn)
        verify_layout.addStretch()

        # ================= LAYER OPTIONS =================
        self.layer_box = QGroupBox("Select Layer")
        self.layer_box.setStyleSheet(self.group_style())
        # self.layer_layout = QVBoxLayout()
        # self.layer_layout.setSpacing(6)
        self.layer_layout = QVBoxLayout()
        self.layer_layout.setSpacing(6)
        self.layer_layout.setContentsMargins(10, 8, 10, 8)

        self.design_cb  = QCheckBox("Design Layer")
        self.material_cb = QCheckBox("Material Layer")
        self.all_cb      = QCheckBox("All")

        checkbox_style = """
            QCheckBox {
                spacing: 8px;
                padding: 4px;
                font-size: 12px;
                color: #333;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
            }
            """

        self.design_cb.setStyleSheet(checkbox_style)
        self.material_cb.setStyleSheet(checkbox_style)
        self.all_cb.setStyleSheet(checkbox_style)

        # ===== CLEAR (safety) =====
        for i in reversed(range(self.layer_layout.count())):
            w = self.layer_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        # ===== SHOW BASED ON COPY =====
        if has_design and not has_material:
            self.layer_layout.addWidget(self.design_cb)
            self.material_cb.hide()
            self.all_cb.hide()

        elif has_material and not has_design:
            self.layer_layout.addWidget(self.material_cb)
            self.design_cb.hide()
            self.all_cb.hide()

        elif has_design and has_material:
            self.layer_layout.addWidget(self.design_cb)
            self.layer_layout.addWidget(self.material_cb)
            self.layer_layout.addWidget(self.all_cb)

        self.layer_box.setLayout(self.layer_layout)
        self.layer_box.setVisible(False)

        main_layout.addLayout(verify_layout)
        main_layout.addWidget(self.layer_box)

        # ================= FOOTER =================
        footer = QHBoxLayout()

        self.paste_btn  = QPushButton("Paste")
        self.paste_btn.setEnabled(False)
        self.paste_btn.setStyleSheet(self.button_style())

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(self.cancel_style())

        footer.addStretch()
        footer.addWidget(self.paste_btn)
        footer.addWidget(self.cancel_btn)

        main_layout.addLayout(footer)

        self.setLayout(main_layout)

        # ================= CONNECTIONS =================
        self.from_km.textChanged.connect(self.update_to_km)
        self.from_chainage.textChanged.connect(self.update_to_chainage)
        self.verify_btn.clicked.connect(self.verify_range)
        self.cancel_btn.clicked.connect(self.reject)
        self.paste_btn.clicked.connect(self.accept)

        self.design_cb.stateChanged.connect(self.handle_design_click)
        self.material_cb.stateChanged.connect(self.handle_material_click)
        self.all_cb.stateChanged.connect(self.handle_all_checkbox)

        self.from_km.textChanged.connect(self.reset_verify_button)
        self.to_km.textChanged.connect(self.reset_verify_button)
        self.from_chainage.textChanged.connect(self.reset_verify_button)
        self.to_chainage.textChanged.connect(self.reset_verify_button)

    # ================= AUTO FILL =================
    def update_to_km(self):
        try:
            from_km = float(self.from_km.text())
            to_km = from_km + self.km_length

            self.to_km.blockSignals(True)
            self.to_km.setText(str(int(to_km)))
            self.to_km.blockSignals(False)

        except ValueError:
            pass

    def update_to_chainage(self):
        try:
            from_ch = float(self.from_chainage.text())
            to_ch = from_ch + self.chainage_length

            self.to_chainage.blockSignals(True)
            self.to_chainage.setText(str(round(to_ch, 3)))
            self.to_chainage.blockSignals(False)

        except ValueError:
            pass

    # ================= STYLES =================
    def group_style(self):
        return """
        QGroupBox {
            border: 2px solid #9C27B0;
            border-radius: 10px;
            margin-top: 10px;
            padding: 10px;
            font-weight: bold;
            color: #4A148C;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 6px;
        }
        """

    def input_style(self):
        return """
        QLineEdit {
            background-color: white;
            border: 2px solid #BA68C8;
            border-radius: 6px;
            padding: 6px;
            font-size: 12px;
        }
        QLineEdit:focus {
            border: 2px solid #8E24AA;
        }
        """

    def button_style(self):
        return """
        QPushButton {
            background-color: #8E24AA;
            color: white;
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 12px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #7B1FA2;
        }
        """

    def cancel_style(self):
        return """
        QPushButton {
            background-color: #CE93D8;
            color: black;
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 12px;
            min-width: 80px;
        }
        """
    

    def verify_range(self):
        try:
            from_km       = float(self.from_km.text())
            to_km         = float(self.to_km.text())
            from_chainage = float(self.from_chainage.text())
            to_chainage   = float(self.to_chainage.text())

        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values")
            return

        # ❗ Basic validation
        if from_km > to_km or from_chainage > to_chainage:
            QMessageBox.warning(self, "Invalid Range", "From value cannot be greater than To value")
            return

        try:
            parent = self.parent()

            if not parent or not hasattr(parent, "current_worksheet_name"):
                QMessageBox.warning(self, "Error", "Worksheet not active")
                return

            worksheet_path = os.path.join(
                parent.WORKSHEETS_BASE_DIR,
                parent.current_worksheet_name
            )

            designs_path = os.path.join(worksheet_path, "designs")

            design_found = False

            self.loaded_design_json = None
            self.design_json_path   = None

            # ================= DESIGN VERIFY (ZERO LINE ONLY) =================
            if os.path.exists(designs_path):
                for layer in os.listdir(designs_path):
                    layer_path = os.path.join(designs_path, layer)
                    if not os.path.isdir(layer_path):
                        continue

                    json_file = os.path.join(layer_path, "design_construction_config.json")
                    if not os.path.exists(json_file):
                        continue

                    try:
                        with open(json_file, "r") as f:
                            data = json.load(f)
                    except:
                        continue

                    zero_line = data.get("design", {}).get("zero_line_config", {})

                    if not zero_line.get("zero_line_set"):
                        continue

                    # ===== Extract zero line range =====
                    zero_from_km = float(zero_line.get("point1", {}).get("from_km", 0))
                    zero_to_km   = float(zero_line.get("point2", {}).get("to_km", 0))

                    zero_from_ch = float(zero_line.get("point1", {}).get("from_chainage", 0))
                    zero_to_ch   = float(zero_line.get("point2", {}).get("to_chainage", 0))

                    # ===== VALIDATION =====
                    km_valid = (
                        zero_from_km <= from_km <= zero_to_km and
                        zero_from_km <= to_km   <= zero_to_km
                    )

                    ch_valid = (
                        zero_from_ch <= from_chainage <= zero_to_ch and
                        zero_from_ch <= to_chainage   <= zero_to_ch
                    )

                    if km_valid and ch_valid:
                        design_found = True
                        self.loaded_design_json = data
                        self.design_json_path   = json_file
                        break

            # ================= RESULT =================
            if not design_found:
                QMessageBox.warning(
                    self,
                    "Out of Range",
                    "Entered range is outside zero line configuration"
                )
                self.paste_btn.setEnabled(False)
                return

            # ================= VERIFIED =================
            self.verify_btn.setText("Verified")
            self.verify_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 8px;
                    padding: 6px 15px;
                    font-weight: bold;
                }
            """)

            self.layer_box.setVisible(True)
            self.paste_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def reset_verify_button(self):
        self.verify_btn.setText("Verify")
        self.verify_btn.setStyleSheet("""
        QPushButton {
            background-color: #9C27B0;
            color: white;
            border-radius: 8px;
            padding: 6px 15px;
        }
        QPushButton:hover {
            background-color: #7B1FA2;
        }
        """)

        if hasattr(self, "loaded_json"):
            del self.loaded_json


    def handle_design_click(self):
        if self.design_cb.isChecked():
            self.material_cb.blockSignals(True)
            self.material_cb.setChecked(False)
            self.material_cb.blockSignals(False)

            self.all_cb.blockSignals(True)
            self.all_cb.setChecked(False)
            self.all_cb.blockSignals(False)

    def handle_material_click(self):
        if self.material_cb.isChecked():
            self.design_cb.blockSignals(True)
            self.design_cb.setChecked(False)
            self.design_cb.blockSignals(False)

            self.all_cb.blockSignals(True)
            self.all_cb.setChecked(False)
            self.all_cb.blockSignals(False)

    def handle_all_checkbox(self):
        if self.all_cb.isChecked():
            self.design_cb.blockSignals(True)
            self.material_cb.blockSignals(True)

            self.design_cb.setChecked(True)
            self.material_cb.setChecked(True)

            self.design_cb.blockSignals(False)
            self.material_cb.blockSignals(False)

        else:
            self.design_cb.blockSignals(True)
            self.material_cb.blockSignals(True)

            self.design_cb.setChecked(False)
            self.material_cb.setChecked(False)

            self.design_cb.blockSignals(False)
            self.material_cb.blockSignals(False)

# ======================================================================================================================================
#                                   *** Under Pass Dialog ***
# ======================================================================================================================================
#                                   *** Share with Buddies Dialog ***
# ======================================================================================================================================
class ShareWithBuddiesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Share with Buddies")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Share functionality is currently under maintenance."))
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

# ======================================================================================================================================
#                                   *** Expanding Road Dialog ***
# ======================================================================================================================================
class ExpandingRoadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Expanding Road")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Expanding Road functionality is currently under maintenance."))
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

# ======================================================================================================================================
#                                   *** Copy Dialog ***
# ======================================================================================================================================
class CopyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Copy")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Copy functionality is currently under maintenance."))
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)


# ======================================================================================================================================
#                                   *** PasteDialog ***
# ======================================================================================================================================
class PasteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PasteDialog")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("PasteDialog functionality is currently under maintenance."))
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
# ======================================================================================================================================
class UnderPassDialog(QDialog):
    """Dialog for capturing Under Pass dimensional parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Under Pass")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #eef4ff, stop:1 #f8fbff);
            }
            QLabel {
                color: #1f2937;
                font-weight: 600;
            }
            QGroupBox {
                border: 2px solid #2f80ed;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: bold;
                color: #174ea6;
                background-color: rgba(255, 255, 255, 0.5);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 10px;
                background-color: #dbeafe;
                border-radius: 6px;
            }
            QLineEdit {
                border: 2px solid #93c5fd;
                border-radius: 8px;
                padding: 7px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #2563eb;
                background-color: #eff6ff;
            }
            QPushButton {
                border-radius: 18px;
                padding: 10px 16px;
                font-weight: bold;
                min-width: 96px;
                border: none;
            }
            QPushButton#okBtn {
                background-color: #16a34a;
                color: white;
            }
            QPushButton#okBtn:hover {
                background-color: #15803d;
            }
            QPushButton#cancelBtn {
                background-color: #e5e7eb;
                color: #111827;
            }
            QPushButton#cancelBtn:hover {
                background-color: #d1d5db;
            }
        """)

        # Collected values (populated on OK)
        self.under_pass_values = {}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        # Title
        title = QLabel("Under Pass Configuration")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #174ea6;")
        main_layout.addWidget(title)

        # Dimensions group
        dimensions_group = QGroupBox("Dimensions")
        grid = QGridLayout(dimensions_group)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        # Define the input fields: (label, key, placeholder)
        field_definitions = [
            ("Length", "length", "e.g. 20 m"),
            ("Width", "width", "e.g. 10 m"),
            ("Height", "height", "e.g. 6 m"),
            ("Wall Thickness", "wall_thickness", "e.g. 0.7 m"),
            ("Slab Thickness", "slab_thickness", "e.g. 0.7 m"),
            ("Bottom Thickness", "bottom_thickness", "e.g. 0.8 m"),
        ]

        self._field_edits = {}
        validator = QDoubleValidator(0.0, 1000000.0, 3)

        for row, (label_text, key, placeholder) in enumerate(field_definitions):
            label = QLabel(f"{label_text}:")
            edit = QLineEdit()
            edit.setValidator(validator)
            edit.setPlaceholderText(placeholder)
            edit.setMinimumHeight(32)
            grid.addWidget(label, row, 0)
            grid.addWidget(edit, row, 1)
            self._field_edits[key] = edit

        main_layout.addWidget(dimensions_group)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setObjectName("okBtn")
        self.ok_btn.clicked.connect(self._on_ok)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(self.ok_btn)
        btn_row.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_row)

    def _on_ok(self):
        """Collect the entered values and accept the dialog."""
        self.under_pass_values = {}
        for key, edit in self._field_edits.items():
            text = edit.text().strip()
            if text:
                try:
                    self.under_pass_values[key] = float(text)
                except ValueError:
                    self.under_pass_values[key] = 0.0
            else:
                self.under_pass_values[key] = 0.0
        self.accept()

# ======================================================================================================================================
#                                   *** Under Pass Preview Dialog ***
# ======================================================================================================================================
class UnderPassPreviewDialog(QDialog):
    """Dialog for previewing the Under Pass geometry based on user dimensions."""

    def __init__(self, dimensions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Under Pass Preview")
        self.setModal(True)
        self.resize(800, 600)
        self.dimensions = dimensions

        main_layout = QVBoxLayout(self)

        # Title
        title = QLabel("Under Pass Preview")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #174ea6;")
        main_layout.addWidget(title)

        # VTK Widget for 3D Preview
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        main_layout.addWidget(self.vtk_widget, stretch=1)

        # Buttons Layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.copy_paste_btn = QPushButton("Copy / Paste")
        self.copy_paste_btn.clicked.connect(self.on_copy_paste_clicked)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)

        # Style buttons similar to existing ones
        btn_style = """
            QPushButton {
                border-radius: 18px;
                padding: 10px 16px;
                font-weight: bold;
                min-width: 96px;
                border: none;
                background-color: #e5e7eb;
                color: #111827;
            }
            QPushButton:hover {
                background-color: #d1d5db;
            }
        """
        self.copy_paste_btn.setStyleSheet(btn_style)
        self.close_btn.setStyleSheet(btn_style)

        btn_layout.addWidget(self.copy_paste_btn)
        btn_layout.addWidget(self.close_btn)

        main_layout.addLayout(btn_layout)

        self.setup_vtk_scene()

    def setup_vtk_scene(self):
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(0.9, 0.9, 0.95)
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

        interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        style = vtkInteractorStyleTrackballCamera()
        interactor.SetInteractorStyle(style)

        # Parse dimensions
        length = self.dimensions.get("length", 20.0)
        width = self.dimensions.get("width", 10.0)
        height = self.dimensions.get("height", 6.0)
        wall_t = self.dimensions.get("wall_thickness", 0.7)
        slab_t = self.dimensions.get("slab_thickness", 0.7)
        bottom_t = self.dimensions.get("bottom_thickness", 0.8)

        append_filter = vtkAppendPolyData()

        # Build geometry (assumes overall width=width, overall height=height)
        # Top Slab
        top_slab = vtkCubeSource()
        top_slab.SetXLength(width)
        top_slab.SetYLength(length)
        top_slab.SetZLength(slab_t)
        top_slab.SetCenter(0, 0, height/2.0 - slab_t/2.0)
        append_filter.AddInputConnection(top_slab.GetOutputPort())

        # Bottom Slab
        bottom_slab = vtkCubeSource()
        bottom_slab.SetXLength(width)
        bottom_slab.SetYLength(length)
        bottom_slab.SetZLength(bottom_t)
        bottom_slab.SetCenter(0, 0, -height/2.0 + bottom_t/2.0)
        append_filter.AddInputConnection(bottom_slab.GetOutputPort())

        # Left Wall
        left_wall = vtkCubeSource()
        left_wall.SetXLength(wall_t)
        left_wall.SetYLength(length)
        wall_height = height - slab_t - bottom_t
        left_wall.SetZLength(wall_height if wall_height > 0 else 0.1)
        left_wall.SetCenter(-width/2.0 + wall_t/2.0, 0, (bottom_t - slab_t)/2.0)
        append_filter.AddInputConnection(left_wall.GetOutputPort())

        # Right Wall
        right_wall = vtkCubeSource()
        right_wall.SetXLength(wall_t)
        right_wall.SetYLength(length)
        right_wall.SetZLength(wall_height if wall_height > 0 else 0.1)
        right_wall.SetCenter(width/2.0 - wall_t/2.0, 0, (bottom_t - slab_t)/2.0)
        append_filter.AddInputConnection(right_wall.GetOutputPort())

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(append_filter.GetOutputPort())

        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.5, 0.5, 0.5)

        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        
        # Initialize
        interactor.Initialize()

    def on_copy_paste_clicked(self):
        # Get active design layer name from the parent application
        active_layer_name = ""
        parent_ui = self.parent()
        if parent_ui and hasattr(parent_ui, 'current_design_layer_path'):
            path = getattr(parent_ui, 'current_design_layer_path', None)
            if path:
                import os
                active_layer_name = os.path.basename(path)
        
        dialog = UnderPassPlacementDialog(self, active_design_layer=active_layer_name)
        if dialog.exec_() == QDialog.Accepted:
            placement_values = dialog.placement_values
            if hasattr(parent_ui, "place_under_pass"):
                parent_ui.place_under_pass(self.dimensions, placement_values)
            self.accept()

# ======================================================================================================================================
#                                   *** Under Pass Placement Dialog ***
# ======================================================================================================================================
class UnderPassPlacementDialog(QDialog):
    """Dialog for collecting placement info for the Under Pass."""

    def __init__(self, parent=None, active_design_layer=""):
        super().__init__(parent)
        self._active_design_layer = active_design_layer
        self.setWindowTitle("Under Pass Placement")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #eef4ff, stop:1 #f8fbff);
            }
            QLabel {
                color: #1f2937;
                font-weight: 600;
            }
            QGroupBox {
                border: 2px solid #2f80ed;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: bold;
                color: #174ea6;
                background-color: rgba(255, 255, 255, 0.5);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 10px;
                background-color: #dbeafe;
                border-radius: 6px;
            }
            QLineEdit {
                border: 2px solid #93c5fd;
                border-radius: 8px;
                padding: 7px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #2563eb;
                background-color: #eff6ff;
            }
            QPushButton {
                border-radius: 18px;
                padding: 10px 16px;
                font-weight: bold;
                min-width: 96px;
                border: none;
            }
            QPushButton#okBtn {
                background-color: #16a34a;
                color: white;
            }
            QPushButton#okBtn:hover {
                background-color: #15803d;
            }
        """)

        self.placement_values = {}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        # Title
        title = QLabel("Under Pass Placement")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #174ea6;")
        main_layout.addWidget(title)

        # Placement Configuration group
        config_group = QGroupBox("Placement Configuration")
        grid = QGridLayout(config_group)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        # Fields definition
        field_definitions = [
            ("Design Layer", "design_layer", ""),
            ("KM", "km", ""),
            ("Chainage", "chainage", ""),
            ("Depth From Road Surface", "depth", "e.g. 0.5 m"),
        ]

        self._field_edits = {}
        for row, (label_text, key, placeholder) in enumerate(field_definitions):
            label = QLabel(f"{label_text}:")
            edit = QLineEdit()
            if placeholder:
                edit.setPlaceholderText(placeholder)
            # Auto-populate Design Layer from active selection
            if key == "design_layer" and self._active_design_layer:
                edit.setText(self._active_design_layer)
                edit.setReadOnly(True)
                edit.setStyleSheet(edit.styleSheet() + "background-color: #f0f4f8; color: #374151;")
            edit.setMinimumHeight(32)
            grid.addWidget(label, row, 0)
            grid.addWidget(edit, row, 1)
            self._field_edits[key] = edit

        main_layout.addWidget(config_group)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setObjectName("okBtn")
        self.ok_btn.clicked.connect(self._on_ok)

        btn_row.addWidget(self.ok_btn)
        main_layout.addLayout(btn_row)

    def _on_ok(self):
        """Temporarily store values and accept."""
        self.placement_values = {}
        for key, edit in self._field_edits.items():
            self.placement_values[key] = edit.text().strip()
        self.accept()

# ===========================================================================================================================
# ** TUNNEL CONFIGURATION DIALOG **
# ===========================================================================================================================
class TunnelConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tunnel Configuration")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.parent = parent
        self.arc_points = []
        self.tunnel_id = None
        
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QLineEdit {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Tunnel Configuration")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1565C0;")
        layout.addWidget(title)
        
        # Grid for KM and Chainage
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(QLabel("Tunnel Start KM:"), 0, 0)
        self.start_km = QLineEdit()
        self.start_km.setPlaceholderText("e.g. 1")
        grid.addWidget(self.start_km, 0, 1)
        
        grid.addWidget(QLabel("Start Chainage:"), 0, 2)
        self.start_ch = QLineEdit()
        self.start_ch.setPlaceholderText("e.g. 200")
        grid.addWidget(self.start_ch, 0, 3)
        
        grid.addWidget(QLabel("Tunnel End KM:"), 1, 0)
        self.end_km = QLineEdit()
        self.end_km.setPlaceholderText("e.g. 1")
        grid.addWidget(self.end_km, 1, 1)
        
        grid.addWidget(QLabel("End Chainage:"), 1, 2)
        self.end_ch = QLineEdit()
        self.end_ch.setPlaceholderText("e.g. 800")
        grid.addWidget(self.end_ch, 1, 3)
        
        layout.addLayout(grid)
        
        # Verify Button
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #1E88E5; color: white;")
        self.verify_btn.clicked.connect(self.verify_chainages)
        layout.addWidget(self.verify_btn)
        
        # Thickness layout
        thick_layout = QHBoxLayout()
        thick_layout.addWidget(QLabel("Tunnel Wall Thickness:"))
        self.thickness = QLineEdit()
        self.thickness.setText("0.5")
        thick_layout.addWidget(self.thickness)
        layout.addLayout(thick_layout)
        
        # Mark ARC button
        self.mark_arc_btn = QPushButton("Mark the ARC")
        self.mark_arc_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.mark_arc_btn.clicked.connect(self.start_arc_marking)
        layout.addWidget(self.mark_arc_btn)
        
        # Status Label for ARC points
        self.status_label = QLabel("ARC Points: Not marked yet (requires 3 points)")
        self.status_label.setStyleSheet("color: red; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # Buttons layout at the bottom
        buttons_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.ok_btn.clicked.connect(self.on_ok_clicked)
        buttons_layout.addWidget(self.ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
    def verify_chainages(self):
        try:
            skm = float(self.start_km.text() or 0.0)
            sch = float(self.start_ch.text() or 0.0)
            ekm = float(self.end_km.text() or 0.0)
            ech = float(self.end_ch.text() or 0.0)
        except:
            QMessageBox.warning(self, "Invalid Input", "Please enter numeric values for KM and Chainage.")
            return
            
        start_abs = skm * 1000 + sch
        end_abs = ekm * 1000 + ech
        
        if end_abs <= start_abs:
            QMessageBox.warning(self, "Invalid Range", "End chainage must be greater than Start chainage.")
            return
            
        # Get baseline range from parent
        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        if not layer_folder or not os.path.exists(layer_folder):
            QMessageBox.warning(self, "Error", "No active design layer folder found to verify range.")
            return
            
        try:
            from json_manager import DesignConstructionManager
            j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'road_surface_baseline')
            if not j:
                j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'surface_baseline')
            
            if not j:
                QMessageBox.warning(self, "No Baseline Data", "No surface or road surface baseline found in design layer to verify chainages.")
                return
                
            global_start_offset = 0.0
            if hasattr(self.parent, '_get_global_start_offset'):
                global_start_offset = self.parent._get_global_start_offset(layer_folder)
            else:
                polylines = j.get("polylines", [])
                if polylines:
                    start_str = polylines[0].get("start_chainage_str", "")
                    if start_str:
                        start_str = start_str.replace(" ", "")
                        if "+" in start_str:
                            parts = start_str.split("+")
                            global_start_offset = float(parts[0]) * 1000 + float(parts[1])
                        else:
                            global_start_offset = float(start_str)

            chs = []
            for poly in j.get("polylines", []):
                for pt in poly.get("points", []):
                    chs.append(pt['chainage_m'] + global_start_offset)
            if not chs:
                QMessageBox.warning(self, "No Points", "Baseline has no chainage points.")
                return
                
            min_ch = min(chs)
            max_ch = max(chs)
            
            if start_abs < min_ch or end_abs > max_ch:
                QMessageBox.warning(self, "Out of Range", f"Chainages are out of design layer range.\nDesign Layer Range: KM {min_ch//1000:.0f} + {min_ch%1000:.2f}m to KM {max_ch//1000:.0f} + {max_ch%1000:.2f}m")
            else:
                QMessageBox.information(self, "Verification Successful", "Verification successful! Start and End chainages are within the design layer range.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to verify chainages: {e}")
            
    def start_arc_marking(self):
        self.hide()
        self.parent.start_arc_marking(self)
        
    def set_arc_points(self, points):
        self.arc_points = points
        if len(points) == 3:
            self.status_label.setText(f"ARC Points: 3 points marked successfully!")
            self.status_label.setStyleSheet("color: green; font-size: 11px;")
        else:
            self.status_label.setText(f"ARC Points: {len(points)} marked (requires 3)")
            self.status_label.setStyleSheet("color: red; font-size: 11px;")
            
    def on_ok_clicked(self):
        # Validation
        try:
            skm = float(self.start_km.text() or 0.0)
            sch = float(self.start_ch.text() or 0.0)
            ekm = float(self.end_km.text() or 0.0)
            ech = float(self.end_ch.text() or 0.0)
            thick = float(self.thickness.text() or 0.5)
        except:
            QMessageBox.warning(self, "Invalid Input", "Please ensure all KM, Chainage, and Thickness inputs are numeric.")
            return
            
        if len(self.arc_points) < 3:
            QMessageBox.warning(self, "Mark ARC Required", "Please click 'Mark the ARC' and click 3 points on the point cloud first.")
            return
            
        self.accept()
        
    def get_data(self):
        if not getattr(self, 'tunnel_id', None):
            skm = int(float(self.start_km.text() or 0.0))
            sch = int(float(self.start_ch.text() or 0.0))
            if hasattr(self.parent, '_generate_tunnel_id'):
                self.tunnel_id = self.parent._generate_tunnel_id(skm, sch)
            else:
                self.tunnel_id = f"TN_{skm:03d}_{sch:03d}_001"

        return {
            "tunnel_id": self.tunnel_id,
            "id": self.tunnel_id,
            "start_km": float(self.start_km.text() or 0.0),
            "start_chainage": float(self.start_ch.text() or 0.0),
            "end_km": float(self.end_km.text() or 0.0),
            "end_chainage": float(self.end_ch.text() or 0.0),
            "wall_thickness": float(self.thickness.text() or 0.5),
            "arc_points": [[float(p[0]), float(p[1]), float(p[2])] for p in self.arc_points]
        }

#### Mayur 17-7-2026 Tunnel
        # ===========================================================================================================================
# ** TUNNEL CONFIGURATION DIALOG **
# ===========================================================================================================================
class TunnelConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tunnel Configuration")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.parent = parent
        self.arc_points = []
        self.tunnel_id = None
        
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QLineEdit {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Tunnel Configuration")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1565C0;")
        layout.addWidget(title)
        
        # Grid for KM and Chainage
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(QLabel("Tunnel Start KM:"), 0, 0)
        self.start_km = QLineEdit()
        self.start_km.setPlaceholderText("e.g. 1")
        grid.addWidget(self.start_km, 0, 1)
        
        grid.addWidget(QLabel("Start Chainage:"), 0, 2)
        self.start_ch = QLineEdit()
        self.start_ch.setPlaceholderText("e.g. 200")
        grid.addWidget(self.start_ch, 0, 3)
        
        grid.addWidget(QLabel("Tunnel End KM:"), 1, 0)
        self.end_km = QLineEdit()
        self.end_km.setPlaceholderText("e.g. 1")
        grid.addWidget(self.end_km, 1, 1)
        
        grid.addWidget(QLabel("End Chainage:"), 1, 2)
        self.end_ch = QLineEdit()
        self.end_ch.setPlaceholderText("e.g. 800")
        grid.addWidget(self.end_ch, 1, 3)
        
        layout.addLayout(grid)
        
        # Verify Button
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #1E88E5; color: white;")
        self.verify_btn.clicked.connect(self.verify_chainages)
        layout.addWidget(self.verify_btn)
        
        # Thickness layout
        thick_layout = QHBoxLayout()
        thick_layout.addWidget(QLabel("Tunnel Wall Thickness:"))
        self.thickness = QLineEdit()
        self.thickness.setText("0.5")
        thick_layout.addWidget(self.thickness)
        layout.addLayout(thick_layout)
        
        # Mark ARC button
        self.mark_arc_btn = QPushButton("Mark the ARC")
        self.mark_arc_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.mark_arc_btn.clicked.connect(self.start_arc_marking)
        layout.addWidget(self.mark_arc_btn)
        
        # Status Label for ARC points
        self.status_label = QLabel("ARC Points: Not marked yet (requires 3 points)")
        self.status_label.setStyleSheet("color: red; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # Buttons layout at the bottom
        buttons_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.ok_btn.clicked.connect(self.on_ok_clicked)
        buttons_layout.addWidget(self.ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
    def verify_chainages(self):
        try:
            skm = float(self.start_km.text() or 0.0)
            sch = float(self.start_ch.text() or 0.0)
            ekm = float(self.end_km.text() or 0.0)
            ech = float(self.end_ch.text() or 0.0)
        except:
            QMessageBox.warning(self, "Invalid Input", "Please enter numeric values for KM and Chainage.")
            return
            
        start_abs = skm * 1000 + sch
        end_abs = ekm * 1000 + ech
        
        if end_abs <= start_abs:
            QMessageBox.warning(self, "Invalid Range", "End chainage must be greater than Start chainage.")
            return
            
        # Get baseline range from parent
        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        if not layer_folder or not os.path.exists(layer_folder):
            QMessageBox.warning(self, "Error", "No active design layer folder found to verify range.")
            return
            
        try:
            from json_manager import DesignConstructionManager
            j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'road_surface_baseline')
            if not j:
                j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'surface_baseline')
            
            if not j:
                QMessageBox.warning(self, "No Baseline Data", "No surface or road surface baseline found in design layer to verify chainages.")
                return
                
            global_start_offset = 0.0
            if hasattr(self.parent, '_get_global_start_offset'):
                global_start_offset = self.parent._get_global_start_offset(layer_folder)
            else:
                polylines = j.get("polylines", [])
                if polylines:
                    start_str = polylines[0].get("start_chainage_str", "")
                    if start_str:
                        start_str = start_str.replace(" ", "")
                        if "+" in start_str:
                            parts = start_str.split("+")
                            global_start_offset = float(parts[0]) * 1000 + float(parts[1])
                        else:
                            global_start_offset = float(start_str)

            chs = []
            for poly in j.get("polylines", []):
                for pt in poly.get("points", []):
                    chs.append(pt['chainage_m'] + global_start_offset)
            if not chs:
                QMessageBox.warning(self, "No Points", "Baseline has no chainage points.")
                return
                
            min_ch = min(chs)
            max_ch = max(chs)
            
            if start_abs < min_ch or end_abs > max_ch:
                QMessageBox.warning(self, "Out of Range", f"Chainages are out of design layer range.\nDesign Layer Range: KM {min_ch//1000:.0f} + {min_ch%1000:.2f}m to KM {max_ch//1000:.0f} + {max_ch%1000:.2f}m")
            else:
                QMessageBox.information(self, "Verification Successful", "Verification successful! Start and End chainages are within the design layer range.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to verify chainages: {e}")
            
    def start_arc_marking(self):
        self.hide()
        self.parent.start_arc_marking(self)
        
    def set_arc_points(self, points):
        self.arc_points = points
        if len(points) == 3:
            self.status_label.setText(f"ARC Points: 3 points marked successfully!")
            self.status_label.setStyleSheet("color: green; font-size: 11px;")
        else:
            self.status_label.setText(f"ARC Points: {len(points)} marked (requires 3)")
            self.status_label.setStyleSheet("color: red; font-size: 11px;")
            
    def on_ok_clicked(self):
        # Validation
        try:
            skm = float(self.start_km.text() or 0.0)
            sch = float(self.start_ch.text() or 0.0)
            ekm = float(self.end_km.text() or 0.0)
            ech = float(self.end_ch.text() or 0.0)
            thick = float(self.thickness.text() or 0.5)
        except:
            QMessageBox.warning(self, "Invalid Input", "Please ensure all KM, Chainage, and Thickness inputs are numeric.")
            return
            
        if len(self.arc_points) < 3:
            QMessageBox.warning(self, "Mark ARC Required", "Please click 'Mark the ARC' and click 3 points on the point cloud first.")
            return
            
        self.accept()
        
    def get_data(self):
        if not getattr(self, 'tunnel_id', None):
            skm = int(float(self.start_km.text() or 0.0))
            sch = int(float(self.start_ch.text() or 0.0))
            if hasattr(self.parent, '_generate_tunnel_id'):
                self.tunnel_id = self.parent._generate_tunnel_id(skm, sch)
            else:
                self.tunnel_id = f"TN_{skm:03d}_{sch:03d}_001"
            
        return {
            "tunnel_id": self.tunnel_id,
            "id": self.tunnel_id,
            "start_km": float(self.start_km.text() or 0.0),
            "start_chainage": float(self.start_ch.text() or 0.0),
            "end_km": float(self.end_km.text() or 0.0),
            "end_chainage": float(self.end_ch.text() or 0.0),
            "wall_thickness": float(self.thickness.text() or 0.5),
            "arc_points": [[float(p[0]), float(p[1]), float(p[2])] for p in self.arc_points]
        }

########### Mayur Wakhare 1-7-2026 Upadate code for tunnel Light  
class TunnelLightDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tunnel Light")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.selected_option = "single"
        self.parent = parent
        self.verified = False
        self.multi_verified = False

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QRadioButton { font-size: 13px; padding: 6px; }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #888;
                border-radius: 10px;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #388E3C;
            }
            QLineEdit {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QComboBox {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        ## Mayur Wakhare 3-7-2026 Tunnel light Dialog box Design scroll
        # ── Scroll Area wrapper ──
        from PyQt5.QtWidgets import QScrollArea
        from PyQt5.QtCore import Qt as QtCore_Qt

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QtCore_Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(QtCore_Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #F5F5F5; }")
        outer_layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_container.setStyleSheet("background-color: #F5F5F5;")
        scroll_area.setWidget(scroll_container)

        layout = QVBoxLayout(scroll_container)
        ###########################################################
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Tunnel Light")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1565C0;")
        layout.addWidget(title)

        # ── Tunnel Selection ──
        tunnel_sel_group = QGroupBox("Tunnel Selection")
        tunnel_sel_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        tunnel_sel_layout = QHBoxLayout(tunnel_sel_group)
        tunnel_sel_layout.addWidget(QLabel("Tunnel ID:"))
        self.tunnel_combo = QComboBox()
        self.tunnel_combo.setStyleSheet("padding: 4px; border: 1px solid #BBB; border-radius: 4px;")
        tunnel_sel_layout.addWidget(self.tunnel_combo)
        layout.addWidget(tunnel_sel_group)

        # Radio buttons
        self.single_radio = QRadioButton("Single Light")
        self.multiple_radio = QRadioButton("Multiple Lights")
        self.single_radio.setChecked(True)

        self.light_group = QButtonGroup(self)
        self.light_group.addButton(self.single_radio)
        self.light_group.addButton(self.multiple_radio)

        layout.addWidget(self.single_radio)
        layout.addWidget(self.multiple_radio)

        # ── Single Light Controls ──
        self.single_light_container = QWidget()
        single_layout = QVBoxLayout(self.single_light_container)
        single_layout.setContentsMargins(0, 5, 0, 0)
        single_layout.setSpacing(10)

        # KM, Chainage, Interval grid
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("KM:"), 0, 0)
        self.km_input = QLineEdit()
        self.km_input.setPlaceholderText("e.g. 1")
        grid.addWidget(self.km_input, 0, 1)

        grid.addWidget(QLabel("Chainage:"), 0, 2)
        self.chainage_input = QLineEdit()
        self.chainage_input.setPlaceholderText("e.g. 200")
        grid.addWidget(self.chainage_input, 0, 3)

        grid.addWidget(QLabel("Interval:"), 1, 0)
        self.interval_input = QLineEdit()
        self.interval_input.setText("20")
        grid.addWidget(self.interval_input, 1, 1)

        single_layout.addLayout(grid)

        # Verify button
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #1E88E5; color: white;")
        self.verify_btn.clicked.connect(self.verify_chainage)
        single_layout.addWidget(self.verify_btn)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
        single_layout.addWidget(self.status_label)

        # ── Post-verification controls (visible but disabled initially) ──
        self.post_verify_container = QWidget()
        post_layout = QGridLayout(self.post_verify_container)
        post_layout.setSpacing(10)
        post_layout.setContentsMargins(0, 0, 0, 0)

        self.arc_label = QLabel("ARC Reference:")
        post_layout.addWidget(self.arc_label, 0, 0)
        self.arc_combo = QComboBox()
        self.arc_combo.addItems(["Left Side (1)", "Top / Center (2)", "Right Side (3)"])
        self.arc_combo.setEnabled(False)
        post_layout.addWidget(self.arc_combo, 0, 1)

        self.distance_label = QLabel("Enter Distance from Right Side (1):")
        post_layout.addWidget(self.distance_label, 1, 0)
        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText("Enter distance")
        self.distance_input.setValidator(QDoubleValidator(0.0, 99999.0, 3))
        self.distance_input.setEnabled(False)
        post_layout.addWidget(self.distance_input, 1, 1)
        
        self.arc_combo.currentTextChanged.connect(
            lambda text: self.distance_label.setText(f"Enter Distance from {text}:")
        )

        single_layout.addWidget(self.post_verify_container)

        layout.addWidget(self.single_light_container)

        # ── Multiple Lights Controls ──
        self.multiple_light_container = QWidget()
        multi_layout = QVBoxLayout(self.multiple_light_container)
        multi_layout.setContentsMargins(0, 5, 0, 0)
        multi_layout.setSpacing(10)

        multi_grid = QGridLayout()
        
        multi_grid.addWidget(QLabel("Start KM:"), 0, 0)
        self.multi_start_km_input = QLineEdit()
        self.multi_start_km_input.setPlaceholderText("e.g. 101")
        multi_grid.addWidget(self.multi_start_km_input, 0, 1)

        multi_grid.addWidget(QLabel("+"), 0, 2)
        self.multi_start_chainage_input = QLineEdit()
        self.multi_start_chainage_input.setPlaceholderText("e.g. 0")
        multi_grid.addWidget(self.multi_start_chainage_input, 0, 3)

        multi_grid.addWidget(QLabel("End KM:"), 1, 0)
        self.multi_end_km_input = QLineEdit()
        self.multi_end_km_input.setPlaceholderText("e.g. 101")
        multi_grid.addWidget(self.multi_end_km_input, 1, 1)

        multi_grid.addWidget(QLabel("+"), 1, 2)
        self.multi_end_chainage_input = QLineEdit()
        self.multi_end_chainage_input.setPlaceholderText("e.g. 200")
        multi_grid.addWidget(self.multi_end_chainage_input, 1, 3)

        multi_grid.addWidget(QLabel("Interval (m):"), 2, 0)
        self.multi_interval_input = QLineEdit()
        self.multi_interval_input.setText("20")
        multi_grid.addWidget(self.multi_interval_input, 2, 1)

        multi_layout.addLayout(multi_grid)

        self.multi_verify_btn = QPushButton("Verify")
        self.multi_verify_btn.setStyleSheet("background-color: #1E88E5; color: white;")
        self.multi_verify_btn.clicked.connect(self.verify_multi_chainage)
        multi_layout.addWidget(self.multi_verify_btn)

        self.multi_status_label = QLabel("")
        self.multi_status_label.setStyleSheet("color: #888; font-size: 11px;")
        multi_layout.addWidget(self.multi_status_label)

        self.multi_post_verify_container = QWidget()
        multi_post_layout = QGridLayout(self.multi_post_verify_container)
        multi_post_layout.setSpacing(10)
        multi_post_layout.setContentsMargins(0, 0, 0, 0)

        self.multi_arc_label = QLabel("ARC Reference:")
        multi_post_layout.addWidget(self.multi_arc_label, 0, 0)
        import PyQt5.QtWidgets as _qt_widgets
        
        self.multi_arc_checkbox_layout = _qt_widgets.QVBoxLayout()
        self.multi_arc_cb1 = _qt_widgets.QCheckBox("Left Side (1)")
        self.multi_arc_cb2 = _qt_widgets.QCheckBox("Top / Center (2)")
        self.multi_arc_cb3 = _qt_widgets.QCheckBox("Right Side (3)")
        self.multi_arc_cb1.setEnabled(False)
        self.multi_arc_cb2.setEnabled(False)
        self.multi_arc_cb3.setEnabled(False)
        self.multi_arc_checkbox_layout.addWidget(self.multi_arc_cb1)
        self.multi_arc_checkbox_layout.addWidget(self.multi_arc_cb2)
        self.multi_arc_checkbox_layout.addWidget(self.multi_arc_cb3)
        multi_post_layout.addLayout(self.multi_arc_checkbox_layout, 0, 1)

        self.multi_distance_container = _qt_widgets.QWidget()
        self.multi_distance_layout = _qt_widgets.QVBoxLayout(self.multi_distance_container)
        self.multi_distance_layout.setContentsMargins(0, 0, 0, 0)
        multi_post_layout.addWidget(self.multi_distance_container, 1, 0, 1, 2)

        self.multi_distance_inputs = {}

        self.multi_arc_cb1.stateChanged.connect(lambda state: self.update_multi_distance_inputs("Right Side (1)", state))
        self.multi_arc_cb2.stateChanged.connect(lambda state: self.update_multi_distance_inputs("Top / Center (2)", state))
        self.multi_arc_cb3.stateChanged.connect(lambda state: self.update_multi_distance_inputs("Left Side (3)", state))

        multi_layout.addWidget(self.multi_post_verify_container)
        ### Mayur Wakhare 3-7-2026 Tunnel dialog box automatic value put for start km and end km
        # ── Placement Summary (read-only preview) ──
        self.multi_summary_label = QLabel("")
        self.multi_summary_label.setWordWrap(True)
        self.multi_summary_label.setStyleSheet(
            "background-color: #E8F5E9; border: 1px solid #A5D6A7; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #333; font-weight: normal;"
        )
        self.multi_summary_label.setVisible(False)
        multi_layout.addWidget(self.multi_summary_label)

        # Connect input changes to auto-update summary
        self.multi_start_km_input.textChanged.connect(self._update_multi_summary)
        self.multi_start_chainage_input.textChanged.connect(self._update_multi_summary)
        self.multi_end_km_input.textChanged.connect(self._update_multi_summary)
        self.multi_end_chainage_input.textChanged.connect(self._update_multi_summary)
        self.multi_interval_input.textChanged.connect(self._update_multi_summary)
        self.multi_arc_cb1.stateChanged.connect(lambda _: self._update_multi_summary())
        self.multi_arc_cb2.stateChanged.connect(lambda _: self._update_multi_summary())
        self.multi_arc_cb3.stateChanged.connect(lambda _: self._update_multi_summary())
        ##########################################################

        self.multiple_light_container.setVisible(False)
        layout.addWidget(self.multiple_light_container)

        # ── OK / Cancel / Undo ──
        buttons_layout = QHBoxLayout()

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        ok_btn.clicked.connect(self.on_ok_clicked)
        buttons_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.undo_btn.clicked.connect(self.on_undo_clicked)
        buttons_layout.addWidget(self.undo_btn)

        self.undo_once_btn = QPushButton("Undo Once")
        self.undo_once_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.undo_once_btn.clicked.connect(self.on_undo_once_clicked)
        buttons_layout.addWidget(self.undo_once_btn)

        self.undo_all_btn = QPushButton("Undo All")
        self.undo_all_btn.setStyleSheet("background-color: #F44336; color: white;")
        self.undo_all_btn.clicked.connect(self.on_undo_all_clicked)
        buttons_layout.addWidget(self.undo_all_btn)

        layout.addLayout(buttons_layout)
        
        # Connect radio toggle
        self.single_radio.toggled.connect(self.on_mode_toggled)
        
        self.update_undo_state()
        ## Mayur Wakhare 3-7-2026 Tunnel light automatic value put up from design file
        # ── Auto-populate chainage from tunnel ──
        tunnel_found = False
        t_start_km, t_start_ch, t_end_km, t_end_ch = "", "", "", ""
        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        import os
        if layer_folder and os.path.exists(layer_folder):
            try:
                from json_manager import DesignConstructionManager
                m_data = DesignConstructionManager.load_master(layer_folder)
                t_conf = m_data.get("design", {}).get("tunnel", {})
                if t_conf and "start_km" in t_conf:
                    t_start_km = str(t_conf.get("start_km", ""))
                    t_start_ch = str(t_conf.get("start_chainage", ""))
                    t_end_km = str(t_conf.get("end_km", ""))
                    t_end_ch = str(t_conf.get("end_chainage", ""))
                    tunnel_found = True
            except Exception:
                pass
                
        if tunnel_found:
            # Set integer part if it ends with .0 for cleaner display
            def clean_str(val):
                return val[:-2] if val.endswith(".0") else val
                
            self.km_input.setText(clean_str(t_start_km))
            self.chainage_input.setText(clean_str(t_start_ch))
            self.multi_start_km_input.setText(clean_str(t_start_km))
            self.multi_start_chainage_input.setText(clean_str(t_start_ch))
            self.multi_end_km_input.setText(clean_str(t_end_km))
            self.multi_end_chainage_input.setText(clean_str(t_end_ch))
        else:
            self.status_label.setText("No active tunnel found.")
            self.multi_status_label.setText("No active tunnel found.")
#########################################################################
        self.on_mode_toggled(self.single_radio.isChecked())

        self.available_tunnels = []
        self._populate_tunnels()

    def _populate_tunnels(self):
        import os
        import json
        if not self.parent:
            return

        active_layer_paths = list(getattr(self.parent, '_per_layer_actors', {}).keys())
        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        if layer_folder and os.path.exists(layer_folder) and layer_folder not in active_layer_paths:
            active_layer_paths.append(layer_folder)

        subfolder = getattr(self.parent, 'current_subfolder_type', 'designs')
        config_paths = []

        for p in active_layer_paths:
            if not p or not isinstance(p, str) or not os.path.exists(p):
                continue
            is_merger = False
            if "merger" in p.lower() or subfolder == "merger":
                merger_jsons = [f for f in os.listdir(p) if f.endswith('.json')]
                for mj in merger_jsons:
                    try:
                        with open(os.path.join(p, mj), 'r', encoding='utf-8') as f:
                            merger_data = json.load(f)
                        if "merger_points" in merger_data:
                            is_merger = True
                            for pt in merger_data.get("merger_points", []):
                                def add_cfg(json_file_path):
                                    if json_file_path:
                                        d_path = os.path.dirname(json_file_path)
                                        cfg = os.path.join(d_path, 'design_construction_config.json')
                                        if os.path.exists(cfg) and cfg not in config_paths:
                                            config_paths.append(cfg)
                                add_cfg(pt.get("primary_json_path"))
                                for lyr in pt.get("layers", []):
                                    add_cfg(lyr.get("json_path"))
                    except Exception:
                        pass
            if not is_merger:
                cfg = os.path.join(p, 'design_construction_config.json')
                if os.path.exists(cfg) and cfg not in config_paths:
                    config_paths.append(cfg)

        for cfg_path in config_paths:
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg_data = json.load(f)
                    tunnel_config = cfg_data.get("design", {}).get("tunnel")
                    if tunnel_config:
                        tid = tunnel_config.get("tunnel_id", tunnel_config.get("id", "Unknown"))
                        layer_name = os.path.basename(os.path.dirname(cfg_path))
                        tunnel_config["source_layer_folder"] = os.path.dirname(cfg_path)
                        self.available_tunnels.append((tunnel_config, layer_name, tid))
                    else:
                        zc = cfg_data.get("design", {}).get("zero_line_config")
                        if zc:
                            tid = "fallback_tunnel"
                            layer_name = os.path.basename(os.path.dirname(cfg_path))
                            fake_tunnel = {"id": tid, "arc_points": zc.get("arc_points", []),
                                           "start_km": zc.get("point1", {}).get("from_km", 0),
                                           "start_chainage": zc.get("point1", {}).get("from_chainage", 0),
                                           "end_km": zc.get("point2", {}).get("to_km", 0),
                                           "end_chainage": zc.get("point2", {}).get("to_chainage", 0),
                                           "road_width": zc.get("road_width", 10.0),
                                           "source_layer_folder": os.path.dirname(cfg_path)}
                            self.available_tunnels.append((fake_tunnel, layer_name, tid))
            except Exception as e:
                pass

        unique_tunnels = {}
        for t, layer, tid in self.available_tunnels:
            key = (layer, tid)
            if key not in unique_tunnels:
                unique_tunnels[key] = (t, layer, tid)
                
        self.available_tunnels = list(unique_tunnels.values())

        self.tunnel_combo.clear()
        for t, layer, tid in self.available_tunnels:
            self.tunnel_combo.addItem(f"{tid} (Layer: {layer})")

    def update_undo_state(self):
        # Single Light Undo
        has_lights = False
        if hasattr(self.parent, 'tunnel_light_groups') and self.parent.tunnel_light_groups:
            has_lights = True
            
        self.undo_btn.setEnabled(has_lights)
        if not has_lights:
            self.undo_btn.setToolTip("No Tunnel Lights to undo.")
        else:
            self.undo_btn.setToolTip("Undo the most recently placed Tunnel Light.")
            
        # Multiple Lights Undo
        has_multi = False
        if hasattr(self.parent, 'multiple_tunnel_light_batches') and self.parent.multiple_tunnel_light_batches:
            has_multi = True
            
        self.undo_once_btn.setEnabled(has_multi)
        self.undo_all_btn.setEnabled(has_multi)
        if not has_multi:
            self.undo_once_btn.setToolTip("No Multiple Tunnel Lights to undo.")
            self.undo_all_btn.setToolTip("No Multiple Tunnel Lights to undo.")
        else:
            self.undo_once_btn.setToolTip("Undo the most recently placed light from the current Multiple Lights placement.")
            self.undo_all_btn.setToolTip("Undo ALL lights from the most recent Multiple Lights placement.")

    def on_undo_clicked(self):
        if hasattr(self.parent, 'undo_last_tunnel_light'):
            success = self.parent.undo_last_tunnel_light()
            if success:
                self.update_undo_state()
            else:
                QMessageBox.information(self, "Undo", "No Tunnel Lights to undo.")

    def on_undo_once_clicked(self):
        if hasattr(self.parent, 'undo_last_multiple_tunnel_light'):
            success = self.parent.undo_last_multiple_tunnel_light()
            if success:
                self.update_undo_state()
            else:
                QMessageBox.information(self, "Undo", "No Multiple Tunnel Lights to undo.")

    def on_undo_all_clicked(self):
        if hasattr(self.parent, 'undo_all_multiple_tunnel_lights'):
            success = self.parent.undo_all_multiple_tunnel_lights()
            if success:
                self.update_undo_state()
            else:
                QMessageBox.information(self, "Undo", "No Multiple Tunnel Lights to undo.")

    def update_multi_distance_inputs(self, name, state):
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
        from PyQt5.QtGui import QDoubleValidator

        if state == Qt.Checked or state == 2:  # 2 is Qt.Checked
            if name not in self.multi_distance_inputs:
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                
                label = QLabel(f"Enter Distance from {name}:")
                input_field = QLineEdit()
                input_field.setPlaceholderText("Enter distance")
                input_field.setValidator(QDoubleValidator(0.0, 99999.0, 3))
                
                row_layout.addWidget(label)
                row_layout.addWidget(input_field)
                
                self.multi_distance_layout.addWidget(row_widget)
                self.multi_distance_inputs[name] = {"widget": row_widget, "input": input_field}
                ## Mayur Wakhare 3-7-2026 Tunnel light dailog box
                input_field.textChanged.connect(self._update_multi_summary)
                #################################################
        else:
            if name in self.multi_distance_inputs:
                data = self.multi_distance_inputs.pop(name)
                data["widget"].setParent(None)
                data["widget"].deleteLater()

    def on_mode_toggled(self, checked):
        self.single_light_container.setVisible(checked)
        self.multiple_light_container.setVisible(not checked)
        self.undo_btn.setVisible(checked)
        self.undo_once_btn.setVisible(not checked)
        self.undo_all_btn.setVisible(not checked)
        self.update_undo_state()

    def verify_chainage(self):
        try:
            km = float(self.km_input.text() or 0.0)
            ch = float(self.chainage_input.text() or 0.0)
            interval = float(self.interval_input.text() or 0.0)
        except:
            QMessageBox.warning(self, "Invalid Input", "Please enter numeric values for KM, Chainage, and Interval.")
            return

        if interval <= 0:
            QMessageBox.warning(self, "Invalid Interval", "Interval must be greater than 0.")
            return

        abs_chainage = km * 1000 + ch

        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        if not layer_folder or not os.path.exists(layer_folder):
            QMessageBox.warning(self, "Error", "No active design layer folder found to verify.")
            return

        try:
            j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'road_surface_baseline')
            if not j:
                j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'surface_baseline')

            if not j:
                QMessageBox.warning(self, "No Baseline Data", "No surface or road surface baseline found in design layer.")
                return

            global_start_offset = 0.0
            if hasattr(self.parent, '_get_global_start_offset'):
                global_start_offset = self.parent._get_global_start_offset(layer_folder)
            else:
                polylines = j.get("polylines", [])
                if polylines:
                    start_str = polylines[0].get("start_chainage_str", "")
                    if start_str:
                        start_str = start_str.replace(" ", "")
                        if "+" in start_str:
                            parts = start_str.split("+")
                            global_start_offset = float(parts[0]) * 1000 + float(parts[1])
                        else:
                            global_start_offset = float(start_str)

            chs = []
            for poly in j.get("polylines", []):
                for pt in poly.get("points", []):
                    chs.append(pt['chainage_m'] + global_start_offset)
            if not chs:
                QMessageBox.warning(self, "No Points", "Baseline has no chainage points.")
                return

            min_ch = min(chs)
            max_ch = max(chs)

            if abs_chainage < min_ch or abs_chainage > max_ch:
                self.verified = False
                self.arc_combo.setEnabled(False)
                self.distance_input.setEnabled(False)
                self.status_label.setText("Verification failed — chainage out of range.")
                self.status_label.setStyleSheet("color: red; font-size: 11px;")
                QMessageBox.warning(self, "Out of Range",
                    f"Chainage is out of design layer range.\n"
                    f"Range: KM {min_ch//1000:.0f} + {min_ch%1000:.2f}m  to  KM {max_ch//1000:.0f} + {max_ch%1000:.2f}m")
            else:
                self.verified = True
                self.arc_combo.setEnabled(True)
                self.distance_input.setEnabled(True)
                self.status_label.setText("Verification successful!")
                self.status_label.setStyleSheet("color: green; font-size: 11px;")
        except Exception as e:
            self.verified = False
            self.arc_combo.setEnabled(False)
            self.distance_input.setEnabled(False)
            self.status_label.setText(f"Verification error.")
            self.status_label.setStyleSheet("color: red; font-size: 11px;")
            QMessageBox.warning(self, "Error", f"Failed to verify chainage: {e}")

    def verify_multi_chainage(self):
        try:
            start_km = float(self.multi_start_km_input.text() or 0.0)
            start_ch = float(self.multi_start_chainage_input.text() or 0.0)
            end_km = float(self.multi_end_km_input.text() or 0.0)
            end_ch = float(self.multi_end_chainage_input.text() or 0.0)
            interval = float(self.multi_interval_input.text() or 20.0)
        except:
            QMessageBox.warning(self, "Invalid Input", "Please enter numeric values for KM, Chainage, and Interval.")
            return

        if interval <= 0:
            QMessageBox.warning(self, "Invalid Interval", "Interval must be greater than 0.")
            return

        abs_start = start_km * 1000 + start_ch
        abs_end = end_km * 1000 + end_ch

        if abs_start >= abs_end:
            QMessageBox.warning(self, "Invalid Range", "Start chainage must be strictly less than End chainage.")
            return

        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        if not layer_folder or not os.path.exists(layer_folder):
            QMessageBox.warning(self, "Error", "No active design layer folder found to verify.")
            return

        try:
            j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'road_surface_baseline')
            if not j:
                j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'surface_baseline')

            if not j:
                QMessageBox.warning(self, "No Baseline Data", "No surface or road surface baseline found in design layer.")
                return

            global_start_offset = 0.0
            if hasattr(self.parent, '_get_global_start_offset'):
                global_start_offset = self.parent._get_global_start_offset(layer_folder)
            else:
                polylines = j.get("polylines", [])
                if polylines:
                    start_str = polylines[0].get("start_chainage_str", "")
                    if start_str:
                        start_str = start_str.replace(" ", "")
                        if "+" in start_str:
                            parts = start_str.split("+")
                            global_start_offset = float(parts[0]) * 1000 + float(parts[1])
                        else:
                            global_start_offset = float(start_str)

            chs = []
            for poly in j.get("polylines", []):
                for pt in poly.get("points", []):
                    chs.append(pt['chainage_m'] + global_start_offset)
            if not chs:
                QMessageBox.warning(self, "No Points", "Baseline has no chainage points.")
                return

            min_ch = min(chs)
            max_ch = max(chs)

            if abs_start < min_ch or abs_end > max_ch:
                self.multi_verified = False
                self.multi_arc_cb1.setEnabled(False)
                self.multi_arc_cb2.setEnabled(False)
                self.multi_arc_cb3.setEnabled(False)
                self.multi_status_label.setText("Verification failed — range out of bounds.")
                self.multi_status_label.setStyleSheet("color: red; font-size: 11px;")
                QMessageBox.warning(self, "Out of Range",
                    f"Selected range is out of design layer bounds.\n"
                    f"Layer Range: KM {min_ch//1000:.0f} + {min_ch%1000:.2f}m  to  KM {max_ch//1000:.0f} + {max_ch%1000:.2f}m")
            else:
                self.multi_verified = True
                self.multi_arc_cb1.setEnabled(True)
                self.multi_arc_cb2.setEnabled(True)
                self.multi_arc_cb3.setEnabled(True)
                self.multi_status_label.setText("Verification successful!")
                self.multi_status_label.setStyleSheet("color: green; font-size: 11px;")
                ### Mayur Wakhare 3-7-2026 Tunnel light dailog box
                self._update_multi_summary()
                #####################################################
        except Exception as e:
            self.multi_verified = False
            self.multi_arc_cb1.setEnabled(False)
            self.multi_arc_cb2.setEnabled(False)
            self.multi_arc_cb3.setEnabled(False)
            self.multi_status_label.setText(f"Verification error.")
            self.multi_status_label.setStyleSheet("color: red; font-size: 11px;")
            QMessageBox.warning(self, "Error", f"Failed to verify chainage: {e}")
            ## Mayur Wakhare 3-7-2026 tunnel light dailog box how many lights are required for these tunnel 
            self._update_multi_summary()

    def _update_multi_summary(self):
        """Calculate and display the Multiple Lights placement preview.
        Uses the exact same boundary-skipping interval logic as _place_multiple_tunnel_lights:
            current_abs = start_abs + interval
            while current_abs < end_abs - 0.001: place; current_abs += interval
        """
        zero_html = (
            "<b>Placement Summary</b><br><br>"
            "Total Tunnel Lights : 0"
        )

        # If not verified, show zero and hide details
        if not self.multi_verified:
            self.multi_summary_label.setText(zero_html)
            self.multi_summary_label.setVisible(True)
            return

        try:
            start_km = float(self.multi_start_km_input.text() or 0.0)
            start_ch = float(self.multi_start_chainage_input.text() or 0.0)
            end_km = float(self.multi_end_km_input.text() or 0.0)
            end_ch = float(self.multi_end_chainage_input.text() or 0.0)
            interval = float(self.multi_interval_input.text() or 20.0)
        except (ValueError, TypeError):
            self.multi_summary_label.setText(zero_html)
            self.multi_summary_label.setVisible(True)
            return

        if interval <= 0:
            self.multi_summary_label.setText(zero_html)
            self.multi_summary_label.setVisible(True)
            return

        start_abs = start_km * 1000 + start_ch
        end_abs = end_km * 1000 + end_ch

        # Collect selected ARC references (same structure as multi_configs in get_data)
        selected_arcs = []
        for name, d in self.multi_distance_inputs.items():
            arc_ref = int(name.split("(")[-1].replace(")", ""))
            selected_arcs.append({"name": name, "arc_reference": arc_ref})

        if not selected_arcs or start_abs >= end_abs:
            self.multi_summary_label.setText(zero_html)
            self.multi_summary_label.setVisible(True)
            return

        # ── Exact same loop as _place_multiple_tunnel_lights ──
        # current_abs = start_abs + interval
        # while current_abs < end_abs - 0.001: count position; current_abs += interval
        current_abs = start_abs + interval
        chainage_positions = []
        while current_abs < end_abs - 0.001:
            chainage_positions.append(current_abs)
            current_abs += interval

        num_positions = len(chainage_positions)
        num_arcs = len(selected_arcs)
        total_lights = num_positions * num_arcs

        if total_lights == 0:
            self.multi_summary_label.setText(zero_html)
            self.multi_summary_label.setVisible(True)
            return

        # Sort: Right Side (1), Top / Center (2), Left Side (3)
        arc_order = {1: 0, 2: 1, 3: 2}
        selected_arcs_sorted = sorted(selected_arcs, key=lambda a: arc_order.get(a["arc_reference"], 99))

        # Estimated Covered Length = last placed position - first placed position
        covered_length = chainage_positions[-1] - chainage_positions[0]

        # Build HTML
        lines = ["<b>Placement Summary</b><br>"]
        lines.append(f"<br>Total Tunnel Lights : <b>{total_lights}</b><br>")
        lines.append("<br><b>Estimated Placement</b><br><br>")
        for arc in selected_arcs_sorted:
            lines.append(f"{arc['name']} : {num_positions}<br>")
        lines.append(f"<br>Estimated Covered Length : <b>{covered_length:.0f} m</b>")

        self.multi_summary_label.setText("".join(lines))
        self.multi_summary_label.setVisible(True)

        #########################################################

    def on_ok_clicked(self):
        if self.single_radio.isChecked():
            self.selected_option = "single"
            # Validate single light inputs before accepting
            if not self.verified:
                QMessageBox.warning(self, "Not Verified", "Please verify the chainage first.")
                return
            distance_text = self.distance_input.text().strip()
            if not distance_text:
                QMessageBox.warning(self, "Missing Distance", "Please enter a Distance / Length value.")
                return
            try:
                dist_val = float(distance_text)
                if dist_val < 0:
                    QMessageBox.warning(self, "Invalid Distance", "Distance must be a positive value.")
                    return
            except ValueError:
                QMessageBox.warning(self, "Invalid Distance", "Please enter a valid numeric distance.")
                return
            self.accept()
        else:
            self.selected_option = "multiple"
            if not self.multi_verified:
                QMessageBox.warning(self, "Not Verified", "Please verify the chainage range first.")
                return
            if not self.multi_distance_inputs:
                QMessageBox.warning(self, "No Selection", "Please select at least one ARC Reference.")
                return
            for name, d in self.multi_distance_inputs.items():
                distance_text = d["input"].text().strip()
                if not distance_text:
                    QMessageBox.warning(self, "Missing Distance", f"Please enter a distance for {name}.")
                    return
                try:
                    dist_val = float(distance_text)
                    if dist_val < 0:
                        QMessageBox.warning(self, "Invalid Distance", f"Distance for {name} must be a positive value.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Invalid Distance", f"Please enter a valid numeric distance for {name}.")
                    return
            self.accept()

    def get_data(self):
        try:
            idx = self.tunnel_combo.currentIndex()
            t_id = "Unknown"
            l_name = "Unknown"
            t_obj = {}
            if idx >= 0 and idx < len(getattr(self, 'available_tunnels', [])):
                t_obj, l_name, t_id = self.available_tunnels[idx]
        except Exception:
            t_id = "Unknown"
            l_name = "Unknown"
            t_obj = {}

        data = {
            "light_mode": self.selected_option,
            "tunnel_id": t_id,
            "layer_name": l_name,
            "source_layer_folder": t_obj.get("source_layer_folder", "")
        }
        if self.selected_option == "single":
            data["km"] = float(self.km_input.text() or 0.0)
            data["chainage"] = float(self.chainage_input.text() or 0.0)
            data["interval"] = float(self.interval_input.text() or 20)
            data["verified"] = self.verified
            if self.verified:
                text = self.arc_combo.currentText()
                data["arc_reference"] = int(text.split("(")[-1].replace(")", ""))
                data["distance"] = float(self.distance_input.text() or 0.0)
        else:
            data["start_km"] = float(self.multi_start_km_input.text() or 0.0)
            data["start_chainage"] = float(self.multi_start_chainage_input.text() or 0.0)
            data["end_km"] = float(self.multi_end_km_input.text() or 0.0)
            data["end_chainage"] = float(self.multi_end_chainage_input.text() or 0.0)
            data["interval"] = float(self.multi_interval_input.text() or 20.0)
            data["verified"] = self.multi_verified
            if self.multi_verified:
                configs = []
                for name, d in self.multi_distance_inputs.items():
                    arc_ref = int(name.split("(")[-1].replace(")", ""))
                    dist = float(d["input"].text() or 0.0)
                    configs.append({"arc_reference": arc_ref, "distance": dist})
                data["multi_configs"] = configs
                
        print(f"[Dialog get_data] Dropdown current text: {self.tunnel_combo.currentText()}")
        print(f"[Dialog get_data] Dropdown current index: {self.tunnel_combo.currentIndex()}")
        print(f"[Dialog get_data] Tunnel ID: {data.get('tunnel_id')}")
        print(f"[Dialog get_data] Source Layer: {data.get('layer_name')}")
        print(f"[Dialog get_data] Source Layer Folder: {data.get('source_layer_folder')}")
        print(f"[Dialog get_data] Final Data Dictionary: {data}")
        return data
#####################################################################
### Mayur Wakhare 3-7-2026 Tunnel Fire Extinguisher Dialog Box ###
class FireExtinguisherDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fire Extinguisher")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.parent = parent
        self.verified = False
        
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QLineEdit {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Fire Extinguisher")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D32F2F;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Start KM:"), 0, 0)
        self.start_km_input = QLineEdit()
        grid.addWidget(self.start_km_input, 0, 1)

        grid.addWidget(QLabel("+"), 0, 2)
        self.start_ch_input = QLineEdit()
        grid.addWidget(self.start_ch_input, 0, 3)

        grid.addWidget(QLabel("End KM:"), 1, 0)
        self.end_km_input = QLineEdit()
        grid.addWidget(self.end_km_input, 1, 1)

        grid.addWidget(QLabel("+"), 1, 2)
        self.end_ch_input = QLineEdit()
        grid.addWidget(self.end_ch_input, 1, 3)

        grid.addWidget(QLabel("Tunnel:"), 2, 0)
        self.tunnel_combo = QComboBox()
        self.tunnel_combo.currentIndexChanged.connect(self._on_tunnel_selected)
        grid.addWidget(self.tunnel_combo, 2, 1, 1, 3)

        grid.addWidget(QLabel("Fire Extinguisher Interval (m):"), 3, 0, 1, 2)
        self.interval_input = QLineEdit()
        self.interval_input.setText("100")
        grid.addWidget(self.interval_input, 3, 2, 1, 2)
        
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 6px; font-weight: bold; border-radius: 4px;")
        grid.addWidget(self.verify_btn, 4, 0, 1, 4)
        self.verify_btn.clicked.connect(self.verify_chainage)
        
        layout.addLayout(grid)

        note_label = QLabel("Recommended spacing: 100–120 m")
        note_label.setStyleSheet("font-size: 11px; color: #666; font-weight: normal; font-style: italic;")
        layout.addWidget(note_label)

        # ── Installation Side ──
        self.side_group = QGroupBox("Installation Side")
        self.side_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        self.side_group.setEnabled(False)
        side_layout = QHBoxLayout(self.side_group)
        
        from PyQt5.QtWidgets import QRadioButton
        self.right_side_rb = QRadioButton("Right Side")
        self.left_side_rb = QRadioButton("Left Side")
        self.both_sides_rb = QRadioButton("Both Sides")
        
        self.both_sides_rb.setChecked(True)
        
        side_layout.addWidget(self.right_side_rb)
        side_layout.addWidget(self.left_side_rb)
        side_layout.addWidget(self.both_sides_rb)
        
        layout.addWidget(self.side_group)
        
        # ── Placement Summary (read-only preview) ──
        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(
            "background-color: #FFEBEE; border: 1px solid #FFCDD2; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #333; font-weight: normal;"
        )
        layout.addWidget(self.summary_label)

        # OK / Cancel / Undo
        buttons_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)
        buttons_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
     ### Mayur Wakhare 4-7-2026 Undo Fire Tunnel   
        self.undo_once_btn = QPushButton("Undo Once")
        self.undo_once_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.undo_once_btn.clicked.connect(self.on_undo_once_clicked)
        buttons_layout.addWidget(self.undo_once_btn)

        self.undo_all_btn = QPushButton("Undo All")
        self.undo_all_btn.setStyleSheet("background-color: #F44336; color: white;")
        self.undo_all_btn.clicked.connect(self.on_undo_all_clicked)
        buttons_layout.addWidget(self.undo_all_btn)
        
        self.update_undo_state()

        #################################################
        
        layout.addLayout(buttons_layout)

    ## Mayur 18-7-2026 auto populated chainage
        # ── Auto-populate chainage from tunnels ──
        self.available_tunnels = []
        self._populate_tunnels()
            
        # Connections for live update
        self.start_km_input.textChanged.connect(self.invalidate_verification)
        self.start_ch_input.textChanged.connect(self.invalidate_verification)
        self.end_km_input.textChanged.connect(self.invalidate_verification)
        self.end_ch_input.textChanged.connect(self.invalidate_verification)
        self.interval_input.textChanged.connect(self.update_summary)
        
        self.right_side_rb.toggled.connect(self.update_summary)
        self.left_side_rb.toggled.connect(self.update_summary)
        self.both_sides_rb.toggled.connect(self.update_summary)
        
        self.invalidate_verification()
#### Mayur 18-7-2026
    def _populate_tunnels(self):
        import os
        import json
        
        self.tunnel_combo.blockSignals(True)
        self.tunnel_combo.clear()
        self.available_tunnels.clear()

        if not hasattr(self.parent, '_per_layer_actors'):
            self.tunnel_combo.blockSignals(False)
            return

        def clean_str(val):
            return str(val)[:-2] if str(val).endswith(".0") else str(val)

        for layer_path in self.parent._per_layer_actors.keys():
            layer_name = os.path.basename(layer_path)
            
            # Check for merged layer
            is_merger = False
            try:
                merger_jsons = [f for f in os.listdir(layer_path) if f.endswith('.json')]
                for mj in merger_jsons:
                    with open(os.path.join(layer_path, mj), 'r', encoding='utf-8') as f:
                        m_data = json.load(f)
                    if "merger_points" in m_data:
                        is_merger = True
                        for pt in m_data.get("merger_points", []):
                            def add_cfg(cpath):
                                if cpath and os.path.exists(cpath):
                                    with open(cpath, 'r', encoding='utf-8') as cf:
                                        cdat = json.load(cf)
                                    t = cdat.get("design", {}).get("tunnel")
                                    if not t:
                                        zc = cdat.get("design", {}).get("zero_line_config")
                                        if zc:
                                            t = {"id": "fallback_tunnel", "start_km": 0, "start_chainage": 0, "end_km": 0, "end_chainage": 0}
                                    if t:
                                        tid = t.get("tunnel_id", t.get("id", "Unknown"))
                                        disp = f"{tid} ({layer_name})"
                                        self.available_tunnels.append((t, layer_name, tid))
                                        self.tunnel_combo.addItem(disp)
                            add_cfg(pt.get("primary_json_path"))
                            for lyr in pt.get("layers", []):
                                add_cfg(lyr.get("json_path"))
            except Exception:
                pass
                
            if not is_merger:
                try:
                    from json_manager import DesignConstructionManager
                    m_data = DesignConstructionManager.load_master(layer_path)
                    t = m_data.get("design", {}).get("tunnel")
                    if not t:
                        zc = m_data.get("design", {}).get("zero_line_config")
                        if zc:
                            t = {"id": "fallback_tunnel", "start_km": 0, "start_chainage": 0, "end_km": 0, "end_chainage": 0}
                    if t:
                        tid = t.get("tunnel_id", t.get("id", "Unknown"))
                        disp = f"{tid} ({layer_name})"
                        self.available_tunnels.append((t, layer_name, tid))
                        self.tunnel_combo.addItem(disp)
                except Exception:
                    pass

        self.tunnel_combo.blockSignals(False)
        if self.tunnel_combo.count() > 0:
            self.tunnel_combo.setCurrentIndex(0)
            self._on_tunnel_selected(0)

    def _on_tunnel_selected(self, index):
        if index < 0 or index >= len(self.available_tunnels):
            return
            
        t, layer_name, tid = self.available_tunnels[index]
        def clean_str(val):
            return str(val)[:-2] if str(val).endswith(".0") else str(val)
            
        self.start_km_input.setText(clean_str(t.get('start_km', '0')))
        self.start_ch_input.setText(clean_str(t.get('start_chainage', '0')))
        self.end_km_input.setText(clean_str(t.get('end_km', '0')))
        self.end_ch_input.setText(clean_str(t.get('end_chainage', '0')))
        self.invalidate_verification()
########################################################################
    def invalidate_verification(self):
        self.verified = False
        self.ok_btn.setEnabled(False)
        self.side_group.setEnabled(False)
        self.summary_label.setText("<b>Total Fire Extinguishers : 0</b><br><br>Estimated Placement<br><br>Right Side : 0<br>Left Side  : 0")
## Mayur 18-7-2026
    def verify_chainage(self):
        from PyQt5.QtWidgets import QMessageBox
        import os
        try:
            start_km = float(self.start_km_input.text() or 0.0)
            start_ch = float(self.start_ch_input.text() or 0.0)
            end_km = float(self.end_km_input.text() or 0.0)
            end_ch = float(self.end_ch_input.text() or 0.0)
            interval = float(self.interval_input.text() or 100.0)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter numeric values for KM, Chainage, and Interval.")
            return

        if interval <= 0:
            QMessageBox.warning(self, "Invalid Interval", "Interval must be greater than 0.")
            return

        start_abs = start_km * 1000 + start_ch
        end_abs = end_km * 1000 + end_ch

        idx = self.tunnel_combo.currentIndex()
        if idx < 0 or idx >= len(self.available_tunnels):
            QMessageBox.warning(self, "No Tunnel", "No valid tunnel selected for verification.")
            return

        t_data, layer_name, tid = self.available_tunnels[idx]
        
        ts_km = float(t_data.get("start_km", 0.0))
        ts_ch = float(t_data.get("start_chainage", 0.0))
        te_km = float(t_data.get("end_km", 0.0))
        te_ch = float(t_data.get("end_chainage", 0.0))
        
        t_start = ts_km * 1000 + ts_ch
        t_end = te_km * 1000 + te_ch

        print("\n--- Fire Extinguisher Verify Debug ---")
        print(f"Selected Tunnel ID: {tid}")
        print(f"Selected Layer: {layer_name}")
        print(f"Tunnel Start Chainage: {t_start}")
        print(f"Tunnel End Chainage: {t_end}")
        print(f"Verify Range: {t_start} - {t_end}")
        print(f"Entered Chainage: {start_abs} - {end_abs}")
        print("--------------------------------------\n")

        if start_abs < t_start or start_abs > t_end or end_abs < t_start or end_abs > t_end:
            QMessageBox.warning(self, "Out of Bounds", f"Locations must be within tunnel limits ({t_start} - {t_end}).")
            return
        if start_abs >= end_abs:
            QMessageBox.warning(self, "Invalid Range", "Start chainage must be less than End chainage.")
            return

        self.verified = True
        self.side_group.setEnabled(True)
        self.ok_btn.setEnabled(True)
        self.update_summary()
        QMessageBox.information(self, "Verified", "Chainage locations and interval successfully verified.")
######################################################################################################
    def update_summary(self):
        if not getattr(self, 'verified', False):
            return
            
        try:
            start_km = float(self.start_km_input.text() or 0.0)
            start_ch = float(self.start_ch_input.text() or 0.0)
            end_km = float(self.end_km_input.text() or 0.0)
            end_ch = float(self.end_ch_input.text() or 0.0)
            interval = float(self.interval_input.text() or 100.0)
        except (ValueError, TypeError):
            self.summary_label.setText("<b>Total Fire Extinguishers : 0</b><br><br>Estimated Placement<br><br>Right Side : 0<br>Left Side  : 0")
            return
            
        if interval <= 0:
            self.summary_label.setText("<b>Total Fire Extinguishers : 0</b><br><br>Estimated Placement<br><br>Right Side : 0<br>Left Side  : 0")
            return
            
        start_abs = start_km * 1000 + start_ch
        end_abs = end_km * 1000 + end_ch
        
        if start_abs >= end_abs:
            self.summary_label.setText("<b>Total Fire Extinguishers : 0</b><br><br>Estimated Placement<br><br>Right Side : 0<br>Left Side  : 0")
            return
            
        count = 0
        current_abs = start_abs + interval
        while current_abs < end_abs - 0.001:
            count += 1
            current_abs += interval
            
        lines = []
        if self.both_sides_rb.isChecked():
            lines.append(f"<b>Total Fire Extinguishers : {count * 2}</b><br>")
            lines.append("<b>Estimated Placement</b><br>")
            lines.append(f"Right Side : {count}")
            lines.append(f"Left Side  : {count}")
        elif self.right_side_rb.isChecked():
            lines.append(f"<b>Total Fire Extinguishers : {count}</b><br>")
            lines.append("<b>Estimated Placement</b><br>")
            lines.append(f"Right Side : {count}")
        elif self.left_side_rb.isChecked():
            lines.append(f"<b>Total Fire Extinguishers : {count}</b><br>")
            lines.append("<b>Estimated Placement</b><br>")
            lines.append(f"Left Side : {count}")
            
        lines.append(f"<br>Estimated Covered Length : {end_abs - start_abs:.2f} m")
        self.summary_label.setText("<br>".join(lines))
#### Mayur 18-7-2026
    def get_data(self):
        try:
            side = "both"
            if self.right_side_rb.isChecked():
                side = "right"
            elif self.left_side_rb.isChecked():
                side = "left"
                
            idx = self.tunnel_combo.currentIndex()
            tunnel_id = "Unknown"
            layer_name = "Unknown"
            if 0 <= idx < len(getattr(self, 'available_tunnels', [])):
                _, layer_name, tunnel_id = self.available_tunnels[idx]
                
            return {
                "start_km": float(self.start_km_input.text() or 0.0),
                "start_chainage": float(self.start_ch_input.text() or 0.0),
                "end_km": float(self.end_km_input.text() or 0.0),
                "end_chainage": float(self.end_ch_input.text() or 0.0),
                "interval": float(self.interval_input.text() or 100.0),
                "installation_side": side,
                "tunnel_id": tunnel_id,
                "layer_name": layer_name
            }
        except ValueError:
            return None
########### Mayur Wakhare 4-7-2026 Fire Undo option Tuunel
    def update_undo_state(self):
        has_multi = False
        if hasattr(self.parent, 'multiple_fire_extinguisher_batches'):
            has_multi = len(self.parent.multiple_fire_extinguisher_batches) > 0
            
        self.undo_once_btn.setEnabled(has_multi)
        self.undo_all_btn.setEnabled(has_multi)

    def on_undo_once_clicked(self):
        if hasattr(self.parent, 'undo_last_multiple_fire_extinguisher'):
            success = self.parent.undo_last_multiple_fire_extinguisher()
            if success:
                self.update_undo_state()

    def on_undo_all_clicked(self):
        if hasattr(self.parent, 'undo_all_multiple_fire_extinguishers'):
            success = self.parent.undo_all_multiple_fire_extinguishers()
            if success:
                self.update_undo_state()
############################################################
            ###############################################################
### Mayur Wakhare 4-7-2026 cctv tunnel
### CCTV Camera Dialog Box ###
class CCTVCameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CCTV Camera")
        self.setModal(True)
        self.setMinimumWidth(420)
        self.parent = parent
        self.verified = False

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QLineEdit {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("CCTV Camera")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1565C0;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Start KM:"), 0, 0)
        self.start_km_input = QLineEdit()
        grid.addWidget(self.start_km_input, 0, 1)

        grid.addWidget(QLabel("+"), 0, 2)
        self.start_ch_input = QLineEdit()
        grid.addWidget(self.start_ch_input, 0, 3)

        grid.addWidget(QLabel("End KM:"), 1, 0)
        self.end_km_input = QLineEdit()
        grid.addWidget(self.end_km_input, 1, 1)

        grid.addWidget(QLabel("+"), 1, 2)
        self.end_ch_input = QLineEdit()
        grid.addWidget(self.end_ch_input, 1, 3)

        grid.addWidget(QLabel("Tunnel:"), 2, 0)
        self.tunnel_combo = QComboBox()
        self.tunnel_combo.currentIndexChanged.connect(self._on_tunnel_selected)
        grid.addWidget(self.tunnel_combo, 2, 1, 1, 3)

        grid.addWidget(QLabel("Camera Interval (m):"), 3, 0, 1, 2)
        self.interval_input = QLineEdit()
        self.interval_input.setText("120")
        grid.addWidget(self.interval_input, 3, 2, 1, 2)

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 6px; font-weight: bold; border-radius: 4px;")
        grid.addWidget(self.verify_btn, 4, 0, 1, 4)
        self.verify_btn.clicked.connect(self.verify_chainage)

        layout.addLayout(grid)

        note_label = QLabel("Recommended spacing: 100\u2013150 m")
        note_label.setStyleSheet("font-size: 11px; color: #666; font-weight: normal; font-style: italic;")
        layout.addWidget(note_label)

        # ── ARC Reference (UI exactly like Tunnel Light) ──
        self.arc_post_verify_container = QWidget()
        arc_layout = QGridLayout(self.arc_post_verify_container)
        arc_layout.setSpacing(10)
        arc_layout.setContentsMargins(0, 0, 0, 0)

        self.arc_label = QLabel("ARC Reference:")
        arc_layout.addWidget(self.arc_label, 0, 0)
        
        from PyQt5.QtWidgets import QRadioButton, QButtonGroup
        self.arc_checkbox_layout = QVBoxLayout()
        self.arc_rb1 = QRadioButton("Left Side (1)")
        self.arc_rb2 = QRadioButton("Top / Center (2)")
        self.arc_rb3 = QRadioButton("Right Side (3)")
        
        self.arc_btn_group = QButtonGroup(self)
        self.arc_btn_group.setExclusive(True)
        self.arc_btn_group.addButton(self.arc_rb1)
        self.arc_btn_group.addButton(self.arc_rb2)
        self.arc_btn_group.addButton(self.arc_rb3)
        
        self.arc_rb1.setEnabled(False)
        self.arc_rb2.setEnabled(False)
        self.arc_rb3.setEnabled(False)
        
        self.arc_checkbox_layout.addWidget(self.arc_rb1)
        self.arc_checkbox_layout.addWidget(self.arc_rb2)
        self.arc_checkbox_layout.addWidget(self.arc_rb3)
        arc_layout.addLayout(self.arc_checkbox_layout, 0, 1)

        from PyQt5.QtGui import QDoubleValidator
        self.distance_label = QLabel("Enter Distance:")
        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText("Enter distance")
        self.distance_input.setValidator(QDoubleValidator(0.0, 99999.0, 3))
        self.distance_label.setVisible(False)
        self.distance_input.setVisible(False)
        
        arc_layout.addWidget(self.distance_label, 1, 0)
        arc_layout.addWidget(self.distance_input, 1, 1)

        layout.addWidget(self.arc_post_verify_container)
        
        # Connect signals
        self.arc_rb1.toggled.connect(lambda checked: self.on_arc_toggled("Left Side", checked))
        self.arc_rb2.toggled.connect(lambda checked: self.on_arc_toggled("Center", checked))
        self.arc_rb3.toggled.connect(lambda checked: self.on_arc_toggled("Right Side", checked))
        self.distance_input.textChanged.connect(self.update_summary)

        # Variables for Arc preparation backend
        self.tunnel_arc_length = 0.0
        self.dummy_arc_points = []
        self.center_dummy_point = None
        self.selected_arc_reference = "None"

        # ── Placement Summary (read-only preview) ──
        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(
            "background-color: #E8F5E9; border: 1px solid #A5D6A7; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #333; font-weight: normal;"
        )
        layout.addWidget(self.summary_label)

        # OK / Cancel / Undo
        buttons_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)
        buttons_layout.addWidget(self.ok_btn)
##### Mayur Wakhare 6-7-2026 undo button 
        self.undo_once_btn = QPushButton("Undo Once")
        self.undo_once_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.undo_once_btn.clicked.connect(self.on_undo_once_clicked)
        buttons_layout.addWidget(self.undo_once_btn)

        self.undo_all_btn = QPushButton("Undo All")
        self.undo_all_btn.setStyleSheet("background-color: #F44336; color: white;")
        self.undo_all_btn.clicked.connect(self.on_undo_all_clicked)
        buttons_layout.addWidget(self.undo_all_btn)
        ################################################################################

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.update_undo_state()

        #################################################

        layout.addLayout(buttons_layout)


        # ── Auto-populate chainage from tunnels ──
        self.available_tunnels = []
        self._populate_tunnels()

        # Connections for live update
        self.start_km_input.textChanged.connect(self.invalidate_verification)
        self.start_ch_input.textChanged.connect(self.invalidate_verification)
        self.end_km_input.textChanged.connect(self.invalidate_verification)
        self.end_ch_input.textChanged.connect(self.invalidate_verification)
        self.interval_input.textChanged.connect(self.update_summary)

        self.invalidate_verification()
        ### Mayur Wakhare 6-7-2026 undo cctv camera tunnel
        self.update_undo_state()
##### Mayur 18-7-2026
    def on_arc_toggled(self, ref_name, checked):
        if not checked:
            return
            
        self.selected_arc_reference = ref_name
        self.distance_label.setText(f"Enter Distance from {ref_name}:")
        self.distance_label.setVisible(True)
        self.distance_input.setVisible(True)
        self.update_summary()
# Mayur 18-7-2026
    def _populate_tunnels(self):
        import os
        import json
        
        self.tunnel_combo.blockSignals(True)
        self.tunnel_combo.clear()
        self.available_tunnels.clear()

        if not hasattr(self.parent, '_per_layer_actors'):
            self.tunnel_combo.blockSignals(False)
            return

        for layer_path in self.parent._per_layer_actors.keys():
            layer_name = os.path.basename(layer_path)
            
            # Check for merged layer
            is_merger = False
            try:
                merger_jsons = [f for f in os.listdir(layer_path) if f.endswith('.json')]
                for mj in merger_jsons:
                    with open(os.path.join(layer_path, mj), 'r', encoding='utf-8') as f:
                        m_data = json.load(f)
                    if "merger_points" in m_data:
                        is_merger = True
                        for pt in m_data.get("merger_points", []):
                            def add_cfg(cpath):
                                if cpath and os.path.exists(cpath):
                                    with open(cpath, 'r', encoding='utf-8') as cf:
                                        cdat = json.load(cf)
                                    t = cdat.get("design", {}).get("tunnel")
                                    if not t:
                                        zc = cdat.get("design", {}).get("zero_line_config")
                                        if zc:
                                            t = {"id": "fallback_tunnel", "start_km": 0, "start_chainage": 0, "end_km": 0, "end_chainage": 0}
                                    if t:
                                        tid = t.get("tunnel_id", t.get("id", "Unknown"))
                                        disp = f"{tid} ({layer_name})"
                                        self.available_tunnels.append((t, layer_name, tid))
                                        self.tunnel_combo.addItem(disp)
                            add_cfg(pt.get("primary_json_path"))
                            for lyr in pt.get("layers", []):
                                add_cfg(lyr.get("json_path"))
            except Exception:
                pass
                
            if not is_merger:
                try:
                    from json_manager import DesignConstructionManager
                    m_data = DesignConstructionManager.load_master(layer_path)
                    t = m_data.get("design", {}).get("tunnel")
                    if not t:
                        zc = m_data.get("design", {}).get("zero_line_config")
                        if zc:
                            t = {"id": "fallback_tunnel", "start_km": 0, "start_chainage": 0, "end_km": 0, "end_chainage": 0}
                    if t:
                        tid = t.get("tunnel_id", t.get("id", "Unknown"))
                        disp = f"{tid} ({layer_name})"
                        self.available_tunnels.append((t, layer_name, tid))
                        self.tunnel_combo.addItem(disp)
                except Exception:
                    pass

        self.tunnel_combo.blockSignals(False)
        if self.tunnel_combo.count() > 0:
            self.tunnel_combo.setCurrentIndex(0)
            self._on_tunnel_selected(0)

    def _on_tunnel_selected(self, index):
        if index < 0 or index >= len(self.available_tunnels):
            return
            
        t, layer_name, tid = self.available_tunnels[index]
        def clean_str(val):
            return str(val)[:-2] if str(val).endswith(".0") else str(val)
            
        self.start_km_input.setText(clean_str(t.get('start_km', '0')))
        self.start_ch_input.setText(clean_str(t.get('start_chainage', '0')))
        self.end_km_input.setText(clean_str(t.get('end_km', '0')))
        self.end_ch_input.setText(clean_str(t.get('end_chainage', '0')))
        self.invalidate_verification()

    def update_undo_state(self):
        has_multi = False
        if hasattr(self.parent, 'cctv_camera_batches'):
            has_multi = len(self.parent.cctv_camera_batches) > 0
            
        self.undo_once_btn.setEnabled(has_multi)
        self.undo_all_btn.setEnabled(has_multi)

    def on_undo_once_clicked(self):
        if hasattr(self.parent, 'undo_last_cctv_camera'):
            success = self.parent.undo_last_cctv_camera()
            if success:
                self.update_undo_state()

    def on_undo_all_clicked(self):
        if hasattr(self.parent, 'undo_all_cctv_cameras'):
            success = self.parent.undo_all_cctv_cameras()
            if success:
                self.update_undo_state()
                #####################################################################
### Mayur 18-7-2026 
    def invalidate_verification(self):
        self.verified = False
        self.ok_btn.setEnabled(False)
        self.arc_rb1.setEnabled(False)
        self.arc_rb2.setEnabled(False)
        self.arc_rb3.setEnabled(False)
        self.summary_label.setText(
            "• Tunnel Arc Length : --\n"
            "• Total Dummy Arc Points : --\n"
            "• Selected ARC Reference : --\n"
            "• Entered Distance : --"
        )
## Mayur 18-7-2026 
    def verify_chainage(self):
        try:
            start_km = float(self.start_km_input.text() or 0.0)
            start_ch = float(self.start_ch_input.text() or 0.0)
            end_km = float(self.end_km_input.text() or 0.0)
            end_ch = float(self.end_ch_input.text() or 0.0)
            interval = float(self.interval_input.text() or 120.0)
        except:
            QMessageBox.warning(self, "Invalid Input", "Please enter numeric values for KM, Chainage, and Interval.")
            return

        if interval <= 0:
            QMessageBox.warning(self, "Invalid Interval", "Interval must be greater than 0.")
            return

        abs_start = start_km * 1000 + start_ch
        abs_end = end_km * 1000 + end_ch

        idx = self.tunnel_combo.currentIndex()
        if idx < 0 or idx >= len(self.available_tunnels):
            QMessageBox.warning(self, "No Tunnel", "No valid tunnel selected for verification.")
            return

        t_data, layer_name, tid = self.available_tunnels[idx]
        
        ts_km = float(t_data.get("start_km", 0.0))
        ts_ch = float(t_data.get("start_chainage", 0.0))
        te_km = float(t_data.get("end_km", 0.0))
        te_ch = float(t_data.get("end_chainage", 0.0))
        
        t_start = ts_km * 1000 + ts_ch
        t_end = te_km * 1000 + te_ch

        if abs_start < t_start or abs_start > t_end or abs_end < t_start or abs_end > t_end:
            QMessageBox.warning(self, "Out of Bounds", f"Locations must be within tunnel limits ({t_start} - {t_end}).")
            return
        if abs_start >= abs_end:
            QMessageBox.warning(self, "Invalid Range", "Start chainage must be strictly less than End chainage.")
            return

        self.verified = True
        self.arc_rb1.setEnabled(True)
        self.arc_rb2.setEnabled(True)
        self.arc_rb3.setEnabled(True)
        self.ok_btn.setEnabled(True)
        
        # Backend Arc Preparation
        arc_points_raw = t_data.get("arc_points", [])
        
        import numpy as np
        import math
        
        self.tunnel_arc_length = 0.0
        self.dummy_arc_points = []
        self.center_dummy_point = None
        
        if len(arc_points_raw) >= 3:
            p1 = np.array(arc_points_raw[0])
            p2 = np.array(arc_points_raw[1])
            p3 = np.array(arc_points_raw[2])
            
            # Simple circle fit for arc length estimation
            a = np.linalg.norm(p2 - p1)
            b = np.linalg.norm(p3 - p2)
            c = np.linalg.norm(p1 - p3)
            s = (a + b + c) / 2.0
            area = math.sqrt(abs(s * (s - a) * (s - b) * (s - c)))
            if area > 1e-6:
                R = (a * b * c) / (4.0 * area)
                # Assuming semicircular tunnel
                self.tunnel_arc_length = math.pi * R
            else:
                self.tunnel_arc_length = a + b
                
            num_points = int(self.tunnel_arc_length / 1.0)
            if num_points > 0:
                self.dummy_arc_points = [{"id": i, "dist": i * 1.0} for i in range(num_points + 1)]
                center_idx = len(self.dummy_arc_points) // 2
                if self.dummy_arc_points:
                    self.center_dummy_point = self.dummy_arc_points[center_idx]
                    
        self.update_summary()
        QMessageBox.information(self, "Verified", "Chainage locations and interval successfully verified.")

    def update_summary(self):
        if not getattr(self, 'verified', False):
            return

        distance = self.distance_input.text() or "0"
        summary_text = (
            f"• Tunnel Arc Length : {self.tunnel_arc_length:.2f} m\n"
            f"• Total Dummy Arc Points : {len(self.dummy_arc_points)}\n"
            f"• Selected ARC Reference : {self.selected_arc_reference}\n"
            f"• Entered Distance : {distance} m"
        )
        self.summary_label.setText(summary_text)
#### Mayur 18-7-2026
    def get_data(self):
        try:
            position = "both_roof_corners" # fallback
            if self.arc_rb1.isChecked():
                position = "left_roof_corner"
            elif self.arc_rb3.isChecked():
                position = "right_roof_corner"
            elif self.arc_rb2.isChecked():
                position = "alternate_sides"

            idx = self.tunnel_combo.currentIndex()
            tunnel_id = "Unknown"
            layer_name = "Unknown"
            if 0 <= idx < len(getattr(self, 'available_tunnels', [])):
                _, layer_name, tunnel_id = self.available_tunnels[idx]

            return {
                "start_km": float(self.start_km_input.text() or 0.0),
                "start_chainage": float(self.start_ch_input.text() or 0.0),
                "end_km": float(self.end_km_input.text() or 0.0),
                "end_chainage": float(self.end_ch_input.text() or 0.0),
                "interval": float(self.interval_input.text() or 120.0),
                "installation_position": position,
                "arc_reference": self.selected_arc_reference,
                "distance": float(self.distance_input.text() or 0.0),
                "tunnel_id": tunnel_id,
                "layer_name": layer_name
            }
        except ValueError:
            return None
###############################################################
######### Mayur Wakhare 4-7-2026 Tunnel Signage Board

class TunnelInfoBoardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tunnel Information Board")
        self.setModal(True)
        self.setMinimumWidth(380)
        self.parent = parent
        self.verified = False
        
        self.setStyleSheet("""
            QDialog { background-color: #F5F5F5; font-family: Segoe UI; }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QLineEdit, QTextEdit { padding: 6px; border: 2px solid #BBB; border-radius: 6px; font-size: 13px; background-color: white; }
            QPushButton { padding: 8px; border-radius: 6px; font-weight: bold; font-size: 13px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Tunnel Information Board")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1565C0;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Placement
        grid.addWidget(QLabel("Placement KM:"), 0, 0)
        self.km_input = QLineEdit()
        grid.addWidget(self.km_input, 0, 1)

        grid.addWidget(QLabel("+"), 0, 2)
        self.ch_input = QLineEdit()
        grid.addWidget(self.ch_input, 0, 3)
    #### Mayur Wakhare 5-7-2026 Tunnel information board  
        # Information Fields
        from PyQt5.QtWidgets import QTextEdit
        grid.addWidget(QLabel("Display Text:"), 1, 0, 1, 4)
        self.text_input = QTextEdit()
        self.text_input.setPlainText("WELCOME\nDRIVE SAFELY")
        self.text_input.setMaximumHeight(60)
        grid.addWidget(self.text_input, 2, 0, 1, 4)
        
        grid.addWidget(QLabel("Speed Limit:"), 3, 0, 1, 2)
        self.speed_limit_input = QLineEdit()
        self.speed_limit_input.setText("80 km/h")
        self.speed_limit_input.setPlaceholderText("e.g. 40 km/h, 60 km/h, 80 km/h")
        grid.addWidget(self.speed_limit_input, 3, 2, 1, 2)
        
        layout.addLayout(grid)
        
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 6px; font-weight: bold; border-radius: 4px;")
        self.verify_btn.clicked.connect(self.verify_placement)
        layout.addWidget(self.verify_btn)
        
        self.summary_label = QLabel("Please verify placement.")
        self.summary_label.setStyleSheet("color: #D32F2F; font-size: 12px; font-weight: bold; padding: 5px;")
        self.summary_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.summary_label)
        #############################################################################################
        
        self.auto_populate()
        
        buttons_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
     ##### Mayur Wakhare 5-7-2026  Button Enable disable based on Verification Status. 
        self.ok_btn.setEnabled(False)
        ########################################################################################
        self.ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_btn)
        
        self.undo_once_btn = QPushButton("Undo Once")
        self.undo_once_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.undo_once_btn.clicked.connect(self.on_undo_once_clicked)
        buttons_layout.addWidget(self.undo_once_btn)

        self.undo_all_btn = QPushButton("Undo All")
        self.undo_all_btn.setStyleSheet("background-color: #F44336; color: white;")
        self.undo_all_btn.clicked.connect(self.on_undo_all_clicked)
        buttons_layout.addWidget(self.undo_all_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
     ######### Mayur Wakhare 5-7-2026 tunnel verify button information board   
        # Connections to invalidate verify
        self.km_input.textChanged.connect(self.invalidate_verification)
        self.ch_input.textChanged.connect(self.invalidate_verification)
        self.text_input.textChanged.connect(self.invalidate_verification)
        self.speed_limit_input.textChanged.connect(self.invalidate_verification)
        ## Mayur Wakhare 6-7-2026 undo all tunnel info board 
        self.update_undo_state()

    def update_undo_state(self):
        has_multi = False
        if hasattr(self.parent, 'tunnel_info_board_batches'):
            has_multi = len(self.parent.tunnel_info_board_batches) > 0
            
        self.undo_once_btn.setEnabled(has_multi)
        self.undo_all_btn.setEnabled(has_multi)

    def on_undo_once_clicked(self):
        if hasattr(self.parent, 'undo_last_tunnel_info_board'):
            success = self.parent.undo_last_tunnel_info_board()
            if success:
                self.update_undo_state()

    def on_undo_all_clicked(self):
        if hasattr(self.parent, 'undo_all_tunnel_info_boards'):
            success = self.parent.undo_all_tunnel_info_boards()
            if success:
                self.update_undo_state()
###########################################################################################
    def invalidate_verification(self):
        self.verified = False
        self.ok_btn.setEnabled(False)
        self.summary_label.setText("Please verify placement.")
        self.summary_label.setStyleSheet("color: #D32F2F; font-size: 12px; font-weight: bold; padding: 5px;")

    def verify_placement(self):
        try:
            km = float(self.km_input.text() or 0.0)
            ch = float(self.ch_input.text() or 0.0)
            text_val = self.text_input.toPlainText().strip()
            
            if not text_val:
                raise ValueError("Display Text is required.")
                
            self.verified = True
            self.ok_btn.setEnabled(True)
            self.summary_label.setText("✅ Placement Verified")
            self.summary_label.setStyleSheet("color: #388E3C; font-size: 12px; font-weight: bold; padding: 5px;")
        except ValueError as e:
            self.invalidate_verification()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Verification Failed", str(e) if str(e) else "Please enter valid numeric values.")
#################################################################################################################
    def auto_populate(self):
        tunnel_found = False
        t_start_km = ""
        t_start_ch = ""
        
        if hasattr(self.parent, 'current_design_layer_path') and self.parent.current_design_layer_path:
            import os
            if os.path.exists(self.parent.current_design_layer_path):
                try:
                    from json_manager import DesignConstructionManager
                    m_data = DesignConstructionManager.load_master(self.parent.current_design_layer_path)
                    t_conf = m_data.get("design", {}).get("tunnel", {})
                    if t_conf and "start_km" in t_conf:
                        t_start_km = str(t_conf.get("start_km", ""))
                        t_start_ch = str(t_conf.get("start_chainage", ""))
                        tunnel_found = True
                except Exception:
                    pass

        if tunnel_found:
            def clean_str(val):
                return val[:-2] if val.endswith(".0") else val
            self.km_input.setText(clean_str(t_start_km))
            self.ch_input.setText(clean_str(t_start_ch))

    def get_data(self):
        ######### Mayur Wakhare 5-7-2026 tunnel verify button information board   
        if not self.verified:
            return None
            ##############################################################
        try:
            return {
                "km": float(self.km_input.text() or 0.0),
            ####### Mayur 5-7-2026 Tunnel information board   
                "chainage": float(self.ch_input.text() or 0.0),
                "display_text": self.text_input.toPlainText().strip(),
                "speed_limit": self.speed_limit_input.text().strip()
                ##################################################################
            }
        except ValueError:
            return None

class SpeedLimitBoardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Speed Limit Board")
        self.setModal(True)
        self.setMinimumWidth(320)
        self.parent = parent
        
        self.setStyleSheet("""
            QDialog { background-color: #F5F5F5; font-family: Segoe UI; }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QLineEdit { padding: 6px; border: 2px solid #BBB; border-radius: 6px; font-size: 13px; background-color: white; }
            QPushButton { padding: 8px; border-radius: 6px; font-weight: bold; font-size: 13px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel("Speed Limit Board")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1565C0;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(QLabel("KM:"), 0, 0)
        self.km_input = QLineEdit()
        grid.addWidget(self.km_input, 0, 1)

        grid.addWidget(QLabel("+"), 0, 2)
        self.ch_input = QLineEdit()
        grid.addWidget(self.ch_input, 0, 3)
        layout.addLayout(grid)
        
        speed_grid = QGridLayout()
        speed_grid.setSpacing(10)
        speed_grid.addWidget(QLabel("Speed Limit (km/h):"), 0, 0)
        self.speed_limit_input = QLineEdit()
        self.speed_limit_input.setText("80")
        speed_grid.addWidget(self.speed_limit_input, 0, 1)
        layout.addLayout(speed_grid)
        
        self.auto_populate()
        
        buttons_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)

    def auto_populate(self):
        tunnel_found = False
        t_start_km = ""
        t_start_ch = ""
        if hasattr(self.parent, 'current_design_layer_path') and self.parent.current_design_layer_path:
            import os
            if os.path.exists(self.parent.current_design_layer_path):
                try:
                    from json_manager import DesignConstructionManager
                    m_data = DesignConstructionManager.load_master(self.parent.current_design_layer_path)
                    t_conf = m_data.get("design", {}).get("tunnel", {})
                    if t_conf and "start_km" in t_conf:
                        t_start_km = str(t_conf.get("start_km", ""))
                        t_start_ch = str(t_conf.get("start_chainage", ""))
                        tunnel_found = True
                except Exception:
                    pass

        if tunnel_found:
            def clean_str(val):
                return val[:-2] if val.endswith(".0") else val
            self.km_input.setText(clean_str(t_start_km))
            self.ch_input.setText(clean_str(t_start_ch))

    def get_data(self):
        try:
            return {
                "km": float(self.km_input.text() or 0.0),
                "chainage": float(self.ch_input.text() or 0.0),
                "speed_limit": int(self.speed_limit_input.text() or 80)
            }
        except ValueError:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values for KM/Chainage.")
            return None

def create_board_dialog_class(class_name, title_text):
    class CustomBoardDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle(title_text)
            self.setModal(True)
            self.setMinimumWidth(320)
            self.parent = parent
            
            self.setStyleSheet("""
                QDialog { background-color: #F5F5F5; font-family: Segoe UI; }
                QLabel { font-size: 13px; color: #333; font-weight: bold; }
                QLineEdit { padding: 6px; border: 2px solid #BBB; border-radius: 6px; font-size: 13px; background-color: white; }
                QPushButton { padding: 8px; border-radius: 6px; font-weight: bold; font-size: 13px; }
            """)
            
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(12)
            
            title = QLabel(title_text)
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1565C0;")
            layout.addWidget(title)
            
            grid = QGridLayout()
            grid.setSpacing(10)
            grid.addWidget(QLabel("KM:"), 0, 0)
            self.km_input = QLineEdit()
            grid.addWidget(self.km_input, 0, 1)
            
            grid.addWidget(QLabel("+"), 0, 2)
            self.ch_input = QLineEdit()
            grid.addWidget(self.ch_input, 0, 3)
            layout.addLayout(grid)
            
            self.auto_populate()
            
            buttons_layout = QHBoxLayout()
            self.ok_btn = QPushButton("OK")
            self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
            self.ok_btn.clicked.connect(self.accept)
            buttons_layout.addWidget(self.ok_btn)
            
            self.cancel_btn = QPushButton("Cancel")
            self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
            self.cancel_btn.clicked.connect(self.reject)
            buttons_layout.addWidget(self.cancel_btn)
            
            layout.addLayout(buttons_layout)
            
        def auto_populate(self):
            tunnel_found = False
            t_start_km = ""
            t_start_ch = ""
            if hasattr(self.parent, 'current_design_layer_path') and self.parent.current_design_layer_path:
                import os
                if os.path.exists(self.parent.current_design_layer_path):
                    try:
                        from json_manager import DesignConstructionManager
                        m_data = DesignConstructionManager.load_master(self.parent.current_design_layer_path)
                        t_conf = m_data.get("design", {}).get("tunnel", {})
                        if t_conf and "start_km" in t_conf:
                            t_start_km = str(t_conf.get("start_km", ""))
                            t_start_ch = str(t_conf.get("start_chainage", ""))
                            tunnel_found = True
                    except Exception:
                        pass
            
            if tunnel_found:
                def clean_str(val):
                    return val[:-2] if val.endswith(".0") else val
                self.km_input.setText(clean_str(t_start_km))
                self.ch_input.setText(clean_str(t_start_ch))
                
        def get_data(self):
            try:
                return {
                    "km": float(self.km_input.text() or 0.0),
                    "chainage": float(self.ch_input.text() or 0.0)
                }
            except ValueError:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values for KM/Chainage.")
                return None
    CustomBoardDialog.__name__ = class_name
    return CustomBoardDialog

EmergencyExitBoardDialog = create_board_dialog_class("EmergencyExitBoardDialog", "Emergency Exit Board")
FireExtinguisherDirBoardDialog = create_board_dialog_class("FireExtinguisherDirBoardDialog", "Fire Extinguisher Direction Board")
CCTVSurveillanceBoardDialog = create_board_dialog_class("CCTVSurveillanceBoardDialog", "CCTV Surveillance Board")
HeadlightsONBoardDialog = create_board_dialog_class("HeadlightsONBoardDialog", "Headlights ON Board")
NoOvertakingBoardDialog = create_board_dialog_class("NoOvertakingBoardDialog", "No Overtaking Board")
ExitDistanceBoardDialog = create_board_dialog_class("ExitDistanceBoardDialog", "Exit Distance Board")
###############################################################
###### Mayur Wakhare 6-7-2026 Telephone dailog box tunnel
class EmergencyTelephoneBoardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Emergency Telephone Board")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.parent = parent
        self.verified = False
        
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QLineEdit, QDoubleSpinBox {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Emergency Telephone Board")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D32F2F;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Start KM:"), 0, 0)
        self.start_km_input = QLineEdit()
        grid.addWidget(self.start_km_input, 0, 1)

        grid.addWidget(QLabel("+"), 0, 2)
        self.start_ch_input = QLineEdit()
        grid.addWidget(self.start_ch_input, 0, 3)

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 6px; font-weight: bold; border-radius: 4px;")
        grid.addWidget(self.verify_btn, 1, 0, 1, 4)
        self.verify_btn.clicked.connect(self.verify_chainage)
        
        layout.addLayout(grid)

        # ── Installation Side ──
        self.side_group = QGroupBox("Installation Side")
        self.side_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        self.side_group.setEnabled(False)
        side_layout = QHBoxLayout(self.side_group)
        
        from PyQt5.QtWidgets import QRadioButton
        self.left_side_rb = QRadioButton("Left")
        self.right_side_rb = QRadioButton("Right")
        self.left_side_rb.setChecked(True)
        
        side_layout.addWidget(self.left_side_rb)
        side_layout.addWidget(self.right_side_rb)
        
        layout.addWidget(self.side_group)

        # Board Settings
        settings_grid = QGridLayout()
        settings_grid.addWidget(QLabel("Board Height from Ground (m):"), 0, 0)
        self.height_input = QLineEdit("2.3")
        settings_grid.addWidget(self.height_input, 0, 1)

        settings_grid.addWidget(QLabel("Display Text:"), 1, 0)
        self.display_text_input = QLineEdit("EMERGENCY TELEPHONE")
        settings_grid.addWidget(self.display_text_input, 1, 1)
        
        layout.addLayout(settings_grid)

        # ── Placement Summary (read-only preview) ──
        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(
            "background-color: #FFEBEE; border: 1px solid #FFCDD2; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #333; font-weight: normal;"
        )
        layout.addWidget(self.summary_label)

        # OK / Cancel
        buttons_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)
        buttons_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)

        # ── Auto-populate chainage from tunnel ──
        tunnel_found = False
        t_start_km, t_start_ch = "", ""
        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        import os
        if layer_folder and os.path.exists(layer_folder):
            try:
                from json_manager import DesignConstructionManager
                m_data = DesignConstructionManager.load_master(layer_folder)
                t_conf = m_data.get("design", {}).get("tunnel", {})
                if t_conf and "start_km" in t_conf:
                    t_start_km = str(t_conf.get("start_km", ""))
                    t_start_ch = str(t_conf.get("start_chainage", ""))
                    tunnel_found = True
            except Exception:
                pass
                
        if tunnel_found:
            def clean_str(val):
                return val[:-2] if val.endswith(".0") else val
                
            self.start_km_input.setText(clean_str(t_start_km))
            self.start_ch_input.setText(clean_str(t_start_ch))
            
        # Connections for live update
        self.start_km_input.textChanged.connect(self.invalidate_verification)
        self.start_ch_input.textChanged.connect(self.invalidate_verification)

        self.left_side_rb.toggled.connect(self.update_summary)
        self.right_side_rb.toggled.connect(self.update_summary)
        
        self.update_summary()

    def invalidate_verification(self):
        self.verified = False
        self.ok_btn.setEnabled(False)
        self.side_group.setEnabled(False)
        self.summary_label.setText("Please Verify chainage location first.")
        self.summary_label.setStyleSheet(
            "background-color: #FFF3E0; border: 1px solid #FFE0B2; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #E65100; font-weight: normal;"
        )

    def verify_chainage(self):
        from PyQt5.QtWidgets import QMessageBox
        import os
        try:
            s_km = float(self.start_km_input.text() or 0.0)
            s_ch = float(self.start_ch_input.text() or 0.0)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values for KM and Chainage.")
            return

        start_abs = s_km * 1000 + s_ch

        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        if layer_folder and os.path.exists(layer_folder):
            from json_manager import DesignConstructionManager
            master_data = DesignConstructionManager.load_master(layer_folder)
            tunnel_data = master_data.get("design", {}).get("tunnel")
            if tunnel_data:
                ts_km = tunnel_data.get("start_km", 0.0)
                ts_ch = tunnel_data.get("start_chainage", 0.0)
                te_km = tunnel_data.get("end_km", 0.0)
                te_ch = tunnel_data.get("end_chainage", 0.0)
                t_start = ts_km * 1000 + ts_ch
                t_end = te_km * 1000 + te_ch

                if start_abs < t_start or start_abs > t_end:
                    QMessageBox.warning(self, "Out of Bounds", f"Location {start_abs} is outside tunnel limits ({t_start} - {t_end}).")
                    return
        
        self.verified = True
        self.side_group.setEnabled(True)
        self.ok_btn.setEnabled(True)
        self.update_summary()
        QMessageBox.information(self, "Verified", "Chainage location successfully verified.")

    def update_summary(self):
        if not self.verified:
            self.invalidate_verification()
            return
            
        self.summary_label.setStyleSheet(
            "background-color: #E8F5E9; border: 1px solid #C8E6C9; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #2E7D32; font-weight: bold;"
        )
        self.summary_label.setText("✅ Ready to Place\n\n1 Emergency Telephone Board will be created.")

    def get_data(self):
        if not self.verified:
            return None
            
        try:
            if self.left_side_rb.isChecked():
                side = "left"
            else:
                side = "right"
                
            return {
                "start_km": float(self.start_km_input.text() or 0.0),
                "start_chainage": float(self.start_ch_input.text() or 0.0),
                "display_text": self.display_text_input.text(),
                "installation_side": side,
                "height_from_ground": float(self.height_input.text() or 2.3)
            }
        except ValueError:
            return None
            ############################################################################################
##### Mayur Wakhare 6-7-2026 tunnel fan 
class TunnelExhaustFanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tunnel Exhaust Fan")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.parent = parent
        self.verified = False
        
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Tunnel Exhaust Fan")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D32F2F;")
        layout.addWidget(title)

        # ── Tunnel Selection ──
        tunnel_sel_group = QGroupBox("Tunnel Selection")
        tunnel_sel_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        tunnel_sel_layout = QHBoxLayout(tunnel_sel_group)
        tunnel_sel_layout.addWidget(QLabel("Tunnel ID:"))
        self.tunnel_combo = QComboBox()
        self.tunnel_combo.setStyleSheet("padding: 4px; border: 1px solid #BBB; border-radius: 4px;")
        tunnel_sel_layout.addWidget(self.tunnel_combo)
        layout.addWidget(tunnel_sel_group)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Start KM:"), 0, 0)
        self.start_km_input = QLineEdit()
        grid.addWidget(self.start_km_input, 0, 1)

        grid.addWidget(QLabel("+"), 0, 2)
        self.start_ch_input = QLineEdit()
        grid.addWidget(self.start_ch_input, 0, 3)

        grid.addWidget(QLabel("End KM:"), 1, 0)
        self.end_km_input = QLineEdit()
        grid.addWidget(self.end_km_input, 1, 1)

        grid.addWidget(QLabel("+"), 1, 2)
        self.end_ch_input = QLineEdit()
        grid.addWidget(self.end_ch_input, 1, 3)

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 6px; font-weight: bold; border-radius: 4px;")
        grid.addWidget(self.verify_btn, 2, 0, 1, 4)
        self.verify_btn.clicked.connect(self.verify_chainage)
        
        layout.addLayout(grid)

        # Main controls container (enabled after verify)
        self.controls_widget = QWidget()
        controls_layout = QVBoxLayout(self.controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_widget.setEnabled(False)

        # ── Installation Type ──
        self.inst_type_group = QGroupBox("Installation Type")
        self.inst_type_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        inst_type_layout = QHBoxLayout(self.inst_type_group)
        
        from PyQt5.QtWidgets import QRadioButton, QStackedWidget, QSpinBox, QDoubleSpinBox
        self.pair_inst_rb = QRadioButton("Pair Installation")
        self.single_inst_rb = QRadioButton("Single Installation")
        self.pair_inst_rb.setChecked(True)
        
        inst_type_layout.addWidget(self.pair_inst_rb)
        inst_type_layout.addWidget(self.single_inst_rb)
        controls_layout.addWidget(self.inst_type_group)

        # Stack for Pair / Single settings
        self.settings_stack = QStackedWidget()
        
        # --- Pair Settings ---
        self.pair_widget = QWidget()
        pair_layout = QGridLayout(self.pair_widget)
        
        pair_layout.addWidget(QLabel("Number of Pairs:"), 0, 0)
        self.num_pairs_input = QSpinBox()
        self.num_pairs_input.setRange(1, 100)
        self.num_pairs_input.setValue(2)
        pair_layout.addWidget(self.num_pairs_input, 0, 1)
        
        pair_layout.addWidget(QLabel("Distance Between Pairs (m):"), 1, 0)
        self.dist_between_pairs_input = QDoubleSpinBox()
        self.dist_between_pairs_input.setRange(1.0, 5000.0)
        self.dist_between_pairs_input.setMaximum(5000.0)
        self.dist_between_pairs_input.setValue(250.0)
        pair_layout.addWidget(self.dist_between_pairs_input, 1, 1)
        
        pair_layout.addWidget(QLabel("Distance Between Fans in a Pair (m):"), 2, 0)
        self.dist_in_pair_input = QDoubleSpinBox()
        self.dist_in_pair_input.setRange(0.5, 50.0)
        self.dist_in_pair_input.setValue(5.0)
        pair_layout.addWidget(self.dist_in_pair_input, 2, 1)
        
        pair_layout.addWidget(QLabel("Pair Arrangement:"), 3, 0)
        self.pair_arrange_layout = QHBoxLayout()
        self.side_by_side_rb = QRadioButton("Side by Side")
        self.inline_rb = QRadioButton("Inline")
        self.side_by_side_rb.setChecked(True)
        self.pair_arrange_layout.addWidget(self.side_by_side_rb)
        self.pair_arrange_layout.addWidget(self.inline_rb)
        pair_layout.addLayout(self.pair_arrange_layout, 3, 1)
        
        self.settings_stack.addWidget(self.pair_widget)
        
        # --- Single Settings ---
        self.single_widget = QWidget()
        single_layout = QGridLayout(self.single_widget)
        
        single_layout.addWidget(QLabel("Number of Fans:"), 0, 0)
        self.num_fans_input = QSpinBox()
        self.num_fans_input.setRange(1, 100)
        self.num_fans_input.setValue(4)
        single_layout.addWidget(self.num_fans_input, 0, 1)
        
        single_layout.addWidget(QLabel("Spacing Between Fans (m):"), 1, 0)
        self.spacing_fans_input = QDoubleSpinBox()
        self.spacing_fans_input.setRange(1.0, 5000.0)
        self.spacing_fans_input.setMaximum(5000.0)
        self.spacing_fans_input.setValue(120.0)
        single_layout.addWidget(self.spacing_fans_input, 1, 1)
        
        single_layout.setRowStretch(2, 1) # pad layout
        
        self.settings_stack.addWidget(self.single_widget)
        
        controls_layout.addWidget(self.settings_stack)

        # ── Global Settings ──
        global_grid = QGridLayout()
        
        global_grid.addWidget(QLabel("Airflow Direction:"), 0, 0)
        self.airflow_layout = QHBoxLayout()
        self.towards_exit_rb = QRadioButton("Towards Tunnel Exit")
        self.towards_entry_rb = QRadioButton("Towards Tunnel Entry")
        self.towards_exit_rb.setChecked(True)
        self.airflow_layout.addWidget(self.towards_exit_rb)
        self.airflow_layout.addWidget(self.towards_entry_rb)
        global_grid.addLayout(self.airflow_layout, 0, 1)
        
        global_grid.addWidget(QLabel("Ceiling Offset (m):"), 1, 0)
        self.ceiling_offset_input = QDoubleSpinBox()
        self.ceiling_offset_input.setRange(0.0, 5.0)
        self.ceiling_offset_input.setSingleStep(0.1)
        self.ceiling_offset_input.setValue(0.40)
        global_grid.addWidget(self.ceiling_offset_input, 1, 1)

        controls_layout.addLayout(global_grid)
        layout.addWidget(self.controls_widget)

        # ── Placement Summary (read-only preview) ──
        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(
            "background-color: #FFEBEE; border: 1px solid #FFCDD2; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #333; font-weight: normal;"
        )
        layout.addWidget(self.summary_label)

        # OK / Cancel / Undo
        buttons_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)
        buttons_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        ### Mayur Wakhare 7-7-2026 undo jet fan tunnel
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.undo_btn.clicked.connect(self.on_undo_clicked)
        # Enable if there's an undo state
        has_undo_state = bool(getattr(self.parent, 'last_jet_fan_undo_state', None))
        self.undo_btn.setEnabled(has_undo_state)
        buttons_layout.addWidget(self.undo_btn)
       ########################################################################## 
        layout.addLayout(buttons_layout)

        # ── Scan and populate tunnels from all active design layers ──
        self.available_tunnels = []
        self._populate_tunnels()

        # Connections for live update
        self.start_km_input.textChanged.connect(self.invalidate_verification)
        self.start_ch_input.textChanged.connect(self.invalidate_verification)
        self.end_km_input.textChanged.connect(self.invalidate_verification)
        self.end_ch_input.textChanged.connect(self.invalidate_verification)

        self.tunnel_combo.currentIndexChanged.connect(self._on_tunnel_selected)
        self.pair_inst_rb.toggled.connect(self.toggle_mode)
        self.num_pairs_input.valueChanged.connect(self.update_summary)
        self.num_fans_input.valueChanged.connect(self.update_summary)

        # Auto-select first tunnel if available
        if self.available_tunnels:
            self._on_tunnel_selected(0)
        else:
            self.update_summary()
## Mauyur 21-7-2026 
    def _populate_tunnels(self):
        """Scan all active design layers for tunnel configurations and populate the dropdown."""
        import os
        import json
        if not self.parent:
            return

        active_layer_paths = list(getattr(self.parent, '_per_layer_actors', {}).keys())
        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        if layer_folder and os.path.exists(layer_folder) and layer_folder not in active_layer_paths:
            active_layer_paths.append(layer_folder)

        subfolder = getattr(self.parent, 'current_subfolder_type', 'designs')
        config_paths = []

        for p in active_layer_paths:
            if not p or not isinstance(p, str) or not os.path.exists(p):
                continue
            is_merger = False
            if "merger" in p.lower() or subfolder == "merger":
                merger_jsons = [f for f in os.listdir(p) if f.endswith('.json')]
                for mj in merger_jsons:
                    try:
                        with open(os.path.join(p, mj), 'r', encoding='utf-8') as f:
                            merger_data = json.load(f)
                        if "merger_points" in merger_data:
                            is_merger = True
                            for pt in merger_data.get("merger_points", []):
                                def add_cfg(json_file_path):
                                    if json_file_path:
                                        d_path = os.path.dirname(json_file_path)
                                        cfg = os.path.join(d_path, 'design_construction_config.json')
                                        if os.path.exists(cfg) and cfg not in config_paths:
                                            config_paths.append(cfg)
                                add_cfg(pt.get("primary_json_path"))
                                for lyr in pt.get("layers", []):
                                    add_cfg(lyr.get("json_path"))
                    except Exception:
                        pass
            if not is_merger:
                cfg = os.path.join(p, 'design_construction_config.json')
                if os.path.exists(cfg) and cfg not in config_paths:
                    config_paths.append(cfg)

        found_tunnels = []
        for cp in config_paths:
            try:
                with open(cp, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                tunnel_obj = data.get('design', {}).get('tunnel')
                if not tunnel_obj:
                    zero_config = data.get('design', {}).get('zero_line_config')
                    if zero_config:
                        tunnel_obj = {
                            'id': 'fallback_tunnel',
                            'start_km': zero_config.get('point1', {}).get('from_km', 0),
                            'start_chainage': zero_config.get('point1', {}).get('from_chainage', 0),
                            'end_km': zero_config.get('point2', {}).get('to_km', 0),
                            'end_chainage': zero_config.get('point2', {}).get('to_chainage', 0)
                        }
                if tunnel_obj and isinstance(tunnel_obj, dict):
                    tunnel_obj['source_layer_folder'] = os.path.dirname(cp)
                    found_tunnels.append(tunnel_obj)
            except Exception:
                pass

        unique_tunnels = {}
        for t in found_tunnels:
            tid = t.get('tunnel_id', t.get('id', 'Unknown'))
            t_layer_folder = t.get('source_layer_folder', '')
            layer_name = os.path.basename(t_layer_folder) if t_layer_folder else 'Unknown'
            key = (layer_name, tid)
            if key not in unique_tunnels:
                unique_tunnels[key] = (t, layer_name, tid)

        self.available_tunnels = list(unique_tunnels.values())

        self.tunnel_combo.blockSignals(True)
        self.tunnel_combo.clear()
        if self.available_tunnels:
            for t, layer_name, tid in self.available_tunnels:
                display_text = f"{tid} ({layer_name})"
                self.tunnel_combo.addItem(display_text)
        else:
            self.tunnel_combo.addItem("No Tunnel Found")
            # Disable all controls when no tunnel exists
            self.start_km_input.setEnabled(False)
            self.start_ch_input.setEnabled(False)
            self.end_km_input.setEnabled(False)
            self.end_ch_input.setEnabled(False)
            self.verify_btn.setEnabled(False)
            self.controls_widget.setEnabled(False)
            self.ok_btn.setEnabled(False)
        self.tunnel_combo.blockSignals(False)

    def _on_tunnel_selected(self, index):
        """Handle tunnel selection — auto-fill KM/Chainage and auto-verify."""
        if index < 0 or index >= len(self.available_tunnels):
            return
        t, layer_name, tid = self.available_tunnels[index]

        def clean_str(val):
            val = str(val)
            return val[:-2] if val.endswith(".0") else val

        # Block signals to avoid invalidate_verification while auto-populating
        self.start_km_input.blockSignals(True)
        self.start_ch_input.blockSignals(True)
        self.end_km_input.blockSignals(True)
        self.end_ch_input.blockSignals(True)

        self.start_km_input.setText(clean_str(t.get('start_km', '0')))
        self.start_ch_input.setText(clean_str(t.get('start_chainage', '0')))
        self.end_km_input.setText(clean_str(t.get('end_km', '0')))
        self.end_ch_input.setText(clean_str(t.get('end_chainage', '0')))

        self.start_km_input.blockSignals(False)
        self.start_ch_input.blockSignals(False)
        self.end_km_input.blockSignals(False)
        self.end_ch_input.blockSignals(False)

        # Auto-verify (same behavior as the existing Verify functionality)
        self.verified = True
        self.controls_widget.setEnabled(True)
        self.ok_btn.setEnabled(True)
        self.update_summary()

    def toggle_mode(self):
        if self.pair_inst_rb.isChecked():
            self.settings_stack.setCurrentIndex(0)
        else:
            self.settings_stack.setCurrentIndex(1)
        self.update_summary()

    def invalidate_verification(self):
        self.verified = False
        self.ok_btn.setEnabled(False)
        self.controls_widget.setEnabled(False)
        self.summary_label.setText("Please Verify chainage location first.")
        self.summary_label.setStyleSheet(
            "background-color: #FFF3E0; border: 1px solid #FFE0B2; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #E65100; font-weight: normal;"
        )
### Mayur 21-7-2026
    def verify_chainage(self):
        from PyQt5.QtWidgets import QMessageBox
        try:
            s_km = float(self.start_km_input.text() or 0.0)
            s_ch = float(self.start_ch_input.text() or 0.0)
            e_km = float(self.end_km_input.text() or 0.0)
            e_ch = float(self.end_ch_input.text() or 0.0)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values for KM and Chainage.")
            return

        start_abs = s_km * 1000 + s_ch
        end_abs = e_km * 1000 + e_ch

       
        # Validate against the currently selected tunnel
        idx = self.tunnel_combo.currentIndex()
        if idx >= 0 and idx < len(self.available_tunnels):
            t_data, _, _ = self.available_tunnels[idx]
            ts_km = float(t_data.get("start_km", 0.0))
            ts_ch = float(t_data.get("start_chainage", 0.0))
            te_km = float(t_data.get("end_km", 0.0))
            te_ch = float(t_data.get("end_chainage", 0.0))
            t_start = ts_km * 1000 + ts_ch
            t_end = te_km * 1000 + te_ch

            if start_abs < t_start or start_abs > t_end or end_abs < t_start or end_abs > t_end:
                QMessageBox.warning(self, "Out of Bounds", f"Locations must be within tunnel limits ({t_start} - {t_end}).")
                return
            if start_abs >= end_abs:
                QMessageBox.warning(self, "Invalid Range", "Start chainage must be less than End chainage.")
                return

        self.verified = True
        self.controls_widget.setEnabled(True)
        self.ok_btn.setEnabled(True)
        self.update_summary()
        QMessageBox.information(self, "Verified", "Chainage location successfully verified.")

    def update_summary(self):
        if not self.verified:
            self.invalidate_verification()
            return
            
        self.summary_label.setStyleSheet(
            "background-color: #E8F5E9; border: 1px solid #C8E6C9; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #2E7D32; font-weight: bold;"
        )
        if self.pair_inst_rb.isChecked():
            total = self.num_pairs_input.value() * 2
        else:
            total = self.num_fans_input.value()
            
        self.summary_label.setText(f"✅ Ready to Place\n\nTotal Fans : {total}")

    def get_data(self):
        if not self.verified:
            return None
            
        try:
            ### Mayur 21-7-2026
            idx = self.tunnel_combo.currentIndex()
            t_id = "Unknown"
            l_name = "Unknown"
            t_obj = {}
            if idx >= 0 and idx < len(self.available_tunnels):
                t_obj, l_name, t_id = self.available_tunnels[idx]
            ########################################################
            data = {
                "start_km": float(self.start_km_input.text() or 0.0),
                "start_chainage": float(self.start_ch_input.text() or 0.0),
                "end_km": float(self.end_km_input.text() or 0.0),
                "end_chainage": float(self.end_ch_input.text() or 0.0),
                "airflow_direction": "exit" if self.towards_exit_rb.isChecked() else "entry",
            # Mayur 21-7-2026
                "ceiling_offset": float(self.ceiling_offset_input.value()),
                "tunnel_id": t_id,
                "layer_name": l_name,
                "source_layer_folder": t_obj.get("source_layer_folder", "")
            }
            if self.pair_inst_rb.isChecked():
                data["installation_type"] = "pair"
                data["num_pairs"] = self.num_pairs_input.value()
                data["distance_between_pairs"] = self.dist_between_pairs_input.value()
                data["distance_in_pair"] = self.dist_in_pair_input.value()
                data["pair_arrangement"] = "side_by_side" if self.side_by_side_rb.isChecked() else "inline"
            else:
                data["installation_type"] = "single"
                data["num_fans"] = self.num_fans_input.value()
                data["spacing_fans"] = self.spacing_fans_input.value()
                
            return data
        except ValueError:
            return None

    def on_undo_clicked(self):
        """Handle Undo button click."""
        if hasattr(self.parent, 'undo_last_jet_fan_placement'):
            success = self.parent.undo_last_jet_fan_placement()
            if success:
                self.undo_btn.setEnabled(False)
            ##############################################################################################

###############################################################
### Mayur Wakhare 7-7-2026 pipe dailog box tunnel
class WaterPipeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Water Pipe")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.parent = parent
        self.verified = False
        
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QLineEdit {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Water Pipe")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        layout.addWidget(title)
        
        # ── Tunnel Information Section ──
        from PyQt5.QtWidgets import QGroupBox, QComboBox, QHBoxLayout
        tunnel_info_group = QGroupBox("Tunnel Information")
        tunnel_info_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        tunnel_info_layout = QHBoxLayout(tunnel_info_group)
        
        tunnel_info_layout.addWidget(QLabel("Tunnel ID:"))
        self.tunnel_combo = QComboBox()
        self.tunnel_combo.setStyleSheet("padding: 4px; border: 1px solid #BBB; border-radius: 4px;")
        tunnel_info_layout.addWidget(self.tunnel_combo)
        layout.addWidget(tunnel_info_group)
        
        self.tunnel_combo.currentIndexChanged.connect(self._on_tunnel_selected)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Start KM:"), 0, 0)
        self.start_km_input = QLineEdit()
        grid.addWidget(self.start_km_input, 0, 1)

        grid.addWidget(QLabel("+"), 0, 2)
        self.start_ch_input = QLineEdit()
        grid.addWidget(self.start_ch_input, 0, 3)

        grid.addWidget(QLabel("End KM:"), 1, 0)
        self.end_km_input = QLineEdit()
        grid.addWidget(self.end_km_input, 1, 1)

        grid.addWidget(QLabel("+"), 1, 2)
        self.end_ch_input = QLineEdit()
        grid.addWidget(self.end_ch_input, 1, 3)

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 6px; font-weight: bold; border-radius: 4px;")
        grid.addWidget(self.verify_btn, 2, 0, 1, 4)
        self.verify_btn.clicked.connect(self.verify_chainage)
        
        layout.addLayout(grid)

        # ── Controls Area (Disabled until verified) ──
        self.controls_widget = QWidget()
        controls_layout = QVBoxLayout(self.controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)
        self.controls_widget.setEnabled(False)

        # ── Installation Side ──
        self.side_group = QGroupBox("Installation Side")
        self.side_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        side_layout = QHBoxLayout(self.side_group)
        
        from PyQt5.QtWidgets import QRadioButton
        self.left_side_rb = QRadioButton("Left (Default)")
        self.right_side_rb = QRadioButton("Right")
        self.left_side_rb.setChecked(True)
        
        side_layout.addWidget(self.left_side_rb)
        side_layout.addWidget(self.right_side_rb)
        controls_layout.addWidget(self.side_group)

        # ── Dimensions Grid ──
        dim_grid = QGridLayout()
        dim_grid.setSpacing(10)

        dim_grid.addWidget(QLabel("Height From Ground:"), 0, 0)
        self.height_input = QLineEdit()
        self.height_input.setText("2.50")
        dim_grid.addWidget(self.height_input, 0, 1)
        dim_grid.addWidget(QLabel("m"), 0, 2)

        dim_grid.addWidget(QLabel("Wall Offset:"), 1, 0)
        self.wall_offset_input = QLineEdit()
        self.wall_offset_input.setText("0.08")
        dim_grid.addWidget(self.wall_offset_input, 1, 1)
        dim_grid.addWidget(QLabel("m"), 1, 2)

        dim_grid.addWidget(QLabel("Pipe Diameter:"), 2, 0)
        self.diameter_input = QLineEdit()
      ### Mayur wakhare 7-7-2026 pipe daimeter 
        self.diameter_input.setText("500")
        dim_grid.addWidget(self.diameter_input, 2, 1)
        dim_grid.addWidget(QLabel("mm"), 2, 2)

        controls_layout.addLayout(dim_grid)

        # ── Pipe Color ──
        self.color_group = QGroupBox("Pipe Color")
        self.color_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        color_layout = QHBoxLayout(self.color_group)
        
        self.color_red_rb = QRadioButton("Fire Red")
        self.color_custom_rb = QRadioButton("Custom")
        self.color_red_rb.setChecked(True)
        
        color_layout.addWidget(self.color_red_rb)
        color_layout.addWidget(self.color_custom_rb)
        controls_layout.addWidget(self.color_group)

        layout.addWidget(self.controls_widget)
        
        # ── Placement Summary (read-only preview) ──
        self.summary_label = QLabel("Pipe Length : Auto\nTunnel Length : Auto")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(
            "background-color: #FFEBEE; border: 1px solid #FFCDD2; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #333; font-weight: normal;"
        )
        layout.addWidget(self.summary_label)

        # OK / Cancel / Undo
        buttons_layout = QHBoxLayout()
        
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.undo_btn.clicked.connect(self.on_undo_clicked)
        buttons_layout.addWidget(self.undo_btn)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)
        buttons_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)

      ## Mayur 18-7-2026 
        # ── Auto-populate chainage from tunnels ──
        self.available_tunnels = []
        self._populate_tunnels()

        self.start_km_input.textChanged.connect(self.invalidate_verification)
        self.start_ch_input.textChanged.connect(self.invalidate_verification)
        self.end_km_input.textChanged.connect(self.invalidate_verification)
        self.end_ch_input.textChanged.connect(self.invalidate_verification)
        ####################################################
### Mayur 18-7-2026 tunnel seperate add
    def _populate_tunnels(self):
        import os
        import json
        if not self.parent:
            return
            
        active_layer_paths = list(getattr(self.parent, '_per_layer_actors', {}).keys())
        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        if layer_folder and os.path.exists(layer_folder) and layer_folder not in active_layer_paths:
            active_layer_paths.append(layer_folder)
            
        subfolder = getattr(self.parent, 'current_subfolder_type', 'designs')
        config_paths = []
        
        for p in active_layer_paths:
            if not p or not isinstance(p, str) or not os.path.exists(p):
                continue
            is_merger = False
            if "merger" in p.lower() or subfolder == "merger":
                merger_jsons = [f for f in os.listdir(p) if f.endswith('.json')]
                for mj in merger_jsons:
                    try:
                        with open(os.path.join(p, mj), 'r', encoding='utf-8') as f:
                            merger_data = json.load(f)
                        if "merger_points" in merger_data:
                            is_merger = True
                            for pt in merger_data.get("merger_points", []):
                                def add_cfg(json_file_path):
                                    if json_file_path:
                                        d_path = os.path.dirname(json_file_path)
                                        cfg = os.path.join(d_path, 'design_construction_config.json')
                                        if os.path.exists(cfg) and cfg not in config_paths:
                                            config_paths.append(cfg)
                                add_cfg(pt.get("primary_json_path"))
                                for lyr in pt.get("layers", []):
                                    add_cfg(lyr.get("json_path"))
                                
                    except Exception:
                        pass
            if not is_merger:
                cfg = os.path.join(p, 'design_construction_config.json')
                if os.path.exists(cfg) and cfg not in config_paths:
                    config_paths.append(cfg)
                    
        found_tunnels = []
        for cp in config_paths:
            try:
                with open(cp, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                tunnel_obj = data.get('design', {}).get('tunnel')
                if not tunnel_obj:
                    zero_config = data.get('design', {}).get('zero_line_config')
                    if zero_config:
                        tunnel_obj = {
                            'id': 'fallback_tunnel',
                            'start_km': zero_config.get('point1', {}).get('from_km', 0),
                            'start_chainage': zero_config.get('point1', {}).get('from_chainage', 0),
                            'end_km': zero_config.get('point2', {}).get('to_km', 0),
                            'end_chainage': zero_config.get('point2', {}).get('to_chainage', 0)
                        }
                if tunnel_obj and isinstance(tunnel_obj, dict):
                    tunnel_obj['source_layer_folder'] = os.path.dirname(cp)
                    found_tunnels.append(tunnel_obj)
            except Exception:
                pass
                
        unique_tunnels = {}
        for t in found_tunnels:
            tid = t.get('tunnel_id', t.get('id', 'Unknown'))
            layer_folder = t.get('source_layer_folder', '')
            layer_name = os.path.basename(layer_folder) if layer_folder else 'Unknown'
            key = (layer_name, tid)
            if key not in unique_tunnels:
                unique_tunnels[key] = (t, layer_name, tid)
                
        self.available_tunnels = list(unique_tunnels.values())
        
        self.tunnel_combo.blockSignals(True)
        self.tunnel_combo.clear()
        for t, layer_name, tid in self.available_tunnels:
            display_text = f"{tid} ({layer_name})"
            self.tunnel_combo.addItem(display_text)
        self.tunnel_combo.blockSignals(False)
        
        self.start_km_input.textChanged.connect(self.invalidate_verification)
        self.start_ch_input.textChanged.connect(self.invalidate_verification)
        self.end_km_input.textChanged.connect(self.invalidate_verification)
        self.end_ch_input.textChanged.connect(self.invalidate_verification)
        
        if self.available_tunnels:
            self._on_tunnel_selected(0)

    def _on_tunnel_selected(self, index):
        if index < 0 or index >= len(self.available_tunnels):
            return
        t, layer_name, tid = self.available_tunnels[index]
        
        def clean_str(val):
            val = str(val)
            return val[:-2] if val.endswith(".0") else val
            
        self.start_km_input.setText(clean_str(t.get('start_km', '0')))
        self.start_ch_input.setText(clean_str(t.get('start_chainage', '0')))
        self.end_km_input.setText(clean_str(t.get('end_km', '0')))
        self.end_ch_input.setText(clean_str(t.get('end_chainage', '0')))
        self.invalidate_verification()
#####################################################################################################
    def invalidate_verification(self):
        self.verified = False
        self.ok_btn.setEnabled(False)
        self.controls_widget.setEnabled(False)
        self.summary_label.setText("Pipe Length : Auto\nTunnel Length : Auto")
        self.summary_label.setStyleSheet(
            "background-color: #FFEBEE; border: 1px solid #FFCDD2; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #333; font-weight: normal;"
        )
##### Mayur 18-7-2026 
    def verify_chainage(self):
        from PyQt5.QtWidgets import QMessageBox
        import os
        try:
            s_km = float(self.start_km_input.text() or 0.0)
            s_ch = float(self.start_ch_input.text() or 0.0)
            e_km = float(self.end_km_input.text() or 0.0)
            e_ch = float(self.end_ch_input.text() or 0.0)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values for KM and Chainage.")
            return

        start_abs = s_km * 1000 + s_ch
        end_abs = e_km * 1000 + e_ch

        idx = self.tunnel_combo.currentIndex()
        if idx < 0 or idx >= len(self.available_tunnels):
            QMessageBox.warning(self, "No Tunnel", "No valid tunnel selected for verification.")
            return

        t_data, layer_name, tid = self.available_tunnels[idx]
        
        ts_km = float(t_data.get("start_km", 0.0))
        ts_ch = float(t_data.get("start_chainage", 0.0))
        te_km = float(t_data.get("end_km", 0.0))
        te_ch = float(t_data.get("end_chainage", 0.0))
        
        t_start = ts_km * 1000 + ts_ch
        t_end = te_km * 1000 + te_ch

        print("\n--- Water Pipe Verify Debug ---")
        print(f"Selected Tunnel ID: {tid}")
        print(f"Selected Layer: {layer_name}")
        print(f"Tunnel Start Chainage: {t_start}")
        print(f"Tunnel End Chainage: {t_end}")
        print(f"Verify Range: {t_start} - {t_end}")
        print(f"Entered Chainage: {start_abs} - {end_abs}")
        print("-------------------------------\n")

        if start_abs < t_start or start_abs > t_end or end_abs < t_start or end_abs > t_end:
            QMessageBox.warning(self, "Out of Bounds", f"Locations must be within tunnel limits ({t_start} - {t_end}).")
            return
        if start_abs >= end_abs:
            QMessageBox.warning(self, "Invalid Range", "Start chainage must be less than End chainage.")
            return
        
        self.verified = True
        self.controls_widget.setEnabled(True)
        self.ok_btn.setEnabled(True)
        length = end_abs - start_abs
        self.summary_label.setText(f"Pipe Length : {length:.2f} m\nTunnel Length : {length:.2f} m")
        self.summary_label.setStyleSheet(
            "background-color: #E8F5E9; border: 1px solid #C8E6C9; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #2E7D32; font-weight: bold;"
        )
        QMessageBox.information(self, "Verified", "Chainage location successfully verified.")
##### Mayur 18-7-2026
    def on_undo_clicked(self):
        """Handle Undo button click using common Asset History Manager."""
        ## Mayur Wakhare 7-7-2026 pipe undo tunnel 
        if hasattr(self.parent, 'undo_last_water_pipe'):
            success = self.parent.undo_last_water_pipe()
            if success:
                self.undo_btn.setEnabled(False)
                ##################################################################################
        else:
            print("Undo triggered (Asset History Manager integration pending execution)")

    def get_data(self):
        if not self.verified:
            return None
            
        try:
            idx = self.tunnel_combo.currentIndex()
            t_id = "Unknown"
            l_name = "Unknown"
            source_folder = ""
            if idx >= 0 and idx < len(self.available_tunnels):
                t_obj, l_name, t_id = self.available_tunnels[idx]
                source_folder = t_obj.get("source_layer_folder", "")
                
            return {
                "start_km": float(self.start_km_input.text() or 0.0),
                "start_chainage": float(self.start_ch_input.text() or 0.0),
                "end_km": float(self.end_km_input.text() or 0.0),
                "end_chainage": float(self.end_ch_input.text() or 0.0),
                "installation_side": "left" if self.left_side_rb.isChecked() else "right",
                "height_from_ground": float(self.height_input.text() or 2.50),
                "wall_offset": float(self.wall_offset_input.text() or 0.08),
                "pipe_diameter": float(self.diameter_input.text() or 500.0),
                "pipe_color": "fire_red" if self.color_red_rb.isChecked() else "custom",
                "tunnel_id": t_id,
                "layer_name": l_name,
                "source_layer_folder": source_folder
            }
        except ValueError:
            return None

            #######################################################################################################
        self.start_chainage_label.setText(start_chainage_val)
        self.end_km_label.setText(start_km_val)
        self.end_chainage_label.setText(start_chainage_val)

    # ────────────────────────────────────────────
    #  Mode & Position Toggling
    # ────────────────────────────────────────────
    def _on_mode_toggled(self, is_single_checked):
        """Toggle between Single Light and Multiple Lights (Coming Soon)."""
        self.single_light_container.setVisible(is_single_checked)
        self.coming_soon_label.setVisible(not is_single_checked)

    def _on_position_toggled(self, button, checked):
        """Enable only the offset field for the selected position radio button."""
        self.left_offset_input.setEnabled(self.left_radio.isChecked())
        self.right_offset_input.setEnabled(self.right_radio.isChecked())
        self.center_offset_input.setEnabled(self.center_radio.isChecked())

        # Clear non-active fields
        if not self.left_radio.isChecked():
            self.left_offset_input.clear()
        if not self.right_radio.isChecked():
            self.right_offset_input.clear()
        if not self.center_radio.isChecked():
            self.center_offset_input.setText("0")

########### Underpass Light Dialog
class UnderPassLightDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Underpass Light")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.selected_option = "single"
        self.parent = parent
        self.verified = False
        self.multi_verified = False

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QRadioButton { font-size: 13px; padding: 6px; }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #888;
                border-radius: 10px;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #388E3C;
            }
            QLineEdit {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QComboBox {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        ## Mayur Wakhare 3-7-2026 Underpass light Dialog box Design scroll
        # ── Scroll Area wrapper ──
        from PyQt5.QtWidgets import QScrollArea
        from PyQt5.QtCore import Qt as QtCore_Qt

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QtCore_Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(QtCore_Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #F5F5F5; }")
        outer_layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_container.setStyleSheet("background-color: #F5F5F5;")
        scroll_area.setWidget(scroll_container)

        layout = QVBoxLayout(scroll_container)
        ###########################################################
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Underpass Light")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1565C0;")
        layout.addWidget(title)

        # Radio buttons
        self.single_radio = QRadioButton("Single Light")
        self.multiple_radio = QRadioButton("Multiple Lights")
        self.single_radio.setChecked(True)

        self.light_group = QButtonGroup(self)
        self.light_group.addButton(self.single_radio)
        self.light_group.addButton(self.multiple_radio)

        layout.addWidget(self.single_radio)
        layout.addWidget(self.multiple_radio)

        # ── Single Light Controls ──
        self.single_light_container = QWidget()
        single_layout = QVBoxLayout(self.single_light_container)
        single_layout.setContentsMargins(0, 5, 0, 0)
        single_layout.setSpacing(10)

        # KM, Chainage, Interval grid
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("KM:"), 0, 0)
        self.km_input = QLineEdit()
        self.km_input.setPlaceholderText("e.g. 1")
        grid.addWidget(self.km_input, 0, 1)

        grid.addWidget(QLabel("Chainage:"), 0, 2)
        self.chainage_input = QLineEdit()
        self.chainage_input.setPlaceholderText("e.g. 200")
        grid.addWidget(self.chainage_input, 0, 3)

        grid.addWidget(QLabel("Interval:"), 1, 0)
        self.interval_input = QLineEdit()
        self.interval_input.setText("20")
        grid.addWidget(self.interval_input, 1, 1)

        single_layout.addLayout(grid)

        # Verify button
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #1E88E5; color: white;")
        self.verify_btn.clicked.connect(self.verify_chainage)
        single_layout.addWidget(self.verify_btn)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
        single_layout.addWidget(self.status_label)

        # ── Post-verification controls (visible but disabled initially) ──
        self.post_verify_container = QWidget()
        post_layout = QGridLayout(self.post_verify_container)
        post_layout.setSpacing(10)
        post_layout.setContentsMargins(0, 0, 0, 0)

        self.arc_label = QLabel("ARC Reference:")
        post_layout.addWidget(self.arc_label, 0, 0)
        self.arc_combo = QComboBox()
        self.arc_combo.addItems(["Left Side (1)", "Top / Center (2)", "Right Side (3)"])
        self.arc_combo.setEnabled(False)
        post_layout.addWidget(self.arc_combo, 0, 1)

        self.distance_label = QLabel("Enter Distance from Right Side (1):")
        post_layout.addWidget(self.distance_label, 1, 0)
        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText("Enter distance")
        self.distance_input.setValidator(QDoubleValidator(0.0, 99999.0, 3))
        self.distance_input.setEnabled(False)
        post_layout.addWidget(self.distance_input, 1, 1)
        
        self.arc_combo.currentTextChanged.connect(
            lambda text: self.distance_label.setText(f"Enter Distance from {text}:")
        )

        single_layout.addWidget(self.post_verify_container)

        layout.addWidget(self.single_light_container)

        # ── Multiple Lights Controls ──
        self.multiple_light_container = QWidget()
        multi_layout = QVBoxLayout(self.multiple_light_container)
        multi_layout.setContentsMargins(0, 5, 0, 0)
        multi_layout.setSpacing(10)

        multi_grid = QGridLayout()
        
        multi_grid.addWidget(QLabel("Start KM:"), 0, 0)
        self.multi_start_km_input = QLineEdit()
        self.multi_start_km_input.setPlaceholderText("e.g. 101")
        multi_grid.addWidget(self.multi_start_km_input, 0, 1)

        multi_grid.addWidget(QLabel("+"), 0, 2)
        self.multi_start_chainage_input = QLineEdit()
        self.multi_start_chainage_input.setPlaceholderText("e.g. 0")
        multi_grid.addWidget(self.multi_start_chainage_input, 0, 3)

        multi_grid.addWidget(QLabel("End KM:"), 1, 0)
        self.multi_end_km_input = QLineEdit()
        self.multi_end_km_input.setPlaceholderText("e.g. 101")
        multi_grid.addWidget(self.multi_end_km_input, 1, 1)

        multi_grid.addWidget(QLabel("+"), 1, 2)
        self.multi_end_chainage_input = QLineEdit()
        self.multi_end_chainage_input.setPlaceholderText("e.g. 200")
        multi_grid.addWidget(self.multi_end_chainage_input, 1, 3)

        multi_grid.addWidget(QLabel("Interval (m):"), 2, 0)
        self.multi_interval_input = QLineEdit()
        self.multi_interval_input.setText("20")
        multi_grid.addWidget(self.multi_interval_input, 2, 1)

        multi_layout.addLayout(multi_grid)

        self.multi_verify_btn = QPushButton("Verify")
        self.multi_verify_btn.setStyleSheet("background-color: #1E88E5; color: white;")
        self.multi_verify_btn.clicked.connect(self.verify_multi_chainage)
        multi_layout.addWidget(self.multi_verify_btn)

        self.multi_status_label = QLabel("")
        self.multi_status_label.setStyleSheet("color: #888; font-size: 11px;")
        multi_layout.addWidget(self.multi_status_label)

        self.multi_post_verify_container = QWidget()
        multi_post_layout = QGridLayout(self.multi_post_verify_container)
        multi_post_layout.setSpacing(10)
        multi_post_layout.setContentsMargins(0, 0, 0, 0)

        self.multi_arc_label = QLabel("ARC Reference:")
        multi_post_layout.addWidget(self.multi_arc_label, 0, 0)
        import PyQt5.QtWidgets as _qt_widgets
        
        self.multi_arc_checkbox_layout = _qt_widgets.QVBoxLayout()
        self.multi_arc_cb1 = _qt_widgets.QCheckBox("Left Side (1)")
        self.multi_arc_cb2 = _qt_widgets.QCheckBox("Top / Center (2)")
        self.multi_arc_cb3 = _qt_widgets.QCheckBox("Right Side (3)")
        self.multi_arc_cb1.setEnabled(False)
        self.multi_arc_cb2.setEnabled(False)
        self.multi_arc_cb3.setEnabled(False)
        self.multi_arc_checkbox_layout.addWidget(self.multi_arc_cb1)
        self.multi_arc_checkbox_layout.addWidget(self.multi_arc_cb2)
        self.multi_arc_checkbox_layout.addWidget(self.multi_arc_cb3)
        multi_post_layout.addLayout(self.multi_arc_checkbox_layout, 0, 1)

        self.multi_distance_container = _qt_widgets.QWidget()
        self.multi_distance_layout = _qt_widgets.QVBoxLayout(self.multi_distance_container)
        self.multi_distance_layout.setContentsMargins(0, 0, 0, 0)
        multi_post_layout.addWidget(self.multi_distance_container, 1, 0, 1, 2)

        self.multi_distance_inputs = {}

        self.multi_arc_cb1.stateChanged.connect(lambda state: self.update_multi_distance_inputs("Right Side (1)", state))
        self.multi_arc_cb2.stateChanged.connect(lambda state: self.update_multi_distance_inputs("Top / Center (2)", state))
        self.multi_arc_cb3.stateChanged.connect(lambda state: self.update_multi_distance_inputs("Left Side (3)", state))

        multi_layout.addWidget(self.multi_post_verify_container)
        ### Mayur Wakhare 3-7-2026 Underpass dialog box automatic value put for start km and end km
        # ── Placement Summary (read-only preview) ──
        self.multi_summary_label = QLabel("")
        self.multi_summary_label.setWordWrap(True)
        self.multi_summary_label.setStyleSheet(
            "background-color: #E8F5E9; border: 1px solid #A5D6A7; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #333; font-weight: normal;"
        )
        self.multi_summary_label.setVisible(False)
        multi_layout.addWidget(self.multi_summary_label)

        # Connect input changes to auto-update summary
        self.multi_start_km_input.textChanged.connect(self._update_multi_summary)
        self.multi_start_chainage_input.textChanged.connect(self._update_multi_summary)
        self.multi_end_km_input.textChanged.connect(self._update_multi_summary)
        self.multi_end_chainage_input.textChanged.connect(self._update_multi_summary)
        self.multi_interval_input.textChanged.connect(self._update_multi_summary)
        self.multi_arc_cb1.stateChanged.connect(lambda _: self._update_multi_summary())
        self.multi_arc_cb2.stateChanged.connect(lambda _: self._update_multi_summary())
        self.multi_arc_cb3.stateChanged.connect(lambda _: self._update_multi_summary())
        ##########################################################

        self.multiple_light_container.setVisible(False)
        layout.addWidget(self.multiple_light_container)

        # ── OK / Cancel / Undo ──
        buttons_layout = QHBoxLayout()

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        ok_btn.clicked.connect(self.on_ok_clicked)
        buttons_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.undo_btn.clicked.connect(self.on_undo_clicked)
        buttons_layout.addWidget(self.undo_btn)

        self.undo_once_btn = QPushButton("Undo Once")
        self.undo_once_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.undo_once_btn.clicked.connect(self.on_undo_once_clicked)
        buttons_layout.addWidget(self.undo_once_btn)

        self.undo_all_btn = QPushButton("Undo All")
        self.undo_all_btn.setStyleSheet("background-color: #F44336; color: white;")
        self.undo_all_btn.clicked.connect(self.on_undo_all_clicked)
        buttons_layout.addWidget(self.undo_all_btn)

        layout.addLayout(buttons_layout)
        
        # Connect radio toggle
        self.single_radio.toggled.connect(self.on_mode_toggled)
        
        self.update_undo_state()
        ## Mayur Wakhare 3-7-2026 Underpass light automatic value put up from design file
        # ── Auto-populate chainage from underpass ──
        underpass_found = False
        t_start_km, t_start_ch, t_end_km, t_end_ch = "", "", "", ""
        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        import os
        if layer_folder and os.path.exists(layer_folder):
            try:
                from json_manager import DesignConstructionManager
                m_data = DesignConstructionManager.load_master(layer_folder)
                # For underpasses, data might be a list
                up_list = m_data.get("under_passes", [])
                ref_ups = m_data.get("reference_assets", {}).get("under_pass", [])
                if isinstance(ref_ups, list): up_list.extend(ref_ups)
                elif isinstance(ref_ups, dict): up_list.append(ref_ups)
                t_conf = up_list[0] if up_list else {}
                if t_conf and "start_km" in t_conf:
                    t_start_km = str(t_conf.get("start_km", ""))
                    t_start_ch = str(t_conf.get("start_chainage", ""))
                    t_end_km = str(t_conf.get("end_km", ""))
                    t_end_ch = str(t_conf.get("end_chainage", ""))
                    underpass_found = True
            except Exception:
                pass
                
        if underpass_found:
            # Set integer part if it ends with .0 for cleaner display
            def clean_str(val):
                return val[:-2] if val.endswith(".0") else val
                
            self.km_input.setText(clean_str(t_start_km))
            self.chainage_input.setText(clean_str(t_start_ch))
            self.multi_start_km_input.setText(clean_str(t_start_km))
            self.multi_start_chainage_input.setText(clean_str(t_start_ch))
            self.multi_end_km_input.setText(clean_str(t_end_km))
            self.multi_end_chainage_input.setText(clean_str(t_end_ch))
        else:
            self.status_label.setText("No active underpass found.")
            self.multi_status_label.setText("No active underpass found.")
#########################################################################
        self.on_mode_toggled(self.single_radio.isChecked())

    def update_undo_state(self):
        # Single Light Undo
        has_lights = False
        if hasattr(self.parent, 'underpass_light_groups') and self.parent.underpass_light_groups:
            has_lights = True
            
        self.undo_btn.setEnabled(has_lights)
        if not has_lights:
            self.undo_btn.setToolTip("No Underpass Lights to undo.")
        else:
            self.undo_btn.setToolTip("Undo the most recently placed Underpass Light.")
            
        # Multiple Lights Undo
        has_multi = False
        if hasattr(self.parent, 'multiple_underpass_light_batches') and self.parent.multiple_underpass_light_batches:
            has_multi = True
            
        self.undo_once_btn.setEnabled(has_multi)
        self.undo_all_btn.setEnabled(has_multi)
        if not has_multi:
            self.undo_once_btn.setToolTip("No Multiple Underpass Lights to undo.")
            self.undo_all_btn.setToolTip("No Multiple Underpass Lights to undo.")
        else:
            self.undo_once_btn.setToolTip("Undo the most recently placed light from the current Multiple Lights placement.")
            self.undo_all_btn.setToolTip("Undo ALL lights from the most recent Multiple Lights placement.")

    def on_undo_clicked(self):
        if hasattr(self.parent, 'undo_last_underpass_light'):
            success = self.parent.undo_last_underpass_light()
            if success:
                self.update_undo_state()
            else:
                QMessageBox.information(self, "Undo", "No Underpass Lights to undo.")

    def on_undo_once_clicked(self):
        if hasattr(self.parent, 'undo_last_multiple_underpass_light'):
            success = self.parent.undo_last_multiple_underpass_light()
            if success:
                self.update_undo_state()
            else:
                QMessageBox.information(self, "Undo", "No Multiple Underpass Lights to undo.")

    def on_undo_all_clicked(self):
        if hasattr(self.parent, 'undo_all_multiple_underpass_lights'):
            success = self.parent.undo_all_multiple_underpass_lights()
            if success:
                self.update_undo_state()
            else:
                QMessageBox.information(self, "Undo", "No Multiple Underpass Lights to undo.")

    def update_multi_distance_inputs(self, name, state):
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
        from PyQt5.QtGui import QDoubleValidator

        if state == Qt.Checked or state == 2:  # 2 is Qt.Checked
            if name not in self.multi_distance_inputs:
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                
                label = QLabel(f"Enter Distance from {name}:")
                input_field = QLineEdit()
                input_field.setPlaceholderText("Enter distance")
                input_field.setValidator(QDoubleValidator(0.0, 99999.0, 3))
                
                row_layout.addWidget(label)
                row_layout.addWidget(input_field)
                
                self.multi_distance_layout.addWidget(row_widget)
                self.multi_distance_inputs[name] = {"widget": row_widget, "input": input_field}
                ## Mayur Wakhare 3-7-2026 Underpass light dailog box
                input_field.textChanged.connect(self._update_multi_summary)
                #################################################
        else:
            if name in self.multi_distance_inputs:
                data = self.multi_distance_inputs.pop(name)
                data["widget"].setParent(None)
                data["widget"].deleteLater()

    def on_mode_toggled(self, checked):
        self.single_light_container.setVisible(checked)
        self.multiple_light_container.setVisible(not checked)
        self.undo_btn.setVisible(checked)
        self.undo_once_btn.setVisible(not checked)
        self.undo_all_btn.setVisible(not checked)
        self.update_undo_state()

    def verify_chainage(self):
        try:
            km = float(self.km_input.text() or 0.0)
            ch = float(self.chainage_input.text() or 0.0)
            interval = float(self.interval_input.text() or 0.0)
        except:
            QMessageBox.warning(self, "Invalid Input", "Please enter numeric values for KM, Chainage, and Interval.")
            return

        if interval <= 0:
            QMessageBox.warning(self, "Invalid Interval", "Interval must be greater than 0.")
            return

        abs_chainage = km * 1000 + ch

        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        if not layer_folder or not os.path.exists(layer_folder):
            QMessageBox.warning(self, "Error", "No active design layer folder found to verify.")
            return

        try:
            j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'road_surface_baseline')
            if not j:
                j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'surface_baseline')

            if not j:
                QMessageBox.warning(self, "No Baseline Data", "No surface or road surface baseline found in design layer.")
                return

            global_start_offset = 0.0
            if hasattr(self.parent, '_get_global_start_offset'):
                global_start_offset = self.parent._get_global_start_offset(layer_folder)
            else:
                polylines = j.get("polylines", [])
                if polylines:
                    start_str = polylines[0].get("start_chainage_str", "")
                    if start_str:
                        start_str = start_str.replace(" ", "")
                        if "+" in start_str:
                            parts = start_str.split("+")
                            global_start_offset = float(parts[0]) * 1000 + float(parts[1])
                        else:
                            global_start_offset = float(start_str)

            chs = []
            for poly in j.get("polylines", []):
                for pt in poly.get("points", []):
                    chs.append(pt['chainage_m'] + global_start_offset)
            if not chs:
                QMessageBox.warning(self, "No Points", "Baseline has no chainage points.")
                return

            min_ch = min(chs)
            max_ch = max(chs)

            if abs_chainage < min_ch or abs_chainage > max_ch:
                self.verified = False
                self.arc_combo.setEnabled(False)
                self.distance_input.setEnabled(False)
                self.status_label.setText("Verification failed — chainage out of range.")
                self.status_label.setStyleSheet("color: red; font-size: 11px;")
                QMessageBox.warning(self, "Out of Range",
                    f"Chainage is out of design layer range.\n"
                    f"Range: KM {min_ch//1000:.0f} + {min_ch%1000:.2f}m  to  KM {max_ch//1000:.0f} + {max_ch%1000:.2f}m")
            else:
                self.verified = True
                self.arc_combo.setEnabled(True)
                self.distance_input.setEnabled(True)
                self.status_label.setText("Verification successful!")
                self.status_label.setStyleSheet("color: green; font-size: 11px;")
        except Exception as e:
            self.verified = False
            self.arc_combo.setEnabled(False)
            self.distance_input.setEnabled(False)
            self.status_label.setText(f"Verification error.")
            self.status_label.setStyleSheet("color: red; font-size: 11px;")
            QMessageBox.warning(self, "Error", f"Failed to verify chainage: {e}")

    def verify_multi_chainage(self):
        try:
            start_km = float(self.multi_start_km_input.text() or 0.0)
            start_ch = float(self.multi_start_chainage_input.text() or 0.0)
            end_km = float(self.multi_end_km_input.text() or 0.0)
            end_ch = float(self.multi_end_chainage_input.text() or 0.0)
            interval = float(self.multi_interval_input.text() or 20.0)
        except:
            QMessageBox.warning(self, "Invalid Input", "Please enter numeric values for KM, Chainage, and Interval.")
            return

        if interval <= 0:
            QMessageBox.warning(self, "Invalid Interval", "Interval must be greater than 0.")
            return

        abs_start = start_km * 1000 + start_ch
        abs_end = end_km * 1000 + end_ch

        if abs_start >= abs_end:
            QMessageBox.warning(self, "Invalid Range", "Start chainage must be strictly less than End chainage.")
            return

        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        if not layer_folder or not os.path.exists(layer_folder):
            QMessageBox.warning(self, "Error", "No active design layer folder found to verify.")
            return

        try:
            j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'road_surface_baseline')
            if not j:
                j = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'surface_baseline')

            if not j:
                QMessageBox.warning(self, "No Baseline Data", "No surface or road surface baseline found in design layer.")
                return

            global_start_offset = 0.0
            if hasattr(self.parent, '_get_global_start_offset'):
                global_start_offset = self.parent._get_global_start_offset(layer_folder)
            else:
                polylines = j.get("polylines", [])
                if polylines:
                    start_str = polylines[0].get("start_chainage_str", "")
                    if start_str:
                        start_str = start_str.replace(" ", "")
                        if "+" in start_str:
                            parts = start_str.split("+")
                            global_start_offset = float(parts[0]) * 1000 + float(parts[1])
                        else:
                            global_start_offset = float(start_str)

            chs = []
            for poly in j.get("polylines", []):
                for pt in poly.get("points", []):
                    chs.append(pt['chainage_m'] + global_start_offset)
            if not chs:
                QMessageBox.warning(self, "No Points", "Baseline has no chainage points.")
                return

            min_ch = min(chs)
            max_ch = max(chs)

            if abs_start < min_ch or abs_end > max_ch:
                self.multi_verified = False
                self.multi_arc_cb1.setEnabled(False)
                self.multi_arc_cb2.setEnabled(False)
                self.multi_arc_cb3.setEnabled(False)
                self.multi_status_label.setText("Verification failed — range out of bounds.")
                self.multi_status_label.setStyleSheet("color: red; font-size: 11px;")
                QMessageBox.warning(self, "Out of Range",
                    f"Selected range is out of design layer bounds.\n"
                    f"Layer Range: KM {min_ch//1000:.0f} + {min_ch%1000:.2f}m  to  KM {max_ch//1000:.0f} + {max_ch%1000:.2f}m")
            else:
                self.multi_verified = True
                self.multi_arc_cb1.setEnabled(True)
                self.multi_arc_cb2.setEnabled(True)
                self.multi_arc_cb3.setEnabled(True)
                self.multi_status_label.setText("Verification successful!")
                self.multi_status_label.setStyleSheet("color: green; font-size: 11px;")
                ### Mayur Wakhare 3-7-2026 Underpass light dailog box
                self._update_multi_summary()
                #####################################################
        except Exception as e:
            self.multi_verified = False
            self.multi_arc_cb1.setEnabled(False)
            self.multi_arc_cb2.setEnabled(False)
            self.multi_arc_cb3.setEnabled(False)
            self.multi_status_label.setText(f"Verification error.")
            self.multi_status_label.setStyleSheet("color: red; font-size: 11px;")
            QMessageBox.warning(self, "Error", f"Failed to verify chainage: {e}")
            ## Mayur Wakhare 3-7-2026 underpass light dailog box how many lights are required for these underpass 
            self._update_multi_summary()

    def _update_multi_summary(self):
        """Calculate and display the Multiple Lights placement preview.
        Uses the exact same boundary-skipping interval logic as _place_multiple_underpass_lights:
            current_abs = start_abs + interval
            while current_abs < end_abs - 0.001: place; current_abs += interval
        """
        zero_html = (
            "<b>Placement Summary</b><br><br>"
            "Total Underpass Lights : 0"
        )

        # If not verified, show zero and hide details
        if not self.multi_verified:
            self.multi_summary_label.setText(zero_html)
            self.multi_summary_label.setVisible(True)
            return

        try:
            start_km = float(self.multi_start_km_input.text() or 0.0)
            start_ch = float(self.multi_start_chainage_input.text() or 0.0)
            end_km = float(self.multi_end_km_input.text() or 0.0)
            end_ch = float(self.multi_end_chainage_input.text() or 0.0)
            interval = float(self.multi_interval_input.text() or 20.0)
        except (ValueError, TypeError):
            self.multi_summary_label.setText(zero_html)
            self.multi_summary_label.setVisible(True)
            return

        if interval <= 0:
            self.multi_summary_label.setText(zero_html)
            self.multi_summary_label.setVisible(True)
            return

        start_abs = start_km * 1000 + start_ch
        end_abs = end_km * 1000 + end_ch

        # Collect selected ARC references (same structure as multi_configs in get_data)
        selected_arcs = []
        for name, d in self.multi_distance_inputs.items():
            arc_ref = int(name.split("(")[-1].replace(")", ""))
            selected_arcs.append({"name": name, "arc_reference": arc_ref})

        if not selected_arcs or start_abs >= end_abs:
            self.multi_summary_label.setText(zero_html)
            self.multi_summary_label.setVisible(True)
            return

        # ── Exact same loop as _place_multiple_underpass_lights ──
        # current_abs = start_abs + interval
        # while current_abs < end_abs - 0.001: count position; current_abs += interval
        current_abs = start_abs + interval
        chainage_positions = []
        while current_abs < end_abs - 0.001:
            chainage_positions.append(current_abs)
            current_abs += interval

        num_positions = len(chainage_positions)
        num_arcs = len(selected_arcs)
        total_lights = num_positions * num_arcs

        if total_lights == 0:
            self.multi_summary_label.setText(zero_html)
            self.multi_summary_label.setVisible(True)
            return

        # Sort: Right Side (1), Top / Center (2), Left Side (3)
        arc_order = {1: 0, 2: 1, 3: 2}
        selected_arcs_sorted = sorted(selected_arcs, key=lambda a: arc_order.get(a["arc_reference"], 99))

        # Estimated Covered Length = last placed position - first placed position
        covered_length = chainage_positions[-1] - chainage_positions[0]

        # Build HTML
        lines = ["<b>Placement Summary</b><br>"]
        lines.append(f"<br>Total Underpass Lights : <b>{total_lights}</b><br>")
        lines.append("<br><b>Estimated Placement</b><br><br>")
        for arc in selected_arcs_sorted:
            lines.append(f"{arc['name']} : {num_positions}<br>")
        lines.append(f"<br>Estimated Covered Length : <b>{covered_length:.0f} m</b>")

        self.multi_summary_label.setText("".join(lines))
        self.multi_summary_label.setVisible(True)

        #########################################################

    def on_ok_clicked(self):
        if self.single_radio.isChecked():
            self.selected_option = "single"
            # Validate single light inputs before accepting
            if not self.verified:
                QMessageBox.warning(self, "Not Verified", "Please verify the chainage first.")
                return
            distance_text = self.distance_input.text().strip()
            if not distance_text:
                QMessageBox.warning(self, "Missing Distance", "Please enter a Distance / Length value.")
                return
            try:
                dist_val = float(distance_text)
                if dist_val < 0:
                    QMessageBox.warning(self, "Invalid Distance", "Distance must be a positive value.")
                    return
            except ValueError:
                QMessageBox.warning(self, "Invalid Distance", "Please enter a valid numeric distance.")
                return
            self.accept()
        else:
            self.selected_option = "multiple"
            if not self.multi_verified:
                QMessageBox.warning(self, "Not Verified", "Please verify the chainage range first.")
                return
            if not self.multi_distance_inputs:
                QMessageBox.warning(self, "No Selection", "Please select at least one ARC Reference.")
                return
            for name, d in self.multi_distance_inputs.items():
                distance_text = d["input"].text().strip()
                if not distance_text:
                    QMessageBox.warning(self, "Missing Distance", f"Please enter a distance for {name}.")
                    return
                try:
                    dist_val = float(distance_text)
                    if dist_val < 0:
                        QMessageBox.warning(self, "Invalid Distance", f"Distance for {name} must be a positive value.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Invalid Distance", f"Please enter a valid numeric distance for {name}.")
                    return
            self.accept()

    def get_data(self):
        try:
            idx = self.tunnel_combo.currentIndex()
            t_id = "Unknown"
            l_name = "Unknown"
            t_obj = {}
            if idx >= 0 and idx < len(self.available_tunnels):
                t_obj, l_name, t_id = self.available_tunnels[idx]
        except Exception:
            t_id = "Unknown"
            l_name = "Unknown"
            t_obj = {}

        data = {
            "light_mode": self.selected_option,
            "tunnel_id": t_id,
            "layer_name": l_name,
            "source_layer_folder": t_obj.get("source_layer_folder", "")
        }
        if self.selected_option == "single":
            data["km"] = float(self.km_input.text() or 0.0)
            data["chainage"] = float(self.chainage_input.text() or 0.0)
            data["interval"] = float(self.interval_input.text() or 20)
            data["verified"] = self.verified
            if self.verified:
                text = self.arc_combo.currentText()
                data["arc_reference"] = int(text.split("(")[-1].replace(")", ""))
                data["distance"] = float(self.distance_input.text() or 0.0)
        else:
            data["start_km"] = float(self.multi_start_km_input.text() or 0.0)
            data["start_chainage"] = float(self.multi_start_chainage_input.text() or 0.0)
            data["end_km"] = float(self.multi_end_km_input.text() or 0.0)
            data["end_chainage"] = float(self.multi_end_chainage_input.text() or 0.0)
            data["interval"] = float(self.multi_interval_input.text() or 20.0)
            data["verified"] = self.multi_verified
            if self.multi_verified:
                configs = []
                for name, d in self.multi_distance_inputs.items():
                    arc_ref = int(name.split("(")[-1].replace(")", ""))
                    dist = float(d["input"].text() or 0.0)
                    configs.append({"arc_reference": arc_ref, "distance": dist})
                data["multi_configs"] = configs
        return data
#####################################################################


### Mayur Wakhare 14-7-2026 underpass lights 
class UnderpassLightDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Underpass Light")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setMinimumHeight(600)
        self.parent = parent

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QRadioButton { font-size: 13px; padding: 6px; }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #888;
                border-radius: 10px;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #388E3C;
            }
            QLineEdit {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QComboBox {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QGroupBox {
                border: 1px solid #CCC;
                border-radius: 6px;
                margin-top: 15px;
                font-weight: bold;
                color: #1565C0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

        from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QRadioButton, QButtonGroup, QLineEdit, QGroupBox, QLabel, QComboBox, QPushButton, QSpacerItem, QSizePolicy
        from PyQt5.QtGui import QDoubleValidator
        from PyQt5.QtCore import Qt as QtCore_Qt

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QtCore_Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(QtCore_Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #F5F5F5; }")
        outer_layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_container.setStyleSheet("background-color: #F5F5F5;")
        scroll_area.setWidget(scroll_container)

        layout = QVBoxLayout(scroll_container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Underpass Light")
        title.setAlignment(QtCore_Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1565C0; margin-bottom: 10px;")
        layout.addWidget(title)

        # ── Underpass Information ──
        info_group = QGroupBox("Underpass Information")
        info_layout = QVBoxLayout(info_group)
        
        self.id_label = QLabel("Underpass ID")
        self.id_label.setAlignment(QtCore_Qt.AlignCenter)
        info_layout.addWidget(self.id_label)

        combo_layout = QHBoxLayout()
        self.id_combo = QComboBox()
        combo_layout.addWidget(self.id_combo, 1)

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.verify_btn.clicked.connect(self.on_verify_clicked)
        combo_layout.addWidget(self.verify_btn)
        
        info_layout.addLayout(combo_layout)

        # Details
        details_layout = QHBoxLayout()
        self.km_label = QLabel("Start KM : --")
        self.chainage_label = QLabel("Start Chainage : --")
        self.length_label = QLabel("Length : --")
        
        self.km_label.setAlignment(QtCore_Qt.AlignCenter)
        self.chainage_label.setAlignment(QtCore_Qt.AlignCenter)
        self.length_label.setAlignment(QtCore_Qt.AlignCenter)
        
        details_layout.addWidget(self.km_label)
        details_layout.addWidget(self.chainage_label)
        details_layout.addWidget(self.length_label)
        info_layout.addLayout(details_layout)
        
        layout.addWidget(info_group)

        # ── Data Loading Logic ──
        self.underpass_data = {}
        found_underpasses = []
        base_dir = getattr(self.parent, 'WORKSHEETS_BASE_DIR', '')
        ws_name = getattr(self.parent, 'current_worksheet_name', '')
        
        import os
        import json
        if base_dir and ws_name:
            designs_dir = os.path.join(base_dir, ws_name, "designs")
            if os.path.exists(designs_dir):
                for layer_folder in os.listdir(designs_dir):
                    layer_path = os.path.join(designs_dir, layer_folder)
                    if os.path.isdir(layer_path) and not layer_folder.endswith('_merged'):
                        config_file = os.path.join(layer_path, "design_construction_config.json")
                        if os.path.exists(config_file):
                            try:
                                with open(config_file, "r", encoding="utf-8") as f:
                                    data = json.load(f)
                                
                                ups = data.get("under_passes")
                                if isinstance(ups, dict):
                                    if "id" in ups or "length" in ups:
                                        ups = [ups]
                                    else:
                                        ups = list(ups.values())
                                elif not isinstance(ups, list):
                                    ups = []
                                
                                if not ups:
                                    ref_ups = data.get("reference_assets", {}).get("under_pass")
                                    if isinstance(ref_ups, dict):
                                        if "id" in ref_ups or "length" in ref_ups:
                                            ups = [ref_ups]
                                        else:
                                            ups = list(ref_ups.values())
                                    elif isinstance(ref_ups, list):
                                        ups = ref_ups
                                
                                if ups:
                                    found_underpasses.extend(ups)
                            except Exception:
                                pass

        if found_underpasses:
            for up in found_underpasses:
                if isinstance(up, dict):
                    up_id = up.get("id", up.get("underpass_id", "Unknown"))
                    self.underpass_data[str(up_id)] = up
                    self.id_combo.addItem(str(up_id))
        else:
            self.id_combo.addItem("No Underpass Available")
            self.id_combo.setEnabled(False)
            
        self.id_combo.currentTextChanged.connect(self.on_underpass_selected)

        # ── Light Mode ──
        self.mode_group = QGroupBox("Light Mode")
        mode_layout = QVBoxLayout(self.mode_group)

        self.single_radio = QRadioButton("Single Light")
        self.single_radio.setChecked(True)

        self.mode_group_btn = QButtonGroup(self)
        self.mode_group_btn.addButton(self.single_radio)

        mode_layout.addWidget(self.single_radio)
        layout.addWidget(self.mode_group)


        # ── Placement ──
        self.placement_group = QGroupBox("Placement")
        place_layout = QVBoxLayout(self.placement_group)
        
        top_slab_label = QLabel("Top Slab")
        top_slab_label.setStyleSheet("color: #1565C0; font-size: 14px;")
        place_layout.addWidget(top_slab_label)

        grid = QGridLayout()
        grid.setSpacing(10)

        # Center
        self.center_radio = QRadioButton("Center")
        self.center_offset_input = QLineEdit()
        self.center_offset_input.setText("0")
        self.center_offset_input.setEnabled(False)
        grid.addWidget(self.center_radio, 0, 0)
        grid.addWidget(QLabel("Offset :"), 0, 1)
        grid.addWidget(self.center_offset_input, 0, 2)

        place_layout.addLayout(grid)
        layout.addWidget(self.placement_group)

        self.placement_btn_group = QButtonGroup(self)
        self.placement_btn_group.addButton(self.center_radio)

        # Connect radio buttons
        self.center_radio.toggled.connect(self.on_placement_toggled)
        # ── Buttons ──
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        
        if not found_underpasses:
            self.ok_btn.setEnabled(False)
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)

        # Initialize
        if hasattr(self, 'mode_group'):
            self.mode_group.setEnabled(False)
        self.placement_group.setEnabled(False)
        self.ok_btn.setEnabled(False)

        if found_underpasses:
            self.on_underpass_selected(self.id_combo.currentText())
            self.center_radio.setChecked(True)

    def get_data(self):
        placement = "center"
        
        offset = 0.0
        try:
            offset = float(self.center_offset_input.text() or 0.0)
        except ValueError:
            offset = 0.0
            
        return {
            "up_id": self.id_combo.currentText(),
            "verified": self.verify_btn.text() == "Verified ✓",
            "light_mode": "single",
            "placement": placement,
            "offset": offset
        }

    def on_placement_toggled(self):
        self.center_offset_input.setEnabled(self.center_radio.isChecked())

    def on_verify_clicked(self):
        up_id = self.id_combo.currentText()
        if not up_id or up_id == "No Underpass Available":
            return
            
        self.verify_btn.setText("Verified ✓")
        self.verify_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        if hasattr(self, 'mode_group'):
            self.mode_group.setEnabled(True)
        if hasattr(self, 'placement_group'):
            self.placement_group.setEnabled(True)
        if hasattr(self, 'ok_btn'):
            self.ok_btn.setEnabled(True)

    def on_underpass_selected(self, up_id):
        if hasattr(self, 'verify_btn'):
            self.verify_btn.setText("Verify")
            self.verify_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
            if hasattr(self, 'mode_group'):
                self.mode_group.setEnabled(False)
            if hasattr(self, 'placement_group'):
                self.placement_group.setEnabled(False)
            if hasattr(self, 'ok_btn'):
                self.ok_btn.setEnabled(False)

        if not up_id or up_id == "No Underpass Available":
            self.km_label.setText("Start KM : --")
            self.chainage_label.setText("Start Chainage : --")
            self.length_label.setText("Length : --")
            return
            
        up = self.underpass_data.get(up_id, {})
        km = up.get("km", "--")
        chainage = up.get("chainage", "--")
        length = up.get("length", "--")
        
        if length != "--":
            length = f"{length} m"
            
        self.km_label.setText(f"Start KM : {km}")
        self.chainage_label.setText(f"Start Chainage : {chainage}")
        self.length_label.setText(f"Length : {length}")

#### Mayur Wakhare 15-07-2026 Tunnel CCTV
class UnderpassCCTVDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Underpass CCTV")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setMinimumHeight(600)
        self.parent = parent

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
                font-family: Segoe UI;
            }
            QLabel { font-size: 13px; color: #333; font-weight: bold; }
            QRadioButton { font-size: 13px; padding: 6px; }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #888;
                border-radius: 10px;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #388E3C;
            }
            QLineEdit {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QComboBox {
                padding: 6px;
                border: 2px solid #BBB;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QGroupBox {
                border: 1px solid #CCC;
                border-radius: 6px;
                margin-top: 15px;
                font-weight: bold;
                color: #1565C0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

        from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QRadioButton, QButtonGroup, QLineEdit, QGroupBox, QLabel, QComboBox, QPushButton, QSpacerItem, QSizePolicy
        from PyQt5.QtGui import QDoubleValidator
        from PyQt5.QtCore import Qt as QtCore_Qt

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QtCore_Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(QtCore_Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #F5F5F5; }")
        outer_layout.addWidget(scroll_area)

        scroll_container = QWidget()
        scroll_container.setStyleSheet("background-color: #F5F5F5;")
        scroll_area.setWidget(scroll_container)

        layout = QVBoxLayout(scroll_container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Underpass CCTV")
        title.setAlignment(QtCore_Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1565C0; margin-bottom: 10px;")
        layout.addWidget(title)

        # ── Underpass Information ──
        info_group = QGroupBox("Underpass Information")
        info_layout = QVBoxLayout(info_group)
        
        self.id_label = QLabel("Underpass ID")
        self.id_label.setAlignment(QtCore_Qt.AlignCenter)
        info_layout.addWidget(self.id_label)

        combo_layout = QHBoxLayout()
        self.id_combo = QComboBox()
        combo_layout.addWidget(self.id_combo, 1)

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.verify_btn.clicked.connect(self.on_verify_clicked)
        combo_layout.addWidget(self.verify_btn)
        
        info_layout.addLayout(combo_layout)

        # Details
        details_layout = QHBoxLayout()
        self.km_label = QLabel("Start KM : --")
        self.chainage_label = QLabel("Start Chainage : --")
        self.length_label = QLabel("Length : --")
        
        self.km_label.setAlignment(QtCore_Qt.AlignCenter)
        self.chainage_label.setAlignment(QtCore_Qt.AlignCenter)
        self.length_label.setAlignment(QtCore_Qt.AlignCenter)
        
        details_layout.addWidget(self.km_label)
        details_layout.addWidget(self.chainage_label)
        details_layout.addWidget(self.length_label)
        info_layout.addLayout(details_layout)
        
        layout.addWidget(info_group)

        # ── Data Loading Logic ──
        self.underpass_data = {}
        self.load_underpass_ids()

        self.id_combo.currentTextChanged.connect(self.on_underpass_selected)

        # ── Placement ──
        self.placement_group = QGroupBox("Placement")
        place_layout = QVBoxLayout(self.placement_group)

        # Left Side
        self.left_radio = QRadioButton("Left Side")
        place_layout.addWidget(self.left_radio)

        # Right Side
        self.right_radio = QRadioButton("Right Side")
        place_layout.addWidget(self.right_radio)

        # Both
        self.both_radio = QRadioButton("Both")
        place_layout.addWidget(self.both_radio)

        layout.addWidget(self.placement_group)

        self.placement_btn_group = QButtonGroup(self)
        self.placement_btn_group.addButton(self.left_radio)
        self.placement_btn_group.addButton(self.right_radio)
        self.placement_btn_group.addButton(self.both_radio)

        # ── Buttons ──
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        
        if not self.underpass_data:
            self.ok_btn.setEnabled(False)
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)

        # Initialize
        self.placement_group.setEnabled(False)
        self.ok_btn.setEnabled(False)

        if self.underpass_data:
            self.on_underpass_selected(self.id_combo.currentText())
            self.left_radio.setChecked(True)

    def load_underpass_ids(self):
        found_underpasses = []
        base_dir = getattr(self.parent, 'WORKSHEETS_BASE_DIR', '')
        ws_name = getattr(self.parent, 'current_worksheet_name', '')
        
        import os
        import json
        if base_dir and ws_name:
            designs_dir = os.path.join(base_dir, ws_name, "designs")
            if os.path.exists(designs_dir):
                for layer_folder in os.listdir(designs_dir):
                    layer_path = os.path.join(designs_dir, layer_folder)
                    if os.path.isdir(layer_path) and not layer_folder.endswith('_merged'):
                        config_file = os.path.join(layer_path, "design_construction_config.json")
                        if os.path.exists(config_file):
                            try:
                                with open(config_file, "r", encoding="utf-8") as f:
                                    data = json.load(f)
                                
                                ups = data.get("under_passes")
                                if isinstance(ups, dict):
                                    if "id" in ups or "length" in ups:
                                        ups = [ups]
                                    else:
                                        ups = list(ups.values())
                                elif not isinstance(ups, list):
                                    ups = []
                                
                                if not ups:
                                    ref_ups = data.get("reference_assets", {}).get("under_pass")
                                    if isinstance(ref_ups, dict):
                                        if "id" in ref_ups or "length" in ref_ups:
                                            ups = [ref_ups]
                                        else:
                                            ups = list(ref_ups.values())
                                    elif isinstance(ref_ups, list):
                                        ups = ref_ups
                                
                                if ups:
                                    found_underpasses.extend(ups)
                            except Exception:
                                pass

        if found_underpasses:
            for up in found_underpasses:
                if isinstance(up, dict):
                    up_id = up.get("id", up.get("underpass_id", "Unknown"))
                    self.underpass_data[str(up_id)] = up
                    self.id_combo.addItem(str(up_id))
        else:
            self.id_combo.addItem("No Underpass Available")
            self.id_combo.setEnabled(False)

    def get_data(self):
        if self.left_radio.isChecked():
            placement = "left"
        elif self.right_radio.isChecked():
            placement = "right"
        else:
            placement = "both"
            
        return {
            "up_id": self.id_combo.currentText(),
            "verified": self.verify_btn.text() == "Verified ✓",
            "placement": placement
        }

    def on_verify_clicked(self):
        up_id = self.id_combo.currentText()
        if not up_id or up_id == "No Underpass Available":
            return
            
        self.verify_btn.setText("Verified ✓")
        self.verify_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        self.placement_group.setEnabled(True)
        self.ok_btn.setEnabled(True)

    def on_underpass_selected(self, up_id):
        self.verify_btn.setText("Verify")
        self.verify_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.placement_group.setEnabled(False)
        self.ok_btn.setEnabled(False)

        if not up_id or up_id == "No Underpass Available":
            self.km_label.setText("Start KM : --")
            self.chainage_label.setText("Start Chainage : --")
            self.length_label.setText("Length : --")
            return
            
        up = self.underpass_data.get(up_id, {})
        km = up.get("km", "--")
        chainage = up.get("chainage", "--")
        length = up.get("length", "--")
        
        if length != "--":
            length = f"{length} m"
            
        self.km_label.setText(f"Start KM : {km}")
        self.chainage_label.setText(f"Start Chainage : {chainage}")
        self.length_label.setText(f"Length : {length}")

### Mayur 21-7-2026 Tunnel wall
class TunnelWallDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Tunnel Wall Settings")
        self.setMinimumWidth(400)
        self.verified = False

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-size: 13px;
                color: #333;
            }
            QLineEdit, QComboBox, QDoubleSpinBox {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QComboBox, QLineEdit, QPushButton, QWidget, QGridLayout, QCheckBox, QDoubleSpinBox
        from PyQt5.QtCore import Qt
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Tunnel Wall")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #673AB7;")
        layout.addWidget(title)

        # ── Tunnel Selection ──
        tunnel_sel_group = QGroupBox("Tunnel Selection")
        tunnel_sel_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        tunnel_sel_layout = QHBoxLayout(tunnel_sel_group)
        tunnel_sel_layout.addWidget(QLabel("Tunnel ID:"))
        self.tunnel_combo = QComboBox()
        self.tunnel_combo.setStyleSheet("padding: 4px; border: 1px solid #BBB; border-radius: 4px;")
        tunnel_sel_layout.addWidget(self.tunnel_combo)
        
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 6px; font-weight: bold; border-radius: 4px;")
        self.verify_btn.clicked.connect(self.verify_chainage)
        tunnel_sel_layout.addWidget(self.verify_btn)
        
        layout.addWidget(tunnel_sel_group)

        # Main controls container (enabled after verify)
        self.controls_widget = QWidget()
        controls_layout = QVBoxLayout(self.controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_widget.setEnabled(False)

        # ── Wall Position ──
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Wall Position:"))
        self.wall_pos_combo = QComboBox()
        self.wall_pos_combo.addItems(["Start", "End"])
        self.wall_pos_combo.setStyleSheet("padding: 4px; border: 1px solid #BBB; border-radius: 4px;")
        pos_layout.addWidget(self.wall_pos_combo)
        pos_layout.addStretch()
        controls_layout.addLayout(pos_layout)

        # ── Wall Settings ──
        wall_settings_group = QGroupBox("Wall Settings")
        wall_settings_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #CCC; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        ws_layout = QGridLayout(wall_settings_group)
        
        ws_layout.addWidget(QLabel("Wall Type:"), 0, 0)
        self.wall_type_combo = QComboBox()
        self.wall_type_combo.addItems(["Concrete", "Brick", "Panel"])
        ws_layout.addWidget(self.wall_type_combo, 0, 1)
        
        ws_layout.addWidget(QLabel("Wall Thickness (m):"), 1, 0)
        self.wall_thickness_input = QDoubleSpinBox()
        self.wall_thickness_input.setRange(0.1, 5.0)
        self.wall_thickness_input.setSingleStep(0.1)
        self.wall_thickness_input.setValue(2.0)
        ws_layout.addWidget(self.wall_thickness_input, 1, 1)
        
        ws_layout.addWidget(QLabel("Wall Width (m):"), 2, 0)
        self.wall_width_input = QDoubleSpinBox()
        self.wall_width_input.setRange(1.0, 50.0)
        self.wall_width_input.setSingleStep(0.5)
        self.wall_width_input.setValue(22.0)
        ws_layout.addWidget(self.wall_width_input, 2, 1)
        
        ws_layout.addWidget(QLabel("Wall Height:"), 3, 0)
        height_layout = QHBoxLayout()
        self.auto_height_cb = QCheckBox("Auto")
        self.auto_height_cb.setChecked(True)
        self.wall_height_input = QDoubleSpinBox()
        self.wall_height_input.setRange(1.0, 20.0)
        self.wall_height_input.setSingleStep(0.5)
        self.wall_height_input.setValue(11.0)
        self.wall_height_input.setEnabled(False)
        self.auto_height_cb.toggled.connect(lambda checked: self.wall_height_input.setEnabled(not checked))
        height_layout.addWidget(self.auto_height_cb)
        height_layout.addWidget(self.wall_height_input)
        ws_layout.addLayout(height_layout, 3, 1)
        
        controls_layout.addWidget(wall_settings_group)
        layout.addWidget(self.controls_widget)

        # ── Placement Summary (read-only preview) ──
        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(
            "background-color: #FFEBEE; border: 1px solid #FFCDD2; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #333; font-weight: normal;"
        )
        layout.addWidget(self.summary_label)

        # OK / Cancel
        buttons_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)
        buttons_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white;")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)

        # ── Scan and populate tunnels from all active design layers ──
        self.available_tunnels = []
        self._populate_tunnels()

        # Connections for live update
        self.tunnel_combo.currentIndexChanged.connect(self._on_tunnel_selected)

        # Auto-select first tunnel if available
        if self.available_tunnels:
            self._on_tunnel_selected(0)
        else:
            self.update_summary()
    def _populate_tunnels(self):
        import os
        import json
        if not self.parent:
            return

        active_layer_paths = list(getattr(self.parent, '_per_layer_actors', {}).keys())
        layer_folder = getattr(self.parent, 'current_design_layer_path', None)
        if layer_folder and os.path.exists(layer_folder) and layer_folder not in active_layer_paths:
            active_layer_paths.append(layer_folder)

        subfolder = getattr(self.parent, 'current_subfolder_type', 'designs')
        config_paths = []

        for p in active_layer_paths:
            if not p or not isinstance(p, str) or not os.path.exists(p):
                continue
            is_merger = False
            if "merger" in p.lower() or subfolder == "merger":
                merger_jsons = [f for f in os.listdir(p) if f.endswith('.json')]
                for mj in merger_jsons:
                    try:
                        with open(os.path.join(p, mj), 'r', encoding='utf-8') as f:
                            merger_data = json.load(f)
                        if "merger_points" in merger_data:
                            is_merger = True
                            for pt in merger_data.get("merger_points", []):
                                def add_cfg(json_file_path):
                                    if json_file_path:
                                        d_path = os.path.dirname(json_file_path)
                                        cfg = os.path.join(d_path, 'design_construction_config.json')
                                        if os.path.exists(cfg) and cfg not in config_paths:
                                            config_paths.append(cfg)
                                add_cfg(pt.get("primary_json_path"))
                                for lyr in pt.get("layers", []):
                                    add_cfg(lyr.get("json_path"))
                    except Exception:
                        pass
            if not is_merger:
                cfg = os.path.join(p, 'design_construction_config.json')
                if os.path.exists(cfg) and cfg not in config_paths:
                    config_paths.append(cfg)

        for cfg_path in config_paths:
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg_data = json.load(f)
                    tunnel_config = cfg_data.get("design", {}).get("tunnel")
                    if tunnel_config:
                        tid = tunnel_config.get("tunnel_id", tunnel_config.get("id", "Unknown"))
                        layer_name = os.path.basename(os.path.dirname(cfg_path))
                        tunnel_config["source_layer_folder"] = os.path.dirname(cfg_path)
                        self.available_tunnels.append((tunnel_config, layer_name, tid))
                    else:
                        zc = cfg_data.get("design", {}).get("zero_line_config")
                        if zc:
                            tid = "fallback_tunnel"
                            layer_name = os.path.basename(os.path.dirname(cfg_path))
                            fake_tunnel = {"id": tid, "arc_points": zc.get("arc_points", []),
                                           "start_km": zc.get("point1", {}).get("from_km", 0),
                                           "start_chainage": zc.get("point1", {}).get("from_chainage", 0),
                                           "end_km": zc.get("point2", {}).get("to_km", 0),
                                           "end_chainage": zc.get("point2", {}).get("to_chainage", 0),
                                           "road_width": zc.get("road_width", 10.0),
                                           "source_layer_folder": os.path.dirname(cfg_path)}
                            self.available_tunnels.append((fake_tunnel, layer_name, tid))
            except Exception as e:
                print(f"DEBUG: Error reading {cfg_path}: {e}")

        self.tunnel_combo.clear()
        for t, layer, tid in self.available_tunnels:
            self.tunnel_combo.addItem(f"{tid} (Layer: {layer})")

    def _on_tunnel_selected(self, index):
        self.invalidate_verification()

    def invalidate_verification(self):
        self.verified = False
        self.controls_widget.setEnabled(False)
        self.ok_btn.setEnabled(False)
        
        self.summary_label.setStyleSheet(
            "background-color: #FFEBEE; border: 1px solid #FFCDD2; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #D32F2F; font-weight: bold;"
        )
        self.summary_label.setText("⚠️ Not Verified\n\nPlease verify tunnel selection.")

    def verify_chainage(self):
        from PyQt5.QtWidgets import QMessageBox
        idx = self.tunnel_combo.currentIndex()
        if idx >= 0 and idx < len(self.available_tunnels):
            self.verified = True
            self.controls_widget.setEnabled(True)
            self.ok_btn.setEnabled(True)
            self.update_summary()
            QMessageBox.information(self, "Verified", "Tunnel verified successfully.")
        else:
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid tunnel.")

    def update_summary(self):
        if not self.verified:
            self.invalidate_verification()
            return
            
        self.summary_label.setStyleSheet(
            "background-color: #E8F5E9; border: 1px solid #C8E6C9; border-radius: 6px; "
            "padding: 10px; font-size: 12px; color: #2E7D32; font-weight: bold;"
        )
        self.summary_label.setText("✅ Ready to Place\n\nTunnel Wall")

    def get_data(self):
        if not self.verified:
            return None
            
        try:
            idx = self.tunnel_combo.currentIndex()
            t_id = "Unknown"
            l_name = "Unknown"
            t_obj = {}
            if idx >= 0 and idx < len(self.available_tunnels):
                t_obj, l_name, t_id = self.available_tunnels[idx]
                
            data = {
                "start_km": 0.0,
                "start_chainage": 0.0,
                "portal_side": self.wall_pos_combo.currentText(),
                "wall_position": self.wall_pos_combo.currentText(),
                "wall_type": self.wall_type_combo.currentText(),
                "thickness": self.wall_thickness_input.value(),
                "wall_width": self.wall_width_input.value(),
                "auto_height": self.auto_height_cb.isChecked(),
                "height": self.wall_height_input.value(),
                "offset": 0.0,
                "tunnel_id": t_id,
                "layer_name": l_name,
                "source_layer_folder": t_obj.get("source_layer_folder", "")
            }
            return data
        except Exception:
            return None
        ######################################################################################