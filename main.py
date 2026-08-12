# main.py
import sys
import os

# 1. FORCE HIGH PERFORMANCE GPU (Must be before any GUI/VTK imports)
try:
    from gpu_connection import apply_gpu_priority
    apply_gpu_priority()    
except:
    pass

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QIcon
from pointcloudviewer import PointCloudViewer
from login import LoginDialog   
from welcome_page import WelcomePage
from utils import resource_path, is_internet_connected

from gpu_connection import get_gpu_info

# =====================================================================================================================================
#                                                 ***  CLASS - Appilcation UI Constructor ***
# =====================================================================================================================================
def main():
    import builtins
    import sys
    
    app = QApplication(sys.argv)
    
    # Set global application icon
    app_icon = QIcon(resource_path(os.path.join("data", "app.ico")))
    app.setWindowIcon(app_icon)

    # Capture potential input file from command line (taskbar opening)
    input_file = None
    if len(sys.argv) > 1:
        arg_path = sys.argv[1]
        if os.path.exists(arg_path) and os.path.isfile(arg_path):
            input_file = arg_path

    # Check for internet connection
    if not is_internet_connected():
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(None, "Internet Connection Required", 
                          "Internet connection are required. Please check your connection and try again.")
        sys.exit(0)

    # Show login dialog first 
    login_dlg = LoginDialog()
    login_result = login_dlg.exec_()
    
    if login_result != QDialog.Accepted:
        # User completely cancelled/closed the app
        sys.exit(0)

    # Proceed to welcome and main app
    username = login_dlg.logged_in_username or "Guest"
    user_id = login_dlg.logged_in_user_id or "guest_id"  # euh_id for folder structure
    api_user_id = getattr(login_dlg, 'logged_in_api_user_id', user_id)  # id for API calls
    
    print(f"DEBUG: main.py - Getting user IDs from login_dlg:")
    print(f"  logged_in_username={login_dlg.logged_in_username}")
    print(f"  logged_in_user_id (euh_id)={login_dlg.logged_in_user_id}")
    print(f"  logged_in_api_user_id={getattr(login_dlg, 'logged_in_api_user_id', 'NOT SET')}")
    print(f"  Final: user_id={user_id}, api_user_id={api_user_id}")
    
    # Get full name from user config file
    user_full_name = username  # Default to username
    try:
        import json
        user_config_path = os.path.join(r"C:\D_Tool\user", user_id, "user_config.txt")
        if os.path.exists(user_config_path):
            with open(user_config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                user_full_name = user_config.get("full_name", username)
    except Exception:
        pass

    # Show Welcome Page after successful login
    welcome_page = WelcomePage(user_full_name=user_full_name)
    if welcome_page.exec_() != QDialog.Accepted:
        # User closed welcome page without clicking Start Now
        sys.exit(0)

    try:
        # Show main application window maximized (with taskbar visible)
        gpu_info = get_gpu_info()
        print(f"Starting application with: {gpu_info}")
        
        # Show main application window maximized (with taskbar visible)
        window = PointCloudViewer(username=username, user_id=user_id, user_full_name=user_full_name, input_file=input_file, api_user_id=api_user_id)
        window.showMaximized()

        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Application Crash", f"An unhandled exception occurred:\n\n{error_msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()