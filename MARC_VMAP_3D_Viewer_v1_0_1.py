# -*- coding: utf-8 -*-
"""
VMAP 3D VIEWER v1.0.37 - Vibracoustic EU FEA Department
NEW: GUI with LabelFrame steps, progress title, watermark, Guideline button
NEW: Full 360-degree rotation and translation
NEW: GIF export with start/end increment range
NEW: Global coordinate system axes in browser
NEW: Color legend with intermediate values on left side
NEW: View Cut Manager (X/Y/Z cutting planes)
NEW: Legend Levels control, Screenshot with XY Plot option
NEW: Reset Axes button, improved Reset Zoom, Load Excel fix
NEW: Excel column header auto-import for XY Plot labels
NEW: Save Configuration - persist all user settings across sessions
NEW: Value Range Filter - dual-slider to show range, out-of-range as feature edges
NEW: Background Color picker for 3D viewport
NEW: XY Sheet rename button, Undeformed mesh with Contour On
NEW: Zoom Box tool for 3D viewport, Table Form for multi-value inspection
NEW: Save and Load section, Mode label for XY Plot toggle
FIX: Real element/node IDs from VMAP file now shown in viewer (was showing array indices)
FIX: Value lookup accepts real IDs
NEW: Legend Extrapolation dialog with Mentat-style method and nodal averaging options
NEW: Extrapolation visualization standards loaded from CMO_031_C_3D_VIEWER.docx
CHANGE: Extrapolation Information refined for CC and PL standards; Mentat explanatory note removed from dialog
CHANGE: Extrapolation button renamed to Visualization Options and highlighted in Legend
CHANGE: Visualization Options list refreshed from updated CMO_031_C_3D_VIEWER.docx and button restyled in standard blue
CHANGE: Table Form Links can now be enabled without requiring Values to be active
CHANGE: Forecast-created dialog boxes no longer show the title "Forecast Result"
CHANGE: Measure supports multiple draggable Distance/Angle info windows with sequential node letters
CHANGE: File Information now shows the current user name
CHANGE: Sidebar control sections can now be reordered as blue cards by dragging their headers
CHANGE: Animation card is now draggable with the same grab header used by the other sidebar cards
CHANGE: File Information is now a fixed blue card with bold labels and stays pinned at the top of the sidebar
CHANGE: Visualization Standards now include CC1/CC2_B TETRA and HEXA variants with the requested extrapolation mappings
CHANGE: Legend Levels selector reduced to match the Dec selector width and stay on the same line as its label
Author: Leandro Barbosa
"""

from __future__ import print_function
import sys
import os
import importlib
import webbrowser
import json
import hashlib
import time

# =============================================================================
# NETWORK DEPENDENCIES
# =============================================================================

NUMPY_LIBS = r"\\frafil002\VC-Marc_Post\VMAP\Marc_numpy"
H5PY_LIBS = r"\\frafil002\VC-Marc_Post\VMAP\Marc_h5py"
NUMPY_LIBS_ALT = r"X:\VC-Marc_Post\VMAP\Marc_numpy"
H5PY_LIBS_ALT = r"X:\VC-Marc_Post\VMAP\Marc_h5py"

GUIDELINE_PATH = r"\\frafil002\VC_FEA\VC-Marc_Post\Marc_Tools_Guideline\Marc_VMAP_3D_Viewer_User_Guide_v1.html"
LOGO_SVG_PATH = r"\\frafil002\VC_FEA\VC-Marc_Post\Marc_Python\Canvas\Vibracoustic.svg"
VIBRA_SVG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VIBRA.svg")
JSON_SCRIPT_CHUNK_SIZE = 200000
CACHE_SCHEMA_VERSION = "vmap_3d_viewer_cache_2026_04_03_restore_functional_base1"
EXTRAPOLATION_STANDARD_PRESETS = [
    {"name": "VISU1", "info": "Stress of Mises averaged to the nodes", "method": "linear", "avg": "on"},
    {"name": "VISU2", "info": "Stress of Mises averaged to the element faces", "method": "translate", "avg": "off"},
    {"name": "VISU3", "info": "Maximal Principal Stress averaged to the nodes", "method": "linear", "avg": "on"},
    {"name": "VISU4", "info": "Equivalent Plastic Strains averaged to the element faces", "method": "translate", "avg": "off"},
    {"name": "VISU5", "info": "Equivalent Plastic Strains averaged to the nodes", "method": "linear", "avg": "on"},
    {"name": "VISU6a", "info": "Maximal Principal Stress averaged to the nodes", "method": "linear", "avg": "on"},
    {"name": "VISU6b", "info": "Minimal Principal Stress averaged to the nodes at the opposite load to VISU6a", "method": "linear", "avg": "on"},
    {"name": "VISU7", "info": "Nominal Strains averaged to the nodes", "method": "average", "avg": "on"},
    {"name": "VISU8", "info": "Minimal Principal Strains averaged to the nodes", "method": None, "avg": None},
    {"name": "VISU9", "info": "Maximal Principal Stress averaged to the element faces", "method": "translate", "avg": "off"},
    {"name": "VISU10", "info": "Minimal Principal Stress averaged to the nodes", "method": "linear", "avg": "on"},
    {"name": "VISU11", "info": "Nominal Strains averaged to the element faces", "method": "average", "avg": "on"},
    {"name": "VISU12a", "info": "Maximal Principal Stress averaged to the element faces", "method": "translate", "avg": "off"},
    {"name": "VISU12b", "info": "Minimal Principal Stress averaged to the element faces at the opposite load to VISU12a", "method": "translate", "avg": "off"},
    {"name": "VISU13", "info": "Magnitude of displacement to the nodes", "method": None, "avg": None},
    {"name": "VISU15a", "info": "Stress of Mises averaged to the nodes", "method": "linear", "avg": "on"},
    {"name": "VISU15b", "info": "Stress of Mises averaged to the nodes at the opposite load to VISU15a", "method": "linear", "avg": "on"},
    {"name": "VISU_CC1_TETRA", "info": "Nominal Strains evraged to the element faces. Used for the output: eps1_en.", "method": "average", "avg": "on"},
    {"name": "VISU_CC1_HEXA", "info": "Nominal Strains evraged to the element faces. Used for the output: eps1_en.", "method": "average", "avg": "off"},
    {"name": "VISU_CC2_B_TETRA", "info": "Vibracoustic Damage B4 Dimensionless and Normalized Value averaged on elements centroid. Used for Damage Analysis (Rubber).", "method": "average", "avg": "on"},
    {"name": "VISU_CC2_B_HEXA", "info": "Vibracoustic Damage B4 Dimensionless and Normalized Value averaged on elements centroid. Used for Damage Analysis (Rubber).", "method": "average", "avg": "off"},
    {"name": "VISU_PL6", "info": "Stress of Mises averaged to the nodes. Used for Plastic parts.", "method": "linear", "avg": "on"},
    {"name": "VISU_PL7", "info": "Maximal Principal Stress averaged to the nodes. Used for Plastic parts.", "method": "linear", "avg": "on"},
]

def make_chunked_json_script(base_id, json_text, chunk_size=JSON_SCRIPT_CHUNK_SIZE):
    if not isinstance(json_text, str):
        json_text = str(json_text)
    # Keep HTML parser stable by avoiding extremely long single lines.
    chunks = [json_text[i:i + chunk_size] for i in range(0, len(json_text), chunk_size)]
    if not chunks:
        chunks = [""]
    tags = []
    for ci, chunk in enumerate(chunks):
        chunk = chunk.replace("</script", "<\\/script")
        tags.append('<script id="{0}-c{1}" type="application/json">{2}</script>'.format(base_id, ci, chunk))
    return {'base': base_id, 'chunks': len(chunks)}, tags


def build_export_cache_path(base_path):
    return base_path + "_3D_View.cache.npz"


def load_export_cache(cache_path):
    try:
        if not os.path.exists(cache_path):
            return None
        with np.load(cache_path, allow_pickle=False) as npz_data:
            if "bundle_json" not in npz_data:
                return None
            raw = npz_data["bundle_json"]
            if isinstance(raw, np.ndarray):
                payload = raw.tobytes()
            else:
                payload = bytes(raw)
        data = json.loads(payload.decode("utf-8"))
        if not isinstance(data, dict):
            return None
        return data
    except Exception:
        return None


def save_export_cache(cache_path, data):
    try:
        payload = json.dumps(data, separators=(',', ':')).encode("utf-8")
        arr = np.frombuffer(payload, dtype=np.uint8)
        np.savez_compressed(cache_path, bundle_json=arr)
        return True
    except Exception:
        return False


def pack_float32_b64(values):
    if values is None:
        return None
    try:
        import base64 as _b64
        arr = np.nan_to_num(np.asarray(values, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        return _b64.b64encode(arr.tobytes()).decode('ascii')
    except Exception:
        return None


def pack_norm_i16_b64(norm_values):
    if norm_values is None:
        return None
    try:
        import base64 as _b64
        arr = np.nan_to_num(np.asarray(norm_values, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        q = np.clip(np.round(arr * 32767.0), 0, 32767).astype(np.int16)
        return _b64.b64encode(q.tobytes()).decode('ascii')
    except Exception:
        return None


def pack_int32_b64(values):
    if values is None:
        return None
    try:
        import base64 as _b64
        arr = np.asarray(values, dtype=np.int32)
        return _b64.b64encode(arr.tobytes()).decode('ascii')
    except Exception:
        return None

def force_import_numpy():
    candidates = [NUMPY_LIBS, NUMPY_LIBS_ALT]
    numpy_root = None
    for p in candidates:
        if os.path.isdir(p) and os.path.isdir(os.path.join(p, "numpy")):
            numpy_root = p
            break
    if not numpy_root:
        raise ImportError("NumPy not found")
    bin_dir = os.path.join(numpy_root, "bin")
    if os.path.isdir(bin_dir):
        os.environ["PATH"] = bin_dir + ";" + os.environ.get("PATH", "")
    if numpy_root in sys.path:
        sys.path.remove(numpy_root)
    sys.path.insert(0, numpy_root)
    for k in list(sys.modules.keys()):
        if k == "numpy" or k.startswith("numpy."):
            del sys.modules[k]
    importlib.invalidate_caches()
    import numpy as np
    return np

def force_import_h5py():
    candidates = [H5PY_LIBS, H5PY_LIBS_ALT]
    h5py_root = None
    for p in candidates:
        if os.path.isdir(p) and os.path.isdir(os.path.join(p, "h5py")):
            h5py_root = p
            break
    if not h5py_root:
        raise ImportError("h5py not found")
    h5py_subfolder = os.path.join(h5py_root, "h5py")
    if os.path.isdir(h5py_subfolder):
        os.environ["PATH"] = h5py_subfolder + ";" + os.environ.get("PATH", "")
    if h5py_root in sys.path:
        sys.path.remove(h5py_root)
    sys.path.insert(1, h5py_root)
    for k in list(sys.modules.keys()):
        if k == "h5py" or k.startswith("h5py.") or k == "six":
            del sys.modules[k]
    importlib.invalidate_caches()
    import h5py
    return h5py

try:
    np = force_import_numpy()
except:
    try:
        import numpy as np
    except:
        np = None

try:
    h5py = force_import_h5py()
except:
    try:
        import h5py
    except:
        h5py = None

import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# =============================================================================
# ULTRA-SAFE CONVERSION FUNCTIONS
# =============================================================================

def is_valid_number(val):
    if val is None:
        return False
    type_name = type(val).__name__
    if 'NoValue' in type_name or 'Empty' in type_name or 'NoneType' in type_name:
        return False
    return True

def safe_number(val, default=0.0, as_int=False):
    if not is_valid_number(val):
        return int(default) if as_int else default
    try:
        if hasattr(val, 'item'):
            result = val.item()
            return int(result) if as_int else float(result)
        if isinstance(val, bytes):
            result = float(val.decode('utf-8'))
            return int(result) if as_int else result
        if as_int:
            return int(val)
        return float(val)
    except:
        return int(default) if as_int else default

def safe_string(val, default=""):
    if val is None:
        return default
    type_name = type(val).__name__
    if 'NoValue' in type_name or 'Empty' in type_name:
        return default
    try:
        if isinstance(val, bytes):
            return val.decode('utf-8', errors='replace')
        return str(val)
    except:
        return default

def read_attr(obj, name, default=None):
    try:
        if name in obj.attrs:
            val = obj.attrs[name]
            if is_valid_number(val) or isinstance(val, (bytes, str)):
                return val
            if hasattr(val, '__len__'):
                return val
        return default
    except:
        return default

import re as _re

def natural_sort_key(s):
    """Sort strings with embedded numbers in natural order.
    'STATE_2' comes before 'STATE_10'."""
    return [int(c) if c.isdigit() else c.lower() for c in _re.split(r'(\d+)', str(s))]


def _norm_token(text):
    try:
        return _re.sub(r'[^A-Za-z0-9]+', '', safe_string(text, "")).upper()
    except Exception:
        return ""

MATERIAL_META_MARKER = "|| MAT="
MATERIAL_META_SEP = ";"
DAT_MATERIAL_MODEL_CARDS = set([
    "isotropic",
    "orthotropic",
    "anisotropic",
    "mooney",
    "ogden",
    "neo",
    "neohook",
    "hyperelastic",
    "viscelmoon",
    "viscoelastic",
    "plastic",
])
DAT_MATERIAL_SKIP_TOKENS = set([
    "VON",
    "MISES",
    "ISOTROPIC",
    "ORTHOTROPIC",
    "ANISOTROPIC",
    "MOONEY",
    "OGDEN",
    "NEO",
    "NEOHOOK",
    "HYPERELASTIC",
    "VISCELMOON",
    "VISCOELASTIC",
    "PLASTIC",
    "TABLE",
    "LOADCASE",
])
DAT_MATERIAL_NAME_RE = _re.compile(r'([A-Za-z][A-Za-z0-9_\-./]{1,120})\s*$')
DAT_MATERIAL_ID_RE = _re.compile(r'(-?\d+)')


def _material_norm_key(name):
    return _re.sub(r'[^A-Za-z0-9]+', '', safe_string(name, "").upper())


def parse_request_and_materials_from_description(desc_text):
    txt = safe_string(desc_text, "").strip()
    if not txt:
        return "", []
    idx = txt.find(MATERIAL_META_MARKER)
    if idx < 0:
        return txt, []
    req = txt[:idx].strip()
    mat_raw = txt[idx + len(MATERIAL_META_MARKER):].strip()
    mats = []
    seen = set()
    for token in mat_raw.split(MATERIAL_META_SEP):
        t = safe_string(token, "").strip()
        if not t:
            continue
        nkey = _material_norm_key(t)
        if not nkey or nkey in seen:
            continue
        seen.add(nkey)
        mats.append(t)
    return req, mats


def find_related_dat_file(source_path):
    if not source_path:
        return None
    base, _ = os.path.splitext(source_path)
    base_candidates = [base]
    if _re.search(r'(?i)_fat$', base):
        base_candidates.append(base[:-4])
    ext_candidates = [".dat", ".DAT", ".Dat"]
    seen = set()
    for b in base_candidates:
        if not b:
            continue
        nb = os.path.normcase(os.path.normpath(b))
        if nb in seen:
            continue
        seen.add(nb)
        for ext in ext_candidates:
            cp = b + ext
            if os.path.exists(cp):
                return cp
    return None


def extract_material_names_from_dat(dat_path, lookahead=10):
    if not dat_path or (not os.path.exists(dat_path)):
        return []
    try:
        with open(dat_path, "r", encoding="latin1", errors="ignore") as df:
            lines = df.read().splitlines()
    except Exception:
        return []

    out = []
    seen = set()
    n_lines = len(lines)
    for i in range(n_lines):
        card = lines[i].strip().lower()
        if card not in DAT_MATERIAL_MODEL_CARDS:
            continue
        end_j = min(n_lines, i + 1 + max(1, int(lookahead)))
        for j in range(i + 1, end_j):
            row = lines[j].strip()
            if not row or row.startswith("$"):
                continue
            row_low = row.lower()
            if row_low in DAT_MATERIAL_MODEL_CARDS and j > i + 1:
                break
            if row_low.startswith("table") or row_low.startswith("loadcase"):
                break
            m = DAT_MATERIAL_NAME_RE.search(row)
            if not m:
                continue
            token = m.group(1).strip()
            prefix = row[:m.start(1)]
            if not _re.search(r'\d', prefix):
                continue
            if token.upper() in DAT_MATERIAL_SKIP_TOKENS:
                continue
            nkey = _material_norm_key(token)
            if not nkey or nkey in seen:
                break
            seen.add(nkey)
            out.append(token)
            break
    return out


def extract_material_entries_from_dat(dat_path, lookahead=10):
    if not dat_path or (not os.path.exists(dat_path)):
        return []
    try:
        with open(dat_path, "r", encoding="latin1", errors="ignore") as df:
            lines = df.read().splitlines()
    except Exception:
        return []

    out = []
    seen = set()
    n_lines = len(lines)
    for i in range(n_lines):
        card = lines[i].strip().lower()
        if card not in DAT_MATERIAL_MODEL_CARDS:
            continue
        end_j = min(n_lines, i + 1 + max(1, int(lookahead)))
        for j in range(i + 1, end_j):
            row = lines[j].strip()
            if not row or row.startswith("$"):
                continue
            row_low = row.lower()
            if row_low in DAT_MATERIAL_MODEL_CARDS and j > i + 1:
                break
            if row_low.startswith("table") or row_low.startswith("loadcase"):
                break
            m = DAT_MATERIAL_NAME_RE.search(row)
            if not m:
                continue
            token = m.group(1).strip()
            prefix = row[:m.start(1)]
            if not _re.search(r'\d', prefix):
                continue
            if token.upper() in DAT_MATERIAL_SKIP_TOKENS:
                continue
            nkey = _material_norm_key(token)
            if not nkey or nkey in seen:
                break
            seen.add(nkey)
            id_match = DAT_MATERIAL_ID_RE.search(prefix or "")
            mat_id = safe_number(id_match.group(1), None, as_int=True) if id_match else None
            out.append({"id": mat_id, "name": token})
            break
    return out


def resolve_material_names_from_sidecar(source_path):
    dat_path = find_related_dat_file(source_path)
    if not dat_path:
        return [], None
    return extract_material_names_from_dat(dat_path), dat_path


def resolve_material_entries_from_sidecar(source_path):
    dat_path = find_related_dat_file(source_path)
    if not dat_path:
        return [], None
    return extract_material_entries_from_dat(dat_path), dat_path


def _material_entries_to_names(entries):
    out = []
    seen = set()
    for entry in (entries or []):
        name = safe_string((entry or {}).get("name"), "").strip()
        nkey = _material_norm_key(name)
        if not nkey or nkey in seen:
            continue
        seen.add(nkey)
        out.append(name)
    return out


def _coerce_material_token_parts(value):
    if value is None:
        return None, None
    try:
        if isinstance(value, bytes):
            value = safe_string(value, "").strip()
    except Exception:
        pass
    if isinstance(value, str):
        txt = safe_string(value, "").strip()
        if not txt:
            return None, None
        num = safe_number(txt, None, as_int=True)
        if num is not None and str(num) == txt:
            return num, None
        return None, txt
    num = safe_number(value, None, as_int=True)
    if num is not None:
        return num, None
    txt = safe_string(value, "").strip()
    if txt:
        return None, txt
    return None, None


def _resolve_material_name_from_token(token, material_entries=None, material_names=None):
    mat_num, mat_text = _coerce_material_token_parts(token)
    names = [safe_string(n, "").strip() for n in (material_names or []) if safe_string(n, "").strip()]
    entries = material_entries or []
    if mat_text:
        tkey = _material_norm_key(mat_text)
        for entry in entries:
            name = safe_string(entry.get("name"), "").strip()
            if _material_norm_key(name) == tkey:
                return name
        for name in names:
            if _material_norm_key(name) == tkey:
                return name
        return mat_text
    if mat_num is not None:
        for entry in entries:
            eid = safe_number(entry.get("id"), None, as_int=True)
            if eid is not None and eid == mat_num:
                name = safe_string(entry.get("name"), "").strip()
                if name:
                    return name
        if 1 <= mat_num <= len(names):
            return names[mat_num - 1]
        return "Material {}".format(mat_num)
    return ""


def _extract_vmap_material_token_from_elem(elem_rec):
    if elem_rec is None:
        return None
    try:
        dtype_names = list(getattr(getattr(elem_rec, "dtype", None), "names", None) or [])
    except Exception:
        dtype_names = []
    priority = []
    fallback = []
    for field in dtype_names:
        low = safe_string(field, "").lower()
        if "material" in low or low.startswith("mymat") or low == "mat":
            priority.append(field)
        elif "property" in low and ("identifier" in low or low.endswith("id")):
            fallback.append(field)
    for field in priority + fallback:
        try:
            raw = elem_rec[field]
        except Exception:
            continue
        num, txt = _coerce_material_token_parts(raw)
        if txt or num is not None:
            return txt if txt else num
    return None


def _extract_vmap_part_material_token(part_group):
    if part_group is None:
        return None
    try:
        attr_keys = list(part_group.attrs.keys())
    except Exception:
        attr_keys = []
    for key in attr_keys:
        low = safe_string(key, "").lower()
        if "material" not in low:
            continue
        try:
            raw = part_group.attrs[key]
        except Exception:
            continue
        num, txt = _coerce_material_token_parts(raw)
        if txt or num is not None:
            return txt if txt else num
    return None


# =============================================================================
# VMAP READER - WITH NODE ID TO INDEX MAPPING AND REQUEST NUMBER
# =============================================================================

class VMAPReader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None
        self.version = ""
        self.request_number = ""
        self.nodes = None
        self.node_ids = None
        self.node_id_to_index = {}
        self.elements = []
        self.states = {}
        self.n_nodes = 0
        self.n_elements = 0
        self.debug_info = []
        self.material_names = []
        self.material_entries = []
        self.material_dat_path = None
        # Caches to avoid repeated heavy computations during HTML generation
        self._scalar_cache = {}
        self._nodal_cache = {}
        self._element_cache = {}
        
    def open(self):
        if not os.path.exists(self.filepath):
            raise IOError("File not found: " + self.filepath)
        self.file = h5py.File(self.filepath, 'r')
        self._read_all()
        return self
    
    def close(self):
        if self.file:
            self.file.close()
    
    def __enter__(self):
        return self.open()
    
    def __exit__(self, *args):
        self.close()

    def _read_state_text(self, sg, candidate_names):
        cand = set(_norm_token(cn) for cn in candidate_names if cn)
        if not cand:
            return ""
        # 1) Attributes
        try:
            for ak in sg.attrs.keys():
                if _norm_token(ak) not in cand:
                    continue
                txt = safe_string(sg.attrs[ak], "").strip()
                if txt:
                    return txt
        except Exception:
            pass
        # 2) Scalar datasets
        try:
            for dk in sg.keys():
                if _norm_token(dk) not in cand:
                    continue
                try:
                    dv = sg[dk][()]
                except Exception:
                    continue
                try:
                    arr = np.asarray(dv).flatten()
                    if arr.size > 0:
                        dv = arr[0]
                except Exception:
                    pass
                txt = safe_string(dv, "").strip()
                if txt:
                    return txt
        except Exception:
            pass
        return ""

    def _read_state_scalar(self, sg, candidate_names):
        cand = set(_norm_token(cn) for cn in candidate_names if cn)
        if not cand:
            return None
        # 1) Group attributes
        try:
            for ak in sg.attrs.keys():
                if _norm_token(ak) not in cand:
                    continue
                v = sg.attrs[ak]
                try:
                    if hasattr(v, '__len__') and not isinstance(v, (bytes, str)):
                        arr = np.asarray(v).flatten()
                        if arr.size > 0:
                            v = arr[0]
                except Exception:
                    pass
                num = safe_number(v, default=None)
                if num is not None and np.isfinite(num):
                    return float(num)
        except Exception:
            pass
        # 2) Scalar datasets directly inside state group
        try:
            for dk in sg.keys():
                if _norm_token(dk) not in cand:
                    continue
                try:
                    dv = sg[dk][()]
                except Exception:
                    continue
                try:
                    arr = np.asarray(dv).flatten()
                    if arr.size == 0:
                        continue
                    dv = arr[0]
                except Exception:
                    pass
                num = safe_number(dv, default=None)
                if num is not None and np.isfinite(num):
                    return float(num)
        except Exception:
            pass
        return None

    def _read_frequency_from_state_name(self, state_name):
        txt = safe_string(state_name, "")
        if not txt:
            return None
        m = _re.search(r'([-+]?\d+(?:[.,]\d+)?)\s*hz\b', txt, flags=_re.IGNORECASE)
        if m:
            try:
                return float(m.group(1).replace(',', '.'))
            except Exception:
                pass
        m = _re.search(r'(?:freq(?:uency)?)\D*([-+]?\d+(?:[.,]\d+)?)', txt, flags=_re.IGNORECASE)
        if m:
            try:
                return float(m.group(1).replace(',', '.'))
            except Exception:
                pass
        return None

    def _read_state_frequency_hz(self, sg, state_name, state_title=""):
        hz_keys = [
            'MYFREQUENCY', 'FREQUENCY', 'MYFREQ', 'FREQ',
            'MYEXCITATIONFREQUENCY', 'EXCITATIONFREQUENCY',
            'MYLOADFREQUENCY', 'LOADFREQUENCY'
        ]
        hz = self._read_state_scalar(sg, hz_keys)
        if hz is not None and np.isfinite(hz):
            return float(hz)

        ang_keys = [
            'MYANGULARFREQUENCY', 'ANGULARFREQUENCY',
            'MYCIRCULARFREQUENCY', 'CIRCULARFREQUENCY',
            'MYOMEGA', 'OMEGA', 'PULSATION'
        ]
        omega = self._read_state_scalar(sg, ang_keys)
        if omega is not None and np.isfinite(omega):
            try:
                return float(omega) / (2.0 * 3.141592653589793)
            except Exception:
                pass

        from_title = self._read_frequency_from_state_name(state_title)
        if from_title is not None and np.isfinite(from_title):
            return float(from_title)

        from_name = self._read_frequency_from_state_name(state_name)
        if from_name is not None and np.isfinite(from_name):
            return float(from_name)
        return None
    
    def _read_all(self):
        f = self.file
        
        # Version
        try:
            if '/VMAP' in f:
                v = read_attr(f['/VMAP'], 'VERSION')
                if v is not None and hasattr(v, '__len__') and len(v) >= 3:
                    v0 = safe_number(v[0], 0, as_int=True)
                    v1 = safe_number(v[1], 0, as_int=True)
                    v2 = safe_number(v[2], 0, as_int=True)
                    self.version = "{}.{}.{}".format(v0, v1, v2)
        except:
            pass
        
        # Read metadata
        try:
            if '/VMAP/META/INFORMATION' in f:
                meta_info = f['/VMAP/META/INFORMATION']
                desc = read_attr(meta_info, 'DESCRIPTION')
                if desc:
                    req, mats = parse_request_and_materials_from_description(desc)
                    self.request_number = req
                    if mats:
                        self.material_names = mats
                        self.material_entries = [{"id": i + 1, "name": name} for i, name in enumerate(mats)]
        except:
            pass
        if not self.material_names:
            try:
                side_entries, side_dat = resolve_material_entries_from_sidecar(self.filepath)
                self.material_entries = side_entries
                self.material_names = _material_entries_to_names(side_entries)
                self.material_dat_path = side_dat
            except Exception:
                pass
        
        # Geometry
        try:
            geom_path = '/VMAP/SIMULATION/GEOMETRY'
            if geom_path in f:
                for part_id in f[geom_path].keys():
                    part = f[geom_path][part_id]
                    part_material_token = _extract_vmap_part_material_token(part)
                    
                    if 'POINTS' in part:
                        pts = part['POINTS']
                        sz = read_attr(pts, 'MYSIZE')
                        self.n_nodes = safe_number(sz, 0, as_int=True)
                        
                        if 'MYCOORDINATES' in pts:
                            self.nodes = pts['MYCOORDINATES'][()]
                        
                        if 'MYIDENTIFIERS' in pts:
                            raw_ids = pts['MYIDENTIFIERS'][()]
                            self.node_ids = raw_ids.flatten()
                            
                            for idx, nid in enumerate(self.node_ids):
                                try:
                                    node_id = int(nid)
                                    self.node_id_to_index[node_id] = idx
                                except:
                                    pass
                            
                            if len(self.node_ids) > 0:
                                first_id = int(self.node_ids[0])
                                last_id = int(self.node_ids[-1])
                                self.debug_info.append("Node IDs: first={}, last={}, count={}".format(
                                    first_id, last_id, len(self.node_ids)))
                    
                    if 'ELEMENTS' in part:
                        elems = part['ELEMENTS']
                        sz = read_attr(elems, 'MYSIZE')
                        self.n_elements = safe_number(sz, 0, as_int=True)
                        
                        if 'MYELEMENTS' in elems:
                            data = elems['MYELEMENTS'][()]
                            
                            for e in data:
                                try:
                                    elem = e[0] if hasattr(e, '__len__') and len(e.shape) > 0 else e
                                    connectivity_ids = [int(n) for n in elem['myConnectivity']]
                                    material_token = _extract_vmap_material_token_from_elem(elem)
                                    material_name = _resolve_material_name_from_token(
                                        material_token if material_token is not None else part_material_token,
                                        self.material_entries,
                                        self.material_names
                                    )
                                    self.elements.append({
                                        'id': int(elem['myIdentifier']),
                                        'type': int(elem['myElementType']),
                                        'connectivity_ids': connectivity_ids,
                                        'material_name': material_name
                                    })
                                except:
                                    pass
                    break
        except Exception as ex:
            self.debug_info.append("Geometry error: {}".format(str(ex)))
        
        # States
        try:
            var_path = '/VMAP/SIMULATION/VARIABLES'
            if var_path in f:
                for state_name in sorted(f[var_path].keys(), key=natural_sort_key):
                    try:
                        sg = f[var_path][state_name]
                        
                        time_attr = read_attr(sg, 'MYTOTALTIME')
                        time_val = safe_number(time_attr, 0.0)
                        
                        inc_attr = read_attr(sg, 'MYSTATEINCREMENT')
                        inc_val = safe_number(inc_attr, 0, as_int=True)
                        state_title = self._read_state_text(
                            sg,
                            ['MYSTATENAME', 'STATENAME', 'MYTITLE', 'TITLE', 'MYDESCRIPTION', 'DESCRIPTION']
                        )
                        if not state_title:
                            state_title = safe_string(state_name, "")
                        freq_val = self._read_state_frequency_hz(sg, state_name, state_title)
                        
                        state_data = {
                            'time': time_val,
                            'increment': inc_val,
                            'frequency': freq_val,
                            'title': state_title,
                            'variables': {}
                        }
                        
                        for gid in sg.keys():
                            if gid.isdigit():
                                vg = sg[gid]
                                for vn in vg.keys():
                                    try:
                                        v = vg[vn]
                                        if isinstance(v, h5py.Group) and 'MYVALUES' in v:
                                            vals = v['MYVALUES'][()]
                                            state_data['variables'][vn] = vals
                                    except:
                                        pass
                        
                        self.states[state_name] = state_data
                    except:
                        pass
        except Exception as ex:
            self.debug_info.append("States error: {}".format(str(ex)))
    
    def get_connectivity_as_indices(self, elem):
        cached = elem.get('_conn_idx')
        if cached is not None:
            return cached
        indices = []
        has_node_id_map = len(self.node_id_to_index) > 0
        for nid in elem['connectivity_ids']:
            if nid in self.node_id_to_index:
                idx = self.node_id_to_index[nid]
            else:
                if not has_node_id_map:
                    # Fallback only when VMAP does not provide explicit node IDs.
                    if nid > 0 and (nid - 1) < self.n_nodes:
                        idx = nid - 1
                    elif 0 <= nid < self.n_nodes:
                        idx = nid
                    else:
                        idx = -1
                else:
                    # Keep invalid IDs explicit so face builders can skip bad elements.
                    idx = -1
            indices.append(idx)
        elem['_conn_idx'] = indices
        return indices
    
    def get_nodes(self, state_name=None, scale=1.0, var_name='Displacement'):
        if self.nodes is None:
            return None
        if state_name and state_name in self.states:
            disp = self.states[state_name]['variables'].get(var_name)
            if disp is not None:
                try:
                    return self.nodes + disp * scale
                except:
                    pass
        return self.nodes.copy()
    
    def element_to_node_values(self, elem_values):
        """Convert element-based values to node-based by averaging at shared nodes"""
        if elem_values is None or self.nodes is None:
            return None
        n_nodes = len(self.nodes)
        node_sums = np.zeros(n_nodes, dtype=np.float64)
        node_counts = np.zeros(n_nodes, dtype=np.float64)
        
        for ei, elem in enumerate(self.elements):
            if ei >= len(elem_values):
                break
            val = float(elem_values[ei])
            if not np.isfinite(val):
                val = 0.0
            indices = self.get_connectivity_as_indices(elem)
            for ni in indices:
                if 0 <= ni < n_nodes:
                    node_sums[ni] += val
                    node_counts[ni] += 1.0
        
        # Avoid division by zero
        mask = node_counts > 0
        result = np.zeros(n_nodes, dtype=np.float64)
        result[mask] = node_sums[mask] / node_counts[mask]
        return result

    def _get_scalar_values(self, state_name, var_name):
        key = (state_name, var_name)
        if key in self._scalar_cache:
            return self._scalar_cache[key]
        if state_name not in self.states:
            self._scalar_cache[key] = None
            return None
        vals = self.states[state_name]['variables'].get(var_name)
        if vals is None:
            self._scalar_cache[key] = None
            return None
        try:
            result = self._compute_scalar(vals)
            if result is not None:
                result = np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
            self._scalar_cache[key] = result
            return result
        except:
            self._scalar_cache[key] = None
            return None
    
    def get_values(self, state_name, var_name):
        key = (state_name, var_name)
        if key in self._nodal_cache:
            return self._nodal_cache[key]
        result = self._get_scalar_values(state_name, var_name)
        if result is None:
            self._nodal_cache[key] = None
            return None
        try:
            # Check if element-based (length matches n_elements, not n_nodes)
            n_nodes = len(self.nodes) if self.nodes is not None else 0
            if len(result) != n_nodes and len(result) == self.n_elements and self.n_elements > 0:
                result = self.element_to_node_values(result)
            self._nodal_cache[key] = result
            return result
        except:
            self._nodal_cache[key] = None
            return None
    
    def get_element_values(self, state_name, var_name):
        """Returns per-element centroid values (no nodal averaging)"""
        key = (state_name, var_name)
        if key in self._element_cache:
            return self._element_cache[key]
        result = self._get_scalar_values(state_name, var_name)
        if result is None:
            self._element_cache[key] = None
            return None
        try:
            n_nodes = len(self.nodes) if self.nodes is not None else 0
            if len(result) == self.n_elements:
                out = np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
                self._element_cache[key] = out
                return out
            elif len(result) == n_nodes and self.n_elements > 0:
                # Average node values per element to get centroid values
                elem_vals = np.zeros(self.n_elements, dtype=np.float64)
                for ei, elem in enumerate(self.elements):
                    if ei >= self.n_elements:
                        break
                    indices = self.get_connectivity_as_indices(elem)
                    valid = [float(result[ni]) for ni in indices if 0 <= ni < n_nodes and np.isfinite(result[ni])]
                    if valid:
                        elem_vals[ei] = np.mean(valid)
                self._element_cache[key] = elem_vals
                return elem_vals
            self._element_cache[key] = None
            return None
        except:
            self._element_cache[key] = None
            return None
    
    def _compute_scalar(self, vals):
        """Compute scalar representation from raw variable data"""
        try:
            result = None
            if len(vals.shape) == 1:
                result = vals.flatten()
            elif len(vals.shape) > 1:
                ncols = vals.shape[1]
                if ncols == 1:
                    result = vals.flatten()
                elif ncols == 3:
                    result = np.sqrt(np.nansum(vals**2, axis=1))
                elif ncols == 6:
                    s = vals
                    result = np.sqrt(0.5 * ((s[:,0]-s[:,1])**2 + (s[:,1]-s[:,2])**2 + (s[:,2]-s[:,0])**2 
                                        + 6.0*(s[:,3]**2 + s[:,4]**2 + s[:,5]**2)))
                elif ncols == 9:
                    s = vals
                    result = np.sqrt(0.5 * ((s[:,0]-s[:,4])**2 + (s[:,4]-s[:,8])**2 + (s[:,8]-s[:,0])**2 
                                        + 6.0*(s[:,1]**2 + s[:,5]**2 + s[:,2]**2)))
                else:
                    result = np.sqrt(np.nansum(vals**2, axis=1))
            else:
                result = vals.flatten()
            # Clean NaN/Inf values
            if result is not None:
                result = np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
            return result
        except:
            return None
    
    def get_available_variables(self):
        """Detect all variable types: scalars, vectors, and tensors"""
        var_info = {}  # {name: type_str}
        for st in self.states.values():
            for var_name, var_data in st.get('variables', {}).items():
                if var_name in var_info:
                    continue
                try:
                    if not hasattr(var_data, 'shape'):
                        continue
                    if len(var_data.shape) == 1:
                        var_info[var_name] = 'Scalar'
                    elif len(var_data.shape) > 1:
                        ncols = var_data.shape[1]
                        if ncols == 1:
                            var_info[var_name] = 'Scalar'
                        elif ncols == 3:
                            var_info[var_name] = 'Vector'
                        elif ncols == 6:
                            var_info[var_name] = 'Tensor (sym)'
                        elif ncols == 9:
                            var_info[var_name] = 'Tensor'
                        else:
                            var_info[var_name] = 'Field ({})'.format(ncols)
                except:
                    pass
        return var_info
    
    def get_available_vector_variables(self):
        """Legacy: return all variable names (backward compatibility)"""
        return sorted(list(self.get_available_variables().keys()))
    
    def get_variable_locations(self):
        """Detect if each variable is natively element-based or node-based.
        Returns dict: {var_name: 'element' or 'node'}"""
        locations = {}
        n_nodes = len(self.nodes) if self.nodes is not None else 0
        for st in self.states.values():
            for var_name, var_data in st.get('variables', {}).items():
                if var_name in locations:
                    continue
                try:
                    if not hasattr(var_data, 'shape'):
                        continue
                    n_rows = var_data.shape[0]
                    if n_rows == self.n_elements and n_rows != n_nodes:
                        locations[var_name] = 'element'
                    else:
                        locations[var_name] = 'node'
                except:
                    pass
        return locations


# =============================================================================
# HTML GENERATOR
# =============================================================================

def generate_html(reader, progress_callback=None, selected_output=None, viewer_mode="static", export_centroid=True, export_all_edges=False):
    
    def update_progress(percent, message=""):
        if progress_callback:
            progress_callback(percent, message)
    
    mode = (viewer_mode or "static").strip().lower()
    harmonic_mode = (mode == "harmonic")
    export_all_edges = bool(export_all_edges)
    if harmonic_mode:
        export_centroid = False

    update_progress(5, "Preparing data...")
    
    base = os.path.splitext(reader.filepath)[0]
    output_file = base + "_3D_View.html"
    material_names = getattr(reader, "material_names", []) or []
    if material_names:
        material_lines = []
        for mat in material_names:
            material_lines.append(
                safe_string(mat, "n/a")
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
        materials_info_html = "<br>".join(material_lines)
    else:
        materials_info_html = "n/a"
    viewer_user_name = (
        safe_string(os.environ.get("USERNAME") or os.environ.get("USER") or "n/a", "n/a")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    
    original_nodes = reader.nodes
    if original_nodes is None:
        raise ValueError("No nodes found in VMAP file")
    
    update_progress(10, "Processing nodes...")
    # Clean NaN/Inf from node coordinates before JSON serialization
    original_nodes = np.nan_to_num(original_nodes, nan=0.0, posinf=0.0, neginf=0.0)
    original_nodes_json = json.dumps(original_nodes.tolist(), separators=(',', ':'))
    
    update_progress(15, "Getting outputs...")
    all_var_info = reader.get_available_variables()
    all_available_outputs = sorted(all_var_info.keys())
    
    virtual_displacement_output = False
    if harmonic_mode:
        if 'Displacement' not in all_available_outputs:
            raise ValueError("Harmonic mode requires 'Displacement' output in VMAP file.")
        export_outputs = ['Displacement']
        viewer_outputs = ['Displacement']
        default_var = 'Displacement'
    elif selected_output and selected_output in all_available_outputs:
        # Export selected output only. Deformation nodes are exported separately by state.
        export_outputs = [selected_output]
        viewer_outputs = [selected_output]
        default_var = selected_output
        if selected_output != 'Displacement' and 'Displacement' in all_available_outputs:
            viewer_outputs.append('Displacement')
            virtual_displacement_output = True
    else:
        export_outputs = all_available_outputs
        viewer_outputs = list(all_available_outputs)
        default_var = 'Displacement' if 'Displacement' in viewer_outputs else (viewer_outputs[0] if viewer_outputs else None)
    
    # Detect native data locations (element vs node) for each variable
    var_locations = reader.get_variable_locations()
    if 'Displacement' in viewer_outputs and 'Displacement' not in var_locations:
        var_locations['Displacement'] = 'node'
    if not harmonic_mode:
        needs_element_contour = any(var_locations.get(v, 'node') == 'element' for v in viewer_outputs)
        if needs_element_contour and not export_centroid:
            export_centroid = True
            update_progress(16, "Element outputs detected: enabling element data export for extrapolation support...")
    state_names = sorted(reader.states.keys(), key=natural_sort_key)
    src_size = 0
    src_mtime = 0.0
    try:
        src_size = int(os.path.getsize(reader.filepath))
        src_mtime = float(os.path.getmtime(reader.filepath))
    except Exception:
        pass
    cache_key = {
        "schema": CACHE_SCHEMA_VERSION,
        "source_path": os.path.normcase(os.path.abspath(reader.filepath)),
        "source_size": src_size,
        "source_mtime": src_mtime,
        "viewer_mode": mode,
        "export_centroid": bool(export_centroid),
        "outputs": list(export_outputs),
        "states": list(state_names),
    }
    cache_path = build_export_cache_path(base)
    cached_bundle = None
    cached_data = load_export_cache(cache_path)
    if cached_data and cached_data.get("key") == cache_key and isinstance(cached_data.get("bundle"), dict):
        cached_bundle = cached_data.get("bundle")

    if cached_bundle:
        update_progress(20, "Using cached processed data...")
        state_meta = cached_bundle.get("state_meta", {})
        state_var_keys = cached_bundle.get("state_var_keys", {})
        disp_nodes_by_state = cached_bundle.get("disp_nodes_by_state", {})
        disp_max_by_state = cached_bundle.get("disp_max_by_state", {})
        all_outputs_data = cached_bundle.get("all_outputs_data", {})
    else:
        state_meta = {}
        state_var_keys = {}
        disp_nodes_by_state = {}
        disp_max_by_state = {}

        update_progress(20, "Pre-processing states...")
        for sn in state_names:
            st = reader.states.get(sn, {})
            time_val = st.get('time', 0)
            if not is_valid_number(time_val):
                time_val = 0.0
            else:
                time_val = safe_number(time_val, 0.0)
            inc_val = st.get('increment', 0)
            if not is_valid_number(inc_val):
                inc_val = 0
            else:
                inc_val = safe_number(inc_val, 0, as_int=True)
            freq_val = st.get('frequency', None)
            if not is_valid_number(freq_val):
                freq_val = None
            else:
                freq_val = safe_number(freq_val, None)
            title_val = safe_string(st.get('title', sn), "")
            # In harmonic exports from MARC_VMAP_GUI, MYTOTALTIME may carry the frequency value.
            if harmonic_mode and ((freq_val is None) or (is_valid_number(freq_val) and abs(safe_number(freq_val, 0.0)) <= 1e-12)) and is_valid_number(time_val):
                tf = safe_number(time_val, None)
                if tf is not None and np.isfinite(tf) and abs(tf) > 1e-12:
                    freq_val = float(tf)
            state_meta[sn] = {'time': time_val, 'increment': inc_val, 'frequency': freq_val, 'title': title_val}
            var_keys = list(st.get('variables', {}).keys())
            state_var_keys[sn] = var_keys

            # Export relative displacement vectors per state. This avoids precision loss
            # when reconstructing displacement magnitudes from large absolute coordinates.
            state_nodes = reader.get_nodes(sn, 1.0, 'Displacement')
            if state_nodes is not None:
                state_nodes = np.nan_to_num(state_nodes, nan=0.0, posinf=0.0, neginf=0.0)
                try:
                    disp_vec = np.nan_to_num(state_nodes - original_nodes, nan=0.0, posinf=0.0, neginf=0.0)
                    disp_mag = np.linalg.norm(disp_vec, axis=1)
                    disp_max = float(np.nanmax(disp_mag)) if disp_mag.size else 0.0
                    if not np.isfinite(disp_max):
                        disp_max = 0.0
                except Exception:
                    disp_vec = None
                    disp_max = 0.0
                disp_max_by_state[sn] = disp_max
                b64_disp = pack_float32_b64(disp_vec) if disp_vec is not None else None
                if b64_disp:
                    disp_nodes_by_state[sn] = {
                        "disp_f32_b64": b64_disp,
                        "n_nodes": int(disp_vec.shape[0])
                    }
                else:
                    disp_nodes_by_state[sn] = None
            else:
                disp_max_by_state[sn] = 0.0
                disp_nodes_by_state[sn] = None

        update_progress(25, "Processing {} output(s)...".format(len(export_outputs)))

        # Build separate dataset for EACH output variable
        # CRITICAL: Node positions ALWAYS use 'Displacement' variable
        all_outputs_data = {}
        for idx, var_name in enumerate(export_outputs):
            percent = 25 + (35 * idx / max(1, len(export_outputs)))
            update_progress(percent, "Processing: {} ...".format(var_name))

            output_states = {}
            for sn in state_names:
                try:
                    if var_name not in state_var_keys.get(sn, []):
                        continue

                    state_colors = reader.get_values(sn, var_name)

                    colors_i16_b64 = None
                    color_count = 0
                    color_min = 0.0
                    color_max = 1.0
                    if state_colors is not None:
                        try:
                            sc = np.nan_to_num(state_colors, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
                            vmin = float(np.nanmin(sc))
                            vmax = float(np.nanmax(sc))
                            if not (np.isfinite(vmin) and np.isfinite(vmax)):
                                vmin, vmax = 0.0, 1.0
                            if abs(vmax - vmin) < 1e-10:
                                vmax = vmin + 1.0
                            colors_normalized = np.clip((sc - vmin) / (vmax - vmin), 0, 1).astype(np.float32)
                            colors_i16_b64 = pack_norm_i16_b64(colors_normalized)
                            color_count = int(colors_normalized.size)
                            color_min = vmin
                            color_max = vmax
                        except Exception:
                            colors_i16_b64 = None
                            color_count = 0
                            color_min = 0.0
                            color_max = 1.0

                    centroid_i16_b64 = None
                    centroid_count = 0
                    centroid_min = 0.0
                    centroid_max = 1.0
                    if export_centroid:
                        centroid_colors = reader.get_element_values(sn, var_name)
                        if centroid_colors is not None:
                            try:
                                cc = np.nan_to_num(centroid_colors, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
                                cvmin = float(np.nanmin(cc))
                                cvmax = float(np.nanmax(cc))
                                if not (np.isfinite(cvmin) and np.isfinite(cvmax)):
                                    cvmin, cvmax = 0.0, 1.0
                                if abs(cvmax - cvmin) < 1e-10:
                                    cvmax = cvmin + 1.0
                                centroid_normalized = np.clip((cc - cvmin) / (cvmax - cvmin), 0, 1).astype(np.float32)
                                centroid_i16_b64 = pack_norm_i16_b64(centroid_normalized)
                                centroid_count = int(centroid_normalized.size)
                                centroid_min = cvmin
                                centroid_max = cvmax
                            except Exception:
                                centroid_i16_b64 = None
                                centroid_count = 0
                                centroid_min = 0.0
                                centroid_max = 1.0

                    meta = state_meta.get(sn, {'time': 0.0, 'increment': 0, 'frequency': None, 'title': ''})
                    item = {
                        'time': meta['time'],
                        'increment': meta['increment'],
                        'frequency': meta.get('frequency'),
                        'title': meta.get('title', ''),
                        'colors_i16_b64': colors_i16_b64,
                        'color_count': color_count,
                        'color_min': color_min,
                        'color_max': color_max
                    }
                    if export_centroid:
                        item['centroid_i16_b64'] = centroid_i16_b64
                        item['centroid_count'] = centroid_count
                        item['centroid_min'] = centroid_min
                        item['centroid_max'] = centroid_max
                    output_states[sn] = item
                except Exception as _e:
                    import traceback
                    print("[WARNING] State '{}' skipped for '{}': {}".format(sn, var_name, _e))
                    traceback.print_exc()
            all_outputs_data[var_name] = output_states

        update_progress(58, "Saving intermediate cache...")
        save_export_cache(cache_path, {
            "key": cache_key,
            "bundle": {
                "state_meta": state_meta,
                "state_var_keys": state_var_keys,
                "disp_nodes_by_state": disp_nodes_by_state,
                "disp_max_by_state": disp_max_by_state,
                "all_outputs_data": all_outputs_data
            }
        })

    # Store output data as inert JSON script blocks (per variable/state).
    # This avoids parsing a giant JS object at startup and loads state data on demand.
    output_state_index = {}
    output_state_tag_map = {}
    output_state_scripts = []
    for var_name in export_outputs:
        states_for_var = all_outputs_data.get(var_name, {})
        sid_list = []
        tag_map = {}
        for sn in state_names:
            if sn not in states_for_var:
                continue
            sid_list.append(sn)
            tag_id = "vmap-out-" + hashlib.md5((var_name + "||" + sn).encode("utf-8")).hexdigest()[:16]
            sjson = json.dumps(states_for_var[sn], separators=(',', ':'))
            info, tags = make_chunked_json_script(tag_id, sjson)
            tag_map[sn] = info
            output_state_scripts.extend(tags)
        output_state_index[var_name] = sid_list
        output_state_tag_map[var_name] = tag_map

    state_nodes_tag_map = {}
    state_nodes_scripts = []
    for sn in state_names:
        sn_nodes = disp_nodes_by_state.get(sn)
        if sn_nodes is None:
            continue
        tag_id = "vmap-nodes-" + hashlib.md5(("nodes||" + sn).encode("utf-8")).hexdigest()[:16]
        njson = json.dumps(sn_nodes, separators=(',', ':'))
        info, tags = make_chunked_json_script(tag_id, njson)
        state_nodes_tag_map[sn] = info
        state_nodes_scripts.extend(tags)

    output_state_index_json = json.dumps(output_state_index, separators=(',', ':'))
    output_state_tag_map_json = json.dumps(output_state_tag_map, separators=(',', ':'))
    state_nodes_tag_map_json = json.dumps(state_nodes_tag_map, separators=(',', ':'))
    state_nodes_scripts_html = "\n".join(state_nodes_scripts)
    output_state_scripts_html = "\n".join(output_state_scripts)

    states_list = [{
        'id': sn,
        'time': state_meta.get(sn, {}).get('time', 0.0),
        'increment': state_meta.get(sn, {}).get('increment', 0),
        'frequency': state_meta.get(sn, {}).get('frequency', None),
        'title': state_meta.get(sn, {}).get('title', ''),
        'variables': state_var_keys.get(sn, [])
    } for sn in state_names]
    states_json = json.dumps(states_list, separators=(',', ':'))
    
    state_name = state_names[-1] if state_names else None
    
    color_range = [0.0, 1.0]
    colors_json = "null"
    if state_name and default_var:
        try:
            sd0 = all_outputs_data.get(default_var, {}).get(state_name, {})
            vmin = sd0.get('color_min')
            vmax = sd0.get('color_max')
            if is_valid_number(vmin) and is_valid_number(vmax):
                color_range = [safe_number(vmin, 0.0), safe_number(vmax, 1.0)]
            c_b64 = sd0.get('colors_i16_b64')
            c_count = safe_number(sd0.get('color_count', 0), 0, as_int=True)
            if c_b64 and c_count > 0:
                colors_json = json.dumps({'i16_b64': c_b64, 'count': c_count}, separators=(',', ':'))
        except Exception:
            pass

    def _calc_harmonic_initial_scale(max_disp):
        try:
            md = abs(float(max_disp))
        except:
            md = 0.0
        if (not np.isfinite(md)) or md <= 0.0:
            return 1.0
        # Example: 1.5E-04 -> ceil(-log10(.)) = 4 -> 0.8 * (10^4 * 10) = 80000
        order = int(np.ceil(-np.log10(md)))
        if order < 0:
            order = 0
        return float(0.8 * (10 ** order) * 10.0)

    harmonic_initial_scale = 1.0
    if harmonic_mode and state_name:
        harmonic_initial_scale = _calc_harmonic_initial_scale(disp_max_by_state.get(state_name, 0.0))
    if not np.isfinite(harmonic_initial_scale) or harmonic_initial_scale <= 0:
        harmonic_initial_scale = 1.0
    harmonic_initial_scale_text = "{:g}".format(harmonic_initial_scale)
    
    update_progress(60, "Building mesh faces...")
    faces = []
    face_element_map = []
    skipped_invalid_conn = 0
    for ei, elem in enumerate(reader.elements):
        try:
            conn = reader.get_connectivity_as_indices(elem)
            n = len(conn)
            valid = all(0 <= idx < reader.n_nodes for idx in conn)
            if not valid:
                skipped_invalid_conn += 1
                continue
            nf = 0
            if n == 4:
                faces.extend([
                    [conn[0], conn[1], conn[2]],
                    [conn[0], conn[1], conn[3]],
                    [conn[0], conn[2], conn[3]],
                    [conn[1], conn[2], conn[3]]
                ])
                nf = 4
            elif n >= 8:
                faces.extend([
                    [conn[0], conn[1], conn[2]], [conn[0], conn[2], conn[3]],
                    [conn[4], conn[6], conn[5]], [conn[4], conn[7], conn[6]],
                    [conn[0], conn[5], conn[1]], [conn[0], conn[4], conn[5]],
                    [conn[2], conn[7], conn[3]], [conn[2], conn[6], conn[7]],
                    [conn[0], conn[7], conn[4]], [conn[0], conn[3], conn[7]],
                    [conn[1], conn[6], conn[2]], [conn[1], conn[5], conn[6]]
                ])
                nf = 12
            elif n == 6:
                faces.extend([
                    [conn[0], conn[1], conn[2]],
                    [conn[3], conn[5], conn[4]],
                    [conn[0], conn[3], conn[4]], [conn[0], conn[4], conn[1]],
                    [conn[1], conn[4], conn[5]], [conn[1], conn[5], conn[2]],
                    [conn[2], conn[5], conn[3]], [conn[2], conn[3], conn[0]]
                ])
                nf = 8
            elif n == 3:
                faces.append([conn[0], conn[1], conn[2]])
                nf = 1
            face_element_map.extend([ei] * nf)
        except:
            pass
    if skipped_invalid_conn > 0:
        print("[WARNING] Skipped {} element(s) with invalid connectivity IDs".format(skipped_invalid_conn))
    
    faces_json = json.dumps(faces, separators=(',', ':'))
    face_element_map_json = json.dumps(face_element_map, separators=(',', ':'))
    
    # BUILD REAL ID ARRAYS for JavaScript
    node_ids_list = []
    if reader.node_ids is not None:
        node_ids_list = [int(x) for x in reader.node_ids.tolist()]
    else:
        node_ids_list = list(range(1, (reader.n_nodes or 0) + 1))
    node_ids_json = json.dumps(node_ids_list, separators=(',', ':'))
    
    elem_ids_list = [int(e.get("id", i + 1)) for i, e in enumerate(reader.elements)]
    elem_ids_json = json.dumps(elem_ids_list, separators=(',', ':'))
    elem_conn_offsets = [0]
    elem_conn_flat = []
    for elem in reader.elements:
        try:
            conn = reader.get_connectivity_as_indices(elem) or []
        except Exception:
            conn = []
        n = len(conn)
        if n == 4:
            export_conn = conn[:4]
        elif n == 6:
            export_conn = conn[:6]
        elif n >= 8:
            export_conn = conn[:8]
        else:
            export_conn = []
        elem_conn_flat.extend(int(idx) for idx in export_conn)
        elem_conn_offsets.append(len(elem_conn_flat))
    elem_conn_offsets_json = json.dumps(
        {'i32_b64': pack_int32_b64(elem_conn_offsets), 'count': len(elem_conn_offsets)},
        separators=(',', ':')
    )
    elem_conn_data_json = json.dumps(
        {'i32_b64': pack_int32_b64(elem_conn_flat), 'count': len(elem_conn_flat)},
        separators=(',', ':')
    )

    material_display_names = []
    material_name_to_idx = {}
    for raw_name in (getattr(reader, "material_names", []) or []):
        name = safe_string(raw_name, "").strip()
        nkey = _material_norm_key(name)
        if not nkey or nkey in material_name_to_idx:
            continue
        material_name_to_idx[nkey] = len(material_display_names)
        material_display_names.append(name)
    elem_material_map = []
    has_unknown_material = False
    for elem in reader.elements:
        material_name = safe_string(elem.get("material_name"), "").strip()
        if not material_name and len(material_display_names) == 1:
            elem_material_map.append(0)
            continue
        nkey = _material_norm_key(material_name)
        if nkey:
            if nkey not in material_name_to_idx:
                material_name_to_idx[nkey] = len(material_display_names)
                material_display_names.append(material_name)
            elem_material_map.append(material_name_to_idx[nkey])
        else:
            elem_material_map.append(-1)
            has_unknown_material = True
    if has_unknown_material:
        unknown_idx = material_name_to_idx.get("__UNKNOWN__")
        if unknown_idx is None:
            unknown_idx = len(material_display_names)
            material_name_to_idx["__UNKNOWN__"] = unknown_idx
            material_display_names.append("Unassigned / Unknown")
        elem_material_map = [unknown_idx if idx < 0 else idx for idx in elem_material_map]
    material_names_json = json.dumps(material_display_names, separators=(',', ':'))
    elem_material_map_json = json.dumps(elem_material_map, separators=(',', ':'))
    
    # Extract boundary (external) faces - faces that appear only once
    update_progress(65, "Extracting boundary faces...")
    face_count = {}
    for f in faces:
        key = tuple(sorted(f))
        face_count[key] = face_count.get(key, 0) + 1
    boundary_faces = []
    boundary_face_elem_map = []
    for fi, f in enumerate(faces):
        if face_count[tuple(sorted(f))] == 1:
            boundary_faces.append(list(f))
            boundary_face_elem_map.append(face_element_map[fi])
    boundary_faces_json = json.dumps(boundary_faces, separators=(',', ':'))
    boundary_face_elem_map_json = json.dumps(boundary_face_elem_map, separators=(',', ':'))

    static_data_tag_map = {}
    static_data_scripts = []
    static_payloads = [
        ('ON', original_nodes_json),
        ('F', faces_json),
        ('BF', boundary_faces_json),
        ('BFE', boundary_face_elem_map_json),
        ('FEM', face_element_map_json),
        ('NIDS', node_ids_json),
        ('EIDS', elem_ids_json),
        ('ECOFF', elem_conn_offsets_json),
        ('ECON', elem_conn_data_json),
        ('MATN', material_names_json),
        ('EMM', elem_material_map_json),
        ('C', colors_json),
        ('SL', states_json)
    ]
    for key, payload in static_payloads:
        tag_id = "vmap-core-" + key.lower()
        info, tags = make_chunked_json_script(tag_id, payload)
        static_data_tag_map[key] = info
        static_data_scripts.extend(tags)
    static_data_tag_map_json = json.dumps(static_data_tag_map, separators=(',', ':'))
    static_data_scripts_html = "\n".join(static_data_scripts)
    
    try:
        center = [float(x) for x in np.nanmean(original_nodes, axis=0).tolist()]
        bbox_size = float(np.nanmax(original_nodes) - np.nanmin(original_nodes))
        if not np.isfinite(bbox_size) or bbox_size < 1e-10:
            bbox_size = 1.0
    except:
        center = [0.0, 0.0, 0.0]
        bbox_size = 1.0
    
    try:
        cr_min = "{:.2e}".format(color_range[0])
        cr_max = "{:.2e}".format(color_range[1])
    except:
        cr_min = "0.00e+00"
        cr_max = "1.00e+00"
    
    request_display = reader.request_number if reader.request_number else "Not specified"
    n_states = len(states_list)
    detected_increment_ids = []
    for st in states_list:
        inc_val = st.get('increment', None)
        if is_valid_number(inc_val):
            detected_increment_ids.append(safe_number(inc_val, 0, as_int=True))
        elif inc_val is not None:
            detected_increment_ids.append(safe_string(inc_val, ""))
    unique_increment_count = len(set(detected_increment_ids)) if detected_increment_ids else n_states
    show_animation_section = bool(n_states > 0 and (harmonic_mode or unique_increment_count > 1))
    animation_range_max = max(0, n_states - 1)
    viewer_mode_label = "harmonic" if harmonic_mode else "static"

    if harmonic_mode:
        scale_controls_html = (
            '<div class="p sidebar-card" data-panel-id="displacement-scale"><div class="pt sidebar-card-handle"><span>Displacement Scale</span><span class="sidebar-card-grip">&#9776;</span></div>'
            '<div class="cg">'
            '<div class="cl">Scale Factor:</div>'
            '<input type="text" id="scf" value="' + harmonic_initial_scale_text + '" '
            'style="width:100%;margin-top:4px;padding:4px 6px;border:1px solid #bbb;border-radius:4px;font-size:10px">'
            '</div>'
            '<button class="bt bt2" onclick="asc()">Apply</button>'
            '<button class="bt bt2" onclick="rsc()">Reset</button>'
            '</div>'
        )
    else:
        scale_controls_html = (
            '<div class="p sidebar-card" data-panel-id="displacement-scale"><div class="pt sidebar-card-handle"><span>Displacement Scale</span><span class="sidebar-card-grip">&#9776;</span></div>'
            '<div class="cg">'
            '<div class="cl">Scale Factor: <span class="sv" id="scv">1.0</span></div>'
            '<input type="range" id="scr" min="0" max="10" step="0.1" value="1" oninput="usc(this.value)">'
            '</div>'
            '<button class="bt bt2" onclick="asc()">Apply</button>'
            '<button class="bt bt2" onclick="rsc()">Reset</button>'
            '</div>'
        )

    animation_panel_html = ""
    if show_animation_section:
        animation_panel_html = (
            '<div class="p sidebar-card" data-panel-id="animation"><div class="pt sidebar-card-handle"><span>Animation</span><span class="sidebar-card-grip">&#9776;</span></div>'
            '<div class="anim">'
            '<div class="cl">Speed: '
            '<input type="range" id="anim-speed" value="5" min="1" max="10" step="1" style="width:120px" oninput="document.getElementById(\'speed-val\').textContent=this.value">'
            '<span id="speed-val" style="margin-left:5px;font-weight:bold">5</span>x'
            '</div>'
            '<div class="cl">GIF Scale: '
            '<input type="range" id="gif-scale" value="1" min="1" max="4" step="1" style="width:120px" oninput="document.getElementById(\'gif-scale-val\').textContent=this.value">'
            '<span id="gif-scale-val" style="margin-left:5px;font-weight:bold">1</span>x'
            '</div>'
            '<div class="range-row"><span>Start Inc:</span><input type="range" id="gif-start" min="0" max="' + str(animation_range_max) + '" value="0" step="1" oninput="ugrl()"><span class="rv" id="gif-start-val">0</span></div>'
            '<div class="range-row"><span>End Inc:</span><input type="range" id="gif-end" min="0" max="' + str(animation_range_max) + '" value="' + str(animation_range_max) + '" step="1" oninput="ugrl()"><span class="rv" id="gif-end-val">' + str(animation_range_max) + '</span></div>'
            '<div class="cl"><span id="anim-mode-label">' + ('Harmonic:' if harmonic_mode else 'Swing:') + '</span>'
            '<button class="bt" id="anim-harmonic-btn" onclick="tgAnimHarmonic()" style="font-size:9px;padding:1px 9px;margin-left:6px;min-width:46px;background:' + ('#00C853' if harmonic_mode else '#D32F2F') + ';color:#fff">' + ('On' if harmonic_mode else 'Off') + '</button>'
            '<span id="anim-mode-hint" style="margin-left:6px;font-size:9px;color:#666">' + ('Full cycle (-180 to 180 deg)' if harmonic_mode else 'Min Inc <-> Max Inc') + '</span>'
            '</div>'
            '<div class="anim-row">'
            '<button class="bt bt3" onclick="playAnimation()" style="flex:1">&#9654; Play</button>'
            '<button class="bt bt2" onclick="stopAnimation()" style="flex:1">&#9208; Stop</button>'
            '</div>'
            '<div class="anim-row">'
            '<button class="bt" id="anim-prev-btn" onclick="animPrevIncrement()" style="flex:1" title="Go to previous increment">&#9664; Prev</button>'
            '<button class="bt bt-yellow" id="anim-pause-btn" onclick="pauseAnimation()" style="flex:1" title="Pause or resume animation">&#10074;&#10074; Pause</button>'
            '<button class="bt" id="anim-next-btn" onclick="animNextIncrement()" style="flex:1" title="Go to next increment">Next &#9654;</button>'
            '</div>'
            '<button class="bt bt-orange" onclick="exportGIF()" style="width:100%;margin-top:8px">&#128248; Export GIF</button>'
            '<div class="cl" id="anim-status" style="margin-top:8px;color:#FF6D00"></div>'
            '</div>'
            '</div>'
        )

    if export_all_edges:
        all_edges_option_html = '<option value="all">All Edges</option>'
    else:
        all_edges_option_html = '<option value="all" disabled>All Edges (disabled in export)</option>'
    
    # Load VIBRA.svg for HTML embedding (fallback to network logo)
    logo_data_uri = ""
    try:
        import base64 as _b64
        logo_path = VIBRA_SVG_PATH if os.path.isfile(VIBRA_SVG_PATH) else LOGO_SVG_PATH
        if os.path.isfile(logo_path):
            with open(logo_path, 'rb') as lf:
                svg_bytes = lf.read()
            logo_data_uri = "data:image/svg+xml;base64," + _b64.b64encode(svg_bytes).decode('ascii')
    except:
        pass
    
    # =========================================================================
    # HTML TEMPLATE
    # =========================================================================
    html = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>VMAP 3D Viewer - Vibracoustic</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Arial,sans-serif;background:#efefef;color:#333;overflow:hidden}
#c{width:100vw;height:100vh;position:relative}
#cv{position:absolute;left:320px;top:0}
#sb{position:absolute;top:0;left:0;width:320px;height:100%;background:#efefef;border-right:2px solid #ccc;overflow-y:auto;overflow-x:hidden;box-shadow:2px 0 10px rgba(0,0,0,0.1)}
.p{padding:14px 16px;border-bottom:1px solid #ddd}
.pt{font-size:12px;font-weight:bold;color:#2196F3;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px}
#sidebar-panel-zone{padding:4px 0 18px 0}
.sidebar-card{position:relative;margin:10px 12px;padding:0 14px 14px;background:linear-gradient(180deg,rgba(255,255,255,0.99) 0%,rgba(247,250,255,0.98) 100%);border:2px solid rgba(33,150,243,0.78);border-radius:10px;border-bottom:none;box-shadow:0 3px 10px rgba(33,150,243,0.10),0 2px 6px rgba(0,0,0,0.06);overflow:hidden}
.sidebar-card .pt{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 -14px 12px -14px;padding:10px 14px;background:linear-gradient(180deg,rgba(33,150,243,0.16) 0%,rgba(255,255,255,0.92) 100%);border-bottom:1px solid rgba(33,150,243,0.26)}
.sidebar-card-handle{cursor:grab;user-select:none}
.sidebar-card-handle:active{cursor:grabbing}
.sidebar-card-grip{flex:0 0 auto;font-size:14px;line-height:1;color:#1976D2;opacity:0.78;letter-spacing:1px}
.sidebar-card.dragging{opacity:0.58;box-shadow:0 10px 24px rgba(33,150,243,0.24),0 4px 14px rgba(0,0,0,0.14)}
.sidebar-card-placeholder{margin:10px 12px;border:2px dashed #2196F3;border-radius:10px;background:rgba(33,150,243,0.08);box-shadow:inset 0 0 0 1px rgba(255,255,255,0.35)}
.sidebar-zone-static{margin:10px 12px;background:rgba(255,255,255,0.9);border:1px solid rgba(33,150,243,0.24);border-radius:10px;border-bottom:none;box-shadow:0 2px 8px rgba(0,0,0,0.04);overflow:hidden}
.sidebar-zone-static .pt{margin-bottom:10px}
.file-info-card .il{font-weight:700;color:#444}
.ir{display:flex;justify-content:space-between;padding:4px 0;font-size:11px}
.il{color:#666}.iv{color:#333;font-weight:600}
.ir-file-name{align-items:flex-start;gap:8px}
.ir-file-name .il{flex:0 0 auto;padding-top:1px}
.ir-file-name .iv{flex:1 1 auto;min-width:0;text-align:right;white-space:normal;overflow-wrap:anywhere;word-break:break-word;line-height:1.25}
.lg{text-align:center;padding:15px 16px;background:#ffffff;border-bottom:3px solid #2196F3}
.lg img{max-width:200px;height:auto;margin-bottom:6px}
.lg h1{font-size:22px;color:#2196F3;font-weight:bold;margin-bottom:4px}
.lg h2{font-size:14px;color:#555;font-weight:bold;margin-bottom:4px}
.lg span{font-size:10px;color:#888}
#cb{width:100%;height:18px;background:linear-gradient(to right,#0000ff,#00ffff,#00ff00,#ffff00,#ff0000);border-radius:4px;margin:10px 0;border:1px solid #ccc}
.cbl{display:flex;justify-content:space-between;font-size:10px;color:#666}
#st{position:absolute;bottom:0;left:320px;right:0;padding:8px 16px;background:#e0e0e0;font-size:11px;color:#555;border-top:1px solid #ccc}
.bt{padding:6px 12px;margin:3px;background:#2196F3;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:11px;font-weight:500;transition:background 0.2s}
.bt:hover{background:#1976D2}
.bt2{background:#666}.bt2:hover{background:#555}
.bt3{background:#00C853}.bt3:hover{background:#00A844}
.bt-orange{background:#FF6D00}.bt-orange:hover{background:#E65100}
.bt-yellow{background:#FFD54F;color:#333}.bt-yellow:hover{background:#FBC02D}
.ck{display:flex;align-items:center;margin:6px 0;font-size:11px;color:#444}
.disp-opt-sec{font-size:11px;font-weight:bold;color:#555;margin:18px 0 8px 0;border-bottom:1px solid #e0e0e0;padding-bottom:2px}
.disp-opt-sec-first{margin-top:6px}
.ck input{margin-right:8px;accent-color:#2196F3}
select{width:100%;padding:8px;background:#fff;border:1px solid #ccc;color:#333;border-radius:4px;font-size:11px;margin:6px 0}
select:focus{outline:none;border-color:#2196F3}
.si{background:#fff;padding:10px;border-radius:4px;margin-top:10px;font-size:10px;border:1px solid #ddd}
.cg{margin:10px 0}
.cl{font-size:11px;color:#666;margin-bottom:4px}
input[type="range"]{width:100%;accent-color:#2196F3}
.sv{background:#fff;padding:3px 8px;border-radius:3px;font-size:11px;border:1px solid #ccc;color:#333}
.anim{background:#fff;padding:10px;border-radius:4px;margin-top:10px;border:1px solid #ddd}
.anim-row{display:flex;gap:5px;margin-top:8px}
#help-overlay{position:absolute;top:15px;right:15px;background:rgba(255,255,255,0.92);padding:12px 16px;border-radius:6px;font-size:11px;color:#444;box-shadow:0 2px 10px rgba(0,0,0,0.15);border:1px solid #ddd;line-height:1.6;z-index:50}
#help-overlay b{color:#2196F3;font-size:12px}
#watermark{position:absolute;bottom:15px;right:15px;font-size:11px;color:rgba(100,100,100,0.5);font-style:italic;z-index:50;user-select:none}
#val-tooltip{position:absolute;display:none;padding:4px 8px;background:rgba(0,0,0,0.8);color:#fff;font-weight:600;border-radius:4px;pointer-events:none;z-index:200;white-space:nowrap}
#cfg-toast{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) scale(0.9);z-index:9999;background:rgba(20,25,35,0.95);color:#fff;border-radius:10px;padding:20px 28px;min-width:320px;max-width:420px;box-shadow:0 8px 32px rgba(0,0,0,0.5),0 0 0 1px rgba(255,255,255,0.1);opacity:0;pointer-events:none;transition:opacity 0.3s,transform 0.3s;font-family:Arial,sans-serif;text-align:center}
#cfg-toast.show{opacity:1;pointer-events:auto;transform:translate(-50%,-50%) scale(1)}
#cfg-toast .ct-icon{font-size:32px;margin-bottom:8px}
#cfg-toast .ct-title{font-size:15px;font-weight:700;margin-bottom:6px}
#cfg-toast .ct-msg{font-size:12px;color:#b0bec5;line-height:1.5}
#cfg-toast .ct-msg b{display:inline-block;max-width:360px;word-break:break-all}
#cfg-toast .ct-key{display:inline-block;background:rgba(255,255,255,0.1);border-radius:4px;padding:2px 8px;font-family:monospace;font-size:11px;margin-top:6px;color:#80CBC4;word-break:break-all}
#cfg-toast .ct-btn{display:inline-block;margin-top:12px;padding:6px 20px;background:#2196F3;color:#fff;border:none;border-radius:5px;cursor:pointer;font-size:12px;font-weight:600}
#cfg-toast .ct-btn:hover{background:#1976D2}
#cfg-toast .ct-btn.ct-del{background:#F44336;margin-left:8px}
#cfg-toast .ct-btn.ct-del:hover{background:#D32F2F}
#pinned-container{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:190;overflow:hidden}
.pinned-label{position:absolute;padding:3px 7px;background:rgba(0,0,0,0.82);color:#fff;font-weight:600;border-radius:4px;white-space:nowrap;pointer-events:none;border:1px solid rgba(255,255,255,0.25);box-shadow:0 1px 4px rgba(0,0,0,0.3);line-height:1.3}
.pinned-label .pn-node{color:#4FC3F7;font-size:0.9em}
.pinned-label .pn-val{color:#FFD54F}
.pinned-label .pn-elem{color:#81C784;font-size:0.9em}
#dialog-link-layer{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:265}
#dialog-box-container{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:191;overflow:hidden}
#measure-label-container{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:192;overflow:hidden}
.measure-node-label{position:absolute;min-width:18px;padding:2px 6px;border-radius:999px;background:#2196F3;color:#fff;font-size:10px;font-weight:800;line-height:1.2;text-align:center;pointer-events:none;border:1px solid rgba(255,255,255,0.35);box-shadow:0 1px 4px rgba(0,0,0,0.28);white-space:nowrap}
.dialog-box{position:absolute;pointer-events:auto;display:inline-block;max-width:340px;min-width:90px;background:rgba(255,255,255,0.95);color:#222;border:1px solid rgba(0,0,0,0.24);border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,0.35);font-size:11px;line-height:1.35;transition:border-color .15s,box-shadow .15s}
.dialog-box.active{border-color:#1976D2;box-shadow:0 0 0 2px rgba(25,118,210,0.22),0 2px 10px rgba(0,0,0,0.35)}
.dialog-box.editing{border-color:#FDD835;box-shadow:0 0 0 2px rgba(253,216,53,0.28),0 2px 10px rgba(0,0,0,0.35)}
.dialog-tools{display:none;align-items:center;justify-content:flex-end;gap:4px;height:18px;padding:2px 4px 0 4px;cursor:move}
.dialog-box.active .dialog-tools,.dialog-box.editing .dialog-tools{display:flex}
.dialog-btn{width:16px;height:16px;border:none;border-radius:3px;font-size:10px;line-height:16px;text-align:center;color:#fff;cursor:pointer;padding:0}
.dialog-btn-del{background:#D32F2F}
.dialog-btn-link{background:#1976D2}
.dialog-btn-copy{background:#00897B;width:auto;min-width:30px;padding:0 4px;font-size:8px;font-weight:700}
.dialog-btn-font{background:#FB8C00}
.dialog-btn-edit{background:#8E24AA}
.dialog-btn-link.dialog-btn-disconnect{background:#616161}
.dialog-body{display:inline-block;min-width:88px;min-height:22px;max-width:330px;padding:5px 7px;white-space:pre-wrap;word-break:break-word;outline:none;cursor:default}
.dialog-body-rich{white-space:normal;line-height:1.45;max-width:390px}
.dialog-body-rich .dlg-rich-head{display:inline-block;margin-bottom:8px;padding:4px 10px;border-radius:999px;background:#6A1B9A;color:#fff;font-weight:800;letter-spacing:0.2px}
.dialog-body-rich .dlg-rich-sec{margin-top:8px;padding:8px 10px;border-radius:8px;background:#fff;border-left:4px solid var(--dlg-accent,#6A1B9A);box-shadow:inset 0 0 0 1px rgba(0,0,0,0.06)}
.dialog-body-rich .dlg-rich-sec-title{font-weight:800;color:var(--dlg-accent,#6A1B9A);margin-bottom:6px}
.dialog-body-rich .dlg-rich-row+.dlg-rich-row{margin-top:5px}
.dialog-body-rich .dlg-rich-tag{display:inline-block;min-width:86px;padding:2px 7px;border-radius:999px;background:var(--dlg-accent,#6A1B9A);color:#fff;font-weight:700;font-size:0.92em;margin-right:6px}
.dialog-body-rich .dlg-rich-val{font-weight:600;color:#222}
.dialog-body-rich .dlg-rich-result{display:inline-block;padding:2px 8px;border-radius:6px;background:#FFF8E1;border:1px solid rgba(0,0,0,0.18);color:#000;font-weight:900}
.dialog-box.editing .dialog-body{cursor:text;border-top:1px solid rgba(253,216,53,0.58)}
.dialog-edit-popup{position:fixed;display:none;min-width:190px;background:rgba(255,255,255,0.98);border:2px solid #8E24AA;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,0.3);padding:10px 12px;z-index:194}
.dialog-edit-popup .dep-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px;font-size:11px;font-weight:800;color:#6A1B9A}
.dialog-edit-popup .dep-close{background:#F44336;color:#fff;border:none;border-radius:4px;font-size:10px;font-weight:700;padding:1px 7px;cursor:pointer}
.dialog-edit-popup .dep-row{display:flex;align-items:center;gap:6px;margin:6px 0;flex-wrap:wrap}
.dialog-edit-popup .dep-row label{font-size:10px;font-weight:700;color:#555}
.dialog-edit-popup .dep-btn{min-width:30px;padding:4px 6px;border:1px solid #bbb;border-radius:4px;background:linear-gradient(#fff,#eee);cursor:pointer;font-size:10px;font-weight:700;color:#333}
.dialog-edit-popup .dep-btn.on{background:linear-gradient(#AB47BC,#8E24AA);border-color:#6A1B9A;color:#fff}
.dialog-edit-popup input[type="color"]{width:38px;height:24px;padding:0;border:1px solid #bbb;border-radius:4px;background:#fff;cursor:pointer}
.dialog-font-popup{position:fixed;display:none;width:220px;max-width:calc(100vw - 20px);box-sizing:border-box;background:rgba(255,255,255,0.98);border:2px solid #FB8C00;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,0.3);padding:10px 12px;z-index:194}
.dialog-font-popup .dfp-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px;font-size:11px;font-weight:800;color:#E65100}
.dialog-font-popup .dfp-close{background:#F44336;color:#fff;border:none;border-radius:4px;font-size:10px;font-weight:700;padding:1px 7px;cursor:pointer}
.dialog-font-popup .dfp-row{display:flex;align-items:center;gap:8px}
.dialog-font-popup .dfp-row input[type="range"]{flex:1;accent-color:#FB8C00}
.dialog-font-popup .dfp-row select{flex:1;font-size:10px;padding:3px 4px;border:1px solid #bbb;border-radius:4px;background:#fff;color:#333}
.dialog-font-popup .dfp-val{font-size:10px;font-weight:700;color:#E65100;min-width:34px;text-align:right}
.dialog-preview{position:fixed;pointer-events:none;z-index:192;min-width:88px;padding:4px 7px;border:1px dashed rgba(33,150,243,0.75);border-radius:6px;background:rgba(18,22,30,0.28);color:#1976D2;font-size:10px;font-weight:700}
#dlg-actions{display:none;gap:4px;margin-left:6px}
#dlg-hint{display:none;font-size:9px;color:#777;margin:2px 0 0 22px}
#hide-elem-actions{display:none;flex-direction:column;gap:4px;margin:3px 0 0 22px;align-items:flex-start}
#hide-elem-hint{display:none;font-size:9px;color:#777;margin:2px 0 0 22px}
#meas-overlay{position:absolute;display:none;bottom:60px;left:50%;transform:translateX(-50%);padding:10px 18px;background:rgba(0,0,0,0.85);color:#fff;font-size:12px;border-radius:6px;z-index:200;white-space:pre;font-family:monospace;line-height:1.6;pointer-events:none;text-align:left;border:1px solid rgba(255,255,255,0.2)}

/* Table Form Window */
#table-form-window{position:absolute;top:80px;right:20px;width:320px;height:260px;max-height:85vh;max-width:70vw;min-width:220px;min-height:140px;background:rgba(255,255,255,0.97);border:2px solid #2196F3;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.25);z-index:250;display:flex;flex-direction:column;overflow:hidden;resize:both;--tf-font-size:10px;--tf-head-size:9px}
#table-form-header{background:#2196F3;color:white;padding:6px 12px;font-size:12px;font-weight:bold;display:flex;justify-content:space-between;align-items:center}
#table-form-close{background:transparent;border:none;color:white;font-size:16px;cursor:pointer;padding:0 4px;line-height:1}
#table-form-close:hover{color:#FFD600}
#table-form-input-row{display:flex;gap:4px;padding:6px 8px;border-bottom:1px solid #ddd}
#table-form-input-row input{flex:1;font-size:10px;padding:4px 6px;border:1px solid #ccc;border-radius:3px}
#table-form-input-row input:focus{border-color:#2196F3;outline:none}
#table-form-input-row button{font-size:10px;padding:4px 10px;background:#2196F3;color:white;border:none;border-radius:3px;cursor:pointer;font-weight:600}
#table-form-input-row button:hover{background:#1976D2}
#table-form-body{overflow-y:auto;flex:1;min-height:0;max-height:none;height:auto;padding:4px}
#table-form-body table{width:100%;height:100%;border-collapse:collapse;table-layout:fixed;font-size:var(--tf-font-size)}
#table-form-body th{background:#2196F3;color:white;padding:4px 8px;text-align:center;font-size:var(--tf-head-size);position:sticky;top:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#table-form-body td{padding:3px 8px;text-align:center;border:1px solid #e0e0e0;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;vertical-align:middle}
#table-form-body tr:hover{outline:2px solid #2196F3}
#table-form-body th.tf-col-sel{background:#FFD54F;color:#333}
#table-form-body td.tf-cell-sel{background:#FFE082!important;color:#333!important;outline:1px solid #FFB300}
#table-form-body tr.tf-row-sel td{background:#FFB74D!important;color:#222!important;outline:1px solid #F57C00}
#file-title-overlay{position:absolute;left:50%;bottom:42px;transform:translateX(-50%);z-index:275;pointer-events:none;font:700 13px Arial;color:rgba(0,0,0,0.92);background:transparent;white-space:nowrap}

/* Color Legend - Left side of 3D view area, below nav buttons, above axes */
#color-legend{
    position:absolute;top:70px;left:340px;
    width:130px;height:calc(100vh - 340px);
    background:rgba(255,255,255,0.95);border:2px solid #2196F3;border-radius:8px;
    box-shadow:0 4px 15px rgba(0,0,0,0.2);padding:15px 10px;z-index:100;
    display:flex;flex-direction:column;
}
#legend-state-meta{position:absolute;top:18px;left:340px;width:130px;padding:6px 7px;border:1px solid rgba(33,150,243,0.5);border-radius:6px;background:rgba(255,255,255,0.92);box-shadow:0 3px 10px rgba(0,0,0,0.12);z-index:101}
.legend-state-line{font-size:11px;font-weight:700;color:#1B3A57;line-height:1.25}
#legend-var-title{font-size:13px;font-weight:bold;color:#2196F3;text-align:center;margin-bottom:10px;line-height:1.2}
.disp-comp-wrap{display:none;margin-top:6px;padding:6px 7px;border:1px solid #d9d9d9;border-radius:6px;background:#fafafa}
.disp-comp-title{font-size:10px;font-weight:700;color:#555;margin-bottom:5px}
.disp-comp-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px}
.disp-comp-btn{font-size:9px;font-weight:700;padding:4px 6px;border-radius:4px;cursor:pointer;line-height:1.2;transition:background-color 0.15s ease,border-color 0.15s ease,color 0.15s ease}
.disp-comp-btn.disp-comp-mag{background:rgba(158,158,158,0.28);border:1px solid rgba(117,117,117,0.55);color:#555}
.disp-comp-btn.disp-comp-mag.active{background:#9E9E9E;border-color:#757575;color:#fff}
.disp-comp-btn.disp-comp-x{background:rgba(255,0,0,0.18);border:1px solid rgba(255,0,0,0.42);color:#B71C1C}
.disp-comp-btn.disp-comp-x.active{background:#FF0000;border-color:#D50000;color:#fff}
.disp-comp-btn.disp-comp-y{background:rgba(0,204,0,0.18);border:1px solid rgba(0,204,0,0.42);color:#1B5E20}
.disp-comp-btn.disp-comp-y.active{background:#00CC00;border-color:#009900;color:#fff}
.disp-comp-btn.disp-comp-z{background:rgba(0,102,255,0.18);border:1px solid rgba(0,102,255,0.42);color:#0D47A1}
.disp-comp-btn.disp-comp-z.active{background:#0066FF;border-color:#0047B3;color:#fff}
#legend-content{flex:1;display:flex;gap:6px;align-items:stretch}
#legend-values{display:flex;flex-direction:column;justify-content:space-between;font-weight:600;color:#333;min-width:55px;text-align:right}
#legend-values.legend-edit{min-width:78px;text-align:left}
.legend-val-row{display:flex;align-items:center;justify-content:flex-end;gap:3px}
.legend-val-text{padding:0;cursor:default}
#legend-values:not(.legend-edit) .legend-val-text{cursor:pointer}
.legend-val-edit{width:58px;font-size:10px;padding:1px 2px;border:1px solid #aaa;border-radius:2px;text-align:right;font-weight:600}
.legend-val-edit:focus{outline:none;border-color:#2196F3}
.legend-col-edit{width:14px;height:14px;padding:0;border:1px solid #666;border-radius:2px;cursor:pointer;background:none}
.legend-col-space{display:inline-block;width:14px;height:14px}
#legend-gradient{width:22px;background:linear-gradient(to bottom,#ff0000,#ffff00,#00ff00,#00ffff,#0000ff);border:1px solid #999;border-radius:3px;flex-shrink:0;overflow:hidden;cursor:pointer}
.leg-input{width:70px;font-size:11px;padding:2px 4px;border:1px solid #999;border-radius:3px;text-align:right;font-weight:600}
.leg-input:focus{border-color:#2196F3;outline:none}
.leg-btn{font-size:10px;padding:2px 8px;border:1px solid #999;border-radius:3px;cursor:pointer;background:#eee;margin:2px}
.leg-btn:hover{background:#2196F3;color:white}
.leg-btn-highlight{background:#2196F3;border-color:#1565C0;color:#fff;font-weight:bold;font-size:11px;padding:4px 14px;border-radius:5px;box-shadow:0 0 0 1px rgba(33,150,243,0.18),0 3px 8px rgba(33,150,243,0.35)}
.leg-btn-highlight:hover{background:#1976D2;color:#fff}

/* Navigation Buttons */
#nav-buttons{position:absolute;top:15px;left:calc(320px + (100vw - 320px)/2);transform:translateX(-50%);display:flex;gap:6px;z-index:100}
.nav-btn{
    width:40px;height:40px;background:rgba(255,255,255,0.95);border:2px solid #2196F3;
    border-radius:6px;cursor:pointer;display:flex;align-items:center;justify-content:center;
    font-size:18px;color:#2196F3;transition:all 0.2s;box-shadow:0 2px 8px rgba(0,0,0,0.15);user-select:none;
}
.nav-btn:hover{background:#2196F3;color:white;transform:scale(1.05)}
.nav-btn:active{transform:scale(0.95)}

/* Dual range slider container */
.range-row{display:flex;align-items:center;gap:6px;margin:6px 0;font-size:10px;color:#666}
.range-row input[type="range"]{flex:1}
.range-row .rv{min-width:20px;text-align:center;font-weight:bold;color:#333}

/* XY Plot Panel */
#xy-panel{position:absolute;top:0;right:0;height:100%;background:#fafafa;border-left:2px solid #2196F3;display:none;flex-direction:column;z-index:90;overflow:hidden}
#xy-panel.xy-fullscreen{position:fixed;top:0;left:0;right:0;bottom:0;width:100%!important;height:100%!important;z-index:9999;border:none}
#xy-panel.visible{display:flex}
#xy-panel-header{background:#2196F3;color:white;padding:8px 12px;font-size:13px;font-weight:bold;text-align:center;flex-shrink:0;position:relative}
#xy-plot-area{flex:1;position:relative;background:#fff;margin:8px;border:1px solid #ddd;border-radius:4px;min-height:200px}
#xy-plot-canvas{width:100%;height:100%;cursor:crosshair}
#xy-controls{flex-shrink:0;padding:8px;border-top:1px solid #ddd;overflow-y:auto;max-height:45%}
.xy-row{display:flex;gap:4px;margin:4px 0;align-items:center}
.xy-lbl{font-size:9px;font-weight:bold;color:#555;min-width:32px}
.xy-inp{flex:1;font-size:9px;padding:3px 5px;border:1px solid #ccc;border-radius:3px}
.xy-inp:focus{border-color:#2196F3;outline:none}
.xy-btn{font-size:10px;padding:4px 10px;border:1px solid #bdbdbd;border-radius:4px;cursor:pointer;background:linear-gradient(#ffffff,#e6e6e6);font-weight:600;transition:all .15s;box-shadow:0 2px 0 #bdbdbd,0 2px 6px rgba(0,0,0,0.15)}
.xy-btn:hover{background:linear-gradient(#e3f2fd,#bbdefb);color:#0D47A1;border-color:#2196F3}
.xy-btn:active{transform:translateY(1px);box-shadow:0 1px 0 #9e9e9e,0 1px 4px rgba(0,0,0,0.2)}
.xy-btn-del{color:#C62828;border-color:#EF9A9A;background:linear-gradient(#fff5f5,#ffd6d6)}
.xy-btn-del:hover{background:linear-gradient(#F44336,#D32F2F);color:white;border-color:#B71C1C}
.xy-btn-add{color:#1B5E20;border-color:#81C784;background:linear-gradient(#E8F5E9,#C8E6C9)}
.xy-btn-add:hover{background:linear-gradient(#66BB6A,#43A047);color:white;border-color:#2E7D32}
.xy-btn-edit{color:#0D47A1;border-color:#90CAF9;background:linear-gradient(#E3F2FD,#BBDEFB)}
.xy-btn-edit:hover{background:linear-gradient(#42A5F5,#1E88E5);color:white;border-color:#1565C0}
.xy-btn-deriv{color:#E65100;border-color:#FFB74D;background:linear-gradient(#FFF3E0,#FFE0B2)}
.xy-btn-deriv:hover{background:linear-gradient(#FFB74D,#FB8C00);color:#fff;border-color:#EF6C00}
.xy-btn-forecast{color:#6A1B9A;border-color:#CE93D8;background:linear-gradient(#F3E5F5,#E1BEE7)}
.xy-btn-forecast:hover{background:linear-gradient(#AB47BC,#8E24AA);color:#fff;border-color:#6A1B9A}
.xy-btn-font{color:#4E342E;border-color:#BCAAA4;background:linear-gradient(#F5F5F5,#E0E0E0)}
.xy-btn-font:hover{background:linear-gradient(#BCAAA4,#8D6E63);color:#fff;border-color:#6D4C41}
.xy-excel-icon{display:inline-flex;align-items:center;justify-content:center;width:12px;height:12px;margin-right:5px;border:1px solid #1B5E20;border-radius:2px;background:linear-gradient(#43A047,#2E7D32);color:#fff;font-size:9px;font-weight:800;line-height:1}
.xy-btn:disabled{opacity:0.55;cursor:not-allowed;box-shadow:none;transform:none}
.xy-btn:disabled:hover{background:linear-gradient(#ffffff,#e6e6e6);color:inherit;border-color:#bdbdbd}
.ncg-list{max-height:120px;overflow:auto;padding-right:2px;border:1px solid #e3e3e3;border-radius:4px;background:#fafafa}
.ncg-row{display:flex;align-items:center;justify-content:space-between;gap:6px;padding:2px 4px}
.ncg-row + .ncg-row{border-top:1px solid #ececec}
.ncg-lbl{font-size:9px;color:#444;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ncg-color{width:30px;height:16px;border:1px solid #999;border-radius:2px;padding:0;background:#fff;cursor:pointer;flex:0 0 auto}
#xy-curve-list{margin:6px 0;font-size:10px}
.xy-curve-item{display:flex;align-items:center;gap:6px;padding:4px 6px;margin:2px 0;background:#fff;border:1px solid #ddd;border-radius:4px;cursor:pointer}
.xy-curve-item:hover{background:#E3F2FD}
.xy-curve-item.selected{background:#BBDEFB;border-color:#2196F3}
.xy-curve-item.hidden{opacity:0.72;border-style:dashed}
.xy-curve-dot{width:10px;height:10px;border-radius:50%;border:2px solid;flex-shrink:0}
.xy-curve-name{flex:1;font-weight:600;color:#333}
.xy-curve-hidden{display:inline-block;margin-left:4px;font-size:9px;font-weight:700;color:#D32F2F}
#xy-table-area{display:none;margin:6px 0}
#xy-table{width:100%;border-collapse:collapse;font-size:10px}
#xy-table th{background:#2196F3;color:white;padding:4px 6px;font-size:9px;cursor:pointer}
#xy-table th.xy-col-sel{background:#FFD54F;color:#333}
#xy-table td{padding:2px 4px;border:1px solid #ddd}
#xy-table td.xy-row-idx{background:#f5f5f5;font-weight:bold;color:#555;cursor:pointer;text-align:center;width:22px}
#xy-table tr.xy-row-sel td{background:#FFF3E0}
#xy-table tr.xy-row-sel td.xy-row-idx{background:#FFCC80;color:#333}
#xy-table input{width:100%;border:none;padding:2px;font-size:10px;text-align:center;background:transparent}
#xy-table input:focus{outline:1px solid #2196F3;background:#fff}
#xy-table input.xy-col-sel{background:#FFF8E1}
#xy-table input.xy-cell-sel{background:#FFE082;border-color:#FFB300}
.xy-edit-divider{height:1px;background:linear-gradient(to right,transparent,#bbb,transparent);margin:6px 2px}
.xy-legend{display:flex;flex-wrap:wrap;gap:6px;margin:4px 8px;font-size:9px}
.xy-legend-item{display:flex;align-items:center;gap:3px}
#xy-font-popup{position:absolute;display:none;min-width:260px;max-width:300px;background:rgba(255,255,255,0.97);border:2px solid #FB8C00;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,0.28);padding:10px 12px;z-index:320}
#xy-font-popup .xyf-title{font-size:12px;font-weight:700;color:#E65100;display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
#xy-font-popup .xyf-close{background:#F44336;color:#fff;border:none;border-radius:3px;font-size:10px;font-weight:700;padding:1px 7px;cursor:pointer}
#xy-font-popup .xyf-row{margin:8px 0}
#xy-font-popup .xyf-lbl{display:flex;justify-content:space-between;align-items:center;font-size:10px;font-weight:700;color:#444;margin-bottom:3px}
#xy-font-popup .xyf-lbl .xyf-val{font-family:monospace;color:#1565C0}
#xy-font-popup input[type="range"]{width:100%;accent-color:#FB8C00}
.xy-modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;display:none;align-items:center;justify-content:center;padding:18px;background:rgba(16,22,34,0.48);z-index:10020}
.xy-modal{width:min(460px,92vw);max-height:90vh;overflow:auto;background:rgba(255,255,255,0.985);border:2px solid #8E24AA;border-radius:10px;box-shadow:0 10px 32px rgba(0,0,0,0.3);padding:14px 16px}
.xy-modal-title{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:10px}
.xy-modal-title span{font-size:13px;font-weight:700;color:#6A1B9A}
.xy-modal-close{background:#F44336;color:#fff;border:none;border-radius:4px;font-size:10px;font-weight:700;padding:2px 8px;cursor:pointer}
.xy-modal-close:hover{background:#D32F2F}
.xy-modal-sub{font-size:10px;color:#666;line-height:1.45;margin-bottom:10px}
.xy-modal-grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.xy-modal-field{display:flex;flex-direction:column;gap:3px;margin:8px 0}
.xy-modal-field label{font-size:10px;font-weight:700;color:#555}
.xy-modal-field input,.xy-modal-field select{width:100%;font-size:10px;padding:5px 7px;border:1px solid #bbb;border-radius:4px;background:#fff}
.xy-modal-field input:focus,.xy-modal-field select:focus{border-color:#8E24AA;outline:none}
.xy-modal-check{display:flex;align-items:flex-start;gap:8px;margin:10px 0 4px 0;font-size:10px;color:#444}
.xy-modal-check input{margin-top:2px;accent-color:#8E24AA}
.xy-modal-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:14px;flex-wrap:wrap}
.matvis-list{display:flex;flex-direction:column;gap:8px;margin-top:8px}
.matvis-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 10px;border:1px solid #D9E2F1;border-radius:8px;background:#F8FBFF}
.matvis-row.matvis-hidden{background:#FFF5F5;border-color:#F3C2C2}
.matvis-name{font-size:10px;font-weight:700;color:#1F3B63;line-height:1.35}
.matvis-count{font-size:9px;color:#666;font-weight:600}
.matvis-actions{display:flex;align-items:center;gap:6px;flex-shrink:0}
.matvis-btn{min-width:52px;padding:3px 10px;border:none;border-radius:5px;font-size:10px;font-weight:700;cursor:pointer}
.matvis-btn-show{background:#CFD8DC;color:#37474F}
.matvis-btn-show.active{background:#00C853;color:#fff}
.matvis-btn-hide{background:#FFCDD2;color:#B71C1C}
.matvis-btn-hide.active{background:#D32F2F;color:#fff}
.matvis-empty{padding:10px 12px;border:1px dashed #B0BEC5;border-radius:8px;background:#FAFAFA;font-size:10px;line-height:1.45;color:#666}
.matvis-floating-layer{position:fixed;inset:0;display:none;pointer-events:none;z-index:10025}
.matvis-floating-window{position:fixed;top:96px;left:calc(50vw - 230px);width:min(560px,94vw);max-height:min(78vh,680px);overflow:auto;background:rgba(255,255,255,0.985);border:2px solid #1976D2;border-radius:10px;box-shadow:0 10px 32px rgba(0,0,0,0.3);padding:14px 16px;pointer-events:auto}
.matvis-floating-title{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:10px;cursor:move;user-select:none}
.matvis-floating-title span{font-size:13px;font-weight:700;color:#1565C0}
.legend-extrap-summary{margin-top:6px;padding:6px 8px;border:1px solid #D1C4E9;border-radius:6px;background:#F6F0FB;font-size:9px;line-height:1.4;color:#5E35B1}
.legend-extrap-info{margin-top:8px;padding:8px 10px;border-radius:8px;background:#EEF6FF;border-left:4px solid #1E88E5;font-size:10px;line-height:1.45;color:#0D47A1}
#xy-forecast-fields{display:flex;flex-direction:column;gap:8px}
.xy-forecast-row{display:flex;align-items:flex-end;gap:6px}
.xy-forecast-row .xy-modal-field{flex:1;margin:0}
.xy-forecast-remove{min-width:30px;padding:4px 0}
.xy-result-box{background:#FAF7FC;border:1px solid #E1BEE7;border-radius:8px;padding:10px 12px;font-size:10px;color:#333;line-height:1.55}
.xy-result-box b{color:#4A148C}
.xy-result-box hr{border:none;border-top:1px solid #E1BEE7;margin:8px 0}
.xy-result-sec{margin-top:8px;padding-top:6px;border-top:1px dashed #CE93D8}
.xy-result-item+.xy-result-item{margin-top:6px}
.xy-result-block{margin-top:8px;padding:8px 10px;border-radius:8px;background:#fff;border-left:4px solid #8E24AA;box-shadow:inset 0 0 0 1px rgba(0,0,0,0.05)}
.xy-result-block-title{font-size:11px;font-weight:800;margin-bottom:6px}
.xy-result-row+.xy-result-row{margin-top:5px}
.xy-result-chip{display:inline-block;min-width:86px;padding:2px 7px;border-radius:999px;font-size:9px;font-weight:800;margin-right:6px}
.xy-result-value-highlight{display:inline-block;padding:2px 8px;border-radius:6px;background:#FFF8E1;border:1px solid rgba(0,0,0,0.18);color:#000;font-weight:900}
/* XY Sheet Tabs */
#xy-sheet-bar{display:flex;align-items:center;background:#1976D2;flex-shrink:0;min-height:28px;overflow-x:auto;padding:0 4px}
.xy-sheet-tab{font-size:10px;font-weight:600;padding:5px 12px;cursor:pointer;color:rgba(255,255,255,0.7);border:none;background:transparent;white-space:nowrap;border-bottom:2px solid transparent;transition:all .2s}
.xy-sheet-tab:hover{color:white;background:rgba(255,255,255,0.1)}
.xy-sheet-tab.active{color:white;background:rgba(255,255,255,0.15);border-bottom:2px solid #FFD600}
.xy-sheet-add{font-size:14px;font-weight:bold;padding:2px 8px;cursor:pointer;color:rgba(255,255,255,0.7);background:transparent;border:1px solid rgba(255,255,255,0.3);border-radius:3px;margin-left:4px;line-height:1;transition:all .2s}
.xy-sheet-add:hover{color:white;background:rgba(255,255,255,0.2)}
.xy-sheet-close{font-size:9px;margin-left:6px;color:rgba(255,255,255,0.5);cursor:pointer;font-weight:bold}
.xy-sheet-close:hover{color:#FF5252}
.xy-sheet-rename{font-size:10px;margin-left:4px;color:rgba(255,255,255,0.5);cursor:pointer}
.xy-sheet-rename:hover{color:#FFD600}
.xy-sheet-name{pointer-events:none}
/* XY Plot Toggle Button */
.xy-toggle-btn{display:inline-block;font-size:10px;font-weight:bold;padding:4px 14px;border-radius:4px;cursor:pointer;border:2px solid;transition:all .2s;min-width:50px;text-align:center}
.xy-toggle-btn.on{background:#4CAF50;color:white;border-color:#388E3C}
.xy-toggle-btn.off{background:#F44336;color:white;border-color:#D32F2F}
/* Value Range Filter dual-slider thumb styles */
#vrf-min::-webkit-slider-thumb{-webkit-appearance:none;pointer-events:all;width:14px;height:14px;border-radius:50%;background:#2196F3;border:2px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.4);cursor:pointer;position:relative;z-index:3}
#vrf-max::-webkit-slider-thumb{-webkit-appearance:none;pointer-events:all;width:14px;height:14px;border-radius:50%;background:#F44336;border:2px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.4);cursor:pointer;position:relative;z-index:4}
#vrf-min::-moz-range-thumb{pointer-events:all;width:12px;height:12px;border-radius:50%;background:#2196F3;border:2px solid white;cursor:pointer}
#vrf-max::-moz-range-thumb{pointer-events:all;width:12px;height:12px;border-radius:50%;background:#F44336;border:2px solid white;cursor:pointer}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gif.js/0.2.0/gif.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
</head><body>
<div id="c"><canvas id="cv"></canvas>

<div id="help-overlay">
<b>Mouse Controls</b><br>
Left Button: Rotate XY<br>
Middle Button: Toggle Zoom Box<br>
Right Button: Pan<br>
Ctrl + Left: Rotate Z<br>
Ctrl + Middle: Rotate Y<br>
Ctrl + Right: Rotate X<br>
Scroll Wheel: Zoom
</div>

<div id="watermark">Author: Leandro Barbosa</div>
<div id="file-title-overlay"></div>
<div id="val-tooltip"></div>
<canvas id="dialog-link-layer"></canvas>
<div id="pinned-container"></div>
<div id="dialog-box-container"></div>
<div id="measure-label-container"></div>
<div id="cfg-toast"></div>
<div id="meas-overlay"></div>
<div id="table-form-window" style="display:none">
<div id="table-form-header"><span>Table Form</span><button id="table-form-close" onclick="tgTableForm(false);document.getElementById('table-form-cb').checked=false">&#x2715;</button></div>
<div id="table-form-input-row">
<input type="text" id="table-form-ids" placeholder="Node or Elem IDs (e.g. 1,5,12 or E1,E5)" onkeyup="if(event.key==='Enter')updateTableForm()">
<button onclick="tfDeleteSelectedRow()">Delete select</button>
<button onclick="tfCopySelection()">Copy</button>
<button onclick="tfUpdateTableForm()">Update</button>
</div>
<div id="table-form-body"></div>
</div>
<input type="file" id="xy-file-input" accept=".xlsx,.xlsm,.csv" style="display:none" onchange="xyOnFileSelected(this)">

<!-- Color Legend with intermediate values on LEFT side -->
<div id="legend-state-meta">
<div class="legend-state-line" id="legend-inc-line">Inc: -</div>
<div class="legend-state-line" id="legend-time-line">Time: -</div>
</div>
<div id="color-legend">
<div id="legend-var-title">''' + (default_var if default_var else 'Variable') + '''</div>
<div id="legend-content">
<div id="legend-values"></div>
<div id="legend-gradient"></div>
</div>
</div>

<!-- Navigation Buttons -->
<div id="nav-buttons">
<div class="nav-btn" onclick="setView('front')" title="Front (XY)">XY</div>
<div class="nav-btn" onclick="setView('top')" title="Top (XZ)">XZ</div>
<div class="nav-btn" onclick="setView('side')" title="Side (YZ)">YZ</div>
<div class="nav-btn" onclick="zoomIn()" title="Zoom In">+</div>
<div class="nav-btn" onclick="zoomOut()" title="Zoom Out">&minus;</div>
<div class="nav-btn" onclick="fillView()" title="Fill View">&#x2302;</div>
<div class="nav-btn" id="zoom-box-btn" onclick="toggleZoomBox()" title="Zoom Box" style="font-size:13px">&#x2B1A;</div>
<div class="nav-btn" onclick="rotCCW()" title="Rotate Counter-Clockwise">&#x21BA;</div>
<div class="nav-btn" onclick="rotCW()" title="Rotate Clockwise">&#x21BB;</div>
</div>

<div id="sb">
<div class="lg">
''' + ('<img src="' + logo_data_uri + '" alt="Vibracoustic">' if logo_data_uri else '<h1>Vibracoustic</h1>') + '''
<h2>VMAP 3D Viewer</h2>
<span>European FEA Department - v1.0.37</span>
</div>
<div class="p sidebar-card file-info-card"><div class="pt"><span>File Information</span></div>
<div class="ir ir-file-name"><span class="il">Name: </span><span class="iv">''' + os.path.basename(reader.filepath) + '''</span></div>
<div class="ir"><span class="il">User: </span><span class="iv">''' + viewer_user_name + '''</span></div>
<div class="ir"><span class="il">Nodes: </span><span class="iv">''' + str(reader.n_nodes) + '''</span></div>
<div class="ir"><span class="il">Elements: </span><span class="iv">''' + str(reader.n_elements) + '''</span></div>
<div class="ir"><span class="il">States: </span><span class="iv">''' + str(len(reader.states)) + '''</span></div>
<div class="ir"><span class="il">Materials: </span><span class="iv" style="white-space:normal;word-break:break-word">''' + materials_info_html + '''</span></div>
</div>
<div id="sidebar-panel-zone">
<div class="p sidebar-card" data-panel-id="output-available"><div class="pt sidebar-card-handle"><span>Output Available</span><span class="sidebar-card-grip">&#9776;</span></div>
<select id="vs" onchange="ovs()">''' + ''.join(['<option value="{0}"{1}>{0}</option>'.format(
    v, ' selected' if v == default_var else '') for v in viewer_outputs]) + '''</select>
<div id="disp-component-wrap" class="disp-comp-wrap">
<div class="disp-comp-title">Displacement Component</div>
<div class="disp-comp-grid">
<button type="button" id="disp-comp-mag" class="disp-comp-btn disp-comp-mag" onclick="setDisplacementComponent('mag')">Displacement Mag</button>
<button type="button" id="disp-comp-x" class="disp-comp-btn disp-comp-x" onclick="setDisplacementComponent('x')">Displacement X</button>
<button type="button" id="disp-comp-y" class="disp-comp-btn disp-comp-y" onclick="setDisplacementComponent('y')">Displacement Y</button>
<button type="button" id="disp-comp-z" class="disp-comp-btn disp-comp-z" onclick="setDisplacementComponent('z')">Displacement Z</button>
</div>
</div>
</div>
<div class="p sidebar-card" data-panel-id="increment-selection"><div class="pt sidebar-card-handle"><span>Increment Selection</span><span class="sidebar-card-grip">&#9776;</span></div>
<select id="ss" onchange="osc()"><option value="">-- Select Increment --</option></select>
</div>
''' + animation_panel_html + '''
<div class="p sidebar-card" data-panel-id="display-options"><div class="pt sidebar-card-handle"><span>Display Options</span><span class="sidebar-card-grip">&#9776;</span></div>
<div class="disp-opt-sec disp-opt-sec-first">Mesh</div>
<div class="ck"><label style="font-size:11px;color:#444">Edges:</label><select id="ed" onchange="tgeMode(this.value)" style="margin-left:6px;font-size:10px;padding:2px 4px;border:1px solid #ccc;border-radius:3px"><option value="feature" selected>Feature Edges</option><option value="none">No Edges</option>''' + all_edges_option_html + '''</select></div>
<div class="ck"><input type="checkbox" id="wf" onchange="tgw(this.checked)"><label>Wireframe Mode</label></div>
<div class="ck"><input type="checkbox" id="um" onchange="tgu(this.checked)"><label>Undeformed Mesh</label></div>
<div class="ck"><label style="font-size:11px;color:#444">Show/Hide:</label><button class="bt bt2" onclick="openMaterialVisibilityDialog()" style="margin-left:6px;font-size:10px;padding:2px 10px">Open</button></div>
<div class="disp-opt-sec">View</div>
<div class="ck"><input type="checkbox" id="persp" onchange="tgp(this.checked)"><label>Perspective View</label></div>
<div class="ck"><input type="checkbox" id="ar" onchange="tgr(this.checked)"><label>Auto Rotate</label></div>
<div class="ck"><input type="checkbox" id="ax" checked onchange="tga(this.checked)"><label>Show Axes</label></div>
<div class="ck"><input type="checkbox" id="mi" checked onchange="tgmi(this.checked)"><label>Mouse Info</label></div>
<div class="ck"><label style="font-size:11px;color:#444">Background:</label><input type="color" id="bg-color" value="#efefef" onchange="setBgColor(this.value)" style="margin-left:6px;width:32px;height:20px;border:1px solid #ccc;border-radius:3px;cursor:pointer;vertical-align:middle"></div>
<div class="disp-opt-sec">Value Range Filter</div>
<div class="ck"><input type="checkbox" id="vrf-on" onchange="tgVRF(this.checked)"><label>Enable Range Filter</label></div>
<div id="vrf-controls" style="display:none;margin:4px 0">
<div style="position:relative;height:22px;margin:8px 6px 4px 6px">
<div id="vrf-track" style="position:absolute;top:8px;left:0;right:0;height:6px;background:linear-gradient(to right,#0000ff,#00ffff,#00ff00,#ffff00,#ff0000);border-radius:3px;border:1px solid #ccc"></div>
<div id="vrf-range" style="position:absolute;top:8px;height:6px;background:rgba(33,150,243,0.3);border-radius:3px"></div>
<input type="range" id="vrf-min" min="0" max="1000" value="0" step="1" oninput="onVRFSlider()" style="position:absolute;top:0;left:0;width:100%;pointer-events:none;-webkit-appearance:none;background:transparent;z-index:3">
<input type="range" id="vrf-max" min="0" max="1000" value="1000" step="1" oninput="onVRFSlider()" style="position:absolute;top:0;left:0;width:100%;pointer-events:none;-webkit-appearance:none;background:transparent;z-index:4">
</div>
<div style="display:flex;justify-content:space-between;font-size:9px;color:#666;margin:0 6px">
<span id="vrf-min-label">0.00e+0</span>
<span id="vrf-max-label">1.00e+0</span>
</div>
<div style="display:flex;justify-content:space-between;font-size:9px;font-weight:bold;color:#2196F3;margin:2px 6px">
<span>Lo: <span id="vrf-lo-val">0.00e+0</span></span>
<span>Hi: <span id="vrf-hi-val">1.00e+0</span></span>
</div>
</div>
<div class="disp-opt-sec">Data</div>
<div class="ck"><input type="checkbox" id="sv" onchange="tgv(this.checked)"><label>Values</label><button class="bt bt2" onclick="clearValuePinsAndTable()" style="margin-left:8px;font-size:9px;padding:1px 8px">Clear</button></div>
<div id="value-font-row" style="display:flex;align-items:center;gap:6px;margin:2px 0 4px 22px">
<span style="font-size:10px;color:#555;font-weight:600">Font</span>
<input type="range" id="value-font-size" min="7" max="20" step="1" value="12" oninput="setValueInfoFontSize(this.value)" style="flex:1;max-width:150px">
<span id="value-font-size-val" style="font-size:10px;font-weight:bold;color:#1976D2;min-width:18px;text-align:right">12</span>
</div>
<div id="val-lookup-bar" style="display:none;margin:2px 0 4px 0;padding:3px 0">
<div style="display:flex;gap:4px;align-items:center">
<input type="text" id="val-lookup-input" placeholder="Real IDs: E137304 or N12345" onkeyup="if(event.key===&apos;Enter&apos;)valLookup()" style="flex:1;font-size:10px;padding:3px 6px;border:1px solid #ccc;border-radius:3px">
<button class="bt bt2" onclick="valLookup()" style="font-size:9px;padding:2px 8px;white-space:nowrap">Find</button>
</div>
<div style="font-size:8px;color:#999;margin-top:2px" id="val-lookup-hint">Enter node IDs, or E1,E5 for elements</div>
</div>
<div id="table-form-row" style="display:none;margin:4px 0">
<div class="ck" style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
<span style="display:inline-flex;align-items:center"><input type="checkbox" id="table-form-cb" onchange="tgTableForm(this.checked)"><label>Table Form</label></span>
<span id="table-form-links-wrap" style="display:none;align-items:center;gap:4px">
<label style="font-size:11px;font-weight:bold;color:#444">Links</label>
<button type="button" id="table-form-links-btn" class="xy-toggle-btn off" style="min-width:46px;padding:2px 10px;font-size:10px" onclick="tgTableFormLinks()">Off</button>
</span>
</div>
</div>
<div id="table-form-font-row" style="display:none;align-items:center;gap:6px;margin:2px 0 4px 22px">
<span style="font-size:10px;color:#555;font-weight:600">Font</span>
<input type="range" id="table-form-font" min="8" max="18" step="1" value="10" oninput="setTableFormFont(this.value)" style="flex:1;max-width:150px">
<span id="table-form-font-val" style="font-size:10px;font-weight:bold;color:#1976D2;min-width:14px;text-align:right">10</span>
</div>
<div class="ck"><label style="font-size:11px;color:#444">Measure:</label><select id="meas-mode" onchange="setMeasMode(this.value)" style="margin-left:6px;font-size:10px;padding:2px 4px;border:1px solid #ccc;border-radius:3px"><option value="off" selected>Off</option><option value="distance">Distance</option><option value="angle">Angle</option></select><button class="bt bt3" onclick="armMeasAdd()" style="margin-left:4px;font-size:10px;padding:1px 8px">+</button><button class="bt bt2" onclick="clearMeas()" style="margin-left:4px;font-size:9px;padding:1px 6px">Clear</button></div>
<div class="disp-opt-sec">Text</div>
<div class="ck">
<input type="checkbox" id="dlg-on" onchange="tgDialogMode(this.checked)">
<label>Dialog Box</label>
<div id="dlg-actions">
<button class="bt bt3" id="dlg-add-btn" onclick="armAddDialogBox()" style="font-size:10px;padding:1px 8px;margin:0">+</button>
<button class="bt bt2" id="dlg-clean-btn" onclick="cleanDialogBoxes()" style="font-size:9px;padding:1px 7px;margin:0">Clean</button>
</div>
</div>
<div id="dlg-hint">Activate and click on the mesh area to place a dialog box.</div>
</div>
<div class="p sidebar-card" data-panel-id="xy-plot"><div class="pt sidebar-card-handle"><span>XY Plot</span><span class="sidebar-card-grip">&#9776;</span></div>
<div style="display:flex;align-items:center;gap:8px">
<span style="font-size:11px;font-weight:bold;color:#555">Mode:</span>
<button class="xy-toggle-btn off" id="xy-toggle-btn" onclick="tgxy(!xyPlotVisible)">Off</button>
</div>
</div>
<div class="p sidebar-card" data-panel-id="view-manager"><div class="pt sidebar-card-handle"><span>View Manager</span><span class="sidebar-card-grip">&#9776;</span></div>
<div class="disp-opt-sec disp-opt-sec-first">Cut View</div>
<div style="font-size:10px;color:#666;margin-bottom:6px">Cut the mesh along X, Y, or Z planes to reveal interior elements.</div>
<div class="ck"><input type="checkbox" id="cut-x-on" onchange="updateCutPlane('x')"><label>Enable X Cut</label></div>
<div class="range-row" id="cut-x-row" style="display:none"><span>X pos:</span><input type="range" id="cut-x-pos" min="0" max="100" value="50" step="1" oninput="updateCutPlane('x')"><span class="rv" id="cut-x-val">50%</span>
<select id="cut-x-dir" onchange="updateCutPlane('x')" style="width:40px;font-size:9px;padding:1px"><option value="+">+</option><option value="-">-</option></select></div>
<div class="ck"><input type="checkbox" id="cut-y-on" onchange="updateCutPlane('y')"><label>Enable Y Cut</label></div>
<div class="range-row" id="cut-y-row" style="display:none"><span>Y pos:</span><input type="range" id="cut-y-pos" min="0" max="100" value="50" step="1" oninput="updateCutPlane('y')"><span class="rv" id="cut-y-val">50%</span>
<select id="cut-y-dir" onchange="updateCutPlane('y')" style="width:40px;font-size:9px;padding:1px"><option value="+">+</option><option value="-">-</option></select></div>
<div class="ck"><input type="checkbox" id="cut-z-on" onchange="updateCutPlane('z')"><label>Enable Z Cut</label></div>
<div class="range-row" id="cut-z-row" style="display:none"><span>Z pos:</span><input type="range" id="cut-z-pos" min="0" max="100" value="50" step="1" oninput="updateCutPlane('z')"><span class="rv" id="cut-z-val">50%</span>
<select id="cut-z-dir" onchange="updateCutPlane('z')" style="width:40px;font-size:9px;padding:1px"><option value="+">+</option><option value="-">-</option></select></div>
<div class="ck" style="margin-top:3px"><input type="checkbox" id="cut-hide-planes" onchange="updateAxisCutVisuals()"><label>Hide planes</label></div>
<div class="ck" style="margin-top:3px"><input type="checkbox" id="cut-section-proj" onchange="tgCutSectionProjection(this.checked)"><label>Section Mesh on Plane</label></div>
<div style="font-size:10px;color:#666;margin:1px 0 6px 22px">Project the cut element edges onto the active cut plane.</div>
<div class="disp-opt-sec">Rotation Cut</div>
<div style="font-size:10px;color:#666;margin-bottom:6px">Rotate a cut plane around a global X, Y, or Z reference line.</div>
<div class="ck"><input type="checkbox" id="rot-cut-on" onchange="updateRotationCut()"><label>Enable Rotation Cut</label></div>
<div id="rot-cut-controls" style="display:none;margin:4px 0 2px 0">
<div class="ck"><label style="font-size:11px;color:#444">Axis:</label><select id="rot-cut-axis" onchange="updateRotationCut()" style="margin-left:6px;width:52px;font-size:10px;padding:1px 3px;border:1px solid #bbb;border-radius:3px"><option value="x" selected>X</option><option value="y">Y</option><option value="z">Z</option></select><span id="rot-cut-plane-hint" style="margin-left:8px;font-size:9px;color:#666">0&deg; =&gt; XY plane</span></div>
<div class="range-row"><span style="color:#1565C0;font-weight:700">Angle:</span><input type="range" id="rot-cut-angle" min="0" max="360" value="0" step="1" oninput="updateRotationCut()" style="accent-color:#1E88E5"><span class="rv" id="rot-cut-angle-val" style="color:#1565C0">0&deg;</span>
<select id="rot-cut-dir" onchange="updateRotationCut()" title="Rotation direction" style="width:40px;font-size:9px;padding:1px;border:1px solid #1E88E5;border-radius:3px;background:#E3F2FD;color:#0D47A1"><option value="+">+</option><option value="-">-</option></select></div>
<div style="display:flex;align-items:center;gap:8px;margin:5px 0 2px 0">
<span style="font-size:10px;color:#555;font-weight:600">Angle 2</span>
<button type="button" id="rot-cut-angle2-toggle" onclick="toggleRotationCutAngle2()" style="min-width:58px;padding:2px 10px;font-size:10px;border:2px solid #B71C1C;border-radius:4px;background:#F44336;color:#fff;font-weight:700;cursor:pointer">Off</button>
</div>
<div class="range-row" id="rot-cut-angle2-row" style="display:none"><span style="color:#2E7D32;font-weight:700">Angle 2:</span><input type="range" id="rot-cut-angle2" min="0" max="180" value="0" step="1" oninput="updateRotationCut()" style="accent-color:#43A047"><span class="rv" id="rot-cut-angle2-val" style="color:#2E7D32">0&deg;</span></div>
<div style="font-size:10px;color:#666;margin:6px 0 2px 0">Move Reference</div>
<div class="range-row"><span id="rot-cut-ref-a-lbl">Y ref:</span><input type="range" id="rot-cut-ref-a" min="0" max="100" value="50" step="1" oninput="updateRotationCut()"><span class="rv" id="rot-cut-ref-a-val">50%</span></div>
<div class="range-row"><span id="rot-cut-ref-b-lbl">Z ref:</span><input type="range" id="rot-cut-ref-b" min="0" max="100" value="50" step="1" oninput="updateRotationCut()"><span class="rv" id="rot-cut-ref-b-val">50%</span></div>
<div class="ck" style="margin-top:3px"><input type="checkbox" id="rot-cut-hide-plane" onchange="updateRotationCutVisualState()"><label>Hide plane</label></div>
<div style="display:flex;gap:4px;margin-top:4px"><button class="bt bt2" onclick="resetRotationCutReference()" style="font-size:9px;padding:1px 8px;flex:1">Center Ref</button><button class="bt bt2" onclick="resetRotationCutAngle()" style="font-size:9px;padding:1px 8px;flex:1">Zero Angle</button></div>
</div>
<button class="bt bt2" id="rot-cut-reset-all-btn" onclick="resetCutPlanes()" style="display:none;margin-top:6px;font-size:10px">Reset All Cuts</button>
<div class="disp-opt-sec">Hide Elements</div>
<div class="ck"><input type="checkbox" id="hide-elem-on" onchange="tgHideElements(this.checked)"><label>Hide Elements</label></div>
<div id="hide-elem-actions">
<div style="display:flex;align-items:center;gap:6px">
<span style="font-size:9px;color:#444;font-weight:600">All Connected:</span>
<button class="bt" id="hide-elem-all-btn" onclick="toggleHideAllConnected()" style="font-size:9px;padding:1px 9px;margin:0;min-width:46px;background:#D32F2F">Off</button>
</div>
<button class="bt bt2" id="hide-elem-unhide-btn" onclick="unhideAllElements()" style="font-size:9px;padding:1px 8px;margin:0">Unhide</button>
</div>
<div id="hide-elem-hint">Hide mode active: click an element or drag a box in the mesh area.</div>
</div>
<div class="p sidebar-card" data-panel-id="legend"><div class="pt sidebar-card-handle"><span>Legend</span><span class="sidebar-card-grip">&#9776;</span></div>
<div class="cl">Variable: <span class="sv" id="cln">''' + (default_var if default_var else 'None') + '''</span></div>
<div id="cb"></div>
<div style="margin-top:6px">
<div style="display:flex;align-items:center;gap:4px;margin:3px 0"><span style="font-size:11px;font-weight:bold;min-width:30px">Max:</span><input type="text" id="leg-max" class="leg-input" value="''' + cr_max + '''"><button class="bt" id="leg-max-mode-btn" onclick="tgLegendMaxMode()" style="font-size:9px;padding:1px 9px;margin:0;min-width:46px;background:#D32F2F">Off</button></div>
<div style="display:flex;align-items:center;gap:4px;margin:3px 0"><span style="font-size:11px;font-weight:bold;min-width:30px">Min:</span><input type="text" id="leg-min" class="leg-input" value="''' + cr_min + '''"><button class="bt" id="leg-min-mode-btn" onclick="tgLegendMinMode()" style="font-size:9px;padding:1px 9px;margin:0;min-width:46px;background:#D32F2F">Off</button></div>
<div style="display:flex;gap:4px;margin-top:4px">
<button class="leg-btn" onclick="applyLegRange()">Apply</button>
<button class="leg-btn" onclick="resetLegRange()">Reset</button>
</div>
<div style="display:flex;justify-content:flex-end;margin-top:4px"><button class="leg-btn leg-btn-highlight" onclick="openExtrapolationDialog()">Visualization Options</button></div>
<div id="legend-extrap-summary" class="legend-extrap-summary">''' + ('Linear | Nodal Avg Off | Element-local contour' if var_locations.get(default_var, 'node') == 'element' else 'Linear | Nodal Avg Off | Native nodal contour') + '''</div>
<div id="leg-data-info" style="font-size:10px;color:#888;margin-top:3px">Data range: ''' + cr_min + ''' ~ ''' + cr_max + '''</div>
<div style="display:flex;align-items:center;gap:4px;margin-top:4px;flex-wrap:wrap"><span style="font-size:10px;font-weight:bold">Font:</span><input type="range" id="leg-font-size" min="7" max="20" step="1" value="14" oninput="setLegFontSize(this.value)" style="width:82px"><span id="leg-font-size-val" style="font-size:10px;font-weight:bold;color:#1976D2;min-width:18px;text-align:right">14</span>
<span style="font-size:10px;font-weight:bold;margin-left:6px">Levels:</span><select id="leg-levels" onchange="setLegLevels(this.value)" style="width:56px;font-size:10px;padding:1px 2px;border:1px solid #999;border-radius:3px"><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="7">7</option><option value="8">8</option><option value="9">9</option><option value="10">10</option><option value="11">11</option><option value="12" selected>12</option><option value="13">13</option><option value="14">14</option><option value="15">15</option></select></div>
<div style="display:flex;align-items:center;gap:4px;margin-top:4px"><span style="font-size:10px;font-weight:bold">Format:</span><select id="leg-format" onchange="setLegFormat(this.value)" style="width:78px;font-size:10px;padding:1px 2px;border:1px solid #999;border-radius:3px"><option value="exp">Exponential</option><option value="float" selected>Floating</option></select><span id="leg-fdec-wrap" style="display:inline-flex;align-items:center;gap:3px;margin-left:2px"><span style="font-size:10px;font-weight:bold">Dec:</span><select id="leg-fdec" onchange="setLegFloatDecimals(this.value)" style="width:56px;font-size:10px;padding:1px 2px;border:1px solid #999;border-radius:3px"><option value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3" selected>3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="7">7</option><option value="8">8</option></select></span></div>
<div style="display:flex;justify-content:flex-end;margin-top:3px"><button class="leg-btn" onclick="legendDefault()">Default</button></div>
<div style="margin-top:6px;border-top:1px solid #e0e0e0;padding-top:4px">
<div class="ck"><input type="checkbox" id="dc" checked onchange="tgd(this.checked)"><label>Discrete Legend</label></div>
<div class="ck"><input type="checkbox" id="dynleg" onchange="tgdl(this.checked)"><label>Dynamic Legend</label></div>
<div class="ck"><input type="checkbox" id="nc" onchange="tgnc(this.checked)"><label>No Contour</label></div>
<div id="nc-groups-wrap" style="display:none;margin:2px 0 4px 22px">
<div style="font-size:9px;color:#555;font-weight:700;margin-bottom:2px">Connected Groups Colors</div>
<div id="nc-groups-body" class="ncg-list"></div>
</div>
<div class="ck"><input type="checkbox" id="umc" onchange="tgUndContour(this.checked)"><label>Undeformed mesh - Contour On</label></div>
</div>
</div>
</div>
''' + scale_controls_html + '''
<div class="p sidebar-card" data-panel-id="save-load"><div class="pt sidebar-card-handle"><span>Save and Load</span><span class="sidebar-card-grip">&#9776;</span></div>
<button class="bt bt-orange" onclick="scs()">&#128247; Screenshot</button>
<button class="bt bt-yellow" onclick="saveCurrentHtmlFile()">&#128196; Save File</button>
<button class="bt bt3" onclick="saveConfig()">&#128190; Save Config</button>
<button class="bt" onclick="document.getElementById('cfg-file-input').click()" style="font-size:10px">&#128194; Load Config</button>
<input type="file" id="cfg-file-input" accept=".json" style="display:none" onchange="loadConfigFile(this)">
</div>
</div>
</div>
<!-- XY Plot Panel -->
<div id="xy-panel">
<div id="xy-panel-header"><input id="xy-plot-title" type="text" value="XY Plot" style="background:transparent;border:none;color:white;font-size:13px;font-weight:bold;text-align:center;width:calc(100% - 50px);outline:none;padding:0"><button id="xy-fullscreen-btn" onclick="xyToggleFullscreen()" style="position:absolute;right:8px;top:6px;background:transparent;border:1px solid rgba(255,255,255,0.6);color:white;font-size:14px;cursor:pointer;padding:2px 6px;border-radius:3px;line-height:1" title="Toggle Fullscreen">&#x26F6;</button></div>
<div id="xy-sheet-bar"><button class="xy-sheet-tab active" data-sheet="0" onclick="xySwitchSheet(0)">Sheet 1</button><button class="xy-sheet-add" onclick="xyAddSheet()" title="Add new sheet">+</button></div>
<div id="xy-plot-area"><canvas id="xy-plot-canvas"></canvas><div id="xy-tooltip" style="position:absolute;display:none;padding:4px 8px;color:#fff;font-size:10px;font-weight:600;border-radius:4px;pointer-events:none;white-space:nowrap;z-index:200"></div><div id="xy-zoom-rect" style="position:absolute;display:none;border:2px dashed #2196F3;background:rgba(33,150,243,0.1);pointer-events:none;z-index:150"></div></div>
<div class="xy-legend" id="xy-legend"></div>
<div id="xy-controls">
<div style="font-size:10px;font-weight:bold;color:#2196F3;cursor:pointer;margin-bottom:2px;user-select:none" id="xy-hdr-axis" onclick="xyToggleSection('xy-sec-axis','xy-hdr-axis')">[+] AXIS SETTINGS</div>
<div id="xy-sec-axis" style="display:none">
<div style="font-size:9px;font-weight:bold;color:#4CAF50;cursor:pointer;margin:4px 0 2px 0;user-select:none;border-bottom:1px solid #ddd;padding-bottom:2px" id="xy-hdr-pri" onclick="xyToggleSection('xy-sec-pri','xy-hdr-pri')">[-] Primary Axis</div>
<div id="xy-sec-pri">
<div class="xy-row"><span class="xy-lbl">X name:</span><input class="xy-inp" id="xy-xname" type="text" value="X" oninput="drawPlot()">
<span class="xy-lbl">Y name:</span><input class="xy-inp" id="xy-yname" type="text" value="Y" oninput="drawPlot()"></div>
<div class="xy-row"><label style="font-size:10px;cursor:pointer"><input type="checkbox" id="xy-origin" checked onchange="drawPlot()" style="margin-right:4px">Origin Lines (0,0)</label></div>
<div class="xy-row"><span class="xy-lbl">X min:</span><input class="xy-inp" id="xy-xmin" type="text" value="auto">
<span class="xy-lbl">X max:</span><input class="xy-inp" id="xy-xmax" type="text" value="auto"></div>
<div class="xy-row"><span class="xy-lbl">Y min:</span><input class="xy-inp" id="xy-ymin" type="text" value="auto">
<span class="xy-lbl">Y max:</span><input class="xy-inp" id="xy-ymax" type="text" value="auto"></div>
<div class="xy-row"><span class="xy-lbl">X step:</span><input class="xy-inp" id="xy-xstep" type="text" value="auto" title="Tick step for X axis (from 0)">
<span class="xy-lbl">Y step:</span><input class="xy-inp" id="xy-ystep" type="text" value="auto" title="Tick step for Y axis (from 0)"></div>
</div>
<div style="font-size:9px;font-weight:bold;color:#F44336;cursor:pointer;margin:6px 0 2px 0;user-select:none;border-bottom:1px solid #ddd;padding-bottom:2px" id="xy-hdr-sec" onclick="xyToggleSection('xy-sec-sec','xy-hdr-sec')">[+] Secondary Y Axis (R)</div>
<div id="xy-sec-sec" style="display:none">
<div class="xy-row"><span class="xy-lbl">Y(R) name:</span><input class="xy-inp" id="xy-syname" type="text" value="Y (R)" oninput="drawPlot()"></div>
<div class="xy-row"><span class="xy-lbl">Y(R) min:</span><input class="xy-inp" id="xy-symin" type="text" value="auto">
<span class="xy-lbl">Y(R) max:</span><input class="xy-inp" id="xy-symax" type="text" value="auto"></div>
<div class="xy-row"><span class="xy-lbl">Y(R) step:</span><input class="xy-inp" id="xy-systep" type="text" value="auto" title="Tick step for secondary Y axis (from 0)"></div>
</div>
<div class="xy-row"><button class="xy-btn" onclick="xyApplyRange()">Apply Range</button>
<button class="xy-btn" onclick="xyAutoRange()">Auto Range</button>
<button class="xy-btn" onclick="xyResetZoom()" title="Reset zoom to applied range">Reset Zoom</button>
<button class="xy-btn" onclick="xyResetAxes()" title="Reset all axis settings to auto (except names)">Reset Axes</button>
<button class="xy-btn" onclick="xyClearPinned()" title="Clear fixed point info">Clear Pin</button>
<button class="xy-btn xy-btn-font" id="xy-font-btn" onclick="xyToggleFontPopup()" title="XY preferences">Preferences</button>
<button class="xy-btn" id="xy-anim-info-btn" onclick="xyToggleAnimInfo()" style="display:none;background:#D32F2F;color:#fff;border-color:#B71C1C">Hide Info.</button></div>
</div>
<div class="xy-edit-divider" style="margin:10px 0 8px 0"></div>
<div style="font-size:10px;font-weight:bold;color:#2196F3;cursor:pointer;margin:14px 0 2px 0;user-select:none" id="xy-hdr-curves" onclick="xyToggleSection('xy-sec-curves','xy-hdr-curves')">[+] CURVES</div>
<div id="xy-sec-curves" style="display:none">
<div id="xy-curve-list"></div>
<div id="xy-table-area">
<div class="xy-row"><span class="xy-lbl">Name:</span><input class="xy-inp" id="xy-curve-name" type="text" value="Curve 1"></div>
<div class="xy-row"><span class="xy-lbl">Axis:</span><label style="font-size:10px;cursor:pointer;margin-right:8px"><input type="radio" name="xy-axis-sel" id="xy-axis-pri" value="primary" checked style="margin-right:2px">Primary (L)</label><label style="font-size:10px;cursor:pointer"><input type="radio" name="xy-axis-sel" id="xy-axis-sec" value="secondary" style="margin-right:2px">Secondary (R)</label></div>
<div class="xy-row"><span class="xy-lbl">X label:</span><input class="xy-inp" id="xy-col-x" type="text" value="X">
<span class="xy-lbl">Y label:</span><input class="xy-inp" id="xy-col-y" type="text" value="Y"></div>
<div style="max-height:200px;overflow-y:auto;margin:4px 0">
<table id="xy-table"><thead><tr><th style="width:22px">#</th><th id="xy-th-x">X</th><th id="xy-th-y">Y</th><th style="width:20px"></th></tr></thead><tbody id="xy-tbody"></tbody></table>
</div>
<div class="xy-row">
<button class="xy-btn" onclick="xyAddRow()">+ Row</button>
<button class="xy-btn" onclick="xyPasteData()" title="Paste X,Y data from clipboard">Paste</button>
<button class="xy-btn" onclick="xyCopySelectedCols()" title="Copy selected X/Y columns">Copy</button>
<button class="xy-btn xy-btn-del" onclick="xyDeleteSelection()" title="Delete selected rows/cells">Delete Sel</button>
<button class="xy-btn" onclick="xyLoadExcel()" title="Load from Excel/CSV file"><span class="xy-excel-icon">X</span>Load Excel</button>
<button class="xy-btn" onclick="xySaveCurve()">Save</button>
<button class="xy-btn" onclick="xyCancelEdit()">Cancel</button>
<button class="xy-btn" id="xy-hide-btn" onclick="xyToggleHideEditingCurve()">Hide</button>
</div>
<div class="xy-edit-divider"></div>
</div>
<div class="xy-row" id="xy-main-btns">
<button class="xy-btn xy-btn-add" onclick="xyAddCurve()">Add</button>
<button class="xy-btn xy-btn-edit" onclick="xyEditCurve()">Edit</button>
<button class="xy-btn xy-btn-deriv" id="xy-deriv-btn" onclick="xyDerivativeCurve()" style="display:none">Derivative</button>
<button class="xy-btn xy-btn-forecast" id="xy-forecast-btn" onclick="xyOpenForecastDialog()" style="display:none">Forecast</button>
<button class="xy-btn xy-btn-del" onclick="xyDeleteCurve()">Delete</button>
<button class="xy-btn xy-btn-del" onclick="xyDeleteAllCurves()">Delete All</button>
</div>
</div>
</div>
<div id="xy-font-popup">
<div class="xyf-title"><span>Preferences</span><button class="xyf-close" onclick="xyToggleFontPopup(false)">X</button></div>
<div class="xyf-row">
<div class="xyf-lbl"><span>Font</span><span class="xyf-val" id="xy-font-val">10 px</span></div>
<input type="range" id="xy-pref-font" min="8" max="24" step="1" value="10" oninput="xySetPrefFont(this.value)">
</div>
<div class="xyf-row">
<div class="xyf-lbl"><span>Format</span><span class="xyf-val" id="xy-format-val">Floating</span></div>
<select id="xy-val-format" onchange="xySetValueFormat(this.value)" style="width:100%;font-size:10px;padding:3px 4px;border:1px solid #bbb;border-radius:4px">
<option value="exp">Exponential</option>
<option value="float" selected>Floating</option>
</select>
</div>
<div class="xyf-row" id="xy-float-levels-row">
<div class="xyf-lbl"><span>Levels</span><span class="xyf-val" id="xy-float-levels-val">2</span></div>
<input type="range" id="xy-float-levels" min="0" max="8" step="1" value="2" oninput="xySetFloatLevels(this.value)">
</div>
</div>
</div>
<div class="xy-modal-overlay" id="xy-forecast-overlay">
<div class="xy-modal">
<div class="xy-modal-title"><span>Forecast</span><button class="xy-modal-close" onclick="xyCloseForecastDialog()">X</button></div>
<div class="xy-modal-sub" id="xy-forecast-curve-info">Select one curve to create a linear forecast using all curve data.</div>
<div class="xy-modal-field">
<label for="xy-forecast-axis">Use Column</label>
<select id="xy-forecast-axis" onchange="xyUpdateForecastDialogText()">
<option value="x" selected>X</option>
<option value="y">Y</option>
</select>
</div>
<div class="xy-modal-sub" id="xy-forecast-axis-note">All forecast fields below use the selected column as the Multipole reference.</div>
<div id="xy-forecast-fields"></div>
<div class="xy-modal-actions" style="justify-content:flex-start;margin-top:8px">
<button class="xy-btn xy-btn-add" onclick="xyAddForecastField()">Add</button>
</div>
<label class="xy-modal-check">
<input type="checkbox" id="xy-forecast-secondary">
<span>Consider secondary axis curves and evaluate their Y value at the forecast X.</span>
</label>
<div class="xy-modal-actions">
<button class="xy-btn" onclick="xyCloseForecastDialog()">Close</button>
<button class="xy-btn xy-btn-forecast" onclick="xyRunForecast()">Run Forecast</button>
</div>
</div>
</div>
<div class="xy-modal-overlay" id="xy-forecast-result-overlay">
<div class="xy-modal">
<div class="xy-modal-title"><span>Forecast Result</span><button class="xy-modal-close" onclick="xyCloseForecastResultDialog()">X</button></div>
<div class="xy-result-box" id="xy-forecast-result-body">No forecast calculated yet.</div>
<div class="xy-modal-actions">
<button class="xy-btn xy-btn-forecast" onclick="xyCreateForecastDialogBox()">Create Diag. Box</button>
<button class="xy-btn" onclick="xyCloseForecastResultDialog()">Close</button>
</div>
</div>
</div>
<div class="xy-modal-overlay" id="legend-extrapolation-overlay" onclick="if(event.target===this)closeExtrapolationDialog()">
<div class="xy-modal">
<div class="xy-modal-title"><span>Legend Extrapolation</span><button class="xy-modal-close" onclick="closeExtrapolationDialog()">X</button></div>
<div class="xy-modal-sub">Mentat-style contour controls for the current output variable.</div>
<div class="xy-modal-field" style="margin-bottom:10px">
<label for="legend-extrap-standard">Visualization Standard</label>
<select id="legend-extrap-standard" onchange="onExtrapolationStandardPresetInput()"></select>
</div>
<div class="xy-modal-grid2">
<div class="xy-modal-field">
<label for="legend-extrap-method">Extrapolation Method</label>
<select id="legend-extrap-method" onchange="onExtrapolationManualSettingInput()">
<option value="linear">Linear</option>
<option value="translate">Translate</option>
<option value="average">Average</option>
</select>
</div>
<div class="xy-modal-field">
<label for="legend-extrap-nodal-avg">Nodal Averaging</label>
<select id="legend-extrap-nodal-avg" onchange="onExtrapolationManualSettingInput()">
<option value="off">Off</option>
<option value="on">On</option>
</select>
</div>
</div>
<div class="xy-modal-field">
<label for="legend-extrap-standard-info">Information</label>
<div id="legend-extrap-standard-info" class="legend-extrap-info">Select a visualization standard to load the mapped Mentat extrapolation settings from CMO_031_C.pdf.</div>
</div>
<div class="xy-modal-actions">
<button class="xy-btn" onclick="closeExtrapolationDialog()">Close</button>
<button class="xy-btn" onclick="resetExtrapolationSettings()">Reset</button>
<button class="xy-btn xy-btn-forecast" onclick="applyExtrapolationDialog()">Apply</button>
</div>
</div>
</div>
<div class="matvis-floating-layer" id="material-visibility-overlay">
<div class="matvis-floating-window" id="material-visibility-window">
<div class="matvis-floating-title" id="material-visibility-handle"><span id="material-visibility-title">Show / Hide</span><button class="xy-modal-close" onclick="closeMaterialVisibilityDialog()">X</button></div>
<div id="material-visibility-sub" class="xy-modal-sub">Show or hide element categories.</div>
<div id="material-visibility-body" class="matvis-list"></div>
<div class="xy-modal-actions">
<button class="xy-btn" onclick="showAllVisibilityCategories()">Show All</button>
<button class="xy-btn" onclick="closeMaterialVisibilityDialog()">Close</button>
</div>
</div>
</div>
<div id="st">Ready</div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
''' + static_data_scripts_html + '''
''' + state_nodes_scripts_html + '''
''' + output_state_scripts_html + '''
<script>
const CORE_DATA_TAG_MAP=''' + static_data_tag_map_json + ''';
function readChunkedJsonTag(tagInfo){
if(!tagInfo)return '';
if(typeof tagInfo==='string'){
var t0=document.getElementById(tagInfo);
if(!t0)return '';
return (t0.textContent||t0.innerText||'');
}
var base=tagInfo.base;
var n=parseInt(tagInfo.chunks,10);
if(!base||!isFinite(n)||n<1)return '';
var parts=[];
for(var i=0;i<n;i++){
var ti=document.getElementById(base+'-c'+i);
if(!ti&&n===1)ti=document.getElementById(base);
if(!ti)return '';
parts.push((ti.textContent||ti.innerText||''));
}
return parts.join('');
}
function parseCoreData(name,fallback){
var info=CORE_DATA_TAG_MAP[name];
if(!info)return fallback;
var txt=readChunkedJsonTag(info);
if(!txt)return fallback;
try{return JSON.parse(txt);}catch(e){console.error('Core data parse failed for '+name+':',e);return fallback;}
}
const ON=parseCoreData('ON',[]);
const BF=parseCoreData('BF',[]);
const BFE=parseCoreData('BFE',[]);
let F=null;
let FEM=null;
function getFullFaces(){if(!F)F=parseCoreData('F',[]);return F;}
function getFullFaceElemMap(){if(!FEM)FEM=parseCoreData('FEM',[]);return FEM;}
const NIDS=parseCoreData('NIDS',[]);
const EIDS=parseCoreData('EIDS',[]);
const ECOFF_RAW=parseCoreData('ECOFF',null);
const ECON_RAW=parseCoreData('ECON',null);
const MATN=parseCoreData('MATN',[]);
const EMM=parseCoreData('EMM',[]);
const NIDS_REV={};NIDS.forEach(function(id,i){NIDS_REV[id]=i;});
const EIDS_REV={};EIDS.forEach(function(id,i){EIDS_REV[id]=i;});
function realElemIdToIdx(realId){var idx=EIDS_REV[realId];return idx!==undefined?idx:(realId>=0&&realId<EIDS.length?realId:-1);}
function realNodeIdToIdx(realId){var idx=NIDS_REV[realId];return idx!==undefined?idx:(realId>=0&&realId<NIDS.length?realId:-1);}
function elemIdxToReal(idx){return (EIDS&&idx>=0&&idx<EIDS.length)?EIDS[idx]:idx;}
function nodeIdxToReal(idx){return (NIDS&&idx>=0&&idx<NIDS.length)?NIDS[idx]:idx;}
let C=null;
function decodeB64Bytes(b64){
if(!b64)return null;
try{
var bin=atob(b64);
var len=bin.length;
var out=new Uint8Array(len);
for(var i=0;i<len;i++)out[i]=bin.charCodeAt(i)&255;
return out;
}catch(e){return null;}
}
function decodeNormI16B64(b64,count){
var bytes=decodeB64Bytes(b64);
if(!bytes)return null;
try{
var buf=bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);
var arr=new Int16Array(buf);
var n=(count&&count>0)?Math.min(count,arr.length):arr.length;
var out=new Array(n);
for(var i=0;i<n;i++){
var v=arr[i];
if(v<0)v=0;
out[i]=v/32767.0;
}
return out;
}catch(e){return null;}
}
function decodeInt32B64(b64,count){
var bytes=decodeB64Bytes(b64);
if(!bytes)return null;
try{
var buf=bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);
var arr=new Int32Array(buf);
var n=(count&&count>0)?Math.min(count,arr.length):arr.length;
var out=new Array(n);
for(var i=0;i<n;i++)out[i]=arr[i]|0;
return out;
}catch(e){return null;}
}
function decodeNodesF32B64(b64,nNodes){
var bytes=decodeB64Bytes(b64);
if(!bytes)return null;
try{
var buf=bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);
var arr=new Float32Array(buf);
var nn=(nNodes&&nNodes>0)?nNodes:ON.length;
var out=new Array(nn);
for(var i=0;i<nn;i++){
var k=i*3;
if(k+2<arr.length)out[i]=[arr[k],arr[k+1],arr[k+2]];
else out[i]=[0,0,0];
}
return out;
}catch(e){return null;}
}
function getInitialColors(){
if(C===null){
C=parseCoreData('C',null);
if(C&&C.i16_b64!==undefined){
C=decodeNormI16B64(C.i16_b64,C.count);
}
}
return C;
}
const ECOFF=(ECOFF_RAW&&ECOFF_RAW.i32_b64!==undefined)?decodeInt32B64(ECOFF_RAW.i32_b64,ECOFF_RAW.count):null;
const ECON=(ECON_RAW&&ECON_RAW.i32_b64!==undefined)?decodeInt32B64(ECON_RAW.i32_b64,ECON_RAW.count):null;
const CR=''' + json.dumps(color_range, separators=(',', ':')) + ''';
const SL=parseCoreData('SL',[]);
const STATE_NODE_TAG_MAP=''' + state_nodes_tag_map_json + ''';
const STATE_NODE_CACHE={};
const STATE_DISP_CACHE={};
const STATE_NODE_PAYLOAD_CACHE={};
const OUT_STATE_INDEX=''' + output_state_index_json + ''';
const OUT_STATE_TAG_MAP=''' + output_state_tag_map_json + ''';
const OUT_STATE_CACHE={};
const VAR_LOCS=''' + json.dumps(var_locations, separators=(',', ':')) + ''';
const VIRTUAL_DISPLACEMENT_OUTPUT=''' + ('true' if virtual_displacement_output else 'false') + ''';
const EXTRAPOLATION_STANDARD_PRESETS=''' + json.dumps(EXTRAPOLATION_STANDARD_PRESETS, separators=(',', ':')) + ''';
const EXTRAPOLATION_STANDARD_PRESET_MAP={};
EXTRAPOLATION_STANDARD_PRESETS.forEach(function(p){
if(p&&p.name!==undefined&&p.name!==null)EXTRAPOLATION_STANDARD_PRESET_MAP[String(p.name)]=p;
});
function getStateNodePayload(sid){
if(!sid)return null;
if(Object.prototype.hasOwnProperty.call(STATE_NODE_PAYLOAD_CACHE,sid))return STATE_NODE_PAYLOAD_CACHE[sid];
var tagInfo=STATE_NODE_TAG_MAP[sid];
if(!tagInfo)return null;
var txt=readChunkedJsonTag(tagInfo);
if(!txt)return null;
try{
var parsed=JSON.parse(txt);
STATE_NODE_PAYLOAD_CACHE[sid]=parsed;
return parsed;
}catch(e){
console.error('State node parse failed for '+sid+':',e);
return null;
}
}
function buildAbsoluteNodesFromDisp(disp){
var nn=ON.length||0;
var out=new Array(nn);
for(var i=0;i<nn;i++){
var o=ON[i]||[0,0,0];
var d=(disp&&disp[i])?disp[i]:[0,0,0];
var dx=Number(d[0]);if(!isFinite(dx))dx=0;
var dy=Number(d[1]);if(!isFinite(dy))dy=0;
var dz=Number(d[2]);if(!isFinite(dz))dz=0;
out[i]=[Number(o[0])+dx,Number(o[1])+dy,Number(o[2])+dz];
}
return out;
}
function getStateDisplacements(sid){
if(!sid)return null;
if(Object.prototype.hasOwnProperty.call(STATE_DISP_CACHE,sid))return STATE_DISP_CACHE[sid];
var payload=getStateNodePayload(sid);
if(!payload)return null;
var disp=null;
if(payload&&payload.disp_f32_b64!==undefined){
disp=decodeNodesF32B64(payload.disp_f32_b64,payload.n_nodes);
}else if(payload&&payload.f32_b64!==undefined){
var absNodes=decodeNodesF32B64(payload.f32_b64,payload.n_nodes);
if(absNodes){
disp=new Array(ON.length);
for(var i=0;i<ON.length;i++){
var o=ON[i]||[0,0,0];
var n=absNodes[i]||o;
disp[i]=[Number(n[0])-Number(o[0]),Number(n[1])-Number(o[1]),Number(n[2])-Number(o[2])];
}
if(!Object.prototype.hasOwnProperty.call(STATE_NODE_CACHE,sid))STATE_NODE_CACHE[sid]=absNodes;
}
}
STATE_DISP_CACHE[sid]=disp;
return disp;
}
function getStateNodes(sid){
if(!sid)return null;
if(Object.prototype.hasOwnProperty.call(STATE_NODE_CACHE,sid))return STATE_NODE_CACHE[sid];
var payload=getStateNodePayload(sid);
if(!payload)return null;
var parsed=null;
if(payload&&payload.disp_f32_b64!==undefined){
var disp=getStateDisplacements(sid);
if(disp)parsed=buildAbsoluteNodesFromDisp(disp);
}else if(payload&&payload.f32_b64!==undefined){
parsed=decodeNodesF32B64(payload.f32_b64,payload.n_nodes);
}
STATE_NODE_CACHE[sid]=parsed;
return parsed;
}
function ensureVarStateCache(v){
if(!v)return {};
if(!OUT_STATE_CACHE[v])OUT_STATE_CACHE[v]={};
return OUT_STATE_CACHE[v];
}
function normalizeDisplacementComponent(mode){
var m=String(mode||'mag').toLowerCase();
return (m==='x'||m==='y'||m==='z'||m==='mag')?m:'mag';
}
function getCurrentVarDisplayName(){
if(currentVar==='Displacement'){
return DISP_COMPONENT_LABELS[normalizeDisplacementComponent(displacementComponent)]||'Displacement Mag';
}
return currentVar||'Variable';
}
function refreshOutputVariableLabels(){
var label=getCurrentVarDisplayName();
var titleEl=document.getElementById('legend-var-title');
if(titleEl){
titleEl.textContent=label;
var keepSingleLine=(label==='Displacement Mag.');
titleEl.style.fontSize=keepSingleLine?'11px':'13px';
titleEl.style.whiteSpace=keepSingleLine?'nowrap':'normal';
titleEl.style.lineHeight=keepSingleLine?'1.1':'1.2';
}
var clnEl=document.getElementById('cln');
if(clnEl)clnEl.textContent=label;
}
function refreshDisplacementComponentUi(){
var wrap=document.getElementById('disp-component-wrap');
var show=(currentVar==='Displacement');
if(wrap)wrap.style.display=show?'block':'none';
var mode=normalizeDisplacementComponent(displacementComponent);
['mag','x','y','z'].forEach(function(key){
var btn=document.getElementById('disp-comp-'+key);
if(!btn)return;
btn.classList.toggle('active',show&&key===mode);
});
refreshOutputVariableLabels();
}
function setDisplacementComponent(mode){
var nextMode=normalizeDisplacementComponent(mode);
if(nextMode===displacementComponent&&currentVar==='Displacement'){
refreshDisplacementComponentUi();
return;
}
displacementComponent=nextMode;
if(OUT_STATE_CACHE&&OUT_STATE_CACHE.Displacement)OUT_STATE_CACHE.Displacement={};
AD=ensureVarStateCache(currentVar);
legendAutoResetPending=true;
refreshDisplacementComponentUi();
if(currentVar==='Displacement'&&cst){
asc();
document.getElementById('st').textContent='Output component changed to: '+getCurrentVarDisplayName();
}else if(currentVar==='Displacement'){
document.getElementById('st').textContent='Output changed to: '+getCurrentVarDisplayName()+' - Select an increment';
}
}
function normalizeExtrapolationMethod(mode){
var m=String(mode||'linear').toLowerCase();
return (m==='translate'||m==='average'||m==='linear')?m:'linear';
}
function normalizeNodalAveragingMode(mode){
return String(mode||'off').toLowerCase()==='on'?'on':'off';
}
function getExtrapolationStandardPreset(name){
if(name===undefined||name===null)return null;
var key=String(name);
return Object.prototype.hasOwnProperty.call(EXTRAPOLATION_STANDARD_PRESET_MAP,key)?EXTRAPOLATION_STANDARD_PRESET_MAP[key]:null;
}
function populateExtrapolationStandardOptions(){
var sel=document.getElementById('legend-extrap-standard');
if(!sel||sel.dataset.loaded==='1')return;
var html=['<option value="">Custom / Manual</option>'];
EXTRAPOLATION_STANDARD_PRESETS.forEach(function(p){
if(!p||!p.name)return;
html.push('<option value="'+p.name+'">'+p.name+'</option>');
});
sel.innerHTML=html.join('');
sel.dataset.loaded='1';
}
function normalizeExtrapolationStandardPresetName(name,method,nodalAvg){
if(name===undefined||name===null||String(name).trim()==='')return '';
var preset=getExtrapolationStandardPreset(name);
if(!preset)return '';
if(preset.method&&normalizeExtrapolationMethod(preset.method)!==normalizeExtrapolationMethod(method))return '';
if(preset.avg&&normalizeNodalAveragingMode(preset.avg)!==normalizeNodalAveragingMode(nodalAvg))return '';
return String(preset.name);
}
function getPendingExtrapolationStandardPreset(){
var sel=document.getElementById('legend-extrap-standard');
if(sel&&sel.value)return getExtrapolationStandardPreset(sel.value);
return getExtrapolationStandardPreset(extrapolationStandardPresetName);
}
function getPendingExtrapolationNodalAveraging(){
var avgEl=document.getElementById('legend-extrap-nodal-avg');
return normalizeNodalAveragingMode(avgEl?avgEl.value:extrapolationNodalAveraging);
}
function refreshExtrapolationStandardInfo(){
var infoEl=document.getElementById('legend-extrap-standard-info');
if(!infoEl)return;
var preset=getPendingExtrapolationStandardPreset();
if(!preset){
infoEl.textContent='Select a visualization standard to load the mapped Mentat extrapolation settings from CMO_031_C.pdf.';
return;
}
infoEl.textContent=preset.info||String(preset.name||'');
}
function syncExtrapolationStandardUiFromState(){
populateExtrapolationStandardOptions();
var sel=document.getElementById('legend-extrap-standard');
if(sel)sel.value=normalizeExtrapolationStandardPresetName(extrapolationStandardPresetName,extrapolationMethod,extrapolationNodalAveraging);
refreshExtrapolationStandardInfo();
}
function onExtrapolationStandardPresetInput(){
populateExtrapolationStandardOptions();
var sel=document.getElementById('legend-extrap-standard');
var preset=sel?getExtrapolationStandardPreset(sel.value):null;
var methEl=document.getElementById('legend-extrap-method');
var avgEl=document.getElementById('legend-extrap-nodal-avg');
if(preset){
if(preset.method&&methEl)methEl.value=normalizeExtrapolationMethod(preset.method);
if(preset.avg&&avgEl)avgEl.value=normalizeNodalAveragingMode(preset.avg);
}
refreshExtrapolationStandardInfo();
var noteEl=document.getElementById('legend-extrap-note');
if(noteEl)noteEl.textContent=getExtrapolationDialogNoteText();
}
function onExtrapolationManualSettingInput(){
populateExtrapolationStandardOptions();
var sel=document.getElementById('legend-extrap-standard');
if(!sel){
refreshExtrapolationStandardInfo();
return;
}
var preset=getExtrapolationStandardPreset(sel.value);
var methEl=document.getElementById('legend-extrap-method');
var avgEl=document.getElementById('legend-extrap-nodal-avg');
if(preset){
if((preset.method&&normalizeExtrapolationMethod(methEl?methEl.value:'linear')!==normalizeExtrapolationMethod(preset.method))||
   (preset.avg&&normalizeNodalAveragingMode(avgEl?avgEl.value:'off')!==normalizeNodalAveragingMode(preset.avg))){
sel.value='';
}
}
refreshExtrapolationStandardInfo();
var noteEl=document.getElementById('legend-extrap-note');
if(noteEl)noteEl.textContent=getExtrapolationDialogNoteText();
}
function extrapolationMethodLabel(mode){
var m=normalizeExtrapolationMethod(mode);
if(m==='translate')return 'Translate';
if(m==='average')return 'Average';
return 'Linear';
}
function isElementBasedVarForExtrapolation(varName){
var v=(varName===undefined||varName===null)?currentVar:varName;
return (VAR_LOCS[v]||'node')==='element';
}
function isElementLocalContourMode(){
return !centroidMode&&CENTROID_EXPORTED&&isElementBasedVarForExtrapolation(currentVar)&&normalizeNodalAveragingMode(extrapolationNodalAveraging)==='off';
}
function clearPinnedNodesOnly(){
if(pinnedNodes.length===0)return;
pinnedMarkers.forEach(function(m){sc.remove(m);});
pinnedLabels.forEach(function(el){if(el.parentNode)el.parentNode.removeChild(el);});
pinnedNodes=[];pinnedMarkers=[];pinnedLabels=[];
showTableFormIfMultiple();
}
function refreshValueLookupHint(){
var hint=document.getElementById('val-lookup-hint');
if(!hint)return;
if(isElementLocalContourMode())hint.textContent='Enter element IDs (e.g. 1,5,12)';
else hint.textContent='Enter node IDs, or E1,E5 for elements';
}
function refreshCentroidInfoText(){
var ci=document.getElementById('centroid-info');
if(!ci)return;
if(!CENTROID_EXPORTED||VIEWER_MODE==='harmonic'){
ci.textContent='(not exported)';
return;
}
if(centroidMode){
ci.textContent=isElementBasedVarForExtrapolation(currentVar)?'(element values)':'(averaged nodal values)';
return;
}
if(isElementBasedVarForExtrapolation(currentVar)){
ci.textContent=isElementLocalContourMode()?'(element-local contour)':'(shared-node contour)';
return;
}
ci.textContent='(native nodal contour)';
}
function getExtrapolationSummaryText(){
var tail='Native nodal contour';
if(isElementBasedVarForExtrapolation(currentVar))tail=isElementLocalContourMode()?'Element-local contour':'Shared-node contour';
return extrapolationMethodLabel(extrapolationMethod)+' | Nodal Avg '+(normalizeNodalAveragingMode(extrapolationNodalAveraging)==='on'?'On':'Off')+' | '+tail;
}
function getLegendDataSourceInfo(){
if(isElementLocalContourMode())return ' (element-local contour)';
if(isElementBasedVarForExtrapolation(currentVar))return ' (shared-node contour)';
return '';
}
function getExtrapolationDialogNoteText(){
var preset=getPendingExtrapolationStandardPreset();
if(!isElementBasedVarForExtrapolation(currentVar)){
var txt='The current variable is already stored as nodal data in this VMAP. Mentat extrapolation controls are shown for parity, but the displayed contour already comes from nodal values.';
if(preset&&(!preset.method||!preset.avg))txt+=' The selected visualization standard does not list explicit Extrapolation Method and Nodal Averaging values in CMO_031_C_3D_VIEWER.docx.';
return txt;
}
if(!CENTROID_EXPORTED){
var txt2='Element-local extrapolation display needs per-element data in the HTML. Regenerate the viewer with extrapolation element data enabled.';
if(preset&&(!preset.method||!preset.avg))txt2+=' The selected visualization standard does not list explicit Extrapolation Method and Nodal Averaging values in CMO_031_C_3D_VIEWER.docx.';
return txt2;
}
if(getPendingExtrapolationNodalAveraging()==='off'){
var txt3='Marc Mentat offers Linear, Translate and Average together with Nodal Averaging On/Off. In this VMAP export the viewer has one scalar per element here, so with Nodal Averaging Off it shows an element-local contour.';
if(preset&&(!preset.method||!preset.avg))txt3+=' The selected visualization standard does not list explicit Extrapolation Method and Nodal Averaging values in CMO_031_C_3D_VIEWER.docx.';
return txt3;
}
var txt4='Marc Mentat offers Linear, Translate and Average together with Nodal Averaging On/Off. With this VMAP payload, the strongest visible change is the Nodal Averaging toggle; Linear, Translate and Average can become visually equivalent without element corner or integration-point values.';
if(preset&&(!preset.method||!preset.avg))txt4+=' The selected visualization standard does not list explicit Extrapolation Method and Nodal Averaging values in CMO_031_C_3D_VIEWER.docx.';
return txt4;
}
function refreshExtrapolationSummary(){
var sumEl=document.getElementById('legend-extrap-summary');
if(sumEl)sumEl.textContent=getExtrapolationSummaryText();
var methEl=document.getElementById('legend-extrap-method');
if(methEl)methEl.value=normalizeExtrapolationMethod(extrapolationMethod);
var avgEl=document.getElementById('legend-extrap-nodal-avg');
if(avgEl)avgEl.value=normalizeNodalAveragingMode(extrapolationNodalAveraging);
syncExtrapolationStandardUiFromState();
var noteEl=document.getElementById('legend-extrap-note');
if(noteEl)noteEl.textContent=getExtrapolationDialogNoteText();
refreshValueLookupHint();
refreshCentroidInfoText();
}
function openExtrapolationDialog(){
refreshExtrapolationSummary();
var ov=document.getElementById('legend-extrapolation-overlay');
if(ov)ov.style.display='flex';
}
function closeExtrapolationDialog(){
var ov=document.getElementById('legend-extrapolation-overlay');
if(ov)ov.style.display='none';
}
function applyExtrapolationSettings(method,nodalAvg,opts){
opts=opts||{};
var nextMethod=normalizeExtrapolationMethod(method);
var nextAvg=normalizeNodalAveragingMode(nodalAvg);
var nextPresetName=normalizeExtrapolationStandardPresetName(
opts.standardPresetName!==undefined?opts.standardPresetName:extrapolationStandardPresetName,
nextMethod,
nextAvg
);
var prevElementDisplay=centroidMode||isElementLocalContourMode();
var nextElementDisplay=centroidMode||(CENTROID_EXPORTED&&isElementBasedVarForExtrapolation(currentVar)&&nextAvg==='off');
var changed=(extrapolationMethod!==nextMethod)||(extrapolationNodalAveraging!==nextAvg);
extrapolationMethod=nextMethod;
extrapolationNodalAveraging=nextAvg;
extrapolationStandardPresetName=nextPresetName;
if(prevElementDisplay!==nextElementDisplay){
hideValueTooltip();
lastValueTooltipInfo=null;
hoveredElemIdx=-1;
if(highlightSphere)highlightSphere.visible=false;
if(showValues||pinnedNodes.length>0||pinnedElems.length>0||tableFormVisible)clearValuePinsAndTable();
}
if(isElementLocalContourMode())clearPinnedNodesOnly();
refreshExtrapolationSummary();
if(cst&&AD[cst]){
legendAutoResetPending=true;
ucr(AD[cst]);
rebuildCurrentMeshColors();
if(pinnedNodes.length>0||pinnedElems.length>0)updatePinnedValues();
updatePinnedPositions();
}
if(!opts.keepDialog)closeExtrapolationDialog();
if(!opts.silent&&changed){
document.getElementById('st').textContent='Extrapolation: '+getExtrapolationSummaryText();
}
}
function applyExtrapolationDialog(){
var methEl=document.getElementById('legend-extrap-method');
var avgEl=document.getElementById('legend-extrap-nodal-avg');
var presetEl=document.getElementById('legend-extrap-standard');
applyExtrapolationSettings(methEl?methEl.value:'linear',avgEl?avgEl.value:'off',{standardPresetName:presetEl?presetEl.value:''});
}
function resetExtrapolationSettings(){
applyExtrapolationSettings('linear','off',{keepDialog:true,standardPresetName:''});
refreshExtrapolationSummary();
}
function isVirtualDisplacementVar(v){
return !!(VIRTUAL_DISPLACEMENT_OUTPUT&&v==='Displacement'&&(!OUT_STATE_INDEX||!OUT_STATE_INDEX[v]||OUT_STATE_INDEX[v].length===0));
}
function getVarStateIds(v){
if(v==='Displacement'){
var dispIds=[];
for(var di=0;di<SL.length;di++){
var ds=SL[di];
if(!ds||ds.id===undefined||ds.id===null)continue;
if(!STATE_NODE_TAG_MAP||!STATE_NODE_TAG_MAP[ds.id])continue;
dispIds.push(ds.id);
}
if(dispIds.length>0)return dispIds;
}
if(isVirtualDisplacementVar(v)){
var ids=[];
for(var i=0;i<SL.length;i++){
var s=SL[i];
if(!s||s.id===undefined||s.id===null)continue;
if(!STATE_NODE_TAG_MAP||!STATE_NODE_TAG_MAP[s.id])continue;
ids.push(s.id);
}
return ids;
}
if(!v||!OUT_STATE_INDEX||!OUT_STATE_INDEX[v])return [];
return OUT_STATE_INDEX[v];
}
function getStateMetaEntry(sid){
if(sid===undefined||sid===null)return null;
var sidTxt=String(sid);
for(var i=0;i<SL.length;i++){
var s=SL[i];
if(s&&String(s.id)===sidTxt)return s;
}
return null;
}
function formatLegendStateTime(v){
var num=Number(v);
if(!isFinite(num))return '-';
return num.toFixed(5).replace(/\.?0+$/,'');
}
function updateLegendStateMeta(info){
var incEl=document.getElementById('legend-inc-line');
var timeEl=document.getElementById('legend-time-line');
if(!incEl||!timeEl)return;
if(!info){
incEl.textContent='Inc: -';
timeEl.textContent='Time: -';
return;
}
var incVal='-';
if(info.increment!==undefined&&info.increment!==null&&String(info.increment)!==''){
incVal=String(info.increment);
}
var timeTxt=formatLegendStateTime(info.time);
incEl.textContent='Inc: '+incVal;
timeEl.textContent='Time: '+timeTxt;
}
function buildVirtualDisplacementStateData(sid){
var disp=getStateDisplacements(sid);
if(!disp||!ON||ON.length===0)return null;
var mode=normalizeDisplacementComponent(displacementComponent);
var vals=new Array(ON.length);
var vmin=Infinity,vmax=-Infinity;
for(var i=0;i<ON.length;i++){
var d=disp[i]||[0,0,0];
var dx=Number(d[0]);
var dy=Number(d[1]);
var dz=Number(d[2]);
if(!isFinite(dx))dx=0;
if(!isFinite(dy))dy=0;
if(!isFinite(dz))dz=0;
var val=0;
if(mode==='x')val=dx;
else if(mode==='y')val=dy;
else if(mode==='z')val=dz;
else{
val=Math.sqrt(dx*dx+dy*dy+dz*dz);
if(!isFinite(val))val=0;
}
if(!isFinite(val))val=0;
vals[i]=val;
if(val<vmin)vmin=val;
if(val>vmax)vmax=val;
}
if(!isFinite(vmin)||!isFinite(vmax)){
vmin=0;
vmax=1;
}
var colorMax=vmax;
if(Math.abs(colorMax-vmin)<1e-10)colorMax=vmin+1.0;
var inv=1/Math.max(1e-30,colorMax-vmin);
var colors=new Array(vals.length);
for(var mi=0;mi<vals.length;mi++){
var nv=(vals[mi]-vmin)*inv;
if(!isFinite(nv))nv=0;
colors[mi]=Math.max(0,Math.min(1,nv));
}
var meta=getStateMetaEntry(sid)||{};
var timeVal=Number(meta.time);
if(!isFinite(timeVal))timeVal=0;
var incVal=Number(meta.increment);
if(!isFinite(incVal))incVal=0;
var freqVal=null;
if(meta.frequency!==undefined&&meta.frequency!==null){
var fNum=Number(meta.frequency);
if(isFinite(fNum))freqVal=fNum;
}
var out={
time:timeVal,
increment:incVal,
frequency:freqVal,
title:(meta.title!==undefined&&meta.title!==null)?String(meta.title):'',
colors:colors,
color_min:vmin,
color_max:colorMax
};
if(CENTROID_EXPORTED){
ensureElemConnectivityMaps();
var centroidVals=[];
var cvmin=Infinity,cvmax=-Infinity;
if(elemNodesMap&&elemNodesMap.length>0){
centroidVals=new Array(elemNodesMap.length);
for(var ei=0;ei<elemNodesMap.length;ei++){
var nodeList=elemNodesMap[ei];
var sum=0,count=0;
if(nodeList&&nodeList.length){
for(var ni=0;ni<nodeList.length;ni++){
var idx=nodeList[ni];
if(idx===undefined||idx===null||idx<0||idx>=vals.length)continue;
var mv=vals[idx];
if(!isFinite(mv))continue;
sum+=mv;
count++;
}
}
var cv=(count>0)?(sum/count):0;
centroidVals[ei]=cv;
if(cv<cvmin)cvmin=cv;
if(cv>cvmax)cvmax=cv;
}
}
if(!isFinite(cvmin)||!isFinite(cvmax)){
cvmin=0;
cvmax=1;
}
var centroidMax=cvmax;
if(Math.abs(centroidMax-cvmin)<1e-10)centroidMax=cvmin+1.0;
var cInv=1/Math.max(1e-30,centroidMax-cvmin);
var centroidColors=new Array(centroidVals.length);
for(var ci=0;ci<centroidVals.length;ci++){
var cnv=(centroidVals[ci]-cvmin)*cInv;
if(!isFinite(cnv))cnv=0;
centroidColors[ci]=Math.max(0,Math.min(1,cnv));
}
out.centroid_colors=centroidColors;
out.centroid_min=cvmin;
out.centroid_max=centroidMax;
}
return out;
}
function hasVarStateData(v){
return getVarStateIds(v).length>0;
}
function hasStateData(v,sid){
if(!v||!sid)return false;
var arr=getVarStateIds(v);
var sidTxt=String(sid);
for(var i=0;i<arr.length;i++){
if(String(arr[i])===sidTxt)return true;
}
return false;
}
function getStateData(v,sid){
if(!v||!sid)return null;
var cache=ensureVarStateCache(v);
if(cache[sid])return cache[sid];
if(v==='Displacement'){
try{
var virtualData=buildVirtualDisplacementStateData(sid);
if(virtualData){
cache[sid]=virtualData;
return virtualData;
}
}catch(e){
console.error('Virtual displacement build failed for '+sid+':',e);
}
return null;
}
var map=OUT_STATE_TAG_MAP[v];
if(!map||!map[sid])return null;
var txt=readChunkedJsonTag(map[sid]);
if(!txt)return null;
try{
var parsed=JSON.parse(txt);
if(parsed&&parsed.colors===undefined&&parsed.colors_i16_b64!==undefined){
parsed.colors=decodeNormI16B64(parsed.colors_i16_b64,parsed.color_count);
}
if(parsed&&parsed.centroid_colors===undefined&&parsed.centroid_i16_b64!==undefined){
parsed.centroid_colors=decodeNormI16B64(parsed.centroid_i16_b64,parsed.centroid_count);
}
cache[sid]=parsed;
return parsed;
}catch(e){
console.error('State data parse failed for '+v+' / '+sid+':',e);
return null;
}
}
let AD=ensureVarStateCache(''' + json.dumps(default_var if default_var else "", separators=(',', ':')) + ''');
const CT=''' + json.dumps(center, separators=(',', ':')) + ''';
const B=''' + str(bbox_size) + ''';
const IS="''' + (state_name or "") + '''";
const HTMLNAME="''' + os.path.splitext(os.path.basename(output_file))[0] + '''";
const VIEWER_MODE="''' + viewer_mode_label + '''";
const CENTROID_EXPORTED=''' + ('true' if export_centroid else 'false') + ''';
const ALL_EDGES_EXPORTED=''' + ('true' if export_all_edges else 'false') + ''';
const EXTERNAL_SURFACE_ONLY=''' + ('true' if harmonic_mode else 'false') + ''';
const DEFAULT_SCALE_FACTOR=''' + harmonic_initial_scale_text + ''';
const BUILD_REV="6.1.4-floating-groupvis-2026-04-03";
const LOGO_URI="''' + (logo_data_uri if logo_data_uri else "") + '''";
var fileTitleOverlayEl=document.getElementById('file-title-overlay');
if(fileTitleOverlayEl)fileTitleOverlayEl.textContent=HTMLNAME+'.html';
const THREE_MISSING=(typeof THREE==='undefined');
if(THREE_MISSING){
var stEl=document.getElementById('st');
if(stEl)stEl.textContent='THREE.js failed to load. Check internet/proxy access to CDN.';
}
let cs=DEFAULT_SCALE_FACTOR,cst=null,cn=ON.slice(),cvEl=null,currentVar="''' + (default_var if default_var else '') + '''";
let sc,ca,caPersp,caOrtho,re,ms,eg,axHelper,dr=false,pn=false,mz=false,pm={x:0,y:0},ir=false,isPerspective=false;
let ctrlRotAxis=null;
let uMs=null,uEg=null,showUndeformed=false;
let undContourMode=false;
let showValues=false,curColors=null;
let centroidMode=false,centroidRawColors=null,centroidDataMin=0,centroidDataMax=1;
var logoImg=null;
if(LOGO_URI){logoImg=new Image();logoImg.src=LOGO_URI;}
var visibleFaceElemIdx=[];
var raycaster=new THREE.Raycaster(),mouseNDC=new THREE.Vector2();
let highlightSphere=null,highlightedNodeIdx=-1;
let featureEg=null,edgeMode='feature';
let noContour=false;
const MAX_FULL_EDGES_FACE_COUNT=180000;
let autoEdgeFallbackNotified=false;
let measMode='off',measDraft=null,measGroups=[],measLabelCounter=0,measureIdSeed=1,measDialogRemovalId=null;
let measHighlightSphere=null;
let pinnedNodes=[],pinnedMarkers=[],pinnedLabels=[];
let pinnedElems=[],pinnedElemMarkers=[],pinnedElemLabels=[],pinnedElemFaces=[];
let dialogBoxes=[],dialogPreviewEl=null,dialogMode=false,dialogAddArmed=false,dialogConnectPendingId=null;
let dialogActiveId=null,dialogEditPopupEl=null,dialogEditBoxId=null;
let dialogFontPopupEl=null,dialogFontBoxId=null;
let dialogFontSize=11;
let tableFormFontSize=10;
let dialogIdSeed=1,dialogDrag=null;
let materialVisibilityDrag=null,materialVisibilityWindowPos={left:null,top:null};
let mouseDownPos={x:0,y:0};
let visibleFaces=[];
let visibleElemMap=Object.create(null),visibleNodeMap=Object.create(null),visibleElemFaceMap=Object.create(null);
let hiddenElemMap=Object.create(null);
let groupVisibilityState=[];
let hideElemMode=false,hideAllConnectedMode=false,hideSelStart=null,hideSelEnd=null,hideSelDiv=null;
let hideHoverElemIdx=-1,hideHoverEdges=null;
let elemNodesMap=null,nodeElemsMap=null;
let hideRefreshPending=false,hideRefreshMsg='';
let remapCacheSrc=null,remapCacheDMin=0,remapCacheDMax=0,remapCacheUMin=0,remapCacheUMax=0,remapCacheOut=null;
let noContourElemGroup=null,noContourGroupSizes=[],noContourGroupColors=[];
const NO_CONTOUR_GROUP_BASE=['#1E88E5','#43A047','#FB8C00','#8E24AA','#D81B60','#00897B','#6D4C41','#3949AB','#7CB342','#EF6C00'];
let legendVisibilityRebuildGuard=false;
let meshNodesRef=ON;
let hoveredElemIdx=-1;
let lastValueTooltipInfo=null,valTooltipInvalidUntilMove=false,valTooltipInvalidAnchor={x:0,y:0};
let legendMaxMode=false,legendMinMode=false;
let legendMaxTarget=null,legendMinTarget=null;
let legendMaxMarker=null,legendMinMarker=null;
let legendMaxLabel=null,legendMinLabel=null;
let cutRebuildTimer=null;
let camDist=B*3,tg=new THREE.Vector3(CT[0],CT[1],CT[2]);
let camQuat=new THREE.Quaternion();
let animInterval=null,animIndex=0,animDirection=1,animRangeStart=0,animRangeEnd=0;
let animMode='none',animPaused=false,animStaticSwing=false,animStepAccum=0;
let animHarmonic=(VIEWER_MODE==='harmonic'),animSwing=false,harmonicPhase=0,harmonicBaseStateId=null,harmonicFrameCount=48;
let harmonicPerfActive=false,harmonicPerfPrevEdgeMode=null,harmonicPerfLastTableUpdateMs=0;
let harmonicLegendSyncDone=false;
let zoomBoxMode=false,zoomBoxStart=null,zoomBoxEnd=null,zoomBoxDiv=null;
let curMin=CR[0],curMax=CR[1];
let legFontSize=14;
let valueInfoFontSize=12;
let dynamicLegend=false;
let legendAutoResetPending=false;
let dataMin=CR[0],dataMax=CR[1];
let discreteMode=true,N_DISC=12;
let legendValueFormat='float',legendFloatDecimals=3;
let legendColorMapId='1';
let extrapolationMethod='linear';
let extrapolationNodalAveraging='off';
let extrapolationStandardPresetName='';
const DISP_COMPONENT_LABELS={mag:'Displacement Mag.',x:'Displacement X',y:'Displacement Y',z:'Displacement Z'};
let displacementComponent='mag';
let legendCustomValues=null,legendCustomColors=null;
let legendEditMode=false;
let legendEditFocusValue=-1,legendEditFocusColor=-1;
let legendOutsideDblInit=false;
let rawColors=null;
let gifWorkerUrl=null;
let axScene,axCamera,showAxes=true;
let cutPlanes={x:{on:false,pos:50,dir:'+'},y:{on:false,pos:50,dir:'+'},z:{on:false,pos:50,dir:'+'},rotation:{on:false,axis:'x',angle:0,dir:'+',angle2On:false,angle2:0,dir2:'+',refA:50,refB:50,hidePlane:false}};
let meshBBox={xmin:0,xmax:1,ymin:0,ymax:1,zmin:0,zmax:1};
let axisCutPlaneMeshes={x:null,y:null,z:null},axisCutPlaneEdges={x:null,y:null,z:null};
let rotationCutLine=null,rotationCutPlaneMesh=null,rotationCutPlaneEdges=null,rotationCutPlaneMesh2=null,rotationCutPlaneEdges2=null;
let cutSectionProjectionOn=false,cutSectionLines=null,cutSectionLinesWide=null,cutSectionSurface=null;
let vrfEnabled=false,vrfLo=0,vrfHi=1;
let xyAppliedRange={xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'};
let xySecAppliedRange={ymin:'auto',ymax:'auto'};
const AX_SIZE=220;
const AX_YOFF=35;
let xyPlotVisible=false;
const CURVE_COLORS=['#2196F3','#F44336','#4CAF50','#FF9800','#9C27B0','#00BCD4','#795548','#E91E63','#607D8B','#CDDC39'];
let saveFileBaseHtml='';
let xyCurves=[];
let xySelectedIdx=-1;
let xyEditingIdx=-1;
let xyPinned=[];
let xyAnimIndex=-1;
let xyAnimInfoVisible=true;
let xyTitleFontSize=10;
let xyValuesFontSize=9;
let xyValueFormat='float';
let xyFloatLevels=2;
let xyForecastLastResult=null;
let xyFontPopupInit=false;
let xySelCols={x:false,y:false};
let xyCellSel={active:false,startRow:0,startCol:0,endRow:0,endCol:0};
let xyCellDrag=false;
let xyCellSelInit=false;
let xyCopyHotkeyInit=false;
let tfSelCols={id:false,val:false};
let tfCellSel={active:false,startRow:0,startCol:0,endRow:0,endCol:0};
let tfIdTypeHint={};
let tfCellDrag=false;
let tfCellMoved=false;
let tfHotkeyInit=false;
let tfRowSelIdx=-1;
let tfElemEdgeCache=Object.create(null);
let tfLastExportTableLayout=null;
let xyUserRange={xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'};
var xySecUserRange={ymin:'auto',ymax:'auto'};
var xyZoomDrag=false,xyZoomStart=null,xyZoomEnd=null;
const MAX_RENDER_PIXEL_RATIO=1.0;
const FAST_NORMAL_UPDATE_MS=250;
let hiddenElemRevision=0;
let meshTopologyKey='';
let meshRenderMode='';
let meshVertexNodeIdx=null;
let meshVertexElemIdx=null;
let lastFastNormalUpdateMs=0;
// Sheet system
let xySheets=[{title:'Sheet 1',curves:[],selectedIdx:-1,editingIdx:-1,pinned:[],userRange:{xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'},secUserRange:{ymin:'auto',ymax:'auto'},appliedRange:{xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'},secAppliedRange:{ymin:'auto',ymax:'auto'},axisNames:{xname:'X',yname:'Y',syname:'Y (R)'},plotTitle:'XY Plot'}];
let xyActiveSheet=0;
let sidebarCardDragEl=null,sidebarCardPlaceholder=null,sidebarCardHandleArmedId=null;

function getViewW(){
var pw=xyPlotVisible?Math.floor(window.innerWidth/3):0;
return window.innerWidth-320-pw;
}
function getPlotW(){return xyPlotVisible?Math.floor(window.innerWidth/3):0;}

function getRenderPixelRatio(){
var dpr=window.devicePixelRatio||1;
if(!isFinite(dpr)||dpr<=0)dpr=1;
return Math.min(MAX_RENDER_PIXEL_RATIO,dpr);
}

function bumpHiddenElemRevision(){
hiddenElemRevision++;
}

function captureBaseHtmlForSaveFile(){
try{
var h=document.documentElement.outerHTML||'';
if(!/^<!doctype/i.test(h.trim()))h='<!DOCTYPE html>\\n'+h;
if(h&&h.indexOf('CORE_DATA_TAG_MAP')>=0&&h.indexOf('STATE_NODE_TAG_MAP')>=0){
saveFileBaseHtml=h;
}
}catch(e){}
}

function getRenderNodes(){
return undContourMode?ON:cn;
}

function getDisplayNodes(){
return (meshNodesRef&&meshNodesRef.length)?meshNodesRef:getRenderNodes();
}

function isElemHidden(elemIdx){
return !!hiddenElemMap[elemIdx]||isElemHiddenByConnectedGroup(elemIdx);
}

function isElemVisibleNow(elemIdx){
if(elemIdx===undefined||elemIdx===null||elemIdx<0)return false;
return !!visibleElemMap[elemIdx];
}

function isNodeVisibleNow(nodeIdx){
if(nodeIdx===undefined||nodeIdx===null||nodeIdx<0)return false;
return !!visibleNodeMap[nodeIdx];
}

function countHiddenElements(){
var n=0;
var total=Math.max(EIDS.length,EMM.length,noContourElemGroup?noContourElemGroup.length:0);
for(var i=0;i<total;i++){if(isElemHidden(i))n++;}
return n;
}

function ensureConnectedGroupVisibilityState(){
ensureNoContourGroups();
var len=noContourGroupSizes?noContourGroupSizes.length:0;
if(!Array.isArray(groupVisibilityState))groupVisibilityState=[];
if(groupVisibilityState.length===len)return;
var next=new Array(len);
for(var i=0;i<len;i++)next[i]=(groupVisibilityState[i]!==false);
groupVisibilityState=next;
}

function isElemHiddenByConnectedGroup(elemIdx){
if(!noContourElemGroup||!Array.isArray(groupVisibilityState)||groupVisibilityState.length===0)return false;
if(elemIdx===undefined||elemIdx===null||elemIdx<0||elemIdx>=noContourElemGroup.length)return false;
var gid=noContourElemGroup[elemIdx];
if(gid===undefined||gid===null||gid<0||gid>=groupVisibilityState.length)return false;
return groupVisibilityState[gid]===false;
}

function renderMaterialVisibilityDialog(){
var titleEl=document.getElementById('material-visibility-title');
var subEl=document.getElementById('material-visibility-sub');
var body=document.getElementById('material-visibility-body');
if(!titleEl||!subEl||!body)return;
ensureConnectedGroupVisibilityState();
titleEl.textContent='Connected Groups';
subEl.innerHTML='Uses the same connected groups identified in <b>No contour</b>. Hide a group to hide all its elements in the mesh.';
if(!noContourGroupSizes||noContourGroupSizes.length===0){
body.innerHTML='<div class="matvis-empty">No connected groups are available for this mesh.</div>';
return;
}
var html='';
for(var i=0;i<noContourGroupSizes.length;i++){
var visible=(groupVisibilityState[i]!==false);
var color=(i<noContourGroupColors.length)?noContourGroupColors[i]:ncDefaultColor(i);
    html+='<div class="matvis-row'+(visible?'':' matvis-hidden')+'">'+
    '<div>'+
    '<div class="matvis-name"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:'+color+';margin-right:6px;vertical-align:middle;border:1px solid rgba(0,0,0,0.18)"></span>Connected Group '+(i+1)+'</div>'+
    '<div class="matvis-count">'+noContourGroupSizes[i]+' element(s)</div>'+
    '</div>'+
    '<div class="matvis-actions">'+
    '<button class="matvis-btn matvis-btn-show'+(visible?' active':'')+'" onclick="setConnectedGroupVisibility('+i+',true)">Show</button>'+
    '<button class="matvis-btn matvis-btn-hide'+(visible?'':' active')+'" onclick="setConnectedGroupVisibility('+i+',false)">Hide</button>'+
    '</div>'+
    '</div>';
}
body.innerHTML=html;
}

function refreshMaterialVisibilityDialog(){
var overlay=document.getElementById('material-visibility-overlay');
if(overlay&&overlay.style.display==='block')renderMaterialVisibilityDialog();
}

function clampMaterialVisibilityWindowPos(left,top){
var win=document.getElementById('material-visibility-window');
var width=win?(win.offsetWidth||560):560;
var height=win?(win.offsetHeight||420):420;
var maxLeft=Math.max(8,window.innerWidth-width-8);
var maxTop=Math.max(8,window.innerHeight-height-8);
var outLeft=isFinite(left)?left:16;
var outTop=isFinite(top)?top:16;
if(outLeft<8)outLeft=8;
if(outTop<8)outTop=8;
if(outLeft>maxLeft)outLeft=maxLeft;
if(outTop>maxTop)outTop=maxTop;
return {left:outLeft,top:outTop};
}

function applyMaterialVisibilityWindowPos(){
var win=document.getElementById('material-visibility-window');
if(!win)return;
var pos=clampMaterialVisibilityWindowPos(materialVisibilityWindowPos.left,materialVisibilityWindowPos.top);
materialVisibilityWindowPos.left=pos.left;
materialVisibilityWindowPos.top=pos.top;
win.style.left=pos.left+'px';
win.style.top=pos.top+'px';
}

function ensureMaterialVisibilityWindowPos(){
if(isFinite(materialVisibilityWindowPos.left)&&isFinite(materialVisibilityWindowPos.top))return;
var win=document.getElementById('material-visibility-window');
var width=win?(win.offsetWidth||560):560;
materialVisibilityWindowPos.left=Math.max(16,Math.round(window.innerWidth-width-26));
materialVisibilityWindowPos.top=88;
	materialVisibilityWindowPos=clampMaterialVisibilityWindowPos(materialVisibilityWindowPos.left,materialVisibilityWindowPos.top);
}

function openMaterialVisibilityDialog(){
renderMaterialVisibilityDialog();
var overlay=document.getElementById('material-visibility-overlay');
if(overlay)overlay.style.display='block';
ensureMaterialVisibilityWindowPos();
applyMaterialVisibilityWindowPos();
}

function closeMaterialVisibilityDialog(){
var overlay=document.getElementById('material-visibility-overlay');
if(overlay)overlay.style.display='none';
materialVisibilityDrag=null;
}

function setConnectedGroupVisibility(groupIdx,visible){
ensureConnectedGroupVisibilityState();
if(groupIdx===undefined||groupIdx===null||groupIdx<0||groupIdx>=groupVisibilityState.length)return;
var nextVisible=!!visible;
if(groupVisibilityState[groupIdx]===nextVisible){
refreshMaterialVisibilityDialog();
return;
}
groupVisibilityState[groupIdx]=nextVisible;
bumpHiddenElemRevision();
markValueTooltipHiddenByElement();
refreshMaterialVisibilityDialog();
refreshAfterHideElementsChange('Connected Group '+(groupIdx+1)+' '+(nextVisible?'shown':'hidden')+' ('+noContourGroupSizes[groupIdx]+' element(s)) - total hidden: '+countHiddenElements(),{defer:true});
}

function showAllVisibilityCategories(){
ensureConnectedGroupVisibilityState();
if(!groupVisibilityState.length)return;
var changed=false;
for(var i=0;i<groupVisibilityState.length;i++){
if(groupVisibilityState[i]===false){groupVisibilityState[i]=true;changed=true;}
}
refreshMaterialVisibilityDialog();
if(!changed)return;
bumpHiddenElemRevision();
refreshAfterHideElementsChange('All connected groups shown - total hidden: '+countHiddenElements(),{defer:true});
}

function hideValueTooltip(resetInfo){
var tt=document.getElementById('val-tooltip');
if(tt){
tt.style.display='none';
tt.innerHTML='';
tt.style.background='rgba(0,0,0,0.8)';
tt.style.border='none';
tt.style.whiteSpace='nowrap';
tt.style.color='#fff';
tt.style.fontSize=valueInfoFontSize+'px';
}
if(resetInfo!==false){
lastValueTooltipInfo=null;
valTooltipInvalidUntilMove=false;
}
}

function showValueTooltip(text,clientX,clientY,meta){
var tt=document.getElementById('val-tooltip');
if(!tt)return;
valTooltipInvalidUntilMove=false;
tt.textContent=text;
tt.style.display='block';
tt.style.left=(clientX+15)+'px';
tt.style.top=(clientY-10)+'px';
tt.style.fontSize=valueInfoFontSize+'px';
tt.style.background='rgba(0,0,0,0.8)';
tt.style.border='none';
tt.style.whiteSpace='nowrap';
tt.style.color='#fff';
lastValueTooltipInfo={
text:text,
x:clientX,
y:clientY,
kind:(meta&&meta.kind)?meta.kind:'node',
elemIdx:(meta&&meta.elemIdx!==undefined&&meta.elemIdx!==null)?meta.elemIdx:null,
rawValue:(meta&&meta.rawValue!==undefined&&meta.rawValue!==null)?meta.rawValue:null,
idText:(meta&&meta.idText!==undefined&&meta.idText!==null)?String(meta.idText):''
};
}

function markValueTooltipHiddenByElement(){
if(!showValues||!lastValueTooltipInfo)return;
var elemIdx=(lastValueTooltipInfo.elemIdx!==undefined&&lastValueTooltipInfo.elemIdx!==null)?lastValueTooltipInfo.elemIdx:-1;
if(elemIdx<0||!isElemHidden(elemIdx))return;
var tt=document.getElementById('val-tooltip');
if(!tt||tt.style.display==='none')return;
tt.innerHTML='<div style="text-decoration:line-through;text-decoration-color:#FF3B30;text-decoration-thickness:2px;color:#FFE0E0">'+lastValueTooltipInfo.text+'</div><div style="margin-top:2px;color:#FF8A80;font-size:'+Math.max(9,valueInfoFontSize-1)+'px">Hidden element: info no longer valid</div>';
tt.style.display='block';
tt.style.left=(lastValueTooltipInfo.x+15)+'px';
tt.style.top=(lastValueTooltipInfo.y-10)+'px';
tt.style.fontSize=valueInfoFontSize+'px';
tt.style.background='rgba(25,25,25,0.92)';
tt.style.border='1px solid #F44336';
tt.style.whiteSpace='normal';
tt.style.color='#fff';
valTooltipInvalidUntilMove=true;
valTooltipInvalidAnchor={x:lastValueTooltipInfo.x,y:lastValueTooltipInfo.y};
}

function handleInvalidTooltipMove(clientX,clientY){
if(!valTooltipInvalidUntilMove)return false;
var moved=(Math.abs(clientX-valTooltipInvalidAnchor.x)>1)||(Math.abs(clientY-valTooltipInvalidAnchor.y)>1);
if(!moved)return false;
valTooltipInvalidUntilMove=false;
hideValueTooltip();
return true;
}

function refreshLegendExtremeButtons(){
var bMax=document.getElementById('leg-max-mode-btn');
if(bMax){
bMax.textContent=legendMaxMode?'On':'Off';
bMax.style.background=legendMaxMode?'#00C853':'#D32F2F';
bMax.style.color='#fff';
}
var bMin=document.getElementById('leg-min-mode-btn');
if(bMin){
bMin.textContent=legendMinMode?'On':'Off';
bMin.style.background=legendMinMode?'#00C853':'#D32F2F';
bMin.style.color='#fff';
}
}

function removeLegendExtremeVisual(which){
var marker=(which==='max')?legendMaxMarker:legendMinMarker;
var label=(which==='max')?legendMaxLabel:legendMinLabel;
if(marker){
try{if(sc)sc.remove(marker);}catch(e){}
try{
if(marker.geometry)marker.geometry.dispose();
if(marker.material)marker.material.dispose();
}catch(e){}
}
if(label&&label.parentNode)label.parentNode.removeChild(label);
if(which==='max'){legendMaxMarker=null;legendMaxLabel=null;}
else{legendMinMarker=null;legendMinLabel=null;}
}

function removeLegendExtremaVisuals(){
removeLegendExtremeVisual('max');
removeLegendExtremeVisual('min');
}

function getVisibleExtremaTargets(){
var out={max:null,min:null};
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){
var cR=centroidDataMax-centroidDataMin;
if(Math.abs(cR)<1e-30)cR=1;
for(var ek in visibleElemMap){
if(!Object.prototype.hasOwnProperty.call(visibleElemMap,ek)||!visibleElemMap[ek])continue;
var ei=parseInt(ek,10);
if(!isFinite(ei)||ei<0||ei>=centroidRawColors.length)continue;
var cv=centroidRawColors[ei];
if(cv===undefined||cv===null||!isFinite(cv))continue;
var rv=centroidDataMin+cv*cR;
if(!isFinite(rv))continue;
if(!out.max||rv>out.max.value)out.max={type:'elem',idx:ei,value:rv};
if(!out.min||rv<out.min.value)out.min={type:'elem',idx:ei,value:rv};
}
return out;
}
var src=rawColors||curColors;
if(!src)return out;
var srcMin=rawColors?dataMin:curMin;
var srcMax=rawColors?dataMax:curMax;
var sR=srcMax-srcMin;
if(Math.abs(sR)<1e-30)sR=1;
for(var nk in visibleNodeMap){
if(!Object.prototype.hasOwnProperty.call(visibleNodeMap,nk)||!visibleNodeMap[nk])continue;
var ni=parseInt(nk,10);
if(!isFinite(ni)||ni<0||ni>=src.length)continue;
var nv=src[ni];
if(nv===undefined||nv===null||!isFinite(nv))continue;
var rvN=srcMin+nv*sR;
if(!isFinite(rvN))continue;
if(!out.max||rvN>out.max.value)out.max={type:'node',idx:ni,value:rvN};
if(!out.min||rvN<out.min.value)out.min={type:'node',idx:ni,value:rvN};
}
return out;
}

function buildLegendExtremeLabelHtml(which,target){
var prefix=(which==='max')?'Max. Value:':'Min. Value:';
var isElem=target&&target.type==='elem';
var rid=isElem?(EIDS[target.idx]!==undefined?EIDS[target.idx]:target.idx):(NIDS[target.idx]!==undefined?NIDS[target.idx]:target.idx);
var idPrefix=isElem?'E':'N';
var cls=isElem?'pn-elem':'pn-node';
return '<span style="color:#FFCDD2;font-size:0.85em">'+prefix+'</span><br><span class="'+cls+'">'+idPrefix+rid+'</span> <span class="pn-val">'+formatLegendDrivenValue(target.value,'N/A')+'</span>';
}

function ensureLegendExtremeVisual(which){
var target=(which==='max')?legendMaxTarget:legendMinTarget;
if(!target){removeLegendExtremeVisual(which);return;}
var marker=(which==='max')?legendMaxMarker:legendMinMarker;
if(!marker){
var sz=B*0.003;
var geo=new THREE.SphereGeometry(sz,10,10);
var isElem=target.type==='elem';
var mat=new THREE.MeshBasicMaterial({color:isElem?0x66BB6A:0xFFD600,depthTest:false});
marker=new THREE.Mesh(geo,mat);
marker.renderOrder=998;
if(sc)sc.add(marker);
if(which==='max')legendMaxMarker=marker;else legendMinMarker=marker;
}
if(marker&&marker.material&&marker.material.color){
marker.material.color.setHex(target.type==='elem'?0x66BB6A:0xFFD600);
}
var label=(which==='max')?legendMaxLabel:legendMinLabel;
if(!label){
var container=document.getElementById('pinned-container');
if(container){
label=document.createElement('div');
label.className='pinned-label';
container.appendChild(label);
if(which==='max')legendMaxLabel=label;else legendMinLabel=label;
}
}
if(label){
label.innerHTML=buildLegendExtremeLabelHtml(which,target);
label.style.fontSize=valueInfoFontSize+'px';
}
}

function updateLegendExtremePosition(which,cuts){
var modeOn=(which==='max')?legendMaxMode:legendMinMode;
if(!modeOn){removeLegendExtremeVisual(which);return;}
var target=(which==='max')?legendMaxTarget:legendMinTarget;
var marker=(which==='max')?legendMaxMarker:legendMinMarker;
var label=(which==='max')?legendMaxLabel:legendMinLabel;
if(!target||!marker||!label||!cvEl||!ca){removeLegendExtremeVisual(which);return;}
var pos=null,show=true;
if(target.type==='elem'){
if(!isElemVisibleNow(target.idx))show=false;
else{
var ctr=getElemCentroid3D(target.idx);
if(!ctr)show=false;
else pos={x:ctr.x,y:ctr.y,z:ctr.z};
}
}else{
var dispNodes=getDisplayNodes();
if(target.idx<0||target.idx>=dispNodes.length||!isNodeVisibleNow(target.idx))show=false;
else pos={x:dispNodes[target.idx][0],y:dispNodes[target.idx][1],z:dispNodes[target.idx][2]};
}
if(show&&cuts&&cuts.length>0){
show=isPointVisibleByCuts([pos.x,pos.y,pos.z],cuts);
}
if(!show||!pos){
marker.visible=false;
label.style.display='none';
return;
}
marker.position.set(pos.x,pos.y,pos.z);
var rect=cvEl.getBoundingClientRect();
var p3=new THREE.Vector3(pos.x,pos.y,pos.z);
p3.project(ca);
var visibleNow=(p3.z<=1);
marker.visible=visibleNow;
if(!visibleNow){
label.style.display='none';
return;
}
var sx=(p3.x*0.5+0.5)*rect.width+rect.left;
var sy=(-p3.y*0.5+0.5)*rect.height+rect.top;
label.style.display='block';
label.style.left=(sx+12)+'px';
label.style.top=(sy-12)+'px';
}

function updateLegendExtremaPositions(cuts){
if(!legendMaxMode&&!legendMinMode)return;
updateLegendExtremePosition('max',cuts);
updateLegendExtremePosition('min',cuts);
}

function updateLegendExtremaTargets(){
if(!(legendMaxMode||legendMinMode)){
removeLegendExtremaVisuals();
legendMaxTarget=null;
legendMinTarget=null;
return;
}
var ext=getVisibleExtremaTargets();
if(legendMaxMode){
legendMaxTarget=ext.max;
ensureLegendExtremeVisual('max');
}else{
legendMaxTarget=null;
removeLegendExtremeVisual('max');
}
if(legendMinMode){
legendMinTarget=ext.min;
ensureLegendExtremeVisual('min');
}else{
legendMinTarget=null;
removeLegendExtremeVisual('min');
}
}

function tgLegendMaxMode(){
legendMaxMode=!legendMaxMode;
refreshLegendExtremeButtons();
updateLegendExtremaTargets();
if(tableFormVisible)updateTableForm();
}

function tgLegendMinMode(){
legendMinMode=!legendMinMode;
refreshLegendExtremeButtons();
updateLegendExtremaTargets();
if(tableFormVisible)updateTableForm();
}

function updateViewerCursorForModes(){
if(!cvEl)return;
if(hideElemMode||zoomBoxMode){cvEl.style.cursor='crosshair';}
else{cvEl.style.cursor='';}
}

function refreshHideAllConnectedButton(){
var btn=document.getElementById('hide-elem-all-btn');
if(!btn)return;
if(hideAllConnectedMode){
btn.textContent='On';
btn.style.background='#00C853';
btn.style.color='#fff';
}else{
btn.textContent='Off';
btn.style.background='#D32F2F';
btn.style.color='#fff';
}
}

function setHideAllConnected(on){
hideAllConnectedMode=!!on;
refreshHideAllConnectedButton();
if(hideElemMode){
document.getElementById('st').textContent='Hide Elements: All Connected '+(hideAllConnectedMode?'ON':'OFF');
}
}

function toggleHideAllConnected(){
setHideAllConnected(!hideAllConnectedMode);
}

function initHideSelectionOverlay(){
if(hideSelDiv)return;
hideSelDiv=document.createElement('div');
hideSelDiv.id='hide-elements-rect';
hideSelDiv.style.cssText='position:absolute;display:none;border:2px dashed #E53935;background:rgba(229,57,53,0.15);pointer-events:none;z-index:151';
document.getElementById('c').appendChild(hideSelDiv);
}

function clearHideSelectionOverlay(){
hideSelStart=null;
hideSelEnd=null;
if(hideSelDiv)hideSelDiv.style.display='none';
}

function clearHideHoverHighlight(){
hideHoverElemIdx=-1;
if(hideHoverEdges){
try{if(sc)sc.remove(hideHoverEdges);}catch(e){}
try{
if(hideHoverEdges.geometry)hideHoverEdges.geometry.dispose();
if(hideHoverEdges.material)hideHoverEdges.material.dispose();
}catch(e){}
hideHoverEdges=null;
}
}

function updateHideHoverHighlightFromElem(elemIdx){
if(elemIdx===hideHoverElemIdx)return;
clearHideHoverHighlight();
if(!hideElemMode||elemIdx===undefined||elemIdx===null||elemIdx<0)return;
var fiList=visibleElemFaceMap[elemIdx];
if(!fiList||fiList.length===0)return;
var dispNodes=getDisplayNodes();
var vv=[];
for(var i=0;i<fiList.length;i++){
var fi=fiList[i];
if(fi<0||fi>=visibleFaces.length)continue;
var tri=visibleFaces[fi];
if(!tri||tri.length<3)continue;
for(var ti=0;ti<tri.length;ti++){
var ni=tri[ti];
if(ni<0||ni>=dispNodes.length)continue;
vv.push(dispNodes[ni][0],dispNodes[ni][1],dispNodes[ni][2]);
}
}
if(vv.length<9)return;
var g=new THREE.BufferGeometry();
g.setAttribute('position',new THREE.Float32BufferAttribute(vv,3));
var eG=new THREE.EdgesGeometry(g,1);
g.dispose();
hideHoverEdges=new THREE.LineSegments(eG,new THREE.LineBasicMaterial({color:0xFF0000,transparent:true,opacity:0.95,depthTest:false}));
hideHoverEdges.renderOrder=1200;
sc.add(hideHoverEdges);
hideHoverElemIdx=elemIdx;
}

function updateHideHoverHighlightFromClient(clientX,clientY){
if(!hideElemMode||hideSelStart||dr||pn||mz||!ms){
clearHideHoverHighlight();
return;
}
var ei=pickVisibleElementFromClient(clientX,clientY);
if(ei<0){clearHideHoverHighlight();return;}
updateHideHoverHighlightFromElem(ei);
}

function ensureElemConnectivityMaps(){
if(elemNodesMap&&nodeElemsMap)return;
var faceSrc=getFullFaces();
var faceElemSrc=getFullFaceElemMap();
var elemNodeSets=[];
nodeElemsMap=new Array(ON.length);
for(var fi=0;fi<faceSrc.length;fi++){
var ei=faceElemSrc[fi];
if(ei===undefined||ei===null||ei<0)continue;
var f=faceSrc[fi];
var setObj=elemNodeSets[ei];
if(!setObj){setObj=Object.create(null);elemNodeSets[ei]=setObj;}
for(var vi=0;vi<f.length;vi++){
var ni=f[vi];
if(ni===undefined||ni===null||ni<0||ni>=ON.length)continue;
if(setObj[ni])continue;
setObj[ni]=1;
var arr=nodeElemsMap[ni];
if(!arr){arr=[];nodeElemsMap[ni]=arr;}
arr.push(ei);
}
}
elemNodesMap=new Array(elemNodeSets.length);
for(var ei=0;ei<elemNodeSets.length;ei++){
var eSet=elemNodeSets[ei];
if(!eSet)continue;
var keys=Object.keys(eSet);
var nodes=new Array(keys.length);
for(var ki=0;ki<keys.length;ki++){nodes[ki]=parseInt(keys[ki],10);}
elemNodesMap[ei]=nodes;
}
}

function ncNormHex(hex){
var h=(hex===undefined||hex===null)?'':String(hex).trim();
if(/^#[0-9a-fA-F]{6}$/.test(h))return h.toUpperCase();
return null;
}
function ncHslToHex(h,s,l){
h=((h%1)+1)%1;
s=Math.max(0,Math.min(1,s));
l=Math.max(0,Math.min(1,l));
function f(p,q,t){
if(t<0)t+=1;if(t>1)t-=1;
if(t<1/6)return p+(q-p)*6*t;
if(t<1/2)return q;
if(t<2/3)return p+(q-p)*(2/3-t)*6;
return p;
}
var r,g,b;
if(s===0){r=g=b=l;}
else{
var q=l<0.5?l*(1+s):l+s-l*s;
var p=2*l-q;
r=f(p,q,h+1/3);g=f(p,q,h);b=f(p,q,h-1/3);
}
function hx(v){var n=Math.round(Math.max(0,Math.min(1,v))*255).toString(16).toUpperCase();return n.length<2?'0'+n:n;}
return '#'+hx(r)+hx(g)+hx(b);
}
function ncDefaultColor(idx){
if(idx>=0&&idx<NO_CONTOUR_GROUP_BASE.length)return NO_CONTOUR_GROUP_BASE[idx];
var h=(idx*0.6180339887498948)%1;
return ncHslToHex(h,0.62,0.48);
}
function ncHexToRgb01(hex){
var h=ncNormHex(hex);
if(!h)h='#BDBDC6';
return{r:parseInt(h.substring(1,3),16)/255,g:parseInt(h.substring(3,5),16)/255,b:parseInt(h.substring(5,7),16)/255};
}
function ensureNoContourGroups(){
if(noContourElemGroup&&noContourGroupSizes&&noContourGroupSizes.length>0)return;
ensureElemConnectivityMaps();
noContourElemGroup=null;
noContourGroupSizes=[];
if(!elemNodesMap||!nodeElemsMap||elemNodesMap.length===0)return;
var nElems=elemNodesMap.length;
var visited=new Uint8Array(nElems);
var elemGroup=new Int32Array(nElems);
for(var i=0;i<nElems;i++)elemGroup[i]=-1;
var sizes=[];
for(var ei=0;ei<nElems;ei++){
var eNodes=elemNodesMap[ei];
if(!eNodes||eNodes.length===0||visited[ei])continue;
var gid=sizes.length;
var cnt=0;
var q=[ei];
visited[ei]=1;
elemGroup[ei]=gid;
while(q.length>0){
var cur=q.pop();
cnt++;
var nodes=(cur<elemNodesMap.length)?elemNodesMap[cur]:null;
if(!nodes)continue;
for(var ni=0;ni<nodes.length;ni++){
var nodeIdx=nodes[ni];
var neigh=nodeElemsMap[nodeIdx];
if(!neigh)continue;
for(var jj=0;jj<neigh.length;jj++){
var ne=neigh[jj];
if(ne===undefined||ne===null||ne<0||ne>=nElems)continue;
if(visited[ne])continue;
var nNodes=elemNodesMap[ne];
if(!nNodes||nNodes.length===0)continue;
visited[ne]=1;
elemGroup[ne]=gid;
q.push(ne);
}
}
}
sizes.push(cnt);
}
var out=new Array(nElems);
for(var k=0;k<nElems;k++)out[k]=elemGroup[k];
noContourElemGroup=out;
noContourGroupSizes=sizes;
if(!Array.isArray(noContourGroupColors))noContourGroupColors=[];
for(var ci=0;ci<sizes.length;ci++){
if(!ncNormHex(noContourGroupColors[ci]))noContourGroupColors[ci]=ncDefaultColor(ci);
else noContourGroupColors[ci]=ncNormHex(noContourGroupColors[ci]);
}
if(noContourGroupColors.length>sizes.length)noContourGroupColors=noContourGroupColors.slice(0,sizes.length);
}
function getNoContourFaceRgb(elemIdx){
ensureNoContourGroups();
if(!noContourElemGroup||elemIdx===undefined||elemIdx===null||elemIdx<0||elemIdx>=noContourElemGroup.length)return{r:0.75,g:0.75,b:0.78};
var gid=noContourElemGroup[elemIdx];
if(gid===undefined||gid===null||gid<0)return{r:0.75,g:0.75,b:0.78};
var hx=(gid<noContourGroupColors.length)?noContourGroupColors[gid]:ncDefaultColor(gid);
return ncHexToRgb01(hx);
}
function renderNoContourGroupControls(){
var wrap=document.getElementById('nc-groups-wrap');
var body=document.getElementById('nc-groups-body');
if(!wrap||!body)return;
if(!noContour){wrap.style.display='none';body.innerHTML='';return;}
ensureNoContourGroups();
if(!noContourGroupSizes||noContourGroupSizes.length===0){
wrap.style.display='none';
body.innerHTML='';
return;
}
wrap.style.display='block';
var html='';
for(var i=0;i<noContourGroupSizes.length;i++){
var c=(i<noContourGroupColors.length)?noContourGroupColors[i]:ncDefaultColor(i);
var cnt=noContourGroupSizes[i];
html+='<div class="ncg-row"><span class="ncg-lbl">Group '+(i+1)+' ('+cnt+' elem)</span><input type="color" class="ncg-color" value="'+c+'" onchange="setNoContourGroupColor('+i+',this.value)"></div>';
}
body.innerHTML=html;
}
function setNoContourGroupColor(idx,val){
ensureNoContourGroups();
if(idx===undefined||idx===null||idx<0||idx>=noContourGroupColors.length)return;
var v=ncNormHex(val);
if(!v)return;
noContourGroupColors[idx]=v;
if(noContour){
cm(getRenderNodes(),null);
updateDialogBoxesVisuals();
}
refreshMaterialVisibilityDialog();
}

function expandHideSelectionWithConnected(elemList){
if(!hideAllConnectedMode||!elemList||elemList.length===0)return elemList||[];
ensureElemConnectivityMaps();
if(!elemNodesMap||!nodeElemsMap)return elemList||[];
var outMap=Object.create(null);
var queue=[];
for(var i=0;i<elemList.length;i++){
var ei=elemList[i];
if(ei===undefined||ei===null||ei<0)continue;
if(outMap[ei])continue;
outMap[ei]=1;
queue.push(ei);
}
while(queue.length>0){
var cur=queue.pop();
var nodes=(cur<elemNodesMap.length)?elemNodesMap[cur]:null;
if(!nodes)continue;
for(var ni=0;ni<nodes.length;ni++){
var nodeIdx=nodes[ni];
var neigh=nodeElemsMap[nodeIdx];
if(!neigh)continue;
for(var ei2=0;ei2<neigh.length;ei2++){
var nElem=neigh[ei2];
if(outMap[nElem])continue;
outMap[nElem]=1;
queue.push(nElem);
}
}
}
var out=[];
for(var k in outMap){if(Object.prototype.hasOwnProperty.call(outMap,k)&&outMap[k])out.push(parseInt(k,10));}
return out;
}

function pickVisibleElementFromClient(clientX,clientY){
if(!ms||!ca||!cvEl)return -1;
var rect=cvEl.getBoundingClientRect();
mouseNDC.x=((clientX-rect.left)/rect.width)*2-1;
mouseNDC.y=-((clientY-rect.top)/rect.height)*2+1;
raycaster.setFromCamera(mouseNDC,ca);
var hits=raycaster.intersectObject(ms);
if(!hits||hits.length===0)return -1;
var fi=hits[0].faceIndex;
if(fi===undefined||fi===null||fi<0||fi>=visibleFaceElemIdx.length)return -1;
var ei=visibleFaceElemIdx[fi];
if(ei===undefined||ei===null||ei<0)return -1;
return ei;
}

function getVisibleElementsInScreenBox(x1,y1,x2,y2){
if(!visibleFaces||visibleFaces.length===0)return [];
var rect=cvEl.getBoundingClientRect();
var minX=Math.max(0,Math.min(x1,x2));
var maxX=Math.min(rect.width,Math.max(x1,x2));
var minY=Math.max(0,Math.min(y1,y2));
var maxY=Math.min(rect.height,Math.max(y1,y2));
if(maxX-minX<2||maxY-minY<2)return [];
var dispNodes=getDisplayNodes();
var acc=Object.create(null);
for(var fi=0;fi<visibleFaces.length;fi++){
var ei=visibleFaceElemIdx[fi];
if(ei===undefined||ei===null||ei<0)continue;
var tri=visibleFaces[fi];
if(!tri||tri.length<3)continue;
var a=acc[ei];
if(!a){a={x:0,y:0,z:0,c:0};acc[ei]=a;}
for(var ti=0;ti<tri.length;ti++){
var ni=tri[ti];
if(ni<0||ni>=dispNodes.length)continue;
a.x+=dispNodes[ni][0];
a.y+=dispNodes[ni][1];
a.z+=dispNodes[ni][2];
a.c++;
}
}
var out=[];
for(var key in acc){
if(!Object.prototype.hasOwnProperty.call(acc,key))continue;
var s=acc[key];
if(!s||s.c<=0)continue;
var pos3=new THREE.Vector3(s.x/s.c,s.y/s.c,s.z/s.c);
pos3.project(ca);
if(pos3.z>1||pos3.z<-1)continue;
var sx=(pos3.x*0.5+0.5)*rect.width;
var sy=(-pos3.y*0.5+0.5)*rect.height;
if(sx>=minX&&sx<=maxX&&sy>=minY&&sy<=maxY)out.push(parseInt(key,10));
}
return out;
}

function runHideElementsRefresh(statusMsg){
var hasState=(cst&&AD[cst]);
if(hasState){rebuildCurrentMeshColors();}
else{cm(getRenderNodes(),null);}
updateValueWindowsForCut();
try{if(tableFormVisible)updateTableForm();}catch(e){}
try{updatePinnedPositions();}catch(e){}
updateDialogBoxesVisuals();
refreshMaterialVisibilityDialog();
if(statusMsg)document.getElementById('st').textContent=statusMsg;
}
function refreshAfterHideElementsChange(statusMsg,opts){
if(statusMsg!==undefined&&statusMsg!==null&&String(statusMsg).length>0)hideRefreshMsg=String(statusMsg);
var defer=!!(opts&&opts.defer);
if(!defer){
hideRefreshPending=false;
var msgNow=(statusMsg!==undefined&&statusMsg!==null)?String(statusMsg):(hideRefreshMsg||'');
hideRefreshMsg='';
runHideElementsRefresh(msgNow);
return;
}
if(hideRefreshPending)return;
hideRefreshPending=true;
var kick=(window&&window.requestAnimationFrame)?window.requestAnimationFrame:function(cb){setTimeout(cb,0);};
kick(function(){
if(!hideRefreshPending)return;
hideRefreshPending=false;
var msg=hideRefreshMsg||'';
hideRefreshMsg='';
runHideElementsRefresh(msg);
});
}

function applyHideElementsSelection(elemList,fromBox){
if(!elemList||elemList.length===0){
document.getElementById('st').textContent=fromBox?'Hide Elements: no visible element in selection':'Hide Elements: no element selected';
return;
}
var expanded=expandHideSelectionWithConnected(elemList);
var added=0;
for(var i=0;i<expanded.length;i++){
var ei=expanded[i];
if(ei===undefined||ei===null||ei<0)continue;
if(hiddenElemMap[ei])continue;
hiddenElemMap[ei]=1;
added++;
}
if(added===0){
document.getElementById('st').textContent='Hide Elements: selected element(s) already hidden';
return;
}
bumpHiddenElemRevision();
var total=countHiddenElements();
var modeTxt=hideAllConnectedMode?' (all connected)':'';
markValueTooltipHiddenByElement();
refreshAfterHideElementsChange(added+' element(s) hidden'+modeTxt+' - total hidden: '+total,{defer:true});
}

function unhideAllElements(){
hiddenElemMap=Object.create(null);
if(Array.isArray(groupVisibilityState)&&groupVisibilityState.length){
for(var i=0;i<groupVisibilityState.length;i++)groupVisibilityState[i]=true;
}
bumpHiddenElemRevision();
refreshAfterHideElementsChange('All hidden elements restored');
}

function tgHideElements(on){
hideElemMode=!!on;
var act=document.getElementById('hide-elem-actions');
var hint=document.getElementById('hide-elem-hint');
if(act)act.style.display=hideElemMode?'flex':'none';
if(hint)hint.style.display=hideElemMode?'block':'none';
refreshHideAllConnectedButton();
if(hideElemMode&&zoomBoxMode)toggleZoomBox();
if(!hideElemMode){
clearHideSelectionOverlay();
clearHideHoverHighlight();
document.getElementById('st').textContent='Hide Elements mode off';
}else{
document.getElementById('st').textContent='Hide Elements mode on: click or drag on mesh area';
}
updateViewerCursorForModes();
}

function getDialogById(id){
for(var i=0;i<dialogBoxes.length;i++){if(dialogBoxes[i].id===id)return dialogBoxes[i];}
return null;
}

function dialogCanvasPosFromClient(clientX,clientY){
if(!cvEl)return null;
var rect=cvEl.getBoundingClientRect();
var x=clientX-rect.left,y=clientY-rect.top;
if(x<0||y<0||x>rect.width||y>rect.height)return null;
return {x:x,y:y,rect:rect};
}

function applyDialogBoxDomPosition(box){
if(!box||!box.el||!cvEl)return;
var rect=cvEl.getBoundingClientRect();
box.el.style.left=(rect.left+box.x)+'px';
box.el.style.top=(rect.top+box.y)+'px';
}

function clampDialogBoxToView(box){
if(!box||!cvEl)return;
var rect=cvEl.getBoundingClientRect();
var bw=box.w||100,bh=box.h||30;
var maxX=Math.max(6,rect.width-bw-6);
var maxY=Math.max(6,rect.height-bh-6);
if(box.x<6)box.x=6;
if(box.y<6)box.y=6;
if(box.x>maxX)box.x=maxX;
if(box.y>maxY)box.y=maxY;
}

function syncDialogBoxSize(box){
if(!box||!box.el)return;
applyDialogFontToBox(box);
applyDialogTextStyle(box);
box.w=Math.max(90,box.el.offsetWidth||90);
box.h=Math.max(24,box.el.offsetHeight||24);
clampDialogBoxToView(box);
applyDialogBoxDomPosition(box);
if(dialogEditBoxId===box.id)positionDialogEditPopup(box);
}

function getDialogFontSizePx(box){
var n=parseInt(box&&box.fontSizePx,10);
if(!isFinite(n))n=dialogFontSize;
return Math.max(8,Math.min(36,n));
}

function applyDialogFontToBox(box){
if(!box||!box.el)return;
box.el.style.fontSize=getDialogFontSizePx(box)+'px';
}

function ensureDialogTextStyle(box){
if(!box)return {bold:false,italic:false,underline:false,color:'#222222'};
if(!box.textStyle||typeof box.textStyle!=='object'){
box.textStyle={bold:false,italic:false,underline:false,color:'#222222'};
}
if(box.textStyle.bold!==true)box.textStyle.bold=false;
if(box.textStyle.italic!==true)box.textStyle.italic=false;
if(box.textStyle.underline!==true)box.textStyle.underline=false;
box.textStyle.color=xyForecastSafeColor(box.textStyle.color,'#222222');
return box.textStyle;
}

function applyDialogTextStyle(box){
if(!box||!box.body)return;
box.body.style.fontWeight='';
box.body.style.fontStyle='';
box.body.style.textDecoration='';
box.body.style.color='';
}

function getDialogSelectionInfo(box){
if(!box||!box.body||!window.getSelection)return null;
var sel=window.getSelection();
if(!sel||sel.rangeCount<1)return null;
var range=sel.getRangeAt(0);
if(!range)return null;
var node=range.commonAncestorContainer;
if(node&&(node===box.body||box.body.contains(node)))return {range:range,collapsed:!!range.collapsed};
return null;
}

function setDialogFontSize(v){
var n=parseInt(v,10);
if(!isFinite(n))n=dialogFontSize;
n=Math.max(8,Math.min(24,n));
dialogFontSize=n;
for(var i=0;i<dialogBoxes.length;i++){
var b=dialogBoxes[i];
if(!b||!b.el)continue;
if(b.fontSizePx!==undefined&&b.fontSizePx!==null&&String(b.fontSizePx)!=='')continue;
applyDialogFontToBox(b);
syncDialogBoxSize(b);
}
updateDialogBoxesVisuals();
}

function syncDialogTextSnapshot(box){
if(!box||!box.body)return;
box.text=(box.body.innerText||box.body.textContent||'').replace(/\\r/g,'');
box.richHtml=box.body.innerHTML||'';
}

function getDialogSelectionRange(box){
var info=getDialogSelectionInfo(box);
return info?info.range:null;
}

function hasDialogExpandedSelection(box){
var info=getDialogSelectionInfo(box);
return !!(info&&!info.collapsed);
}

function saveDialogSelection(box){
var range=getDialogSelectionRange(box);
if(!range)return false;
try{
box.savedRange=range.cloneRange();
return true;
}catch(e){}
return false;
}

function placeDialogCaretAtEnd(box){
if(!box||!box.body||!window.getSelection)return false;
try{
var range=document.createRange();
range.selectNodeContents(box.body);
range.collapse(false);
var sel=window.getSelection();
sel.removeAllRanges();
sel.addRange(range);
box.savedRange=range.cloneRange();
return true;
}catch(e){}
return false;
}

function restoreDialogSelection(box){
if(!box||!box.body||!window.getSelection)return false;
box.body.focus();
var sel=window.getSelection();
if(!sel)return false;
try{
if(box.savedRange){
sel.removeAllRanges();
sel.addRange(box.savedRange);
return true;
}
}catch(e){}
return placeDialogCaretAtEnd(box);
}

function dialogCssColorToHex(v){
var s=(v===undefined||v===null)?'':String(v).trim();
if(!s)return '#222222';
if(/^#[0-9a-f]{3}$/i.test(s)){
return '#'+s.charAt(1)+s.charAt(1)+s.charAt(2)+s.charAt(2)+s.charAt(3)+s.charAt(3);
}
if(/^#[0-9a-f]{6}$/i.test(s))return s.toUpperCase();
var rgb=s.match(/^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})/i);
if(rgb){
var r=Math.max(0,Math.min(255,parseInt(rgb[1],10)||0));
var g=Math.max(0,Math.min(255,parseInt(rgb[2],10)||0));
var b=Math.max(0,Math.min(255,parseInt(rgb[3],10)||0));
return '#'+[r,g,b].map(function(n){var h=n.toString(16).toUpperCase();return h.length<2?('0'+h):h;}).join('');
}
var num=parseInt(s,10);
if(isFinite(num)){
num=Math.max(0,Math.min(0xFFFFFF,num));
var h=num.toString(16).toUpperCase();
while(h.length<6)h='0'+h;
return '#'+h;
}
return xyForecastSafeColor(s,'#222222');
}

function captureDialogTypingStyle(box,keepColor){
var style=ensureDialogTextStyle(box);
try{style.bold=!!document.queryCommandState('bold');}catch(e){}
try{style.italic=!!document.queryCommandState('italic');}catch(e){}
try{style.underline=!!document.queryCommandState('underline');}catch(e){}
if(keepColor!==true){
try{style.color=dialogCssColorToHex(document.queryCommandValue('foreColor'));}catch(e){}
}
return style;
}

function updateDialogStoredTypingStyle(box,cmd,value){
var style=ensureDialogTextStyle(box);
if(cmd==='bold'||cmd==='italic'||cmd==='underline'){
style[cmd]=!style[cmd];
}else if(cmd==='foreColor'){
style.color=dialogCssColorToHex(value);
}
return style;
}

function applyDialogTypingStyle(box){
if(!box||!box.body||box.readOnly||box.allowRichEdit===false||!box.editing)return false;
var info=getDialogSelectionInfo(box);
if(!info||!info.collapsed)return false;
var style=ensureDialogTextStyle(box);
try{document.execCommand('styleWithCSS',false,true);}catch(e){}
function syncCmd(cmd,desired){
var current=false;
try{current=!!document.queryCommandState(cmd);}catch(e){}
if(current===!!desired)return;
try{document.execCommand(cmd,false,null);}catch(e){}
}
syncCmd('bold',style.bold);
syncCmd('italic',style.italic);
syncCmd('underline',style.underline);
var currentColor='#222222';
try{currentColor=dialogCssColorToHex(document.queryCommandValue('foreColor'));}catch(e){}
if(String(currentColor).toLowerCase()!==String(style.color).toLowerCase()){
try{document.execCommand('foreColor',false,style.color);}catch(e){}
}
saveDialogSelection(box);
return true;
}

function dialogExecRichCommand(box,cmd,value){
if(!box||!box.body||box.readOnly||box.allowRichEdit===false)return;
setDialogEditing(box,true);
restoreDialogSelection(box);
var hadExpandedSelection=hasDialogExpandedSelection(box);
if(!hadExpandedSelection){
updateDialogStoredTypingStyle(box,cmd,value);
box.body.focus();
applyDialogTypingStyle(box);
saveDialogSelection(box);
syncDialogTextSnapshot(box);
syncDialogBoxSize(box);
syncDialogEditPopup(box);
updateDialogBoxesVisuals();
return;
}
try{document.execCommand('styleWithCSS',false,true);}catch(e){}
try{document.execCommand(cmd,false,value!==undefined?value:null);}catch(e){}
box.body.focus();
saveDialogSelection(box);
syncDialogTextSnapshot(box);
syncDialogBoxSize(box);
syncDialogEditPopup(box);
updateDialogBoxesVisuals();
}

function setDialogEditing(box,on){
if(!box||!box.el||!box.body)return;
if(on&&box.readOnly)return;
if(on)setActiveDialogBox(box.id,false);
if(!on)saveDialogSelection(box);
box.editing=!!on;
box.el.classList.toggle('editing',box.editing);
box.body.contentEditable=box.editing?'true':'false';
if(box.editing){
box.body.focus();
restoreDialogSelection(box);
applyDialogTypingStyle(box);
}
}

function setActiveDialogBox(id,keepEditPopup){
var nextId=(id===undefined||id===null)?null:id;
dialogActiveId=nextId;
for(var i=0;i<dialogBoxes.length;i++){
var b=dialogBoxes[i];
if(!b||!b.el)continue;
var on=(nextId!==null&&b.id===nextId);
if(!on&&b.editing)setDialogEditing(b,false);
b.el.classList.toggle('active',on);
}
if(dialogEditBoxId!==null&&dialogEditBoxId!==nextId&&!keepEditPopup){
closeDialogEditPopup();
}else if(dialogEditBoxId!==null&&dialogEditBoxId===nextId){
var activeBox=getDialogById(dialogEditBoxId);
if(activeBox){syncDialogEditPopup(activeBox);positionDialogEditPopup(activeBox);}
}
if(dialogFontBoxId!==null&&dialogFontBoxId!==nextId&&!keepEditPopup){
closeDialogFontPopup();
}else if(dialogFontBoxId!==null&&dialogFontBoxId===nextId){
var fontBox=getDialogById(dialogFontBoxId);
if(fontBox){syncDialogFontPopup(fontBox);}
}
}

function ensureDialogEditPopup(){
if(dialogEditPopupEl)return dialogEditPopupEl;
var pop=document.createElement('div');
pop.className='dialog-edit-popup';
pop.innerHTML='<div class="dep-head"><span>Edit</span><button type="button" class="dep-close">X</button></div><div class="dep-row"><button type="button" class="dep-btn" data-style="bold">B</button><button type="button" class="dep-btn" data-style="italic">I</button><button type="button" class="dep-btn" data-style="underline">U</button></div><div class="dep-row"><label for="dialog-edit-color">Color</label><input type="color" id="dialog-edit-color" value="#222222"></div>';
document.body.appendChild(pop);
pop.querySelector('.dep-close').onclick=function(ev){ev.stopPropagation();closeDialogEditPopup();};
var btns=pop.querySelectorAll('.dep-btn[data-style]');
for(var i=0;i<btns.length;i++){
btns[i].onmousedown=function(ev){ev.preventDefault();ev.stopPropagation();};
btns[i].onclick=function(ev){
ev.stopPropagation();
var box=getDialogById(dialogEditBoxId);
if(!box)return;
var styleName=this.getAttribute('data-style');
dialogExecRichCommand(box,styleName);
};
}
var colorIn=pop.querySelector('#dialog-edit-color');
colorIn.oninput=function(ev){
ev.stopPropagation();
var box=getDialogById(dialogEditBoxId);
if(!box)return;
dialogExecRichCommand(box,'foreColor',dialogCssColorToHex(this.value));
};
dialogEditPopupEl=pop;
return dialogEditPopupEl;
}

function positionDialogEditPopup(box){
if(!dialogEditPopupEl||!box||!box.el)return;
var rect=box.el.getBoundingClientRect();
var left=rect.right+10;
var top=rect.top;
dialogEditPopupEl.style.display='block';
var pw=dialogEditPopupEl.offsetWidth||190;
var ph=dialogEditPopupEl.offsetHeight||98;
if(left+pw>window.innerWidth-10)left=Math.max(10,rect.left-pw-10);
if(top+ph>window.innerHeight-10)top=Math.max(10,window.innerHeight-ph-10);
dialogEditPopupEl.style.left=left+'px';
dialogEditPopupEl.style.top=top+'px';
}

function syncDialogEditPopup(box){
if(!dialogEditPopupEl||!box)return;
if(box.readOnly||box.allowRichEdit===false){closeDialogEditPopup();return;}
var selInfo=getDialogSelectionInfo(box);
var useStoredStyle=!selInfo||selInfo.collapsed;
var style=ensureDialogTextStyle(box);
var btns=dialogEditPopupEl.querySelectorAll('.dep-btn[data-style]');
for(var i=0;i<btns.length;i++){
var k=btns[i].getAttribute('data-style');
var on=!!style[k];
if(!useStoredStyle){
try{on=!!document.queryCommandState(k);}catch(e){}
}
btns[i].classList.toggle('on',on);
}
var colorIn=dialogEditPopupEl.querySelector('#dialog-edit-color');
if(colorIn){
var color=style.color||'#222222';
if(!useStoredStyle){
try{color=dialogCssColorToHex(document.queryCommandValue('foreColor'));}catch(e){}
}
if(String(colorIn.value).toLowerCase()!==String(color).toLowerCase())colorIn.value=color;
}
}

function openDialogEditPopup(box){
if(!box||box.readOnly||box.allowRichEdit===false)return;
setActiveDialogBox(box.id,false);
setDialogEditing(box,true);
dialogEditBoxId=box.id;
var pop=ensureDialogEditPopup();
syncDialogEditPopup(box);
positionDialogEditPopup(box);
pop.style.display='block';
}

function closeDialogEditPopup(){
dialogEditBoxId=null;
if(dialogEditPopupEl)dialogEditPopupEl.style.display='none';
}

function ensureDialogFontPopup(){
if(dialogFontPopupEl)return dialogFontPopupEl;
var pop=document.createElement('div');
pop.className='dialog-font-popup';
pop.innerHTML='<div class="dfp-head"><span>Font Size</span><button type="button" class="dfp-close">X</button></div><div class="dfp-row"><label for="dialog-font-size-range" style="font-size:10px;font-weight:700;color:#555;min-width:54px">Font</label><input type="range" id="dialog-font-size-range" min="8" max="36" step="1" value="11"><span id="dialog-font-size-val" class="dfp-val">11</span></div><div class="dfp-row" id="dialog-forecast-format-row" style="display:none;margin-top:8px"><label for="dialog-forecast-format" style="font-size:10px;font-weight:700;color:#555;min-width:54px">Format</label><select id="dialog-forecast-format"><option value="float">Floating</option><option value="exp">Exponential</option></select></div><div class="dfp-row" id="dialog-forecast-decimals-row" style="display:none;margin-top:8px"><label for="dialog-forecast-decimals-range" style="font-size:10px;font-weight:700;color:#555;min-width:54px">Decimals</label><input type="range" id="dialog-forecast-decimals-range" min="0" max="10" step="1" value="6"><span id="dialog-forecast-decimals-val" class="dfp-val">6</span></div>';
document.body.appendChild(pop);
pop.querySelector('.dfp-close').onclick=function(ev){ev.stopPropagation();closeDialogFontPopup();};
var rangeEl=pop.querySelector('#dialog-font-size-range');
rangeEl.oninput=function(ev){
ev.stopPropagation();
var box=getDialogById(dialogFontBoxId);
if(!box)return;
setDialogBoxFontSize(box,this.value);
};
var fmtSel=pop.querySelector('#dialog-forecast-format');
if(fmtSel)fmtSel.onchange=function(ev){
ev.stopPropagation();
var box=getDialogById(dialogFontBoxId);
if(!box||!isForecastDialogBox(box))return;
box.forecastDialogFormat=(this.value==='exp')?'exp':'float';
refreshForecastDialogBoxContent(box);
};
var decRangeEl=pop.querySelector('#dialog-forecast-decimals-range');
if(decRangeEl)decRangeEl.oninput=function(ev){
ev.stopPropagation();
var box=getDialogById(dialogFontBoxId);
if(!box||!isForecastDialogBox(box))return;
box.forecastDialogDecimals=parseInt(this.value,10);
refreshForecastDialogBoxContent(box);
};
dialogFontPopupEl=pop;
return dialogFontPopupEl;
}

function positionDialogFontPopup(box){
if(!dialogFontPopupEl||!box||!box.el)return;
var rect=box.el.getBoundingClientRect();
var left=rect.right+10;
var top=rect.bottom+8;
if(dialogEditPopupEl&&dialogEditPopupEl.style.display==='block'&&dialogEditBoxId===box.id){
top=Math.max(rect.top,(dialogEditPopupEl.offsetTop||rect.top)+(dialogEditPopupEl.offsetHeight||0)+8);
}
dialogFontPopupEl.style.display='block';
var pw=dialogFontPopupEl.offsetWidth||210;
var ph=dialogFontPopupEl.offsetHeight||72;
if(left+pw>window.innerWidth-10)left=Math.max(10,rect.left-pw-10);
if(top+ph>window.innerHeight-10)top=Math.max(10,window.innerHeight-ph-10);
dialogFontPopupEl.style.left=left+'px';
dialogFontPopupEl.style.top=top+'px';
}

function syncDialogFontPopup(box){
if(!dialogFontPopupEl||!box)return;
var n=getDialogFontSizePx(box);
var rangeEl=dialogFontPopupEl.querySelector('#dialog-font-size-range');
var valEl=dialogFontPopupEl.querySelector('#dialog-font-size-val');
if(rangeEl&&String(rangeEl.value)!==String(n))rangeEl.value=String(n);
if(valEl)valEl.textContent=String(n);
var fmtRow=dialogFontPopupEl.querySelector('#dialog-forecast-format-row');
var fmtSel=dialogFontPopupEl.querySelector('#dialog-forecast-format');
var decRow=dialogFontPopupEl.querySelector('#dialog-forecast-decimals-row');
var decRangeEl=dialogFontPopupEl.querySelector('#dialog-forecast-decimals-range');
var decValEl=dialogFontPopupEl.querySelector('#dialog-forecast-decimals-val');
var showForecast=isForecastDialogBox(box);
if(fmtRow)fmtRow.style.display=showForecast?'flex':'none';
if(decRow)decRow.style.display=showForecast?'flex':'none';
if(showForecast){
var fmt=getForecastDialogFormat(box);
if(fmtSel&&fmtSel.value!==fmt)fmtSel.value=fmt;
var d=getForecastDialogDecimals(box);
if(decRangeEl&&String(decRangeEl.value)!==String(d))decRangeEl.value=String(d);
if(decValEl)decValEl.textContent=String(d);
}
}

function setDialogBoxFontSize(box,v){
if(!box||!box.el)return;
var n=parseInt(v,10);
if(!isFinite(n))n=getDialogFontSizePx(box);
n=Math.max(8,Math.min(36,n));
box.fontSizePx=n;
applyDialogFontToBox(box);
syncDialogBoxSize(box);
syncDialogFontPopup(box);
updateDialogBoxesVisuals();
}

function openDialogFontPopup(box){
if(!box)return;
setActiveDialogBox(box.id,false);
dialogFontBoxId=box.id;
var pop=ensureDialogFontPopup();
syncDialogFontPopup(box);
positionDialogFontPopup(box);
pop.style.display='block';
}

function closeDialogFontPopup(){
dialogFontBoxId=null;
if(dialogFontPopupEl)dialogFontPopupEl.style.display='none';
}

function ensureDialogPreview(){
if(dialogPreviewEl)return dialogPreviewEl;
dialogPreviewEl=document.createElement('div');
dialogPreviewEl.className='dialog-preview';
dialogPreviewEl.textContent='Dialog Box';
dialogPreviewEl.style.display='none';
document.body.appendChild(dialogPreviewEl);
return dialogPreviewEl;
}

function hideDialogPreview(){
if(dialogPreviewEl)dialogPreviewEl.style.display='none';
}

function updateDialogPreviewFromEvent(e){
if(!dialogMode||!dialogAddArmed){hideDialogPreview();return;}
var p=dialogCanvasPosFromClient(e.clientX,e.clientY);
if(!p){hideDialogPreview();return;}
var pv=ensureDialogPreview();
pv.style.display='block';
pv.style.left=(e.clientX+14)+'px';
pv.style.top=(e.clientY+12)+'px';
}

function tgDialogMode(on){
dialogMode=!!on;
var act=document.getElementById('dlg-actions');
var hint=document.getElementById('dlg-hint');
if(act)act.style.display=dialogMode?'flex':'none';
if(hint)hint.style.display=dialogMode?'block':'none';
if(!dialogMode){
dialogAddArmed=false;
dialogConnectPendingId=null;
hideDialogPreview();
dialogBoxes.forEach(function(b){setDialogEditing(b,false);});
setActiveDialogBox(null,false);
closeDialogEditPopup();
closeDialogFontPopup();
document.getElementById('st').textContent='Dialog Box mode off';
return;
}
dialogAddArmed=true;
document.getElementById('st').textContent='Dialog Box mode on: click mesh area to place';
}

function armAddDialogBox(){
if(!dialogMode){var cb=document.getElementById('dlg-on');if(cb){cb.checked=true;tgDialogMode(true);}return;}
dialogAddArmed=true;
document.getElementById('st').textContent='Click mesh area to place a new dialog box';
}

function removeDialogBoxById(id){
for(var i=0;i<dialogBoxes.length;i++){
if(dialogBoxes[i].id===id){
var b=dialogBoxes[i];
if(isMeasureGroupBox(b)&&measDialogRemovalId!==id){removeMeasureGroupById(b.measureGroupId);return;}
if(b.el&&b.el.parentNode)b.el.parentNode.removeChild(b.el);
dialogBoxes.splice(i,1);
if(dialogConnectPendingId===id)dialogConnectPendingId=null;
if(dialogActiveId===id)dialogActiveId=null;
if(dialogEditBoxId===id)closeDialogEditPopup();
if(dialogFontBoxId===id)closeDialogFontPopup();
break;
}
}
updateDialogBoxesVisuals();
}

function cleanDialogBoxes(){
var ids=[];
dialogBoxes.forEach(function(b){if(!isMeasureGroupBox(b))ids.push(b.id);});
ids.forEach(function(id){removeDialogBoxById(id);});
dialogConnectPendingId=null;
dialogAddArmed=dialogMode;
if(dialogActiveId!==null&&!getDialogById(dialogActiveId))dialogActiveId=null;
if(dialogEditBoxId!==null&&!getDialogById(dialogEditBoxId))closeDialogEditPopup();
if(dialogFontBoxId!==null&&!getDialogById(dialogFontBoxId))closeDialogFontPopup();
hideDialogPreview();
updateDialogBoxesVisuals();
document.getElementById('st').textContent='All dialog boxes removed';
}

function isDialogConnected(box){
return !!(box&&box.nodeIdx!==undefined&&box.nodeIdx!==null&&box.nodeIdx>=0);
}

function refreshDialogConnectButton(box){
if(!box||!box.linkBtn)return;
if(isMeasureGroupBox(box)){box.linkBtn.style.display='none';return;}
box.linkBtn.style.display='inline-block';
if(isDialogConnected(box)){
box.linkBtn.textContent='D';
box.linkBtn.title='Disconnect from node';
box.linkBtn.classList.add('dialog-btn-disconnect');
}else{
box.linkBtn.textContent='c';
box.linkBtn.title='Connect to node';
box.linkBtn.classList.remove('dialog-btn-disconnect');
}
}

function refreshDialogCopyButton(box){
if(!box||!box.copyBtn)return;
if(isMeasureGroupBox(box)){box.copyBtn.style.display='none';return;}
box.copyBtn.style.display=isForecastDialogBox(box)?'inline-block':'none';
}

function refreshDialogEditButton(box){
if(!box||!box.editBtn)return;
var show=(box.allowRichEdit!==false)&&!box.readOnly;
box.editBtn.style.display=show?'inline-block':'none';
if(!show&&dialogEditBoxId===box.id)closeDialogEditPopup();
}

function startDialogConnect(id){
var box=getDialogById(id);
if(!box)return;
dialogConnectPendingId=id;
document.getElementById('st').textContent='Dialog '+id+': click a node to connect';
}

function pickNearestNodeFromClient(clientX,clientY){
if(!ms||!ca||!cvEl)return -1;
var rect=cvEl.getBoundingClientRect();
mouseNDC.x=((clientX-rect.left)/rect.width)*2-1;
mouseNDC.y=-((clientY-rect.top)/rect.height)*2+1;
raycaster.setFromCamera(mouseNDC,ca);
var hits=raycaster.intersectObject(ms);
if(!hits||hits.length===0)return -1;
var fi=hits[0].faceIndex;
var tri=visibleFaces[fi];
if(!tri)return -1;
var pickNodes=getDisplayNodes();
var p=hits[0].point;
var p0=new THREE.Vector3(pickNodes[tri[0]][0],pickNodes[tri[0]][1],pickNodes[tri[0]][2]);
var p1=new THREE.Vector3(pickNodes[tri[1]][0],pickNodes[tri[1]][1],pickNodes[tri[1]][2]);
var p2=new THREE.Vector3(pickNodes[tri[2]][0],pickNodes[tri[2]][1],pickNodes[tri[2]][2]);
var d0=p.distanceTo(p0),d1=p.distanceTo(p1),d2=p.distanceTo(p2);
var nearest=tri[0];if(d1<d0&&d1<d2)nearest=tri[1];else if(d2<d0&&d2<d1)nearest=tri[2];
return nearest;
}

function createDialogBoxAtClient(clientX,clientY){
var p=dialogCanvasPosFromClient(clientX,clientY);
if(!p)return null;
var container=document.getElementById('dialog-box-container');
if(!container)return null;
var box={id:dialogIdSeed++,x:p.x+12,y:p.y+12,w:120,h:30,text:'Text',nodeIdx:-1,editing:false,readOnly:false,allowRichEdit:true,textStyle:{bold:false,italic:false,underline:false,color:'#222222'},fontSizePx:dialogFontSize,savedRange:null,richHtml:null,forecastDialogData:null,forecastDialogFormat:'float',forecastDialogDecimals:6,el:null,body:null,tools:null,linkBtn:null,copyBtn:null,fontBtn:null,editBtn:null};
var el=document.createElement('div');
el.className='dialog-box';
el.setAttribute('data-did',String(box.id));
var tools=document.createElement('div');
tools.className='dialog-tools';
var btnC=document.createElement('button');
btnC.className='dialog-btn dialog-btn-link';
btnC.addEventListener('click',function(ev){
ev.stopPropagation();
if(isDialogConnected(box)){
box.nodeIdx=-1;
if(dialogConnectPendingId===box.id)dialogConnectPendingId=null;
refreshDialogConnectButton(box);
updateDialogBoxesVisuals();
document.getElementById('st').textContent='Dialog '+box.id+' disconnected';
return;
}
startDialogConnect(box.id);
});
var btnCopy=document.createElement('button');
btnCopy.className='dialog-btn dialog-btn-copy';
btnCopy.textContent='copy';
btnCopy.title='Copy forecast data to clipboard';
btnCopy.style.display='none';
btnCopy.addEventListener('click',function(ev){
ev.stopPropagation();
copyForecastDialogBoxData(box);
});
var btnF=document.createElement('button');
btnF.className='dialog-btn dialog-btn-font';
btnF.textContent='f';
btnF.title='Font size';
btnF.addEventListener('click',function(ev){
ev.stopPropagation();
if(dialogFontBoxId===box.id&&dialogFontPopupEl&&dialogFontPopupEl.style.display==='block'){closeDialogFontPopup();return;}
openDialogFontPopup(box);
});
var btnE=document.createElement('button');
btnE.className='dialog-btn dialog-btn-edit';
btnE.textContent='e';
btnE.title='Edit text style';
btnE.addEventListener('click',function(ev){
ev.stopPropagation();
if(dialogEditBoxId===box.id&&dialogEditPopupEl&&dialogEditPopupEl.style.display==='block'){closeDialogEditPopup();return;}
openDialogEditPopup(box);
});
var btnX=document.createElement('button');
btnX.className='dialog-btn dialog-btn-del';
btnX.textContent='x';
btnX.title='Delete';
btnX.addEventListener('click',function(ev){ev.stopPropagation();removeDialogBoxById(box.id);});
tools.appendChild(btnC);
tools.appendChild(btnCopy);
tools.appendChild(btnF);
tools.appendChild(btnE);
tools.appendChild(btnX);
var body=document.createElement('div');
body.className='dialog-body';
body.contentEditable='false';
body.textContent='Text';
body.addEventListener('focus',function(){
if(box.editing)applyDialogTypingStyle(box);
if(dialogEditBoxId===box.id)syncDialogEditPopup(box);
});
body.addEventListener('dblclick',function(ev){
ev.stopPropagation();
if(box.readOnly)return;
for(var i=0;i<dialogBoxes.length;i++){if(dialogBoxes[i].id!==box.id)setDialogEditing(dialogBoxes[i],false);}
setDialogEditing(box,true);
});
body.addEventListener('beforeinput',function(ev){
if(!box.editing)return;
var it=(ev&&ev.inputType)?String(ev.inputType):'';
if(it.indexOf('insert')===0)applyDialogTypingStyle(box);
});
body.addEventListener('mouseup',function(){
if(box.editing&&!hasDialogExpandedSelection(box))applyDialogTypingStyle(box);
else saveDialogSelection(box);
if(dialogEditBoxId===box.id)syncDialogEditPopup(box);
});
body.addEventListener('keyup',function(ev){
if(box.editing&&!(ev&&((ev.ctrlKey||ev.metaKey||ev.altKey)))&&!hasDialogExpandedSelection(box))applyDialogTypingStyle(box);
else saveDialogSelection(box);
if(dialogEditBoxId===box.id)syncDialogEditPopup(box);
});
body.addEventListener('input',function(){
syncDialogTextSnapshot(box);
saveDialogSelection(box);
syncDialogBoxSize(box);
if(dialogEditBoxId===box.id)syncDialogEditPopup(box);
});
el.appendChild(tools);
el.appendChild(body);
el.addEventListener('mousedown',function(ev){
if(ev.target&&ev.target.closest&&ev.target.closest('.dialog-edit-popup'))return;
if(ev.target&&ev.target.closest&&ev.target.closest('.dialog-font-popup'))return;
setActiveDialogBox(box.id,false);
if(box.editing)return;
if(ev.target&&ev.target.closest&&ev.target.closest('button'))return;
ev.preventDefault();ev.stopPropagation();
var rect=cvEl?cvEl.getBoundingClientRect():{left:0,top:0};
dialogDrag={id:box.id,ox:ev.clientX-rect.left-box.x,oy:ev.clientY-rect.top-box.y};
});
container.appendChild(el);
box.el=el;box.body=body;box.tools=tools;box.linkBtn=btnC;box.copyBtn=btnCopy;box.fontBtn=btnF;box.editBtn=btnE;
dialogBoxes.push(box);
applyDialogFontToBox(box);
applyDialogTextStyle(box);
refreshDialogConnectButton(box);
refreshDialogCopyButton(box);
refreshDialogEditButton(box);
syncDialogTextSnapshot(box);
syncDialogBoxSize(box);
setDialogEditing(box,false);
setActiveDialogBox(box.id,false);
updateDialogBoxesVisuals();
return box;
}

function getTableFormLinkTargets(){
if(!tableLinksActive()||!cvEl)return null;
var win=document.getElementById('table-form-window');
var table=document.getElementById('table-form-table');
var body=document.getElementById('table-form-body');
if(!win||!table||!body)return null;
var ws=window.getComputedStyle?window.getComputedStyle(win):null;
if(!ws||ws.display==='none'||ws.visibility==='hidden'||parseFloat(ws.opacity||'1')<=0)return null;
var cvRect=cvEl.getBoundingClientRect();
if(cvRect.width<6||cvRect.height<6)return null;
var tableRect=table.getBoundingClientRect();
var bodyRect=body.getBoundingClientRect();
var side=(tableRect.left+tableRect.width*0.5)<(cvRect.left+cvRect.width*0.5)?'right':'left';
var rows=table.querySelectorAll('tbody tr[data-kind][data-idx]');
if(!rows||rows.length===0)return{cvRect:cvRect,side:side,items:[]};
var dispNodes=getDisplayNodes();
var cuts=getActiveCuts();
var hasCuts=cuts.length>0;
var items=[];
for(var i=0;i<rows.length;i++){
var tr=rows[i];
var rr=tr.getBoundingClientRect();
if(rr.bottom<bodyRect.top||rr.top>bodyRect.bottom)continue;
var tdId=tr.querySelector('td[data-col="0"]');
var tdVal=tr.querySelector('td[data-col="1"]');
var srcCell=(side==='right')?(tdVal||tdId):(tdId||tdVal);
if(!srcCell)continue;
var sr=srcCell.getBoundingClientRect();
if(sr.bottom<bodyRect.top||sr.top>bodyRect.bottom)continue;
var kind=(tr.getAttribute('data-kind')||'').toUpperCase();
var idx=parseInt(tr.getAttribute('data-idx'),10);
if(!isFinite(idx)||idx<0)continue;
var wx=0,wy=0,wz=0,isElem=(kind==='E');
if(isElem){
if(!isElemVisibleNow(idx))continue;
var ctr=getElemCentroid3D(idx);
if(!ctr)continue;
if(hasCuts&&!isPointVisibleByCuts([ctr.x,ctr.y,ctr.z],cuts))continue;
wx=ctr.x;wy=ctr.y;wz=ctr.z;
}else{
if(idx>=dispNodes.length||!isNodeVisibleNow(idx))continue;
if(hasCuts&&!isPointVisibleByCuts(dispNodes[idx],cuts))continue;
wx=dispNodes[idx][0];wy=dispNodes[idx][1];wz=dispNodes[idx][2];
}
var p3=new THREE.Vector3(wx,wy,wz);
p3.project(ca);
if(p3.z>1)continue;
var tx=(p3.x*0.5+0.5)*cvRect.width+cvRect.left;
var ty=(-p3.y*0.5+0.5)*cvRect.height+cvRect.top;
var sx=((side==='right')?sr.right:sr.left)+((side==='right')?1.2:-1.2);
var sy=sr.top+sr.height*0.5;
items.push({sx:sx,sy:sy,tx:tx,ty:ty,isElem:isElem,idx:idx});
}
return{cvRect:cvRect,side:side,items:items};
}

function getElemEdgesForLink(elemIdx){
var key=String(elemIdx);
if(tfElemEdgeCache[key])return tfElemEdgeCache[key];
var faces=getFullFaces();
var fem=getFullFaceElemMap();
var unique=Object.create(null);
var edges=[];
function addEdge(a,b){
if(a===undefined||b===undefined||a<0||b<0)return;
var k=a<b?(a+'_'+b):(b+'_'+a);
if(unique[k])return;
unique[k]=1;
edges.push([a,b]);
}
for(var fi=0;fi<faces.length;fi++){
if(fem[fi]!==elemIdx)continue;
var f=faces[fi];
if(!f||f.length<3)continue;
addEdge(f[0],f[1]);
addEdge(f[1],f[2]);
addEdge(f[2],f[0]);
}
tfElemEdgeCache[key]=edges;
return edges;
}

function drawTableLinkElemEdgesOverlay(ctx,data){
if(!data||!data.items||data.items.length===0||!centroidMode)return;
var elems=Object.create(null);
for(var i=0;i<data.items.length;i++){
var it=data.items[i];
if(it&&it.isElem&&it.idx!==undefined&&it.idx!==null)elems[it.idx]=1;
}
var keys=Object.keys(elems);
if(keys.length===0)return;
var dispNodes=getDisplayNodes();
var cuts=getActiveCuts();
var hasCuts=cuts.length>0;
var cvRect=data.cvRect;
ctx.save();
ctx.strokeStyle='rgba(255,0,255,0.95)';
ctx.lineWidth=1.2;
for(var ki=0;ki<keys.length;ki++){
var ei=parseInt(keys[ki],10);
if(!isFinite(ei)||ei<0||!isElemVisibleNow(ei))continue;
var edges=getElemEdgesForLink(ei);
for(var eii=0;eii<edges.length;eii++){
var e=edges[eii];
var n0=e[0],n1=e[1];
if(n0<0||n1<0||n0>=dispNodes.length||n1>=dispNodes.length)continue;
var p0=dispNodes[n0],p1=dispNodes[n1];
if(hasCuts&&!(isPointVisibleByCuts(p0,cuts)||isPointVisibleByCuts(p1,cuts)))continue;
var v0=new THREE.Vector3(p0[0],p0[1],p0[2]);
var v1=new THREE.Vector3(p1[0],p1[1],p1[2]);
v0.project(ca);v1.project(ca);
if(v0.z>1||v1.z>1||v0.z<-1||v1.z<-1)continue;
var x0=(v0.x*0.5+0.5)*cvRect.width+cvRect.left;
var y0=(-v0.y*0.5+0.5)*cvRect.height+cvRect.top;
var x1=(v1.x*0.5+0.5)*cvRect.width+cvRect.left;
var y1=(-v1.y*0.5+0.5)*cvRect.height+cvRect.top;
ctx.beginPath();
ctx.moveTo(x0,y0);
ctx.lineTo(x1,y1);
ctx.stroke();
}
}
ctx.restore();
}

function drawTableLinkElemEdgesOnCanvas(ctx,data,w,h){
if(!data||!data.items||data.items.length===0||!centroidMode)return;
var elems=Object.create(null);
for(var i=0;i<data.items.length;i++){
var it=data.items[i];
if(it&&it.isElem&&it.idx!==undefined&&it.idx!==null)elems[it.idx]=1;
}
var keys=Object.keys(elems);
if(keys.length===0)return;
var dispNodes=getDisplayNodes();
var cuts=getActiveCuts();
var hasCuts=cuts.length>0;
ctx.save();
ctx.strokeStyle='rgba(255,0,255,0.95)';
ctx.lineWidth=Math.max(1,1.2*(w/Math.max(1,data.cvRect.width)));
for(var ki=0;ki<keys.length;ki++){
var ei=parseInt(keys[ki],10);
if(!isFinite(ei)||ei<0||!isElemVisibleNow(ei))continue;
var edges=getElemEdgesForLink(ei);
for(var eii=0;eii<edges.length;eii++){
var e=edges[eii];
var n0=e[0],n1=e[1];
if(n0<0||n1<0||n0>=dispNodes.length||n1>=dispNodes.length)continue;
var p0=dispNodes[n0],p1=dispNodes[n1];
if(hasCuts&&!(isPointVisibleByCuts(p0,cuts)||isPointVisibleByCuts(p1,cuts)))continue;
var v0=new THREE.Vector3(p0[0],p0[1],p0[2]);
var v1=new THREE.Vector3(p1[0],p1[1],p1[2]);
v0.project(ca);v1.project(ca);
if(v0.z>1||v1.z>1||v0.z<-1||v1.z<-1)continue;
var x0=(v0.x*0.5+0.5)*w;
var y0=(-v0.y*0.5+0.5)*h;
var x1=(v1.x*0.5+0.5)*w;
var y1=(-v1.y*0.5+0.5)*h;
ctx.beginPath();
ctx.moveTo(x0,y0);
ctx.lineTo(x1,y1);
ctx.stroke();
}
}
ctx.restore();
}

function drawTableFormLinksOverlay(ctx){
var data=getTableFormLinkTargets();
if(!data||!data.items||data.items.length===0)return;
drawTableLinkElemEdgesOverlay(ctx,data);
ctx.save();
ctx.lineWidth=1.4;
ctx.strokeStyle='rgba(255,152,0,0.92)';
for(var i=0;i<data.items.length;i++){
var it=data.items[i];
ctx.beginPath();
ctx.arc(it.sx,it.sy,2.8,0,Math.PI*2);
ctx.fillStyle='rgba(244,67,54,0.96)';
ctx.fill();
ctx.strokeStyle='rgba(183,28,28,0.95)';
ctx.lineWidth=0.95;
ctx.stroke();
ctx.strokeStyle='rgba(255,152,0,0.92)';
ctx.lineWidth=1.35;
ctx.beginPath();
ctx.moveTo(it.sx,it.sy);
ctx.lineTo(it.tx,it.ty);
ctx.stroke();
ctx.beginPath();
ctx.arc(it.tx,it.ty,3.2,0,Math.PI*2);
ctx.fillStyle=it.isElem?'#66BB6A':'#FFD600';
ctx.fill();
ctx.strokeStyle='rgba(0,0,0,0.65)';
ctx.lineWidth=1;
ctx.stroke();
ctx.strokeStyle='rgba(255,152,0,0.92)';
ctx.lineWidth=1.4;
}
ctx.restore();
}

function drawTableFormLinksOnCanvas(ctx,w,h){
var data=getTableFormLinkTargets();
if(!data||!data.items||data.items.length===0)return;
drawTableLinkElemEdgesOnCanvas(ctx,data,w,h);
var cvRect=data.cvRect;
var sxScale=w/Math.max(1,cvRect.width);
var syScale=h/Math.max(1,cvRect.height);
var startMap=Object.create(null);
if(tfLastExportTableLayout&&tfLastExportTableLayout.rows&&tfLastExportTableLayout.rows.length){
for(var li=0;li<tfLastExportTableLayout.rows.length;li++){
var lr=tfLastExportTableLayout.rows[li];
var lk=(lr.kind||'N')+':'+lr.idx;
startMap[lk]={sx:lr.sx,sy:lr.sy};
}
}
ctx.save();
ctx.lineWidth=Math.max(1,1.4*Math.min(sxScale,syScale));
ctx.strokeStyle='rgba(255,152,0,0.92)';
for(var i=0;i<data.items.length;i++){
var it=data.items[i];
var k=(it.isElem?'E':'N')+':'+it.idx;
var mapPt=startMap[k];
if(tfLastExportTableLayout&&tfLastExportTableLayout.rows&&tfLastExportTableLayout.rows.length&&!mapPt)continue;
var sx=mapPt?mapPt.sx:(it.sx-cvRect.left)*sxScale;
var sy=mapPt?mapPt.sy:(it.sy-cvRect.top)*syScale;
var tx=(it.tx-cvRect.left)*sxScale;
var ty=(it.ty-cvRect.top)*syScale;
var sRad=Math.max(2.0,2.8*Math.min(sxScale,syScale));
ctx.beginPath();
ctx.arc(sx,sy,sRad,0,Math.PI*2);
ctx.fillStyle='rgba(244,67,54,0.96)';
ctx.fill();
ctx.strokeStyle='rgba(183,28,28,0.95)';
ctx.lineWidth=Math.max(1,0.95*Math.min(sxScale,syScale));
ctx.stroke();
ctx.strokeStyle='rgba(255,152,0,0.92)';
ctx.lineWidth=Math.max(1,1.35*Math.min(sxScale,syScale));
ctx.beginPath();
ctx.moveTo(sx,sy);
ctx.lineTo(tx,ty);
ctx.stroke();
ctx.beginPath();
ctx.arc(tx,ty,Math.max(2.6,3.2*Math.min(sxScale,syScale)),0,Math.PI*2);
ctx.fillStyle=it.isElem?'#66BB6A':'#FFD600';
ctx.fill();
ctx.strokeStyle='rgba(0,0,0,0.65)';
ctx.lineWidth=Math.max(1,Math.min(1.2,1.1*Math.min(sxScale,syScale)));
ctx.stroke();
ctx.strokeStyle='rgba(255,152,0,0.92)';
ctx.lineWidth=Math.max(1,1.4*Math.min(sxScale,syScale));
}
ctx.restore();
}

function buildDialogLinkRect(left,top,width,height){
var w=Math.max(2,width||0),h=Math.max(2,height||0);
return{left:left,top:top,width:w,height:h,right:left+w,bottom:top+h};
}

function getDialogLinkAnchorFromRect(rect,targetX,targetY,offsetPx){
if(!rect)return null;
var cx=rect.left+rect.width*0.5;
var cy=rect.top+rect.height*0.5;
var dx=targetX-cx;
var dy=targetY-cy;
if(Math.abs(dx)<1e-9&&Math.abs(dy)<1e-9)dx=1;
var hw=Math.max(1,rect.width*0.5);
var hh=Math.max(1,rect.height*0.5);
var tx=(Math.abs(dx)<1e-9)?1e9:(hw/Math.abs(dx));
var ty=(Math.abs(dy)<1e-9)?1e9:(hh/Math.abs(dy));
var t=Math.min(tx,ty);
var ax=cx+dx*t;
var ay=cy+dy*t;
var len=Math.sqrt(dx*dx+dy*dy);
var out=isFinite(offsetPx)?offsetPx:0;
if(len>1e-9&&out!==0){
ax+=(dx/len)*out;
ay+=(dy/len)*out;
}
var dl=Math.abs(ax-rect.left),dr=Math.abs(ax-rect.right),dt=Math.abs(ay-rect.top),db=Math.abs(ay-rect.bottom);
var side='left',best=dl;
if(dr<best){best=dr;side='right';}
if(dt<best){best=dt;side='top';}
if(db<best){side='bottom';}
return{x:ax,y:ay,cx:cx,cy:cy,side:side};
}

function getDialogBoxClientLinkAnchor(box,targetX,targetY){
if(!box||!box.el)return null;
var r=box.el.getBoundingClientRect();
return getDialogLinkAnchorFromRect(buildDialogLinkRect(r.left,r.top,r.width,r.height),targetX,targetY,1.2);
}

function updateDialogBoxesVisuals(){
var layer=document.getElementById('dialog-link-layer');
if(!layer||!cvEl)return;
var dpr=window.devicePixelRatio||1;
var ww=Math.max(1,window.innerWidth),hh=Math.max(1,window.innerHeight);
var pw=Math.floor(ww*dpr),ph=Math.floor(hh*dpr);
if(layer.width!==pw||layer.height!==ph){layer.width=pw;layer.height=ph;}
layer.style.width=ww+'px';layer.style.height=hh+'px';
var ctx=layer.getContext('2d');
ctx.setTransform(dpr,0,0,dpr,0,0);
ctx.clearRect(0,0,ww,hh);
drawTableFormLinksOverlay(ctx);
var rect=cvEl.getBoundingClientRect();
var dispNodes=getDisplayNodes();
for(var i=0;i<dialogBoxes.length;i++){
var b=dialogBoxes[i];
if(!b||!b.el)continue;
refreshDialogConnectButton(b);
syncDialogBoxSize(b);
applyDialogBoxDomPosition(b);
if(b.nodeIdx===undefined||b.nodeIdx===null||b.nodeIdx<0||b.nodeIdx>=dispNodes.length)continue;
if(!isNodeVisibleNow(b.nodeIdx))continue;
var pos3=new THREE.Vector3(dispNodes[b.nodeIdx][0],dispNodes[b.nodeIdx][1],dispNodes[b.nodeIdx][2]);
pos3.project(ca);
if(pos3.z>1)continue;
var sx=(pos3.x*0.5+0.5)*rect.width+rect.left;
var sy=(-pos3.y*0.5+0.5)*rect.height+rect.top;
var anchor=getDialogBoxClientLinkAnchor(b,sx,sy);
if(!anchor)continue;
ctx.strokeStyle='#FF5BFF';
 ctx.lineWidth=1.5;
ctx.beginPath();ctx.moveTo(sx,sy);ctx.lineTo(anchor.x,anchor.y);ctx.stroke();
ctx.beginPath();ctx.arc(anchor.x,anchor.y,2.8,0,Math.PI*2);
ctx.fillStyle='rgba(255,255,255,0.98)';
ctx.fill();
ctx.strokeStyle='rgba(255,91,255,0.96)';
ctx.lineWidth=1.2;
ctx.stroke();
ctx.beginPath();ctx.arc(sx,sy,2.6,0,Math.PI*2);
ctx.fillStyle='#2196F3';ctx.fill();
ctx.strokeStyle='rgba(0,0,0,0.65)';
ctx.lineWidth=1;
ctx.stroke();
}
if(dialogEditBoxId!==null){
var eb=getDialogById(dialogEditBoxId);
if(eb){syncDialogEditPopup(eb);positionDialogEditPopup(eb);}
else{closeDialogEditPopup();}
}
}

function wrapDialogTextForCanvas(ctx,text,maxWidth){
var out=[];
var src=(text!==undefined&&text!==null)?String(text):'';
var paras=src.replace(/\\r/g,'').split(/\\n/);
if(maxWidth<8)maxWidth=8;
for(var pi=0;pi<paras.length;pi++){
var para=paras[pi];
if(para===''){out.push('');continue;}
var line='';
for(var ci=0;ci<para.length;ci++){
var ch=para.charAt(ci);
if(ch==='\\t')ch='    ';
var cand=line+ch;
if(line!==''&&ctx.measureText(cand).width>maxWidth){
out.push(line);
line=(ch===' ')?'':ch;
}else{
line=cand;
}
}
if(line!=='')out.push(line);
}
if(out.length===0)out.push('');
return out;
}

function getDialogCanvasStyle(box){
var out={bold:false,italic:false,underline:false,color:'#222222'};
if(!box||!box.body||!window.getComputedStyle)return out;
if(box.body.classList&&box.body.classList.contains('dialog-body-rich'))return out;
try{
var srcEl=box.body;
var richEl=box.body.querySelector('span,b,strong,i,em,u,font');
if(richEl)srcEl=richEl;
var cs=window.getComputedStyle(srcEl);
var fw=String(cs.fontWeight||'').toLowerCase();
out.bold=(fw==='bold'||parseInt(fw,10)>=600);
out.italic=String(cs.fontStyle||'').toLowerCase()==='italic';
var td=String(cs.textDecoration||cs.textDecorationLine||'').toLowerCase();
out.underline=td.indexOf('underline')>=0;
out.color=dialogCssColorToHex(cs.color||'#222222');
}catch(e){}
return out;
}

function drawDialogBoxesOnCanvas(ctx,w,h){
if(!dialogBoxes||dialogBoxes.length===0||!cvEl)return;
var rect=cvEl.getBoundingClientRect();
var sxScale=w/Math.max(1,rect.width),syScale=h/Math.max(1,rect.height);
var dispNodes=getDisplayNodes();
ctx.save();
for(var i=0;i<dialogBoxes.length;i++){
var b=dialogBoxes[i];
if(!b)continue;
if(b.el)syncDialogBoxSize(b);
var bx=b.x*sxScale,by=b.y*syScale;
var baseScale=Math.max(0.2,Math.min(sxScale,syScale));
var bw=Math.max(90*baseScale,(b.w||100)*sxScale);
var bh=Math.max(24*baseScale,(b.h||24)*syScale);
var dlgFs=Math.max(8,Math.round(getDialogFontSizePx(b)*baseScale));
var lh=Math.max(dlgFs+3,Math.ceil(dlgFs*1.35));
var padX=Math.max(6,7*baseScale);
var padY=Math.max(5,5*baseScale);
var tStyle=getDialogCanvasStyle(b);
var linkNodePt=null,linkAnchor=null;
if(b.nodeIdx!==undefined&&b.nodeIdx!==null&&b.nodeIdx>=0&&b.nodeIdx<dispNodes.length&&isNodeVisibleNow(b.nodeIdx)){
var sp=projectNodeToCanvas(b.nodeIdx,w,h);
if(sp){
linkNodePt=sp;
}
}
ctx.font=(tStyle.italic?'italic ':'')+(tStyle.bold?'700 ':'600 ')+dlgFs+'px Arial';
var txt=(b.text!==undefined&&b.text!==null)?String(b.text):'';
var lines=wrapDialogTextForCanvas(ctx,txt,Math.max(12,bw-padX*2));
var textH=lines.length*lh;
var innerH=Math.max(22*baseScale,bh-padY*2);
if(textH>innerH){innerH=textH;bh=innerH+padY*2;}
if(linkNodePt){
linkAnchor=getDialogLinkAnchorFromRect(buildDialogLinkRect(bx,by,bw,bh),linkNodePt.x,linkNodePt.y,Math.max(1,1.1*baseScale));
ctx.strokeStyle='#FF5BFF';
ctx.lineWidth=Math.max(1,1.2*sxScale);
ctx.beginPath();ctx.moveTo(linkNodePt.x,linkNodePt.y);ctx.lineTo(linkAnchor.x,linkAnchor.y);ctx.stroke();
}
ctx.fillStyle='rgba(255,255,255,0.95)';
ctx.strokeStyle='rgba(0,0,0,0.24)';
ctx.lineWidth=1;
roundRectPath(ctx,bx,by,bw,bh,Math.max(4,4*sxScale));
ctx.save();
ctx.beginPath();
ctx.rect(bx,by,bw,bh);
ctx.clip();
ctx.fillStyle='#222';
var txtAlign='left';
try{
if(b.body){
var ta=window.getComputedStyle(b.body).textAlign;
if(ta==='center'||ta==='right'||ta==='left')txtAlign=ta;
}
}catch(e){}
ctx.textAlign=txtAlign;
ctx.textBaseline='top';
ctx.font=(tStyle.italic?'italic ':'')+(tStyle.bold?'700 ':'600 ')+dlgFs+'px Arial';
ctx.fillStyle=tStyle.color||'#222';
var tx=(txtAlign==='center')?(bx+bw*0.5):((txtAlign==='right')?(bx+bw-padX):(bx+padX));
var ty=by+padY+Math.max(0,(innerH-textH)*0.5);
for(var li=0;li<lines.length;li++){
var ly=ty+li*lh;
ctx.fillText(lines[li],tx,ly);
if(tStyle.underline&&lines[li]){
var mw=ctx.measureText(lines[li]).width;
var ux1=(txtAlign==='center')?(tx-mw*0.5):((txtAlign==='right')?(tx-mw):tx);
var ux2=ux1+mw;
var uy=ly+Math.max(1,Math.round(dlgFs*1.05));
ctx.strokeStyle=tStyle.color||'#222';
ctx.lineWidth=Math.max(1,0.9*baseScale);
ctx.beginPath();ctx.moveTo(ux1,uy);ctx.lineTo(ux2,uy);ctx.stroke();
}
}
ctx.restore();
if(linkAnchor){
ctx.beginPath();
ctx.arc(linkAnchor.x,linkAnchor.y,Math.max(2.1,2.7*Math.min(sxScale,syScale)),0,Math.PI*2);
ctx.fillStyle='rgba(255,255,255,0.98)';
ctx.fill();
ctx.strokeStyle='rgba(255,91,255,0.96)';
ctx.lineWidth=Math.max(1,1.1*Math.min(sxScale,syScale));
ctx.stroke();
}
if(linkNodePt){
ctx.beginPath();
ctx.arc(linkNodePt.x,linkNodePt.y,Math.max(2.0,2.5*Math.min(sxScale,syScale)),0,Math.PI*2);
ctx.fillStyle='#2196F3';
ctx.fill();
ctx.strokeStyle='rgba(0,0,0,0.65)';
ctx.lineWidth=Math.max(1,Math.min(1.2,1.0*Math.min(sxScale,syScale)));
ctx.stroke();
}
}
ctx.restore();
}

function initDialogBoxSystem(){
if(window._dlgBoxInitDone)return;
window._dlgBoxInitDone=true;
document.addEventListener('mousemove',function(e){
if(!dialogDrag)return;
var b=getDialogById(dialogDrag.id);
if(!b)return;
var rect=cvEl?cvEl.getBoundingClientRect():{left:0,top:0};
b.x=e.clientX-rect.left-dialogDrag.ox;
b.y=e.clientY-rect.top-dialogDrag.oy;
clampDialogBoxToView(b);
applyDialogBoxDomPosition(b);
updateDialogBoxesVisuals();
});
document.addEventListener('mouseup',function(){dialogDrag=null;});
document.addEventListener('mousedown',function(e){
var inDlg=e.target&&e.target.closest&&e.target.closest('.dialog-box');
var inDlgEdit=e.target&&e.target.closest&&e.target.closest('.dialog-edit-popup');
var inDlgFont=e.target&&e.target.closest&&e.target.closest('.dialog-font-popup');
if(inDlgEdit||inDlgFont)return;
if(inDlg)return;
for(var i=0;i<dialogBoxes.length;i++){setDialogEditing(dialogBoxes[i],false);}
setActiveDialogBox(null,false);
closeDialogEditPopup();
closeDialogFontPopup();
});
document.addEventListener('selectionchange',function(){
var box=getDialogById(dialogActiveId);
if(!box||!box.editing||!box.body)return;
if(saveDialogSelection(box)&&dialogEditBoxId===box.id)syncDialogEditPopup(box);
});
document.addEventListener('keydown',function(e){
if(e.key==='Escape'){
dialogConnectPendingId=null;
dialogAddArmed=false;
hideDialogPreview();
for(var i=0;i<dialogBoxes.length;i++){setDialogEditing(dialogBoxes[i],false);}
setActiveDialogBox(null,false);
closeDialogEditPopup();
closeDialogFontPopup();
}
});
}

// Initialize camera quaternion from default spherical angles
(function(){
const t=Math.PI/4,p=Math.PI/4;
const x=camDist*Math.sin(p)*Math.cos(t);
const y=camDist*Math.cos(p);
const z=camDist*Math.sin(p)*Math.sin(t);
const m=new THREE.Matrix4();
m.lookAt(new THREE.Vector3(x,y,z),new THREE.Vector3(0,0,0),new THREE.Vector3(0,1,0));
camQuat.setFromRotationMatrix(m);
})();

function createRendererWithFallback(canvas,w,h){
var tries=[
{antialias:true,preserveDrawingBuffer:true},
{antialias:false,preserveDrawingBuffer:true},
{antialias:false,preserveDrawingBuffer:false}
];
var lastErr=null;
for(var i=0;i<tries.length;i++){
try{
var o=tries[i];
var r=new THREE.WebGLRenderer({canvas:canvas,antialias:o.antialias,preserveDrawingBuffer:o.preserveDrawingBuffer,powerPreference:'high-performance'});
r.setPixelRatio(getRenderPixelRatio());
r.setSize(w,h);
r.autoClear=false;
r.localClippingEnabled=true;
if(i>0)console.warn('WebGL fallback renderer mode',o);
return r;
}catch(e){lastErr=e;}
}
throw (lastErr||new Error('WebGL renderer creation failed'));
}

function disposeUndeformedOverlay(){
if(uMs){try{sc.remove(uMs);uMs.geometry.dispose();uMs.material.dispose();}catch(e){}uMs=null;}
if(uEg){try{sc.remove(uEg);uEg.geometry.dispose();uEg.material.dispose();}catch(e){}uEg=null;}
}
function buildUndeformedOverlay(useCuts){
disposeUndeformedOverlay();
var cuts=useCuts?getActiveCuts():null;
var g2=new THREE.BufferGeometry(),v2=[],visCount=0;
BF.forEach(function(f,bfi){
var bElem=BFE[bfi];
if(bElem!==undefined&&bElem!==null&&bElem>=0&&isElemHidden(bElem))return;
if(cuts&&!isFaceVisible(f,ON,cuts))return;
visCount++;
f.forEach(function(i){if(i>=0&&i<ON.length){v2.push(ON[i][0],ON[i][1],ON[i][2]);}});
});
if(v2.length===0)return;
g2.setAttribute('position',new THREE.Float32BufferAttribute(v2,3));
g2.computeVertexNormals();
uMs=new THREE.Mesh(g2,new THREE.MeshPhongMaterial({color:0xffffff,opacity:0.22,transparent:true,side:THREE.DoubleSide,flatShading:false,depthWrite:false}));
uMs.visible=showUndeformed;
uMs.renderOrder=-1;
sc.add(uMs);
if(visCount<=MAX_FULL_EDGES_FACE_COUNT){
uEg=new THREE.LineSegments(new THREE.EdgesGeometry(g2,15),new THREE.LineBasicMaterial({color:0x999999,opacity:0.3,transparent:true}));
uEg.visible=showUndeformed;
sc.add(uEg);
}
if(cutSectionProjectionOn&&anyCutEnabled())applyCutClipping();
}

function init(){
sc=new THREE.Scene();sc.background=new THREE.Color(0xefefef);
cvEl=document.getElementById('cv');
const w=getViewW(),h=window.innerHeight;
const aspect=w/h;
caPersp=new THREE.PerspectiveCamera(45,aspect,0.1,B*100);
const frustumSize=B*2;
caOrtho=new THREE.OrthographicCamera(frustumSize*aspect/-2,frustumSize*aspect/2,frustumSize/2,frustumSize/-2,0.1,B*100);
ca=caOrtho;
uc();
re=createRendererWithFallback(cvEl,w,h);
computeMeshBBox();
sc.add(new THREE.AmbientLight(0xffffff,0.5));
const d1=new THREE.DirectionalLight(0xffffff,0.7);d1.position.set(B,B,B);sc.add(d1);
const d2=new THREE.DirectionalLight(0xffffff,0.3);d2.position.set(-B,-B,B);sc.add(d2);

// Axes HUD - separate scene rendered in bottom-left viewport
axScene=new THREE.Scene();
axCamera=new THREE.PerspectiveCamera(50,1,0.1,100);
axScene.add(new THREE.AmbientLight(0xffffff,0.7));
const axLight=new THREE.DirectionalLight(0xffffff,0.5);axLight.position.set(3,3,3);axScene.add(axLight);
axHelper=createAxes(0.8);
axScene.add(axHelper);

// Create highlight sphere for node probing
(function(){
var hSize=B*0.002;
var hGeo=new THREE.SphereGeometry(hSize,8,8);
var hMat=new THREE.MeshBasicMaterial({color:0xff0000,depthTest:false});
highlightSphere=new THREE.Mesh(hGeo,hMat);
highlightSphere.visible=false;
highlightSphere.renderOrder=999;
sc.add(highlightSphere);
// Yellow sphere for measure node highlight
var mhGeo=new THREE.SphereGeometry(hSize,8,8);
var mhMat=new THREE.MeshBasicMaterial({color:0xFFD600,depthTest:false});
measHighlightSphere=new THREE.Mesh(mhGeo,mhMat);
measHighlightSphere.visible=false;
measHighlightSphere.renderOrder=999;
sc.add(measHighlightSphere);
})();

cvEl.onmousedown=e=>{
if(hideElemMode&&e.button===0){
var hRect=cvEl.getBoundingClientRect();
hideSelStart={x:e.clientX,y:e.clientY,rx:e.clientX-hRect.left,ry:e.clientY-hRect.top};
hideSelEnd=null;
if(!hideSelDiv)initHideSelectionOverlay();
hideSelDiv.style.display='none';
e.preventDefault();return;
}
if(zoomBoxMode&&e.button===0){
var rect=cvEl.getBoundingClientRect();
zoomBoxStart={x:e.clientX,y:e.clientY,rx:e.clientX-rect.left,ry:e.clientY-rect.top};
zoomBoxEnd=null;
if(!zoomBoxDiv)initZoomBoxOverlay();
zoomBoxDiv.style.display='none';
e.preventDefault();return;
}
if(!e.ctrlKey&&e.button===1){
toggleZoomBox();
e.preventDefault();return;
}
ctrlRotAxis=null;
if(e.ctrlKey){
if(e.button===0)ctrlRotAxis='z';
else if(e.button===1)ctrlRotAxis='y';
else if(e.button===2)ctrlRotAxis='x';
}
if(!ctrlRotAxis){
if(e.button===0)dr=true;
if(e.button===2)pn=true;
}else{
dr=false;mz=false;pn=false;
}
pm={x:e.clientX,y:e.clientY};
mouseDownPos={x:e.clientX,y:e.clientY};
e.preventDefault();
};
cvEl.onmousemove=e=>{
if(hideElemMode&&hideSelStart){
hideSelEnd={x:e.clientX,y:e.clientY};
if(hideSelDiv){
var hx1=Math.min(hideSelStart.x,hideSelEnd.x),hy1=Math.min(hideSelStart.y,hideSelEnd.y);
var hw=Math.abs(hideSelEnd.x-hideSelStart.x),hh=Math.abs(hideSelEnd.y-hideSelStart.y);
hideSelDiv.style.left=hx1+'px';hideSelDiv.style.top=hy1+'px';
hideSelDiv.style.width=hw+'px';hideSelDiv.style.height=hh+'px';
hideSelDiv.style.display=(hw>3||hh>3)?'block':'none';
}
return;
}
if(zoomBoxMode&&zoomBoxStart){
zoomBoxEnd={x:e.clientX,y:e.clientY};
if(zoomBoxDiv){
var x1=Math.min(zoomBoxStart.x,zoomBoxEnd.x),y1=Math.min(zoomBoxStart.y,zoomBoxEnd.y);
var w=Math.abs(zoomBoxEnd.x-zoomBoxStart.x),h=Math.abs(zoomBoxEnd.y-zoomBoxStart.y);
zoomBoxDiv.style.left=x1+'px';zoomBoxDiv.style.top=y1+'px';
zoomBoxDiv.style.width=w+'px';zoomBoxDiv.style.height=h+'px';
zoomBoxDiv.style.display=(w>3||h>3)?'block':'none';
}
return;
}
if(hideElemMode){
updateHideHoverHighlightFromClient(e.clientX,e.clientY);
}else if(hideHoverEdges){
clearHideHoverHighlight();
}
updateDialogPreviewFromEvent(e);
const dx=e.clientX-pm.x,dy=e.clientY-pm.y;
if(ctrlRotAxis&&!e.ctrlKey){
ctrlRotAxis=null;
}
if(ctrlRotAxis){
var ax=new THREE.Vector3(0,0,1);
var ang=0;
if(ctrlRotAxis==='z'){
ax.set(0,0,1);
ang=dx*0.005;
}else if(ctrlRotAxis==='y'){
ax.set(0,1,0);
ang=-dx*0.005;
}else{
ax.set(1,0,0);
ang=-dy*0.005;
}
const qA=new THREE.Quaternion().setFromAxisAngle(ax,ang);
camQuat.premultiply(qA);
camQuat.normalize();
uc();
}
if(!ctrlRotAxis&&dr){
// Orbit: rotate around camera-local up (horizontal) and right (vertical)
const up=new THREE.Vector3(0,1,0).applyQuaternion(camQuat);
const right=new THREE.Vector3(1,0,0).applyQuaternion(camQuat);
const qH=new THREE.Quaternion().setFromAxisAngle(up,-dx*0.005);
const qV=new THREE.Quaternion().setFromAxisAngle(right,-dy*0.005);
camQuat.premultiply(qH).premultiply(qV);
camQuat.normalize();
uc();
}
if(!ctrlRotAxis&&pn){
const ps=camDist*0.001;
const right=new THREE.Vector3(1,0,0).applyQuaternion(camQuat);
const up=new THREE.Vector3(0,1,0).applyQuaternion(camQuat);
tg.add(right.multiplyScalar(-dx*ps));
tg.add(up.multiplyScalar(dy*ps));
uc();
}
pm={x:e.clientX,y:e.clientY};
if(handleInvalidTooltipMove(e.clientX,e.clientY)){
if(highlightSphere)highlightSphere.visible=false;
if(measHighlightSphere)measHighlightSphere.visible=false;
highlightedNodeIdx=-1;
hoveredElemIdx=-1;
return;
}
// Measure highlight (priority) or Value probe on hover
if(!dr&&!pn&&ms){
var rect=cvEl.getBoundingClientRect();
mouseNDC.x=((e.clientX-rect.left)/rect.width)*2-1;
mouseNDC.y=-((e.clientY-rect.top)/rect.height)*2+1;
raycaster.setFromCamera(mouseNDC,ca);
var hits=raycaster.intersectObject(ms);
var pickNodes=getDisplayNodes();
if(measMode!=='off'){
// Measure mode: yellow highlight on nearest node, hide value tooltip
hideValueTooltip();
if(highlightSphere)highlightSphere.visible=false;
highlightedNodeIdx=-1;
hoveredElemIdx=-1;
if(hits.length>0){
var fi=hits[0].faceIndex;
var tri=visibleFaces[fi];
if(tri){
var d0=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[0]][0],pickNodes[tri[0]][1],pickNodes[tri[0]][2]));
var d1=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[1]][0],pickNodes[tri[1]][1],pickNodes[tri[1]][2]));
var d2=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[2]][0],pickNodes[tri[2]][1],pickNodes[tri[2]][2]));
var nearest=tri[0];if(d1<d0&&d1<d2)nearest=tri[1];else if(d2<d0&&d2<d1)nearest=tri[2];
if(measHighlightSphere&&nearest<pickNodes.length){
measHighlightSphere.position.set(pickNodes[nearest][0],pickNodes[nearest][1],pickNodes[nearest][2]);
measHighlightSphere.visible=true;
}
}else{if(measHighlightSphere)measHighlightSphere.visible=false;}
}else{if(measHighlightSphere)measHighlightSphere.visible=false;}
}else if(valueInfoVisible()&&(curColors||centroidRawColors)){
// Value probe mode
if(measHighlightSphere)measHighlightSphere.visible=false;
if(hits.length>0){
var fi=hits[0].faceIndex;
var tri=visibleFaces[fi];
if(tri){
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){
// Centroid mode: show element value
var ei=visibleFaceElemIdx[fi];
if(ei!==undefined&&ei<centroidRawColors.length){
hoveredElemIdx=ei;
var cv=centroidRawColors[ei];
var realVal=centroidDataMin+cv*(centroidDataMax-centroidDataMin);
var elemIdTxt='E'+(EIDS[ei]||ei);
showValueTooltip(elemIdTxt+': '+formatLegendDrivenValue(realVal,'N/A'),e.clientX,e.clientY,{kind:'elem',elemIdx:ei,rawValue:realVal,idText:elemIdTxt});
// Position highlight at face centroid
var cx=(pickNodes[tri[0]][0]+pickNodes[tri[1]][0]+pickNodes[tri[2]][0])/3;
var cy=(pickNodes[tri[0]][1]+pickNodes[tri[1]][1]+pickNodes[tri[2]][1])/3;
var cz=(pickNodes[tri[0]][2]+pickNodes[tri[1]][2]+pickNodes[tri[2]][2])/3;
if(highlightSphere){highlightSphere.position.set(cx,cy,cz);highlightSphere.visible=true;highlightedNodeIdx=-1;}
}else{hoveredElemIdx=-1;hideValueTooltip();if(highlightSphere)highlightSphere.visible=false;highlightedNodeIdx=-1;}
}else{
// Normal nodal mode
hoveredElemIdx=-1;
var d0=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[0]][0],pickNodes[tri[0]][1],pickNodes[tri[0]][2]));
var d1=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[1]][0],pickNodes[tri[1]][1],pickNodes[tri[1]][2]));
var d2=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[2]][0],pickNodes[tri[2]][1],pickNodes[tri[2]][2]));
var nearest=tri[0];if(d1<d0&&d1<d2)nearest=tri[1];else if(d2<d0&&d2<d1)nearest=tri[2];
var nv=rawColors?rawColors[nearest]:curColors[nearest];
if(nv!==undefined&&nv!==null){
var realVal=dataMin+nv*(dataMax-dataMin);
var nodeIdTxt='N'+(NIDS[nearest]||nearest);
showValueTooltip(nodeIdTxt+': '+formatLegendDrivenValue(realVal,'N/A'),e.clientX,e.clientY,{kind:'node',elemIdx:visibleFaceElemIdx[fi],rawValue:realVal,idText:nodeIdTxt});
if(highlightSphere&&nearest<pickNodes.length){highlightSphere.position.set(pickNodes[nearest][0],pickNodes[nearest][1],pickNodes[nearest][2]);highlightSphere.visible=true;highlightedNodeIdx=nearest;}
}else{hideValueTooltip();if(highlightSphere)highlightSphere.visible=false;highlightedNodeIdx=-1;}
}
}else{hideValueTooltip();if(highlightSphere)highlightSphere.visible=false;highlightedNodeIdx=-1;}
}else{hoveredElemIdx=-1;hideValueTooltip();if(highlightSphere)highlightSphere.visible=false;highlightedNodeIdx=-1;}
}else{
if(measHighlightSphere)measHighlightSphere.visible=false;
hoveredElemIdx=-1;
}
}
};
cvEl.onmouseup=e=>{
if(hideElemMode&&hideSelStart&&e.button===0){
if(hideSelDiv)hideSelDiv.style.display='none';
var hRect=cvEl.getBoundingClientRect();
var hrx1=hideSelStart.rx;
var hry1=hideSelStart.ry;
var hrx2=(hideSelEnd?hideSelEnd.x:e.clientX)-hRect.left;
var hry2=(hideSelEnd?hideSelEnd.y:e.clientY)-hRect.top;
var hbw=Math.abs(hrx2-hrx1),hbh=Math.abs(hry2-hry1);
if(hbw>8&&hbh>8){
var elemsInBox=getVisibleElementsInScreenBox(hrx1,hry1,hrx2,hry2);
applyHideElementsSelection(elemsInBox,true);
}else{
var pickedElem=(hideHoverElemIdx>=0&&isElemVisibleNow(hideHoverElemIdx))?hideHoverElemIdx:pickVisibleElementFromClient(e.clientX,e.clientY);
if(pickedElem>=0)applyHideElementsSelection([pickedElem],false);
else document.getElementById('st').textContent='Hide Elements: click on a visible element';
}
clearHideSelectionOverlay();
clearHideHoverHighlight();
dr=false;mz=false;
return;
}
if(zoomBoxMode&&zoomBoxStart&&e.button===0){
if(zoomBoxDiv)zoomBoxDiv.style.display='none';
if(zoomBoxEnd){
var rect=cvEl.getBoundingClientRect();
var x1=Math.min(zoomBoxStart.x,zoomBoxEnd.x)-rect.left;
var y1=Math.min(zoomBoxStart.y,zoomBoxEnd.y)-rect.top;
var x2=Math.max(zoomBoxStart.x,zoomBoxEnd.x)-rect.left;
var y2=Math.max(zoomBoxStart.y,zoomBoxEnd.y)-rect.top;
var bw=x2-x1,bh=y2-y1;
if(bw>10&&bh>10){
// Calculate NDC center of the box
var cxNDC=((x1+x2)/2/rect.width)*2-1;
var cyNDC=-((y1+y2)/2/rect.height)*2+1;
// Unproject box center to find new target
var dir=new THREE.Vector3(cxNDC,cyNDC,0.5).unproject(ca).sub(ca.position).normalize();
// Move target along ray by current distance
var newTarget=ca.position.clone().add(dir.multiplyScalar(camDist));
tg.copy(newTarget);
// Zoom factor based on box size vs viewport size
var zf=Math.max(bw/rect.width,bh/rect.height);
if(zf>0.01)camDist*=zf;
camDist=Math.max(B*0.1,Math.min(B*80,camDist));
uc();
document.getElementById('st').textContent='Zoom box applied';
}
}
zoomBoxStart=null;zoomBoxEnd=null;
toggleZoomBox();
return;
}
if(e.button===0){
var dx=Math.abs(e.clientX-mouseDownPos.x),dy=Math.abs(e.clientY-mouseDownPos.y);
var pickNodes=getDisplayNodes();
if(dx<5&&dy<5&&dialogConnectPendingId!==null){
var bConn=getDialogById(dialogConnectPendingId);
var niConn=pickNearestNodeFromClient(e.clientX,e.clientY);
if(bConn&&niConn>=0){
bConn.nodeIdx=niConn;
refreshDialogConnectButton(bConn);
document.getElementById('st').textContent='Dialog '+bConn.id+' connected to node N'+(NIDS[niConn]||niConn);
updateDialogBoxesVisuals();
}else{
document.getElementById('st').textContent='Connection failed: click a visible node';
}
dialogConnectPendingId=null;
dr=false;mz=false;
return;
}
if(dx<5&&dy<5&&dialogMode&&dialogAddArmed){
var nb=createDialogBoxAtClient(e.clientX,e.clientY);
dialogAddArmed=false;
hideDialogPreview();
if(nb){document.getElementById('st').textContent='Dialog '+nb.id+' created';}
else{document.getElementById('st').textContent='Dialog not created: click inside mesh area';}
dr=false;mz=false;
return;
}
if(dx<5&&dy<5&&measMode!=='off'&&ms){
var rect=cvEl.getBoundingClientRect();
mouseNDC.x=((e.clientX-rect.left)/rect.width)*2-1;
mouseNDC.y=-((e.clientY-rect.top)/rect.height)*2+1;
raycaster.setFromCamera(mouseNDC,ca);
var hits=raycaster.intersectObject(ms);
if(hits.length>0){
var fi=hits[0].faceIndex;
var tri=visibleFaces[fi];
if(tri){
var d0=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[0]][0],pickNodes[tri[0]][1],pickNodes[tri[0]][2]));
var d1=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[1]][0],pickNodes[tri[1]][1],pickNodes[tri[1]][2]));
var d2=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[2]][0],pickNodes[tri[2]][1],pickNodes[tri[2]][2]));
var nearest=tri[0];if(d1<d0&&d1<d2)nearest=tri[1];else if(d2<d0&&d2<d1)nearest=tri[2];
onMeasClick(nearest);
}
}
}
// Pin value on click when Values is ON and Measure is OFF
if(dx<5&&dy<5&&showValues&&measMode==='off'&&!tableLinksActive()&&ms&&(curColors||centroidRawColors)){
var rect=cvEl.getBoundingClientRect();
mouseNDC.x=((e.clientX-rect.left)/rect.width)*2-1;
mouseNDC.y=-((e.clientY-rect.top)/rect.height)*2+1;
raycaster.setFromCamera(mouseNDC,ca);
var hits=raycaster.intersectObject(ms);
if(hits.length>0){
var fi=hits[0].faceIndex;
var tri=visibleFaces[fi];
if(tri){
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){
// Pin element in centroid mode
var ei=hoveredElemIdx>=0?hoveredElemIdx:visibleFaceElemIdx[fi];
if(ei!==undefined&&ei>=0)pinElemValue(ei,fi);
}else{
var d0=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[0]][0],pickNodes[tri[0]][1],pickNodes[tri[0]][2]));
var d1=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[1]][0],pickNodes[tri[1]][1],pickNodes[tri[1]][2]));
var d2=hits[0].point.distanceTo(new THREE.Vector3(pickNodes[tri[2]][0],pickNodes[tri[2]][1],pickNodes[tri[2]][2]));
var nearest=tri[0];if(d1<d0&&d1<d2)nearest=tri[1];else if(d2<d0&&d2<d1)nearest=tri[2];
pinNodeValue(nearest);
}
}
}
}
dr=false;mz=false;}
if(e.button===1)mz=false;
if(e.button===2)pn=false;
if((e.button===0&&ctrlRotAxis==='z')||(e.button===1&&ctrlRotAxis==='y')||(e.button===2&&ctrlRotAxis==='x'))ctrlRotAxis=null;
};
cvEl.oncontextmenu=e=>e.preventDefault();
cvEl.onauxclick=e=>e.preventDefault();
cvEl.onmouseleave=function(){ctrlRotAxis=null;valTooltipInvalidUntilMove=false;hideValueTooltip();if(highlightSphere)highlightSphere.visible=false;if(measHighlightSphere)measHighlightSphere.visible=false;highlightedNodeIdx=-1;hoveredElemIdx=-1;hideDialogPreview();clearHideSelectionOverlay();clearHideHoverHighlight();};
cvEl.onwheel=e=>{e.preventDefault();camDist*=e.deltaY>0?1.1:0.9;camDist=Math.max(B*0.1,Math.min(B*80,camDist));uc()};
window.onresize=onResize;
if(!legendOutsideDblInit){
document.addEventListener('dblclick',function(e){
if(!legendEditMode)return;
var leg=document.getElementById('color-legend');
if(leg&&leg.contains(e.target))return;
exitLegendEdit();
document.getElementById('st').textContent='Legend edit mode off';
});
legendOutsideDblInit=true;
}
safeViewerInitStep('increment list',function(){pss();});
var ssEl=document.getElementById('ss');
if(ssEl&&ssEl.options&&ssEl.options.length<=1)safeViewerInitStep('increment list fallback',function(){pssFallback();});
safeViewerInitStep('output ui',function(){refreshDisplacementComponentUi();});
safeViewerInitStep('extrapolation ui',function(){refreshExtrapolationSummary();});
safeViewerInitStep('legend values',function(){ulv(curMin,curMax);});
safeViewerInitStep('legend format controls',function(){updateLegendFormatControls();});
safeViewerInitStep('animation range labels',function(){ugrl();});
safeViewerInitStep('rotation cut ui',function(){updateRotationCutUi(cutPlanes.rotation);});
safeViewerInitStep('dialog box system',function(){initDialogBoxSystem();});
safeViewerInitStep('sidebar cards',function(){initSidebarCards();});
safeViewerInitStep('hide connected button',function(){refreshHideAllConnectedButton();});
safeViewerInitStep('legend extreme buttons',function(){refreshLegendExtremeButtons();});
safeViewerInitStep('animation mode button',function(){refreshAnimHarmonicButton();});
safeViewerInitStep('edge mode availability',function(){syncAllEdgesOptionAvailability();});
refreshExtrapolationSummary();
captureBaseHtmlForSaveFile();
safeViewerInitStep('xy sheet tabs',function(){xyRenderSheetTabs();});
safeViewerInitStep('xy animation info button',function(){xyRefreshAnimInfoButton();});
safeViewerInitStep('table form links button',function(){refreshTableFormLinksButton();});
safeViewerInitStep('xy font controls',function(){xyUpdateFontControls();});
if(!xyFontPopupInit){
document.addEventListener('mousedown',function(e){
var pop=document.getElementById('xy-font-popup');
if(!pop||pop.style.display!=='block')return;
var btn=document.getElementById('xy-font-btn');
if((btn&&btn.contains(e.target))||pop.contains(e.target))return;
xyToggleFontPopup(false);
});
window.addEventListener('resize',function(){xyPositionFontPopup();});
var xyCtr=document.getElementById('xy-controls');
if(xyCtr){
xyCtr.addEventListener('scroll',function(){
var pop=document.getElementById('xy-font-popup');
if(pop&&pop.style.display==='block')xyPositionFontPopup();
});
}
xyFontPopupInit=true;
}
// Pre-load GIF worker for file:// compatibility
try{
fetch('https://cdnjs.cloudflare.com/ajax/libs/gif.js/0.2.0/gif.worker.js')
.then(function(r){return r.text();})
.then(function(txt){gifWorkerUrl=URL.createObjectURL(new Blob([txt],{type:'application/javascript'}));
console.log('GIF worker loaded');})
.catch(function(e){console.warn('GIF worker load failed:',e);});
}catch(e){}
setTimeout(function(){
safeViewerInitStep('initial mesh load',function(){
if(IS&&hasStateData(currentVar,IS)){
document.getElementById('ss').value=IS;
osc();
}else{
cm(ON,getInitialColors());
}
});
},40);
an();
}

function createAxes(size){
const g=new THREE.Group();
const orig=new THREE.Vector3(0,0,0);
function mkLine(dir,color,label){
const endPt=new THREE.Vector3(dir[0]*size,dir[1]*size,dir[2]*size);
const geo=new THREE.BufferGeometry().setFromPoints([orig,endPt]);
const mat=new THREE.LineBasicMaterial({color:color,linewidth:2});
g.add(new THREE.Line(geo,mat));
// Thicker line using thin cylinder for visibility
const cylLen=size*0.85;
const cylGeo=new THREE.CylinderGeometry(size*0.02,size*0.02,cylLen,6);
const cylMat=new THREE.MeshBasicMaterial({color:color});
const cyl=new THREE.Mesh(cylGeo,cylMat);
cyl.position.set(dir[0]*cylLen/2,dir[1]*cylLen/2,dir[2]*cylLen/2);
if(dir[0]===1){cyl.rotation.z=Math.PI/2;}
else if(dir[2]===1){cyl.rotation.x=Math.PI/2;}
g.add(cyl);
// Arrowhead cone
const coneGeo=new THREE.ConeGeometry(size*0.08,size*0.22,8);
const coneMat=new THREE.MeshBasicMaterial({color:color});
const cone=new THREE.Mesh(coneGeo,coneMat);
cone.position.copy(endPt);
if(dir[0]===1)cone.rotation.z=-Math.PI/2;
else if(dir[2]===1)cone.rotation.x=Math.PI/2;
g.add(cone);
// Label sprite - sizeAttenuation:true for HUD (world-space sizing)
const canvas=document.createElement('canvas');canvas.width=64;canvas.height=64;
const ctx=canvas.getContext('2d');
ctx.clearRect(0,0,64,64);
ctx.fillStyle=color===0xff0000?'#ff0000':(color===0x00cc00?'#00cc00':'#0066ff');
ctx.font='bold 52px Arial';ctx.textAlign='center';ctx.textBaseline='middle';
ctx.fillText(label,32,32);
const tex=new THREE.CanvasTexture(canvas);
const spriteMat=new THREE.SpriteMaterial({map:tex,sizeAttenuation:true,transparent:true,depthTest:false});
const sprite=new THREE.Sprite(spriteMat);
sprite.scale.set(0.5,0.5,1);
sprite.position.set(dir[0]*size*1.35,dir[1]*size*1.35,dir[2]*size*1.35);
g.add(sprite);
}
mkLine([1,0,0],0xff0000,'X');
mkLine([0,1,0],0x00cc00,'Y');
mkLine([0,0,1],0x0066ff,'Z');
return g;
}

function onResize(){
const w=getViewW(),h=window.innerHeight;
const pw=getPlotW();
const aspect=w/h;
caPersp.aspect=aspect;caPersp.updateProjectionMatrix();
const frustumSize=B*2;
caOrtho.left=frustumSize*aspect/-2;caOrtho.right=frustumSize*aspect/2;
caOrtho.top=frustumSize/2;caOrtho.bottom=frustumSize/-2;
caOrtho.updateProjectionMatrix();re.setPixelRatio(getRenderPixelRatio());re.setSize(w,h);
// Reposition nav buttons centered in 3D area
var nb=document.getElementById('nav-buttons');
if(nb)nb.style.left=(320+w/2)+'px';
// Reposition color legend
var cl=document.getElementById('color-legend');
if(cl)cl.style.left='340px';
// Reposition help overlay
var ho=document.getElementById('help-overlay');
if(ho)ho.style.right=(pw+15)+'px';
// Reposition watermark
var wm=document.getElementById('watermark');
if(wm)wm.style.right=(pw+15)+'px';
// Reposition file title (centered in 3D manipulation area, above watermark bar)
var fto=document.getElementById('file-title-overlay');
if(fto)fto.style.left=(320+w/2)+'px';
// Reposition status bar
var st=document.getElementById('st');
if(st)st.style.right=pw+'px';
// XY panel width
var xp=document.getElementById('xy-panel');
if(xp)xp.style.width=pw+'px';
// Resize plot canvas
if(xyPlotVisible)xyResizePlot();
updateDialogBoxesVisuals();
}

function tgp(usePersp){isPerspective=usePersp;ca=isPerspective?caPersp:caOrtho;uc();
document.getElementById('st').textContent=isPerspective?'Perspective view':'Orthographic view';}

function tga(show){showAxes=show;}
function tgu(show){
showUndeformed=show;
if(!show){
if(uMs)uMs.visible=false;
if(uEg)uEg.visible=false;
return;
}
var hasCuts=anyCutEnabled();
if(!uMs||hasCuts){
buildUndeformedOverlay(hasCuts);
}
if(uMs)uMs.visible=true;
if(uEg)uEg.visible=true;
}
function valueInfoVisible(){return showValues;}
function pinnedValueWindowsVisible(){return showValues||pinnedNodes.length>0||pinnedElems.length>0;}
function setValueWindowsVisible(on){
var bar=document.getElementById('val-lookup-bar');if(bar)bar.style.display=on?'block':'none';
if(!on){
valTooltipInvalidUntilMove=false;
hideValueTooltip();
if(highlightSphere)highlightSphere.visible=false;highlightedNodeIdx=-1;
}
var win=document.getElementById('table-form-window');
if(tableFormVisible){
if(win)win.style.display='flex';
updateTableForm();
}else if(win){
win.style.display='none';
}
refreshTableFormLinksButton();
updatePinnedPositions();
updateDialogBoxesVisuals();
}
function updateValueWindowsForCut(){
if(tableFormVisible)updateTableForm();
}
function tgv(show){showValues=show;setValueWindowsVisible(show);updateValueWindowsForCut();}

function valLookup(){
var inp=document.getElementById('val-lookup-input').value.trim();
if(!inp){document.getElementById('st').textContent='Enter node or element IDs (use real IDs)';return;}
var parts=inp.split(/[,;\s]+/);
var nPinned=0,ePinned=0,errors=[];
parts.forEach(function(p){
p=p.trim();if(!p)return;
var isElem=false;
var modeChar=p.toUpperCase().charAt(0);
var forceNode=(modeChar==='N');
if(modeChar==='E'||modeChar==='N'){isElem=(modeChar==='E');p=p.substring(1);}
var id=parseInt(p);
if(isNaN(id)||id<0){errors.push(p);return;}
if(isElem||centroidMode||(isElementLocalContourMode()&&!forceNode)){
// Pin element - convert real ID to array index
var eidx=realElemIdToIdx(id);
if(eidx>=0&&centroidRawColors&&eidx<centroidRawColors.length&&isElemVisibleNow(eidx)){
var already=false;
for(var i=0;i<pinnedElems.length;i++){if(pinnedElems[i]===eidx){already=true;break;}}
if(!already){pinElemValue(eidx,0);ePinned++;}
}else{errors.push('E'+id);}
}else{
// Pin node - convert real ID to array index
var nidx=realNodeIdToIdx(id);
if(nidx>=0&&nidx<cn.length&&isNodeVisibleNow(nidx)){
var already=false;
for(var i=0;i<pinnedNodes.length;i++){if(pinnedNodes[i]===nidx){already=true;break;}}
if(!already){pinNodeValue(nidx);nPinned++;}
}else{errors.push('N'+id);}
}
});
var msg=[];
if(nPinned>0)msg.push(nPinned+' node'+(nPinned>1?'s':''));
if(ePinned>0)msg.push(ePinned+' element'+(ePinned>1?'s':''));
var result=msg.length>0?msg.join(' + ')+' pinned':'No items pinned';
if(errors.length>0)result+=' (invalid: '+errors.join(', ')+')';
document.getElementById('st').textContent=result;
document.getElementById('val-lookup-input').value='';
showTableFormIfMultiple();
}

// ==================== TABLE FORM ====================
let tableFormVisible=false;
let tableFormLinksOn=false;
let tfResizeObserver=null;
function tableLinksActive(){return tableFormVisible&&tableFormLinksOn;}
function fitTableFormCellsToWindow(){
var win=document.getElementById('table-form-window');
var body=document.getElementById('table-form-body');
if(!win||!body)return;
var table=document.getElementById('table-form-table');
if(!table)return;
table.style.width='100%';
table.style.tableLayout='fixed';
var ths=table.querySelectorAll('thead th');
if(ths&&ths.length>=2){
ths[0].style.width='42%';
ths[1].style.width='58%';
}
var tbody=(table.tBodies&&table.tBodies.length>0)?table.tBodies[0]:null;
if(!tbody)return;
var trs=tbody.querySelectorAll('tr');
if(!trs||trs.length===0)return;
var headH=table.tHead?table.tHead.getBoundingClientRect().height:0;
var bodyH=Math.max(24,body.clientHeight-8);
var availRows=Math.max(12,bodyH-headH);
var baseH=Math.max(1,Math.floor(availRows/trs.length));
var rem=Math.max(0,availRows-baseH*trs.length);
body.style.overflowY='hidden';
for(var i=0;i<trs.length;i++){
var hPx=baseH+(i<rem?1:0);
trs[i].style.height=hPx+'px';
var tds=trs[i].querySelectorAll('td');
for(var j=0;j<tds.length;j++)tds[j].style.height=hPx+'px';
}
}
function applyTableFormFontSize(){
var win=document.getElementById('table-form-window');
if(!win)return;
var fs=Math.max(8,Math.min(18,tableFormFontSize||10));
win.style.setProperty('--tf-font-size',fs+'px');
win.style.setProperty('--tf-head-size',Math.max(8,fs-1)+'px');
}
function setTableFormFont(v){
var n=parseInt(v,10);
if(!isFinite(n))n=tableFormFontSize;
n=Math.max(8,Math.min(18,n));
tableFormFontSize=n;
var inp=document.getElementById('table-form-font');
if(inp&&String(inp.value)!==String(n))inp.value=String(n);
var val=document.getElementById('table-form-font-val');
if(val)val.textContent=String(n);
applyTableFormFontSize();
fitTableFormCellsToWindow();
}
function refreshTableFormLinksButton(){
var wrap=document.getElementById('table-form-links-wrap');
var btn=document.getElementById('table-form-links-btn');
var fontRow=document.getElementById('table-form-font-row');
if(fontRow)fontRow.style.display=tableFormVisible?'flex':'none';
if(!wrap||!btn){
if(tableFormVisible)applyTableFormFontSize();
if(tableFormVisible)fitTableFormCellsToWindow();
return;
}
if(!tableFormVisible){
wrap.style.display='none';
tableFormLinksOn=false;
}else{
wrap.style.display='inline-flex';
}
btn.textContent=tableFormLinksOn?'On':'Off';
btn.className='xy-toggle-btn '+(tableFormLinksOn?'on':'off');
if(tableFormVisible)applyTableFormFontSize();
if(tableFormVisible)fitTableFormCellsToWindow();
}
function tgTableFormLinks(force){
var on=(force===undefined)?!tableFormLinksOn:!!force;
if(!tableFormVisible)on=false;
tableFormLinksOn=on;
refreshTableFormLinksButton();
updatePinnedPositions();
updateDialogBoxesVisuals();
document.getElementById('st').textContent='Table Form Links: '+(tableFormLinksOn?'On':'Off');
}
function tgTableForm(on){
tableFormVisible=on;
var win=document.getElementById('table-form-window');
var row=document.getElementById('table-form-row');
win.style.display=on?'flex':'none';
if(on){
// Pre-fill with currently pinned nodes/elements
var ids=[];
tfIdTypeHint={};
pinnedNodes.forEach(function(n){
var rid=''+(NIDS[n]!==undefined?NIDS[n]:n);
ids.push(rid);
tfIdTypeHint[rid]='N';
});
pinnedElems.forEach(function(e){
var rid=''+(EIDS[e]!==undefined?EIDS[e]:e);
ids.push(rid);
tfIdTypeHint[rid]='E';
});
document.getElementById('table-form-ids').value=ids.join(',');
updateTableForm();
}
if(!on)tgTableFormLinks(false);
refreshTableFormLinksButton();
}
function tfUpdateTableForm(){
if(!tableFormVisible){
document.getElementById('st').textContent='Enable Table Form first';
return;
}
var cb=document.getElementById('table-form-cb');
tgTableForm(false);
tgTableForm(true);
if(cb)cb.checked=true;
document.getElementById('st').textContent='Table Form updated';
}
function showTableFormIfMultiple(){
// Show table form checkbox if more than 1 item pinned
var total=pinnedNodes.length+pinnedElems.length;
var row=document.getElementById('table-form-row');
if(row)row.style.display=total>1?'block':'none';
if(!tableFormVisible)refreshTableFormLinksButton();
if(tableFormVisible)updateTableForm();
}
function getColorForNormVal(normVal,realVal){
var c=null;
if(realVal!==undefined&&realVal!==null){
c=getLegendColorFromReal(realVal);
}
if(!c){
normVal=clamp01(normVal);
c=gc(normVal);
}
var r=Math.round(c.r*255),g=Math.round(c.g*255),b=Math.round(c.b*255);
return 'rgb('+r+','+g+','+b+')';
}
function updateTableForm(){
applyTableFormFontSize();
var inpEl=document.getElementById('table-form-ids');
var inp=inpEl.value.trim();
var body=document.getElementById('table-form-body');
var parts=inp?inp.split(/[,;\s]+/):[];
var rows=[];var items=[];var seen={};
var dispNodes=getDisplayNodes();
var cuts=getActiveCuts();
var hasCuts=cuts.length>0;
function addItem(id,isElem){
var key=(isElem?'E':'N')+id;
if(seen[key])return;
seen[key]=true;items.push({id:id,isElem:isElem});
}
parts.forEach(function(p){
p=p.trim();if(!p)return;
var isElem=false;
var p0=p.toUpperCase().charAt(0);
if(p0==='E'||p0==='N'){isElem=(p0==='E');p=p.substring(1);}
var id=parseInt(p);
if(isNaN(id)||id<0)return;
if((centroidMode||isElementLocalContourMode())&&p0!=='N'&&!isElem)isElem=true;
if(!(centroidMode||isElementLocalContourMode())&&p0!=='E'&&p0!=='N'){
var hint=tfIdTypeHint[String(id)];
if(hint==='E')isElem=true;
}
// Convert real ID to array index
if(isElem){var idx=realElemIdToIdx(id);if(idx>=0)addItem(idx,isElem);}
else{var idx=realNodeIdToIdx(id);if(idx>=0)addItem(idx,isElem);}
});
if(centroidMode||isElementLocalContourMode()){
pinnedElems.forEach(function(e){addItem(e,true);});
}else{
pinnedNodes.forEach(function(n){addItem(n,false);});
pinnedElems.forEach(function(e){addItem(e,true);});
}
if(legendMaxMode&&legendMaxTarget){
if(legendMaxTarget.type==='elem')addItem(legendMaxTarget.idx,true);
else addItem(legendMaxTarget.idx,false);
}
if(legendMinMode&&legendMinTarget){
if(legendMinTarget.type==='elem')addItem(legendMinTarget.idx,true);
else addItem(legendMinTarget.idx,false);
}
if(items.length===0){
body.innerHTML=inp?'<div style="text-align:center;color:#999;padding:10px;font-size:10px">No valid IDs found</div>':'<div style="text-align:center;color:#999;padding:10px;font-size:10px">Enter IDs above</div>';
return;}
tfIdTypeHint={};
inpEl.value=items.map(function(it){
var rid=it.isElem?(EIDS[it.id]!==undefined?EIDS[it.id]:it.id):(NIDS[it.id]!==undefined?NIDS[it.id]:it.id);
tfIdTypeHint[String(rid)]=it.isElem?'E':'N';
return ''+rid;
}).join(',');
items.forEach(function(it){
var id=it.id;var isElem=it.isElem;
if(isElem){
if(!isElemVisibleNow(id))return;
if(centroidRawColors&&id<centroidRawColors.length){
var cv=centroidRawColors[id];
var realVal=centroidDataMin+cv*(centroidDataMax-centroidDataMin);
var uR=curMax-curMin;if(Math.abs(uR)<1e-30)uR=1;
var normMapped=Math.max(0,Math.min(1,(realVal-curMin)/uR));
var bgColor=getColorForNormVal(normMapped,realVal);
var ctr=getElemCentroid3D(id);
if(!hasCuts||(ctr&&isPointVisibleByCuts([ctr.x,ctr.y,ctr.z],cuts)))rows.push({label:''+(EIDS[id]!==undefined?EIDS[id]:id),isElem:true,srcIdx:id,value:realVal,bgColor:bgColor});
}else{rows.push({label:''+(EIDS[id]!==undefined?EIDS[id]:id),isElem:true,srcIdx:id,value:null,bgColor:'#eee'});}
}else{
if(id<dispNodes.length){
if(!isNodeVisibleNow(id))return;
var nv=rawColors?rawColors[id]:(curColors?curColors[id]:null);
var realVal=(nv!==undefined&&nv!==null)?dataMin+nv*(dataMax-dataMin):null;
var bgColor='#eee';
if(realVal!==null){
var uR=curMax-curMin;if(Math.abs(uR)<1e-30)uR=1;
var normMapped=Math.max(0,Math.min(1,(realVal-curMin)/uR));
bgColor=getColorForNormVal(normMapped,realVal);
}
if(!hasCuts||isPointVisibleByCuts(dispNodes[id],cuts))rows.push({label:''+(NIDS[id]!==undefined?NIDS[id]:id),isElem:false,srcIdx:id,value:realVal,bgColor:bgColor});
}else{rows.push({label:''+(NIDS[id]!==undefined?NIDS[id]:id),isElem:false,srcIdx:id,value:null,bgColor:'#eee'});}
}
});
rows.sort(function(a,b){
var av=(a.value!==null&&a.value!==undefined&&isFinite(a.value))?a.value:null;
var bv=(b.value!==null&&b.value!==undefined&&isFinite(b.value))?b.value:null;
if(av===null&&bv===null)return 0;
if(av===null)return 1;
if(bv===null)return -1;
return bv-av;
});
if(rows.length===0){
body.innerHTML=(hasCuts||countHiddenElements()>0)?'<div style="text-align:center;color:#999;padding:10px;font-size:10px">All IDs hidden by cut or Hide Elements</div>':'<div style="text-align:center;color:#999;padding:10px;font-size:10px">No valid IDs found</div>';
return;}
var allElem=true,allNode=true;
rows.forEach(function(r){if(r.isElem)allNode=false;else allElem=false;});
var idHeader='ID - Node';
if(allElem)idHeader='ID - Element';
var html='<table id="table-form-table"><thead><tr><th data-col="0">'+idHeader+'</th><th data-col="1">Value ('+currentVar+')</th></tr></thead><tbody>';
rows.forEach(function(r,rowIdx){
var valStr=(r.value!==null)?formatLegendDrivenValue(r.value,'N/A'):'N/A';
var textColor=(r.value!==null)?getContrastColor(r.bgColor):'#333';
var rKind=r.isElem?'E':'N';
var rIdx=(r.srcIdx!==undefined&&r.srcIdx!==null)?r.srcIdx:-1;
html+='<tr data-row="'+rowIdx+'" data-kind="'+rKind+'" data-idx="'+rIdx+'"><td data-row="'+rowIdx+'" data-col="0" style="background:#f5f5f5;font-weight:bold;color:#333">'+r.label+'</td>';
html+='<td data-row="'+rowIdx+'" data-col="1" style="background:'+r.bgColor+';color:'+textColor+'">'+valStr+'</td></tr>';
});
html+='</tbody></table>';
body.innerHTML=html;
tfBindTableInteractions();
fitTableFormCellsToWindow();
}
function getContrastColor(rgbStr){
var m=rgbStr.match(/\d+/g);
if(!m||m.length<3)return '#000';
var r=parseInt(m[0]),g=parseInt(m[1]),b=parseInt(m[2]);
var lum=(0.299*r+0.587*g+0.114*b)/255;
return lum>0.5?'#000':'#fff';
}
function tfClearColSelection(){
var table=document.getElementById('table-form-table');
if(!table)return;
table.querySelectorAll('th[data-col]').forEach(function(th){th.classList.remove('tf-col-sel');});
tfSelCols={id:false,val:false};
}
function tfClearCellSelection(){
var table=document.getElementById('table-form-table');
if(!table)return;
table.querySelectorAll('td.tf-cell-sel').forEach(function(td){td.classList.remove('tf-cell-sel');});
tfCellSel.active=false;
}
function tfClearRowSelection(){
var table=document.getElementById('table-form-table');
if(!table){tfRowSelIdx=-1;return;}
table.querySelectorAll('tr.tf-row-sel').forEach(function(tr){tr.classList.remove('tf-row-sel');});
tfRowSelIdx=-1;
}
function tfApplyRowSelection(rowIdx){
var table=document.getElementById('table-form-table');
if(!table)return;
tfClearRowSelection();
if(rowIdx===undefined||rowIdx===null||rowIdx<0)return;
var tr=table.querySelector('tbody tr[data-row="'+rowIdx+'"]');
if(!tr)return;
tr.classList.add('tf-row-sel');
tfRowSelIdx=rowIdx;
}
function tfCollectRowsForDelete(table){
var out=[];var seen={};
if(!table)return out;
table.querySelectorAll('tbody tr.tf-row-sel').forEach(function(tr){
var rk=tr.getAttribute('data-row');
if(rk===null||rk===undefined)rk='r'+out.length;
if(seen[rk])return;
seen[rk]=1;out.push(tr);
});
if(out.length>0)return out;
table.querySelectorAll('td.tf-cell-sel').forEach(function(td){
var tr=td&&td.closest?td.closest('tr[data-row]'):null;
if(!tr)return;
var rk=tr.getAttribute('data-row');
if(rk===null||rk===undefined)rk='r'+out.length;
if(seen[rk])return;
seen[rk]=1;out.push(tr);
});
return out;
}
function tfRemoveIdFromInput(kind,idx){
var inpEl=document.getElementById('table-form-ids');
if(!inpEl)return;
var rid=(kind==='E')?(EIDS[idx]!==undefined?EIDS[idx]:idx):(NIDS[idx]!==undefined?NIDS[idx]:idx);
var tokens=inpEl.value.trim()?inpEl.value.split(/[,;\s]+/):[];
var out=[];
tokens.forEach(function(tok){
var t=(tok||'').trim();
if(!t)return;
var p=t.toUpperCase().charAt(0);
var tk='',numTxt=t;
if(p==='E'||p==='N'){tk=p;numTxt=t.substring(1);}
var n=parseInt(numTxt,10);
if(isNaN(n)){out.push(t);return;}
if(n!==rid){out.push(t);return;}
if(tk&&tk!==kind){out.push(t);return;}
if(!tk){
var hint=tfIdTypeHint[String(n)];
if(hint&&hint!==kind){out.push(t);return;}
}
});
inpEl.value=out.join(',');
}
function tfDeleteSelectedRow(){
var table=document.getElementById('table-form-table');
if(!table){document.getElementById('st').textContent='Table Form has no rows to delete';return;}
var selected=tfCollectRowsForDelete(table);
if(!selected||selected.length===0){document.getElementById('st').textContent='Select one or more Table Form rows to delete';return;}
var targets=[];var seen=Object.create(null);
for(var si=0;si<selected.length;si++){
var tr=selected[si];
var kind=(tr.getAttribute('data-kind')||'N').toUpperCase();
var idx=parseInt(tr.getAttribute('data-idx'),10);
if(!isFinite(idx)||idx<0)continue;
var k=kind+':'+idx;
if(seen[k])continue;
seen[k]=1;
targets.push({kind:kind,idx:idx});
}
if(targets.length===0){document.getElementById('st').textContent='Selected rows are invalid';return;}
var removedPinned=0;
var legendChanged=false;
for(var ti=0;ti<targets.length;ti++){
var kind=targets[ti].kind;
var idx=targets[ti].idx;
if(kind==='E'){
for(var i=0;i<pinnedElems.length;i++){
if(pinnedElems[i]!==idx)continue;
if(pinnedElemMarkers[i])sc.remove(pinnedElemMarkers[i]);
if(pinnedElemLabels[i]&&pinnedElemLabels[i].parentNode)pinnedElemLabels[i].parentNode.removeChild(pinnedElemLabels[i]);
pinnedElems.splice(i,1);
pinnedElemMarkers.splice(i,1);
pinnedElemLabels.splice(i,1);
pinnedElemFaces.splice(i,1);
removedPinned++;
break;
}
}else{
for(var i=0;i<pinnedNodes.length;i++){
if(pinnedNodes[i]!==idx)continue;
if(pinnedMarkers[i])sc.remove(pinnedMarkers[i]);
if(pinnedLabels[i]&&pinnedLabels[i].parentNode)pinnedLabels[i].parentNode.removeChild(pinnedLabels[i]);
pinnedNodes.splice(i,1);
pinnedMarkers.splice(i,1);
pinnedLabels.splice(i,1);
removedPinned++;
break;
}
}
if(legendMaxMode&&legendMaxTarget&&legendMaxTarget.type===(kind==='E'?'elem':'node')&&legendMaxTarget.idx===idx){legendMaxMode=false;legendChanged=true;}
if(legendMinMode&&legendMinTarget&&legendMinTarget.type===(kind==='E'?'elem':'node')&&legendMinTarget.idx===idx){legendMinMode=false;legendChanged=true;}
tfRemoveIdFromInput(kind,idx);
}
if(legendChanged){
refreshLegendExtremeButtons();
updateLegendExtremaTargets();
}
tfClearCellSelection();
tfClearColSelection();
tfClearRowSelection();
if(tableFormLinksOn){
tableFormLinksOn=false;
refreshTableFormLinksButton();
}
updateTableForm();
showTableFormIfMultiple();
updatePinnedPositions();
updateDialogBoxesVisuals();
document.getElementById('st').textContent='Deleted '+targets.length+' row'+(targets.length===1?'':'s')+(removedPinned>0?' and unpinned '+removedPinned+' item'+(removedPinned===1?'':'s'):'');
}
function tfApplyCellSelection(){
var table=document.getElementById('table-form-table');
if(!table||!tfCellSel.active)return;
tfClearCellSelection();
tfCellSel.active=true;
var r1=Math.min(tfCellSel.startRow,tfCellSel.endRow);
var r2=Math.max(tfCellSel.startRow,tfCellSel.endRow);
var c1=Math.min(tfCellSel.startCol,tfCellSel.endCol);
var c2=Math.max(tfCellSel.startCol,tfCellSel.endCol);
for(var r=r1;r<=r2;r++){
for(var c=c1;c<=c2;c++){
var td=table.querySelector('td[data-row="'+r+'"][data-col="'+c+'"]');
if(td)td.classList.add('tf-cell-sel');
}
}
}
function tfHasCellSelection(){
var table=document.getElementById('table-form-table');
if(!table)return false;
return table.querySelector('td.tf-cell-sel')!==null;
}
function tfInitHotkeys(){
if(tfHotkeyInit)return;
tfHotkeyInit=true;
document.addEventListener('mouseup',function(){tfCellDrag=false;});
document.addEventListener('keydown',function(e){
if(!(e.ctrlKey||e.metaKey)||String(e.key).toLowerCase()!=='c')return;
if(!tableFormVisible)return;
if(tfHasCellSelection()||tfSelCols.id||tfSelCols.val){
e.preventDefault();
tfCopySelection();
}
});
}
function tfBindTableInteractions(){
tfInitHotkeys();
tfCellDrag=false;
tfCellMoved=false;
tfCellSel.active=false;
tfSelCols={id:false,val:false};
tfRowSelIdx=-1;
var table=document.getElementById('table-form-table');
if(!table)return;
var body=document.getElementById('table-form-body');
if(!body)return;
body.onmousedown=function(e){
var td=e.target&&e.target.closest?e.target.closest('td[data-col]'):null;
if(!td||!table.contains(td)||e.button!==0)return;
var row=parseInt(td.getAttribute('data-row'));
var col=parseInt(td.getAttribute('data-col'));
if(isNaN(row)||isNaN(col))return;
tfCellDrag=true;
tfCellMoved=false;
tfClearRowSelection();
tfClearColSelection();
tfCellSel={active:true,startRow:row,startCol:col,endRow:row,endCol:col};
tfApplyCellSelection();
e.preventDefault();
};
body.onmouseover=function(e){
if(!tfCellDrag)return;
var td=e.target&&e.target.closest?e.target.closest('td[data-col]'):null;
if(!td||!table.contains(td))return;
var row=parseInt(td.getAttribute('data-row'));
var col=parseInt(td.getAttribute('data-col'));
if(isNaN(row)||isNaN(col))return;
if(row!==tfCellSel.endRow||col!==tfCellSel.endCol)tfCellMoved=true;
tfCellSel.endRow=row;
tfCellSel.endCol=col;
tfApplyCellSelection();
};
body.onclick=function(e){
var th=e.target&&e.target.closest?e.target.closest('th[data-col]'):null;
if(th&&table.contains(th)){
var col=parseInt(th.getAttribute('data-col'));
if(isNaN(col))return;
tfClearCellSelection();
tfClearRowSelection();
if(col===0)tfSelCols.id=!tfSelCols.id;
if(col===1)tfSelCols.val=!tfSelCols.val;
if(!tfSelCols.id&&!tfSelCols.val){th.classList.remove('tf-col-sel');}
table.querySelectorAll('th[data-col]').forEach(function(h){
var hc=parseInt(h.getAttribute('data-col'));
h.classList.toggle('tf-col-sel',(hc===0&&tfSelCols.id)||(hc===1&&tfSelCols.val));
});
return;
}
var td=e.target&&e.target.closest?e.target.closest('td[data-col]'):null;
if(td&&table.contains(td)){
if(tfCellMoved){tfCellMoved=false;return;}
var row=parseInt(td.getAttribute('data-row'));
if(isNaN(row))return;
tfClearCellSelection();
tfClearColSelection();
if(e.ctrlKey||e.metaKey){
var tr=table.querySelector('tbody tr[data-row="'+row+'"]');
if(!tr)return;
if(tr.classList.contains('tf-row-sel'))tr.classList.remove('tf-row-sel');
else tr.classList.add('tf-row-sel');
var selectedRows=table.querySelectorAll('tbody tr.tf-row-sel');
tfRowSelIdx=selectedRows.length===1?row:-1;
}else{
if(tfRowSelIdx===row)tfClearRowSelection();
else tfApplyRowSelection(row);
}
return;
}
};
}
function tfEscapeHtml(s){
return String(s===undefined||s===null?'':s)
.replace(/&/g,'&amp;')
.replace(/</g,'&lt;')
.replace(/>/g,'&gt;')
.replace(/"/g,'&quot;')
.replace(/'/g,'&#39;');
}
function tfBuildCopyCellHtml(td,colIdx){
if(!td)return '<td></td>';
var txt=tfEscapeHtml(td.textContent.trim());
var st=[];
if(colIdx===1){
var cs=window.getComputedStyle?window.getComputedStyle(td):null;
var bg=(td.style&&td.style.backgroundColor)?td.style.backgroundColor:(cs?cs.backgroundColor:'');
var fg=(td.style&&td.style.color)?td.style.color:(cs?cs.color:'');
if(bg&&bg!=='transparent'&&bg!=='rgba(0, 0, 0, 0)')st.push('background-color:'+bg);
if(fg&&fg!=='rgba(0, 0, 0, 0)')st.push('color:'+fg);
st.push('font-weight:600');
}
return '<td'+(st.length?' style="'+st.join(';')+'"':'')+'>'+txt+'</td>';
}
function tfCopyWithHtml(text,html,rowCount){
function okMsg(){
document.getElementById('st').textContent='Table Form copied ('+rowCount+' row'+(rowCount===1?'':'s')+')';
}
function fallback(){
try{
navigator.clipboard.writeText(text).then(okMsg).catch(function(){xyFallbackCopy(text);});
}catch(e){xyFallbackCopy(text);}
}
try{
if(window.ClipboardItem&&navigator.clipboard&&navigator.clipboard.write){
var item=new ClipboardItem({
'text/plain':new Blob([text],{type:'text/plain'}),
'text/html':new Blob([html],{type:'text/html'})
});
navigator.clipboard.write([item]).then(okMsg).catch(function(){fallback();});
return;
}
}catch(e){}
fallback();
}
function tfCopySelection(){
var table=document.getElementById('table-form-table');
if(!table){document.getElementById('st').textContent='Table Form has no data to copy';return;}
var lines=[];
var htmlRows=[];
if(tfHasCellSelection()){
var selected=table.querySelectorAll('td.tf-cell-sel');
var rMin=1e9,rMax=-1,cMin=1e9,cMax=-1;
selected.forEach(function(td){
var r=parseInt(td.getAttribute('data-row'));
var c=parseInt(td.getAttribute('data-col'));
if(r<rMin)rMin=r;if(r>rMax)rMax=r;
if(c<cMin)cMin=c;if(c>cMax)cMax=c;
});
for(var r=rMin;r<=rMax;r++){
var vals=[];
var hVals=[];
for(var c=cMin;c<=cMax;c++){
var td=table.querySelector('td[data-row="'+r+'"][data-col="'+c+'"]');
if(td&&td.classList.contains('tf-cell-sel')){
vals.push(td.textContent.trim());
hVals.push(tfBuildCopyCellHtml(td,c));
}
}
if(vals.length>0){
lines.push(vals.join('\\t'));
htmlRows.push('<tr>'+hVals.join('')+'</tr>');
}
}
}else{
var useCols=[];
if(tfSelCols.id)useCols.push(0);
if(tfSelCols.val)useCols.push(1);
if(useCols.length===0)useCols=[0,1];
table.querySelectorAll('tbody tr').forEach(function(tr){
var vals=[];
var hVals=[];
useCols.forEach(function(c){
var td=tr.querySelector('td[data-col="'+c+'"]');
vals.push(td?td.textContent.trim():'');
hVals.push(tfBuildCopyCellHtml(td,c));
});
lines.push(vals.join('\\t'));
htmlRows.push('<tr>'+hVals.join('')+'</tr>');
});
}
var text=lines.join('\\n');
var html='<table style="border-collapse:collapse">'+htmlRows.join('')+'</table>';
tfCopyWithHtml(text,html,lines.length);
}
function getSidebarPanelZone(){
return document.getElementById('sidebar-panel-zone');
}
function getSidebarPanelItems(){
var zone=getSidebarPanelZone();
if(!zone)return [];
return Array.prototype.slice.call(zone.children).filter(function(el){
return !!(el&&el.getAttribute&&el.getAttribute('data-panel-id'));
});
}
function getSidebarPanelOrder(){
return getSidebarPanelItems().map(function(el){return el.getAttribute('data-panel-id');}).filter(function(id){return !!id;});
}
function applySidebarPanelOrder(order,silent){
if(!Array.isArray(order)||order.length===0)return;
var zone=getSidebarPanelZone();
if(!zone)return;
var items=getSidebarPanelItems();
var itemMap=Object.create(null);
items.forEach(function(el){itemMap[el.getAttribute('data-panel-id')]=el;});
order.forEach(function(id){
if(itemMap[id]){
zone.appendChild(itemMap[id]);
delete itemMap[id];
}
});
Object.keys(itemMap).forEach(function(id){zone.appendChild(itemMap[id]);});
if(!silent&&document.getElementById('st'))document.getElementById('st').textContent='Sidebar cards reordered';
}
function getSidebarInsertBefore(clientY){
var items=getSidebarPanelItems().filter(function(el){return el!==sidebarCardDragEl&&el!==sidebarCardPlaceholder;});
var closest={offset:Number.NEGATIVE_INFINITY,el:null};
items.forEach(function(el){
var rect=el.getBoundingClientRect();
var offset=clientY-(rect.top+rect.height*0.5);
if(offset<0&&offset>closest.offset)closest={offset:offset,el:el};
});
return closest.el;
}
function finishSidebarCardDrag(){
if(!sidebarCardDragEl)return;
var zone=getSidebarPanelZone();
if(zone&&sidebarCardPlaceholder&&sidebarCardPlaceholder.parentNode===zone){
zone.insertBefore(sidebarCardDragEl,sidebarCardPlaceholder);
}
sidebarCardDragEl.style.display='';
sidebarCardDragEl.classList.remove('dragging');
if(sidebarCardPlaceholder&&sidebarCardPlaceholder.parentNode)sidebarCardPlaceholder.parentNode.removeChild(sidebarCardPlaceholder);
sidebarCardDragEl=null;
sidebarCardPlaceholder=null;
sidebarCardHandleArmedId=null;
if(document.getElementById('st'))document.getElementById('st').textContent='Sidebar cards reordered';
}
function initSidebarCards(){
var zone=getSidebarPanelZone();
if(!zone||zone.getAttribute('data-ready')==='1')return;
zone.setAttribute('data-ready','1');
var cards=Array.prototype.slice.call(zone.querySelectorAll('.sidebar-card[data-panel-id]'));
cards.forEach(function(card){
var id=card.getAttribute('data-panel-id');
var handle=card.querySelector('.sidebar-card-handle')||card.querySelector('.pt');
if(!id||!handle)return;
card.setAttribute('draggable','true');
handle.setAttribute('title','Drag to reorder');
handle.addEventListener('mousedown',function(ev){
if(ev.button!==0)return;
sidebarCardHandleArmedId=id;
});
handle.addEventListener('mouseup',function(){sidebarCardHandleArmedId=null;});
card.addEventListener('dragstart',function(ev){
if(sidebarCardHandleArmedId!==id){
ev.preventDefault();
return;
}
sidebarCardDragEl=card;
sidebarCardPlaceholder=document.createElement('div');
sidebarCardPlaceholder.className='sidebar-card-placeholder';
sidebarCardPlaceholder.style.height=Math.max(24,card.offsetHeight)+'px';
card.classList.add('dragging');
if(ev.dataTransfer){
ev.dataTransfer.effectAllowed='move';
try{ev.dataTransfer.setData('text/plain',id);}catch(e){}
}
zone.insertBefore(sidebarCardPlaceholder,card.nextSibling);
setTimeout(function(){if(sidebarCardDragEl===card)card.style.display='none';},0);
});
card.addEventListener('dragend',finishSidebarCardDrag);
});
zone.addEventListener('dragover',function(ev){
if(!sidebarCardDragEl)return;
ev.preventDefault();
var before=getSidebarInsertBefore(ev.clientY);
if(before)zone.insertBefore(sidebarCardPlaceholder,before);
else zone.appendChild(sidebarCardPlaceholder);
var sb=document.getElementById('sb');
if(sb){
var rect=sb.getBoundingClientRect();
if(ev.clientY<rect.top+60)sb.scrollTop-=18;
else if(ev.clientY>rect.bottom-60)sb.scrollTop+=18;
}
});
zone.addEventListener('drop',function(ev){
if(!sidebarCardDragEl)return;
ev.preventDefault();
finishSidebarCardDrag();
});
document.addEventListener('mouseup',function(){sidebarCardHandleArmedId=null;});
}
// Make table form draggable
(function(){
var tfWin=null,tfHdr=null,tfDrag=false,tfOfs={x:0,y:0};
document.addEventListener('DOMContentLoaded',function(){
tfWin=document.getElementById('table-form-window');
tfHdr=document.getElementById('table-form-header');
var tfFontInp=document.getElementById('table-form-font');
if(tfFontInp)setTableFormFont(tfFontInp.value);
else applyTableFormFontSize();
fitTableFormCellsToWindow();
if(window.ResizeObserver&&tfWin){
try{if(tfResizeObserver)tfResizeObserver.disconnect();}catch(e){}
tfResizeObserver=new ResizeObserver(function(){fitTableFormCellsToWindow();});
tfResizeObserver.observe(tfWin);
}
window.addEventListener('resize',fitTableFormCellsToWindow);
if(!tfHdr)return;
tfHdr.style.cursor='move';
tfHdr.addEventListener('mousedown',function(e){
if(e.target.id==='table-form-close')return;
tfDrag=true;tfOfs.x=e.clientX-tfWin.offsetLeft;tfOfs.y=e.clientY-tfWin.offsetTop;e.preventDefault();
});
document.addEventListener('mousemove',function(e){
if(!tfDrag)return;
tfWin.style.left=(e.clientX-tfOfs.x)+'px';tfWin.style.top=(e.clientY-tfOfs.y)+'px';
tfWin.style.right='auto';
});
document.addEventListener('mouseup',function(){tfDrag=false;});
});
})();

(function(){
var win=document.getElementById('material-visibility-window');
var handle=document.getElementById('material-visibility-handle');
if(!win||!handle)return;
handle.addEventListener('mousedown',function(e){
if(e.target&&e.target.closest&&e.target.closest('button'))return;
materialVisibilityDrag={ox:e.clientX-win.offsetLeft,oy:e.clientY-win.offsetTop};
e.preventDefault();
e.stopPropagation();
});
document.addEventListener('mousemove',function(e){
if(!materialVisibilityDrag)return;
var pos=clampMaterialVisibilityWindowPos(e.clientX-materialVisibilityDrag.ox,e.clientY-materialVisibilityDrag.oy);
materialVisibilityWindowPos.left=pos.left;
materialVisibilityWindowPos.top=pos.top;
applyMaterialVisibilityWindowPos();
});
document.addEventListener('mouseup',function(){materialVisibilityDrag=null;});
window.addEventListener('resize',function(){
var overlay=document.getElementById('material-visibility-overlay');
if(overlay&&overlay.style.display==='block')applyMaterialVisibilityWindowPos();
});
})();

// ==================== PINNED VALUES ====================
function pinNodeValue(nodeIdx){
// Check if already pinned - if so, unpin it
for(var i=0;i<pinnedNodes.length;i++){
if(pinnedNodes[i]===nodeIdx){
sc.remove(pinnedMarkers[i]);
pinnedLabels[i].parentNode.removeChild(pinnedLabels[i]);
pinnedNodes.splice(i,1);
pinnedMarkers.splice(i,1);
pinnedLabels.splice(i,1);
document.getElementById('st').textContent='Unpinned N'+(NIDS[nodeIdx]||nodeIdx);
showTableFormIfMultiple();
return;
}
}
// Add new pin
var dispNodes=getDisplayNodes();
if(nodeIdx>=dispNodes.length)return;
pinnedNodes.push(nodeIdx);
// Create 3D marker sphere
var sz=B*0.0025;
var geo=new THREE.SphereGeometry(sz,8,8);
var mat=new THREE.MeshBasicMaterial({color:0xFFD600,depthTest:false});
var marker=new THREE.Mesh(geo,mat);
marker.position.set(dispNodes[nodeIdx][0],dispNodes[nodeIdx][1],dispNodes[nodeIdx][2]);
marker.renderOrder=998;
sc.add(marker);
pinnedMarkers.push(marker);
// Create HTML label
var container=document.getElementById('pinned-container');
var lbl=document.createElement('div');
lbl.className='pinned-label';
lbl.style.fontSize=valueInfoFontSize+'px';
var nv=rawColors?rawColors[nodeIdx]:curColors[nodeIdx];
var realVal=(nv!==undefined&&nv!==null)?dataMin+nv*(dataMax-dataMin):0;
lbl.innerHTML='<span class="pn-node">N'+(NIDS[nodeIdx]||nodeIdx)+'</span> <span class="pn-val">'+formatLegendDrivenValue(realVal,'N/A')+'</span>';
container.appendChild(lbl);
pinnedLabels.push(lbl);
document.getElementById('st').textContent='Pinned N'+(NIDS[nodeIdx]||nodeIdx)+': '+formatLegendDrivenValue(realVal,'N/A')+' ('+pinnedNodes.length+' pinned)';
showTableFormIfMultiple();
}

function clearPinned(){
pinnedMarkers.forEach(function(m){sc.remove(m);});
pinnedLabels.forEach(function(el){if(el.parentNode)el.parentNode.removeChild(el);});
pinnedNodes=[];pinnedMarkers=[];pinnedLabels=[];
clearPinnedElems();
document.getElementById('st').textContent='Pinned values cleared';
showTableFormIfMultiple();
}

function clearValuePinsAndTable(){
clearPinned();
tableFormVisible=false;
tableFormLinksOn=false;
var cb=document.getElementById('table-form-cb');
if(cb)cb.checked=false;
var win=document.getElementById('table-form-window');
if(win)win.style.display='none';
refreshTableFormLinksButton();
updateDialogBoxesVisuals();
}

function updatePinnedValues(){
var dispNodes=getDisplayNodes();
for(var i=0;i<pinnedNodes.length;i++){
var ni=pinnedNodes[i];
// Update marker position to current deformed coords
if(ni<dispNodes.length){
pinnedMarkers[i].position.set(dispNodes[ni][0],dispNodes[ni][1],dispNodes[ni][2]);
}
// Update value text
var nv=rawColors?rawColors[ni]:(curColors?curColors[ni]:null);
var realVal=(nv!==undefined&&nv!==null)?dataMin+nv*(dataMax-dataMin):0;
pinnedLabels[i].innerHTML='<span class="pn-node">N'+(NIDS[ni]||ni)+'</span> <span class="pn-val">'+formatLegendDrivenValue(realVal,'N/A')+'</span>';
pinnedLabels[i].style.fontSize=valueInfoFontSize+'px';
}
if(pinnedElems.length>0)updatePinnedElemValues();
if(tableFormVisible)updateTableForm();
}

function updatePinnedPositions(){
if(pinnedNodes.length===0&&pinnedElems.length===0&&!legendMaxMode&&!legendMinMode)return;
var rect=cvEl.getBoundingClientRect();
var w=rect.width,h=rect.height;
var offsetLeft=rect.left;
var offsetTop=rect.top;
var dispNodes=getDisplayNodes();
var cuts=getActiveCuts();
var hasCuts=cuts.length>0;
var linksOn=tableLinksActive();
var keepPinnedVisible=pinnedValueWindowsVisible();
for(var i=0;i<pinnedNodes.length;i++){
var ni=pinnedNodes[i];
if(ni>=dispNodes.length)continue;
var pos3=new THREE.Vector3(dispNodes[ni][0],dispNodes[ni][1],dispNodes[ni][2]);
pos3.project(ca);
var sx=(pos3.x*0.5+0.5)*w+offsetLeft;
var sy=(-pos3.y*0.5+0.5)*h+offsetTop;
// Check if behind camera
var show=keepPinnedVisible&&(pos3.z<=1)&&isNodeVisibleNow(ni)&&(!hasCuts||isPointVisibleByCuts(dispNodes[ni],cuts));
pinnedMarkers[i].visible=show;
if(!show||linksOn){pinnedLabels[i].style.display='none';continue;}
pinnedLabels[i].style.display='block';
pinnedLabels[i].style.left=(sx+12)+'px';
pinnedLabels[i].style.top=(sy-12)+'px';
}
updatePinnedElemPositions(cuts);
updateLegendExtremaPositions(cuts);
}

function projectNodeToCanvas(nodeIdx,canvasW,canvasH){
var dispNodes=getDisplayNodes();
if(nodeIdx>=dispNodes.length)return null;
if(!isNodeVisibleNow(nodeIdx))return null;
var pos3=new THREE.Vector3(dispNodes[nodeIdx][0],dispNodes[nodeIdx][1],dispNodes[nodeIdx][2]);
pos3.project(ca);
if(pos3.z>1)return null;
var sx=(pos3.x*0.5+0.5)*canvasW;
var sy=(-pos3.y*0.5+0.5)*canvasH;
return{x:sx,y:sy};
}

function drawPinnedOnCanvas(ctx,w,h){
if(pinnedNodes.length===0||!pinnedValueWindowsVisible())return;
var dispNodes=getDisplayNodes();
var cuts=getActiveCuts();
var hasCuts=cuts.length>0;
var linksOn=tableLinksActive();
ctx.save();
ctx.textAlign='left';
for(var i=0;i<pinnedNodes.length;i++){
var ni=pinnedNodes[i];
if(!isNodeVisibleNow(ni))continue;
var sp=projectNodeToCanvas(ni,w,h);
if(!sp)continue;
if(hasCuts&&!isPointVisibleByCuts(dispNodes[ni],cuts))continue;
var nv=rawColors?rawColors[ni]:(curColors?curColors[ni]:null);
var realVal=(nv!==undefined&&nv!==null)?dataMin+nv*(dataMax-dataMin):0;
var txt='N'+(NIDS[ni]||ni)+': '+formatLegendDrivenValue(realVal,'N/A');
ctx.font='600 '+valueInfoFontSize+'px Arial';
var tw=ctx.measureText(txt).width;
var pad=5,bx=sp.x+10,by=sp.y-8;
// Draw marker circle
ctx.beginPath();ctx.arc(sp.x,sp.y,3,0,Math.PI*2);
ctx.fillStyle='#FFD600';ctx.fill();
ctx.strokeStyle='#333';ctx.lineWidth=1;ctx.stroke();
if(linksOn)continue;
// Draw label background
ctx.fillStyle='rgba(0,0,0,0.82)';
ctx.strokeStyle='rgba(255,255,255,0.25)';
ctx.lineWidth=1;
roundRectPath(ctx,bx-pad,by-valueInfoFontSize+1,tw+pad*2,valueInfoFontSize+pad*2,4);
// Draw text
var nodeW=ctx.measureText('N'+(NIDS[ni]||ni)).width;
ctx.fillStyle='#4FC3F7';ctx.font='600 '+(valueInfoFontSize*0.9)+'px Arial';
ctx.fillText('N'+(NIDS[ni]||ni),bx,by+pad);
ctx.fillStyle='#FFD54F';ctx.font='600 '+valueInfoFontSize+'px Arial';
ctx.fillText(formatLegendDrivenValue(realVal,'N/A'),bx+nodeW+4,by+pad);
}
ctx.restore();
}


// ==================== PINNED ELEMENT VALUES ====================
function getElemCentroid3D(elemIdx){
// Find all faces belonging to this element and average their node positions
var dispNodes=getDisplayNodes();
var allFaces=getFullFaces();
var allFaceElemMap=getFullFaceElemMap();
var sumX=0,sumY=0,sumZ=0,cnt=0;
var seen={};
for(var fi=0;fi<allFaces.length;fi++){
if(allFaceElemMap[fi]===elemIdx){
allFaces[fi].forEach(function(ni){
if(!seen[ni]&&ni<dispNodes.length){
seen[ni]=true;
sumX+=dispNodes[ni][0];sumY+=dispNodes[ni][1];sumZ+=dispNodes[ni][2];cnt++;
}
});
}
}
if(cnt===0)return null;
return{x:sumX/cnt,y:sumY/cnt,z:sumZ/cnt};
}

function pinElemValue(elemIdx,faceIdx){
// Check if already pinned - unpin
for(var i=0;i<pinnedElems.length;i++){
if(pinnedElems[i]===elemIdx){
sc.remove(pinnedElemMarkers[i]);
pinnedElemLabels[i].parentNode.removeChild(pinnedElemLabels[i]);
pinnedElems.splice(i,1);
pinnedElemMarkers.splice(i,1);
pinnedElemLabels.splice(i,1);
pinnedElemFaces.splice(i,1);
document.getElementById('st').textContent='Unpinned E'+(EIDS[elemIdx]||elemIdx);
showTableFormIfMultiple();
return;
}
}
// Add new pin
pinnedElems.push(elemIdx);
pinnedElemFaces.push(faceIdx);
var ctr=getElemCentroid3D(elemIdx);
if(!ctr)return;
// Create 3D marker (green sphere)
var sz=B*0.003;
var geo=new THREE.SphereGeometry(sz,8,8);
var mat=new THREE.MeshBasicMaterial({color:0x66BB6A,depthTest:false});
var marker=new THREE.Mesh(geo,mat);
marker.position.set(ctr.x,ctr.y,ctr.z);
marker.renderOrder=998;
sc.add(marker);
pinnedElemMarkers.push(marker);
// Create HTML label
var container=document.getElementById('pinned-container');
var lbl=document.createElement('div');
lbl.className='pinned-label';
lbl.style.fontSize=valueInfoFontSize+'px';
var cv=centroidRawColors&&elemIdx<centroidRawColors.length?centroidRawColors[elemIdx]:null;
var realVal=(cv!==null&&cv!==undefined)?centroidDataMin+cv*(centroidDataMax-centroidDataMin):0;
lbl.innerHTML='<span class="pn-elem">E'+(EIDS[elemIdx]||elemIdx)+'</span> <span class="pn-val">'+formatLegendDrivenValue(realVal,'N/A')+'</span>';
container.appendChild(lbl);
pinnedElemLabels.push(lbl);
document.getElementById('st').textContent='Pinned E'+(EIDS[elemIdx]||elemIdx)+': '+formatLegendDrivenValue(realVal,'N/A')+' ('+(pinnedNodes.length+pinnedElems.length)+' pinned)';
showTableFormIfMultiple();
}

function clearPinnedElems(){
pinnedElemMarkers.forEach(function(m){sc.remove(m);});
pinnedElemLabels.forEach(function(el){if(el.parentNode)el.parentNode.removeChild(el);});
pinnedElems=[];pinnedElemMarkers=[];pinnedElemLabels=[];pinnedElemFaces=[];
}

function updatePinnedElemValues(){
for(var i=0;i<pinnedElems.length;i++){
var ei=pinnedElems[i];
// Update marker position to current deformed centroid
var ctr=getElemCentroid3D(ei);
if(ctr)pinnedElemMarkers[i].position.set(ctr.x,ctr.y,ctr.z);
// Update value
var cv=centroidRawColors&&ei<centroidRawColors.length?centroidRawColors[ei]:null;
var realVal=(cv!==null&&cv!==undefined)?centroidDataMin+cv*(centroidDataMax-centroidDataMin):0;
pinnedElemLabels[i].innerHTML='<span class="pn-elem">E'+(EIDS[ei]||ei)+'</span> <span class="pn-val">'+formatLegendDrivenValue(realVal,'N/A')+'</span>';
pinnedElemLabels[i].style.fontSize=valueInfoFontSize+'px';
}
}

function updatePinnedElemPositions(cuts){
if(pinnedElems.length===0)return;
var rect=cvEl.getBoundingClientRect();
var w=rect.width,h=rect.height;
var offsetLeft=rect.left,offsetTop=rect.top;
var useCuts=cuts&&cuts.length>0;
var linksOn=tableLinksActive();
var keepPinnedVisible=pinnedValueWindowsVisible();
for(var i=0;i<pinnedElems.length;i++){
// Use marker's already-computed 3D position (updated in updatePinnedElemValues)
var mp=pinnedElemMarkers[i].position;
var pos3=new THREE.Vector3(mp.x,mp.y,mp.z);
pos3.project(ca);
var sx=(pos3.x*0.5+0.5)*w+offsetLeft;
var sy=(-pos3.y*0.5+0.5)*h+offsetTop;
var show=keepPinnedVisible&&(pos3.z<=1)&&isElemVisibleNow(pinnedElems[i])&&(!useCuts||isPointVisibleByCuts([mp.x,mp.y,mp.z],cuts));
pinnedElemMarkers[i].visible=show;
if(!show||linksOn){pinnedElemLabels[i].style.display='none';continue;}
pinnedElemLabels[i].style.display='block';
pinnedElemLabels[i].style.left=(sx+12)+'px';
pinnedElemLabels[i].style.top=(sy-12)+'px';
}
}

function projectElemToCanvas(elemIdx,canvasW,canvasH){
if(!isElemVisibleNow(elemIdx))return null;
// Find the marker for this element
for(var i=0;i<pinnedElems.length;i++){
if(pinnedElems[i]===elemIdx){
var mp=pinnedElemMarkers[i].position;
var pos3=new THREE.Vector3(mp.x,mp.y,mp.z);
pos3.project(ca);
if(pos3.z>1)return null;
return{x:(pos3.x*0.5+0.5)*canvasW,y:(-pos3.y*0.5+0.5)*canvasH};
}
}
return null;
}

function drawPinnedElemsOnCanvas(ctx,w,h){
if(pinnedElems.length===0||!pinnedValueWindowsVisible())return;
var cuts=getActiveCuts();
var hasCuts=cuts.length>0;
var linksOn=tableLinksActive();
ctx.save();
ctx.textAlign='left';
for(var i=0;i<pinnedElems.length;i++){
var ei=pinnedElems[i];
if(!isElemVisibleNow(ei))continue;
var sp=projectElemToCanvas(ei,w,h);
if(!sp)continue;
if(hasCuts){
var mp=pinnedElemMarkers[i].position;
if(!isPointVisibleByCuts([mp.x,mp.y,mp.z],cuts))continue;
}
var cv=centroidRawColors&&ei<centroidRawColors.length?centroidRawColors[ei]:null;
var realVal=(cv!==null&&cv!==undefined)?centroidDataMin+cv*(centroidDataMax-centroidDataMin):0;
var txt='E'+(EIDS[ei]||ei)+': '+formatLegendDrivenValue(realVal,'N/A');
ctx.font='600 '+valueInfoFontSize+'px Arial';
var tw=ctx.measureText(txt).width;
var pad=5,bx=sp.x+10,by=sp.y-8;
// Marker
ctx.beginPath();ctx.arc(sp.x,sp.y,3,0,Math.PI*2);
ctx.fillStyle='#66BB6A';ctx.fill();
ctx.strokeStyle='#333';ctx.lineWidth=1;ctx.stroke();
if(linksOn)continue;
// Label background
ctx.fillStyle='rgba(0,0,0,0.82)';
ctx.strokeStyle='rgba(255,255,255,0.25)';
ctx.lineWidth=1;
roundRectPath(ctx,bx-pad,by-valueInfoFontSize+1,tw+pad*2,valueInfoFontSize+pad*2,4);
// Text
var elemW=ctx.measureText('E'+(EIDS[ei]||ei)).width;
ctx.fillStyle='#81C784';ctx.font='600 '+(valueInfoFontSize*0.9)+'px Arial';
ctx.fillText('E'+(EIDS[ei]||ei),bx,by+pad);
ctx.fillStyle='#FFD54F';ctx.font='600 '+valueInfoFontSize+'px Arial';
ctx.fillText(formatLegendDrivenValue(realVal,'N/A'),bx+elemW+4,by+pad);
}
ctx.restore();
}

// =================================================================

function tgnc(on){
noContour=on;
var legEl=document.getElementById('color-legend');
if(on){
ensureNoContourGroups();
renderNoContourGroupControls();
if(legEl)legEl.style.display='none';
cm(getRenderNodes(),null);
var ng=(noContourGroupSizes&&noContourGroupSizes.length)?noContourGroupSizes.length:0;
document.getElementById('st').textContent='No Contour: '+ng+' connected group'+(ng===1?'':'s')+' colored';
}else{
renderNoContourGroupControls();
if(legEl)legEl.style.display='flex';
if(cst&&AD[cst]){
var sd=AD[cst];
var cols=sd.colors?sd.colors.slice():null;
rawColors=cols;
centroidRawColors=sd.centroid_colors?sd.centroid_colors.slice():null;
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){
cm(getRenderNodes(),cols);
}else if(!dynamicLegend&&cols&&(Math.abs(curMin-dataMin)>1e-20||Math.abs(curMax-dataMax)>1e-20)){
cols=remapColors(rawColors,dataMin,dataMax,curMin,curMax);
cm(getRenderNodes(),cols);
}else{
cm(getRenderNodes(),cols);
}
}else{cm(getRenderNodes(),null);}
document.getElementById('st').textContent='Contour restored';
}
}
function tgmi(show){var ho=document.getElementById('help-overlay');if(ho)ho.style.display=show?'block':'none';}

function tgUndContour(on){
undContourMode=on;
if(on){
// Show undeformed mesh with contour colors
var drawColors=noContour?null:rawColors;
if(!noContour&&rawColors&&(Math.abs(curMin-dataMin)>1e-20||Math.abs(curMax-dataMax)>1e-20)){
drawColors=remapColors(rawColors,dataMin,dataMax,curMin,curMax);
}
cm(ON,drawColors);
var legEl=document.getElementById('color-legend');
if(legEl)legEl.style.display='flex';
document.getElementById('st').textContent='Undeformed mesh with contour colors';
}else{
// Restore deformed mesh with colors
if(cst&&AD[cst]){
var sd=AD[cst];
rawColors=sd.colors?sd.colors.slice():null;
centroidRawColors=sd.centroid_colors?sd.centroid_colors.slice():null;
var sdNodes=getStateNodes(cst);
if(sdNodes){
cn=[];
for(var i=0;i<ON.length;i++){
var o=ON[i],d=(sdNodes[i]||o);
cn.push([o[0]+(d[0]-o[0])*cs,o[1]+(d[1]-o[1])*cs,o[2]+(d[2]-o[2])*cs]);
}
}
var drawColors=noContour?null:rawColors;
if(!noContour&&rawColors&&(Math.abs(curMin-dataMin)>1e-20||Math.abs(curMax-dataMax)>1e-20)){
drawColors=remapColors(rawColors,dataMin,dataMax,curMin,curMax);
}
cm(getRenderNodes(),drawColors);
}
document.getElementById('st').textContent='Deformed mesh restored';
}
if(pinnedNodes.length>0||pinnedElems.length>0){
updatePinnedValues();
updatePinnedPositions();
}
}
function tgCentroid(on){
centroidMode=false;
refreshExtrapolationSummary();
}
function setBgColor(hex){
if(sc)sc.background=new THREE.Color(hex);
}
function tgVRF(on){
vrfEnabled=on;
document.getElementById('vrf-controls').style.display=on?'block':'none';
if(on){updateVRFLabels();}
rebuildVRFMesh();
}
function updateVRFLabels(){
var mn=curMin,mx=curMax;
document.getElementById('vrf-min-label').textContent=mn.toExponential(2);
document.getElementById('vrf-max-label').textContent=mx.toExponential(2);
var loSlider=document.getElementById('vrf-min');
var hiSlider=document.getElementById('vrf-max');
var loVal=parseInt(loSlider.value)/1000;
var hiVal=parseInt(hiSlider.value)/1000;
vrfLo=mn+loVal*(mx-mn);
vrfHi=mn+hiVal*(mx-mn);
document.getElementById('vrf-lo-val').textContent=vrfLo.toExponential(2);
document.getElementById('vrf-hi-val').textContent=vrfHi.toExponential(2);
var loPct=(loVal*100).toFixed(1);
var hiPct=(hiVal*100).toFixed(1);
var rng=document.getElementById('vrf-range');
if(rng){rng.style.left=loPct+'%';rng.style.width=(hiVal-loVal)*100+'%';}
}
function onVRFSlider(){
var loSlider=document.getElementById('vrf-min');
var hiSlider=document.getElementById('vrf-max');
var lo=parseInt(loSlider.value),hi=parseInt(hiSlider.value);
if(lo>hi){loSlider.value=hi;lo=hi;}
if(hi<lo){hiSlider.value=lo;hi=lo;}
updateVRFLabels();
if(vrfRebuildTimer)clearTimeout(vrfRebuildTimer);
vrfRebuildTimer=setTimeout(function(){vrfRebuildTimer=null;rebuildVRFMesh();},150);
}
var vrfRebuildTimer=null;
function rebuildVRFMesh(){
if(!cst||!AD[cst])return;
var sd=AD[cst];
rawColors=sd.colors?sd.colors.slice():null;
centroidRawColors=sd.centroid_colors?sd.centroid_colors.slice():null;
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){
cm(getRenderNodes(),noContour?null:rawColors);
}else{
var drawColors=noContour?null:rawColors;
if(!noContour&&rawColors&&(Math.abs(curMin-dataMin)>1e-20||Math.abs(curMax-dataMax)>1e-20)){
drawColors=remapColors(rawColors,dataMin,dataMax,curMin,curMax);
}
cm(getRenderNodes(),drawColors);
}
}
function clamp01(v){return Math.max(0,Math.min(1,v));}
function normalizeLegendColorMapId(v){
return (String(v)==='2')?'2':'1';
}
function legendClassicWarp(t){return Math.pow(clamp01(t),1.45);}
function getColormap1ContinuousColor(t){
var tw=legendClassicWarp(t);
var h=(1-tw)*0.7;
var c=new THREE.Color();
c.setHSL(h,1,0.5);
return c;
}
function getColormap1DiscreteHex(levelIdx,levelCount){
var n=parseInt(levelCount,10);
if(!isFinite(n))n=N_DISC;
if(n<2)n=2;
if(n>15)n=15;
var idx=Math.max(0,Math.min(n-1,parseInt(levelIdx,10)||0));
var den=Math.max(1,n-1);
var tBand=1-(idx/den);
if(n>=5&&idx===0)tBand=1.00;
else if(n>=5&&idx===1)tBand=0.95;
else if(n>=5&&idx===2)tBand=0.90;
else if(n>=5&&idx===3)tBand=0.80;
else if(n>=5&&idx===4)tBand=0.68;
else if(n===4&&idx===0)tBand=1.00;
else if(n===4&&idx===1)tBand=0.92;
else if(n===4&&idx===2)tBand=0.80;
else if(n===4&&idx===3)tBand=0.68;
else if(n===3&&idx===0)tBand=1.00;
else if(n===3&&idx===1)tBand=0.80;
else if(n===3&&idx===2)tBand=0.68;
else if(n===2&&idx===0)tBand=1.00;
else if(n===2&&idx===1)tBand=0.75;
return '#'+getColormap1ContinuousColor(tBand).getHexString();
}
// Extracted from the local Mentat installation:
// C:\Program Files\MSC.Software\Marc\2020.1.0\mentat2020.1\bin\whitemap -> colormap_002 contour ramp.
const MENTAT_COLORMAP2_HEX=['#0000ff','#1200ed','#2300dc','#3500ca','#4600b9','#5800a7','#6a0095','#7b0084','#8d0072','#9e0061','#b0004f','#c2003d','#d3002c','#e5001a','#f60009','#ff0900','#ff1a00','#ff2c00','#ff3d00','#ff4f00','#ff6100','#ff7200','#ff8400','#ff9500','#ffa700','#ffb900','#ffca00','#ffdc00','#ffed00','#ffff00'];
function getMentatColormap2Pos(t){
return clamp01(t)*(MENTAT_COLORMAP2_HEX.length-1);
}
function getMentatColormap2DiscreteHex(levelIdx,levelCount){
var n=parseInt(levelCount,10);
if(!isFinite(n))n=N_DISC;
if(n<2)n=2;
if(n>15)n=15;
var idx=Math.max(0,Math.min(n-1,parseInt(levelIdx,10)||0));
var den=Math.max(1,n-1);
var t=1-(idx/den);
var pos=Math.round(getMentatColormap2Pos(t));
pos=Math.max(0,Math.min(MENTAT_COLORMAP2_HEX.length-1,pos));
return MENTAT_COLORMAP2_HEX[pos];
}
function getMentatColormap2ContinuousColor(t){
var pos=getMentatColormap2Pos(t);
var lo=Math.floor(pos);
var hi=Math.min(MENTAT_COLORMAP2_HEX.length-1,lo+1);
var a=pos-lo;
var c1=new THREE.Color(MENTAT_COLORMAP2_HEX[lo]);
if(hi===lo)return c1;
var c2=new THREE.Color(MENTAT_COLORMAP2_HEX[hi]);
return c1.lerp(c2,a);
}
function getLegendContinuousColorForMap(mapId,t){
return normalizeLegendColorMapId(mapId)==='2'?getMentatColormap2ContinuousColor(t):getColormap1ContinuousColor(t);
}
function getLegendDiscreteHexForMap(mapId,levelIdx,levelCount){
return normalizeLegendColorMapId(mapId)==='2'?getMentatColormap2DiscreteHex(levelIdx,levelCount):getColormap1DiscreteHex(levelIdx,levelCount);
}
function legendBaseColor(t){
return getLegendContinuousColorForMap(legendColorMapId,t);
}
function getBaseLegendHex(t){return '#'+legendBaseColor(t).getHexString();}
function buildLegendGradientCSS(direction){
var stops=[];var steps=28;
for(var i=0;i<=steps;i++){
var p=i/steps;
var tVal=1-p;
stops.push(getBaseLegendHex(tVal)+' '+(p*100).toFixed(1)+'%');
}
return 'linear-gradient('+direction+','+stops.join(',')+')';
}
function buildCustomLegendGradientCSS(direction){
if(!hasCustomLegend())return buildLegendGradientCSS(direction);
var stops=[];
for(var i=0;i<N_DISC;i++){
var p1=(i/N_DISC*100).toFixed(1);
var p2=((i+1)/N_DISC*100).toFixed(1);
var c=getLegendBandHex(i);
stops.push(c+' '+p1+'%');
stops.push(c+' '+p2+'%');
}
return 'linear-gradient('+direction+','+stops.join(',')+')';
}
function buildLinearLegendValues(vmin,vmax){
var vals=[];
for(var i=0;i<=N_DISC;i++){
var frac=1-i/N_DISC;
vals.push(vmin+frac*(vmax-vmin));
}
return vals;
}
function buildLegendColorsForLevels(levelCount){
var n=parseInt(levelCount,10);
if(!isFinite(n))n=N_DISC;
if(n<2)n=2;
if(n>15)n=15;
var cols=[];
for(var i=0;i<n;i++){
cols.push(getLegendDiscreteHexForMap(legendColorMapId,i,n));
}
return cols;
}
function buildDefaultLegendColors(){
return buildLegendColorsForLevels(N_DISC);
}
function formatLegendNumber(v){
if(!isFinite(v))return '0';
if(legendValueFormat==='float'){
var dec=parseInt(legendFloatDecimals);
if(!isFinite(dec))dec=6;
if(dec<0)dec=0;
if(dec>8)dec=8;
return Number(v).toFixed(dec);
}
return v.toExponential(2);
}
function formatLegendDrivenValue(v,nullText){
var txt=(nullText===undefined||nullText===null)?'N/A':String(nullText);
var num=Number(v);
if(!isFinite(num))return txt;
return formatLegendNumber(num);
}
function refreshValueTooltipFormat(){
if(valTooltipInvalidUntilMove||!lastValueTooltipInfo)return;
var tt=document.getElementById('val-tooltip');
if(!tt||tt.style.display==='none')return;
if(!lastValueTooltipInfo.idText)return;
var num=Number(lastValueTooltipInfo.rawValue);
if(!isFinite(num))return;
var txt=lastValueTooltipInfo.idText+': '+formatLegendDrivenValue(num,'N/A');
tt.textContent=txt;
lastValueTooltipInfo.text=txt;
}
function refreshLegendDrivenValueDisplays(){
refreshValueTooltipFormat();
if(pinnedNodes.length>0||pinnedElems.length>0)updatePinnedValues();
if(tableFormVisible)updateTableForm();
if(legendMaxMode||legendMinMode)updateLegendExtremaTargets();
if(hasAnyMeasurements())updateMeasurement();
}
function updateLegendFormatControls(){
var fmtSel=document.getElementById('leg-format');
if(fmtSel)fmtSel.value=legendValueFormat;
var decSel=document.getElementById('leg-fdec');
if(decSel){
var d=parseInt(legendFloatDecimals);
if(!isFinite(d))d=6;
if(d<0)d=0;
if(d>8)d=8;
legendFloatDecimals=d;
decSel.value=String(d);
}
var wrap=document.getElementById('leg-fdec-wrap');
if(wrap)wrap.style.display=(legendValueFormat==='float')?'inline-flex':'none';
}
function updateLegendRangeInputs(){
var minEl=document.getElementById('leg-min');
var maxEl=document.getElementById('leg-max');
if(minEl)minEl.value=formatLegendNumber(curMin);
if(maxEl)maxEl.value=formatLegendNumber(curMax);
}
function setLegFormat(fmt){
legendValueFormat=(fmt==='float')?'float':'exp';
updateLegendFormatControls();
updateLegendRangeInputs();
ulv(curMin,curMax);
updGrad();
updCb();
if(cst&&AD[cst])rebuildCurrentMeshColors();
refreshLegendDrivenValueDisplays();
document.getElementById('st').textContent='Legend format: '+(legendValueFormat==='float'?'Floating':'Exponential');
}
function setLegFloatDecimals(n){
var d=parseInt(n);
if(!isFinite(d))d=6;
if(d<0)d=0;
if(d>8)d=8;
legendFloatDecimals=d;
updateLegendFormatControls();
updateLegendRangeInputs();
ulv(curMin,curMax);
updGrad();
updCb();
if(cst&&AD[cst])rebuildCurrentMeshColors();
refreshLegendDrivenValueDisplays();
document.getElementById('st').textContent='Legend floating decimals: '+d;
}
function setLegFontSize(sz){
var n=parseInt(sz,10);
if(!isFinite(n))n=12;
if(n<7)n=7;
if(n>20)n=20;
legFontSize=n;
var fs=document.getElementById('leg-font-size');
if(fs)fs.value=String(n);
var fv=document.getElementById('leg-font-size-val');
if(fv)fv.textContent=String(n);
ulv(curMin,curMax);
updGrad();
updCb();
document.getElementById('st').textContent='Legend font size: '+n;
}
function setValueInfoFontSize(sz){
var n=parseInt(sz,10);
if(!isFinite(n))n=12;
if(n<7)n=7;
if(n>20)n=20;
valueInfoFontSize=n;
var fs=document.getElementById('value-font-size');
if(fs)fs.value=String(n);
var fv=document.getElementById('value-font-size-val');
if(fv)fv.textContent=String(n);
var vt=document.getElementById('val-tooltip');
if(vt)vt.style.fontSize=valueInfoFontSize+'px';
for(var i=0;i<pinnedLabels.length;i++){pinnedLabels[i].style.fontSize=valueInfoFontSize+'px';}
for(var j=0;j<pinnedElemLabels.length;j++){pinnedElemLabels[j].style.fontSize=valueInfoFontSize+'px';}
if(legendMaxLabel)legendMaxLabel.style.fontSize=valueInfoFontSize+'px';
if(legendMinLabel)legendMinLabel.style.fontSize=valueInfoFontSize+'px';
document.getElementById('st').textContent='Value info font size: '+n;
}
function setLegLevels(n){
var newN=parseInt(n,10);
if(!isFinite(newN))newN=10;
if(newN<2)newN=2;
if(newN>15)newN=15;
N_DISC=newN;
var lvlSel=document.getElementById('leg-levels');
if(lvlSel)lvlSel.value=String(newN);
var lvlVal=document.getElementById('leg-levels-val');
if(lvlVal)lvlVal.textContent=String(newN);
legendCustomValues=buildLinearLegendValues(curMin,curMax);
legendCustomColors=buildLegendColorsForLevels(newN);
ulv(curMin,curMax);
updGrad();
updCb();
if(cst&&AD[cst]){
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){
cm(getRenderNodes(),noContour?null:rawColors);
}else if(rawColors){
var displayColors=rawColors;
if(Math.abs(curMin-dataMin)>1e-20||Math.abs(curMax-dataMax)>1e-20){
displayColors=remapColors(rawColors,dataMin,dataMax,curMin,curMax);
}
cm(getRenderNodes(),displayColors);
}
}
document.getElementById('st').textContent='Legend levels set to '+N_DISC;
}
function tgdl(on){
dynamicLegend=on;
if(!on){
var si=parseInt(document.getElementById('gif-start').value);
var ei=parseInt(document.getElementById('gif-end').value);
var sIdx=Math.min(si,ei),eIdx=Math.max(si,ei);
var gMin=Infinity,gMax=-Infinity;
var mnKey=(centroidMode||isElementLocalContourMode())?'centroid_min':'color_min';
var mxKey=(centroidMode||isElementLocalContourMode())?'centroid_max':'color_max';
for(var ki=sIdx;ki<=eIdx;ki++){
if(ki<SL.length){
var sk=SL[ki].id;
var sd=getStateData(currentVar,sk);
if(sd&&sd[mnKey]!==undefined){
if(sd[mnKey]<gMin)gMin=sd[mnKey];
if(sd[mxKey]>gMax)gMax=sd[mxKey];
}
}
}
if(!isFinite(gMin)){
var allStateIds=getVarStateIds(currentVar);
for(var ai=0;ai<allStateIds.length;ai++){
var k=allStateIds[ai];
var kd=getStateData(currentVar,k);
if(kd&&kd[mnKey]!==undefined){
if(kd[mnKey]<gMin)gMin=kd[mnKey];
if(kd[mxKey]>gMax)gMax=kd[mxKey];
}
}
}
if(isFinite(gMin)){
curMin=gMin;curMax=gMax;
if(hasCustomLegend())legendCustomValues=buildLinearLegendValues(curMin,curMax);
updateLegendRangeInputs();
ulv(curMin,curMax);updGrad();updCb();
var csd=(cst?(AD[cst]||getStateData(currentVar,cst)):null);
if(csd){
if(centroidMode||isElementLocalContourMode()){dataMin=csd.centroid_min;dataMax=csd.centroid_max;}
else{dataMin=csd.color_min;dataMax=csd.color_max;}
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){cm(getRenderNodes(),rawColors);}
else if(rawColors){var rc=remapColors(rawColors,dataMin,dataMax,curMin,curMax);cm(getRenderNodes(),rc);}
}
}
}else if(on&&cst){
var csdOn=AD[cst]||getStateData(currentVar,cst);
if(csdOn)ucr(csdOn);
}
if(cst)syncLegendToVisibleRange();
}
function hasCustomLegend(){
return !!(legendCustomValues&&legendCustomColors&&legendCustomValues.length===N_DISC+1&&legendCustomColors.length===N_DISC);
}
function seedCustomLegend(){
legendCustomValues=buildLinearLegendValues(curMin,curMax);
legendCustomColors=buildDefaultLegendColors();
}
function normalizeHexColor(v){
if(!v)return null;
var s=(''+v).trim().toLowerCase();
if(/^#[0-9a-f]{6}$/.test(s))return s;
if(/^[0-9a-f]{6}$/.test(s))return '#'+s;
return null;
}
function getLegendBandHex(idx){
if(idx<0||idx>=N_DISC)return '#808080';
if(hasCustomLegend()){
var hx=normalizeHexColor(legendCustomColors[idx]);
if(hx)return hx;
}
if(discreteMode){
return getLegendDiscreteHexForMap(legendColorMapId,idx,N_DISC);
}
var den=Math.max(1,N_DISC-1);
var tBand=1-(idx/den);
return getBaseLegendHex(tBand);
}
function getCustomLegendColor(realVal){
if(!hasCustomLegend())return null;
var vals=legendCustomValues;
if(realVal>=vals[0])return new THREE.Color(getLegendBandHex(0));
if(realVal<=vals[N_DISC])return new THREE.Color(getLegendBandHex(N_DISC-1));
for(var i=0;i<N_DISC;i++){
if(realVal<=vals[i]&&realVal>=vals[i+1]){
var c1=new THREE.Color(getLegendBandHex(i));
if(discreteMode||i===N_DISC-1)return c1;
var c2=new THREE.Color(getLegendBandHex(Math.min(i+1,N_DISC-1)));
var den=vals[i]-vals[i+1];
var a=Math.abs(den)<1e-30?0:(vals[i]-realVal)/den;
a=clamp01(a);
return c1.lerp(c2,a);
}
}
return new THREE.Color(getLegendBandHex(N_DISC-1));
}
function getLegendColorFromReal(realVal){
if(hasCustomLegend()){
var cc=getCustomLegendColor(realVal);
if(cc)return cc;
}
var uR=curMax-curMin;if(Math.abs(uR)<1e-30)uR=1;
var mapped=(realVal-curMin)/uR;
return gc(mapped);
}
function getMeshDrawColors(){
if(noContour||!rawColors)return null;
if(Math.abs(curMin-dataMin)<=1e-20&&Math.abs(curMax-dataMax)<=1e-20)return rawColors;
if(remapCacheSrc===rawColors&&Math.abs(remapCacheDMin-dataMin)<=1e-30&&Math.abs(remapCacheDMax-dataMax)<=1e-30&&Math.abs(remapCacheUMin-curMin)<=1e-30&&Math.abs(remapCacheUMax-curMax)<=1e-30&&remapCacheOut){
return remapCacheOut;
}
var out=remapColors(rawColors,dataMin,dataMax,curMin,curMax);
remapCacheSrc=rawColors;
remapCacheDMin=dataMin;remapCacheDMax=dataMax;
remapCacheUMin=curMin;remapCacheUMax=curMax;
remapCacheOut=out;
return out;
}
function rebuildCurrentMeshColors(){
if(!(cst&&AD[cst]))return;
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){
cm(getRenderNodes(),noContour?null:rawColors);
return;
}
if(rawColors){
cm(getRenderNodes(),getMeshDrawColors());
}
}
function enterLegendEdit(opts){
if(!hasCustomLegend())seedCustomLegend();
legendEditMode=true;
if(opts&&opts.valueIdx!==undefined)legendEditFocusValue=opts.valueIdx;
if(opts&&opts.colorIdx!==undefined)legendEditFocusColor=opts.colorIdx;
ulv(curMin,curMax);
updGrad();
updCb();
document.getElementById('st').textContent='Legend edit mode: double-click values or colors';
}
function exitLegendEdit(){
if(!legendEditMode)return;
legendEditMode=false;
legendEditFocusValue=-1;
legendEditFocusColor=-1;
ulv(curMin,curMax);
updGrad();
updCb();
}
function onLegendGradientDblClick(ev){
if(legendEditMode)return;
var el=document.getElementById('legend-gradient');
if(!el)return;
var rect=el.getBoundingClientRect();
if(!rect||rect.height<=0){enterLegendEdit();return;}
var y=ev.clientY-rect.top;
var frac=clamp01(y/rect.height);
var idx=Math.floor(frac*N_DISC);
if(idx<0)idx=0;
if(idx>=N_DISC)idx=N_DISC-1;
enterLegendEdit({colorIdx:idx});
}
function onLegendValueEdit(idx,valStr){
var v=parseFloat((''+valStr).replace(',','.'));
if(!isFinite(v)){ulv(curMin,curMax);return;}
if(!hasCustomLegend())seedCustomLegend();
var vals=legendCustomValues.slice();
var N=N_DISC;
if(idx<=0){
vals[0]=v;
if(vals[0]<=vals[N])vals[N]=vals[0]-1e-12;
for(var i=1;i<N;i++)vals[i]=vals[0]+(vals[N]-vals[0])*(i/N);
}else if(idx>=N){
vals[N]=v;
if(vals[N]>=vals[0])vals[0]=vals[N]+1e-12;
for(var j=1;j<N;j++)vals[j]=vals[0]+(vals[N]-vals[0])*(j/N);
}else{
if(v>vals[0])v=vals[0];
if(v<vals[N])v=vals[N];
vals[idx]=v;
for(var a=1;a<idx;a++)vals[a]=vals[0]+(v-vals[0])*(a/idx);
for(var b=idx+1;b<N;b++)vals[b]=v+(vals[N]-v)*((b-idx)/(N-idx));
}
legendCustomValues=vals;
curMax=vals[0];
curMin=vals[N];
updateLegendRangeInputs();
ulv(curMin,curMax);
updGrad();
updCb();
rebuildCurrentMeshColors();
if(vrfEnabled)updateVRFLabels();
}
function onLegendColorEdit(idx,val){
if(idx<0||idx>=N_DISC)return;
if(!hasCustomLegend())seedCustomLegend();
var hx=normalizeHexColor(val);
if(!hx){ulv(curMin,curMax);return;}
legendCustomColors[idx]=hx;
updGrad();
updCb();
rebuildCurrentMeshColors();
}
function editLegendValues(){enterLegendEdit();}
function editLegendColors(){enterLegendEdit();}
function legendDefault(){
legendCustomValues=null;
legendCustomColors=null;
legendEditMode=false;
legendEditFocusValue=-1;
legendEditFocusColor=-1;
legendValueFormat='float';
legendFloatDecimals=3;
legendColorMapId='1';
extrapolationMethod='linear';
extrapolationNodalAveraging='off';
N_DISC=12;
legFontSize=14;
updateLegendFormatControls();
refreshExtrapolationSummary();
var lvlSel=document.getElementById('leg-levels');if(lvlSel)lvlSel.value='12';
var fs=document.getElementById('leg-font-size');if(fs)fs.value='14';
var fv=document.getElementById('leg-font-size-val');if(fv)fv.textContent='14';
legendAutoResetPending=true;
if(cst&&AD[cst]){ucr(AD[cst]);}
else{
updateLegendRangeInputs();
ulv(curMin,curMax);
updGrad();
updCb();
}
rebuildCurrentMeshColors();
document.getElementById('st').textContent='Legend reset to default';
}
function resetCustomLegend(){legendDefault();}
function tgd(on){
discreteMode=on;
updGrad();
updCb();
if(!noContour&&cst&&AD[cst]){
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){
cm(getRenderNodes(),rawColors);
}else if(rawColors){
var displayColors=rawColors;
if(Math.abs(curMin-dataMin)>1e-20||Math.abs(curMax-dataMax)>1e-20){
displayColors=remapColors(rawColors,dataMin,dataMax,curMin,curMax);
}
cm(getRenderNodes(),displayColors);
}
}
}
function drawDiscreteLegendBar(el,isHorizontal){
el.innerHTML='';
el.style.background='none';
el.style.display='flex';
el.style.flexDirection=isHorizontal?'row':'column';
for(var i=0;i<N_DISC;i++){
var band=document.createElement('div');
band.style.flex='1';
band.style.background=getLegendBandHex(i);
band.style.boxSizing='border-box';
if(!legendEditMode){
(function(idx){
band.addEventListener('dblclick',function(ev){
ev.stopPropagation();
enterLegendEdit({colorIdx:idx});
});
})(i);
}
if(isHorizontal){if(i<N_DISC-1)band.style.borderRight='1px solid rgba(0,0,0,0.5)';}
else{if(i<N_DISC-1)band.style.borderBottom='1px solid rgba(0,0,0,0.5)';}
el.appendChild(band);
}
}
// Update legend gradient bar (continuous or discrete)
function updGrad(){
var el=document.getElementById('legend-gradient');
if(!el)return;
el.onclick=null;
el.ondblclick=onLegendGradientDblClick;
if(discreteMode){
drawDiscreteLegendBar(el,false);
return;
}
el.innerHTML='';
el.style.display='block';
el.style.background=hasCustomLegend()?buildCustomLegendGradientCSS('to bottom'):buildLegendGradientCSS('to bottom');
}

// Update small horizontal color bar in sidebar Color Legend section
function updCb(){
var el=document.getElementById('cb');
if(!el)return;
if(discreteMode){
drawDiscreteLegendBar(el,true);
return;
}
el.innerHTML='';
el.style.display='block';
el.style.background=hasCustomLegend()?buildCustomLegendGradientCSS('to right'):buildLegendGradientCSS('to right');
}

// --- Element-based cut view filtering ---
function getActiveCuts(){
var cuts=[];
['x','y','z'].forEach(function(axis){
var cut=buildAxisAlignedCut(axis);
if(cut)cuts.push(cut);
});
var rotCut=getRotationCutData();
if(rotCut&&rotCut.enabled){
if(rotCut.state.angle2On&&rotCut.secondary){
cuts.push({
type:'rotation-sector',
axisDir:[rotCut.axisDir.x,rotCut.axisDir.y,rotCut.axisDir.z],
refPoint:[rotCut.refPoint.x,rotCut.refPoint.y,rotCut.refPoint.z],
baseVisible:[rotCut.baseVisible.x,rotCut.baseVisible.y,rotCut.baseVisible.z],
angle1:rotCut.primarySignedAngle,
angle2:rotCut.secondarySignedAngle
});
}else{
cuts.push({
type:'rotation',
normal:[rotCut.clipNormal.x,rotCut.clipNormal.y,rotCut.clipNormal.z],
constant:rotCut.constant
});
}
}
return cuts;
}
function getActiveClipHalfspaces(){
var planes=[];
['x','y','z'].forEach(function(axis){
var cut=buildAxisAlignedCut(axis);
if(!cut)return;
var visual=getAxisCutVisualData(axis);
if(!visual)return;
planes.push({
id:'axis-'+axis,
normal:cut.normal.slice(),
constant:cut.constant,
point:[visual.point.x,visual.point.y,visual.point.z]
});
});
var rotData=getRotationCutData();
if(rotData&&rotData.enabled){
planes.push({
id:'rotation-primary',
normal:[rotData.primary.clipNormal.x,rotData.primary.clipNormal.y,rotData.primary.clipNormal.z],
constant:rotData.primary.constant,
point:[rotData.refPoint.x,rotData.refPoint.y,rotData.refPoint.z]
});
if(rotData.state&&rotData.state.angle2On&&rotData.secondary){
planes.push({
id:'rotation-secondary',
normal:[rotData.secondary.clipNormal.x,rotData.secondary.clipNormal.y,rotData.secondary.clipNormal.z],
constant:rotData.secondary.constant,
point:[rotData.refPoint.x,rotData.refPoint.y,rotData.refPoint.z]
});
}
}
return planes;
}
function getClipPlaneSignedDistance(p,plane){
if(!p||!plane||!plane.normal)return -Infinity;
return (p[0]*plane.normal[0])+(p[1]*plane.normal[1])+(p[2]*plane.normal[2])+plane.constant;
}
function addCutSectionPoint(points,p,tolSq){
if(!p)return;
for(var i=0;i<points.length;i++){
var q=points[i];
var dx=p[0]-q[0],dy=p[1]-q[1],dz=p[2]-q[2];
if((dx*dx+dy*dy+dz*dz)<=tolSq)return;
}
points.push([p[0],p[1],p[2]]);
}
function getTrianglePlaneIntersection(face,nodes,plane,eps){
if(!face||face.length<3||!nodes||!plane)return null;
var pts=[];
var tolSq=eps*eps;
var edgePairs=[[0,1],[1,2],[2,0]];
for(var ei=0;ei<edgePairs.length;ei++){
var edge=edgePairs[ei];
var ia=face[edge[0]],ib=face[edge[1]];
if(ia<0||ib<0||ia>=nodes.length||ib>=nodes.length)continue;
var pa=nodes[ia],pb=nodes[ib];
if(!pa||!pb)continue;
var da=getClipPlaneSignedDistance(pa,plane);
var db=getClipPlaneSignedDistance(pb,plane);
var aOn=Math.abs(da)<=eps;
var bOn=Math.abs(db)<=eps;
if(aOn&&bOn){
addCutSectionPoint(pts,pa,tolSq);
addCutSectionPoint(pts,pb,tolSq);
continue;
}
if(aOn)addCutSectionPoint(pts,pa,tolSq);
if(bOn)addCutSectionPoint(pts,pb,tolSq);
if((da<-eps&&db>eps)||(da>eps&&db<-eps)){
var denom=da-db;
if(Math.abs(denom)>1e-20){
var t=da/denom;
if(t>=-1e-8&&t<=1+1e-8){
addCutSectionPoint(pts,[
pa[0]+(pb[0]-pa[0])*t,
pa[1]+(pb[1]-pa[1])*t,
pa[2]+(pb[2]-pa[2])*t
],tolSq);
}
}
}
}
if(pts.length<2)return null;
if(pts.length===2)return [pts[0],pts[1]];
var bestA=pts[0],bestB=pts[1],bestD=-1;
for(var i=0;i<pts.length;i++){
for(var j=i+1;j<pts.length;j++){
var dx=pts[i][0]-pts[j][0],dy=pts[i][1]-pts[j][1],dz=pts[i][2]-pts[j][2];
var d=dx*dx+dy*dy+dz*dz;
if(d>bestD){bestD=d;bestA=pts[i];bestB=pts[j];}
}
}
return bestD>tolSq?[bestA,bestB]:null;
}
function clipSegmentToHalfspaces(a,b,planes,skipPlaneId,eps){
var t0=0,t1=1;
for(var i=0;i<planes.length;i++){
var plane=planes[i];
if(!plane||plane.id===skipPlaneId)continue;
var d0=getClipPlaneSignedDistance(a,plane);
var d1=getClipPlaneSignedDistance(b,plane);
var in0=d0>=-eps,in1=d1>=-eps;
if(in0&&in1)continue;
if(!in0&&!in1)return null;
var denom=d0-d1;
if(Math.abs(denom)<=1e-20)return null;
var t=d0/denom;
if(!in0){if(t>t0)t0=t;}
else if(!in1){if(t<t1)t1=t;}
if(t0>t1+1e-8)return null;
}
var outA=[
a[0]+(b[0]-a[0])*t0,
a[1]+(b[1]-a[1])*t0,
a[2]+(b[2]-a[2])*t0
];
var outB=[
a[0]+(b[0]-a[0])*t1,
a[1]+(b[1]-a[1])*t1,
a[2]+(b[2]-a[2])*t1
];
var dx=outA[0]-outB[0],dy=outA[1]-outB[1],dz=outA[2]-outB[2];
if((dx*dx+dy*dy+dz*dz)<=eps*eps)return null;
return [outA,outB];
}
function getCutSectionSegmentKey(a,b,tol,planeId){
function qp(p){
return [
Math.round(p[0]/tol),
Math.round(p[1]/tol),
Math.round(p[2]/tol)
].join(',');
}
var ka=qp(a),kb=qp(b);
return planeId+'|'+(ka<kb?(ka+'|'+kb):(kb+'|'+ka));
}
function getSectionElementConn(elemIdx,nodes){
if(!ECOFF||!ECON||elemIdx===undefined||elemIdx===null||elemIdx<0||elemIdx+1>=ECOFF.length||!nodes)return null;
var s=ECOFF[elemIdx]|0,e=ECOFF[elemIdx+1]|0;
if(!(e>s))return null;
var out=[];
for(var i=s;i<e&&i<ECON.length;i++){
var ni=ECON[i]|0;
if(ni>=0&&ni<nodes.length)out.push(ni);
}
return out.length>=4?out:null;
}
function getSectionElementEdgePairs(conn){
if(!conn)return null;
var n=conn.length;
if(n===4)return [[0,1],[1,2],[2,0],[0,3],[1,3],[2,3]];
if(n===6)return [[0,1],[1,2],[2,0],[3,4],[4,5],[5,3],[0,3],[1,4],[2,5]];
if(n>=8)return [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
return null;
}
function isCutSectionElementMode(){
return !!(((typeof isElementDisplayMode==='function'&&isElementDisplayMode())||centroidMode||isElementLocalContourMode())&&centroidRawColors&&!noContour);
}
function getCutSectionNodeRealValue(nodeIdx){
if(noContour)return curMin;
if(nodeIdx===undefined||nodeIdx===null||nodeIdx<0)return curMin;
if(rawColors&&nodeIdx<rawColors.length)return dataMin+rawColors[nodeIdx]*(dataMax-dataMin);
if(curColors&&nodeIdx<curColors.length){
var uR=curMax-curMin;if(Math.abs(uR)<1e-30)uR=1;
return curMin+curColors[nodeIdx]*uR;
}
return curMin;
}
function getCutSectionFaceRealValue(faceElemIdx){
if(isCutSectionElementMode()&&faceElemIdx!==undefined&&faceElemIdx!==null&&faceElemIdx>=0&&faceElemIdx<centroidRawColors.length){
return centroidDataMin+centroidRawColors[faceElemIdx]*(centroidDataMax-centroidDataMin);
}
return null;
}
function addCutSectionDataPoint(pts,pos,realValue,tolSq){
for(var i=0;i<pts.length;i++){
var dx=pts[i].pos[0]-pos[0],dy=pts[i].pos[1]-pos[1],dz=pts[i].pos[2]-pos[2];
if((dx*dx+dy*dy+dz*dz)<=tolSq){
pts[i].realValue=(pts[i].realValue+realValue)*0.5;
return;
}
}
pts.push({pos:[pos[0],pos[1],pos[2]],realValue:realValue});
}
function getTrianglePlaneIntersectionData(face,nodes,plane,eps,faceElemIdx){
if(!face||face.length<3||!nodes||!plane)return null;
var pts=[];
var tolSq=eps*eps;
var edgePairs=[[0,1],[1,2],[2,0]];
var faceVal=getCutSectionFaceRealValue(faceElemIdx);
for(var ei=0;ei<edgePairs.length;ei++){
var edge=edgePairs[ei];
var ia=face[edge[0]],ib=face[edge[1]];
if(ia<0||ib<0||ia>=nodes.length||ib>=nodes.length)continue;
var pa=nodes[ia],pb=nodes[ib];
if(!pa||!pb)continue;
var va=(faceVal!==null)?faceVal:getCutSectionNodeRealValue(ia);
var vb=(faceVal!==null)?faceVal:getCutSectionNodeRealValue(ib);
var da=getClipPlaneSignedDistance(pa,plane);
var db=getClipPlaneSignedDistance(pb,plane);
var aOn=Math.abs(da)<=eps;
var bOn=Math.abs(db)<=eps;
if(aOn&&bOn){
addCutSectionDataPoint(pts,pa,va,tolSq);
addCutSectionDataPoint(pts,pb,vb,tolSq);
continue;
}
if(aOn)addCutSectionDataPoint(pts,pa,va,tolSq);
if(bOn)addCutSectionDataPoint(pts,pb,vb,tolSq);
if((da<-eps&&db>eps)||(da>eps&&db<-eps)){
var denom=da-db;
if(Math.abs(denom)>1e-20){
var t=da/denom;
if(t>=-1e-8&&t<=1+1e-8){
addCutSectionDataPoint(pts,[
pa[0]+(pb[0]-pa[0])*t,
pa[1]+(pb[1]-pa[1])*t,
pa[2]+(pb[2]-pa[2])*t
],va+(vb-va)*t,tolSq);
}
}
}
}
if(pts.length<2)return null;
if(pts.length===2)return [pts[0],pts[1]];
var bestA=pts[0],bestB=pts[1],bestD=-1;
for(var i=0;i<pts.length;i++){
for(var j=i+1;j<pts.length;j++){
var dx=pts[i].pos[0]-pts[j].pos[0],dy=pts[i].pos[1]-pts[j].pos[1],dz=pts[i].pos[2]-pts[j].pos[2];
var d=dx*dx+dy*dy+dz*dz;
if(d>bestD){bestD=d;bestA=pts[i];bestB=pts[j];}
}
}
return bestD>tolSq?[bestA,bestB]:null;
}
function lerpCutSectionDataPoint(a,b,t){
return{
pos:[
a.pos[0]+(b.pos[0]-a.pos[0])*t,
a.pos[1]+(b.pos[1]-a.pos[1])*t,
a.pos[2]+(b.pos[2]-a.pos[2])*t
],
realValue:a.realValue+(b.realValue-a.realValue)*t
};
}
function clipSectionSegmentToHalfspaces(a,b,planes,skipPlaneId,eps){
var t0=0,t1=1;
for(var i=0;i<planes.length;i++){
var plane=planes[i];
if(!plane||plane.id===skipPlaneId)continue;
var d0=getClipPlaneSignedDistance(a.pos,plane);
var d1=getClipPlaneSignedDistance(b.pos,plane);
var in0=d0>=-eps,in1=d1>=-eps;
if(in0&&in1)continue;
if(!in0&&!in1)return null;
var denom=d0-d1;
if(Math.abs(denom)<=1e-20)return null;
var t=d0/denom;
if(!in0){if(t>t0)t0=t;}
else if(!in1){if(t<t1)t1=t;}
if(t0>t1+1e-8)return null;
}
var outA=lerpCutSectionDataPoint(a,b,t0);
var outB=lerpCutSectionDataPoint(a,b,t1);
var dx=outA.pos[0]-outB.pos[0],dy=outA.pos[1]-outB.pos[1],dz=outA.pos[2]-outB.pos[2];
if((dx*dx+dy*dy+dz*dz)<=eps*eps)return null;
return [outA,outB];
}
function sortSectionPolygonPoints(poly,plane){
if(!poly||poly.length<3)return poly;
var basis=getCutSectionPlaneBasis(plane);
var cx=0,cy=0,cz=0;
for(var i=0;i<poly.length;i++){
cx+=poly[i].pos[0];cy+=poly[i].pos[1];cz+=poly[i].pos[2];
}
cx/=poly.length;cy/=poly.length;cz/=poly.length;
poly.sort(function(pa,pb){
var va=new THREE.Vector3(pa.pos[0]-cx,pa.pos[1]-cy,pa.pos[2]-cz);
var vb=new THREE.Vector3(pb.pos[0]-cx,pb.pos[1]-cy,pb.pos[2]-cz);
var aa=Math.atan2(va.dot(basis.v),va.dot(basis.u));
var ab=Math.atan2(vb.dot(basis.v),vb.dot(basis.u));
return aa-ab;
});
return poly;
}
function clipSectionPolygonAgainstHalfspace(poly,plane,eps){
if(!poly||poly.length<3)return [];
var out=[];
for(var i=0;i<poly.length;i++){
var a=poly[i],b=poly[(i+1)%poly.length];
var da=getClipPlaneSignedDistance(a.pos,plane);
var db=getClipPlaneSignedDistance(b.pos,plane);
var aIn=da>=-eps,bIn=db>=-eps;
if(aIn&&bIn){
out.push({pos:b.pos.slice(),realValue:b.realValue});
continue;
}
if(aIn&&!bIn){
var t1=da/(da-db);
out.push(lerpCutSectionDataPoint(a,b,t1));
continue;
}
if(!aIn&&bIn){
var t2=da/(da-db);
out.push(lerpCutSectionDataPoint(a,b,t2));
out.push({pos:b.pos.slice(),realValue:b.realValue});
}
}
return out;
}
function getElementCutSectionPolygon(elemIdx,nodes,plane,planes,eps){
var conn=getSectionElementConn(elemIdx,nodes);
var edges=getSectionElementEdgePairs(conn);
if(!conn||!edges)return null;
var pts=[];
var tolSq=eps*eps;
var elemVal=getCutSectionFaceRealValue(elemIdx);
for(var ei=0;ei<edges.length;ei++){
var edge=edges[ei];
var ia=conn[edge[0]],ib=conn[edge[1]];
if(ia<0||ib<0||ia>=nodes.length||ib>=nodes.length)continue;
var pa=nodes[ia],pb=nodes[ib];
if(!pa||!pb)continue;
var va=(elemVal!==null)?elemVal:getCutSectionNodeRealValue(ia);
var vb=(elemVal!==null)?elemVal:getCutSectionNodeRealValue(ib);
var da=getClipPlaneSignedDistance(pa,plane);
var db=getClipPlaneSignedDistance(pb,plane);
var aOn=Math.abs(da)<=eps;
var bOn=Math.abs(db)<=eps;
if(aOn&&bOn){
addCutSectionDataPoint(pts,pa,va,tolSq);
addCutSectionDataPoint(pts,pb,vb,tolSq);
continue;
}
if(aOn)addCutSectionDataPoint(pts,pa,va,tolSq);
if(bOn)addCutSectionDataPoint(pts,pb,vb,tolSq);
if((da<-eps&&db>eps)||(da>eps&&db<-eps)){
var denom=da-db;
if(Math.abs(denom)>1e-20){
var t=da/denom;
if(t>=-1e-8&&t<=1+1e-8){
addCutSectionDataPoint(pts,[
pa[0]+(pb[0]-pa[0])*t,
pa[1]+(pb[1]-pa[1])*t,
pa[2]+(pb[2]-pa[2])*t
],va+(vb-va)*t,tolSq);
}
}
}
}
if(pts.length<3)return null;
var poly=sortSectionPolygonPoints(pts,plane);
for(var pi=0;pi<planes.length;pi++){
var other=planes[pi];
if(!other||other.id===plane.id)continue;
poly=clipSectionPolygonAgainstHalfspace(poly,other,eps);
if(poly.length<3)return null;
poly=sortSectionPolygonPoints(poly,plane);
}
return poly;
}
function getCutSectionPlaneBasis(plane){
var n=new THREE.Vector3(plane.normal[0],plane.normal[1],plane.normal[2]).normalize();
var ref=Math.abs(n.z)<0.9?new THREE.Vector3(0,0,1):new THREE.Vector3(0,1,0);
var u=new THREE.Vector3().crossVectors(ref,n).normalize();
if(u.lengthSq()<1e-16)u=new THREE.Vector3().crossVectors(new THREE.Vector3(1,0,0),n).normalize();
var v=new THREE.Vector3().crossVectors(n,u).normalize();
return{u:u,v:v};
}
function collectCutSectionLoops(segments,plane,tol){
if(!segments||segments.length===0)return [];
var basis=getCutSectionPlaneBasis(plane);
var origin=new THREE.Vector3(segments[0].a.pos[0],segments[0].a.pos[1],segments[0].a.pos[2]);
function projectPoint(pos){
var pv=new THREE.Vector3(pos[0],pos[1],pos[2]).sub(origin);
return{x:pv.dot(basis.u),y:pv.dot(basis.v)};
}
function pointKey(pos){
var p2=projectPoint(pos);
return Math.round(p2.x/tol)+','+Math.round(p2.y/tol);
}
var verts=Object.create(null),edges=[];
function ensureVert(segPoint){
var key=pointKey(segPoint.pos);
var p2=projectPoint(segPoint.pos);
if(!verts[key]){
verts[key]={key:key,pos:segPoint.pos.slice(),realValue:segPoint.realValue,x:p2.x,y:p2.y,links:[]};
}else{
verts[key].pos[0]=(verts[key].pos[0]+segPoint.pos[0])*0.5;
verts[key].pos[1]=(verts[key].pos[1]+segPoint.pos[1])*0.5;
verts[key].pos[2]=(verts[key].pos[2]+segPoint.pos[2])*0.5;
verts[key].realValue=(verts[key].realValue+segPoint.realValue)*0.5;
verts[key].x=(verts[key].x+p2.x)*0.5;
verts[key].y=(verts[key].y+p2.y)*0.5;
}
return key;
}
for(var i=0;i<segments.length;i++){
var sa=ensureVert(segments[i].a),sb=ensureVert(segments[i].b);
if(sa===sb)continue;
if(verts[sa].links.indexOf(sb)<0)verts[sa].links.push(sb);
if(verts[sb].links.indexOf(sa)<0)verts[sb].links.push(sa);
edges.push([sa,sb]);
}
var visited=Object.create(null),loops=[];
function edgeKey(a,b){return a<b?(a+'|'+b):(b+'|'+a);}
for(var ei=0;ei<edges.length;ei++){
var start=edges[ei][0],next=edges[ei][1];
if(visited[edgeKey(start,next)])continue;
var loop=[start],prev=null,curr=start,guard=0;
while(next&&guard<edges.length+8){
guard++;
visited[edgeKey(curr,next)]=1;
prev=curr;
curr=next;
if(curr===start){break;}
loop.push(curr);
var links=verts[curr].links;
next=null;
for(var li=0;li<links.length;li++){
if(links[li]===prev)continue;
if(!visited[edgeKey(curr,links[li])]){next=links[li];break;}
}
if(!next){
for(var li2=0;li2<links.length;li2++){
if(links[li2]!==prev){next=links[li2];break;}
}
}
}
if(curr===start&&loop.length>=3){
loops.push(loop.map(function(k){return verts[k];}));
}
}
return loops;
}
function getCutSectionLoopColor(realVal){
if(noContour)return new THREE.Color(0.78,0.78,0.78);
return getLegendColorFromReal(realVal);
}
function appendElementCutSectionSurface(poly,planeOffsetVec,posOut,colOut,valOut){
if(!poly||poly.length<3)return;
for(var i=1;i<poly.length-1;i++){
var tri=[poly[0],poly[i],poly[i+1]];
for(var k=0;k<3;k++){
var p=tri[k].pos;
var cc=getCutSectionLoopColor(tri[k].realValue);
posOut.push(p[0]+planeOffsetVec[0],p[1]+planeOffsetVec[1],p[2]+planeOffsetVec[2]);
colOut.push(cc.r,cc.g,cc.b);
if(valOut)valOut.push(tri[k].realValue);
}
}
}
function appendCutSectionSurfaceGeometry(segments,plane,tol,posOut,colOut){
if(!segments||segments.length===0||!THREE.ShapeUtils||!THREE.ShapeUtils.triangulateShape)return;
var loops=collectCutSectionLoops(segments,plane,tol);
for(var li=0;li<loops.length;li++){
var loop=loops[li];
if(!loop||loop.length<3)continue;
var contour=[];
for(var i=0;i<loop.length;i++)contour.push(new THREE.Vector2(loop[i].x,loop[i].y));
var tris=THREE.ShapeUtils.triangulateShape(contour,[]);
if(!tris||tris.length===0)continue;
for(var ti=0;ti<tris.length;ti++){
var tri=tris[ti];
for(var k=0;k<3;k++){
var vtx=loop[tri[k]];
var cc=getCutSectionLoopColor(vtx.realValue);
posOut.push(vtx.pos[0],vtx.pos[1],vtx.pos[2]);
colOut.push(cc.r,cc.g,cc.b);
}
}
}
}
function ensureCutSectionProjectionLines(){
if(!sc)return null;
if(!cutSectionLines){
var geo=new THREE.BufferGeometry();
geo.setAttribute('position',new THREE.Float32BufferAttribute([],3));
cutSectionLines=new THREE.LineSegments(geo,new THREE.LineBasicMaterial({color:0x000000,transparent:true,opacity:0.98,depthTest:true,depthWrite:false}));
cutSectionLines.renderOrder=999;
cutSectionLines.frustumCulled=false;
sc.add(cutSectionLines);
}
return cutSectionLines;
}
function ensureCutSectionProjectionWideLines(){
if(!sc)return null;
if(!cutSectionLinesWide){
var geo=new THREE.BufferGeometry();
geo.setAttribute('position',new THREE.Float32BufferAttribute([],3));
cutSectionLinesWide=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({
color:0x000000,
side:THREE.DoubleSide,
transparent:true,
opacity:0.98,
depthTest:true,
depthWrite:false,
polygonOffset:true,
polygonOffsetFactor:-2,
polygonOffsetUnits:-2
}));
cutSectionLinesWide.renderOrder=998;
cutSectionLinesWide.frustumCulled=false;
sc.add(cutSectionLinesWide);
}
return cutSectionLinesWide;
}
function appendCutSectionWideSegment(a,b,normal,offset,halfWidth,posOut){
if(!a||!b||!normal||!posOut)return;
var ax=a[0]+normal[0]*offset,ay=a[1]+normal[1]*offset,az=a[2]+normal[2]*offset;
var bx=b[0]+normal[0]*offset,by=b[1]+normal[1]*offset,bz=b[2]+normal[2]*offset;
var tx=bx-ax,ty=by-ay,tz=bz-az;
var tLen=Math.sqrt(tx*tx+ty*ty+tz*tz);
if(!(tLen>1e-12))return;
var sx=(normal[1]*tz)-(normal[2]*ty);
var sy=(normal[2]*tx)-(normal[0]*tz);
var sz=(normal[0]*ty)-(normal[1]*tx);
var sLen=Math.sqrt(sx*sx+sy*sy+sz*sz);
if(!(sLen>1e-12))return;
sx=(sx/sLen)*halfWidth;
sy=(sy/sLen)*halfWidth;
sz=(sz/sLen)*halfWidth;
var p1=[ax-sx,ay-sy,az-sz];
var p2=[ax+sx,ay+sy,az+sz];
var p3=[bx+sx,by+sy,bz+sz];
var p4=[bx-sx,by-sy,bz-sz];
posOut.push(
p1[0],p1[1],p1[2], p2[0],p2[1],p2[2], p3[0],p3[1],p3[2],
p1[0],p1[1],p1[2], p3[0],p3[1],p3[2], p4[0],p4[1],p4[2]
);
}
function ensureCutSectionProjectionSurface(){
if(!sc)return null;
if(!cutSectionSurface){
var geo=new THREE.BufferGeometry();
geo.setAttribute('position',new THREE.Float32BufferAttribute([],3));
geo.setAttribute('color',new THREE.Float32BufferAttribute([],3));
geo.setAttribute('sval',new THREE.Float32BufferAttribute([],1));
cutSectionSurface=new THREE.Mesh(geo,new THREE.MeshPhongMaterial({
vertexColors:true,
side:THREE.DoubleSide,
flatShading:false,
depthWrite:true,
polygonOffset:true,
polygonOffsetFactor:-1,
polygonOffsetUnits:-1
}));
cutSectionSurface.renderOrder=997;
cutSectionSurface.frustumCulled=false;
sc.add(cutSectionSurface);
}
return cutSectionSurface;
}
function shouldUseCutSectionSharpDiscrete(){
return !!(discreteMode&&!noContour&&!isCutSectionElementMode());
}
function createCutSectionProjectionColorMaterial(){
return new THREE.MeshPhongMaterial({
vertexColors:true,
side:THREE.DoubleSide,
flatShading:false,
depthWrite:true,
polygonOffset:true,
polygonOffsetFactor:-1,
polygonOffsetUnits:-1
});
}
function createCutSectionProjectionSharpMaterial(){
var mat=createSharpDiscreteMaterial(getDiscreteLegendShaderData());
mat.depthWrite=true;
mat.depthTest=true;
mat.polygonOffset=true;
mat.polygonOffsetFactor=-1;
mat.polygonOffsetUnits=-1;
return mat;
}
function syncCutSectionProjectionSurfaceMaterial(mesh){
if(!mesh)return;
var wantsSharp=shouldUseCutSectionSharpDiscrete();
var modeKey=wantsSharp?'sharp':'color';
if(wantsSharp||!mesh.material||mesh.userData.cutSectionSurfaceMode!==modeKey){
if(mesh.material)mesh.material.dispose();
mesh.material=wantsSharp?createCutSectionProjectionSharpMaterial():createCutSectionProjectionColorMaterial();
mesh.userData.cutSectionSurfaceMode=modeKey;
}
}
function clearCutSectionProjection(){
if(cutSectionLines)cutSectionLines.visible=false;
if(cutSectionLinesWide)cutSectionLinesWide.visible=false;
if(cutSectionSurface)cutSectionSurface.visible=false;
}
function updateCutSectionProjection(nodes){
var obj=ensureCutSectionProjectionLines();
var wide=ensureCutSectionProjectionWideLines();
var surf=ensureCutSectionProjectionSurface();
if(!obj||!wide||!surf)return;
syncCutSectionProjectionSurfaceMaterial(surf);
if(!cutSectionProjectionOn||!anyCutEnabled()||!nodes||!visibleFaces||visibleFaces.length===0){
obj.visible=false;
wide.visible=false;
surf.visible=false;
return;
}
var planes=getActiveClipHalfspaces();
if(!planes||planes.length===0){
obj.visible=false;
wide.visible=false;
surf.visible=false;
return;
}
var diag=Math.max(getMeshDiagonalSize(),1);
var eps=Math.max(diag*1e-7,1e-9);
var dedupeTol=Math.max(diag*2e-6,1e-8);
var planeOffset=Math.max(diag*1e-4,1e-8);
var lineOffset=planeOffset*1.8;
var wideOffset=planeOffset*1.2;
var wideHalfWidth=Math.max(diag*0.0018,planeOffset*8.0);
var pos=[],widePos=[];
var surfPos=[],surfCol=[],surfVal=[];
var segBuckets=Object.create(null);
for(var pi=0;pi<planes.length;pi++){
var plane=planes[pi];
var nx=plane.normal[0],ny=plane.normal[1],nz=plane.normal[2];
for(var fi=0;fi<visibleFaces.length;fi++){
var seg=getTrianglePlaneIntersectionData(visibleFaces[fi],nodes,plane,eps,visibleFaceElemIdx[fi]);
if(!seg)continue;
seg=clipSectionSegmentToHalfspaces(seg[0],seg[1],planes,plane.id,eps);
if(!seg)continue;
var a=seg[0].pos,b=seg[1].pos;
var key=getCutSectionSegmentKey(a,b,dedupeTol,plane.id);
var bucket=segBuckets[key];
if(!bucket){
bucket={a:seg[0],b:seg[1],nx:nx,ny:ny,nz:nz,count:0,planeId:plane.id};
segBuckets[key]=bucket;
}else{
bucket.a.realValue=(bucket.a.realValue+seg[0].realValue)*0.5;
bucket.b.realValue=(bucket.b.realValue+seg[1].realValue)*0.5;
}
bucket.count++;
}
}
for(var key in segBuckets){
if(!Object.prototype.hasOwnProperty.call(segBuckets,key))continue;
var bucket=segBuckets[key];
if(bucket.count!==1)continue;
appendCutSectionWideSegment(bucket.a.pos,bucket.b.pos,[bucket.nx,bucket.ny,bucket.nz],wideOffset,wideHalfWidth,widePos);
pos.push(
bucket.a.pos[0]+bucket.nx*lineOffset,bucket.a.pos[1]+bucket.ny*lineOffset,bucket.a.pos[2]+bucket.nz*lineOffset,
bucket.b.pos[0]+bucket.nx*lineOffset,bucket.b.pos[1]+bucket.ny*lineOffset,bucket.b.pos[2]+bucket.nz*lineOffset
);
}
if(obj.geometry)obj.geometry.dispose();
obj.geometry=new THREE.BufferGeometry();
if(pos.length>0){
obj.geometry.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
obj.visible=true;
}else{
obj.visible=false;
}
if(wide.geometry)wide.geometry.dispose();
wide.geometry=new THREE.BufferGeometry();
if(widePos.length>0){
wide.geometry.setAttribute('position',new THREE.Float32BufferAttribute(widePos,3));
wide.geometry.computeVertexNormals();
wide.visible=true;
}else{
wide.visible=false;
}
for(var pi2=0;pi2<planes.length;pi2++){
var plane2=planes[pi2];
var planeOffsetVec=[plane2.normal[0]*planeOffset,plane2.normal[1]*planeOffset,plane2.normal[2]*planeOffset];
for(var ei=0;ei<EIDS.length;ei++){
if(isElemHidden(ei))continue;
var poly=getElementCutSectionPolygon(ei,nodes,plane2,planes,eps);
if(!poly||poly.length<3)continue;
appendElementCutSectionSurface(poly,planeOffsetVec,surfPos,surfCol,surfVal);
}
}
if(surf.geometry)surf.geometry.dispose();
surf.geometry=new THREE.BufferGeometry();
if(surfPos.length>0){
surf.geometry.setAttribute('position',new THREE.Float32BufferAttribute(surfPos,3));
surf.geometry.setAttribute('color',new THREE.Float32BufferAttribute(surfCol,3));
surf.geometry.setAttribute('sval',new THREE.Float32BufferAttribute(surfVal,1));
surf.geometry.computeVertexNormals();
surf.visible=true;
}else{
surf.visible=false;
}
}
function tgCutSectionProjection(enabled){
cutSectionProjectionOn=!!enabled;
var cb=document.getElementById('cut-section-proj');
if(cb)cb.checked=cutSectionProjectionOn;
if(anyCutEnabled()){
if(cutSectionProjectionOn)applyCutClipping();
else setCutClippingPlanesForScene([]);
}
rebuildCutMesh();
}
function getCutSignedDistance(p,cut){
if(!p||!cut)return -Infinity;
if(cut.type==='rotation-sector'&&cut.axisDir&&cut.refPoint&&cut.baseVisible){
var ax=cut.axisDir[0],ay=cut.axisDir[1],az=cut.axisDir[2];
var px0=p[0]-cut.refPoint[0],py0=p[1]-cut.refPoint[1],pz0=p[2]-cut.refPoint[2];
var dotAxis=(px0*ax)+(py0*ay)+(pz0*az);
var qx=px0-dotAxis*ax,qy=py0-dotAxis*ay,qz=pz0-dotAxis*az;
var qLen=Math.sqrt(qx*qx+qy*qy+qz*qz);
if(!(qLen>1e-12))return 1;
qx/=qLen;qy/=qLen;qz/=qLen;
var bx=cut.baseVisible[0],by=cut.baseVisible[1],bz=cut.baseVisible[2];
var bLen=Math.sqrt(bx*bx+by*by+bz*bz);
if(!(bLen>1e-12))return -Infinity;
bx/=bLen;by/=bLen;bz/=bLen;
var cx=(by*qz)-(bz*qy),cy=(bz*qx)-(bx*qz),cz=(bx*qy)-(by*qx);
var phi=Math.atan2((ax*cx)+(ay*cy)+(az*cz),(bx*qx)+(by*qy)+(bz*qz));
var delta=Math.atan2(Math.sin(cut.angle2-cut.angle1),Math.cos(cut.angle2-cut.angle1));
var mid=cut.angle1+(delta*0.5);
var diff=Math.atan2(Math.sin(phi-mid),Math.cos(phi-mid));
var half=(Math.PI-Math.abs(delta))*0.5;
return half-Math.abs(diff);
}
if(!cut.normal)return -Infinity;
return (p[0]*cut.normal[0])+(p[1]*cut.normal[1])+(p[2]*cut.normal[2])+cut.constant;
}
function isPointVisibleByCuts(p,cuts){
if(!p)return false;
if(!cuts||cuts.length===0)return true;
for(var ci=0;ci<cuts.length;ci++){
if(getCutSignedDistance(p,cuts[ci])<-1e-10)return false;
}
return true;
}
function isFaceVisible(face,nodes,cuts){
if(cuts.length===0)return true;
// Face is visible if at least one vertex is on the visible side of ALL cut planes
for(var vi=0;vi<face.length;vi++){
var nIdx=face[vi];
if(nIdx<0||nIdx>=nodes.length)continue;
var p=nodes[nIdx];
var passAll=true;
for(var ci=0;ci<cuts.length;ci++){
if(getCutSignedDistance(p,cuts[ci])<-1e-10){passAll=false;break;}
}
if(passAll)return true;
}
return false;
}

let vrfGhostMs=null,vrfGhostEg=null;
function getDiscreteLegendShaderData(){
var valsReal=hasCustomLegend()?legendCustomValues.slice():buildLinearLegendValues(curMin,curMax);
if(!valsReal||valsReal.length!==N_DISC+1)valsReal=buildLinearLegendValues(curMin,curMax);
var valsFix=[];
for(var i=0;i<valsReal.length;i++){
var vv=Number(valsReal[i]);
if(!isFinite(vv))vv=(i>0?valsFix[i-1]:curMax);
valsFix.push(vv);
}
// enforce descending thresholds for robust shader classification
for(var j=1;j<valsFix.length;j++){
if(valsFix[j]>valsFix[j-1])valsFix[j]=valsFix[j-1];
}
var cols=[];
for(var k=0;k<N_DISC;k++){
cols.push(new THREE.Color(getLegendBandHex(k)));
}
return {vals:valsFix,cols:cols};
}
function createSharpDiscreteMaterial(shaderData){
var MAX_BANDS=32;
var vals=(shaderData&&shaderData.vals)?shaderData.vals:[];
var cols=(shaderData&&shaderData.cols)?shaderData.cols:[];
var count=Math.max(1,Math.min(N_DISC,MAX_BANDS));
var uVals=new Array(MAX_BANDS+1).fill(0);
var uCols=[];
for(var uc=0;uc<MAX_BANDS;uc++){uCols.push(new THREE.Vector3(0,0,0));}
for(var vi=0;vi<=count;vi++){
var vv=(vi<vals.length)?vals[vi]:vals[vals.length-1];
if(!isFinite(vv))vv=(vals.length?vals[vals.length-1]:curMin);
uVals[vi]=vv;
}
for(var fi=count+1;fi<=MAX_BANDS;fi++){uVals[fi]=uVals[count];}
for(var ci=0;ci<count;ci++){
var cc=(ci<cols.length&&cols[ci])?cols[ci]:new THREE.Color(getLegendBandHex(ci));
uCols[ci]=new THREE.Vector3(cc.r,cc.g,cc.b);
}
for(var cj=count;cj<MAX_BANDS;cj++){uCols[cj]=uCols[Math.max(0,count-1)].clone();}
var vtxSrc=`attribute float sval;
varying float vVal;
varying vec3 vNormalV;
varying vec3 vViewDir;
#include <clipping_planes_pars_vertex>
void main(){
vVal=sval;
vec4 mvPos=modelViewMatrix*vec4(position,1.0);
vNormalV=normalize(normalMatrix*normal);
vViewDir=normalize(-mvPos.xyz);
#include <clipping_planes_vertex>
gl_Position=projectionMatrix*mvPos;
}`;
var fragSrc=`precision mediump float;
varying float vVal;
varying vec3 vNormalV;
varying vec3 vViewDir;
uniform int uCount;
uniform float uVals[33];
uniform vec3 uCols[32];
#include <clipping_planes_pars_fragment>
void main(){
#include <clipping_planes_fragment>
float t=vVal;
int idx=0;
if(uCount>0){idx=uCount-1;}
if(uCount>0){
float vTop=uVals[0];
float vBot=uVals[32];
if(t>=vTop-1e-8){idx=0;}
else if(t<=vBot+1e-8){idx=uCount-1;}
else{
for(int i=0;i<32;i++){
if(i>=uCount)break;
float vHi=uVals[i];
float vLo=uVals[i+1];
if(t<=vHi+1e-8&&t>=vLo-1e-8){idx=i;break;}
}
}
}
vec3 base=uCols[idx];
vec3 n=normalize(gl_FrontFacing?vNormalV:-vNormalV);
vec3 l1=normalize(vec3(0.577,0.577,0.577));
vec3 l2=normalize(vec3(-0.577,-0.577,0.577));
float diff=max(dot(n,l1),0.0)*0.70+max(dot(n,l2),0.0)*0.30;
float amb=0.35;
vec3 v=normalize(vViewDir);
vec3 h1=normalize(l1+v);
vec3 h2=normalize(l2+v);
float spec=pow(max(dot(n,h1),0.0),24.0)*0.10+pow(max(dot(n,h2),0.0),24.0)*0.04;
vec3 lit=base*(amb+diff)+vec3(spec);
gl_FragColor=vec4(clamp(lit,0.0,1.0),1.0);
}`;
return new THREE.ShaderMaterial({
uniforms:{uCount:{value:count},uVals:{value:uVals},uCols:{value:uCols}},
vertexShader:vtxSrc,
fragmentShader:fragSrc,
clipping:true,
side:THREE.DoubleSide
});
}
function getMeshRenderMode(useCentroid,useSharpDiscrete){
if(useCentroid)return 'centroid';
if(useSharpDiscrete)return 'sharp';
if(noContour)return 'nocontour';
return 'nodal';
}

function getCutTopologySignature(){
var axes=['x','y','z'];
var parts=[];
for(var i=0;i<axes.length;i++){
var a=axes[i];
var c=cutPlanes[a];
if(c&&c.on)parts.push(a+':'+c.pos+':'+c.dir);
else parts.push(a+':off');
}
var rc=sanitizeRotationCutState(cutPlanes.rotation||{});
if(rc.on)parts.push('rot:'+rc.axis+':'+rc.angle+':'+rc.dir+':'+(rc.angle2On?'on':'off')+':'+rc.angle2+':'+rc.dir2+':'+rc.refA+':'+rc.refB);
else parts.push('rot:off');
return parts.join('|');
}

function buildMeshTopologyKey(renderMode){
var vrfSig='off';
if(vrfEnabled){
var lo=isFinite(vrfLo)?Number(vrfLo).toExponential(4):'0';
var hi=isFinite(vrfHi)?Number(vrfHi).toExponential(4):'0';
var contourSig=centroidMode?'centroid':(isElementLocalContourMode()?'elementlocal':'nodal');
vrfSig=lo+':'+hi+':'+contourSig+':'+(currentVar||'');
}
return [
renderMode,
'edge='+edgeMode,
'section='+(cutSectionProjectionOn?'on':'off'),
'cuts='+getCutTopologySignature(),
'hide='+hiddenElemRevision,
'vrf='+vrfSig
].join('|');
}

function finalizeMeshRefresh(){
syncLegendToVisibleRange();
if(hideElemMode&&hideHoverElemIdx>=0&&isElemVisibleNow(hideHoverElemIdx)){
updateHideHoverHighlightFromElem(hideHoverElemIdx);
}else{
clearHideHoverHighlight();
}
updateLegendExtremaTargets();
if(anyCutEnabled()){
if(cutSectionProjectionOn)applyCutClipping();
else setCutClippingPlanesForScene([]);
}
updateCutSectionProjection(meshNodesRef||getRenderNodes());
}

function tryFastUpdateMeshBuffers(nodes,colors,renderMode,topologyKey){
if(vrfEnabled)return false;
if(anyCutEnabled())return false;
if(edgeMode!=='none')return false;
if(!ms||!ms.geometry)return false;
if(meshTopologyKey!==topologyKey||meshRenderMode!==renderMode)return false;
if(!meshVertexNodeIdx||!meshVertexElemIdx)return false;
var g=ms.geometry;
var posAttr=g.getAttribute('position');
var colAttr=g.getAttribute('color');
var svalAttr=g.getAttribute('sval');
if(!posAttr)return false;
if(renderMode==='sharp'){
if(!svalAttr)return false;
if(posAttr.count!==meshVertexNodeIdx.length||svalAttr.count!==meshVertexNodeIdx.length)return false;
}else{
if(!colAttr)return false;
if(posAttr.count!==meshVertexNodeIdx.length||colAttr.count!==meshVertexNodeIdx.length)return false;
}

var posArr=posAttr.array;
for(var i=0,pj=0;i<meshVertexNodeIdx.length;i++,pj+=3){
var ni=meshVertexNodeIdx[i];
var p=(ni>=0&&ni<nodes.length)?nodes[ni]:null;
if(p){
posArr[pj]=p[0];
posArr[pj+1]=p[1];
posArr[pj+2]=p[2];
}else{
posArr[pj]=0;
posArr[pj+1]=0;
posArr[pj+2]=0;
}
}
posAttr.needsUpdate=true;
g.computeBoundingSphere();

var dR=dataMax-dataMin;if(Math.abs(dR)<1e-30)dR=1;
var uR=curMax-curMin;if(Math.abs(uR)<1e-30)uR=1;
if(renderMode==='sharp'){
var svalArr=svalAttr.array;
for(var si=0;si<meshVertexNodeIdx.length;si++){
var nIdxSharp=meshVertexNodeIdx[si];
var rvSharp=curMin;
if(rawColors&&nIdxSharp>=0&&nIdxSharp<rawColors.length){
rvSharp=dataMin+rawColors[nIdxSharp]*dR;
}else if(colors&&nIdxSharp>=0&&nIdxSharp<colors.length){
rvSharp=curMin+colors[nIdxSharp]*uR;
}
if(!isFinite(rvSharp))rvSharp=curMin;
svalArr[si]=rvSharp;
}
svalAttr.needsUpdate=true;
}else{
var colArr=colAttr.array;
for(var ci=0,cj=0;ci<meshVertexNodeIdx.length;ci++,cj+=3){
var nIdx=meshVertexNodeIdx[ci];
var eIdx=meshVertexElemIdx[ci];
var rr=0.6,gg=0.6,bb=0.7;

if(renderMode==='centroid'){
if(centroidRawColors&&eIdx!==undefined&&eIdx!==null&&eIdx>=0&&eIdx<centroidRawColors.length){
var cv=centroidRawColors[eIdx];
var rv=centroidDataMin+cv*(centroidDataMax-centroidDataMin);
var cc=getLegendColorFromReal(rv);
rr=cc.r;gg=cc.g;bb=cc.b;
}
}else if(renderMode==='nocontour'){
var nc=getNoContourFaceRgb(eIdx);
if(nc){rr=nc.r;gg=nc.g;bb=nc.b;}
}else if(colors&&nIdx>=0&&nIdx<colors.length){
if(hasCustomLegend()){
var rvNode;
if(rawColors&&nIdx<rawColors.length){rvNode=dataMin+rawColors[nIdx]*dR;}
else{rvNode=curMin+colors[nIdx]*uR;}
var cCust=getLegendColorFromReal(rvNode);
rr=cCust.r;gg=cCust.g;bb=cCust.b;
}else{
var cStd=gc(colors[nIdx]);
rr=cStd.r;gg=cStd.g;bb=cStd.b;
}
}

colArr[cj]=rr;
colArr[cj+1]=gg;
colArr[cj+2]=bb;
}
colAttr.needsUpdate=true;
}

var wfOn=document.getElementById('wf')?document.getElementById('wf').checked:false;
if(ms.material&&ms.material.wireframe!==undefined)ms.material.wireframe=wfOn;

var now=(window&&window.performance&&window.performance.now)?window.performance.now():Date.now();
if((now-lastFastNormalUpdateMs)>=FAST_NORMAL_UPDATE_MS){
g.computeVertexNormals();
lastFastNormalUpdateMs=now;
}
return true;
}

function cm(nodes,colors,opts){
opts=opts||{};
if(edgeMode==='all'&&!ALL_EDGES_EXPORTED){
edgeMode='feature';
var edSelAllOff=document.getElementById('ed');
if(edSelAllOff)edSelAllOff.value='feature';
}
meshNodesRef=nodes;
curColors=colors;
var cuts=getActiveCuts();
var useElementLocalContour=isElementLocalContourMode()&&centroidRawColors&&!noContour;
var useCentroid=(centroidMode||useElementLocalContour)&&centroidRawColors&&!noContour;
var useSharpDiscrete=discreteMode&&!useCentroid&&!noContour;
var renderMode=getMeshRenderMode(useCentroid,useSharpDiscrete);
var topologyKey=buildMeshTopologyKey(renderMode);

if(!opts.forceRebuild&&tryFastUpdateMeshBuffers(nodes,colors,renderMode,topologyKey)){
finalizeMeshRefresh();
return;
}

if(ms)sc.remove(ms);if(eg)sc.remove(eg);if(featureEg)sc.remove(featureEg);
if(vrfGhostMs){sc.remove(vrfGhostMs);vrfGhostMs=null;}
if(vrfGhostEg){sc.remove(vrfGhostEg);vrfGhostEg=null;}
ms=null;eg=null;featureEg=null;

// Harmonic mode can force external surface only for higher performance.
// Section mesh on plane also needs the boundary shell only, otherwise internal faces
// remain visible behind the cut and the model looks transparent.
var useBoundarySurface=EXTERNAL_SURFACE_ONLY||cutSectionProjectionOn;
var faceSrc=useBoundarySurface?BF:getFullFaces();
var faceElemSrc=useBoundarySurface?BFE:getFullFaceElemMap();
visibleFaces=[];
visibleFaceElemIdx=[];
visibleElemMap=Object.create(null);
visibleNodeMap=Object.create(null);
visibleElemFaceMap=Object.create(null);
const g=new THREE.BufferGeometry(),v=[],cl=[],sv=[];
const meshNodeIdx=[],meshElemIdx=[];

faceSrc.forEach(function(f,fi){
var faceEi=faceElemSrc[fi];
if(faceEi!==undefined&&faceEi!==null&&faceEi>=0&&isElemHidden(faceEi))return;
if(!isFaceVisible(f,nodes,cuts))return;
var verts=[];
f.forEach(function(i){if(i>=0&&i<nodes.length)verts.push(i);});
if(verts.length<3)return;

// VRF check
if(vrfEnabled&&!noContour){
var srcColors=useCentroid?null:rawColors;
if(useCentroid&&centroidRawColors){
var ei=faceElemSrc[fi];
if(ei!==undefined&&ei<centroidRawColors.length){
var rv=centroidDataMin+centroidRawColors[ei]*(centroidDataMax-centroidDataMin);
if(rv<vrfLo||rv>vrfHi)return;
}
}else if(srcColors){
var sum=0,cnt=0;
verts.forEach(function(i){if(i<srcColors.length){sum+=srcColors[i];cnt++;}});
if(cnt>0){
var avgNorm=sum/cnt;
var realVal=dataMin+avgNorm*(dataMax-dataMin);
if(realVal<vrfLo||realVal>vrfHi)return;
}
}
}

visibleFaces.push(f);
visibleFaceElemIdx.push(faceEi);
if(faceEi!==undefined&&faceEi!==null&&faceEi>=0){
visibleElemMap[faceEi]=1;
var faceList=visibleElemFaceMap[faceEi];
if(!faceList){faceList=[];visibleElemFaceMap[faceEi]=faceList;}
faceList.push(visibleFaces.length-1);
}
for(var vi=0;vi<verts.length;vi++){visibleNodeMap[verts[vi]]=1;}

// Element-driven mode: uniform color per face from element value
if(useCentroid){
var eiFace=faceEi;
if(eiFace!==undefined&&eiFace<centroidRawColors.length){
var cv=centroidRawColors[eiFace];
var rvFace=centroidDataMin+cv*(centroidDataMax-centroidDataMin);
var cFace=getLegendColorFromReal(rvFace);
verts.forEach(function(){cl.push(cFace.r,cFace.g,cFace.b);});
}else{
verts.forEach(function(){cl.push(0.6,0.6,0.7);});
}
verts.forEach(function(i){
v.push(nodes[i][0],nodes[i][1],nodes[i][2]);
meshNodeIdx.push(i);
meshElemIdx.push(faceEi!==undefined&&faceEi!==null?faceEi:-1);
});
return;
}

// Sharp + Discrete mode: interpolated scalar with sharp contour bands (no blur)
if(useSharpDiscrete){
var uRsharp=curMax-curMin;if(Math.abs(uRsharp)<1e-30)uRsharp=1;
verts.forEach(function(i){
v.push(nodes[i][0],nodes[i][1],nodes[i][2]);
meshNodeIdx.push(i);
meshElemIdx.push(faceEi!==undefined&&faceEi!==null?faceEi:-1);
var rvNode;
if(rawColors&&i<rawColors.length){rvNode=dataMin+rawColors[i]*(dataMax-dataMin);}
else if(colors&&i<colors.length){rvNode=curMin+colors[i]*uRsharp;}
else{rvNode=curMin;}
if(!isFinite(rvNode))rvNode=curMin;
sv.push(rvNode);
});
return;
}

var ncFaceColor=noContour?getNoContourFaceRgb(faceEi):null;
verts.forEach(function(i){
v.push(nodes[i][0],nodes[i][1],nodes[i][2]);
meshNodeIdx.push(i);
meshElemIdx.push(faceEi!==undefined&&faceEi!==null?faceEi:-1);
if(noContour){
cl.push(ncFaceColor.r,ncFaceColor.g,ncFaceColor.b);
}
else if(colors&&i<colors.length){
var cNode;
if(hasCustomLegend()){
var rvNode;
if(rawColors&&i<rawColors.length){rvNode=dataMin+rawColors[i]*(dataMax-dataMin);}
else{var uRnode=curMax-curMin;if(Math.abs(uRnode)<1e-30)uRnode=1;rvNode=curMin+colors[i]*uRnode;}
cNode=getLegendColorFromReal(rvNode);
}else{
cNode=gc(colors[i]);
}
cl.push(cNode.r,cNode.g,cNode.b);
}
else{cl.push(0.6,0.6,0.7);}
});
});

g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));
if(useSharpDiscrete){
g.setAttribute('sval',new THREE.Float32BufferAttribute(sv,1));
}else{
g.setAttribute('color',new THREE.Float32BufferAttribute(cl,3));
}
g.computeVertexNormals();

var wfOn=document.getElementById('wf')?document.getElementById('wf').checked:false;
var meshMat;
if(useSharpDiscrete){
var shData=getDiscreteLegendShaderData();
meshMat=createSharpDiscreteMaterial(shData);
}else{
meshMat=new THREE.MeshPhongMaterial({vertexColors:true,side:THREE.DoubleSide,flatShading:false});
}
meshMat.wireframe=wfOn;
ms=new THREE.Mesh(g,meshMat);
sc.add(ms);

meshTopologyKey=topologyKey;
meshRenderMode=renderMode;
meshVertexNodeIdx=meshNodeIdx;
meshVertexElemIdx=meshElemIdx;
lastFastNormalUpdateMs=0;

if(edgeMode==='all'){
// In heavy export mode, allow attempting full-edge build regardless of face count.
var canAttemptAllEdges=ALL_EDGES_EXPORTED||visibleFaces.length<=MAX_FULL_EDGES_FACE_COUNT;
if(canAttemptAllEdges){
try{
eg=new THREE.LineSegments(new THREE.EdgesGeometry(g,1),new THREE.LineBasicMaterial({color:0x333333,opacity:0.4,transparent:true}));
eg.visible=true;
sc.add(eg);
}catch(e){
eg=null;
console.warn('All edges build failed:',e);
}
}else{
eg=null;
edgeMode='feature';
var edSel=document.getElementById('ed');
if(edSel)edSel.value='feature';
if(!autoEdgeFallbackNotified){
autoEdgeFallbackNotified=true;
document.getElementById('st').textContent='All Edges unavailable for this mesh size. Switched to Feature Edges.';
}
}
}

if(edgeMode==='feature'){
var bfGeo=new THREE.BufferGeometry(),bfV=[];
BF.forEach(function(f,bfi){
var bElem=BFE[bfi];
if(bElem!==undefined&&bElem!==null&&bElem>=0&&isElemHidden(bElem))return;
if(!isFaceVisible(f,nodes,cuts))return;
// For boundary feature edges, also check VRF
if(vrfEnabled&&!noContour){
if(useCentroid&&centroidRawColors){
// In element-driven mode, check element value for this boundary face
var bei=BFE[bfi];
if(bei!==undefined&&bei<centroidRawColors.length){
var rv=centroidDataMin+centroidRawColors[bei]*(centroidDataMax-centroidDataMin);
if(rv<vrfLo||rv>vrfHi)return;
}
}else if(rawColors){
var anyIn=false;
f.forEach(function(i){
if(i>=0&&i<rawColors.length){
var rv=dataMin+rawColors[i]*(dataMax-dataMin);
if(rv>=vrfLo&&rv<=vrfHi)anyIn=true;
}
});
if(!anyIn)return;
}
}
f.forEach(function(i){if(i>=0&&i<nodes.length){bfV.push(nodes[i][0],nodes[i][1],nodes[i][2]);}});
});
if(bfV.length>0){
bfGeo.setAttribute('position',new THREE.Float32BufferAttribute(bfV,3));
bfGeo.computeVertexNormals();
featureEg=new THREE.LineSegments(new THREE.EdgesGeometry(bfGeo,25),new THREE.LineBasicMaterial({color:0x222222,opacity:0.7,transparent:true}));
featureEg.visible=true;
sc.add(featureEg);
}
}

// VRF ghost mesh: use BOUNDARY faces only (external) - same as undeformed mesh
if(vrfEnabled&&!noContour&&(rawColors||centroidRawColors)){
var ghostBfV=[];
BF.forEach(function(f,bfi){
var bElem=BFE[bfi];
if(bElem!==undefined&&bElem!==null&&bElem>=0&&isElemHidden(bElem))return;
if(!isFaceVisible(f,nodes,cuts))return;
if(useCentroid&&centroidRawColors){
// In element-driven mode, check element value
var bei=BFE[bfi];
if(bei!==undefined&&bei<centroidRawColors.length){
var rv=centroidDataMin+centroidRawColors[bei]*(centroidDataMax-centroidDataMin);
if(rv>=vrfLo&&rv<=vrfHi)return;// in range = not ghost
}else{return;}
}else if(rawColors){
var allOut=true;
f.forEach(function(i){
if(i>=0&&i<rawColors.length){
var rv=dataMin+rawColors[i]*(dataMax-dataMin);
if(rv>=vrfLo&&rv<=vrfHi)allOut=false;
}
});
if(!allOut)return;
}
f.forEach(function(i){if(i>=0&&i<nodes.length){ghostBfV.push(nodes[i][0],nodes[i][1],nodes[i][2]);}});
});
if(ghostBfV.length>0){
var gGeo=new THREE.BufferGeometry();
gGeo.setAttribute('position',new THREE.Float32BufferAttribute(ghostBfV,3));
gGeo.computeVertexNormals();
vrfGhostMs=new THREE.Mesh(gGeo,new THREE.MeshPhongMaterial({color:0xffffff,opacity:0.22,transparent:true,side:THREE.FrontSide,depthWrite:false}));
vrfGhostMs.renderOrder=-2;
sc.add(vrfGhostMs);
vrfGhostEg=new THREE.LineSegments(new THREE.EdgesGeometry(gGeo,25),new THREE.LineBasicMaterial({color:0x999999,opacity:0.3,transparent:true}));
vrfGhostEg.renderOrder=-1;
sc.add(vrfGhostEg);
}
}

if(eg)eg.visible=(edgeMode==='all');
if(featureEg)featureEg.visible=(edgeMode==='feature');
finalizeMeshRefresh();
}

// Remap 0-1 colors from data range to user range
function remapColors(origColors,dMin,dMax,uMin,uMax){
if(!origColors)return null;
var out=[];
var dR=dMax-dMin;if(Math.abs(dR)<1e-30)dR=1;
var uR=uMax-uMin;if(Math.abs(uR)<1e-30)uR=1;
for(var i=0;i<origColors.length;i++){
var realVal=dMin+origColors[i]*dR;
var nv=(realVal-uMin)/uR;
out.push(Math.max(0,Math.min(1,nv)));
}
return out;
}

// Apply user legend range
function applyLegRange(){
var uMinStr=document.getElementById('leg-min').value.trim();
var uMaxStr=document.getElementById('leg-max').value.trim();
var uMin=parseFloat(uMinStr),uMax=parseFloat(uMaxStr);
if(isNaN(uMin)||isNaN(uMax)){document.getElementById('st').textContent='Invalid min/max values';return;}
if(uMin>=uMax){document.getElementById('st').textContent='Min must be less than Max';return;}
curMin=uMin;curMax=uMax;
legendAutoResetPending=false;
if(hasCustomLegend())legendCustomValues=buildLinearLegendValues(curMin,curMax);
updateLegendRangeInputs();
ulv(curMin,curMax);
updGrad();
updCb();
if(cst&&AD[cst]){
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){
cm(getRenderNodes(),rawColors);
}else if(rawColors){
var rc=remapColors(rawColors,dataMin,dataMax,curMin,curMax);
cm(getRenderNodes(),rc);
}
if(vrfEnabled)updateVRFLabels();
document.getElementById('st').textContent='Legend range applied: '+formatLegendNumber(curMin)+' to '+formatLegendNumber(curMax);
}
}

// Reset legend to data range
function resetLegRange(){
curMin=dataMin;curMax=dataMax;
legendAutoResetPending=false;
if(hasCustomLegend())legendCustomValues=buildLinearLegendValues(curMin,curMax);
updateLegendRangeInputs();
ulv(curMin,curMax);
updGrad();
updCb();
// Restore original colors
if(cst&&AD[cst]){
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){
cm(getRenderNodes(),rawColors);
}else if(rawColors){
cm(getRenderNodes(),rawColors.slice());
}
if(vrfEnabled)updateVRFLabels();
document.getElementById('st').textContent='Legend range reset to data range';
}
}

function gc(t){
t=clamp01(t);
if(discreteMode){
if(!hasCustomLegend()){
var idx=Math.floor((1-t)*N_DISC);
if(idx<0)idx=0;
if(idx>=N_DISC)idx=N_DISC-1;
return new THREE.Color(getLegendDiscreteHexForMap(legendColorMapId,idx,N_DISC));
}
t=Math.floor(t*N_DISC)/N_DISC;
}
return legendBaseColor(t);
}

function uc(){
// Camera position = target + quaternion-rotated forward vector * distance
const fwd=new THREE.Vector3(0,0,1).applyQuaternion(camQuat);
const pos=tg.clone().add(fwd.multiplyScalar(camDist));
const up=new THREE.Vector3(0,1,0).applyQuaternion(camQuat);
caPersp.position.copy(pos);caPersp.up.copy(up);caPersp.lookAt(tg);
caOrtho.position.copy(pos);caOrtho.up.copy(up);caOrtho.lookAt(tg);
const zoomFactor=B*3/camDist;caOrtho.zoom=zoomFactor;caOrtho.updateProjectionMatrix();
}

function viewerInitWarn(step,e){
console.error('[VMAP] Init step failed ['+step+']:',e);
var stEl=document.getElementById('st');
if(stEl){
var msg='Warning ['+step+']: '+(e&&e.message?e.message:e);
if(String(stEl.textContent||'').indexOf('ERROR:')!==0)stEl.textContent=msg;
}
}

function safeViewerInitStep(step,fn){
try{
return fn();
}catch(e){
viewerInitWarn(step,e);
return null;
}
}

function pssFallback(){
const sel=document.getElementById('ss');
if(!sel)return;
if(!SL||SL.length===0){
sel.innerHTML='<option value="">No increments</option>';
return;
}
sel.innerHTML='<option value="">-- Select Increment --</option>';
SL.forEach(function(s){
const o=document.createElement('option');
o.value=s&&s.id!==undefined&&s.id!==null?s.id:'';
var inc=(s&&s.increment!==undefined&&s.increment!==null)?s.increment:'?';
o.textContent='Inc '+inc;
sel.appendChild(o);
});
}

function pss(){
const sel=document.getElementById('ss');
if(SL.length===0){sel.innerHTML='<option value="">No increments</option>';return;}
sel.innerHTML='<option value="">-- Select Increment --</option>';
SL.forEach(function(s){
const o=document.createElement('option');
o.value=s.id;
var timeVal=Number(s.time);
if(!isFinite(timeVal))timeVal=0;
var freqVal=Number(s.frequency);
if(!isFinite(freqVal)){
freqVal=NaN;
if(VIEWER_MODE==='harmonic'&&isFinite(timeVal)&&Math.abs(timeVal)>1e-12){
freqVal=timeVal;
}
var srcTxt=(s&&s.title!==undefined&&s.title!==null&&String(s.title).trim().length>0)?String(s.title):((s&&s.id!==undefined&&s.id!==null)?String(s.id):'');
var mHz=srcTxt.match(/([-+]?\\d+(?:[.,]\\d+)?)\\s*hz/i);
if(mHz&&mHz[1]){
var fParsed=parseFloat(String(mHz[1]).replace(',','.'));
if(isFinite(fParsed))freqVal=fParsed;
}
}
if(VIEWER_MODE==='harmonic'){
if(isFinite(freqVal)){
var fTxt=(Math.abs(freqVal-Math.round(freqVal))<1e-9)?String(Math.round(freqVal)):freqVal.toFixed(5).replace(/\.?0+$/,'');
o.textContent='Inc '+s.increment+' (freq='+fTxt+'Hz)';
}else{
o.textContent='Inc '+s.increment+' (freq=n/a)';
}
}else{
o.textContent='Inc '+s.increment+' (t='+timeVal.toFixed(5)+')';
}
sel.appendChild(o);
});
}

function ovs(){
const sel=document.getElementById('vs');
currentVar=sel.value;
AD=ensureVarStateCache(currentVar);
cst=null;rawColors=null;centroidRawColors=null;
dataMin=0;dataMax=1;curMin=0;curMax=1;
legendAutoResetPending=true;
refreshDisplacementComponentUi();
updateLegendRangeInputs();
document.getElementById('leg-data-info').textContent='Data range: select an increment';
document.getElementById('ss').value='';
updateLegendStateMeta(null);
refreshExtrapolationSummary();
cn=ON.slice();cm(getRenderNodes(),null);
ulv(0,1);
updGrad();
updCb();
document.getElementById('st').textContent='Output changed to: '+getCurrentVarDisplayName()+' - Select an increment';
}

function osc(){
const sel=document.getElementById('ss');
const sid=sel.value;
if(!sid){
cst=null;cn=ON.slice();cm(getRenderNodes(),null);
updateLegendStateMeta(null);
document.getElementById('st').textContent='Undeformed mesh';
return;}
const sd=getStateData(currentVar,sid);
if(!sd){
cst=null;cn=ON.slice();cm(getRenderNodes(),null);
updateLegendStateMeta(null);
document.getElementById('st').textContent='Increment data not available for '+sid;
return;
}
AD=ensureVarStateCache(currentVar);
cst=sid;
asc();
document.getElementById('st').textContent='Increment '+sd.increment+' loaded';
}

function scaleText(v){
if(!isFinite(v))return '1';
return String(Number(v.toPrecision(8)));
}
function getScaleFactorFromUI(){
var sf=document.getElementById('scf');
if(sf){
var txt=String(sf.value||'').trim();
var val=parseFloat(txt);
if(!isFinite(val))val=cs;
if(!isFinite(val)||val<=0)val=DEFAULT_SCALE_FACTOR>0?DEFAULT_SCALE_FACTOR:1;
return val;
}
var sr=document.getElementById('scr');
if(sr){
var sval=parseFloat(sr.value);
if(isFinite(sval))return sval;
}
return (isFinite(cs)&&cs>0)?cs:(DEFAULT_SCALE_FACTOR>0?DEFAULT_SCALE_FACTOR:1);
}
function setScaleFactorToUI(v){
var val=(isFinite(v)&&v>0)?v:(DEFAULT_SCALE_FACTOR>0?DEFAULT_SCALE_FACTOR:1);
cs=val;
var sf=document.getElementById('scf');
if(sf)sf.value=scaleText(val);
var sr=document.getElementById('scr');
if(sr)sr.value=String(val);
var sv=document.getElementById('scv');
if(sv)sv.textContent=scaleText(val);
}
function usc(v){
var vv=parseFloat(v);
if(!isFinite(vv)||vv<=0)return;
setScaleFactorToUI(vv);
}

function asc(){
if(!cst){document.getElementById('st').textContent='Select increment first';return;}
setScaleFactorToUI(getScaleFactorFromUI());
const sd=AD[cst]||getStateData(currentVar,cst);
if(!sd){document.getElementById('st').textContent='Increment data unavailable';return;}
updateLegendStateMeta({increment:(sd.increment!==undefined?sd.increment:null),time:(sd.time!==undefined?sd.time:null)});
rawColors=sd.colors?sd.colors.slice():null;
centroidRawColors=sd.centroid_colors?sd.centroid_colors.slice():null;
// Update legend range FIRST so cm() uses correct curMin/curMax for centroid mapping
ucr(sd);
var drawColors=noContour?null:sd.colors;
var sdNodes=getStateNodes(cst);
if(sdNodes){
cn=[];
for(let i=0;i<ON.length;i++){
const o=ON[i],d=(sdNodes[i]||o);
cn.push([o[0]+(d[0]-o[0])*cs,o[1]+(d[1]-o[1])*cs,o[2]+(d[2]-o[2])*cs]);}
cm(getRenderNodes(),drawColors);
document.getElementById('st').textContent='Scale '+scaleText(cs)+'x applied ('+getCurrentVarDisplayName()+')';
}else{cm(ON,drawColors);
document.getElementById('st').textContent='No displacement data';}
// Update active measurement for new increment
if(hasAnyMeasurements())updateMeasurement();
// Update pinned/table values for new increment
if(pinnedNodes.length>0||pinnedElems.length>0)updatePinnedValues();
else if(tableFormVisible)updateTableForm();
}

function ucr(sd){
if(!sd||sd.color_min===undefined||sd.color_max===undefined){ulv(0,1);return;}
// Always update centroid ranges if available
if(sd.centroid_min!==undefined){centroidDataMin=sd.centroid_min;centroidDataMax=sd.centroid_max;}
// Set legend data range based on mode
if((centroidMode||isElementLocalContourMode())&&sd.centroid_min!==undefined){
dataMin=sd.centroid_min;dataMax=sd.centroid_max;
}else{
dataMin=sd.color_min;dataMax=sd.color_max;
}
if(dynamicLegend||legendAutoResetPending||!isFinite(curMin)||!isFinite(curMax)){
curMin=dataMin;curMax=dataMax;
legendAutoResetPending=false;
if(hasCustomLegend())legendCustomValues=buildLinearLegendValues(curMin,curMax);
}
updateLegendRangeInputs();
var srcInfo=getLegendDataSourceInfo();
document.getElementById('leg-data-info').textContent='Data range: '+formatLegendNumber(dataMin)+' ~ '+formatLegendNumber(dataMax)+srcInfo;
ulv(curMin,curMax);
updGrad();updCb();
if(vrfEnabled)updateVRFLabels();
// For non-centroid mode with manual legend range, remap nodal colors
if(!(centroidMode||isElementLocalContourMode())&&!noContour&&!dynamicLegend&&rawColors&&(Math.abs(curMin-dataMin)>1e-20||Math.abs(curMax-dataMax)>1e-20)){
var rc=remapColors(rawColors,dataMin,dataMax,curMin,curMax);cm(getRenderNodes(),rc);}
}

function computeVisibleLegendRange(){
var minV=Infinity,maxV=-Infinity;
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){
var cR=centroidDataMax-centroidDataMin;
if(Math.abs(cR)<1e-30)cR=1;
for(var ek in visibleElemMap){
if(!Object.prototype.hasOwnProperty.call(visibleElemMap,ek)||!visibleElemMap[ek])continue;
var ei=parseInt(ek,10);
if(!isFinite(ei)||ei<0||ei>=centroidRawColors.length)continue;
var cv=centroidRawColors[ei];
if(cv===undefined||cv===null||!isFinite(cv))continue;
var rv=centroidDataMin+cv*cR;
if(rv<minV)minV=rv;
if(rv>maxV)maxV=rv;
}
}else if(rawColors){
var dR=dataMax-dataMin;
if(Math.abs(dR)<1e-30)dR=1;
for(var nk in visibleNodeMap){
if(!Object.prototype.hasOwnProperty.call(visibleNodeMap,nk)||!visibleNodeMap[nk])continue;
var ni=parseInt(nk,10);
if(!isFinite(ni)||ni<0||ni>=rawColors.length)continue;
var nv=rawColors[ni];
if(nv===undefined||nv===null||!isFinite(nv))continue;
var realVal=dataMin+nv*dR;
if(realVal<minV)minV=realVal;
if(realVal>maxV)maxV=realVal;
}
}
if(!isFinite(minV)||!isFinite(maxV))return null;
if(Math.abs(maxV-minV)<1e-30){
var tiny=Math.max(1e-12,Math.abs(minV)*1e-12);
maxV=minV+tiny;
}
return {min:minV,max:maxV};
}

function syncLegendToVisibleRange(){
if(!cst)return;
var visRange=computeVisibleLegendRange();
var srcInfo=getLegendDataSourceInfo();
if(dynamicLegend){
var oldMin=curMin,oldMax=curMax;
if(visRange){
curMin=visRange.min;curMax=visRange.max;
}else{
curMin=dataMin;curMax=dataMax;
}
if(hasCustomLegend())legendCustomValues=buildLinearLegendValues(curMin,curMax);
updateLegendRangeInputs();
if(!legendVisibilityRebuildGuard&&!(centroidMode||isElementLocalContourMode())&&!noContour&&rawColors){
var rangeChanged=(Math.abs(oldMin-curMin)>1e-20||Math.abs(oldMax-curMax)>1e-20);
if(rangeChanged){
legendVisibilityRebuildGuard=true;
try{
var rc=remapColors(rawColors,dataMin,dataMax,curMin,curMax);
cm(getRenderNodes(),rc);
return;
}finally{
legendVisibilityRebuildGuard=false;
}
}
}
}
var infoEl=document.getElementById('leg-data-info');
if(infoEl){
if(visRange){
infoEl.textContent='Data range: '+formatLegendNumber(visRange.min)+' ~ '+formatLegendNumber(visRange.max)+srcInfo+' (visible)';
}else if(countHiddenElements()>0){
infoEl.textContent='Data range: no visible values (all selected elements hidden)';
}else{
infoEl.textContent='Data range: '+formatLegendNumber(dataMin)+' ~ '+formatLegendNumber(dataMax)+srcInfo;
}
}
ulv(curMin,curMax);
updGrad();updCb();
if(vrfEnabled)updateVRFLabels();
}

// Update legend with N intermediate values on the LEFT side (editable)
function ulv(vmin,vmax){
const cont=document.getElementById('legend-values');
if(!cont)return;
cont.innerHTML='';
const vals=hasCustomLegend()?legendCustomValues.slice():buildLinearLegendValues(vmin,vmax);
if(!legendEditMode){
cont.classList.remove('legend-edit');
for(let i=0;i<=N_DISC;i++){
const d=document.createElement('div');
d.className='legend-val-text';
d.textContent=formatLegendNumber(vals[i]);
d.style.fontSize=legFontSize+'px';
d.title='Double-click to edit legend values';
d.addEventListener('dblclick',function(){enterLegendEdit({valueIdx:i});});
cont.appendChild(d);
}
return;
}
cont.classList.add('legend-edit');
for(let i=0;i<=N_DISC;i++){
const row=document.createElement('div');
row.className='legend-val-row';
const inp=document.createElement('input');
inp.type='text';
inp.className='legend-val-edit';
inp.setAttribute('data-vidx',String(i));
inp.value=formatLegendNumber(vals[i]);
inp.style.fontSize=legFontSize+'px';
inp.addEventListener('change',function(){onLegendValueEdit(i,this.value);});
row.appendChild(inp);
if(i<N_DISC){
const cInp=document.createElement('input');
cInp.type='color';
cInp.className='legend-col-edit';
cInp.setAttribute('data-cidx',String(i));
cInp.value=getLegendBandHex(i);
cInp.addEventListener('input',function(){onLegendColorEdit(i,this.value);});
row.appendChild(cInp);
}else{
const sp=document.createElement('span');
sp.className='legend-col-space';
row.appendChild(sp);
}
cont.appendChild(row);
}
if(legendEditFocusValue>=0){
var fVal=cont.querySelector('input.legend-val-edit[data-vidx="'+legendEditFocusValue+'"]');
if(fVal){fVal.focus();fVal.select();}
}
if(legendEditFocusColor>=0){
var fCol=cont.querySelector('input.legend-col-edit[data-cidx="'+legendEditFocusColor+'"]');
if(fCol){fCol.focus();fCol.click();}
}
legendEditFocusValue=-1;
legendEditFocusColor=-1;
}

function ugrl(){
var startIn=document.getElementById('gif-start');
var endIn=document.getElementById('gif-end');
var startVal=document.getElementById('gif-start-val');
var endVal=document.getElementById('gif-end-val');
if(!startIn||!endIn||!startVal||!endVal)return;
const si=parseInt(startIn.value);
const ei=parseInt(endIn.value);
startVal.textContent=SL[si]?SL[si].increment:si;
endVal.textContent=SL[ei]?SL[ei].increment:ei;
}

function getAnimSpeedValue(){
var speedInput=document.getElementById('anim-speed');
if(!speedInput)return 5;
var speed=parseInt(speedInput.value,10);
if(!isFinite(speed))speed=5;
if(speed<1)speed=1;
if(speed>10)speed=10;
return speed;
}

function animIsActive(){
return animMode!=='none';
}

function setAnimStatus(msg,color){
var stEl=document.getElementById('anim-status');
if(!stEl)return;
stEl.textContent=msg;
if(color)stEl.style.color=color;
}

function refreshAnimTransportButtons(){
var isActive=animIsActive();
var canStep=(isActive&&animMode==='static');
var prevBtn=document.getElementById('anim-prev-btn');
var pauseBtn=document.getElementById('anim-pause-btn');
var nextBtn=document.getElementById('anim-next-btn');
if(prevBtn){
prevBtn.disabled=!canStep;
prevBtn.style.opacity=canStep?'1':'0.55';
prevBtn.style.cursor=canStep?'pointer':'not-allowed';
}
if(nextBtn){
nextBtn.disabled=!canStep;
nextBtn.style.opacity=canStep?'1':'0.55';
nextBtn.style.cursor=canStep?'pointer':'not-allowed';
}
if(pauseBtn){
pauseBtn.disabled=!isActive;
pauseBtn.style.opacity=isActive?'1':'0.55';
pauseBtn.style.cursor=isActive?'pointer':'not-allowed';
pauseBtn.innerHTML=(isActive&&animPaused)?'&#9654; Resume':'&#10074;&#10074; Pause';
}
}

function applyStaticAnimationState(idx){
if(!SL||SL.length===0)return false;
if(!isFinite(idx))return false;
if(idx<animRangeStart)idx=animRangeStart;
if(idx>animRangeEnd)idx=animRangeEnd;
if(idx<0||idx>=SL.length)return false;
animIndex=idx;
var state=SL[animIndex];
if(!state)return false;
xyAnimIndex=animIndex;
var sel=document.getElementById('ss');
if(sel)sel.value=state.id;
if(cst!==state.id){osc();}
else{asc();}
if(xyPlotVisible)drawPlot();
return true;
}

function stepStaticAnimation(dir){
if(animMode!=='static')return false;
if(!isFinite(dir)||dir===0)return false;
if(animIndex<animRangeStart||animIndex>animRangeEnd){
animIndex=Math.max(animRangeStart,Math.min(animRangeEnd,animIndex));
}
if(dir>0){
if(animIndex<animRangeEnd)animIndex++;
}else{
if(animIndex>animRangeStart)animIndex--;
}
if(animStaticSwing)animDirection=(dir>0)?1:-1;
return applyStaticAnimationState(animIndex);
}

function startStaticAnimationTimer(){
if(animMode!=='static')return;
if(animInterval){clearInterval(animInterval);animInterval=null;}
animPaused=false;
animStepAccum=0;
const tickMs=16;
var lastTickMs=(window&&window.performance&&window.performance.now)?window.performance.now():Date.now();
animInterval=setInterval(function(){
var now=(window&&window.performance&&window.performance.now)?window.performance.now():Date.now();
var dt=(now-lastTickMs)/1000;
if(!isFinite(dt)||dt<=0)dt=tickMs/1000;
if(dt>0.25)dt=0.25;
lastTickMs=now;
var speedNow=getAnimSpeedValue();
var statesPerSec=0.8+(2.2*speedNow);
animStepAccum+=dt*statesPerSec;
var steps=Math.floor(animStepAccum);
if(steps<1)return;
if(steps>300)steps=300;
animStepAccum-=steps;
for(var k=0;k<steps;k++){
if(animStaticSwing){
if(animDirection>0&&animIndex>=animRangeEnd)animDirection=-1;
else if(animDirection<0&&animIndex<=animRangeStart)animDirection=1;
animIndex+=animDirection;
if(animIndex<animRangeStart)animIndex=animRangeStart;
if(animIndex>animRangeEnd)animIndex=animRangeEnd;
}else{
animIndex++;
if(animIndex>animRangeEnd)animIndex=animRangeStart;
}
}
applyStaticAnimationState(animIndex);
},tickMs);
refreshAnimTransportButtons();
}

function startHarmonicAnimationTimer(){
if(animMode!=='harmonic')return;
if(animInterval){clearInterval(animInterval);animInterval=null;}
animPaused=false;
const tickMs=16;
var lastTickMs=(window&&window.performance&&window.performance.now)?window.performance.now():Date.now();
animInterval=setInterval(function(){
var now=(window&&window.performance&&window.performance.now)?window.performance.now():Date.now();
var dt=(now-lastTickMs)/1000;
if(!isFinite(dt)||dt<=0)dt=tickMs/1000;
if(dt>0.25)dt=0.25;
lastTickMs=now;
var speedNow=getAnimSpeedValue();
var cyclesPerSec=0.12+(0.10*speedNow);
harmonicPhase+=dt*cyclesPerSec*(Math.PI*2);
if(harmonicPhase>Math.PI*2)harmonicPhase=harmonicPhase%(Math.PI*2);
if(!applyHarmonicFrame(harmonicPhase)){stopAnimation();return;}
},tickMs);
refreshAnimTransportButtons();
}

function updateAnimationModeControls(){
var lockHarmonic=(VIEWER_MODE==='harmonic');
if(lockHarmonic&&(!animHarmonic))animHarmonic=true;
var useHarmonic=lockHarmonic;
var sIn=document.getElementById('gif-start');
var eIn=document.getElementById('gif-end');
if(sIn){
sIn.disabled=useHarmonic;
sIn.style.opacity=useHarmonic?'0.55':'1';
sIn.style.cursor=useHarmonic?'not-allowed':'';
}
if(eIn){
eIn.disabled=useHarmonic;
eIn.style.opacity=useHarmonic?'0.55':'1';
eIn.style.cursor=useHarmonic?'not-allowed':'';
}
var sVal=document.getElementById('gif-start-val');
if(sVal)sVal.style.opacity=useHarmonic?'0.55':'1';
var eVal=document.getElementById('gif-end-val');
if(eVal)eVal.style.opacity=useHarmonic?'0.55':'1';
var btn=document.getElementById('anim-harmonic-btn');
if(btn){
btn.disabled=lockHarmonic;
btn.style.opacity=lockHarmonic?'0.75':'1';
btn.style.cursor=lockHarmonic?'not-allowed':'pointer';
}
var modeLbl=document.getElementById('anim-mode-label');
if(modeLbl)modeLbl.textContent=lockHarmonic?'Harmonic:':'Swing:';
var modeHint=document.getElementById('anim-mode-hint');
if(modeHint)modeHint.textContent=lockHarmonic?'Full cycle (-180 to 180 deg)':'Min Inc <-> Max Inc';
refreshAnimTransportButtons();
}

function refreshAnimHarmonicButton(){
var btn=document.getElementById('anim-harmonic-btn');
if(!btn)return;
if(VIEWER_MODE==='harmonic'){
animHarmonic=true;
animSwing=false;
btn.textContent='On';
btn.style.background='#00C853';
}else{
animHarmonic=false;
btn.textContent=animSwing?'On':'Off';
btn.style.background=animSwing?'#00C853':'#D32F2F';
}
btn.style.color='#fff';
updateAnimationModeControls();
}

function getHarmonicBaseStateId(){
var sel=document.getElementById('ss');
var sid=sel?sel.value:'';
if(!sid&&cst)sid=cst;
if(!sid)return null;
if(!hasStateData(currentVar,sid))return null;
var sd=AD[sid]||getStateData(currentVar,sid);
if(!sd)return null;
return sid;
}

function beginHarmonicPerformanceMode(){
if(harmonicPerfActive)return;
harmonicPerfActive=true;
harmonicPerfPrevEdgeMode=edgeMode;
harmonicPerfLastTableUpdateMs=0;
var edSel=document.getElementById('ed');
if(edSel){
edSel.disabled=true;
edSel.style.opacity='0.55';
edSel.style.cursor='not-allowed';
}
if(edgeMode!=='none'){
edgeMode='none';
if(eg)eg.visible=false;
if(featureEg)featureEg.visible=false;
if(edSel)edSel.value='none';
}
}

function endHarmonicPerformanceMode(){
if(!harmonicPerfActive)return;
harmonicPerfActive=false;
harmonicPerfLastTableUpdateMs=0;
var restoreEdgeMode=harmonicPerfPrevEdgeMode;
harmonicPerfPrevEdgeMode=null;
var edSel=document.getElementById('ed');
if(edSel){
edSel.disabled=false;
edSel.style.opacity='1';
edSel.style.cursor='';
}
if(restoreEdgeMode&&restoreEdgeMode!==edgeMode){
tgeMode(restoreEdgeMode);
}
}

function applyHarmonicFrame(phase){
if(!cst)return false;
const sd=AD[cst]||getStateData(currentVar,cst);
if(!sd)return false;
rawColors=sd.colors||null;
centroidRawColors=sd.centroid_colors||null;
if(!harmonicLegendSyncDone){
ucr(sd);
harmonicLegendSyncDone=true;
}
var drawColors=noContour?null:sd.colors;
var sdNodes=getStateNodes(cst);
if(!sdNodes){
cm(ON,drawColors);
if(hasAnyMeasurements())updateMeasurement();
if(pinnedNodes.length>0||pinnedElems.length>0)updatePinnedValues();
else if(tableFormVisible){
var nowNoDisp=(window&&window.performance&&window.performance.now)?window.performance.now():Date.now();
if(!harmonicPerfActive||nowNoDisp-harmonicPerfLastTableUpdateMs>=180){
updateTableForm();
harmonicPerfLastTableUpdateMs=nowNoDisp;
}
}
return true;
}
var amp=cs*Math.sin(phase);
if(!cn||cn.length!==ON.length){
cn=[];
for(let ci=0;ci<ON.length;ci++)cn.push([0,0,0]);
}
for(let i=0;i<ON.length;i++){
const o=ON[i],d=(sdNodes[i]||o);
var row=cn[i];
row[0]=o[0]+(d[0]-o[0])*amp;
row[1]=o[1]+(d[1]-o[1])*amp;
row[2]=o[2]+(d[2]-o[2])*amp;
}
cm(getRenderNodes(),drawColors);
if(hasAnyMeasurements())updateMeasurement();
if(pinnedNodes.length>0||pinnedElems.length>0)updatePinnedValues();
else if(tableFormVisible){
var now=(window&&window.performance&&window.performance.now)?window.performance.now():Date.now();
if(!harmonicPerfActive||now-harmonicPerfLastTableUpdateMs>=180){
updateTableForm();
harmonicPerfLastTableUpdateMs=now;
}
}
return true;
}

function restoreHarmonicBaseState(){
if(!harmonicBaseStateId)return;
if(!hasStateData(currentVar,harmonicBaseStateId))return;
var sel=document.getElementById('ss');
if(sel)sel.value=harmonicBaseStateId;
if(cst!==harmonicBaseStateId){osc();}
else{asc();}
}

function tgAnimHarmonic(forceOn){
if(animIsActive()||animInterval)stopAnimation();
if(VIEWER_MODE==='harmonic'){
animHarmonic=true;
animSwing=false;
}else{
animHarmonic=false;
animSwing=(forceOn===undefined)?(!animSwing):!!forceOn;
}
harmonicLegendSyncDone=false;
refreshAnimHarmonicButton();
if(VIEWER_MODE==='harmonic'){
setAnimStatus('Harmonic mode ON (full cycle)','#00C853');
}else{
harmonicPhase=0;
if(animSwing){
setAnimStatus('Swing mode ON (min to max to min)','#00C853');
}else{
setAnimStatus('Swing mode OFF','#FF6D00');
}
}
refreshAnimTransportButtons();
}

function playAnimation(){
if(animIsActive()&&animPaused){
if(animMode==='harmonic'){
startHarmonicAnimationTimer();
const sidResume=harmonicBaseStateId||getHarmonicBaseStateId();
const sdResume=sidResume?(AD[sidResume]||getStateData(currentVar,sidResume)):null;
setAnimStatus('Playing Harmonic: Inc '+(sdResume?sdResume.increment:sidResume)+' (full cycle)...','#00C853');
}else if(animMode==='static'){
startStaticAnimationTimer();
if(SL[animRangeStart]&&SL[animRangeEnd]){
setAnimStatus(animStaticSwing?('Playing Swing: Inc '+SL[animRangeStart].increment+' <-> '+SL[animRangeEnd].increment+'...'):('Playing Inc '+SL[animRangeStart].increment+' to '+SL[animRangeEnd].increment+'...'),'#00C853');
}else{
setAnimStatus('Playing animation...','#00C853');
}
}
refreshAnimTransportButtons();
return;
}
if(animIsActive()&&!animPaused){
refreshAnimTransportButtons();
return;
}
if(VIEWER_MODE==='harmonic'||animHarmonic){
const sid=getHarmonicBaseStateId();
if(!sid){
setAnimStatus('Select one increment for Harmonic mode','#FF6D00');
refreshAnimTransportButtons();
return;
}
stopAnimation();
harmonicBaseStateId=sid;
document.getElementById('ss').value=sid;
if(cst!==sid){osc();}else{asc();}
const sdBase=AD[sid]||getStateData(currentVar,sid);
harmonicPhase=0;
harmonicLegendSyncDone=false;
beginHarmonicPerformanceMode();
if(!applyHarmonicFrame(harmonicPhase)){
setAnimStatus('Harmonic animation unavailable for selected increment','#FF6D00');
endHarmonicPerformanceMode();
refreshAnimTransportButtons();
return;
}
xyAnimIndex=-1;
if(xyPlotVisible)drawPlot();
animMode='harmonic';
animPaused=false;
startHarmonicAnimationTimer();
setAnimStatus('Playing Harmonic: Inc '+(sdBase?sdBase.increment:sid)+' (full cycle)...','#00C853');
refreshAnimTransportButtons();
return;
}
if(SL.length<2){setAnimStatus('Need 2+ increments','#FF6D00');refreshAnimTransportButtons();return;}
stopAnimation();
const startIdx=parseInt(document.getElementById('gif-start').value);
const endIdx=parseInt(document.getElementById('gif-end').value);
const si=Math.min(startIdx,endIdx),ei=Math.max(startIdx,endIdx);
if(ei<=si){setAnimStatus('Invalid range','#FF6D00');refreshAnimTransportButtons();return;}
animStaticSwing=!!animSwing;
animRangeStart=si;
animRangeEnd=ei;
animIndex=si;
animDirection=1;
animMode='static';
animPaused=false;
beginHarmonicPerformanceMode();
if(animIndex>animRangeEnd)animIndex=animRangeStart;
if(!applyStaticAnimationState(animIndex)){
stopAnimation();
setAnimStatus('Increment data unavailable for animation','#FF6D00');
refreshAnimTransportButtons();
return;
}
startStaticAnimationTimer();
setAnimStatus(animStaticSwing?('Playing Swing: Inc '+SL[si].increment+' <-> '+SL[ei].increment+'...'):('Playing Inc '+SL[si].increment+' to '+SL[ei].increment+'...'),'#00C853');
refreshAnimTransportButtons();
}

function pauseAnimation(){
if(!animIsActive()){
setAnimStatus('Start animation first','#FF6D00');
refreshAnimTransportButtons();
return;
}
if(animPaused){
playAnimation();
return;
}
if(animInterval){
clearInterval(animInterval);
animInterval=null;
}
animPaused=true;
if(animMode==='harmonic'){
const sid=harmonicBaseStateId||getHarmonicBaseStateId();
const sd=sid?(AD[sid]||getStateData(currentVar,sid)):null;
setAnimStatus('Paused Harmonic: Inc '+(sd?sd.increment:sid)+' (full cycle)','#FFB300');
}else if(animMode==='static'){
const sCur=SL[animIndex];
setAnimStatus(sCur?('Paused at Inc '+sCur.increment):'Paused','#FFB300');
}else{
setAnimStatus('Paused','#FFB300');
}
refreshAnimTransportButtons();
}

function animPrevIncrement(){
if(animMode!=='static'){
setAnimStatus(animIsActive()?'Previous/Next increment is only available for static animation':'Start animation first','#FF6D00');
refreshAnimTransportButtons();
return;
}
if(!animPaused)pauseAnimation();
if(stepStaticAnimation(-1)){
var cur=SL[animIndex];
setAnimStatus(cur?('Paused at Inc '+cur.increment):'Paused','#FFB300');
}else{
setAnimStatus('Cannot move to previous increment','#FF6D00');
}
refreshAnimTransportButtons();
}

function animNextIncrement(){
if(animMode!=='static'){
setAnimStatus(animIsActive()?'Previous/Next increment is only available for static animation':'Start animation first','#FF6D00');
refreshAnimTransportButtons();
return;
}
if(!animPaused)pauseAnimation();
if(stepStaticAnimation(1)){
var cur=SL[animIndex];
setAnimStatus(cur?('Paused at Inc '+cur.increment):'Paused','#FFB300');
}else{
setAnimStatus('Cannot move to next increment','#FF6D00');
}
refreshAnimTransportButtons();
}

function stopAnimation(){
var hadActive=animIsActive()||!!animInterval||animPaused;
if(animInterval){clearInterval(animInterval);animInterval=null;}
animMode='none';
animPaused=false;
animStaticSwing=false;
animStepAccum=0;
animDirection=1;
animRangeStart=0;
animRangeEnd=0;
if((VIEWER_MODE==='harmonic'||animHarmonic)&&harmonicBaseStateId)restoreHarmonicBaseState();
endHarmonicPerformanceMode();
harmonicLegendSyncDone=false;
harmonicPhase=0;
xyAnimIndex=-1;
if(xyPlotVisible)drawPlot();
if(hadActive)setAnimStatus('Stopped','#FF6D00');
refreshAnimTransportButtons();
}

function roundRectPath(ctx,x,y,w,h,r){
ctx.beginPath();ctx.moveTo(x+r,y);ctx.lineTo(x+w-r,y);ctx.quadraticCurveTo(x+w,y,x+w,y+r);
ctx.lineTo(x+w,y+h-r);ctx.quadraticCurveTo(x+w,y+h,x+w-r,y+h);ctx.lineTo(x+r,y+h);
ctx.quadraticCurveTo(x,y+h,x,y+h-r);ctx.lineTo(x,y+r);ctx.quadraticCurveTo(x,y,x+r,y);
ctx.closePath();ctx.fill();ctx.stroke();
}
function drawMeasOnCanvas(ctx,w,h){
if(!hasAnyMeasurements())return;
var dispNodes=getDisplayNodes();
var cuts=getActiveCuts();
var hasCuts=cuts.length>0;
ctx.save();
ctx.textAlign='center';
ctx.textBaseline='middle';
ctx.font='700 11px Arial';
function drawBundle(bundle){
if(!bundle||!bundle.nodes)return;
for(var i=0;i<bundle.nodes.length;i++){
var ni=bundle.nodes[i];
if(ni<0||ni>=dispNodes.length)continue;
if(!isNodeVisibleNow(ni))continue;
if(hasCuts&&!isPointVisibleByCuts(dispNodes[ni],cuts))continue;
var sp=projectNodeToCanvas(ni,w,h);
if(!sp)continue;
var txt=measureLabelFromIndex(bundle.labelStart+i);
var bg=getMeasureNodeRoleColor(i);
var boxW=Math.max(18,ctx.measureText(txt).width+12);
var boxH=18;
var bx=sp.x+10,by=sp.y-18;
ctx.fillStyle=bg;
ctx.strokeStyle='rgba(255,255,255,0.7)';
ctx.lineWidth=1;
roundRectPath(ctx,bx,by,boxW,boxH,5);
ctx.fill();
ctx.stroke();
ctx.fillStyle='#fff';
ctx.fillText(txt,bx+boxW*0.5,by+boxH*0.5+0.5);
}
}
measGroups.forEach(drawBundle);
if(measDraft)drawBundle(measDraft);
ctx.restore();
}

function fitCanvasText(ctx,text,maxW){
var t=(text===undefined||text===null)?'':String(text);
if(maxW<=6)return '';
if(ctx.measureText(t).width<=maxW)return t;
var ell='...';
var out=t;
while(out.length>0&&ctx.measureText(out+ell).width>maxW){
out=out.slice(0,-1);
}
return out+ell;
}

function drawTableFormOnCanvas(ctx,w,h){
tfLastExportTableLayout=null;
if(!tableFormVisible||!cvEl)return;
var win=document.getElementById('table-form-window');
if(!win)return;
var ws=window.getComputedStyle?window.getComputedStyle(win):null;
if(!ws||ws.display==='none'||ws.visibility==='hidden'||parseFloat(ws.opacity||'1')<=0)return;
var cvRect=cvEl.getBoundingClientRect();
var wr=win.getBoundingClientRect();
var interL=Math.max(cvRect.left,wr.left),interT=Math.max(cvRect.top,wr.top);
var interR=Math.min(cvRect.right,wr.right),interB=Math.min(cvRect.bottom,wr.bottom);
if(interR-interL<6||interB-interT<6)return;
var pxScale=1;
if(re&&re.domElement&&re.domElement.clientWidth){
pxScale=re.domElement.width/re.domElement.clientWidth;
}
var table=document.getElementById('table-form-table');
var body=document.getElementById('table-form-body');
var msg=body?body.textContent.trim():'';
var hasTable=!!table;
var rows=[];
var th0='ID';
var th1='Value';
if(hasTable){
var ths=table.querySelectorAll('thead th');
var trs=table.querySelectorAll('tbody tr');
th0=ths[0]?ths[0].textContent.trim():th0;
th1=ths[1]?ths[1].textContent.trim():th1;
for(var ri=0;ri<trs.length;ri++){
var tds=trs[ri].querySelectorAll('td');
var td0=tds[0],td1=tds[1];
var rk=(trs[ri].getAttribute('data-kind')||'N').toUpperCase();
var rIdx=parseInt(trs[ri].getAttribute('data-idx'),10);
if(!isFinite(rIdx))rIdx=-1;
rows.push({
c0:td0?td0.textContent.trim():'',
c1:td1?td1.textContent.trim():'',
kind:rk,
idx:rIdx,
bg0:(td0&&td0.style&&td0.style.background)?td0.style.background:'#f5f5f5',
bg1:(td1&&td1.style&&td1.style.background)?td1.style.background:'#fff',
fg1:(td1&&td1.style&&td1.style.color)?td1.style.color:'#333'
});
}
}
if(!hasTable&&(!msg||msg.length===0))return;
var preserveSize=tableLinksActive()&&hasTable;
var anchorRect=preserveSize?wr:(hasTable?table.getBoundingClientRect():(body?body.getBoundingClientRect():wr));
var bx=(anchorRect.left-cvRect.left)*pxScale;
var by=(anchorRect.top-cvRect.top)*pxScale;
var outerPad=Math.max(3,Math.round(4*pxScale));
var cellPadX=Math.max(4,Math.round(6*pxScale));
var tfFs=Math.max(8,Math.min(18,tableFormFontSize||10));
var rowFontPx=Math.max(8,Math.round(tfFs*pxScale));
var hdrFontPx=Math.max(8,Math.round(Math.max(8,tfFs-1)*pxScale));
var hdrH=Math.max(rowFontPx+4,Math.round((tfFs+6)*pxScale));
var rowH=Math.max(rowFontPx+4,Math.round((tfFs+5)*pxScale));
var minColW=Math.max(56,Math.round(64*pxScale));
var maxTableW=Math.max(150,Math.min(Math.round(w*0.9),Math.round(430*pxScale)));
ctx.save();
ctx.beginPath();
ctx.rect(0,0,w,h);
ctx.clip();
if(hasTable){
ctx.font='bold '+hdrFontPx+'px Arial';
var mCol0=Math.max(minColW,ctx.measureText(th0).width+cellPadX*2);
var mCol1=Math.max(minColW,ctx.measureText(th1).width+cellPadX*2);
ctx.font='bold '+rowFontPx+'px Arial';
for(var i=0;i<rows.length;i++){
var mw0=ctx.measureText(rows[i].c0).width+cellPadX*2;
var mw1=ctx.measureText(rows[i].c1).width+cellPadX*2;
if(mw0>mCol0)mCol0=mw0;
if(mw1>mCol1)mCol1=mw1;
}
if(preserveSize){
var bw=Math.max(140,wr.width*pxScale);
var bh=Math.max(hdrH+rowH+outerPad*2,wr.height*pxScale);
bx=(wr.left-cvRect.left)*pxScale;
by=(wr.top-cvRect.top)*pxScale;
bx=Math.max(2,Math.min(bx,w-bw-2));
by=Math.max(2,Math.min(by,h-bh-2));
ctx.fillStyle='rgba(255,255,255,0.97)';
ctx.strokeStyle='#2196F3';
ctx.lineWidth=Math.max(1,1.3*pxScale);
roundRectPath(ctx,bx,by,bw,bh,Math.max(4,5*pxScale));
var tx=bx+outerPad;
var ty=by+outerPad;
var tableW=Math.max(80,bw-outerPad*2);
var tableH=Math.max(hdrH+rowH,bh-outerPad*2);
var maxColW=Math.max(72,Math.round(tableW*0.72));
var col0W=Math.min(mCol0,maxColW);
var col1W=Math.min(mCol1,maxColW);
if(col0W+col1W>tableW){
var s=tableW/Math.max(1,col0W+col1W);
col0W=Math.max(40,col0W*s);
col1W=Math.max(40,tableW-col0W);
}
if(col0W+col1W<tableW)col1W=tableW-col0W;
ctx.fillStyle='#2196F3';
ctx.fillRect(tx,ty,tableW,hdrH);
ctx.strokeStyle='#000';
ctx.lineWidth=Math.max(1,1*pxScale);
ctx.beginPath();ctx.moveTo(tx+col0W,ty);ctx.lineTo(tx+col0W,ty+tableH);ctx.stroke();
ctx.fillStyle='#fff';
ctx.textAlign='center';
ctx.textBaseline='middle';
ctx.font='bold '+hdrFontPx+'px Arial';
ctx.fillText(fitCanvasText(ctx,th0,col0W-cellPadX*2),tx+col0W/2,ty+hdrH/2);
ctx.fillText(fitCanvasText(ctx,th1,col1W-cellPadX*2),tx+col0W+col1W/2,ty+hdrH/2);
var rowAreaH=Math.max(1,tableH-hdrH);
var drawCount=Math.max(1,rows.length);
var rowHDraw=rowAreaH/drawCount;
if(rowHDraw<7){
drawCount=Math.max(1,Math.floor(rowAreaH/7));
rowHDraw=rowAreaH/drawCount;
}
var side=((wr.left+wr.width*0.5)<(cvRect.left+cvRect.width*0.5))?'right':'left';
var sx=(side==='right')?(tx+tableW+Math.max(1,1.2*pxScale)):(tx-Math.max(1,1.2*pxScale));
var layoutRows=[];
for(var r=0;r<drawCount&&r<rows.length;r++){
var row=rows[r];
var y1=ty+hdrH+r*rowHDraw;
ctx.fillStyle=row.bg0||'#f5f5f5';ctx.fillRect(tx,y1,col0W,rowHDraw);
ctx.fillStyle=row.bg1||'#fff';ctx.fillRect(tx+col0W,y1,col1W,rowHDraw);
ctx.strokeStyle='#000';
ctx.lineWidth=Math.max(1,1*pxScale);
ctx.beginPath();ctx.moveTo(tx,y1+rowHDraw);ctx.lineTo(tx+tableW,y1+rowHDraw);ctx.stroke();
ctx.textAlign='center';
ctx.textBaseline='middle';
ctx.font='bold '+rowFontPx+'px Arial';
ctx.fillStyle='#333';
ctx.fillText(fitCanvasText(ctx,row.c0,col0W-cellPadX*2),tx+col0W/2,y1+rowHDraw*0.5);
ctx.fillStyle=row.fg1||'#333';
ctx.fillText(fitCanvasText(ctx,row.c1,col1W-cellPadX*2),tx+col0W+col1W/2,y1+rowHDraw*0.5);
layoutRows.push({kind:row.kind,idx:row.idx,sx:sx,sy:y1+rowHDraw*0.5});
}
tfLastExportTableLayout={rows:layoutRows};
}else{
var maxColW=Math.max(72,Math.round(maxTableW*0.7));
var col0W=Math.min(mCol0,maxColW);
var col1W=Math.min(mCol1,maxColW);
var tableW=col0W+col1W;
if(tableW>maxTableW){
var flex=Math.max(30,maxTableW-minColW);
if(col0W>flex)col0W=flex;
col1W=Math.max(minColW,maxTableW-col0W);
tableW=col0W+col1W;
}
var maxAvailH=Math.max(rowH+hdrH+outerPad*2+2,h-8);
var maxRows=Math.floor((maxAvailH-outerPad*2-hdrH)/rowH);
if(!isFinite(maxRows)||maxRows<1)maxRows=1;
var drawCount=Math.min(rows.length,maxRows);
var tableH=hdrH+drawCount*rowH;
var bw=tableW+outerPad*2;
var bh=tableH+outerPad*2;
bx=Math.max(2,Math.min(bx,w-bw-2));
by=Math.max(2,Math.min(by,h-bh-2));
ctx.fillStyle='rgba(255,255,255,0.97)';
ctx.strokeStyle='#2196F3';
ctx.lineWidth=Math.max(1,1.3*pxScale);
roundRectPath(ctx,bx,by,bw,bh,Math.max(4,5*pxScale));
var tx=bx+outerPad;
var ty=by+outerPad;
ctx.fillStyle='#2196F3';
ctx.fillRect(tx,ty,tableW,hdrH);
ctx.strokeStyle='#000';
ctx.lineWidth=Math.max(1,1*pxScale);
ctx.beginPath();ctx.moveTo(tx+col0W,ty);ctx.lineTo(tx+col0W,ty+tableH);ctx.stroke();
ctx.fillStyle='#fff';
ctx.textAlign='center';
ctx.textBaseline='middle';
ctx.font='bold '+hdrFontPx+'px Arial';
ctx.fillText(fitCanvasText(ctx,th0,col0W-cellPadX*2),tx+col0W/2,ty+hdrH/2);
ctx.fillText(fitCanvasText(ctx,th1,col1W-cellPadX*2),tx+col0W+col1W/2,ty+hdrH/2);
var y=ty+hdrH;
for(var r=0;r<drawCount;r++){
var row=rows[r];
ctx.fillStyle=row.bg0||'#f5f5f5';ctx.fillRect(tx,y,col0W,rowH);
ctx.fillStyle=row.bg1||'#fff';ctx.fillRect(tx+col0W,y,col1W,rowH);
ctx.strokeStyle='#000';
ctx.lineWidth=Math.max(1,1*pxScale);
ctx.beginPath();ctx.moveTo(tx,y+rowH);ctx.lineTo(tx+tableW,y+rowH);ctx.stroke();
ctx.textAlign='center';
ctx.textBaseline='middle';
ctx.font='bold '+rowFontPx+'px Arial';
ctx.fillStyle='#333';
ctx.fillText(fitCanvasText(ctx,row.c0,col0W-cellPadX*2),tx+col0W/2,y+rowH/2);
ctx.fillStyle=row.fg1||'#333';
ctx.fillText(fitCanvasText(ctx,row.c1,col1W-cellPadX*2),tx+col0W+col1W/2,y+rowH/2);
y+=rowH;
}
}
}else{
ctx.font='bold '+rowFontPx+'px Arial';
var msgW=Math.max(Math.round(120*pxScale),Math.min(Math.round(maxTableW),ctx.measureText(msg).width+cellPadX*2));
var msgH=Math.max(18,rowH);
var bw=msgW+outerPad*2;
var bh=msgH+outerPad*2;
bx=Math.max(2,Math.min(bx,w-bw-2));
by=Math.max(2,Math.min(by,h-bh-2));
ctx.fillStyle='rgba(255,255,255,0.97)';
ctx.strokeStyle='#2196F3';
ctx.lineWidth=Math.max(1,1.3*pxScale);
roundRectPath(ctx,bx,by,bw,bh,Math.max(4,5*pxScale));
ctx.fillStyle='#555';
ctx.textAlign='center';
ctx.textBaseline='middle';
ctx.fillText(fitCanvasText(ctx,msg,msgW-cellPadX*2),bx+bw/2,by+bh/2);
}
ctx.restore();
}

function roundRect(ctx,x,y,w,h,r){
ctx.beginPath();ctx.moveTo(x+r,y);ctx.lineTo(x+w-r,y);ctx.quadraticCurveTo(x+w,y,x+w,y+r);
ctx.lineTo(x+w,y+h-r);ctx.quadraticCurveTo(x+w,y+h,x+w-r,y+h);ctx.lineTo(x+r,y+h);
ctx.quadraticCurveTo(x,y+h,x,y+h-r);ctx.lineTo(x,y+r);ctx.quadraticCurveTo(x,y,x+r,y);
ctx.closePath();ctx.fill();ctx.stroke();
}

function drawBrandingOverlay(ctx,w,h){
ctx.save();
var pxScale=1;
if(re&&re.domElement&&re.domElement.clientWidth){pxScale=re.domElement.width/re.domElement.clientWidth;}
var topPad=8*pxScale;
var fname=HTMLNAME+'.html';
ctx.font='bold '+Math.round(13*pxScale)+'px Arial';
ctx.fillStyle='rgba(0,0,0,0.92)';
ctx.textAlign='center';
ctx.textBaseline='top';
ctx.fillText(fname,w/2,topPad);
ctx.restore();
}

function buildGifWatermarkTextureFromLogo(){
if(!logoImg||!logoImg.complete||logoImg.naturalWidth<=0||logoImg.naturalHeight<=0)return null;
try{
var srcW=logoImg.naturalWidth,srcH=logoImg.naturalHeight;
var maxSide=1024;
var scale=1.0;
if(srcW>maxSide||srcH>maxSide){scale=maxSide/Math.max(srcW,srcH);}
var w=Math.max(2,Math.round(srcW*scale));
var h=Math.max(2,Math.round(srcH*scale));
var cv=document.createElement('canvas');
cv.width=w;cv.height=h;
var c2=cv.getContext('2d');
c2.clearRect(0,0,w,h);
c2.drawImage(logoImg,0,0,w,h);
var img=c2.getImageData(0,0,w,h);
var d=img.data;
for(var i=0;i<d.length;i+=4){
var a=d[i+3];
if(a===0)continue;
var r=d[i],g=d[i+1],b=d[i+2];
var mn=Math.min(r,g,b);
var mx=Math.max(r,g,b);
// Remove pure/near-white background while preserving colored logo strokes.
if(mn>=248){
d[i+3]=0;
}else if(mn>=232&&(mx-mn)<=18){
var keep=(248-mn)/16;
if(keep<0)keep=0;
if(keep>1)keep=1;
d[i+3]=Math.round(a*keep);
}
}
c2.putImageData(img,0,0);
var tex=new THREE.CanvasTexture(cv);
tex.needsUpdate=true;
tex.minFilter=THREE.LinearFilter;
tex.magFilter=THREE.LinearFilter;
tex.premultiplyAlpha=true;
return tex;
}catch(e){return null;}
}

function createGifWatermarkSprite(){
if(!sc||!ca||!logoImg||!logoImg.complete||logoImg.naturalWidth<=0)return null;
try{
var tex=buildGifWatermarkTextureFromLogo();
if(!tex){
tex=new THREE.Texture(logoImg);
tex.needsUpdate=true;
tex.minFilter=THREE.LinearFilter;
tex.magFilter=THREE.LinearFilter;
}
var mat=new THREE.SpriteMaterial({map:tex,transparent:true,alphaTest:0.02,opacity:0.12,depthTest:true,depthWrite:false});
var spr=new THREE.Sprite(mat);
spr.renderOrder=-5;
updateGifWatermarkSprite(spr);
sc.add(spr);
return spr;
}catch(e){return null;}
}

function updateGifWatermarkSprite(spr,scaleMul){
if(!spr||!ca)return;
var sm=(scaleMul===undefined||scaleMul===null)?1.0:Number(scaleMul);
if(!isFinite(sm)||sm<=0)sm=1.0;
var dir=new THREE.Vector3();
ca.getWorldDirection(dir);
// Keep watermark behind the model and place it at bottom-right of mesh view area.
var distBehind=Math.max(B*0.10,camDist*0.08);
var basePos=tg.clone().add(dir.multiplyScalar(distBehind));
var viewH;
var viewW;
if(ca.isOrthographicCamera){
viewH=Math.abs(ca.top-ca.bottom)/Math.max(1e-6,(ca.zoom||1));
viewW=Math.abs(ca.right-ca.left)/Math.max(1e-6,(ca.zoom||1));
}else{
var fov=((ca.fov!==undefined?ca.fov:45)*Math.PI)/180.0;
var depth=Math.max(B*0.01,camDist+distBehind);
viewH=2.0*Math.tan(fov*0.5)*depth;
var asp=(ca.aspect!==undefined&&isFinite(ca.aspect)&&ca.aspect>0)?ca.aspect:1.0;
viewW=viewH*asp;
}
var hRaw=viewH*0.22;
// 60% smaller than previous size (keep 40%).
var h=Math.max(B*0.064,Math.min(B*0.208,hRaw*0.40));
h=h*sm;
var ar=(logoImg&&logoImg.naturalHeight>0)?(logoImg.naturalWidth/logoImg.naturalHeight):2.8;
spr.scale.set(h*ar,h,1);
var marginX=viewW*0.03;
var marginY=viewH*0.04;
var xOff=Math.max(0,viewW*0.5-spr.scale.x*0.5-marginX);
var yOff=Math.max(0,viewH*0.5-spr.scale.y*0.5-marginY);
var right=new THREE.Vector3(1,0,0).applyQuaternion(ca.quaternion);
var up=new THREE.Vector3(0,1,0).applyQuaternion(ca.quaternion);
spr.position.copy(basePos);
spr.position.add(right.multiplyScalar(xOff));
spr.position.add(up.multiplyScalar(-yOff));
}

function disposeGifWatermarkSprite(spr){
if(!spr||!sc)return;
try{sc.remove(spr);}catch(e){}
try{
if(spr.material){
if(spr.material.map)spr.material.map.dispose();
spr.material.dispose();
}
}catch(e){}
}

function drawXYTitleBar(ctx,x,y,w,text){
var pxScale=1;
if(re&&re.domElement&&re.domElement.clientWidth){pxScale=re.domElement.width/re.domElement.clientWidth;}
var h=18*pxScale;
var ty=Math.max(0,y-h-4*pxScale);
ctx.save();
ctx.fillStyle='#2196F3';
ctx.fillRect(x,ty,w,h);
ctx.fillStyle='#fff';
ctx.font='bold '+Math.round(12*pxScale)+'px Arial';
ctx.textAlign='center';
ctx.textBaseline='middle';
ctx.fillText(text,x+w/2,ty+h/2);
ctx.restore();
}

function getXYExportLegendItems(){
var out=[];
if(!xyCurves||xyCurves.length===0)return out;
for(var i=0;i<xyCurves.length;i++){
var c=xyCurves[i]||{};
if(!xyIsCurveVisible(c))continue;
var nm=(c.name&&String(c.name).trim().length>0)?String(c.name):('Curve '+(i+1));
if(c.axis==='secondary')nm+=' (R)';
var col=(c.color&&String(c.color).trim().length>0)?String(c.color):CURVE_COLORS[i%CURVE_COLORS.length];
out.push({name:nm,color:col});
}
return out;
}

function xyGetLegendMetrics(){
var font=Math.max(8,Math.min(24,xyTitleFontSize||10));
var dot=Math.max(8,Math.round(font*0.8));
return{
font:font,
dot:dot,
gap:Math.max(4,Math.round(font*0.6)),
itemGap:Math.max(3,Math.round(font*0.35)),
border:Math.max(1,Math.round(dot*0.22)),
pad:Math.max(6,Math.round(font*0.6)),
lineH:Math.max(14,Math.round(font*1.35)),
titleFont:Math.max(9,Math.round(font*0.95)),
tailPad:Math.max(10,Math.round(font*1.2))
};
}

function measureXYExportLegendHeight(ctx,w){
var items=getXYExportLegendItems();
if(items.length===0||w<80)return 0;
var lm=xyGetLegendMetrics();
ctx.save();
ctx.font=lm.font+'px Arial';
var pad=lm.pad;
var lineH=lm.lineH;
var x=pad;
var rows=1;
for(var i=0;i<items.length;i++){
var label=items[i].name;
var iw=Math.ceil(lm.dot+lm.itemGap+ctx.measureText(label).width+lm.tailPad);
if(x+iw>w-pad){rows++;x=pad;}
x+=iw+lm.gap;
}
ctx.restore();
var titleH=Math.max(lineH,Math.round(lm.titleFont+6));
var h=pad+titleH+rows*lineH+pad;
if(h<24)h=24;
return h;
}

function drawXYExportLegend(ctx,x,y,w,h){
if(h<=4||w<=40)return;
var items=getXYExportLegendItems();
var lm=xyGetLegendMetrics();
ctx.save();
ctx.fillStyle='#fff';
ctx.fillRect(x,y,w,h);
ctx.strokeStyle='rgba(0,0,0,0.18)';
ctx.lineWidth=1;
ctx.beginPath();
ctx.moveTo(x+1,y+0.5);
ctx.lineTo(x+w-1,y+0.5);
ctx.stroke();
if(items.length===0){ctx.restore();return;}
var pad=lm.pad;
var titleH=Math.max(lm.lineH,Math.round(lm.titleFont+6));
var titleY=y+pad+Math.round(titleH*0.5);
ctx.fillStyle='#444';
ctx.font='bold '+lm.titleFont+'px Arial';
ctx.textAlign='left';
ctx.textBaseline='middle';
ctx.fillText('Curves:',x+pad,titleY);
ctx.font=lm.font+'px Arial';
var lineH=lm.lineH;
var cx=x+pad;
var cy=y+pad+titleH+Math.round(lineH*0.5);
var bottom=y+h-4;
for(var i=0;i<items.length;i++){
var it=items[i];
var txt=it.name;
var iw=Math.ceil(lm.dot+lm.itemGap+ctx.measureText(txt).width+lm.tailPad);
if(cx+iw>x+w-pad){cx=x+pad;cy+=lineH;}
if(cy>bottom)break;
var r=Math.max(3,lm.dot*0.5);
ctx.beginPath();
ctx.arc(cx+r,cy,r,0,Math.PI*2);
ctx.fillStyle='#fff';
ctx.fill();
ctx.strokeStyle=it.color;
ctx.lineWidth=lm.border;
ctx.stroke();
ctx.fillStyle='#222';
ctx.fillText(txt,cx+lm.dot+lm.itemGap,cy);
cx+=iw+lm.gap;
}
ctx.restore();
}

function exportGIF(saveHandle){
if(saveHandle===undefined&&window.showSaveFilePicker&&window.isSecureContext!==false){
try{
window.showSaveFilePicker({suggestedName:HTMLNAME+'.gif',types:[{description:'GIF Image',accept:{'image/gif':['.gif']}}]}).then(function(handle){
exportGIF(handle);
}).catch(function(err){
if(err&&err.name==='AbortError')return;
exportGIF(null);
});
return;
}catch(e){}
}
var useHarmonic=(VIEWER_MODE==='harmonic')||!!animHarmonic;
if(!useHarmonic&&SL.length<2){alert('Need at least 2 increments');return;}
if(!gifWorkerUrl){
document.getElementById('anim-status').textContent='GIF encoder not ready - retrying...';
try{
fetch('https://cdnjs.cloudflare.com/ajax/libs/gif.js/0.2.0/gif.worker.js')
.then(function(r){return r.text();})
.then(function(txt){
gifWorkerUrl=URL.createObjectURL(new Blob([txt],{type:'application/javascript'}));
exportGIF(saveHandle);
}).catch(function(e){
document.getElementById('anim-status').textContent='Error: Cannot load GIF encoder. Check internet.';
});
}catch(e){document.getElementById('anim-status').textContent='Error: '+e.message;}
return;
}
var si=0,ei=0;
var harmonicIncLabel='';
if(useHarmonic){
var harmonicSid=getHarmonicBaseStateId();
if(!harmonicSid){alert('Select one increment before exporting Harmonic GIF');return;}
var hsd=AD[harmonicSid]||getStateData(currentVar,harmonicSid);
if(!hsd){alert('Selected harmonic increment data is unavailable');return;}
harmonicBaseStateId=harmonicSid;
document.getElementById('ss').value=harmonicSid;
if(cst!==harmonicSid){osc();}else{asc();}
si=0;
ei=Math.max(1,harmonicFrameCount)-1;
harmonicIncLabel=(hsd.increment!==undefined&&hsd.increment!==null)?String(hsd.increment):String(harmonicSid);
}else{
const startIdx=parseInt(document.getElementById('gif-start').value);
const endIdx=parseInt(document.getElementById('gif-end').value);
si=Math.min(startIdx,endIdx);
ei=Math.max(startIdx,endIdx);
if(ei<=si){alert('Select a valid increment range (start must differ from end)');return;}
}
var swingBtnEl=document.getElementById('anim-harmonic-btn');
var swingBtnOn=!!(swingBtnEl&&String(swingBtnEl.textContent||'').trim().toLowerCase()==='on');
var staticSwingGif=(!useHarmonic)&&(!!animSwing||swingBtnOn);
var staticFrameSeq=null;
if(staticSwingGif){
staticFrameSeq=[];
for(var sfi=si;sfi<=ei;sfi++)staticFrameSeq.push(sfi);
for(var sbi=ei-1;sbi>=si;sbi--)staticFrameSeq.push(sbi);
}
var totalCaptureFrames=useHarmonic?(ei-si+1):(staticSwingGif?staticFrameSeq.length:(ei-si+1));
stopAnimation();
var gifRotationCutState=hideRotationCutVisualsForCapture();
const speed=parseInt(document.getElementById('anim-speed').value);
const frameDelay=Math.max(80,600/speed);
var prevXYAnim=xyAnimIndex;
var gifSaveHandle=saveHandle||null;
var scaleEl=document.getElementById('gif-scale');
var requestedScale=parseInt(scaleEl?scaleEl.value:'1',10);
if(!isFinite(requestedScale)||requestedScale<1)requestedScale=1;
if(requestedScale>4)requestedScale=4;
var baseCW=re.domElement.width,baseCH=re.domElement.height;
var baseCssW=re.domElement.clientWidth||Math.max(1,Math.round(baseCW/(window.devicePixelRatio||1)));
var baseCssH=re.domElement.clientHeight||Math.max(1,Math.round(baseCH/(window.devicePixelRatio||1)));
var basePixelRatio=baseCssW>0?(baseCW/baseCssW):(window.devicePixelRatio||1);
var xyCV=xyPlotVisible?document.getElementById('xy-plot-canvas'):null;
var xyBaseW=xyCV?xyCV.width:0;
var totalBaseW=baseCW+xyBaseW;
var maxGifSide=4096;
var maxGifPixels=16000000;
var maxScaleBySide=Math.min(maxGifSide/Math.max(1,totalBaseW),maxGifSide/Math.max(1,baseCH));
var maxScaleByPixels=Math.sqrt(maxGifPixels/Math.max(1,totalBaseW*baseCH));
if(maxScaleBySide<1||maxScaleByPixels<1){
alert('Current viewport is too large for GIF export. Reduce window size or disable XY panel.');
return;
}
var safeScale=Math.max(1,Math.floor(Math.min(4,maxScaleBySide,maxScaleByPixels)));
var gifScale=Math.min(requestedScale,safeScale);
if(!isFinite(gifScale)||gifScale<1)gifScale=1;
if(gifScale<requestedScale){
document.getElementById('anim-status').textContent='GIF scale limited to '+gifScale+'x (memory safety)';
}else{
if(useHarmonic){
document.getElementById('anim-status').textContent='Capturing harmonic cycle for Inc '+harmonicIncLabel+' ('+totalCaptureFrames+' frames) at '+gifScale+'x...';
}else{
if(staticSwingGif){
document.getElementById('anim-status').textContent='Capturing swing frames '+(si+1)+' <-> '+(ei+1)+' ('+totalCaptureFrames+' frames) at '+gifScale+'x...';
}else{
document.getElementById('anim-status').textContent='Capturing frames '+(si+1)+' to '+(ei+1)+' at '+gifScale+'x...';
}
}
}
var xyState=null;
var restoredExportView=false;
function restoreExportView(){
if(restoredExportView)return;
restoredExportView=true;
restoreRotationCutVisualsAfterCapture(gifRotationCutState);
try{
re.setPixelRatio(basePixelRatio);
re.setSize(baseCssW,baseCssH,false);
}catch(e){}
if(xyCV&&xyState){
try{
xyCV.width=xyState.width;
xyCV.height=xyState.height;
xyCV._dpr=xyState.dpr;
if(xyState.cssW!==undefined)xyCV._cssW=xyState.cssW;else delete xyCV._cssW;
if(xyState.cssH!==undefined)xyCV._cssH=xyState.cssH;else delete xyCV._cssH;
if(xyState.styleW!==undefined)xyCV.style.width=xyState.styleW;
if(xyState.styleH!==undefined)xyCV.style.height=xyState.styleH;
}catch(e){}
}
if(gifWatermarkSprite){
disposeGifWatermarkSprite(gifWatermarkSprite);
gifWatermarkSprite=null;
}
if(useHarmonic&&harmonicBaseStateId)restoreHarmonicBaseState();
xyAnimIndex=prevXYAnim;
if(xyPlotVisible)drawPlot();
renderFrame();
}
try{
re.setPixelRatio(basePixelRatio*gifScale);
re.setSize(baseCssW,baseCssH,false);
}catch(e){
restoreExportView();
alert('GIF export failed: '+e.message);
return;
}
var cW=re.domElement.width,cH=re.domElement.height;
if(cW<2||cH<2){
restoreExportView();
alert('GIF export failed: invalid canvas size '+cW+'x'+cH);
return;
}
var xyW=0;
var xyH=0;
if(xyCV){
xyState={width:xyCV.width,height:xyCV.height,dpr:(xyCV._dpr||1),cssW:xyCV._cssW,cssH:xyCV._cssH,styleW:xyCV.style.width,styleH:xyCV.style.height};
var xyCssW=(xyState.cssW!==undefined)?xyState.cssW:(xyCV.clientWidth||Math.max(1,Math.round(xyState.width/Math.max(1e-6,xyState.dpr))));
var xyCssH=(xyState.cssH!==undefined)?xyState.cssH:(xyCV.clientHeight||Math.max(1,Math.round(xyState.height/Math.max(1e-6,xyState.dpr))));
xyCV._cssW=Math.floor(xyCssW);
xyCV._cssH=Math.floor(xyCssH);
xyCV._dpr=xyState.dpr*gifScale;
xyCV.width=Math.max(2,Math.floor(xyCV._cssW*xyCV._dpr));
xyCV.height=Math.max(2,Math.floor(xyCV._cssH*xyCV._dpr));
xyCV.style.width=xyCV._cssW+'px';
xyCV.style.height=xyCV._cssH+'px';
drawPlot();
xyW=xyCV.width;
xyH=xyCV.height;
}
var totalW=xyCV?cW+xyW:cW;
var compCanvas=document.createElement('canvas');compCanvas.width=totalW;compCanvas.height=cH;
var compCtx=compCanvas.getContext('2d');
compCtx.imageSmoothingEnabled=true;compCtx.imageSmoothingQuality='high';
// Use global palette to reduce per-frame color shifts in GIF output.
var gif=new GIF({workers:2,quality:1,workerScript:gifWorkerUrl,width:totalW,height:cH,globalPalette:true,dither:false,repeat:0});
var gifSavedDynamic=dynamicLegend;
var gifStaticMin=curMin,gifStaticMax=curMax;
var gifLegendFixedColors=[];
for(var gi=0;gi<N_DISC;gi++){gifLegendFixedColors.push(getLegendBandHex(gi));}
var gifLegendFixedValues=gifSavedDynamic?null:(hasCustomLegend()?legendCustomValues.slice():buildLinearLegendValues(gifStaticMin,gifStaticMax));
var gifWatermarkSprite=createGifWatermarkSprite();
var capIndex=0;
function drawLegend(ctx,w,h){
ctx.save();
// Legend dimensions - position above axes HUD area
var lW=100,lH=Math.round(h*0.55),lX=15;
var maxBottom=h-AX_SIZE-AX_YOFF-10;
var lY=Math.max(15,Math.round((maxBottom-lH)/2));
if(lY+lH>maxBottom)lH=maxBottom-lY;
var gW=16,pad=10;
var legMin=gifSavedDynamic?curMin:gifStaticMin;
var legMax=gifSavedDynamic?curMax:gifStaticMax;
// Background
ctx.fillStyle='rgba(255,255,255,0.92)';
ctx.strokeStyle='#2196F3';ctx.lineWidth=2;
roundRect(ctx,lX,lY,lW,lH,6);
// Title
ctx.fillStyle='#2196F3';ctx.font='bold 11px Arial';ctx.textAlign='center';
ctx.fillText(currentVar,lX+lW/2,lY+16);
// Gradient bar
var gX=lX+lW-gW-pad,gY=lY+28,gH=lH-42;
if(discreteMode){
for(var b=0;b<N_DISC;b++){
var bY=gY+b*(gH/N_DISC);
var bH=gH/N_DISC;
ctx.fillStyle=(b<gifLegendFixedColors.length)?gifLegendFixedColors[b]:getLegendBandHex(b);
ctx.fillRect(gX,bY,gW,bH);
if(b<N_DISC-1){ctx.strokeStyle='rgba(0,0,0,0.55)';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(gX,bY+bH);ctx.lineTo(gX+gW,bY+bH);ctx.stroke();}
}
}else{
var grad=ctx.createLinearGradient(0,gY,0,gY+gH);
if(hasCustomLegend()){
for(var ci=0;ci<N_DISC;ci++){
var p1=ci/N_DISC;
var p2=(ci+1)/N_DISC;
var ch=(ci<gifLegendFixedColors.length)?gifLegendFixedColors[ci]:getLegendBandHex(ci);
grad.addColorStop(p1,ch);
grad.addColorStop(p2,ch);
}
}else{
var st=28;
for(var si=0;si<=st;si++){
var pp=si/st;
grad.addColorStop(pp,getBaseLegendHex(1-pp));
}
}
ctx.fillStyle=grad;ctx.fillRect(gX,gY,gW,gH);
}
ctx.strokeStyle='#999';ctx.lineWidth=1;ctx.strokeRect(gX,gY,gW,gH);
// Values
ctx.fillStyle='#333';ctx.font='600 '+legFontSize+'px Arial';ctx.textAlign='right';
var vals;
if(!gifSavedDynamic&&gifLegendFixedValues&&gifLegendFixedValues.length===N_DISC+1){
vals=gifLegendFixedValues.slice();
}else{
vals=hasCustomLegend()?legendCustomValues.slice():buildLinearLegendValues(legMin,legMax);
}
for(var i=0;i<=N_DISC;i++){
var yy=gY+i*(gH/N_DISC);
ctx.fillText(formatLegendNumber(vals[i]),gX-4,yy+3);
}
ctx.restore();
}

function saveBlobWithPicker(blob,fname){
if(window.showSaveFilePicker&&window.isSecureContext!==false){
try{
window.showSaveFilePicker({suggestedName:fname,types:[{description:'Image',accept:{'image/png':['.png'],'image/gif':['.gif']}}]}).then(function(handle){
return handle.createWritable().then(function(writable){
return writable.write(blob).then(function(){return writable.close();});
});
}).catch(function(err){
if(err&&err.name==='AbortError')return;
fallbackDownload(blob,fname);
});
return;
}catch(e){}
}
fallbackDownload(blob,fname);
}

function fallbackDownload(blob,fname){
var a=document.createElement('a');
a.href=URL.createObjectURL(blob);
a.download=fname;
document.body.appendChild(a);a.click();document.body.removeChild(a);
setTimeout(function(){URL.revokeObjectURL(a.href);},1000);
}

function saveCanvasPNG(canvas,fname){
try{
if(canvas.width<2||canvas.height<2){alert('Screenshot failed: empty canvas');return;}
if(canvas.toBlob){
canvas.toBlob(function(blob){
if(!blob||blob.size===0){alert('Screenshot failed: empty image');return;}
fallbackDownload(blob,fname);
},'image/png');
}else{
fallbackDownload(dataURLToBlob(canvas.toDataURL('image/png')),fname);
}
}catch(err){
alert('Screenshot failed: '+err.message);
}
}

function dataURLToBlob(dataURL){
var parts=dataURL.split(',');
var mime=parts[0].match(/:(.*?);/)[1];
var bstr=atob(parts[1]);var n=bstr.length;var u8arr=new Uint8Array(n);
while(n--){u8arr[n]=bstr.charCodeAt(n);}
return new Blob([u8arr],{type:mime});
}
function writeBlobToHandle(blob,handle,fname){
if(!blob||blob.size===0){alert('Screenshot failed: empty image');return;}
if(handle&&handle.createWritable){
handle.createWritable().then(function(writable){
return writable.write(blob).then(function(){return writable.close();});
}).catch(function(){
try{
handle.createWritable().then(function(writable2){
return writable2.write({type:'write',position:0,data:blob}).then(function(){return writable2.close();});
}).catch(function(){fallbackDownload(blob,fname);});
}catch(e){fallbackDownload(blob,fname);}
});
}else{
fallbackDownload(blob,fname);
}
}
function writePngWithHandle(canvas,handle,fname){
try{
if(canvas.width<2||canvas.height<2){alert('Screenshot failed: empty canvas');return;}
if(canvas.toBlob){
canvas.toBlob(function(blob){
if(!blob||blob.size===0){alert('Screenshot failed: empty image');return;}
writeBlobToHandle(blob,handle,fname);
},'image/png');
}else{
var dataURL=canvas.toDataURL('image/png');
if(!dataURL||dataURL.length<100){alert('Screenshot failed: invalid image');return;}
var blob=dataURLToBlob(dataURL);
writeBlobToHandle(blob,handle,fname);
}
}catch(e){
alert('Screenshot failed: '+e.message);
}
}
function cap(){
if(capIndex<totalCaptureFrames){
if(useHarmonic){
var denom=Math.max(1,totalCaptureFrames);
var phase=(Math.PI*2*capIndex)/denom;
if(!applyHarmonicFrame(phase)){
restoreExportView();
document.getElementById('anim-status').textContent='GIF export error: harmonic frame failed';
return;
}
xyAnimIndex=-1;
if(xyPlotVisible&&capIndex===0)drawPlot();
document.getElementById('anim-status').textContent='Harmonic frame '+(capIndex+1)+'/'+totalCaptureFrames+'...';
}else{
var stateIdx=staticSwingGif?staticFrameSeq[capIndex]:(si+capIndex);
var state=SL[stateIdx];
document.getElementById('ss').value=state.id;osc();
xyAnimIndex=stateIdx;
if(xyPlotVisible)drawPlot();
document.getElementById('anim-status').textContent='Frame '+(capIndex+1)+'/'+totalCaptureFrames+'...';
}
setTimeout(function(){try{
if(gifWatermarkSprite)updateGifWatermarkSprite(gifWatermarkSprite);
renderFrameWhite();
compCtx.clearRect(0,0,totalW,cH);
compCtx.fillStyle='#fff';compCtx.fillRect(0,0,totalW,cH);
compCtx.drawImage(re.domElement,0,0);
drawLegend(compCtx,cW,cH);
drawMeasOnCanvas(compCtx,cW,cH);
drawPinnedOnCanvas(compCtx,cW,cH);
drawPinnedElemsOnCanvas(compCtx,cW,cH);
drawDialogBoxesOnCanvas(compCtx,cW,cH);
drawTableFormOnCanvas(compCtx,cW,cH);
drawTableFormLinksOnCanvas(compCtx,cW,cH);
if(xyCV){
compCtx.save();
compCtx.strokeStyle='#2196F3';compCtx.lineWidth=2;
compCtx.beginPath();compCtx.moveTo(cW+0.5,0);compCtx.lineTo(cW+0.5,cH);compCtx.stroke();
compCtx.restore();
var xyLegendH=Math.min(Math.round(cH*0.38),measureXYExportLegendHeight(compCtx,xyW));
var maxPlotH=Math.max(20,cH-xyLegendH);
var xyDrawH=Math.min(xyH,maxPlotH);
var stackH=xyDrawH+xyLegendH;
var xyY=Math.max(0,Math.round((cH-stackH)/2));
var legendY=xyY+xyDrawH;
compCtx.fillStyle='#fff';compCtx.fillRect(cW,0,xyW,cH);
var ttl=document.getElementById('xy-plot-title');
var ttxt=ttl?(ttl.value||'XY Plot'):'XY Plot';
drawXYTitleBar(compCtx,cW,xyY,xyW,ttxt);
compCtx.drawImage(xyCV,0,0,xyCV.width,xyCV.height,cW,xyY,xyW,xyDrawH);
drawXYExportLegend(compCtx,cW,legendY,xyW,xyLegendH);
}
gif.addFrame(compCanvas,{delay:frameDelay,copy:true});
capIndex++;cap();
}catch(err){
restoreExportView();
document.getElementById('anim-status').textContent='GIF export error: '+err.message;
}},250);
}else{
document.getElementById('anim-status').textContent='Encoding GIF...';
gif.on('finished',function(blob){
if(gifSaveHandle&&gifSaveHandle.createWritable){
gifSaveHandle.createWritable().then(function(writable){
return writable.write(blob).then(function(){return writable.close();});
}).then(function(){
document.getElementById('anim-status').textContent='GIF saved! ('+Math.round(blob.size/1024)+' KB)';
}).catch(function(){
fallbackDownload(blob,HTMLNAME+'.gif');
document.getElementById('anim-status').textContent='GIF saved! ('+Math.round(blob.size/1024)+' KB)';
});
}else{
fallbackDownload(blob,HTMLNAME+'.gif');
document.getElementById('anim-status').textContent='GIF saved! ('+Math.round(blob.size/1024)+' KB)';
}
});
restoreExportView();
try{gif.render();}catch(err){document.getElementById('anim-status').textContent='GIF export error: '+err.message;}}
}
cap();
}

function rsc(){setScaleFactorToUI(DEFAULT_SCALE_FACTOR);asc();}
function syncAllEdgesOptionAvailability(){
var edSel=document.getElementById('ed');
if(!edSel)return;
var allOpt=edSel.querySelector('option[value="all"]');
if(!allOpt)return;
allOpt.disabled=!ALL_EDGES_EXPORTED;
allOpt.title=ALL_EDGES_EXPORTED?'':'Disabled in this HTML export. Enable it in Tkinter before generating.';
if(!ALL_EDGES_EXPORTED&&edSel.value==='all'){
edSel.value='feature';
}
if(!ALL_EDGES_EXPORTED&&edgeMode==='all'){
edgeMode='feature';
}
}
function tgeMode(mode){
if(mode!=='all'&&mode!=='feature'&&mode!=='none')mode='none';
if(mode==='all'&&!ALL_EDGES_EXPORTED){
mode='feature';
var edSelLock=document.getElementById('ed');
if(edSelLock)edSelLock.value='feature';
document.getElementById('st').textContent='All Edges is disabled in this HTML export.';
}
edgeMode=mode;
var drawColors=null;
if(cst&&AD[cst]){
if((centroidMode||isElementLocalContourMode())&&centroidRawColors){drawColors=rawColors;}
else{drawColors=getMeshDrawColors();}
}
var needsRebuild=(edgeMode==='all'&&!eg)||(edgeMode==='feature'&&!featureEg);
if(needsRebuild){
cm(getRenderNodes(),drawColors,{forceRebuild:true});
}
if(edgeMode==='all'&&!eg){
edgeMode='feature';
if(!featureEg){
cm(getRenderNodes(),drawColors,{forceRebuild:true});
}
if(!featureEg){
edgeMode='none';
}
var edSelFallback=document.getElementById('ed');
if(edSelFallback)edSelFallback.value=edgeMode;
var fallbackMsg;
if(ALL_EDGES_EXPORTED){
fallbackMsg=(edgeMode==='feature')?'All Edges build failed (browser/GPU memory limit). Switched to Feature Edges.':'All Edges/Feature Edges unavailable. Switched to No Edges.';
}else{
fallbackMsg=(edgeMode==='feature')?'All Edges unavailable for this mesh size. Switched to Feature Edges.':'All/Feature Edges unavailable for this mesh size. Switched to No Edges.';
}
document.getElementById('st').textContent=fallbackMsg;
return;
}
if(eg)eg.visible=(edgeMode==='all');
if(featureEg)featureEg.visible=(edgeMode==='feature');
var edSel=document.getElementById('ed');
if(edSel)edSel.value=edgeMode;
document.getElementById('st').textContent='Edge mode: '+edgeMode;
}
function tgw(s){if(ms)ms.material.wireframe=s;}
function tgr(s){ir=s;}
function rv(){
tg=new THREE.Vector3(CT[0],CT[1],CT[2]);camDist=B*3;
const t=Math.PI/4,p=Math.PI/4;
const x=camDist*Math.sin(p)*Math.cos(t),y=camDist*Math.cos(p),z=camDist*Math.sin(p)*Math.sin(t);
const m=new THREE.Matrix4();m.lookAt(new THREE.Vector3(x,y,z),new THREE.Vector3(0,0,0),new THREE.Vector3(0,1,0));
camQuat.setFromRotationMatrix(m);uc();
}

function setView(view){
tg=new THREE.Vector3(CT[0],CT[1],CT[2]);camDist=B*3;
let eye;
if(view==='front') eye=new THREE.Vector3(0,0,camDist);
else if(view==='top') eye=new THREE.Vector3(0,camDist,0.001);
else if(view==='side') eye=new THREE.Vector3(camDist,0,0);
else eye=new THREE.Vector3(camDist*0.577,camDist*0.577,camDist*0.577);
const m=new THREE.Matrix4();m.lookAt(eye,new THREE.Vector3(0,0,0),new THREE.Vector3(0,1,0));
camQuat.setFromRotationMatrix(m);uc();
document.getElementById('st').textContent=view.charAt(0).toUpperCase()+view.slice(1)+' view';
}

function zoomIn(){camDist=Math.max(B*0.1,camDist*0.8);uc();}
function zoomOut(){camDist=Math.min(B*80,camDist*1.25);uc();}
function fillView(){rv();}

function toggleZoomBox(){
zoomBoxMode=!zoomBoxMode;
if(zoomBoxMode&&hideElemMode){
var hcb=document.getElementById('hide-elem-on');
if(hcb)hcb.checked=false;
tgHideElements(false);
}
var btn=document.getElementById('zoom-box-btn');
if(zoomBoxMode){
btn.style.background='#2196F3';btn.style.color='white';
updateViewerCursorForModes();
document.getElementById('st').textContent='Zoom Box: drag a rectangle on the 3D view';
}else{
btn.style.background='';btn.style.color='';
updateViewerCursorForModes();
if(zoomBoxDiv){zoomBoxDiv.style.display='none';}
document.getElementById('st').textContent='Zoom Box cancelled';
}
}

function initZoomBoxOverlay(){
zoomBoxDiv=document.createElement('div');
zoomBoxDiv.id='zoom-box-rect';
zoomBoxDiv.style.cssText='position:absolute;display:none;border:2px dashed #2196F3;background:rgba(33,150,243,0.15);pointer-events:none;z-index:150';
document.getElementById('c').appendChild(zoomBoxDiv);
}

// Rotate CW/CCW - roll around the current screen normal
function getScreenNormalAxis(){
const axis=new THREE.Vector3(0,0,1).applyQuaternion(camQuat);
if(axis.lengthSq()<1e-12)return new THREE.Vector3(0,0,1);
return axis.normalize();
}
function rotCW(){
const q=new THREE.Quaternion().setFromAxisAngle(getScreenNormalAxis(),Math.PI/12);
camQuat.premultiply(q);camQuat.normalize();uc();
}
function rotCCW(){
const q=new THREE.Quaternion().setFromAxisAngle(getScreenNormalAxis(),-Math.PI/12);
camQuat.premultiply(q);camQuat.normalize();uc();
}

function hideRotationCutVisualsForCapture(){
var state={
line:!!(rotationCutLine&&rotationCutLine.visible),
plane:!!(rotationCutPlaneMesh&&rotationCutPlaneMesh.visible),
edges:!!(rotationCutPlaneEdges&&rotationCutPlaneEdges.visible),
plane2:!!(rotationCutPlaneMesh2&&rotationCutPlaneMesh2.visible),
edges2:!!(rotationCutPlaneEdges2&&rotationCutPlaneEdges2.visible)
};
if(rotationCutLine)rotationCutLine.visible=false;
if(rotationCutPlaneMesh)rotationCutPlaneMesh.visible=false;
if(rotationCutPlaneEdges)rotationCutPlaneEdges.visible=false;
if(rotationCutPlaneMesh2)rotationCutPlaneMesh2.visible=false;
if(rotationCutPlaneEdges2)rotationCutPlaneEdges2.visible=false;
return state;
}

function restoreRotationCutVisualsAfterCapture(state){
if(!state)return;
if(rotationCutLine)rotationCutLine.visible=!!state.line;
if(rotationCutPlaneMesh)rotationCutPlaneMesh.visible=!!state.plane;
if(rotationCutPlaneEdges)rotationCutPlaneEdges.visible=!!state.edges;
if(rotationCutPlaneMesh2)rotationCutPlaneMesh2.visible=!!state.plane2;
if(rotationCutPlaneEdges2)rotationCutPlaneEdges2.visible=!!state.edges2;
}

function drawScreenshotLegend(ctx,w,h){
if(noContour)return;
ctx.save();
var lW=100,lH=Math.round(h*0.55),lX=15;
var maxBottom=h-AX_SIZE-AX_YOFF-10;
var lY=Math.max(15,Math.round((maxBottom-lH)/2));
if(lY+lH>maxBottom)lH=maxBottom-lY;
var gW=16,pad=10;
var legMin=curMin,legMax=curMax;
// Background
ctx.fillStyle='rgba(255,255,255,0.92)';
ctx.strokeStyle='#2196F3';ctx.lineWidth=2;
roundRectPath(ctx,lX,lY,lW,lH,6);
// Title
ctx.fillStyle='#2196F3';ctx.font='bold 11px Arial';ctx.textAlign='center';
ctx.fillText(currentVar,lX+lW/2,lY+16);
// Gradient bar
var gX=lX+lW-gW-pad,gY=lY+28,gH=lH-42;
if(discreteMode){
for(var b=0;b<N_DISC;b++){
var bY=gY+b*(gH/N_DISC);
var bH=gH/N_DISC;
ctx.fillStyle=getLegendBandHex(b);
ctx.fillRect(gX,bY,gW,bH);
if(b<N_DISC-1){ctx.strokeStyle='rgba(0,0,0,0.55)';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(gX,bY+bH);ctx.lineTo(gX+gW,bY+bH);ctx.stroke();}
}
}else{
var grad=ctx.createLinearGradient(0,gY,0,gY+gH);
if(hasCustomLegend()){
for(var ci=0;ci<N_DISC;ci++){
var p1=ci/N_DISC;
var p2=(ci+1)/N_DISC;
var ch=getLegendBandHex(ci);
grad.addColorStop(p1,ch);
grad.addColorStop(p2,ch);
}
}else{
var st=28;
for(var si=0;si<=st;si++){
var pp=si/st;
grad.addColorStop(pp,getBaseLegendHex(1-pp));
}
}
ctx.fillStyle=grad;ctx.fillRect(gX,gY,gW,gH);
}
ctx.strokeStyle='#999';ctx.lineWidth=1;ctx.strokeRect(gX,gY,gW,gH);
// Values
ctx.fillStyle='#333';ctx.font='600 '+legFontSize+'px Arial';ctx.textAlign='right';
var vals=hasCustomLegend()?legendCustomValues.slice():buildLinearLegendValues(legMin,legMax);
for(var i=0;i<=N_DISC;i++){
var yy=gY+i*(gH/N_DISC);
ctx.fillText(formatLegendNumber(vals[i]),gX-4,yy+3);
}
ctx.restore();
}
function scs(){
renderFrame();
if(xyPlotVisible){
var overlay=document.createElement('div');
overlay.style.cssText='position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.4);z-index:10000;display:flex;align-items:center;justify-content:center';
var box=document.createElement('div');
box.style.cssText='background:white;border-radius:8px;padding:20px 30px;box-shadow:0 4px 20px rgba(0,0,0,0.3);text-align:center;min-width:250px';
box.innerHTML='<div style="font-size:13px;font-weight:bold;color:#333;margin-bottom:15px">Include XY Plot in screenshot?</div>';
var btnYes=document.createElement('button');btnYes.textContent='Yes';
btnYes.style.cssText='font-size:13px;font-weight:bold;padding:8px 30px;margin:0 8px;border:2px solid #4CAF50;background:#4CAF50;color:white;border-radius:5px;cursor:pointer';
btnYes.onclick=function(){document.body.removeChild(overlay);scsCapture(true);};
var btnNo=document.createElement('button');btnNo.textContent='No';
btnNo.style.cssText='font-size:13px;font-weight:bold;padding:8px 30px;margin:0 8px;border:2px solid #2196F3;background:#2196F3;color:white;border-radius:5px;cursor:pointer';
btnNo.onclick=function(){document.body.removeChild(overlay);scsCapture(false);};
var btnC=document.createElement('button');btnC.textContent='Cancel';
btnC.style.cssText='font-size:11px;padding:5px 15px;margin-top:12px;border:1px solid #ccc;background:#f5f5f5;color:#666;border-radius:4px;cursor:pointer;display:block;margin-left:auto;margin-right:auto';
btnC.onclick=function(){document.body.removeChild(overlay);};
box.appendChild(btnYes);box.appendChild(btnNo);box.appendChild(document.createElement('br'));box.appendChild(btnC);
overlay.appendChild(box);document.body.appendChild(overlay);
}else{scsCapture(false);}
}
function scsCapture(includeXY){
var scsWatermarkSprite=null;
var scsRotationCutState=null;
try{
scsRotationCutState=hideRotationCutVisualsForCapture();
scsWatermarkSprite=createGifWatermarkSprite();
if(scsWatermarkSprite)updateGifWatermarkSprite(scsWatermarkSprite,0.6);
renderFrameWhite();
var cW=re.domElement.width,cH=re.domElement.height;
if(cW<2||cH<2){alert('Screenshot failed: canvas is '+cW+'x'+cH);return;}
var finalCanvas=document.createElement('canvas');
var finalCtx;
if(includeXY&&xyPlotVisible){
var xyCV=document.getElementById('xy-plot-canvas');
var xyW=xyCV?xyCV.width:0,xyH=xyCV?xyCV.height:0;
var totalW=cW+xyW;
finalCanvas.width=totalW;finalCanvas.height=cH;
finalCtx=finalCanvas.getContext('2d');
finalCtx.imageSmoothingEnabled=true;finalCtx.imageSmoothingQuality='high';
finalCtx.fillStyle='#fff';finalCtx.fillRect(0,0,totalW,cH);
finalCtx.drawImage(re.domElement,0,0);
drawScreenshotLegend(finalCtx,cW,cH);
drawMeasOnCanvas(finalCtx,cW,cH);
drawPinnedOnCanvas(finalCtx,cW,cH);
drawPinnedElemsOnCanvas(finalCtx,cW,cH);
drawDialogBoxesOnCanvas(finalCtx,cW,cH);
drawBrandingOverlay(finalCtx,cW,cH);
drawTableFormOnCanvas(finalCtx,cW,cH);
drawTableFormLinksOnCanvas(finalCtx,cW,cH);
if(xyCV){
finalCtx.save();
finalCtx.strokeStyle='#2196F3';finalCtx.lineWidth=2;
finalCtx.beginPath();finalCtx.moveTo(cW+0.5,0);finalCtx.lineTo(cW+0.5,cH);finalCtx.stroke();
finalCtx.restore();
var xyLegendH=Math.min(Math.round(cH*0.38),measureXYExportLegendHeight(finalCtx,xyW));
var maxPlotH=Math.max(20,cH-xyLegendH);
var xyDrawH=Math.min(xyH,maxPlotH);
var stackH=xyDrawH+xyLegendH;
var xyY=Math.max(0,Math.round((cH-stackH)/2));
var legendY=xyY+xyDrawH;
finalCtx.fillStyle='#fff';finalCtx.fillRect(cW,0,xyW,cH);
var ttl=document.getElementById('xy-plot-title');
var ttxt=ttl?(ttl.value||'XY Plot'):'XY Plot';
drawXYTitleBar(finalCtx,cW,xyY,xyW,ttxt);
finalCtx.drawImage(xyCV,0,0,xyCV.width,xyCV.height,cW,xyY,xyW,xyDrawH);
drawXYExportLegend(finalCtx,cW,legendY,xyW,xyLegendH);
}
}else{
finalCanvas.width=cW;finalCanvas.height=cH;
finalCtx=finalCanvas.getContext('2d');
finalCtx.imageSmoothingEnabled=true;finalCtx.imageSmoothingQuality='high';
finalCtx.fillStyle='#fff';finalCtx.fillRect(0,0,cW,cH);
finalCtx.drawImage(re.domElement,0,0);
drawScreenshotLegend(finalCtx,cW,cH);
drawMeasOnCanvas(finalCtx,cW,cH);
drawPinnedOnCanvas(finalCtx,cW,cH);
drawPinnedElemsOnCanvas(finalCtx,cW,cH);
drawDialogBoxesOnCanvas(finalCtx,cW,cH);
drawBrandingOverlay(finalCtx,cW,cH);
drawTableFormOnCanvas(finalCtx,cW,cH);
drawTableFormLinksOnCanvas(finalCtx,cW,cH);
}
var fname=HTMLNAME+'_screenshot.png';
var dataURL=finalCanvas.toDataURL('image/png');
if(!dataURL||dataURL==='data:,'||dataURL.length<100){alert('Screenshot failed: toDataURL returned empty');return;}
var byteString=atob(dataURL.split(',')[1]);
var ab=new ArrayBuffer(byteString.length);
var ia=new Uint8Array(ab);
for(var i=0;i<byteString.length;i++){ia[i]=byteString.charCodeAt(i);}
var blob=new Blob([ab],{type:'image/png'});
if(!blob||blob.size===0){alert('Screenshot failed: blob is empty');return;}
var url=URL.createObjectURL(blob);
var a=document.createElement('a');
a.href=url;
a.download=fname;
a.style.display='none';
document.body.appendChild(a);
a.click();
setTimeout(function(){document.body.removeChild(a);URL.revokeObjectURL(url);},3000);
}catch(ex){
alert('Screenshot error: '+ex.message);
}finally{
restoreRotationCutVisualsAfterCapture(scsRotationCutState);
if(scsWatermarkSprite)disposeGifWatermarkSprite(scsWatermarkSprite);
}
}
function renderFrame(){
const w=re.domElement.width,h=re.domElement.height;
re.setViewport(0,0,w,h);
re.setScissorTest(false);
re.clear();
re.render(sc,ca);
// Axes HUD overlay in bottom-left corner (raised by AX_YOFF)
if(showAxes&&axScene&&axCamera){
var fwd=new THREE.Vector3(0,0,1).applyQuaternion(camQuat);
axCamera.position.copy(fwd.multiplyScalar(3.5));
axCamera.up.set(0,1,0).applyQuaternion(camQuat);
axCamera.lookAt(0,0,0);
re.setScissorTest(true);
re.setViewport(0,AX_YOFF,AX_SIZE,AX_SIZE);
re.setScissor(0,AX_YOFF,AX_SIZE,AX_SIZE);
re.clear(false,true,false);
re.render(axScene,axCamera);
re.setScissorTest(false);
re.setViewport(0,0,w,h);
}
}

function renderFrameWhite(){
var prevBg=sc.background;
sc.background=new THREE.Color(0xffffff);
const w=re.domElement.width,h=re.domElement.height;
re.setViewport(0,0,w,h);
re.setScissorTest(false);
re.clear();
re.render(sc,ca);
if(showAxes&&axScene&&axCamera){
var fwd=new THREE.Vector3(0,0,1).applyQuaternion(camQuat);
axCamera.position.copy(fwd.multiplyScalar(3.5));
axCamera.up.set(0,1,0).applyQuaternion(camQuat);
axCamera.lookAt(0,0,0);
re.setScissorTest(true);
re.setViewport(0,AX_YOFF,AX_SIZE,AX_SIZE);
re.setScissor(0,AX_YOFF,AX_SIZE,AX_SIZE);
var prevClr=new THREE.Color();
re.getClearColor(prevClr);
var prevAlpha=re.getClearAlpha();
re.setClearColor(0xffffff,1);
re.clear(true,true,true);
re.render(axScene,axCamera);
re.setClearColor(prevClr,prevAlpha);
re.setScissorTest(false);
re.setViewport(0,0,w,h);
}
sc.background=prevBg;
}

function an(){requestAnimationFrame(an);
if(ir){const qY=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),0.005);camQuat.premultiply(qY);camQuat.normalize();uc();}
renderFrame();
updatePinnedPositions();
updateMeasureLabelPositions();
updateDialogBoxesVisuals();
}
// ==================== XY PLOT ====================
function tgxy(on){
xyPlotVisible=on;
var xp=document.getElementById('xy-panel');
var btn=document.getElementById('xy-toggle-btn');
if(on){xp.classList.add('visible');btn.textContent='On';btn.className='xy-toggle-btn on';}
else{xp.classList.remove('visible');btn.textContent='Off';btn.className='xy-toggle-btn off';xyToggleFontPopup(false);}
onResize();
if(on){
var secCurves=document.getElementById('xy-sec-curves');
var hdrCurves=document.getElementById('xy-hdr-curves');
if(xyCurves.length===0&&secCurves&&hdrCurves&&secCurves.style.display==='none'){
secCurves.style.display='block';
hdrCurves.textContent=hdrCurves.textContent.replace('[+]','[-]');
}
void xp.offsetHeight;xyResizePlot();requestAnimationFrame(function(){xyResizePlot();});
}
}

function xyResizePlot(){
var area=document.getElementById('xy-plot-area');
var cv=document.getElementById('xy-plot-canvas');
if(!area||!cv)return;
var r=area.getBoundingClientRect();
if(r.width<10||r.height<10)return;
var dpr=window.devicePixelRatio||1;
cv._dpr=dpr;
cv._cssW=Math.floor(r.width);
cv._cssH=Math.floor(r.height);
cv.width=Math.floor(r.width*dpr);
cv.height=Math.floor(r.height*dpr);
cv.style.width=cv._cssW+'px';
cv.style.height=cv._cssH+'px';
drawPlot();
if(!cv._xyTipSetup){
cv._xyTipSetup=true;
cv.addEventListener('mousemove',xyOnHover);
cv.addEventListener('mouseleave',function(){document.getElementById('xy-tooltip').style.display='none';});
cv.addEventListener('mousedown',xyZoomMouseDown);
cv.addEventListener('mousemove',xyZoomMouseMove);
cv.addEventListener('mouseup',xyZoomMouseUp);
cv.addEventListener('mouseleave',xyZoomCancel);
}
}

function xyUpdatePlotSize(){
if(!xyPlotVisible)return;
setTimeout(function(){xyResizePlot();},50);
}

function xyIsCurveHidden(c){
if(!c)return false;
return c.hidden===true||c.hidden===1||c.hidden==='1'||c.hidden==='true';
}

function xyIsCurveVisible(c){
return !!c&&!xyIsCurveHidden(c);
}

function xyRefreshHideButton(){
var btn=document.getElementById('xy-hide-btn');
if(!btn)return;
if(xyEditingIdx<0||xyEditingIdx>=xyCurves.length){
btn.disabled=true;
btn.textContent='Hide';
btn.title='Double-click a curve to edit and hide/show it';
return;
}
var c=xyCurves[xyEditingIdx];
var hidden=xyIsCurveHidden(c);
btn.disabled=false;
btn.textContent=hidden?'Show':'Hide';
btn.title=hidden?'Show this curve in XY Plot and legend':'Hide this curve from XY Plot and legend';
}

function xyToggleHideEditingCurve(){
if(xyEditingIdx<0||xyEditingIdx>=xyCurves.length)return;
var c=xyCurves[xyEditingIdx];
if(!c)return;
c.hidden=!xyIsCurveHidden(c);
xyRefreshHideButton();
xyRefreshList();
drawPlot();
var st=document.getElementById('st');
if(st){
var nm=(c.name&&String(c.name).trim().length>0)?String(c.name):('Curve '+(xyEditingIdx+1));
st.textContent='Curve "'+nm+'" '+(c.hidden?'hidden':'shown')+' in XY Plot';
}
}

function xyHasAnimHighlightCurves(){
if(!xyCurves||xyCurves.length===0||SL.length===0)return false;
for(var i=0;i<xyCurves.length;i++){
var c=xyCurves[i];
if(c&&xyIsCurveVisible(c)&&c.data&&c.data.length===SL.length)return true;
}
return false;
}

function xyRefreshAnimInfoButton(){
var btn=document.getElementById('xy-anim-info-btn');
if(!btn)return;
var eligible=xyHasAnimHighlightCurves();
if(!eligible){
btn.style.display='none';
return;
}
btn.style.display='inline-block';
if(xyAnimInfoVisible){
btn.textContent='Hide Info.';
btn.style.background='#D32F2F';
btn.style.borderColor='#B71C1C';
btn.style.color='#fff';
}else{
btn.textContent='Show Info.';
btn.style.background='#2E7D32';
btn.style.borderColor='#1B5E20';
btn.style.color='#fff';
}
}

function xyApplyPanelTitleFont(){
var t=document.getElementById('xy-plot-title');
var hdr=document.getElementById('xy-panel-header');
var fsBtn=document.getElementById('xy-fullscreen-btn');
var n=Math.max(8,Math.min(24,xyTitleFontSize||10));
var titlePx=n+3;
if(t){
t.style.fontSize=titlePx+'px';
t.style.lineHeight='1.15';
}
if(hdr){
var vPad=Math.max(6,Math.round(titlePx*0.45));
hdr.style.padding=vPad+'px 12px';
hdr.style.minHeight=Math.max(30,Math.round(titlePx*1.65))+'px';
}
if(fsBtn){
fsBtn.style.top=Math.max(4,Math.round(titlePx*0.28))+'px';
}
}

function xyUpdateFontControls(){
var fontIn=document.getElementById('xy-pref-font');
var fontVal=document.getElementById('xy-font-val');
var fmtSel=document.getElementById('xy-val-format');
var fmtVal=document.getElementById('xy-format-val');
var lvlIn=document.getElementById('xy-float-levels');
var lvlVal=document.getElementById('xy-float-levels-val');
var lvlRow=document.getElementById('xy-float-levels-row');
if(fontIn)fontIn.value=String(xyTitleFontSize);
if(fontVal)fontVal.textContent=xyTitleFontSize+' px';
if(fmtSel)fmtSel.value=xyValueFormat;
if(fmtVal)fmtVal.textContent=xyValueFormat==='float'?'Floating':'Exponential';
if(lvlIn)lvlIn.value=String(xyFloatLevels);
if(lvlVal)lvlVal.textContent=String(xyFloatLevels);
if(lvlRow){
var en=(xyValueFormat==='float');
lvlRow.style.opacity=en?'1':'0.55';
if(lvlIn)lvlIn.disabled=!en;
}
xyApplyPanelTitleFont();
}

function xyPositionFontPopup(){
var pop=document.getElementById('xy-font-popup');
var btn=document.getElementById('xy-font-btn');
var panel=document.getElementById('xy-panel');
if(!pop||!btn||!panel)return;
var br=btn.getBoundingClientRect();
var rr=panel.getBoundingClientRect();
var left=br.left-rr.left;
var top=br.bottom-rr.top+6;
pop.style.left=left+'px';
pop.style.top=top+'px';
var pw=pop.offsetWidth||280;
var ph=pop.offsetHeight||130;
var maxLeft=Math.max(10,panel.clientWidth-pw-10);
var maxTop=Math.max(10,panel.clientHeight-ph-10);
if(left>maxLeft){
left=maxLeft;
pop.style.left=left+'px';
}
if(top>maxTop){
top=Math.max(10,(br.top-rr.top)-ph-6);
pop.style.top=top+'px';
}
}

function xySetTitleFont(v){
var n=parseInt(v,10);
if(!isFinite(n))n=10;
n=Math.max(8,Math.min(24,n));
xyTitleFontSize=n;
if(xyValuesFontSize>n)xyValuesFontSize=n;
xyUpdateFontControls();
xyUpdatePlotSize();
drawPlot();
}

function xySetValuesFont(v){
var n=parseInt(v,10);
if(!isFinite(n))n=9;
n=Math.max(7,Math.min(20,n));
xyValuesFontSize=n;
xyUpdateFontControls();
drawPlot();
}

function xySetPrefFont(v){
var n=parseInt(v,10);
if(!isFinite(n))n=10;
n=Math.max(8,Math.min(24,n));
xyTitleFontSize=n;
xyValuesFontSize=Math.max(7,Math.min(20,n-1));
xyUpdateFontControls();
xyUpdatePlotSize();
drawPlot();
}

function xySetValueFormat(fmt){
xyValueFormat=(fmt==='float')?'float':'exp';
xyUpdateFontControls();
drawPlot();
}

function xySetFloatLevels(v){
var n=parseInt(v,10);
if(!isFinite(n))n=4;
n=Math.max(0,Math.min(8,n));
xyFloatLevels=n;
xyUpdateFontControls();
drawPlot();
}

function xyToggleFontPopup(show){
var pop=document.getElementById('xy-font-popup');
if(!pop)return;
var shouldShow=(show===undefined)?(pop.style.display!=='block'):!!show;
if(!shouldShow){
pop.style.display='none';
return;
}
xyUpdateFontControls();
pop.style.display='block';
xyPositionFontPopup();
}

function xyToggleAnimInfo(){
xyAnimInfoVisible=!xyAnimInfoVisible;
xyRefreshAnimInfoButton();
drawPlot();
}

function xyGetInfoBoxFontSpec(){
var titlePx=Math.max(8,Math.min(24,xyTitleFontSize||10));
var bodyPx=Math.max(7,Math.min(20,xyValuesFontSize||9));
var pad=Math.max(6,Math.round(bodyPx*0.7));
var titleLineH=Math.max(12,Math.round(titlePx*1.2));
var bodyLineH=Math.max(12,Math.round(bodyPx*1.25));
return {
titleFont:'bold '+titlePx+'px Arial',
bodyFont:bodyPx+'px Arial',
pad:pad,
titleLineH:titleLineH,
bodyLineH:bodyLineH
};
}

function xyDrawAnimHighlightInfo(ctx,ml,mt,pw,ph,items,occupied){
if(!occupied)occupied=[];
if(!xyAnimInfoVisible||xyAnimIndex<0||!items||items.length===0)return;
var xn=document.getElementById('xy-xname');
var yn=document.getElementById('xy-yname');
var syn=document.getElementById('xy-syname');
var xlbl=xn?xn.value||'X':'X';
var ylblL=yn?yn.value||'Y':'Y';
var ylblR=syn?syn.value||'Y (R)':'Y (R)';
for(var ii=0;ii<items.length;ii++){
var it=items[ii];
if(!it||!it.curve||!it.point)continue;
var c=it.curve;
var p=it.point;
var cCol=c.color||CURVE_COLORS[ii%CURVE_COLORS.length];
var ylbl=(c.axis==='secondary')?ylblR:ylblL;
var lines=['Pin: '+c.name+(c.axis==='secondary'?' (R)':''),xlbl+': '+xyFmt(p[0]),ylbl+': '+xyFmt(p[1])];
var fontSpec=xyGetInfoBoxFontSpec();
ctx.save();
var pad=fontSpec.pad;
ctx.font=fontSpec.titleFont;
var maxW=ctx.measureText(lines[0]).width;
ctx.font=fontSpec.bodyFont;
for(var li=1;li<lines.length;li++){
var w=ctx.measureText(lines[li]).width;
if(w>maxW)maxW=w;
}
var boxW=maxW+pad*2,boxH=pad*2+fontSpec.titleLineH+Math.max(0,lines.length-1)*fontSpec.bodyLineH;
var place=xyPlaceInfoBox(it.x,it.y,boxW,boxH,ml,mt,pw,ph,occupied);
occupied.push(place);
xyDrawInfoConnector(ctx,it.x,it.y,place,xyHexToRgba(cCol,0.9));
ctx.fillStyle='rgba(255,235,59,0.55)';
ctx.strokeStyle=xyHexToRgba(cCol,0.85);
ctx.lineWidth=1;
roundRectPath(ctx,place.x,place.y,boxW,boxH,4);
ctx.fillStyle='#5D4037';
ctx.textAlign='left';
ctx.textBaseline='top';
ctx.font=fontSpec.titleFont;
ctx.fillText(lines[0],place.x+pad,place.y+pad);
ctx.font=fontSpec.bodyFont;
for(var li=1;li<lines.length;li++){
ctx.fillText(lines[li],place.x+pad,place.y+pad+fontSpec.titleLineH+(li-1)*fontSpec.bodyLineH);
}
ctx.restore();
}
}

function xyToggleSection(secId,hdrId){
var sec=document.getElementById(secId);
var hdr=document.getElementById(hdrId);
if(!sec||!hdr)return;
if(sec.style.display==='none'){sec.style.display='block';hdr.textContent=hdr.textContent.replace('[+]','[-]');}
else{sec.style.display='none';hdr.textContent=hdr.textContent.replace('[-]','[+]');}
setTimeout(function(){xyResizePlot();},50);
}

function xyOnHover(e){
if(xyZoomDrag)return;
var cv=document.getElementById('xy-plot-canvas');
var tt=document.getElementById('xy-tooltip');
if(!cv||!tt||xyCurves.length===0){if(tt)tt.style.display='none';return;}
var rect=cv.getBoundingClientRect();
var mx=e.clientX-rect.left,my=e.clientY-rect.top;
var W=cv._cssW||rect.width,H=cv._cssH||rect.height;
var ctx=cv.getContext('2d');
var layout=xyGetPlotLayout(W,H,ctx);
var hasSec=layout.hasSec;
var ml=layout.ml,mr=layout.mr,mt=layout.mt,mb=layout.mb;
var pw=layout.pw,ph=layout.ph;
if(pw<20||ph<20){tt.style.display='none';return;}
var priR=layout.priR;
var secR=layout.secR;
var bestDist=8,bestPt=null,bestCurve=null,bestCol=null;
xyCurves.forEach(function(c,ci){
if(!xyIsCurveVisible(c)||!c.data)return;
var col=c.color||CURVE_COLORS[ci%CURVE_COLORS.length];
var rngY=(c.axis==='secondary'&&secR)?secR:priR;
c.data.forEach(function(p){
var px=ml+(p[0]-priR.xmin)/(priR.xmax-priR.xmin)*pw;
var py=mt+(rngY.ymax-p[1])/(rngY.ymax-rngY.ymin)*ph;
var d=Math.sqrt((mx-px)*(mx-px)+(my-py)*(my-py));
if(d<bestDist){bestDist=d;bestPt=p;bestCurve=c;bestCol=col;}
});
});
if(bestPt&&bestCurve){
var xn=document.getElementById('xy-xname');
var yn=document.getElementById('xy-yname');
var syn=document.getElementById('xy-syname');
var xlbl=xn?xn.value||'X':'X';
var ylbl=(bestCurve.axis==='secondary')?(syn?syn.value||'Y (R)':'Y (R)'):(yn?yn.value||'Y':'Y');
var fontSpec=xyGetInfoBoxFontSpec();
var titlePx=Math.max(8,Math.min(24,xyTitleFontSize||10));
var bodyPx=Math.max(7,Math.min(20,xyValuesFontSize||9));
var gap=Math.max(2,Math.round(bodyPx*0.2));
tt.style.padding=fontSpec.pad+'px';
tt.style.fontSize=bodyPx+'px';
tt.style.lineHeight=fontSpec.bodyLineH+'px';
tt.style.borderRadius=Math.max(4,Math.round(bodyPx*0.45))+'px';
tt.innerHTML='<div style="font-size:'+titlePx+'px;line-height:'+fontSpec.titleLineH+'px;font-weight:700;margin-bottom:'+gap+'px"><b>'+bestCurve.name+'</b>'+(bestCurve.axis==='secondary'?' (R)':'')+'</div><div>'+xlbl+': '+xyFmt(bestPt[0])+'</div><div>'+ylbl+': '+xyFmt(bestPt[1])+'</div>';
tt.style.background=bestCol;
tt.style.display='block';
var tx=e.clientX-rect.left+12,ty=e.clientY-rect.top-10;
var tw=tt.offsetWidth||130;
var th=tt.offsetHeight||40;
if(tx+tw>rect.width-4)tx=Math.max(4,e.clientX-rect.left-tw-12);
if(ty+th>rect.height-4)ty=Math.max(4,rect.height-th-4);
if(ty<4)ty=Math.min(rect.height-th-4,e.clientY-rect.top+12);
tt.style.left=tx+'px';tt.style.top=ty+'px';
}else{tt.style.display='none';}
}

function xyHexToRgba(hex,alpha){
if(!hex)return 'rgba(0,0,0,'+alpha+')';
var h=hex.charAt(0)==='#'?hex.substring(1):hex;
if(h.length===3){h=h[0]+h[0]+h[1]+h[1]+h[2]+h[2];}
var r=parseInt(h.substring(0,2),16);
var g=parseInt(h.substring(2,4),16);
var b=parseInt(h.substring(4,6),16);
if(isNaN(r)||isNaN(g)||isNaN(b))return 'rgba(0,0,0,'+alpha+')';
return 'rgba('+r+','+g+','+b+','+alpha+')';
}

function xyPickPoint(e){
var cv=document.getElementById('xy-plot-canvas');
if(!cv||xyCurves.length===0)return null;
var rect=cv.getBoundingClientRect();
var W=cv._cssW||rect.width,H=cv._cssH||rect.height;
var mx=e.clientX-rect.left;
var my=e.clientY-rect.top;
var ctx=cv.getContext('2d');
var layout=xyGetPlotLayout(W,H,ctx);
var ml=layout.ml,mr=layout.mr,mt=layout.mt,mb=layout.mb;
var pw=layout.pw,ph=layout.ph;
if(pw<20||ph<20)return null;
if(mx<ml||mx>ml+pw||my<mt||my>mt+ph)return null;
var priR=layout.priR;
var secR=layout.secR;
var bestDist=8,best=null;
xyCurves.forEach(function(c,ci){
if(!xyIsCurveVisible(c)||!c.data)return;
var col=c.color||CURVE_COLORS[ci%CURVE_COLORS.length];
var rngY=(c.axis==='secondary'&&secR)?secR:priR;
for(var pi=0;pi<c.data.length;pi++){
var p=c.data[pi];
var px=ml+(p[0]-priR.xmin)/(priR.xmax-priR.xmin)*pw;
var py=mt+(rngY.ymax-p[1])/(rngY.ymax-rngY.ymin)*ph;
var d=Math.sqrt((mx-px)*(mx-px)+(my-py)*(my-py));
if(d<bestDist){bestDist=d;best={curveIdx:ci,pointIdx:pi,color:col};}
}
});
return best;
}

function xySelectPoint(e){
var hit=xyPickPoint(e);
if(!hit)return;
var idx=-1;
for(var i=0;i<xyPinned.length;i++){
if(xyPinned[i].curveIdx===hit.curveIdx&&xyPinned[i].pointIdx===hit.pointIdx){idx=i;break;}
}
if(idx>=0){xyPinned.splice(idx,1);drawPlot();return;}
xyPinned.push({curveIdx:hit.curveIdx,pointIdx:hit.pointIdx,color:hit.color});
drawPlot();
}

function xyClearPinned(){xyPinned=[];drawPlot();}

function xyBoxesOverlap(a,b,pad){
var p=(pad===undefined||pad===null)?0:pad;
return !(a.x+a.w+p<=b.x||b.x+b.w+p<=a.x||a.y+a.h+p<=b.y||b.y+b.h+p<=a.y);
}

function xyPlaceInfoBox(px,py,boxW,boxH,ml,mt,pw,ph,occupied){
var candidates=[
{x:px+10,y:py-boxH-10},
{x:px-boxW-10,y:py-boxH-10},
{x:px+10,y:py+10},
{x:px-boxW-10,y:py+10},
{x:px+16,y:py-boxH*0.5},
{x:px-boxW-16,y:py-boxH*0.5},
{x:px-boxW*0.5,y:py-boxH-14},
{x:px-boxW*0.5,y:py+14}
];
var best=null,bestScore=1e9,bestDist=1e9;
for(var ci=0;ci<candidates.length;ci++){
var c=candidates[ci];
var bx=Math.max(ml+2,Math.min(c.x,ml+pw-boxW-2));
var by=Math.max(mt+2,Math.min(c.y,mt+ph-boxH-2));
var box={x:bx,y:by,w:boxW,h:boxH};
var ov=0;
for(var oi=0;oi<occupied.length;oi++){
if(xyBoxesOverlap(box,occupied[oi],4))ov++;
}
var dx=(bx-px),dy=(by-py),dist=dx*dx+dy*dy;
if(ov===0)return box;
if(ov<bestScore||(ov===bestScore&&dist<bestDist)){
bestScore=ov;
bestDist=dist;
best=box;
}
}
return best||{x:Math.max(ml+2,Math.min(px+10,ml+pw-boxW-2)),y:Math.max(mt+2,Math.min(py-boxH-10,mt+ph-boxH-2)),w:boxW,h:boxH};
}

function xyDrawInfoConnector(ctx,px,py,box,color){
if(!box)return;
var tx=Math.max(box.x,Math.min(px,box.x+box.w));
var ty=Math.max(box.y,Math.min(py,box.y+box.h));
ctx.save();
ctx.strokeStyle=color||'rgba(0,0,0,0.55)';
ctx.lineWidth=1;
ctx.setLineDash([4,3]);
ctx.beginPath();
ctx.moveTo(px,py);
ctx.lineTo(tx,ty);
ctx.stroke();
ctx.restore();
}

function xyDrawPinned(ctx,ml,mt,pw,ph,priR,secR,occupied){
if(!occupied)occupied=[];
if(!xyPinned||xyPinned.length===0)return;
for(var pi=0;pi<xyPinned.length;pi++){
var pin=xyPinned[pi];
var c=xyCurves[pin.curveIdx];
if(!xyIsCurveVisible(c)||!c.data||pin.pointIdx<0||pin.pointIdx>=c.data.length)continue;
var p=c.data[pin.pointIdx];
if(!p||p.length<2)continue;
var x=p[0],y=p[1];
var yR=(c.axis==='secondary'&&secR)?secR:priR;
var px=ml+(x-priR.xmin)/(priR.xmax-priR.xmin)*pw;
var py=mt+(yR.ymax-y)/(yR.ymax-yR.ymin)*ph;
if(!isFinite(px)||!isFinite(py))continue;
if(px<ml||px>ml+pw||py<mt||py>mt+ph)continue;
var col=c.color||CURVE_COLORS[pin.curveIdx%CURVE_COLORS.length];
ctx.save();
ctx.beginPath();ctx.rect(ml,mt,pw,ph);ctx.clip();
ctx.setLineDash([5,4]);
ctx.strokeStyle='rgba(0,0,0,0.35)';
ctx.lineWidth=1;
ctx.beginPath();ctx.moveTo(px,mt);ctx.lineTo(px,mt+ph);ctx.stroke();
ctx.beginPath();ctx.moveTo(ml,py);ctx.lineTo(ml+pw,py);ctx.stroke();
ctx.setLineDash([]);
ctx.beginPath();ctx.arc(px,py,6.2,0,Math.PI*2);
ctx.strokeStyle=xyHexToRgba(col,0.35);ctx.lineWidth=4;ctx.stroke();
ctx.beginPath();ctx.arc(px,py,4.6,0,Math.PI*2);
ctx.fillStyle=col;ctx.fill();
ctx.strokeStyle='#fff';ctx.lineWidth=1.6;ctx.stroke();
ctx.restore();
var xn=document.getElementById('xy-xname');
var yn=document.getElementById('xy-yname');
var syn=document.getElementById('xy-syname');
var xlbl=xn?xn.value||'X':'X';
var ylbl=(c.axis==='secondary')?(syn?syn.value||'Y (R)':'Y (R)'):(yn?yn.value||'Y':'Y');
var title=c.name+(c.axis==='secondary'?' (R)':'');
var lines=[title,xlbl+': '+xyFmt(x),ylbl+': '+xyFmt(y)];
var fontSpec=xyGetInfoBoxFontSpec();
ctx.save();
var pad=fontSpec.pad;
ctx.font=fontSpec.titleFont;
var maxW=ctx.measureText(lines[0]).width;
ctx.font=fontSpec.bodyFont;
for(var li=1;li<lines.length;li++){
var w=ctx.measureText(lines[li]).width;
if(w>maxW)maxW=w;
}
var boxW=maxW+pad*2,boxH=pad*2+fontSpec.titleLineH+Math.max(0,lines.length-1)*fontSpec.bodyLineH;
var place=xyPlaceInfoBox(px,py,boxW,boxH,ml,mt,pw,ph,occupied);
occupied.push(place);
xyDrawInfoConnector(ctx,px,py,place,xyHexToRgba(col,0.85));
ctx.fillStyle='rgba(255,255,255,0.75)';
ctx.strokeStyle=xyHexToRgba(col,0.6);ctx.lineWidth=1;
roundRectPath(ctx,place.x,place.y,boxW,boxH,4);
ctx.fillStyle='#333';ctx.textAlign='left';ctx.textBaseline='top';
ctx.font=fontSpec.titleFont;ctx.fillText(lines[0],place.x+pad,place.y+pad);
ctx.font=fontSpec.bodyFont;
for(var li=1;li<lines.length;li++){ctx.fillText(lines[li],place.x+pad,place.y+pad+fontSpec.titleLineH+(li-1)*fontSpec.bodyLineH);}
ctx.restore();
}
}

function xyCalcRange(axisType,ml,mr,mt,mb,W,H){
var xmin=Infinity,xmax=-Infinity,ymin=Infinity,ymax=-Infinity;
var found=0;
function xyRangeAccPoint(p){
if(!p||p.length<2)return;
var px=Number(p[0]),py=Number(p[1]);
if(!isFinite(px)||!isFinite(py))return;
if(px<xmin)xmin=px;if(px>xmax)xmax=px;
if(py<ymin)ymin=py;if(py>ymax)ymax=py;
found++;
}
xyCurves.forEach(function(c){
if(!xyIsCurveVisible(c))return;
var match=(axisType==='secondary')?(c.axis==='secondary'):(c.axis!=='secondary');
if(!match)return;
c.data.forEach(function(p){xyRangeAccPoint(p);});
});
// If primary curves were deleted and only secondary remain, fallback to all curves.
if(found===0&&axisType!=='secondary'&&xyCurves&&xyCurves.length>0){
xyCurves.forEach(function(c){
if(!xyIsCurveVisible(c)||!c.data)return;
c.data.forEach(function(p){xyRangeAccPoint(p);});
});
}
if(!isFinite(xmin)){xmin=0;xmax=1;ymin=0;ymax=1;}
if(Math.abs(xmax-xmin)<1e-20){xmin-=0.5;xmax+=0.5;}
if(Math.abs(ymax-ymin)<1e-20){ymin-=0.5;ymax+=0.5;}
var dx=(xmax-xmin)*0.05,dy=(ymax-ymin)*0.05;
var r={xmin:xmin-dx,xmax:xmax+dx,ymin:ymin-dy,ymax:ymax+dy};
if(axisType!=='secondary'){
var ux=xyUserRange.xmin,uxm=xyUserRange.xmax,uy=xyUserRange.ymin,uym=xyUserRange.ymax;
if(ux!=='auto'&&!isNaN(parseFloat(ux)))r.xmin=parseFloat(ux);
if(uxm!=='auto'&&!isNaN(parseFloat(uxm)))r.xmax=parseFloat(uxm);
if(uy!=='auto'&&!isNaN(parseFloat(uy)))r.ymin=parseFloat(uy);
if(uym!=='auto'&&!isNaN(parseFloat(uym)))r.ymax=parseFloat(uym);
}else{
var ux=xyUserRange.xmin,uxm=xyUserRange.xmax;
if(ux!=='auto'&&!isNaN(parseFloat(ux)))r.xmin=parseFloat(ux);
if(uxm!=='auto'&&!isNaN(parseFloat(uxm)))r.xmax=parseFloat(uxm);
var sy=xySecUserRange.ymin,sym=xySecUserRange.ymax;
if(sy!=='auto'&&!isNaN(parseFloat(sy)))r.ymin=parseFloat(sy);
if(sym!=='auto'&&!isNaN(parseFloat(sym)))r.ymax=parseFloat(sym);
}
return r;
}

function xyZoomMouseDown(e){
if(e.button!==0)return;
var cv=document.getElementById('xy-plot-canvas');
var rect=cv.getBoundingClientRect();
var W=cv._cssW||rect.width,H=cv._cssH||rect.height;
var mx=e.clientX-rect.left;
var my=e.clientY-rect.top;
var ctx=cv.getContext('2d');
var layout=xyGetPlotLayout(W,H,ctx);
var ml=layout.ml,mr=layout.mr,mt=layout.mt,mb=layout.mb;
var pw=layout.pw,ph=layout.ph;
if(mx>=ml&&mx<=ml+pw&&my>=mt&&my<=mt+ph){
xyZoomDrag=true;xyZoomStart={x:mx,y:my,cx:e.clientX-rect.left,cy:e.clientY-rect.top};xyZoomEnd=null;
}
}
function xyZoomMouseMove(e){
if(!xyZoomDrag||!xyZoomStart)return;
var cv=document.getElementById('xy-plot-canvas');
var rect=cv.getBoundingClientRect();
var cx=e.clientX-rect.left,cy=e.clientY-rect.top;
xyZoomEnd={x:cx,y:cy};
var zr=document.getElementById('xy-zoom-rect');
if(zr){
var x1=Math.min(xyZoomStart.cx,cx),y1=Math.min(xyZoomStart.cy,cy);
var w=Math.abs(cx-xyZoomStart.cx),h=Math.abs(cy-xyZoomStart.cy);
zr.style.left=x1+'px';zr.style.top=y1+'px';zr.style.width=w+'px';zr.style.height=h+'px';
zr.style.display=(w>5||h>5)?'block':'none';
}
}
function xyZoomMouseUp(e){
if(!xyZoomDrag||!xyZoomStart){xyZoomCancel();return;}
if(!xyZoomEnd){xySelectPoint(e);xyZoomCancel();return;}
var cv=document.getElementById('xy-plot-canvas');
var rect=cv.getBoundingClientRect();
var W=cv._cssW||rect.width,H=cv._cssH||rect.height;
var ctx=cv.getContext('2d');
var layout=xyGetPlotLayout(W,H,ctx);
var ml=layout.ml,mr=layout.mr,mt=layout.mt,mb=layout.mb;
var pw=layout.pw,ph=layout.ph;
var x1=Math.min(xyZoomStart.x,xyZoomEnd.x),x2=Math.max(xyZoomStart.x,xyZoomEnd.x);
var y1=Math.min(xyZoomStart.y,xyZoomEnd.y),y2=Math.max(xyZoomStart.y,xyZoomEnd.y);
if(x2-x1<5||y2-y1<5){xySelectPoint(e);xyZoomCancel();return;}
var rng=layout.priR;
var nXmin=rng.xmin+(x1-ml)/pw*(rng.xmax-rng.xmin);
var nXmax=rng.xmin+(x2-ml)/pw*(rng.xmax-rng.xmin);
var nYmax=rng.ymax-(y1-mt)/ph*(rng.ymax-rng.ymin);
var nYmin=rng.ymax-(y2-mt)/ph*(rng.ymax-rng.ymin);
xyUserRange.xmin=nXmin.toString();xyUserRange.xmax=nXmax.toString();
xyUserRange.ymin=nYmin.toString();xyUserRange.ymax=nYmax.toString();
document.getElementById('xy-xmin').value=xyFmt(nXmin);
document.getElementById('xy-xmax').value=xyFmt(nXmax);
document.getElementById('xy-ymin').value=xyFmt(nYmin);
document.getElementById('xy-ymax').value=xyFmt(nYmax);
xyZoomCancel();drawPlot();
}
function xyZoomCancel(){
xyZoomDrag=false;xyZoomStart=null;xyZoomEnd=null;
var zr=document.getElementById('xy-zoom-rect');if(zr)zr.style.display='none';
}
function xyResetZoom(){
xyUserRange.xmin=xyAppliedRange.xmin;
xyUserRange.xmax=xyAppliedRange.xmax;
xyUserRange.ymin=xyAppliedRange.ymin;
xyUserRange.ymax=xyAppliedRange.ymax;
xySecUserRange.ymin=xySecAppliedRange.ymin;
xySecUserRange.ymax=xySecAppliedRange.ymax;
document.getElementById('xy-xmin').value=xyAppliedRange.xmin;
document.getElementById('xy-xmax').value=xyAppliedRange.xmax;
document.getElementById('xy-ymin').value=xyAppliedRange.ymin;
document.getElementById('xy-ymax').value=xyAppliedRange.ymax;
document.getElementById('xy-symin').value=xySecAppliedRange.ymin;
document.getElementById('xy-symax').value=xySecAppliedRange.ymax;
drawPlot();
}
var xyIsFullscreen=false;
function xyToggleFullscreen(){
var panel=document.getElementById('xy-panel');
var btn=document.getElementById('xy-fullscreen-btn');
if(!panel)return;
xyIsFullscreen=!xyIsFullscreen;
if(xyIsFullscreen){panel.classList.add('xy-fullscreen');btn.innerHTML='&#x2715;';btn.title='Exit Fullscreen';}
else{panel.classList.remove('xy-fullscreen');btn.innerHTML='&#x26F6;';btn.title='Toggle Fullscreen';}
void panel.offsetHeight;xyResizePlot();
}

function xyAskColumn(callback){
var overlay=document.createElement('div');
overlay.style.cssText='position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.4);z-index:10000;display:flex;align-items:center;justify-content:center';
var box=document.createElement('div');
box.style.cssText='background:white;border-radius:8px;padding:20px 30px;box-shadow:0 4px 20px rgba(0,0,0,0.3);text-align:center;min-width:200px';
box.innerHTML='<div style="font-size:13px;font-weight:bold;color:#333;margin-bottom:15px">Single column detected.<br>Paste data as:</div>';
var btnX=document.createElement('button');btnX.textContent='X';
btnX.style.cssText='font-size:14px;font-weight:bold;padding:8px 30px;margin:0 8px;border:2px solid #2196F3;background:#2196F3;color:white;border-radius:5px;cursor:pointer';
btnX.onclick=function(){document.body.removeChild(overlay);callback('X');};
var btnY=document.createElement('button');btnY.textContent='Y';
btnY.style.cssText='font-size:14px;font-weight:bold;padding:8px 30px;margin:0 8px;border:2px solid #FF9800;background:#FF9800;color:white;border-radius:5px;cursor:pointer';
btnY.onclick=function(){document.body.removeChild(overlay);callback('Y');};
var btnC=document.createElement('button');btnC.textContent='Cancel';
btnC.style.cssText='font-size:11px;padding:5px 15px;margin-top:12px;border:1px solid #ccc;background:#f5f5f5;color:#666;border-radius:4px;cursor:pointer;display:block;margin-left:auto;margin-right:auto';
btnC.onclick=function(){document.body.removeChild(overlay);};
box.appendChild(btnX);box.appendChild(btnY);box.appendChild(btnC);
overlay.appendChild(box);document.body.appendChild(overlay);
}

function xyAskColumns(callback,includeHarmonic){
var overlay=document.createElement('div');
overlay.style.cssText='position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.4);z-index:10000;display:flex;align-items:center;justify-content:center';
var box=document.createElement('div');
box.style.cssText='background:white;border-radius:8px;padding:20px 30px;box-shadow:0 4px 20px rgba(0,0,0,0.3);text-align:center;min-width:250px';
box.innerHTML='<div style="font-size:13px;font-weight:bold;color:#333;margin-bottom:15px">Select column layout:</div>';
var btn2=document.createElement('button');btn2.textContent='2x Columns';
btn2.style.cssText='font-size:13px;font-weight:bold;padding:10px 20px;margin:4px 8px;border:2px solid #2196F3;background:#2196F3;color:white;border-radius:5px;cursor:pointer;display:block;width:90%;margin-left:auto;margin-right:auto';
btn2.onclick=function(){document.body.removeChild(overlay);callback('2x');};
var btn3=document.createElement('button');btn3.textContent='3x Columns';
btn3.style.cssText='font-size:13px;font-weight:bold;padding:10px 20px;margin:4px 8px;border:2px solid #FF9800;background:#FF9800;color:white;border-radius:5px;cursor:pointer;display:block;width:90%;margin-left:auto;margin-right:auto';
btn3.onclick=function(){document.body.removeChild(overlay);callback('3x');};
var btnC=document.createElement('button');btnC.textContent='Cancel';
btnC.style.cssText='font-size:11px;padding:5px 15px;margin-top:12px;border:1px solid #ccc;background:#f5f5f5;color:#666;border-radius:4px;cursor:pointer;display:block;margin-left:auto;margin-right:auto';
btnC.onclick=function(){document.body.removeChild(overlay);};
box.appendChild(btn2);box.appendChild(btn3);
if(includeHarmonic){
var btnH=document.createElement('button');btnH.textContent='Harmonic';
btnH.style.cssText='font-size:13px;font-weight:bold;padding:10px 20px;margin:4px 8px;border:2px solid #7B1FA2;background:#7B1FA2;color:white;border-radius:5px;cursor:pointer;display:block;width:90%;margin-left:auto;margin-right:auto';
btnH.onclick=function(){document.body.removeChild(overlay);callback('harmonic');};
box.appendChild(btnH);
}
box.appendChild(btnC);
overlay.appendChild(box);document.body.appendChild(overlay);
}

function xyLoadExcel(){
document.getElementById('xy-file-input').click();
}

function xyOnFileSelected(input){
if(!input.files||!input.files[0])return;
var file=input.files[0];
var ext=file.name.split('.').pop().toLowerCase();
if(ext==='csv'){
var reader=new FileReader();
reader.onload=function(e){
var text=e.target.result;
xyAskColumns(function(mode){xyProcessCSV(text,mode);},true);
};
reader.readAsText(file);
}else{
if(typeof XLSX==='undefined'){alert('SheetJS library not loaded. Please check internet connection.');input.value='';return;}
var reader=new FileReader();
reader.onload=function(e){
var data=new Uint8Array(e.target.result);
var wb=XLSX.read(data,{type:'array'});
if(VIEWER_MODE==='harmonic'){
try{
if(xyTryImportHarmonicWorkbook(wb))return;
}catch(ex){
console.warn('Harmonic Excel import fallback:',ex);
}
}
xyAskColumns(function(mode){xyProcessWorkbook(wb,mode);},true);
};
reader.readAsArrayBuffer(file);
}
input.value='';
}

function xyProcessCSV(text,mode){
var NL=String.fromCharCode(10);var CR=String.fromCharCode(13);
var raw=text.replace(new RegExp(CR,'g'),'');
var lines=raw.split(NL);
if(mode==='harmonic'){
if(lines.length===0){alert('CSV is empty.');return;}
var hLine=lines[0].trim();
var hParts=hLine.indexOf(';')>=0?hLine.split(';'):hLine.split(',');
if(hParts.length<6){alert('Harmonic mode requires 6 columns (A..F).');return;}
var xHeader=(hParts[0]!==undefined&&hParts[0]!==null&&String(hParts[0]).trim()!=='')?String(hParts[0]).trim():'Frequency (Hz)';
var ampHeader=(hParts[1]!==undefined&&hParts[1]!==null&&String(hParts[1]).trim()!=='')?String(hParts[1]).trim():'Displacement Magnitude';
var ampData=[],stiffData=[],phaseData=[];
var nonEmptyRows=0;
var EPS=1e-20;
for(var li=1;li<lines.length;li++){
var line=lines[li].trim();
if(!line)continue;
var parts=line.indexOf(';')>=0?line.split(';'):line.split(',');
if(parts.length<6)continue;
var parseCsvNum=function(tok){
if(tok===undefined||tok===null)return null;
var t=String(tok).trim();
if(!t)return null;
t=t.replace(/,/g,'.');
var n=parseFloat(t);
return isFinite(n)?n:null;
};
var a=parseCsvNum(parts[0]);
var b=parseCsvNum(parts[1]);
var c=parseCsvNum(parts[2]);
var d=parseCsvNum(parts[3]);
var e=parseCsvNum(parts[4]);
var f=parseCsvNum(parts[5]); // kept for row-validity check
var hasAny=(a!==null||b!==null||c!==null||d!==null||e!==null||f!==null);
if(!hasAny)continue;
nonEmptyRows++;
if(a!==null&&b!==null)ampData.push([a,b]);
if(a!==null&&b!==null&&c!==null&&Math.abs(b)>EPS){
var stiffVal=xyRoundCalc5(c/b);
if(stiffVal!==null)stiffData.push([a,stiffVal]);
}
if(a!==null&&b!==null&&c!==null&&d!==null&&e!==null&&Math.abs(b)>EPS&&Math.abs(c)>EPS){
var phase=xyComputeHarmonicPhaseDeg(b,c,d,e);
if(phase!==null)phaseData.push([a,phase]);
}
}
if(nonEmptyRows===0||(!ampData.length&&!stiffData.length&&!phaseData.length)){
alert('Harmonic CSV import failed: no valid numeric rows found in columns A..F.');
return;
}
xyApplyHarmonicCurves(xHeader,ampHeader,ampData,stiffData,phaseData);
document.getElementById('st').textContent='Harmonic CSV imported';
return;
}
var headers=[];
if(lines.length>0){
var hLine=lines[0].trim();
var hParts=hLine.indexOf(';')>=0?hLine.split(';'):hLine.split(',');
for(var j=1;j<hParts.length;j++){headers.push(hParts[j].trim());}
}
var rows=[];
for(var i=1;i<lines.length;i++){
var line=lines[i].trim();if(!line)continue;
var parts=line.indexOf(';')>=0?line.split(';'):line.split(',');
var nums=[];
for(var j=1;j<parts.length;j++){var v=parseFloat(parts[j].replace(',','.'));nums.push(isNaN(v)?null:v);}
rows.push(nums);
}
xyCreateCurvesFromRows(rows,mode,headers);
}

function xyCellNumberOrNull(ws,row,col){
var addr=XLSX.utils.encode_cell({r:row,c:col});
var cell=ws[addr];
if(!cell||cell.v===undefined||cell.v===null)return null;
var v=cell.v;
if(typeof v==='number')return isFinite(v)?v:null;
var txt=String(v).trim();
if(!txt)return null;
txt=txt.replace(/,/g,'.');
var n=parseFloat(txt);
return isFinite(n)?n:null;
}

function xyCellTextOrEmpty(ws,row,col){
var addr=XLSX.utils.encode_cell({r:row,c:col});
var cell=ws[addr];
if(!cell||cell.v===undefined||cell.v===null)return '';
return String(cell.v).trim();
}

function xyRoundCalc5(v){
var n=Number(v);
if(!isFinite(n))return null;
var r=Number(n.toFixed(5));
if(!isFinite(r))return null;
if(r===0)r=0;
return r;
}

function xyComputeHarmonicPhaseDeg(b,c,d,e){
var EPS=1e-20;
if(!isFinite(b)||!isFinite(c)||!isFinite(d)||!isFinite(e))return null;
if(Math.abs(b)<=EPS||Math.abs(c)<=EPS)return null;
var magNorm=c/b;
if(!isFinite(magNorm)||Math.abs(magNorm)<=EPS)return null;
var realNorm=d/b;
if(!isFinite(realNorm))return null;
var ratio=realNorm/magNorm;
if(!isFinite(ratio))return null;
if(ratio>1)ratio=1;
if(ratio<-1)ratio=-1;
var angleDeg=Math.acos(ratio)*(180/Math.PI);
var phase=((e/b)<0)?(360-angleDeg):angleDeg;
phase=phase-180;
return xyRoundCalc5(phase);
}

function xyApplyHarmonicCurves(xHeader,ampHeader,ampData,stiffData,phaseData){
if(!ampData.length&&!stiffData.length&&!phaseData.length)return false;
var stiffnessLabel='Stiffness';
var phaseLabel='Phase Angle';
xySaveCurrentSheet();
while(xySheets.length<2){
xySheets.push(makeDefaultXySheetState('Sheet '+(xySheets.length+1)));
}
var s1=makeDefaultXySheetState('Sheet 1');
s1.title='Sheet 1';
s1.axisNames.xname=xHeader||'X';
s1.axisNames.yname=stiffnessLabel;
s1.axisNames.syname=phaseLabel;
s1.secUserRange={ymin:'-180',ymax:'180'};
s1.secAppliedRange={ymin:'-180',ymax:'180'};
if(stiffData.length>0){
s1.curves.push({name:'FreqxStiffness',xlabel:s1.axisNames.xname,ylabel:stiffnessLabel,color:CURVE_COLORS[0],data:stiffData,axis:'primary'});
}
if(phaseData.length>0){
s1.curves.push({name:'FreqxPhaseAngle',xlabel:s1.axisNames.xname,ylabel:phaseLabel,color:CURVE_COLORS[1],data:phaseData,axis:'secondary'});
}
s1.selectedIdx=s1.curves.length>0?0:-1;
xySheets[0]=s1;
var s2=makeDefaultXySheetState('Sheet 2');
s2.title='Sheet 2';
s2.axisNames.xname=s1.axisNames.xname;
s2.axisNames.yname=ampHeader||'Amplitude';
if(ampData.length>0){
s2.curves.push({name:'FreqxAmplitude',xlabel:s2.axisNames.xname,ylabel:s2.axisNames.yname,color:CURVE_COLORS[2],data:ampData,axis:'primary'});
}
s2.selectedIdx=s2.curves.length>0?0:-1;
xySheets[1]=s2;
xyActiveSheet=0;
xyLoadSheet(0);
var syMinEl=document.getElementById('xy-symin');
var syMaxEl=document.getElementById('xy-symax');
var syStepEl=document.getElementById('xy-systep');
if(syMinEl)syMinEl.value='-180';
if(syMaxEl)syMaxEl.value='180';
if(syStepEl)syStepEl.value='20';
xySecUserRange={ymin:'-180',ymax:'180'};
xySecAppliedRange={ymin:'-180',ymax:'180'};
xyValueFormat='float';
xyFloatLevels=2;
xyUpdateFontControls();
xyRenderSheetTabs();
xyEditingIdx=-1;
xySelectedIdx=(xyCurves.length>0)?0:-1;
xyRefreshList();
xyUpdatePlotSize();
drawPlot();
document.getElementById('st').textContent='Harmonic Excel imported: Sheet 1 ('+s1.curves.length+' curve(s)), Sheet 2 ('+s2.curves.length+' curve(s)).';
return true;
}

function xyTryImportHarmonicWorkbook(wb,forceMode){
var forced=!!forceMode;
if(!forced&&VIEWER_MODE!=='harmonic')return false;
if(!wb||!wb.SheetNames||wb.SheetNames.length===0)return false;
var ws=wb.Sheets[wb.SheetNames[0]];
if(!ws||!ws['!ref'])return false;
var range=XLSX.utils.decode_range(ws['!ref']);
if(range.e.c<5){
if(forced)alert('Harmonic mode requires at least 6 columns (A..F).');
return false;
}

var headers=[];
for(var hc=0;hc<=5;hc++)headers.push(xyCellTextOrEmpty(ws,0,hc));
if(!forced){
for(var hi=0;hi<headers.length;hi++){
if(!headers[hi])return false;
}
}

var xHeader=headers[0]||'Frequency (Hz)';
var ampHeader=headers[1]||'Displacement Magnitude';
var ampData=[],stiffData=[],phaseData=[];
var nonEmptyRows=0;
var EPS=1e-20;
for(var ri=1;ri<=range.e.r;ri++){
var a=xyCellNumberOrNull(ws,ri,0);
var b=xyCellNumberOrNull(ws,ri,1);
var c=xyCellNumberOrNull(ws,ri,2);
var d=xyCellNumberOrNull(ws,ri,3);
var e=xyCellNumberOrNull(ws,ri,4);
var f=xyCellNumberOrNull(ws,ri,5); // kept for row-validity check
var hasAny=(a!==null||b!==null||c!==null||d!==null||e!==null||f!==null);
if(!hasAny)continue;
nonEmptyRows++;
if(a!==null&&b!==null)ampData.push([a,b]);
if(a!==null&&b!==null&&c!==null&&Math.abs(b)>EPS){
var stiffVal=xyRoundCalc5(c/b);
if(stiffVal!==null)stiffData.push([a,stiffVal]);
}
if(a!==null&&b!==null&&c!==null&&d!==null&&e!==null&&Math.abs(b)>EPS&&Math.abs(c)>EPS){
var phase=xyComputeHarmonicPhaseDeg(b,c,d,e);
if(phase!==null)phaseData.push([a,phase]);
}
}
if(nonEmptyRows===0||(!ampData.length&&!stiffData.length&&!phaseData.length)){
if(forced)alert('Harmonic import failed: no valid numeric rows found in columns A..F.');
return false;
}
return xyApplyHarmonicCurves(xHeader,ampHeader,ampData,stiffData,phaseData);
}

function xyProcessWorkbook(wb,mode){
if(mode==='harmonic'){
xyTryImportHarmonicWorkbook(wb,true);
return;
}
var ws=wb.Sheets[wb.SheetNames[0]];
if(!ws||!ws['!ref']){alert('Empty worksheet.');return;}
var range=XLSX.utils.decode_range(ws['!ref']);
var headers=[];
for(var ci=1;ci<=range.e.c;ci++){
var addr=XLSX.utils.encode_cell({r:0,c:ci});
var cell=ws[addr];
var hdr=(cell&&cell.v!==undefined&&cell.v!==null)?String(cell.v).trim():'';
headers.push(hdr);
}
var rows=[];
for(var ri=1;ri<=range.e.r;ri++){
var nums=[];
var hasAny=false;
for(var ci=1;ci<=range.e.c;ci++){
var addr=XLSX.utils.encode_cell({r:ri,c:ci});
var cell=ws[addr];
var v=(cell&&cell.v!==undefined&&cell.v!==null)?parseFloat(cell.v):null;
if(v!==null&&isNaN(v))v=null;
nums.push(v);
if(v!==null)hasAny=true;
}
if(hasAny)rows.push(nums);
}
xyCreateCurvesFromRows(rows,mode,headers);
}

function xyCreateCurvesFromRows(rows,mode,headers){
if(rows.length===0){alert('No data found starting from row 2, column B.');return;}
var maxCols=0;rows.forEach(function(r){if(r.length>maxCols)maxCols=r.length;});
if(!headers)headers=[];
var firstCurve=true;
var firstXLabel='',firstYLabel='',firstSYLabel='';
if(mode==='2x'){
for(var ci=0;ci+1<maxCols;ci+=2){
var data=[];
for(var ri=0;ri<rows.length;ri++){
var xv=rows[ri][ci],yv=rows[ri][ci+1];
if(xv!==null&&xv!==undefined&&yv!==null&&yv!==undefined)data.push([xv,yv]);
}
if(data.length>0){
var xl=(headers[ci]&&headers[ci]!=='')?headers[ci]:'X';
var yl=(headers[ci+1]&&headers[ci+1]!=='')?headers[ci+1]:'Y';
if(firstCurve){firstXLabel=xl;firstYLabel=yl;}
if(firstCurve&&xyEditingIdx>=0&&xyEditingIdx<xyCurves.length){
xyAppendOrReplaceEditingCurveData(data,'primary',xl,yl);
firstCurve=false;
}else{
var idx=xyCurves.length;
xyCurves.push({name:yl||('Curve '+(idx+1)),xlabel:xl,ylabel:yl,color:CURVE_COLORS[idx%CURVE_COLORS.length],data:data,axis:'primary'});
firstCurve=false;
}
}
}
}else{
for(var ci=0;ci+2<maxCols;ci+=3){
var d1=[],d2=[];
for(var ri=0;ri<rows.length;ri++){
var xv=rows[ri][ci],yv1=rows[ri][ci+1],yv2=rows[ri][ci+2];
if(xv!==null&&xv!==undefined&&yv1!==null&&yv1!==undefined)d1.push([xv,yv1]);
if(xv!==null&&xv!==undefined&&yv2!==null&&yv2!==undefined)d2.push([xv,yv2]);
}
var xl=(headers[ci]&&headers[ci]!=='')?headers[ci]:'X';
var yl1=(headers[ci+1]&&headers[ci+1]!=='')?headers[ci+1]:'Y';
var yl2=(headers[ci+2]&&headers[ci+2]!=='')?headers[ci+2]:'Y2';
if(firstCurve){firstXLabel=xl;firstYLabel=yl1;firstSYLabel=yl2;}
if(d1.length>0){
if(firstCurve&&xyEditingIdx>=0&&xyEditingIdx<xyCurves.length){
xyAppendOrReplaceEditingCurveData(d1,'primary',xl,yl1);
firstCurve=false;
}else{
var idx=xyCurves.length;
xyCurves.push({name:yl1||('Curve '+(idx+1)),xlabel:xl,ylabel:yl1,color:CURVE_COLORS[idx%CURVE_COLORS.length],data:d1,axis:'primary'});
firstCurve=false;
}
}
if(d2.length>0){
var idx=xyCurves.length;
xyCurves.push({name:yl2||('Curve '+(idx+1)),xlabel:xl,ylabel:yl2,color:CURVE_COLORS[idx%CURVE_COLORS.length],data:d2,axis:'secondary'});
}
}
}
if(firstXLabel){document.getElementById('xy-xname').value=firstXLabel;}
if(firstYLabel){document.getElementById('xy-yname').value=firstYLabel;}
if(mode==='3x'&&firstSYLabel){document.getElementById('xy-syname').value=firstSYLabel;}
xyEditingIdx=-1;xySelectedIdx=-1;
document.getElementById('xy-table-area').style.display='none';
xyClearCellSelection();
xyUpdatePlotSize();
xyRefreshList();drawPlot();
document.getElementById('st').textContent='Loaded '+xyCurves.length+' curve(s) from file';
}

function xyGetDataRange(){
var xmin=Infinity,xmax=-Infinity,ymin=Infinity,ymax=-Infinity;
xyCurves.forEach(function(c){
if(!xyIsCurveVisible(c)||!c.data)return;
c.data.forEach(function(p){
if(p[0]<xmin)xmin=p[0];if(p[0]>xmax)xmax=p[0];
if(p[1]<ymin)ymin=p[1];if(p[1]>ymax)ymax=p[1];
});
});
if(!isFinite(xmin)){xmin=0;xmax=1;ymin=0;ymax=1;}
if(Math.abs(xmax-xmin)<1e-20){xmin-=0.5;xmax+=0.5;}
if(Math.abs(ymax-ymin)<1e-20){ymin-=0.5;ymax+=0.5;}
// Add 5% padding
var dx=(xmax-xmin)*0.05,dy=(ymax-ymin)*0.05;
return{xmin:xmin-dx,xmax:xmax+dx,ymin:ymin-dy,ymax:ymax+dy};
}

function xyGetRange(){
var dr=xyGetDataRange();
var r={xmin:dr.xmin,xmax:dr.xmax,ymin:dr.ymin,ymax:dr.ymax};
var ux=xyUserRange.xmin,uxm=xyUserRange.xmax,uy=xyUserRange.ymin,uym=xyUserRange.ymax;
if(ux!=='auto'&&!isNaN(parseFloat(ux)))r.xmin=parseFloat(ux);
if(uxm!=='auto'&&!isNaN(parseFloat(uxm)))r.xmax=parseFloat(uxm);
if(uy!=='auto'&&!isNaN(parseFloat(uy)))r.ymin=parseFloat(uy);
if(uym!=='auto'&&!isNaN(parseFloat(uym)))r.ymax=parseFloat(uym);
return r;
}

function xyBuildTicks(mn,mx,stepStr){
var step=0;
if(stepStr&&stepStr!=='auto'){step=parseFloat(stepStr);if(isNaN(step)||step<=0)step=0;}
if(step===0){
var range=mx-mn;
var raw=range/6;
var mag=Math.pow(10,Math.floor(Math.log10(raw)));
var opts=[1,2,2.5,5,10];
step=mag;
for(var oi=0;oi<opts.length;oi++){if(mag*opts[oi]>=raw){step=mag*opts[oi];break;}}
}
var ticks=[];
var start=Math.ceil(mn/step)*step;
start=parseFloat(start.toPrecision(12));
for(var t=start;t<=mx+step*0.5;t+=step){
var tv=parseFloat(t.toPrecision(12));
if(tv>=mn-step*0.01&&tv<=mx+step*0.01)ticks.push(tv);
if(ticks.length>500)break;
}
ticks.sort(function(a,b){return a-b;});
if(ticks.length===0||Math.abs(ticks[0]-mn)>step*0.02)ticks.unshift(mn);
if(Math.abs(ticks[ticks.length-1]-mx)>step*0.02)ticks.push(mx);
var unique=[];
for(var ui=0;ui<ticks.length;ui++){
if(ui===0||Math.abs(ticks[ui]-ticks[ui-1])>step*0.01)unique.push(ticks[ui]);
}
var maxTicks=12;
if(unique.length>maxTicks){
var keep=[];
var stride=Math.ceil(unique.length/maxTicks);
for(var ki=0;ki<unique.length;ki+=stride){keep.push(unique[ki]);}
if(keep[keep.length-1]!==unique[unique.length-1])keep.push(unique[unique.length-1]);
unique=keep;
}
return unique;
}

function xyPruneTicks(ticks,mn,mx,pixelSpan,minPx){
if(!ticks||ticks.length<=2)return ticks||[];
if(!isFinite(mn)||!isFinite(mx)||Math.abs(mx-mn)<1e-30)return ticks.slice();
if(!isFinite(pixelSpan)||pixelSpan<=0)return ticks.slice();
var out=[ticks[0]];
var lastV=ticks[0];
var lastPos=((lastV-mn)/(mx-mn))*pixelSpan;
var lastLbl=xyFmt(lastV);
for(var i=1;i<ticks.length-1;i++){
var v=ticks[i];
var pos=((v-mn)/(mx-mn))*pixelSpan;
var lbl=xyFmt(v);
var dist=Math.abs(pos-lastPos);
if(dist<minPx)continue;
if(lbl===lastLbl&&dist<minPx*1.35)continue;
out.push(v);
lastV=v;lastPos=pos;lastLbl=lbl;
}
var lv=ticks[ticks.length-1];
var lpos=((lv-mn)/(mx-mn))*pixelSpan;
var llbl=xyFmt(lv);
var pv=out[out.length-1];
var ppos=((pv-mn)/(mx-mn))*pixelSpan;
var plbl=xyFmt(pv);
var ldist=Math.abs(lpos-ppos);
if(lv!==pv){
if(llbl===plbl&&ldist<minPx){
out[out.length-1]=lv;
}else if(ldist<minPx*0.55){
out[out.length-1]=lv;
}else{
out.push(lv);
}
}
return out;
}

function xyMeasureTickMaxWidth(ctx,ticks,fontPx){
if(!ctx||!ticks||ticks.length===0)return 0;
var mw=0;
ctx.save();
ctx.font=fontPx+'px Arial';
for(var i=0;i<ticks.length;i++){
var w=ctx.measureText(xyFmt(ticks[i])).width;
if(w>mw)mw=w;
}
ctx.restore();
return mw;
}

function xyGetPlotLayout(W,H,ctx){
var hasSec=xyCurves.some(function(c){return xyIsCurveVisible(c)&&c.axis==='secondary';});
var mt=15;
var xyTickFont=Math.max(7,Math.min(20,xyValuesFontSize||9));
var xyAxisTitleFont=Math.max(8,Math.min(24,xyTitleFontSize||10));
var axisLabelPad=Math.max(8,Math.ceil(xyAxisTitleFont*0.78));
var priR=xyCalcRange('primary',0,0,0,0,W,H);
var secR=hasSec?xyCalcRange('secondary',0,0,0,0,W,H):null;
var xStepV=document.getElementById('xy-xstep')?document.getElementById('xy-xstep').value:'auto';
var yStepV=document.getElementById('xy-ystep')?document.getElementById('xy-ystep').value:'auto';
var sStepV=document.getElementById('xy-systep')?document.getElementById('xy-systep').value:'auto';
var xTicks=xyBuildTicks(priR.xmin,priR.xmax,xStepV);
var yTicks=xyBuildTicks(priR.ymin,priR.ymax,yStepV);
var secYTicks=secR?xyBuildTicks(secR.ymin,secR.ymax,sStepV):[];
var leftTickW=xyMeasureTickMaxWidth(ctx,yTicks,xyTickFont);
var rightTickW=hasSec?xyMeasureTickMaxWidth(ctx,secYTicks,xyTickFont):0;
var axisBand=Math.ceil(xyAxisTitleFont*1.2);
var ml=Math.max(55,Math.ceil(8+axisBand+leftTickW+8));
var mr=hasSec?Math.max(55,Math.ceil(8+axisBand+rightTickW+8)):15;
var mb=Math.max(40,Math.ceil(xyTickFont+xyAxisTitleFont+22));
var pw=W-ml-mr;
var ph=H-mt-mb;
if(pw<20){
var lack=20-pw;
var canL=Math.max(0,ml-42);
var canR=Math.max(0,mr-(hasSec?42:15));
var takeL=Math.min(canL,Math.ceil(lack*0.5));
ml-=takeL;
lack-=takeL;
mr-=Math.min(canR,lack);
pw=W-ml-mr;
}
if(ph<20){
mb=Math.max(24,H-mt-20);
ph=H-mt-mb;
}
// Final tick pruning by available pixel space to prevent overlap after range changes/deletions.
var minXPx=Math.max(32,Math.round(xyTickFont*4.2));
var minYPx=Math.max(16,Math.round(xyTickFont*1.9));
xTicks=xyPruneTicks(xTicks,priR.xmin,priR.xmax,pw,minXPx);
yTicks=xyPruneTicks(yTicks,priR.ymin,priR.ymax,ph,minYPx);
if(secR)secYTicks=xyPruneTicks(secYTicks,secR.ymin,secR.ymax,ph,minYPx);
return{
hasSec:hasSec,
ml:ml,mr:mr,mt:mt,mb:mb,pw:pw,ph:ph,
priR:priR,secR:secR,
xTicks:xTicks,yTicks:yTicks,secYTicks:secYTicks,
xyTickFont:xyTickFont,xyAxisTitleFont:xyAxisTitleFont,
leftAxisLabelX:axisLabelPad,rightAxisLabelX:Math.max(axisLabelPad,W-axisLabelPad)
};
}

function drawPlot(){
var cv=document.getElementById('xy-plot-canvas');
if(!cv)return;
xyRefreshAnimInfoButton();
var ctx=cv.getContext('2d');
var dpr=cv._dpr||1;
var W=(cv._cssW!==undefined)?cv._cssW:cv.width/dpr;
var H=(cv._cssH!==undefined)?cv._cssH:cv.height/dpr;
ctx.setTransform(dpr,0,0,dpr,0,0);
ctx.clearRect(0,0,W,H);
ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);
var hasVisible=xyCurves.some(function(c){return xyIsCurveVisible(c);});
if(xyCurves.length===0||!hasVisible){
var leg0=document.getElementById('xy-legend');
if(leg0){leg0.innerHTML='';}
ctx.fillStyle='#aaa';ctx.font='12px Arial';ctx.textAlign='center';
ctx.fillText(xyCurves.length===0?'No curves. Click "Add" to create one.':'All curves are hidden. Double-click a curve and click "Show".',W/2,H/2);
return;
}
var layout=xyGetPlotLayout(W,H,ctx);
var hasSec=layout.hasSec;
var ml=layout.ml,mr=layout.mr,mt=layout.mt,mb=layout.mb;
var pw=layout.pw,ph=layout.ph;
if(pw<20||ph<20)return;
var priR=layout.priR;
var secR=layout.secR;
var rng=priR;
var xTicks=layout.xTicks;
var yTicks=layout.yTicks;
var secYTicks=layout.secYTicks;
function mapXp(v){return ml+(v-rng.xmin)/(rng.xmax-rng.xmin)*pw;}
function mapYp(v){return mt+(rng.ymax-v)/(rng.ymax-rng.ymin)*ph;}
function mapYs(v){return secR?mt+(secR.ymax-v)/(secR.ymax-secR.ymin)*ph:0;}
ctx.strokeStyle='#eee';ctx.lineWidth=1;
for(var gi=0;gi<xTicks.length;gi++){var gx=mapXp(xTicks[gi]);ctx.beginPath();ctx.moveTo(gx,mt);ctx.lineTo(gx,mt+ph);ctx.stroke();}
for(var gi=0;gi<yTicks.length;gi++){var gy=mapYp(yTicks[gi]);ctx.beginPath();ctx.moveTo(ml,gy);ctx.lineTo(ml+pw,gy);ctx.stroke();}
if(hasSec&&secR){
ctx.save();
ctx.strokeStyle='rgba(244,67,54,0.22)';
ctx.lineWidth=0.8;
for(var gi=0;gi<secYTicks.length;gi++){
var gsy=mapYs(secYTicks[gi]);
ctx.beginPath();
ctx.moveTo(ml,gsy);
ctx.lineTo(ml+pw,gsy);
ctx.stroke();
}
ctx.restore();
}
ctx.strokeStyle='#333';ctx.lineWidth=1.5;
ctx.strokeRect(ml,mt,pw,ph);
var oriCb=document.getElementById('xy-origin');
if(oriCb&&oriCb.checked){
ctx.save();ctx.setLineDash([6,4]);ctx.lineWidth=1;ctx.strokeStyle='rgba(255,0,0,0.5)';
if(rng.xmin<=0&&rng.xmax>=0){var zx=mapXp(0);ctx.beginPath();ctx.moveTo(zx,mt);ctx.lineTo(zx,mt+ph);ctx.stroke();}
if(rng.ymin<=0&&rng.ymax>=0){var zy=mapYp(0);ctx.beginPath();ctx.moveTo(ml,zy);ctx.lineTo(ml+pw,zy);ctx.stroke();}
ctx.restore();
}
var xyTickFont=layout.xyTickFont;
var xyAxisTitleFont=layout.xyAxisTitleFont;
var leftAxisLabelX=layout.leftAxisLabelX;
var rightAxisLabelX=layout.rightAxisLabelX;
ctx.fillStyle='#333';ctx.font=xyTickFont+'px Arial';
ctx.textAlign='center';ctx.textBaseline='top';
for(var ti=0;ti<xTicks.length;ti++){ctx.fillText(xyFmt(xTicks[ti]),mapXp(xTicks[ti]),mt+ph+4);}
ctx.textAlign='right';ctx.textBaseline='middle';
for(var ti=0;ti<yTicks.length;ti++){ctx.fillText(xyFmt(yTicks[ti]),ml-4,mapYp(yTicks[ti]));}
if(hasSec&&secR){
ctx.fillStyle='#F44336';ctx.textAlign='left';
for(var ti=0;ti<secYTicks.length;ti++){ctx.fillText(xyFmt(secYTicks[ti]),ml+pw+4,mapYs(secYTicks[ti]));}
}
// Axis labels from global inputs
var xlbl=document.getElementById('xy-xname')?document.getElementById('xy-xname').value||'X':'X';
var ylbl=document.getElementById('xy-yname')?document.getElementById('xy-yname').value||'Y':'Y';
ctx.fillStyle='#555';ctx.font='bold '+xyAxisTitleFont+'px Arial';
ctx.textAlign='center';ctx.textBaseline='top';
ctx.fillText(xlbl,ml+pw/2,mt+ph+22);
ctx.save();ctx.translate(leftAxisLabelX,mt+ph/2);ctx.rotate(-Math.PI/2);
ctx.textBaseline='middle';ctx.fillText(ylbl,0,0);ctx.restore();
if(hasSec){var sylbl=document.getElementById('xy-syname')?document.getElementById('xy-syname').value||'Y (R)':'Y (R)';ctx.save();ctx.fillStyle='#F44336';ctx.font='bold '+xyAxisTitleFont+'px Arial';
ctx.translate(rightAxisLabelX,mt+ph/2);ctx.rotate(Math.PI/2);
ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(sylbl,0,0);ctx.restore();}
// Draw curves - CLIPPED, with secondary axis support
var xyAnimHighlights=[];
ctx.save();ctx.beginPath();ctx.rect(ml,mt,pw,ph);ctx.clip();
xyCurves.forEach(function(c,ci){
if(!xyIsCurveVisible(c))return;
var col=c.color||CURVE_COLORS[ci%CURVE_COLORS.length];
var pts=c.data;if(pts.length===0)return;
var isSec=(c.axis==='secondary'&&secR);
function mapX(v){return ml+(v-rng.xmin)/(rng.xmax-rng.xmin)*pw;}
function mapY(v){return isSec?mapYs(v):mapYp(v);}
if(pts.length>1){
ctx.strokeStyle=col;ctx.lineWidth=1.5;
ctx.beginPath();
var sorted=pts.slice().sort(function(a,b){return a[0]-b[0];});
ctx.moveTo(mapX(sorted[0][0]),mapY(sorted[0][1]));
for(var j=1;j<sorted.length;j++){ctx.lineTo(mapX(sorted[j][0]),mapY(sorted[j][1]));}
ctx.stroke();
}
pts.forEach(function(p,pi){
var px=mapX(p[0]),py=mapY(p[1]);
ctx.beginPath();ctx.arc(px,py,4,0,Math.PI*2);
var hi=(xyAnimIndex>=0&&pts.length===SL.length&&pi===xyAnimIndex);
ctx.globalAlpha=1;
ctx.fillStyle=hi?'#FFD600':'#fff';ctx.fill();
ctx.strokeStyle=col;ctx.lineWidth=2;ctx.stroke();
if(hi){
ctx.beginPath();ctx.arc(px,py,6.5,0,Math.PI*2);
ctx.strokeStyle='#FFD600';ctx.lineWidth=2;ctx.stroke();
xyAnimHighlights.push({curve:c,point:p,x:px,y:py});
}
});
});
ctx.restore();
var xyInfoOccupied=[];
xyDrawAnimHighlightInfo(ctx,ml,mt,pw,ph,xyAnimHighlights,xyInfoOccupied);
xyDrawPinned(ctx,ml,mt,pw,ph,priR,secR,xyInfoOccupied);
// Legend
var leg=document.getElementById('xy-legend');
var lm=xyGetLegendMetrics();
var xyLegendFont=lm.font;
var xyLegendDot=lm.dot;
var xyLegendGap=lm.gap;
var xyLegendItemGap=lm.itemGap;
var xyLegendBorder=lm.border;
if(leg){
leg.style.fontSize=xyLegendFont+'px';
leg.style.gap=xyLegendGap+'px';
leg.innerHTML='';
xyCurves.forEach(function(c,ci){
if(!xyIsCurveVisible(c))return;
var col=c.color||CURVE_COLORS[ci%CURVE_COLORS.length];
var d=document.createElement('div');d.className='xy-legend-item';
d.style.fontSize=xyLegendFont+'px';
d.style.gap=xyLegendItemGap+'px';
d.innerHTML='<span style="width:'+xyLegendDot+'px;height:'+xyLegendDot+'px;border-radius:50%;border:'+xyLegendBorder+'px solid '+col+';background:#fff;display:inline-block;flex:0 0 auto"></span><span>'+c.name+(c.axis==='secondary'?' (R)':'')+'</span>';
leg.appendChild(d);
});
}
}

function xyFmt(v){
if(v===undefined||v===null||!isFinite(v))return String(v);
if(xyValueFormat==='float'){
var dec=Math.max(0,Math.min(8,xyFloatLevels||0));
var s=Number(v).toFixed(dec);
// Keep fixed decimals so the Levels slider affects every axis label consistently.
if(Number(s)===0)return dec>0?('0.'+'0'.repeat(dec)):'0';
return s;
}
return Number(v).toExponential(1);
}

function xyAddCurve(){
var idx=xyCurves.length;
var c={name:'Curve '+(idx+1),xlabel:'X',ylabel:'Y',color:CURVE_COLORS[idx%CURVE_COLORS.length],data:[[0,0]],axis:'primary'};
xyCurves.push(c);
xyStartEdit(idx);
}

function xyDeriv3PointAtX(x0,y0,x1,y1,x2,y2,x){
var d0=(x0-x1)*(x0-x2);
var d1=(x1-x0)*(x1-x2);
var d2=(x2-x0)*(x2-x1);
if(Math.abs(d0)<1e-30||Math.abs(d1)<1e-30||Math.abs(d2)<1e-30)return null;
var l0=(2*x-x1-x2)/d0;
var l1=(2*x-x0-x2)/d1;
var l2=(2*x-x0-x1)/d2;
var v=y0*l0+y1*l1+y2*l2;
if(!isFinite(v))return null;
return v;
}

function xySafeDiff(xa,ya,xb,yb){
var dx=xb-xa;
if(Math.abs(dx)<1e-30)return null;
var v=(yb-ya)/dx;
return isFinite(v)?v:null;
}

function xyNormalizeDerivativeData(srcData){
if(!srcData||srcData.length===0)return null;
var pts=[];
for(var i=0;i<srcData.length;i++){
var p=srcData[i];
if(!p||p.length<2)continue;
var x=Number(p[0]),y=Number(p[1]);
if(!isFinite(x)||!isFinite(y))continue;
pts.push([x,y]);
}
if(pts.length<3)return null;
pts.sort(function(a,b){return a[0]-b[0];});
var merged=[];
var i0=0;
while(i0<pts.length){
var x0=pts[i0][0],sumY=0,cnt=0,j=i0;
while(j<pts.length&&Math.abs(pts[j][0]-x0)<1e-12){sumY+=pts[j][1];cnt++;j++;}
merged.push([x0,sumY/Math.max(1,cnt)]);
i0=j;
}
if(merged.length<3)return null;
return merged;
}

function xyComputeDerivativeData(srcData){
var data=xyNormalizeDerivativeData(srcData);
if(!data||data.length<3)return null;
var n=data.length;
var out=new Array(n);
for(var i=0;i<n;i++){
var x=data[i][0],y=data[i][1];
if(!isFinite(x)||!isFinite(y))return null;
var d=null;
if(i===0){
var p0=data[0],p1=data[1],p2=data[2];
d=xyDeriv3PointAtX(p0[0],p0[1],p1[0],p1[1],p2[0],p2[1],p0[0]);
if(d===null)d=xySafeDiff(p0[0],p0[1],p1[0],p1[1]);
}else if(i===n-1){
var q0=data[n-3],q1=data[n-2],q2=data[n-1];
d=xyDeriv3PointAtX(q0[0],q0[1],q1[0],q1[1],q2[0],q2[1],q2[0]);
if(d===null)d=xySafeDiff(q1[0],q1[1],q2[0],q2[1]);
}else{
var a=data[i-1],b=data[i],c=data[i+1];
d=xyDeriv3PointAtX(a[0],a[1],b[0],b[1],c[0],c[1],b[0]);
if(d===null)d=xySafeDiff(a[0],a[1],c[0],c[1]);
}
if(d===null||!isFinite(d))return null;
out[i]=[x,d];
}
return out;
}

function xyEscapeHtml(text){
var s=(text===undefined||text===null)?'':String(text);
return s.split('&').join('&amp;').split('<').join('&lt;').split('>').join('&gt;').split('"').join('&quot;');
}

function xyForecastFormatNumber(v){
if(v===undefined||v===null||!isFinite(v))return String(v);
if(v===0)return '0';
var av=Math.abs(v);
if(av>=1e4||av<1e-4)return Number(v).toExponential(6);
var s=Number(v).toFixed(6);
while(s.indexOf('.')>=0&&(s.charAt(s.length-1)==='0'||s.charAt(s.length-1)==='.')){
if(s.charAt(s.length-1)==='.'){s=s.slice(0,-1);break;}
s=s.slice(0,-1);
}
if(s==='-0')s='0';
return s;
}

function getForecastDialogFormat(box){
return (box&&box.forecastDialogFormat==='exp')?'exp':'float';
}

function formatForecastDialogValue(v,format,decimals){
if(v===undefined||v===null||!isFinite(v))return String(v);
var d=parseInt(decimals,10);
if(!isFinite(d))d=6;
d=Math.max(0,Math.min(10,d));
if((format==='exp')||String(format).toLowerCase()==='exponential'){
return Number(v).toExponential(d);
}
var s=Number(v).toFixed(d);
if(Number(s)===0)return d>0?('0.'+'0'.repeat(d)):'0';
return s;
}

function xyForecastParseValue(raw){
var txt=(raw===undefined||raw===null)?'':String(raw).trim();
if(!txt)return null;
txt=txt.split(',').join('.');
var v=Number(txt);
return isFinite(v)?v:null;
}

function xyNormalizeForecastData(srcData){
if(!srcData||srcData.length===0)return null;
var pts=[];
for(var i=0;i<srcData.length;i++){
var p=srcData[i];
if(!p||p.length<2)continue;
var x=Number(p[0]),y=Number(p[1]);
if(!isFinite(x)||!isFinite(y))continue;
pts.push([x,y]);
}
return pts.length>=2?pts:null;
}

function xyForecastSafeColor(color,fallback){
var c=(color===undefined||color===null)?'':String(color).trim();
if(/^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(c))return c;
if(/^rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+(?:\s*,\s*(?:0|1|0?\.\d+))?\s*\)$/.test(c))return c;
return fallback||'#8E24AA';
}

function xyForecastColorToRgb(color){
var c=xyForecastSafeColor(color,'');
var m3=c.match(/^#([0-9a-fA-F]{3})$/);
if(m3){
return {
r:parseInt(m3[1].charAt(0)+m3[1].charAt(0),16),
g:parseInt(m3[1].charAt(1)+m3[1].charAt(1),16),
b:parseInt(m3[1].charAt(2)+m3[1].charAt(2),16)
};
}
var m6=c.match(/^#([0-9a-fA-F]{6})$/);
if(m6){
return {
r:parseInt(m6[1].slice(0,2),16),
g:parseInt(m6[1].slice(2,4),16),
b:parseInt(m6[1].slice(4,6),16)
};
}
var mrgb=c.match(/^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i);
if(mrgb){
return {
r:Math.max(0,Math.min(255,parseInt(mrgb[1],10))),
g:Math.max(0,Math.min(255,parseInt(mrgb[2],10))),
b:Math.max(0,Math.min(255,parseInt(mrgb[3],10)))
};
}
return null;
}

function xyForecastTextColorForBg(color){
var rgb=xyForecastColorToRgb(color);
if(!rgb)return '#fff';
var lum=(0.299*rgb.r+0.587*rgb.g+0.114*rgb.b)/255;
return lum>0.65?'#111':'#fff';
}

function xyForecastGetCurveColor(curve,idx){
return xyForecastSafeColor(curve&&curve.color?curve.color:CURVE_COLORS[idx%CURVE_COLORS.length],'#8E24AA');
}

function xyForecastModeLabel(mode){
if(mode==='extrapolate-high')return 'Multipole extrapolation (high end)';
if(mode==='extrapolate-low')return 'Multipole extrapolation (low end)';
return 'Multipole interpolation';
}

function xyForecastBuildSignal(data,sourceAxisKey){
if(!data||data.length<2)return null;
var srcPos=(sourceAxisKey==='y')?1:0;
var dstPos=(srcPos===0)?1:0;
var signal=[],maxi=-Infinity,mini=Infinity;
for(var i=0;i<data.length;i++){
var p=data[i];
if(!p||p.length<2)continue;
var x=Number(p[0]),y=Number(p[1]),src=Number(p[srcPos]),dst=Number(p[dstPos]);
if(!isFinite(x)||!isFinite(y)||!isFinite(src)||!isFinite(dst))continue;
signal.push({x:x,y:y,source:src,target:dst});
if(src>maxi)maxi=src;
if(src<mini)mini=src;
}
if(signal.length<2||!isFinite(maxi)||!isFinite(mini))return null;
return {signal:signal,count:signal.length,maxi:maxi,mini:mini,increasing:(signal[signal.length-1].source>signal[0].source)};
}

function xyForecastFindFallbackSegment(signal,forecastSourceValue){
var best=-1,bestDiff=Infinity;
for(var i=0;i<signal.length-1;i++){
var a=signal[i],b=signal[i+1];
if(Math.abs(b.source-a.source)<1e-30)continue;
var diff=Math.min(Math.abs(forecastSourceValue-a.source),Math.abs(forecastSourceValue-b.source));
if(diff<bestDiff){best=i;bestDiff=diff;}
}
return best;
}

function xyForecastMultipole(data,sourceAxisKey,forecastSourceValue){
var pack=xyForecastBuildSignal(data,sourceAxisKey);
if(!pack)return null;
var signal=pack.signal,n=signal.length,idx=-1,mode='interpolate';
if(forecastSourceValue>=pack.maxi&&pack.increasing){
idx=n-2;mode='extrapolate-high';
}else if(forecastSourceValue>=pack.maxi&&!pack.increasing){
idx=0;mode='extrapolate-high';
}else if(forecastSourceValue<=pack.mini&&pack.increasing){
idx=0;mode='extrapolate-low';
}else if(forecastSourceValue<=pack.mini&&!pack.increasing){
idx=n-2;mode='extrapolate-low';
}else{
for(var i=0;i<n-1;i++){
var s0=signal[i].source,s1=signal[i+1].source;
if((forecastSourceValue>s0&&forecastSourceValue<=s1)||(forecastSourceValue<s0&&forecastSourceValue>=s1)){
idx=i;
break;
}
}
if(idx<0)idx=xyForecastFindFallbackSegment(signal,forecastSourceValue);
}
if(idx<0||idx>=n-1)return null;
var a=signal[idx],b=signal[idx+1];
if(Math.abs(b.source-a.source)<1e-30){
idx=xyForecastFindFallbackSegment(signal,forecastSourceValue);
if(idx<0||idx>=n-1)return null;
a=signal[idx];b=signal[idx+1];
if(Math.abs(b.source-a.source)<1e-30)return null;
}
var targetValue=a.target+(forecastSourceValue-a.source)*(b.target-a.target)/(b.source-a.source);
if(!isFinite(targetValue))return null;
return {
count:pack.count,
mode:mode,
methodLabel:xyForecastModeLabel(mode),
segment:{a:{x:a.x,y:a.y,source:a.source,target:a.target},b:{x:b.x,y:b.y,source:b.source,target:b.target}},
forecastSourceValue:forecastSourceValue,
forecastX:(sourceAxisKey==='x')?forecastSourceValue:targetValue,
forecastY:(sourceAxisKey==='x')?targetValue:forecastSourceValue
};
}

function xyGetSelectedForecastCurveData(){
if(xyCurves.length===0){alert('No curves available.');return null;}
if(xySelectedIdx<0||xySelectedIdx>=xyCurves.length){
alert('Please select one curve from the list before using Forecast.');
return null;
}
if(xyEditingIdx===xySelectedIdx)xyCommitEditingCurveDraft();
var curve=xyCurves[xySelectedIdx];
var data=xyNormalizeForecastData(curve?curve.data:null);
if(!curve||!data){
alert('Selected curve needs at least 2 valid points for Forecast.');
return null;
}
return {curve:curve,data:data,index:xySelectedIdx,color:xyForecastGetCurveColor(curve,xySelectedIdx)};
}

function xyRefreshForecastFieldLabels(){
var container=document.getElementById('xy-forecast-fields');
if(!container)return;
var axisEl=document.getElementById('xy-forecast-axis');
var axisLetter=(axisEl&&axisEl.value==='y')?'Y':'X';
var rows=container.querySelectorAll('.xy-forecast-row');
for(var i=0;i<rows.length;i++){
var row=rows[i];
var lbl=row.querySelector('label');
var inp=row.querySelector('input.xy-forecast-input');
var rm=row.querySelector('.xy-forecast-remove');
if(lbl)lbl.textContent='Forecast '+(i+1)+' ('+axisLetter+')';
if(inp)inp.placeholder='Enter forecast '+axisLetter+' value';
if(rm)rm.style.display=(rows.length>1)?'inline-block':'none';
}
}

function xyAddForecastField(value){
var container=document.getElementById('xy-forecast-fields');
if(!container)return null;
var row=document.createElement('div');
row.className='xy-forecast-row';
var field=document.createElement('div');
field.className='xy-modal-field';
var lbl=document.createElement('label');
lbl.textContent='Forecast';
var inp=document.createElement('input');
inp.type='text';
inp.className='xy-forecast-input';
inp.value=(value!==undefined&&value!==null)?String(value):'';
inp.onkeyup=function(event){if(event.key==='Enter')xyRunForecast();};
field.appendChild(lbl);
field.appendChild(inp);
row.appendChild(field);
var rm=document.createElement('button');
rm.type='button';
rm.className='xy-btn xy-btn-del xy-forecast-remove';
rm.textContent='X';
rm.onclick=function(){
if(container.children.length<=1){
inp.value='';
inp.focus();
return;
}
container.removeChild(row);
xyRefreshForecastFieldLabels();
};
row.appendChild(rm);
container.appendChild(row);
xyRefreshForecastFieldLabels();
return inp;
}

function xyResetForecastFields(){
var container=document.getElementById('xy-forecast-fields');
if(!container)return;
container.innerHTML='';
xyAddForecastField('');
}

function xyForecastAxisNameFromUi(inputId,fallback){
var el=document.getElementById(inputId);
var txt=el?String(el.value||'').trim():'';
if(txt)return txt;
return fallback;
}

function xyForecastGetDisplayAxisLabels(curve,axisKey){
var isSecondary=!!(curve&&curve.axis==='secondary');
var xAxisLabel=xyForecastAxisNameFromUi('xy-xname',(curve&&curve.xlabel)||'X');
var primaryAxisLabel=xyForecastAxisNameFromUi('xy-yname',(!isSecondary&&(curve&&curve.ylabel))?curve.ylabel:'Y');
var secondaryAxisLabel=xyForecastAxisNameFromUi('xy-syname',(isSecondary&&(curve&&curve.ylabel))?curve.ylabel:'Y (R)');
var curveAxisLabel=isSecondary?secondaryAxisLabel:primaryAxisLabel;
return {
xAxisLabel:xAxisLabel,
primaryAxisLabel:primaryAxisLabel,
secondaryAxisLabel:secondaryAxisLabel,
curveAxisLabel:curveAxisLabel,
sourceAxisLabel:(axisKey==='y')?curveAxisLabel:xAxisLabel,
targetAxisLabel:(axisKey==='y')?xAxisLabel:curveAxisLabel
};
}

function xyForecastGetSecondaryRowLabel(sec,result,totalSecondary){
var base=(result&&result.secondaryAxisLabel)?result.secondaryAxisLabel:((sec&&sec.ylabel)?sec.ylabel:'Y (R)');
base=String(base||'').trim()||'Y (R)';
if(totalSecondary>1&&sec&&sec.name){
return base+' ('+sec.name+')';
}
return base;
}

function xyCollectForecastInputValues(){
var container=document.getElementById('xy-forecast-fields');
if(!container)return null;
var inputs=container.querySelectorAll('input.xy-forecast-input');
var out=[];
for(var i=0;i<inputs.length;i++){
var txt=inputs[i].value!==undefined?String(inputs[i].value).trim():'';
if(!txt)continue;
var v=xyForecastParseValue(txt);
if(v===null){
alert('Enter a valid number in Forecast '+(i+1)+'.');
return null;
}
out.push({index:i+1,value:v});
}
if(out.length===0){
alert('Add at least one Forecast value before running Forecast.');
return null;
}
return out;
}

function xyUpdateForecastDialogText(curveOverride){
var curve=curveOverride;
if(!curve&&xySelectedIdx>=0&&xySelectedIdx<xyCurves.length)curve=xyCurves[xySelectedIdx];
var curveInfo=document.getElementById('xy-forecast-curve-info');
var axisNote=document.getElementById('xy-forecast-axis-note');
var axisEl=document.getElementById('xy-forecast-axis');
var axisKey=(axisEl&&axisEl.value==='y')?'y':'x';
var axisLabels=xyForecastGetDisplayAxisLabels(curve,axisKey);
var sourceLabel=axisLabels.sourceAxisLabel;
var targetLabel=axisLabels.targetAxisLabel;
var curveName=curve&&curve.name?curve.name:((xySelectedIdx>=0)?('Curve '+(xySelectedIdx+1)):'Selected curve');
var axisSide=(curve&&curve.axis==='secondary')?('Secondary '+axisLabels.secondaryAxisLabel+' axis (R)'):('Primary '+axisLabels.primaryAxisLabel+' axis (L)');
if(curveInfo)curveInfo.textContent='Curve: '+curveName+' | '+axisSide;
if(axisNote)axisNote.textContent='All Forecast fields use "'+sourceLabel+'" as the reference and estimate "'+targetLabel+'" with the Multipole interpolation/extrapolation logic along the selected curve.';
xyRefreshForecastFieldLabels();
}

function xyOpenForecastDialog(){
var info=xyGetSelectedForecastCurveData();
if(!info)return;
xyForecastLastResult=null;
xyCloseForecastResultDialog();
xyResetForecastFields();
xyUpdateForecastDialogText(info.curve);
var ov=document.getElementById('xy-forecast-overlay');
if(ov)ov.style.display='flex';
var firstInput=document.querySelector('#xy-forecast-fields input.xy-forecast-input');
if(firstInput)firstInput.focus();
}

function xyCloseForecastDialog(){
var ov=document.getElementById('xy-forecast-overlay');
if(ov)ov.style.display='none';
}

function xyCloseForecastResultDialog(){
var ov=document.getElementById('xy-forecast-result-overlay');
if(ov)ov.style.display='none';
}

function xyForecastGetSecondarySeries(excludeIdx){
var series=[],skipped=[];
for(var i=0;i<xyCurves.length;i++){
var c=xyCurves[i];
if(!c||c.axis!=='secondary'||i===excludeIdx)continue;
var data=xyNormalizeForecastData(c.data);
if(!data){skipped.push((c.name||('Curve '+(i+1)))+' (need at least 2 valid points)');continue;}
var probe=xyForecastMultipole(data,'x',data[0][0]);
if(!probe){skipped.push((c.name||('Curve '+(i+1)))+' (need valid X sequence for Multipole)');continue;}
series.push({
name:c.name||('Curve '+(i+1)),
color:xyForecastGetCurveColor(c,i),
data:data,
ylabel:c.ylabel||'Y',
xlabel:c.xlabel||'X'
});
}
return {series:series,skipped:skipped};
}

function xyForecastEvaluateSecondaryAtX(forecastX,secondarySeries){
var results=[];
for(var i=0;i<secondarySeries.length;i++){
var it=secondarySeries[i];
var calc=xyForecastMultipole(it.data,'x',forecastX);
if(!calc)continue;
results.push({
name:it.name,
color:it.color,
forecastX:calc.forecastX,
forecastY:calc.forecastY,
mode:calc.mode,
methodLabel:calc.methodLabel,
segment:calc.segment,
count:calc.count,
ylabel:it.ylabel,
xlabel:it.xlabel
});
}
return results;
}

function xyForecastResultRowHtml(label,value,color){
var bg=xyForecastSafeColor(color,'#8E24AA');
var fg=xyForecastTextColorForBg(bg);
return '<div class="xy-result-row"><span class="xy-result-chip" style="background:'+bg+';color:'+fg+'">'+xyEscapeHtml(label)+'</span><span>'+xyEscapeHtml(value)+'</span></div>';
}

function xyForecastResultForecastRowHtml(sourceAxisLabel,sourceValue,targetAxisLabel,targetValue,color){
var bg=xyForecastSafeColor(color,'#8E24AA');
var fg=xyForecastTextColorForBg(bg);
return '<div class="xy-result-row"><span class="xy-result-chip" style="background:'+bg+';color:'+fg+'">Forecast</span><span>'+xyEscapeHtml(sourceAxisLabel)+' = '+xyForecastFormatNumber(sourceValue)+' | <span class="xy-result-value-highlight">'+xyEscapeHtml(targetAxisLabel)+' = '+xyForecastFormatNumber(targetValue)+'</span></span></div>';
}

function xyForecastResultBlockHtml(title,color,rows){
var bg=xyForecastSafeColor(color,'#8E24AA');
return '<div class="xy-result-block" style="border-left-color:'+bg+'"><div class="xy-result-block-title" style="color:'+bg+'">'+xyEscapeHtml(title)+'</div>'+rows.join('')+'</div>';
}

function xyRenderForecastResult(result){
var body=document.getElementById('xy-forecast-result-body');
if(!body||!result)return;
var html=[];
html.push('<div><span class="xy-result-chip" style="min-width:0;background:#6A1B9A;color:#fff">Forecast Result</span></div>');
for(var i=0;i<result.entries.length;i++){
var entry=result.entries[i];
var mainRows=[];
mainRows.push(xyForecastResultRowHtml('Axis',result.sourceAxisLetter+' -> '+result.targetAxisLetter+' | '+result.axisCaption,result.curveColor));
var primaryTargetValue=(result.targetAxisLetter==='X')?entry.forecastX:entry.forecastY;
mainRows.push(xyForecastResultForecastRowHtml(result.sourceAxisLetter,entry.inputValue,result.targetAxisLetter,primaryTargetValue,result.curveColor));
html.push(xyForecastResultBlockHtml(result.curveName, result.curveColor, mainRows));
}
if(result.includeSecondary){
for(var ei=0;ei<result.entries.length;ei++){
var e=result.entries[ei];
if(e.secondary.length===0){
html.push(xyForecastResultBlockHtml('Secondary Axis','#757575',[xyForecastResultRowHtml('Axis','X -> Y | Secondary Y axis (R)','#757575'),xyForecastResultRowHtml('Forecast','No secondary-axis result available for this forecast value.','#757575')]));
continue;
}
for(var si=0;si<e.secondary.length;si++){
var sec=e.secondary[si];
var secRows=[];
secRows.push(xyForecastResultRowHtml('Axis','X -> Y | Secondary Y axis (R)',sec.color));
secRows.push(xyForecastResultForecastRowHtml('X',e.forecastX,'Y',sec.forecastY,sec.color));
html.push(xyForecastResultBlockHtml(sec.name, sec.color, secRows));
}
}
}
body.innerHTML=html.join('');
}

function xyBuildForecastDialogText(result,format,decimals){
if(!result)return 'Forecast result unavailable';
var lines=[];
for(var i=0;i<result.entries.length;i++){
var entry=result.entries[i];
lines.push('');
lines.push(result.curveName);
lines.push((result.sourceAxisLabel||result.sourceAxisLetter||'X')+': '+formatForecastDialogValue(entry.inputValue,format,decimals));
lines.push((result.targetAxisLabel||result.targetAxisLetter||'Y')+': '+formatForecastDialogValue((result.targetAxisLetter==='X')?entry.forecastX:entry.forecastY,format,decimals));
if(result.includeSecondary&&Array.isArray(entry.secondary)&&entry.secondary.length>0){
for(var si=0;si<entry.secondary.length;si++){
var sec=entry.secondary[si];
lines.push(xyForecastGetSecondaryRowLabel(sec,result,entry.secondary.length)+': '+formatForecastDialogValue(sec.forecastY,format,decimals));
}
}
}
return lines.join('\\n');
}

function xyForecastDialogRowHtml(label,value,color){
var bg=xyForecastSafeColor(color,'#8E24AA');
var fg=xyForecastTextColorForBg(bg);
return '<div class="dlg-rich-row" style="--dlg-accent:'+bg+'"><span class="dlg-rich-tag" style="background:'+bg+';color:'+fg+'">'+xyEscapeHtml(label)+'</span><span class="dlg-rich-val">'+xyEscapeHtml(value)+'</span></div>';
}

function xyForecastDialogNumberRowHtml(label,value,color,format,decimals,highlight){
var bg=xyForecastSafeColor(color,'#8E24AA');
var fg=xyForecastTextColorForBg(bg);
var valHtml=xyEscapeHtml(formatForecastDialogValue(value,format,decimals));
if(highlight)valHtml='<span class="dlg-rich-result">'+valHtml+'</span>';
return '<div class="dlg-rich-row" style="--dlg-accent:'+bg+'"><span class="dlg-rich-tag" style="background:'+bg+';color:'+fg+'">'+xyEscapeHtml(label)+'</span><span class="dlg-rich-val">'+valHtml+'</span></div>';
}

function xyForecastDialogSectionHtml(title,color,rows){
var bg=xyForecastSafeColor(color,'#8E24AA');
return '<div class="dlg-rich-sec" style="--dlg-accent:'+bg+'"><div class="dlg-rich-sec-title">'+xyEscapeHtml(title)+'</div>'+rows.join('')+'</div>';
}

function xyBuildForecastDialogHtml(result,format,decimals){
if(!result)return '';
var html=[];
for(var i=0;i<result.entries.length;i++){
var entry=result.entries[i];
var mainRows=[];
mainRows.push(xyForecastDialogNumberRowHtml(result.sourceAxisLabel||result.sourceAxisLetter||'X',entry.inputValue,result.curveColor,format,decimals,false));
mainRows.push(xyForecastDialogNumberRowHtml(result.targetAxisLabel||result.targetAxisLetter||'Y',(result.targetAxisLetter==='X')?entry.forecastX:entry.forecastY,result.curveColor,format,decimals,true));
if(result.includeSecondary&&Array.isArray(entry.secondary)&&entry.secondary.length>0){
for(var si=0;si<entry.secondary.length;si++){
var sec=entry.secondary[si];
mainRows.push(xyForecastDialogNumberRowHtml(xyForecastGetSecondaryRowLabel(sec,result,entry.secondary.length),sec.forecastY,sec.color||result.curveColor,format,decimals,true));
}
}
html.push(xyForecastDialogSectionHtml(result.curveName, result.curveColor, mainRows));
}
return html.join('');
}

function getForecastDialogDecimals(box){
var n=parseInt(box&&box.forecastDialogDecimals,10);
if(!isFinite(n))n=6;
return Math.max(0,Math.min(10,n));
}

function isForecastDialogBox(box){
return !!(box&&box.forecastDialogData&&typeof box.forecastDialogData==='object');
}

function buildForecastDialogClipboardRows(box){
if(!isForecastDialogBox(box))return [];
var result=box.forecastDialogData;
if(!result||!Array.isArray(result.entries)||result.entries.length===0)return [];
var format=getForecastDialogFormat(box);
var decimals=getForecastDialogDecimals(box);
var rows=[['Source Axis','Source Value','Target Axis','Target Value']];
for(var i=0;i<result.entries.length;i++){
var entry=result.entries[i];
if(!entry)continue;
var primaryTargetValue=(result.targetAxisLetter==='X')?entry.forecastX:entry.forecastY;
rows.push([
result.sourceAxisLabel||result.sourceAxisLetter||'X',
formatForecastDialogValue(entry.inputValue,format,decimals),
result.targetAxisLabel||result.targetAxisLetter||'Y',
formatForecastDialogValue(primaryTargetValue,format,decimals)
]);
if(result.includeSecondary){
if(Array.isArray(entry.secondary)&&entry.secondary.length>0){
for(var si=0;si<entry.secondary.length;si++){
var sec=entry.secondary[si];
if(!sec)continue;
rows.push([
(result.xAxisLabel||'X'),
formatForecastDialogValue(entry.forecastX,format,decimals),
xyForecastGetSecondaryRowLabel(sec,result,entry.secondary.length),
formatForecastDialogValue(sec.forecastY,format,decimals)
]);
}
}
}
}
return rows;
}

function buildForecastDialogClipboardText(box){
var rows=buildForecastDialogClipboardRows(box);
if(rows.length===0)return '';
return rows.map(function(row){
return row.map(function(cell){
return String(cell===undefined||cell===null?'':cell).replace(/\\r?\\n/g,' ');
}).join('\\t');
}).join('\\n');
}

function copyForecastDialogBoxData(box){
if(!isForecastDialogBox(box)){
document.getElementById('st').textContent='Copy is only available for Forecast Dialog Boxes';
return;
}
var rows=buildForecastDialogClipboardRows(box);
if(rows.length<=1){
document.getElementById('st').textContent='Forecast Dialog has no data to copy';
return;
}
var text=buildForecastDialogClipboardText(box);
function okMsg(){
document.getElementById('st').textContent='Forecast Dialog copied ('+(rows.length-1)+' row'+((rows.length-1)===1?'':'s')+')';
}
try{
navigator.clipboard.writeText(text).then(okMsg).catch(function(){xyFallbackCopy(text);});
}catch(e){xyFallbackCopy(text);}
}

function refreshForecastDialogBoxContent(box){
if(!box||!box.body||!isForecastDialogBox(box))return;
var format=getForecastDialogFormat(box);
var decimals=getForecastDialogDecimals(box);
box.forecastDialogFormat=format;
box.forecastDialogDecimals=decimals;
box.text=xyBuildForecastDialogText(box.forecastDialogData,format,decimals);
box.body.className='dialog-body dialog-body-rich';
box.richHtml=xyBuildForecastDialogHtml(box.forecastDialogData,format,decimals);
box.body.innerHTML=box.richHtml;
refreshDialogCopyButton(box);
syncDialogTextSnapshot(box);
syncDialogBoxSize(box);
if(dialogFontBoxId===box.id)syncDialogFontPopup(box);
}

function xyApplyForecastDialogBoxContent(box,result){
if(!box||!box.body||!result)return;
box.readOnly=true;
box.allowRichEdit=false;
box.forecastDialogData=cfgClone(result);
box.forecastDialogFormat=getForecastDialogFormat(box);
box.forecastDialogDecimals=getForecastDialogDecimals(box);
box.text=xyBuildForecastDialogText(result,box.forecastDialogFormat,box.forecastDialogDecimals);
box.body.className='dialog-body dialog-body-rich';
box.richHtml=xyBuildForecastDialogHtml(result,box.forecastDialogFormat,box.forecastDialogDecimals);
box.body.innerHTML=box.richHtml;
refreshDialogCopyButton(box);
refreshDialogEditButton(box);
applyDialogTextStyle(box);
}

function xyCreateForecastDialogBox(){
if(!xyForecastLastResult){alert('Run Forecast first.');return;}
if(!cvEl){alert('Viewer canvas not ready.');return;}
var cb=document.getElementById('dlg-on');
if(cb&&!cb.checked){
cb.checked=true;
tgDialogMode(true);
}
dialogAddArmed=false;
hideDialogPreview();
var rect=cvEl.getBoundingClientRect();
var clientX=rect.left+Math.max(36,Math.min(rect.width-36,rect.width*0.62));
var clientY=rect.top+Math.max(36,Math.min(rect.height-36,rect.height*0.22));
var box=createDialogBoxAtClient(clientX,clientY);
if(!box){
alert('Could not create Dialog Box inside the viewer area.');
return;
}
xyApplyForecastDialogBoxContent(box,xyForecastLastResult);
syncDialogBoxSize(box);
setDialogEditing(box,false);
updateDialogBoxesVisuals();
document.getElementById('st').textContent='Forecast Dialog Box created';
}

function xyRunForecast(){
var info=xyGetSelectedForecastCurveData();
if(!info)return;
var axisEl=document.getElementById('xy-forecast-axis');
var axisKey=(axisEl&&axisEl.value==='y')?'y':'x';
var sourceAxisLetter=(axisKey==='y')?'Y':'X';
var targetAxisLetter=(axisKey==='y')?'X':'Y';
var axisLabels=xyForecastGetDisplayAxisLabels(info.curve,axisKey);
var sourceAxisLabel=axisLabels.sourceAxisLabel;
var targetAxisLabel=axisLabels.targetAxisLabel;
var inputs=xyCollectForecastInputValues();
if(!inputs)return;
var includeSecondary=!!(document.getElementById('xy-forecast-secondary')&&document.getElementById('xy-forecast-secondary').checked);
var secondaryPack=includeSecondary?xyForecastGetSecondarySeries(info.index):{series:[],skipped:[]};
var entries=[];
for(var i=0;i<inputs.length;i++){
var srcVal=inputs[i].value;
var calc=xyForecastMultipole(info.data,axisKey,srcVal);
if(!calc)continue;
entries.push({
label:'Forecast '+inputs[i].index,
sourceAxisLetter:sourceAxisLetter,
inputValue:srcVal,
forecastX:calc.forecastX,
forecastY:calc.forecastY,
mode:calc.mode,
methodLabel:calc.methodLabel,
segment:calc.segment,
count:calc.count,
secondary:includeSecondary?xyForecastEvaluateSecondaryAtX(calc.forecastX,secondaryPack.series):[]
});
}
if(entries.length===0){
alert('Forecast could not be calculated for the entered values.');
return;
}
xyForecastLastResult={
curveName:info.curve.name||('Curve '+(info.index+1)),
curveColor:info.color,
curveAxis:(info.curve.axis==='secondary')?'secondary':'primary',
axisCaption:(info.curve.axis==='secondary')?'Secondary Y axis (R)':'Primary Y axis (L)',
sourceAxisLetter:sourceAxisLetter,
targetAxisLetter:targetAxisLetter,
sourceAxisLabel:sourceAxisLabel,
targetAxisLabel:targetAxisLabel,
xAxisLabel:axisLabels.xAxisLabel,
primaryAxisLabel:axisLabels.primaryAxisLabel,
secondaryAxisLabel:axisLabels.secondaryAxisLabel,
dataPointCount:info.data.length,
includeSecondary:includeSecondary,
entries:entries,
secondarySkipped:secondaryPack.skipped
};
xyRenderForecastResult(xyForecastLastResult);
xyCloseForecastDialog();
var ov=document.getElementById('xy-forecast-result-overlay');
if(ov)ov.style.display='flex';
document.getElementById('st').textContent='Forecast created for '+(info.curve.name||('Curve '+(info.index+1)));
}

function xyDerivativeCurve(){
if(xyCurves.length===0){alert('No curves available.');return;}
if(xySelectedIdx<0||xySelectedIdx>=xyCurves.length){
alert('Please select one curve from the list before using Derivative.');
return;
}
var refIdx=xySelectedIdx;
var ref=xyCurves[refIdx];
if(!ref||!ref.data||ref.data.length<3){
alert('Selected curve needs at least 3 points for second-order derivative.');
return;
}
var derivData=xyComputeDerivativeData(ref.data);
if(!derivData){
alert('Derivative could not be computed. Need at least 3 valid points with distinct X values.');
return;
}
var xLbl=ref.xlabel||'X';
var yLbl=ref.ylabel||'Y';
var dLbl='d('+yLbl+')/d('+xLbl+')';
var idx=xyCurves.length;
var dName=(ref.name||('Curve '+(refIdx+1)))+' - Derivative';
xyCurves.push({name:dName,xlabel:xLbl,ylabel:dLbl,color:CURVE_COLORS[idx%CURVE_COLORS.length],data:derivData,axis:'secondary'});
xySelectedIdx=idx;
xyEditingIdx=-1;
document.getElementById('xy-table-area').style.display='none';
xyClearCellSelection();
xyRefreshList();
drawPlot();
document.getElementById('st').textContent='Derivative curve created on Secondary Y axis (R)';
}

function xyStartEdit(idx){
if(idx<0||idx>=xyCurves.length)return;
xyEditingIdx=idx;xySelectedIdx=idx;
xyShowTable(xyCurves[idx]);
xyRefreshList();
xyRefreshHideButton();
}

function xyEditCurve(){
if(xySelectedIdx<0||xySelectedIdx>=xyCurves.length){
alert('Please select a curve from the list first.');return;
}
xyStartEdit(xySelectedIdx);
}

function xyDeleteCurve(){
if(xySelectedIdx<0||xySelectedIdx>=xyCurves.length){
alert('Please select a curve from the list first.');return;
}
if(!confirm('Delete "'+xyCurves[xySelectedIdx].name+'"?'))return;
var delIdx=xySelectedIdx;
var deletedAxis=(xyCurves[delIdx]&&xyCurves[delIdx].axis==='secondary')?'secondary':'primary';
xyCurves.splice(delIdx,1);
if(xyPinned&&xyPinned.length>0){
var next=[];
for(var i=0;i<xyPinned.length;i++){
var p=xyPinned[i];
if(p.curveIdx===delIdx)continue;
if(p.curveIdx>delIdx)p.curveIdx--;
next.push(p);
}
xyPinned=next;
}
var hasPrimaryAfterDelete=xyCurves.some(function(c){return c&&c.axis!=='secondary';});
if(deletedAxis!=='secondary'){
var uxMin=parseFloat(xyUserRange.xmin),uxMax=parseFloat(xyUserRange.xmax);
var uyMin=parseFloat(xyUserRange.ymin),uyMax=parseFloat(xyUserRange.ymax);
var badX=(xyUserRange.xmin!=='auto'&&xyUserRange.xmax!=='auto'&&isFinite(uxMin)&&isFinite(uxMax)&&uxMin>=uxMax);
var badY=(xyUserRange.ymin!=='auto'&&xyUserRange.ymax!=='auto'&&isFinite(uyMin)&&isFinite(uyMax)&&uyMin>=uyMax);
if(!hasPrimaryAfterDelete||badX||badY){
// If no primary curve remains (or manual range became invalid), clear stale primary ranges.
xyUserRange.xmin='auto';xyUserRange.xmax='auto';xyUserRange.ymin='auto';xyUserRange.ymax='auto';
xyAppliedRange.xmin='auto';xyAppliedRange.xmax='auto';xyAppliedRange.ymin='auto';xyAppliedRange.ymax='auto';
var xmn=document.getElementById('xy-xmin'),xmx=document.getElementById('xy-xmax');
var ymn=document.getElementById('xy-ymin'),ymx=document.getElementById('xy-ymax');
if(xmn)xmn.value='auto';if(xmx)xmx.value='auto';if(ymn)ymn.value='auto';if(ymx)ymx.value='auto';
var xst=document.getElementById('xy-xstep'),yst=document.getElementById('xy-ystep');
if(xst)xst.value='auto';if(yst)yst.value='auto';
}
}
var hasSecondaryAfterDelete=xyCurves.some(function(c){return c&&c.axis==='secondary';});
if(!hasSecondaryAfterDelete){
xySecUserRange.ymin='auto';xySecUserRange.ymax='auto';
xySecAppliedRange.ymin='auto';xySecAppliedRange.ymax='auto';
var symn=document.getElementById('xy-symin'),symx=document.getElementById('xy-symax'),syst=document.getElementById('xy-systep');
if(symn)symn.value='auto';if(symx)symx.value='auto';if(syst)syst.value='auto';
}
xySelectedIdx=-1;xyEditingIdx=-1;
document.getElementById('xy-table-area').style.display='none';
xyClearCellSelection();
xyRefreshList();
xyResizePlot();
xyUpdatePlotSize();
}

function xyShowTable(c){
document.getElementById('xy-table-area').style.display='block';
xyUpdatePlotSize();
document.getElementById('xy-curve-name').value=c.name;
if(c.axis==='secondary'){document.getElementById('xy-axis-sec').checked=true;}
else{document.getElementById('xy-axis-pri').checked=true;}
document.getElementById('xy-col-x').value=c.xlabel||'X';
document.getElementById('xy-col-y').value=c.ylabel||'Y';
document.getElementById('xy-th-x').textContent=c.xlabel||'X';
document.getElementById('xy-th-y').textContent=c.ylabel||'Y';
var tbody=document.getElementById('xy-tbody');
tbody.innerHTML='';
xyClearColSelection();
xyClearRowSelection();
xyClearCellSelection();
c.data.forEach(function(p,i){xyAddTableRow(p[0],p[1]);});
xyApplyColSelection();
var thx=document.getElementById('xy-th-x');
var thy=document.getElementById('xy-th-y');
if(thx){thx.onclick=function(){xyToggleColSelect('x');};thx.title='Click to select column';}
if(thy){thy.onclick=function(){xyToggleColSelect('y');};thy.title='Click to select column';}
xySetupCopyHotkey();
xyInitCellSelection();
// Update headers on label change
document.getElementById('xy-col-x').oninput=function(){document.getElementById('xy-th-x').textContent=this.value;};
document.getElementById('xy-col-y').oninput=function(){document.getElementById('xy-th-y').textContent=this.value;};
var tblArea=document.getElementById('xy-table-area');
tblArea.onpaste=function(e){
var clip=e.clipboardData||window.clipboardData;if(!clip)return;
var text=clip.getData('text');
if(text&&text.indexOf(String.fromCharCode(10))>=0){e.preventDefault();e.stopPropagation();xyParseAndFill(text);}
};
xyRefreshHideButton();
}

function xyApplyColSelection(){
var thx=document.getElementById('xy-th-x');
var thy=document.getElementById('xy-th-y');
if(thx)thx.classList.toggle('xy-col-sel',xySelCols.x);
if(thy)thy.classList.toggle('xy-col-sel',xySelCols.y);
var tbody=document.getElementById('xy-tbody');
if(!tbody)return;
var rows=tbody.querySelectorAll('tr');
for(var i=0;i<rows.length;i++){
var inputs=rows[i].querySelectorAll('input');
if(inputs[0])inputs[0].classList.toggle('xy-col-sel',xySelCols.x);
if(inputs[1])inputs[1].classList.toggle('xy-col-sel',xySelCols.y);
}
}

function xyToggleColSelect(col){
xyClearCellSelection();
if(col==='x')xySelCols.x=!xySelCols.x;
if(col==='y')xySelCols.y=!xySelCols.y;
xyApplyColSelection();
}

function xyClearColSelection(){
xySelCols.x=false;xySelCols.y=false;xyApplyColSelection();
}

function xyToggleRowSelect(tr){
if(!tr)return;
xyClearCellSelection();
tr.classList.toggle('xy-row-sel');
}

function xyClearRowSelection(){
var rows=document.getElementById('xy-tbody')?document.getElementById('xy-tbody').querySelectorAll('tr'):[];
rows.forEach(function(r){r.classList.remove('xy-row-sel');});
}

function xyGetCellPos(input){
var tbody=document.getElementById('xy-tbody');
if(!tbody||!input)return null;
var tr=input.closest('tr');
if(!tr)return null;
var rows=tbody.querySelectorAll('tr');
var row=-1;
for(var i=0;i<rows.length;i++){if(rows[i]===tr){row=i;break;}}
if(row<0)return null;
var col=parseInt(input.getAttribute('data-col'));
if(isNaN(col)){
var inputs=tr.querySelectorAll('input');
col=(inputs[0]===input)?0:1;
}
return{row:row,col:col};
}

function xyClearCellSelection(){
var tbody=document.getElementById('xy-tbody');
if(!tbody)return;
var sel=tbody.querySelectorAll('input.xy-cell-sel');
sel.forEach(function(inp){inp.classList.remove('xy-cell-sel');});
xyCellSel.active=false;
xyCellDrag=false;
}

function xyClearCellHighlight(){
var tbody=document.getElementById('xy-tbody');
if(!tbody)return;
var sel=tbody.querySelectorAll('input.xy-cell-sel');
sel.forEach(function(inp){inp.classList.remove('xy-cell-sel');});
}

function xyApplyCellSelection(){
var tbody=document.getElementById('xy-tbody');
if(!tbody)return;
xyClearCellHighlight();
if(!xyCellSel.active)return;
var rows=tbody.querySelectorAll('tr');
if(rows.length===0)return;
var r1=Math.max(0,Math.min(xyCellSel.startRow,xyCellSel.endRow));
var r2=Math.min(rows.length-1,Math.max(xyCellSel.startRow,xyCellSel.endRow));
var c1=Math.max(0,Math.min(xyCellSel.startCol,xyCellSel.endCol));
var c2=Math.min(1,Math.max(xyCellSel.startCol,xyCellSel.endCol));
for(var r=r1;r<=r2;r++){
var inputs=rows[r].querySelectorAll('input');
for(var c=c1;c<=c2;c++){
if(inputs[c])inputs[c].classList.add('xy-cell-sel');
}
}
}

function xyInitCellSelection(){
if(xyCellSelInit)return;
xyCellSelInit=true;
document.addEventListener('mouseup',function(){xyCellDrag=false;});
}

function xyCellMouseDown(e){
if(!e||e.button!==0)return;
var pos=xyGetCellPos(e.target);
if(!pos)return;
xyCellDrag=true;
xyCellSel={active:true,startRow:pos.row,startCol:pos.col,endRow:pos.row,endCol:pos.col};
xyClearRowSelection();
xyClearColSelection();
xyApplyCellSelection();
e.preventDefault();
if(e.target&&e.target.focus)e.target.focus();
}

function xyCellMouseOver(e){
if(!xyCellDrag)return;
var pos=xyGetCellPos(e.target);
if(!pos)return;
xyCellSel.endRow=pos.row;
xyCellSel.endCol=pos.col;
xyApplyCellSelection();
}

function xyHasCellSelection(){
var tbody=document.getElementById('xy-tbody');
if(!tbody)return false;
return tbody.querySelector('input.xy-cell-sel')!==null;
}

function xyGetCellSelectionInfo(){
var tbody=document.getElementById('xy-tbody');
if(!tbody)return null;
var rows=tbody.querySelectorAll('tr');
var info=[];
for(var i=0;i<rows.length;i++){
var inputs=rows[i].querySelectorAll('input');
if(inputs.length<2)continue;
var xSel=inputs[0].classList.contains('xy-cell-sel');
var ySel=inputs[1].classList.contains('xy-cell-sel');
if(xSel||ySel){
info.push({xSel:xSel,ySel:ySel,xInput:inputs[0],yInput:inputs[1]});
}
}
return info.length>0?info:null;
}

function xyRenumberRows(){
var rows=document.getElementById('xy-tbody')?document.getElementById('xy-tbody').querySelectorAll('tr'):[];
for(var i=0;i<rows.length;i++){
var idxCell=rows[i].querySelector('.xy-row-idx');
if(idxCell)idxCell.textContent=(i+1);
}
}

function xyRemoveRow(el){
var tr=el&&el.parentElement?el.parentElement:null;
if(tr&&tr.parentElement)tr.parentElement.removeChild(tr);
xyRenumberRows();
}

function xyCopySelectedCols(){
var cellInfo=xyGetCellSelectionInfo();
if(cellInfo){
var lines=[];
for(var i=0;i<cellInfo.length;i++){
var r=cellInfo[i];
var xv=r.xInput?r.xInput.value:'';
var yv=r.yInput?r.yInput.value:'';
if(r.xSel&&r.ySel)lines.push(xv+'\\t'+yv);
else if(r.xSel)lines.push(xv);
else if(r.ySel)lines.push(yv);
}
var text=lines.join('\\n');
try{
navigator.clipboard.writeText(text).then(function(){
document.getElementById('st').textContent='Copied '+lines.length+' row'+(lines.length!==1?'s':'');
}).catch(function(){xyFallbackCopy(text);});
}catch(e){xyFallbackCopy(text);}
return;
}
var useX=xySelCols.x,useY=xySelCols.y;
if(!useX&&!useY){useX=true;useY=true;}
var rowsAll=document.getElementById('xy-tbody').querySelectorAll('tr');
var rowsSel=[];
rowsAll.forEach(function(r){if(r.classList.contains('xy-row-sel'))rowsSel.push(r);});
var rows=rowsSel.length>0?rowsSel:rowsAll;
var lines=[];
for(var i=0;i<rows.length;i++){
var inputs=rows[i].querySelectorAll('input');
var xVal=inputs[0]?inputs[0].value:'';var yVal=inputs[1]?inputs[1].value:'';
if(useX&&useY)lines.push(xVal+'\\t'+yVal);
else if(useX)lines.push(xVal);
else lines.push(yVal);
}
var text=lines.join('\\n');
try{
navigator.clipboard.writeText(text).then(function(){
document.getElementById('st').textContent='Copied '+lines.length+' row'+(lines.length!==1?'s':'');
}).catch(function(){xyFallbackCopy(text);});
}catch(e){xyFallbackCopy(text);}
}

function xyFallbackCopy(text){
var ta=document.createElement('textarea');
ta.value=text;ta.style.position='fixed';ta.style.left='-9999px';
document.body.appendChild(ta);ta.select();
try{document.execCommand('copy');document.getElementById('st').textContent='Copied to clipboard';}
catch(e){alert('Copy failed');}
document.body.removeChild(ta);
}

function xyDeleteSelection(){
var tbody=document.getElementById('xy-tbody');
if(!tbody)return;
var cellInfo=xyGetCellSelectionInfo();
if(cellInfo){
cellInfo.forEach(function(r){
if(r.xSel&&r.xInput)r.xInput.value='';
if(r.ySel&&r.yInput)r.yInput.value='';
});
return;
}
var rowsAll=[].slice.call(tbody.querySelectorAll('tr'));
var rowsSel=rowsAll.filter(function(r){return r.classList.contains('xy-row-sel');});
var useX=xySelCols.x,useY=xySelCols.y;
if(rowsSel.length===0&&!useX&&!useY)return;
if(rowsSel.length>0&&!useX&&!useY){
rowsSel.forEach(function(r){tbody.removeChild(r);});
xyRenumberRows();
return;
}
var target=rowsSel.length>0?rowsSel:rowsAll;
target.forEach(function(r){
var inputs=r.querySelectorAll('input');
if(useX)inputs[0].value='';
if(useY)inputs[1].value='';
});
}

function xySetupCopyHotkey(){
if(xyCopyHotkeyInit)return;
xyCopyHotkeyInit=true;
document.addEventListener('keydown',function(e){
if(xyEditingIdx<0)return;
if((e.ctrlKey||e.metaKey)&&(e.key==='c'||e.key==='C')){
var rows=document.getElementById('xy-tbody')?document.getElementById('xy-tbody').querySelectorAll('tr'):null;
var hasRowSel=false;
if(rows){for(var ri=0;ri<rows.length;ri++){if(rows[ri].classList.contains('xy-row-sel')){hasRowSel=true;break;}}}
var hasCellSel=xyHasCellSelection();
if(xySelCols.x||xySelCols.y||hasRowSel||hasCellSel){
e.preventDefault();e.stopPropagation();xyCopySelectedCols();
}
}
});
}

function xyAddTableRow(x,y){
var tbody=document.getElementById('xy-tbody');
var tr=document.createElement('tr');
var idx=tbody.querySelectorAll('tr').length+1;
tr.innerHTML='<td class="xy-row-idx" onclick="xyToggleRowSelect(this.parentElement)">'+idx+'</td><td><input type="text" data-col="0" value="'+(x!==undefined?x:'')+'"></td><td><input type="text" data-col="1" value="'+(y!==undefined?y:'')+'"></td><td style="text-align:center;cursor:pointer;color:#F44336;font-weight:bold" onclick="xyRemoveRow(this)">&#x2715;</td>';
tbody.appendChild(tr);
var inputs=tr.querySelectorAll('input');
if(inputs[0]){inputs[0].onmousedown=xyCellMouseDown;inputs[0].onmouseenter=xyCellMouseOver;}
if(inputs[1]){inputs[1].onmousedown=xyCellMouseDown;inputs[1].onmouseenter=xyCellMouseOver;}
xyInitCellSelection();
if(xySelCols.x||xySelCols.y){
var inputs=tr.querySelectorAll('input');
if(inputs[0]&&xySelCols.x)inputs[0].classList.add('xy-col-sel');
if(inputs[1]&&xySelCols.y)inputs[1].classList.add('xy-col-sel');
}
}

function xyAddRow(){xyAddTableRow('','');}

function xyIsDefaultOriginRow(xv,yv){
var xNum=Number(xv),yNum=Number(yv);
if(!isFinite(xNum)||!isFinite(yNum))return false;
return Math.abs(xNum)<=1e-12&&Math.abs(yNum)<=1e-12;
}

function xyCurveHasOnlyDefaultOriginRow(curve){
if(!curve||!Array.isArray(curve.data)||curve.data.length!==1)return false;
var p=curve.data[0];
if(!p||p.length<2)return false;
return xyIsDefaultOriginRow(p[0],p[1]);
}

function xyTableHasOnlyDefaultOriginRow(){
var tbody=document.getElementById('xy-tbody');
if(!tbody)return false;
var rows=tbody.querySelectorAll('tr');
if(rows.length!==1)return false;
var inputs=rows[0].querySelectorAll('input');
if(inputs.length<2)return false;
return xyIsDefaultOriginRow(parseFloat(inputs[0].value),parseFloat(inputs[1].value));
}

function xyAppendOrReplaceEditingCurveData(data,axisType,xLabel,yLabel){
if(xyEditingIdx<0||xyEditingIdx>=xyCurves.length||!Array.isArray(data)||data.length===0)return false;
var c=xyCurves[xyEditingIdx];
var replacePlaceholder=xyCurveHasOnlyDefaultOriginRow(c);
if(replacePlaceholder){
c.data=data.slice();
c.axis=axisType||c.axis||'primary';
c.xlabel=xLabel||c.xlabel||'X';
c.ylabel=yLabel||c.ylabel||'Y';
if(yLabel)c.name=yLabel;
return true;
}
var baseData=Array.isArray(c.data)?c.data.slice():[];
c.data=baseData.concat(data);
return false;
}

function xyPasteData(){
try{
navigator.clipboard.readText().then(function(text){xyParseAndFill(text);}).catch(function(){
var text=prompt('Paste data here:');if(text)xyParseAndFill(text);
});
}catch(ex){var text=prompt('Paste data here:');if(text)xyParseAndFill(text);}
}

function xyParseAndFill(text){
if(!text||!text.trim())return;
var NL=String.fromCharCode(10);var CR=String.fromCharCode(13);var TAB=String.fromCharCode(9);
var raw=text.replace(new RegExp(CR,'g'),'');
var lines=raw.split(NL);
var allParts=[];
for(var li=0;li<lines.length;li++){
var line=lines[li].trim();if(!line)continue;
var parts=line.split(TAB);
if(parts.length<2)parts=line.split(';');
if(parts.length<2)parts=line.split('  ');
if(parts.length<2)parts=line.split(' ');
allParts.push(parts);
}
if(allParts.length===0){alert('No data found.');return;}
var maxCols=0;allParts.forEach(function(p){if(p.length>maxCols)maxCols=p.length;});
if(maxCols>=3){
var d1=[],d2=[];
for(var i=0;i<allParts.length;i++){
var xv=parseFloat(allParts[i][0].replace(',','.'));
var y1=parseFloat(allParts[i][1].replace(',','.'));
var y2=parseFloat(allParts[i][2].replace(',','.'));
if(!isNaN(xv)&&!isNaN(y1))d1.push([xv,y1]);
if(!isNaN(xv)&&!isNaN(y2))d2.push([xv,y2]);
}
if(d1.length>0){
var replacedPrimary=xyAppendOrReplaceEditingCurveData(d1,'primary','X','Y');
if(replacedPrimary){
document.getElementById('xy-axis-pri').checked=true;
}
}
if(d2.length>0){
var idx=xyCurves.length;
xyCurves.push({name:'Curve '+(idx+1),xlabel:'X',ylabel:'Y',color:CURVE_COLORS[idx%CURVE_COLORS.length],data:d2,axis:'secondary'});
}
xyEditingIdx=-1;
document.getElementById('xy-table-area').style.display='none';
xyClearCellSelection();
xyUpdatePlotSize();
xyRefreshList();drawPlot();
document.getElementById('st').textContent='Pasted 3-column data: 2 curves created';
return;
}
var parsed=[];var singleCol=[];var isSingle=true;
for(var li=0;li<allParts.length;li++){
var parts=allParts[li];
if(parts.length>=2){
var xv=parseFloat(parts[0].replace(',','.'));
var yv=parseFloat(parts[1].replace(',','.'));
if(!isNaN(xv)&&!isNaN(yv)){parsed.push([xv,yv]);isSingle=false;}
}else if(parts.length===1){
var v=parseFloat(parts[0].replace(',','.'));
if(!isNaN(v))singleCol.push(v);
}
}
if(isSingle&&singleCol.length>0&&parsed.length===0){
xyAskColumn(function(choice){
var result=[];
if(choice==='X'){for(var si=0;si<singleCol.length;si++)result.push([singleCol[si],'']);}
else{for(var si=0;si<singleCol.length;si++)result.push(['',singleCol[si]]);}
xyFillTable(result);
});
return;
}
if(parsed.length===0){alert('No valid numeric data found.');return;}
xyFillTable(parsed);
}

function xyFillTable(parsed){
if(parsed.length===0)return;
var tbody=document.getElementById('xy-tbody');
xyClearRowSelection();
var existingRows=tbody.querySelectorAll('tr');
var hasData=false;
for(var ri=0;ri<existingRows.length;ri++){
var inputs=existingRows[ri].querySelectorAll('input');
if(inputs[0].value.trim()||inputs[1].value.trim()){hasData=true;break;}
}
if(!hasData||xyTableHasOnlyDefaultOriginRow())tbody.innerHTML='';
for(var pi=0;pi<parsed.length;pi++){xyAddTableRow(parsed[pi][0],parsed[pi][1]);}
xyRenumberRows();
document.getElementById('st').textContent='Pasted '+parsed.length+' data points';
}

function xySaveCurve(){
if(xyEditingIdx<0)return;
var c=xyCurves[xyEditingIdx];
c.name=document.getElementById('xy-curve-name').value||('Curve '+(xyEditingIdx+1));
c.xlabel=document.getElementById('xy-col-x').value||'X';
c.ylabel=document.getElementById('xy-col-y').value||'Y';
c.axis=document.getElementById('xy-axis-sec').checked?'secondary':'primary';
var rows=document.getElementById('xy-tbody').querySelectorAll('tr');
var data=[];
rows.forEach(function(r){
var inputs=r.querySelectorAll('input');
var xv=parseFloat(inputs[0].value),yv=parseFloat(inputs[1].value);
var xE=isNaN(xv)&&inputs[0].value.trim()==='';
var yE=isNaN(yv)&&inputs[1].value.trim()==='';
if(!isNaN(xv)&&!isNaN(yv)){data.push([xv,yv]);}
else if(!isNaN(xv)&&yE){data.push([xv,0]);}
else if(xE&&!isNaN(yv)){data.push([0,yv]);}
});
c.data=data;
xyEditingIdx=-1;
document.getElementById('xy-table-area').style.display='none';
xyClearCellSelection();
xyUpdatePlotSize();
xyRefreshList();drawPlot();
}

function xyCommitEditingCurveDraft(){
if(xyEditingIdx<0||xyEditingIdx>=xyCurves.length)return;
var c=xyCurves[xyEditingIdx];
c.name=document.getElementById('xy-curve-name').value||('Curve '+(xyEditingIdx+1));
c.xlabel=document.getElementById('xy-col-x').value||'X';
c.ylabel=document.getElementById('xy-col-y').value||'Y';
c.axis=document.getElementById('xy-axis-sec').checked?'secondary':'primary';
var rows=document.getElementById('xy-tbody').querySelectorAll('tr');
var data=[];
rows.forEach(function(r){
var inputs=r.querySelectorAll('input');
var xv=parseFloat(inputs[0].value),yv=parseFloat(inputs[1].value);
var xE=isNaN(xv)&&inputs[0].value.trim()==='';
var yE=isNaN(yv)&&inputs[1].value.trim()==='';
if(!isNaN(xv)&&!isNaN(yv)){data.push([xv,yv]);}
else if(!isNaN(xv)&&yE){data.push([xv,0]);}
else if(xE&&!isNaN(yv)){data.push([0,yv]);}
});
c.data=data;
}

function xyCancelEdit(){
xyEditingIdx=-1;
document.getElementById('xy-table-area').style.display='none';
xyClearCellSelection();
xyUpdatePlotSize();
// Remove empty curves that were never saved
if(xyCurves.length>0){
var last=xyCurves[xyCurves.length-1];
if(last.data.length===1&&last.data[0][0]===0&&last.data[0][1]===0&&last.name.match(/^Curve \d+$/)){
// Check if it was just added and not saved with real data
}
}
xyRefreshList();
xyRefreshHideButton();
drawPlot();
}

function xyRefreshList(){
var list=document.getElementById('xy-curve-list');
var tableArea=document.getElementById('xy-table-area');
if(tableArea&&tableArea.parentElement===list){list.removeChild(tableArea);}
list.innerHTML='';
xyCurves.forEach(function(c,i){
var col=c.color||CURVE_COLORS[i%CURVE_COLORS.length];
var d=document.createElement('div');
var hidden=xyIsCurveHidden(c);
d.className='xy-curve-item'+(i===xySelectedIdx?' selected':'')+(hidden?' hidden':'');
var axisTag=(c.axis==='secondary')?' (R)':' (L)';
var hiddenTag=hidden?' <span class="xy-curve-hidden">Hidden</span>':'';
d.innerHTML='<div class="xy-curve-dot" style="border-color:'+col+';background:white"></div><span class="xy-curve-name">'+c.name+axisTag+hiddenTag+'</span>';
d.onclick=function(){xySelectedIdx=i;xyRefreshList();};
d.ondblclick=function(e){e.stopPropagation();if(xyEditingIdx===i){xyCancelEdit();}else{xyStartEdit(i);}};
list.appendChild(d);
});
if(tableArea){
if(xyEditingIdx>=0&&xyEditingIdx<xyCurves.length){
tableArea.style.display='block';
var items=list.querySelectorAll('.xy-curve-item');
if(items[xyEditingIdx]){items[xyEditingIdx].insertAdjacentElement('afterend',tableArea);}
else{list.appendChild(tableArea);}
}else{
tableArea.style.display='none';
list.appendChild(tableArea);
}
}
var dBtn=document.getElementById('xy-deriv-btn');
if(dBtn){
var hasCurves=xyCurves.length>0;
var hasSelection=xySelectedIdx>=0&&xySelectedIdx<xyCurves.length;
dBtn.style.display=hasCurves?'inline-block':'none';
dBtn.disabled=!hasSelection;
dBtn.title=hasSelection?'Create derivative from selected curve':'Select one curve first';
}
var fBtn=document.getElementById('xy-forecast-btn');
if(fBtn){
var hasCurvesF=xyCurves.length>0;
var hasSelectionF=xySelectedIdx>=0&&xySelectedIdx<xyCurves.length;
fBtn.style.display=hasCurvesF?'inline-block':'none';
fBtn.disabled=!hasSelectionF;
fBtn.title=hasSelectionF?'Create forecast from selected curve':'Select one curve first';
}
xyRefreshHideButton();
}

function xyApplyRange(){
xyUserRange.xmin=document.getElementById('xy-xmin').value.trim();
xyUserRange.xmax=document.getElementById('xy-xmax').value.trim();
xyUserRange.ymin=document.getElementById('xy-ymin').value.trim();
xyUserRange.ymax=document.getElementById('xy-ymax').value.trim();
xySecUserRange.ymin=document.getElementById('xy-symin').value.trim();
xySecUserRange.ymax=document.getElementById('xy-symax').value.trim();
xyAppliedRange={xmin:xyUserRange.xmin,xmax:xyUserRange.xmax,ymin:xyUserRange.ymin,ymax:xyUserRange.ymax};
xySecAppliedRange={ymin:xySecUserRange.ymin,ymax:xySecUserRange.ymax};
drawPlot();
}

function xyAutoRange(){
xyUserRange={xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'};
xySecUserRange={ymin:'auto',ymax:'auto'};
xyAppliedRange={xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'};
xySecAppliedRange={ymin:'auto',ymax:'auto'};
document.getElementById('xy-xmin').value='auto';
document.getElementById('xy-xmax').value='auto';
document.getElementById('xy-ymin').value='auto';
document.getElementById('xy-ymax').value='auto';
document.getElementById('xy-xstep').value='auto';
document.getElementById('xy-ystep').value='auto';
document.getElementById('xy-symin').value='auto';
document.getElementById('xy-symax').value='auto';
document.getElementById('xy-systep').value='auto';
drawPlot();
}

function xyResetAxes(){
document.getElementById('xy-xmin').value='auto';
document.getElementById('xy-xmax').value='auto';
document.getElementById('xy-ymin').value='auto';
document.getElementById('xy-ymax').value='auto';
document.getElementById('xy-xstep').value='auto';
document.getElementById('xy-ystep').value='auto';
document.getElementById('xy-symin').value='auto';
document.getElementById('xy-symax').value='auto';
document.getElementById('xy-systep').value='auto';
xyUserRange={xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'};
xySecUserRange={ymin:'auto',ymax:'auto'};
xyAppliedRange={xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'};
xySecAppliedRange={ymin:'auto',ymax:'auto'};
drawPlot();
}

// ==================== XY SHEET SYSTEM ====================
function xySaveCurrentSheet(){
var s=xySheets[xyActiveSheet];
s.curves=JSON.parse(JSON.stringify(xyCurves));
s.selectedIdx=xySelectedIdx;
s.editingIdx=xyEditingIdx;
s.pinned=JSON.parse(JSON.stringify(xyPinned));
s.userRange={xmin:document.getElementById('xy-xmin').value,xmax:document.getElementById('xy-xmax').value,ymin:document.getElementById('xy-ymin').value,ymax:document.getElementById('xy-ymax').value};
s.secUserRange={ymin:document.getElementById('xy-symin').value,ymax:document.getElementById('xy-symax').value};
s.appliedRange=JSON.parse(JSON.stringify(xyAppliedRange));
s.secAppliedRange=JSON.parse(JSON.stringify(xySecAppliedRange));
s.axisNames={xname:document.getElementById('xy-xname').value,yname:document.getElementById('xy-yname').value,syname:document.getElementById('xy-syname').value};
s.plotTitle=document.getElementById('xy-plot-title').value;
}
function xyLoadSheet(idx){
var s=xySheets[idx];
xyCurves=JSON.parse(JSON.stringify(s.curves));
xySelectedIdx=s.selectedIdx;
xyEditingIdx=-1;
xyPinned=JSON.parse(JSON.stringify(s.pinned||[]));
document.getElementById('xy-table-area').style.display='none';
xyClearCellSelection();
xyUpdatePlotSize();
xyAppliedRange=JSON.parse(JSON.stringify(s.appliedRange));
xySecAppliedRange=JSON.parse(JSON.stringify(s.secAppliedRange));
xyUserRange=JSON.parse(JSON.stringify(s.userRange));
xySecUserRange=JSON.parse(JSON.stringify(s.secUserRange));
document.getElementById('xy-xmin').value=s.userRange.xmin;
document.getElementById('xy-xmax').value=s.userRange.xmax;
document.getElementById('xy-ymin').value=s.userRange.ymin;
document.getElementById('xy-ymax').value=s.userRange.ymax;
document.getElementById('xy-symin').value=s.secUserRange.ymin;
document.getElementById('xy-symax').value=s.secUserRange.ymax;
document.getElementById('xy-xname').value=s.axisNames.xname||'X';
document.getElementById('xy-yname').value=s.axisNames.yname||'Y';
document.getElementById('xy-syname').value=s.axisNames.syname||'Y (R)';
document.getElementById('xy-plot-title').value=s.plotTitle||'XY Plot';
xyRefreshList();
drawPlot();
}
function xySwitchSheet(idx){
if(idx===xyActiveSheet)return;
xySaveCurrentSheet();
xyActiveSheet=idx;
xyLoadSheet(idx);
xyRenderSheetTabs();
}
function xyAddSheet(){
xySaveCurrentSheet();
var n=xySheets.length+1;
xySheets.push({title:'Sheet '+n,curves:[],selectedIdx:-1,editingIdx:-1,pinned:[],userRange:{xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'},secUserRange:{ymin:'auto',ymax:'auto'},appliedRange:{xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'},secAppliedRange:{ymin:'auto',ymax:'auto'},axisNames:{xname:'X',yname:'Y',syname:'Y (R)'},plotTitle:'XY Plot'});
xyActiveSheet=xySheets.length-1;
xyLoadSheet(xyActiveSheet);
xyRenderSheetTabs();
}
function xyRemoveSheet(idx){
if(xySheets.length<=1)return;
xySheets.splice(idx,1);
if(xyActiveSheet>=xySheets.length)xyActiveSheet=xySheets.length-1;
if(xyActiveSheet<0)xyActiveSheet=0;
xyLoadSheet(xyActiveSheet);
xyRenderSheetTabs();
}
function xyRenderSheetTabs(){
var bar=document.getElementById('xy-sheet-bar');
bar.innerHTML='';
xySheets.forEach(function(s,i){
var tab=document.createElement('button');
tab.className='xy-sheet-tab'+(i===xyActiveSheet?' active':'');
tab.setAttribute('data-sheet',i);
tab.onclick=function(e){if(e.target.classList.contains('xy-sheet-close')||e.target.classList.contains('xy-sheet-rename'))return;xySwitchSheet(i);};
var nameSpan=document.createElement('span');
nameSpan.className='xy-sheet-name';
nameSpan.textContent=s.title;
tab.appendChild(nameSpan);
var rnBtn=document.createElement('span');
rnBtn.className='xy-sheet-rename';
rnBtn.innerHTML='&#9998;';
rnBtn.title='Rename sheet';
rnBtn.onclick=function(e){e.stopPropagation();var newName=prompt('Rename sheet:',xySheets[i].title);if(newName&&newName.trim()){xySheets[i].title=newName.trim();xyRenderSheetTabs();}};
tab.appendChild(rnBtn);
if(xySheets.length>1){
var cl=document.createElement('span');
cl.className='xy-sheet-close';
cl.textContent='\u00D7';
cl.onclick=function(e){e.stopPropagation();if(confirm('Delete "'+s.title+'"?')){xyRemoveSheet(i);}};
tab.appendChild(cl);
}
bar.appendChild(tab);
});
// Rename on double-click
bar.querySelectorAll('.xy-sheet-tab').forEach(function(tab,i){
tab.ondblclick=function(){
var newName=prompt('Rename sheet:',xySheets[i].title);
if(newName&&newName.trim()){xySheets[i].title=newName.trim();xyRenderSheetTabs();}
};
});
var addBtn=document.createElement('button');
addBtn.className='xy-sheet-add';
addBtn.textContent='+';
addBtn.title='Add new sheet';
addBtn.onclick=xyAddSheet;
bar.appendChild(addBtn);
}

function xyDeleteAllCurves(){
if(xyCurves.length===0){alert('No curves to delete.');return;}
if(!confirm('Delete all '+xyCurves.length+' curves from this sheet?'))return;
xyCurves=[];xySelectedIdx=-1;xyEditingIdx=-1;xyPinned=[];
xyUserRange={xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'};
xySecUserRange={ymin:'auto',ymax:'auto'};
xyAppliedRange={xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'};
xySecAppliedRange={ymin:'auto',ymax:'auto'};
var xmn=document.getElementById('xy-xmin'),xmx=document.getElementById('xy-xmax');
var ymn=document.getElementById('xy-ymin'),ymx=document.getElementById('xy-ymax');
var symn=document.getElementById('xy-symin'),symx=document.getElementById('xy-symax');
var xst=document.getElementById('xy-xstep'),yst=document.getElementById('xy-ystep'),syst=document.getElementById('xy-systep');
if(xmn)xmn.value='auto';if(xmx)xmx.value='auto';if(ymn)ymn.value='auto';if(ymx)ymx.value='auto';
if(symn)symn.value='auto';if(symx)symx.value='auto';
if(xst)xst.value='auto';if(yst)yst.value='auto';if(syst)syst.value='auto';
document.getElementById('xy-table-area').style.display='none';
xyClearCellSelection();
xyRefreshList();
xyResizePlot();
xyUpdatePlotSize();
}

// ==================== VIEW CUT MANAGER ====================
var clipEnabled=[false,false,false];
var clipPlanesThree=[new THREE.Plane(),new THREE.Plane(),new THREE.Plane()];
var rotationClipPlaneThree=new THREE.Plane(),rotationClipPlaneThree2=new THREE.Plane();
var activeClipPlanesArr=[];
function anyCutEnabled(){return clipEnabled[0]||clipEnabled[1]||clipEnabled[2]||!!(cutPlanes.rotation&&cutPlanes.rotation.on);}
function clampCutPercent(v){
var n=parseInt(v,10);
if(!isFinite(n))n=50;
if(n<0)n=0;
if(n>100)n=100;
return n;
}
function computeMeshBBox(){
var xmin=Infinity,xmax=-Infinity,ymin=Infinity,ymax=-Infinity,zmin=Infinity,zmax=-Infinity;
for(var i=0;i<ON.length;i++){
var p=ON[i];
if(p[0]<xmin)xmin=p[0];if(p[0]>xmax)xmax=p[0];
if(p[1]<ymin)ymin=p[1];if(p[1]>ymax)ymax=p[1];
if(p[2]<zmin)zmin=p[2];if(p[2]>zmax)zmax=p[2];
}
meshBBox={xmin:xmin,xmax:xmax,ymin:ymin,ymax:ymax,zmin:zmin,zmax:zmax};
}
function getAxisRangeInfo(axis){
if(axis==='x'){
return{axis:'x',min:meshBBox.xmin,max:meshBBox.xmax,mid:(meshBBox.xmin+meshBBox.xmax)*0.5,range:Math.max(Math.abs(meshBBox.xmax-meshBBox.xmin),1e-20)};
}
if(axis==='y'){
return{axis:'y',min:meshBBox.ymin,max:meshBBox.ymax,mid:(meshBBox.ymin+meshBBox.ymax)*0.5,range:Math.max(Math.abs(meshBBox.ymax-meshBBox.ymin),1e-20)};
}
return{axis:'z',min:meshBBox.zmin,max:meshBBox.zmax,mid:(meshBBox.zmin+meshBBox.zmax)*0.5,range:Math.max(Math.abs(meshBBox.zmax-meshBBox.zmin),1e-20)};
}
function getMeshDiagonalSize(){
var dx=meshBBox.xmax-meshBBox.xmin;
var dy=meshBBox.ymax-meshBBox.ymin;
var dz=meshBBox.zmax-meshBBox.zmin;
var diag=Math.sqrt(dx*dx+dy*dy+dz*dz);
if(!isFinite(diag)||diag<1e-12)diag=Math.max(B,1);
return diag;
}
function getRotationCutAxisInfo(axis){
axis=(axis==='y'||axis==='z')?axis:'x';
if(axis==='y'){
return{
axis:'y',
dir:new THREE.Vector3(0,1,0),
baseNormal:new THREE.Vector3(1,0,0),
refAxes:['x','z'],
refLabels:['X ref:','Z ref:'],
planeLabel:'YZ'
};
}
if(axis==='z'){
return{
axis:'z',
dir:new THREE.Vector3(0,0,1),
baseNormal:new THREE.Vector3(0,1,0),
refAxes:['x','y'],
refLabels:['X ref:','Y ref:'],
planeLabel:'XZ'
};
}
return{
axis:'x',
dir:new THREE.Vector3(1,0,0),
baseNormal:new THREE.Vector3(0,0,1),
refAxes:['y','z'],
refLabels:['Y ref:','Z ref:'],
planeLabel:'XY'
};
}
function sanitizeRotationCutState(src){
src=src||{};
var dir=(src.dir==='-')?'-':'+';
return{
on:!!src.on,
axis:(src.axis==='y'||src.axis==='z')?src.axis:'x',
angle:Math.max(0,Math.min(360,parseInt(src.angle,10)||0)),
dir:dir,
angle2On:!!src.angle2On,
angle2:Math.max(0,Math.min(180,parseInt(src.angle2,10)||0)),
dir2:dir,
refA:clampCutPercent(src.refA),
refB:clampCutPercent(src.refB),
hidePlane:!!src.hidePlane
};
}
function readRotationCutStateFromUi(){
var state=sanitizeRotationCutState(cutPlanes.rotation||{});
var onEl=document.getElementById('rot-cut-on');
var axisEl=document.getElementById('rot-cut-axis');
var angleEl=document.getElementById('rot-cut-angle');
var dirEl=document.getElementById('rot-cut-dir');
var angle2Btn=document.getElementById('rot-cut-angle2-toggle');
var angle2El=document.getElementById('rot-cut-angle2');
var refAEl=document.getElementById('rot-cut-ref-a');
var refBEl=document.getElementById('rot-cut-ref-b');
var hidePlaneEl=document.getElementById('rot-cut-hide-plane');
return sanitizeRotationCutState({
on:onEl?onEl.checked:state.on,
axis:axisEl?axisEl.value:state.axis,
angle:angleEl?angleEl.value:state.angle,
dir:dirEl?dirEl.value:state.dir,
angle2On:angle2Btn?(angle2Btn.getAttribute('data-on')==='1'):state.angle2On,
angle2:angle2El?angle2El.value:state.angle2,
dir2:dirEl?dirEl.value:state.dir,
refA:refAEl?refAEl.value:state.refA,
refB:refBEl?refBEl.value:state.refB,
hidePlane:hidePlaneEl?hidePlaneEl.checked:state.hidePlane
});
}
function updateRotationCutAngle2Button(enabled){
var btn=document.getElementById('rot-cut-angle2-toggle');
if(!btn)return;
btn.setAttribute('data-on',enabled?'1':'0');
btn.textContent=enabled?'On':'Off';
btn.style.background=enabled?'#43A047':'#F44336';
btn.style.borderColor=enabled?'#1B5E20':'#B71C1C';
btn.style.color='#fff';
}
function updateRotationCutUi(state){
state=sanitizeRotationCutState(state||cutPlanes.rotation||{});
cutPlanes.rotation=state;
var onEl=document.getElementById('rot-cut-on');
var controls=document.getElementById('rot-cut-controls');
var axisEl=document.getElementById('rot-cut-axis');
var angleEl=document.getElementById('rot-cut-angle');
var angleVal=document.getElementById('rot-cut-angle-val');
var dirEl=document.getElementById('rot-cut-dir');
var angle2Row=document.getElementById('rot-cut-angle2-row');
var angle2El=document.getElementById('rot-cut-angle2');
var angle2Val=document.getElementById('rot-cut-angle2-val');
var refAEl=document.getElementById('rot-cut-ref-a');
var refBEl=document.getElementById('rot-cut-ref-b');
var refALbl=document.getElementById('rot-cut-ref-a-lbl');
var refBLbl=document.getElementById('rot-cut-ref-b-lbl');
var refAVal=document.getElementById('rot-cut-ref-a-val');
var refBVal=document.getElementById('rot-cut-ref-b-val');
var planeHint=document.getElementById('rot-cut-plane-hint');
var hidePlaneEl=document.getElementById('rot-cut-hide-plane');
var resetAllBtn=document.getElementById('rot-cut-reset-all-btn');
var info=getRotationCutAxisInfo(state.axis);
if(onEl)onEl.checked=state.on;
if(controls)controls.style.display=state.on?'block':'none';
if(resetAllBtn)resetAllBtn.style.display=state.on?'inline-block':'none';
if(axisEl)axisEl.value=info.axis;
if(angleEl)angleEl.value=String(state.angle);
if(angleVal)angleVal.innerHTML=String(state.angle)+'&deg;';
if(dirEl)dirEl.value=state.dir;
updateRotationCutAngle2Button(state.angle2On);
if(angle2Row)angle2Row.style.display=state.angle2On?'flex':'none';
if(angle2El)angle2El.value=String(state.angle2);
if(angle2Val)angle2Val.innerHTML=String(state.angle2)+'&deg;';
if(refAEl)refAEl.value=String(state.refA);
if(refBEl)refBEl.value=String(state.refB);
if(refALbl)refALbl.textContent=info.refLabels[0];
if(refBLbl)refBLbl.textContent=info.refLabels[1];
if(refAVal)refAVal.textContent=String(state.refA)+'%';
if(refBVal)refBVal.textContent=String(state.refB)+'%';
if(planeHint)planeHint.innerHTML='0&deg; =&gt; '+info.planeLabel+' plane';
if(hidePlaneEl)hidePlaneEl.checked=!!state.hidePlane;
}
function toggleRotationCutAngle2(force){
var state=readRotationCutStateFromUi();
var next=(force===undefined)?(!state.angle2On):!!force;
if(next&&!state.angle2On){
state.angle2=0;
state.dir2=state.dir;
}
state.angle2On=next;
cutPlanes.rotation=sanitizeRotationCutState(state);
updateRotationCutUi(cutPlanes.rotation);
applyCutClipping();
updateValueWindowsForCut();
scheduleCutMeshRebuild();
}
function buildAxisAlignedCut(axis){
var cfg=cutPlanes[axis];
if(!cfg||!cfg.on)return null;
var bounds=getAxisRangeInfo(axis);
var cutPos=bounds.min+(clampCutPercent(cfg.pos)/100)*bounds.range;
var normal=[0,0,0];
var constant=0;
if(axis==='x'){
if(cfg.dir==='+'){normal=[-1,0,0];constant=cutPos;}
else{normal=[1,0,0];constant=-cutPos;}
}
else if(axis==='y'){
if(cfg.dir==='+'){normal=[0,-1,0];constant=cutPos;}
else{normal=[0,1,0];constant=-cutPos;}
}
else{
if(cfg.dir==='+'){normal=[0,0,-1];constant=cutPos;}
else{normal=[0,0,1];constant=-cutPos;}
}
return{type:'axis',axis:axis,normal:normal,constant:constant};
}
function hideAxisCutPlanesEnabled(){
var el=document.getElementById('cut-hide-planes');
return !!(el&&el.checked);
}
function getAxisCutVisualStyle(axis){
if(axis==='x')return{mesh:0xEF5350,edge:0xC62828};
if(axis==='y')return{mesh:0x66BB6A,edge:0x2E7D32};
return{mesh:0x42A5F5,edge:0x1565C0};
}
function getAxisCutVisualData(axis){
var cfg=cutPlanes[axis];
if(!cfg||!cfg.on)return null;
var posInfo=getAxisRangeInfo(axis);
var cutPos=posInfo.min+(clampCutPercent(cfg.pos)/100)*posInfo.range;
var xInfo=getAxisRangeInfo('x');
var yInfo=getAxisRangeInfo('y');
var zInfo=getAxisRangeInfo('z');
var diag=getMeshDiagonalSize();
var point=new THREE.Vector3(xInfo.mid,yInfo.mid,zInfo.mid);
var uDir=new THREE.Vector3(1,0,0),vDir=new THREE.Vector3(0,1,0),normal=new THREE.Vector3(0,0,1);
var width=Math.max(diag*0.18,1e-9),height=Math.max(diag*0.18,1e-9);
if(axis==='x'){
point.x=cutPos;
uDir.set(0,1,0);
vDir.set(0,0,1);
normal.set(1,0,0);
width=Math.max(yInfo.range*1.18,diag*0.18);
height=Math.max(zInfo.range*1.18,diag*0.18);
}else if(axis==='y'){
point.y=cutPos;
uDir.set(1,0,0);
vDir.set(0,0,-1);
normal.set(0,1,0);
width=Math.max(xInfo.range*1.18,diag*0.18);
height=Math.max(zInfo.range*1.18,diag*0.18);
}else{
point.z=cutPos;
uDir.set(1,0,0);
vDir.set(0,1,0);
normal.set(0,0,1);
width=Math.max(xInfo.range*1.18,diag*0.18);
height=Math.max(yInfo.range*1.18,diag*0.18);
}
return{
axis:axis,
point:point,
uDir:uDir,
vDir:vDir,
normal:normal,
width:width,
height:height,
style:getAxisCutVisualStyle(axis)
};
}
function ensureAxisCutVisual(axis){
if(!sc)return;
if(!axisCutPlaneMeshes[axis]){
var style=getAxisCutVisualStyle(axis);
var planeGeo=new THREE.PlaneGeometry(1,1,1,1);
axisCutPlaneMeshes[axis]=new THREE.Mesh(planeGeo,new THREE.MeshBasicMaterial({color:style.mesh,transparent:true,opacity:0.13,side:THREE.DoubleSide,depthWrite:false}));
axisCutPlaneMeshes[axis].renderOrder=994;
axisCutPlaneMeshes[axis].frustumCulled=false;
sc.add(axisCutPlaneMeshes[axis]);
axisCutPlaneEdges[axis]=new THREE.LineSegments(new THREE.EdgesGeometry(planeGeo),new THREE.LineBasicMaterial({color:style.edge,transparent:true,opacity:0.88,depthTest:false}));
axisCutPlaneEdges[axis].renderOrder=995;
axisCutPlaneEdges[axis].frustumCulled=false;
sc.add(axisCutPlaneEdges[axis]);
}
}
function setAxisCutVisualVisibility(axis,show){
if(axisCutPlaneMeshes[axis])axisCutPlaneMeshes[axis].visible=show;
if(axisCutPlaneEdges[axis])axisCutPlaneEdges[axis].visible=show;
}
function updateAxisCutVisuals(){
if(!sc)return;
var hide=hideAxisCutPlanesEnabled();
['x','y','z'].forEach(function(axis){
ensureAxisCutVisual(axis);
var data=getAxisCutVisualData(axis);
if(!data||hide){
setAxisCutVisualVisibility(axis,false);
return;
}
var basis=new THREE.Matrix4();
basis.makeBasis(data.uDir.clone().normalize(),data.vDir.clone().normalize(),data.normal.clone().normalize());
var quat=new THREE.Quaternion().setFromRotationMatrix(basis);
if(axisCutPlaneMeshes[axis]){
axisCutPlaneMeshes[axis].position.copy(data.point);
axisCutPlaneMeshes[axis].quaternion.copy(quat);
axisCutPlaneMeshes[axis].scale.set(data.width,data.height,1);
}
if(axisCutPlaneEdges[axis]){
axisCutPlaneEdges[axis].position.copy(data.point);
axisCutPlaneEdges[axis].quaternion.copy(quat);
axisCutPlaneEdges[axis].scale.set(data.width,data.height,1);
}
setAxisCutVisualVisibility(axis,true);
});
}
function buildRotationCutPlaneData(axisDir,baseNormal,refPoint,angleDeg,dirValue){
var baseNormalUnit=baseNormal.clone().normalize();
var planeNormal=baseNormalUnit.clone();
var signedAngle=((dirValue==='-')?-1:1)*((parseFloat(angleDeg)||0)*Math.PI/180.0);
planeNormal.applyAxisAngle(axisDir,signedAngle).normalize();
var clipNormal=(dirValue==='-')?planeNormal.clone():planeNormal.clone().negate();
var constant=-clipNormal.dot(refPoint);
var planeDir=planeNormal.clone().cross(axisDir).normalize();
if(planeDir.lengthSq()<1e-16){
planeDir=new THREE.Vector3(0,1,0).cross(axisDir).normalize();
if(planeDir.lengthSq()<1e-16)planeDir=new THREE.Vector3(0,0,1).cross(axisDir).normalize();
}
return{
planeNormal:planeNormal,
clipNormal:clipNormal,
constant:constant,
planeDir:planeDir
};
}
function getRotationCutSignedAngleRad(angleDeg,dirValue){
return ((dirValue==='-')?-1:1)*((parseFloat(angleDeg)||0)*Math.PI/180.0);
}
function getRotationCutSecondaryAngleDeg(state){
state=sanitizeRotationCutState(state||{});
return (parseFloat(state.angle)||0)+(parseFloat(state.angle2)||0);
}
function chooseRotationCutSectorMid(axisDir,baseNormal,angle1,dir1,angle2,dir2){
if(!axisDir||!baseNormal)return null;
var axis=axisDir.clone().normalize();
var base=baseNormal.clone().normalize();
if(axis.lengthSq()<1e-16||base.lengthSq()<1e-16)return null;
var visibleBase=(dir1==='-')?base:base.clone().negate();
var sAngle1=getRotationCutSignedAngleRad(angle1,dir1);
var sAngle2=getRotationCutSignedAngleRad(angle2,dir2);
var delta=Math.atan2(Math.sin(sAngle2-sAngle1),Math.cos(sAngle2-sAngle1));
var midAngle=sAngle1+(delta*0.5);
var sectorMid=visibleBase.clone().applyAxisAngle(axis,midAngle);
if(sectorMid.lengthSq()<1e-16)return null;
return sectorMid.normalize();
}
function orientRotationCutPlaneToSector(planeData,sectorMid){
if(!planeData||!sectorMid||sectorMid.lengthSq()<1e-16)return planeData;
var clipNormal=planeData.clipNormal.clone();
var constant=planeData.constant;
if(clipNormal.dot(sectorMid)<0){
clipNormal.negate();
constant=-constant;
}
return{
planeNormal:planeData.planeNormal,
clipNormal:clipNormal,
constant:constant,
planeDir:planeData.planeDir
};
}
function getRotationCutData(){
var state=sanitizeRotationCutState(cutPlanes.rotation||{});
if(!state.on)return null;
var info=getRotationCutAxisInfo(state.axis);
var axisDir=info.dir.clone().normalize();
var refPoint=new THREE.Vector3(
getAxisRangeInfo('x').mid,
getAxisRangeInfo('y').mid,
getAxisRangeInfo('z').mid
);
var refAInfo=getAxisRangeInfo(info.refAxes[0]);
var refBInfo=getAxisRangeInfo(info.refAxes[1]);
refPoint[info.refAxes[0]]=refAInfo.min+(state.refA/100)*refAInfo.range;
refPoint[info.refAxes[1]]=refBInfo.min+(state.refB/100)*refBInfo.range;
var primaryAngle=state.angle;
var secondaryAngle=state.angle2On?getRotationCutSecondaryAngleDeg(state):null;
var baseVisible=(state.dir==='-')?info.baseNormal.clone():info.baseNormal.clone().negate();
var primary=buildRotationCutPlaneData(axisDir,info.baseNormal,refPoint,primaryAngle,state.dir);
var secondary=state.angle2On?buildRotationCutPlaneData(axisDir,info.baseNormal,refPoint,secondaryAngle,state.dir2):null;
if(state.angle2On&&secondary){
var sectorMid=chooseRotationCutSectorMid(axisDir,info.baseNormal,primaryAngle,state.dir,secondaryAngle,state.dir2);
if(sectorMid){
primary=orientRotationCutPlaneToSector(primary,sectorMid);
secondary=orientRotationCutPlaneToSector(secondary,sectorMid);
}
}
var splitDir=info.baseNormal.clone().cross(axisDir).normalize();
if(splitDir.lengthSq()<1e-16)splitDir=primary.planeDir.clone();
var axisInfo=getAxisRangeInfo(info.axis);
var diag=getMeshDiagonalSize();
var linePad=Math.max(diag*0.08,axisInfo.range*0.05);
var lineStart=refPoint.clone();
var lineEnd=refPoint.clone();
lineStart[info.axis]=axisInfo.min-linePad;
lineEnd[info.axis]=axisInfo.max+linePad;
var lineLength=Math.max(lineStart.distanceTo(lineEnd),diag*0.6);
var planeSize=Math.max(diag*1.35,refAInfo.range*1.25,refBInfo.range*1.25);
return{
enabled:true,
state:state,
info:info,
axisDir:axisDir,
baseVisible:baseVisible,
primaryAngle:primaryAngle,
secondaryAngle:secondaryAngle,
primarySignedAngle:getRotationCutSignedAngleRad(primaryAngle,state.dir),
secondarySignedAngle:state.angle2On?getRotationCutSignedAngleRad(secondaryAngle,state.dir2):null,
planeNormal:primary.planeNormal,
clipNormal:primary.clipNormal,
constant:primary.constant,
planeDir:primary.planeDir,
primary:primary,
secondary:secondary,
splitDir:splitDir,
refPoint:refPoint,
lineStart:lineStart,
lineEnd:lineEnd,
lineLength:lineLength,
planeSize:planeSize
};
}
function ensureRotationCutVisuals(){
if(!sc)return;
if(!rotationCutLine){
var lineGeo=new THREE.BufferGeometry();
lineGeo.setAttribute('position',new THREE.Float32BufferAttribute([0,0,0,0,0,0],3));
rotationCutLine=new THREE.LineSegments(lineGeo,new THREE.LineBasicMaterial({color:0xFF6D00,transparent:true,opacity:1,depthTest:false,depthWrite:false}));
rotationCutLine.renderOrder=999;
rotationCutLine.frustumCulled=false;
sc.add(rotationCutLine);
}
if(!rotationCutPlaneMesh){
var planeGeo=new THREE.PlaneGeometry(1,1,1,1);
rotationCutPlaneMesh=new THREE.Mesh(planeGeo,new THREE.MeshBasicMaterial({color:0x29B6F6,transparent:true,opacity:0.14,side:THREE.DoubleSide,depthWrite:false}));
rotationCutPlaneMesh.renderOrder=996;
rotationCutPlaneMesh.frustumCulled=false;
sc.add(rotationCutPlaneMesh);
rotationCutPlaneEdges=new THREE.LineSegments(new THREE.EdgesGeometry(planeGeo),new THREE.LineBasicMaterial({color:0x0288D1,transparent:true,opacity:0.85,depthTest:false}));
rotationCutPlaneEdges.renderOrder=997;
rotationCutPlaneEdges.frustumCulled=false;
sc.add(rotationCutPlaneEdges);
rotationCutPlaneMesh2=new THREE.Mesh(planeGeo,new THREE.MeshBasicMaterial({color:0x43A047,transparent:true,opacity:0.14,side:THREE.DoubleSide,depthWrite:false}));
rotationCutPlaneMesh2.renderOrder=996;
rotationCutPlaneMesh2.frustumCulled=false;
sc.add(rotationCutPlaneMesh2);
rotationCutPlaneEdges2=new THREE.LineSegments(new THREE.EdgesGeometry(planeGeo),new THREE.LineBasicMaterial({color:0x1B5E20,transparent:true,opacity:0.85,depthTest:false}));
rotationCutPlaneEdges2.renderOrder=997;
rotationCutPlaneEdges2.frustumCulled=false;
sc.add(rotationCutPlaneEdges2);
}
}
function setRotationCutVisualVisibility(showPrimary,showSecondary){
var showLine=!!(showPrimary||showSecondary);
if(rotationCutLine)rotationCutLine.visible=showLine;
if(rotationCutPlaneMesh)rotationCutPlaneMesh.visible=!!showPrimary;
if(rotationCutPlaneEdges)rotationCutPlaneEdges.visible=!!showPrimary;
if(rotationCutPlaneMesh2)rotationCutPlaneMesh2.visible=!!showSecondary;
if(rotationCutPlaneEdges2)rotationCutPlaneEdges2.visible=!!showSecondary;
}
function updateRotationCutVisuals(rotData){
if(!sc)return;
ensureRotationCutVisuals();
if(!rotData||!rotData.enabled){
setRotationCutVisualVisibility(false,false);
return;
}
var lp=rotationCutLine.geometry.getAttribute('position');
lp.array[0]=rotData.lineStart.x;lp.array[1]=rotData.lineStart.y;lp.array[2]=rotData.lineStart.z;
lp.array[3]=rotData.lineEnd.x;lp.array[4]=rotData.lineEnd.y;lp.array[5]=rotData.lineEnd.z;
lp.needsUpdate=true;
rotationCutLine.geometry.computeBoundingSphere();
if(rotationCutLine.material){
rotationCutLine.material.color.setHex(0xFF6D00);
rotationCutLine.material.opacity=1;
rotationCutLine.material.depthTest=false;
rotationCutLine.material.depthWrite=false;
rotationCutLine.material.transparent=true;
rotationCutLine.material.needsUpdate=true;
}
var show=!rotData.state.hidePlane;
var basis1=new THREE.Matrix4();
basis1.makeBasis(rotData.axisDir,rotData.primary.planeDir,rotData.primary.planeNormal);
var quat1=new THREE.Quaternion().setFromRotationMatrix(basis1);
rotationCutPlaneMesh.quaternion.copy(quat1);
rotationCutPlaneEdges.quaternion.copy(quat1);
if(rotData.state.angle2On&&rotData.secondary){
var basis2=new THREE.Matrix4();
basis2.makeBasis(rotData.axisDir,rotData.secondary.planeDir,rotData.secondary.planeNormal);
var quat2=new THREE.Quaternion().setFromRotationMatrix(basis2);
var halfSize=rotData.planeSize*0.5;
rotationCutPlaneMesh.position.copy(rotData.refPoint).add(rotData.primary.planeDir.clone().multiplyScalar(rotData.planeSize*0.25));
rotationCutPlaneMesh.scale.set(rotData.lineLength,halfSize,1);
rotationCutPlaneEdges.position.copy(rotationCutPlaneMesh.position);
rotationCutPlaneEdges.scale.set(rotData.lineLength,halfSize,1);
rotationCutPlaneMesh2.position.copy(rotData.refPoint).add(rotData.secondary.planeDir.clone().multiplyScalar(-rotData.planeSize*0.25));
rotationCutPlaneMesh2.quaternion.copy(quat2);
rotationCutPlaneMesh2.scale.set(rotData.lineLength,halfSize,1);
rotationCutPlaneEdges2.position.copy(rotationCutPlaneMesh2.position);
rotationCutPlaneEdges2.quaternion.copy(quat2);
rotationCutPlaneEdges2.scale.set(rotData.lineLength,halfSize,1);
setRotationCutVisualVisibility(show,show);
return;
}
rotationCutPlaneMesh.position.copy(rotData.refPoint);
rotationCutPlaneMesh.scale.set(rotData.lineLength,rotData.planeSize,1);
rotationCutPlaneEdges.position.copy(rotData.refPoint);
rotationCutPlaneEdges.scale.set(rotData.lineLength,rotData.planeSize,1);
setRotationCutVisualVisibility(show,false);
}
function scheduleCutMeshRebuild(){
if(cutRebuildTimer)clearTimeout(cutRebuildTimer);
clearCutSectionProjection();
var rotState=sanitizeRotationCutState(cutPlanes.rotation||{});
var delay=(rotState.on&&rotState.angle2On)?90:250;
cutRebuildTimer=setTimeout(function(){cutRebuildTimer=null;rebuildCutMesh();},delay);
}
function updateCutPlane(axis){
var idx=axis==='x'?0:(axis==='y'?1:2);
var cb=document.getElementById('cut-'+axis+'-on');
var slider=document.getElementById('cut-'+axis+'-pos');
var valEl=document.getElementById('cut-'+axis+'-val');
var dirEl=document.getElementById('cut-'+axis+'-dir');
var row=document.getElementById('cut-'+axis+'-row');
var enabled=cb.checked;
cutPlanes[axis]={on:enabled,pos:clampCutPercent(slider.value),dir:(dirEl&&dirEl.value==='-')?'-':'+'};
row.style.display=enabled?'flex':'none';
slider.value=String(cutPlanes[axis].pos);
valEl.textContent=String(cutPlanes[axis].pos)+'%';
clipEnabled[idx]=enabled;
// Instant visual feedback using Three.js clipping planes
applyCutClipping();
updateValueWindowsForCut();
scheduleCutMeshRebuild();
}
function updateRotationCut(){
cutPlanes.rotation=readRotationCutStateFromUi();
updateRotationCutUi(cutPlanes.rotation);
applyCutClipping();
updateValueWindowsForCut();
scheduleCutMeshRebuild();
}
function updateRotationCutVisualState(){
cutPlanes.rotation=readRotationCutStateFromUi();
updateRotationCutUi(cutPlanes.rotation);
updateRotationCutVisuals(getRotationCutData());
}
function resetRotationCutReference(){
var refAEl=document.getElementById('rot-cut-ref-a');
var refBEl=document.getElementById('rot-cut-ref-b');
if(refAEl)refAEl.value='50';
if(refBEl)refBEl.value='50';
updateRotationCut();
}
function resetRotationCutAngle(){
var angleEl=document.getElementById('rot-cut-angle');
var dirEl=document.getElementById('rot-cut-dir');
var angle2El=document.getElementById('rot-cut-angle2');
if(angleEl)angleEl.value='0';
if(dirEl)dirEl.value='+';
if(angle2El)angle2El.value='0';
updateRotationCut();
}
function computeClipPlane(axis){
var idx=axis==='x'?0:(axis==='y'?1:2);
var cut=buildAxisAlignedCut(axis);
if(!cut)return;
clipPlanesThree[idx]=new THREE.Plane(new THREE.Vector3(cut.normal[0],cut.normal[1],cut.normal[2]),cut.constant);
}
function setCutClippingPlanesForScene(cArr){
var planes=(cArr&&cArr.length)?cArr:[];
if(ms&&ms.material)ms.material.clippingPlanes=planes;
if(eg&&eg.material)eg.material.clippingPlanes=planes;
if(featureEg&&featureEg.material)featureEg.material.clippingPlanes=planes;
if(uMs&&uMs.material)uMs.material.clippingPlanes=planes;
if(uEg&&uEg.material)uEg.material.clippingPlanes=planes;
if(vrfGhostMs&&vrfGhostMs.material)vrfGhostMs.material.clippingPlanes=planes;
if(vrfGhostEg&&vrfGhostEg.material)vrfGhostEg.material.clippingPlanes=planes;
}
// Apply Three.js clipping planes for instant visual feedback during slider drag
function applyCutClipping(){
['x','y','z'].forEach(function(a){computeClipPlane(a);});
activeClipPlanesArr=[];
for(var i=0;i<3;i++){if(clipEnabled[i])activeClipPlanesArr.push(clipPlanesThree[i]);}
updateAxisCutVisuals();
var rotData=getRotationCutData();
updateRotationCutVisuals(rotData);
if(rotData&&rotData.enabled){
rotationClipPlaneThree=new THREE.Plane(rotData.primary.clipNormal.clone(),rotData.primary.constant);
activeClipPlanesArr.push(rotationClipPlaneThree);
if(rotData.state&&rotData.state.angle2On&&rotData.secondary){
rotationClipPlaneThree2=new THREE.Plane(rotData.secondary.clipNormal.clone(),rotData.secondary.constant);
activeClipPlanesArr.push(rotationClipPlaneThree2);
}
}
var cArr=activeClipPlanesArr.length>0?activeClipPlanesArr:[];
setCutClippingPlanesForScene(cArr);
}
function rebuildCutMesh(){
setCutClippingPlanesForScene([]);
updateAxisCutVisuals();
updateRotationCutVisuals(getRotationCutData());
// Rebuild mesh with element-based filtering
var drawColors=null;
if(!noContour&&rawColors){
if(Math.abs(curMin-dataMin)>1e-20||Math.abs(curMax-dataMax)>1e-20){
drawColors=remapColors(rawColors,dataMin,dataMax,curMin,curMax);
}else{drawColors=rawColors;}
}else if(!noContour&&curColors){drawColors=curColors;}
cm(getRenderNodes(),drawColors);
// Also rebuild undeformed mesh if visible
if(showUndeformed){
buildUndeformedOverlay(true);
if(uMs)uMs.visible=true;
if(uEg)uEg.visible=true;
}
}
function applyClipping(){
rebuildCutMesh();
}
function resetCutPlanes(){
['x','y','z'].forEach(function(axis){
document.getElementById('cut-'+axis+'-on').checked=false;
document.getElementById('cut-'+axis+'-pos').value=50;
document.getElementById('cut-'+axis+'-val').textContent='50%';
document.getElementById('cut-'+axis+'-dir').value='+';
document.getElementById('cut-'+axis+'-row').style.display='none';
cutPlanes[axis]={on:false,pos:50,dir:'+'};
});
clipEnabled=[false,false,false];
cutPlanes.rotation={on:false,axis:'x',angle:0,dir:'+',angle2On:false,angle2:0,dir2:'+',refA:50,refB:50,hidePlane:false};
var hideAxisEl=document.getElementById('cut-hide-planes');
if(hideAxisEl)hideAxisEl.checked=false;
updateRotationCutUi(cutPlanes.rotation);
var rotHideEl=document.getElementById('rot-cut-hide-plane');
if(rotHideEl)rotHideEl.checked=false;
var rotAngle2El=document.getElementById('rot-cut-angle2');
if(rotAngle2El)rotAngle2El.value='0';
updateAxisCutVisuals();
updateRotationCutVisuals(null);
activeClipPlanesArr=[];
setCutClippingPlanesForScene([]);
clearCutSectionProjection();
updateValueWindowsForCut();
rebuildCutMesh();
}

// --- Measure Tool ---
function getMeasureNeeded(mode){
return mode==='angle'?3:(mode==='distance'?2:0);
}
function getMeasureModeLabel(mode){
if(mode==='distance')return 'Distance';
if(mode==='angle')return 'Angle';
return 'Measure';
}
function getMeasureNodeRoleColor(order){
var colors=[0x2196F3,0x4CAF50,0xFF9800];
order=parseInt(order,10);
if(!isFinite(order))order=0;
order=Math.max(0,Math.min(colors.length-1,order));
return colors[order];
}
function getMeasureNodeRoleColorHex(order){
var colors=['#2196F3','#4CAF50','#FF9800'];
order=parseInt(order,10);
if(!isFinite(order))order=0;
order=Math.max(0,Math.min(colors.length-1,order));
return colors[order];
}
function measureLabelFromIndex(idx){
idx=parseInt(idx,10);
if(!isFinite(idx)||idx<0)idx=0;
var out='';
do{
out=String.fromCharCode(65+(idx%26))+out;
idx=Math.floor(idx/26)-1;
}while(idx>=0);
return out;
}
function getMeasureNodeDisplayId(nodeIdx){
if(NIDS&&NIDS[nodeIdx]!==undefined&&NIDS[nodeIdx]!==null)return String(NIDS[nodeIdx]);
return String(nodeIdx);
}
function isMeasureGroupBox(box){
return !!(box&&box.measureGroupId!==undefined&&box.measureGroupId!==null);
}
function hasAnyMeasurements(){
return measGroups.length>0||!!(measDraft&&measDraft.nodes&&measDraft.nodes.length>0);
}
function getMeasureLabelContainer(){
return document.getElementById('measure-label-container');
}
function createMeasureNodeLabel(text,color){
var container=getMeasureLabelContainer();
if(!container)return null;
var el=document.createElement('div');
el.className='measure-node-label';
el.textContent=text||'';
el.style.background=color||'#2196F3';
container.appendChild(el);
return el;
}
function ensureMeasureLabelElements(bundle){
if(!bundle)return;
if(!bundle.labelEls)bundle.labelEls=[];
while(bundle.labelEls.length<bundle.nodes.length){
var idx=bundle.labelEls.length;
bundle.labelEls.push(createMeasureNodeLabel(measureLabelFromIndex(bundle.labelStart+idx),getMeasureNodeRoleColorHex(idx)));
}
while(bundle.labelEls.length>bundle.nodes.length){
var dead=bundle.labelEls.pop();
if(dead&&dead.parentNode)dead.parentNode.removeChild(dead);
}
for(var i=0;i<bundle.labelEls.length;i++){
var el=bundle.labelEls[i];
if(!el)continue;
el.textContent=measureLabelFromIndex(bundle.labelStart+i);
el.style.background=getMeasureNodeRoleColorHex(i);
}
}
function createMeasureDraft(){
return{id:'draft',mode:measMode,nodes:[],markers:[],line:null,labelStart:measLabelCounter,dialogBoxId:null,labelEls:[]};
}
function removeMeasureBundleVisuals(bundle){
if(!bundle)return;
if(bundle.markers){
bundle.markers.forEach(function(m){
if(!m)return;
sc.remove(m);
try{if(m.geometry&&m.geometry.dispose)m.geometry.dispose();}catch(e){}
try{if(m.material&&m.material.dispose)m.material.dispose();}catch(e){}
});
}
bundle.markers=[];
if(bundle.line){
sc.remove(bundle.line);
try{if(bundle.line.geometry&&bundle.line.geometry.dispose)bundle.line.geometry.dispose();}catch(e){}
try{if(bundle.line.material&&bundle.line.material.dispose)bundle.line.material.dispose();}catch(e){}
bundle.line=null;
}
if(bundle.labelEls){
bundle.labelEls.forEach(function(el){if(el&&el.parentNode)el.parentNode.removeChild(el);});
bundle.labelEls=[];
}
}
function clearMeasureDraft(){
if(!measDraft)return;
removeMeasureBundleVisuals(measDraft);
measDraft=null;
}
function findDistanceMeasureGroup(a,b){
for(var i=0;i<measGroups.length;i++){
var g=measGroups[i];
if(!g||g.mode!=='distance'||!g.nodes||g.nodes.length<2)continue;
if((g.nodes[0]===a&&g.nodes[1]===b)||(g.nodes[0]===b&&g.nodes[1]===a))return g;
}
return null;
}
function buildMeasureLineVertices(mode,nodes){
var verts=[];
if(!nodes||nodes.length<2)return verts;
if(mode==='distance'){
verts.push(cn[nodes[0]][0],cn[nodes[0]][1],cn[nodes[0]][2],cn[nodes[1]][0],cn[nodes[1]][1],cn[nodes[1]][2]);
}else if(mode==='angle'){
verts.push(cn[nodes[0]][0],cn[nodes[0]][1],cn[nodes[0]][2],cn[nodes[1]][0],cn[nodes[1]][1],cn[nodes[1]][2]);
if(nodes.length>=3){
verts.push(cn[nodes[1]][0],cn[nodes[1]][1],cn[nodes[1]][2],cn[nodes[2]][0],cn[nodes[2]][1],cn[nodes[2]][2]);
}
}
return verts;
}
function createMeasureLine(verts){
var lineGeo=new THREE.BufferGeometry();
lineGeo.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));
var line=new THREE.LineSegments(lineGeo,new THREE.LineBasicMaterial({color:0xffff00,linewidth:2,depthTest:false}));
line.renderOrder=997;
sc.add(line);
return line;
}
function syncMeasureBundleVisuals(bundle){
if(!bundle||!bundle.nodes)return;
if(!bundle.markers)bundle.markers=[];
ensureMeasureLabelElements(bundle);
while(bundle.markers.length<bundle.nodes.length){
var mi=bundle.markers.length;
bundle.markers.push(createMeasMarker(cn[bundle.nodes[mi]],getMeasureNodeRoleColor(mi)));
}
while(bundle.markers.length>bundle.nodes.length){
var mk=bundle.markers.pop();
if(!mk)continue;
sc.remove(mk);
try{if(mk.geometry&&mk.geometry.dispose)mk.geometry.dispose();}catch(e){}
try{if(mk.material&&mk.material.dispose)mk.material.dispose();}catch(e){}
}
for(var i=0;i<bundle.nodes.length;i++){
var ni=bundle.nodes[i];
if(i>=bundle.markers.length)continue;
bundle.markers[i].position.set(cn[ni][0],cn[ni][1],cn[ni][2]);
bundle.markers[i].material.color.setHex(getMeasureNodeRoleColor(i));
bundle.markers[i].visible=isNodeVisibleNow(ni);
}
if(bundle.line){
sc.remove(bundle.line);
try{if(bundle.line.geometry&&bundle.line.geometry.dispose)bundle.line.geometry.dispose();}catch(e){}
try{if(bundle.line.material&&bundle.line.material.dispose)bundle.line.material.dispose();}catch(e){}
bundle.line=null;
}
var verts=buildMeasureLineVertices(bundle.mode,bundle.nodes);
if(verts.length>=6)bundle.line=createMeasureLine(verts);
}
function buildMeasureResult(bundle){
if(!bundle||!bundle.nodes)return null;
if(bundle.mode==='distance'){
if(bundle.nodes.length<2)return null;
var n1=bundle.nodes[0],n2=bundle.nodes[1];
var p1=cn[n1],p2=cn[n2];
var dx=p2[0]-p1[0],dy=p2[1]-p1[1],dz=p2[2]-p1[2];
var mag=Math.sqrt(dx*dx+dy*dy+dz*dz);
var la=measureLabelFromIndex(bundle.labelStart),lb=measureLabelFromIndex(bundle.labelStart+1);
return{
plainLines:[
'Distance Measurement',
'Node '+la+': N'+getMeasureNodeDisplayId(n1)+'  Node '+lb+': N'+getMeasureNodeDisplayId(n2),
'\\u0394X = '+formatLegendDrivenValue(dx,'N/A'),
'\\u0394Y = '+formatLegendDrivenValue(dy,'N/A'),
'\\u0394Z = '+formatLegendDrivenValue(dz,'N/A'),
'Magnitude = '+formatLegendDrivenValue(mag,'N/A')
],
html:
'<div style="font-weight:700;color:#0D47A1;margin-bottom:4px">Distance Measurement</div>'+
'<div><span style="color:'+getMeasureNodeRoleColorHex(0)+';font-weight:700">'+la+'</span>: N'+getMeasureNodeDisplayId(n1)+' &nbsp; <span style="color:'+getMeasureNodeRoleColorHex(1)+';font-weight:700">'+lb+'</span>: N'+getMeasureNodeDisplayId(n2)+'</div>'+
'<div>\\u0394X = '+formatLegendDrivenValue(dx,'N/A')+'</div>'+
'<div>\\u0394Y = '+formatLegendDrivenValue(dy,'N/A')+'</div>'+
'<div>\\u0394Z = '+formatLegendDrivenValue(dz,'N/A')+'</div>'+
'<div style="margin-top:4px;font-weight:700;color:#2E7D32">Magnitude = '+formatLegendDrivenValue(mag,'N/A')+'</div>'
};
}
if(bundle.mode==='angle'){
if(bundle.nodes.length<3)return null;
var a=bundle.nodes[0],b=bundle.nodes[1],c=bundle.nodes[2];
var pa=cn[a],pb=cn[b],pc=cn[c];
var v1=[pa[0]-pb[0],pa[1]-pb[1],pa[2]-pb[2]];
var v2=[pc[0]-pb[0],pc[1]-pb[1],pc[2]-pb[2]];
var dot=v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2];
var m1=Math.sqrt(v1[0]*v1[0]+v1[1]*v1[1]+v1[2]*v1[2]);
var m2=Math.sqrt(v2[0]*v2[0]+v2[1]*v2[1]+v2[2]*v2[2]);
var cosA=(m1>1e-20&&m2>1e-20)?dot/(m1*m2):0;
cosA=Math.max(-1,Math.min(1,cosA));
var angleRad=Math.acos(cosA);
var angleDeg=angleRad*180/Math.PI;
var l0=measureLabelFromIndex(bundle.labelStart),l1=measureLabelFromIndex(bundle.labelStart+1),l2=measureLabelFromIndex(bundle.labelStart+2);
return{
plainLines:[
'Angle Measurement',
'Node '+l0+': N'+getMeasureNodeDisplayId(a)+'  Node '+l1+' (vertex): N'+getMeasureNodeDisplayId(b)+'  Node '+l2+': N'+getMeasureNodeDisplayId(c),
'Angle at '+l1+' = '+formatLegendDrivenValue(angleDeg,'N/A')+'\\u00B0',
'('+formatLegendDrivenValue(angleRad,'N/A')+' rad)'
],
html:
'<div style="font-weight:700;color:#0D47A1;margin-bottom:4px">Angle Measurement</div>'+
'<div><span style="color:'+getMeasureNodeRoleColorHex(0)+';font-weight:700">'+l0+'</span>: N'+getMeasureNodeDisplayId(a)+' &nbsp; <span style="color:'+getMeasureNodeRoleColorHex(1)+';font-weight:700">'+l1+'</span> (vertex): N'+getMeasureNodeDisplayId(b)+' &nbsp; <span style="color:'+getMeasureNodeRoleColorHex(2)+';font-weight:700">'+l2+'</span>: N'+getMeasureNodeDisplayId(c)+'</div>'+
'<div style="margin-top:4px;font-weight:700;color:#2E7D32">Angle at '+l1+' = '+formatLegendDrivenValue(angleDeg,'N/A')+'\\u00B0</div>'+
'<div>('+formatLegendDrivenValue(angleRad,'N/A')+' rad)</div>'
};
}
return null;
}
function getMeasureAnchorClient(bundle){
if(!cvEl||!ca||!bundle||!bundle.nodes||bundle.nodes.length===0)return null;
var rect=cvEl.getBoundingClientRect();
var wx=0,wy=0,wz=0;
if(bundle.mode==='distance'&&bundle.nodes.length>=2){
var p0=cn[bundle.nodes[0]],p1=cn[bundle.nodes[1]];
wx=(p0[0]+p1[0])*0.5;wy=(p0[1]+p1[1])*0.5;wz=(p0[2]+p1[2])*0.5;
}else if(bundle.mode==='angle'&&bundle.nodes.length>=2){
wx=cn[bundle.nodes[1]][0];wy=cn[bundle.nodes[1]][1];wz=cn[bundle.nodes[1]][2];
}else{
var p=cn[bundle.nodes[bundle.nodes.length-1]];
wx=p[0];wy=p[1];wz=p[2];
}
var pos3=new THREE.Vector3(wx,wy,wz);
pos3.project(ca);
if(pos3.z>1)return{x:rect.left+rect.width*0.5,y:rect.top+rect.height*0.5};
return{x:(pos3.x*0.5+0.5)*rect.width+rect.left,y:(-pos3.y*0.5+0.5)*rect.height+rect.top};
}
function applyMeasureDialogBoxContent(bundle){
if(!bundle||bundle.dialogBoxId===null||bundle.dialogBoxId===undefined)return;
var box=getDialogById(bundle.dialogBoxId);
var result=buildMeasureResult(bundle);
if(!box||!result)return;
box.measureGroupId=bundle.id;
box.readOnly=true;
box.allowRichEdit=false;
box.nodeIdx=-1;
box.body.contentEditable='false';
box.body.classList.add('dialog-body-rich');
box.body.style.lineHeight='1.35';
box.body.innerHTML=result.html;
box.text=result.plainLines.join('\\n');
box.richHtml=box.body.innerHTML;
if(box.fontBtn)box.fontBtn.style.display='none';
if(box.editBtn)box.editBtn.style.display='none';
if(box.linkBtn)box.linkBtn.style.display='none';
if(box.copyBtn)box.copyBtn.style.display='none';
refreshDialogConnectButton(box);
refreshDialogCopyButton(box);
refreshDialogEditButton(box);
syncDialogTextSnapshot(box);
syncDialogBoxSize(box);
}
function createMeasureDialogBoxForBundle(bundle){
if(!bundle)return null;
var anchor=getMeasureAnchorClient(bundle);
var rect=cvEl?cvEl.getBoundingClientRect():null;
var clientX=anchor?anchor.x:(rect?(rect.left+rect.width*0.5):window.innerWidth*0.5);
var clientY=anchor?anchor.y:(rect?(rect.top+rect.height*0.5):window.innerHeight*0.5);
var box=createDialogBoxAtClient(clientX,clientY);
if(!box)return null;
bundle.dialogBoxId=box.id;
box.measureGroupId=bundle.id;
box.readOnly=true;
box.allowRichEdit=false;
box.nodeIdx=-1;
box.fontSizePx=Math.max(10,dialogFontSize);
box.body.contentEditable='false';
box.body.classList.add('dialog-body-rich');
if(box.fontBtn)box.fontBtn.style.display='none';
if(box.editBtn)box.editBtn.style.display='none';
if(box.linkBtn)box.linkBtn.style.display='none';
if(box.copyBtn)box.copyBtn.style.display='none';
refreshDialogConnectButton(box);
refreshDialogCopyButton(box);
refreshDialogEditButton(box);
return box;
}
function removeMeasureGroupById(id){
for(var i=0;i<measGroups.length;i++){
var g=measGroups[i];
if(!g||g.id!==id)continue;
removeMeasureBundleVisuals(g);
if(g.dialogBoxId!==null&&g.dialogBoxId!==undefined){
measDialogRemovalId=g.dialogBoxId;
removeDialogBoxById(g.dialogBoxId);
measDialogRemovalId=null;
}
measGroups.splice(i,1);
updateMeasureLabelPositions();
if(!hasAnyMeasurements()){
var overlay=document.getElementById('meas-overlay');
if(overlay)overlay.style.display='none';
}
document.getElementById('st').textContent='Measurement removed';
return;
}
}
function armMeasAdd(){
if(measMode==='off'){
document.getElementById('st').textContent='Measure: choose Distance or Angle first';
return;
}
if(measDraft&&measDraft.nodes&&measDraft.nodes.length>0&&measDraft.nodes.length<getMeasureNeeded(measDraft.mode)){
document.getElementById('st').textContent='Finish the current '+getMeasureModeLabel(measDraft.mode).toLowerCase()+' measurement first';
return;
}
clearMeasureDraft();
measDraft=createMeasureDraft();
document.getElementById('st').textContent='Measure '+getMeasureModeLabel(measMode)+': click '+getMeasureNeeded(measMode)+' node'+(getMeasureNeeded(measMode)>1?'s':'')+' on the mesh';
updateMeasurement();
}
function setMeasMode(mode){
measMode=mode;
if(measHighlightSphere)measHighlightSphere.visible=false;
clearMeasureDraft();
var overlay=document.getElementById('meas-overlay');
if(overlay)overlay.style.display='none';
if(mode==='off'){
document.getElementById('st').textContent='Measure: off';
updateMeasureLabelPositions();
return;
}
if(measGroups.length===0){
measDraft=createMeasureDraft();
document.getElementById('st').textContent='Measure '+getMeasureModeLabel(mode)+': click '+getMeasureNeeded(mode)+' node'+(getMeasureNeeded(mode)>1?'s':'')+' on the mesh';
}else{
document.getElementById('st').textContent='Measure '+getMeasureModeLabel(mode)+': click + to start a new measurement';
}
updateMeasurement();
}
function clearMeas(){
clearMeasureDraft();
var ids=measGroups.map(function(g){return g.id;});
ids.forEach(function(id){removeMeasureGroupById(id);});
measGroups=[];
measLabelCounter=0;
var overlay=document.getElementById('meas-overlay');
if(overlay)overlay.style.display='none';
updateMeasureLabelPositions();
if(measMode!=='off'){
measDraft=createMeasureDraft();
document.getElementById('st').textContent='Measure '+getMeasureModeLabel(measMode)+': click '+getMeasureNeeded(measMode)+' node'+(getMeasureNeeded(measMode)>1?'s':'')+' on the mesh';
}else{
document.getElementById('st').textContent='Measurements cleared';
}
updateMeasurement();
}
function createMeasMarker(pos,color){
var sz=B*0.003;
var geo=new THREE.SphereGeometry(sz,8,8);
var mat=new THREE.MeshBasicMaterial({color:color,depthTest:false});
var m=new THREE.Mesh(geo,mat);
m.position.set(pos[0],pos[1],pos[2]);
m.renderOrder=998;
sc.add(m);
return m;
}
function updateMeasureLabelPositions(){
var bundles=measGroups.slice();
if(measDraft)bundles.push(measDraft);
if(bundles.length===0)return;
var container=getMeasureLabelContainer();
if(!container||!cvEl)return;
var rect=cvEl.getBoundingClientRect();
var dispNodes=getDisplayNodes();
var cuts=getActiveCuts();
var hasCuts=cuts.length>0;
bundles.forEach(function(bundle){
if(!bundle||!bundle.nodes)return;
ensureMeasureLabelElements(bundle);
for(var i=0;i<bundle.labelEls.length;i++){
var el=bundle.labelEls[i];
var ni=bundle.nodes[i];
if(!el||ni===undefined||ni===null||ni<0||ni>=dispNodes.length||!isNodeVisibleNow(ni)||(hasCuts&&!isPointVisibleByCuts(dispNodes[ni],cuts))){
if(el)el.style.display='none';
continue;
}
var pos3=new THREE.Vector3(dispNodes[ni][0],dispNodes[ni][1],dispNodes[ni][2]);
pos3.project(ca);
if(pos3.z>1){
el.style.display='none';
continue;
}
var sx=(pos3.x*0.5+0.5)*rect.width+rect.left;
var sy=(-pos3.y*0.5+0.5)*rect.height+rect.top;
el.style.display='block';
el.style.left=(sx+10)+'px';
el.style.top=(sy-18)+'px';
}
});
}
function updateMeasurement(){
if(measDraft)syncMeasureBundleVisuals(measDraft);
for(var i=0;i<measGroups.length;i++){
var g=measGroups[i];
syncMeasureBundleVisuals(g);
if(g.dialogBoxId===null||g.dialogBoxId===undefined||!getDialogById(g.dialogBoxId))createMeasureDialogBoxForBundle(g);
applyMeasureDialogBoxContent(g);
}
updateMeasureLabelPositions();
updateDialogBoxesVisuals();
}
function finalizeMeasureDraft(){
if(!measDraft)return null;
var needed=getMeasureNeeded(measDraft.mode);
if(measDraft.nodes.length<needed)return null;
var g={
id:measureIdSeed++,
mode:measDraft.mode,
nodes:measDraft.nodes.slice(),
markers:measDraft.markers||[],
line:measDraft.line||null,
labelStart:measDraft.labelStart,
dialogBoxId:null,
labelEls:measDraft.labelEls||[]
};
measDraft=null;
measGroups.push(g);
measLabelCounter=g.labelStart+g.nodes.length;
createMeasureDialogBoxForBundle(g);
applyMeasureDialogBoxContent(g);
return g;
}
function onMeasClick(nodeIdx){
if(measMode==='off')return;
if(!measDraft){
if(measGroups.length>0){
document.getElementById('st').textContent='Measure '+getMeasureModeLabel(measMode)+': click + to start a new measurement';
return;
}
measDraft=createMeasureDraft();
}
if(measDraft.mode!==measMode){
clearMeasureDraft();
measDraft=createMeasureDraft();
}
if(measDraft.nodes.indexOf(nodeIdx)>=0){
measDraft.nodes=measDraft.nodes.filter(function(v){return v!==nodeIdx;});
syncMeasureBundleVisuals(measDraft);
updateMeasurement();
document.getElementById('st').textContent='N'+getMeasureNodeDisplayId(nodeIdx)+' removed from current measurement';
return;
}
measDraft.nodes.push(nodeIdx);
syncMeasureBundleVisuals(measDraft);
if(measDraft.mode==='distance'&&measDraft.nodes.length===2){
var existing=findDistanceMeasureGroup(measDraft.nodes[0],measDraft.nodes[1]);
if(existing){
clearMeasureDraft();
removeMeasureGroupById(existing.id);
document.getElementById('st').textContent='Distance '+measureLabelFromIndex(existing.labelStart)+'-'+measureLabelFromIndex(existing.labelStart+1)+' cleared';
updateMeasurement();
return;
}
}
var needed=getMeasureNeeded(measDraft.mode);
if(measDraft.nodes.length<needed){
var remaining=needed-measDraft.nodes.length;
document.getElementById('st').textContent='N'+getMeasureNodeDisplayId(nodeIdx)+' selected. Click '+remaining+' more node'+(remaining>1?'s':'')+'.';
updateMeasurement();
return;
}
var done=finalizeMeasureDraft();
updateMeasurement();
if(done){
document.getElementById('st').textContent=getMeasureModeLabel(done.mode)+' measurement '+measureLabelFromIndex(done.labelStart)+(done.mode==='distance'?'-'+measureLabelFromIndex(done.labelStart+1):'-'+measureLabelFromIndex(done.labelStart+1)+'-'+measureLabelFromIndex(done.labelStart+2))+' created';
}
}

// ==================== SAVE / LOAD CONFIGURATION ====================
function getConfigKey(){return 'VMAP3D_'+HTMLNAME;}
var cfgToastTimer=null;
function showCfgToast(html,duration){
var t=document.getElementById('cfg-toast');
t.innerHTML=html;
t.classList.add('show');
if(cfgToastTimer)clearTimeout(cfgToastTimer);
if(duration>0){cfgToastTimer=setTimeout(function(){t.classList.remove('show');},duration);}
}
function hideCfgToast(){var t=document.getElementById('cfg-toast');t.classList.remove('show');if(cfgToastTimer)clearTimeout(cfgToastTimer);}
function cfgWrapName(name){
if(!name)return '';
var max=30;
if(name.length<=max)return name;
var mid=Math.ceil(name.length/2);
return name.slice(0,mid)+'<br>'+name.slice(mid);
}
function saveConfigFallback(json,fname,nSettings){
var blob=new Blob([json],{type:'application/json'});
var a=document.createElement('a');
a.href=URL.createObjectURL(blob);
a.download=fname;
document.body.appendChild(a);a.click();document.body.removeChild(a);
setTimeout(function(){URL.revokeObjectURL(a.href);},1000);
showCfgToast('<div class="ct-icon">&#9989;</div><div class="ct-title">Configuration Saved</div><div class="ct-msg">'+nSettings+' settings exported as:<br><b>'+cfgWrapName(fname)+'</b><br><br>File saved to Downloads folder.<br>Move it to the same folder as your .html file.</div><br><button class="ct-btn" onclick="hideCfgToast()">OK</button>',0);
}
function cfgClone(v){
try{return JSON.parse(JSON.stringify(v));}catch(e){return v;}
}
function buildRuntimeConfig(){
try{xyCommitEditingCurveDraft();}catch(e){}
try{xySaveCurrentSheet();}catch(e){}
var cfg={};
cfg.edgeMode=edgeMode;
cfg.wireframe=document.getElementById('wf').checked;
cfg.undeformed=document.getElementById('um').checked;
cfg.perspective=document.getElementById('persp').checked;
cfg.autoRotate=document.getElementById('ar').checked;
cfg.showAxes=document.getElementById('ax').checked;
cfg.mouseInfo=document.getElementById('mi').checked;
cfg.showValues=document.getElementById('sv').checked;
cfg.valueInfoFontSize=document.getElementById('value-font-size').value;
cfg.xyPlot=xyPlotVisible;
cfg.noContour=document.getElementById('nc').checked;
cfg.noContourGroupColors=cfgClone(noContourGroupColors);
cfg.undContour=document.getElementById('umc').checked;
cfg.discreteLeg=document.getElementById('dc').checked;
cfg.dynamicLeg=document.getElementById('dynleg').checked;
cfg.bgColor=document.getElementById('bg-color').value;
cfg.vrfEnabled=document.getElementById('vrf-on').checked;
cfg.vrfMin=document.getElementById('vrf-min').value;
cfg.vrfMax=document.getElementById('vrf-max').value;
cfg.legMin=document.getElementById('leg-min').value;
cfg.legMax=document.getElementById('leg-max').value;
cfg.legFontSize=document.getElementById('leg-font-size').value;
cfg.legLevels=document.getElementById('leg-levels').value;
cfg.legFormat=document.getElementById('leg-format').value;
cfg.legFloatDecimals=document.getElementById('leg-fdec')?document.getElementById('leg-fdec').value:String(legendFloatDecimals);
cfg.legendCustomValues=cfgClone(legendCustomValues);
cfg.legendCustomColors=cfgClone(legendCustomColors);
cfg.extrapolationMethod=normalizeExtrapolationMethod(extrapolationMethod);
cfg.extrapolationNodalAveraging=normalizeNodalAveragingMode(extrapolationNodalAveraging);
cfg.extrapolationStandardPresetName=extrapolationStandardPresetName;
cfg.scale=cs;
cfg.currentVar=currentVar;
cfg.displacementComponent=normalizeDisplacementComponent(displacementComponent);
cfg.currentState=cst;
cfg.cutX={on:document.getElementById('cut-x-on').checked,pos:document.getElementById('cut-x-pos').value,dir:document.getElementById('cut-x-dir').value};
cfg.cutY={on:document.getElementById('cut-y-on').checked,pos:document.getElementById('cut-y-pos').value,dir:document.getElementById('cut-y-dir').value};
cfg.cutZ={on:document.getElementById('cut-z-on').checked,pos:document.getElementById('cut-z-pos').value,dir:document.getElementById('cut-z-dir').value};
cfg.cutHidePlanes=!!(document.getElementById('cut-hide-planes')&&document.getElementById('cut-hide-planes').checked);
cfg.cutSectionProjection=!!(document.getElementById('cut-section-proj')&&document.getElementById('cut-section-proj').checked);
var rcState=sanitizeRotationCutState(cutPlanes.rotation||readRotationCutStateFromUi());
cfg.rotationCut={
on:rcState.on,
axis:rcState.axis,
angle:rcState.angle,
dir:rcState.dir,
angle2On:rcState.angle2On,
angle2:rcState.angle2,
dir2:rcState.dir2,
refA:rcState.refA,
refB:rcState.refB,
hidePlane:rcState.hidePlane
};
cfg.measMode=document.getElementById('meas-mode').value;
cfg.xyCurves=cfgClone(xyCurves);
cfg.xySheets=cfgClone(xySheets);
cfg.xyActiveSheet=xyActiveSheet;
cfg.xyXname=document.getElementById('xy-xname').value;
cfg.xyYname=document.getElementById('xy-yname').value;
cfg.xySYname=document.getElementById('xy-syname').value;
cfg.xyPlotTitle=document.getElementById('xy-plot-title').value;
cfg.xyXmin=document.getElementById('xy-xmin').value;
cfg.xyXmax=document.getElementById('xy-xmax').value;
cfg.xyYmin=document.getElementById('xy-ymin').value;
cfg.xyYmax=document.getElementById('xy-ymax').value;
cfg.xyXstep=document.getElementById('xy-xstep').value;
cfg.xyYstep=document.getElementById('xy-ystep').value;
cfg.xySYmin=document.getElementById('xy-symin').value;
cfg.xySYmax=document.getElementById('xy-symax').value;
cfg.xySYstep=document.getElementById('xy-systep').value;
cfg.xyOrigin=document.getElementById('xy-origin').checked;
cfg.xyTitleFontSize=xyTitleFontSize;
cfg.xyValuesFontSize=xyValuesFontSize;
cfg.xyValueFormat=xyValueFormat;
cfg.xyFloatLevels=xyFloatLevels;
var gifStartEl=document.getElementById('gif-start');
var gifEndEl=document.getElementById('gif-end');
var animSpeedEl=document.getElementById('anim-speed');
var gifScaleEl=document.getElementById('gif-scale');
if(gifStartEl&&gifEndEl&&animSpeedEl&&gifScaleEl){
cfg.gifStart=gifStartEl.value;
cfg.gifEnd=gifEndEl.value;
cfg.animSpeed=animSpeedEl.value;
cfg.gifScale=gifScaleEl.value;
}
cfg.animHarmonic=animHarmonic;
cfg.animSwing=animSwing;
cfg.pinnedNodes=pinnedNodes.slice();
cfg.pinnedElems=pinnedElems.slice();
cfg.dialogMode=dialogMode;
cfg.dialogFontSize=dialogFontSize;
cfg.tableFormFontSize=tableFormFontSize;
cfg.sidebarPanelOrder=getSidebarPanelOrder();
var seenDialogIds={};
cfg.dialogBoxes=dialogBoxes.filter(function(b){return !isMeasureGroupBox(b);}).map(function(b){
return{
id:b.id,
x:b.x,
y:b.y,
w:b.w,
h:b.h,
text:(b.body?(b.body.innerText||b.body.textContent):b.text)||'',
richHtml:(b.body?(b.body.innerHTML||''):b.richHtml)||'',
bodyClass:(b.body&&b.body.className)?b.body.className:'dialog-body',
textStyle:cfgClone(ensureDialogTextStyle(b)),
readOnly:!!b.readOnly,
allowRichEdit:(b.allowRichEdit!==false),
fontSizePx:getDialogFontSizePx(b),
forecastDialogData:isForecastDialogBox(b)?cfgClone(b.forecastDialogData):null,
forecastDialogFormat:isForecastDialogBox(b)?getForecastDialogFormat(b):null,
forecastDialogDecimals:isForecastDialogBox(b)?getForecastDialogDecimals(b):null,
nodeIdx:(b.nodeIdx!==undefined?b.nodeIdx:-1)
};
}).filter(function(b){
var sid=(b.id!==undefined&&b.id!==null)?String(b.id):'';
if(!sid)return true;
if(seenDialogIds[sid])return false;
seenDialogIds[sid]=1;
return true;
});
cfg.hideElements=hideElemMode;
cfg.hideAllConnected=hideAllConnectedMode;
cfg.hiddenElements=Object.keys(hiddenElemMap).map(function(k){return parseInt(k,10);}).filter(function(v){return isFinite(v)&&v>=0;});
cfg.groupVisibilityState=cfgClone(groupVisibilityState);
cfg.camDist=camDist;
cfg.camQuat={x:camQuat.x,y:camQuat.y,z:camQuat.z,w:camQuat.w};
cfg.tg={x:tg.x,y:tg.y,z:tg.z};
cfg.savedAt=new Date().toLocaleString();
cfg._fileInfo=HTMLNAME;
return cfg;
}
function embedConfigIntoHtml(html,cfg){
var jsonText=JSON.stringify(cfg);
// Escape script-close tokens inside JSON payload.
jsonText=jsonText.replace(/<\\/script/gi,'<\\/script').replace(/<\/script/gi,'<\\/script');
var scriptClose='</'+'script>';
var tag='\\n<script id="vmap-embedded-config" type="application/json">'+jsonText+scriptClose+'\\n';
// Remove an existing embedded-config tag only when it appears as a real HTML tag line,
// not when "<script id=...>" appears inside JavaScript string literals.
var realTagRx=/(?:^|\\n)\\s*<script[^>]*id=["']vmap-embedded-config["'][^>]*>[\\s\\S]*?<\\/script>\\s*/i;
var legacyTagRx=/(?:^|\\n)\\s*<script[^>]*id=["']vmap-embedded-config["'][^>]*>[\\s\\S]*?<\\\\\\/script>\\s*/i;
if(realTagRx.test(html))html=html.replace(realTagRx,'\\n');
else if(legacyTagRx.test(html))html=html.replace(legacyTagRx,'\\n');
var bi=html.lastIndexOf('</body>');
if(bi>=0)return html.slice(0,bi)+tag+'\\n'+html.slice(bi);
return html+'\\n'+tag;
}
function loadRuntimeConfig(cfg){
if(!cfg)return;
var hasVar=false;
if(cfg.displacementComponent!==undefined&&cfg.displacementComponent!==null){
displacementComponent=normalizeDisplacementComponent(cfg.displacementComponent);
}
if(cfg.currentVar!==undefined&&cfg.currentVar!==null&&String(cfg.currentVar)!==''){
var vName=String(cfg.currentVar);
if(hasVarStateData(vName)){
document.getElementById('vs').value=vName;
ovs();
hasVar=true;
}else{
console.warn('Runtime config: currentVar not found:',vName);
}
}else{
refreshDisplacementComponentUi();
}
if(cfg.currentState!==undefined&&cfg.currentState!==null&&String(cfg.currentState)!==''){
setTimeout(function(){
var sid=String(cfg.currentState);
var ss=document.getElementById('ss');
var stateApplied=false;
if(ss){
for(var i=0;i<ss.options.length;i++){
if(String(ss.options[i].value)===sid){ss.value=ss.options[i].value;sid=ss.value;break;}
}
}
if(hasStateData(currentVar,sid)){
osc();
stateApplied=true;
}else{
console.warn('Runtime config: currentState not found for selected output:',sid);
}
setTimeout(function(){applyConfigAfterLoad(cfg);},stateApplied?120:20);
},hasVar?220:120);
}else{
setTimeout(function(){applyConfigAfterLoad(cfg);},40);
}
}
function loadEmbeddedConfigIfAny(){
try{
var tag=document.getElementById('vmap-embedded-config');
if(!tag)return false;
var txt=(tag.textContent||tag.innerText||'').trim();
if(!txt)return false;
var cfg=JSON.parse(txt);
loadRuntimeConfig(cfg);
return true;
}catch(e){
console.warn('Embedded config load failed:',e);
return false;
}
}
function saveCurrentHtmlFile(){
try{
var cfg=buildRuntimeConfig();
var html=(saveFileBaseHtml&&saveFileBaseHtml.length>0)?saveFileBaseHtml:(document.documentElement.outerHTML||'');
if(!/^<!doctype/i.test(html.trim()))html='<!DOCTYPE html>\\n'+html;
if(!(html.indexOf('CORE_DATA_TAG_MAP')>=0&&html.indexOf('STATE_NODE_TAG_MAP')>=0)){
html=document.documentElement.outerHTML||'';
if(!/^<!doctype/i.test(html.trim()))html='<!DOCTYPE html>\\n'+html;
}
if(!(html.indexOf('CORE_DATA_TAG_MAP')>=0&&html.indexOf('STATE_NODE_TAG_MAP')>=0)){
throw new Error('Save source is incomplete (mesh/state data tags missing)');
}
html=embedConfigIntoHtml(html,cfg);
var blob=new Blob([html],{type:'text/html;charset=utf-8'});
var fname=HTMLNAME+'_saved.html';
if(window.showSaveFilePicker&&window.isSecureContext!==false){
try{
window.showSaveFilePicker({suggestedName:fname,types:[{description:'HTML File',accept:{'text/html':['.html']}}]}).then(function(handle){
return handle.createWritable().then(function(writable){
return writable.write(blob).then(function(){return writable.close();}).then(function(){
showCfgToast('<div class="ct-icon">&#9989;</div><div class="ct-title">File Saved</div><div class="ct-msg">HTML saved with embedded runtime state:<br><b>'+cfgWrapName(handle.name)+'</b><br><br>Reopen this file to restore current viewer edits automatically.</div><br><button class="ct-btn" onclick="hideCfgToast()">OK</button>',0);
});
});
}).catch(function(err){
if(err&&err.name==='AbortError')return;
fallbackDownload(blob,fname);
showCfgToast('<div class="ct-icon">&#9989;</div><div class="ct-title">File Saved</div><div class="ct-msg">HTML exported as:<br><b>'+cfgWrapName(fname)+'</b><br><br>Reopen it to restore current viewer edits automatically.</div><br><button class="ct-btn" onclick="hideCfgToast()">OK</button>',0);
});
return;
}catch(e){}
}
fallbackDownload(blob,fname);
showCfgToast('<div class="ct-icon">&#9989;</div><div class="ct-title">File Saved</div><div class="ct-msg">HTML exported as:<br><b>'+cfgWrapName(fname)+'</b><br><br>Reopen it to restore current viewer edits automatically.</div><br><button class="ct-btn" onclick="hideCfgToast()">OK</button>',0);
}catch(e){
showCfgToast('<div class="ct-icon">&#10060;</div><div class="ct-title">Save File Failed</div><div class="ct-msg">'+e.message+'</div><br><button class="ct-btn" onclick="hideCfgToast()">OK</button>',0);
}
}
function saveConfig(){
try{
var cfg=buildRuntimeConfig();
var json=JSON.stringify(cfg,null,2);
var fname=HTMLNAME+'_config.json';
var nSettings=Object.keys(cfg).length;
// Try File System Access API (Chrome/Edge) to let user choose save location
if(window.showSaveFilePicker&&window.isSecureContext!==false){
try{
window.showSaveFilePicker({suggestedName:fname,types:[{description:'JSON Config',accept:{'application/json':['.json']}}]}).then(function(handle){
return handle.createWritable().then(function(writable){
return writable.write(json).then(function(){return writable.close();}).then(function(){
showCfgToast('<div class="ct-icon">&#9989;</div><div class="ct-title">Configuration Saved</div><div class="ct-msg">'+nSettings+' settings saved to:<br><b>'+cfgWrapName(handle.name)+'</b><br><br>File saved in the folder you selected.</div><br><button class="ct-btn" onclick="hideCfgToast()">OK</button>',0);
});
});
}).catch(function(err){
if(err.name==='AbortError')return;
// Fallback on error (e.g. SecurityError on file://)
saveConfigFallback(json,fname,nSettings);
});
}catch(syncErr){
saveConfigFallback(json,fname,nSettings);
}
}else{
saveConfigFallback(json,fname,nSettings);
}
}catch(e){
showCfgToast('<div class="ct-icon">&#10060;</div><div class="ct-title">Save Failed</div><div class="ct-msg">'+e.message+'</div><br><button class="ct-btn" onclick="hideCfgToast()">OK</button>',0);
}
}
function loadConfigFile(input){
if(!input.files||!input.files[0])return;
var file=input.files[0];
var reader=new FileReader();
reader.onload=function(ev){
try{
var cfg=JSON.parse(ev.target.result);
loadRuntimeConfig(cfg);
var savedAt=cfg.savedAt||'unknown';
var nSettings=Object.keys(cfg).length;
showCfgToast('<div class="ct-icon">&#9989;</div><div class="ct-title">Configuration Loaded</div><div class="ct-msg">'+nSettings+' settings restored from:<br><b>'+cfgWrapName(file.name)+'</b><br>Saved at: '+savedAt+'</div><br><button class="ct-btn" onclick="hideCfgToast()">OK</button>',0);
}catch(e){
showCfgToast('<div class="ct-icon">&#10060;</div><div class="ct-title">Load Failed</div><div class="ct-msg">Invalid config file: '+e.message+'</div><br><button class="ct-btn" onclick="hideCfgToast()">OK</button>',0);
}
};
reader.readAsText(file);
input.value='';
}
function cfgTextOrAuto(v){
if(v===undefined||v===null)return 'auto';
var s=String(v).trim();
return s===''?'auto':s;
}
function cfgNumOr(v,defv){
var n=Number(v);
return isFinite(n)?n:defv;
}
function makeDefaultXySheetState(title){
return{
title:title||'Sheet 1',
curves:[],
selectedIdx:-1,
editingIdx:-1,
pinned:[],
userRange:{xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'},
secUserRange:{ymin:'auto',ymax:'auto'},
appliedRange:{xmin:'auto',xmax:'auto',ymin:'auto',ymax:'auto'},
secAppliedRange:{ymin:'auto',ymax:'auto'},
axisNames:{xname:'X',yname:'Y',syname:'Y (R)'},
plotTitle:'XY Plot'
};
}
function normalizeXySheetState(src,idx){
var s=makeDefaultXySheetState('Sheet '+(idx+1));
if(!src||typeof src!=='object')return s;
if(typeof src.title==='string'&&src.title.trim())s.title=src.title.trim();
if(Array.isArray(src.curves))s.curves=cfgClone(src.curves);
if(Array.isArray(src.pinned))s.pinned=cfgClone(src.pinned);
if(src.selectedIdx!==undefined){var si=parseInt(src.selectedIdx,10);s.selectedIdx=isFinite(si)?si:-1;}
if(src.editingIdx!==undefined){var ei=parseInt(src.editingIdx,10);s.editingIdx=isFinite(ei)?ei:-1;}
if(src.userRange&&typeof src.userRange==='object'){
s.userRange.xmin=cfgTextOrAuto(src.userRange.xmin);
s.userRange.xmax=cfgTextOrAuto(src.userRange.xmax);
s.userRange.ymin=cfgTextOrAuto(src.userRange.ymin);
s.userRange.ymax=cfgTextOrAuto(src.userRange.ymax);
}
if(src.secUserRange&&typeof src.secUserRange==='object'){
s.secUserRange.ymin=cfgTextOrAuto(src.secUserRange.ymin);
s.secUserRange.ymax=cfgTextOrAuto(src.secUserRange.ymax);
}
if(src.appliedRange&&typeof src.appliedRange==='object'){
s.appliedRange.xmin=cfgTextOrAuto(src.appliedRange.xmin);
s.appliedRange.xmax=cfgTextOrAuto(src.appliedRange.xmax);
s.appliedRange.ymin=cfgTextOrAuto(src.appliedRange.ymin);
s.appliedRange.ymax=cfgTextOrAuto(src.appliedRange.ymax);
}
if(src.secAppliedRange&&typeof src.secAppliedRange==='object'){
s.secAppliedRange.ymin=cfgTextOrAuto(src.secAppliedRange.ymin);
s.secAppliedRange.ymax=cfgTextOrAuto(src.secAppliedRange.ymax);
}
if(src.axisNames&&typeof src.axisNames==='object'){
if(src.axisNames.xname!==undefined&&src.axisNames.xname!==null)s.axisNames.xname=String(src.axisNames.xname);
if(src.axisNames.yname!==undefined&&src.axisNames.yname!==null)s.axisNames.yname=String(src.axisNames.yname);
if(src.axisNames.syname!==undefined&&src.axisNames.syname!==null)s.axisNames.syname=String(src.axisNames.syname);
}
if(src.plotTitle!==undefined&&src.plotTitle!==null)s.plotTitle=String(src.plotTitle);
return s;
}
function restoreDialogBoxesFromConfig(savedBoxes){
if(!Array.isArray(savedBoxes))return;
cleanDialogBoxes();
if(savedBoxes.length===0){updateDialogBoxesVisuals();return;}
if(!cvEl)return;
var rect=cvEl.getBoundingClientRect();
var maxId=0;
var seenSavedIds={};
savedBoxes.forEach(function(src){
if(!src||typeof src!=='object')return;
var px=cfgNumOr(src.x,20);
var py=cfgNumOr(src.y,20);
var sid=parseInt(src.id,10);
if(isFinite(sid)&&sid>0){
if(seenSavedIds[sid])return;
seenSavedIds[sid]=1;
}
var b=createDialogBoxAtClient(rect.left+px,rect.top+py);
if(!b)return;
if(isFinite(sid)&&sid>0){
b.id=sid;
b.el.setAttribute('data-did',String(sid));
if(sid>maxId)maxId=sid;
}else if(b.id>maxId){maxId=b.id;}
if(src.readOnly!==undefined)b.readOnly=!!src.readOnly;
if(src.allowRichEdit!==undefined)b.allowRichEdit=!!src.allowRichEdit;
if(src.fontSizePx!==undefined&&src.fontSizePx!==null&&String(src.fontSizePx)!==''){
b.fontSizePx=Math.max(8,Math.min(36,cfgNumOr(src.fontSizePx,dialogFontSize)));
}
if(src.text!==undefined&&src.text!==null){
b.text=String(src.text);
}
var bodyClass='dialog-body';
if(src.bodyClass!==undefined&&src.bodyClass!==null&&String(src.bodyClass).trim()!==''){
bodyClass=String(src.bodyClass).indexOf('dialog-body-rich')>=0?'dialog-body dialog-body-rich':'dialog-body';
}
if(src.richHtml!==undefined&&src.richHtml!==null&&String(src.richHtml)!==''){
if(b.body){
b.body.className=bodyClass;
b.body.innerHTML=String(src.richHtml);
}
b.richHtml=String(src.richHtml);
syncDialogTextSnapshot(b);
}else if(b.body){
b.body.className=bodyClass;
b.body.textContent=b.text;
b.richHtml=b.body.innerHTML||'';
}
if(src.textStyle&&typeof src.textStyle==='object'&&b.body&&(!src.richHtml||String(src.richHtml)==='')){
var legacyStyle=[];
if(src.textStyle.bold)legacyStyle.push('font-weight:700');
if(src.textStyle.italic)legacyStyle.push('font-style:italic');
if(src.textStyle.underline)legacyStyle.push('text-decoration:underline');
legacyStyle.push('color:'+xyForecastSafeColor(src.textStyle.color,'#222222'));
var escaped=String(b.text||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>');
b.body.innerHTML='<span style="'+legacyStyle.join(';')+'">'+escaped+'</span>';
b.richHtml=b.body.innerHTML||'';
}
if(src.nodeIdx!==undefined&&src.nodeIdx!==null){
var ni=parseInt(src.nodeIdx,10);
b.nodeIdx=(isFinite(ni)&&ni>=0&&ni<ON.length)?ni:-1;
}else{
b.nodeIdx=-1;
}
if(src.forecastDialogData&&typeof src.forecastDialogData==='object'){
b.forecastDialogData=cfgClone(src.forecastDialogData);
if(src.forecastDialogFormat!==undefined&&src.forecastDialogFormat!==null)b.forecastDialogFormat=(String(src.forecastDialogFormat)==='exp')?'exp':'float';
if(src.forecastDialogDecimals!==undefined&&src.forecastDialogDecimals!==null)b.forecastDialogDecimals=Math.max(0,Math.min(10,cfgNumOr(src.forecastDialogDecimals,6)));
refreshForecastDialogBoxContent(b);
}
refreshDialogConnectButton(b);
refreshDialogEditButton(b);
applyDialogTextStyle(b);
syncDialogBoxSize(b);
b.x=cfgNumOr(src.x,b.x);
b.y=cfgNumOr(src.y,b.y);
clampDialogBoxToView(b);
applyDialogBoxDomPosition(b);
setDialogEditing(b,false);
});
if(maxId>=dialogIdSeed)dialogIdSeed=maxId+1;
dialogConnectPendingId=null;
dialogAddArmed=dialogMode;
hideDialogPreview();
updateDialogBoxesVisuals();
}
function applyConfigAfterLoad(cfg){
try{
// Scale
if(cfg.scale!==undefined){
setScaleFactorToUI(parseFloat(cfg.scale));
asc();
}
// Display Options
if(cfg.edgeMode){document.getElementById('ed').value=cfg.edgeMode;tgeMode(cfg.edgeMode);}
if(cfg.wireframe!==undefined){document.getElementById('wf').checked=cfg.wireframe;tgw(cfg.wireframe);}
if(cfg.undeformed!==undefined){document.getElementById('um').checked=cfg.undeformed;tgu(cfg.undeformed);}
if(cfg.perspective!==undefined){document.getElementById('persp').checked=cfg.perspective;tgp(cfg.perspective);}
if(cfg.autoRotate!==undefined){document.getElementById('ar').checked=cfg.autoRotate;tgr(cfg.autoRotate);}
if(cfg.showAxes!==undefined){document.getElementById('ax').checked=cfg.showAxes;tga(cfg.showAxes);}
if(cfg.mouseInfo!==undefined){document.getElementById('mi').checked=cfg.mouseInfo;tgmi(cfg.mouseInfo);}
if(cfg.showValues!==undefined){document.getElementById('sv').checked=cfg.showValues;tgv(cfg.showValues);}
if(cfg.valueInfoFontSize!==undefined){var vf=document.getElementById('value-font-size');if(vf)vf.value=cfg.valueInfoFontSize;setValueInfoFontSize(cfg.valueInfoFontSize);}
if(cfg.noContourGroupColors&&Array.isArray(cfg.noContourGroupColors)){
noContourGroupColors=cfg.noContourGroupColors.map(function(v,i){
var h=ncNormHex(v);
return h?h:ncDefaultColor(i);
});
}
if(cfg.noContour!==undefined){document.getElementById('nc').checked=cfg.noContour;tgnc(cfg.noContour);}
if(cfg.undContour!==undefined){document.getElementById('umc').checked=cfg.undContour;tgUndContour(cfg.undContour);}
if(cfg.discreteLeg!==undefined){document.getElementById('dc').checked=cfg.discreteLeg;tgd(cfg.discreteLeg);}
if(cfg.dynamicLeg!==undefined){document.getElementById('dynleg').checked=cfg.dynamicLeg;tgdl(cfg.dynamicLeg);}
if(cfg.bgColor){document.getElementById('bg-color').value=cfg.bgColor;setBgColor(cfg.bgColor);}
// VRF
if(cfg.vrfEnabled!==undefined){
document.getElementById('vrf-on').checked=cfg.vrfEnabled;
if(cfg.vrfMin)document.getElementById('vrf-min').value=cfg.vrfMin;
if(cfg.vrfMax)document.getElementById('vrf-max').value=cfg.vrfMax;
tgVRF(cfg.vrfEnabled);
}
// Legend
if(cfg.legMin)document.getElementById('leg-min').value=cfg.legMin;
if(cfg.legMax)document.getElementById('leg-max').value=cfg.legMax;
if(cfg.legFontSize){document.getElementById('leg-font-size').value=cfg.legFontSize;setLegFontSize(cfg.legFontSize);}
if(cfg.legLevels){document.getElementById('leg-levels').value=cfg.legLevels;setLegLevels(cfg.legLevels);}
if(cfg.legFormat){document.getElementById('leg-format').value=cfg.legFormat;setLegFormat(cfg.legFormat);}
if(cfg.legFloatDecimals!==undefined){if(document.getElementById('leg-fdec'))document.getElementById('leg-fdec').value=cfg.legFloatDecimals;setLegFloatDecimals(cfg.legFloatDecimals);}
applyExtrapolationSettings(
cfg.extrapolationMethod!==undefined?cfg.extrapolationMethod:extrapolationMethod,
cfg.extrapolationNodalAveraging!==undefined?cfg.extrapolationNodalAveraging:extrapolationNodalAveraging,
{silent:true,keepDialog:true,standardPresetName:(cfg.extrapolationStandardPresetName!==undefined?cfg.extrapolationStandardPresetName:extrapolationStandardPresetName)}
);
if(cfg.legMin)document.getElementById('leg-min').value=cfg.legMin;
if(cfg.legMax)document.getElementById('leg-max').value=cfg.legMax;
if(cfg.legMin&&cfg.legMax){applyLegRange();}
if(cfg.legendCustomValues&&cfg.legendCustomColors){
legendCustomValues=cfg.legendCustomValues;
legendCustomColors=cfg.legendCustomColors;
ulv(curMin,curMax);updGrad();updCb();rebuildCurrentMeshColors();
}
// Cut planes
if(cfg.cutX){
document.getElementById('cut-x-on').checked=cfg.cutX.on;
document.getElementById('cut-x-pos').value=cfg.cutX.pos;
document.getElementById('cut-x-dir').value=cfg.cutX.dir;
updateCutPlane('x');
}
if(cfg.cutY){
document.getElementById('cut-y-on').checked=cfg.cutY.on;
document.getElementById('cut-y-pos').value=cfg.cutY.pos;
document.getElementById('cut-y-dir').value=cfg.cutY.dir;
updateCutPlane('y');
}
if(cfg.cutZ){
document.getElementById('cut-z-on').checked=cfg.cutZ.on;
document.getElementById('cut-z-pos').value=cfg.cutZ.pos;
document.getElementById('cut-z-dir').value=cfg.cutZ.dir;
updateCutPlane('z');
}
if(cfg.cutHidePlanes!==undefined){
document.getElementById('cut-hide-planes').checked=!!cfg.cutHidePlanes;
updateAxisCutVisuals();
}
if(cfg.cutSectionProjection!==undefined){
tgCutSectionProjection(!!cfg.cutSectionProjection);
}
if(cfg.rotationCut){
document.getElementById('rot-cut-on').checked=cfg.rotationCut.on;
document.getElementById('rot-cut-axis').value=cfg.rotationCut.axis||'x';
document.getElementById('rot-cut-angle').value=(cfg.rotationCut.angle!==undefined&&cfg.rotationCut.angle!==null)?cfg.rotationCut.angle:'0';
document.getElementById('rot-cut-dir').value=(cfg.rotationCut.dir==='-')?'-':'+';
if(document.getElementById('rot-cut-angle2'))document.getElementById('rot-cut-angle2').value=(cfg.rotationCut.angle2!==undefined&&cfg.rotationCut.angle2!==null)?cfg.rotationCut.angle2:document.getElementById('rot-cut-angle').value;
if(document.getElementById('rot-cut-angle2-toggle'))document.getElementById('rot-cut-angle2-toggle').setAttribute('data-on',cfg.rotationCut.angle2On?'1':'0');
document.getElementById('rot-cut-ref-a').value=(cfg.rotationCut.refA!==undefined&&cfg.rotationCut.refA!==null)?cfg.rotationCut.refA:'50';
document.getElementById('rot-cut-ref-b').value=(cfg.rotationCut.refB!==undefined&&cfg.rotationCut.refB!==null)?cfg.rotationCut.refB:'50';
document.getElementById('rot-cut-hide-plane').checked=!!cfg.rotationCut.hidePlane;
updateRotationCut();
}else{
updateRotationCutUi(cutPlanes.rotation);
}
// Measure
if(cfg.measMode){document.getElementById('meas-mode').value=cfg.measMode;setMeasMode(cfg.measMode);}
// Animation range
var cfgGifStartEl=document.getElementById('gif-start');
var cfgGifEndEl=document.getElementById('gif-end');
var cfgAnimSpeedEl=document.getElementById('anim-speed');
var cfgSpeedValEl=document.getElementById('speed-val');
var cfgGifScaleEl=document.getElementById('gif-scale');
var cfgGifScaleValEl=document.getElementById('gif-scale-val');
if(cfgGifStartEl&&cfgGifEndEl&&cfgAnimSpeedEl&&cfgSpeedValEl&&cfgGifScaleEl&&cfgGifScaleValEl){
if(cfg.gifStart)cfgGifStartEl.value=cfg.gifStart;
if(cfg.gifEnd)cfgGifEndEl.value=cfg.gifEnd;
if(cfg.animSpeed){cfgAnimSpeedEl.value=cfg.animSpeed;cfgSpeedValEl.textContent=cfg.animSpeed;}
if(cfg.gifScale){cfgGifScaleEl.value=cfg.gifScale;cfgGifScaleValEl.textContent=cfg.gifScale;}
if(VIEWER_MODE==='harmonic'){
if(cfg.animHarmonic!==undefined){tgAnimHarmonic(cfg.animHarmonic);}
else{refreshAnimHarmonicButton();}
}else{
if(cfg.animSwing!==undefined){tgAnimHarmonic(cfg.animSwing);}
else if(cfg.animHarmonic!==undefined){tgAnimHarmonic(cfg.animHarmonic);}
else{refreshAnimHarmonicButton();}
}
ugrl();
}
// XY Plot
if(cfg.xySheets&&Array.isArray(cfg.xySheets)&&cfg.xySheets.length>0){
xySheets=cfg.xySheets.map(function(s,i){return normalizeXySheetState(s,i);});
if(xySheets.length===0)xySheets=[makeDefaultXySheetState('Sheet 1')];
var ai=parseInt(cfg.xyActiveSheet,10);
if(!isFinite(ai))ai=0;
xyActiveSheet=Math.max(0,Math.min(xySheets.length-1,ai));
xyLoadSheet(xyActiveSheet);
xyRenderSheetTabs();
}else if(cfg.xyCurves&&cfg.xyCurves.length>0){
xyCurves=cfgClone(cfg.xyCurves);
xyRefreshList();
}
if(cfg.xyXname!==undefined&&cfg.xyXname!==null)document.getElementById('xy-xname').value=String(cfg.xyXname);
if(cfg.xyYname!==undefined&&cfg.xyYname!==null)document.getElementById('xy-yname').value=String(cfg.xyYname);
if(cfg.xySYname!==undefined&&cfg.xySYname!==null)document.getElementById('xy-syname').value=String(cfg.xySYname);
if(cfg.xyPlotTitle!==undefined&&cfg.xyPlotTitle!==null)document.getElementById('xy-plot-title').value=String(cfg.xyPlotTitle);
if(cfg.xyXmin!==undefined&&cfg.xyXmin!==null)document.getElementById('xy-xmin').value=String(cfg.xyXmin);
if(cfg.xyXmax!==undefined&&cfg.xyXmax!==null)document.getElementById('xy-xmax').value=String(cfg.xyXmax);
if(cfg.xyYmin!==undefined&&cfg.xyYmin!==null)document.getElementById('xy-ymin').value=String(cfg.xyYmin);
if(cfg.xyYmax!==undefined&&cfg.xyYmax!==null)document.getElementById('xy-ymax').value=String(cfg.xyYmax);
if(cfg.xyXstep!==undefined&&cfg.xyXstep!==null)document.getElementById('xy-xstep').value=String(cfg.xyXstep);
if(cfg.xyYstep!==undefined&&cfg.xyYstep!==null)document.getElementById('xy-ystep').value=String(cfg.xyYstep);
if(cfg.xySYmin!==undefined&&cfg.xySYmin!==null)document.getElementById('xy-symin').value=String(cfg.xySYmin);
if(cfg.xySYmax!==undefined&&cfg.xySYmax!==null)document.getElementById('xy-symax').value=String(cfg.xySYmax);
if(cfg.xySYstep!==undefined&&cfg.xySYstep!==null)document.getElementById('xy-systep').value=String(cfg.xySYstep);
if(cfg.xyOrigin!==undefined)document.getElementById('xy-origin').checked=cfg.xyOrigin;
if(cfg.xyTitleFontSize!==undefined&&cfg.xyTitleFontSize!==null)xySetTitleFont(cfg.xyTitleFontSize);
if(cfg.xyValuesFontSize!==undefined&&cfg.xyValuesFontSize!==null)xySetValuesFont(cfg.xyValuesFontSize);
if(cfg.xyValueFormat!==undefined&&cfg.xyValueFormat!==null)xySetValueFormat(cfg.xyValueFormat);
if(cfg.xyFloatLevels!==undefined&&cfg.xyFloatLevels!==null)xySetFloatLevels(cfg.xyFloatLevels);
try{xySaveCurrentSheet();}catch(e){}
if(cfg.xyPlot!==undefined){tgxy(cfg.xyPlot);}
// Restore pinned values
if(cfg.pinnedNodes&&cfg.pinnedNodes.length>0){
clearPinned();
cfg.pinnedNodes.forEach(function(ni){
if(ni>=0&&ni<cn.length&&curColors)pinNodeValue(ni);
});
}
// Restore pinned element values
if(cfg.pinnedElems&&cfg.pinnedElems.length>0){
clearPinnedElems();
cfg.pinnedElems.forEach(function(ei){
if(ei>=0&&centroidRawColors&&ei<centroidRawColors.length)pinElemValue(ei,0);
});
}
// Camera
if(cfg.camDist)camDist=cfg.camDist;
if(cfg.camQuat)camQuat.set(cfg.camQuat.x,cfg.camQuat.y,cfg.camQuat.z,cfg.camQuat.w);
if(cfg.tg)tg.set(cfg.tg.x,cfg.tg.y,cfg.tg.z);
uc();
if(cfg.dialogMode!==undefined){
document.getElementById('dlg-on').checked=!!cfg.dialogMode;
tgDialogMode(!!cfg.dialogMode);
}
if(cfg.dialogFontSize!==undefined){
setDialogFontSize(cfg.dialogFontSize);
}
if(cfg.tableFormFontSize!==undefined){
setTableFormFont(cfg.tableFormFontSize);
}
if(cfg.sidebarPanelOrder&&Array.isArray(cfg.sidebarPanelOrder)){
applySidebarPanelOrder(cfg.sidebarPanelOrder,true);
}
if(cfg.dialogBoxes!==undefined&&Array.isArray(cfg.dialogBoxes)){
restoreDialogBoxesFromConfig(cfg.dialogBoxes);
}
var cfgHideMode=cfg.hideElements!==undefined?!!cfg.hideElements:!!(cfg.hiddenElements&&cfg.hiddenElements.length>0);
hiddenElemMap=Object.create(null);
if(cfgHideMode&&cfg.hiddenElements&&Array.isArray(cfg.hiddenElements)){
cfg.hiddenElements.forEach(function(ei){
var n=parseInt(ei,10);
if(isFinite(n)&&n>=0)hiddenElemMap[n]=1;
});
}
ensureConnectedGroupVisibilityState();
if(cfg.groupVisibilityState&&Array.isArray(cfg.groupVisibilityState)&&groupVisibilityState.length){
for(var gi=0;gi<groupVisibilityState.length;gi++){
groupVisibilityState[gi]=(cfg.groupVisibilityState[gi]!==false);
}
}
bumpHiddenElemRevision();
var cfgHideAll=cfg.hideAllConnected!==undefined?!!cfg.hideAllConnected:false;
setHideAllConnected(cfgHideAll);
document.getElementById('hide-elem-on').checked=cfgHideMode;
tgHideElements(cfgHideMode);
refreshAfterHideElementsChange();
refreshDisplacementComponentUi();
drawPlot();
updateDialogBoxesVisuals();
document.getElementById('st').textContent='Configuration loaded successfully!';
}catch(e){
console.error('Error applying config:',e);
try{cst=null;cn=ON.slice();cm(getRenderNodes(),null);uc();}catch(_){}
document.getElementById('st').textContent='Error applying config: '+e.message;
}
}

try{
console.log('[VMAP] Build='+BUILD_REV);
var fLen=(Array.isArray(F)?F.length:'lazy');
var femLen=(Array.isArray(FEM)?FEM.length:'lazy');
console.log('[VMAP] Data check: ON='+ON.length+' F='+fLen+' BF='+BF.length+' BFE='+BFE.length+' FEM='+femLen+' SL='+SL.length);
console.log('[VMAP] B='+B+' CT='+JSON.stringify(CT)+' IS="'+IS+'" currentVar="'+currentVar+'"');
console.log('[VMAP] Output vars='+Object.keys(OUT_STATE_INDEX).join(','));
console.log('[VMAP] State node payloads='+Object.keys(STATE_NODE_TAG_MAP).length);
console.log('[VMAP] Loaded states for currentVar='+Object.keys(AD).length+' VAR_LOCS='+JSON.stringify(VAR_LOCS));
if(ON.length===0){throw new Error('No nodes (ON is empty)');}
if(BF.length===0){throw new Error('No boundary faces (BF is empty)');}
if(THREE_MISSING){
try{pss();}catch(_){try{pssFallback();}catch(__){}}
try{ugrl();}catch(_){}
try{xyRenderSheetTabs();}catch(_){}
throw new Error('Three.js not loaded - check internet connection');
}
document.getElementById('st').textContent='Initializing 3D viewer...';
init();
console.log('[VMAP] Init complete');
setTimeout(function(){
if(loadEmbeddedConfigIfAny()){
console.log('[VMAP] Embedded runtime config restored');
}
},60);
}catch(initErr){
console.error('[VMAP] Init failed:',initErr);
document.getElementById('st').textContent='ERROR: '+initErr.message;
document.getElementById('st').style.background='#fdd';document.getElementById('st').style.color='#c00';
try{pss();ugrl();xyRenderSheetTabs();}catch(_){}
}
</script></body></html>'''
    
    update_progress(90, "Writing HTML file...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    
    update_progress(100, "Complete!")
    return output_file


# =============================================================================
# GUI APPLICATION
# =============================================================================

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VMAP 3D Viewer v1.0.37")
        self.root.geometry("820x740")
        self.root.resizable(True, True)
        
        # State variables
        self.fp = tk.StringVar()
        self.fp.trace('w', self.on_file_path_changed)
        self.st = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar()
        self.reader = None
        self.available_outputs = []
        self.selected_output = None
        self.viewer_mode = tk.StringVar(value="static")
        self.export_all_edges_var = tk.BooleanVar(value=False)
        self.output_summary_text = "Select VMAP file first"
        self._default_window_height = 740
        self._output_listbox_base_rows = 6
        self._output_listbox_current_rows = self._output_listbox_base_rows
        self._output_resize_after_id = None
        
        self.setup()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    @staticmethod
    def _norm_path(path):
        return os.path.normcase(os.path.abspath(path.strip().strip('"').strip("'")))

    def _close_reader(self):
        if self.reader:
            try:
                self.reader.close()
            except:
                pass
        self.reader = None

    def reset_session_state(self, status_message="Ready"):
        self._close_reader()
        self.available_outputs = []
        self.selected_output = None
        self.output_summary_text = "Select VMAP file first"

        self.output_listbox.delete(0, tk.END)
        self.output_listbox.selection_clear(0, tk.END)
        self.output_listbox.config(state='normal', bg='#f5f5f5')

        self.output_info_label.config(text=self.output_summary_text, fg='gray')
        self.generate_btn.config(state='disabled', bg='#808080')
        self.export_all_edges_var.set(False)

        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        self.progress_status_label.config(text="Ready", fg='green')
        self.st.set(status_message)

        self.apply_mode_rules()

    def set_mode_controls_enabled(self, enabled):
        state = 'normal' if enabled else 'disabled'
        if hasattr(self, 'mode_static_rb') and self.mode_static_rb:
            self.mode_static_rb.config(state=state)
        if hasattr(self, 'mode_harmonic_rb') and self.mode_harmonic_rb:
            self.mode_harmonic_rb.config(state=state)

    def _schedule_output_list_resize(self):
        if self._output_resize_after_id is not None:
            try:
                self.root.after_cancel(self._output_resize_after_id)
            except:
                pass
        self._output_resize_after_id = self.root.after(30, self._apply_output_list_resize)

    def _sync_main_canvas_window_size(self, target_width=None):
        if not hasattr(self, '_main_canvas') or not self._main_canvas:
            return
        if not hasattr(self, '_main_canvas_window') or self._main_canvas_window is None:
            return
        if not hasattr(self, '_main_content_frame') or not self._main_content_frame:
            return
        try:
            canvas = self._main_canvas
            frame = self._main_content_frame
            width = max(1, int(target_width if target_width is not None else canvas.winfo_width()))
            canvas_h = max(1, int(canvas.winfo_height()))
            req_h = max(1, int(frame.winfo_reqheight()))
            target_h = max(canvas_h, req_h)
            canvas.itemconfig(self._main_canvas_window, width=width, height=target_h)
            canvas.configure(scrollregion=(0, 0, width, target_h))
        except:
            pass

    def _apply_output_list_resize(self):
        self._output_resize_after_id = None
        if not hasattr(self, 'output_listbox') or not self.output_listbox:
            return
        try:
            current_height = max(1, int(self.root.winfo_height()))
        except:
            return
        base_height = max(1, int(self._default_window_height))
        base_rows = max(1, int(self._output_listbox_base_rows))
        target_rows = max(base_rows, int(round(float(base_rows) * float(current_height) / float(base_height))))
        if target_rows != self._output_listbox_current_rows:
            self.output_listbox.config(height=target_rows)
            self._output_listbox_current_rows = target_rows
        self._sync_main_canvas_window_size()

    def _on_root_resize(self, event):
        if event.widget is self.root:
            self._schedule_output_list_resize()
    
    def on_closing(self):
        self._close_reader()
        self.root.destroy()
    
    def setup(self):
        # Header
        tf = tk.Frame(self.root, bg='#d4542a', relief='raised', bd=3)
        tf.pack(fill='x', padx=10, pady=(10, 5))
        
        # Title labels - centered
        tk.Label(tf, text="Vibracoustic", font=('Arial', 18, 'bold'), fg='white', bg='#d4542a', pady=3).pack()
        tk.Label(tf, text="VMAP 3D Viewer", font=('Arial', 12), fg='white', bg='#d4542a', pady=1).pack()
        tk.Label(tf, text="European FEA Department - v1.0.37", font=('Arial', 9, 'italic'), fg='#ffccaa', bg='#d4542a').pack()
        
        # Guideline button - floating in top-right corner of title frame
        guideline_btn = tk.Button(tf, text="Guideline", command=self.open_guideline,
                  font=('Arial', 9, 'bold'), bg='#FFD700', fg='#333',
                  activebackground='#FFC000', relief='raised', bd=2, padx=10, pady=2)
        guideline_btn.place(relx=1.0, x=-10, y=6, anchor='ne')
        
        # Scrollable main area
        scroll_container = tk.Frame(self.root)
        scroll_container.pack(fill='both', expand=True, padx=10, pady=0)
        
        main_canvas = tk.Canvas(scroll_container, highlightthickness=0)
        main_scrollbar = tk.Scrollbar(scroll_container, orient='vertical', command=main_canvas.yview)
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        main_scrollbar.pack(side='right', fill='y')
        main_canvas.pack(side='left', fill='both', expand=True)
        
        # Inner frame for all content
        mf = tk.Frame(main_canvas)
        canvas_window = main_canvas.create_window((0, 0), window=mf, anchor='nw')
        self._main_canvas = main_canvas
        self._main_canvas_window = canvas_window
        self._main_content_frame = mf
        
        # Make inner frame width follow canvas width
        def on_canvas_configure(event):
            self._sync_main_canvas_window_size(target_width=event.width)
        main_canvas.bind('<Configure>', on_canvas_configure)
        
        # Update scroll region when content changes
        def on_frame_configure(event):
            self._sync_main_canvas_window_size()
        mf.bind('<Configure>', on_frame_configure)
        
        # Mouse wheel scrolling (Windows + Linux)
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
        def on_mousewheel_linux_up(event):
            main_canvas.yview_scroll(-3, 'units')
        def on_mousewheel_linux_down(event):
            main_canvas.yview_scroll(3, 'units')
        main_canvas.bind_all('<MouseWheel>', on_mousewheel)
        main_canvas.bind_all('<Button-4>', on_mousewheel_linux_up)
        main_canvas.bind_all('<Button-5>', on_mousewheel_linux_down)
        self.root.bind('<Configure>', self._on_root_resize, add='+')
        
        # STEP 1: File Selection - LabelFrame
        step1 = tk.LabelFrame(mf, text="Step 1: Select VMAP File",
                               font=('Arial', 10, 'bold'), fg='#333', padx=10, pady=8)
        step1.pack(fill='x', pady=(5, 8))
        
        ff = tk.Frame(step1)
        ff.pack(fill='x')
        tk.Entry(ff, textvariable=self.fp, font=('Arial', 9), width=75).pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Button(ff, text="Browse", command=self.browse, font=('Arial', 9, 'bold'),
                  bg='#2196F3', fg='white', width=10).pack(side='left')
        
        # STEP 2: Analysis Mode - LabelFrame
        step2 = tk.LabelFrame(mf, text="Step 2: Analysis Mode",
                               font=('Arial', 10, 'bold'), fg='#333', padx=10, pady=8)
        step2.pack(fill='x', pady=(0, 8))

        mode_row = tk.Frame(step2)
        mode_row.pack(anchor='w')
        self.mode_static_rb = tk.Radiobutton(
            mode_row, text="Static", variable=self.viewer_mode, value="static",
            command=self.on_mode_changed, font=('Arial', 9, 'bold'), state='disabled'
        )
        self.mode_static_rb.pack(side='left', padx=(0, 16))
        self.mode_harmonic_rb = tk.Radiobutton(
            mode_row, text="Harmonic", variable=self.viewer_mode, value="harmonic",
            command=self.on_mode_changed, font=('Arial', 9, 'bold'), state='disabled'
        )
        self.mode_harmonic_rb.pack(side='left')

        self.mode_info_label = tk.Label(step2,
                                        text="Static: normal workflow | Harmonic: External Surface + Displacement only",
                                        font=('Arial', 9), fg='#666')
        self.mode_info_label.pack(anchor='w', pady=(3, 0))

        options_row = tk.Frame(step2)
        options_row.pack(anchor='w', pady=(4, 0))
        self.export_all_edges_cb = tk.Checkbutton(
            options_row,
            text="Enable All Edges option in HTML (Increase file size)",
            variable=self.export_all_edges_var,
            font=('Arial', 9),
            state='disabled'
        )
        self.export_all_edges_cb.pack(side='left')

        # STEP 3: Output Selection - LabelFrame
        step3 = tk.LabelFrame(mf, text="Step 3: Select Output Variable",
                               font=('Arial', 10, 'bold'), fg='#333', padx=10, pady=8)
        step3.pack(fill='both', expand=True, pady=(0, 8))
        
        self.output_info_label = tk.Label(step3, text=self.output_summary_text,
                                           font=('Arial', 9), fg='gray')
        self.output_info_label.pack(anchor='w', pady=(0, 3))
        
        lf = tk.Frame(step3)
        lf.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(lf)
        scrollbar.pack(side='right', fill='y')
        
        self.output_listbox = tk.Listbox(lf, height=self._output_listbox_base_rows, font=('Courier', 9),
                                          yscrollcommand=scrollbar.set,
                                          selectmode='single', bg='#f5f5f5',
                                          relief='sunken', bd=1)
        self.output_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.output_listbox.yview)
        
        self.output_listbox.bind('<<ListboxSelect>>', self.on_output_selected)
        self.root.after_idle(self._apply_output_list_resize)
        
        # STEP 4: Generate - LabelFrame
        step4 = tk.LabelFrame(mf, text="Step 4: Generate 3D Viewer",
                               font=('Arial', 10, 'bold'), fg='#333', padx=10, pady=8)
        step4.pack(fill='x', pady=(0, 8))
        
        self.generate_btn = tk.Button(step4, text="Generate 3D Viewer", command=self.generate,
                                       font=('Arial', 12, 'bold'), bg='#808080', fg='white',
                                       width=20, height=2, state='disabled')
        self.generate_btn.pack(pady=5)
        
        # Progress section - LabelFrame
        progress_frame = tk.LabelFrame(mf, text="3D viewer creation Progress",
                                        font=('Arial', 9, 'italic'), fg='#666', padx=10, pady=8)
        progress_frame.pack(fill='x', pady=(0, 8))
        
        pf = tk.Frame(progress_frame)
        pf.pack(fill='x')
        
        self.progressbar = ttk.Progressbar(pf, variable=self.progress_var, maximum=100,
                                            length=500, mode='determinate')
        self.progressbar.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.progress_label = tk.Label(pf, text="0%", font=('Arial', 9, 'bold'), width=5)
        self.progress_label.pack(side='right')
        
        self.progress_status_label = tk.Label(progress_frame, text="Ready",
                                               font=('Arial', 9), fg='green')
        self.progress_status_label.pack(anchor='w', fill='x', pady=(3, 0))
        
        # Bottom bar: Exit button + watermark
        bottom_frame = tk.Frame(mf)
        bottom_frame.pack(fill='x', padx=8, pady=(8, 4))

        tk.Button(bottom_frame, text="Exit", command=self.on_closing,
                  font=('Arial', 10, 'bold'), bg='#666', fg='white',
                  width=10, height=1).pack(side='right')
        
        # Status bar with watermark
        sf = tk.Frame(self.root, relief='sunken', bd=1)
        sf.pack(fill='x', side='bottom', padx=10, pady=(0, 5))
        
        tk.Label(sf, textvariable=self.st, font=('Arial', 9), anchor='w').pack(side='left', fill='x', expand=True, padx=5, pady=2)
        tk.Label(sf, text="Author: Leandro Barbosa", font=('Arial', 8, 'italic'),
                 fg='#999', anchor='e').pack(side='right', padx=10, pady=2)

        self.on_mode_changed()
    
    def open_guideline(self):
        guideline = GUIDELINE_PATH
        try:
            if os.path.exists(guideline):
                os.startfile(guideline)
            else:
                messagebox.showwarning("Guideline", "File not found:\n" + guideline)
        except Exception as e:
            messagebox.showwarning("Guideline", "Could not open file:\n" + str(e))
    
    def update_progress(self, percent, message=""):
        self.progress_var.set(percent)
        self.progress_label.config(text="{}%".format(int(percent)))
        if message:
            self.st.set(message)
            self.progress_status_label.config(text=message,
                                               fg='green' if percent >= 100 else '#666')
        if percent >= 100:
            self.progress_status_label.config(text="Ready", fg='green')
        self.root.update_idletasks()
    
    def browse(self):
        f = filedialog.askopenfilename(filetypes=[("VMAP", "*.vmap"), ("HDF5", "*.h5"), ("All", "*.*")])
        if f:
            new_path = self._norm_path(f)
            loaded_path = self._norm_path(self.reader.filepath) if self.reader and getattr(self.reader, 'filepath', None) else None
            if loaded_path and new_path != loaded_path:
                self.reset_session_state("Previous session cleared. Loading new VMAP...")
            self.fp.set(new_path)
    
    def on_file_path_changed(self, *args):
        path = self.fp.get().strip().strip('"').strip("'")
        if path and os.path.exists(path):
            new_path = self._norm_path(path)
            loaded_path = self._norm_path(self.reader.filepath) if self.reader and getattr(self.reader, 'filepath', None) else None
            if loaded_path and new_path != loaded_path:
                self.reset_session_state("Previous session cleared. Loading new VMAP...")
            self.root.after(100, lambda p=new_path: self.load_vmap(p))
    
    def on_mode_changed(self):
        self.apply_mode_rules()
    
    def apply_mode_rules(self):
        mode = self.viewer_mode.get()
        has_reader = self.reader is not None and len(self.available_outputs) > 0
        self.set_mode_controls_enabled(has_reader)

        if not has_reader:
            if hasattr(self, 'export_all_edges_cb') and self.export_all_edges_cb:
                self.export_all_edges_cb.config(state='disabled')
            self.export_all_edges_var.set(False)
            self.selected_output = None
            self.output_listbox.selection_clear(0, tk.END)
            self.output_listbox.config(state='disabled')
            self.output_info_label.config(text=self.output_summary_text, fg='gray')
            self.generate_btn.config(state='disabled', bg='#808080')
            return
        
        if mode == "harmonic":
            if hasattr(self, 'export_all_edges_cb') and self.export_all_edges_cb:
                self.export_all_edges_cb.config(state='normal')
            self.output_listbox.config(state='disabled')
            if has_reader and 'Displacement' in self.available_outputs:
                idx = self.available_outputs.index('Displacement')
                self.output_listbox.selection_clear(0, tk.END)
                self.output_listbox.selection_set(idx)
                self.output_listbox.activate(idx)
                self.output_listbox.see(idx)
                self.selected_output = 'Displacement'
                self.generate_btn.config(state='normal', bg='#4CAF50')
                self.output_info_label.config(
                    text="Harmonic mode: output locked to Displacement",
                    fg='#2E7D32'
                )
                self.st.set("Mode: Harmonic | Output fixed: Displacement")
            elif has_reader:
                self.selected_output = None
                self.generate_btn.config(state='disabled', bg='#808080')
                self.output_info_label.config(
                    text="Harmonic mode requires Displacement output.",
                    fg='red'
                )
                self.st.set("Displacement output not found for Harmonic mode")
            else:
                self.selected_output = None
                self.generate_btn.config(state='disabled', bg='#808080')
                self.output_info_label.config(text=self.output_summary_text, fg='gray')
        else:
            if hasattr(self, 'export_all_edges_cb') and self.export_all_edges_cb:
                self.export_all_edges_cb.config(state='normal')
            self.output_listbox.config(state='normal')
            self.output_info_label.config(
                text=self.output_summary_text,
                fg='green' if has_reader else 'gray'
            )
            if self.selected_output in self.available_outputs:
                idx = self.available_outputs.index(self.selected_output)
                self.output_listbox.selection_clear(0, tk.END)
                self.output_listbox.selection_set(idx)
                self.output_listbox.activate(idx)
                self.output_listbox.see(idx)
                self.generate_btn.config(state='normal', bg='#4CAF50')
            else:
                self.selected_output = None
                self.output_listbox.selection_clear(0, tk.END)
                self.generate_btn.config(state='disabled', bg='#808080')

    def load_vmap(self, path):
        if not os.path.exists(path):
            return
        
        self.st.set("Auto-loading VMAP file...")
        self.root.update()
        
        try:
            self._close_reader()
            
            self.reader = VMAPReader(path).open()
            
            var_info = self.reader.get_available_variables()
            self.available_outputs = sorted(var_info.keys())
            
            # Ensure listbox is editable by code while repopulating items.
            self.output_listbox.config(state='normal')
            self.output_listbox.delete(0, tk.END)
            self.output_listbox.config(bg='white')
            
            for i, output in enumerate(self.available_outputs):
                var_type = var_info.get(output, '?')
                display_text = "{:2d}. {} [{}]".format(i + 1, output, var_type)
                self.output_listbox.insert(tk.END, display_text)
                # Highlight Displacement in green
                if output == 'Displacement':
                    self.output_listbox.itemconfig(i, bg='#C8E6C9', fg='#2E7D32')
            
            n_vectors = sum(1 for v in var_info.values() if v == 'Vector')
            n_scalars = sum(1 for v in var_info.values() if v == 'Scalar')
            n_tensors = sum(1 for v in var_info.values() if 'Tensor' in v)

            self.output_summary_text = "{} outputs ({} vectors, {} scalars, {} tensors) - Select ONE to keep file size small".format(
                len(self.available_outputs), n_vectors, n_scalars, n_tensors)
            self.selected_output = None
            self.output_listbox.selection_clear(0, tk.END)
            self.apply_mode_rules()
            
            info_msg = "Loaded: {:,} nodes, {:,} elements, {} states, {} outputs".format(
                self.reader.n_nodes, self.reader.n_elements,
                len(self.reader.states), len(self.available_outputs))
            self.st.set(info_msg)
            
        except Exception as e:
            import traceback
            self.st.set("Error loading VMAP: {}".format(str(e)))
            messagebox.showerror("Error loading VMAP", str(e))
            traceback.print_exc()
    
    def on_output_selected(self, event):
        if self.viewer_mode.get() == "harmonic":
            return
        selection = self.output_listbox.curselection()
        if selection:
            idx = selection[0]
            self.selected_output = self.available_outputs[idx]
            self.generate_btn.config(state='normal', bg='#4CAF50')
            self.st.set("Selected: {}".format(self.selected_output))
    
    def generate(self):
        if not self.reader:
            messagebox.showwarning("Error", "Please select a VMAP file first")
            return

        mode = self.viewer_mode.get()
        if mode == "harmonic":
            if 'Displacement' not in self.available_outputs:
                messagebox.showwarning("Error", "Harmonic mode requires Displacement output")
                return
            selected_output = 'Displacement'
        else:
            selected_output = self.selected_output
            if not selected_output:
                messagebox.showwarning("Error", "Please select ONE output from the list")
                return

        export_centroid = False
        if mode != "harmonic":
            try:
                var_locations = self.reader.get_variable_locations()
                needs_element_contour = any(var_locations.get(v, 'node') == 'element' for v in [selected_output] if v)
                if needs_element_contour:
                    export_centroid = True
                    self.st.set("Element output detected: element data auto-embedded for extrapolation support")
            except Exception:
                pass
        export_all_edges = bool(self.export_all_edges_var.get())

        start_ts = time.perf_counter()
        self.update_progress(
            0,
            "Generating ({}) : {} | Element Data: {} | All Edges Opt: {} | Cache: Auto".format(
                mode.capitalize(), selected_output, "On" if export_centroid else "Off",
                "On" if export_all_edges else "Off"
            )
        )
        
        try:
            html_file = generate_html(
                self.reader,
                self.update_progress,
                selected_output=selected_output,
                viewer_mode=mode,
                export_centroid=export_centroid,
                export_all_edges=export_all_edges
            )
            
            html_size_mb = os.path.getsize(html_file) / (1024 * 1024)
            elapsed_s = max(0.0, time.perf_counter() - start_ts)
            if elapsed_s < 60.0:
                elapsed_text = "{:.2f} s".format(elapsed_s)
            else:
                hours = int(elapsed_s // 3600)
                minutes = int((elapsed_s % 3600) // 60)
                seconds = elapsed_s % 60.0
                if hours > 0:
                    elapsed_text = "{} h {:02d} min {:04.1f} s".format(hours, minutes, seconds)
                else:
                    elapsed_text = "{} min {:04.1f} s".format(minutes, seconds)
            
            self.update_progress(100, "Ready")
            webbrowser.open('file://' + os.path.abspath(html_file))
            self.st.set("Done: {} ({})".format(os.path.basename(html_file), elapsed_text))
            
            message = "Generated: {}\n\n".format(os.path.basename(html_file))
            message += "Size: {:.1f} MB\n".format(html_size_mb)
            message += "Generation time: {}\n".format(elapsed_text)
            message += "Nodes: {:,}\n".format(self.reader.n_nodes)
            message += "Elements: {:,}\n".format(self.reader.n_elements)
            message += "States: {}\n\n".format(len(self.reader.states))
            if getattr(self.reader, "material_names", None):
                message += "Materials: {}\n".format(", ".join(self.reader.material_names))
            else:
                message += "Materials: n/a\n"
            message += "Mode: {}\n".format(mode.capitalize())
            message += "Selected Output: {}\n".format(selected_output)
            message += "Element data for extrapolation: {}\n".format("On" if export_centroid else "Off")
            message += "All Edges option in HTML: {}\n".format("On" if export_all_edges else "Off")
            message += "Cache: Auto\n"
            if selected_output != 'Displacement':
                message += "Displacement: included (mesh deformation)"
            
            messagebox.showinfo("Success", message)
            
        except Exception as e:
            import traceback
            self.st.set("Error")
            self.progress_var.set(0)
            messagebox.showerror("Error", str(e) + "\n\n" + traceback.format_exc())
    
    def run(self):
        self.root.mainloop()


def main():
    App().run()

if __name__ == '__main__':
    main()
