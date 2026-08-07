# API.py
import requests
import json
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class WorksheetAPI:
    """Handles communications with the 3dbharat.com server for worksheet data."""
    
    BASE_URL = "https://edu.3dbharat.com/server"

    @staticmethod
    def get_shared_files(user_id, buddy_id=None):
        """
        Fetches shared files for a given user from the API endpoint.

        Args:
            user_id: ID of the user who is receiving/shared-to (required)
            buddy_id: ID of the buddy who shared the files (optional)
        """
        url = f"{WorksheetAPI.BASE_URL}/3dtrial/buddy/shared-files"
        params = {"user_id": user_id}
        # If a buddy_id is provided, add it so server can filter files shared by that buddy
        if buddy_id is not None:
            params.update({"buddy_id": buddy_id})
        try:
            import collections
            response = requests.get(url, params=params, timeout=20)
            print(f"DEBUG: get_shared_files API called with user_id={user_id}, buddy_id={buddy_id}")
            print(f"DEBUG: API URL: {response.url}")
            if response.status_code == 200:
                # Use OrderedDict to absolutely guarantee original JSON order is preserved
                data = response.json(object_pairs_hook=collections.OrderedDict)
                print(f"DEBUG: get_shared_files JSON response: {data}")
                if data.get("status_code") == 200:
                    # Provide fallback in case the API places the list in 'buddy_shared' or 'data'
                    payload = data.get("data") if "data" in data else data.get("buddy_shared", [])
                    return {"success": True, "data": payload}
                else:
                    return {"success": False, "message": data.get("message", "API Error")}
            else:
                return {"success": False, "message": f"Failed with status code {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": f"Error fetching shared files: {str(e)}"}


    @staticmethod
    def login_edu_user(mobile_no, password, login_type=1, app_token=""):
        """
        Authenticates user with mobile number and password.
        login_type: 1 for road (default), other values for different types
        app_token: Token from user_config.txt if available, else empty string
        Returns the API response containing user details.
        """
        url = f"{WorksheetAPI.BASE_URL}/user/edu-login"
        payload = {
            "mobile_no": mobile_no,
            "password": password,
            "login_type": login_type,
        }
        if app_token:
            payload["app_token"] = app_token
        try:
            headers = {
                "Accept": "*/*",
                "Content-Type": "application/json",
                "User-Agent": "PostmanRuntime/7.44.0",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
            response = requests.post(
                url,
                data=json.dumps(payload),
                headers=headers,
                timeout=20
            )
            
            if response.status_code == 200 or response.status_code == 201:
                # Print API payload for debugging
                print("\n=== LOGIN API PAYLOAD (DEBUG) ===")
                print(f"Mobile No: {mobile_no}")
                print(f"Login Type: {login_type}")
                print(f"App Token: {app_token if app_token else '(empty)'}")
                print(f"Full Payload: {json.dumps(payload, indent=2)}")
                print("=== END PAYLOAD DEBUG ===")
                
                return {
                    "success": True,
                    "message": "Login successful.",
                    "data": response.json()
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "message": "incorrect the mobile number & password",
                    "details": response.text
                }
            else:
                details = response.text.strip()
                if not details:
                    details = f"HTTP {response.status_code} returned an empty body"
                return {
                    "success": False,
                    "message": f"Login failed ({response.status_code})",
                    "details": details
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Login error: {str(e)}"
            }

    @staticmethod
    def get_edu_3d_files(user_id):
        """
        Fetches the list of available 3D files for a specific user from the server.
        
        Args:
            user_id: The user ID obtained from the login API response (e.g., 7)
        
        Returns:
            Dictionary with success status and file data or error message
        """
        url = f"{WorksheetAPI.BASE_URL}/3dtrial/files"
        params = {
            "user_id": user_id
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"DEBUG: API /3dtrial/files called with user_id={user_id}")
            print(f"DEBUG: API /3dtrial/files status={response.status_code}")
            print(f"DEBUG: API URL: {response.url}")
            if response.status_code == 200:
                json_data = response.json()
                import json
                print("\n================ FULL API RESPONSE ================")
                print(json.dumps(json_data, indent=4))
                print("===================================================\n")
                
                print("DEBUG: API response data details:")
                if "data" in json_data and isinstance(json_data["data"], list):
                    for i, file_item in enumerate(json_data["data"]):
                        fname = file_item.get("file_name", "Unknown")
                        p_status = file_item.get("purchase_status", "-")
                        p_type = file_item.get("purchase_type", "-")
                        is_purchased = file_item.get("purchased", "False")
                        cat = file_item.get("category_name", "-")
                        print(f"  [{i+1}] File: {fname} | Category: {cat} | Purchase Status: {p_status} | Purchase Type: {p_type} | Purchased: {is_purchased}")
                else:
                    import json
                    print(json.dumps(json_data, indent=4))
                
                # The API might return data in 'data' or 'chainageFiles' or just as the response
                files = json_data.get("data")
                if files is None:
                    files = json_data.get("chainageFiles")
                if files is None:
                    files = json_data.get("files")
                if files is None:
                    files = []

                return {
                    "success": True,
                    "data": files
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to fetch files: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching 3D files: {str(e)}"
            }

    @staticmethod
    def download_file_by_url(url, save_path, progress_callback=None):
        """
        Downloads a file from a direct URL or Google Drive, 
        handling large file confirmation redirects.
        """
        def get_gdrive_params(response_text):
            # Extract all hidden inputs from the Google Drive warning page form
            params = {}
            # Look for <input type="hidden" name="xxx" value="yyy">
            matches = re.findall(r'<input type="hidden" name="([^"]+)" value="([^"]+)">', response_text)
            for name, value in matches:
                params[name] = value
            return params

        try:
            session = requests.Session()
            
            # Google Drive handling
            if 'drive.google.com' in url or 'drive.usercontent.google.com' in url:
                # Initial request to get the warning page
                response = session.get(url, timeout=120)
                # Try to extract parameters from the HTML form (e.g., id, export, confirm, uuid)
                g_params = get_gdrive_params(response.text)
                
                if 'confirm' in g_params:
                    # Found the confirmation form!
                    print(f"DEBUG: Found Google Drive confirmation parameters: {list(g_params.keys())}")
                    # Use the form's action URL or fallback to the standard one
                    action_match = re.search(r'action="([^"]+)"', response.text)
                    download_url = action_match.group(1) if action_match else "https://drive.google.com/uc"
                    
                    # Ensure it's an absolute URL
                    if download_url.startswith('/'):
                        download_url = "https://drive.google.com" + download_url
                    
                    response = session.get(download_url, params=g_params, stream=True, timeout=120)
                else:
                    # No confirm token in form, check cookies as fallback
                    confirm_token = None
                    for key, value in response.cookies.items():
                        if key.startswith('download_warning'):
                            confirm_token = value
                            break
                    
                    if confirm_token:
                        file_id = ""
                        id_match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
                        if id_match:
                            file_id = id_match.group(1)
                        else:
                            parsed = urlparse(url)
                            file_id = parse_qs(parsed.query).get('id', [''])[0]
                        
                        if file_id:
                            print(f"DEBUG: Found GD warning cookie. Resubmitting for ID: {file_id}")
                            params = {'id': file_id, 'confirm': confirm_token, 'export': 'download'}
                            response = session.get("https://drive.google.com/uc", params=params, stream=True, timeout=120)
                    else:
                        # If no token at all, maybe it's already the file or needs to be streamed
                        content_sample = response.content[:100].decode('utf-8', errors='ignore').lower()
                        if "<!doctype html" not in content_sample and "<html" in content_sample:
                            response = session.get(url, stream=True, timeout=120)
            else:
                # Non-GDrive or already direct: USE STREAM=TRUE TO START IMMEDIATELY
                response = session.get(url, stream=True, timeout=120)
            
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            # Write to file
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if progress_callback and total_size > 0:
                            percent = int((downloaded_size / total_size) * 100)
                            progress_callback(percent)
                        
            return {"success": True, "message": "File downloaded successfully."}
        except Exception as e:
            print(f"DEBUG: Download failed: {str(e)}")
            return {"success": False, "message": str(e)}



    @staticmethod
    def send_feedback(user_id, user_type, message):
        """
        Sends user feedback to the server.
        """
        url = f"{WorksheetAPI.BASE_URL}/user/feedback"
        payload = {
            "euh_id": user_id,
            "user_type": user_type,
            "feedback_message": message
        }
        try:
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                return {
                    "success": True,
                    "message": "Feedback sent successfully."
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to send feedback ({response.status_code})",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error sending feedback: {str(e)}"
            }


    @staticmethod
    def get_road_materials():
        """
        Fetches the list of available road materials from the server.
        Returns a list of dicts: [{'id': 1, 'material_name': '...', 'rmh_id': ...}, ...]
        """
        url = f"{WorksheetAPI.BASE_URL}/road/get-materials"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Debug print (disabled)
                # print(f"API Response for get-road-materials: {data}")
                
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # Try common keys for wrapped lists
                    if 'data' in data and isinstance(data['data'], list):
                        return data['data']
                    if 'materials' in data and isinstance(data['materials'], list):
                        return data['materials']
                    if 'result' in data and isinstance(data['result'], list):
                        return data['result']
                    # If it's a dict but we can't find a list, maybe the dict itself is the object? 
                    # Unlikely for "get all", but safe to return empty list or specific handling
                    return []
                return []
            else:
                print(f"Failed to fetch materials: {response.status_code} {response.text}")
                return []
        except Exception as e:
            print(f"Error fetching materials: {e}")
            return []
        
    @staticmethod
    def get_asset_data():
        """
        Fetches the list of available assets from the server.
        Returns a list of dicts: [{'id': 1, 'asset_name': '...', 'asset_type': ...}, ...]
        """
        url = f"{WorksheetAPI.BASE_URL}/asset/get-data"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    if 'data' in data and isinstance(data['data'], list):
                        return data['data']
                    if 'assets' in data and isinstance(data['assets'], list):
                        return data['assets']
                    if 'result' in data and isinstance(data['result'], list):
                        return data['result']
                    return []
                return []
            else:
                print(f"Failed to fetch assets: {response.status_code} {response.text}")
                return []
        except Exception as e:
            print(f"Error fetching assets: {e}")
            return []

    @staticmethod
    def upload_technical_data(file_id, file_name, category_id, upload_design, upload_material):
        """
        Uploads design and material JSON data to the server.
        
        Args:
            file_id: The ID of the file.
            file_name: The name of the file (e.g., 'Road Design.ply').
            category_id: The category ID.
            upload_design: Dictionary containing design_construction_config.json data.
            upload_material: Dictionary containing material_construction_config.json data.
            
        Returns:
            Dictionary with success status, message, and details.
        """
        url = f"{WorksheetAPI.BASE_URL}/3dtrial/files/update-technical-data"
        payload = {
            "file_id": file_id,
            "file_name": file_name,
            "category_id": category_id,
            "upload_design": upload_design,
            "upload_material": upload_material
        }
        
        print("\n=== UPLOAD TECHNICAL DATA PAYLOAD (DEBUG) ===")
        print(json.dumps(payload, indent=4))
        print("=============================================\n")
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 201:
                return {
                    "success": True,
                    "message": "Technical data uploaded successfully.",
                    "data": response.json() if response.text else {}
                }
            else:
                return {
                    "success": False,
                    "message": f"Upload failed ({response.status_code})",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Upload error: {str(e)}"
            }



    @staticmethod
    def search_buddy(user_id, buddy_email, buddy_mobile, login_type=1):
        """
        Mode 1: Search for a buddy by email and mobile number.
        
        Args:
            user_id: Current logged-in user ID (req_sent_by)
            buddy_email: Email of the buddy to search
            buddy_mobile: Mobile number of the buddy to search
            login_type: User login type (default 1 for road)
        
        Returns:
            Dictionary with success status and buddy data or error message
        """
        url = f"{WorksheetAPI.BASE_URL}/3dtrial/buddy/send-request"
        payload = {
            "mode": 1,
            "req_sent_by": user_id,
            "buddy_email": buddy_email,
            "buddy_mobile": buddy_mobile
        }
        try:
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=20
            )
            
            print(f"\n=== BUDDY SEARCH API DEBUG ===")
            print(f"URL: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            print("==============================\n")
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Buddy found",
                    "data": response.json()
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "message": "Buddy not found",
                    "details": response.text
                }
            else:
                return {
                    "success": False,
                    "message": f"Search failed ({response.status_code})",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Buddy search error: {str(e)}"
            }

    @staticmethod
    def make_buddy(user_id, buddy_id):
        """
        Mode 2: Send a buddy request to create a buddy relationship.
        
        Args:
            user_id: Current logged-in user ID (req_sent_by)
            buddy_id: ID of the buddy to send request to (req_sent_to). Can be a single ID or a list of IDs.
        
        Returns:
            Dictionary with success status and response data or error message
        """
        url = f"{WorksheetAPI.BASE_URL}/3dtrial/buddy/send-request"
        
        # Handle both single ID and list of IDs
        if isinstance(buddy_id, list):
            req_sent_to = buddy_id
        else:
            req_sent_to = buddy_id
            
        payload = {
            "mode": 2,
            "req_sent_by": user_id,
            "req_sent_to": req_sent_to
        }
        try:
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=20
            )
            
            print(f"\n=== MAKE BUDDY API DEBUG ===")
            print(f"URL: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            print("=============================\n")
            
            if response.status_code == 201:
                return {
                    "success": True,
                    "message": "Buddy request sent successfully",
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": f"Make buddy failed ({response.status_code})",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Make buddy error: {str(e)}"
            }

    @staticmethod
    def get_buddies(user_id):
        """
        Get all buddies for a user.
        
        Args:
            user_id: Current logged-in user ID (euh_id for folder structure)
        
        Returns:
            Dictionary with success status and buddies data or error message
        """
        url = f"{WorksheetAPI.BASE_URL}/3dtrial/buddy/get-buddies/{user_id}"
        try:
            response = requests.get(
                url,
                headers={'Content-Type': 'application/json'},
                timeout=20
            )
            
            print(f"\n=== GET BUDDIES API DEBUG ===")
            print(f"URL: {url}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            print("==============================\n")
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Buddies fetched successfully",
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": f"Get buddies failed ({response.status_code})",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Get buddies error: {str(e)}"
            }

    # @staticmethod
    # def create_worksheet(payload):
    #     """
    #     Create worksheet (mode 1 / mode 2) via server endpoint.
    #     Payload should include the required fields, e.g.:
    #       {"mode":1, "user_id":1, "worksheet_name":"...", "file_id":123}
    #     or mode 2 payload.

    #     Returns a dict: {"success": bool, "status_code": int, "data": dict, "text": str}
    #     """
    #     url = f"{WorksheetAPI.BASE_URL}/3dtrial/create-worksheet"
    #     try:
    #         resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=20)
    #         text = resp.text
    #         try:
    #             data = resp.json()
    #         except Exception:
    #             data = {}

    #         ok = resp.status_code in (200, 201)
    #         return {"success": ok, "status_code": resp.status_code, "data": data, "text": text}
    #     except Exception as e:
    #         return {"success": False, "message": str(e)}

    @staticmethod
    def update_worksheet_layer(user_id, mode, layer_id, worksheet_id, layer_json_data):
        """
        Sends a PUT request to update a worksheet layer on the server.

        Args:
            user_id: integer or string user id to identify the requester
            mode: operation mode (int) - use 1 by default from caller
            layer_id: integer id of the design layer on server (can be None)
            worksheet_id: integer id of the worksheet on server
            layer_json_data: dict containing the full design_construction_config.json contents

        Returns: dict with keys: success, status_code, data, text
        """
        # Ensure we call the correct endpoint for updating a worksheet layer
        url = f"{WorksheetAPI.BASE_URL}/3dtrial/create-worksheet"  # Assuming same endpoint with mode=3 for update, adjust if different

        # Normalize worksheet_id: reject dicts (common error response) and extract scalar id when possible
        def _normalize_wsid(c):
            if c is None:
                return None
            if isinstance(c, dict):
                for k in ('worksheet_id', 'worksheetId', 'id'):
                    v = c.get(k)
                    if v is not None and not isinstance(v, dict):
                        return int(v) if (isinstance(v, (int, str)) and str(v).isdigit()) else v
                return None
            if isinstance(c, (int, str)):
                s = str(c).strip()
                return int(s) if s.isdigit() else s
            return None

        safe_wsid = _normalize_wsid(worksheet_id)
        payload = {
            "user_id": user_id,
            "mode": mode,
            "layer_id": layer_id,
            "worksheet_id": safe_wsid,
            "layer_json_data": layer_json_data
        }
        # Debug: print payload and URL for troubleshooting
        try:
            print("\n=== UPDATE WORKSHEET LAYER PAYLOAD (DEBUG) ===")
            print(f"URL: {url}")
            print(json.dumps(payload, indent=4))
            print("=============================================" + "\n")
        except Exception:
            pass

        # If caller requested mode=2, provide an explicit, easy-to-find dump
        if mode == 2:
            try:
                print("\n=== MODE=2 PAYLOAD (DEBUG) ===")
                print(json.dumps(payload, indent=4))
                print("===============================\n")
            except Exception:
                pass
            # # Attempt to save payload to workspace for offline inspection
            # try:
            #     with open('last_update_worksheet_layer_mode2_payload.json', 'w', encoding='utf-8') as pf:
            #         json.dump(payload, pf, indent=2, ensure_ascii=False)
            #     print("Saved MODE=2 payload to last_update_worksheet_layer_mode2_payload.json")
            # except Exception as e:
            #     print(f"Could not save MODE=2 payload file: {e}")
        try:
            # Debug helper: if worksheet_id was dropped, log a warning to help debug caller plumbing
            if worksheet_id is not None and safe_wsid is None:
                print("WARNING: Provided worksheet_id was a non-scalar or contained error data; sending null instead.")

            resp = requests.put(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
            text = resp.text
            print(f"DEBUG: Response Status: {resp.status_code}")
            print(f"DEBUG: Response Text: {text}")
            try:
                data = resp.json()
            except Exception:
                data = {}

            ok = resp.status_code in (200, 201)
            return {"success": ok, "status_code": resp.status_code, "data": data, "text": text}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_worksheet_layer_data(user_id, mode, worksheet_id=None):
        """
        Fetches worksheet layer data from the server.
        mode 1: Get worksheets
        mode 2: Get design layers for a worksheet
        mode 3: Get material layers for a worksheet
        """
        url = f"{WorksheetAPI.BASE_URL}/3dtrial/get-worksheet-layer-data"
        params = {
            "mode": mode,
            "user_id": user_id
        }
        if worksheet_id is not None:
            params["worksheet_id"] = worksheet_id

        try:
            response = requests.get(
                url,
                params=params,
                headers={'Content-Type': 'application/json'},
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                # Debug logging
                # print(f"\n=== GET WORKSHEET LAYER DATA (Mode {mode}) ===")
                # print(f"URL: {response.url}")
                # print(f"Data: {json.dumps(data, indent=2)}")
                return {
                    "success": True,
                    "data": data
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed ({response.status_code})",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    @staticmethod
    def share_file_to_buddy(payload):
        """
        Share a worksheet/file with buddies.
        Payload should include:
        {
          "shared_by": 100007,
          "shared_to": [100002, 100003, 100005],
          "worksheet_id": 108185,
          "design_layer_id": 109001,
          "material_layer_id": 109002,
          "file_id": 1
        }
        """
        url = f"{WorksheetAPI.BASE_URL}/3dtrial/buddy/share-file"
        try:
            import json
            print("\n=== SHARE FILE PAYLOAD (DEBUG) ===")
            print(json.dumps(payload, indent=4))
            print("==================================\n")
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=20
            )
            print(f"DEBUG: Share File Status Code: {response.status_code}")
            print(f"DEBUG: Share File Response: {response.text}")
            if response.status_code in (200, 201):
                return {
                    "success": True,
                    "data": response.json() if response.text else {}
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to share file ({response.status_code})",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error sharing file: {str(e)}"
            }

