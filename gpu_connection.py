import sys
import os
import vtk
import ctypes
from PyQt5.QtWidgets import QMessageBox

def apply_gpu_priority():
    """
    Sets environment variables to hint the OS/Driver to use the High-Performance GPU.
    These must be set before any VTK or OpenGL contexts are created.
    """
    # Hints for NVIDIA Optimus and AMD Dual Graphics
    os.environ["__NV_PRIME_RENDER_OFFLOAD"] = "1"
    os.environ["__GLX_VENDOR_LIBRARY_NAME"] = "nvidia"
    os.environ["VK_ICD_FILENAMES"] = "nvidia_icd.json" # For Vulkan fallback
    
    # Windows Specific: Try to load NVIDIA/AMD libraries to 'wake up' the performance profile
    if sys.platform == "win32":
        try:
            # Loading nvapi64 often triggers the driver to switch the process to 'High Performance'
            ctypes.windll.kernel32.LoadLibraryW("nvapi64.dll")
        except: pass
        try:
            ctypes.windll.kernel32.LoadLibraryW("atiadlxx.dll") # AMD equivalent
        except: pass

# Run priority hints immediately on import
apply_gpu_priority()

def get_gpu_info():
    """
    Detects available GPU hardware and returns a description.
    Priority: NVIDIA -> AMD/Generic GPU -> CPU
    """
    try:
        # 1. Check for NVIDIA using nvidia-smi (if installed)
        import subprocess
        try:
            nvidia_info = subprocess.check_output("nvidia-smi --query-gpu=name --format=csv,noheader", shell=True).decode().strip()
            if nvidia_info:
                return f"NVIDIA GPU Detected: {nvidia_info}"
        except:
            pass

        # 2. Check VTK's OpenGL capabilities
        render_window = vtk.vtkRenderWindow()
        render_window.SetOffScreenRendering(1)
        
        gpu_vendor = "Unknown Vendor"
        gpu_renderer = "Unknown Renderer"
        
        try:
            render_window.Render()
            # Try newer methods first
            if hasattr(render_window, 'GetReportGraphicVendor'):
                gpu_vendor = render_window.GetReportGraphicVendor()
                gpu_renderer = render_window.GetReportGraphicRenderer()
            else:
                # Fallback to older/more universal methods if available
                # Note: vtkRenderWindow doesn't always expose these strings directly
                # We'll use a generic status if we can't get details
                gpu_vendor = "Hardware Accelerated"
                gpu_renderer = "Generic GPU"
        except:
            pass
        
        if "NVIDIA" in gpu_vendor.upper():
            return f"NVIDIA GPU Accelerated: {gpu_renderer}"
        elif "AMD" in gpu_vendor.upper() or "ATI" in gpu_vendor.upper():
            return f"AMD GPU Accelerated: {gpu_renderer}"
        elif "INTEL" in gpu_vendor.upper():
            return f"Intel Integrated Graphics: {gpu_renderer}"
        
        return f"Graphics Status: {gpu_vendor} / {gpu_renderer}"
    except Exception as e:
        return f"Fallback Rendering Mode: {str(e)}"

def setup_gpu_acceleration(render_window):
    """
    Configures the VTK RenderWindow for maximum hardware performance.
    """
    try:
        # Enable multi-sampling for better quality
        render_window.SetMultiSamples(4)
        
        # Check if we can use hardware-accelerated depth peeling (for transparency)
        renderer = render_window.GetRenderers().GetFirstRenderer()
        if renderer:
            # Try to enable hardware acceleration features
            render_window.SetAlphaBitPlanes(1)
            renderer.SetUseDepthPeeling(1)
            renderer.SetMaximumNumberOfPeels(8)
            renderer.SetOcclusionRatio(0.1)
            
        return True
    except Exception as e:
        print(f"Hardware optimization note: {e}")
        return False

def show_gpu_status(parent=None):
    """Shows a message box with the current hardware status"""
    info = get_gpu_info()
    QMessageBox.information(parent, "Hardware Acceleration Status", 
                            f"The application is optimized for high performance.\n\n"
                            f"Current Backend: {info}\n\n"
                            "Priority: NVIDIA > AMD > Integrated > CPU")
