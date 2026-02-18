import streamlit as st
from source import Dictionary, WikitionaryReaderException, make_filters

st.set_page_config(
    page_title="Polish Dictionary",
    page_icon="📖",
    layout="centered",
)

st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stTextInput input {
            font-family: Courier, monospace;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📖 Polish Dictionary")

@st.cache_resource
def load_dictionary():
    return Dictionary()

dictionary = load_dictionary()

def render_filters():
    st.subheader("Filters")
    
    type_config = [("Rzeczownik", "rz"), ("Czasownik", "cz"), ("Przymiotnik", "p")]
    
    type_map = {
        key: col.checkbox(label, True) 
        for col, (label, key) in zip(st.columns(len(type_config)), type_config)
    }

    range_in_col = lambda col, label, limit: (
        col.number_input(f"Min {label}", 0, limit, 0),
        col.number_input(f"Max {label}", 0, limit, limit)
    )

    c1, c2 = st.columns(2)
    l_min, l_max = range_in_col(c1, "letters", 50)
    s_min, s_max = range_in_col(c2, "syllables", 10)

    return type_map, l_min, l_max, s_min, s_max

def perform_search(regex, type_map, l_min, l_max, s_min, s_max):
    selected_types = [k for k, v in type_map.items() if v] or None
    if not selected_types:
        return []
    
    filters = make_filters(
        regex=regex,
        types=selected_types,
        min_letters=l_min,
        max_letters=l_max,
        min_syllables=s_min,
        max_syllables=s_max,
    )
    results = dictionary.search(filters)
    return sorted({result["word"] for result in results})

regex_filter = st.text_input("Regex", placeholder="^fumu.*")
type_map, l_min, l_max, s_min, s_max = render_filters()

if regex_filter:
    try:
        words = perform_search(regex_filter, type_map, l_min, l_max, s_min, s_max)
        st.success(f"Found: {len(words)}")
        if words:
            st.text_area("Results", "\n".join(words), height=400)
    except WikitionaryReaderException as error:
        st.error(str(error))