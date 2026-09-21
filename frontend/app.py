import streamlit as st
import requests
import pandas as pd
import importlib
import backend.pdf_generator
importlib.reload(backend.pdf_generator)
from backend.pdf_generator import generate_invoice_pdf
from streamlit_calendar import calendar
from streamlit_tags import st_tags

API_URL = "http://127.0.0.1:8000"

if "http_session" not in st.session_state:
    st.session_state.http_session = requests.Session()
session = st.session_state.http_session


st.set_page_config(page_title="Hospital Management System", layout="wide")

import streamlit.components.v1 as components


st.markdown('''
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}

/* Buttons */
.stButton > button {
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s ease-in-out !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0, 210, 255, 0.2) !important;
}

/* Primary Button Gradient */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%) !important;
    color: white !important;
}

/* Secondary Button */
.stButton > button[kind="secondary"] {
    background: #1f242d !important;
    color: #e6e6e6 !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
}
.stButton > button[kind="secondary"]:hover {
    border: 1px solid rgba(0, 210, 255, 0.5) !important;
    color: #00d2ff !important;
}

/* Inputs and Selectboxes */
div[data-baseweb="input"],
div[data-baseweb="select"],
div[data-baseweb="textarea"] {
    background-color: #1a1e24 !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    transition: all 0.3s ease !important;
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"]:focus-within,
div[data-baseweb="textarea"]:focus-within {
    border-color: #00d2ff !important;
    box-shadow: 0 0 0 2px rgba(0, 210, 255, 0.2) !important;
    outline: none !important;
}

/* Kill inner default borders */
div[data-baseweb="input"] > input,
div[data-baseweb="textarea"] > textarea {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    color: white !important;
}
div[data-baseweb="input"] > input:focus,
div[data-baseweb="textarea"] > textarea:focus {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Containers (Cards) */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    background: linear-gradient(180deg, rgba(30, 34, 43, 0.4) 0%, rgba(22, 27, 34, 0.6) 100%) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
}

/* Form container */
[data-testid="stForm"] {
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    background-color: #161b22 !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2) !important;
}

/* Alerts / Info boxes */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}

/* Markdown tables */
table {
    border-radius: 12px;
    overflow: hidden;
    border-collapse: collapse;
    width: 100%;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
th {
    background-color: #1a1e24 !important;
    color: #00d2ff !important;
    font-weight: 600 !important;
    padding: 12px 15px !important;
    border-bottom: 2px solid rgba(255,255,255,0.05) !important;
}
td {
    background-color: #161b22 !important;
    padding: 12px 15px !important;
    border-bottom: 1px solid rgba(255,255,255,0.02) !important;
}
tr:hover td {
    background-color: rgba(0, 210, 255, 0.03) !important;
}

/* Smooth Tabs if any */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 20px !important;
}
</style>
''', unsafe_allow_html=True)


# Helper function to fetch data
@st.cache_data(ttl=2)
def fetch_data(endpoint):
    try:
        response = session.get(f"{API_URL}/{endpoint}/")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []



def format_display_data(data, data_type):
    if not data: return []
    formatted = []
    for item in data:
        if data_type == "users":
            formatted.append({
                "User ID": item.get("id"),
                "Username": item.get("username"),
                "Role": item.get("role", "").capitalize()
            })
        elif data_type == "medicines":
            formatted.append({
                "Med ID": item.get("id"),
                "Name": item.get("name"),
                "Description": item.get("description"),
                "Price (₹)": f"{item.get('price', 0):.2f}",
                "Stock": item.get("stock_quantity")
            })
        elif data_type == "appointments":
            patient_info = ""
            if item.get("patient"):
                p = item["patient"]
                patient_info = f"**Name:** {p.get('name')}<br>**Age:** {p.get('age')}<br>**Blood:** {p.get('blood_group')}"
            else:
                patient_info = f"Patient {item.get('patient_id')}"
                
            doctor_info = ""
            if item.get("doctor"):
                d = item["doctor"]
                doctor_info = f"**Name:** {d.get('name')}<br>**Spec:** {d.get('specialization')}<br>**Contact:** {d.get('contact')}"
            else:
                doctor_info = f"Doctor {item.get('doctor_id')}"
                
            formatted.append({
                "Apt ID": item.get("id"),
                "Date & Time": item.get("datetime"),
                "Patient Info": patient_info,
                "Doctor Info": doctor_info,
                "Status": item.get("status")
            })
        elif data_type == "records":
            patient_info = ""
            if item.get("patient"):
                p = item["patient"]
                patient_info = f"**Name:** {p.get('name')}<br>**Age:** {p.get('age')}<br>**Blood:** {p.get('blood_group')}"
            else:
                patient_info = f"Patient {item.get('patient_id')}"
                
            doctor_info = ""
            if item.get("doctor"):
                d = item["doctor"]
                doctor_info = f"**Name:** {d.get('name')}<br>**Spec:** {d.get('specialization')}"
            else:
                doctor_info = f"Doctor {item.get('doctor_id')}"
                
            formatted.append({
                "Record ID": item.get("id"),
                "Patient": patient_info,
                "Doctor": doctor_info,
                "Diagnosis": item.get("diagnosis_history"),
                "Vitals": item.get("vitals"),
                "Notes": item.get("physician_notes")
            })
        elif data_type == "prescriptions":
            patient_info = ""
            if item.get("patient"):
                p = item["patient"]
                patient_info = f"**Name:** {p.get('name')}<br>**Age:** {p.get('age')}"
            else:
                patient_info = f"Patient {item.get('patient_id')}"
                
            doctor_info = ""
            if item.get("doctor"):
                d = item["doctor"]
                doctor_info = f"**Name:** {d.get('name')}<br>**Spec:** {d.get('specialization')}<br>**Contact:** {d.get('contact')}"
            else:
                doctor_info = f"Doctor {item.get('doctor_id')}"
                
            medicine_info = ""
            if item.get("medicine"):
                m = item["medicine"]
                medicine_info = f"**Name:** {m.get('name')}<br>**Desc:** {m.get('description')}"
            else:
                medicine_info = f"Medicine {item.get('medicine_id')}"
                
            formatted.append({
                "Rx ID": item.get("id"),
                "Doctor": doctor_info,
                "Patient": patient_info,
                "Medicine": medicine_info,
                "Dosage": item.get("dosage"),
                "Instructions": item.get("instructions")
            })
        else:
            formatted.append(item)
    return formatted

def render_table(df):
    if not df.empty:
        st.markdown(df.to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.info("No data available.")

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.profile_id = None

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("Hospital Management System - Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            res = session.post(f"{API_URL}/login/", json={"username": username, "password": password})
            if res.status_code == 200:
                data = res.json()
                st.session_state.logged_in = True
                st.session_state.user_id = data["user_id"]
                st.session_state.username = data["username"]
                st.session_state.role = data["role"]
                st.session_state.profile_id = data["profile_id"]
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.info("Default Admin Account - Username: admin | Password: password")
    
    # Hide the default top bar on login screen
    components.html("""
    <script>
        const deco = window.parent.document.querySelector('[data-testid="stDecoration"]');
        if (deco) deco.style.display = 'none';
        
        // Remove our custom bar if we logged out
        const oldBar = window.parent.document.getElementById('dynamic-top-bar');
        if (oldBar) oldBar.remove();
    </script>
    """, height=0, width=0)
    
    st.stop()

# --- MAIN APP (LOGGED IN) ---

# Dynamic Top Bar Injection (Only when logged in)
components.html("""
<script>
    const parentDoc = window.parent.document;
    const parentWin = window.parent;
    
    // Hide default decoration
    const deco = parentDoc.querySelector('[data-testid="stDecoration"]');
    if (deco) deco.style.display = 'none';
    
    if (!parentDoc.getElementById('dynamic-top-bar')) {
        const bar = parentDoc.createElement('div');
        bar.id = 'dynamic-top-bar';
        
        bar.style.position = 'fixed';
        bar.style.top = '0';
        bar.style.height = '14px';
        bar.style.backgroundColor = '#00d2ff';
        bar.style.zIndex = '999999';
        bar.style.transition = 'height 0.05s ease-out';
        
        parentDoc.body.appendChild(bar);
        
        // Find main section to bind width/left so it doesn't leak into sidebar
        const mainSection = parentDoc.querySelector('.main') || parentDoc.querySelector('[data-testid="stAppViewMain"]');
        
        const syncLayout = () => {
            if (mainSection) {
                const rect = mainSection.getBoundingClientRect();
                bar.style.left = rect.left + 'px';
                bar.style.width = rect.width + 'px';
            }
        };

        if (mainSection && parentWin.ResizeObserver) {
            new parentWin.ResizeObserver(syncLayout).observe(mainSection);
        }
        syncLayout();

        // Use capture phase to catch scroll events from the internal Streamlit divs
        parentWin.addEventListener('scroll', (e) => {
            let st = 0;
            if (e.target && e.target.scrollTop !== undefined) {
                st = e.target.scrollTop;
            } else if (e.target && e.target.scrollingElement) {
                st = e.target.scrollingElement.scrollTop;
            } else {
                st = parentWin.scrollY;
            }
            
            // Apply thinning
            const newHeight = Math.max(0, 14 - (st / 8));
            bar.style.height = newHeight + 'px';
        }, true);
    }
</script>
""", height=0, width=0)

import base64
import os

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

logo_base64 = get_base64_image("frontend/logo.png")

# --- MAIN APP (LOGGED IN) ---
st.sidebar.markdown(f"""
<div style="display: flex; align-items: center; margin-bottom: 20px;">
    <img src="data:image/png;base64,{logo_base64}" width="45" height="45" style="margin-right: 15px; border-radius: 4px;" />
    <span style="color: #00d2ff; font-size: 30px; font-weight: bold; font-family: sans-serif;">HM-DB</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.subheader(f"Welcome, {st.session_state.username}")
st.sidebar.write(f"Role: **{st.session_state.role.upper()}**")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.profile_id = None
    st.rerun()

st.sidebar.markdown("---")

role = st.session_state.role

# Role-based menu
if role == "admin":
    menu = ["User Management", "Ward & Bed Management", "Hospital Queue Override", "System Audits", "Medicine Inventory"]
elif role == "doctor":
    menu = ["Encounter Queue", "Clinical Records (EHR)", "E-Prescribing", "Telemedicine Chat", "Settings"]
elif role == "patient":
    menu = ["Book Appointment", "My Health Record (EHR)", "My Prescriptions & Pharmacy", "Billing & Invoices", "Telemedicine Chat", "Settings"]
else:
    menu = []

if "current_page" not in st.session_state:
    st.session_state.current_page = menu[0] if menu else None

if st.session_state.current_page not in menu and menu:
    st.session_state.current_page = menu[0]

st.sidebar.markdown("<br><p style='font-size: 14px; color: #888; font-weight: 600; margin-bottom: 5px;'>MAIN MENU</p>", unsafe_allow_html=True)

for item in menu:
    # Assign some icons to match the screenshot's vibe
    icon = "🏥"
    if "User" in item: icon = "👥"
    elif "Queue" in item: icon = "📅"
    elif "Audit" in item: icon = "🛡️"
    elif "Inventory" in item: icon = "📦"
    elif "Records" in item: icon = "📁"
    elif "Prescribing" in item or "Prescriptions" in item: icon = "💊"
    elif "Book" in item: icon = "🗓️"

    b_type = "primary" if st.session_state.current_page == item else "secondary"
    
    if st.sidebar.button(f"{icon}  {item}", type=b_type, use_container_width=True):
        st.session_state.current_page = item
        st.rerun()

choice = st.session_state.current_page

# Aggressive scroll lock for specific pages
if choice in ["Encounter Queue", "E-Prescribing"]:
    st.markdown('''
    <style>
    /* Lock scrolling on html/body and Streamlit app containers */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], .stApp, [data-testid="stMain"], .stMain {
        overflow: hidden !important;
        overscroll-behavior: none;
    }
    .block-container {
        padding-bottom: 0rem !important;
        margin-bottom: 0rem !important;
    }
    footer { display: none !important; }
    </style>
    ''', unsafe_allow_html=True)


st.markdown('''
<style>
/* Remove the yellow box from today's date in FullCalendar */
.fc-day-today {
    background-color: transparent !important;
}
</style>
''', unsafe_allow_html=True)


# ==========================================
# ADMIN VIEWS
# ==========================================
if role == "admin":
    if choice == "User Management":
        st.header("User Accounts & Auth (Provisioning)")
        st.write("CRUD capabilities for system-wide roles.")
        
        with st.form("create_user"):
            st.subheader("Provision New Account")
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password")
            new_role = st.selectbox("Role", ["doctor", "patient"])
            name = st.text_input("Full Name (for profile)")
            contact = st.text_input("Contact Info")
            
            # Specifics
            spec = st.text_input("Specialization (if Doctor)")
            age = st.number_input("Age (if Patient)", min_value=0)
            blood = st.text_input("Blood Group (if Patient)")
            
            if st.form_submit_button("Create Account"):
                # 1. Create User
                user_res = session.post(f"{API_URL}/users/", json={"username": new_user, "password": new_pass, "role": new_role})
                if user_res.status_code == 200:
                    uid = user_res.json()["id"]
                    # 2. Create Profile
                    if new_role == "doctor":
                        session.post(f"{API_URL}/doctors/", json={"user_id": uid, "name": name, "specialization": spec, "contact": contact})
                    elif new_role == "patient":
                        session.post(f"{API_URL}/patients/", json={"user_id": uid, "name": name, "age": age, "blood_group": blood, "contact": contact})
                    st.success("Account provisioned successfully!")
                else:
                    st.error("Error creating user.")
                    
        st.subheader("System Users")
        
        if "confirm_delete_user" not in st.session_state:
            st.session_state.confirm_delete_user = None
            
        users = fetch_data("users")
        if users:
            for user in users:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
                    
                    with c1:
                        st.markdown(f"**ID:** {user['id']}")
                    with c2:
                        st.markdown(f"**Username:** {user['username']}")
                    with c3:
                        st.markdown(f"**Role:** {user.get('role', 'Unknown').capitalize()}")
                        
                    with c4:
                        # If this user is currently marked for deletion confirmation
                        if st.session_state.confirm_delete_user == user['id']:
                            st.warning("Delete this user?", icon="⚠️")
                            y_col, n_col = st.columns(2)
                            if y_col.button("Yes", key=f"del_y_{user['id']}", type="primary"):
                                res = session.delete(f"{API_URL}/users/{user['id']}")
                                if res.status_code == 200:
                                    st.toast("User deleted successfully!", icon="✅")
                                    st.session_state.confirm_delete_user = None
                                    fetch_data.clear() # clear cache
                                    st.rerun()
                                else:
                                    st.error("Error deleting user")
                            if n_col.button("No", key=f"del_n_{user['id']}"):
                                st.session_state.confirm_delete_user = None
                                st.rerun()
                        else:
                            # Default Delete Button
                            if st.button("🗑️ Delete", key=f"del_{user['id']}", type="secondary"):
                                st.session_state.confirm_delete_user = user['id']
                                st.rerun()

    
    elif choice == "Ward & Bed Management":
        st.header("Ward & Bed Management")
        st.write("Visually manage hospital bed allocations and patient admissions.")
        
        beds = fetch_data("beds")
        patients = fetch_data("patients")
        
        # If no beds exist, initialize some dummy beds
        if not beds:
            st.info("Initializing hospital wards...")
            for i in range(1, 11):
                session.post(f"{API_URL}/beds/", json={"ward": "General Ward", "bed_number": f"G-{i}", "status": "Available"})
            for i in range(1, 6):
                session.post(f"{API_URL}/beds/", json={"ward": "ICU", "bed_number": f"ICU-{i}", "status": "Available"})
            st.rerun()
            
        # Group beds by ward
        wards = {}
        for b in beds:
            wards.setdefault(b['ward'], []).append(b)
            
        for ward_name, ward_beds in wards.items():
            st.subheader(f"🛏️ {ward_name}")
            cols = st.columns(5)
            for idx, bed in enumerate(ward_beds):
                with cols[idx % 5]:
                    with st.container(border=True):
                        # Color coding
                        color = "#28a745" if bed['status'] == 'Available' else "#dc3545" if bed['status'] == 'Occupied' else "#ffc107"
                        st.markdown(f"<h3 style='text-align:center; color:{color}; margin-bottom:0;'>{bed['bed_number']}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; font-size:12px; margin-top:0;'>{bed['status']}</p>", unsafe_allow_html=True)
                        
                        if bed['status'] == 'Available':
                            with st.popover("Assign Patient", use_container_width=True):
                                selected_p = st.selectbox("Select Patient", [p['id'] for p in patients], format_func=lambda x: next(p['name'] for p in patients if p['id']==x), key=f"sel_{bed['id']}")
                                if st.button("Admit", key=f"admit_{bed['id']}", type="primary"):
                                    session.put(f"{API_URL}/beds/{bed['id']}", json={"ward": bed['ward'], "bed_number": bed['bed_number'], "status": "Occupied", "patient_id": selected_p})
                                    # Log action
                                    session.post(f"{API_URL}/audits/", json={"user": "Admin", "action": f"Admitted Patient {selected_p} to {bed['bed_number']}", "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")})
                                    fetch_data.clear()
                                    st.rerun()
                                    
                        elif bed['status'] == 'Occupied':
                            p_name = next((p['name'] for p in patients if p['id'] == bed['patient_id']), "Unknown")
                            st.caption(f"👤 {p_name}")
                            if st.button("Discharge", key=f"dis_{bed['id']}", use_container_width=True):
                                session.put(f"{API_URL}/beds/{bed['id']}", json={"ward": bed['ward'], "bed_number": bed['bed_number'], "status": "Cleaning", "patient_id": None})
                                session.post(f"{API_URL}/audits/", json={"user": "Admin", "action": f"Discharged Patient {bed['patient_id']} from {bed['bed_number']}", "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")})
                                fetch_data.clear()
                                st.rerun()
                                
                        elif bed['status'] == 'Cleaning':
                            if st.button("Mark Clean", key=f"clean_{bed['id']}", use_container_width=True):
                                session.put(f"{API_URL}/beds/{bed['id']}", json={"ward": bed['ward'], "bed_number": bed['bed_number'], "status": "Available", "patient_id": None})
                                fetch_data.clear()
                                st.rerun()

    elif choice == "Hospital Queue Override":
        st.header("Appointments & Queue (Override)")
        st.write("Hospital-wide schedule adjustments and cancellations.")
        
        apps = fetch_data("appointments")
        if apps:
            for app in apps:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    patient = app.get("patient", {})
                    doctor = app.get("doctor", {})
                    p_name = patient.get("name", f"Patient {app.get('patient_id')}")
                    d_name = doctor.get("name", f"Doctor {app.get('doctor_id')}")
                    
                    with col1:
                        st.markdown(f"**Patient:** {p_name}<br>**Doctor:** {d_name}<br>**Time:** `{app.get('datetime')}`", unsafe_allow_html=True)
                        
                    with col2:
                        status = app.get("status")
                        color = "#28a745" if status in ["Accepted", "Completed"] else "#ffc107" if status == "Pending" else "#dc3545"
                        st.markdown(f"**Status:**<br><span style='color:{color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
                        
                    with col3:
                        opts = ["Cancelled", "Open", "Pending", "Accepted", "Postponed", "Completed"]
                        idx = opts.index(status) if status in opts else 0
                        new_status = st.selectbox("Action", opts, index=idx, key=f"adm_app_{app['id']}", label_visibility="collapsed")
                        
                        if new_status != status:
                            session.put(f"{API_URL}/appointments/{app['id']}", json={"status": new_status})
                            st.rerun()
                            
            st.markdown("<hr>", unsafe_allow_html=True)
        else:
            st.info("No appointments in system.")

    elif choice == "System Audits":
        st.header("HIPAA System Audit Logs")
        st.write("Tamper-proof terminal logging of all system actions.")
        
        audits = fetch_data("audits")
        
        st.markdown('''
        <style>
        .audit-terminal {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            color: #00ff00;
            height: 600px;
            overflow-y: auto;
        }
        .audit-line { margin: 0; padding: 2px 0; font-size: 13px; border-bottom: 1px dotted #30363d; }
        .audit-time { color: #8b949e; margin-right: 15px; }
        .audit-user { color: #58a6ff; font-weight: bold; margin-right: 15px; }
        </style>
        ''', unsafe_allow_html=True)
        
        if audits:
            log_html = "<div class='audit-terminal'>"
            for log in audits:
                log_html += f"<div class='audit-line'><span class='audit-time'>[{log['timestamp']}]</span><span class='audit-user'>{log['user']}</span> > {log['action']}</div>"
            log_html += "</div>"
            st.markdown(log_html, unsafe_allow_html=True)
        else:
            st.info("No audit logs available.")
        
    elif choice == "Medicine Inventory":
        st.header("Medicine Inventory Management")
        with st.form("add_medicine"):
            name = st.text_input("Name")
            desc = st.text_input("Description")
            price = st.number_input("Price", min_value=0.0)
            stock = st.number_input("Stock Quantity", min_value=0)
            if st.form_submit_button("Add Medicine"):
                session.post(f"{API_URL}/medicines/", json={"name": name, "description": desc, "price": price, "stock_quantity": stock})
                st.success("Medicine added")
        render_table(pd.DataFrame(format_display_data(fetch_data("medicines"), "medicines")))

# ==========================================
# DOCTOR VIEWS
# ==========================================
elif role == "doctor":
    doctor_id = st.session_state.profile_id
    
    if choice == "Encounter Queue":
        st.header("Appointments & Queue")
        st.write("Click on a day in the calendar to view and manage requested time slots.")
        
        apps = fetch_data("appointments")
        my_apps = [a for a in apps if a["doctor_id"] == doctor_id]
        
        if "doc_selected_date" not in st.session_state:
            st.session_state.doc_selected_date = None
            
        cal_data = st.session_state.get("doctor_cal", {})
        if cal_data and cal_data.get("callback") == "dateClick":
            st.session_state.doc_selected_date = cal_data["dateClick"]["date"].split("T")[0]
        elif cal_data and cal_data.get("callback") == "eventClick":
            st.session_state.doc_selected_date = cal_data["eventClick"]["event"]["extendedProps"]["exact_date"]
            
        events = []
        if st.session_state.doc_selected_date:
            events.append({
                "start": st.session_state.doc_selected_date,
                "display": "background",
                "backgroundColor": "rgba(0, 210, 255, 0.3)" # Cyan highlight
            })
            
        for app in my_apps:
            date_str = app["datetime"].split(" ")[0] if " " in app["datetime"] else app["datetime"]
            status = app.get("status")
            color = "#ffc107" if status == "Pending" else "#28a745" if status in ["Accepted", "Completed"] else "#dc3545"
            time_part = app["datetime"].split(" ", 1)[-1] if " " in app["datetime"] else ""
            events.append({
                "title": time_part,
                "start": date_str,
                "backgroundColor": color,
                "borderColor": color,
                "extendedProps": {"exact_date": date_str}
            })
            
        cal_col, list_col = st.columns([1.5, 1], gap="large")
        
        with cal_col:
            cal_state = calendar(events=events, options={
                "headerToolbar": {"left": "prev,next", "center": "title", "right": "today"},
                "initialView": "dayGridMonth",
                "aspectRatio": 1.6,
                "timeZone": "UTC"
            }, custom_css='''
            .fc-daygrid-day-frame, .fc-event { cursor: pointer !important; transition: background-color 0.2s ease !important; }
            .fc-daygrid-day-frame:hover { background-color: rgba(255, 255, 255, 0.05) !important; }
            .fc-day-today { background-color: transparent !important; }
            .fc-scroller { overflow: visible !important; }
            .fc-daygrid-day-frame { height: 100% !important; min-height: 100% !important; display: flex; flex-direction: column; }
            .fc-daygrid-day-events { min-height: 10px !important; margin-bottom: 0px !important; }
            .fc-daygrid-event-harness { margin-top: 1px !important; }
            .fc { border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important; }
            ''', key="doctor_cal")
        
        if cal_state.get("callback") == "dateClick":
            st.session_state.doc_selected_date = cal_state["dateClick"]["date"].split("T")[0]
        elif cal_state.get("callback") == "eventClick":
            st.session_state.doc_selected_date = cal_state["eventClick"]["event"]["extendedProps"]["exact_date"]
            
        selected_date = st.session_state.doc_selected_date
            
        with list_col:
            if selected_date:
                st.subheader(f"Requests for {selected_date}")
                
                day_apps = [a for a in my_apps if a["datetime"].startswith(selected_date)]
                
                if day_apps:
                    for app in day_apps:
                        with st.container(border=True):
                            col1, col2 = st.columns([2, 1])
                            
                            patient = app.get("patient", {})
                            p_name = patient.get("name", f"Patient {app.get('patient_id')}")
                            
                            with col1:
                                st.markdown(f"**Patient:** {p_name}<br>**Time:** `{app.get('datetime').split(' ')[-2] + ' ' + app.get('datetime').split(' ')[-1] if ' ' in app.get('datetime') else app.get('datetime')}`", unsafe_allow_html=True)
                                
                            with col2:
                                status = app.get("status")
                                opts = ["Pending", "Accepted", "Rejected", "Postponed", "Completed"]
                                idx = opts.index(status) if status in opts else 0
                                new_status = st.selectbox("Action", opts, index=idx, key=f"doc_app_{app['id']}", label_visibility="collapsed")
                                
                                if new_status != status:
                                    session.put(f"{API_URL}/appointments/{app['id']}", json={"status": new_status})
                                    fetch_data.clear()
                                    st.rerun()
                else:
                    st.info("No appointments on this day.")
            else:
                st.info("👈 Select a date on the calendar to manage slots.")

    elif choice == "Clinical Records (EHR)":
        st.header("Clinical Records (Scoped Write)")
        st.write("Full access to consult notes & vitals of assigned patients.")
        
        patients = fetch_data("patients")
        
        with st.form("add_ehr"):
            patient_id = st.selectbox("Select Patient", [p["id"] for p in patients], format_func=lambda x: next(p["name"] for p in patients if p["id"] == x))
            history = st.text_area("Diagnosis History")
            vitals = st.text_input("Vitals (e.g. BP 120/80, HR 72)")
            notes = st.text_area("Physician Consult Notes")
            
            if st.form_submit_button("Save Clinical Record"):
                res = session.post(f"{API_URL}/records/", json={
                    "patient_id": patient_id, "doctor_id": doctor_id,
                    "diagnosis_history": history, "vitals": vitals, "physician_notes": notes
                })
                if res.status_code == 200:
                    st.success("EHR saved.")
                    
        records = fetch_data("records")
        my_records = [r for r in records if r["doctor_id"] == doctor_id]
        if my_records:
            st.subheader("Your Authored Records")
            render_table(pd.DataFrame(format_display_data(my_records, "records")))

    elif choice == "E-Prescribing":
        st.header("Prescriptions (Authorize)")
        st.write("Issue Rx, update dosages, and sign digital pharmacy orders.")
        
        patients = fetch_data("patients")
        medicines = fetch_data("medicines")
        
        if patients:
            patient_id = st.selectbox("Patient", [p["id"] for p in patients], format_func=lambda x: next(p["name"] for p in patients if p["id"] == x))
            
            # Using st_tags to allow both selecting from suggestions AND typing a custom value in the SAME input box
            med_names = [m["name"] for m in medicines]
            selected_meds = st_tags(
                label='Medicine (Type or select from suggestions)',
                text='Press enter to add',
                value=[],
                suggestions=med_names,
                maxtags=1,
                key='med_tags'
            )
                
            dosage = st.text_input("Dosage")
            instructions = st.text_area("Instructions")
            
            if st.button("Issue Prescription", type="primary"):
                if not selected_meds:
                    st.error("Please enter or select a medicine.")
                else:
                    med_name = selected_meds[0]
                    
                    # Try to find the medicine in the existing inventory by name
                    existing_med = next((m for m in medicines if m["name"].lower() == med_name.lower()), None)
                    
                    if existing_med:
                        final_med_id = existing_med["id"]
                    else:
                        # Create the custom medicine dynamically in the DB first
                        res = session.post(f"{API_URL}/medicines/", json={
                            "name": med_name, "description": "Custom prescribed by doctor", "price": 0.0, "stock_quantity": 0
                        })
                        if res.status_code == 200:
                            final_med_id = res.json()["id"]
                        else:
                            st.error("Error saving custom medicine to database.")
                            final_med_id = None
                            
                    if final_med_id:
                        res = session.post(f"{API_URL}/prescriptions/", json={
                            "doctor_id": doctor_id, "patient_id": patient_id, "medicine_id": final_med_id,
                            "dosage": dosage, "instructions": instructions
                        })
                        if res.status_code == 200:
                            st.success("Prescription successfully issued.")
                            fetch_data.clear() # Clear cache so the new medicine shows up instantly!
        else:
            st.warning("No patients available.")


    elif choice == "Telemedicine Chat":
        st.header("Telemedicine Chat")
        st.write("Securely message your patients.")
        
        patients = fetch_data("patients")
        if not patients:
            st.warning("No patients registered yet.")
        else:
            selected_patient_id = st.selectbox("Select Patient to Message", [p['id'] for p in patients], format_func=lambda x: next(p['name'] for p in patients if p['id']==x))
            
            messages = fetch_data("messages")
            patient_user_id = next((p['user_id'] for p in patients if p['id'] == selected_patient_id), None)
            doc_user_id = st.session_state.user_id
            
            # Filter messages between this doctor and the selected patient
            chat_history = [m for m in messages if (m['sender_id'] == doc_user_id and m['receiver_id'] == patient_user_id) or (m['sender_id'] == patient_user_id and m['receiver_id'] == doc_user_id)]
            
            chat_html = "<div style='height: 400px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding: 10px; background-color: #0e1117; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);'>"
            for msg in chat_history:
                is_me = msg['sender_id'] == doc_user_id
                align = "flex-end" if is_me else "flex-start"
                bg = "#00d2ff" if is_me else "#1f242d"
                color = "white" if is_me else "#e6e6e6"
                chat_html += f"<div style='align-self: {align}; background-color: {bg}; color: {color}; padding: 10px 15px; border-radius: 15px; max-width: 70%; width: fit-content;'>{msg['content']}<br><span style='font-size:10px; opacity: 0.7;'>{msg['timestamp']}</span></div>"
            chat_html += "</div>"
            st.markdown(chat_html, unsafe_allow_html=True)
            
            new_msg = st.chat_input("Type your message to the patient...")
            if new_msg:
                session.post(f"{API_URL}/messages/", json={"sender_id": doc_user_id, "receiver_id": patient_user_id, "content": new_msg, "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")})
                fetch_data.clear()
                st.rerun()


    elif choice == "Settings":
        st.header("Account Settings")
        st.write("Manage your account security.")
        
        with st.container(border=True):
            st.subheader("Change Password")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            if st.button("Update Password"):
                if new_pass and new_pass == confirm_pass:
                    res = session.put(f"{API_URL}/users/{st.session_state.user_id}/password", json={"password": new_pass})
                    if res.status_code == 200:
                        session.post(f"{API_URL}/audits/", json={"user": f"{role.capitalize()} {st.session_state.user_id}", "action": "Changed account password", "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")})
                        st.success("Password updated successfully!")
                        st.balloons()
                    else:
                        st.error("Failed to update password.")
                else:
                    st.error("Passwords do not match or are empty.")

# ==========================================
# PATIENT VIEWS
# ==========================================
elif role == "patient":
    patient_id = st.session_state.profile_id
    
    if choice == "Book Appointment":
        st.header("Appointments & Queue (Book)")
        st.write("Click a day on the calendar to select your preferred date.")
        
        # Persistent state to prevent double-rerun reset
        if "patient_selected_date" not in st.session_state:
            st.session_state.patient_selected_date = None
            
        cal_data = st.session_state.get("patient_cal", {})
        if cal_data and cal_data.get("callback") == "dateClick":
            st.session_state.patient_selected_date = cal_data["dateClick"]["date"].split("T")[0]
            
        events = []
        if st.session_state.patient_selected_date:
            events.append({
                "start": st.session_state.patient_selected_date,
                "display": "background",
                "backgroundColor": "rgba(0, 210, 255, 0.3)" # Cyan highlight
            })
        
        cal_col, form_col = st.columns([1.5, 1], gap="large")
        
        with cal_col:
            cal_state = calendar(events=events, options={
                "headerToolbar": {"left": "prev,next", "center": "title", "right": "today"},
                "initialView": "dayGridMonth",
                "aspectRatio": 1.6,
                "timeZone": "UTC"
            }, custom_css='''
            .fc-daygrid-day-frame, .fc-event { cursor: pointer !important; transition: background-color 0.2s ease !important; }
            .fc-daygrid-day-frame:hover { background-color: rgba(255, 255, 255, 0.05) !important; }
            .fc-day-today { background-color: transparent !important; }
            .fc-scroller { overflow: visible !important; }
            .fc-daygrid-day-frame { height: 100% !important; min-height: 100% !important; display: flex; flex-direction: column; }
            .fc-daygrid-day-events { min-height: 10px !important; margin-bottom: 0px !important; }
            .fc-daygrid-event-harness { margin-top: 1px !important; }
            .fc { border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important; }
            ''', key="patient_cal")
            
            if cal_state.get("callback") == "dateClick":
                st.session_state.patient_selected_date = cal_state["dateClick"]["date"].split("T")[0]
                
        selected_date = st.session_state.patient_selected_date
            
        with form_col:
            if selected_date:
                st.subheader(f"Book for {selected_date}")
                doctors = fetch_data("doctors")
                
                with st.form("book_visit"):
                    doc_id = st.selectbox("Select Doctor", [d["id"] for d in doctors], format_func=lambda x: next(d["name"] for d in doctors if d["id"] == x))
                    time_slot = st.selectbox("Select Time Slot", ["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM"])
                    
                    if st.form_submit_button("Request Booking", type="primary"):
                        dt = f"{selected_date} {time_slot}"
                        res = session.post(f"{API_URL}/appointments/", json={
                            "patient_id": patient_id, "doctor_id": doc_id, "datetime": dt, "status": "Pending"
                        })
                        if res.status_code == 200:
                            st.success("Booking requested! Waiting for doctor to accept.")
                            fetch_data.clear()
            else:
                st.info("👈 Select a date on the calendar to see available slots.")
                
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("My Upcoming Visits")
        apps = fetch_data("appointments")
        my_apps = [a for a in apps if a["patient_id"] == patient_id]
        if my_apps:
            render_table(pd.DataFrame(format_display_data(my_apps, "appointments")))

    elif choice == "My Health Record (EHR)":
        st.header("Clinical Records (Read Only)")
        st.write("View own diagnosis history, vitals, and physician notes.")
        
        records = fetch_data("records")
        my_records = [r for r in records if r["patient_id"] == patient_id]
        if my_records:
            render_table(pd.DataFrame(format_display_data(my_records, "records")))
        else:
            st.info("No records found.")

    elif choice == "My Prescriptions & Pharmacy":
        st.header("Prescriptions (Read Only)")
        st.write("View and download authorized digital prescriptions.")
        
        prescriptions = fetch_data("prescriptions")
        my_rx = [p for p in prescriptions if p["patient_id"] == patient_id]
        if my_rx:
            render_table(pd.DataFrame(format_display_data(my_rx, "prescriptions")))
        else:
            st.info("No prescriptions.")
            
        st.subheader("Reserve Medication at Pharmacy")
        medicines = fetch_data("medicines")
        if medicines:
            med_id = st.selectbox("Medicine", [m["id"] for m in medicines], format_func=lambda x: next(m["name"] for m in medicines if m["id"] == x))
            
            # Find selected medicine price
            selected_med = next(m for m in medicines if m["id"] == med_id)
            unit_price = selected_med.get("price", 0.0)
            
            qty = st.number_input("Quantity", min_value=1)
            total_price = unit_price * qty
            
            # Show the requested pricing boxes
            col1, col2 = st.columns(2)
            col1.info(f"**Price per unit:** ₹{unit_price:,.2f}")
            col2.success(f"**Total Amount:** ₹{total_price:,.2f}")
            
            if st.button("Reserve"):
                res = session.post(f"{API_URL}/reservations/", json={
                    "patient_id": patient_id, "medicine_id": med_id, "quantity": qty
                })
                if res.status_code == 200:
                    med_name = selected_med.get("name", "Medicine")
                    session.post(f"{API_URL}/invoices/", json={
                        "patient_id": patient_id,
                        "amount": total_price,
                        "description": f"Pharmacy: {qty}x {med_name}",
                        "created_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    session.post(f"{API_URL}/audits/", json={"user": f"Patient {patient_id}", "action": f"Reserved {qty}x {med_name}", "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")})
                    
                    st.toast("Reserved for pickup! 🎈 Invoice generated.")
                    fetch_data.clear()
                    st.rerun()
                else:
                    st.error("Failed. Might be out of stock.")
        else:
            st.warning("No medicines available right now.")

    elif choice == "Telemedicine Chat":
        st.header("Telemedicine Chat")
        st.write("Securely message your doctors.")
        
        doctors = fetch_data("doctors")
        if not doctors:
            st.warning("No doctors available.")
        else:
            selected_doc_id = st.selectbox("Select Doctor to Message", [d['id'] for d in doctors], format_func=lambda x: next(d['name'] for d in doctors if d['id']==x))
            
            messages = fetch_data("messages")
            doc_user_id = next((d['user_id'] for d in doctors if d['id'] == selected_doc_id), None)
            pat_user_id = st.session_state.user_id
            
            chat_history = [m for m in messages if (m['sender_id'] == pat_user_id and m['receiver_id'] == doc_user_id) or (m['sender_id'] == doc_user_id and m['receiver_id'] == pat_user_id)]
            
            chat_html = "<div style='height: 400px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding: 10px; background-color: #0e1117; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);'>"
            for msg in chat_history:
                is_me = msg['sender_id'] == pat_user_id
                align = "flex-end" if is_me else "flex-start"
                bg = "#00d2ff" if is_me else "#1f242d"
                color = "white" if is_me else "#e6e6e6"
                chat_html += f"<div style='align-self: {align}; background-color: {bg}; color: {color}; padding: 10px 15px; border-radius: 15px; max-width: 70%; width: fit-content;'>{msg['content']}<br><span style='font-size:10px; opacity: 0.7;'>{msg['timestamp']}</span></div>"
            chat_html += "</div>"
            st.markdown(chat_html, unsafe_allow_html=True)
            
            new_msg = st.chat_input("Type your message to the doctor...")
            if new_msg:
                session.post(f"{API_URL}/messages/", json={"sender_id": pat_user_id, "receiver_id": doc_user_id, "content": new_msg, "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")})
                fetch_data.clear()
                st.rerun()

    elif choice == "Billing & Invoices":
        st.header("Billing & Payments")
        st.write("Manage and pay your hospital invoices securely.")
        
        invoices = fetch_data("invoices")
        my_invoices = [inv for inv in invoices if inv['patient_id'] == patient_id]
        
        if not my_invoices:
            st.success("You have no pending invoices! 🎉")
        else:
            for inv in my_invoices:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                    c1.write(f"**Description:** {inv['description']}")
                    c2.write(f"**Amount:** ₹{inv['amount']:,.2f}")
                    color = "#28a745" if inv['status'] == "Paid" else "#dc3545"
                    c3.markdown(f"**Status:** <span style='color:{color}'>{inv['status']}</span>", unsafe_allow_html=True)
                    
                    if inv['status'] == "Pending":
                        with c4:
                            with st.popover("Pay Now"):
                                st.write("Mock Secure Checkout")
                                st.text_input("Card Number", placeholder="XXXX-XXXX-XXXX-XXXX", key=f"card_{inv['id']}")
                                c_a, c_b = st.columns(2)
                                c_a.text_input("Expiry", placeholder="MM/YY", key=f"exp_{inv['id']}")
                                c_b.text_input("CVV", placeholder="123", key=f"cvv_{inv['id']}")
                                if st.button("Submit Payment", type="primary", key=f"pay_{inv['id']}"):
                                    session.put(f"{API_URL}/invoices/{inv['id']}/pay")
                                    session.post(f"{API_URL}/audits/", json={"user": f"Patient {patient_id}", "action": f"Paid Invoice #{inv['id']} (₹{inv['amount']})", "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")})
                                    st.toast("Payment Successful! ✅")
                                    fetch_data.clear()
                                    st.rerun()
                    else:
                        with c4:
                            pdf_bytes = generate_invoice_pdf(inv)
                            st.download_button(
                                label="📄 Export PDF",
                                data=pdf_bytes,
                                file_name=f"HMS_Invoice_{inv['id']}.pdf",
                                mime="application/pdf",
                                key=f"pdf_{inv['id']}"
                            )

    elif choice == "Settings":
        st.header("Account Settings")
        st.write("Manage your account security.")
        
        with st.container(border=True):
            st.subheader("Change Password")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            if st.button("Update Password"):
                if new_pass and new_pass == confirm_pass:
                    res = session.put(f"{API_URL}/users/{st.session_state.user_id}/password", json={"password": new_pass})
                    if res.status_code == 200:
                        session.post(f"{API_URL}/audits/", json={"user": f"{role.capitalize()} {st.session_state.user_id}", "action": "Changed account password", "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")})
                        st.success("Password updated successfully!")
                        st.balloons()
                    else:
                        st.error("Failed to update password.")
                else:
                    st.error("Passwords do not match or are empty.")
