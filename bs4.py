# Starticulation with Country-Specific Norms
# Updated to include a country dropdown and dialect-aware articulation expectations

import streamlit as st
import pandas as pd

# --- Country-Specific Mastery Ages (in months) ---
# Values are approximations based on international research

def get_mastery_ages(country):
    base = {
        'p': 36, 'b': 36, 'm': 36, 'n': 36, 'd': 36, 't': 36,
        'k': 48, 'g': 48, 'ŋ': 48, 'h': 36, 'w': 36, 'j': 36,
        'f': 42, 'v': 60, 's': 60, 'z': 60, 'l': 60, 'r': 72,
        'ʃ': 60, 'ʒ': 72, 'tʃ': 60, 'dʒ': 72,
        'θ': 84, 'ð': 84
    }
    if country == "USA" or country == "Canada":
        base['r'] = 72
        base['θ'] = 84
        base['ð'] = 72
    elif country == "UK":
        base['r'] = 60
        base['θ'] = 96
        base['ð'] = 96
    elif country == "Australia":
        base['r'] = 60
        base['θ'] = 96
        base['ð'] = 96

    # Add clusters (defaults for all countries)
    cluster_age = 60
    for cluster in [
        'bl', 'fl', 'pl', 'br', 'fr', 'pr', 'kw', 'tw',
        'gl', 'kl', 'dr', 'gr', 'kr', 'tr', 'θr',
        'sm', 'sp', 'sw', 'sk', 'sl', 'sn', 'st',
        'skr', 'spr', 'skw', 'spl'
    ]:
        base[cluster] = cluster_age
    return base

# --- Target Positions ---
def get_target_positions():
    tp = {
        'tʃ': ['initial', 'medial', 'final'], 'dʒ': ['initial', 'medial', 'final'],
        'ʒ': ['medial'], 'ð': ['initial', 'medial'], 'j': ['initial'], 'h': ['initial'],
        'w': ['initial', 'medial'], 'r': ['initial', 'medial', 'final'], 'ŋ': ['medial', 'final'],
    }
    clusters = [
        'bl', 'fl', 'pl', 'br', 'fr', 'pr', 'kw', 'tw',
        'gl', ' 'kl', 'dr', 'gr', 'kr', 'tr', 'θr',
        'sm', 'sp', 'sw', 'sk', 'sl', 'sn', 'st',
        'skr', 'spr', 'skw', 'spl'
    ]
    for cl in clusters:
        tp[cl] = ['initial']
    return tp

# --- UI Setup ---
st.set_page_config("Starticulation", layout="wide")
st.title("Starticulation Articulation Assessment")

country = st.selectbox("Select Country for Norms", ["Australia", "United Kingdom", "USA", "Canada"])
mastery_ages = get_mastery_ages(country)
target_positions = get_target_positions()

for s in mastery_ages:
    if s not in target_positions:
        target_positions[s] = ['initial', 'medial', 'final']

child_name = st.text_input("Child's First Name")
age_input = st.text_input("Child's Age (e.g., 4;6)")

def get_age_in_months(age_str):
    try:
        y, m = map(int, age_str.split(";"))
        return y * 12 + m
    except:
        return 0

age_months = get_age_in_months(age_input)

if child_name and age_months:
    data = []
    for s in mastery_ages:
        for p in target_positions[s]:
            data.append({'Sound': s, 'Position': p, 'Produced': s})
    df = pd.DataFrame(data)
    edited = st.data_editor(df, use_container_width=True)

    results, delayed, age_app, correct = [], [], [], []

    for _, row in edited.iterrows():
        s, p, prod = row["Sound"], row["Position"], row["Produced"].strip()
        mastery = mastery_ages[s]
        if prod == s:
            results.append((s, p, "Age Appropriate"))
            correct.append(f"/{s}/ ({p})")
        else:
            if age_months >= mastery:
                results.append((s, p, "Delayed"))
                delayed.append((s, p, mastery))
            else:
                results.append((s, p, "Incorrect but Age Appropriate"))
                age_app.append((s, p, mastery))

    color_map = {
        "Age Appropriate": "#d4edda", "Incorrect but Age Appropriate": "#ffe082", "Delayed": "#f8d7da"
    }

    def highlight(val):
        return f"background-color:{color_map.get(val,'')}; color:black;"

    st.subheader("Assessment Results")
    st.markdown(pd.DataFrame(results, columns=["Sound", "Position", "Result"])
        .style.applymap(highlight, subset=["Result"]).to_html(), unsafe_allow_html=True)

    st.subheader("Summary Report")
    d_html = ''.join([f"<li>/{s}/ ({p}) – expected by {m//12} yrs</li>" for s, p, m in delayed]) or "<li>None</li>"
    a_html = ''.join([f"<li>/{s}/ ({p}) – expected by {m//12} yrs</li>" for s, p, m in age_app]) or "<li>None</li>"
    st.markdown(f"<div style='font-size:16px;'>"
                f"<strong>Delayed:</strong><ul>{d_html}</ul>"
                f"<strong>Age Appropriate but Incorrect:</strong><ul>{a_html}</ul>"
                f"</div>", unsafe_allow_html=True)

    st.subheader("Recommended SMART Goals")
    if delayed:
        goal_list = [
            f"{child_name} will accurately produce the /{s}/ sound in the {p.lower()} position of single words "
            f"with 80% accuracy across 3 consecutive sessions, following auditory discrimination and isolation practice, "
            f"after 3 weeks of traditional articulation therapy."
            for s, p, m in delayed
        ]
        st.markdown("<ul>" + ''.join(f"<li>{g}</li>" for g in goal_list) + "</ul>", unsafe_allow_html=True)
        st.download_button("Download SMART Goals (TXT)", "\n".join(goal_list), file_name=f"{child_name}_goals.txt")
