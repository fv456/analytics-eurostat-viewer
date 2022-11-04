# -*- coding: utf-8 -*-
"""
@author: fv456
"""
import logging
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

import dtd_streamlit_utils as utils

# %% Streamlit app


@st.cache
def get_countries_delta_data(
    country_B: str, year: int, delta_colname: str
):  # TODO: ristrutturare questa funzione
    # Data comes from `dtd_analytics_desi/EuroStat/structural_business_statistics.ipynb`
    sbs = (
        pd.read_csv("data/sbs_with_sizen.csv")
        .drop(columns=["INDIC_SB"])
        .rename(columns={"time": "YEAR", "SIZEN": "BREAKDOWN_TYPE"})
    )
    sbs.YEAR += 2  # SBS is actually up to the 2019: we move year forward in order to match our data

    # Data comes from `dtd_analytics_desi/EuroStat/enterprises-treemap.ipynb` (dataset `ENT2-2009-2021-v220315`)
    df = pd.read_pickle("data/ENT2-2009-2021-v220315-filtered+gdp.pickle").drop(
        columns=["NACE", "NACE_CAPTION", "GDP"]
    )

    df = df.merge(sbs, on=["YEAR", "GEO", "BREAKDOWN_TYPE"], how="left")

    df_ita_YY = df.query(f"YEAR=={year} and GEO=='IT'")[
        ["VAR_AND_BRK", "N_ENTERPRISE", "VALUE"]
    ]
    df_ita_YY.columns = ["VAR_AND_BRK", "N_ENTERPRISE", "VAL_IT"]

    # Utilizziamo come base per la differenza le combinazioni var/brk disponibili per
    # l'Italia nell'anno selezionato
    df_deltas = df_ita_YY[["VAR_AND_BRK"]].copy(deep=True)

    df_country_YY = df.query(f"YEAR=={year} and GEO=='{country_B}'")[
        ["VAR_AND_BRK", "VALUE"]
    ]
    df_country_YY.columns = ["VAR_AND_BRK", f"VAL_{country_B}"]
    df_temp = pd.merge(df_ita_YY, df_country_YY)
    df_temp[delta_colname] = df_temp["VAL_IT"] - df_temp[f"VAL_{country_B}"]

    df_deltas = pd.merge(df_deltas, df_temp[["VAR_AND_BRK", delta_colname]])

    df_deltas = df_deltas.sort_values(delta_colname)
    df_deltas = df_deltas.dropna()
    df_temp = df.query(f"YEAR=={year} and GEO=='IT'")[
        [
            "VAR_AND_BRK",
            # "CAPTION_ALL",
            "VARIABLE_CAPTION",
            "BREAKDOWN_CAPTION",
            "VARIABLE",
            "BREAKDOWN_TYPE",
            "N_ENTERPRISE",
        ]
    ].drop_duplicates()
    df_deltas = pd.merge(df_deltas, df_temp, on="VAR_AND_BRK")

    return df_deltas


def app():
    logging.info("Sidebar loading...")
    year = st.sidebar.selectbox("Year?", [2021, 2020], index=0)

    EU_COUNTRIES = {"EU27_2020": "European Average",} | utils.get_eu_countries(
        eu_union=True, eu_candidates=False, eu_other=False
    )  # , drop_italy=True)

    country = st.sidebar.selectbox(
        "Compare Italy with..?",
        EU_COUNTRIES,  # view.EU_27_AND_AVG # df.GEO.unique()[37]
        index=0,  # 27,
        format_func=lambda id: EU_COUNTRIES[id],
    )

    treemap_style = st.sidebar.radio(
        "Treemap style", ("VAR -> BRKDWN", "BRKDWN -> VAR"), index=0
    )

    brkdwn_weighting = st.sidebar.radio(
        "Breakdown weighting by n° of enterprises", ("No", "Yes"), index=0
    )

    if country == "EU":
        country = "EU27_2020"

    COLNAME = f"DELTA_{country}"
    logging.info("Data loading...")
    df_deltas = get_countries_delta_data(str(country), int(str(year)), COLNAME)
    logging.info("...data loaded.")

    # Filtraggi sulle soglie dei valori di confronto
    v_max_range = max(abs(df_deltas[COLNAME]))
    v_max = max(df_deltas[COLNAME])
    v_min = min(df_deltas[COLNAME])
    threshold_min, threshold_max = st.sidebar.slider(
        "Threshold for delta", min_value=v_min, max_value=v_max, value=(v_min, v_max)
    )
    df_deltas = df_deltas.query(
        f"{COLNAME} <= {threshold_max} and {COLNAME} >= {threshold_min}"
    )

    # Base per le variabili: tutte le disponibili nel dataset
    # ALL_VARS = np.sort(df_deltas["VARIABLE"].unique())

    # Filtri su categorie di variabili
    st.sidebar.write("Variable categories")
    ALL_VARS = pd.Series(df_deltas["VARIABLE"].unique())
    SEL_VARS = []
    # `list(set(...))` to avoid duplicates
    if st.sidebar.checkbox("Artificial Intelligence", True):
        SEL_VARS = list(
            set(
                SEL_VARS
                + list(ALL_VARS[ALL_VARS.str.upper().str.contains("AI")].values)
            )
        )
    if st.sidebar.checkbox("Big Data", True):
        SEL_VARS = list(
            set(
                SEL_VARS
                + list(ALL_VARS[ALL_VARS.str.upper().str.contains("BD")].values)
            )
        )
    if st.sidebar.checkbox("Cloud Computing", True):
        SEL_VARS = list(
            set(
                SEL_VARS
                + list(ALL_VARS[ALL_VARS.str.upper().str.contains("CC")].values)
            )
        )
    if st.sidebar.checkbox("Cyber Security", True):
        SEL_VARS = list(
            set(
                SEL_VARS
                + list(ALL_VARS[ALL_VARS.str.upper().str.contains("SEC")].values)
            )
        )
    if st.sidebar.checkbox("Enterprise Website", True):
        SEL_VARS = list(
            set(
                SEL_VARS
                + list(ALL_VARS[ALL_VARS.str.upper().str.contains("WEB")].values)
            )
        )
    if st.sidebar.checkbox("Internet of Things", True):
        SEL_VARS = list(
            set(
                SEL_VARS
                + list(ALL_VARS[ALL_VARS.str.upper().str.contains("IOT")].values)
            )
        )
    if st.sidebar.checkbox("All others (longer loading time)", False):
        SEL_VARS = list(set(SEL_VARS + list(ALL_VARS[~ALL_VARS.isin(SEL_VARS)].values)))

    exclude_negative_vars = st.sidebar.radio(
        "Exclude negative vars (i.e.: 'Don't ...')?", ("True", "False"), index=0
    )

    if exclude_negative_vars == "True":
        SEL_VARS = [v for v in SEL_VARS if v.upper()[-1] != "X"]

    df_deltas = df_deltas[df_deltas["VARIABLE"].isin(SEL_VARS)]

    # Filtri sulle variabili
    # selected_variables = st.sidebar.multiselect('Selected variables:',ALL_VARS,ALL_VARS)
    # df_deltas = df_deltas[df_deltas["VARIABLE"].isin(selected_variables)]
    selected_variables = st.sidebar.text_input("Filter variable names").lower()
    df_deltas = df_deltas[
        df_deltas["VARIABLE"].str.lower().str.contains(selected_variables)
    ]
    filter_var_d = st.sidebar.text_input("Filter variables descriptions").lower()
    df_deltas = df_deltas[
        df_deltas["VARIABLE_CAPTION"].str.lower().str.contains(filter_var_d)
    ]

    # -> i breakdown sono troppi, diventa poco usabile in questo modo
    # ALL_BRKS = np.sort(df_deltas["BREAKDOWN_TYPE"].unique())
    # selected_breakdowns = st.sidebar.multiselect('Selected breakdowns:',ALL_BRKS,ALL_BRKS)
    # df_deltas = df_deltas[df_deltas["BREAKDOWN_TYPE"].isin(selected_breakdowns)]

    # Filtri sui breakdown
    filter_brk = st.sidebar.text_input("Filter breakdowns names").lower()
    df_deltas = df_deltas[
        df_deltas["BREAKDOWN_TYPE"].str.lower().str.contains(filter_brk)
    ]
    filter_brk_d = st.sidebar.text_input("Filter breakdowns descriptions").lower()
    df_deltas = df_deltas[
        df_deltas["BREAKDOWN_CAPTION"].str.lower().str.contains(filter_brk_d)
    ]

    logging.info("...sidebar loaded.")
    # --------------------------------------------------------------------------------

    # ---- MAIN PAGE START
    logging.info("Main page loading...")
    st.title("ICT usage in enterprises")
    st.header("Comparison tool")
    st.write(
        "Source data link: https://ec.europa.eu/eurostat/web/digital-economy-and-society/data/comprehensive-database"
    )
    st.write("Statistics on Enterprises, db version 15 March 2022")
    st.write(
        "Web app source code link: https://github.com/teamdigitale/eurostat-isoc-dashboard/pages/ict_in_enterprises.py"
    )

    if len(df_deltas) == 0:
        st.markdown("WARNING: filter resulted in **NO DATA**.")
        st.write()
        return

    logging.info("Computing treemap...")
    if treemap_style == "VAR -> BRKDWN":
        fig = px.treemap(
            df_deltas,
            path=[px.Constant("EUROSTAT"), "VARIABLE", "BREAKDOWN_TYPE"],
            values=px.Constant(1)
            if brkdwn_weighting == "No"
            else df_deltas["N_ENTERPRISE"].fillna(1e-7),
            color=COLNAME,
            hover_data=[
                "VARIABLE_CAPTION",
                "BREAKDOWN_CAPTION",
            ],
            color_continuous_scale="RdBu",
            height=750,
            title=f"Variable -> breakdown combinations",
            range_color=[-v_max_range, v_max_range],
        )  # per ottenere range simmetrico (bianco sullo zero)
        st.plotly_chart(fig, use_container_width=True)

        dwnld_button = st.empty()
        if dwnld_button.button(
            "Prepare download filtered treemap VAR->BRK above (HTML file)"
        ):
            utils.st_create_download_btn_2(
                dwnld_button, fig, "Download", "eurostat_ent_var_brk_treemap.html"
            )
    else:
        fig = px.treemap(
            df_deltas,
            path=[px.Constant("EUROSTAT"), "BREAKDOWN_TYPE", "VARIABLE"],
            values=px.Constant(1)
            if brkdwn_weighting == "No"
            else df_deltas["N_ENTERPRISE"].fillna(1e-7),
            color=COLNAME,
            hover_data=[
                "VARIABLE_CAPTION",
                "BREAKDOWN_CAPTION",
            ],
            color_continuous_scale="RdBu",
            height=750,
            title=f"Breakdown -> variable combinations",
            range_color=[-v_max_range, v_max_range],
        )  # per ottenere range simmetrico (bianco sullo zero)
        st.plotly_chart(fig, use_container_width=True)

        dwnld_button = st.empty()
        if dwnld_button.button(
            "Prepare download filtered treemap BRK->VAR above (HTML file)"
        ):
            utils.st_create_download_btn_2(
                dwnld_button, fig, "Download", "eurostat_ent_brk_var_treemap.html"
            )
    logging.info("...treemap computed.")

    logging.info("...main page loaded.")


# %% Exec with file
if __name__ == "__main__":
    logging.info("App loading...")
    st.set_page_config(layout="wide")
    app()
    logging.info("...app loaded.")
