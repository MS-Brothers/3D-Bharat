"""
JSON Manager Module - Unified Design & Construction Configuration File Handler
Consolidates all design layer and construction layer JSON data into a single master file.
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

class DesignConstructionManager:
    """
    Manages unified design & construction JSON file.
    All design and construction configurations are saved in one master JSON file.
    
    Structure:
    {
        "design": {
            "zero_line_config": {...},
            "surface_baseline": {...},
            "construction_baseline": {...},
            "road_surface_baseline": {...},
            "operational_config": {...}
        },
        "construction": {
            "zero_line_config": {...},
            "materials": {
                "material_name": {...},
                ...
            }
        },
        "lane_marking": { ... },
        "reference_assets": {
            "side_wall": { ... },
            "divider": { ... },
            "footpath": { ... }
        },
        "asset_mapping": [ ... ]
    }
    """
    
    MASTER_FILENAME = "design_construction_config.json"
    
    @staticmethod
    def get_master_path(layer_root: str) -> str:
        """Get the full path to the master JSON file"""
        return os.path.join(layer_root, DesignConstructionManager.MASTER_FILENAME)
    
    @staticmethod
    def get_default_structure() -> Dict[str, Any]:
        """Get the default empty structure for master JSON"""
        return {
            "design": {
                "zero_line_config": None,
                "surface_baseline": None,
                "construction_baseline": None,
                "road_surface_baseline": None,
                "operational_config": None,
                "polygon_points": None
            },
            "construction": {
                "zero_line_config": None,
                "materials": {}
            },
            "lane_marking": None,
            "reference_assets": {
                "side_wall": None,
                "divider": None,
                "footpath": None
            },
            "asset_mapping": None,
            "underpass_lights": [],
            "underpass_cctvs": []
        }
    
    @staticmethod
    def load_master(layer_root: str) -> Dict[str, Any]:
        """
        Load master JSON file. If it doesn't exist, return default structure.
        
        Args:
            layer_root (str): Path to the design or construction layer root directory
            
        Returns:
            dict: Master configuration dictionary
        """
        path = DesignConstructionManager.get_master_path(layer_root)
        
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
            except Exception as e:
                print(f"ERROR loading master JSON from {path}: {str(e)}")
                return DesignConstructionManager.get_default_structure()
        
        return DesignConstructionManager.get_default_structure()
    
    @staticmethod
    def save_master(layer_root: str, data: Dict[str, Any]) -> bool:
        """
        Save master JSON file.
        
        Args:
            layer_root (str): Path to the design or construction layer root directory
            data (dict): Master configuration dictionary to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        path = DesignConstructionManager.get_master_path(layer_root)
        
        try:
            # Ensure directory exists
            os.makedirs(layer_root, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"ERROR saving master JSON to {path}: {str(e)}")
            return False
    
    @staticmethod
    def set_design_zero_line_config(layer_root: str, config: Dict[str, Any]) -> bool:
        """
        Set zero line configuration for design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            config (dict): Zero line configuration data
            
        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        data["design"]["zero_line_config"] = config
        return DesignConstructionManager.save_master(layer_root, data)
    
    @staticmethod
    def get_design_zero_line_config(layer_root: str) -> Optional[Dict[str, Any]]:
        """
        Get zero line configuration from design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            
        Returns:
            dict or None: Zero line configuration or None if not found
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("design", {}).get("zero_line_config")
    
    @staticmethod
    def set_design_surface_baseline(layer_root: str, surface_baseline: Dict[str, Any]) -> bool:
        """
        Set surface baseline for design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            surface_baseline (dict): Surface baseline data
            
        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        data["design"]["surface_baseline"] = surface_baseline
        return DesignConstructionManager.save_master(layer_root, data)
    
    @staticmethod
    def get_design_surface_baseline(layer_root: str) -> Optional[Dict[str, Any]]:
        """
        Get surface baseline from design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            
        Returns:
            dict or None: Surface baseline or None if not found
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("design", {}).get("surface_baseline")
    
    @staticmethod
    def set_design_construction_baseline(layer_root: str, construction_baseline: Dict[str, Any]) -> bool:
        """
        Set construction baseline for design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            construction_baseline (dict): Construction baseline data
            
        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        data["design"]["construction_baseline"] = construction_baseline
        return DesignConstructionManager.save_master(layer_root, data)
    
    @staticmethod
    def get_design_construction_baseline(layer_root: str) -> Optional[Dict[str, Any]]:
        """
        Get construction baseline from design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            
        Returns:
            dict or None: Construction baseline or None if not found
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("design", {}).get("construction_baseline")
    
    @staticmethod
    def set_design_road_surface_baseline(layer_root: str, road_surface_baseline: Dict[str, Any]) -> bool:
        """
        Set road surface baseline for design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            road_surface_baseline (dict): Road surface baseline data
            
        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        data["design"]["road_surface_baseline"] = road_surface_baseline
        return DesignConstructionManager.save_master(layer_root, data)
    
    @staticmethod
    def get_design_road_surface_baseline(layer_root: str) -> Optional[Dict[str, Any]]:
        """
        Get road surface baseline from design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            
        Returns:
            dict or None: Road surface baseline or None if not found
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("design", {}).get("road_surface_baseline")
    
    @staticmethod
    def set_design_operational_config(layer_root: str, operational_config: Dict[str, Any]) -> bool:
        """
        Set operational configuration for design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            operational_config (dict): Operational configuration data
            
        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        data["design"]["operational_config"] = operational_config
        return DesignConstructionManager.save_master(layer_root, data)
    
    @staticmethod
    def get_design_operational_config(layer_root: str) -> Optional[Dict[str, Any]]:
        """
        Get operational configuration from design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            
        Returns:
            dict or None: Operational configuration or None if not found
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("design", {}).get("operational_config")
    
    @staticmethod
    def set_design_lane_marking(layer_root: str, lane_marking: Dict[str, Any]) -> bool:
        """
        Set lane marking for design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            lane_marking (dict): Lane marking data
            
        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        data["design"]["lane_marking"] = lane_marking
        return DesignConstructionManager.save_master(layer_root, data)
    
    @staticmethod
    def get_design_lane_marking(layer_root: str) -> Optional[Dict[str, Any]]:
        """
        Get lane marking from design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            
        Returns:
            dict or None: Lane marking or None if not found
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("design", {}).get("lane_marking")
    
    @staticmethod
    def set_design_asset_mapping(layer_root: str, asset_mapping: Dict[str, Any]) -> bool:
        """
        Set asset mapping for design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            asset_mapping (dict): Asset mapping data
            
        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        data["design"]["asset_mapping"] = asset_mapping
        return DesignConstructionManager.save_master(layer_root, data)
    
    @staticmethod
    def get_design_asset_mapping(layer_root: str) -> Optional[Dict[str, Any]]:
        """
        Get asset mapping from design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            
        Returns:
            dict or None: Asset mapping or None if not found
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("design", {}).get("asset_mapping")
  #### Mayur Wakhare 17-7-2026 tunnel polygon   
    @staticmethod
    def set_design_polygon_points(layer_root: str, polygon_points: list) -> bool:
        """
        Set polygon points for design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            polygon_points (list): List of polygon points
            
        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        data["design"]["polygon_points"] = polygon_points
        return DesignConstructionManager.save_master(layer_root, data)
    
    @staticmethod
    def get_design_polygon_points(layer_root: str) -> Optional[list]:
        """
        Get polygon points from design layer.
        
        Args:
            layer_root (str): Path to the design layer root directory
            
        Returns:
            list or None: Polygon points or None if not found
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("design", {}).get("polygon_points")
########################################################################################################
    # ==================== HELPER FUNCTIONS FOR LOADING FROM UNIFIED FILE ====================
    
    @staticmethod
    def load_baseline_from_unified(layer_root: str, baseline_key: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific baseline from the unified design_construction_config.json file.
        Used by dialogs and other functions to reference baseline data.
        
        Args:
            layer_root (str): Path to the design layer root directory
            baseline_key (str): Key name like 'surface_baseline', 'construction_baseline', 
                              'road_surface_baseline', 'operational_config', etc.
            
        Returns:
            dict or None: Baseline data or None if not found
        """
        try:
            master_path = DesignConstructionManager.get_master_path(layer_root)
            if os.path.exists(master_path):
                with open(master_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("design", {}).get(baseline_key)
        except Exception as e:
            print(f"Error loading baseline {baseline_key} from unified file: {e}")
        return None

    @staticmethod
    def load_all_baselines_from_unified(layer_root: str) -> Dict[str, Any]:
        """
        Load all baselines from the unified design_construction_config.json file.
        
        Args:
            layer_root (str): Path to the design layer root directory
            
        Returns:
            dict: Dictionary containing all design baselines and configs
        """
        try:
            master_path = DesignConstructionManager.get_master_path(layer_root)
            if os.path.exists(master_path):
                with open(master_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("design", {})
        except Exception as e:
            print(f"Error loading all baselines from unified file: {e}")
        return {}

    @staticmethod
    def load_baseline_by_type(layer_root: str, baseline_type: str) -> Optional[Dict[str, Any]]:
        """
        Load baseline by its type (e.g., 'Surface', 'Construction', 'Road Surface').
        Searches through all baselines in the unified file.
        
        Args:
            layer_root (str): Path to the design layer root directory
            baseline_type (str): Type to search for (e.g., 'Surface', 'Construction')
            
        Returns:
            dict or None: Baseline data if found, None otherwise
        """
        try:
            all_baselines = DesignConstructionManager.load_all_baselines_from_unified(layer_root)
            for key, baseline_data in all_baselines.items():
                if baseline_data and isinstance(baseline_data, dict):
                    if baseline_data.get("baseline_type") == baseline_type:
                        return baseline_data
        except Exception as e:
            print(f"Error loading baseline by type: {e}")
        return None
    
    @staticmethod
    def load_construction_material_from_unified(layer_root: str, material_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific construction material from the unified file.
        
        Args:
            layer_root (str): Path to the construction layer root directory
            material_name (str): Name of the material
            
        Returns:
            dict or None: Material data or None if not found
        """
        try:
            master_path = DesignConstructionManager.get_master_path(layer_root)
            if os.path.exists(master_path):
                with open(master_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    materials = data.get("construction", {}).get("materials", {})
                    return materials.get(material_name)
        except Exception as e:
            print(f"Error loading material {material_name} from unified file: {e}")
        return None
    
    @staticmethod
    def get_construction_zero_line_config(layer_root: str) -> Optional[Dict[str, Any]]:
        """
        Get zero line configuration from construction layer (from unified file).
        
        Args:
            layer_root (str): Path to the construction layer root directory
            
        Returns:
            dict or None: Zero line configuration or None if not found
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("construction", {}).get("zero_line_config")
    
    @staticmethod
    def load_all_construction_materials_from_unified(layer_root: str) -> Dict[str, Any]:
        """
        Load all materials from the unified construction file.
        
        Args:
            layer_root (str): Path to the construction layer root directory
            
        Returns:
            dict: Dictionary containing all construction materials
        """
        try:
            master_path = DesignConstructionManager.get_master_path(layer_root)
            if os.path.exists(master_path):
                with open(master_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("construction", {}).get("materials", {})
        except Exception as e:
            print(f"Error loading all materials from unified file: {e}")
        return {}
    
    # ==================== TOP-LEVEL: lane_marking ====================

    @staticmethod
    def set_lane_marking(layer_root: str, lane_marking: Dict[str, Any]) -> bool:
        """
        Save lane marking data as a top-level 'lane_marking' key in the master JSON.

        Args:
            layer_root (str): Path to the design layer root directory
            lane_marking (dict): Lane marking configuration data

        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        data["lane_marking"] = lane_marking
        return DesignConstructionManager.save_master(layer_root, data)

    @staticmethod
    def get_lane_marking(layer_root: str) -> Optional[Dict[str, Any]]:
        """
        Get the top-level lane marking data from the master JSON.

        Args:
            layer_root (str): Path to the design layer root directory

        Returns:
            dict or None: Lane marking data or None if not found
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("lane_marking")

    # ==================== TOP-LEVEL: reference_assets (side_wall / divider / footpath) ====================

    @staticmethod
    def set_reference_asset(layer_root: str, asset_key: str, asset_data: Dict[str, Any]) -> bool:
        """
        Save a single road reference asset (side_wall | divider | footpath) into the
        top-level 'reference_assets' object of the master JSON.
        Now supports managing multiple elements of the same asset type (e.g. side walls) via dictionary keys based on lane name.
        
        This method can handle two cases:
        1. Single asset with 'lane_name' field: asset_data = {"asset_id": "...", "lane_name": "Left Side Wall", ...}
           -> Will be stored as: reference_assets[asset_key]["Left Side Wall"] = asset_data
        
        2. Dictionary of assets: asset_data = {"Left Side Wall": {...}, "Right Side Wall": {...}}
           -> Will be stored as: reference_assets[asset_key] = asset_data (for drop mode compatibility)

        Args:
            layer_root (str): Path to the design layer root directory
            asset_key (str): One of 'side_wall', 'divider', 'footpath'
            asset_data (dict): Either a single asset config with lane_name, or a dict of assets

        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        if "reference_assets" not in data or not isinstance(data["reference_assets"], dict):
            data["reference_assets"] = {"side_wall": {}, "divider": {}, "footpath": {}}
        
        # Check if asset_data is a single asset or a dict of assets
        # A single asset will have 'asset_id' or 'lane_name' but NOT have all values as dicts
        is_single_asset = isinstance(asset_data, dict) and (
            'asset_id' in asset_data or 'lane_name' in asset_data or
            (asset_data and not all(isinstance(v, dict) for v in asset_data.values() if isinstance(v, dict)))
        )
        
        if is_single_asset:
            # Handle single asset case - extract lane_name and store under that key
            lane_name = asset_data.get("lane_name", "").strip()
            if not lane_name:
                raise ValueError(f"asset_data must contain 'lane_name'. Received: {asset_data}")
            
            # Ensure the category is a dict
            if not isinstance(data["reference_assets"].get(asset_key), dict):
                if data["reference_assets"].get(asset_key) is not None:
                    # Convert old single object format
                    old_obj = data["reference_assets"][asset_key]
                    old_name = old_obj.get("lane_name", "")
                    if old_name:
                        data["reference_assets"][asset_key] = {old_name: old_obj}
                    else:
                        data["reference_assets"][asset_key] = {}
                else:
                    data["reference_assets"][asset_key] = {}
            
            # Store single asset under its lane_name
            data["reference_assets"][asset_key][lane_name] = asset_data
        else:
            # Handle dict of assets case (for drop/bulk operations)
            # asset_data is like {"Left Side Wall": {...}, "Right Side Wall": {...}}
            data["reference_assets"][asset_key] = asset_data
        
        return DesignConstructionManager.save_master(layer_root, data)

    @staticmethod
    def get_reference_asset(layer_root: str, asset_key: str, lane_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Get a specific reference asset. If it's a dict with multiple walls, return the dict or first one depending on usage.

        Args:
            layer_root (str): Path to the design layer root directory
            asset_key (str): One of 'side_wall', 'divider', 'footpath'
            lane_name (str, optional): If provided, returns the specific asset for that lane.

        Returns:
            dict or None: Asset data or None
        """
        data = DesignConstructionManager.load_master(layer_root)
        asset_obj = data.get("reference_assets", {}).get(asset_key)
        
        if isinstance(asset_obj, dict):
            if lane_name and lane_name in asset_obj:
                return asset_obj[lane_name]
            elif asset_obj and "asset_id" not in asset_obj:
                # If it's a dictionary of multiple assets but no specific lane requested, 
                # just return the whole dict of assets or fallback mechanism needed for legacy calls.
                return asset_obj
        return asset_obj

    @staticmethod
    def get_all_reference_assets(layer_root: str) -> Dict[str, Any]:
        """
        Get the entire 'reference_assets' block from the master JSON.

        Args:
            layer_root (str): Path to the design layer root directory

        Returns:
            dict: flattened dictionary of all assets across categories for easy consumption
        """
        data = DesignConstructionManager.load_master(layer_root)
        ref_assets = data.get("reference_assets", {})
        
        flattened = {}
        for key, val in ref_assets.items():
            if val is None:
                continue
            if isinstance(val, dict):
                # Check if it's a nested mapping (multiple matching side walls)
                # or a single old-style dict (legacy support)
                if "asset_id" in val:
                    # Old format: single configuration directly mapped to asset_key
                    flattened[f"{key}_default"] = val
                else:
                    # New format: nested configuration (e.g. key = side_wall, sub_k = "Right Side Wall")
                    for sub_k, sub_val in val.items():
                        flattened[f"{key}_{sub_k}"] = sub_val
            else:
                flattened[f"{key}"] = val
        return flattened

    # ==================== TOP-LEVEL: asset_mapping ====================

    @staticmethod
    def set_asset_mapping(layer_root: str, asset_mapping) -> bool:
        """
        Save pole/street-light asset mapping list as the top-level 'asset_mapping'
        key in the master JSON.

        Args:
            layer_root (str): Path to the design layer root directory
            asset_mapping (list | dict): Asset mapping data (usually a list of records)

        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        data["asset_mapping"] = asset_mapping
        return DesignConstructionManager.save_master(layer_root, data)

    @staticmethod
    def get_asset_mapping(layer_root: str):
        """
        Get the top-level asset mapping data from the master JSON.

        Args:
            layer_root (str): Path to the design layer root directory

        Returns:
            list | dict | None: Asset mapping data or None
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("asset_mapping")

    @staticmethod
    def append_asset_mapping_record(layer_root: str, record: Dict[str, Any]) -> bool:
        """
        Append a single asset mapping record to the top-level 'asset_mapping' list.
        If the list doesn't exist yet it is created.

        Args:
            layer_root (str): Path to the design layer root directory
            record (dict): A single pole/asset mapping record

        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        existing = data.get("asset_mapping") or []
        if not isinstance(existing, list):
            existing = [existing]
        existing.append(record)
        data["asset_mapping"] = existing
        return DesignConstructionManager.save_master(layer_root, data)
    
    @staticmethod
    def set_construction_material(layer_root: str, material_name: str, material_data: Dict[str, Any]) -> bool:
        """
        Set or update a material in construction layer.
        
        Args:
            layer_root (str): Path to the construction layer root directory
            material_name (str): Name of the material
            material_data (dict): Material configuration data
            
        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        data["construction"]["materials"][material_name] = material_data
        return DesignConstructionManager.save_master(layer_root, data)
    
    @staticmethod
    def get_construction_material(layer_root: str, material_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific material from construction layer.
        
        Args:
            layer_root (str): Path to the construction layer root directory
            material_name (str): Name of the material
            
        Returns:
            dict or None: Material data or None if not found
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("construction", {}).get("materials", {}).get(material_name)
    
    @staticmethod
    def get_all_construction_materials(layer_root: str) -> Dict[str, Any]:
        """
        Get all materials from construction layer.
        
        Args:
            layer_root (str): Path to the construction layer root directory
            
        Returns:
            dict: All material configurations
        """
        data = DesignConstructionManager.load_master(layer_root)
        return data.get("construction", {}).get("materials", {})
    
    @staticmethod
    def list_construction_materials(layer_root: str) -> list:
        """
        Get list of all material names in construction layer.
        
        Args:
            layer_root (str): Path to the construction layer root directory
            
        Returns:
            list: List of material names
        """
        materials = DesignConstructionManager.get_all_construction_materials(layer_root)
        return list(materials.keys())
    
    @staticmethod
    def delete_construction_material(layer_root: str, material_name: str) -> bool:
        """
        Delete a material from construction layer.
        
        Args:
            layer_root (str): Path to the construction layer root directory
            material_name (str): Name of the material to delete
            
        Returns:
            bool: True if successful
        """
        data = DesignConstructionManager.load_master(layer_root)
        if material_name in data.get("construction", {}).get("materials", {}):
            del data["construction"]["materials"][material_name]
            return DesignConstructionManager.save_master(layer_root, data)
        return False

    @staticmethod
    def consolidate_design_baselines_from_folder(layer_root: str) -> Dict[str, Any]:
        """
        Consolidate all individual baseline JSON files from design folder
        into the master JSON structure under design.
        
        Also consolidates road asset / lane-marking files into the three new
        top-level sections:
          - lane_marking      <- lane_marking.json
          - reference_assets  <- { side_wall, divider, footpath }
          - asset_mapping     <- assets_mapping.json
        
        Reads files:
        - zero_line_config.json
        - surface_baseline.json
        - construction_baseline.json
        - road_surface_baseline.json
        - operation_config.json  (operational_config)
        - operational_config.json
        - lane_marking.json      -> top-level lane_marking
        - side_wall.json         -> reference_assets.side_wall
        - divider.json           -> reference_assets.divider
        - footpath.json          -> reference_assets.footpath
        - assets_mapping.json    -> top-level asset_mapping
        
        Args:
            layer_root (str): Path to the design layer root directory
            
        Returns:
            Dict: Updated master JSON data with all baselines consolidated
        """
        import glob
        
        # Load or create master JSON
        data = DesignConstructionManager.load_master(layer_root)
        
        # Initialize design if needed
        if "design" not in data:
            data["design"] = {
                "zero_line_config": None,
                "surface_baseline": None,
                "construction_baseline": None,
                "road_surface_baseline": None,
                "operational_config": None,
                "polygon_points": None,
            }

        # Ensure new top-level keys exist
        if "reference_assets" not in data or not isinstance(data.get("reference_assets"), dict):
            data["reference_assets"] = {"side_wall": None, "divider": None, "footpath": None}
        if "lane_marking" not in data:
            data["lane_marking"] = None
        if "asset_mapping" not in data:
            data["asset_mapping"] = None
        
        # ── Design baseline files (mapped under data["design"]) ──────────
        baseline_mappings = {
            "zero_line_config.json": "zero_line_config",
            "surface_baseline.json": "surface_baseline",
            "construction_baseline.json": "construction_baseline",
            "road_surface_baseline.json": "road_surface_baseline",
            "operation_config.json": "operational_config",
            "operational_config.json": "operational_config",
        }
        
        consolidated_count = 0
        
        for filename, design_key in baseline_mappings.items():
            file_path = os.path.join(layer_root, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        baseline_data = json.load(f)
                    data["design"][design_key] = baseline_data
                    consolidated_count += 1
                    print(f"Consolidated {filename} -> design.{design_key}")
                except Exception as e:
                    print(f"Error consolidating baseline from {file_path}: {str(e)})")

        # ── Top-level: lane_marking ──────────────────────────────────────
        lm_path = os.path.join(layer_root, "lane_marking.json")
        if os.path.exists(lm_path):
            try:
                with open(lm_path, 'r', encoding='utf-8') as f:
                    data["lane_marking"] = json.load(f)
                consolidated_count += 1
                print("Consolidated lane_marking.json -> lane_marking")
            except Exception as e:
                print(f"Error consolidating lane_marking.json: {str(e)}")

        # ── Top-level: reference_assets (side_wall, divider, footpath) ──
        ref_asset_files = {
            "side_wall.json": "side_wall",
            "divider.json":   "divider",
            "footpath.json":  "footpath",
        }
        for filename, asset_key in ref_asset_files.items():
            file_path = os.path.join(layer_root, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data["reference_assets"][asset_key] = json.load(f)
                    consolidated_count += 1
                    print(f"Consolidated {filename} -> reference_assets.{asset_key}")
                except Exception as e:
                    print(f"Error consolidating {filename}: {str(e)}")

        # ── Top-level: asset_mapping (pole / street-light mappings) ─────
        am_path = os.path.join(layer_root, "assets_mapping.json")
        if os.path.exists(am_path):
            try:
                with open(am_path, 'r', encoding='utf-8') as f:
                    data["asset_mapping"] = json.load(f)
                consolidated_count += 1
                print("Consolidated assets_mapping.json -> asset_mapping")
            except Exception as e:
                print(f"Error consolidating assets_mapping.json: {str(e)}")
        
        # Save consolidated data back to master JSON
        if consolidated_count > 0:
            success = DesignConstructionManager.save_master(layer_root, data)
            if success:
                print(f"✓ Consolidated {consolidated_count} file(s) into {DesignConstructionManager.get_master_path(layer_root)}")
            return data
        
        return data

    @staticmethod
    def consolidate_material_lines_from_folder(layer_root: str) -> Dict[str, Any]:
        """
        Consolidate all individual material line JSON files from construction folder
        into the master JSON structure under construction.materials.
        
        Scans for files ending with '_material_line.json' and consolidates them.
        
        Args:
            layer_root (str): Path to the construction layer root directory
            
        Returns:
            Dict: Updated master JSON data with all materials consolidated
        """
        import glob
        
        # Load or create master JSON
        data = DesignConstructionManager.load_master(layer_root)
        
        # Initialize construction.materials if needed
        if "construction" not in data:
            data["construction"] = {}
        if "materials" not in data["construction"]:
            data["construction"]["materials"] = {}
        
        # Find all material line JSON files in construction folder
        # Pattern: *_material_line.json or material_*.json or similar
        pattern1 = os.path.join(layer_root, "*_material_line.json")
        pattern2 = os.path.join(layer_root, "material_*.json")
        
        material_files = glob.glob(pattern1) + glob.glob(pattern2)
        
        consolidated_count = 0
        
        for file_path in material_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    material_data = json.load(f)
                
                # Extract material key (use material_line_id, material_line_name, or filename)
                if isinstance(material_data, dict):
                    # Get identifier for this material
                    mat_key = material_data.get('material_line_id') or \
                              material_data.get('material_line_name') or \
                              material_data.get('material_line_folder') or \
                              os.path.splitext(os.path.basename(file_path))[0]
                    
                    # Merge into master JSON
                    data["construction"]["materials"][mat_key] = material_data
                    consolidated_count += 1
                    
            except Exception as e:
                print(f"Error consolidating material from {file_path}: {str(e)}")
        
        # Save consolidated data back to master JSON
        if consolidated_count > 0:
            DesignConstructionManager.save_master(layer_root, data)
        
        return data

    @staticmethod
    def save_all_design_layer_baselines(layer_root: str, layer_name: str = None,
                                       zero_line_config: Dict[str, Any] = None,
                                       surface_baseline: Dict[str, Any] = None,
                                       construction_baseline: Dict[str, Any] = None,
                                       road_surface_baseline: Dict[str, Any] = None,
                                       deck_line: Dict[str, Any] = None,
                                       projection_line: Dict[str, Any] = None,
                                       operational_config: Dict[str, Any] = None,
                                       tunnels: list = None,
                                       tunnel_config: Dict[str, Any] = None,
                                       saved_by: str = "") -> bool:
        """
        Save all design layer baselines into a SINGLE unified JSON file: design_construction_config.json
        
        File name: design_construction_config.json (ALWAYS uses this name, ignores layer_name)
        File location: layer_root directory
        
        Structure:
        {
            "design": {
                "zero_line_config": {...},
                "surface_baseline": {...},
                "construction_baseline": {...},
                "road_surface_baseline": {...},
                "deck_line": {...},
                "projection_line": {...},
                "operational_config": {...},
                "tunnels": [...]
            },
            "saved_at": "timestamp",
            "saved_by": "username"
        }
        
        Args:
            layer_root (str): Path to the design layer root directory
            layer_name (str): Ignored - always saves to design_construction_config.json
            zero_line_config (dict): Zero line configuration data
            surface_baseline (dict): Surface baseline data (or None)
            construction_baseline (dict): Construction baseline data (or None)
            road_surface_baseline (dict): Road surface baseline data (or None)
            deck_line (dict): Deck line data (or None)
            projection_line (dict): Projection line data (or None)
            operational_config (dict): Operational configuration (or None)
            tunnels (list): List of tunnel objects (or None)
            saved_by (str): Username or identifier of person saving
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(layer_root, exist_ok=True)
            
            # ALWAYS use design_construction_config.json filename
            master_filename = "design_construction_config.json"
            master_file_path = os.path.join(layer_root, master_filename)
            
            # Build complete design layer data structure with ALL baselines
            design_data = {
                "zero_line_config": zero_line_config,
                "surface_baseline": surface_baseline,
                "construction_baseline": construction_baseline,
                "road_surface_baseline": road_surface_baseline,
                "deck_line": deck_line,
                "projection_line": projection_line,
                "operational_config": operational_config
            }
            ## Mayur 10-8-2026
            if tunnels is not None:
                design_data["tunnels"] = tunnels
            
            # Load existing master JSON to preserve other sections
            master_data = DesignConstructionManager.load_master(layer_root)
            
            if tunnel_config is not None:
                existing_tunnel = master_data.get("design", {}).get("tunnel", {})
                merged_tunnel = dict(existing_tunnel)
                merged_tunnel.update(tunnel_config)
                design_data["tunnel"] = merged_tunnel
            if "design" not in master_data:
                master_data["design"] = {}
                
            # Preserve existing design data that is not part of this save (like older "tunnel" config, etc.)
            for k, v in design_data.items():
                master_data["design"][k] = v
                
            master_data["saved_at"] = datetime.now().isoformat()
            master_data["saved_by"] = saved_by
            
            with open(master_file_path, 'w', encoding='utf-8') as f:
                json.dump(master_data, f, indent=2, ensure_ascii=False)

            
            print(f"✓ All baselines saved to {master_file_path}")
            return True
            
        except Exception as e:
            print(f"ERROR saving all design layer baselines to {layer_root}: {str(e)}")
            return False

    @staticmethod
    def load_all_design_layer_baselines(layer_root: str, layer_name: str) -> Dict[str, Any]:
        """
        Load all design layer baselines from a single layer JSON file.
        
        Args:
            layer_root (str): Path to the design layer root directory
            layer_name (str): Name of the layer (e.g., "layer-1")
            
        Returns:
            dict: Dictionary containing all baselines:
                  {
                      "zero_line_config": {...},
                      "surface_baseline": {...},
                      "construction_baseline": {...},
                      "road_surface_baseline": {...},
                      "operational_config": {...}
                  }
        """
        layer_filename = f"{layer_name}.json"
        layer_file_path = os.path.join(layer_root, layer_filename)
        
        if os.path.exists(layer_file_path):
            try:
                with open(layer_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
            except Exception as e:
                print(f"Error loading design layer baselines from {layer_file_path}: {str(e)}")
                return {}
        else:
            print(f"Design layer file not found: {layer_file_path}")
            return {}

    @staticmethod
    def get_design_layer_baseline(layer_root: str, layer_name: str, baseline_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific baseline from the layer JSON file.
        
        Args:
            layer_root (str): Path to the design layer root directory
            layer_name (str): Name of the layer (e.g., "layer-1")
            baseline_key (str): Key name (e.g., "surface_baseline", "construction_baseline", "operational_config")
            
        Returns:
            dict or None: Baseline data or None if not found
        """
        layer_data = DesignConstructionManager.load_all_design_layer_baselines(layer_root, layer_name)
        return layer_data.get(baseline_key)


def update_design_construction_config(directory_path, key, data):
    """
    Updates the master Design_construction_config.json file with new data for a specific key.
    Creates the file if it doesn't exist.
    """
    output_filepath = os.path.join(directory_path, "Design_construction_config.json")
    
    # Initialize empty config or load existing
    master_config = {}
    if os.path.exists(output_filepath):
        try:
            with open(output_filepath, 'r') as f:
                master_config = json.load(f)
        except Exception as e:
            print(f"Error reading master config: {e}")
            master_config = {}

    # Update the specific component's data
    master_config[key] = data

    # Save back to file
    try:
        os.makedirs(directory_path, exist_ok=True)
        with open(output_filepath, 'w') as f:
            json.dump(master_config, f, indent=4)
        print(f"Successfully saved {key} to master config at {output_filepath}")
        return True
    except Exception as e:
        print(f"Error saving to master config: {e}")
        return False

def load_from_master_config(directory_path, key):
    """
    Reads specific data from the master Design_construction_config.json file.
    Returns the data if found, or None if the file/key doesn't exist.
    """
    master_filepath = os.path.join(directory_path, "Design_construction_config.json")
    if not os.path.exists(master_filepath):
        return None
        
    try:
        with open(master_filepath, 'r') as f:
            master_config = json.load(f)
            return master_config.get(key)
    except Exception as e:
        print(f"Error reading master config for {key}: {e}")
        return None

def get_config_data(directory_path, filename):
    """
    Unified loader that first checks the master config, then falls back to the individual file.
    """
    key = filename.replace('.json', '')
    if key == "zero_line_config": key = "Zero_linr_config"
    elif key == "bridge_components": key = "Bridge_components"
    
    data = load_from_master_config(directory_path, key)
    if data is not None:
        return data
        
    filepath = os.path.join(directory_path, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading fallback {filepath}: {e}")
    return None

def merge_design_construction_json(directory_path, output_filepath=None):
    """
    Reads multiple JSON files from a directory and merges them into a single 
    JSON dictionary according to the specified structure.
    Saves it to 'Design_construction_config.json' if output_filepath is provided.
    """
    if output_filepath is None:
        output_filepath = os.path.join(directory_path, "Design_construction_config.json")
    
    def load_json(filename):
        filepath = os.path.join(directory_path, filename)
        if not os.path.exists(filepath) and os.path.exists(filepath + '.json'):
            filepath = filepath + '.json'
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                return {}
        return {}

    merged_data = {
        "Zero_linr_config": load_json("zero_line_config.json"),
        "Projection_baseline": load_json("projection_line_baseline.json"),
        "Bridge_components": load_json("bridge_components.json"),
        "decks": load_json("decks.json"),
        "lane_marking": load_json("lane_marking.json"),
        "refernce_assets": {
            "side_wall": load_json("side_wall.json"),
            "anti_crash_barrier": load_json("bridge_anti_crash_barrier.json"),
            "Divider": load_json("divider.json"),
            "Foothpath": load_json("foothpath.json")
        },
        "asset_mapping": {
            "one_direction_strret_light_pole": load_json("single_street_light_pole.json"),
            "two_directional_strret_light_pole": load_json("two_directional_strret_light_pole.json"),
            "four_directional_strret_light_pole": load_json("four_directional_strret_light_pole.json"),
            "one_direction_signal_pole": load_json("one_direction_signal_pole.json"),
            "two_direction_signal_pole": load_json("two_direction_signal_pole.json"),
            "four_direction_signal_pole": load_json("four_direction_signal_pole.json")
        }
    }

    try:
        with open(output_filepath, 'w') as f:
            json.dump(merged_data, f, indent=4)
        print(f"Successfully saved merged data to {output_filepath}")
        return merged_data
    except Exception as e:
        print(f"Error saving to {output_filepath}: {e}")
        return None

