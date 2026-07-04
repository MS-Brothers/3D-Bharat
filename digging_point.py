# digging_point.py

import numpy as np

import vtk

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QGroupBox, QMessageBox,QFormLayout, QComboBox, QLineEdit)
from PyQt5.QtGui import QDoubleValidator


# ==================================================================================================================================
#                                                    ** CLASS DIGGING POINT INPUT **
# ==================================================================================================================================

# Create a class for the Digging Point Inputs::
class DiggingPointInput(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Digging Point")
        self.parent = parent
        self.current_digging_point = 0
        self.current_polygon_point = 0
        self.digging_points = [] # Intilized for to store digging points
        self.polygon_points = [] # Intilized for to store polygon points
        self.input_slides = []   # Intialized for the add new digging slide 
        self.layout = QVBoxLayout()

        # Digging Point Selection Section
        self.digging_point_selection_group = QGroupBox("Digging Point Selection")
        self.digging_point_selection_layout = QHBoxLayout()
        
        # Create a 'New' button to plot new digging point
        self.new_digging_button = QPushButton("New")
        self.new_digging_button.clicked.connect(self.add_new_digging_point)
        self.digging_point_combo = QComboBox()
        self.digging_point_combo.currentIndexChanged.connect(self.select_digging_point)
        
        self.digging_point_selection_layout.addWidget(self.new_digging_button)
        self.digging_point_selection_layout.addWidget(self.digging_point_combo)
        self.digging_point_selection_group.setLayout(self.digging_point_selection_layout)
        self.digging_point_selection_group.setFixedWidth(270)
        
        # Polygon Point Selection Section
        self.polygon_point_group = QGroupBox("Polygon Point Reference")
        self.polygon_point_layout = QHBoxLayout()
        
        # Create a 'Go' button for the to open input slides for that digging-polygon point
        self.go_polygon_button = QPushButton("Go")
        self.go_polygon_button.clicked.connect(self.go_polygon_point)
        self.polygon_point_combo = QComboBox()
        self.polygon_point_combo.currentIndexChanged.connect(self.update_current_polygon_point)
        
        self.polygon_point_layout.addWidget(self.go_polygon_button)
        self.polygon_point_layout.addWidget(self.polygon_point_combo)
        self.polygon_point_group.setLayout(self.polygon_point_layout)
        self.polygon_point_group.setFixedWidth(270)
        
        # Container for input slides
        self.input_slides_container = QWidget()
        self.input_slides_layout = QVBoxLayout()
        self.input_slides_container.setLayout(self.input_slides_layout)
        
        # Action buttons
        self.button_group = QGroupBox()
        self.button_layout = QVBoxLayout()  # Change to vertical layout
        
        # Top row with Save and Reset buttons
        self.top_button_row = QHBoxLayout()
        
        # Create a 'Save' button
        '''Create a save to button to save a diggin points inputs measurements/ lengths of X,Y & Z axis lengths'''
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_digging_point)
        
        '''Reset all button to reset/clear all measurements and visualization'''
        self.reset_button = QPushButton("Reset All")
        self.reset_button.clicked.connect(self.reset_digging_points)
        
        # Add to top row
        self.top_button_row.addWidget(self.save_button)
        self.top_button_row.addWidget(self.reset_button)
        
        '''Plot Digging Point button use to plot digging point on point cloud data by taking reference of the polygon point
        with its digging point axis lengths'''
        self.plot_button = QPushButton("Plot Digging Point")
        self.plot_button.clicked.connect(self.plot_digging_point_from_references)
        self.plot_button.setEnabled(False)
        
        # Buttons Layout
        self.button_layout.addLayout(self.top_button_row)  # Add top row first
        self.button_layout.addWidget(self.plot_button)     # Then add plot button below
        self.button_group.setLayout(self.button_layout)

        # Initialize digging point colors
        self.digging_point_colors = {}        
        
        # Add all sections to main layout
        self.layout.addWidget(self.digging_point_selection_group)
        self.layout.addWidget(self.polygon_point_group)
        self.layout.addWidget(self.input_slides_container)
        self.layout.addWidget(self.button_group)
        
        self.setLayout(self.layout)
        self.setVisible(False)
        
        # Initialize state
        self.button_group.setEnabled(False)

# =============================================================================================================================================
# Add New Input Slide:
    def create_input_slides(self, polygon_point_idx):
        """ Create a new input slide for a polygon point"""
        slide = QGroupBox(f"Polygon Point {chr(65 + polygon_point_idx)}")
        slide_layout = QVBoxLayout()

        # Input fields for X, Y, Z coordinates
        input_group = QGroupBox("Offset Values")
        input_layout = QFormLayout()
        
        x_input = QLineEdit()
        y_input = QLineEdit()
        z_input = QLineEdit()
        
        # Set validators to allow only numbers
        for input_field in [x_input, y_input, z_input]:
            input_field.setValidator(QDoubleValidator())
            input_field.setPlaceholderText("Enter length")
        
        # Add fields to layout
        input_layout.addRow("X-axis length:", x_input)
        input_layout.addRow("Y-axis length:", y_input)
        input_layout.addRow("Z-axis length:", z_input)
        input_group.setLayout(input_layout)
        
        # Next button for this slide
        next_button = QPushButton("Next Polygon Point")
        next_button.clicked.connect(lambda: self.next_polygon_point(polygon_point_idx))
        
        slide_layout.addWidget(input_group)
        slide_layout.addWidget(next_button)
        slide.setLayout(slide_layout)
        
        # Store references to this slide's components
        slide_data = {
            'widget': slide,
            'x_input': x_input,
            'y_input': y_input,
            'z_input': z_input,
            'next_button': next_button,
            'polygon_point_idx': polygon_point_idx
        }
        
        self.input_slides.append(slide_data)
        self.input_slides_layout.addWidget(slide)

        # Load existing values if available
        digging_point = self.digging_points[self.current_digging_point]
        if len(digging_point['offsets']) > polygon_point_idx:
            offsets = digging_point['offsets'][polygon_point_idx]
            x_input.setText(f"{offsets[0]:.2f}")
            y_input.setText(f"{offsets[1]:.2f}")
            z_input.setText(f"{offsets[2]:.2f}")
        
        return slide_data

# =============================================================================================================================================
# Define a function for the add new digging point
    def add_new_digging_point(self):
        """Add a new digging point to the list"""
        new_number = len(self.digging_points) + 1
        self.digging_points.append({
            'number': new_number,
            'polygon_refs': [],
            'offsets': []
        })
        self.digging_point_combo.addItem(f"Digging Point {new_number}")
        self.digging_point_combo.setCurrentIndex(new_number - 1)
        
        # Enable polygon point selection
        if self.parent.measurement_points:
            self.polygon_point_group.setEnabled(True)
            self.update_polygon_point_combo()
            self.plot_button.setEnabled(False)
    
# ==============================================================================================================================================
# Define a fucnction for update the current polygon point
    def update_current_polygon_point(self, index):
        """Update the current polygon point when combo box changes"""
        self.current_polygon_point = index
        #self.select_polygon_point(index)

# ==============================================================================================================================================
# Define a function for the selecting a polygon point by using 'Go' button:
    def go_polygon_point(self):
        """Handle Go button click - activate inputs for selected polygon point and change its color from Red to Green"""
        if not self.digging_points or self.current_digging_point >= len(self.digging_points):
            return
    
        # First reset all polygon point colors to red
        for i in range(len(self.parent.measurement_points)):
            self.parent.change_polygon_point_color(i, "Red")
    
        # Now change the selected point to LightGreen
        selected_point_idx = self.current_polygon_point
        self.parent.change_polygon_point_color(selected_point_idx, "LightGreen")
    
        # Create input slide if it doesn't exist
        slide_exists = any(slide['polygon_point_idx'] == selected_point_idx 
                         for slide in self.input_slides)
    
        if not slide_exists:
            self.create_input_slides(selected_point_idx)
    
        # Enable the button group
        self.button_group.setEnabled(True)
    
        # Load existing values if available
        digging_point = self.digging_points[self.current_digging_point]
        if len(digging_point['offsets']) > selected_point_idx:
            offsets = digging_point['offsets'][selected_point_idx]
            # Find the slide for this polygon point
            for slide in self.input_slides:
                if slide['polygon_point_idx'] == selected_point_idx:
                    slide['x_input'].setText(f"{offsets[0]:.2f}")
                    slide['y_input'].setText(f"{offsets[1]:.2f}")
                    slide['z_input'].setText(f"{offsets[2]:.2f}")
                    break
        else:
            # Clear inputs if no existing values
            for slide in self.input_slides:
                if slide['polygon_point_idx'] == selected_point_idx:
                    slide['x_input'].clear()
                    slide['y_input'].clear()
                    slide['z_input'].clear()
                    break
    
        self.parent.vtk_widget.GetRenderWindow().Render()

# ==============================================================================================================================================
# Define a function after selecting a polygon point change its color from Red to Green to visualize the user
    def select_polygon_point(self, idx=None):
        """Select a polygon point as reference and change its color"""
        if idx is None:
            idx = self.current_polygon_point
        
        if idx < 0 or idx >= len(self.parent.measurement_points):
            return
        
        # Reset all polygon point colors to red first
        for i, point in enumerate(self.parent.measurement_points):
            self.parent.change_polygon_point_color(i, "Red")
    
        # Change selected point to light green
        self.parent.change_polygon_point_color(idx, "LightGreen")
    
        self.current_polygon_point = idx
        self.parent.vtk_widget.GetRenderWindow().Render()

# ==============================================================================================================================================    
# Define a function for select next polygon point for inputs the digging point value
    def next_polygon_point(self, current_idx):
        """Add new input slide for next polygon point and update dropdown"""
        self.save_current_offsets(current_idx)
    
        # Calculate next point index
        next_index = (current_idx + 1) % len(self.parent.measurement_points)
    
        # Update dropdown selection
        self.polygon_point_combo.setCurrentIndex(next_index)
        self.current_polygon_point = next_index
    
        # Change color of new selected point by calling parent's method
        self.parent.change_polygon_point_color(next_index, "LightGreen")
    
        # Create new input slide
        self.go_polygon_point()

# ==============================================================================================================================================    
# Define a function for the plot digging point from the taking reference of polygon point
    def plot_digging_point_from_references(self):
        """Plot digging point using the current polygon point reference"""
        if not self.digging_points or self.current_digging_point >= len(self.digging_points):
            return
            
        current_dp = self.digging_points[self.current_digging_point]
        polygon_point_idx = self.current_polygon_point
        
        # Get the slide for the current polygon point
        current_slide = None
        for slide in self.input_slides:
            if slide['polygon_point_idx'] == polygon_point_idx:
                current_slide = slide
                break
                
        if not current_slide:
            return
            
        try:
            # Get offset values from inputs
            x_offset = float(current_slide['x_input'].text())
            y_offset = float(current_slide['y_input'].text())
            z_offset = float(current_slide['z_input'].text())
            
            # Get the selected polygon point position
            if polygon_point_idx < len(self.parent.measurement_points):
                ref_point = self.parent.measurement_points[polygon_point_idx]
                
                # Calculate digging point position
                digging_pos = ref_point + np.array([x_offset, y_offset, z_offset])
                ''' Calculate interdection point position for the digging point '''
                
                # Plot the digging point
                ''' Plot digging point as per intersection point position '''
                label = f"DP{self.current_digging_point+1}_{chr(65 + polygon_point_idx)}"
                self.parent.add_digging_point(digging_pos, label)
                
                # Save the offsets
                self.save_current_offsets(polygon_point_idx)
                
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter valid numbers for all coordinates!")

# ==============================================================================================================================================
# Define the function for the save current offsets:
    def save_current_offsets(self, polygon_point_idx):
        """Save offset values for current polygon point"""
        slide = next((s for s in self.input_slides 
                     if s['polygon_point_idx'] == polygon_point_idx), None)
        
        if not slide:
            return
            
        try:
            x = float(slide['x_input'].text())
            y = float(slide['y_input'].text())
            z = float(slide['z_input'].text())
            
            digging_point = self.digging_points[self.current_digging_point]
            
            while len(digging_point['offsets']) <= polygon_point_idx:
                digging_point['offsets'].append([0, 0, 0])
                
            digging_point['offsets'][polygon_point_idx] = [x, y, z]
            
            if polygon_point_idx not in digging_point['polygon_refs']:
                digging_point['polygon_refs'].append(polygon_point_idx)
                
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter valid numbers for all coordinates!")

# ==============================================================================================================================================    
# Define a function for to save a digging point:
    def save_digging_point(self):
        """Save the current digging point data without plotting"""
        # Save all open slides
        for slide in self.input_slides:
            self.save_current_offsets(slide['polygon_point_idx'])
        
        self.save_to_file()
        self.plot_button.setEnabled(True)

# ==============================================================================================================================================
# Define a function to sava a input values in .txt file
    def save_to_file(self):
        """Save digging points data to a file"""
        try:
            with open("digging_points.txt", "w") as f:
                for dp in self.digging_points:
                    f.write(f"Digging Point {dp['number']}:\n")
                    for i, offsets in zip(dp['polygon_refs'], dp['offsets']):
                        if i < len(self.parent.measurement_points):
                            label = chr(65 + i)
                            f.write(f"  From Point {label}: X={offsets[0]:.2f}, Y={offsets[1]:.2f}, Z={offsets[2]:.2f}\n")
                    f.write("\n")
                    
            #self.parent.output_list.addItem("Digging points saved to digging_points.txt")
        except Exception as e:
            self.parent.output_list.addItem(f"Error saving digging points: {str(e)}")

# ==============================================================================================================================================
# Define a function for the reset digging points from the point cloud data:
    def reset_digging_points(self):
        """Reset all digging points"""
        # Remove all input slides
        for slide in self.input_slides:
            self.input_slides_layout.removeWidget(slide['widget'])
            slide['widget'].deleteLater()
        self.input_slides = []

        if hasattr(self.parent, 'measurement_actors'):
            # Remove all blue digging point actors and their connecting lines
            actors_to_remove = []

            for actor in self.parent.measurement_actors:
                if isinstance(actor.GetMapper().GetInput(), (vtk.vtkSphereSource, vtk.vtkLineSource)):
                    if (actor.GetProperty().GetColor() == self.parent.colors.GetColor3d("Blue") or 
                        actor.GetProperty().GetColor() == self.parent.colors.GetColor3d("LightGreen")):
                        actors_to_remove.append(actor)

            # Remove all digging point label actors
            for actor in self.parent.measurement_actors:
                if isinstance(actor, vtk.vtkFollower):
                    try:
                        text_source = actor.GetMapper().GetInputConnection(0, 0).GetProducer()
                        if isinstance(text_source, vtk.vtkVectorText):
                            text = text_source.GetText()
                            if text and text.startswith("DP"):  # Digging point labels start with DP
                                actors_to_remove.append(actor)
                    except:
                        continue

            # Remove the actors
            for actor in actors_to_remove:
                self.parent.renderer.RemoveActor(actor)
                if actor in self.parent.measurement_actors:
                    self.parent.measurement_actors.remove(actor)

            self.parent.vtk_widget.GetRenderWindow().Render()

        # Reset UI
        self.digging_points = []
        self.digging_point_combo.clear()
        self.polygon_point_combo.clear()

        self.button_group.setEnabled(False)
        self.polygon_point_group.setEnabled(False)

        # Clear digging points info if it exists
        if hasattr(self.parent, 'digging_points_info'):
            del self.parent.digging_points_info

        self.parent.output_list.addItem("Digging points reset")

        # Hide connection group if visible
        if hasattr(self.parent, 'connection_group'):
            self.parent.connection_group.setVisible(False)
            self.parent.from_digging_combo.clear()
            self.parent.to_digging_combo.clear()
            
        # Deactivate the Action section and reset its background color
        self.parent.action_group.setEnabled(False)
        self.parent.action_group.setStyleSheet("""
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
        """)  # This resets to default styling without the green background
        
        # Uncheck all checkboxes in Action section
        self.parent.measurement_check.setChecked(False)
        self.parent.filling_check.setChecked(False)
        self.parent.cutting_check.setChecked(False)
        self.parent.extraction_check.setChecked(False)
                
# ==============================================================================================================================================
# Define the function for the upadate the polygon points measurements
    def update_polygon_point_combo(self):
        """Update the polygon point combo box with available points"""
        self.polygon_point_combo.clear()
        
        if not hasattr(self.parent, 'measurement_points') or not self.parent.measurement_points:
            return
            
        for i, point in enumerate(self.parent.measurement_points):
            label = chr(65 + i)  # A, B, C, etc.
            self.polygon_point_combo.addItem(f"Point {label}")

# ==============================================================================================================================================
# Define a function for selecting the digging points:
    def select_digging_point(self, index):
        """Select an existing digging point to edit"""
        if index < 0 or index >= len(self.digging_points):
            return
            
        self.current_digging_point = index
        digging_point = self.digging_points[index]
        
        # Clear existing input slides
        for slide in self.input_slides:
            self.input_slides_layout.removeWidget(slide['widget'])
            slide['widget'].deleteLater()
        self.input_slides = []
        
        # Update UI with existing data
        if digging_point['polygon_refs']:
            self.update_polygon_point_combo()
            self.polygon_point_combo.setCurrentIndex(0)
            self.select_polygon_point(0)
            
            # Create input slides for all references
            for i, ref_idx in enumerate(digging_point['polygon_refs']):
                if ref_idx < len(self.parent.measurement_points):
                    self.current_polygon_point = ref_idx
                    slide_data = self.create_input_slides(ref_idx)
                    
                    # Set values from saved data
                    if i < len(digging_point['offsets']):
                        offsets = digging_point['offsets'][i]
                        slide_data['x_input'].setText(f"{offsets[0]:.2f}")
                        slide_data['y_input'].setText(f"{offsets[1]:.2f}")
                        slide_data['z_input'].setText(f"{offsets[2]:.2f}")
            
            self.button_group.setEnabled(True)
            self.plot_button.setEnabled(True)
