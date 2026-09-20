import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Hospital Management System", layout="wide")

import streamlit.components.v1 as components

# Helper function to fetch data
@st.cache_data(ttl=2)
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}/")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

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
            res = requests.post(f"{API_URL}/login/", json={"username": username, "password": password})
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
    menu = ["User Management", "Hospital Queue Override", "System Audits", "Medicine Inventory"]
elif role == "doctor":
    menu = ["Encounter Queue", "Clinical Records (EHR)", "E-Prescribing"]
elif role == "patient":
    menu = ["Book Appointment", "My Health Record (EHR)", "My Prescriptions & Pharmacy"]
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
                user_res = requests.post(f"{API_URL}/users/", json={"username": new_user, "password": new_pass, "role": new_role})
                if user_res.status_code == 200:
                    uid = user_res.json()["id"]
                    # 2. Create Profile
                    if new_role == "doctor":
                        requests.post(f"{API_URL}/doctors/", json={"user_id": uid, "name": name, "specialization": spec, "contact": contact})
                    elif new_role == "patient":
                        requests.post(f"{API_URL}/patients/", json={"user_id": uid, "name": name, "age": age, "blood_group": blood, "contact": contact})
                    st.success("Account provisioned successfully!")
                else:
                    st.error("Error creating user.")
                    
        st.subheader("System Users")
        users = fetch_data("users")
        if users:
            st.dataframe(pd.DataFrame(users))

    elif choice == "Hospital Queue Override":
        st.header("Appointments & Queue (Override)")
        st.write("Hospital-wide schedule adjustments and cancellations.")
        
        apps = fetch_data("appointments")
        if apps:
            df = pd.DataFrame(apps)
            st.dataframe(df)
            
            with st.form("override_app"):
                st.subheader("Override Status")
                app_id = st.selectbox("Select Appointment ID", [a["id"] for a in apps])
                new_status = st.selectbox("New Status", ["Cancelled", "Open", "Pending", "Accepted", "Postponed"])
                if st.form_submit_button("Apply Override"):
                    res = requests.put(f"{API_URL}/appointments/{app_id}", json={"status": new_status})
                    if res.status_code == 200:
                        st.success("Status overridden.")
                        st.rerun()
        else:
            st.info("No appointments in system.")

    elif choice == "System Audits":
        st.header("Clinical Records & Prescriptions")
        st.error("NO READ/WRITE ACCESS. Metadata audit only (HIPAA / GDPR safe-harbor).")
        st.write("You are denied access to view medical details or medication orders.")
        
    elif choice == "Medicine Inventory":
        st.header("Medicine Inventory Management")
        with st.form("add_medicine"):
            name = st.text_input("Name")
            desc = st.text_input("Description")
            price = st.number_input("Price", min_value=0.0)
            stock = st.number_input("Stock Quantity", min_value=0)
            if st.form_submit_button("Add Medicine"):
                requests.post(f"{API_URL}/medicines/", json={"name": name, "description": desc, "price": price, "stock_quantity": stock})
                st.success("Medicine added")
        st.dataframe(pd.DataFrame(fetch_data("medicines")))

# ==========================================
# DOCTOR VIEWS
# ==========================================
elif role == "doctor":
    doctor_id = st.session_state.profile_id
    
    if choice == "Encounter Queue":
        st.header("Appointments & Queue")
        st.write("Accept, reject, postpone, and mark visits completed.")
        
        apps = fetch_data("appointments")
        my_apps = [a for a in apps if a["doctor_id"] == doctor_id]
        
        if my_apps:
            st.dataframe(pd.DataFrame(my_apps))
            
            with st.form("manage_queue"):
                app_id = st.selectbox("Select Appointment ID", [a["id"] for a in my_apps])
                new_status = st.selectbox("Update Status", ["Accepted", "Rejected", "Postponed", "Completed"])
                if st.form_submit_button("Update Status"):
                    res = requests.put(f"{API_URL}/appointments/{app_id}", json={"status": new_status})
                    if res.status_code == 200:
                        st.success("Queue updated.")
                        st.rerun()
        else:
            st.info("No appointments assigned to you.")

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
                res = requests.post(f"{API_URL}/records/", json={
                    "patient_id": patient_id, "doctor_id": doctor_id,
                    "diagnosis_history": history, "vitals": vitals, "physician_notes": notes
                })
                if res.status_code == 200:
                    st.success("EHR saved.")
                    
        records = fetch_data("records")
        my_records = [r for r in records if r["doctor_id"] == doctor_id]
        if my_records:
            st.subheader("Your Authored Records")
            st.dataframe(pd.DataFrame(my_records))

    elif choice == "E-Prescribing":
        st.header("Prescriptions (Authorize)")
        st.write("Issue Rx, update dosages, and sign digital pharmacy orders.")
        
        patients = fetch_data("patients")
        medicines = fetch_data("medicines")
        
        with st.form("issue_rx"):
            patient_id = st.selectbox("Patient", [p["id"] for p in patients], format_func=lambda x: next(p["name"] for p in patients if p["id"] == x))
            medicine_id = st.selectbox("Medicine", [m["id"] for m in medicines], format_func=lambda x: next(m["name"] for m in medicines if m["id"] == x))
            dosage = st.text_input("Dosage")
            instructions = st.text_area("Instructions")
            
            if st.form_submit_button("Issue Prescription"):
                requests.post(f"{API_URL}/prescriptions/", json={
                    "doctor_id": doctor_id, "patient_id": patient_id, "medicine_id": medicine_id,
                    "dosage": dosage, "instructions": instructions
                })
                st.success("Prescription issued.")

# ==========================================
# PATIENT VIEWS
# ==========================================
elif role == "patient":
    patient_id = st.session_state.profile_id
    
    if choice == "Book Appointment":
        st.header("Appointments & Queue (Book)")
        st.write("Create booking in open slots, view own upcoming visits.")
        
        doctors = fetch_data("doctors")
        
        with st.form("book_visit"):
            doc_id = st.selectbox("Select Doctor", [d["id"] for d in doctors], format_func=lambda x: next(d["name"] for d in doctors if d["id"] == x))
            dt = st.text_input("Requested Date & Time (e.g. 2026-10-01 10:00 AM)")
            
            if st.form_submit_button("Request Booking"):
                res = requests.post(f"{API_URL}/appointments/", json={
                    "patient_id": patient_id, "doctor_id": doc_id, "datetime": dt, "status": "Pending"
                })
                if res.status_code == 200:
                    st.success("Booking requested! Waiting for doctor to accept.")
                    
        st.subheader("My Upcoming Visits")
        apps = fetch_data("appointments")
        my_apps = [a for a in apps if a["patient_id"] == patient_id]
        if my_apps:
            st.dataframe(pd.DataFrame(my_apps))

    elif choice == "My Health Record (EHR)":
        st.header("Clinical Records (Read Only)")
        st.write("View own diagnosis history, vitals, and physician notes.")
        
        records = fetch_data("records")
        my_records = [r for r in records if r["patient_id"] == patient_id]
        if my_records:
            st.dataframe(pd.DataFrame(my_records))
        else:
            st.info("No records found.")

    elif choice == "My Prescriptions & Pharmacy":
        st.header("Prescriptions (Read Only)")
        st.write("View and download authorized digital prescriptions.")
        
        prescriptions = fetch_data("prescriptions")
        my_rx = [p for p in prescriptions if p["patient_id"] == patient_id]
        if my_rx:
            st.dataframe(pd.DataFrame(my_rx))
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
                res = requests.post(f"{API_URL}/reservations/", json={
                    "patient_id": patient_id, "medicine_id": med_id, "quantity": qty
                })
                if res.status_code == 200:
                    st.success("Reserved for pickup!")
                    st.balloons()
                else:
                    st.error("Failed. Might be out of stock.")
        else:
            st.warning("No medicines available right now.")
