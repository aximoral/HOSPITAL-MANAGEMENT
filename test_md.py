import streamlit as st
import pandas as pd

df = pd.DataFrame({
    "Doctor Info": ["**Name:** Dr. Smith<br>**Spec:** Cardio<br>**Contact:** 123-456"],
    "Patient Info": ["**Name:** John<br>**Age:** 30<br>**Blood:** O+"]
})

st.markdown(df.to_markdown(index=False), unsafe_allow_html=True)
