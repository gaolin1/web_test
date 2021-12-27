from collections import defaultdict
from itertools import count
from typing import List
from numpy.core.shape_base import stack
from numpy.lib.function_base import select
from pandas._config.config import options
from pandas.core.reshape.reshape import stack_multiple
import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

def main():
    df = import_df()
    #df = pd.DataFrame(px.data.gapminder())
    try:
        df = df.set_index("Antibiotic")
        all_drugs = df.index.unique().tolist()
        container = st.container()
        all = st.checkbox("Select all medications")
        if all:
            drugs = container.multiselect("Choose antibiotic", options=all_drugs, default=all_drugs, key="4")
            if not drugs:
                container.error("Please select at least one antibiotic or use select all")
        else:
            drugs = container.multiselect("Choose antibiotic", options=all_drugs, key="1")
            if not drugs:
                container.error("{Please select at least one antibiotic")
        departments_select = get_departments(df, drugs, "Department")
        locations_select = get_departments(df, drugs, "Location")
        container = st.container()
        all = st.checkbox("Select all departments")
        if all:
            departments = container.multiselect("Choose department", options=departments_select, default=departments_select, key="2")
        else:
            departments = container.multiselect("Choose department", options=departments_select, key="5")
        container = st.container()
        all = st.checkbox("Select all locations")
        if all:
            locations = container.multiselect("Choose location", options=locations_select, default=locations_select, key="3")
        else:
            locations = container.multiselect("Choose location", options=locations_select, key="6")
        drugs_and_department = merge_list(drugs, departments)
        drugs_and_locations = merge_list(drugs, locations)
        all_merged = merge_list_3(drugs, departments, locations)
        df_filtered = pivot_table(df, drugs, departments, drugs_and_department,
            locations, drugs_and_locations, all_merged, "Antibiotic", "Department", "Location")
        st.write("Usage per department/location", df_filtered)
        total_chart = make_chart(df,all_merged, "Antibiotic",drugs)
        department_chart = make_chart(df, drugs_and_department, "Department",drugs)
        location_chart = make_chart(df, drugs_and_locations, "Location", drugs)
        st.altair_chart(total_chart, use_container_width=True)
        st.altair_chart(department_chart, use_container_width=True)
        st.altair_chart(location_chart, use_container_width=True)
    except AttributeError:
        pass

def import_df():
    df = st.file_uploader("Upload Epic export", type=["xlsx"])
    try:
        df = pd.read_excel(df)
        return df
    except ValueError:
        pass

def get_departments(df, drugs, type):
    df_filtered = df.loc[drugs]
    departments = df_filtered[type].unique().tolist()
    return departments

def merge_list_3(list1, list2, list3):
    import itertools
    combined_list = list(itertools.product(list1, list2, list3))
    return combined_list

def merge_list(list1, list2):
    import itertools
    combined_list = list(itertools.product(list1, list2))
    return combined_list


def pivot_table(df, var1, var2, list2, var3, list3, list, col1, col2, col3):
    df = df.reset_index()
    if var2 != []:
        if var2 and var3 != []:
            plot_df = df[df[[col1, col2, col3]].apply(tuple,1).isin(list)]
            data = pd.pivot_table(plot_df, values="Amount", index=[col1, col2, col3],
            columns=["Date"]
        )
        else:
            plot_df = df[df[[col1, col2]].apply(tuple,1).isin(list2)]
            data = pd.pivot_table(plot_df, values="Amount", index=[col1, col2],
            columns=["Date"]
        )
    elif var3 != []:
        plot_df = df[df[[col1, col3]].apply(tuple,1).isin(list3)]
        data = pd.pivot_table(plot_df, values="Amount", index=[col1, col3],
            columns=["Date"]
        )
    else:
        plot_df = df[df[col1].isin(var1)]
        data = pd.pivot_table(plot_df, values="Amount", index=[col1],
            columns=["Date"])
    return data

def make_chart(data,list, type,drugs):
    data = data.reset_index()
    if type != "Antibiotic":
        plot_df = data[data[["Antibiotic", type]].apply(tuple,1).isin(list)]
        chart = (
            alt.Chart(plot_df)
            .mark_line(opacity=0.4)
            .encode(
                x="Date:T",
                y=alt.Y("Amount:Q",stack=None, aggregate="sum"),
                color=type+":N"
            )
            .interactive()
        )
        return chart
    else:
        plot_df = data[data["Antibiotic"].isin(drugs)]
        chart = (
            alt.Chart(plot_df)
            .mark_line(opacity=0.4)
            .encode(
                x="Date:T",
                y=alt.Y("Amount:Q",stack=None),
                color=type+":N"
            )
            .interactive()
        )
        return chart

if __name__ == '__main__':
    main()
