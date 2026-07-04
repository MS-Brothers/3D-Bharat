import os
import json
import math
import random
import base64
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QWidget, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QCursor, QPixmap, QIcon, QPainter, QColor, QRadialGradient, QLinearGradient, QPen
from utils import resource_path
from API import WorksheetAPI

# Folder and file paths
USER_FOLDER = r"C:\3D_Tool\user"
LAST_LOGIN_FILE = os.path.join(USER_FOLDER, "last_login.json")
try:
    os.makedirs(USER_FOLDER, exist_ok=True)
except Exception as e:
    print(f"Error creating user folder: {e}")


# ========== PASSWORD ENCRYPTION/DECRYPTION ==========
# Simple encryption for password storage (NOT military grade - for UI convenience only)
# WARNING: This is basic obfuscation. For production, use cryptography library!

ENCRYPTION_KEY = "3DBharat2024RoadDesign"  # Fixed key for this app

def encrypt_password(password: str) -> str:
    """Encrypt password with simple XOR cipher + base64 encoding"""
    try:
        # XOR with key
        encrypted = bytearray()
        key_index = 0
        for char in password:
            encrypted.append(ord(char) ^ ord(ENCRYPTION_KEY[key_index % len(ENCRYPTION_KEY)]))
            key_index += 1
        
        # Base64 encode for safe storage
        return base64.b64encode(bytes(encrypted)).decode('utf-8')
    except:
        return ""

def decrypt_password(encrypted_password: str) -> str:
    """Decrypt password"""
    try:
        if not encrypted_password:
            return ""
        
        # Base64 decode
        encrypted = base64.b64decode(encrypted_password.encode('utf-8'))
        
        # XOR with key
        decrypted = ""
        key_index = 0
        for byte in encrypted:
            decrypted += chr(byte ^ ord(ENCRYPTION_KEY[key_index % len(ENCRYPTION_KEY)]))
            key_index += 1
        
        return decrypted
    except:
        return ""
# ====================================================


class ModernInfoDialog(QDialog):
    """Attractive modern dialog for notifications"""
    def __init__(self, title, message, icon_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        # Add Qt.Dialog and Qt.SubWindow to flags for better reliability as a frameless modal
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Determine fixed size
        self.setFixedSize(500, 300)
        
        # Use a single layout for the dialog to hold the container
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main container with glassmorphism effect
        self.container = QFrame(self)
        self.container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(15, 25, 45, 0.98), 
                    stop:1 rgba(10, 15, 30, 1.0));
                border: 2px solid rgba(0, 200, 255, 0.5);
                border-radius: 20px;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(15)
        
        # Header / Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #00C8FF;
            font-size: 24px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Message
        msg_label = QLabel(message)
        msg_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            background: transparent;
            border: none;
        """)
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setWordWrap(True)
        container_layout.addWidget(msg_label)
        
        container_layout.addStretch()
        
        # Close/OK Button
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.ok_btn.setFixedSize(120, 40)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0080A0, stop:1 #00B4D8);
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00A0C0, stop:1 #00D4F8);
            }
        """)
        self.ok_btn.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addStretch()
        container_layout.addLayout(btn_layout)
        
        # Add container to main layout only once
        main_layout.addWidget(self.container)

        # Better centering logic
        if parent and parent.isVisible():
            # Center on parent rect
            parent_geo = parent.geometry()
            self.move(parent_geo.center() - self.rect().center())
        else:
            # Fallback to screen center
            from PyQt5.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            self.move(screen.center() - self.rect().center())


class Particle:
    """A glowing particle for the tech animation"""
    def __init__(self, x, y, speed, angle, size, color):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.size = size
        self.color = color
        self.alpha = random.uniform(0.3, 1.0)
        self.alpha_speed = random.uniform(0.01, 0.03)
        self.alpha_dir = 1

    def update(self, width, height):
        # Move particle
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Pulse alpha
        self.alpha += self.alpha_speed * self.alpha_dir
        if self.alpha >= 1.0:
            self.alpha = 1.0
            self.alpha_dir = -1
        elif self.alpha <= 0.2:
            self.alpha = 0.2
            self.alpha_dir = 1
        
        # Wrap around
        if self.x < -20:
            self.x = width + 20
        elif self.x > width + 20:
            self.x = -20
        if self.y < -20:
            self.y = height + 20
        elif self.y > height + 20:
            self.y = -20


class CircuitLine:
    """Animated circuit line for tech effect"""
    def __init__(self, start_x, start_y, length, is_horizontal, color):
        self.start_x = start_x
        self.start_y = start_y
        self.length = length
        self.is_horizontal = is_horizontal
        self.color = color
        self.progress = 0
        self.speed = random.uniform(0.005, 0.02)
        self.glow_phase = random.uniform(0, math.pi * 2)

    def update(self):
        self.progress += self.speed
        if self.progress > 1:
            self.progress = 0
        self.glow_phase += 0.05


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon(resource_path(os.path.join("data", "MI_logo.png"))))
        self.setModal(True)
        
        # Make truly fullscreen - get screen geometry
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # Set frameless and position at 0,0 with full screen size
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(screen_geometry)
        self.move(0, 0)
        
        # Initialize animation elements
        self.particles = []
        self.circuit_lines = []
        self.glow_phase = 0
        self.init_particles()
        self.init_circuit_lines()
        
        # Animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(100)  # ~20 FPS for better performance on low-end systems
        
        # Setup UI
        self.setup_ui()
        
        self.logged_in_username = None
        self.logged_in_user_id = None
        self.load_last_login()

    def init_particles(self):
        """Create floating particles"""
        colors = [
            QColor(0, 200, 255),   # Cyan
            QColor(0, 150, 255),   # Blue
            QColor(100, 200, 255), # Light blue
            QColor(0, 255, 200),   # Teal
        ]
        # Reduced from 50 to 25 for optimization
        for _ in range(25):
            self.particles.append(Particle(
                x=random.uniform(0, 1920),
                y=random.uniform(0, 1080),
                speed=random.uniform(0.3, 1.0),
                angle=random.uniform(0, math.pi * 2),
                size=random.uniform(2, 6),
                color=random.choice(colors)
            ))

    def init_circuit_lines(self):
        """Create circuit line patterns"""
        color = QColor(0, 180, 255, 100)
        # Horizontal lines - Reduced count
        for i in range(8):
            self.circuit_lines.append(CircuitLine(
                start_x=random.uniform(0, 1920),
                start_y=random.uniform(0, 1080),
                length=random.uniform(100, 400),
                is_horizontal=True,
                color=color
            ))
        # Vertical lines - Reduced count
        for i in range(8):
            self.circuit_lines.append(CircuitLine(
                start_x=random.uniform(0, 1920),
                start_y=random.uniform(0, 1080),
                length=random.uniform(100, 400),
                is_horizontal=False,
                color=color
            ))

    def update_animation(self):
        """Update all animation elements"""
        self.glow_phase += 0.02
        for p in self.particles:
            p.update(self.width(), self.height())
        for line in self.circuit_lines:
            line.update()
        self.update()

    def paintEvent(self, event):
        """Paint the animated tech background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # Dark blue gradient background
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(10, 15, 35))
        gradient.setColorAt(0.5, QColor(15, 25, 55))
        gradient.setColorAt(1, QColor(10, 20, 45))
        painter.fillRect(self.rect(), gradient)
        
        # Draw circuit lines
        for line in self.circuit_lines:
            glow = 0.3 + 0.7 * abs(math.sin(line.glow_phase))
            color = QColor(0, 180, 255, int(80 * glow))
            pen = QPen(color, 1)
            painter.setPen(pen)
            
            if line.is_horizontal:
                end_x = line.start_x + line.length * line.progress
                painter.drawLine(int(line.start_x), int(line.start_y), 
                               int(end_x), int(line.start_y))
                # Glowing dot at end
                if line.progress > 0.1:
                    dot_color = QColor(0, 220, 255, int(200 * glow))
                    painter.setBrush(dot_color)
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(QPointF(end_x, line.start_y), 3, 3)
            else:
                end_y = line.start_y + line.length * line.progress
                painter.drawLine(int(line.start_x), int(line.start_y),
                               int(line.start_x), int(end_y))
                if line.progress > 0.1:
                    dot_color = QColor(0, 220, 255, int(200 * glow))
                    painter.setBrush(dot_color)
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(QPointF(line.start_x, end_y), 3, 3)
        
        # Draw floating particles with glow
        for p in self.particles:
            # Outer glow
            glow_gradient = QRadialGradient(QPointF(p.x, p.y), p.size * 3)
            glow_color = QColor(p.color)
            glow_color.setAlpha(int(50 * p.alpha))
            glow_gradient.setColorAt(0, glow_color)
            glow_color.setAlpha(0)
            glow_gradient.setColorAt(1, glow_color)
            painter.setBrush(glow_gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(p.x, p.y), p.size * 3, p.size * 3)
            
            # Core
            core_color = QColor(p.color)
            core_color.setAlpha(int(255 * p.alpha))
            painter.setBrush(core_color)
            painter.drawEllipse(QPointF(p.x, p.y), p.size, p.size)
        
        # Draw corner decorations (tech frame effect)
        self.draw_corner_decorations(painter)
        
        painter.end()

    def draw_corner_decorations(self, painter):
        """Draw futuristic corner decorations"""
        glow = 0.5 + 0.5 * abs(math.sin(self.glow_phase))
        color = QColor(0, 200, 255, int(150 * glow))
        pen = QPen(color, 2)
        painter.setPen(pen)
        
        corner_size = 50
        margin = 30
        w, h = self.width(), self.height()
        
        # Top-left corner
        painter.drawLine(margin, margin, margin + corner_size, margin)
        painter.drawLine(margin, margin, margin, margin + corner_size)
        
        # Top-right corner
        painter.drawLine(w - margin, margin, w - margin - corner_size, margin)
        painter.drawLine(w - margin, margin, w - margin, margin + corner_size)
        
        # Bottom-left corner
        painter.drawLine(margin, h - margin, margin + corner_size, h - margin)
        painter.drawLine(margin, h - margin, margin, h - margin - corner_size)
        
        # Bottom-right corner
        painter.drawLine(w - margin, h - margin, w - margin - corner_size, h - margin)
        painter.drawLine(w - margin, h - margin, w - margin, h - margin - corner_size)

    def setup_ui(self):
        """Setup the login UI on top of the animated background"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Floating close button at top right corner
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setFixedSize(45, 45)
        self.close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 22px;
                color: rgba(255, 255, 255, 0.7);
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 80, 80, 0.6);
                color: white;
            }
            QPushButton:pressed {
                background: rgba(255, 50, 50, 0.8);
            }
        """)
        self.close_btn.clicked.connect(self.close_application)
        # Position at top right corner
        self.close_btn.move(self.width() - 65, 20)
        self.close_btn.raise_()  # Ensure button is on top
        
        # Floating minimize button next to close button
        self.minimize_btn = QPushButton("—", self)
        self.minimize_btn.setFixedSize(45, 45)
        self.minimize_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 22px;
                color: rgba(255, 255, 255, 0.7);
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
                color: white;
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.4);
            }
        """)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.move(self.width() - 120, 20)
        self.minimize_btn.raise_()
        
        # Center container
        main_layout.addStretch(1)
        
        center_h_layout = QHBoxLayout()
        center_h_layout.addStretch(1)
        
        # Main card container - glassmorphic style
        self.card = QFrame()
        self.card.setFixedSize(900, 500)
        self.card.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 40, 0.85);
                border: none;
                border-radius: 15px;
            }
        """)
        
        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        # LEFT SIDEBAR
        left_sidebar = QWidget()
        left_sidebar.setFixedWidth(450)
        left_sidebar.setStyleSheet("background: transparent;")
        sidebar_layout = QVBoxLayout(left_sidebar)
        sidebar_layout.setContentsMargins(30, 40, 30, 40)
        sidebar_layout.setSpacing(20)
        
        # Welcome title
        title = QLabel("Welcome")
        title.setStyleSheet("""
            color: #00C8FF; 
            font-size: 38px; 
            font-weight: bold; 
            background: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title)
        
        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(140, 140)
        self.logo_label.setStyleSheet("background: transparent;")
        logo_path = resource_path(os.path.join("data", "MI_logo.png"))
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.logo_label.setText("LOGO")
            self.logo_label.setStyleSheet("""
                color: #00C8FF; font-size: 24px; font-weight: bold;
                background: rgba(0, 200, 255, 0.1); border-radius: 70px;
                border: none;
            """)
        sidebar_layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
        
        # App name
        app_name = QLabel("Micro Integrated Semiconductor \n Systems Pvt. Ltd.")
        app_name.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background: transparent;")
        app_name.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(app_name)
        
        # Subtitle
        subtitle = QLabel("3D Bharat")
        subtitle.setStyleSheet("color: rgba(0, 200, 255, 0.8); font-size: 22px; background: transparent;")
        subtitle.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(subtitle)
        
        # Decorative line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: rgba(0, 200, 255, 0.2); max-height: 4px; border: none;")
        sidebar_layout.addWidget(line)
        
        # Tagline
        tagline = QLabel("Design Tool")
        tagline.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 22px; background: transparent;")
        tagline.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(tagline)
        
        sidebar_layout.addStretch(1)
        
        # RIGHT CONTENT
        right_frame = QWidget()
        right_frame.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 30, 20)
        
        # Create Login UI directly
        login_widget = self.create_login_ui()
        right_layout.addWidget(login_widget)
        
        card_layout.addWidget(left_sidebar)
        card_layout.addWidget(right_frame, stretch=1)
        
        center_h_layout.addWidget(self.card)
        center_h_layout.addStretch(1)
        
        main_layout.addLayout(center_h_layout)
        main_layout.addStretch(1)

    def load_last_login(self):
        """Load last login credentials including password"""
        if not os.path.exists(LAST_LOGIN_FILE):
            return
        try:
            with open(LAST_LOGIN_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                mobile = data.get("username", "")  # "username" key is reused for mobile/id for compatibility
                encrypted_password = data.get("password", "")
                
                if mobile:
                    self.login_mobile.setText(mobile)
                
                # Decrypt and fill password field
                if encrypted_password:
                    password = decrypt_password(encrypted_password)
                    if password:
                        self.login_pin.setText(password)
        except Exception as e:
            print(f"Error loading last login: {e}")
            pass

    def save_last_login(self, mobile, password=""):
        """Save last login credentials including encrypted password"""
        try:
            encrypted_pwd = encrypt_password(password) if password else ""
            data = {
                "username": mobile,
                "password": encrypted_pwd,
                "saved_at": datetime.now().isoformat()
            }
            with open(LAST_LOGIN_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving last login: {e}")
            pass

    def toggle_login_password_visibility(self):
        """Toggle password visibility in login form"""
        if self.login_pin.echoMode() == QLineEdit.Password:
            self.login_pin.setEchoMode(QLineEdit.Normal)
            # Password now visible - show "hide" icon
            self.login_pin_toggle.setText("\U0001F441\u200D\U0001F5E8")
        else:
            self.login_pin.setEchoMode(QLineEdit.Password)
            # Password now hidden - show "show" icon
            self.login_pin_toggle.setText("\U0001F441")

    def create_login_ui(self):
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 30, 25, 30)

        # Title
        title = QLabel("<h2 style='color:#00C8FF;'>Login to Your Account</h2>")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background: transparent;")
        layout.addWidget(title)

        # Description
        desc = QLabel("Enter your mobile number and password")
        desc.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 12px; background: transparent;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        layout.addSpacing(10)

        # Input field style
        input_style = """
            QLineEdit {
                font-size: 14px; 
                padding: 12px 14px; 
                background: rgba(0, 50, 80, 0.5); 
                border: none; 
                border-radius: 8px;
                color: white;
            }
            QLineEdit:focus {
                background: rgba(0, 60, 100, 0.6);
            }
            QLineEdit::placeholder {
                color: rgba(255,255,255,0.3);
            }
        """

        # Mobile Number
        layout.addWidget(QLabel("Mobile Number:", styleSheet="color:rgba(255,255,255,0.8); font-size:18px; background:transparent;"))
        self.login_mobile = QLineEdit(placeholderText="Enter your mobile number")
        self.login_mobile.setStyleSheet(input_style)
        self.login_mobile.returnPressed.connect(self.do_login)
        layout.addWidget(self.login_mobile)

        # Password with toggle
        layout.addWidget(QLabel("Password:", styleSheet="color:rgba(255,255,255,0.8); font-size:18px; background:transparent;"))
        
        # Create a frame to hold password input and toggle button
        password_frame = QFrame()
        password_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 50, 80, 0.5);
                border: none;
                border-radius: 8px;
            }
        """)
        password_frame_layout = QHBoxLayout(password_frame)
        password_frame_layout.setContentsMargins(0, 0, 8, 0)
        password_frame_layout.setSpacing(0)
        
        self.login_pin = QLineEdit(placeholderText="Enter your password")
        self.login_pin.setEchoMode(QLineEdit.Password)
        self.login_pin.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 12px 14px;
                background: transparent;
                border: none;
                color: white;
            }
            QLineEdit::placeholder {
                color: rgba(255,255,255,0.3);
            }
        """)
        self.login_pin.returnPressed.connect(self.do_login)
        password_frame_layout.addWidget(self.login_pin)
        
        self.login_pin_toggle = QPushButton("\U0001F441")  # Eye icon - click to show password
        self.login_pin_toggle.setFixedSize(36, 36)
        self.login_pin_toggle.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_pin_toggle.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
                color: rgba(0, 200, 255, 0.7);
            }
            QPushButton:hover { color: #00C8FF; }
        """)
        self.login_pin_toggle.clicked.connect(self.toggle_login_password_visibility)
        password_frame_layout.addWidget(self.login_pin_toggle)
        layout.addWidget(password_frame)

        layout.addSpacing(15)

        # Login button only (Get Started removed)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        login_btn = QPushButton("  Login  ")
        login_btn.setCursor(QCursor(Qt.PointingHandCursor))
        login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0080A0, stop:1 #00B4D8);
                color: white; 
                padding: 12px 30px; 
                font-size: 15px; 
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00A0C0, stop:1 #00D4F8);
            }
        """)
        login_btn.clicked.connect(self.do_login)
        btn_layout.addWidget(login_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()
        return widget

    def do_login(self):
        mobile = self.login_mobile.text().strip()
        password = self.login_pin.text()

        if not mobile or not password:
            QMessageBox.warning(self, "Error", "Please enter mobile number and password!")
            return

        if len(mobile) != 10 or not mobile.isdigit():
             QMessageBox.warning(self, "Error", "Mobile number must be 10 digits!")
             return

        # ========== READ APP_TOKEN FROM USER_CONFIG.TXT ==========
        app_token = ""
        login_type = 1  # Default: 1 for road

        # Try to find the most relevant user config: prefer config matching entered mobile
        fallback_token = ""
        if os.path.exists(USER_FOLDER):
            try:
                for user_id_folder in os.listdir(USER_FOLDER):
                    user_config_file = os.path.join(USER_FOLDER, user_id_folder, "user_config.txt")
                    if not os.path.exists(user_config_file):
                        continue
                    try:
                        with open(user_config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    except Exception as e:
                        print(f"DEBUG: Failed to read config {user_config_file}: {e}")
                        continue

                    # If this config matches the entered mobile, prefer it
                    cfg_mobile = config.get("mobile_number") or config.get("username") or config.get("user_mob_no")
                    if cfg_mobile and str(cfg_mobile) == str(mobile):
                        # Prefer explicit app_token field first
                        if config.get("app_token"):
                            app_token = config.get("app_token")
                            print(f"DEBUG: Using app_token from matching user config: {user_config_file}")
                            break
                        # Fallback to token inside raw_api_response
                        raw = config.get("raw_api_response") or {}
                        token_from_response = raw.get("token", "") if isinstance(raw, dict) else ""
                        if token_from_response:
                            app_token = token_from_response
                            print(f"DEBUG: Using token from raw_api_response in matching config: {user_config_file}")
                            break

                    # Keep a fallback token if present (use if no matching mobile found)
                    if not fallback_token:
                        if config.get("app_token"):
                            fallback_token = config.get("app_token")
                        else:
                            raw = config.get("raw_api_response") or {}
                            token_from_response = raw.get("token", "") if isinstance(raw, dict) else ""
                            if token_from_response:
                                fallback_token = token_from_response
                # If we didn't find a matching mobile config but have a fallback, use it
                if not app_token and fallback_token:
                    app_token = fallback_token
                    print(f"DEBUG: No matching mobile config found; using fallback token from another user config")
            except Exception as e:
                print(f"DEBUG: Error while scanning user configs: {e}")

        # Call API with login_type and app_token
        result = WorksheetAPI.login_edu_user(mobile, password, login_type=login_type, app_token=app_token)
        
        # If login fails with 403 (Forbidden) and we had an app_token, retry without it
        if not result.get("success") and "403" in result.get("message", ""):
            print(f"DEBUG: Login failed with 403 (token expired). Retrying without app_token...")
            result = WorksheetAPI.login_edu_user(mobile, password, login_type=login_type, app_token="")
        
        
        if not result.get("success"):
            QMessageBox.warning(self, "Login Failed", result.get("message", "Unknown error"))
            return

        api_data = result.get("data", {})
        user = api_data.get("user", {})
        
        if not user:
            QMessageBox.warning(self, "Login Failed", "Invalid server response: No user data.")
            return

        remaining_days = user.get("remaining_days", 0)
        if remaining_days is None:
            remaining_days = 0
        
        # Check if trial expired
        if remaining_days <= 0:
            msg = (
                "To activate your license for 3D Bharat Road Design Application, "
                "please contact:\n\n"
                "📞 +91 79879 13708\n"
                "📧 sales3@microintegrated.in"
            )
            dlg = ModernInfoDialog("Activate Your License", msg, parent=self)
            dlg.exec_()
            return

        euh_id = user.get("euh_id")
        user_id = user.get("id")  # Extract the user ID for API calls (e.g., 3D files)
        user_name = user.get("user_name")
        
        if not euh_id:
            QMessageBox.warning(self, "Login Failed", "Invalid server response: Missing euh_id.")
            return
        
        if not user_id:
            QMessageBox.warning(self, "Login Failed", "Invalid server response: Missing user id.")
            return

        # ========== LOGIN SUCCESSFUL ==========
        self.logged_in_username = user_name
        self.logged_in_user_id = euh_id  # User ID for general use (folder structure, etc.)
        self.logged_in_api_user_id = user_id  # API User ID for API calls (e.g., 3D files)
        print(f"DEBUG: Login successful. API user_id={user_id}, euh_id={euh_id}, user_name={user_name}")

        # ========== CREATE USER FOLDER AND CONFIG FILE ==========
        user_folder = os.path.join(USER_FOLDER, str(euh_id))
        
        # Create user folder if it doesn't exist
        try:
            if not os.path.exists(user_folder):
                os.makedirs(user_folder, exist_ok=True)
                print(f"Created user folder: {user_folder}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create user directory: {e}")
            return

        # Create/Update user_config.txt
        user_config_file = os.path.join(user_folder, "user_config.txt")
        now = datetime.now()

        # Load existing config to preserve some fields like last_reminder_date
        existing_config = {}
        if os.path.exists(user_config_file):
            try:
                with open(user_config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
            except:
                pass

        # Extract the new app_token from API response for future logins
        new_app_token = ""
        if api_data.get("raw_api_response"):
            new_app_token = api_data.get("raw_api_response", {}).get("token", "")

        # User config data based on API response
        user_config_data = {
            "user_id": str(user_id),  # API User ID (e.g., 7) for API calls like get_edu_3d_files
            "euh_id": str(euh_id),  # EUH ID (e.g., 126002) for folder structure
            "full_name": user_name,
            "email": user.get("user_email_id", ""),
            "username": mobile,
            "mobile_number": user.get("user_mob_no", mobile),
            "login_type": login_type,
            "app_token": new_app_token,
            "employee_data": user.get("employee_data"),
            "student_data": user.get("student_data"),
            "allocation_data": api_data.get("allocation", {}),
            "project_data": api_data.get("project", {}),
            "current_project_id": api_data.get("project", {}).get("ph_id") if api_data.get("project") else None,
            "remaining_days": remaining_days,
            "last_login": now.isoformat(),
            "last_reminder_date": existing_config.get("last_reminder_date"), # Preserve this!
            "raw_api_response": api_data
        }

        try:
            with open(user_config_file, 'w', encoding='utf-8') as f:
                json.dump(user_config_data, f, indent=4, ensure_ascii=False)
        except Exception as file_error:
            print(f"Warning: Could not create user config file: {file_error}")

        # Update last_login.json
        self.save_last_login(mobile, password)

        self.accept()

    def close_application(self):
        """Close the entire application when X button is clicked"""
        from PyQt5.QtWidgets import QApplication
        QApplication.quit()

    def resizeEvent(self, event):
        """Reposition the close button when window resizes"""
        super().resizeEvent(event)
        if hasattr(self, 'close_btn'):
            self.close_btn.move(self.width() - 65, 20)
            self.close_btn.raise_()
        if hasattr(self, 'minimize_btn'):
            self.minimize_btn.move(self.width() - 120, 20)
            self.minimize_btn.raise_()

