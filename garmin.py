import pandas as pd
import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.let_it_rain import rain
from streamlit_extras.stoggle import stoggle
from streamlit_toggle import st_toggle_switch
import datetime
from io import StringIO,BytesIO
# from pyxlsb import open_workbook as open_xlsb


st.set_page_config(  # Alternate names: setup_page, page, layout
    layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
    initial_sidebar_state="collapsed",  # Can be "auto", "expanded", "collapsed"
    page_title=None,  # String or None. Strings get appended with "• Streamlit".
    page_icon="🛤️",
    # menu_items={
    #     'Get Help': 'https://www.extremelycoolapp.com/help',
    #     'Report a bug': "https://www.extremelycoolapp.com/bug",
    #     'About': "# This is a header. This is an *extremely* cool app!"
    # }
)

## hide streamlit main menu !
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
##
st.write("## Garmin Activity hiking")

@st.cache
def data_upload():
    fileToView = 'AcuGarminData.csv'
    df = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vSoaEtjUeoTjzneWdwZR9d5qA_unCnYc5tW5f-9y1jbvjQx7TkS0Qby7LtLjklvg-ak7GZ2H3o4YOO6/pub?gid=0&single=true&output=csv')
    # df = pd.read_csv(fileToView)
    df.index = df.index + 1
    df = df.replace(r',', '', regex=True)
    df = df.filter(items=['Typ aktywności', 'Data', 'Ulubiony', 'Tytuł', 'Dystans', 'Kalorie'
        , 'Czas', 'Średnie tętno', 'Maksymalne tętno', 'Całkowity wznios'
        , 'Maksymalna wysokość'])
    df = df.astype({"Maksymalna wysokość":"int","Kalorie":"int"})
    df['Data'] = pd.to_datetime(df['Data'].str.slice(0, 10), format='%Y-%m-%d')
    df = df.sort_values(by=['Data'], ascending=False)
    return df

def print_chart(df):
    # print(df)
    d = {'Data': df['Data'].dt.strftime('%Y-%m'), 'Dystans': df['Dystans'].values}
    Datafram_chart = pd.DataFrame(data=d)
    Datafram_chart = Datafram_chart.groupby(by="Data").sum()
    st.bar_chart(Datafram_chart)

def to_excel(df):
    df.to_excel("Hiking.xlsx",
                sheet_name='Hiking')
    return df

df = data_upload()
# print(df)
distans2022 = round(df.loc[df['Data'].dt.strftime('%Y') == '2022', 'Dystans'].sum(), 2)
distans2023 = round(df.loc[df['Data'].dt.strftime('%Y') == '2023', 'Dystans'].sum(), 2)
distance = round(df['Dystans'].sum(), 2)
Best_alt = df['Maksymalna wysokość'].max()
best_trip =  df['Dystans'].max()
avg_dist  = round(df['Dystans'].mean(),1)
# Nie działa za dobrze
# filtered_df = dataframe_explorer(df)
#st.dataframe(filtered_df, use_container_width=True)

# filtr dataframe
place_title = list(df['Tytuł'].drop_duplicates())
place = st.sidebar.multiselect(
    'Place:', place_title, default=place_title)


distans_choice = st.sidebar.slider(
    'max distans:', min_value=4, max_value=100, step=1, value=100)

with st.sidebar:
    isSnow = st_toggle_switch(
        label="Snow?",
        key="switch_1",
        default_value=False,
        label_after=False,
        inactive_color="#D3D3D3",  # optional
        active_color="#11567f",  # optional
        track_color="#29B5E8",  # optional
        )


start_date = st.date_input(
    "Start date",
    datetime.date(2022, 1, 10))
st.write('Start date:', start_date)

today = datetime.date.today()
end_date = st.date_input(
    "End date ",
    datetime.date(today.year, today.month, today.day))
st.write('End date:', end_date)


df = df[df['Dystans'] < distans_choice]
df = df[df['Tytuł'].isin(place)]

df = df.loc[(df['Data'] >= start_date.strftime('%Y-%m-%d'))
                     & (df['Data'] <= end_date.strftime('%Y-%m-%d'))]
st.dataframe(df, use_container_width=True)
# podusmwanie
st.info(len(df))

col1, col2 , col3, col4 ,col5 = st.columns(5)
with col1:
    if st.button('Refresh', key=1):
        df = data_upload()

with col2:
    to_excel(df)
    with open("Hiking.xlsx", "rb") as file:
        btn = st.download_button(
            label="Download Excel",
            data=file,
            file_name="Hiking.xlsx",
            mime="image/png"
        )

if isSnow:
    rain(
        emoji="❄️",
        font_size=54,
        falling_speed=5,
        animation_length="infinite",
    )

st.header(f' Total distans in 2022  _:green[{distans2022}] km_ 💪🗻🗻🗻  ')
st.header(f' Total distans in 2023  _:blue[{distans2023}] km_ 👽')
st.header(f' Total distans _:red[{distance}] km_ 🛤️💪 ')
st.header(f' Best altitude _:orange[{Best_alt}]m_ 💪 🌋 ⬆️ ')
st.header(f' Best distance on the trip _:red[{best_trip}] km_ 🚵‍♀️ 🚴🏻‍♂️ ')
st.header(f' Avg distance on the trip _:blue[{avg_dist}] km_ ️ 🏃')


print_chart(df)
col1, col2, col3, col4 = st.columns(4)
with col1:
    uploaded_file = st.file_uploader("Select a file .CSV")
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        st.write(bytes_data)

        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        st.write(string_data)

        # Can be used wherever a "file-like" object is accepted:
        df = pd.read_csv(uploaded_file)
        df = df.filter(items=['Typ aktywności', 'Data', 'Ulubiony', 'Tytuł', 'Dystans', 'Kalorie'
            , 'Czas', 'Średnie tętno', 'Maksymalne tętno', 'Całkowity wznios'
            , 'Maksymalna wysokość'])

        df = df.replace(r',', '', regex=True)
        df.to_csv('AcuGarminData.csv', index=False)


# st.write(st.session_state)  ## Debug
