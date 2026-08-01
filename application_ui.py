    # Application_UI.py
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QWidget, QGroupBox, QMenu, QAction, QComboBox, QLineEdit,
    QFrame, QPushButton, QToolButton, QSizePolicy, QTextEdit, QCheckBox, QScrollArea, QSlider, QListWidget, QStackedWidget, QMessageBox, QDialog,
    QRadioButton, QGraphicsOpacityEffect
    
)
from PyQt5.QtCore import Qt, QByteArray, QSize, QRectF, QTimer, QPoint, QEvent, QPropertyAnimation, QEasingCurve, QRect, QParallelAnimationGroup
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QFont, QDoubleValidator, QCursor, QColor, QRegion
import os
from utils import resource_path
from PyQt5.QtSvg import QSvgRenderer

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

# VTK imports
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
## Mayur Wakhare 30-06-2026
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera, vtkInteractorStyleUser
#########################################################

from vtkmodules.vtkRenderingCore import (vtkRenderer)
from vtkmodules.vtkCommonColor import vtkNamedColors

from digging_point import DiggingPointInput
from API import WorksheetAPI
# Mayur Wakhare 06-06-2026 : Go to the dialogs module and bring the ShareWithBuddiesDialog, ExpandingRoadDialog, and UnderPassDialog objects into my current file so I can use them directly. ############
from dialogs import ShareWithBuddiesDialog, ExpandingRoadDialog, CenterLineDialog, TBMSetupDialog

import vtk
import math as _math

### Mayur Wakhare 30-06-2026
class TunnelFPSInteractorStyle(vtkInteractorStyleUser):
    """Custom VTK interactor style for Tunnel Camera Mode with Robot control.

    Supports TWO modes controlled by viewer._robot_active:
    ─────────────────────────────────────────────────────
    ROBOT MODE (viewer._robot_active == True):
      • RMB drag: Look around (updates viewer._robot_yaw and _robot_pitch)
      • MMB drag: Translate (Forward/Backward/Strafe relative to camera view)
      • WASD keys: Tracked in viewer._robot_keys_pressed set for movement.
      • Camera is strictly locked to the robot.

    LEGACY MODE (viewer._robot_active == False):
      • LMB drag: Original behaviour (rotates focal point only).
      • Camera position is locked to the tunnel-path controller value.
    """
################################################################

#### Mayur Wakhare 1-7-2026 Camera
    def __init__(self, viewer=None):
        super().__init__()
        self._viewer = viewer
        # Configurable scroll wheel movement speed (meters per wheel notch)
        self.SCROLL_STEP_DISTANCE = 7.0  # was 3.5; doubled for faster scroll
        ### Mayur Wakhare 13-07-2026 Underpass Camera movement 
        self.UNDERPASS_SCROLL_STEP_MULTIPLIER = 10.0  # Configurable movem######## Mayur Wakhare 30-06-2026
        self._locked_position = None  # (x, y, z) — used only in legacy mode
        self._lmb_dragging = False
        ##############################################################
        self._last_x = 0
        self._last_y = 0
  ########### Mayur Wakhare 30-06-2026
        self._sensitivity_look = 0.15  # degrees per pixel
        self._sensitivity_move = 0.05  # meters per pixel
##########################################################
        self.AddObserver("LeftButtonPressEvent", self._on_left_press)
        self.AddObserver("LeftButtonReleaseEvent", self._on_left_release)
        ###################################################################
        self.AddObserver("MouseMoveEvent", self._on_mouse_move)#######################################################
        self.AddObserver("MouseMoveEvent", self._on_mouse_move)
####### Mayur Wakhare 30-06-2026        
        self.AddObserver("MouseWheelForwardEvent", self._on_mouse_wheel_forward)
        self.AddObserver("MouseWheelBackwardEvent", self._on_mouse_wheel_backward)
        self.AddObserver("KeyPressEvent", self._on_key_press)
        self.AddObserver("KeyReleaseEvent", self._on_key_release)

    def _is_robot_mode(self):
        return self._viewer and getattr(self._viewer, '_robot_active', False)
########################################################################
    def set_locked_position(self, x, y, z):
        self._locked_position = (x, y, z)

    def _enforce_position(self):
########## Mayur Wakhare 30-06-2026
        if self._is_robot_mode():
            return
 ######################################################
        if self._locked_position is None:
            return
        ren = self.GetCurrentRenderer()
########### Mayur Wakhare 30-06-2026
        if not ren: return
        ####################################################
        cam = ren.GetActiveCamera()
        pos = cam.GetPosition()
        lp = self._locked_position
        if abs(pos[0] - lp[0]) > 0.001 or abs(pos[1] - lp[1]) > 0.001 or abs(pos[2] - lp[2]) > 0.001:
            cam.SetPosition(lp)
############ Mayur Wakhare 30-06-2026
    def _update_last_pos(self):
 ##############################################################
        interactor = self.GetInteractor()
        if interactor:
            self._last_x, self._last_y = interactor.GetEventPosition()
#### Mayur Wakhare 30-06-2026
    def _on_left_press(self, obj, event):
        self._update_last_pos()
        self._lmb_dragging = True
        print("DEBUG: Mouse Drag Started")
########################################################
    def _on_left_release(self, obj, event):
 ####### Mayur Wakhare 30-06-2026
        self._lmb_dragging = False
        print("DEBUG: Mouse Drag Ended")
 ################################################
        self._enforce_position()

    def _on_key_press(self, obj, event):
        if not self._is_robot_mode(): return
        interactor = self.GetInteractor()
        if not interactor: return
        key = interactor.GetKeySym()
        if key and self._viewer:
            key_lower = key.lower()
 ############### Mayur Wakhare 01-07-2026
            if key_lower in ('w', 'a', 's', 'd', 'left', 'right'):
                #################################################################
                if not hasattr(self._viewer, '_robot_keys_pressed'):
                    self._viewer._robot_keys_pressed = set()
                self._viewer._robot_keys_pressed.add(key_lower)

    def _on_key_release(self, obj, event):
        if not self._is_robot_mode(): return
        interactor = self.GetInteractor()
        if not interactor: return
        key = interactor.GetKeySym()
        if key and self._viewer:
            key_lower = key.lower()
            if hasattr(self._viewer, '_robot_keys_pressed'):
                self._viewer._robot_keys_pressed.discard(key_lower)

    def _on_mouse_wheel_forward(self, obj, event):
        ### Mayur Wakhare 13-07-2026 Underpass Camera movement 
        if not self._is_robot_mode():
            if self._viewer and getattr(self._viewer, '_underpass_camera_active', False):
                if not hasattr(self._viewer, '_fly_path') or not self._viewer._fly_path:
                    return
                cam = None
                if hasattr(self._viewer, 'renderer') and self._viewer.renderer:
                    cam = self._viewer.renderer.GetActiveCamera()
                    
                old_idx = getattr(self._viewer, '_fly_idx', 0)
                old_pos = cam.GetPosition() if cam else (0,0,0)
                old_chainage = 0.0
                if old_idx < len(self._viewer._fly_path):
                    old_chainage = self._viewer._fly_path[old_idx][0]

                # Mouse Scroll Up -> Advance path
                scroll_step = getattr(self, 'UNDERPASS_SCROLL_STEP_MULTIPLIER', 10.0)
                self._viewer._fly_t += getattr(self._viewer, '_fly_speed', 0.015) * scroll_step
                while self._viewer._fly_t >= 1.0:
                    self._viewer._fly_idx += 1
                    self._viewer._fly_t -= 1.0
                    
                if self._viewer._fly_idx >= len(self._viewer._fly_path) - 2:
                    self._viewer._fly_idx = len(self._viewer._fly_path) - 3
                    self._viewer._fly_t = 0.99
                
                # Forcefully invoke the camera pipeline
                self._viewer._set_camera_to_path_index(self._viewer._fly_idx, self._viewer._fly_t)
                
                # Sync slider UI visually
                if hasattr(self._viewer, 'tc_slider'):
                    self._viewer.tc_slider.blockSignals(True)
                    max_idx = len(self._viewer._fly_path) - 2
                    curr_val = self._viewer._fly_idx + self._viewer._fly_t
                    percent = curr_val / max_idx if max_idx > 0 else 0
                    self._viewer.tc_slider.setValue(int(percent * 1000))
                    self._viewer.tc_slider.blockSignals(False)
                
                new_idx = self._viewer._fly_idx
                new_pos = cam.GetPosition() if cam else (0,0,0)
                new_chainage = 0.0
                if new_idx < len(self._viewer._fly_path):
                    new_chainage = self._viewer._fly_path[new_idx][0]

                print(f"  -> Current path index: {old_idx}")
                print(f"  -> New path index: {new_idx}")
                print(f"  -> Current chainage: {old_chainage:.2f}")
                print(f"  -> New chainage: {new_chainage:.2f}")
                print(f"  -> Camera position before movement: ({old_pos[0]:.2f}, {old_pos[1]:.2f}, {old_pos[2]:.2f})")
                print(f"  -> Camera position after movement: ({new_pos[0]:.2f}, {new_pos[1]:.2f}, {new_pos[2]:.2f})")
                print("  -> Render called: Yes")
            return
            ####################################################################
        import math as _math
        if self._viewer and hasattr(self._viewer, '_robot_position'):
            step = self.SCROLL_STEP_DISTANCE
            yaw = self._viewer._robot_yaw
            new_x = self._viewer._robot_position[0] + _math.cos(yaw) * step
            new_y = self._viewer._robot_position[1] + _math.sin(yaw) * step
   ############### Mayur Wakhare 01-07-2026 Robot camera control zoom       
            if hasattr(self._viewer, '_check_wall_collision'):
                new_x, new_y = self._viewer._check_wall_collision(new_x, new_y)
         #####################################################################################   
         ### Mayur Wakhare 30-06-2026 Robot camera control zoom
            if hasattr(self._viewer, '_snap_robot_to_road_z'):
                new_z = self._viewer._snap_robot_to_road_z(new_x, new_y)
            else:
                new_z = self._viewer._robot_position[2]
             ####################################################   
            self._viewer._robot_position = [new_x, new_y, new_z]
            
            if self._viewer._robot_assembly:
                self._viewer._robot_assembly.SetPosition(new_x, new_y, new_z)
                
            if hasattr(self._viewer, '_update_robot_camera'):
                self._viewer._update_robot_camera()

    def _on_mouse_wheel_backward(self, obj, event):
        ### Mayur Wakhare 13-07-2026 Underpass Camera movement 
        if not self._is_robot_mode():
            if self._viewer and getattr(self._viewer, '_underpass_camera_active', False):
                if not hasattr(self._viewer, '_fly_path') or not self._viewer._fly_path:
                    return
                cam = None
                if hasattr(self._viewer, 'renderer') and self._viewer.renderer:
                    cam = self._viewer.renderer.GetActiveCamera()
                    
                old_idx = getattr(self._viewer, '_fly_idx', 0)
                old_pos = cam.GetPosition() if cam else (0,0,0)
                old_chainage = 0.0
                if old_idx < len(self._viewer._fly_path):
                    old_chainage = self._viewer._fly_path[old_idx][0]

                # Mouse Scroll Down -> Move backward along the road centerline
                scroll_step = getattr(self, 'UNDERPASS_SCROLL_STEP_MULTIPLIER', 10.0)
                self._viewer._fly_t -= getattr(self._viewer, '_fly_speed', 0.015) * scroll_step
                while self._viewer._fly_t < 0.0:
                    self._viewer._fly_idx -= 1
                    self._viewer._fly_t += 1.0
                    
                if self._viewer._fly_idx < 0:
                    self._viewer._fly_idx = 0
                    self._viewer._fly_t = 0.0
                
                # Forcefully invoke the camera pipeline
                self._viewer._set_camera_to_path_index(self._viewer._fly_idx, self._viewer._fly_t)
                
                # Sync slider UI visually
                if hasattr(self._viewer, 'tc_slider'):
                    self._viewer.tc_slider.blockSignals(True)
                    max_idx = len(self._viewer._fly_path) - 2
                    curr_val = self._viewer._fly_idx + self._viewer._fly_t
                    percent = curr_val / max_idx if max_idx > 0 else 0
                    self._viewer.tc_slider.setValue(int(percent * 1000))
                    self._viewer.tc_slider.blockSignals(False)
                
                new_idx = self._viewer._fly_idx
                new_pos = cam.GetPosition() if cam else (0,0,0)
                new_chainage = 0.0
                if new_idx < len(self._viewer._fly_path):
                    new_chainage = self._viewer._fly_path[new_idx][0]

                print(f"  -> Current path index: {old_idx}")
                print(f"  -> New path index: {new_idx}")
                print(f"  -> Current chainage: {old_chainage:.2f}")
                print(f"  -> New chainage: {new_chainage:.2f}")
                print(f"  -> Camera position before movement: ({old_pos[0]:.2f}, {old_pos[1]:.2f}, {old_pos[2]:.2f})")
                print(f"  -> Camera position after movement: ({new_pos[0]:.2f}, {new_pos[1]:.2f}, {new_pos[2]:.2f})")
                print("  -> Render called: Yes")
            return
            ###############################################################################################
        import math as _math
        if self._viewer and hasattr(self._viewer, '_robot_position'):
            step = self.SCROLL_STEP_DISTANCE
            yaw = self._viewer._robot_yaw
            new_x = self._viewer._robot_position[0] - _math.cos(yaw) * step
            new_y = self._viewer._robot_position[1] - _math.sin(yaw) * step
################## Mayur Wakhare 01-07-2026 Robot camera control zoom      
            if hasattr(self._viewer, '_check_wall_collision'):
                new_x, new_y = self._viewer._check_wall_collision(new_x, new_y)
                   
            if hasattr(self._viewer, '_snap_robot_to_road_z'):
                new_z = self._viewer._snap_robot_to_road_z(new_x, new_y)
            else:
                new_z = self._viewer._robot_position[2]
             ####################################################################################################################   
            self._viewer._robot_position = [new_x, new_y, new_z]
            
            if self._viewer._robot_assembly:
                self._viewer._robot_assembly.SetPosition(new_x, new_y, new_z)
                
            if hasattr(self._viewer, '_update_robot_camera'):
                self._viewer._update_robot_camera()
#####################################################################
###### Mayur Wakhare 30-06-2026 Robot camera contol mouse movement
    def _on_mouse_move(self, obj, event):
        if not self._lmb_dragging:
            return
            
        interactor = self.GetInteractor()
        if not interactor: return
        ren = self.GetCurrentRenderer()
        if not ren:
            ren = interactor.FindPokedRenderer(*interactor.GetEventPosition())
            if not ren: return

        x, y = interactor.GetEventPosition()
        dx = x - self._last_x
        dy = y - self._last_y
        self._last_x = x
        self._last_y = y

        if dx == 0 and dy == 0:
            return

        import math as _math

        if self._is_robot_mode():
            # ── LMB: Look Around (Yaw/Pitch) ──
            yaw_delta = -dx * self._sensitivity_look * _math.pi / 180.0
            self._viewer._robot_yaw += yaw_delta

            pitch_delta = dy * self._sensitivity_look * _math.pi / 180.0
            self._viewer._robot_pitch += pitch_delta
            max_pitch = 80.0 * _math.pi / 180.0
            self._viewer._robot_pitch = max(-max_pitch, min(max_pitch, self._viewer._robot_pitch))
            
            print(f"DEBUG: Current Yaw: {self._viewer._robot_yaw:.4f}")
            print(f"DEBUG: Current Pitch: {self._viewer._robot_pitch:.4f}")

            if hasattr(self._viewer, '_update_robot_camera'):
                self._viewer._update_robot_camera()
        else:
            # ── Legacy Mode: Rotate Focal Point on LMB Drag ──
            cam = ren.GetActiveCamera()
            pos = cam.GetPosition()
            fp = cam.GetFocalPoint()

            vx = fp[0] - pos[0]
            vy = fp[1] - pos[1]
            vz = fp[2] - pos[2]
            dist = _math.sqrt(vx*vx + vy*vy + vz*vz)
            if dist < 1e-9: dist = 1.0

            yaw_angle = -dx * self._sensitivity_look * _math.pi / 180.0
            cos_y = _math.cos(yaw_angle)
            sin_y = _math.sin(yaw_angle)
            nvx = vx * cos_y - vy * sin_y
            nvy = vx * sin_y + vy * cos_y
            nvz = vz

            pitch_angle = -dy * self._sensitivity_look * _math.pi / 180.0
            horiz = _math.sqrt(nvx*nvx + nvy*nvy)
            cur_elev = _math.atan2(nvz, horiz) if horiz > 1e-9 else 0.0
            new_elev = cur_elev + pitch_angle
            max_elev = 80.0 * _math.pi / 180.0
            new_elev = max(-max_elev, min(max_elev, new_elev))

            if horiz > 1e-9:
                h_dir_x = nvx / horiz
                h_dir_y = nvy / horiz
            else:
                h_dir_x = 1.0
                h_dir_y = 0.0
            new_horiz = dist * _math.cos(new_elev)
            new_vz = dist * _math.sin(new_elev)

            new_fp = (
                pos[0] + h_dir_x * new_horiz,
                pos[1] + h_dir_y * new_horiz,
                pos[2] + new_vz
            )

            cam.SetFocalPoint(new_fp)
            self._enforce_position()

            rw = interactor.GetRenderWindow()
            if rw: rw.Render()

        # Log Camera Position and Forward Vector
        cam = ren.GetActiveCamera()
        if cam:
            pos = cam.GetPosition()
            fp = cam.GetFocalPoint()
            fx = fp[0] - pos[0]
            fy = fp[1] - pos[1]
            fz = fp[2] - pos[2]
            dist = _math.sqrt(fx*fx + fy*fy + fz*fz)
            if dist > 0:
                fx /= dist; fy /= dist; fz /= dist
            print(f"DEBUG: Camera Position: ({pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f})")
            print(f"DEBUG: Camera Forward Vector: ({fx:.4f}, {fy:.4f}, {fz:.4f})")
#####################################################################################################################################################
# =====================================================================================================================================
#                                               ***  CLASS - Start Page ***
# =====================================================================================================================================
class StartPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StartPage")
        self.setStyleSheet("""
            #StartPage {
                background: transparent;
                border: none;
                border-radius: 0px;
            }
            #StartPage QLabel {
                background: transparent;
                border: none;
            }
            #StartPage QWidget#card_container {
                background: transparent;
            }
        """)
        
        # Main layout for overlay
        overlay_layout = QVBoxLayout(self)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.setSpacing(0)
        
        # Centered container for cards
        center_container = QWidget()
        center_container.setObjectName("card_container")
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(50, 50, 50, 50)
        center_layout.setSpacing(60)
        center_layout.setAlignment(Qt.AlignCenter)
        
        # 1. Create New Worksheet Card (AutoCAD "Start Drawing" style)
        self.create_card = self.create_action_card(
            "Create New Worksheet", 
            "Initialize a new project, define project boundaries, and set up your design workspace.", 
            "📄", 
            "#00BCD4"
        )
        center_layout.addWidget(self.create_card)
        
        # 2. Open Existing Worksheet Card
        self.open_card = self.create_action_card(
            "Open Existing Worksheet",
            "Load and continue working on your previously saved projects and measurements.",
            "📂",
            "#FF9800"
        )
        center_layout.addWidget(self.open_card)

        # 3. View System Design Card (NEW)
        self.view_design_card = self.create_action_card(
            "View System Design",
            "Browse and load 3D system designs from the road design library.",
            "🖼️",
            "#4CAF50"
        )
        center_layout.addWidget(self.view_design_card)

        overlay_layout.addStretch(1)
        overlay_layout.addWidget(center_container)
        overlay_layout.addStretch(1)
        
        # Footer
        footer = QLabel("3D Bharat Road Design Tool")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #fff; font-size: 28px; margin-bottom: 20px;")
        overlay_layout.addWidget(footer)

    def create_action_card(self, title, desc, icon_char, accent_color):
        card = QFrame()
        card.setFixedSize(380, 500)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #252525;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(25)
        
        # Large Icon placeholder
        icon_label = QLabel(icon_char)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 100px; color: {accent_color}; background: transparent; border: none;")
        card_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(f"font-size: 26px; font-weight: bold; color: #fff; background: transparent; border: none;")
        card_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(desc)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 14px; color: #aaa; background: transparent; border: none; line-height: 1.5;")
        card_layout.addWidget(desc_label)
        
        card_layout.addStretch()
        
        # Selection Indicator / Button
        self.btn = QPushButton("GET STARTED")
        self.btn.setFixedHeight(50)
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {accent_color};
                border: 2px solid {accent_color};
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {accent_color};
                color: white;
            }}
        """)
        card_layout.addWidget(self.btn)
        
        # Store for referencing
        card.action_button = self.btn
        
        return card


# =====================================================================================================================================
#                                               ***  CLASS - Appilcation UI Constructor ***
# =====================================================================================================================================
#### Mayur Wakhare 30-06-2026
# Camera constants for Robot Mode
CAMERA_BACK_OFFSET = 10.0
CAMERA_HEIGHT_OFFSET = 1.8
CAMERA_LOOK_OFFSET = 1.2
###################################################################
class ApplicationUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.point_cloud = None
        self.vtk_widget = None
        self.renderer = None
        self.message_section = None
        self.message_text = None
        self.message_visible = False
        self.canvas = None
        self.ax = None
        self.scale_ax = None # For scale graph
        self.start_point = None
        self.end_point = None
        self.total_distance = 100.0
        self.original_total_distance = self.total_distance
        self.zero_line_actor = None
        self.zero_start_actor = None
        self.zero_end_actor = None
        self.zero_graph_line = None
        self.zero_line_set = False
        self.zero_start_point = None
        self.zero_end_point = None
        self.zero_start_km = None
        self.zero_start_chainage = None
        self.zero_end_km = None
        self.zero_end_chainage = None
        self.zero_interval = None
        self.zero_physical_dist = 0.0
        self.zero_start_z = 0.0 # Reference zero elevation (Z of Point_1)
        self.drawing_zero_line = False
        self.zero_points = []
        self.temp_zero_actors = []
        self.line_types = {
            'construction': {'color': 'red', 'polylines': [], 'artists': []},
            'surface': {'color': 'green', 'polylines': [], 'artists': []},
            'zero': {'color':'purple', 'polylines': [], 'artists':[]},
            'road_surface': {'color': 'blue', 'polylines': [], 'artists': []},
            'deck_line': {'color': 'blue', 'polylines': [], 'artists': []},
            'projection_line': {'color': 'green', 'polylines': [], 'artists': []},
            'construction_dots': {'color': 'red', 'polylines': [], 'artists': []},
            'material': {'color': 'orange', 'polylines': [], 'artists': []}
        }
        self.active_line_type = None
        self.current_points = []
        self.current_artist = None
        self.cid_click = None
        self.cid_key = None

# --------------------------------------------------------------------------------------------------------------------------------
        self.PENCIL_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
        viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 20h9"/> <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
        </svg>"""

# --------------------------------------------------------------------------------------------------------------------------------
        self.svg_left = b"""<svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M15 18L9 12L15 6" stroke="white" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>"""
        self.svg_right = b"""<svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M9 6L15 12L9 18" stroke="white" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>"""
# --------------------------------------------------------------------------------------------------------------------------------
        self.baseline_actors = []
        self.measurement_actors = []
        self.measurement_points = []
        self.point_cloud = None
        self.point_cloud_actor = None
        # Colors
        self.colors = vtkNamedColors()
        self.measurement_active = True
        self.current_measurement = None
        self.measurement_started = False
        self.main_line_actor = None
        self.point_a_actor = None
        self.point_b_actor = None

        self.current_vertical_points = []        # stores the two points of the current vertical line
        self.is_presized_mode = False
        # Initialize actors for horizontal line measurement
        self.horizontal_line_actor = None
        self.point_p_actor = None
        self.point_q_actor = None
        self.horizontal_distance_label_actor = None
        # To save and load actors
        self.vertical_points = [] # for vertical line
        self.horizontal_points = [] # for horizontal line
        # For polygon
        self.polygon_points = []
        self.polygon_actors = []
        self.vertical_height_meters = 0.0 # Store vertical height
        self.distance_label_actor = None # Store distance label actor
        self.polygon_area_meters = 0.0 # Store polygon Surface Area
        self.horizontal_length_meters = 0.0 # Store horizontal length
        self.polygon_perimeter_meters = 0.0
        self.polygon_volume_meters = 0.0
        self.polygon_outer_surface_meters = 0.0
        self.presized_volume = 0.0
        self.presized_outer_surface = 0.0
        # ============ Aniket Addded on 07-05-2026 : for the point cloud data freez on X & Y axis ======
        # NEW: View control states
        self.freeze_view = False # Track if view is frozen
        self.rotation_values = {
            'x_left': 90.0,
            'x_right': 90.0,
            'y_left': 90.0,
            'y_right': 90.0,
        }
        self.rotation_lock_active = False
        self.rotation_lock_dragging = False
        self.rotation_lock_observer_tags = []
        self.rotation_lock_state = None
        ### Mayur Wakhare 30-06-2026 Robot camera control 
        # ===============================================================================
        # ── Robot/Player state for Tunnel Camera Mode ──
        self._robot_active = False          # True when robot mode is engaged
        self._robot_actors = []             # VTK actors for robot geometry
        self._robot_assembly = None         # vtkAssembly grouping body + head
        self._robot_position = None         # [x, y, z] world position
        self._robot_yaw = 0.0              # facing direction (radians from east, CCW)
        self._robot_pitch = 0.0            # look pitch (radians, + is up)
        self._robot_speed = 0.3            # movement speed (meters per tick)
        self._robot_keys_pressed = set()   # currently held WASD keys
        self._robot_move_timer = None      # QTimer for movement updates
        self._robot_cam_offset_back = CAMERA_BACK_OFFSET  # camera distance behind robot (meters)
        self._robot_cam_offset_up = CAMERA_HEIGHT_OFFSET    # camera height above robot (meters)
        self._robot_eye_height = CAMERA_LOOK_OFFSET       # focal target height above robot base
        ##################################################################################
        # ===============================================================================
        self.plotting_active = True # Track if plotting is active
        self.preview_actors = []
        self.all_graph_lines = []
        self.redo_stack = []
        self.current_redo_points = []

        # Initialize the list to track items
        self.material_items = []  # Important: add this in __init__ or here

        # Add this new variable to store point labels
        self.point_labels = []  # For storing point label annotations
        self.current_point_labels = []  # For current drawing session

        self.three_D_layers_layout = None
        self.two_D_layers_layout = None

        # ADD THESE TWO LINES
        self.three_D_frame = None   # Will hold the 3D Layers frame
        self.two_D_frame = None     # Will hold the 2D Layers frame

        self.current_worksheet_name = None
        self.current_project_name = None

        # App-level mode must exist before initUI() applies the initial mode.
        self.app_mode = "Design"

        self.initUI()
        self.create_progress_bar()
        self.create_file_load_section()
        self.create_action_section()
        self.create_measurement_section()
        self.create_output_section()
        self.create_menu_section()
        self.create_simulation_panel()

        # Add curve-related attributes here:
        self.curve_annotation = None
        self.curve_arrow_annotation = None
        self.curve_pick_id = None
        self.curve_annotation_x_pos = None

        # To store the last point of the surface line (for curve annotation)
        self.last_surface_point_x = None

        self.curve_annotation_x_pos = None  # To remember where it is placed

        # ADD THESE NEW VARIABLES (near other self. variables)
        self.curve_pick_id = None  # For clickable annotation
        self.curve_annotation = None
        self.curve_arrow_annotation = None
        self.current_curve_config = {'outer_curve': False, 'inner_curve': False, 'angle': 0.0}
        self.curve_active = False  # NEW: Track if a curve is currently active

        # Add these attributes
        self.current_mode = None  # 'road' or 'bridge'
        self.road_lines_data = {}  # Store road lines when switching to bridge
        self.bridge_lines_data = {}  # Store bridge lines when switching to road

        # Add these to the __init__ method
        self.road_lines_data = {
            'construction': {'polylines': [], 'artists': []},
            'surface': {'polylines': [], 'artists': []},
            'road_surface': {'polylines': [], 'artists': []},
            'zero': {'polylines': [], 'artists': []}
        }

        self.bridge_lines_data = {
            'deck_line': {'polylines': [], 'artists': []},
            'projection_line': {'polylines': [], 'artists': []},
            'construction_dots': {'polylines': [], 'artists': []},
            'zero': {'polylines': [], 'artists': []}
        }

        self.current_mode = None 

        # Per-layer actor tracking: { layer_full_path: [vtk_actor, ...] }
        # Used to independently remove a specific layer's 3D actors when eye is toggled off
        self._per_layer_actors = {}

        # In the __init__ method, add these attributes:
        self.last_click_time = 0
        self.double_click_threshold = 0.5

        self.construction_dot_artists = [] 

        self.material_items = []

        # Create a layout for material items if it doesn't exist
        if not hasattr(self, 'material_items_layout'):
            self.material_items_layout = QVBoxLayout()
            self.material_items_layout.setContentsMargins(0, 0, 0, 0)
            self.material_items_layout.setSpacing(5)
            
            # Create a widget to hold the material items
            material_items_widget = QWidget()
            material_items_widget.setLayout(self.material_items_layout)

        # Track last clicked point for elevation angle
        self.last_clicked_surface_point = None  # Store (chainage, elevation)
        self.last_clicked_point_index = -1      # Index in current polyline

# ========================================================================================================================================================
#                                                           *** Application UI Function ***
# =========================================================================================================================================================
    def show_viewer(self):
        """Switch to the 3D/2D viewer and show side panels."""
        if hasattr(self, 'middle_stack'):
            self.middle_stack.setCurrentWidget(self.vtk_container)
            # Force a re-render with a small delay once visible to avoid OpenGL glitches
            if hasattr(self, 'vtk_widget'):
                QTimer.singleShot(100, lambda: self.vtk_widget.GetRenderWindow().Render())
            if hasattr(self, 'threeD_button'):
                QTimer.singleShot(0, self.update_3d_button_position)
        # Show floating overlay buttons (hidden during start screen)
        ## Mayur Wakhare 13/7/2026 robot bar button right side tunnel 
        for _btn in ('threeD_button', 'camera_floating_button', 'tunnel_camera_button', 'underpass_camera_button', 'rotation_state_badge'):
            #####################################################
            if hasattr(self, _btn):
                getattr(self, _btn).setVisible(True)
                getattr(self, _btn).raise_()
        # Show the toggle tab so the user can open the left panel
        if hasattr(self, 'left_toggle_btn'):
            self.left_toggle_btn.setVisible(True)
            QTimer.singleShot(60, self.update_left_panel_position)

    def show_start_screen(self):
        """Switch to the AutoCAD-like start screen."""
        if hasattr(self, 'middle_stack'):
            self.middle_stack.setCurrentWidget(self.start_page)
        # Hide the overlay left panel and its toggle tab on start screen
        if hasattr(self, 'left_section'):
            self.left_section.setVisible(False)
        if hasattr(self, 'left_toggle_btn'):
            self.left_toggle_btn.setVisible(False)
        # Hide floating overlay buttons — not relevant on the start screen
        ## Mayur Wakhare 13/7/2026 robot bar button right side tunnel 
        
        for _btn in ('threeD_button', 'camera_floating_button', 'tunnel_camera_button', 'underpass_camera_button', 'rotation_state_badge'):
         #################################################################
            if hasattr(self, _btn):
                getattr(self, _btn).setVisible(False)
    
    def set_menu_buttons_enabled(self, enabled):
        buttons = [
            'edit_button', 'clear_button', 'copy_button', 'paste_button',
            'save_file_button', 'save_worksheet_button', 'tunnel_excavation_button',
            'expanding_road_button', 'excavation_btn'
        ]
        for btn_name in buttons:
            if hasattr(self, btn_name):
                getattr(self, btn_name).setEnabled(enabled)

    def _slow_mouse_move(self, obj, event):
        """Slow down mouse rotation, panning, and zooming by scaling the delta."""
        if not hasattr(self, 'interactor') or not self.interactor:
            return
        style = self.interactor.GetInteractorStyle()
        if style:
            state = style.GetState()
            if state != 0:  # 1=Rotate, 2=Pan, 3=Spin, 4=Dolly/Zoom
                last = self.interactor.GetLastEventPosition()
                curr = self.interactor.GetEventPosition()
                dx = curr[0] - last[0]
                dy = curr[1] - last[1]
                # Scale down movement to reduce speed (e.g., 5% of original speed)
                speed_factor = 0.0005
                self.interactor.SetEventPosition(int(last[0] + dx * speed_factor), int(last[1] + dy * speed_factor))
    def initUI(self):
        self.setWindowTitle('3D Bharat Design & Measurement Tool')
        self.setWindowIcon(QIcon(resource_path(os.path.join("data", "MI_logo.png"))))
        self.setGeometry(100, 100, 1200, 800)
        
        # Main vertical layout for the entire window
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)
        
        # -----------------------------------------------------------------
        # TOP SECTION – Toolbar
        # ------------------------------------------------------------------
        top_section = QFrame()
        top_section.setFrameStyle(QFrame.Box | QFrame.Raised)
        top_section.setFixedHeight(80)
        top_section.setStyleSheet("""
            QFrame {
                border: 3px solid #8F8F8F;
                border-radius: 10px;
                background-color: #8FBFEF;
                margin-left: 3px;
                margin-right: 3px;
            }
        """)
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(10, 5, 10, 5)
        top_layout.setSpacing(10)
        top_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Logo instead of hamburger menu
        top_logo = QLabel()
        logo_path = resource_path(os.path.join("data", "3D Bharat logo.png"))
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            top_logo.setPixmap(scaled_logo)
        top_logo.setStyleSheet("background: transparent; border:None;")
        top_layout.addWidget(top_logo)
        # ------------------------------------------------------------------
        # Helper: create a button with dropdown (New / Existing)
        # ------------------------------------------------------------------
        def create_dropdown_button(text, emoji, width=120):
            btn = QPushButton(f"{emoji} {text}")
            btn.setFixedWidth(width)
            btn.setFixedHeight(65)
            btn.setCheckable(True)

            # Dropdown widget (the little box that appears below)
            dropdown = QWidget()
            dropdown.setWindowFlags(Qt.Popup)
            dropdown_layout = QVBoxLayout(dropdown)
            dropdown_layout.setContentsMargins(4, 4, 4, 4)
            dropdown_layout.setSpacing(2)

            btn_new = QPushButton("New")
            btn_existing = QPushButton("Existing")
            btn_new.setFixedHeight(40)
            btn_new.setFixedWidth(100)
            btn_existing.setFixedWidth(100)
            btn_existing.setFixedHeight(40)

            dropdown_layout.addWidget(btn_new)
            dropdown_layout.addWidget(btn_existing)

            # Connect (you can change these slots to your real functions)
            btn_new.clicked.connect(lambda: self.on_dropdown_choice(btn, "New"))
            btn_existing.clicked.connect(lambda: self.on_dropdown_choice(btn, "Existing"))

            # Show/hide logic
            def toggle():
                if btn.isChecked():
                    # close any other open dropdown first
                    for other in [self.worksheet_button, self.design_button,
                                  self.construction_button, self.setting_button,
                                  self.buddy_button]:  # <-- added new buttons
                        if other is not btn and other.isChecked():
                            other.setChecked(False)
                            other.property("dropdown").hide()
                    # position exactly under the button
                    pos = btn.mapToGlobal(QPoint(0, btn.height()))
                    dropdown.move(pos)
                    dropdown.show()
                    btn.setProperty("dropdown", dropdown)
                else:
                    dropdown.hide()

            btn.clicked.connect(toggle)

            # Close when clicking outside
            dropdown.installEventFilter(self)

            return btn, dropdown, btn_new, btn_existing
        

        # ------------------------------------------------------------------
        # NEW: Earthwork button + dropdown (only "Rolling")
        # ------------------------------------------------------------------
        self.menu_bar_button = QPushButton("☰ \n Menu")
        self.menu_bar_button.setFixedWidth(80)
        self.menu_bar_button.setFixedHeight(65)
        self.menu_bar_button.setCheckable(True)
        self.menu_bar_button.setStyleSheet("font-weight: bold;")

        menu_bar_dropdown = QWidget()
        menu_bar_dropdown.setWindowFlags(Qt.Popup)
        menu_bar_dd_layout = QVBoxLayout(menu_bar_dropdown)
        menu_bar_dd_layout.setContentsMargins(4, 4, 4, 4)
        menu_bar_dd_layout.setSpacing(2)

        self.edit_button = QPushButton("Edit")
        self.edit_button.setFixedHeight(40)
        self.edit_button.setFixedWidth(100)
        menu_bar_dd_layout.addWidget(self.edit_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setFixedHeight(40)
        self.clear_button.setFixedWidth(100)
        menu_bar_dd_layout.addWidget(self.clear_button)
        self.clear_button.clicked.connect(self.open_clear_layers_dialog)    
        
        self.copy_button = QPushButton("Copy")
        self.copy_button.setFixedHeight(40)
        self.copy_button.setFixedWidth(100)
        menu_bar_dd_layout.addWidget(self.copy_button)
        self.copy_button.clicked.connect(self.open_copy_dialog)

        self.paste_button = QPushButton("Paste")
        self.paste_button.setFixedHeight(40)
        self.paste_button.setFixedWidth(100)
        menu_bar_dd_layout.addWidget(self.paste_button)
        self.paste_button.clicked.connect(self.open_paste_dialog)

        self.save_file_button = QPushButton("Save")
        self.save_file_button.setFixedHeight(40)
        self.save_file_button.setFixedWidth(100)
        menu_bar_dd_layout.addWidget(self.save_file_button)

        self.save_worksheet_button = QPushButton("Save As")
        self.save_worksheet_button.setFixedHeight(40)
        self.save_worksheet_button.setFixedWidth(100)
        menu_bar_dd_layout.addWidget(self.save_worksheet_button)
        self.save_worksheet_button.clicked.connect(self.save_as_worksheet)

        self.tunnel_excavation_button = QPushButton("Tunnel Excavation ▶")
        self.tunnel_excavation_button.setFixedHeight(40)
        self.tunnel_excavation_button.setFixedWidth(120)
        self.tunnel_excavation_button.setCheckable(True)
        self.tunnel_excavation_button.setVisible(False)
        menu_bar_dd_layout.addWidget(self.tunnel_excavation_button)

        # Sub-dropdown: Tunnel Excavation Options
        self.tunnel_sub_dropdown = QWidget()
        self.tunnel_sub_dropdown.setWindowFlags(Qt.Popup)
        tunnel_sub_layout = QVBoxLayout(self.tunnel_sub_dropdown)
        tunnel_sub_layout.setContentsMargins(4, 4, 4, 4)
        tunnel_sub_layout.setSpacing(2)

        self.tunnel_mark_points_btn = QPushButton("Mark Points")
        self.tunnel_cut_btn = QPushButton("Cut")
        self.tunnel_start_end_btn = QPushButton("Tunnel Start/ End")
        self.tunnel_view_hide_road_btn = QPushButton("View/ Hide Road")
        self.tunnel_view_hide_btn = QPushButton("View/ Hide Tunnel")

        for tbtn in [self.tunnel_mark_points_btn, self.tunnel_cut_btn, self.tunnel_start_end_btn, self.tunnel_view_hide_road_btn, self.tunnel_view_hide_btn]:
            tbtn.setFixedHeight(40)
            tbtn.setFixedWidth(140)
            tunnel_sub_layout.addWidget(tbtn)

        def toggle_tunnel_sub():
            if self.tunnel_excavation_button.isChecked():
                pos = self.tunnel_excavation_button.mapToGlobal(QPoint(self.tunnel_excavation_button.width(), 0))
                self.tunnel_sub_dropdown.move(pos)
                self.tunnel_sub_dropdown.show()
            else:
                self.tunnel_sub_dropdown.hide()

        self.tunnel_excavation_button.clicked.connect(toggle_tunnel_sub)
        self.expanding_road_button = QPushButton("Expanding Road")
        self.expanding_road_button.setFixedHeight(40)   
        self.expanding_road_button.setFixedWidth(120)
        self.expanding_road_button.clicked.connect(self.open_expanding_road_dialog)
        menu_bar_dd_layout.addWidget(self.expanding_road_button)

        # Excavation Button (Moved here as requested by USER)
        self.excavation_btn = QPushButton("⛏ Excavation")
        self.excavation_btn.setFixedHeight(40)
        self.excavation_btn.setFixedWidth(120)
        self.excavation_btn.setCursor(Qt.PointingHandCursor)
        self.excavation_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
        """)
        if hasattr(self, 'handle_excavation_clicked'):
            self.excavation_btn.clicked.connect(self.handle_excavation_clicked)
        menu_bar_dd_layout.addWidget(self.excavation_btn)
        
        
        
########## Mayur Wakhare 05-06-2026 : Added Under pass button on Menu bar ############
        self.under_pass_btn = QPushButton("Under Pass")
        self.under_pass_btn.setFixedHeight(40)
        self.under_pass_btn.setFixedWidth(100)
        self.under_pass_btn.clicked.connect(self.handle_under_pass_clicked)
        menu_bar_dd_layout.addWidget(self.under_pass_btn)

########## Mayur Wakhare 31-07-2026 : Added Tunnel button on Menu bar ############
        self.tunnel_btn = QPushButton("Menu_Tunnel ▶")
        self.tunnel_btn.setFixedHeight(40)
        self.tunnel_btn.setFixedWidth(120)
        self.tunnel_btn.setCheckable(True)
        menu_bar_dd_layout.addWidget(self.tunnel_btn)

        # Sub-dropdown: Menu Tunnel Options
        self.menu_tunnel_sub_dropdown = QWidget()
        self.menu_tunnel_sub_dropdown.setWindowFlags(Qt.Popup)
        menu_tunnel_sub_layout = QVBoxLayout(self.menu_tunnel_sub_dropdown)
        menu_tunnel_sub_layout.setContentsMargins(4, 4, 4, 4)
        menu_tunnel_sub_layout.setSpacing(2)

        self.menu_tunnel_center_line_btn = QPushButton("Center Line")
        self.menu_tunnel_center_line_btn.setFixedHeight(40)
        self.menu_tunnel_center_line_btn.setFixedWidth(140)
        
        def handle_center_line_click():
            # 1. Immediately hide the menus
            if hasattr(self, 'menu_tunnel_sub_dropdown'):
                self.menu_tunnel_sub_dropdown.hide()
            if hasattr(self, 'tunnel_btn'):
                self.tunnel_btn.setChecked(False)
            if hasattr(self, 'menu_bar_button'):
                self.menu_bar_button.setChecked(False)
                if self.menu_bar_button.property("dropdown"):
                    self.menu_bar_button.property("dropdown").hide()

            worksheet_open = bool(getattr(self, "current_worksheet_name", None))
            design_active = (str(getattr(self, "active_layer_highlight_subfolder", "")).lower() == "designs")
            
            if not worksheet_open or not design_active:
                QMessageBox.warning(self, "Action Unavailable", "Center Line is available only when a Worksheet is open and a Design Layer is active.")
                return
           ### Mayur 1-8-2026 Center Line Implementation Start  
            def on_center_line_picked(p1, p2):
                def show_dialog():
                    existing_config = None
                    if getattr(self, 'center_line_p1', None) is not None:
                        existing_config = {
                            'count': getattr(self, 'center_line_cp_count', 0),
                            'angles': getattr(self, 'center_line_angles', []),
                            'turns': getattr(self, 'center_line_turns', []),
                            'v_angles': getattr(self, 'center_line_v_angles', []),
                            'v_turns': getattr(self, 'center_line_v_turns', [])
                        }
                    dialog = CenterLineDialog(p1, p2, existing_config, parent=self)
                    if dialog.exec_() == QDialog.Accepted:
                        self.center_line_p1 = p1
                        self.center_line_p2 = p2
                        count = dialog.cp_spinbox.value()
                        self.center_line_cp_count = count
                        self.center_line_angles = dialog.get_angles()
                        self.center_line_turns = dialog.get_turns()
                        self.center_line_v_angles = dialog.get_v_angles()
                        self.center_line_v_turns = dialog.get_v_turns()
                        if hasattr(self, 'preview_center_line_control_points'):
                            self.preview_center_line_control_points(p1, p2, count, self.center_line_angles, self.center_line_turns, self.center_line_v_angles, self.center_line_v_turns)
                # Delay the dialog slightly so VTK receives the mouse release event, preventing the camera spin
                QTimer.singleShot(100, show_dialog)
                
            if getattr(self, 'center_line_p1', None) is not None and getattr(self, 'center_line_p2', None) is not None:
                on_center_line_picked(self.center_line_p1, self.center_line_p2)
            else:
                if hasattr(self, 'start_center_line_picking'):
                    self.start_center_line_picking(on_center_line_picked)

        self.menu_tunnel_center_line_btn.clicked.connect(handle_center_line_click)
        menu_tunnel_sub_layout.addWidget(self.menu_tunnel_center_line_btn)
        
        self.menu_tunnel_clear_center_line_btn = QPushButton("Clear Center Line")
        self.menu_tunnel_clear_center_line_btn.setFixedHeight(40)
        self.menu_tunnel_clear_center_line_btn.setFixedWidth(140)
        self.menu_tunnel_clear_center_line_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FFFFFF;
                border: 1px solid #4D4D4D;
                border-radius: 8px;
                padding: 10px;
                text-align: left;
                padding-left: 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #666666;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)
        def handle_clear_center_line():
            self.center_line_p1 = None
            self.center_line_p2 = None
            self.center_line_cp_count = 0
            self.center_line_angles = []
            self.center_line_turns = []
            self.center_line_v_angles = []
            self.center_line_v_turns = []
            if hasattr(self, 'preview_center_line_control_points'):
                self.preview_center_line_control_points(None, None, 0)
        self.menu_tunnel_clear_center_line_btn.clicked.connect(handle_clear_center_line)
        menu_tunnel_sub_layout.addWidget(self.menu_tunnel_clear_center_line_btn)

        self.menu_tunnel_tbm_setup_btn = QPushButton("TBM Setup")
        self.menu_tunnel_tbm_setup_btn.setFixedHeight(40)
        self.menu_tunnel_tbm_setup_btn.setFixedWidth(140)
    ## Mayur 1-8-2026: Added Tunnel boring Machine on menu bar
        def handle_tbm_setup_click():
            # 1. Immediately hide the menus
            if hasattr(self, 'menu_tunnel_sub_dropdown'):
                self.menu_tunnel_sub_dropdown.hide()
            if hasattr(self, 'tunnel_btn'):
                self.tunnel_btn.setChecked(False)
            if hasattr(self, 'menu_bar_button'):
                self.menu_bar_button.setChecked(False)
                if self.menu_bar_button.property("dropdown"):
                    self.menu_bar_button.property("dropdown").hide()

            worksheet_open = bool(getattr(self, "current_worksheet_name", None))
            design_active = (str(getattr(self, "active_layer_highlight_subfolder", "")).lower() == "designs")
            
            if not worksheet_open or not design_active:
                QMessageBox.warning(self, "Action Unavailable", "TBM Setup is available only when a Worksheet is open and a Design Layer is active.")
                return

            if not hasattr(self, 'center_line_points') or len(self.center_line_points) < 2:
                QMessageBox.warning(self, "Action Unavailable", "Please define a Center Line first.")
                return

            dialog = TBMSetupDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.tbm_setup_length = dialog.tbm_length
                self.tbm_setup_breadth = dialog.tbm_breadth
                self.tbm_setup_thickness = dialog.tbm_thickness
                self.tbm_setup_offset = dialog.tbm_offset
                
                # Render the RCC Setup Block
                import numpy as np
                import vtk
                
                p1 = np.array(self.center_line_points[0])
                p2 = np.array(self.center_line_points[1])
                
                dir_vec = p2 - p1
                norm = np.linalg.norm(dir_vec)
                if norm == 0:
                    return
                dir_vec = dir_vec / norm
                
                L = self.tbm_setup_length
                B = self.tbm_setup_breadth
                T = self.tbm_setup_thickness
                
                # To ensure the slab appears at the given offset behind the start point (opposite side) 
                # and does not overlap it, the offset marks the beginning of the slab.
                # Therefore, the geometric center of the slab is at offset + L/2 in the opposite direction.
                offset_dist = self.tbm_setup_offset + (L / 2.0)
                center_pos = p1 - dir_vec * offset_dist
                
                # Single solid slab
                slab = vtk.vtkCubeSource()
                slab.SetXLength(L)
                slab.SetYLength(B)
                slab.SetZLength(T)
                # Position the slab so its top aligns with the center line (z=0)
                slab.SetCenter(0, 0, -T/2)
                slab.Update()
                
                # Setup transformation to align with center line
                math = vtk.vtkMath()
                forward = dir_vec.tolist()
                right_vec = [0.0, 0.0, 0.0]
                up_vec = [0.0, 0.0, 1.0] # assume vertical is mostly up
                
                # Avoid singularity if dir is exactly vertical
                if abs(forward[2]) > 0.99:
                    up_vec = [0.0, 1.0, 0.0]
                    
                math.Cross(forward, up_vec, right_vec)
                math.Normalize(right_vec)
                math.Cross(right_vec, forward, up_vec)
                math.Normalize(up_vec)
                
                matrix = vtk.vtkMatrix4x4()
                for i in range(3):
                    matrix.SetElement(i, 0, forward[i])
                    matrix.SetElement(i, 1, right_vec[i])
                    matrix.SetElement(i, 2, up_vec[i])
                    matrix.SetElement(i, 3, center_pos[i])
                
                transform = vtk.vtkTransform()
                transform.SetMatrix(matrix)
                
                transform_filter = vtk.vtkTransformPolyDataFilter()
                transform_filter.SetInputData(slab.GetOutput())
                transform_filter.SetTransform(transform)
                transform_filter.Update()
                
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputData(transform_filter.GetOutput())
                
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                # Realistic silver/light grey concrete finish
                prop = actor.GetProperty()
                prop.SetColor(0.75, 0.75, 0.75) 
                prop.SetAmbient(0.5)
                prop.SetDiffuse(0.6)
                prop.SetSpecular(0.3)
                prop.SetSpecularPower(20.0)
                prop.SetOpacity(1.0)
                
                if hasattr(self, 'tbm_setup_actor') and self.tbm_setup_actor:
                    self.renderer.RemoveActor(self.tbm_setup_actor)
                    
                self.tbm_setup_actor = actor
                self.renderer.AddActor(actor)
                self.vtk_widget.GetRenderWindow().Render()

        self.menu_tunnel_tbm_setup_btn.clicked.connect(handle_tbm_setup_click)
        menu_tunnel_sub_layout.addWidget(self.menu_tunnel_tbm_setup_btn)

        def toggle_menu_tunnel_sub():
            if self.tunnel_btn.isChecked():
                pos = self.tunnel_btn.mapToGlobal(QPoint(self.tunnel_btn.width(), 0))
                self.menu_tunnel_sub_dropdown.move(pos)
                self.menu_tunnel_sub_dropdown.show()
            else:
                self.menu_tunnel_sub_dropdown.hide()

        self.tunnel_btn.clicked.connect(toggle_menu_tunnel_sub)

######################################################################
        
        
        def toggle_menu_bar():
            if self.menu_bar_button.isChecked():
                # Close other dropdowns
                for other in [self.worksheet_button, self.design_button,
                              self.construction_button, self.setting_button,
                              self.buddy_button]:
                    if other.isChecked():
                        other.setChecked(False)
                        other.property("dropdown").hide()
                pos = self.menu_bar_button.mapToGlobal(QPoint(0, self.menu_bar_button.height()))
                menu_bar_dropdown.move(pos)
                menu_bar_dropdown.show()
                self.menu_bar_button.setProperty("dropdown", menu_bar_dropdown)
            else:
                menu_bar_dropdown.hide()
                if hasattr(self, 'tunnel_excavation_button'):
                    self.tunnel_excavation_button.setChecked(False)
                if hasattr(self, 'tunnel_sub_dropdown'):
                    self.tunnel_sub_dropdown.hide()
                ### Mayur 31-7-2026 : Added Tunnel button on Menu bar
                if hasattr(self, 'tunnel_btn'):
                    self.tunnel_btn.setChecked(False)
                if hasattr(self, 'menu_tunnel_sub_dropdown'):
                    self.menu_tunnel_sub_dropdown.hide()
                ##############################################
        self.menu_bar_button.clicked.connect(toggle_menu_bar)
        menu_bar_dropdown.installEventFilter(self)

        top_layout.addWidget(self.menu_bar_button)

    #  Aniket Added on 29-05-2026 : For the Modes of the application (Design, Measurement, Comparison, Simulation)
        # ------------------------------------------------------------------
        # Mode button + dropdown
        # ------------------------------------------------------------------
        self.mode_button = QToolButton(top_section)
        self.mode_button.setText("Mode")
        self.mode_button.setFixedWidth(90)
        self.mode_button.setFixedHeight(65)
        self.mode_button.setPopupMode(QToolButton.InstantPopup)
        self.mode_button.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.mode_button.setCursor(Qt.PointingHandCursor)
        self.mode_button.setStyleSheet("""
            QToolButton {
                font-weight: bold;
                padding: 6px 12px;
            }
            QToolButton::menu-indicator {
                image: none;
                width: 0px;
                height: 0px;
            }
        """)

        self.mode_menu = QMenu(self)
        self.mode_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #3F51B5;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
            }
            QMenu::item:selected {
                background-color: #E8EAF6;
                color: #3F51B5;
            }
            QMenu::item:checked {
                background-color: #DCE6FF;
                color: #1A237E;
                font-weight: bold;
            }
        """)

        self.mode_actions = {}

        for mode_name in ["Design", "Measurement", "Comparison", "Simulation"]:
            action = self.mode_menu.addAction(mode_name)
            action.setCheckable(True)
            self.mode_actions[mode_name] = action
            action.triggered.connect(lambda checked=False, name=mode_name: self.set_mode(name))

        self.mode_button.setMenu(self.mode_menu)
        top_layout.addWidget(self.mode_button)

        # ------------------------------------------------------------------
        # Worksheet button + dropdown
        # ------------------------------------------------------------------
        (self.worksheet_button, dropdown1,
        self.new_worksheet_button, self.existing_worksheet_button) = create_dropdown_button(
            "\n Worksheet", "📊", width=110)
        self.worksheet_button.setStyleSheet("font-weight: bold;")
        # self.new_worksheet_button.clicked.connect(self.open_new_worksheet_dialog)
        top_layout.addWidget(self.worksheet_button)

        # ------------------------------------------------------------------
        # Design button + dropdown
        # ------------------------------------------------------------------
        (self.design_button, dropdown2,
        self.new_design_button, self.existing_design_button) = create_dropdown_button(
            "\n Design", "📐", width=100)
        self.design_button.setStyleSheet("font-weight: bold;")
        # self.new_design_button.clicked.connect(self.open_create_new_design_layer_dialog)
        top_layout.addWidget(self.design_button)

        # ------------------------------------------------------------------
        # Construction button + dropdown
        # ------------------------------------------------------------------
        (self.construction_button, dropdown3,
        self.new_construction_button, self.existing_construction_button) = create_dropdown_button(
            "\n Construction", "🏗", width=130)
        self.construction_button.setStyleSheet("font-weight: bold;")
        # self.new_construction_button.clicked.connect(self.open_construction_layer_dialog)
        top_layout.addWidget(self.construction_button)

        # ------------------------------------------------------------------
        # Measurement button – toggles right-side measurement panel open/close
        # ------------------------------------------------------------------
        self.measurement_button = QPushButton("📏\n Measurement")
        self.measurement_button.setFixedWidth(150)
        self.measurement_button.setFixedHeight(65)
        self.measurement_button.setStyleSheet("font-weight: bold;")
        self.measurement_button.setCursor(Qt.PointingHandCursor)

        def toggle_measurement_panel():
            panel = getattr(self, 'main_measurement_section', None)
            if panel and panel.isVisible():
                # Panel is open → close it, revert to Design mode
                panel.setVisible(False)
            else:
                # Panel is closed → open it via Measurement mode
                self.set_mode("Measurement")

        self.measurement_button.clicked.connect(toggle_measurement_panel)
        top_layout.addWidget(self.measurement_button)

        # ---------------------------------------------------------------
        # Other buttons (unchanged)
        # ------------------------------------------------------------------
        self.layers_button = QPushButton("🔀 \n Create Merger")
        self.layers_button.setStyleSheet("font-weight: bold;")
        self.layers_button.setFixedWidth(125)
        self.layers_button.setFixedHeight(65)
        top_layout.addWidget(self.layers_button)


        self.feedback_button = QPushButton("💬\n Feedback")
        self.feedback_button.setStyleSheet("font-weight: bold;")
        self.feedback_button.setFixedWidth(100)
        self.feedback_button.setFixedHeight(65)
        top_layout.addWidget(self.feedback_button)

        # ========== BUY 3D FILES BUTTON ==========
        self.buy_files_button = QPushButton("🛒\n Buy 3D Files")
        self.buy_files_button.setStyleSheet("font-weight: bold;")
        self.buy_files_button.setFixedWidth(110)
        self.buy_files_button.setFixedHeight(65)
        top_layout.addWidget(self.buy_files_button)

        # ------------------------------------------------------------------
        # UPDATED: Settings button with multi-level nested dropdowns
        # ------------------------------------------------------------------
        self.setting_button = QPushButton("⚙ \n Settings")
        self.setting_button.setStyleSheet("font-weight: bold;")
        self.setting_button.setFixedWidth(100)
        self.setting_button.setFixedHeight(65)
        self.setting_button.setCheckable(True)

        # Main Settings Dropdown
        settings_dropdown = QWidget()
        settings_dropdown.setWindowFlags(Qt.Popup)
        settings_layout = QVBoxLayout(settings_dropdown)
        settings_layout.setContentsMargins(4, 4, 4, 4)
        settings_layout.setSpacing(2)

        self.general_setting_btn = QPushButton("General Setting")
        self.camera_setting_btn = QPushButton("Camera Setting ▶")
        self.simulation_setting_btn = QPushButton("Simulation Setting")

        for btn in [self.general_setting_btn, self.camera_setting_btn, self.simulation_setting_btn]:
            btn.setFixedHeight(40)
            btn.setFixedWidth(160)
            settings_layout.addWidget(btn)

        # Upload Design button inside Settings dropdown (blue styled)
        self.upload_design_btn = QPushButton("⬆ Upload Design")
        self.upload_design_btn.setFixedHeight(40)
        self.upload_design_btn.setFixedWidth(160)
        self.upload_design_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        settings_layout.addWidget(self.upload_design_btn)

        # Sub-dropdown: Camera Settings (Angle, Zoom, View)
        camera_sub_dropdown = QWidget()
        camera_sub_dropdown.setWindowFlags(Qt.Popup)
        camera_sub_layout = QVBoxLayout(camera_sub_dropdown)
        camera_sub_layout.setContentsMargins(4, 4, 4, 4)
        camera_sub_layout.setSpacing(2)

        self.angle_btn = QPushButton("Angle")
        self.zoom_btn = QPushButton("Zoom")
        self.view_btn = QPushButton("View ▶")

        for btn in [self.angle_btn, self.zoom_btn, self.view_btn]:
            btn.setFixedHeight(40)
            btn.setFixedWidth(140)
            camera_sub_layout.addWidget(btn)

        # Sub-sub-dropdown: View Options (Top, Left, Right)
        view_sub_dropdown = QWidget()
        view_sub_dropdown.setWindowFlags(Qt.Popup)
        view_sub_layout = QVBoxLayout(view_sub_dropdown)
        view_sub_layout.setContentsMargins(4, 4, 4, 4)
        view_sub_layout.setSpacing(2)

        self.top_view_btn = QPushButton("Top View")
        self.left_side_btn = QPushButton("Left Side")
        self.right_side_btn = QPushButton("Right Side")

        for vbtn in [self.top_view_btn, self.left_side_btn, self.right_side_btn]:
            vbtn.setFixedHeight(40)
            vbtn.setFixedWidth(120)
            view_sub_layout.addWidget(vbtn)

        # Toggle View sub-dropdown (Top/Left/Right)
        def toggle_view_sub():
            if self.view_btn.isChecked():
                pos = self.view_btn.mapToGlobal(QPoint(self.view_btn.width(), 0))
                view_sub_dropdown.move(pos)
                view_sub_dropdown.show()
            else:
                view_sub_dropdown.hide()

        self.view_btn.setCheckable(True)
        self.view_btn.clicked.connect(toggle_view_sub)

        # Toggle Camera sub-dropdown (Angle, Zoom, View)
        def toggle_camera_sub():
            if self.camera_setting_btn.isChecked():
                pos = self.camera_setting_btn.mapToGlobal(QPoint(self.camera_setting_btn.width(), 0))
                camera_sub_dropdown.move(pos)
                camera_sub_dropdown.show()
                # Uncheck View to prevent overlap
                self.view_btn.setChecked(False)
                view_sub_dropdown.hide()
            else:
                camera_sub_dropdown.hide()
                view_sub_dropdown.hide()
                self.view_btn.setChecked(False)

        self.camera_setting_btn.setCheckable(True)
        self.camera_setting_btn.clicked.connect(toggle_camera_sub)

        # Main Settings toggle
        def toggle_settings():
            if self.setting_button.isChecked():
                # Close other main dropdowns
                for other in [self.worksheet_button, self.design_button,
                              self.construction_button, self.menu_bar_button,
                              self.buddy_button]:
                    if other.isChecked():
                        other.setChecked(False)
                        if other.property("dropdown"):
                            other.property("dropdown").hide()
                pos = self.setting_button.mapToGlobal(QPoint(0, self.setting_button.height()))
                settings_dropdown.move(pos)
                settings_dropdown.show()
                self.setting_button.setProperty("dropdown", settings_dropdown)
            else:
                settings_dropdown.hide()
                camera_sub_dropdown.hide()
                view_sub_dropdown.hide()
                self.camera_setting_btn.setChecked(False)
                self.view_btn.setChecked(False)

        self.setting_button.clicked.connect(toggle_settings)
        settings_dropdown.installEventFilter(self)

        top_layout.addWidget(self.setting_button)

        # ========== CONNECT BUDDY BUTTON ==========
        self.buddy_button = QPushButton("👥➕\n Buddy")
        self.buddy_button.setStyleSheet("font-weight: bold;")
        self.buddy_button.setFixedWidth(120)
        self.buddy_button.setFixedHeight(65)
        self.buddy_button.setCheckable(True)

        buddy_bar_dropdown = QWidget()
        buddy_bar_dropdown.setWindowFlags(Qt.Popup)
        buddy_bar_dd_layout = QVBoxLayout(buddy_bar_dropdown)
        buddy_bar_dd_layout.setContentsMargins(4, 4, 4, 4)
        buddy_bar_dd_layout.setSpacing(2)

        self.make_buddy_button = QPushButton("Make Buddy")
        self.make_buddy_button.setFixedHeight(40)
        self.make_buddy_button.setFixedWidth(150)
        buddy_bar_dd_layout.addWidget(self.make_buddy_button)

        self.show_buddy_button = QPushButton("My Buddies")
        self.show_buddy_button.setFixedHeight(40)
        self.show_buddy_button.setFixedWidth(150)
        buddy_bar_dd_layout.addWidget(self.show_buddy_button)

        self.share_data_button = QPushButton("Share with My Buddies")
        self.share_data_button.setFixedHeight(40)
        self.share_data_button.setFixedWidth(150)

        buddy_bar_dd_layout.addWidget(self.share_data_button)

        def toggle_buddy_bar():
            if self.buddy_button.isChecked():
                # Close other dropdowns
                for other in [self.worksheet_button, self.design_button,
                              self.construction_button, self.setting_button,
                                self.menu_bar_button]:
                    if other.isChecked():
                        other.setChecked(False)
                        other.property("dropdown").hide()
                pos = self.buddy_button.mapToGlobal(QPoint(0, self.buddy_button.height()))
                buddy_bar_dropdown.move(pos)
                buddy_bar_dropdown.show()
                self.buddy_button.setProperty("dropdown", buddy_bar_dropdown)
            else:
                buddy_bar_dropdown.hide()

        self.buddy_button.clicked.connect(toggle_buddy_bar)
        buddy_bar_dropdown.installEventFilter(self)

        top_layout.addWidget(self.buddy_button)

        # ========== SIMULATION BUTTON ==========
        self.simulation_button = QPushButton("⚡\n Simulation")
        self.simulation_button.setStyleSheet("font-weight: bold;")
        self.simulation_button.setFixedWidth(110)
        self.simulation_button.setFixedHeight(65)
        self.simulation_button.setCheckable(False)
        self.simulation_button.setCursor(Qt.PointingHandCursor)
        top_layout.addWidget(self.simulation_button)

        # ========== EARNINGS DISPLAY =========="
        self.earning_frame = QFrame()
        self.earning_frame.setFixedHeight(65)
        self.earning_frame.setMinimumWidth(160)
        self.earning_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #66bb6a,
                    stop:1 #ffffff
                );
                border: 2px solid white;
                border-radius: 5px;
                margin: 0px;
            }
            QLabel {
                background: transparent;
                border: none;
                color: black;
                font-family: "Segoe UI", Arial, sans-serif;
            }
        """)
        earning_layout = QVBoxLayout()
        earning_layout.setContentsMargins(5, 2, 5, 2)
        earning_layout.setSpacing(0)
        
        top_earning_layout = QHBoxLayout()
        top_earning_label = QLabel("💰 Earnings")
        top_earning_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        top_earning_label.setAlignment(Qt.AlignCenter)
        top_earning_layout.addWidget(top_earning_label)
        
        bottom_earning_layout = QHBoxLayout()
        bottom_earning_layout.setAlignment(Qt.AlignCenter)
        amount_label = QLabel("$ 20.20")
        amount_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        bottom_earning_layout.addWidget(amount_label)
        
        earning_layout.addLayout(top_earning_layout)
        earning_layout.addLayout(bottom_earning_layout)
        self.earning_frame.setLayout(earning_layout)
        
        self.earning_frame.setCursor(Qt.PointingHandCursor)
        self.earning_frame.mousePressEvent = self.show_how_to_earn_dialog
        
        top_layout.addWidget(self.earning_frame)

        top_layout.addStretch()          # push everything to the left  

        # ------------------- Upload Design Button (moved to Settings dropdown) ========
        # NOTE: self.upload_design_btn is now defined inside the Settings dropdown above.

        main_layout.addWidget(top_section)
        self.top_section = top_section  # store ref so menu panel can sit below it
        
        # ------------------------------------------------------------------
        # USER MENU BUTTON (Right side of header) - UPDATED
        # ------------------------------------------------------------------
        # Rectangle button with icon and initials
        self.user_menu_btn = QPushButton(" 👤 G ")  # Default to 'Guest' with icon
        self.user_menu_btn.setFixedHeight(65)
        self.user_menu_btn.setMinimumWidth(75) # Ensure enough space
        self.user_menu_btn.setToolTip("Guest Account")
        self.user_menu_btn.setCursor(Qt.PointingHandCursor)
        
        # Modern rectangle style
        self.user_menu_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3f51b5,
                    stop:1 #ffffff
                );
                color: black;   /* Better visibility on white center */
                font-weight: bold;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 20px;
                border: 2px solid white;
                border-radius: 5px;
                padding: 0 10px;
                text-align: center;
                margin: 0px;
            }

            QPushButton:hover {
                background: qlineargradient(
                    x1:1, y1:1, x2:0, y2:0,
                    stop:0 #3f51b5,
                    stop:1 #ffffff
                );
                border: 2px solid #e0e0e0;
            }

            QPushButton:menu-indicator { 
                image: none; 
            }
        """)

        # Create Menu
        self.user_menu = QMenu(self)
        self.user_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                font-size: 14px;
                color: #333;
            }
            QMenu::item:selected {
                background-color: #f5f5f5;
                color: #3f51b5;
            }
            QMenu::separator {
                height: 1px;
                background: #e0e0e0;
                margin: 5px 0;
            }
        """)
        
        # Add Actions
        # My Profile Action
        self.profile_action = QAction("My Profile", self)
        # self.profile_action.triggered.connect(self.open_profile) # Placeholder
        self.user_menu.addAction(self.profile_action)
        
        self.user_menu.addSeparator()
        
        # Logout Action
        self.logout_action = QAction("Logout", self)
        self.logout_action.triggered.connect(self.close) # Close app for now
        self.user_menu.addAction(self.logout_action)

        self.user_menu.addSeparator()

        self.my_earnings_action = QAction("My Earnings", self)
        # self.my_earnings_action.triggered.connect(self.show_earnings) 
        self.user_menu.addAction(self.my_earnings_action)
        
        # Attach menu
        self.user_menu_btn.setMenu(self.user_menu)
        
        top_layout.addWidget(self.user_menu_btn)

        #------------------- Menu Button ========
        self.menu_button = QToolButton(top_section)
        self.menu_button.setFixedSize(55, 35)
        self.menu_button.setText("🡸")  
        self.menu_button.setStyleSheet("""
        QToolButton {
            background-color: #28a745;
            border: none;
            border-radius: 3px;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }
        QToolButton:hover {
            background-color: #218838;
        }
        QToolButton:pressed {
            background-color: #1e7e34;
        }
        QToolTip {
            background-color: #fffacd;   /* soft yellow */
            color: black;
            border: 1px solid gray;
            padding: 4px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 14px;
        }
        """)
        self.menu_button.setToolTip("Open Assets Menu")

        top_layout.addWidget(self.menu_button)
        
        # -----------------------------------------------------------------
        # BODY AREA: body_widget is the independent parent of BOTH
        # left_section AND content_widget. This makes left_section a SIBLING
        # of the VTK/middle area — NOT nested inside it.
        # -----------------------------------------------------------------
        self.body_widget = QWidget()
        self.body_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body_layout = QHBoxLayout(self.body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # content_widget holds ONLY the right/middle VTK area + measurement section
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_widget.setMinimumWidth(400)
        content_layout = QHBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)

        # --------------------------------
        # LEFT SECTION – Settings
        # ------------------------------------------------------------------
        left_section = QFrame()
        left_section.setFrameStyle(QFrame.NoFrame)
        left_section.setStyleSheet("""
            QFrame {
                border: none;
                border-right: 1px solid rgba(0,0,0,0.10);
                background-color: #FAFAFA;
                margin: 0px;
            }
            QFrame QFrame {
                border: inherit;
                background-color: transparent;
            }
        """)
        self.left_layout = QVBoxLayout(left_section)
        self.left_layout.setContentsMargins(8, 8, 8, 8)
        self.left_layout.setSpacing(6)

        # ------------------------------------------------------------------
        # NEW: Mode Banner (Measurement / Design) - TOP MOST in left panel
        # ------------------------------------------------------------------
        self.mode_banner = QLabel("No Mode Active")
        self.mode_banner.setAlignment(Qt.AlignCenter)
        self.mode_banner.setVisible(False)  # Hidden until worksheet is loaded
        self.left_layout.addWidget(self.mode_banner)

        # ---------------------------------------------------------------------------
        # Merger Layers Section
        # ---------------------------------------------------------------------------
        merger_frame = QFrame()
        merger_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        merger_frame.setStyleSheet("""
            QFrame { 
                border: 2px solid #42A5F5; 
                border-radius: 10px; 
                background-color: #E3F2FD; 
                margin: 5px; 
            }
        """)
        merger_layout = QVBoxLayout(merger_frame)
        merger_frame.setVisible(False)                    # change

        merger_title = QLabel("Merger Layers")
        merger_title.setAlignment(Qt.AlignCenter)
        merger_title.setStyleSheet("""
            font-weight: bold; 
            font-size: 13px; 
            padding: 8px; 
            background-color: #E3F2FD; 
            border-radius: 5px;
        """)
        merger_layout.addWidget(merger_title)
        merger_layout.addStretch()
    

        # --------------------------------------------------------------------------- 
        # 3D Layers Section
        # ---------------------------------------------------------------------------
        self.three_D_frame = QFrame()
        self.three_D_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.three_D_frame.setStyleSheet("""
            QFrame { 
                border: 2px solid #42A5F5; 
                border-radius: 10px; 
                background-color: #E3F2FD; 
                margin: 5px;
            }
        """)
        self.three_D_frame.setMinimumHeight(260)
        self.three_D_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        three_D_layout = QVBoxLayout(self.three_D_frame)
        self.three_D_frame.setVisible(False)

        three_D_title = QLabel("3D Layers")
        three_D_title.setAlignment(Qt.AlignCenter)
        three_D_title.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            padding: 8px; 
            background-color: #BBDEFB; 
            border-radius: 6px;
            color: #1565C0;
        """)
        three_D_layout.addWidget(three_D_title)

        # Scroll area for 3D layers
        three_D_scroll = QScrollArea()
        three_D_scroll.setWidgetResizable(True)
        three_D_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        three_D_scroll.setMinimumHeight(200)
        three_D_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        three_D_scroll.setStyleSheet("""
            QScrollArea { background-color: white; border: none; }
            QScrollBar:vertical {
                background: #BBDEFB;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #42A5F5;
                min-height: 24px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        three_D_content = QWidget()
        self.three_D_layers_layout = QVBoxLayout(three_D_content)
        self.three_D_layers_layout.setAlignment(Qt.AlignTop)
        self.three_D_layers_layout.setSpacing(6)
        self.three_D_layers_layout.addStretch()  # Push items to top
        
        three_D_scroll.setWidget(three_D_content)
        three_D_layout.addWidget(three_D_scroll)
# ---------------------------------------------------------------------------
        # Worksheets Section
        # ---------------------------------------------------------------------------
        self.worksheets_frame = QFrame()
        self.worksheets_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.worksheets_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.worksheets_frame.setStyleSheet("""
            QFrame { 
                border: 2px solid #9C27B0; 
                border-radius: 10px; 
                background-color: #F3E5F5; 
                margin: 5px;
            }
        """)
        worksheets_layout = QVBoxLayout(self.worksheets_frame)
        worksheets_layout.setContentsMargins(5, 5, 5, 5)
        worksheets_layout.setSpacing(4)
        self.worksheets_frame.setVisible(True)

        worksheets_title = QLabel("Worksheets")
        worksheets_title.setAlignment(Qt.AlignCenter)
        worksheets_title.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            padding: 8px; 
            background-color: #E1BEE7; 
            border-radius: 6px;
            color: #6A1B9A;
            border: none;
        """)
        worksheets_layout.addWidget(worksheets_title)

        self.add_worksheet_btn = QPushButton("+ Add")
        self.add_worksheet_btn.setStyleSheet("""
            QPushButton {
                background-color: white; 
                border: 1px solid #9C27B0; 
                border-radius: 5px; 
                padding: 2px 8px;
                color: #6A1B9A;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #F3E5F5; }
        """)
        self.add_worksheet_btn.setCursor(Qt.PointingHandCursor)
        add_button_row = QHBoxLayout()
        add_button_row.addStretch()
        add_button_row.addWidget(self.add_worksheet_btn)
        worksheets_layout.addLayout(add_button_row)

        worksheets_scroll = QScrollArea()
        worksheets_scroll.setWidgetResizable(True)
        worksheets_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        worksheets_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        worksheets_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        worksheets_scroll.setMinimumHeight(0)
        worksheets_scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: #F3E5F5; 
            }
            QScrollBar:vertical {
                background: #E1BEE7;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #9C27B0;
                min-height: 24px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QWidget#WorksheetsContent { background-color: #F3E5F5; }
            QCheckBox { padding: 2px; font-size: 13px; }
        """)

        worksheets_content = QWidget()
        worksheets_content.setObjectName("WorksheetsContent")
        worksheets_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.worksheets_inner_layout = QVBoxLayout(worksheets_content)
        self.worksheets_inner_layout.setContentsMargins(5, 5, 5, 5)
        self.worksheets_inner_layout.setSpacing(6)
        self.worksheets_inner_layout.setAlignment(Qt.AlignTop)

        worksheets_scroll.setWidget(worksheets_content)

        # Store reference to scroll area for dynamic height updates
        self.worksheets_scroll = worksheets_scroll
        self.worksheets_content = worksheets_content

        worksheets_layout.addWidget(worksheets_scroll)
        
        # --------------------------------------------------------------------------- 
        # 2D Layers Section
        # ---------------------------------------------------------------------------
        self.two_D_frame = QFrame()
        self.two_D_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.two_D_frame.setStyleSheet("""
            QFrame { 
                border: 2px solid #66BB6A; 
                border-radius: 10px; 
                background-color: #E8F5E9; 
                margin: 5px;
            }
        """)
        self.two_D_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        two_D_layout = QVBoxLayout(self.two_D_frame)
        self.two_D_frame.setVisible(False)

        two_D_title = QLabel("2D Layers")
        two_D_title.setAlignment(Qt.AlignCenter)
        two_D_title.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            padding: 8px; 
            background-color: #C8E6C9; 
            border-radius: 6px;
            color: #2E7D32;
        """)
        two_D_layout.addWidget(two_D_title)

        # Scroll area for 2D layers
        two_D_scroll = QScrollArea()
        two_D_scroll.setWidgetResizable(True)
        two_D_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        two_D_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        two_D_scroll.setMinimumHeight(0)
        two_D_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        two_D_scroll.setStyleSheet("""
            QScrollArea { background-color: white; border: none; }
            QScrollBar:vertical {
                background: #C8E6C9;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #66BB6A;
                min-height: 24px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        two_D_content = QWidget()
        two_D_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.two_D_layers_layout = QVBoxLayout(two_D_content)
        self.two_D_layers_layout.setAlignment(Qt.AlignTop)
        self.two_D_layers_layout.setSpacing(6)
        self.two_D_layers_layout.addStretch()
        
        two_D_scroll.setWidget(two_D_content)
        
        # Store references for dynamic height updates
        self.two_D_scroll = two_D_scroll
        self.two_D_content = two_D_content
        
        two_D_layout.addWidget(two_D_scroll)

# ======== Aniket Added on 02-05-2026: for the shows the Report section & hide 2D frame ===

        # ---------------------------------------------------------------------------
        # Report Section
        # ---------------------------------------------------------------------------
        self.report_frame = QFrame()
        self.report_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.report_frame.setStyleSheet("""
            QFrame { 
                border: 2px solid #FF9800; 
                border-radius: 10px; 
                background-color: #FFF3E0; 
                margin: 5px;
            }
        """)
        report_layout = QVBoxLayout(self.report_frame)
        self.report_frame.setVisible(False)

        report_title = QLabel("Report")
        report_title.setAlignment(Qt.AlignCenter)
        report_title.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            padding: 8px; 
            background-color: #FFE0B2; 
            border-radius: 6px;
            color: #E65100;
        """)
        report_layout.addWidget(report_title)

        # Scroll area for report content
        report_scroll = QScrollArea()
        report_scroll.setWidgetResizable(True)
        report_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        report_scroll.setStyleSheet("background-color: transparent; border: none;")
        
        report_content = QWidget()
        report_content.setStyleSheet("background-color: transparent;")
        self.report_layout = QVBoxLayout(report_content)
        self.report_layout.setAlignment(Qt.AlignTop)
        self.report_layout.setSpacing(6)
        
        # Placeholder text
        placeholder = QLabel("No reports generated yet.")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #757575; font-style: italic;")
        self.report_layout.addWidget(placeholder)
        
        self.report_layout.addStretch()
        
        report_scroll.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        report_scroll.setWidget(report_content)
        report_layout.addWidget(report_scroll)
        
        self.report_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        # Insert report frame just below the active worksheet (which is at index 1)
        # Give it a stretch factor of 1 so it expands to fill available space down to the Message button
        self.left_layout.insertWidget(2, self.report_frame, 1)

# ====================================== Aniket added =======================================
        # === ADD BOTH FRAMES TO LEFT PANEL ===
        self.checkboxes = self.add_layers_content()
        self.left_layout.addWidget(self.checkboxes)
        self.left_layout.addWidget(merger_frame)
        # self.left_layout.addWidget(self.three_D_frame)
        self.left_layout.addWidget(self.worksheets_frame)
        self.left_layout.addWidget(self.two_D_frame)
        self.left_layout.addWidget(self.three_D_frame)
        self.checkboxes.setVisible(False)

        # Optional: Add stretch at bottom so layers stay at top
        self.left_layout.addStretch()

        # --------------------------------------------------------------------
        # Point Cloud File Section
        # --------------------------------------------------------------------
        self.pc_file_group = QFrame()
        self.pc_file_group.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #333333;
                border-radius: 8px;
                margin: 5px 10px;
            }
        """)
        pc_layout = QVBoxLayout(self.pc_file_group)
        pc_layout.setContentsMargins(15, 15, 15, 15)
        pc_layout.setSpacing(15)

        pc_title = QLabel("Point Cloud File")
        pc_title.setAlignment(Qt.AlignCenter)
        pc_title.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #000000;
                border: none;
                background: transparent;
                margin: 0px;
            }
        """)
        pc_layout.addWidget(pc_title)

        file_name_layout = QHBoxLayout()
        file_name_layout.setSpacing(5)
        
        file_name_label = QLabel("File Name:")
        file_name_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333333;
                border: none;
                background: transparent;
                margin: 0px;
            }
        """)
        
        self.pc_file_display = QLabel("Road Design.ply")
        self.pc_file_display.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333333;
                border: none;
                border-bottom: 1px solid #777777;
                border-radius: 0px;
                background: transparent;
                padding-bottom: 2px;
                margin: 0px;
            }
        """)
        self.pc_file_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Pencil edit icon button – opens the file browser
        _pencil_svg = b'''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#555555" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
</svg>'''
        def _make_pencil_icon():
            pix = QPixmap(24, 24)
            pix.fill(Qt.transparent)
            try:
                rdr = QSvgRenderer(QByteArray(_pencil_svg))
                p = QPainter(pix)
                p.setRenderHint(QPainter.Antialiasing)
                rdr.render(p)
                p.end()
            except Exception:
                pass
            return QIcon(pix)

        self.pc_edit_btn = QPushButton("")
        self.pc_edit_btn.setIcon(_make_pencil_icon())
        self.pc_edit_btn.setIconSize(QSize(16, 16))
        self.pc_edit_btn.setFixedSize(26, 26)
        self.pc_edit_btn.setToolTip("Browse & update point cloud file")
        self.pc_edit_btn.setCursor(Qt.PointingHandCursor)
        self.pc_edit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #aaaaaa;
                border-radius: 5px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #e8f0fe;
                border-color: #3f51b5;
            }
            QPushButton:pressed {
                background-color: #c5cae9;
            }
        """)
        self.pc_edit_btn.clicked.connect(self.handle_point_cloud_update)

        file_name_layout.addWidget(file_name_label)
        file_name_layout.addWidget(self.pc_file_display)
        file_name_layout.addWidget(self.pc_edit_btn)
        
        pc_layout.addLayout(file_name_layout)
        
        self.left_layout.addWidget(self.pc_file_group)
        self.pc_file_group.setVisible(False)


        # ==================== MESSAGE SECTION (COLLAPSIBLE) ====================
        self.message_button = QPushButton("Message")
        self.message_button.setStyleSheet("""
            QPushButton { 
                background-color: #FF8A65; 
                color: white; 
                border: none; 
                padding: 8px;
                border-radius: 5px; 
                font-weight: bold; 
                font-size: 12px; 
                Margin-left: 5px;   
                Margin-right: 5px;
            }
            QPushButton:hover { background-color: #FFCCBC; }
        """)
        self.message_button.clicked.connect(self.toggle_message_section)
        self.left_layout.addWidget(self.message_button)
        
        self.message_section = QFrame()
        self.message_section.setVisible(False)
        self.message_section.setStyleSheet("""
            QFrame { 
                border: 2px solid #FF5722; 
                border-radius: 8px; 
                background-color: #FFF3E0; 
                margin: 5px 10px; 
            }
        """)
        msg_layout = QVBoxLayout(self.message_section)
        msg_title = QLabel("Terminal Output / Errors")
        msg_title.setStyleSheet("font-weight: bold; color: #D84315; padding: 5px;")
        msg_layout.addWidget(msg_title)
        
        self.message_text = QTextEdit()
        self.message_text.setReadOnly(True)
        self.message_text.setStyleSheet("""
            QTextEdit { 
                background-color: #FFF8E1; 
                border: 1px solid #FF8A65; 
                border-radius: 5px;
                font-family: Consolas, monospace; 
                font-size: 11px; 
                padding: 5px; 
            }
        """)
        self.message_text.setMinimumHeight(150)
        msg_layout.addWidget(self.message_text)
        self.left_layout.addWidget(self.message_section)

        # Reset buttons container
        self.reset_buttons_container = QWidget()
        self.reset_buttons_layout = QHBoxLayout(self.reset_buttons_container)
        self.reset_buttons_layout.setSpacing(10)
        ##### Mayur Wakhare 30-06-2026 Reset camera button add
        self.reset_action_button = QPushButton("Reset")
        self.reset_all_button = QPushButton("Reset_All")
        
        self.reset_buttons_layout.addWidget(self.reset_action_button)
        self.reset_buttons_layout.addWidget(self.reset_all_button)
        
        self.left_layout.addWidget(self.reset_buttons_container)
#################################################################
        # Store left_section reference — it will be reparented to central_widget as an overlay
        # after central_widget is created (further below in initUI).
        self.left_section = left_section
        self._left_panel_open = False  # overlay starts CLOSED
        self._left_panel_user_hidden = True  # treat as user-hidden initially

        # Floating toggle tab — will be reparented to central_widget below
        # Circular blue gradient arrow toggle button (matches reference image)
        _arrow_open_svg = b'''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 56 56">
  <defs>
    <radialGradient id="bg" cx="40%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#64B5F6"/>
      <stop offset="60%" stop-color="#1E88E5"/>
      <stop offset="100%" stop-color="#0D47A1"/>
    </radialGradient>
  </defs>
  <circle cx="28" cy="28" r="27" fill="url(#bg)" stroke="#1565C0" stroke-width="1.5"/>
  <polyline points="24,14 38,28 24,42" fill="none" stroke="white"
            stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''
        _arrow_close_svg = b'''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 56 56">
  <defs>
    <radialGradient id="bg2" cx="40%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#64B5F6"/>
      <stop offset="60%" stop-color="#1E88E5"/>
      <stop offset="100%" stop-color="#0D47A1"/>
    </radialGradient>
  </defs>
  <circle cx="28" cy="28" r="27" fill="url(#bg2)" stroke="#1565C0" stroke-width="1.5"/>
  <polyline points="32,14 18,28 32,42" fill="none" stroke="white"
            stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

        def _make_arrow_icon(svg_bytes):
            pix = QPixmap(32, 32)
            pix.fill(Qt.transparent)
            try:
                rdr = QSvgRenderer(QByteArray(svg_bytes))
                p = QPainter(pix)
                p.setRenderHint(QPainter.Antialiasing)
                rdr.render(p)
                p.end()
            except Exception:
                pass
            return QIcon(pix), pix

        self._icon_open,  self._pix_open  = _make_arrow_icon(_arrow_open_svg)
        self._icon_close, self._pix_close = _make_arrow_icon(_arrow_close_svg)

        self.left_toggle_btn = QPushButton("", self)
        self.left_toggle_btn.setFixedSize(32, 32)
        self.left_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.left_toggle_btn.setToolTip("Open Assets Panel")
        self.left_toggle_btn.setFlat(True)
        self.left_toggle_btn.setAttribute(Qt.WA_TranslucentBackground, True)
        self.left_toggle_btn.setAutoFillBackground(False)
        self.left_toggle_btn.setIcon(self._icon_open)
        self.left_toggle_btn.setIconSize(QSize(32, 32))
        self.left_toggle_btn.setMask(QRegion(0, 0, 32, 32, QRegion.Ellipse))
        self.left_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover  { background-color: transparent; }
            QPushButton:pressed { background-color: transparent; }
        """)

        def toggle_left_panel():
            if self._left_panel_open:
                self._close_left_panel()
            else:
                self._open_left_panel()

        self.left_toggle_btn.clicked.connect(toggle_left_panel)
        # NOTE: Do NOT add left_section or left_toggle_btn to body_layout here.
        # They are reparented to central_widget as overlays after central_widget is created.

        # ------------------------------------------------------------------
        # RIGHT SECTION (Visualization + Controls) - NOW SCROLLABLE
        # ------------------------------------------------------------------
        # Create the main container widget
        self.right_section = QWidget()
        right_layout = QVBoxLayout(self.right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(2)  # Small spacing between sections
        self.right_section.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QFrame { 
                margin: 3px;
            }
        """)

        # Create a scroll area for the right section
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.right_section)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Style the scroll area
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
                margin: 0px;
                padding: 0px;
            }
            QScrollBar:vertical {
                border: 1px solid #cccccc;
                background: #f0f0f0;
                width: 14px;
                margin: 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #a0a0a0;
                min-height: 30px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background: #808080;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)

        # Make sure the right_section has a minimum size to trigger scrolling
        self.right_section.setMinimumHeight(900) 

        # Store scroll_area as instance variable for event handling
        self.right_scroll_area = scroll_area

        # ------------------------------------------------------------------
        # MIDDLE SECTION – Visualization
        # ------------------------------------------------------------------
        middle_section = QFrame()
        middle_section.setObjectName("MiddleSection")
        middle_section.setFrameStyle(QFrame.Box | QFrame.Raised)
        middle_section.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        )
        middle_section.setStyleSheet("""
            #MiddleSection {
                border: 3px solid #BA68C8;
                border-radius: 10px;
                background-color: #ffffff;
            }
        """)
        middle_layout = QVBoxLayout(middle_section)
        middle_layout.setContentsMargins(2, 2, 2, 2)

        # Middle content stack (Viewer vs Start Page)
        self.middle_stack = QStackedWidget(middle_section)
        middle_layout.addWidget(self.middle_stack)
        
        # 1. VTK Viewer Section
        self.vtk_container = QWidget()
        vtk_container_layout = QVBoxLayout(self.vtk_container)
        vtk_container_layout.setContentsMargins(0, 0, 0, 0)
        self.vtk_container.setStyleSheet("background-color: #ffffff; border: none;")
        
        self.vtk_widget = QVTKRenderWindowInteractor(self.vtk_container)
        self.vtk_widget.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        )
        self.vtk_widget.setMinimumHeight(380)
        self.vtk_widget.installEventFilter(self)
        self.vtk_widget.setStyleSheet("background-color: #ffffff; border: none;")
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(1, 1, 1)  # white background
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        vtk_container_layout.addWidget(self.vtk_widget)

        # --- Simulation Stage Floating Label ---
        self.sim_stage_label = QLabel(self.vtk_container)
        self.sim_stage_label.setObjectName("SimStageLabel")
        self.sim_stage_label.setAlignment(Qt.AlignCenter)
        self.sim_stage_label.setVisible(False)
        self.sim_stage_label.setStyleSheet("""
            #SimStageLabel {
                background-color: rgba(26, 35, 126, 0.85);
                color: #ffffff;
                font-weight: bold;
                font-size: 18px;
                padding: 12px 25px;
                border-radius: 15px;
                border: 2px solid #3f51b5;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
            }
        """)
        # We will position it dynamically in resizeEvent or just use fixed top-center
        self.sim_stage_label.setFixedHeight(50)
        # --- Floating 3D Button (top-right of VTK viewer) ---
        # Draw an isometric cube as SVG and render it into a QIcon so the button looks 3D
        cube_svg = r'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
          <defs>
            <linearGradient id="g1" x1="0" x2="1" y1="0" y2="1">
              <stop offset="0%" stop-color="#4FC3F7"/>
              <stop offset="100%" stop-color="#0288D1"/>
            </linearGradient>
            <linearGradient id="g2" x1="0" x2="1" y1="0" y2="1">
              <stop offset="0%" stop-color="#81D4FA"/>
              <stop offset="100%" stop-color="#039BE5"/>
            </linearGradient>
          </defs>
          <!-- left face -->
          <polygon points="32,6 6,20 6,44 32,58 32,6" fill="url(#g2)" stroke="#01579B" stroke-width="1"/>
          <!-- right face -->
          <polygon points="32,6 58,20 58,44 32,58 32,6" fill="url(#g1)" stroke="#013A63" stroke-width="1"/>
          <!-- top face -->
          <polygon points="32,6 6,20 32,34 58,20 32,6" fill="#B3E5FC" stroke="#0277BD" stroke-width="1"/>
        </svg>
        '''

        # Render SVG to QPixmap and set as icon
        pix = QPixmap(64, 64)
        pix.fill(Qt.transparent)
        try:
            renderer = QSvgRenderer(bytearray(cube_svg, 'utf-8'))
            painter = QPainter(pix)
            renderer.render(painter)
            painter.end()
            icon = QIcon(pix)
        except Exception:
            icon = QIcon()

        self.threeD_button = QPushButton("", self)
        self.threeD_button.setObjectName("ThreeDButton")
        self.threeD_button.setToolTip("Lock 360 Rotation")
        self.threeD_button.setCheckable(True)
        self.threeD_button.setFlat(True)
        self.threeD_button.setAutoDefault(False)
        self.threeD_button.setDefault(False)
        self.threeD_button.setAutoFillBackground(False)
        self.threeD_button.setAttribute(Qt.WA_TranslucentBackground, True)
        self.threeD_button.setFixedSize(64, 64)
        self.threeD_button.setCursor(Qt.PointingHandCursor)
        self.threeD_button.setIcon(icon)
        self.threeD_button.setIconSize(QSize(48, 48))
        self.threeD_button.setStyleSheet("""
            #ThreeDButton {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                outline: none;
            }
            #ThreeDButton:hover {
                background-color: transparent;
            }
            #ThreeDButton:pressed {
                background-color: transparent;
            }
            #ThreeDButton:checked {
                background-color: transparent;
                border: none;
            }
            #ThreeDButton:checked:hover {
                background-color: transparent;
            }
            #ThreeDButton:checked:pressed {
                background-color: transparent;
            }
        """)
        self.threeD_button.setMask(pix.mask())
        self.threeD_button.clicked.connect(self.on_3d_button_clicked)
        # Hidden until point cloud / viewer is active (shown in show_viewer)
        self.threeD_button.setVisible(False)
        self.threeD_button.raise_()

    # ======= Aniket Added on 08-05-2026: for set the camera view ======
        # Floating camera shortcut button below the 3D control
        camera_svg = r'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
          <rect x="11" y="20" width="42" height="29" rx="7" ry="7" fill="none" stroke="#FFFFFF" stroke-width="4"/>
          <rect x="20" y="14" width="12" height="7" rx="2" ry="2" fill="#FFFFFF"/>
          <circle cx="32" cy="34" r="9" fill="none" stroke="#FFFFFF" stroke-width="4"/>
          <circle cx="45" cy="26" r="2.4" fill="#FFFFFF"/>
        </svg>
        '''

        camera_pix = QPixmap(64, 64)
        camera_pix.fill(Qt.transparent)
        try:
            camera_renderer = QSvgRenderer(bytearray(camera_svg, 'utf-8'))
            camera_painter = QPainter(camera_pix)
            camera_renderer.render(camera_painter)
            camera_painter.end()
            camera_icon = QIcon(camera_pix)
        except Exception:
            camera_icon = QIcon()

        self.camera_floating_button = QPushButton("", self)
        self.camera_floating_button.setObjectName("FloatingCameraButton")
        self.camera_floating_button.setToolTip("Reset Camera View")
        self.camera_floating_button.setCursor(Qt.PointingHandCursor)
        self.camera_floating_button.setFlat(True)
        self.camera_floating_button.setAutoFillBackground(False)
        self.camera_floating_button.setAttribute(Qt.WA_TranslucentBackground, True)
        self.camera_floating_button.setFixedSize(58, 58)
        self.camera_floating_button.setIcon(camera_icon)
        self.camera_floating_button.setIconSize(QSize(32, 32))
        self.camera_floating_button.setMask(QRegion(0, 0, 58, 58, QRegion.Ellipse))
        self.camera_floating_button.setStyleSheet("""
            #FloatingCameraButton {
                background-color: #4A148C;
                border: 2px solid rgba(255, 255, 255, 215);
                border-radius: 29px;
                padding: 0px;
            }
            #FloatingCameraButton:hover {
                background-color: #6A1B9A;
                border: 2px solid rgba(255, 255, 255, 245);
            }
            #FloatingCameraButton:pressed {
                background-color: #311B92;
                border: 2px solid rgba(255, 255, 255, 210);
            }
        """)
        self.camera_floating_button.clicked.connect(self.on_floating_camera_button_clicked)
        # Hidden until point cloud / viewer is active (shown in show_viewer)
        self.camera_floating_button.setVisible(False)
        self.camera_floating_button.raise_()

    # ======= Tunnel Camera View floating button =======
        # Floating tunnel camera button below the camera shortcut button
        tunnel_cam_svg = r'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
          <!-- tunnel arch -->
          <path d="M10,52 L10,28 A22,22 0 0,1 54,28 L54,52"
                fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>
          <!-- road lines -->
          <line x1="22" y1="52" x2="22" y2="36" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="4,3"/>
          <line x1="42" y1="52" x2="42" y2="36" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="4,3"/>
          <!-- road base -->
          <line x1="6" y1="52" x2="58" y2="52" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
        </svg>
        '''

        tunnel_cam_pix = QPixmap(64, 64)
        tunnel_cam_pix.fill(Qt.transparent)
        try:
            tunnel_cam_renderer = QSvgRenderer(bytearray(tunnel_cam_svg, 'utf-8'))
            tunnel_cam_painter = QPainter(tunnel_cam_pix)
            tunnel_cam_renderer.render(tunnel_cam_painter)
            tunnel_cam_painter.end()
            tunnel_cam_icon = QIcon(tunnel_cam_pix)
        except Exception:
            tunnel_cam_icon = QIcon()

        self.tunnel_camera_button = QPushButton("", self)
        self.tunnel_camera_button.setObjectName("FloatingTunnelCameraButton")
        self.tunnel_camera_button.setToolTip("Tunnel Camera View")
        self.tunnel_camera_button.setCursor(Qt.PointingHandCursor)
        self.tunnel_camera_button.setFlat(True)
        self.tunnel_camera_button.setAutoFillBackground(False)
        self.tunnel_camera_button.setAttribute(Qt.WA_TranslucentBackground, True)
        self.tunnel_camera_button.setFixedSize(58, 58)
        self.tunnel_camera_button.setIcon(tunnel_cam_icon)
        self.tunnel_camera_button.setIconSize(QSize(32, 32))
        self.tunnel_camera_button.setMask(QRegion(0, 0, 58, 58, QRegion.Ellipse))
        self.tunnel_camera_button.setStyleSheet("""
            #FloatingTunnelCameraButton {
                background-color: #00695C;
                border: 2px solid rgba(255, 255, 255, 215);
                border-radius: 29px;
                padding: 0px;
            }
            #FloatingTunnelCameraButton:hover {
                background-color: #00897B;
                border: 2px solid rgba(255, 255, 255, 245);
            }
            #FloatingTunnelCameraButton:pressed {
                background-color: #004D40;
                border: 2px solid rgba(255, 255, 255, 210);
            }
        """)
        self.tunnel_camera_button.clicked.connect(self.on_tunnel_camera_button_clicked)
        # Hidden until point cloud / viewer is active (shown in show_viewer)
        self.tunnel_camera_button.setVisible(False)
        self.tunnel_camera_button.raise_()
        ### Mayur Wakhare 13/7/2026 robot bar button right side tunnel underpass
        # ======= Underpass Camera View floating button =======
        underpass_cam_svg = r'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
          <!-- underpass box -->
          <rect x="10" y="24" width="44" height="28" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>
          <line x1="10" y1="24" x2="54" y2="24" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round"/>
          <!-- road lines -->
          <line x1="22" y1="52" x2="22" y2="36" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="4,3"/>
          <line x1="42" y1="52" x2="42" y2="36" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="4,3"/>
          <!-- road base -->
          <line x1="6" y1="52" x2="58" y2="52" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
        </svg>
        '''

        underpass_cam_pix = QPixmap(64, 64)
        underpass_cam_pix.fill(Qt.transparent)
        try:
            underpass_cam_renderer = QSvgRenderer(bytearray(underpass_cam_svg, 'utf-8'))
            underpass_cam_painter = QPainter(underpass_cam_pix)
            underpass_cam_renderer.render(underpass_cam_painter)
            underpass_cam_painter.end()
            underpass_cam_icon = QIcon(underpass_cam_pix)
        except Exception:
            underpass_cam_icon = QIcon()

        self.underpass_camera_button = QPushButton("", self)
        self.underpass_camera_button.setObjectName("FloatingUnderpassCameraButton")
        self.underpass_camera_button.setToolTip("Underpass Camera View")
        self.underpass_camera_button.setCursor(Qt.PointingHandCursor)
        self.underpass_camera_button.setFlat(True)
        self.underpass_camera_button.setAutoFillBackground(False)
        self.underpass_camera_button.setAttribute(Qt.WA_TranslucentBackground, True)
        self.underpass_camera_button.setFixedSize(58, 58)
        self.underpass_camera_button.setIcon(underpass_cam_icon)
        self.underpass_camera_button.setIconSize(QSize(32, 32))
        self.underpass_camera_button.setMask(QRegion(0, 0, 58, 58, QRegion.Ellipse))
        self.underpass_camera_button.setStyleSheet("""
            #FloatingUnderpassCameraButton {
                background-color: #00695C;
                border: 2px solid rgba(255, 255, 255, 215);
                border-radius: 29px;
                padding: 0px;
            }
            #FloatingUnderpassCameraButton:hover {
                background-color: #00897B;
                border: 2px solid rgba(255, 255, 255, 245);
            }
            #FloatingUnderpassCameraButton:pressed {
                background-color: #004D40;
                border: 2px solid rgba(255, 255, 255, 210);
            }
        """)
        self.underpass_camera_button.clicked.connect(self.on_underpass_camera_button_clicked)
        self.underpass_camera_button.setVisible(False)
        self.underpass_camera_button.raise_()
        ##############################################################################################
        ## Mayur Wakhare 10-6-2026 robot button (reset,.....)
        print(f"""
DEBUG INFO:
Camera button:
- objectName: {self.camera_floating_button.objectName()}
- className: {self.camera_floating_button.__class__.__name__}
- geometry: {self.camera_floating_button.geometry()}

Tunnel Camera View button:
- objectName: {self.tunnel_camera_button.objectName()}
- className: {self.tunnel_camera_button.__class__.__name__}
- geometry: {self.tunnel_camera_button.geometry()}
""")
###########################################################################################################
######## Mayur Wakhare 10-6-2026 robot button (reset,.....)

        # ======= Tunnel Right-Side Floating Control Bar =======
        self.tunnel_control_bar = QWidget(self)
        self.tunnel_control_bar.setObjectName("TunnelControlBar")
        self.tunnel_control_bar.setVisible(False)
        self.tunnel_control_bar.setAttribute(Qt.WA_TranslucentBackground, True)
        self.tunnel_control_bar.setFixedSize(128, 128)
        self.tunnel_control_bar.setStyleSheet("""
            QWidget#TunnelControlBar {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 64px;
                border: 1px solid rgba(255, 255, 255, 50);
            }
            QPushButton {
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 22px;
                min-width: 44px;
                max-width: 44px;
                min-height: 44px;
                max-height: 44px;
                margin: 0px;
            }
        """)

        try:
            from PyQt5.QtWidgets import QGraphicsDropShadowEffect
            from PyQt5.QtGui import QColor
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 150))
            shadow.setOffset(0, 4)
            self.tunnel_control_bar.setGraphicsEffect(shadow)
        except ImportError:
            pass

        from PyQt5.QtWidgets import QGridLayout
        tcb_layout = QGridLayout(self.tunnel_control_bar)
        tcb_layout.setContentsMargins(15, 15, 15, 15)
        tcb_layout.setSpacing(10)

        self.tc_play_btn = QPushButton("▶")
        self.tc_play_btn.setCheckable(True)
        self.tc_play_btn.setChecked(False)
        self.tc_play_btn.setCursor(Qt.PointingHandCursor)
        self.tc_play_btn.setToolTip("Auto")
        self.tc_play_btn.setStyleSheet("""
            QPushButton { background: rgba(76, 175, 80, 150); border: 1px solid rgba(76, 175, 80, 200); }
            QPushButton:hover { background: rgba(76, 175, 80, 200); border: 1px solid #4CAF50; }
            QPushButton:checked { background: rgba(76, 175, 80, 255); border: 2px solid white; }
        """)
        
        self.tc_stop_btn = QPushButton("⏹")
        self.tc_stop_btn.setCursor(Qt.PointingHandCursor)
        self.tc_stop_btn.setToolTip("Stop")
        self.tc_stop_btn.setStyleSheet("""
            QPushButton { background: rgba(244, 67, 54, 150); border: 1px solid rgba(244, 67, 54, 200); }
            QPushButton:hover { background: rgba(244, 67, 54, 200); border: 1px solid #F44336; }
            QPushButton:pressed { background: rgba(244, 67, 54, 255); }
        """)
        
        self.tc_reset_btn = QPushButton("↻")
        self.tc_reset_btn.setCursor(Qt.PointingHandCursor)
        self.tc_reset_btn.setToolTip("Reset")
        self.tc_reset_btn.setStyleSheet("""
            QPushButton { background: rgba(255, 152, 0, 150); border: 1px solid rgba(255, 152, 0, 200); }
            QPushButton:hover { background: rgba(255, 152, 0, 200); border: 1px solid #FF9800; }
            QPushButton:pressed { background: rgba(255, 152, 0, 255); }
        """)
        
        self.tc_reset_view_btn = QPushButton("🎯")
        self.tc_reset_view_btn.setCursor(Qt.PointingHandCursor)
        self.tc_reset_view_btn.setToolTip("Reset View Direction")
        self.tc_reset_view_btn.setStyleSheet("""
            QPushButton { background: rgba(33, 150, 243, 150); border: 1px solid rgba(33, 150, 243, 200); }
            QPushButton:hover { background: rgba(33, 150, 243, 200); border: 1px solid #2196F3; }
            QPushButton:pressed { background: rgba(33, 150, 243, 255); }
        """)

        tcb_layout.addWidget(self.tc_play_btn, 0, 0)
        tcb_layout.addWidget(self.tc_stop_btn, 0, 1)
        tcb_layout.addWidget(self.tc_reset_btn, 1, 0)
        tcb_layout.addWidget(self.tc_reset_view_btn, 1, 1)
######################################################################################################
########### Mayur Wakhare 1-7-2026 Camera Control
        self.tc_play_btn.clicked.connect(self._toggle_tunnel_auto)
        ######################################################
        self.tc_stop_btn.clicked.connect(self._on_tunnel_stop_clicked)
        self.tc_reset_btn.clicked.connect(self._reset_tunnel_camera)
        ##### Mayur Wakhare 1-7-2026 Camera
        self.tc_reset_view_btn.clicked.connect(self._tunnel_reset_view_direction)
###########################################################################

    # ======= Aniket Added on 08-05-2026: Three view shortcut buttons (TOP / LEFT / Right) =======
        # Distinct gradient styles for the three view buttons with a black circular border
        _view_btn_style = """
            QPushButton {{
                background-color: {bg};
                background-image: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 {start}, stop:1 {end});
                color: white;
                border: 2px solid #000000;
                border-radius: {r}px;
                font-size: 11px;
                font-weight: bold;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-image: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 {hover_start}, stop:1 {hover_end});
            }}
            QPushButton:pressed {{
                background-image: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 {pressed_start}, stop:1 {pressed_end});
            }}
        """

        _btn_size  = 44   # diameter — tight circle around short text labels
        _btn_r     = _btn_size // 2

        # --- TOP view button ---
        self.view_top_button = QPushButton("TOP", self)
        self.view_top_button.setObjectName("ViewTopButton")
        self.view_top_button.setToolTip("Set Top View")
        self.view_top_button.setCursor(Qt.PointingHandCursor)
        self.view_top_button.setFlat(True)
        self.view_top_button.setAttribute(Qt.WA_TranslucentBackground, True)
        self.view_top_button.setFixedSize(_btn_size, _btn_size)
        self.view_top_button.setMask(QRegion(0, 0, _btn_size, _btn_size, QRegion.Ellipse))
        self.view_top_button.setStyleSheet(_view_btn_style.format(
            bg="#1565C0",
            start="#42A5F5",
            end="#1565C0",
            hover_start="#64B5F6",
            hover_end="#1976D2",
            pressed_start="#0D47A1",
            pressed_end="#1565C0",
            r=_btn_r))
        self.view_top_button.clicked.connect(self.on_view_top_clicked)
        self.view_top_button.setVisible(False)
        self.view_top_button.raise_()

        # --- LEFT view button ---
        self.view_left_button = QPushButton("LEFT", self)
        self.view_left_button.setObjectName("ViewLeftButton")
        self.view_left_button.setToolTip("Set Left View")
        self.view_left_button.setCursor(Qt.PointingHandCursor)
        self.view_left_button.setFlat(True)
        self.view_left_button.setAttribute(Qt.WA_TranslucentBackground, True)
        self.view_left_button.setFixedSize(_btn_size, _btn_size)
        self.view_left_button.setMask(QRegion(0, 0, _btn_size, _btn_size, QRegion.Ellipse))
        self.view_left_button.setStyleSheet(_view_btn_style.format(
            bg="#2E7D32",
            start="#66BB6A",
            end="#2E7D32",
            hover_start="#81C784",
            hover_end="#388E3C",
            pressed_start="#1B5E20",
            pressed_end="#2E7D32",
            r=_btn_r))
        self.view_left_button.clicked.connect(self.on_view_left_clicked)
        self.view_left_button.setVisible(False)
        self.view_left_button.raise_()

        # --- RIGHT view button ---
        self.view_right_button = QPushButton("Right", self)
        self.view_right_button.setObjectName("ViewRightButton")
        self.view_right_button.setToolTip("Set Right View")
        self.view_right_button.setCursor(Qt.PointingHandCursor)
        self.view_right_button.setFlat(True)
        self.view_right_button.setAttribute(Qt.WA_TranslucentBackground, True)
        self.view_right_button.setFixedSize(_btn_size, _btn_size)
        self.view_right_button.setMask(QRegion(0, 0, _btn_size, _btn_size, QRegion.Ellipse))
        self.view_right_button.setStyleSheet(_view_btn_style.format(
            bg="#EF6C00",
            start="#FFB74D",
            end="#EF6C00",
            hover_start="#FFCC80",
            hover_end="#F57C00",
            pressed_start="#E65100",
            pressed_end="#EF6C00",
            r=_btn_r))
        self.view_right_button.clicked.connect(self.on_view_right_clicked)
        self.view_right_button.setVisible(False)
        self.view_right_button.raise_()

        # State flag — whether the three view buttons are currently shown
        self._view_buttons_open = False

        # Small status badge so users can instantly see whether rotation is locked or free
        self.rotation_state_badge = QLabel("UNLOCKED", self)
        self.rotation_state_badge.setObjectName("RotationStateBadge")
        self.rotation_state_badge.setAlignment(Qt.AlignCenter)
        self.rotation_state_badge.setFixedHeight(22)
        self.rotation_state_badge.setFixedWidth(88)
        self.rotation_state_badge.setStyleSheet("""
            #RotationStateBadge {
                background-color: #2E7D32;
                color: white;
                border: 1px solid #1B5E20;
                border-radius: 11px;
                padding-left: 6px;
                padding-right: 6px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        # Hidden until point cloud / viewer is active (shown in show_viewer)
        self.rotation_state_badge.setVisible(False)
        self.rotation_state_badge.raise_()
        QTimer.singleShot(0, self.update_3d_button_position)
        self.update_rotation_state_badge()
        
        # 2. Start Page Section
        self.start_page = StartPage(self)
        # Backward-compatible alias for existing code that still expects the old name.
        self.start_overlay = self.start_page
        
        # Add both to stack
        self.middle_stack.addWidget(self.vtk_container)
        self.middle_stack.addWidget(self.start_page)
        
        # Initially show start overlay
        self.show_start_screen()

        # ------------------------------------------------------------------
        # SCALE SECTION
        # ------------------------------------------------------------------
        scale_section = QFrame()
        scale_section.setFrameStyle(QFrame.Box | QFrame.Raised)
        scale_section.setStyleSheet("""
            QFrame {
                border: 2px solid #FF9800;
                border-radius: 10px;
                background-color: #FFF3E0;
            }
        """)
        scale_section.setFixedHeight(180)
        scale_layout = QVBoxLayout(scale_section)
        scale_layout.setContentsMargins(0, 0, 0, 0)

        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(0)
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.setTickInterval(5)
        self.volume_slider.setStyleSheet("""
            QSlider {
                padding-left: 16px;
                padding-right: 17px;
                margin: 2px 2px;
            }
            QSlider::groove:horizontal {
                border: none;
                height: 9px;
                background: #E0E0E0;
                border-radius: 3px;
                margin: 0px 0;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 2px solid #4CAF50;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #F1F8E9;
                border: 2px solid #2E7D32;
            }
        """)
        # self.volume_slider.valueChanged.connect(self.volume_changed)
        scale_layout.addWidget(self.volume_slider)

        # Scale figure
        self.scale_figure = Figure(dpi=100)
        self.scale_figure.set_size_inches(8, 1.2)
        self.scale_canvas = FigureCanvas(self.scale_figure)
        self.scale_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.scale_canvas.setMinimumHeight(120)
        self.scale_canvas.setMaximumHeight(140)

        # Initialize the scale axes
        self.scale_ax = self.scale_figure.add_subplot(111)
        self.scale_ax.set_xlim(0, self.total_distance)
        self.scale_ax.set_ylim(0, 1.2)
        self.scale_ax.set_facecolor('#FFF3E0')
        self.scale_ax.set_xlabel('Chainage', labelpad=3)
        self.scale_ax.set_ylabel('')
        self.scale_ax.set_yticks([])
        self.scale_ax.set_yticklabels([])

        # Create initial scale line and marker
        self.scale_line, = self.scale_ax.plot([0, self.total_distance], [0.5, 0.5], 
                                            color='black', linewidth=3)
        self.scale_marker, = self.scale_ax.plot([0, 0], [0, 1], color='red', 
                                            linewidth=2, linestyle='--')

        # Set initial ticks
        self.scale_ax.set_xticks([])
        self.scale_ax.set_xticklabels([])
        self.scale_ax.tick_params(axis='x', which='both', bottom=True, labelbottom=True, pad=5)
        self.scale_ax.grid(True, axis='x', linestyle='-', alpha=0.3)
        self.scale_ax.spines['top'].set_visible(False)
        self.scale_ax.spines['right'].set_visible(False)
        self.scale_ax.spines['left'].set_visible(False)

        # Adjust layout
        self.scale_figure.tight_layout(rect=[0, 0.1, 1, 0.95])
        self.scale_canvas.draw()
        self.scale_canvas.setMinimumWidth(2500) # Ensure wide enough to prevent tick overlap

        scale_scroll_area = QScrollArea()
        scale_scroll_area.setWidget(self.scale_canvas)
        scale_scroll_area.setWidgetResizable(True)
        scale_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scale_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scale_scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: rgba(209, 196, 233, 0.5); /* blend with purple background */
                height: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(94, 53, 177, 0.7); /* dark purple thumb */
                min-width: 40px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(94, 53, 177, 1.0);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
                height: 0px;
            }
        """)
        scale_layout.addWidget(scale_scroll_area)

        # HIDE THE SCALE SECTION INITIALLY
        scale_section.setVisible(False)
        self.scale_section = scale_section

        self.scale_section.installEventFilter(self)
        self.volume_slider.installEventFilter(self)
        self.scale_canvas.installEventFilter(self)

        # ------------------------------------------------------------------
        # BOTTOM SECTION – Controls
        # ------------------------------------------------------------------
        self.bottom_section = QFrame()
        self.bottom_section.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.bottom_section.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        )
        self.bottom_section.setStyleSheet("""
            QFrame {
                border: 3px solid #8F8F8F;
                border-radius: 10px;
                background-color: #8FBFEF;
            }
        """)
        self.bottom_section.setMinimumHeight(400)
        bottom_layout = QVBoxLayout(self.bottom_section)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        self.bottom_section.setVisible(False)  # Hide bottom section initially
        
        # ---------------------------------------------------------------------
        # Line Section (Collapsible)
        # ---------------------------------------------------------------------
        self.line_section = QFrame()
        self.line_section.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.line_section.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        )
        self.line_section.setStyleSheet("""
            QFrame {
                border: 3px solid #BA68C8;
                border-radius: 10px;
                background-color: #E6E6FA;
                margin: 0px;
                padding: 0px;
            }
        """)
        self.line_section.setMinimumWidth(100)
        self.line_section.setMaximumWidth(320)
        line_layout = QVBoxLayout(self.line_section)
        line_layout.setContentsMargins(5, 5, 5, 5)  # Remove margins
        line_layout.setSpacing(5)  # Remove spacing

        # Create a container for the top bar (header)
        self.header_container = QWidget()
        self.header_container.setFixedHeight(45)  # Fixed height for header
        header_layout = QHBoxLayout(self.header_container)
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(5)

        # Collapse button (left aligned)
        self.collapse_button = QPushButton("◀")
        self.collapse_button.setFixedSize(35, 35)
        self.collapse_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:pressed {
                background-color: #6A1B9A;
            }
        """)
        self.collapse_button.clicked.connect(self.toggle_line_section)
        self.collapse_button.setCursor(Qt.PointingHandCursor)
        self.collapse_button.setToolTip("Close Line Section")
        header_layout.addWidget(self.collapse_button)

        # Stretch to push undo/redo to right
        header_layout.addStretch()

        # Undo button
        self.undo_button = QPushButton()
        svg_data_left = QByteArray(self.svg_left)
        renderer_left = QSvgRenderer(svg_data_left)
        pixmap_left = QPixmap(30, 30)
        pixmap_left.fill(Qt.transparent)
        painter_left = QPainter(pixmap_left)
        renderer_left.render(painter_left, QRectF(0, 0, 24, 24))
        painter_left.end()
        self.undo_button.setIcon(QIcon(pixmap_left))
        self.undo_button.setIconSize(QSize(24, 24))
        self.undo_button.setFixedSize(35, 35)
        self.undo_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                stop:0 #6366f1, stop:1 #4f46e5);
                border: none;
                padding: 0px;
                margin: 0px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                stop:0 #4f46e5, stop:1 #4338ca);
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
        """)
        self.undo_button.setCursor(Qt.PointingHandCursor)
        self.undo_button.setToolTip("Undo")
        header_layout.addWidget(self.undo_button)

        # Redo button
        self.redo_button = QPushButton()
        svg_data_right = QByteArray(self.svg_right)
        renderer_right = QSvgRenderer(svg_data_right)
        pixmap_right = QPixmap(30, 30)
        pixmap_right.fill(Qt.transparent)
        painter_right = QPainter(pixmap_right)
        renderer_right.render(painter_right, QRectF(0, 0, 24, 24))
        painter_right.end()
        self.redo_button.setIcon(QIcon(pixmap_right))
        self.redo_button.setIconSize(QSize(24, 24))
        self.redo_button.setFixedSize(35, 35)
        self.redo_button.setStyleSheet(self.undo_button.styleSheet())
        self.redo_button.setCursor(Qt.PointingHandCursor)
        self.redo_button.setToolTip("Redo")
        header_layout.addWidget(self.redo_button)

        # Add header container to line layout
        line_layout.addWidget(self.header_container)

        # Create line_content_widget (the collapsible part)
        self.line_content_widget = QWidget()
        self.line_content_layout = QVBoxLayout(self.line_content_widget)
        self.line_content_layout.setContentsMargins(0, 5, 0, 0)
        self.line_content_layout.setSpacing(5)

        # Add line_content_widget to line layout
        line_layout.addWidget(self.line_content_widget)

        # Function to create checkbox rows
        def create_line_checkbox_with_pencil(checkbox_text, info_text, item_id, color_style=""):
            container = QWidget()
            container.setFixedWidth(290)
            container.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border: none;
                    margin: 1px;
                }
            """)
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 5, 5, 5)
            layout.setSpacing(5)
            
            checkbox = QCheckBox()
            checkbox.setFixedSize(35, 35)
            checkbox.setText("")
            checkbox.setObjectName(item_id)
            
            pencil_button = QPushButton()
            svg_data = QByteArray()
            svg_data.append(self.PENCIL_SVG)
            renderer = QSvgRenderer(svg_data)
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter, QRectF(pixmap.rect()))
            painter.end()
            icon = QIcon(pixmap)
            pencil_button.setIcon(icon)
            pencil_button.setIconSize(QSize(24, 24))
            pencil_button.setFixedSize(30, 30)
            pencil_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    border: none;
                    padding: 0px;
                    margin: 0px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
            pencil_button.setCursor(Qt.PointingHandCursor)
            
            text_label = QLabel(checkbox_text)
            text_label.setStyleSheet(f"""
                QLabel {{
                    background-color: transparent;
                    border: none;
                    padding: 0px;
                    font-weight: bold;
                    font-size: 16px;
                    color: #000000;
                    text-align: left;
                }}
            """)
            
            layout.addWidget(checkbox)
            layout.addWidget(text_label, 1)
            layout.addWidget(pencil_button)
            
            return container, checkbox, text_label, pencil_button

        # # Create checkbox rows
        # Zero Line
        self.zero_container, self.zero_line, zero_label, self.zero_pencil = create_line_checkbox_with_pencil(
            "Zero Line",
            "Shows the zero reference line for elevation measurements",
            'zero_line'
        )
        self.zero_line.setStyleSheet("""
            QCheckBox {
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.zero_container.setVisible(False)

        # Connect state change → change label text color to purple when checked
        self.zero_line.stateChanged.connect(lambda state: zero_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: purple;
            }
        """ if state == Qt.Checked else """
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: #000000;
            }
        """))
        # self.zero_line.stateChanged.connect(lambda state: self.on_checkbox_changed(state, 'zero'))
        # self.zero_pencil.clicked.connect(self.edit_zero_line)
        line_layout.addWidget(self.zero_container)

        # self.zero_container.setVisible(False)
 

        # Surface Line
        self.surface_container, self.surface_baseline, surface_label, self.surface_pencil = create_line_checkbox_with_pencil(
            "Surface Line",
            "Shows the ground surface baseline",
            'surface_line'
        )
        self.surface_baseline.setStyleSheet("""
            QCheckBox {
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.surface_container.setVisible(False)

        self.surface_baseline.stateChanged.connect(lambda state: surface_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: green;
            }
        """ if state == Qt.Checked else """
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: #000000;
            }
        """))

        line_layout.addWidget(self.surface_container)

        # Construction Line
        self.construction_container, self.construction_line, construction_label, self.construction_pencil = create_line_checkbox_with_pencil(
            "Construction Line",
            "Shows the construction reference line",
            'construction_line'
        )
        self.construction_line.setStyleSheet("""
            QCheckBox {
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.construction_container.setVisible(False)

        self.construction_line.stateChanged.connect(lambda state: construction_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: red;
            }
        """ if state == Qt.Checked else """
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: #000000;
            }
        """))

        line_layout.addWidget(self.construction_container)

        # Road Surface Line
        self.road_surface_container, self.road_surface_line, road_surface_label, self.road_pencil = create_line_checkbox_with_pencil(
            "Road Surface Line",
            "Shows the road surface elevation profile",
            'road_surface_line'
        )
        self.road_surface_line.setStyleSheet("""
            QCheckBox {
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.road_surface_container.setVisible(False)

        self.road_surface_line.stateChanged.connect(lambda state: road_surface_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: blue;
            }
        """ if state == Qt.Checked else """
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: #000000;
            }
        """))

        line_layout.addWidget(self.road_surface_container)

        # Bridge-specific Zero Line
        self.bridge_zero_container, self.bridge_zero_line, bridge_zero_label, self.bridge_zero_pencil = create_line_checkbox_with_pencil(
            "Zero Line",
            "Shows the bridge zero reference line for elevation measurements",
            'zero_line'
        )
        self.bridge_zero_line.setStyleSheet("""
            QCheckBox {
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.bridge_zero_container.setVisible(False)

        self.bridge_zero_line.stateChanged.connect(lambda state: bridge_zero_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: purple;
            }
        """ if state == Qt.Checked else """
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: #000000;
            }
        """))

        line_layout.addWidget(self.bridge_zero_container)

        # Projection Line
        self.projection_container, self.projection_line, projection_label, projection_pencil = create_line_checkbox_with_pencil(
            " Projection Line",
            "Shows the projection elevation profile",
            'projection_line'
        )
        self.projection_line.setStyleSheet("""
            QCheckBox {
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.projection_container.setVisible(False)

        self.projection_line.stateChanged.connect(lambda state: projection_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: green;
            }
        """ if state == Qt.Checked else """
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: #000000;
            }
        """))

        line_layout.addWidget(self.projection_container)

        # Construction Dots Line
        self.construction_dots_container, self.construction_dots_line, construction_dots_label, self.construction_dots_pencil = create_line_checkbox_with_pencil(
            "Construction Dots",
            "Shows the construction reference dots line",
            'construction_dots_line'
        )
        self.construction_dots_line.setStyleSheet("""
            QCheckBox {
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.construction_dots_container.setVisible(False)

        self.construction_dots_line.stateChanged.connect(lambda state: construction_dots_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: red;
            }
        """ if state == Qt.Checked else """
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: #000000;
            }
        """))

        line_layout.addWidget(self.construction_dots_container)

        # Deck Line
        self.deck_line_container, self.deck_line, deck_label, self.deck_pencil = create_line_checkbox_with_pencil(
            "Deck Line",
            "Shows the deck elevation profile",
            'deck_line'
        )
        self.deck_line.setStyleSheet("""
            QCheckBox {
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.deck_line_container.setVisible(False)

        self.deck_line.stateChanged.connect(lambda state: deck_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: blue;
            }
        """ if state == Qt.Checked else """
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                color: #000000;
            }
        """))

        line_layout.addWidget(self.deck_line_container)

# ================================================================================================================================== 

        # Additional buttons - "Add Material Line" (now always visible)
        self.add_material_line_button = QPushButton("Add Material Line")
        self.add_material_line_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;  /* Green */
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        # Button is now always visible from the start
        self.add_material_line_button.setVisible(True)

        line_layout.addWidget(self.add_material_line_button)

        # Aniket added 05-05-2026: Scrollable Material List Section (Prevents UI compression)
        self.material_scroll_area = QScrollArea()
        self.material_scroll_area.setWidgetResizable(True)
        self.material_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.material_scroll_area.setFrameShape(QFrame.NoFrame)
        self.material_scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F3E5F5;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #9C27B0;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        self.material_scroll_content = QWidget()
        self.material_scroll_content.setStyleSheet("background: transparent;")
        
        # Create the dedicated layout inside the scrollable content widget
        self.material_items_layout = QVBoxLayout(self.material_scroll_content)
        self.material_items_layout.setSpacing(8)
        self.material_items_layout.setContentsMargins(0, 10, 5, 10)
        self.material_items_layout.setAlignment(Qt.AlignTop)
        
        self.material_scroll_area.setWidget(self.material_scroll_content)
        
        # Add the scroll area to the main line_layout right after the button
        line_layout.addWidget(self.material_scroll_area, 1)

        # Removed stretch to allow scroll area to expand fully

        # Storage for material configurations and UI items
        self.material_configs = []   # list of dicts with material data
        self.material_items = []     # list of UI item dicts

        # Additional buttons
        self.preview_button = QPushButton("Curve")
        self.elivation_angle_button = QPushButton("Elevation Angle")

        # Angle buttons container
        self.angle_buttons_container = QWidget()
        self.angle_buttons_container.setFixedHeight(40)
        self.angle_buttons_layout = QHBoxLayout(self.angle_buttons_container)
        self.angle_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.angle_buttons_layout.setSpacing(5)
        
        # Set minimum heights for consistency
        self.preview_button.setFixedHeight(35)
        self.preview_button.setFixedWidth(80)
        
        self.elivation_angle_button.setFixedHeight(35)
        self.elivation_angle_button.setFixedWidth(160)

        self.angle_buttons_layout.addWidget(self.preview_button)
        self.angle_buttons_layout.addWidget(self.elivation_angle_button)
        
        self.angle_buttons_layout.addWidget(self.preview_button)
        self.angle_buttons_layout.addWidget(self.elivation_angle_button)

        self.threed_map_button = QPushButton("Map on 3D")
        self.save_button = QPushButton("Save")
        
        self.preview_button.setStyleSheet("""
            QPushButton {
                background-color: #808080;
                color: white;
                border: none;
                padding: 0px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #6E6E6E; }
            QPushButton:pressed { background-color: #5A5A5A; }
        """)

        self.elivation_angle_button.setStyleSheet("""
            QPushButton {
                background-color: #808080;
                color: white;
                border: none;
                padding: 0px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #6E6E6E; }
            QPushButton:pressed { background-color: #5A5A5A; }
        """)
        
        self.threed_map_button.setStyleSheet("""
            QPushButton {
                background-color: #008CBA;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #007bb5; }
            QPushButton:pressed { background-color: #006f9a; }
        """)
        
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #F57C00; }
            QPushButton:pressed { background-color: #EF6C00; }
        """)
        
        self.preview_button.setVisible(False)
        self.elivation_angle_button.setVisible(False)
        self.threed_map_button.setVisible(False)
        self.save_button.setVisible(False)
        
        line_layout.addWidget(self.angle_buttons_container)
        line_layout.addSpacing(8)
        line_layout.addWidget(self.threed_map_button)
        line_layout.addWidget(self.save_button)

        # Graph Canvas
        self.figure = Figure(dpi=100)
        base_width = max(self.total_distance / 3.0, 10)  # Minimum 10 inches
        self.figure.set_size_inches(base_width, 6)
        self.canvas = FigureCanvas(self.figure)

        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumWidth(800)  # Adjust as needed

        self.ax = self.figure.add_subplot(111)
        self.ax.grid(True, which='both', linestyle='-', linewidth=0.5, alpha=0.7)
        self.ax.set_xlim(0, self.total_distance)
        self.ax.set_ylim(-3, 3)

        # Set axis labels and title with proper padding
        self.ax.set_xlabel('Y (Distance)', fontsize=12, labelpad=10)  # Added labelpad
        self.ax.set_ylabel('Z (Elevation)', fontsize=12, labelpad=10)  # Added labelpad
        self.ax.set_title('Road Construction Layers', fontsize=12, fontweight='bold', color='#4A148C', pad=8)  # Added pad

        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

        # Adjust subplot parameters to minimize unused space around the graph
        self.figure.subplots_adjust(left=0.08, bottom=0.14, right=0.98, top=0.92)

        self.annotation = self.ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                                        bbox=dict(boxstyle="round,pad=0.5"), arrowprops=dict(arrowstyle="->"),
                                        ha='left', va='bottom')
        self.annotation.set_visible(False)

        self.canvas.draw()

        # ---------------------------------------------------------------------
        # Zoom Controls Toolbar - UPDATED WITH TOGGLE START/STOP BUTTON
        # ---------------------------------------------------------------------
        zoom_toolbar = QWidget()
        zoom_toolbar.setFixedHeight(40)
        zoom_toolbar.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                margin: 0px;
                padding: 0px;
            }
        """)

        zoom_layout = QHBoxLayout(zoom_toolbar)
        zoom_layout.setContentsMargins(8, 2, 8, 2)  # Reduced margins
        zoom_layout.setSpacing(5)  # Reduced spacing between controls

        # Zoom label
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("font-weight: bold; color: #333;")
        zoom_layout.addWidget(zoom_label)

        # Zoom out button
        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.setFixedWidth(30)
        self.zoom_out_button.setFixedHeight(30)
        self.zoom_out_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        zoom_layout.addWidget(self.zoom_out_button)

        # Zoom level display
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(60)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
            }
        """)
        zoom_layout.addWidget(self.zoom_label)

        # Zoom in button
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setFixedWidth(30)
        self.zoom_in_button.setFixedHeight(30)
        self.zoom_in_button.setStyleSheet(self.zoom_out_button.styleSheet())
        zoom_layout.addWidget(self.zoom_in_button)

        # Reset zoom button
        self.reset_zoom_button = QPushButton("Reset")
        self.reset_zoom_button.setFixedHeight(30)
        self.reset_zoom_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
                padding: 0 15px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        zoom_layout.addWidget(self.reset_zoom_button)

        # Simple slider
        zoom_layout.addWidget(QLabel("Scale:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 200)  # 10% to 200%
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickPosition(QSlider.NoTicks)
        self.zoom_slider.setFixedWidth(100)
        zoom_layout.addWidget(self.zoom_slider)

        # Pan controls
        zoom_layout.addWidget(QLabel("Pan:"))
        self.pan_left_button = QPushButton("◀")
        self.pan_left_button.setFixedWidth(30)
        self.pan_left_button.setFixedHeight(30)
        self.pan_left_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #388E3C; }
        """)
        zoom_layout.addWidget(self.pan_left_button)

        self.pan_right_button = QPushButton("▶")
        self.pan_right_button.setFixedWidth(30)
        self.pan_right_button.setFixedHeight(30)
        self.pan_right_button.setStyleSheet(self.pan_left_button.styleSheet())
        zoom_layout.addWidget(self.pan_right_button)

        self.pan_up_button = QPushButton("▲")
        self.pan_up_button.setFixedWidth(30)
        self.pan_up_button.setFixedHeight(30)
        self.pan_up_button.setStyleSheet(self.pan_left_button.styleSheet())
        zoom_layout.addWidget(self.pan_up_button)

        self.pan_down_button = QPushButton("▼")
        self.pan_down_button.setFixedWidth(30)
        self.pan_down_button.setFixedHeight(30)
        self.pan_down_button.setStyleSheet(self.pan_left_button.styleSheet())
        zoom_layout.addWidget(self.pan_down_button)

        # Auto-fit button
        self.autofit_button = QPushButton("Auto Fit")
        self.autofit_button.setFixedHeight(30)
        self.autofit_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
                padding: 0 15px;
            }
            QPushButton:hover { background-color: #7B1FA2; }
        """)
        zoom_layout.addWidget(self.autofit_button)

        # === NEW: Toggle Start / Stop Button ===
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.setFixedHeight(30)
        self.start_stop_button.setCheckable(True)  # Allows toggle state
        self.start_stop_button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
                padding: 0 15px;
            }
            QPushButton:checked {
                background-color: #D32F2F;  /* Red when "Stop" */
            }
            QPushButton:!checked {
                background-color: #4CAF50;  /* Purple when "Start" */
            }
            QPushButton:hover:checked {
                background-color: #B71C1C;
            }
            QPushButton:hover:!checked {
                background-color: #4CAF50;
            }
        """)
        # Optional: connect to your actual start/stop logic here
        # self.start_stop_button.clicked.connect(self.on_start_stop_clicked)
        zoom_layout.addWidget(self.start_stop_button)

        # Connect the toggle behavior to update text
        def on_start_stop_toggled(checked):
            if checked:
                self.start_stop_button.setText("Stop")
            else:
                self.start_stop_button.setText("Start")

        self.start_stop_button.toggled.connect(on_start_stop_toggled)

        # Add stretch to push everything left
        zoom_layout.addStretch()

        # Add zoom toolbar to the layout BEFORE the graph
        bottom_layout.addWidget(zoom_toolbar)

        # Create horizontal layout for line section and canvas
        content_layout_bottom = QHBoxLayout()
        content_layout_bottom.setContentsMargins(0, 0, 0, 0)
        content_layout_bottom.setSpacing(0)
        content_layout_bottom.addWidget(self.line_section)
        content_layout_bottom.addWidget(self.canvas, 4)
        bottom_layout.addLayout(content_layout_bottom, 1)
        bottom_layout.setAlignment(content_layout_bottom, Qt.AlignRight)

        # ------------------------------------------------------------------
        # HERARCHY SECTION – Controls
        # ------------------------------------------------------------------
        self.herarchy_section = QFrame()
        self.herarchy_section.setVisible(False)

        # Add middle, scale, and bottom sections to right layout
        right_layout.addWidget(middle_section, 3)  # 3 parts for visualization
        right_layout.addWidget(scale_section, 1)   # 1 part for scale
        right_layout.addWidget(self.bottom_section, 1)  # 1 part for controls
        right_layout.addWidget(self.herarchy_section, 1)  # 1 part for controls

        # Add right section to content layout
        content_layout.addWidget(scroll_area, 3)

        # --------------------------------
        # Measurement SECTION – Settings
        # ------------------------------------------------------------------
        self.main_measurement_section = QFrame()  # Changed here
        self.main_measurement_section.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.main_measurement_section.setStyleSheet("""
            QFrame { 
            background-color: #DCEDC8;      /* panel color */
            border: 1px solid black;      /* thin black border */
            border-radius: 6px;           /* rounded corners */
            background-color: #E8F5E9; 
            margin: 3px;
            }
        """)
        self.main_measurement_section.setMinimumWidth(300)
        self.main_measurement_section.setMaximumWidth(300)
        self.main_measurement_section.setVisible(False)

        self.main_measurement_layout = QVBoxLayout(self.main_measurement_section)
        # Remove margins and spacing to minimize empty space
        self.main_measurement_layout.setContentsMargins(5, 5, 5, 5) 
        self.main_measurement_layout.setSpacing(3)

        # Add measurement section to content_widget (right area only)
        content_layout.addWidget(self.main_measurement_section, 1)

        # Now assemble body_layout: left_section | toggle | content_widget(VTK)
        body_layout.addWidget(self.content_widget, 1)  # VTK area takes all remaining space

        # body_widget (left panel + VTK area together) goes into main_layout
        main_layout.addWidget(self.body_widget, 1)

        # Create central widget and set layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # ── Re-parent floating overlay buttons to central_widget ──────────────
        # These buttons were created earlier with `self` as a temporary parent
        # (central_widget didn't exist yet). Now that central_widget is set,
        # reparent them so mapTo(central_widget) works correctly in
        # update_3d_button_position() — same pattern as play_simulation_btn.
        for _overlay_widget in (
            self.threeD_button,
            self.camera_floating_button,
            self.tunnel_camera_button,
            ## Mayur Wakhare 13-7-2026
            self.underpass_camera_button,
            ## Mayur Wakhare 10-07-2026
            self.tunnel_control_bar,
            ##############################
            self.rotation_state_badge,
            self.view_top_button,
            self.view_left_button,
            self.view_right_button,
        ):
            _overlay_widget.setParent(central_widget)
            _overlay_widget.raise_()

        # ── Re-parent left_section and toggle button as overlay widgets ──────
        # left_section acts like an asset panel drawer: it overlays the VTK viewer
        # instead of pushing it aside. It starts hidden (closed).
        self.left_section.setParent(central_widget)
        self.left_section.setVisible(False)  # Closed initially
        self.left_section.raise_()

        self.left_toggle_btn.setParent(central_widget)
        self.left_toggle_btn.setVisible(False)  # Hidden until viewer is shown
        self.left_toggle_btn.raise_()

        # Keep floating VTK controls attached to the visible scroll viewport
        # so they remain on screen while the right panel scrolls.
        for _overlay_widget in (
            self.threeD_button,
            self.camera_floating_button,
            self.tunnel_camera_button,
            self.underpass_camera_button,
            #Mayur Wakhare 10-7-2026 ...robot control bartunnel
            self.tunnel_control_bar,
#########################################################################
            self.rotation_state_badge,
            self.view_top_button,
            self.view_left_button,
            self.view_right_button,
        ):
            _overlay_widget.setParent(self.right_scroll_area.viewport())
            _overlay_widget.raise_()

        # Position the overlay widgets once layout is computed
        QTimer.singleShot(50, self.update_left_panel_position)
        QTimer.singleShot(50, self.update_3d_button_position)

        # Setup zoom and pan controls
        self.setup_zoom_controls()

        # Initial zoom display
        self.update_zoom_display()

        self.setup_scroll_behavior()

        # Apply the default mode so the initial UI matches the active dropdown state.
        self.set_mode(self.app_mode)

    def show_how_to_earn_dialog(self, event=None):
        msg = QMessageBox(self)
        msg.setWindowTitle("How to Earn")
        msg.setIcon(QMessageBox.Information)
        
        info_text = (
            "<h3>Want to earn more? 🌟</h3>"
            "<p>Here are a few ways to increase your earnings:</p>"
            "<ul>"
            "<li><b>Upload Designs:</b> Share your high-quality pavement and infrastructure designs.</li>"
            "<li><b>Contribute Materials:</b> Add custom materials to the directory.</li>"
            "<li><b>Complete Worksheets:</b> Finish required worksheets accurately and efficiently.</li>"
            "<li><b>Collaborate:</b> Invite and assist your buddies.</li>"
            "</ul>"
            "<p><i>Keep building and watch your earnings grow!</i></p>"
        )
        msg.setText(info_text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QPushButton {
                background-color: #66bb6a;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
            }
        """)
        msg.exec_()

# ================ Aniket Added 19-05-2026: Expanding Road Dialog =====================
    def open_expanding_road_dialog(self, *args):
        if not getattr(self, "current_worksheet_name", None):
            QMessageBox.warning(self, "No Worksheet", "Please open a worksheet first.")
            return
        dialog = ExpandingRoadDialog(self)
        dialog.exec_()
        
# ###### Mayur Wakhare 05-06-2026 : Added "Under pass" button on Menu bar ############
#     def handle_under_pass_clicked(self):
#         """Open the Under Pass configuration dialog."""
#         dialog = UnderPassDialog(self)
#         if dialog.exec_() == QDialog.Accepted:
#             self.under_pass_values = dialog.under_pass_values
#             print(f"Under Pass values: {self.under_pass_values}")
            
#             # Open the preview dialog
#             preview_dialog = UnderPassPreviewDialog(self.under_pass_values, self)
#             preview_dialog.exec_()
# ##### Mayur Wakhare 14-7-2026 underpass lights button on menu bar ##################
#     def open_underpass_light_dialog(self, *args):
#         if not getattr(self, "current_worksheet_name", None):
#             QMessageBox.warning(self, "No Worksheet", "Please open a worksheet first.")
#             return
#         dialog = UnderpassLightDialog(self)
#         if dialog.exec_() == QDialog.Accepted:
#             data = dialog.get_data()
#             if data.get("verified") and data.get("light_mode") == "single":
#                 up = dialog.underpass_data.get(data.get("up_id"))
#                 if up and hasattr(self, '_place_single_underpass_light'):
#                     self._place_single_underpass_light(data, up)
                    
#                     if hasattr(self, 'vtk_widget') and self.vtk_widget:
#                         self.vtk_widget.GetRenderWindow().Render()
# ### Mayur Wakhare 15-07-2026 Underpass CCTV button on menu bar ##################
#     def open_underpass_cctv_dialog(self, *args):
#         if not getattr(self, "current_worksheet_name", None):
#             QMessageBox.warning(self, "No Worksheet", "Please open a worksheet first.")
#             return
#         dialog = UnderpassCCTVDialog(self)
#         if dialog.exec_() == QDialog.Accepted:
#             data = dialog.get_data()
#             if data.get("verified"):
#                 up = dialog.underpass_data.get(data.get("up_id"))
#                 if up and hasattr(self, '_place_underpass_cctv'):
#                     self._place_underpass_cctv(data, up)
                    
#                     if hasattr(self, 'vtk_widget') and self.vtk_widget:
#                         self.vtk_widget.GetRenderWindow().Render()

# #############################################################################
#     def place_under_pass(self, dimensions, placement_values):
#         from PyQt5.QtWidgets import QMessageBox
#         import os
#         import json
#         import math
#         import random

#         if not getattr(self, 'current_worksheet_name', None):
#             QMessageBox.warning(self, "No Worksheet", "Please load a worksheet first.")
#             return

#         design_layer = placement_values.get("design_layer")
#         if not design_layer:
#             QMessageBox.warning(self, "Error", "No Design Layer specified.")
#             return
        
#         # Load unified config
#         try:
#             from json_manager import DesignConstructionManager
#             subfolder = getattr(self, 'current_subfolder_type', 'designs')
#             designs_base = os.path.join(self.WORKSHEETS_BASE_DIR, self.current_worksheet_name, subfolder)
            
#             # Fast path: if current_design_layer_path matches, use it directly
#             active_path = getattr(self, 'current_design_layer_path', None)
#             if active_path and os.path.exists(active_path) and os.path.basename(active_path) == design_layer:
#                 layer_folder = active_path
#                 print(f"Design Layer resolved from active path: {layer_folder}")
#             else:
#                 layer_folder = os.path.join(designs_base, design_layer)
            
#             # If exact match not found, try partial match (e.g. user enters "D1", folder is "W1 - D1")
#             if not os.path.exists(layer_folder):
#                 matched_folder = None
#                 if os.path.isdir(designs_base):
#                     available_layers = [d for d in os.listdir(designs_base) if os.path.isdir(os.path.join(designs_base, d))]
#                     print(f"User entered: {design_layer}")
#                     print(f"Available layers:")
#                     for lyr in available_layers:
#                         print(f"  - {lyr}")
                    
#                     # Try suffix match: "W1 - D1" ends with "D1"
#                     for lyr in available_layers:
#                         if lyr.endswith(design_layer) or lyr.endswith(f"- {design_layer}") or lyr.endswith(f" {design_layer}"):
#                             matched_folder = lyr
#                             break
                    
#                     # Try contains match as fallback
#                     if not matched_folder:
#                         for lyr in available_layers:
#                             if design_layer in lyr:
#                                 matched_folder = lyr
#                                 break
                
#                 if matched_folder:
#                     print(f"Matched Design Layer: {matched_folder}")
#                     layer_folder = os.path.join(designs_base, matched_folder)
#                     design_layer = matched_folder
#                 else:
#                     QMessageBox.warning(self, "Error", f"Design Layer '{design_layer}' not found.\nAvailable: {', '.join(available_layers) if os.path.isdir(designs_base) else 'N/A'}")
#                     return

#             road_data = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'road_surface_baseline')
#             if not road_data:
#                 road_data = DesignConstructionManager.load_baseline_from_unified(layer_folder, 'surface_baseline')
#                 if not road_data:
#                     QMessageBox.warning(self, "Missing Data", "No surface baseline found in the specified design layer.")
#                     return
            
#             # Find coordinates for chainage
#             km_str = placement_values.get("km", "0").strip()
#             ch_str = placement_values.get("chainage", "0").strip()
#             if not km_str: km_str = "0"
#             if not ch_str: ch_str = "0"
            
#             # Handle chainage in "KM+chainage" format (e.g. "101+080")
#             if "+" in ch_str:
#                 parts = ch_str.split("+")
#                 km = float(parts[0])
#                 chainage = float(parts[1])
#             else:
#                 km = float(km_str)
#                 chainage = float(ch_str)
#             target_abs = km * 1000 + chainage
            
#             # Extract world_coordinates
#             all_points = []
#             for poly in road_data.get("polylines", []):
#                 for pt in poly.get("points", []):
#                     pt_ch_str = pt.get("chainage_str", "")
#                     if "+" in pt_ch_str:
#                         try:
#                             k_s, c_s = pt_ch_str.split("+")
#                             pt_abs = float(k_s) * 1000 + float(c_s)
#                             wc = pt.get("world_coordinates")
#                             if wc and len(wc) >= 3:
#                                 all_points.append((pt_abs, wc))
#                         except Exception:
#                             pass
            
#             if not all_points:
#                 QMessageBox.warning(self, "Error", "No valid coordinates found in the baseline.")
#                 return
            
#             # Sort points by absolute chainage
#             all_points.sort(key=lambda x: x[0])
            
#             target_coord = None
#             tangent_vec = None
            
#             # Find the segment containing the target chainage
#             for i in range(len(all_points) - 1):
#                 p1_abs, p1_wc = all_points[i]
#                 p2_abs, p2_wc = all_points[i+1]
                
#                 if p1_abs <= target_abs <= p2_abs:
#                     if p2_abs - p1_abs > 0.001:
#                         t = (target_abs - p1_abs) / (p2_abs - p1_abs)
#                     else:
#                         t = 0
                    
#                     target_coord = [
#                         p1_wc[0] + t * (p2_wc[0] - p1_wc[0]),
#                         p1_wc[1] + t * (p2_wc[1] - p1_wc[1]),
#                         p1_wc[2] + t * (p2_wc[2] - p1_wc[2])
#                     ]
                    
#                     vx = p2_wc[0] - p1_wc[0]
#                     vy = p2_wc[1] - p1_wc[1]
#                     vz = p2_wc[2] - p1_wc[2]
#                     length = math.sqrt(vx*vx + vy*vy + vz*vz)
#                     if length > 0:
#                         tangent_vec = [vx/length, vy/length, vz/length]
#                     break
            
#             if not target_coord:
#                 if target_abs < all_points[0][0]:
#                     target_coord = list(all_points[0][1])
#                     if len(all_points) > 1:
#                         vx = all_points[1][1][0] - all_points[0][1][0]
#                         vy = all_points[1][1][1] - all_points[0][1][1]
#                         vz = all_points[1][1][2] - all_points[0][1][2]
#                     else:
#                         vx, vy, vz = 1, 0, 0
#                 else:
#                     target_coord = list(all_points[-1][1])
#                     if len(all_points) > 1:
#                         vx = all_points[-1][1][0] - all_points[-2][1][0]
#                         vy = all_points[-1][1][1] - all_points[-2][1][1]
#                         vz = all_points[-1][1][2] - all_points[-2][1][2]
#                     else:
#                         vx, vy, vz = 1, 0, 0
                
#                 length = math.sqrt(vx*vx + vy*vy + vz*vz)
#                 if length > 0:
#                     tangent_vec = [vx/length, vy/length, vz/length]
#                 else:
#                     tangent_vec = [1.0, 0.0, 0.0]
            
#             # Apply depth offset
#             try:
#                 depth_str = str(placement_values.get("depth", "0")).replace("e.g.", "").replace("m", "").strip()
#                 DepthFromRoadSurface = float(depth_str) if depth_str else 0.5
#             except Exception:
#                 DepthFromRoadSurface = 0.5
                
#             # RoadSurface_Z = road elevation at selected KM/Chainage
#             RoadSurface_Z = target_coord[2]
            
#             # TopOfUnderPass_Z = RoadSurface_Z - DepthFromRoadSurface
#             TopOfUnderPass_Z = RoadSurface_Z - DepthFromRoadSurface
            
#             # The depth from user represents the vertical distance between road surface and TOP slab.
#             # Since visualize_under_pass builds geometry with local Z=0 at the center,
#             # and the top slab is at +height/2.0, the world center needs to be positioned
#             # so the top slab reaches exactly TopOfUnderPass_Z.
#             # We apply this as a true vertical offset.
#             height = float(dimensions.get("height", 6.0))
#             target_coord[2] = TopOfUnderPass_Z - (height / 2.0)

            
#             # Calculate rotation angle from tangent
#             angle_rad = math.atan2(tangent_vec[1], tangent_vec[0])
#             angle_deg = math.degrees(angle_rad)
            
#             # Build comprehensive Under Pass data record
#             under_pass_id = f"UP_{int(km):03d}_{int(chainage):03d}_{random.randint(100, 999)}"
# ############################################################################ Mayur Wakhare 09-06-2026 : New Code Added          
#             # Pre-compute cavity (hollow interior) dimensions for geometry subtraction
#             up_length = float(dimensions.get("length", 20.0))
#             up_width = float(dimensions.get("width", 10.0))
#             up_height_val = float(dimensions.get("height", 6.0))
#             up_wall_t = float(dimensions.get("wall_thickness", 0.7))
#             up_slab_t = float(dimensions.get("slab_thickness", 0.7))
#             up_bottom_t = float(dimensions.get("bottom_thickness", 0.8))

#             cavity_hollow_width = up_width - 2.0 * up_wall_t
#             cavity_hollow_length = up_length
#             cavity_hollow_height = up_height_val - up_slab_t - up_bottom_t
#             cavity_center_z_offset = (up_bottom_t - up_slab_t) / 2.0
# ############################################################################ Mayur Wakhare 09-06-2026 : New Code Added          
#             under_pass_data = {
#                 "id": under_pass_id,
#                 "worksheet": self.current_worksheet_name,
#                 "design_layer": design_layer,
#                 "length": up_length,
#                 "width": up_width,
#                 "height": up_height_val,
#                 "wall_thickness": up_wall_t,
#                 "slab_thickness": up_slab_t,
#                 "bottom_thickness": up_bottom_t,
# ########################################################################
#                 "km": int(km),
#                 "chainage": f"{int(km)}+{int(chainage):03d}",
#                 "chainage_abs": target_abs,
#                 "depth_from_road_surface": DepthFromRoadSurface,
#                 "road_surface_z": RoadSurface_Z,
#                 "position": {
#                     "x": round(target_coord[0], 6),
#                     "y": round(target_coord[1], 6),
#                     "z": round(target_coord[2], 6)
#                 },
#                 "rotation": {
#                     "rx": 0.0,
#                     "ry": 0.0,
#                     "rz": round(angle_deg, 4)
#                 },
#                 "tangent": tangent_vec,
#                 # Keep dimensions dict for backward compatibility with visualize_under_pass
#                 "dimensions": dimensions,
# ###########################################################################
# # Mayur Wakhare 09-06-2026 New Code Added
#                 "world_coordinates": target_coord,
#                 # Pre-computed cavity bounds for permanent geometry subtraction
#                 "cavity": {
#                     "hollow_width": round(cavity_hollow_width, 6),
#                     "hollow_length": round(cavity_hollow_length, 6),
#                     "hollow_height": round(cavity_hollow_height, 6),
#                     "hollow_center_z_offset": round(cavity_center_z_offset, 6),
#                     "world_center": [round(target_coord[0], 6), round(target_coord[1], 6), round(target_coord[2], 6)],
#                     "rotation_deg": round(angle_deg, 4),
#                     "tangent": tangent_vec
#                 }
# ###########################################################################
#             }
            
#             # ── Save to design_construction_config.json ──
#             master_data = DesignConstructionManager.load_master(layer_folder)
            
#             # Ensure under_passes section exists at top level
#             if "under_passes" not in master_data:
#                 master_data["under_passes"] = []
            
#             # Also keep backward-compatible reference_assets entry
#             if "reference_assets" not in master_data:
#                 master_data["reference_assets"] = {}
#             if "under_pass" not in master_data["reference_assets"]:
#                 master_data["reference_assets"]["under_pass"] = []
            
#             # Append to both locations
#             master_data["under_passes"].append(under_pass_data)
            
#             current_ref = master_data["reference_assets"]["under_pass"]
#             if isinstance(current_ref, list):
#                 current_ref.append(under_pass_data)
#             else:
#                 master_data["reference_assets"]["under_pass"] = [under_pass_data]
            
#             DesignConstructionManager.save_master(layer_folder, master_data)
            
#             print(f"Under Pass saved: {under_pass_id} at {int(km)}+{int(chainage):03d}")
#             print(f"  Position: ({target_coord[0]:.3f}, {target_coord[1]:.3f}, {target_coord[2]:.3f})")
#             print(f"  Rotation: {angle_deg:.2f} degrees")
#             print(f"  Layer: {design_layer}")
#             print(f"  Saved to: {layer_folder}")
            
#             QMessageBox.information(self, "Success", f"Under Pass '{under_pass_id}' placed at {int(km)}+{int(chainage):03d} in layer '{design_layer}'.")
            
#             # ── Immediately render the actor ──
#             up_actor = self.visualize_under_pass(under_pass_data)
            
#             # ── Rebuild material meshes with permanent geometry subtraction ──
#             # Instead of runtime clipping, re-generate material 3D meshes so the
#             # cavity hole is baked into the geometry and survives save/reload.
# #Mayur Wakhare 09-06-2026 Update code
#             self._rebuild_materials_after_underpass()
#             self._rebuild_baselines_after_underpass()
                
#         except Exception as e:
#             print(f"Error placing Under Pass: {e}")
#             import traceback
#             traceback.print_exc()
#             QMessageBox.critical(self, "Error", f"Failed to place Under Pass: {str(e)}")

#     def apply_under_pass_clipping(self, data, under_pass_actor=None):
#         """
#         Removes the material/construction layers from the hollow internal cavity 
#         of the Under Pass to create a clear empty passage.
#         """
#         print("DEBUG: apply_under_pass_clipping called")
#         import vtk
#         import math

#         if not hasattr(self, 'vtk_widget') or not self.vtk_widget:
#             return

#         renderer = self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()
#         if not renderer: return

#         dims = data.get("dimensions", {})
#         length = float(dims.get("length", 20.0))
#         width = float(dims.get("width", 10.0))
#         height = float(dims.get("height", 6.0))
#         wall_t = float(dims.get("wall_thickness", 0.7))
#         slab_t = float(dims.get("slab_thickness", 0.7))
#         bottom_t = float(dims.get("bottom_thickness", 0.8))

#         wc = data.get("world_coordinates", [0, 0, 0])
#         tangent = data.get("tangent", [1, 0, 0])
        
#         # Calculate angle of tangent from X axis
#         tx, ty = tangent[0], tangent[1]
#         angle_rad = math.atan2(ty, tx)
#         angle_deg = math.degrees(angle_rad)

#         # The space occupied by the tunnel opening
#         hollow_width = width - 2.0 * wall_t
#         hollow_length = length  # Use exact internal length
#         hollow_height = height - slab_t - bottom_t
#         hollow_center_z = (bottom_t - slab_t) / 2.0

#         box = vtk.vtkBox()
#         box.SetBounds(
#             -hollow_width / 2.0, hollow_width / 2.0,
#             -hollow_length / 2.0, hollow_length / 2.0,
#             hollow_center_z - hollow_height / 2.0, hollow_center_z + hollow_height / 2.0
#         )

#         # The Box evaluates points in its local space. 
#         # We need to supply the INVERSE transform so world coordinates map to the box's local origin.
#         transform = vtk.vtkTransform()
#         transform.Translate(wc[0], wc[1], wc[2])
#         transform.RotateZ(angle_deg)
        
#         inv_transform = vtk.vtkTransform()
#         inv_transform.DeepCopy(transform)
#         inv_transform.Inverse()
#         box.SetTransform(inv_transform)

#         actors = renderer.GetActors()
#         actors.InitTraversal()
#         num_actors = actors.GetNumberOfItems()

#         for _ in range(num_actors):
#             a = actors.GetNextActor()
#             if not a.GetVisibility():
#                 continue
            
#             # Skip clipping the under pass itself
#             if a == under_pass_actor:
#                 continue

#             mapper = a.GetMapper()
#             if not mapper:
#                 continue

#             mapper.Update()
#             if hasattr(mapper, 'GetInputDataObject'):
#                 input_data = mapper.GetInputDataObject(0, 0)
#             else:
#                 input_data = mapper.GetInput()

#             if not input_data or not input_data.IsA("vtkDataSet"):
#                 continue

#             actor_matrix = a.GetMatrix()
#             actor_to_world = vtk.vtkTransform()
#             actor_to_world.SetMatrix(actor_matrix)

#             box_transform = vtk.vtkTransform()
#             box_transform.PostMultiply()
#             box_transform.Concatenate(actor_to_world)
#             box_transform.Concatenate(inv_transform)
            
#             box_clone = vtk.vtkBox()
#             box_clone.SetBounds(box.GetBounds())
#             box_clone.SetTransform(box_transform)

#             # Use vtkClipPolyData for PolyData to preserve structures (like point clouds), else vtkClipDataSet
#             if input_data.IsA("vtkPolyData"):
#                 clipper = vtk.vtkClipPolyData()
#             else:
#                 clipper = vtk.vtkClipDataSet()
                
#             clipper.SetInputData(input_data)
#             clipper.SetClipFunction(box_clone)
#             clipper.SetInsideOut(False) 
#             clipper.Update()

#             new_data = clipper.GetOutput()
#             if new_data and new_data.GetNumberOfPoints() > 0:
#                 if isinstance(mapper, vtk.vtkPolyDataMapper) and not new_data.IsA("vtkPolyData"):
#                     surface_filter = vtk.vtkDataSetSurfaceFilter()
#                     surface_filter.SetInputData(new_data)
#                     surface_filter.Update()
#                     mapper.SetInputData(surface_filter.GetOutput())
#                 else:
#                     mapper.SetInputData(new_data)
#             else:
#                 a.SetVisibility(False)

#                 # Apply clipping to material layer actors (if any)\n        if hasattr(self, 'material_3d_actors'):\n            for actor_list in self.material_3d_actors.values():\n                for act in actor_list:\n                    if not act.GetVisibility():\n                        continue\n                    mapper = act.GetMapper()\n                    if not mapper:\n                        continue\n                    mapper.Update()\n                    if hasattr(mapper, 'GetInputDataObject'):\n                        input_data = mapper.GetInputDataObject(0, 0)\n                    else:\n                        input_data = mapper.GetInput()\n                    if not input_data or not input_data.IsA("vtkDataSet"):\n                        continue\n                    # Transform box to actor space\n                    actor_matrix = act.GetMatrix()\n                    actor_to_world = vtk.vtkTransform()\n                    actor_to_world.SetMatrix(actor_matrix)\n                    box_transform = vtk.vtkTransform()\n                    box_transform.PostMultiply()\n                    box_transform.Concatenate(actor_to_world)\n                    box_transform.Concatenate(inv_transform)\n                    box_clone = vtk.vtkBox()\n                    box_clone.SetBounds(box.GetBounds())\n                    box_clone.SetTransform(box_transform)\n                    # Choose appropriate clipper\n                    if input_data.IsA("vtkPolyData"):\n                        clipper = vtk.vtkClipPolyData()\n                    else:\n                        clipper = vtk.vtkClipDataSet()\n                    clipper.SetInputData(input_data)\n                    clipper.SetClipFunction(box_clone)\n                    clipper.SetInsideOut(False)\n                    clipper.Update()\n                    new_data = clipper.GetOutput()\n                    if new_data and new_data.GetNumberOfPoints() > 0:\n                        if isinstance(mapper, vtk.vtkPolyDataMapper) and not new_data.IsA("vtkPolyData"):\n                            surface_filter = vtk.vtkDataSetSurfaceFilter()\n                            surface_filter.SetInputData(new_data)\n                            surface_filter.Update()\n                            mapper.SetInputData(surface_filter.GetOutput())\n                        else:\n                            mapper.SetInputData(new_data)\n                    else:\n                        act.SetVisibility(False)\n        # Render the updated scene\n        self.vtk_widget.GetRenderWindow().Render()
# # Mayur Wakhare 09-06-2026 : New Code Added
#     def _rebuild_materials_after_underpass(self):
#         """
#         Re-generate all active material 3D actors so that the geometry subtraction
#         in draw_material_filling produces permanent hollow meshes at Under Pass cavities.
#         Called after an Under Pass is placed instead of runtime clipping.
#         """
#         print("DEBUG: Rebuilding material actors")
#         try:
#             if not hasattr(self, 'material_3d_actors') or not self.material_3d_actors:
#                 return

#             # Get the list of active material indices that have 3D actors
#             active_indices = list(self.material_3d_actors.keys())
#             if not active_indices:
#                 return

#             print(f"Rebuilding {len(active_indices)} material layers after Under Pass placement...")
            
#             # Print underpass count here to verify
#             if hasattr(self, '_get_all_under_pass_cavities'):
#                 cavs = self._get_all_under_pass_cavities()
#                 print(f"DEBUG: Found {len(cavs) if cavs else 0} cavities in _get_all_under_pass_cavities before rebuild loop")

#             for material_index in active_indices:
#                 try:
#                     self.load_and_draw_material_filling(material_index)
#                     print(f"  Rebuilt material M{material_index + 1} with cavity subtraction")
#                 except Exception as e:
#                     print(f"  Error rebuilding material M{material_index + 1}: {e}")

#             # Render the updated scene
#             if hasattr(self, 'vtk_widget') and self.vtk_widget:
#                 self.vtk_widget.GetRenderWindow().Render()

#             print("Material rebuild complete — cavities permanently subtracted.")
#         except Exception as e:
#             print(f"Error in _rebuild_materials_after_underpass: {e}")
#             import traceback
#             traceback.print_exc()

#     def _rebuild_baselines_after_underpass(self):
#         """
#         Re-generate baseline 3D planes so that the cavity hole is accurately clipped
#         for surface lines during live mode placement.
#         """
#         print("DEBUG: Rebuilding baseline actors")
#         try:
#             layer_folder = getattr(self, 'current_design_layer_path', None)
#             if not layer_folder:
#                 return

#             # Clear existing 3D baseline planes from the scene
#             if hasattr(self, 'clear_baseline_planes'):
#                 self.clear_baseline_planes()
                
#             # Reload and draw them using the existing loaded configuration
#             if hasattr(self, 'load_all_baselines_from_layer') and hasattr(self, 'map_baselines_to_3d_planes_from_data'):
#                 loaded_baselines = self.load_all_baselines_from_layer(layer_folder)
#                 if loaded_baselines:
#                     self.map_baselines_to_3d_planes_from_data(loaded_baselines)
#                     print("  Rebuilt baselines with cavity subtraction")
                    
#             if hasattr(self, 'vtk_widget') and self.vtk_widget:
#                 self.vtk_widget.GetRenderWindow().Render()

#         except Exception as e:
#             print(f"Error in _rebuild_baselines_after_underpass: {e}")
#             import traceback
#             traceback.print_exc()
# ###########################################################################
#     def visualize_under_pass(self, data):
#         import vtk
#         import math

#         if not hasattr(self, 'vtk_widget') or not self.vtk_widget:
#             return

#         renderer = self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()
#         if not renderer: return

#         dims = data.get("dimensions", {})
#         length = dims.get("length", 20.0)
#         width = dims.get("width", 10.0)
#         height = dims.get("height", 6.0)
#         wall_t = dims.get("wall_thickness", 0.7)
#         slab_t = dims.get("slab_thickness", 0.7)
#         bottom_t = dims.get("bottom_thickness", 0.8)

#         append_filter = vtk.vtkAppendPolyData()

#         # Top Slab
#         top_slab = vtk.vtkCubeSource()
#         top_slab.SetXLength(width)
#         top_slab.SetYLength(length)
#         top_slab.SetZLength(slab_t)
#         top_slab.SetCenter(0, 0, height/2.0 - slab_t/2.0)
#         append_filter.AddInputConnection(top_slab.GetOutputPort())

#         # Bottom Slab
#         bottom_slab = vtk.vtkCubeSource()
#         bottom_slab.SetXLength(width)
#         bottom_slab.SetYLength(length)
#         bottom_slab.SetZLength(bottom_t)
#         bottom_slab.SetCenter(0, 0, -height/2.0 + bottom_t/2.0)
#         append_filter.AddInputConnection(bottom_slab.GetOutputPort())

#         # Left Wall
#         left_wall = vtk.vtkCubeSource()
#         left_wall.SetXLength(wall_t)
#         left_wall.SetYLength(length)
#         wall_height = height - slab_t - bottom_t
#         left_wall.SetZLength(wall_height if wall_height > 0 else 0.1)
#         left_wall.SetCenter(-width/2.0 + wall_t/2.0, 0, (bottom_t - slab_t)/2.0)
#         append_filter.AddInputConnection(left_wall.GetOutputPort())

#         # Right Wall
#         right_wall = vtk.vtkCubeSource()
#         right_wall.SetXLength(wall_t)
#         right_wall.SetYLength(length)
#         right_wall.SetZLength(wall_height if wall_height > 0 else 0.1)
#         right_wall.SetCenter(width/2.0 - wall_t/2.0, 0, (bottom_t - slab_t)/2.0)
#         append_filter.AddInputConnection(right_wall.GetOutputPort())

#         wc = data.get("world_coordinates", [0, 0, 0])
#         tangent = data.get("tangent", [1, 0, 0])
        
#         # Calculate angle of tangent from X axis
#         tx, ty = tangent[0], tangent[1]
#         angle_rad = math.atan2(ty, tx)
#         angle_deg = math.degrees(angle_rad)

#         transform = vtk.vtkTransform()
#         transform.Translate(wc[0], wc[1], wc[2])
#         transform.RotateZ(angle_deg)

#         transform_filter = vtk.vtkTransformPolyDataFilter()
#         transform_filter.SetTransform(transform)
#         transform_filter.SetInputConnection(append_filter.GetOutputPort())
#         transform_filter.Update()

#         mapper = vtk.vtkPolyDataMapper()
#         mapper.SetInputConnection(transform_filter.GetOutputPort())

#         actor = vtk.vtkActor()
#         actor.SetMapper(mapper)
#         actor.GetProperty().SetColor(0.55, 0.55, 0.55)
        
#         # Track actor for general references
#         if hasattr(self, 'reference_actors'):
#             self.reference_actors.append(actor)
            
#         # Track actor for layer-specific visibility
#         if hasattr(self, '_per_layer_actors'):
#             layer_path = None
#             ws_name = data.get("worksheet", getattr(self, 'current_worksheet_name', ''))
#             layer_name = data.get("design_layer", getattr(self, 'current_layer_name', ''))
#             subfolder = getattr(self, 'current_subfolder_type', 'designs')
            
#             if hasattr(self, 'WORKSHEETS_BASE_DIR') and ws_name and layer_name:
#                 layer_path = os.path.join(self.WORKSHEETS_BASE_DIR, ws_name, subfolder, layer_name)
#             elif hasattr(self, 'current_design_layer_path') and getattr(self, 'current_design_layer_path'):
#                 layer_path = getattr(self, 'current_design_layer_path')
                
#             if layer_path:
#                 if layer_path not in self._per_layer_actors:
#                     self._per_layer_actors[layer_path] = []
#                 if actor not in self._per_layer_actors[layer_path]:
#                     self._per_layer_actors[layer_path].append(actor)
#                 self.message_text.append(f" Under Pass added to layer: {layer_name}")

#         renderer.AddActor(actor)
#         self.vtk_widget.GetRenderWindow().Render()
#         return actor

# ==============================================================================================
    def update_user_info(self, full_name):
        """
        Updates the user menu button with initials and tooltip based on full name.
        Example: "Aniket Pund" -> "AP"
        """
        if not full_name:
            full_name = "Guest"
            
        initials = "G"
        if full_name and full_name.lower() != "guest":
            parts = full_name.strip().split()
            if len(parts) >= 2:
                initials = f"{parts[0][0]}{parts[1][0]}".upper()
            elif len(parts) == 1:
                initials = parts[0][0:2].upper()
                
                
        if hasattr(self, 'user_menu_btn'):
            # Prepend icon to initials
            self.user_menu_btn.setText(f" 👤 {initials} ")
            self.user_menu_btn.setToolTip(f"Logged in as: {full_name}")

    def set_mode(self, mode_name):
        self.app_mode = mode_name
        if hasattr(self, 'mode_banner'):
            self.mode_banner.setText(f"Current Mode: {mode_name}")
            self.mode_banner.setVisible(True)

        # Keep the mode dropdown in sync with the active mode.
        if hasattr(self, 'mode_actions'):
            for name, action in self.mode_actions.items():
                action.setChecked(name == mode_name)

        # Centralize mode-specific visibility rules for a user-friendly layout.
        show_measurement_panel = mode_name == "Measurement"

        if hasattr(self, 'scale_section') and self.scale_section:
            self.scale_section.setVisible(False)
        if hasattr(self, 'bottom_section') and self.bottom_section:
            if mode_name != "Design":
                self.bottom_section.setVisible(False)
        if hasattr(self, 'main_measurement_section') and self.main_measurement_section:
            self.main_measurement_section.setVisible(show_measurement_panel)

        # Refresh C & T button states across all 2D layer rows
        self._refresh_ct_button_states()

    def _refresh_ct_button_states(self):
        """Enable/disable C & T buttons in all 2D layer rows based on current app_mode.
        Only 'Comparison' mode enables C & T buttons; all other modes disable them."""
        if not hasattr(self, 'two_D_layers_layout') or self.two_D_layers_layout is None:
            return
        enabled = (getattr(self, 'app_mode', 'Design') == "Comparison")

        # ── C button styles (Green / Emerald) ──────────────────────────────
        c_disabled_style = """
            QPushButton {
                border-radius: 13px;
                border: 1px solid #b0c8b0;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d8e8d8, stop:0.5 #c8dcc8, stop:1 #b8ccb8);
                color: #99aa99;
                font-weight: bold;
                font-size: 11px;
            }
        """
        c_enabled_style = """
            QPushButton {
                border-radius: 13px;
                border: 1px solid #2e7d32;
                border-top: 1px solid #66bb6a;
                border-left: 1px solid #66bb6a;
                border-right: 1px solid #1b5e20;
                border-bottom: 2px solid #1b5e20;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #81c784, stop:0.3 #66bb6a, stop:0.5 #4caf50, stop:1 #388e3c);
                color: white;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a5d6a7, stop:0.3 #81c784, stop:0.5 #66bb6a, stop:1 #4caf50);
                border: 1px solid #43a047;
                border-bottom: 2px solid #2e7d32;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2e7d32, stop:0.5 #388e3c, stop:1 #4caf50);
                border: 1px solid #1b5e20;
                border-top: 2px solid #1b5e20;
                padding-top: 1px;
            }
        """

        # ── T button styles (Purple / Violet) ──────────────────────────────
        t_disabled_style = """
            QPushButton {
                border-radius: 13px;
                border: 1px solid #c0b0d0;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e0d8e8, stop:0.5 #d4c8dc, stop:1 #c8b8d0);
                color: #aa99bb;
                font-weight: bold;
                font-size: 11px;
            }
        """
        t_enabled_style = """
            QPushButton {
                border-radius: 13px;
                border: 1px solid #6a1b9a;
                border-top: 1px solid #ba68c8;
                border-left: 1px solid #ba68c8;
                border-right: 1px solid #4a148c;
                border-bottom: 2px solid #4a148c;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ce93d8, stop:0.3 #ba68c8, stop:0.5 #ab47bc, stop:1 #8e24aa);
                color: white;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e1bee7, stop:0.3 #ce93d8, stop:0.5 #ba68c8, stop:1 #ab47bc);
                border: 1px solid #9c27b0;
                border-bottom: 2px solid #7b1fa2;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6a1b9a, stop:0.5 #7b1fa2, stop:1 #9c27b0);
                border: 1px solid #4a148c;
                border-top: 2px solid #4a148c;
                padding-top: 1px;
            }
        """

        for i in range(self.two_D_layers_layout.count()):
            item = self.two_D_layers_layout.itemAt(i)
            if not item or not item.widget():
                continue
            # Each item is a container_widget holding row_widget + optional slider_row
            container_widget = item.widget()
            container_layout = container_widget.layout()
            if container_layout is None:
                continue
            # Traverse container children to find the row_widget (first child)
            for ci in range(container_layout.count()):
                c_item = container_layout.itemAt(ci)
                if not c_item or not c_item.widget():
                    continue
                child_widget = c_item.widget()
                row_layout = child_widget.layout()
                if row_layout is None:
                    continue
                # Look for C and T buttons in this sub-widget
                c_btn = None
                t_btn = None
                for j in range(row_layout.count()):
                    btn_item = row_layout.itemAt(j)
                    if btn_item and btn_item.widget():
                        w = btn_item.widget()
                        if isinstance(w, QPushButton):
                            if w.text() == "C":
                                c_btn = w
                            elif w.text() == "T":
                                t_btn = w
                # Apply C button state
                if c_btn is not None:
                    c_btn.setEnabled(enabled)
                    if not enabled:
                        # Leaving Comparison mode: reset compare_active, use disabled style
                        c_btn.setProperty("compare_active", False)
                        c_btn.setStyleSheet(c_disabled_style)
                        c_btn.setCursor(Qt.ForbiddenCursor)
                    else:
                        # Entering Comparison mode: use enabled style (not active yet)
                        c_btn.setStyleSheet(c_enabled_style)
                        c_btn.setCursor(Qt.PointingHandCursor)
                # Apply T button state
                if t_btn is not None:
                    if not enabled:
                        # Leaving Comparison mode: always disable T, hide slider
                        t_btn.setEnabled(False)
                        t_btn.setStyleSheet(t_disabled_style)
                        t_btn.setCursor(Qt.ForbiddenCursor)
                        t_btn.setProperty("slider_open", False)
                        # Hide any open slider rows (second child in container)
                        for sci in range(container_layout.count()):
                            sc_item = container_layout.itemAt(sci)
                            if sc_item and sc_item.widget() and sc_item.widget() is not child_widget:
                                sc_item.widget().setVisible(False)
                    else:
                        # In Comparison mode: T is only enabled after C is pressed
                        c_is_active = bool(c_btn.property("compare_active")) if c_btn else False
                        t_btn.setEnabled(c_is_active)
                        t_btn.setStyleSheet(t_enabled_style if c_is_active else t_disabled_style)
                        t_btn.setCursor(Qt.PointingHandCursor if c_is_active else Qt.ForbiddenCursor)

    def create_progress_bar(self):
        """Create and configure the progress bar widget"""
        from utils import resource_path
        import os
        logo_path = resource_path(os.path.join("data", "3D Bharat logo.png"))
        self.progress_bar = RectangularProgressWindow(logo_path)
        
        # Center on screen precisely
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.progress_bar.width()) // 2
        y = (screen_geometry.height() - self.progress_bar.height()) // 2
        self.progress_bar.move(x, y)

    def show_progress_bar(self, file_path=None):
        """Show and position the progress bar"""
        if file_path:
            file_name = os.path.basename(file_path)
            # Get and format file size
            try:
                file_size_bytes = os.path.getsize(file_path)
                if file_size_bytes < 1024 * 1024: # Less than 1 MB
                    size_str = f"{file_size_bytes/1024:.1f} KB"
                elif file_size_bytes < 1024 * 1024 * 1024: # Less than 1 GB
                    size_str = f"{file_size_bytes/(1024*1024):.1f} MB"
                else: # GB or more
                    size_str = f"{file_size_bytes/(1024*1024*1024):.1f} GB"
            except:
                size_str = "Unknown"
            
            self.progress_bar.set_file_info(f"File: {file_name}", f"Size: {size_str}")
        
        self.progress_bar.set_progress(0)
        self.progress_bar.show()
        QApplication.processEvents() # Force UI update

    def update_progress(self, value, message=None):
        """Update progress bar value and optionally the message"""
        self.progress_bar.set_progress(value)
        if message:
            self.progress_bar.set_loading_message(message)
        QApplication.processEvents() # Ensure UI updates

    def hide_progress_bar(self):
        """Hide the progress bar with a smooth fade-out"""
        self.progress_bar.hide()
        self.progress_bar.set_progress(0)

    def toggle_line_section(self):
        """Toggle visibility of the line section"""
        if self.line_content_widget.isVisible():
            # Collapse the section
            self.line_content_widget.hide()
            self.collapse_button.setText("▶")
            self.collapse_button.setToolTip("Open Line Section")
            # Hide undo/redo buttons
            self.undo_button.hide()
            self.redo_button.hide()
            # Set fixed width for collapsed state
            self.line_section.setFixedWidth(80)
            # Update the layout to remove space for hidden buttons
            self.header_container.layout().setContentsMargins(0, 5, 0, 5)
        else:
            # Expand the section
            self.line_content_widget.show()
            self.collapse_button.setText("◀")
            self.collapse_button.setToolTip("Close Line Section")
            # Show undo/redo buttons
            self.undo_button.show()
            self.redo_button.show()
            # Aniket updated 05-05-2026: Set fixed width to match new expanded size
            self.line_section.setFixedWidth(320)

        # Force layout update
        self.header_container.updateGeometry()
        self.line_section.updateGeometry()
        QApplication.processEvents()  # Force immediate UI update
        self.canvas.draw()

    def setup_zoom_controls(self):
        """Connect zoom controls to their functions"""
        self.zoom_in_button.clicked.connect(self.zoom_in_simple)
        self.zoom_out_button.clicked.connect(self.zoom_out_simple)
        self.reset_zoom_button.clicked.connect(self.reset_zoom_simple)
        self.zoom_slider.valueChanged.connect(self.zoom_slider_changed_simple)
        
        # Pan controls
        self.pan_left_button.clicked.connect(self.pan_left_simple)
        self.pan_right_button.clicked.connect(self.pan_right_simple)
        self.pan_up_button.clicked.connect(self.pan_up_simple)
        self.pan_down_button.clicked.connect(self.pan_down_simple)
        
        # Set up mouse wheel zoom
        self.canvas.mpl_connect('scroll_event', self.on_mouse_wheel_simple)
        
        # Initialize zoom state
        self.current_zoom = 100  # 100%
        self.original_xlim = (0, self.total_distance)
        self.original_ylim = (-3, 3)

        self.autofit_button.clicked.connect(self.autofit_graph_simple)

    def zoom_in_simple(self):
        """Zoom in by 20%"""
        self.current_zoom = min(500, self.current_zoom * 1.2)  # Cap at 500%
        self.apply_zoom()
        self.update_zoom_display()

    def zoom_out_simple(self):
        """Zoom out by 20%"""
        self.current_zoom = max(10, self.current_zoom / 1.2)  # Minimum 10%
        self.apply_zoom()
        self.update_zoom_display()

    def reset_zoom_simple(self):
        """Reset zoom to original view"""
        self.current_zoom = 100
        self.ax.set_xlim(self.original_xlim)
        self.ax.set_ylim(self.original_ylim)
        self.zoom_slider.setValue(100)
        self.update_zoom_display()
        self.canvas.draw()

    def zoom_slider_changed_simple(self, value):
        """Handle zoom slider changes"""
        self.current_zoom = value
        self.apply_zoom()
        self.update_zoom_display()

    def apply_zoom(self):
        """Apply the current zoom level to the graph - Zoom relative to visible left"""
        current_xlim = self.ax.get_xlim()
        current_left = current_xlim[0]  # Get current left position
        
        # Calculate new range based on zoom level
        original_range = self.original_xlim[1] - self.original_xlim[0]
        new_range = original_range * (100 / self.current_zoom)
        
        # Keep the current left position fixed, adjust right based on zoom
        new_xlim = (current_left, current_left + new_range)
        
        # Apply new limits
        self.ax.set_xlim(new_xlim)
        
        # Keep y-axis at original scale for now
        self.ax.set_ylim(self.original_ylim)
        
        self.canvas.draw()

    def update_zoom_display(self):
        """Update zoom label"""
        self.zoom_label.setText(f"{int(self.current_zoom)}%")

    def on_mouse_wheel_simple(self, event):
        """Mouse wheel zoom - simpler version"""
        if event.inaxes != self.ax:
            return
        
        # Try to detect Ctrl - check both string and Qt modifiers
        ctrl_pressed = False
        
        # Check event.key (matplotlib's representation)
        if event.key and isinstance(event.key, str) and 'control' in event.key.lower():
            ctrl_pressed = True
        
        # Check Qt modifiers if available
        if not ctrl_pressed and hasattr(event, 'guiEvent') and event.guiEvent:
            from PyQt5.QtCore import Qt
            if event.guiEvent.modifiers() & Qt.ControlModifier:
                ctrl_pressed = True
        
        # If Ctrl is pressed, zoom
        if ctrl_pressed:
            if event.button == 'up':
                self.zoom_in_simple()
            elif event.button == 'down':
                self.zoom_out_simple()

    def pan_left_simple(self):
        """Pan graph to the left, but not beyond 0"""
        current_xlim = self.ax.get_xlim()
        
        # Calculate pan amount (10% of current width)
        pan_amount = (current_xlim[1] - current_xlim[0]) * 0.1
        
        # Calculate new left position
        new_left = current_xlim[0] - pan_amount
        
        # Don't go below 0
        if new_left < 0:
            new_left = 0
        
        # Calculate new right position
        new_right = current_xlim[1] - (current_xlim[0] - new_left)
        
        self.ax.set_xlim(new_left, new_right)
        self.canvas.draw()

    def pan_right_simple(self):
        """Pan graph to the right"""
        current_xlim = self.ax.get_xlim()
        pan_amount = (current_xlim[1] - current_xlim[0]) * 0.1
        self.ax.set_xlim(current_xlim[0] + pan_amount, current_xlim[1] + pan_amount)
        self.canvas.draw()

    def pan_up_simple(self):
        """Pan graph up"""
        current_ylim = self.ax.get_ylim()
        pan_amount = (current_ylim[1] - current_ylim[0]) * 0.1
        self.ax.set_ylim(current_ylim[0] + pan_amount, current_ylim[1] + pan_amount)
        self.canvas.draw()

    def pan_down_simple(self):
        """Pan graph down"""
        current_ylim = self.ax.get_ylim()
        pan_amount = (current_ylim[1] - current_ylim[0]) * 0.1
        self.ax.set_ylim(current_ylim[0] - pan_amount, current_ylim[1] - pan_amount)
        self.canvas.draw()

    def autofit_graph_simple(self):
        """Auto-fit the graph to show all lines"""
        try:
            # Get all line data
            all_x = []
            all_y = []
            
            # Check each line type for data
            for line_type, data in self.line_types.items():
                for polyline in data['polylines']:
                    if polyline and len(polyline) > 0:
                        xs = [p[0] for p in polyline]
                        ys = [p[1] for p in polyline]
                        all_x.extend(xs)
                        all_y.extend(ys)
            
            if all_x and all_y:
                # Calculate bounds with minimal asymmetric padding so plot hugs the data
                x_min, x_max = min(all_x), max(all_x)
                y_min, y_max = min(all_y), max(all_y)

                # Protect against zero ranges
                x_range = x_max - x_min
                if x_range <= 0:
                    x_range = 1.0
                y_range = y_max - y_min
                if y_range <= 0:
                    y_range = 1.0

                # Use very small padding (1% left, 0.5% right) to avoid large empty areas
                left_padding = x_range * 0.01
                right_padding = x_range * 0.005
                y_padding = y_range * 0.02

                # Apply new bounds (right edge slightly tighter)
                self.ax.set_xlim(x_min - left_padding, x_max + right_padding)
                self.ax.set_ylim(y_min - y_padding, y_max + y_padding)

                # Reduce extra white space around the axes
                try:
                    self.figure.tight_layout(pad=0.2)
                except Exception:
                    pass
                
                # Update zoom display
                visible_range = (x_max + right_padding) - (x_min - left_padding)
                self.current_zoom = (self.original_xlim[1] / visible_range) * 100
                self.update_zoom_display()
                self.zoom_slider.setValue(int(self.current_zoom))
                
                self.canvas.draw()
                self.message_text.append("Graph auto-fitted to show all data.")
            else:
                self.message_text.append("No data available for auto-fit.")
        except Exception as e:
            self.message_text.append(f"Auto-fit error: {str(e)}")

# =============================================================================
    def _ensure_layer_panel_state(self):
        if not hasattr(self, 'layer_panel_buttons'):
            self.layer_panel_buttons = []
        if not hasattr(self, 'active_layer_highlight_name'):
            self.active_layer_highlight_name = None
        if not hasattr(self, 'active_layer_highlight_subfolder'):
            self.active_layer_highlight_subfolder = None
        if not hasattr(self, 'linked_design_layer_highlight_name'):
            self.linked_design_layer_highlight_name = None

    def _build_layer_button_style(self, is_construction_or_material=False, is_selected=False):
        text_color = "#E65100" if is_construction_or_material else "#0D47A1"
        border_color = "#FB8C00" if is_construction_or_material else "#1976D2"
        hover_bg = "#FFE0B2" if is_construction_or_material else "#BBDEFB"
        selected_bg = "#F6D8A8" if is_construction_or_material else "#D6E7FF"

        base_bg = selected_bg if is_selected else "rgba(255, 255, 255, 0.9)"
        left_border = "6px" if is_selected else "4px"

        return f"""
            QPushButton {{
                text-align: left;
                padding: 8px 12px;
                background-color: {base_bg};
                border-radius: 8px;
                margin: 3px 8px;
                font-size: 13px;
                color: {text_color};
                border: None;
                border-left: {left_border} solid {border_color};
                font-weight: {'bold' if is_selected else 'normal'};
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
        """

    def _apply_layer_button_style(self, button, is_selected=False):
        is_construction_or_material = bool(button.property("is_construction_or_material"))
        button.setStyleSheet(self._build_layer_button_style(is_construction_or_material, is_selected))
        button.setProperty("is_panel_selected", bool(is_selected))

    def set_layer_panel_highlight(self, active_layer_name=None, active_subfolder=None, linked_design_layer_name=None):
        self._ensure_layer_panel_state()
        self.active_layer_highlight_name = active_layer_name
        self.active_layer_highlight_subfolder = (str(active_subfolder).lower() if active_subfolder else None)
        self.linked_design_layer_highlight_name = linked_design_layer_name
        self._refresh_layer_panel_highlight()

    def _refresh_layer_panel_highlight(self):
        self._ensure_layer_panel_state()

        if not self.layer_panel_buttons:
            return

        active_name = str(self.active_layer_highlight_name or "")
        active_subfolder = str(self.active_layer_highlight_subfolder or "").lower()
        linked_design_name = str(self.linked_design_layer_highlight_name or "")

        alive_buttons = []
        for button in self.layer_panel_buttons:
            if button is None:
                continue

            btn_name = str(button.property("layer_name") or "")
            btn_subfolder = str(button.property("subfolder") or "").lower()
            btn_dimension = str(button.property("dimension") or "")

            is_selected = False
            if btn_name == active_name and (not active_subfolder or btn_subfolder == active_subfolder):
                is_selected = True

            if linked_design_name and btn_name == linked_design_name and btn_subfolder == "designs" and btn_dimension == "2D":
                is_selected = True

            self._apply_layer_button_style(button, is_selected=is_selected)
            alive_buttons.append(button)

        self.layer_panel_buttons = alive_buttons

    def clear_layer_panel_button_registry(self, dimension=None):
        self._ensure_layer_panel_state()
        if dimension is None:
            self.layer_panel_buttons = []
            return

        dim_u = str(dimension).upper()
        self.layer_panel_buttons = [
            btn for btn in self.layer_panel_buttons
            if str(btn.property("dimension") or "") != dim_u
        ]

    def add_layer_to_panel(self, layer_name: str, dimension: str, full_path: str = None, subfolder: str = None):
        """
        Adds a layer label to the correct panel (3D or 2D Layers).
        Used for both worksheet initial layers and design layers.
        For 2D layers, always uses the row-with-actions format (W1 prefix + Eye/C/T buttons)
        to keep the 2D panel consistent before and after visualization.
        """
        self._ensure_layer_panel_state()

        if str(dimension).strip().upper() == "2D":
            # Always use the row-with-actions (Image 2) format for 2D layers.
            # Build a ws_id from the current worksheet name when available.
            ws_name = getattr(self, 'current_worksheet_name', None)
            if ws_name:
                ws_id = f"W1"
            else:
                ws_id = "W1"
            display_name = f"{ws_id} - {layer_name}"

            # Build a minimal ws dict so toggle_eye can open the layer if needed.
            ws_data = None
            if hasattr(self, 'current_worksheet_data') and self.current_worksheet_data:
                ws_data = {
                    "id": ws_id,
                    "data": {
                        "worksheet_data": self.current_worksheet_data,
                        "folder_path": full_path.replace(
                            f"/{subfolder}/{layer_name}", ""
                        ).replace(
                            f"\\{subfolder}\\{layer_name}", ""
                        ) if full_path and subfolder else "",
                    }
                }

            if hasattr(self, 'add_layer_with_actions_to_2d_panel'):
                self.add_layer_with_actions_to_2d_panel(
                    display_name,
                    "2D",
                    full_path,
                    subfolder or "designs",
                    layer_name,
                    ws_data
                )
            return

        # --- 3D layers keep the existing pill-button style ---
        label = QPushButton(f"• {layer_name}")
        label.setCursor(Qt.PointingHandCursor)
        label.setProperty("layer_name", str(layer_name))
        label.setProperty("subfolder", str(subfolder or ""))
        label.setProperty("dimension", "3D")
        label.setProperty("is_construction_or_material", False)
        self._apply_layer_button_style(label, is_selected=False)
        label.setToolTip(f"3D Layer: {layer_name}")

        if full_path and subfolder and hasattr(self, 'switch_to_layer_from_panel'):
            label.clicked.connect(lambda checked=False, ln=layer_name, p=full_path, s=subfolder: self.switch_to_layer_from_panel(ln, p, s))

        if self.three_D_layers_layout:
            self.three_D_layers_layout.insertWidget(self.three_D_layers_layout.count() - 1, label)

        self.layer_panel_buttons.append(label)
        self._refresh_layer_panel_highlight()

 # ==================================================================================================================================
# Define function for the Load Point Cloud Data File & Start Measurements Buttons:
    def create_file_load_section(self):
        self.file_load_group = QGroupBox("File Load") # Section Name
        self.file_load_layout = QVBoxLayout()

        # Remove margins and spacing to minimize empty space
        self.file_load_layout.setContentsMargins(5, 5, 5, 5) 
        self.file_load_layout.setSpacing(3)
        
        self.start_button = QPushButton("Start Measurement") # Button for the start Measurements
        
        # self.start_button.setEnabled(False)
        
        self.file_load_layout.addWidget(self.start_button)

        self.file_load_group.setLayout(self.file_load_layout)

        self.main_measurement_layout.addWidget(self.file_load_group)

        self.file_load_group.setStyleSheet("""
            QGroupBox {
            border: 1px solid gray;
            border-radius: 5px;
            margin-top: 0.5em;
            }
            QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
            }
            """)

    def handle_point_cloud_update(self):
        loader = getattr(self, "load_point_cloud", None)
        if not callable(loader):
            QMessageBox.information(self, "Point Cloud", "Point cloud loading is not available in this view.")
            return

        loader()

        file_path = getattr(self, "loaded_file_path", "")
        if file_path:
            basename = os.path.basename(file_path)
            # Update the new bottom Point Cloud File section
            if hasattr(self, 'pc_file_display'):
                self.pc_file_display.setText(basename)
            if hasattr(self, 'pc_file_group'):
                self.pc_file_group.setVisible(True)
        else:
            if hasattr(self, 'pc_file_display'):
                self.pc_file_display.setText("")
        
# ==================================================================================================================================
# Define function for Measurement Section:
    def create_measurement_section(self):
        self.measurement_group = QGroupBox("Measurement") # Section Name
        self.measurement_layout = QVBoxLayout()

        self.measurement_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add metrics selection dropdown at the top
        self.metrics_group = QGroupBox("Measurement Metrics")
        metrics_layout = QHBoxLayout()
        self.metrics_group.setFixedHeight(70)
        self.metrics_group.setFixedWidth(230)
        
        self.metrics_combo = QComboBox()
        self.metrics_combo.addItems(["Meter", "Centimeter", "Millimeter"])
        self.metrics_combo.currentTextChanged.connect(self.update_measurement_metrics)
        
        metrics_layout.addWidget(QLabel("Units:"))
        metrics_layout.addWidget(self.metrics_combo)
        self.metrics_group.setLayout(metrics_layout)
        self.measurement_layout.addWidget(self.metrics_group)

        # Create a container widget for measurement buttons that will be shown/hidden
        self.measurement_buttons_container = QWidget()
        self.measurement_buttons_layout = QVBoxLayout()
        self.measurement_buttons_container.setLayout(self.measurement_buttons_layout)
        
        # Measurement buttons
        self.line_button = QPushButton("Line")  # New Line button
        self.line_menu = QMenu()  # Create dropdown menu
        self.vertical_line_action = QAction("Vertical Line", self)  # Vertical line option
        self.horizontal_line_action = QAction("Horizontal Line", self)  # Horizontal line option
        self.measurement_line_action = QAction("Measurement Line", self)
        self.presized_button = QPushButton("Presized")
        self.presized_button.setVisible(False)  # Start hidde
        self.line_menu.addAction(self.vertical_line_action)
        self.line_menu.addAction(self.horizontal_line_action)
        self.line_menu.addAction(self.measurement_line_action)
        self.line_button.setMenu(self.line_menu)  # Attach menu to button

        self.round_pillar_polygon_button = QPushButton("Round Pillar Polygon")
        self.polygon_button = QPushButton("Polygon") # Polygon button to measure a surface area of uneven structure land, angles, and Distances
        
        # Add Complete Polygon button (initially hidden
        self.complete_polygon_button = QPushButton("Complete Polygon")
        self.complete_polygon_button.setVisible(False)  # Start hidden
        self.pillar_dimension = QPushButton("Pillar Dimensions") 

        self.cut_hill_button = QPushButton("Cut Hill")
        self.excavate_button = QPushButton("Excavate and Remove")
        self.excavate_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;  /* Red color for destructive action */
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C82333;  /* Darker red on hover */
            }
            QPushButton:pressed {
                background-color: #BD2130;  /* Even darker when pressed */
            }
        """)
        self.excavate_button.setVisible(False)

        self.Ohe_angle_button = QPushButton("OHE Pole Angle with Rail")
        self.defect_angle_button = QPushButton("Angle of Defect")        
        self.all_angle_button = QPushButton("Angle")        

        self.elivation_btn_catenary_raillevel_button = QPushButton("Distance between Catenary Wire to Rail")
        self.elivation_btn_contact_raillevel_button = QPushButton("Distance between Contact Wire to Rail")

        self.elivation_btn_catenary_contact_button = QPushButton("Distance between Contact and Catenary")
        
        self.elivation_btn_catenary_contact_menu = QMenu()  # Create dropdown menu
        self.contact_action = QAction("Contact Points", self) 
        self.catenary_action = QAction("Catenary Points", self)  
        self.elivation_btn_catenary_contact_menu.addAction(self.contact_action)
        self.elivation_btn_catenary_contact_menu.addAction(self.catenary_action)
        self.elivation_btn_catenary_contact_button.setMenu(self.elivation_btn_catenary_contact_menu)
        
        # Add Complete Eclipse button (initially hidden)
        self.complete_curve_button = QPushButton("Complete Curve")
        self.complete_curve_button.setVisible(False) 

        self.baseline_button = QPushButton("Baseline")
        self.inclination_button = QPushButton("Inclination Angle")

        crop_button_row = QHBoxLayout()
        self.crop_button = QPushButton("Crop Selected Area")
        crop_button_row.addWidget(self.crop_button)
        
        self.save_crop_button = QPushButton("Save Cropped Data")
        self.save_crop_button.setEnabled(False)
        crop_button_row.addWidget(self.save_crop_button)
        self.measurement_buttons_layout.addLayout(crop_button_row)

        # Checkboxes
        self.height_check = QCheckBox("Height") # Checkbox for the height measurement
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Enter the height in meters")
        self.height_input.setValidator(QDoubleValidator(0.1, 100.0, 2))
        self.height_input.setVisible(False)

        self.depth_check = QCheckBox("Depth") # Checkbox for depth measurement
        self.depth_input = QLineEdit()
        self.depth_input.setPlaceholderText("Enter the depth in meters")
        self.depth_input.setValidator(QDoubleValidator(0.1, 100.0, 2))
        self.depth_input.setVisible(False)

        self.volume_check = QCheckBox("Volume")

        self.height_check.toggled.connect(lambda: self.depth_check.setChecked(False) if self.height_check.isChecked() else None)
        self.depth_check.toggled.connect(lambda: self.height_check.setChecked(False) if self.depth_check.isChecked() else None)
        
        # Add all buttons to layout
        self.measurement_buttons_layout.addWidget(self.line_button)
        self.measurement_buttons_layout.addWidget(self.presized_button)
        self.measurement_buttons_layout.addWidget(self.polygon_button)
        self.measurement_buttons_layout.addWidget(self.complete_polygon_button)  # Add complete button
        self.measurement_buttons_layout.addWidget(self.round_pillar_polygon_button)
        self.measurement_buttons_layout.addWidget(self.baseline_button)
        self.measurement_buttons_layout.addWidget(self.inclination_button)
        self.measurement_buttons_layout.addWidget(self.pillar_dimension)
        self.measurement_buttons_layout.addWidget(self.Ohe_angle_button)
        self.measurement_buttons_layout.addWidget(self.all_angle_button)    
        self.measurement_buttons_layout.addWidget(self.defect_angle_button)
        self.measurement_buttons_layout.addWidget(self.elivation_btn_catenary_raillevel_button)
        self.measurement_buttons_layout.addWidget(self.elivation_btn_contact_raillevel_button)
        self.measurement_buttons_layout.addWidget(self.complete_curve_button)  # Add complete button
        self.measurement_buttons_layout.addWidget(self.elivation_btn_catenary_contact_button)
        self.measurement_buttons_layout.addWidget(self.cut_hill_button)
        self.measurement_buttons_layout.addWidget(self.excavate_button)
        
        self.measurement_buttons_layout.addWidget(self.depth_check)
        self.measurement_buttons_layout.addWidget(self.depth_input)

        self.measurement_buttons_layout.addWidget(self.height_check)
        self.measurement_buttons_layout.addWidget(self.height_input)

        self.measurement_buttons_layout.addWidget(self.volume_check)

        # ========== (3) POLYGON-DIGGING CONNECTION ========== #
        # self.create_polygon_digging_connection_section()

        # Add the container to the main layout
        self.measurement_layout.addWidget(self.measurement_buttons_container)
        
        # Initially hide the measurement buttons
        self.measurement_buttons_container.setVisible(False)
        
        self.measurement_group.setLayout(self.measurement_layout)
        self.measurement_group.setEnabled(False)

        # Create a scroll area for the measurement section
        self.measurement_scroll = QScrollArea()
        self.measurement_scroll.setWidgetResizable(True)
        self.measurement_scroll.setWidget(self.measurement_group)
        self.measurement_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Set a fixed minimum height (e.g., 400 pixels)
        self.measurement_scroll.setMinimumHeight(200)
        self.main_measurement_layout.addWidget(self.measurement_scroll, stretch=3) 
        # self.main_measurement_layout.addWidget(self.measurement_group)

        self.measurement_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid gray;
                border-radius: 5px;
                margin: 0.2em;
                margin-top: 0.5em;
                padding-left: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)

# ==================================================================================================================================
# Define function for the Output section:
    def create_action_section(self):
        self.action_group = QGroupBox("Action")
        self.action_layout = QVBoxLayout()
        
        # Remove margins and spacing to minimize empty space
        self.action_layout.setContentsMargins(8, 3, 5, 5) 
        self.action_layout.setSpacing(3)  # Increased spacing between checkboxes
        
        # Create checkboxes directly in the layout (no extra group box)
        self.measurement_check = QCheckBox("Measurement")
        self.measurement_check.setMinimumHeight(30)  # Set minimum height for each checkbox
        self.filling_check = QCheckBox("Filling")
        self.filling_check.setMinimumHeight(30)
        self.cutting_check = QCheckBox("Cutting")
        self.cutting_check.setMinimumHeight(30)
        self.extraction_check = QCheckBox("Extraction")
        self.extraction_check.setMinimumHeight(30)
        self.railway_measurement_check = QCheckBox("Railway Measurement")
        self.railway_measurement_check.setMinimumHeight(30)
        
        # Initially disable all checkboxes (will be enabled after Start Measurement)
        self.measurement_check.setEnabled(False)
        self.filling_check.setEnabled(False)
        self.cutting_check.setEnabled(False)
        self.extraction_check.setEnabled(False)
        self.railway_measurement_check.setEnabled(False)
        
        # Add checkboxes directly to the layout with proper spacing
        self.action_layout.addWidget(self.measurement_check)
        self.action_layout.addSpacing(3)  # Add extra spacing between checkboxes
        self.action_layout.addWidget(self.filling_check)
        self.action_layout.addSpacing(3)  # Add extra spacing between checkboxes
        self.action_layout.addWidget(self.cutting_check)
        self.action_layout.addSpacing(3)  # Add extra spacing between checkboxes
        self.action_layout.addWidget(self.extraction_check)
        self.action_layout.addSpacing(3)  # Add extra spacing between checkboxes
        self.action_layout.addWidget(self.railway_measurement_check)
        
        # ========== DIGGING POINT SECTION (TOP) ========== #
        self.digging_point_input = DiggingPointInput(self)
        self.action_layout.addWidget(self.digging_point_input)
        self.digging_point_input.setVisible(False)
        
        # ========== FINALIZE LAYOUT ========== #
        self.action_group.setLayout(self.action_layout)
        
        # Set fixed height for the action group (200 as requested)
        self.action_group.setFixedHeight(170)
        
        # Add attribute to store cropped data
        self.cropped_cloud = None
        
        # Add the action group directly to the left layout (no scroll area)
        self.main_measurement_layout.addWidget(self.action_group)

        self.action_group.setStyleSheet("""
            QGroupBox {
            border: 1px solid gray;
            border-radius: 5px;
            margin-top: 0.5em;
            }
            QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
            }
            """)
        
# ==================================================================================================================================   
# Define function for the Output section:
    def create_output_section(self):
        self.output_group = QGroupBox("Output") # Section Name
        self.output_layout = QVBoxLayout()

        # Remove margins and spacing to minimize empty space
        self.output_layout.setContentsMargins(5, 5, 5, 5) 
        self.output_layout.setSpacing(3)
        
        self.output_list = QListWidget()
        self.output_list.setMinimumHeight(150)

        self.output_list.setStyleSheet("""
            QListWidget {
                font-size: 17px;  /* Increase font size for output text */
                font-family: Bold;
            }
            QListWidget::item {
                padding: 5px;  /* Add padding for better readability */
            }
        """)
        
        # Add output list to the group
        self.output_layout.addWidget(self.output_list)
        
        # Create Report Button with dropdown menu
        self.save_layer_button = QPushButton("Save Layer")

        self.output_layout.addWidget(self.save_layer_button)
        
        self.output_group.setLayout(self.output_layout)
        self.main_measurement_layout.addWidget(self.output_group)

        self.output_group.setStyleSheet("""
            QGroupBox {
            border: 1px solid gray;
            border-radius: 5px;
            margin-top: 0.5em;
            }
            QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
            }
            """)
        
    def setup_scroll_behavior(self):
        """Setup proper scroll behavior for the right section.

        Floating overlay buttons (3D cube, camera, rotation badge, left-panel
        toggle) are parented to central_widget and positioned via mapTo().
        They only reposition on resizeEvent by default, so when the user
        scrolls the right_scroll_area the VTK container shifts but the overlays
        stay put — causing visual conflicts / drift.

        Fix: keep the 3D/camera overlays fixed to the VTK viewer; only the
        left drawer continues to use layout-based repositioning.
        """
        # ── Connect the main right scroll-area vertical bar ──────────────────
        if hasattr(self, 'right_scroll_area') and self.right_scroll_area:
            vsb = self.right_scroll_area.verticalScrollBar()
            if vsb:
                try:
                    vsb.valueChanged.disconnect(self._on_scroll_value_changed)
                except TypeError:
                    pass
            # Viewport event filter (for wheel-blocking logic — unchanged)
            self.right_scroll_area.viewport().installEventFilter(self)

        # ── Event filters for scale section widgets (unchanged) ───────────────
        if hasattr(self, 'scale_section') and self.scale_section:
            self.scale_section.installEventFilter(self)
        if hasattr(self, 'volume_slider') and self.volume_slider:
            self.volume_slider.installEventFilter(self)
        if hasattr(self, 'scale_canvas') and self.scale_canvas:
            self.scale_canvas.installEventFilter(self)

    def _on_scroll_value_changed(self, _value):
        """Scroll handler intentionally left empty for the fixed VTK overlays."""
        return

    def _reposition_all_overlays(self):
        """Reposition every floating overlay so they stay locked to the viewer
        after a scroll event. Called via the debounce timer at ≤60 fps."""
        if hasattr(self, 'threeD_button'):
            self.update_3d_button_position()
        if hasattr(self, 'left_toggle_btn'):
            self.update_left_panel_position()



    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'sim_stage_label') and self.sim_stage_label.isVisible():
            self.update_sim_label_position()
        # Update floating 3D button position when window resizes
        if hasattr(self, 'threeD_button'):
            self.update_3d_button_position()
        # Update left overlay panel position when window resizes
        if hasattr(self, 'left_toggle_btn'):
            self.update_left_panel_position()

    # =========================================================================
    # Left Overlay Panel Helpers
    # =========================================================================
    def update_left_panel_position(self):
        """
        Positions the left overlay panel and its toggle tab relative to the
        VTK viewer (body_widget) in central_widget coordinates.
        The panel drawer slides from the left edge of the viewer.
        The toggle tab sits at the left edge of the viewer, vertically centred.

        IMPORTANT: When the panel is closed, it is moved completely off-screen
        (negative x) so that Qt never paints any part of it over the VTK /
        middle section.  Only when open is it moved to the visible position.
        """
        cw = self.centralWidget()
        if not cw or not hasattr(self, 'body_widget') or not hasattr(self, 'left_toggle_btn'):
            return

        # Map body_widget top-left corner to central_widget coords
        bw_origin = self.body_widget.mapTo(cw, QPoint(0, 0))
        bw_h = self.body_widget.height()

        panel_w = 360   # wider overlay panel width (fixed)
        panel_h = bw_h  # full height of viewer body
        tab_h   = self.left_toggle_btn.height()

        self.left_section.setFixedSize(panel_w, panel_h)

        panel_open = getattr(self, '_left_panel_open', False)

        if panel_open:
            # Panel visible: place flush at the LEFT edge of body_widget
            panel_x = bw_origin.x()
            panel_y = bw_origin.y()
            self.left_section.move(panel_x, panel_y)
            self.left_section.raise_()

            # Toggle tab protrudes to the RIGHT of the open panel
            tab_x = panel_x + panel_w
            tab_y = bw_origin.y() + max(0, (bw_h - tab_h) // 2)
            self.left_toggle_btn.move(tab_x, tab_y)
            self.left_toggle_btn.raise_()
        else:
            # Panel closed: push it COMPLETELY OFF-SCREEN so Qt never
            # paints any pixel of it over the main viewer area.
            self.left_section.move(-(panel_w + 20), 0)
            # left_section should already be hidden; ensure it stays hidden
            self.left_section.setVisible(False)

            # Toggle tab rests at the viewer's left edge when closed
            tab_x = bw_origin.x()
            tab_y = bw_origin.y() + max(0, (bw_h - tab_h) // 2)
            self.left_toggle_btn.move(tab_x, tab_y)
            self.left_toggle_btn.raise_()

    def _open_left_panel(self):
        """Open the left overlay panel (asset drawer)."""
        if not hasattr(self, 'left_section') or not hasattr(self, 'left_toggle_btn'):
            return
        self._left_panel_open = True
        self._left_panel_user_hidden = False
        self.update_left_panel_position()   # positions panel + moves tab to right side
        self.left_section.setVisible(True)
        self.left_section.raise_()
        # Switch to the close (right-pointing) icon
        if hasattr(self, '_icon_close'):
            self.left_toggle_btn.setIcon(self._icon_close)
        self.left_toggle_btn.setToolTip("Close Assets Panel")
        self.left_toggle_btn.raise_()

    def _close_left_panel(self):
        """Close the left overlay panel (asset drawer)."""
        if not hasattr(self, 'left_section') or not hasattr(self, 'left_toggle_btn'):
            return
        self._left_panel_open = False
        self._left_panel_user_hidden = True

        # Hide immediately and move off-screen so Qt cannot paint any ghost
        # of the panel over the VTK / middle section.
        self.left_section.setVisible(False)
        self.left_section.move(-(self.left_section.width() + 20), 0)

        # Reposition the toggle tab to the viewer's left edge
        self.update_left_panel_position()

        # Force the central widget to repaint the area where the panel was,
        # clearing any residual pixels (e.g. the purple Worksheets header).
        cw = self.centralWidget()
        if cw:
            cw.update()
            cw.repaint()

        # Switch back to the open (right-pointing arrow) icon
        if hasattr(self, '_icon_open'):
            self.left_toggle_btn.setIcon(self._icon_open)
        self.left_toggle_btn.setToolTip("Open Assets Panel")

    def update_sim_label_position(self):
        if hasattr(self, 'sim_stage_label') and hasattr(self, 'vtk_container'):
            # Force layout to update so widths are correct
            self.sim_stage_label.adjustSize()
            container_width = self.vtk_container.width()
            label_width = self.sim_stage_label.width()
            # Calculate center X
            x = (container_width - label_width) // 2
            # Set Y at 20px from top
            self.sim_stage_label.move(x, 20)
            self.sim_stage_label.raise_()

    def update_3d_button_position(self):
        """
        Position the floating 3D cube button, UNLOCKED badge and camera button
        inside the VTK viewer itself so scrolling the outer layout cannot move them.

        All coordinates are computed in scroll-viewport local space so the overlay
        widgets stay visible even when the right panel scrolls.
        """
        if not hasattr(self, 'vtk_widget') or not hasattr(self, 'threeD_button'):
            return

        if not hasattr(self, 'right_scroll_area') or not self.right_scroll_area:
            return

        viewport = self.right_scroll_area.viewport()
        if not viewport:
            return

        # Anchor to the visible top-right corner of the scroll viewport.
        origin_x = viewport.width()
        origin_y = 0

        margin_x   = 28    # gap from right edge of viewer (moved slightly left)
        margin_y   = 6     # gap from top edge of viewer
        vertical_gap = 8   # gap between stacked buttons

        self.threeD_button.adjustSize()
        btn_w = self.threeD_button.width()
        btn_h = self.threeD_button.height()

        # 3D cube button — top-right, fixed
        x = origin_x - btn_w - margin_x
        y = origin_y + margin_y
        self.threeD_button.move(x, y)
        self.threeD_button.raise_()

        # UNLOCKED / LOCKED badge — centred below the cube button
        if hasattr(self, 'rotation_state_badge'):
            self.rotation_state_badge.adjustSize()
            badge_w = self.rotation_state_badge.width()
            badge_h = self.rotation_state_badge.height()
            badge_x = x + ((btn_w - badge_w) // 2)
            badge_y = y + btn_h + vertical_gap
            self.rotation_state_badge.move(badge_x, badge_y)
            self.rotation_state_badge.raise_()
##### Mayur Wakhare 13-07-2026 underpass camera view button
        # Track running Y coordinate to strictly prevent overlaps
        current_y = y + btn_h + vertical_gap
        if hasattr(self, 'rotation_state_badge'):
            current_y = self.rotation_state_badge.y() + self.rotation_state_badge.height() + vertical_gap

        # 1. Reset Camera View
        if hasattr(self, 'camera_floating_button'):
            self.camera_floating_button.adjustSize()
            cw = self.camera_floating_button.width()
            ch = self.camera_floating_button.height()
            cx = x + max(0, (btn_w - cw) // 2)
            self.camera_floating_button.move(cx, current_y)
            self.camera_floating_button.raise_()
            if self.camera_floating_button.isVisible():
                current_y += ch + vertical_gap

        # 2. Tunnel Camera View
        if hasattr(self, 'tunnel_camera_button'):
            self.tunnel_camera_button.adjustSize()
            tw = self.tunnel_camera_button.width()
            th = self.tunnel_camera_button.height()
            tx = x + max(0, (btn_w - tw) // 2)
            self.tunnel_camera_button.move(tx, current_y)
            self.tunnel_camera_button.raise_()
            if self.tunnel_camera_button.isVisible():
                current_y += th + vertical_gap

        # 3. Underpass Camera View
        if hasattr(self, 'underpass_camera_button'):
            self.underpass_camera_button.adjustSize()
            uw = self.underpass_camera_button.width()
            uh = self.underpass_camera_button.height()
            ux = x + max(0, (btn_w - uw) // 2)
            self.underpass_camera_button.move(ux, current_y)
            self.underpass_camera_button.raise_()
            if self.underpass_camera_button.isVisible():
                current_y += uh + vertical_gap

        # --- User requested debug logs ---
        if hasattr(self, 'camera_floating_button'):
            print(f"Reset Button Y: {self.camera_floating_button.y()}")
        if hasattr(self, 'tunnel_camera_button'):
            print(f"Tunnel Button Y: {self.tunnel_camera_button.y()}")
        if hasattr(self, 'underpass_camera_button'):
            print(f"Underpass Button Y: {self.underpass_camera_button.y()}")
            
        print("Function modifying geometry: update_3d_button_position")

            ##########################################################
            ## Mayur Wakhare 10-7-2026 robot bar button right side tunnel
        print(f"""
DEBUG INFO:
Camera button:
- objectName: {self.camera_floating_button.objectName()}
- className: {self.camera_floating_button.__class__.__name__}
- geometry: {self.camera_floating_button.geometry()}

Tunnel Camera View button:
- objectName: {self.tunnel_camera_button.objectName()}
- className: {self.tunnel_camera_button.__class__.__name__}
- geometry: {self.tunnel_camera_button.geometry()}
""")
########################################################################################

###### Mayur Wakhare 10-7-2026 robot bar button right side tunnel
        # Tunnel Control Bar
        if hasattr(self, 'tunnel_control_bar') and self.tunnel_control_bar.isVisible():
            tcb_w = self.tunnel_control_bar.width()
            tcb_h = self.tunnel_control_bar.height()
            
          ## Mayur Wakhare 13-07-2026 underpass camera button -> 4 buttons position
            if hasattr(self, 'underpass_camera_button') and self.underpass_camera_button.isVisible():
                geom = self.underpass_camera_button.geometry()
                
                # Center horizontally relative to Underpass Camera View button
                cx = geom.center().x() - tcb_w // 2
                
                if cx + tcb_w > geom.right():
                    cx = geom.right() - tcb_w
                
                # Place directly below with a 20px gap
                cy = geom.bottom() + 20
                self.tunnel_control_bar.move(cx, cy)
            elif hasattr(self, 'tunnel_camera_button') and self.tunnel_camera_button.isVisible():
                ###########################################################
                geom = self.tunnel_camera_button.geometry()
                
                # Center horizontally relative to Tunnel Camera View button
                cx = geom.center().x() - tcb_w // 2
                
                # Clamp horizontally so it NEVER overlaps the right-side toolbar/panel.
                # Because the button is close to the right edge, centering a 128px hub pushes it past the edge.
                if cx + tcb_w > geom.right():
                    cx = geom.right() - tcb_w
                
                # Place directly below with a 20px gap
                cy = geom.bottom() + 20
                self.tunnel_control_bar.move(cx, cy)
            elif hasattr(self, 'vtk_container'):
                # Fallback if tunnel_camera_button is hidden
                cx = self.vtk_container.x() + self.vtk_container.width() - tcb_w - 20
                cy = self.vtk_container.y() + (self.vtk_container.height() - tcb_h) // 2
                self.tunnel_control_bar.move(cx, cy)
 ##########################################################################################               
            self.tunnel_control_bar.raise_()

        # ── Three view shortcut buttons (TOP / LEFT / Right) ──
        if (hasattr(self, 'view_top_button') and
                hasattr(self, 'view_left_button') and
                hasattr(self, 'view_right_button') and
                hasattr(self, 'camera_floating_button')):

            cam_x = self.camera_floating_button.x()
            cam_y = self.camera_floating_button.y()
            cam_w = self.camera_floating_button.width()
            cam_h = self.camera_floating_button.height()

            vb_size = self.view_top_button.width()
            gap     = 8

            v_step = cam_h + gap

            # TOP  → same row as camera, flush left of camera with gap
            top_x = cam_x - gap - vb_size
            top_y = cam_y

            # LEFT → one row below TOP, same column as TOP
            left_x = top_x
            left_y = cam_y + v_step

            # Right → one row below camera, same column as camera
            right_x = cam_x
            right_y = cam_y + v_step

            for btn, bx, by in [
                (self.view_top_button,   top_x,   top_y),
                (self.view_left_button,  left_x,  left_y),
                (self.view_right_button, right_x, right_y),
            ]:
                btn.move(bx, by)
                btn.raise_()

    def update_rotation_state_badge(self):
        """Refresh the lock/unlock badge text and colors."""
        if not hasattr(self, 'rotation_state_badge'):
            return

        locked = bool(getattr(self, 'threeD_mode_active', False))
        if locked:
            self.rotation_state_badge.setText("LOCKED")
            self.rotation_state_badge.setStyleSheet("""
                #RotationStateBadge {
                    background-color: #C62828;
                    color: white;
                    border: 1px solid #8E0000;
                    border-radius: 11px;
                    padding-left: 6px;
                    padding-right: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            self.rotation_state_badge.setToolTip("Rotation is locked to the configured limits")
        else:
            self.rotation_state_badge.setText("UNLOCKED")
            self.rotation_state_badge.setStyleSheet("""
                #RotationStateBadge {
                    background-color: #2E7D32;
                    color: white;
                    border: 1px solid #1B5E20;
                    border-radius: 11px;
                    padding-left: 6px;
                    padding-right: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """)
            self.rotation_state_badge.setToolTip("Rotation is free and can move 360 degrees")

        self.rotation_state_badge.adjustSize()
        self.rotation_state_badge.raise_()
        self.update_3d_button_position()

# ================= Aniket updated 07-05-2026: Add 3D rotation lock functionality ================= #
    def on_3d_button_clicked(self):
        """Handler for 3D button. Toggles bounded rotation lock and provides feedback."""
        locked = self.threeD_button.isChecked()
        self.threeD_mode_active = locked
        if locked:
            self.threeD_button.setToolTip("Unlock 360 Rotation")
            self.apply_rotation_constraint()
        else:
            self.threeD_button.setToolTip("Lock 360 Rotation")
            self.remove_rotation_constraint()
        self.update_rotation_state_badge()
## Mayur Wakhare 01-07-2026 Camera Button 
    def on_tunnel_camera_button_clicked(self):
        ### Mayur Wakhare 13-7-2026 underpass camera 
        self._underpass_camera_active = False
###################################################################
        """Read the tunnel definition from the active design configuration/model data
        instead of VTK actors. Uses design.tunnel as the authoritative source.
        Stores the detected tunnel model data for future camera calculations.
        No camera movement happens here.
        """
        print("\n[TunnelCamera]")
        print("- Button Clicked")
        import os
        import json

        layer_folder = getattr(self, 'current_design_layer_path', None)
        subfolder = getattr(self, 'current_subfolder_type', 'designs')
        
        # Fallback for resolving the active path
        if not layer_folder or not os.path.exists(layer_folder):
            ws_name = getattr(self, 'current_worksheet_name', '')
            base_dir = getattr(self, 'WORKSHEETS_BASE_DIR', '')
            layer_name = getattr(self, 'current_layer_name', '')
            if base_dir and ws_name and layer_name:
                layer_folder = os.path.join(base_dir, ws_name, subfolder, layer_name)

        mode_str = 'Merged' if subfolder == 'merger' else 'Single'
        print(f"- Current Mode: {mode_str}")
        
        viewer_addr = hex(id(self.vtk_widget)) if hasattr(self, 'vtk_widget') else 'None'
        print(f"- Active Viewer Address: {viewer_addr}")

        config_paths = []
    ###### Mayur 17-7-2026 Tunnel camera view id selection    
        # 1. Gather ALL actively rendered layers from the 3D viewer state
        active_layer_paths = list(getattr(self, '_per_layer_actors', {}).keys())
        
        # 2. Add the currently selected folder as a fallback if not in active paths
        if layer_folder and os.path.exists(layer_folder) and layer_folder not in active_layer_paths:
            active_layer_paths.append(layer_folder)

        # 3. Process every active path to find design configurations
        for p in active_layer_paths:
            if not p or not isinstance(p, str) or not os.path.exists(p):
                continue
                
            is_merger = False
            # Check if this is a merger folder by checking for .json files with merger_points
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
                        
            # If not a merger folder, just add its own design config
            if not is_merger:
                cfg = os.path.join(p, 'design_construction_config.json')
                if os.path.exists(cfg) and cfg not in config_paths:
                    config_paths.append(cfg)
                    
        active_layer_count = len(config_paths)
        print(f"- Active Layer Count: {active_layer_count}")
#########################################################################################################
        # Search for design.tunnel
        found_tunnels = []
        for cp in config_paths:
            try:
                with open(cp, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                tunnel_obj = data.get('design', {}).get('tunnel')
                
                # Check for zero_line_config fallback if tunnel not found
                if not tunnel_obj:
                    zero_config = data.get('design', {}).get('zero_line_config')
                    if zero_config:
                        tunnel_obj = {
                            'id': 'fallback_tunnel',
                            'start_km': zero_config.get('point1', {}).get('from_km', 0),
                            'start_chainage': zero_config.get('point1', {}).get('from_chainage', 0),
                            'end_km': zero_config.get('point2', {}).get('to_km', 0),
                            'end_chainage': zero_config.get('point2', {}).get('to_chainage', 0),
                            'radius': 5.0
                        }

                if tunnel_obj and isinstance(tunnel_obj, dict):
                    tunnel_obj['source_layer_folder'] = os.path.dirname(cp)
                    found_tunnels.append(tunnel_obj)
            except Exception as e:
                pass
                
        print(f"- Tunnel Count: {len(found_tunnels)}")
        
        # Process results
 ###### Mayur 17-7-2026 tunnel camere view buuton to show active layers
        # Debug info
        active_layers_debug = set()
        tunnel_count_per_layer = {}
        tunnel_ids_per_layer = {}

        # Deduplicate found tunnels
        unique_tunnels = {}
        import os
        for t in found_tunnels:
            tid = t.get('tunnel_id', t.get('id', 'Unknown'))
            layer_folder = t.get('source_layer_folder', '')
            layer_name = os.path.basename(layer_folder) if layer_folder else 'Unknown'
            
            active_layers_debug.add(layer_name)
            tunnel_count_per_layer[layer_name] = tunnel_count_per_layer.get(layer_name, 0) + 1
            if layer_name not in tunnel_ids_per_layer:
                tunnel_ids_per_layer[layer_name] = []
            tunnel_ids_per_layer[layer_name].append(tid)
            
            key = (layer_name, tid)
            if key not in unique_tunnels:
                unique_tunnels[key] = (t, layer_name, tid)
                
        print("\nActive merged layers:")
        print(f"Layers scanned: {list(active_layers_debug)}")
        for ln in active_layers_debug:
            print(f"Tunnels found in {ln}: {tunnel_count_per_layer.get(ln, 0)}")
        print(f"Final dropdown list: {len(unique_tunnels)}\n")
                
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
        dlg = QDialog(self)
        dlg.setWindowTitle("Tunnel Selection")
        dlg.resize(300, 100)
        
        layout = QVBoxLayout(dlg)
        
        info_label = QLabel("Tunnel Information")
        layout.addWidget(info_label)
        
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("Tunnel ID:"))
        tunnel_combo = QComboBox()
        
        if not unique_tunnels:
            tunnel_combo.addItem("No Tunnel Available")
            tunnel_combo.setEnabled(False)
        else:
            for key, (t, layer_name, tid) in unique_tunnels.items():
                display_text = f"{tid} ({layer_name})"
                tunnel_combo.addItem(display_text, userData=t)
            
        combo_layout.addWidget(tunnel_combo)
        layout.addLayout(combo_layout)
        
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        
        if not unique_tunnels:
            btn_ok.setEnabled(False)
            
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        btn_ok.clicked.connect(dlg.accept)
        btn_cancel.clicked.connect(dlg.reject)
        
        if dlg.exec_() != QDialog.Accepted:
            return
            
        target_tunnel = tunnel_combo.currentData()
        
        if target_tunnel:
            #########################################################################################
            self._tunnel_camera_target = target_tunnel
            active_tunnel_id = target_tunnel.get('id', target_tunnel.get('tunnel_id', 'N/A'))
            target_layer = target_tunnel.get('source_layer_folder', '')
            layer_name = os.path.basename(target_layer) if target_layer else 'Unknown'
            
            print(f"Selected Tunnel ID: {active_tunnel_id}")
            print(f"Selected Layer: {layer_name}")
            print(f"Matched Tunnel: {target_tunnel}")
            print(f"Camera initialized for: {active_tunnel_id} in {layer_name}")
            
            # Calculate dimensions for logging
            try:
                start_ch_abs = float(target_tunnel.get('start_km', 0)) * 1000.0 + float(target_tunnel.get('start_chainage', 0))
                end_ch_abs = float(target_tunnel.get('end_km', 0)) * 1000.0 + float(target_tunnel.get('end_chainage', 0))
                
                # Use global offset if available to ensure correct chainage mapping
                global_start_offset = 0.0
                if hasattr(self, 'zero_start_km') and getattr(self, 'zero_start_km') is not None:
                    global_start_offset = float(getattr(self, 'zero_start_km')) * 1000.0 + float(getattr(self, 'zero_start_chainage', 0.0))
                
                # Auto-correct if user left KM as 0 but project starts at a high KM
                if float(target_tunnel.get('start_km', 0)) == 0 and global_start_offset > 1000.0:
                    start_ch_abs += global_start_offset
                if float(target_tunnel.get('end_km', 0)) == 0 and global_start_offset > 1000.0:
                    end_ch_abs += global_start_offset

                length = end_ch_abs - start_ch_abs
                wall_t = target_tunnel.get('wall_thickness', 'N/A')
                dimensions_str = f"Length={length:.2f}m, Wall Thickness={wall_t}m"

                print(f"Tunnel dimensions: {dimensions_str}")
                print("Tunnel successfully selected.")

                # -------------------------------------------------------------
                # Centerline and Road Surface Calculation
                # -------------------------------------------------------------
                if hasattr(self, 'get_curve_aware_path'):
                    # get_curve_aware_path returns (chainage, pos_xyz, perp_vec, dir_vec)
                    # pos_xyz uses the road_surface_baseline Z elevation automatically
                    path_samples = self.get_curve_aware_path(start_ch_abs - 5.0, end_ch_abs, step=1.0, target_layer=target_layer)
                  ######### Mayur Wakhare 10-7-2026 tunnel camera right side buttons   
                    master_samples_count = len(getattr(self, 'master_curved_path_samples', [])) if hasattr(self, 'master_curved_path_samples') and getattr(self, 'master_curved_path_samples') else 0
                    
                    if path_samples:
                        print(f"- Navigation Path Available: Yes")
                        print(f"- Path Sample Count: {len(path_samples)}")
                        if len(path_samples) >= 2:
                            print("- Camera Initialized: Yes")
                        else:
                            print("- Camera Initialized: No")
                            print("- Initialization Failed Reason: Navigation Path Size < 2.")
                    else:
                        print(f"- Navigation Path Available: No")
                        print(f"- Path Sample Count: 0")
                        print("- Camera Initialized: No")
                        print("- Initialization Failed Reason: Navigation Path is empty.")
                    ##########################################################################
                    if path_samples and len(path_samples) >= 2:
                        start_sample = path_samples[0]
                        end_sample = path_samples[-1]
                        mid_idx = len(path_samples) // 2
                        center_sample = path_samples[mid_idx]

                        # Store calculated properties (Camera logic will use these later)
                        self._tunnel_centerline = path_samples
                        self._tunnel_forward_dir = center_sample[3]     # d_vec (forward direction)
                        self._tunnel_center_point = center_sample[1]    # pos_xyz [x,y,z]
                        self._tunnel_road_surface_z = center_sample[1][2] # Z elevation from road surface
                        
                        # Print requested debug logs
                        print(f"Tunnel start position: ({start_sample[1][0]:.2f}, {start_sample[1][1]:.2f}, {start_sample[1][2]:.2f})")
                        print(f"Tunnel end position: ({end_sample[1][0]:.2f}, {end_sample[1][1]:.2f}, {end_sample[1][2]:.2f})")
                        print(f"Tunnel center position: ({center_sample[1][0]:.2f}, {center_sample[1][1]:.2f}, {center_sample[1][2]:.2f})")
                        print(f"Forward direction vector: ({center_sample[3][0]:.4f}, {center_sample[3][1]:.4f}, {center_sample[3][2]:.4f})")
                        print(f"Road surface elevation: {center_sample[1][2]:.2f}")

                        # -- INITIAL CAMERA PLACEMENT (Dual-Reference System) --
                        if hasattr(self, 'renderer') and self.renderer:
                            self._tunnel_h_val = float(target_tunnel.get('tunnel_height', target_tunnel.get('height', target_tunnel.get('arch_radius', target_tunnel.get('radius', 5.0)))))

                            # ── Identify tunnel entry in road surface path ──
                            tunnel_entry_idx_in_path = 0
                            for i, sample in enumerate(path_samples):
                                if sample[0] >= start_ch_abs:
                                    tunnel_entry_idx_in_path = i
                                    break

                            entry_sample = path_samples[tunnel_entry_idx_in_path]
                            entry_pos  = entry_sample[1]   # [x, y, z]
                            entry_fwd_raw = entry_sample[3] # forward direction (may not be unit length)
                            entry_perp = entry_sample[2]    # perpendicular vector
######## Mayur Wakhare 13-07-2026 tunnel camera view
                            # === DIAGNOSTIC LOGGING FOR USER COMPARISON ===
                            print("\n" + "="*50)
                            print(f"--- TUNNEL CAMERA INIT MODE: {'MERGED' if subfolder == 'merger' else 'SINGLE'} ---")
                            print(f"master_curved_path_samples length: {master_samples_count}")
                            if master_samples_count > 0:
                                print(f"master_curved_path_samples[0] chainage: {self.master_curved_path_samples[0]['ch']}")
                                print(f"master_curved_path_samples[-1] chainage: {self.master_curved_path_samples[-1]['ch']}")
                            print(f"tunnel_entry_position (start_ch_abs={start_ch_abs}): {entry_pos}")
                            print(f"tunnel_exit_position (end_ch_abs={end_ch_abs}): {path_samples[-1][1]}")
                            print(f"navigation_path length: {len(path_samples)}")
                            if len(path_samples) > 1:
                                print(f"path ordering (first 2 ch): {path_samples[0][0]}, {path_samples[1][0]}")
                                print(f"path ordering (last 2 ch): {path_samples[-2][0]}, {path_samples[-1][0]}")
                            print(f"path index (tunnel_entry_idx_in_path): {tunnel_entry_idx_in_path}")
                            print(f"dir_vec (entry_fwd_raw): {entry_fwd_raw}")
                            print(f"tangent vector (from path logic): {entry_fwd_raw}")
                            print(f"normal (entry_perp): {entry_perp}")
                            print("="*50 + "\n")
                            # ===============================================
#############################################################################################
                            # ── Normalize forward vector (XY) ──
                            # get_curve_aware_path dir_vec may NOT be unit-length.
                            # Without normalization, '10m offset' could be < 1m.
                            import math
                            fwd_mag_xy = math.sqrt(entry_fwd_raw[0]**2 + entry_fwd_raw[1]**2)
                            if fwd_mag_xy < 1e-9:
                                fwd_mag_xy = 1.0  # safety fallback
                            entry_fwd = [
                                entry_fwd_raw[0] / fwd_mag_xy,
                                entry_fwd_raw[1] / fwd_mag_xy,
                                entry_fwd_raw[2] / fwd_mag_xy if fwd_mag_xy > 1e-9 else 0.0,
                            ]


                            # ── Create synthetic pre-entry path (straight line) ──
                            # Road path may NOT exist outside the tunnel, so we build
                            # a straight approach segment from tunnel entry coordinates.
                            DEFAULT_PRE_ENTRY_OFFSET = 50.0  # configurable: camera starts this far before tunnel
                            num_pre_points = int(DEFAULT_PRE_ENTRY_OFFSET)  # 1 point per metre
                            pre_entry_path = []
                            for pi in range(num_pre_points):
                                dist_back = float(num_pre_points - pi)  # 50, 49, … 1
                                synth_ch = start_ch_abs - dist_back
                                synth_pos = [
                                    entry_pos[0] - entry_fwd[0] * dist_back,
                                    entry_pos[1] - entry_fwd[1] * dist_back,
                                    entry_pos[2],  # same Z as tunnel entry (no terrain)
                                ]
                                pre_entry_path.append((synth_ch, synth_pos, entry_perp, entry_fwd))

                            # ── Build combined navigation path ──
                            road_path_from_entry = path_samples[tunnel_entry_idx_in_path:]
                            combined_path = pre_entry_path + road_path_from_entry

                            self._fly_path        = combined_path
                            self._tunnel_entry_idx = num_pre_points   # index where tunnel begins
                            self._tunnel_entry_pos = list(entry_pos)  # tunnel entry X,Y,Z
                            self._tunnel_entry_fwd = list(entry_fwd)  # NORMALIZED forward at entry
                            self._pre_entry_offset = DEFAULT_PRE_ENTRY_OFFSET  # store for camera methods
                            self._fly_speed = 0.25  # moderate speed
                            
                            is_resuming = hasattr(self, '_saved_tunnel_cam_pos') and self._saved_tunnel_cam_pos is not None
                            if not is_resuming:
                                self._fly_idx  = 0
                                self._fly_t    = 0.0

                            # Automatically set near/far clipping range BEFORE rendering
                            tunnel_length_safe = max(50.0, float(length))
                            self.renderer.GetActiveCamera().SetClippingRange(0.5, tunnel_length_safe + 200.0)

                            # Debug
                            print(f"")
                            print(f"{'='*60}")
                            print(f"  Camera Placement (pre-entry offset = {DEFAULT_PRE_ENTRY_OFFSET}m)")
                            print(f"{'='*60}")
                            print(f"Tunnel entry position:  ({entry_pos[0]:.2f}, {entry_pos[1]:.2f}, {entry_pos[2]:.2f})")
                            print(f"Tunnel entry forward (normalized): ({entry_fwd[0]:.6f}, {entry_fwd[1]:.6f}, {entry_fwd[2]:.6f})")
                            print(f"Pre-entry offset: {DEFAULT_PRE_ENTRY_OFFSET}m, Pre-entry points: {num_pre_points}, Road path points: {len(road_path_from_entry)}")
                            print(f"Total navigation path: {len(combined_path)} points")
                            print(f"Tunnel entry at path index: {self._tunnel_entry_idx}")
                            first_synth = pre_entry_path[0][1]
                            print(f"First pre-entry point (should be -{DEFAULT_PRE_ENTRY_OFFSET:.0f}m): ({first_synth[0]:.2f}, {first_synth[1]:.2f}, {first_synth[2]:.2f})")
                            synth_dist = math.sqrt((first_synth[0] - entry_pos[0])**2 + (first_synth[1] - entry_pos[1])**2)
                            print(f"Distance from first synth to entry: {synth_dist:.2f}m (should be ~{DEFAULT_PRE_ENTRY_OFFSET:.0f}m)")
                            print(f"------------------------------")

                            is_resuming = hasattr(self, '_saved_tunnel_cam_pos') and self._saved_tunnel_cam_pos is not None
                            if is_resuming:
                                if hasattr(self, 'renderer') and self.renderer:
                                    camera = self.renderer.GetActiveCamera()
                                    camera.SetPosition(*self._saved_tunnel_cam_pos)
                                    camera.SetFocalPoint(*self._saved_tunnel_cam_fp)
                                    self.vtk_widget.GetRenderWindow().Render()
                                cam_after = self.renderer.GetActiveCamera().GetPosition()
                                # Clear the saved state so Stop can save a new state later
                                self._saved_tunnel_cam_pos = None
                                self._saved_tunnel_cam_fp = None
                            else:
                                # ── Block slider signals to prevent override ──
                                if hasattr(self, 'tc_slider'):
                                    self.tc_slider.blockSignals(True)
                                    self.tc_slider.setValue(0)
                                    self.tc_slider.blockSignals(False)

                                # Initialize camera outside the entrance
                                self._set_camera_to_initial_outside_view()

                                # Verify camera position immediately after SetPosition
                                cam_after = self.renderer.GetActiveCamera().GetPosition()
                                #### Mayur Wakhare 13-07-2026 
                                cam_fp = self.renderer.GetActiveCamera().GetFocalPoint()

                            # === DIAGNOSTIC LOGGING FOR USER COMPARISON ===
                            try:
                                import json
                                debug_file = os.path.join(getattr(self, 'WORKSHEETS_BASE_DIR', ''), 'tunnel_camera_debug.json')
                                debug_data = {}
                                if os.path.exists(debug_file):
                                    with open(debug_file, 'r') as df:
                                        try: debug_data = json.load(df)
                                        except: pass
                                
                                mode_key = "Merged" if subfolder == "merger" else "Single"
                                debug_data[mode_key] = {
                                    "Tunnel ID": str(target_tunnel.get('uuid', 'N/A')),
                                    "Tunnel Entry Position": f"({entry_pos[0]:.2f}, {entry_pos[1]:.2f}, {entry_pos[2]:.2f})",
                                    "Tunnel Exit Position": f"({path_samples[-1][1][0]:.2f}, {path_samples[-1][1][1]:.2f}, {path_samples[-1][1][2]:.2f})",
                                    "Navigation Path Size": str(len(path_samples)),
                                    "First Path Point": f"ch={path_samples[0][0]:.2f}, pos=({path_samples[0][1][0]:.2f}, {path_samples[0][1][1]:.2f}, {path_samples[0][1][2]:.2f})",
                                    "Last Path Point": f"ch={path_samples[-1][0]:.2f}, pos=({path_samples[-1][1][0]:.2f}, {path_samples[-1][1][1]:.2f}, {path_samples[-1][1][2]:.2f})",
                                    "Current Path Index": str(tunnel_entry_idx_in_path),
                                    "Robot Spawn Position": f"({self._tunnel_entry_pos[0]:.2f}, {self._tunnel_entry_pos[1]:.2f}, {self._tunnel_entry_pos[2]:.2f})",
                                    "Robot Forward Vector": f"({self._tunnel_entry_fwd[0]:.4f}, {self._tunnel_entry_fwd[1]:.4f}, {self._tunnel_entry_fwd[2]:.4f})",
                                    "Camera Position": f"({cam_after[0]:.2f}, {cam_after[1]:.2f}, {cam_after[2]:.2f})",
                                    "Camera Focal Point": f"({cam_fp[0]:.2f}, {cam_fp[1]:.2f}, {cam_fp[2]:.2f})",
                                    "dir_vec": f"({entry_fwd_raw[0]:.4f}, {entry_fwd_raw[1]:.4f}, {entry_fwd_raw[2]:.4f})",
                                    "normal": f"({entry_perp[0]:.4f}, {entry_perp[1]:.4f}, {entry_perp[2]:.4f})",
                                    "tangent": f"({entry_fwd_raw[0]:.4f}, {entry_fwd_raw[1]:.4f}, {entry_fwd_raw[2]:.4f})"
                                }
                                with open(debug_file, 'w') as df:
                                    json.dump(debug_data, df, indent=4)
                                print(f"=== Debug data written for {mode_key} mode to {debug_file} ===")
                            except Exception as e:
                                print(f"Failed to write debug data: {e}")
                            # ===============================================
################################################################################################################

                            # Start smooth fly-through setup
                            if not hasattr(self, '_tunnel_fly_timer'):
                                self._tunnel_fly_timer = QTimer(self)
                                self._tunnel_fly_timer.timeout.connect(self._update_tunnel_flythrough)

                            if hasattr(self, 'tunnel_control_bar'):
                                if hasattr(self, 'vtk_widget') and self.vtk_widget:
                                    interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
                                    if interactor:
                                        # Capture active style and picker for debug
                                        current_style = interactor.GetInteractorStyle()
                                        style_name = current_style.__class__.__name__ if current_style else "None"
                                        current_picker = interactor.GetPicker()
                                        picker_name = current_picker.__class__.__name__ if current_picker else "None"


                                        # Save original style/picker for restoration on exit
                                        self._saved_interactor_style = current_style
                                        self._saved_picker = current_picker

                                        # Install FPS look-only interactor (no pan/zoom/pick)
                                        tunnel_style = TunnelFPSInteractorStyle(viewer=self)
                                        cam_pos = self.renderer.GetActiveCamera().GetPosition()
                                        tunnel_style.set_locked_position(*cam_pos)
                                        interactor.SetInteractorStyle(tunnel_style)
                                        interactor.SetPicker(None)
                                        self._tunnel_fps_style = tunnel_style


                                self.tunnel_control_bar.setVisible(True)
                                self.update_3d_button_position()
###### Mayur Wakhare 30-06-2026 Robot Camera control
                                print(f"- Robot Exists: Yes")
                                # ── Spawn Robot at tunnel entrance ──
                                import math as _m
                                _entry_pos = getattr(self, '_tunnel_entry_pos', None)
                                _entry_fwd = getattr(self, '_tunnel_entry_fwd', [1, 0, 0])
                                
                                _exit_pos = self._fly_path[-1][1] if hasattr(self, '_fly_path') and self._fly_path else None
                                _total_pts = len(self._fly_path) if hasattr(self, '_fly_path') else 0
                                _robot_yaw = _m.atan2(_entry_fwd[1], _entry_fwd[0])
                                
                                print("--- TUNNEL CAMERA INIT DEBUG ---")
                                print(f"Tunnel Entry Position: {_entry_pos}")
                                print(f"Tunnel Exit Position: {_exit_pos}")
                                print(f"Current Path Index: {getattr(self, '_tunnel_entry_idx', 0)}")
                                print(f"Total Path Points: {_total_pts}")
                                print(f"dir_vec: {_entry_fwd}")
                                print(f"Robot Forward Vector: ({_m.cos(_robot_yaw):.4f}, {_m.sin(_robot_yaw):.4f}, 0.0)")
                                
                                if hasattr(self, 'renderer') and self.renderer:
                                    _cam = self.renderer.GetActiveCamera()
                                    if _cam:
                                        _cp = _cam.GetPosition()
                                        _cf = _cam.GetFocalPoint()
                                        _cfx = _cf[0] - _cp[0]
                                        _cfy = _cf[1] - _cp[1]
                                        _cfz = _cf[2] - _cp[2]
                                        _cd = _m.sqrt(_cfx**2 + _cfy**2 + _cfz**2)
                                        if _cd > 0:
                                            _cfx /= _cd; _cfy /= _cd; _cfz /= _cd
                                        print(f"Camera Forward Vector: ({_cfx:.4f}, {_cfy:.4f}, {_cfz:.4f})")
                                print("--------------------------------")

                                if _entry_pos:
                                    _robot_z = _entry_pos[2]  # Road surface Z at entrance
                                    self._create_robot_actor(
                                        position=[_entry_pos[0], _entry_pos[1], _robot_z],
                                        yaw=_robot_yaw
                                    )

                                # Block signals during play-button reset — keep auto OFF (robot mode is manual)
                                ##########################################
                                self.tc_play_btn.blockSignals(True)
                                self.tc_play_btn.setChecked(False)
                                self.tc_play_btn.blockSignals(False)
                                ###### Mayur Wakhare 30-06-2026
                                # Do NOT call _toggle_tunnel_auto() — robot mode uses WASD, not auto-fly
                                #####################################
                                self.tunnel_control_bar.raise_()


                            else:
                                if hasattr(self, '_tunnel_fly_timer') and self._tunnel_fly_timer.isActive():
                                    self._tunnel_fly_timer.stop()
            except Exception as e:
                pass
        else:
            self._tunnel_camera_target = None
            print("- Active Tunnel ID: None")
            print("- Navigation Path Available: No")
            print("- Path Sample Count: 0")
            print("- Robot Exists: No")
            print("- Camera Initialized: No")
            print("- Initialization Failed Reason: No tunnel configuration found in the active layer or its merged layers.")
            try:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Tunnel Camera", "Cannot activate Tunnel Camera View.\nNo tunnel configuration found in the active layer or its merged layers.")
            except ImportError:
                pass
########## Mayur Wakhare 13-7-2026 underpass camera button clicked
    def on_underpass_camera_button_clicked(self):

        self._underpass_camera_active = True
        """Find the underpass in active config, generate a synthetic path, and reuse tunnel camera mode."""
        print("\n[Underpass Camera activated]")
        print("- Button Clicked")
        import os
        import json
        import math

        config_paths = set()
        
        # 1. Gather all directories from eye-open states
        active_layer_folders = []
        if hasattr(self, '_eye_open_states'):
            for folder, is_open in self._eye_open_states.items():
                if is_open and folder and os.path.exists(folder):
                    active_layer_folders.append(folder)
                    
        # 2. Add the current active layer folder just in case
        layer_folder = getattr(self, 'current_design_layer_path', None)
        if layer_folder and os.path.exists(layer_folder) and layer_folder not in active_layer_folders:
            active_layer_folders.append(layer_folder)
            
        # 3. Fallback to worksheet properties if still empty
        if not active_layer_folders:
            subfolder = getattr(self, 'current_subfolder_type', 'designs')
            ws_name = getattr(self, 'current_worksheet_name', '')
            base_dir = getattr(self, 'WORKSHEETS_BASE_DIR', '')
            layer_name = getattr(self, 'current_layer_name', '')
            if base_dir and ws_name and layer_name:
                folder = os.path.join(base_dir, ws_name, subfolder, layer_name)
                if os.path.exists(folder):
                    active_layer_folders.append(folder)
                    
        num_loaded = len(active_layer_folders)
        num_merged_sources = 0
        
        for folder in active_layer_folders:
            if "merger" in folder.lower():
                merger_jsons = [f for f in os.listdir(folder) if f.endswith('.json')]
                for mj in merger_jsons:
                    try:
                        with open(os.path.join(folder, mj), 'r', encoding='utf-8') as f:
                            merger_data = json.load(f)
                        for pt in merger_data.get("merger_points", []):
                            primary_src = pt.get("primary_json_path")
                            if primary_src and os.path.exists(primary_src):
                                config_paths.add(primary_src)
                                num_merged_sources += 1
                            for lyr in pt.get("layers", []):
                                src = lyr.get("json_path")
                                if src and os.path.exists(src):
                                    config_paths.add(src)
                                    num_merged_sources += 1
                    except Exception:
                        pass
            else:
                cfg = os.path.join(folder, 'design_construction_config.json')
                if os.path.exists(cfg):
                    config_paths.add(cfg)
                    
        config_paths = list(config_paths)

        print(f"- Number of loaded layers (eye open/active): {num_loaded}")
        print(f"- Number of merged source layers: {num_merged_sources}")
        print(f"- Total config files to check: {len(config_paths)}")

        # Search for underpasses
        found_underpasses = []
        for cp in config_paths:
            print(f"  Checking layer config: {cp}")
            try:
                with open(cp, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check top-level list
                ups = data.get("under_passes", [])
                
                # Check reference_assets legacy list
                ref_ups = data.get("reference_assets", {}).get("under_pass", [])
                if isinstance(ref_ups, list):
                    ups.extend(ref_ups)
                elif isinstance(ref_ups, dict):
                    ups.append(ref_ups)
                    
                if ups:
                    print(f"    -> Found {len(ups)} Underpass(es) in this config.")
                    found_underpasses.extend(ups)
                else:
                    print("    -> No Underpass found.")
            except Exception as e:
                print(f"    -> Error checking config: {e}")
                
        if not found_underpasses:
            print("- No Underpass found in active layers.")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Underpass Camera", "No Underpass found in active layers.")
            self._underpass_camera_active = False
            return

        # --- Underpass selection dialog ---
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
        from PyQt5.QtCore import Qt

        select_dlg = QDialog(self)
        select_dlg.setWindowTitle("Camera View")
        select_dlg.setModal(True)
        select_dlg.setMinimumWidth(320)
        select_dlg.setStyleSheet("""
            QDialog { background-color: #F5F5F5; font-family: Segoe UI; }
            QLabel  { font-size: 13px; color: #333; font-weight: bold; }
            QComboBox {
                padding: 6px; border: 2px solid #BBB;
                border-radius: 6px; font-size: 13px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 18px; border-radius: 6px;
                font-weight: bold; font-size: 13px;
            }
        """)

        dlg_layout = QVBoxLayout(select_dlg)
        dlg_layout.addWidget(QLabel("Select Underpass:"))

        combo = QComboBox()
        for idx, up in enumerate(found_underpasses):
            up_id = up.get("id", f"Underpass_{idx + 1}")
            combo.addItem(str(up_id), idx)  # store list index as user data
        dlg_layout.addWidget(combo)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #E0E0E0; color: #333;")
        ok_btn.clicked.connect(select_dlg.accept)
        cancel_btn.clicked.connect(select_dlg.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        dlg_layout.addLayout(btn_layout)

        if select_dlg.exec_() != QDialog.Accepted:
            print("- Underpass selection cancelled by user.")
            self._underpass_camera_active = False
            return

        selected_idx = combo.currentData()
        target_up = found_underpasses[selected_idx]
        print(f"- User selected Underpass: {combo.currentText()} (index {selected_idx})")

        if True:  # preserves original indentation block
            dims = target_up.get("dimensions", {})
            length = float(dims.get("length", 20.0))
            width = float(dims.get("width", 20.0))
            height = float(dims.get("height", 6.0))
            
            wc = target_up.get("world_coordinates", [0, 0, 0])
            tangent = target_up.get("tangent", [1, 0, 0])
            
            # The underpass tangent is the main road's tangent (X-axis).
            mag = math.sqrt(tangent[0]**2 + tangent[1]**2)
            if mag > 0:
                tx, ty = tangent[0]/mag, tangent[1]/mag
            else:
                tx, ty = 1.0, 0.0
                
            angle_rad = math.atan2(ty, tx)
            
            print(f"- Found Underpass at: ({wc[0]:.2f}, {wc[1]:.2f}, {wc[2]:.2f})")
            print(f"- Dimensions: L={length:.2f}, W={width:.2f}, H={height:.2f}")

            intersecting_road_path = []
            
            # Helper to check if a point is inside the underpass box
            def is_point_in_underpass(px, py, pz):
                # Translate to local
                dx = px - wc[0]
                dy = py - wc[1]
                dz = pz - wc[2]
                # Rotate back by -angle_rad around Z
                # Main road tangent is X-axis. Underpass goes across, so underpass length is along Y-axis, width is along X-axis.
                local_x = dx * math.cos(-angle_rad) - dy * math.sin(-angle_rad)
                local_y = dx * math.sin(-angle_rad) + dy * math.cos(-angle_rad)
                local_z = dz
                # Check bounds with extra margin for Z (road could be slightly above/below the exact center)
                return (abs(local_x) <= (width / 2.0) + 5.0) and (abs(local_y) <= (length / 2.0) + 10.0) and (abs(local_z) <= (height / 2.0) + 10.0)

            candidate_paths = []

            # Search all configs for road_surface_baseline
            for cp in config_paths:
                try:
                    with open(cp, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    design = data.get("design", {})
                    road_surface = design.get("road_surface_baseline") or design.get("road_surface")
                    if road_surface and isinstance(road_surface, dict):
                        for poly in road_surface.get("polylines", []):
                            pts = poly.get("points", [])
                            # Check overlap with the underpass by interpolating segments
                            overlap_points = []
                            intersection_length = 0.0
                            
                            for k in range(len(pts) - 1):
                                p1 = pts[k].get("world_coordinates")
                                p2 = pts[k+1].get("world_coordinates")
                                if not p1 or not p2: continue
                                
                                if k == 0 and is_point_in_underpass(p1[0], p1[1], p1[2]):
                                    overlap_points.append(p1)
                                    
                                if is_point_in_underpass(p2[0], p2[1], p2[2]):
                                    overlap_points.append(p2)
                                
                                dx, dy, dz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
                                seg_len = math.sqrt(dx*dx + dy*dy + dz*dz)
                                if seg_len > 0:
                                    # Sample this segment every 0.5 meters
                                    samples = int(math.ceil(seg_len / 0.5))
                                    inside_samples = 0
                                    for j in range(samples):
                                        t = (j + 0.5) / float(samples) # Check midpoint of sub-segment
                                        sp = [p1[0] + dx*t, p1[1] + dy*t, p1[2] + dz*t]
                                        if is_point_in_underpass(sp[0], sp[1], sp[2]):
                                            inside_samples += 1
                                            
                                    fraction_inside = inside_samples / float(samples)
                                    intersection_length += (seg_len * fraction_inside)
                                        
                            if intersection_length > 0:
                                # Extract points for this entire polyline
                                extracted_path = []
                                for i, pt in enumerate(pts):
                                    pwc = pt.get("world_coordinates")
                                    ch = float(pt.get("chainage_m", 0.0))
                                    if not pwc: continue
                                    
                                    # Calculate dir_vec (using next point or previous if last)
                                    if i < len(pts) - 1:
                                        nxt = pts[i+1].get("world_coordinates")
                                        if nxt:
                                            dx = nxt[0] - pwc[0]
                                            dy = nxt[1] - pwc[1]
                                            dz = nxt[2] - pwc[2]
                                            dmag = math.sqrt(dx*dx + dy*dy + dz*dz)
                                            if dmag > 0:
                                                dir_vec = [dx/dmag, dy/dmag, dz/dmag]
                                            else:
                                                dir_vec = [1, 0, 0]
                                        else:
                                            dir_vec = [1, 0, 0]
                                    else:
                                        if extracted_path:
                                            dir_vec = extracted_path[-1][3]
                                        else:
                                            dir_vec = [1, 0, 0]
                                    
                                    # Perp vec (horizontal)
                                    perp_vec = [-dir_vec[1], dir_vec[0], 0.0]
                                    pmag = math.sqrt(perp_vec[0]**2 + perp_vec[1]**2)
                                    if pmag > 0:
                                        perp_vec = [perp_vec[0]/pmag, perp_vec[1]/pmag, 0.0]
                                        
                                    extracted_path.append([ch, pwc, perp_vec, dir_vec])
                                    
                                # Calculate average distance of overlapping points to underpass center
                                if overlap_points:
                                    total_dist = sum(math.sqrt((p[0]-wc[0])**2 + (p[1]-wc[1])**2 + (p[2]-wc[2])**2) for p in overlap_points)
                                    avg_dist = total_dist / len(overlap_points)
                                else:
                                    # If no discrete points inside but intersection length > 0, the segment just crosses it
                                    avg_dist = 0.0
                                
                                candidate_paths.append({
                                    "path": extracted_path,
                                    "intersection_length": intersection_length,
                                    "overlap_count": len(overlap_points),
                                    "avg_dist": avg_dist,
                                    "file": cp
                                })
                except Exception as e:
                    pass
                    
            intersecting_road_path = []
            if candidate_paths:
                import os
                print("\n[Underpass Camera Detection Ranking]")
                # Rank primarily by longest intersection length, then minimum avg distance
                candidate_paths.sort(key=lambda x: (-x["intersection_length"], x["avg_dist"]))
                
                for rank, cand in enumerate(candidate_paths, start=1):
                    folder_name = os.path.basename(os.path.dirname(cand["file"]))
                    print(f"  Rank {rank}:")
                    print(f"    - Layer Name: {folder_name}")
                    print(f"    - Config Path: {cand['file']}")
                    print(f"    - Intersection Length: {cand['intersection_length']:.2f} m")
                    print(f"    - Overlap count: {cand['overlap_count']}")
                    print(f"    - Avg distance: {cand['avg_dist']:.2f}")

                best_candidate = candidate_paths[0]
                intersecting_road_path = best_candidate["path"]
                best_layer_name = os.path.basename(os.path.dirname(best_candidate["file"]))
                
                print(f"\n[Selected Reference Layer]")
                print(f"- Selected Layer: {best_layer_name}")
                print(f"- Config Path: {best_candidate['file']}")
                print(f"- Reason for selection: Achieved Rank 1 with the longest intersection path ({best_candidate['intersection_length']:.2f} m) passing directly through the underpass volume.")
                
                # Assign to a clear property for debugging
                self._tunnel_active_reference_layer = best_layer_name
                    
            if not intersecting_road_path:
                print("- No intersecting road layer found for the underpass.")
                try:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Underpass Camera", "Cannot activate Underpass Camera View.\nNo road surface passes through the underpass volume.")
                except ImportError:
                    pass
            else:
                print(f"- Found intersecting road layer! Extracted {len(intersecting_road_path)} points.")
                
                # Filter path to just the segment around the underpass (+ some margin)
                filtered_path = []
                for sample in intersecting_road_path:
                    pwc = sample[1]
                    if is_point_in_underpass(pwc[0], pwc[1], pwc[2]):
                        filtered_path.append(sample)
                        
                # If filtered is empty or too small, fallback to whole path
                if len(filtered_path) >= 2:
                    path_samples = filtered_path
                else:
                    path_samples = intersecting_road_path
                    
                start_sample = path_samples[0]
                end_sample = path_samples[-1]
                mid_idx = len(path_samples) // 2
                center_sample = path_samples[mid_idx]

                # Store properties to reuse Tunnel Camera logic
                self._tunnel_centerline = path_samples
                self._tunnel_forward_dir = center_sample[3]
                self._tunnel_center_point = center_sample[1]
                self._tunnel_road_surface_z = center_sample[1][2]
                self._tunnel_h_val = height

                entry_sample = path_samples[0]
                entry_pos  = entry_sample[1]
                entry_fwd = entry_sample[3]
                
                # Setup Entry Coordinates for _set_camera_to_initial_outside_view
                self._tunnel_entry_pos = list(entry_pos)
                self._tunnel_entry_fwd = list(entry_fwd)
                
                
                ## Mayur Wakhare 13-07-2026 underpass offset starting
                # Configurable offset before the underpass entrance (meters)
                self.UNDERPASS_PRE_ENTRY_OFFSET = 50.0 ## Main starting offet camera position from underpass entrance
                ####################################################
                pre_entry_path = []
               ### Mayur Wakhare 13-07-2026 underpass offset ending
                # Find where the entry_sample is in the full intersecting_road_path
                entry_idx_in_full = -1
                for idx, sample in enumerate(intersecting_road_path):
                    if sample is entry_sample:
                        entry_idx_in_full = idx
                        break
                        
                if entry_idx_in_full > 0:
                    collected_dist = 0.0
                    last_pos = entry_sample[1]
                    
                    # Collect actual road samples backwards until we reach the desired offset
                    # or the start of the available road
                    for i in range(entry_idx_in_full - 1, -1, -1):
                        sample = intersecting_road_path[i]
                        pre_entry_path.insert(0, sample)
                        
                        curr_pos = sample[1]
                        import math
                        dist = math.sqrt((curr_pos[0]-last_pos[0])**2 + (curr_pos[1]-last_pos[1])**2 + (curr_pos[2]-last_pos[2])**2)
                        collected_dist += dist
                        last_pos = curr_pos
                        
                        if collected_dist >= self.UNDERPASS_PRE_ENTRY_OFFSET:
                            break
                        #######################################################################
                            
                self._fly_path = pre_entry_path + path_samples
                self._fly_idx = 0
                self._fly_t = 0.0
                self._fly_speed = 0.015

                # CLEAR previous camera caches so we re-compute approach for the new underpass
                self._initial_cam_pos = None
                if hasattr(self, 'renderer') and self.renderer:
                    self.renderer.GetActiveCamera().SetViewUp(0, 0, 1)

            ## Mayur Wakhare 13-07-2026 underpass offset ending camera start position
                # Set entry index so the camera starts outside, facing in, and
                # transitions to the road-centerline path at the underpass entrance.
                self._tunnel_entry_idx = len(pre_entry_path)
                self._pre_entry_offset = self.UNDERPASS_PRE_ENTRY_OFFSET

                # Set clipping range appropriate for the underpass size
                underpass_length_safe = max(50.0, length)
                if hasattr(self, 'renderer') and self.renderer:
                    self.renderer.GetActiveCamera().SetClippingRange(0.5, underpass_length_safe + 200.0)

                print(f"- Pre-entry points: {len(pre_entry_path)}, Path points: {len(path_samples)}")
                print(f"- Total fly path: {len(self._fly_path)} points")
                print(f"- Tunnel entry at path index: {self._tunnel_entry_idx}")
##############################################################
                # Setup the UI
                is_resuming = hasattr(self, '_saved_tunnel_cam_pos') and self._saved_tunnel_cam_pos is not None
                if is_resuming:
                    if hasattr(self, 'renderer') and self.renderer:
                        camera = self.renderer.GetActiveCamera()
                        camera.SetPosition(*self._saved_tunnel_cam_pos)
                        camera.SetFocalPoint(*self._saved_tunnel_cam_fp)
                        self.vtk_widget.GetRenderWindow().Render()
                    self._saved_tunnel_cam_pos = None
                    self._saved_tunnel_cam_fp = None
                else:
                    if hasattr(self, 'tc_slider'):
                        self.tc_slider.blockSignals(True)
                        self.tc_slider.setValue(0)
                        self.tc_slider.blockSignals(False)

                    ## Mayur Wakhare 13-07-2026 underpass offset ending
                    # Initialize camera directly onto the road surface offset path
                    print(f"Initial path index after camera initialization: {self._fly_idx}")
                    self._set_camera_to_path_index(self._fly_idx, self._fly_t)
                ##############################################################
                if not hasattr(self, '_tunnel_fly_timer'):
                    from PyQt5.QtCore import QTimer
                    self._tunnel_fly_timer = QTimer(self)
                    self._tunnel_fly_timer.timeout.connect(self._update_tunnel_flythrough)

                if hasattr(self, 'tunnel_control_bar'):
                    if hasattr(self, 'vtk_widget') and self.vtk_widget:
                        interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
                        if interactor:
                            current_style = interactor.GetInteractorStyle()
                            current_picker = interactor.GetPicker()
                            ## Mayur Wakhare 13-07-2026 underpass offset ending
                            if getattr(self, '_saved_interactor_style', None) is None:
                                #######################################################
                                self._saved_interactor_style = current_style
                                self._saved_picker = current_picker

                            tunnel_style = TunnelFPSInteractorStyle(viewer=self)
                            cam_pos = self.renderer.GetActiveCamera().GetPosition()
                            tunnel_style.set_locked_position(*cam_pos)
                            interactor.SetInteractorStyle(tunnel_style)
                            interactor.SetPicker(None)
                            self._tunnel_fps_style = tunnel_style
                            ##### Mayur Wakhare 13-07-2026 underpass camera view button ending
                            has_fwd = tunnel_style.HasObserver("MouseWheelForwardEvent")
                            print(f"- Mouse wheel observers registered: {'Yes' if has_fwd else 'No'}")
                            valid_path = hasattr(self, '_fly_path') and bool(self._fly_path)
                            print(f"- Current camera path valid: {'Yes' if valid_path else 'No'}")
                            print(f"- Current path index: {getattr(self, '_fly_idx', 0)}")
                            #####################################################################

                    self.tunnel_control_bar.setVisible(True)
                    self.update_3d_button_position()
                    
                    if hasattr(self, 'tc_play_btn'):
                        self.tc_play_btn.blockSignals(True)
                        self.tc_play_btn.setChecked(False)
                        self.tc_play_btn.blockSignals(False)
                    self.tunnel_control_bar.raise_()

        # (empty-underpass case is now handled above with early return)

#######################################################################
######## Mayur Wakhare 1-7-2026 Tunnel Fly through update code Camera Follow path in tunnel ####
    def _update_tunnel_flythrough(self):
        if not hasattr(self, '_fly_path') or not self._fly_path:
            if hasattr(self, '_tunnel_fly_timer'):
                self._tunnel_fly_timer.stop()
            return
            
        self._fly_t += self._fly_speed
        while self._fly_t >= 1.0:
            self._fly_idx += 1
            self._fly_t -= 1.0
            
        if self._fly_idx >= len(self._fly_path) - 2:
            if hasattr(self, 'tc_play_btn'):
                self.tc_play_btn.setChecked(False)
                self._toggle_tunnel_auto()
            return
            
        self._set_camera_to_path_index(self._fly_idx, self._fly_t)
        
        if hasattr(self, 'tc_slider'):
            self.tc_slider.blockSignals(True)
            max_idx = len(self._fly_path) - 2
            curr_val = self._fly_idx + self._fly_t
            percent = curr_val / max_idx if max_idx > 0 else 0
            self.tc_slider.setValue(int(percent * 1000))
            self.tc_slider.blockSignals(False)
#########################################################################

## Mayur Wakhare 1-7-2026 Camera
    def _toggle_tunnel_auto(self):
        if hasattr(self, 'tc_play_btn'):
            if self.tc_play_btn.isChecked():
                self.tc_play_btn.setText("⏸ Auto")
                self.tc_play_btn.setStyleSheet("color: #4CAF50;")
                
                # Check if we are resuming from a stopped state
                if hasattr(self, '_saved_tunnel_cam_pos') and self._saved_tunnel_cam_pos is not None:
                    if hasattr(self, 'renderer') and self.renderer:
                        camera = self.renderer.GetActiveCamera()
                        camera.SetPosition(self._saved_tunnel_cam_pos)
                        camera.SetFocalPoint(self._saved_tunnel_cam_fp)
                        
                        # Re-install FPS interactor
                        if hasattr(self, 'vtk_widget') and self.vtk_widget:
                            interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
                            if interactor and hasattr(self, '_tunnel_fps_style'):
                                self._tunnel_fps_style.set_locked_position(*self._saved_tunnel_cam_pos)
                                interactor.SetInteractorStyle(self._tunnel_fps_style)
                        
                        self.vtk_widget.GetRenderWindow().Render()
                    self._saved_tunnel_cam_pos = None
                    self._saved_tunnel_cam_fp = None
                
                if hasattr(self, '_tunnel_fly_timer') and not self._tunnel_fly_timer.isActive():
                    self._tunnel_fly_timer.start(33)
            else:
                self.tc_play_btn.setText("▶ Auto")
                self.tc_play_btn.setStyleSheet("color: white;")
                if hasattr(self, '_tunnel_fly_timer') and self._tunnel_fly_timer.isActive():
                    self._tunnel_fly_timer.stop()

    def _on_tunnel_slider_changed(self, value):
        if not hasattr(self, '_fly_path') or not self._fly_path:
            return
        
        # Only manually jump if Auto is off
        if hasattr(self, 'tc_play_btn') and not self.tc_play_btn.isChecked():
            # If we were in overview mode, moving slider should snap back into tunnel
            if hasattr(self, '_saved_tunnel_cam_pos') and self._saved_tunnel_cam_pos is not None:
                self._saved_tunnel_cam_pos = None
                self._saved_tunnel_cam_fp = None
                if hasattr(self, 'vtk_widget') and self.vtk_widget:
                    interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
                    if interactor and hasattr(self, '_tunnel_fps_style'):
                        interactor.SetInteractorStyle(self._tunnel_fps_style)
            
            percent = value / 1000.0
            max_idx = len(self._fly_path) - 2
            target_val = percent * max_idx
            self._fly_idx = int(target_val)
            self._fly_t = target_val - self._fly_idx
            
            if value == 0:
                self._set_camera_to_initial_outside_view()
            else:
                self._set_camera_to_path_index(self._fly_idx, self._fly_t)

    def _on_tunnel_stop_clicked(self):
        #### Mayur Wakhare 13-07-2026 Underpass Camera movement 
        self._underpass_camera_active = False
        ######################################################
        """Pause tunnel flythrough, save current camera state, and move to overview."""
        if not hasattr(self, 'renderer') or not self.renderer:
            return

        # 1. Save current camera state (only if not already stopped)
        if not hasattr(self, '_saved_tunnel_cam_pos') or self._saved_tunnel_cam_pos is None:
            camera = self.renderer.GetActiveCamera()
            self._saved_tunnel_cam_pos = camera.GetPosition()
            self._saved_tunnel_cam_fp = camera.GetFocalPoint()

        # 2. Pause auto if running
        if hasattr(self, 'tc_play_btn') and self.tc_play_btn.isChecked():
            self.tc_play_btn.setChecked(False)
            self._toggle_tunnel_auto()

        # 3. Hide the tunnel control bar since we're exiting Tunnel Camera Mode
        if hasattr(self, 'tunnel_control_bar'):
            self.tunnel_control_bar.setVisible(False)

        # 4. Restore original interactor style (disable TunnelFPSInteractorStyle)
        if hasattr(self, 'vtk_widget') and self.vtk_widget:
            interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
            if interactor and hasattr(self, '_saved_interactor_style'):
                interactor.SetInteractorStyle(self._saved_interactor_style)
                if hasattr(self, '_saved_picker'):
                    interactor.SetPicker(self._saved_picker)
##### Mayur Wakhare 30-06-2026 Camera reset
        # 5. Destroy robot if active
        if hasattr(self, '_destroy_robot_actor'):
            self._destroy_robot_actor()

        # 6. Move to overview using the exact same logic as Reset
        #########################################################
        self._set_camera_to_initial_outside_view()
        
######################################################################################################################################################

## Mayur Wakhare 1-7-2026 Camera
    def _reset_tunnel_camera(self):
        ### Mayur Wakhare 13-07-2026 Underpass Camera movement 
        self._underpass_camera_active = False
        ######################################################
        if not hasattr(self, '_fly_path') or not self._fly_path:
            return
            
        if hasattr(self, 'tc_play_btn'):
            self.tc_play_btn.setChecked(False)
            self._toggle_tunnel_auto()
            
        if hasattr(self, 'tc_slider'):
            self.tc_slider.blockSignals(True)
            self.tc_slider.setValue(0)
            self.tc_slider.blockSignals(False)
            
        self._fly_idx = 0
        if self._fly_idx >= len(self._fly_path) - 1:
            self._fly_idx = max(0, len(self._fly_path) - 2)
            
        self._fly_t = 0.0

        # CLEAR the saved state so next stop/resume uses new path position
        self._saved_tunnel_cam_pos = None
        self._saved_tunnel_cam_fp = None
        
        self._set_camera_to_initial_outside_view()
        

        # Ensure the FPS style is locked to the new position if we reset from inside the tunnel
        if hasattr(self, 'vtk_widget') and self.vtk_widget:
            interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
            if interactor and hasattr(self, '_tunnel_fps_style'):
                interactor.SetInteractorStyle(self._tunnel_fps_style)

    def _tunnel_look_rotate(self, yaw_deg=0.0, pitch_deg=0.0):
        """Rotate the tunnel camera view by a fixed angle (button click).
        Only changes the focal point; camera position stays locked."""
        if not hasattr(self, 'renderer') or not self.renderer:
            return
        import math
###################################################################################################################################################
############# Mayur Wakhare 30-06-2026
        robot_active = getattr(self, '_robot_active', False)
        if robot_active:
            self._robot_yaw += (yaw_deg * math.pi / 180.0)
            
            new_pitch = self._robot_pitch + (pitch_deg * math.pi / 180.0)
            max_elev = 85.0 * math.pi / 180.0
            self._robot_pitch = max(-max_elev, min(max_elev, new_pitch))
            
            if getattr(self, '_robot_assembly', None):
                self._robot_assembly.SetOrientation(0, 0, math.degrees(self._robot_yaw))
            if hasattr(self, '_update_robot_camera'):
                self._update_robot_camera()
            return
##########################################################################
        camera = self.renderer.GetActiveCamera()
        pos = camera.GetPosition()
        fp  = camera.GetFocalPoint()

        vx = fp[0] - pos[0]
        vy = fp[1] - pos[1]
        vz = fp[2] - pos[2]
        dist = math.sqrt(vx*vx + vy*vy + vz*vz)
        if dist < 1e-9:
            dist = 50.0

        # Yaw (rotate around world Z axis)
        yaw_rad = yaw_deg * math.pi / 180.0
        cos_y = math.cos(yaw_rad)
        sin_y = math.sin(yaw_rad)
        nvx = vx * cos_y - vy * sin_y
        nvy = vx * sin_y + vy * cos_y
        nvz = vz

        # Pitch (rotate up/down, clamped to ±85°)
        horiz = math.sqrt(nvx*nvx + nvy*nvy)
        cur_elev = math.atan2(nvz, horiz) if horiz > 1e-9 else 0.0
        new_elev = cur_elev + (pitch_deg * math.pi / 180.0)
        max_elev = 85.0 * math.pi / 180.0
        new_elev = max(-max_elev, min(max_elev, new_elev))

        if horiz > 1e-9:
            h_dir_x = nvx / horiz
            h_dir_y = nvy / horiz
        else:
            h_dir_x, h_dir_y = 1.0, 0.0

        new_horiz = dist * math.cos(new_elev)
        new_vz    = dist * math.sin(new_elev)

        new_fp = (
            pos[0] + h_dir_x * new_horiz,
            pos[1] + h_dir_y * new_horiz,
            pos[2] + new_vz
        )

        camera.SetFocalPoint(new_fp)
        self.vtk_widget.GetRenderWindow().Render()
######### Mayur Wakhare 1-7-2026 Camera
    def _tunnel_reset_view_direction(self):
        """Reset the camera to face the default forward direction along the
        tunnel path without changing the camera position."""
        if not hasattr(self, 'renderer') or not self.renderer:
            return
        if not hasattr(self, '_fly_path') or not self._fly_path:
            return

        camera = self.renderer.GetActiveCamera()
        pos = camera.GetPosition()

        # Determine the current forward direction from the path
        idx = getattr(self, '_fly_idx', 0)
        tunnel_entry_idx = getattr(self, '_tunnel_entry_idx', 0)

        if idx < tunnel_entry_idx:
            # Pre-entry: forward is toward the tunnel entrance
            entry_fwd = getattr(self, '_tunnel_entry_fwd', [1, 0, 0])
            fx, fy, fz = entry_fwd[0], entry_fwd[1], entry_fwd[2]
        else:
            # Inside tunnel: forward from consecutive road path points
            import math
            p0 = self._fly_path[min(idx, len(self._fly_path) - 1)][1]
            p1 = self._fly_path[min(idx + 1, len(self._fly_path) - 1)][1]
            fx = p1[0] - p0[0]
            fy = p1[1] - p0[1]
            fz = p1[2] - p0[2]
            mag = math.sqrt(fx*fx + fy*fy + fz*fz)
            if mag > 1e-9:
                fx /= mag; fy /= mag; fz /= mag
            else:
                entry_fwd = getattr(self, '_tunnel_entry_fwd', [1, 0, 0])
                fx, fy, fz = entry_fwd[0], entry_fwd[1], entry_fwd[2]
                ###################################################################################################################
######### Mayur Wakhare 30-06-2026
        robot_active = getattr(self, '_robot_active', False)
        if robot_active:
            import math as _math
            if fx != 0 or fy != 0:
                self._robot_yaw = _math.atan2(fy, fx)
                self._robot_pitch = 0.0
                if getattr(self, '_robot_assembly', None):
                    self._robot_assembly.SetOrientation(0, 0, _math.degrees(self._robot_yaw))
                if hasattr(self, '_update_robot_camera'):
                    self._update_robot_camera()
        else:
            ##################################################################
            focal_dist = 50.0
            new_fp = (pos[0] + fx * focal_dist,
                      pos[1] + fy * focal_dist,
                      pos[2] + fz * focal_dist)

            camera.SetFocalPoint(new_fp)
            self.vtk_widget.GetRenderWindow().Render()
### Mayur Wakhare 1-7-2026 Camera
    def _set_camera_to_initial_outside_view(self):
        """Place camera DEFAULT_PRE_ENTRY_OFFSET m before tunnel entrance
        using tunnel entry X,Y coordinates as reference.
        Does NOT use road surface path (it may not exist outside the tunnel).
        Forward vector is expected to already be normalized (done during setup)."""
        if not hasattr(self, '_fly_path') or not self._fly_path:
            return

        # Use tunnel entry coordinates as reference (NOT road path point)
        entry_pos = getattr(self, '_tunnel_entry_pos', self._fly_path[0][1])
        entry_fwd = getattr(self, '_tunnel_entry_fwd', self._fly_path[0][3])

        # Configurable pre-entry offset
        _OFFSET = getattr(self, '_pre_entry_offset', 50.0)

        # Safety: re-normalize XY in case fallback was used
        import math
        fwd_mag_xy = math.sqrt(entry_fwd[0]**2 + entry_fwd[1]**2)
        if fwd_mag_xy < 1e-9:
            fwd_mag_xy = 1.0
        nfwd = [entry_fwd[0] / fwd_mag_xy,
                entry_fwd[1] / fwd_mag_xy,
                entry_fwd[2] / fwd_mag_xy if fwd_mag_xy > 1e-9 else 0.0]

        # Camera XY: _OFFSET m before tunnel entrance along reverse direction
        cam_x = entry_pos[0] - (nfwd[0] * _OFFSET)
        cam_y = entry_pos[1] - (nfwd[1] * _OFFSET)

        # Height: entry Z + eye height (no terrain reference)
        cam_height = entry_pos[2] + 1.7
        min_z = entry_pos[2] + 1.2
        max_z = entry_pos[2] + getattr(self, '_tunnel_h_val', 5.0) - 1.0
        cam_height = max(min_z, min(cam_height, max_z))

        # Store for pre-entry interpolation
        self._initial_cam_pos = (cam_x, cam_y, cam_height)

        # Look toward tunnel entrance and beyond
        focal_x = entry_pos[0] + (nfwd[0] * 20.0)
        focal_y = entry_pos[1] + (nfwd[1] * 20.0)
        focal_z = cam_height + (nfwd[2] * 20.0)
        ######################################################################################################################################
###### Mayur Wakhare 30-06-2026
        robot_active = getattr(self, '_robot_active', False)
        if robot_active:
            import math as _math
            robot_z = cam_height - 1.7
            self._robot_position = [cam_x, cam_y, robot_z]
            
            dx_dir = focal_x - cam_x
            dy_dir = focal_y - cam_y
            if dx_dir != 0 or dy_dir != 0:
                self._robot_yaw = _math.atan2(dy_dir, dx_dir)
            
            if getattr(self, '_robot_assembly', None):
                self._robot_assembly.SetPosition(cam_x, cam_y, robot_z)
                self._robot_assembly.SetOrientation(0, 0, _math.degrees(self._robot_yaw))
            
            if hasattr(self, '_update_robot_camera'):
                self._update_robot_camera()
        else:
            ######################################################
            if hasattr(self, 'renderer') and self.renderer:
                camera = self.renderer.GetActiveCamera()
                camera.SetPosition(cam_x, cam_y, cam_height)
                camera.SetFocalPoint(focal_x, focal_y, focal_z)
                # Update FPS position lock
                fps = getattr(self, '_tunnel_fps_style', None)
                if fps:
                    fps.set_locked_position(cam_x, cam_y, cam_height)
                self.vtk_widget.GetRenderWindow().Render()


###### Mayur Wakhare 1-7-2026 Camera move
    def _set_camera_to_path_index(self, idx, t):
        """Navigate camera along the dual-reference path.
        Before tunnel_entry_idx → Tunnel Entry X,Y reference (straight line)
        At/after tunnel_entry_idx → Road Surface Centerline reference (curve-aware)
        """
        if not hasattr(self, '_fly_path') or not self._fly_path or idx >= len(self._fly_path) - 1:
            return

        tunnel_entry_idx = getattr(self, '_tunnel_entry_idx', 0)

        if idx < tunnel_entry_idx:
            # ── BEFORE TUNNEL ENTRY: Tunnel Entry X,Y Reference ──
            # Straight-line interpolation from initial camera position
            # toward the tunnel entrance.  Does NOT use road surface path.
            initial_pos = getattr(self, '_initial_cam_pos', None)
            entry_pos   = getattr(self, '_tunnel_entry_pos', self._fly_path[0][1])
            entry_fwd   = getattr(self, '_tunnel_entry_fwd', self._fly_path[0][3])

            if initial_pos is None:
                # Normalize fallback forward vector
                import math
                _OFFSET_FB = getattr(self, '_pre_entry_offset', 50.0)
                fmag = math.sqrt(entry_fwd[0]**2 + entry_fwd[1]**2)
                if fmag < 1e-9: fmag = 1.0
                initial_pos = (entry_pos[0] - (entry_fwd[0]/fmag) * _OFFSET_FB,
                               entry_pos[1] - (entry_fwd[1]/fmag) * _OFFSET_FB,
                               entry_pos[2] + 1.7)

            # Progress 0→1 across the pre-entry segment
            total_pre = float(tunnel_entry_idx)
            progress  = (float(idx) + t) / total_pre if total_pre > 0 else 1.0
            progress  = max(0.0, min(1.0, progress))

            cam_x = initial_pos[0] + (entry_pos[0] - initial_pos[0]) * progress
            cam_y = initial_pos[1] + (entry_pos[1] - initial_pos[1]) * progress

            # Height: uses entry Z (no terrain reference)
            cam_height = entry_pos[2] + 1.7
            min_z = entry_pos[2] + 1.2
            max_z = entry_pos[2] + getattr(self, '_tunnel_h_val', 5.0) - 1.0
            cam_height = max(min_z, min(cam_height, max_z))

            # Look toward tunnel entrance and beyond
            focal_x = entry_pos[0] + entry_fwd[0] * 50.0
            focal_y = entry_pos[1] + entry_fwd[1] * 50.0
            focal_z = cam_height   + entry_fwd[2] * 50.0
####### Mayur Wakhare 30-06-2026
            robot_active = getattr(self, '_robot_active', False)
            if robot_active:
                # ── Move the ROBOT instead of the camera ──
                import math as _math
                robot_z = cam_height - 1.7  # Revert camera height to get ground Z
                self._robot_position = [cam_x, cam_y, robot_z]
                
                dx_dir = focal_x - cam_x
                dy_dir = focal_y - cam_y
                if dx_dir != 0 or dy_dir != 0:
                    self._robot_yaw = _math.atan2(dy_dir, dx_dir)
                
                if getattr(self, '_robot_assembly', None):
                    self._robot_assembly.SetPosition(cam_x, cam_y, robot_z)
                    self._robot_assembly.SetOrientation(0, 0, _math.degrees(self._robot_yaw))
                
                if hasattr(self, '_update_robot_camera'):
                    self._update_robot_camera()
            else:
                #################################################
                if hasattr(self, 'renderer') and self.renderer:
                    camera = self.renderer.GetActiveCamera()
                    camera.SetPosition(cam_x, cam_y, cam_height)
                    camera.SetFocalPoint(focal_x, focal_y, focal_z)
                    # Update FPS position lock
                    fps = getattr(self, '_tunnel_fps_style', None)
                    if fps:
                        fps.set_locked_position(cam_x, cam_y, cam_height)
                    self.vtk_widget.GetRenderWindow().Render()


            if progress >= 0.95:
                pass
        else:
            # ── INSIDE TUNNEL: Road Surface Centerline Reference ──
            # Camera follows curve-aware road path; direction from consecutive points.
            p0 = self._fly_path[idx][1]
            p1 = self._fly_path[idx + 1][1]

            cam_x  = p0[0] + (p1[0] - p0[0]) * t
            cam_y  = p0[1] + (p1[1] - p0[1]) * t
            path_z = p0[2] + (p1[2] - p0[2]) * t

            cam_height = path_z + 1.7
            min_z = path_z + 1.2
            max_z = path_z + getattr(self, '_tunnel_h_val', 5.0) - 1.0
            cam_height = max(min_z, min(cam_height, max_z))

            # Direction calculated from consecutive road path points
            p2 = self._fly_path[min(idx + 2, len(self._fly_path) - 1)][1]

            dx0 = p1[0] - p0[0]
            dy0 = p1[1] - p0[1]
            dz0 = p1[2] - p0[2]

            dx1 = p2[0] - p1[0]
            dy1 = p2[1] - p1[1]
            dz1 = p2[2] - p1[2]

            dx = dx0 + (dx1 - dx0) * t
            dy = dy0 + (dy1 - dy0) * t
            dz = dz0 + (dz1 - dz0) * t

            import math
            mag = math.sqrt(dx**2 + dy**2 + dz**2)
            if mag == 0:
                mag = 1.0

            focal_x = cam_x     + (dx / mag) * 50.0
            focal_y = cam_y     + (dy / mag) * 50.0
            focal_z = cam_height + (dz / mag) * 50.0
###### Mayur Wakhare 30-06-2026
            robot_active = getattr(self, '_robot_active', False)
            if robot_active:
                # ── Move the ROBOT instead of the camera ──
                import math as _math
                robot_z = cam_height - 1.7
                self._robot_position = [cam_x, cam_y, robot_z]
                
                dx_dir = focal_x - cam_x
                dy_dir = focal_y - cam_y
                if dx_dir != 0 or dy_dir != 0:
                    self._robot_yaw = _math.atan2(dy_dir, dx_dir)
                
                if getattr(self, '_robot_assembly', None):
                    self._robot_assembly.SetPosition(cam_x, cam_y, robot_z)
                    self._robot_assembly.SetOrientation(0, 0, _math.degrees(self._robot_yaw))
                
                if hasattr(self, '_update_robot_camera'):
                    self._update_robot_camera()
            else:
                #####################################################
                if hasattr(self, 'renderer') and self.renderer:
                    camera = self.renderer.GetActiveCamera()
                    camera.SetPosition(cam_x, cam_y, cam_height)
                    camera.SetFocalPoint(focal_x, focal_y, focal_z)
                    # Update FPS position lock
                    fps = getattr(self, '_tunnel_fps_style', None)
                    if fps:
                        fps.set_locked_position(cam_x, cam_y, cam_height)
                    self.vtk_widget.GetRenderWindow().Render()

##########################################################################

    def on_floating_camera_button_clicked(self):
        """Toggle the three view-shortcut buttons with a spin animation open or closed.
        Clicking the camera icon also resets to FREE mode (slider uses auto side-view again).
        # ======= Aniket Added on 08-05-2026: reset active view mode + spin animation =======
        """
      # Mayur Wakhare 13-07-2026 underpass camera view button
        print("\n[Reset Camera View clicked]")
        print(f"- Current Underpass Camera active flag: {getattr(self, '_underpass_camera_active', False)}")
        
        if getattr(self, '_underpass_camera_active', False):
            print("- Underpass Camera deactivated")
            
        self._underpass_camera_active = False
        self._fly_path = []
        self._fly_idx = 0
        self._tunnel_entry_idx = 0
#########################################################################################
        if hasattr(self, 'tunnel_control_bar'):
            self.tunnel_control_bar.setVisible(False)

        # ── Restore original interactor style when leaving Tunnel Mode ──
        if hasattr(self, 'vtk_widget') and self.vtk_widget:
            try:
                interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
                if interactor:
                    saved_style = getattr(self, '_saved_interactor_style', None)
                    if saved_style:
                        interactor.SetInteractorStyle(saved_style)
                    else:
                        interactor.SetInteractorStyle(vtkInteractorStyleTrackballCamera())
                    saved_picker = getattr(self, '_saved_picker', None)
                    if saved_picker:
                        interactor.SetPicker(saved_picker)
                    self._saved_interactor_style = None
                    self._saved_picker = None
                    self._tunnel_fps_style = None
            except Exception as e:
                pass
        if hasattr(self, '_tunnel_fly_timer') and self._tunnel_fly_timer.isActive():
            self._tunnel_fly_timer.stop()
######## Mayur Wakhare 30-06-2026 Camera reset
        # ── Destroy robot when leaving Tunnel Mode ──
        if hasattr(self, '_destroy_robot_actor'):
            self._destroy_robot_actor()
##############################################################
        self._active_view_mode = 'free'   # camera reset → slider auto-view re-enabled

        try:
            if not hasattr(self, 'renderer') or not self.renderer:
                return
            if not hasattr(self, 'vtk_widget') or not self.vtk_widget:
                return
            self.renderer.ResetCamera()
            self.renderer.ResetCameraClippingRange()
            self.vtk_widget.GetRenderWindow().Render()
        except Exception as e:
            print(f"Error resetting camera view: {e}")

        # Toggle open / closed with spin animation
        self._view_buttons_open = not getattr(self, '_view_buttons_open', False)
        self._animate_view_buttons(opening=self._view_buttons_open)

    # ======= Aniket Added on 08-05-2026: spin animation helper =======
    def _animate_view_buttons(self, opening: bool):
        """Animate the three view buttons with a spin + slide + fade effect.

        Opening  → buttons spin in from the camera-button centre outward to their target positions.
        Closing  → buttons spin out back toward the camera-button centre and disappear.

        Animation breakdown (all three run in parallel):
          • geometry  – slides from camera-centre (collapsed) ↔ target position (expanded)
          • opacity   – fades 0 → 1  (open)  /  1 → 0  (close)
          • spin      – QTimer drives a fast border-radius pulse that gives a "spinning coin"
                        illusion (radius 22 → 0 → 22 while size stays constant)
        """
        DURATION  = 320   # ms — total animation duration
        SPIN_STEPS = 10   # number of spin frames
        BTN_SIZE  = 44    # view-button diameter (matches _btn_size set earlier)

        buttons = []
        for attr in ('view_top_button', 'view_left_button', 'view_right_button'):
            if hasattr(self, attr):
                buttons.append(getattr(self, attr))

        if not buttons:
            return

        # Ensure positions are current before animating
        self.update_3d_button_position()

        cam_x = self.camera_floating_button.x()
        cam_y = self.camera_floating_button.y()

        # Collect each button's resting target position (set by update_3d_button_position)
        target_positions = [btn.pos() for btn in buttons]

        # ── Set up opacity effects (reuse if already attached) ──────────────
        for btn in buttons:
            if btn.graphicsEffect() is None:
                effect = QGraphicsOpacityEffect(btn)
                effect.setOpacity(0.0 if opening else 1.0)
                btn.setGraphicsEffect(effect)

        # ── If opening, make buttons visible immediately at the camera position ──
        if opening:
            for btn in buttons:
                btn.move(cam_x, cam_y)
                btn.setVisible(True)
                btn.raise_()

        # ── Build one QPropertyAnimation per button for geometry + opacity ──
        anim_group = QParallelAnimationGroup(self)

        for btn, target_pos in zip(buttons, target_positions):
            effect = btn.graphicsEffect()

            # Geometry: collapsed (at camera centre) ↔ expanded (target position)
            collapsed_rect = QRect(cam_x, cam_y, BTN_SIZE, BTN_SIZE)
            expanded_rect  = QRect(target_pos.x(), target_pos.y(), BTN_SIZE, BTN_SIZE)

            geo_anim = QPropertyAnimation(btn, b"geometry", self)
            geo_anim.setDuration(DURATION)
            geo_anim.setEasingCurve(
                QEasingCurve.OutBack if opening else QEasingCurve.InBack
            )
            if opening:
                geo_anim.setStartValue(collapsed_rect)
                geo_anim.setEndValue(expanded_rect)
            else:
                geo_anim.setStartValue(expanded_rect)
                geo_anim.setEndValue(collapsed_rect)
            anim_group.addAnimation(geo_anim)

            # Opacity fade
            op_anim = QPropertyAnimation(effect, b"opacity", self)
            op_anim.setDuration(DURATION)
            op_anim.setEasingCurve(QEasingCurve.InOutQuad)
            op_anim.setStartValue(0.0 if opening else 1.0)
            op_anim.setEndValue(1.0 if opening else 0.0)
            anim_group.addAnimation(op_anim)

        # ── After geometry+opacity animation finishes, hide buttons if closing ──
        def _on_finished():
            if not opening:
                for btn in buttons:
                    btn.setVisible(False)
            else:
                # Restore exact target positions (OutBack may overshoot slightly)
                for btn, tp in zip(buttons, target_positions):
                    btn.move(tp)
                    btn.raise_()

        anim_group.finished.connect(_on_finished)
        anim_group.start()

        # Keep a reference so Python doesn't GC the group before it finishes
        self._view_btn_anim_group = anim_group

        # ── Spin effect: QTimer drives border-radius oscillation ────────────
        # This simulates a "spinning coin" by rapidly toggling the border-radius
        # between full-circle (22) and 0, giving a squish/spin visual.
        spin_interval = max(1, DURATION // (SPIN_STEPS * 2))
        spin_cycle    = [0] * 1  # mutable counter

        _view_btn_style_tpl = """
            QPushButton {{
                background-color: {bg};
                background-image: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 {start}, stop:1 {end});
                color: white;
                border: 2px solid #000000;
                border-radius: {r}px;
                font-size: 11px;
                font-weight: bold;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-image: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 {hover_start}, stop:1 {hover_end});
            }}
            QPushButton:pressed {{
                background-image: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                  stop:0 {pressed_start}, stop:1 {pressed_end});
            }}
        """

        def _spin_tick():
            step = spin_cycle[0]
            # Radius oscillates: 22 → 0 → 22 over SPIN_STEPS*2 ticks
            half = SPIN_STEPS
            r = int(BTN_SIZE // 2 * abs(half - (step % (half * 2))) / half)
            r = max(4, r)  # never fully square — keep at least slightly rounded
            for btn in buttons:
                name_map = {
                    'view_top_button':   ("#1565C0", "#42A5F5", "#1565C0", "#64B5F6", "#1976D2", "#0D47A1", "#1565C0"),
                    'view_left_button':  ("#2E7D32", "#66BB6A", "#2E7D32", "#81C784", "#388E3C", "#1B5E20", "#2E7D32"),
                    'view_right_button': ("#EF6C00", "#FFB74D", "#EF6C00", "#FFCC80", "#F57C00", "#E65100", "#EF6C00"),
                }
                for attr, colors in name_map.items():
                    if hasattr(self, attr) and getattr(self, attr) is btn:
                        bg, start, end, hover_start, hover_end, pressed_start, pressed_end = colors
                        btn.setStyleSheet(_view_btn_style_tpl.format(
                            bg=bg, start=start, end=end,
                            hover_start=hover_start, hover_end=hover_end,
                            pressed_start=pressed_start, pressed_end=pressed_end,
                            r=r))
                        break
            spin_cycle[0] += 1
            if spin_cycle[0] >= SPIN_STEPS * 2:
                # Animation done — restore final full-circle style
                for btn in buttons:
                    final_map = {
                        'ViewTopButton': ("#1565C0", "#42A5F5", "#1565C0", "#64B5F6", "#1976D2", "#0D47A1", "#1565C0"),
                        'ViewLeftButton': ("#2E7D32", "#66BB6A", "#2E7D32", "#81C784", "#388E3C", "#1B5E20", "#2E7D32"),
                        'ViewRightButton': ("#EF6C00", "#FFB74D", "#EF6C00", "#FFCC80", "#F57C00", "#E65100", "#EF6C00"),
                    }
                    bg, start, end, hover_start, hover_end, pressed_start, pressed_end = final_map.get(
                        btn.objectName(),
                        ("#1A6E8C", "#4FC3F7", "#1A6E8C", "#81D4FA", "#0288D1", "#01579B", "#1A6E8C"),
                    )
                    btn.setStyleSheet(_view_btn_style_tpl.format(
                        bg=bg,
                        start=start,
                        end=end,
                        hover_start=hover_start,
                        hover_end=hover_end,
                        pressed_start=pressed_start,
                        pressed_end=pressed_end,
                        r=BTN_SIZE // 2))
                self._spin_timer.stop()

        self._spin_timer = QTimer(self)
        self._spin_timer.setInterval(spin_interval)
        self._spin_timer.timeout.connect(_spin_tick)
        self._spin_timer.start()

    # ======= Aniket Added on 08-05-2026: individual view-set handlers =======
    def on_view_top_clicked(self):
        """Lock camera to Top-Down view. Slider will keep this view while scrolling."""
        # ======= Aniket Added on 08-05-2026: lock active view mode =======
        self._active_view_mode = 'top'
        try:
            if not hasattr(self, 'renderer') or not self.renderer:
                return
            camera = self.renderer.GetActiveCamera()
            if not camera:
                return
            fp = camera.GetFocalPoint()
            distance = camera.GetDistance()
            camera.SetPosition(fp[0], fp[1], fp[2] + distance)
            camera.SetViewUp(0, 1, 0)
            self.renderer.ResetCameraClippingRange()
            self.vtk_widget.GetRenderWindow().Render()
        except Exception as e:
            print(f"Error setting top view: {e}")

    def on_view_left_clicked(self):
        """Lock camera to Left-Side view. Slider will keep this view while scrolling."""
        # ======= Aniket Added on 08-05-2026: lock active view mode =======
        self._active_view_mode = 'left'
        try:
            if not hasattr(self, 'renderer') or not self.renderer:
                return
            camera = self.renderer.GetActiveCamera()
            if not camera:
                return
            fp = camera.GetFocalPoint()
            distance = camera.GetDistance()
            camera.SetPosition(fp[0] - distance, fp[1], fp[2])
            camera.SetViewUp(0, 0, 1)
            self.renderer.ResetCameraClippingRange()
            self.vtk_widget.GetRenderWindow().Render()
        except Exception as e:
            print(f"Error setting left view: {e}")

    def on_view_right_clicked(self):
        """Lock camera to Right-Side view. Slider will keep this view while scrolling."""
        # ======= Aniket Added on 08-05-2026: lock active view mode =======
        self._active_view_mode = 'right'
        try:
            if not hasattr(self, 'renderer') or not self.renderer:
                return
            camera = self.renderer.GetActiveCamera()
            if not camera:
                return
            fp = camera.GetFocalPoint()
            distance = camera.GetDistance()
            camera.SetPosition(fp[0] + distance, fp[1], fp[2])
            camera.SetViewUp(0, 0, 1)
            self.renderer.ResetCameraClippingRange()
            self.vtk_widget.GetRenderWindow().Render()
        except Exception as e:
            print(f"Error setting right view: {e}")

    # =============== Aniket  added on 07-05-2026: Rotation constraint implementation =============== #
    def apply_rotation_constraint(self):
        """Freeze the camera rotation to bounded angles while keeping the point cloud visible."""
        if not self.renderer or not self.interactor:
            return

        try:
            import math

            camera = self.renderer.GetActiveCamera()
            if not camera:
                return

            if hasattr(self, 'rotation_lock_observer_tags') and self.rotation_lock_observer_tags:
                self.remove_rotation_constraint()
                camera = self.renderer.GetActiveCamera()
                if not camera:
                    return

            focal_point = camera.GetFocalPoint()
            position = camera.GetPosition()
            view_vector = (
                position[0] - focal_point[0],
                position[1] - focal_point[1],
                position[2] - focal_point[2]
            )
            distance = math.sqrt(
                view_vector[0] ** 2 + view_vector[1] ** 2 + view_vector[2] ** 2
            )
            if distance == 0:
                return

            base_azimuth = math.degrees(math.atan2(view_vector[1], view_vector[0]))
            base_elevation = math.degrees(
                math.atan2(view_vector[2], math.sqrt(view_vector[0] ** 2 + view_vector[1] ** 2))
            )

            x_left = float(self.rotation_values.get('x_left', 90.0))
            x_right = float(self.rotation_values.get('x_right', 90.0))
            y_left = float(self.rotation_values.get('y_left', 90.0))
            y_right = float(self.rotation_values.get('y_right', 90.0))

            self.rotation_lock_state = {
                'focal_point': focal_point,
                'distance': distance,
                'base_azimuth': base_azimuth,
                'base_elevation': base_elevation,
                'x_left': x_left,
                'x_right': x_right,
                'y_left': y_left,
                'y_right': y_right,
            }
            self.rotation_lock_active = True
            self.rotation_lock_dragging = False

            def add_observer(event_name, callback):
                tag = self.interactor.AddObserver(event_name, callback)
                self.rotation_lock_observer_tags.append(tag)

            add_observer('LeftButtonPressEvent', self._on_rotation_lock_press)
            add_observer('LeftButtonReleaseEvent', self._on_rotation_lock_release)
            add_observer('InteractionEvent', self._on_rotation_lock_interaction)

            print(
                f"Rotation locked with angles: X-Left={x_left}°, X-Right={x_right}°, "
                f"Y-Left={y_left}°, Y-Right={y_right}°"
            )
            self.update_rotation_state_badge()
        except Exception as e:
            print(f"Error applying rotation constraint: {e}")

    def remove_rotation_constraint(self):
        """Restore free 360° camera interaction."""
        try:
            self.rotation_lock_active = False
            self.rotation_lock_dragging = False
            self.rotation_lock_state = None

            if hasattr(self, 'rotation_lock_observer_tags') and self.rotation_lock_observer_tags and self.interactor:
                for tag in self.rotation_lock_observer_tags:
                    try:
                        self.interactor.RemoveObserver(tag)
                    except Exception:
                        pass
                self.rotation_lock_observer_tags = []

            if hasattr(self, 'vtk_widget') and self.vtk_widget:
                interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
                if interactor:
                    interactor.SetInteractorStyle(vtkInteractorStyleTrackballCamera())

            self.update_rotation_state_badge()
            print("Rotation unlocked - 360° rotation enabled")
        except Exception as e:
            print(f"Error removing rotation constraint: {e}")

    def _normalize_angle(self, angle):
        """Normalize an angle to the [-180, 180] range."""
        while angle > 180.0:
            angle -= 360.0
        while angle < -180.0:
            angle += 360.0
        return angle

    def _on_rotation_lock_press(self, obj, event):
        if self.rotation_lock_active:
            self.rotation_lock_dragging = True

    def _on_rotation_lock_release(self, obj, event):
        self.rotation_lock_dragging = False

    def _on_rotation_lock_interaction(self, obj, event):
        """Clamp camera movement so the point cloud stays visible and does not rotate below the surface."""
        if not self.rotation_lock_active or not self.rotation_lock_state or not self.rotation_lock_dragging:
            return

        try:
            import math

            camera = self.renderer.GetActiveCamera()
            if not camera:
                return

            focal_point = self.rotation_lock_state['focal_point']
            position = camera.GetPosition()
            view_vector = (
                position[0] - focal_point[0],
                position[1] - focal_point[1],
                position[2] - focal_point[2]
            )

            distance = math.sqrt(
                view_vector[0] ** 2 + view_vector[1] ** 2 + view_vector[2] ** 2
            )
            if distance == 0:
                return

            current_azimuth = math.degrees(math.atan2(view_vector[1], view_vector[0]))
            current_elevation = math.degrees(
                math.atan2(view_vector[2], math.sqrt(view_vector[0] ** 2 + view_vector[1] ** 2))
            )

            base_azimuth = self.rotation_lock_state['base_azimuth']
            base_elevation = self.rotation_lock_state['base_elevation']

            azimuth_delta = self._normalize_angle(current_azimuth - base_azimuth)
            elevation_delta = current_elevation - base_elevation

            y_left = self.rotation_lock_state['y_left']
            y_right = self.rotation_lock_state['y_right']
            x_left = self.rotation_lock_state['x_left']
            x_right = self.rotation_lock_state['x_right']

            clamped_azimuth_delta = max(-y_left, min(y_right, azimuth_delta))

            min_elevation = max(0.0, base_elevation - x_left)
            max_elevation = min(90.0, base_elevation + x_right)
            clamped_elevation = max(min_elevation, min(max_elevation, base_elevation + elevation_delta))

            azimuth = base_azimuth + clamped_azimuth_delta
            elevation = clamped_elevation

            azimuth_rad = math.radians(azimuth)
            elevation_rad = math.radians(elevation)
            cos_elevation = math.cos(elevation_rad)

            new_position = (
                focal_point[0] + distance * cos_elevation * math.cos(azimuth_rad),
                focal_point[1] + distance * cos_elevation * math.sin(azimuth_rad),
                focal_point[2] + distance * math.sin(elevation_rad)
            )

            camera.SetPosition(new_position)
            camera.SetFocalPoint(focal_point)
            camera.SetViewUp(0.0, 0.0, 1.0)
            camera.OrthogonalizeViewUp()
            self.renderer.ResetCameraClippingRange()
            self.vtk_widget.GetRenderWindow().Render()
        except Exception as e:
            print(f"Error applying rotation clamp: {e}")

    def eventFilter(self, obj, event):
        """Handle mouse wheel events to prevent scrolling when over VTK or matplotlib"""
        
        if event.type() == QEvent.Wheel:
            # Check if this is the scroll area viewport
            if hasattr(self, 'right_scroll_area') and obj == self.right_scroll_area.viewport():
                # Get current mouse position
                mouse_pos = QCursor.pos()
                
                # Check if mouse is over VTK widget
                if self.vtk_widget:
                    vtk_global_rect = self.vtk_widget.frameGeometry()
                    vtk_global_rect.moveTopLeft(self.vtk_widget.mapToGlobal(self.vtk_widget.rect().topLeft()))
                    
                    if vtk_global_rect.contains(mouse_pos):
                        # Mouse is over VTK - block scroll, allow zoom
                        return True
                
                # Check if mouse is over matplotlib canvas
                if self.canvas:
                    canvas_global_rect = self.canvas.frameGeometry()
                    canvas_global_rect.moveTopLeft(self.canvas.mapToGlobal(self.canvas.rect().topLeft()))
                    
                    if canvas_global_rect.contains(mouse_pos):
                        # Mouse is over canvas - block scroll
                        return True
                    
                # NEW: Check if mouse is over scale section
                if hasattr(self, 'scale_section') and self.scale_section:
                    scale_global_rect = self.scale_section.frameGeometry()
                    scale_global_rect.moveTopLeft(self.scale_section.mapToGlobal(self.scale_section.rect().topLeft()))
                    
                    if scale_global_rect.contains(mouse_pos):
                        # Mouse is over scale section - block scroll, allow scale slider to work
                        return True
        
        return super().eventFilter(obj, event)           

# =================================================================================================================================
    
    def create_menu_section(self):
        """Create right-side menu panel with dynamic asset categories."""
        # --- MENU PANEL SETUP ---
        central_widget = self.centralWidget()
        self.menu_panel = QFrame(central_widget)
        self.menu_panel.setFixedWidth(450)

        # CRITICAL: Set NoFrame to remove any default borders
        self.menu_panel.setFrameShape(QFrame.NoFrame)
        self.menu_panel.setFrameShadow(QFrame.Plain)
        
        # Simple solid background with no borders
        self.menu_panel.setStyleSheet("""
            QFrame {
                background-color: #E8F5E9;
                border: 3px solid #4CAF50;
                border-radius: 5px;
                margin: 0px;
                padding: 0px;
            }
            
            /* Ensure all child widgets have no borders */
            QFrame * {
                border: none;
            }
        """)
        
        # Force white background
        self.menu_panel.setAutoFillBackground(True)
        palette = self.menu_panel.palette()
        palette.setColor(self.menu_panel.backgroundRole(), QColor(255, 255, 255))
        self.menu_panel.setPalette(palette)
        
        # Store animation reference
        self.menu_animation = None
        self.menu_panel.hide()

        # Set up menu layout with no margins at the edges
        menu_layout = QVBoxLayout(self.menu_panel)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)
        
        # Create a container widget for the content
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
                margin: 0px;
                padding: 15px;
            }
        """)
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)
        
        # Create a container for the header to remove spacing between label and button
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # Add title
        title_label = QLabel("MENU")
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 18px;
                color: #2c3e50;
                padding: 15px;
                background-color: #6A0DAD;
                color: white;
                border: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin: 0px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Add Properties Button
        self.properties_btn = QPushButton("Road & Bridge Properties")
        self.properties_btn.setCursor(Qt.PointingHandCursor)
        self.properties_btn.setCheckable(True)
        self.properties_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 12px;
                border: none;
                border-top: 1px solid #218838;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
                text-align: center;
                margin: 8px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:checked {
                background-color: #1e7e34;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)
        header_layout.addWidget(self.properties_btn)

        
        # Create Sub-menu container for "Lane Marking"
        self.properties_submenu = QWidget()
        self.properties_submenu.setVisible(False)
        self.properties_submenu.setStyleSheet("background-color: transparent;")
        submenu_layout = QVBoxLayout(self.properties_submenu)
        submenu_layout.setContentsMargins(0, 0, 0, 0)
        submenu_layout.setSpacing(0)
        
        # Lane Marking Button
        self.lane_marking_btn = QPushButton(" ⛙ Lane Marking")
        self.lane_marking_btn.setCursor(Qt.PointingHandCursor)
        self.lane_marking_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f5;
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border: 1px solid #dee2e6;
                border-top: none;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
                text-align: left;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                color: #28a745;
            }
        """)

        if hasattr(self, 'open_lane_marking_dialog'):
            self.lane_marking_btn.clicked.connect(self.open_lane_marking_dialog)
        
        submenu_layout.addWidget(self.lane_marking_btn)
        header_layout.addWidget(self.properties_submenu)

        # ASSETS Label
        assets_label = QLabel("ASSETS")
        assets_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 16px;
                color: white;
                padding: 10px;
                background-color: #6A0DAD;
                border: none;
                margin: 10px;
            }
        """)
        assets_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(assets_label)

        # Toggle Logic
        self.properties_btn.toggled.connect(self.properties_submenu.setVisible)
        
        content_layout.addWidget(header_container)
        
        # Scroll area for assets
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)
        scroll_area.setWidget(scroll_content)
        content_layout.addWidget(scroll_area)

        # Main Categories
        self.asset_categories = {
            1: {"name": "Road", "icon": "🛣️", "layout": None, "container": None, "button": None},
            2: {"name": "Bridge", "icon": "🌉", "layout": None, "container": None, "button": None},
            3: {"name": "Building", "icon": "🏢", "layout": None, "container": None, "button": None},
            5: {"name": "Tunnel", "icon":"🚇","layout": None, "container": None, "button": None},
            6: {"name": "UnderPass", "icon":"🛣️", "layout": None, "container": None, "button": None}
        }
        
        # Create Category Buttons and Containers based on metadata ONLY
        for cat_id, cat_data in self.asset_categories.items():
            btn = QPushButton(f"{cat_data['icon']} {cat_data['name']}")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 12px;
                    font-size: 16px;
                    font-weight: bold;
                    background-color: #f1f3f5;
                    border: 1px solid #ced4da;
                    border-radius: 5px;
                    color: #495057;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    color: #28a745;
                }
                QPushButton:checked {
                    background-color: #28a745;
                    color: white;
                }
            """)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            
            container = QWidget()
            container.setVisible(False)
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(20, 5, 5, 5)
            container_layout.setSpacing(5)
            
            # Handler to fetch assets dynamically when category is expanded
            def on_category_toggled(checked, c_id=cat_id, c_layout=container_layout, c_widget=container):
                c_widget.setVisible(checked)
                if checked:
                    # Clear existing items first
                    while c_layout.count() > 1: # Keep the stretch
                        item = c_layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                    
                    try:
                        assets = WorksheetAPI.get_asset_data()
                        
                        # Map friendly names to known handlers
                        handlers_map = {
                            "street light": "open_street_light_dialog",
                            "street lights": "open_street_light_dialog",
                            "one directional street light": "open_one_direction_street_light_dialog",
                            "two directional street light": "open_two_direction_street_light_dialog",
                            "four directional street light": "open_four_direction_street_light_dialog",
                            "signal": "open_signal_pole_dialog",
                            "signal pole": "open_signal_pole_dialog",
                            "signals": "open_signal_pole_dialog",
                            "one directional signal pole": "open_one_direction_signal_pole_dialog",
                            "two directional signal pole": "open_two_direction_signal_pole_dialog",
                            "four directional signal pole": "open_four_direction_signal_pole_dialog",
                            "side wall": "open_side_wall_dialog",
                            "side walls": "open_side_wall_dialog",
                            "side wall / anticrash barrier": "open_side_wall_dialog",
                            "side wall/ anticrash barrier": "open_side_wall_dialog",
                            "side wall /anticrash barrier": "open_side_wall_dialog",
                            "anti crash barrier or side edge": "open_side_wall_dialog",
                            "anti crash barrier": "open_side_wall_dialog",
                            "anticrash barrier": "open_side_wall_dialog",
                            "foothpath": "open_footpath_dialog",
                            "foothpaths": "open_footpath_dialog",
                            "footpath": "open_footpath_dialog",
                            "footpaths": "open_footpath_dialog",
                            "divider": "open_divider_dialog",
                            ## Mayur Wakhare 1-07-2026 Upadate code for tunnel Light 
                            "dividers": "open_divider_dialog",
                            ## Mayur Wakhare 3-7-2026 Tunnel Fire
                            "tunnel light": "open_tunnel_light_dialog",
                            "underpass light": "open_underpass_light_dialog",
                            "underpass cctv": "open_underpass_cctv_dialog",
                            "fire extinguisher": "open_fire_extinguisher_dialog",
                            "cctv camera": "open_cctv_camera_dialog",
                            "tunnel exhaust fan": "open_tunnel_exhaust_fan_dialog",
                            "water pipe": "open_water_pipe_dialog",
                            "tunnel wall": "open_tunnel_wall_dialog",
                            "underpass wall": "open_underpass_wall_dialog"
                            ########################################
                        }

                        # Filter and add asset buttons
                        has_assets = False
                        for asset in assets:
                            a_name = asset.get("asset_name", "Unknown")
                            a_belongs_to = asset.get("asset_belongs_to") # 1=Road, 2=Bridge, 3=Building
                            
                            # Filter: Must match category ID AND NOT be "Lane Marking" or "Lane"
                            lower_name = a_name.lower().strip()
                            if a_belongs_to == c_id and "lane" not in lower_name:
                                has_assets = True
                                asset_btn = QPushButton(f"➔ {a_name}")
                                asset_btn.setStyleSheet("""
                                    QPushButton {
                                        text-align: left;
                                        padding: 8px;
                                        font-size: 14px;
                                        background: transparent;
                                        border: none;
                                        color: #6c757d;
                                    }
                                    QPushButton:hover {
                                        color: #28a745;
                                        font-weight: bold;
                                        background-color: #f8fff9;
                                        border-radius: 4px;
                                    }
                                """)
                                asset_btn.setCursor(Qt.PointingHandCursor)
                                asset_btn.setObjectName(f"btn_asset_{lower_name.replace(' ', '_')}")
                                ### Mayur Wakhare 4-7-2026 Tunnel Signage Board Code start
                                if lower_name == "tunnel signage board":
                                    from PyQt5.QtWidgets import QMenu, QAction
                                    menu = QMenu(asset_btn)
                                    menu.setStyleSheet("""
                                        QMenu { background-color: white; border: 1px solid #ccc; }
                                        QMenu::item { padding: 8px 25px; font-size: 13px; color: #333; }
                                        QMenu::item:selected { background-color: #f8fff9; color: #28a745; font-weight: bold; }
                                    """)
                                    
                                    actions_map = {
                                        "Tunnel Information Board": "open_tunnel_info_board_dialog",
                                        # "Speed Limit Board": "open_speed_limit_board_dialog",
                                        # "Emergency Exit Board": "open_emergency_exit_board_dialog",
                                        "Fire Extinguisher Board": "open_fire_extinguisher_dir_board_dialog",
                                        "Emergency Telephone Board": "open_emergency_telephone_board_dialog",
                                        # "CCTV Surveillance Board": "open_cctv_surveillance_board_dialog",
                                        # "Headlights ON Board": "open_headlights_on_board_dialog",
                                        # "No Overtaking Board": "open_no_overtaking_board_dialog",
                                        # "Variable Message Sign (VMS)": "open_vms_board_dialog",
                                        # "Exit Distance Board": "open_exit_distance_board_dialog"
                                    }
                                    
                                    for label, method_name in actions_map.items():
                                        action = QAction(label, menu)
                                        menu.addAction(action)
                                        
                                        if hasattr(self, 'handle_asset_selection'):
                                            a_id = asset.get('aha_id') or asset.get('asset_id')
                                            action.triggered.connect(lambda ch=False, x_id=a_id, m=method_name: self.handle_asset_selection(x_id, m))
                                        else:
                                            if hasattr(self, method_name):
                                                action.triggered.connect(getattr(self, method_name))
                                                
                                    asset_btn.setMenu(menu)
                                else:
                                    #######################################################
                                    handler_name = handlers_map.get(lower_name)
                                    if hasattr(self, 'handle_asset_selection') and handler_name:
                                        a_id = asset.get('aha_id') or asset.get('asset_id')
                                    ### Mayur Wakhare 4-7-2026 Tunnel Signage Board
                                        asset_btn.clicked.connect(lambda ch=False, x_id=a_id, x_h=handler_name: self.handle_asset_selection(x_id, x_h))
                                    ########################################################################################
                                    elif handler_name and hasattr(self, handler_name):
                                        asset_btn.clicked.connect(getattr(self, handler_name))
                                
                                # Compatibility references
                                if lower_name in ["street lights", "street light"]:
                                    self.street_light_btn = asset_btn
                                elif lower_name in ["signal", "signal pole", "signals"]:
                                    self.signal_btn = asset_btn

                                c_layout.insertWidget(c_layout.count() - 1, asset_btn)
                        
                        if not has_assets:
                            no_msg = QLabel("No assets found")
                            no_msg.setStyleSheet("color: gray; font-style: italic; padding-left: 10px;")
                            c_layout.insertWidget(0, no_msg)

                    except Exception as e:
                        print(f"Error fetching assets for category {c_id}: {e}")

            btn.toggled.connect(on_category_toggled)

            scroll_layout.addWidget(btn)
            scroll_layout.addWidget(container)
            
            self.asset_categories[cat_id]["layout"] = container_layout
            self.asset_categories[cat_id]["container"] = container
            self.asset_categories[cat_id]["button"] = btn

        # Add stretch to push everything up
        scroll_layout.addStretch()

        
        menu_layout.addWidget(content_widget)
        self.menu_panel_initial_pos = QPoint(0, 0)
        
        # Connect the menu button (green arrow) to toggle the menu
        if hasattr(self, 'menu_button'):
            try:
                self.menu_button.clicked.disconnect()
            except:
                pass
            # Try to connect to toggle_menu_panel first (new name), then toggle_menu (old name)
            if hasattr(self, 'toggle_menu_panel'):
                self.menu_button.clicked.connect(self.toggle_menu_panel)
            elif hasattr(self, 'toggle_menu'):
                self.menu_button.clicked.connect(self.toggle_menu)

    def handle_asset_selection(self, asset_id, handler_name):
        """Stores the selected asset ID and calls the specific dialog handler."""
        self.current_asset_id = asset_id
        # print(f"Asset selected: {asset_id}, calling handler: {handler_name}")
        if hasattr(self, handler_name):
            getattr(self, handler_name)()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Not Implemented", f"Handler '{handler_name}' is not yet implemented.")

    def create_simulation_panel(self):
        """Create an empty simulation panel that opens from the right side."""
        central_widget = self.centralWidget()
        self.simulation_panel = QFrame(central_widget)
        # 250 is a much more realistic narrow width that fits the text
        self.simulation_panel.setFixedWidth(250)
        
        # Set NoFrame to remove any default borders
        self.simulation_panel.setFrameShape(QFrame.NoFrame)
        self.simulation_panel.setFrameShadow(QFrame.Plain)
        
        # Styling for simulation panel
        self.simulation_panel.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 3px solid #2196F3;
                border-radius: 5px;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        # Force background color
        self.simulation_panel.setAutoFillBackground(True)
        palette = self.simulation_panel.palette()
        palette.setColor(self.simulation_panel.backgroundRole(), QColor(245, 245, 245))
        self.simulation_panel.setPalette(palette)
        
        # Store animation reference
        self.simulation_animation = None
        self.simulation_panel.hide()
        
        # Set up panel layout
        simulation_layout = QVBoxLayout(self.simulation_panel)
        simulation_layout.setContentsMargins(0, 0, 0, 0)
        simulation_layout.setSpacing(0)
        
        # Create content widget
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
                margin: 0px;
                padding: 15px;
            }
        """)
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 20)
        content_layout.setSpacing(10)
        
        # Title
        title_label = QLabel("SIMULATION")
        title_label.setMinimumWidth(100) # Allow label to be compressed
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 18px;
                color: white;
                padding: 15px;
                background-color: #2196F3;
                border: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin: 0px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Worksheet Name Label
        self.simulation_worksheet_label = QLabel("No active worksheet")
        self.simulation_worksheet_label.setAlignment(Qt.AlignCenter)
        self.simulation_worksheet_label.setWordWrap(True)
        self.simulation_worksheet_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #333;
                padding: 10px;
                background-color: #e3f2fd;
                border-radius: 4px;
                margin-bottom: 10px;
            }
        """)
        content_layout.addWidget(self.simulation_worksheet_label)
        
        # --- NEW: Simulation Stages Section ---
        self.stages_group = QGroupBox("Simulation Stages")
        self.stages_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #2196F3;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #0D47A1;
                background-color: #E3F2FD;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                background-color: #2196F3;
                color: white;
                border-radius: 3px;
            }
            QCheckBox {
                font-size: 13px;
                color: #333;
                padding: 5px;
            }
            QCheckBox:disabled {
                color: #9E9E9E;
            }
        """)
        self.stages_vbox = QVBoxLayout(self.stages_group)
        self.stage_checkboxes = []
        content_layout.addWidget(self.stages_group)
        # --------------------------------------
        
        # Create Scroll Area for the report content
        from PyQt5.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        
        # Create a container for the report
        report_container = QWidget()
        report_container.setStyleSheet("background: transparent; border: none;")
        self.simulation_report_layout = QVBoxLayout(report_container)
        self.simulation_report_layout.setContentsMargins(10, 5, 10, 5)
        self.simulation_report_layout.setSpacing(8)
        
        scroll_area.setWidget(report_container)
        content_layout.addWidget(scroll_area, 1) # Add stretch factor to push button down
        
    # === Anket made changes for the simulation button and panel === on 04-05-2026
        # --- Floating Play Simulation Button ---
        self.play_simulation_btn = QPushButton("▶")
        # Ensure it's parented to the main application window or central widget
        # so it floats above the rest of the UI.
        self.play_simulation_btn.setParent(central_widget)
        self.play_simulation_btn.setToolTip("Play/Pause Simulation")
        # Fixed size for a round floating button
        self.play_simulation_btn.setFixedSize(60, 60)
        self.play_simulation_btn.setCursor(Qt.PointingHandCursor)
        # Style as a floating, round video play button
        self.play_simulation_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 28px;
                border: none;
                border-radius: 30px; /* half of 60 to make it circular */
                padding-left: 4px; /* offset slightly for visual centering of inner triangle */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        self.play_simulation_btn.hide() # Hidden until a worksheet is active
        # We don't add it to any layout so it stays floating
        
        simulation_layout.addWidget(content_widget)
        self.simulation_panel_initial_pos = QPoint(0, 0)
        
        # Connect simulation button to toggle panel
        if hasattr(self, 'simulation_button'):
            self.simulation_button.clicked.connect(self.toggle_simulation_panel)


    def _update_worksheets_scroll_height(self):
        """
        Dynamically resize the worksheets scroll area to exactly fit its
        content — no fixed cap, no wasted empty space.
        Scrollbar only appears when entries overflow the maximum allowed height.
        """
        if not hasattr(self, 'worksheets_content') or not hasattr(self, 'worksheets_scroll'):
            return

        # Let Qt calculate the natural content height
        self.worksheets_content.adjustSize()
        needed_height = self.worksheets_content.sizeHint().height()

        # Optional: cap height so it doesn't eat the whole left panel
        MAX_HEIGHT = 250
        capped_height = min(needed_height, MAX_HEIGHT)

        # Show scrollbar only when content exceeds the cap
        if needed_height > MAX_HEIGHT:
            self.worksheets_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.worksheets_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.worksheets_scroll.setMinimumHeight(capped_height)
        self.worksheets_scroll.setMaximumHeight(capped_height)

        # Shrink/grow the frame itself to match
        if hasattr(self, 'worksheets_frame'):
            self.worksheets_frame.adjustSize()

    def _update_two_D_scroll_height(self):
        """
        Dynamically resize the 2D layers scroll area to exactly fit its
        content. Scrollbar only appears when entries overflow the maximum allowed height.
        """
        if not hasattr(self, 'two_D_content') or not hasattr(self, 'two_D_scroll'):
            return

        # Calculate height based on number of items to ensure it doesn't get squished
        # Subtract 1 for the stretch at the bottom
        row_count = max(1, self.two_D_layers_layout.count() - 1)
        needed_height = row_count * 45  # ~45px per row + padding

        # Optional: cap height so it doesn't eat the whole left panel
        MAX_HEIGHT = 350
        capped_height = min(needed_height, MAX_HEIGHT)

        # Show scrollbar only when content exceeds the cap
        if needed_height > MAX_HEIGHT:
            self.two_D_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.two_D_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Give it a safe absolute minimum so it never looks completely broken
        final_height = max(60, capped_height)
        self.two_D_scroll.setMinimumHeight(final_height)
        self.two_D_scroll.setMaximumHeight(final_height)

        # Shrink/grow the frame itself to match
        if hasattr(self, 'two_D_frame'):
            self.two_D_frame.adjustSize()


class WorksheetExistsDialog(QDialog):
    def __init__(self, worksheet_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Worksheet already exists")
        self.setFixedSize(450, 220)
        self.setModal(True)
        self.selected_option = "replace"  # Default selection

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Title label with bold font
        title_label = QLabel(f"Worksheet '{worksheet_name}' already exists")
        title_font = title_label.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Choose what you want to do:")
        layout.addWidget(subtitle_label)

        # Create a group for radio buttons
        radio_group_layout = QVBoxLayout()
        radio_group_layout.setSpacing(10)
        
        # Radio buttons with better spacing
        self.replace_radio = QRadioButton("Replace existing worksheet (overwrite the file)")
        self.new_name_radio = QRadioButton("Save changes with a different name")

        self.replace_radio.setChecked(True)
        self.replace_radio.setMinimumHeight(25)
        self.new_name_radio.setMinimumHeight(25)

        radio_group_layout.addWidget(self.replace_radio)
        radio_group_layout.addWidget(self.new_name_radio)
        layout.addLayout(radio_group_layout)

        layout.addSpacing(15)

        # Buttons with proper size and connection
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        
        self.ok_btn.setMinimumWidth(100)
        self.cancel_btn.setMinimumWidth(100)
        self.ok_btn.setMinimumHeight(35)
        self.cancel_btn.setMinimumHeight(35)
        
        # Set default button
        self.ok_btn.setDefault(True)

        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect buttons - using explicit method references
        self.ok_btn.clicked.connect(self.on_ok_clicked)
        self.cancel_btn.clicked.connect(self.on_cancel_clicked)

    def on_ok_clicked(self):
        """Handle OK button click"""
        print(f"DEBUG: OK button clicked. Replace radio: {self.replace_radio.isChecked()}, New name radio: {self.new_name_radio.isChecked()}")
        self.selected_option = "replace" if self.replace_radio.isChecked() else "new_name"
        print(f"DEBUG: Setting selected_option to: {self.selected_option}")
        self.accept()
    
    def on_cancel_clicked(self):
        """Handle Cancel button click"""
        print("DEBUG: Cancel button clicked")
        self.reject()

    def get_selection(self):
        print(f"DEBUG: get_selection() called. Returning: {self.selected_option}")
        return self.selected_option

class RectangularProgressWindow(QWidget):
    def __init__(self, logo_path, parent=None):
        # Aniket change the code 16-06-2026
        from PyQt5.QtCore import Qt
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(800, 600)
        
        self.progress = 0
        self.displayed_progress = 0.0
        self.loading_message = "Loading !"
        self.file_name = ""
        self.file_size = ""

        from PyQt5.QtGui import QPixmap
        self.logo_pixmap = QPixmap(logo_path)
        
        # Aniket change the code 16-06-2026
        self.cached_shadow = None
        
        import os
        from utils import resource_path
        self.images_dir = resource_path("slide_images")
        self.image_files = []
        for i in range(1, 5):
            path = os.path.join(self.images_dir, f"image_{i}.png")
            if os.path.exists(path):
                # Aniket change the code 16-06-2026
                pixmap = QPixmap(path)
                # Pre-scale images to save CPU during animation
                scaled = pixmap.scaled(730, 390, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.image_files.append(scaled)
                
        self.current_img_idx = 0
        self.next_img_idx = 1 if len(self.image_files) > 1 else 0
        
        self.slide_offset = 0.0
        self.is_sliding = False
        self.wave_offset = 0.0
        
        from PyQt5.QtCore import QTimer
        
        # Timer for animating progress bar smoothly
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.animate_progress)
        self.progress_timer.start(50)
        
        # Timer for triggering slide
        self.slide_timer = QTimer(self)
        self.slide_timer.timeout.connect(self.start_slide)
        self.slide_timer.start(4000) # Switch every 4 seconds
        
        # Timer for sliding animation
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_slide)

    def start_slide(self):
        if len(self.image_files) > 1 and not self.is_sliding:
            self.is_sliding = True
            self.slide_offset = 0.0
            self.anim_timer.start(16) # ~60 fps
            
    def update_slide(self):
        self.slide_offset += 25.0 # pixels per frame (controls sliding speed)
        slide_distance = self.width() - 70 # 2 * margin
        if self.slide_offset >= slide_distance:
            self.slide_offset = 0.0
            self.is_sliding = False
            self.anim_timer.stop()
            self.current_img_idx = self.next_img_idx
            self.next_img_idx = (self.next_img_idx + 1) % len(self.image_files)
        self.update()

    def animate_progress(self):
        diff = self.progress - self.displayed_progress
        if abs(diff) > 0.1:
            self.displayed_progress += diff * 0.02  # Slower easing
        else:
            self.displayed_progress = float(self.progress)
            
        self.wave_offset += 0.5
        if self.wave_offset > 1000:
            self.wave_offset -= 1000
            
        self.update()

    def set_progress(self, val):
        self.progress = val
        self.update()

    def set_loading_message(self, message):
        msg_lower = message.lower()
        if "finalizing" in msg_lower:
            self.loading_message = "Finalize !"
        elif "ready" in msg_lower or "complete" in msg_lower:
            self.loading_message = "Ready !"
        else:
            self.loading_message = "Loading !"
        self.update()

    def set_file_info(self, name, size):
        self.file_name = name
        self.file_size = size
        self.update()

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QBrush, QPainterPath
        from PyQt5.QtCore import Qt, QRect, QRectF
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        rect = self.rect()
        margin = 35 # Margin for shadow
        draw_rect = rect.adjusted(margin, margin, -margin, -margin)

        # 1. Draw glowing shadow
        # Aniket change the code 16-06-2026
        # 1. Draw glowing shadow
        if self.cached_shadow is None:
            from PyQt5.QtGui import QPixmap
            self.cached_shadow = QPixmap(rect.size())
            self.cached_shadow.fill(Qt.transparent)
            shadow_painter = QPainter(self.cached_shadow)
            shadow_painter.setRenderHint(QPainter.Antialiasing)
            for i in range(1, 20):
                opacity = int((20 - i) * 2.5) # Fading out opacity
                shadow_painter.setPen(QPen(QColor(0, 0, 0, opacity), 1))
                shadow_painter.setBrush(Qt.NoBrush)
                shadow_painter.drawRoundedRect(draw_rect.adjusted(-i, -i, i, i), 15, 15)
            shadow_painter.end()

        painter.drawPixmap(0, 0, self.cached_shadow)

        # Define areas
        black_section_height = 140
        image_rect = QRectF(draw_rect.left(), draw_rect.top(), draw_rect.width(), draw_rect.height() - black_section_height)
        black_rect = QRectF(draw_rect.left(), draw_rect.bottom() - black_section_height, draw_rect.width(), black_section_height)

        # 2. Draw Background Image with Clip Path (Top part)
        painter.setClipping(True)
        clip_path = QPainterPath()
        clip_path.addRoundedRect(QRectF(draw_rect), 15, 15)
        painter.setClipPath(clip_path)

        # Base background color
        painter.fillRect(draw_rect, QColor(25, 25, 30))

        # Aniket change the code 16-06-2026
        if self.image_files:
            if self.is_sliding:
                curr_scaled = self.image_files[self.current_img_idx]
                next_scaled = self.image_files[self.next_img_idx]
                
                cx_curr = image_rect.x() + (image_rect.width() - curr_scaled.width()) // 2
                cy_curr = image_rect.y() + (image_rect.height() - curr_scaled.height()) // 2
                
                cx_next = image_rect.x() + (image_rect.width() - next_scaled.width()) // 2
                cy_next = image_rect.y() + (image_rect.height() - next_scaled.height()) // 2
                
                # Draw current image
                painter.save()
                curr_frame = QRectF(image_rect.x() - self.slide_offset, image_rect.y(), image_rect.width(), image_rect.height())
                painter.setClipRect(curr_frame, Qt.IntersectClip)
                painter.drawPixmap(int(cx_curr - self.slide_offset), int(cy_curr), curr_scaled)
                painter.restore()

                # Draw next image
                painter.save()
                next_frame = QRectF(image_rect.x() + image_rect.width() - self.slide_offset, image_rect.y(), image_rect.width(), image_rect.height())
                painter.setClipRect(next_frame, Qt.IntersectClip)
                painter.drawPixmap(int(cx_next + image_rect.width() - self.slide_offset), int(cy_next), next_scaled)
                painter.restore()
            else:
                # Aniket change the code 16-06-2026
                curr_scaled = self.image_files[self.current_img_idx]
                cx_curr = image_rect.x() + (image_rect.width() - curr_scaled.width()) // 2
                cy_curr = image_rect.y() + (image_rect.height() - curr_scaled.height()) // 2
                painter.drawPixmap(int(cx_curr), int(cy_curr), curr_scaled)

        # 3. Draw black section at the bottom
        painter.fillRect(black_rect, QColor(15, 15, 18))
        
        painter.setClipping(False)

        # Content in the black section
        y_start = black_rect.top()

        # 4. Logo and BHARAT Text (Top Left of black section)
        logo_size = 65
        logo_x = draw_rect.left() + 25
        logo_y = y_start + 12
        if not self.logo_pixmap.isNull():
            scaled_logo = self.logo_pixmap.scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(int(logo_x), int(logo_y), scaled_logo)

        bharat_font = QFont('Segoe UI', 22, QFont.Black)
        painter.setFont(bharat_font)
        bharat_text = "BHARAT"
        bharat_width = painter.fontMetrics().boundingRect(bharat_text).width()
        b_x = logo_x + logo_size + 15
        b_y = logo_y + 45

        gradient = QLinearGradient(b_x, 0, b_x + bharat_width, 0)
        gradient.setColorAt(0.0, QColor(255, 153, 51))   # Orange/Saffron
        gradient.setColorAt(0.45, QColor(255, 255, 255)) # White
        gradient.setColorAt(0.55, QColor(255, 255, 255)) # White
        gradient.setColorAt(1.0, QColor(19, 136, 8))     # Green
        
        painter.setPen(QPen(QBrush(gradient), 1))
        painter.drawText(int(b_x), int(b_y), bharat_text)

        # 5. File Info (Top Right of black section)
        fname_font = QFont('Segoe UI', 13)
        painter.setFont(fname_font)
        painter.setPen(QColor(220, 220, 220))
        fm = painter.fontMetrics()
        elided_fname = fm.elidedText(self.file_name, Qt.ElideRight, 350)
        fname_width = fm.boundingRect(elided_fname).width()
        painter.drawText(int(draw_rect.right() - 25 - fname_width), int(y_start + 38), elided_fname)
        
        fsize_font = QFont('Segoe UI', 13, QFont.Bold)
        painter.setFont(fsize_font)
        painter.setPen(QColor(146, 254, 157)) # Light Green
        fsize_width = painter.fontMetrics().boundingRect(self.file_size).width()
        painter.drawText(int(draw_rect.right() - 25 - fsize_width), int(y_start + 63), self.file_size)

        # 6. Loading Message (Bottom Left of black section)
        if self.displayed_progress < 30:
            display_msg = "Loading !"
        elif self.displayed_progress < 70:
            display_msg = "Processing !"
        elif self.displayed_progress < 95:
            display_msg = "Finalizing !"
        else:
            display_msg = "Ready !"
            
        msg_font = QFont('Segoe UI', 14, QFont.Bold)
        painter.setFont(msg_font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(int(draw_rect.left() + 25), int(draw_rect.bottom() - 42), display_msg)

        # 7. Percentage (Bottom Right of black section)
        pct_font = QFont('Segoe UI', 16, QFont.Black)
        painter.setFont(pct_font)
        painter.setPen(QColor(0, 201, 255))
        pct_text = f"{int(self.displayed_progress)}%"
        pct_width = painter.fontMetrics().boundingRect(pct_text).width()
        painter.drawText(int(draw_rect.right() - 25 - pct_width), int(draw_rect.bottom() - 42), pct_text)

        # 8. Linear Progress Bar Track
        bar_height = 14
        bar_rect = QRectF(draw_rect.left() + 25, draw_rect.bottom() - 32, draw_rect.width() - 50, bar_height)
        painter.setBrush(QColor(255, 255, 255, 40))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bar_rect, bar_height/2, bar_height/2)

        # 9. Linear Progress Bar Fill with Continuous Processing
        if self.displayed_progress > 0:
            fill_width = (self.displayed_progress / 100.0) * bar_rect.width()
            fill_rect = QRectF(bar_rect.x(), bar_rect.y(), fill_width, bar_height)
            
            fill_gradient = QLinearGradient(fill_rect.topLeft(), fill_rect.bottomRight())
            fill_gradient.setColorAt(0, QColor(0, 201, 255))
            fill_gradient.setColorAt(1, QColor(0, 150, 255))
            
            painter.save()
            clip_fill = QPainterPath()
            clip_fill.addRoundedRect(fill_rect, bar_height/2, bar_height/2)
            painter.setClipPath(clip_fill)
            
            # Base Fill
            painter.setBrush(QBrush(fill_gradient))
            painter.drawRect(fill_rect)
            
            # Continuous processing animation (sliding angled stripes)
            from PyQt5.QtGui import QPolygonF
            from PyQt5.QtCore import QPointF
            
            stripe_width = 25
            stripe_spacing = 25
            
            # self.wave_offset increments by 0.5 every 50ms. Multiplying by 3 gives a nice, smooth speed.
            offset = (self.wave_offset * 3) % (stripe_width + stripe_spacing)
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 255, 255, 75)) # Increased opacity for much better visibility
            
            # Save state before translating for stripes
            painter.save()
            # Shift the painter starting origin to handle the animation offset and over-draw to the left
            painter.translate(fill_rect.x() + offset - (stripe_width + stripe_spacing), fill_rect.y())
            
            x = 0
            while x < fill_rect.width() + (stripe_width + stripe_spacing) * 2:
                poly = QPolygonF([
                    QPointF(x, bar_height),
                    QPointF(x + stripe_width, bar_height),
                    QPointF(x + stripe_width + bar_height, 0),
                    QPointF(x + bar_height, 0)
                ])
                painter.drawPolygon(poly)
                x += stripe_width + stripe_spacing
            
            painter.restore() # Restore translation
            
            # Sweeping Glow Animation (moves independently faster across the bar)
            glow_width = 80
            glow_x = fill_rect.x() + (self.wave_offset * 8) % (fill_width + glow_width * 2) - glow_width
            glow_rect = QRectF(glow_x, fill_rect.y(), glow_width, bar_height)
            
            glow_gradient = QLinearGradient(glow_rect.topLeft(), glow_rect.topRight())
            glow_gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
            glow_gradient.setColorAt(0.5, QColor(255, 255, 255, 220)) # Very bright center
            glow_gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
            
            painter.setBrush(QBrush(glow_gradient))
            painter.drawRect(glow_rect)
            
            painter.restore()












































