import re

with open("frontend/app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace format_display_data logic
new_formatter = """
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
                "Price ($)": f"{item.get('price', 0):.2f}",
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
"""

# replace old format_display_data function
start = code.find("def format_display_data")
end = code.find("# Initialize Session State")
if start != -1 and end != -1:
    code = code[:start] + new_formatter + "\n" + code[end:]

# replace st.dataframe calls with render_table
code = code.replace('st.dataframe(pd.DataFrame(format_display_data(users, "users")), hide_index=True)', 'render_table(pd.DataFrame(format_display_data(users, "users")))')
code = code.replace('st.dataframe(df, hide_index=True)', 'render_table(df)')
code = code.replace('st.dataframe(pd.DataFrame(format_display_data(fetch_data("medicines"), "medicines")), hide_index=True)', 'render_table(pd.DataFrame(format_display_data(fetch_data("medicines"), "medicines")))')
code = code.replace('st.dataframe(pd.DataFrame(format_display_data(my_apps, "appointments")), hide_index=True)', 'render_table(pd.DataFrame(format_display_data(my_apps, "appointments")))')
code = code.replace('st.dataframe(pd.DataFrame(format_display_data(my_records, "records")), hide_index=True)', 'render_table(pd.DataFrame(format_display_data(my_records, "records")))')
code = code.replace('st.dataframe(pd.DataFrame(format_display_data(my_rx, "prescriptions")), hide_index=True)', 'render_table(pd.DataFrame(format_display_data(my_rx, "prescriptions")))')

with open("frontend/app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Replaced!")
