import pandas as pd
import streamlit as st
st.set_page_config(layout='wide')
with st.container():
    df = pd.read_csv("https://cdncontribute.geeksforgeeks.org/wp-content/uploads/nba.csv")
    teams = df['Team'].unique()
    selected_team = st.selectbox("Select Team:", teams)
    filtered_df = df[df['Team'] == selected_team]
    df2 = filtered_df.groupby('Team')['Salary'].sum().sort_values(ascending=False).head()
    df3 = filtered_df.sort_values(by="Salary", ascending=False).head()
    df4 = df.groupby('Position')['Salary'].sum().sort_values(ascending=False).head()
    if st.button("Exibir Dados"):
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        with col1:
            st.title("Maior Salarios")
            st.write(df3)
        with col2:
            st.title("Salários por Posição")
            st.write(df4)
        with col3:
            st.title("Salários por idade")
            st.bar_chart(filtered_df[['Salary', 'Age']])
        with col4:
            st.title("Média Salarial por Posição")
            st.line_chart(df.groupby('Position')['Salary'].mean())
