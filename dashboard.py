import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from PIL import Image
import os
import time

# ─── Config ───────────────────────────────────────────────────────────────────
DATA_FILE = (
    "/Users/park/Library/CloudStorage/"
    "OneDrive-ChulalongkornUniversity/"
    "CUTI-Sharepoint.Group - เอกสาร/"
    "CUTI-Research/On-going Projects/"
    "Columbia_ISM_LivingLab/"
    "Supply and Demand Survey/Pilot results/"
    "Data_Pilot_Submitted.xlsx"
)

LOGO_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Motorcycle Taxi Survey — Bangkok Living Lab",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Auto-refresh when file changes ───────────────────────────────────────────
@st.cache_data(ttl=30)          # re-reads from disk every 30 s
def load_data():
    mtime = os.path.getmtime(DATA_FILE)
    xls = pd.ExcelFile(DATA_FILE)
    sheets = {}
    for name in xls.sheet_names:
        df = xls.parse(name)
        df.replace({888: None, 999: None}, inplace=True)
        sheets[name] = df
    return sheets, mtime

sheets, mtime = load_data()
demand_win   = sheets["Demand_Win"]
demand_rider = sheets["Demand_Rider"]
supply_win   = sheets["Supply_Win"]
supply_rider = sheets["Supply_Rider"]

# ─── Helpers ──────────────────────────────────────────────────────────────────
COLORS = px.colors.qualitative.Pastel

def fmt_ts(ts):
    import datetime
    return datetime.datetime.fromtimestamp(ts).strftime("%d %b %Y  %H:%M:%S")

def bar(df, col, labels, title, colors=COLORS):
    counts = df[col].value_counts().reindex(labels.keys()).fillna(0)
    fig = px.bar(
        x=list(labels.values()),
        y=counts.values,
        labels={"x": "", "y": "Count"},
        title=title,
        color=list(labels.values()),
        color_discrete_sequence=colors,
    )
    fig.update_layout(showlegend=False, title_font_size=14, height=340)
    return fig

def pie(df, col, labels, title):
    counts = df[col].value_counts().reindex(labels.keys()).fillna(0)
    fig = px.pie(
        names=list(labels.values()),
        values=counts.values,
        title=title,
        color_discrete_sequence=COLORS,
        hole=0.35,
    )
    fig.update_layout(title_font_size=14, height=340)
    return fig

def binary_bar(df, cols, labels, title):
    """For Q16/Q17 multi-select columns (0/1)."""
    pct = {labels[c]: int(df[c].sum()) for c in cols if c in df.columns}
    fig = px.bar(
        x=list(pct.values()),
        y=list(pct.keys()),
        orientation="h",
        title=title,
        labels={"x": "# Selected", "y": ""},
        color=list(pct.keys()),
        color_discrete_sequence=COLORS,
    )
    fig.update_layout(showlegend=False, title_font_size=14, height=360)
    return fig

def rating_bar(df, cols, labels, title):
    """Heatmap-style stacked bar for Likert / comparison questions."""
    data = {labels[c]: df[c].value_counts().sort_index() for c in cols if c in df.columns}
    fig = go.Figure()
    value_labels = {1: "Win better", 2: "Similar", 3: "App better", 4: "Never used other"}
    clr = ["#4CAF50", "#FFC107", "#2196F3", "#9E9E9E"]
    for i, (val, clr_) in enumerate(zip([1, 2, 3, 4], clr), 1):
        fig.add_trace(go.Bar(
            name=value_labels.get(val, str(val)),
            y=list(data.keys()),
            x=[data[k].get(val, 0) for k in data],
            orientation="h",
            marker_color=clr_,
        ))
    fig.update_layout(
        barmode="stack",
        title=title,
        title_font_size=14,
        height=360,
        legend_title="Response",
    )
    return fig

# ─── Sidebar ──────────────────────────────────────────────────────────────────
img_cuti     = Image.open(os.path.join(LOGO_DIR, "logo_cuti.png"))
img_columbia = Image.open(os.path.join(LOGO_DIR, "logo_columbia.png"))
img_ism      = Image.open(os.path.join(LOGO_DIR, "logo_ism.png"))

# Three logos side-by-side in the sidebar
col_a, col_b, col_c = st.sidebar.columns(3)
col_a.image(img_cuti,     use_container_width=True)
col_b.image(img_columbia, use_container_width=True)
col_c.image(img_ism,      use_container_width=True)

st.sidebar.title("Bangkok Living Lab")
st.sidebar.markdown("**Motorcycle Taxi Survey**  \nCUTI · Columbia ISM")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Section",
    ["Overview", "Demand — Usage & Behavior",
     "Demand — EV Attitudes", "Demand — Demographics",
     "Supply — Driver Profile"],
)
st.sidebar.markdown("---")
st.sidebar.caption(f"File last modified:  \n`{fmt_ts(mtime)}`")
st.sidebar.caption("Dashboard auto-refreshes every 30 s.")

# ─── Overview ─────────────────────────────────────────────────────────────────
if page == "Overview":
    h1, h2, h3, h4 = st.columns([1, 1, 1, 5])
    h1.image(img_cuti,     use_container_width=True)
    h2.image(img_columbia, use_container_width=True)
    h3.image(img_ism,      use_container_width=True)
    h4.markdown(
        "## 🛵 Motorcycle Taxi Survey — Pilot Results\n"
        "Survey data from **Bangkok Living Lab** pilot (March 2025). "
        "Covers both *demand* (passengers) and *supply* (drivers) sides, "
        "split between traditional Win stands and app-based riders."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Demand · Win", f"{len(demand_win)} resp.")
    c2.metric("Demand · App", f"{len(demand_rider)} resp.")
    c3.metric("Supply · Win", f"{len(supply_win)} resp.")
    c4.metric("Supply · App", f"{len(supply_rider)} resp.")

    st.markdown("---")
    st.subheader("Survey Locations (map)")

    all_pts = pd.concat([
        demand_win[["Latitude","Longitude","ParkingSpot"]].assign(Group="Demand Win"),
        demand_rider[["Latitude","Longitude","ParkingSpot"]].assign(Group="Demand App"),
        supply_win[["Latitude","Longitude","ParkingSpot"]].assign(Group="Supply Win"),
        supply_rider[["Latitude","Longitude","ParkingSpot"]].assign(Group="Supply App"),
    ]).dropna(subset=["Latitude","Longitude"])

    m = folium.Map(location=[13.75, 100.535], zoom_start=14, tiles="CartoDB positron")
    color_map = {"Demand Win": "blue", "Demand App": "green",
                 "Supply Win": "orange", "Supply App": "red"}
    for _, row in all_pts.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=8,
            color=color_map[row["Group"]],
            fill=True,
            fill_opacity=0.7,
            tooltip=f"{row['Group']}: {row['ParkingSpot']}",
        ).add_to(m)

    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                background:white;padding:10px;border-radius:8px;font-size:13px;">
      <b>Legend</b><br>
      <span style="color:blue">●</span> Demand Win &nbsp;
      <span style="color:green">●</span> Demand App<br>
      <span style="color:orange">●</span> Supply Win &nbsp;
      <span style="color:red">●</span> Supply App
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))
    st_folium(m, width=900, height=480)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            x=["Demand Win", "Demand App", "Supply Win", "Supply App"],
            y=[len(demand_win), len(demand_rider), len(supply_win), len(supply_rider)],
            color=["Demand Win", "Demand App", "Supply Win", "Supply App"],
            color_discrete_sequence=COLORS,
            title="Responses by Survey Group",
            labels={"x": "", "y": "Count"},
        )
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        spot_counts = (
            pd.concat([
                demand_win[["ParkingSpot"]],
                demand_rider[["ParkingSpot"]],
                supply_win[["ParkingSpot"]],
                supply_rider[["ParkingSpot"]],
            ])
            .dropna()
            .value_counts()
            .head(10)
            .reset_index()
        )
        spot_counts.columns = ["Location", "Count"]
        fig2 = px.bar(
            spot_counts, x="Count", y="Location",
            orientation="h", title="Top Survey Locations",
            color="Count", color_continuous_scale="Blues",
        )
        fig2.update_layout(height=300, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)

# ─── Demand — Usage & Behavior ────────────────────────────────────────────────
elif page == "Demand — Usage & Behavior":
    st.title("Demand Side — Usage & Behavior")
    tab1, tab2 = st.tabs(["Win Passengers", "App Passengers"])

    for tab, df, label in [
        (tab1, demand_win, "Win"),
        (tab2, demand_rider, "App"),
    ]:
        with tab:
            c1, c2, c3 = st.columns(3)
            c1.metric("Responses", len(df))
            c2.metric("Avg trips/week", f"{df['Q2Times'].mean():.1f}" if "Q2Times" in df else "—")

            row1c1, row1c2 = st.columns(2)
            with row1c1:
                st.plotly_chart(bar(df, "Q1",
                    {1:"Win only", 2:"App only", 3:"Both equally"},
                    "Q1 · Preferred type"), use_container_width=True)
            with row1c2:
                st.plotly_chart(bar(df, "Q3",
                    {1:"Work",2:"School",3:"Shopping",4:"Grocery",
                     5:"Social",6:"Personal",7:"Tourism",8:"Other"},
                    "Q3 · Trip purpose"), use_container_width=True)

            row2c1, row2c2, row2c3 = st.columns(3)
            with row2c1:
                st.plotly_chart(bar(df, "Q6",
                    {1:"<1 km",2:"1–3 km",3:"3–5 km",4:"5–10 km",5:">10 km"},
                    "Q6 · Distance per trip"), use_container_width=True)
            with row2c2:
                st.plotly_chart(bar(df, "Q7",
                    {1:"<5 min",2:"5–10 min",3:"11–20 min",4:">20 min"},
                    "Q7 · Travel time"), use_container_width=True)
            with row2c3:
                st.plotly_chart(bar(df, "Q8",
                    {1:"<3 min",2:"3–5 min",3:"6–10 min",4:">10 min"},
                    "Q8 · Waiting time"), use_container_width=True)

            row3c1, row3c2, row3c3 = st.columns(3)
            with row3c1:
                st.plotly_chart(bar(df, "Q9",
                    {1:"≤20 ฿",2:"21–40 ฿",3:"41–60 ฿",4:"61–100 ฿",5:">100 ฿"},
                    "Q9 · Fare per trip"), use_container_width=True)
            with row3c2:
                st.plotly_chart(bar(df, "Q10",
                    {1:"Walk to stand",2:"App",3:"Call driver",4:"Mixed"},
                    "Q10 · How hailed"), use_container_width=True)
            with row3c3:
                st.plotly_chart(bar(df, "Q11",
                    {1:"Cash",2:"Mobile/QR",3:"Credit card"},
                    "Q11 · Payment method"), use_container_width=True)

            st.markdown("### Q12 · Top reasons for choosing motorcycle taxi")
            reasons = {
                "Q12_1":"Faster",
                "Q12_2":"Avoid traffic",
                "Q12_3":"Door-to-door",
                "Q12_4":"No other transit",
                "Q12_5":"Affordable",
                "Q12_6":"Short distance",
                "Q12_7":"Safer",
                "Q12_8":"Trust driver",
            }
            # Ranked 1 = top choice; count how many ranked each
            ranked = {v: (df[k] == 1).sum() for k, v in reasons.items() if k in df.columns}
            fig_r = px.bar(
                x=list(ranked.values()), y=list(ranked.keys()),
                orientation="h", title="Times ranked #1",
                color=list(ranked.values()), color_continuous_scale="Teal",
            )
            fig_r.update_layout(showlegend=False, height=320,
                                 yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_r, use_container_width=True)

            if "Q13" in df.columns:
                alt_labels = {
                    1:"Walk",2:"Bicycle",3:"Bus",4:"BTS/MRT",
                    5:"Boat",6:"Taxi",7:"App car",8:"Informal transit",
                    9:"Own motorbike",10:"Own car",11:"Other",
                }
                st.plotly_chart(
                    bar(df, "Q13", alt_labels, "Q13 · Alternative if no motorcycle taxi"),
                    use_container_width=True)

            if "Q14_1" in df.columns:
                q14_cols = [f"Q14_{i}" for i in range(1, 7)]
                q14_labels = {
                    "Q14_1":"Price",
                    "Q14_2":"Waiting time",
                    "Q14_3":"Convenience",
                    "Q14_4":"Safety",
                    "Q14_5":"Driver trustworthiness",
                    "Q14_6":"Driver professionalism",
                }
                st.markdown("### Q14 · Win vs App comparison")
                st.plotly_chart(
                    rating_bar(df, q14_cols, q14_labels, "Win vs App — by dimension"),
                    use_container_width=True)

# ─── Demand — EV Attitudes ────────────────────────────────────────────────────
elif page == "Demand — EV Attitudes":
    st.title("Demand Side — Electric Motorcycle Taxi Attitudes")
    tab1, tab2 = st.tabs(["Win Passengers", "App Passengers"])

    for tab, df, label in [
        (tab1, demand_win, "Win"),
        (tab2, demand_rider, "App"),
    ]:
        with tab:
            row1c1, row1c2 = st.columns(2)
            with row1c1:
                st.plotly_chart(bar(df, "Q15",
                    {1:"Definitely yes",2:"Probably yes",3:"Unsure",
                     4:"Probably no",5:"Definitely no"},
                    "Q15 · Likelihood to use EV motorcycle taxi"), use_container_width=True)
            with row1c2:
                st.plotly_chart(bar(df, "Q19",
                    {1:"Win service first",2:"App service first",
                     3:"Both simultaneously",4:"Not sure"},
                    "Q19 · Which service should adopt EV first?"), use_container_width=True)

            row2c1, row2c2 = st.columns(2)
            with row2c1:
                pros_cols = ["Q16_1","Q16_2","Q16_3","Q16_4","Q16_5","Q16_6","Q16_7","Q16_8No"]
                pros_labels = {
                    "Q16_1":"Less air pollution",
                    "Q16_2":"Less noise",
                    "Q16_3":"Eco-friendly",
                    "Q16_4":"Lower operating cost",
                    "Q16_5":"Safer",
                    "Q16_6":"New tech / app",
                    "Q16_7":"Other",
                    "Q16_8No":"No advantages",
                }
                st.plotly_chart(
                    binary_bar(df, pros_cols, pros_labels, "Q16 · Perceived EV advantages"),
                    use_container_width=True)
            with row2c2:
                cons_cols = ["Q17_1","Q17_2","Q17_3","Q17_4","Q17_5","Q17_6","Q17_7No"]
                cons_labels = {
                    "Q17_1":"More dangerous",
                    "Q17_2":"Not eco-friendly",
                    "Q17_3":"Higher fare",
                    "Q17_4":"Lower speed/power",
                    "Q17_5":"Less reliable/unfamiliar",
                    "Q17_6":"Other",
                    "Q17_7No":"No disadvantages",
                }
                st.plotly_chart(
                    binary_bar(df, cons_cols, cons_labels, "Q17 · Perceived EV disadvantages"),
                    use_container_width=True)

            st.markdown("### Q18 · Willingness to pay for EV motorcycle taxi")
            fare_cols = {"Q18_1":"40 ฿","Q18_2":"50 ฿","Q18_3":"60 ฿","Q18_4":"80 ฿"}
            wtp = {v: int(df[k].sum()) for k, v in fare_cols.items() if k in df.columns}
            fig_wtp = px.bar(
                x=list(wtp.keys()), y=list(wtp.values()),
                color=list(wtp.keys()), color_discrete_sequence=COLORS,
                title="Would pay this fare (yes count)",
                labels={"x": "Fare level", "y": "# Willing"},
            )
            fig_wtp.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig_wtp, use_container_width=True)

            st.plotly_chart(bar(df, "Q20",
                {1:"Strongly support",2:"Support",3:"Neutral",
                 4:"Oppose",5:"Strongly oppose"},
                "Q20 · Support for government EV promotion policy"),
                use_container_width=True)

# ─── Demand — Demographics ────────────────────────────────────────────────────
elif page == "Demand — Demographics":
    st.title("Demand Side — Demographics")

    combined = pd.concat([
        demand_win.assign(Group="Win"),
        demand_rider.assign(Group="App"),
    ])
    tab1, tab2, tab3 = st.tabs(["Combined", "Win only", "App only"])

    for tab, df in [(tab1, combined), (tab2, demand_win), (tab3, demand_rider)]:
        with tab:
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1:
                st.plotly_chart(pie(df, "Q21Age",
                    {1:"18–24",2:"25–34",3:"35–44",4:"45–54",5:"55+"},
                    "Age group"), use_container_width=True)
            with r1c2:
                st.plotly_chart(pie(df, "Q22Sex",
                    {1:"Male",2:"Female",3:"LGBTQ+",4:"Prefer not to say"},
                    "Gender"), use_container_width=True)
            with r1c3:
                st.plotly_chart(pie(df, "Q25Salary",
                    {1:"≤10k",2:"10–15k",3:"15–20k",4:"20–25k",
                     5:"25–30k",6:"30–35k",7:"35–40k",8:">40k"},
                    "Monthly income (฿)"), use_container_width=True)

            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.plotly_chart(bar(df, "Q23Edu",
                    {1:"< Jr. High",2:"Jr. High",3:"Sr. High",4:"Vocational",
                     5:"Higher Voc.",6:"Bachelor",7:"Master",8:"PhD"},
                    "Education level"), use_container_width=True)
            with r2c2:
                st.plotly_chart(bar(df, "Q24Occ",
                    {1:"Student",2:"Private employee",3:"Government",
                     4:"Self-employed",5:"Freelance",6:"Professional",
                     7:"Labor",8:"Unemployed",9:"Other"},
                    "Occupation"), use_container_width=True)

# ─── Supply — Driver Profile ───────────────────────────────────────────────────
elif page == "Supply — Driver Profile":
    st.title("Supply Side — Driver Profile")
    tab1, tab2 = st.tabs(["Win Drivers", "App Drivers"])

    for tab, df, label in [
        (tab1, supply_win, "Win"),
        (tab2, supply_rider, "App"),
    ]:
        with tab:
            c1, c2, c3 = st.columns(3)
            c1.metric("Responses", len(df))
            if "D10Salary_Baht" in df.columns:
                c2.metric("Avg monthly income (฿)",
                          f"{df['D10Salary_Baht'].mean():,.0f}")
            if "D14Hours" in df.columns:
                c3.metric("Avg hours/day", f"{df['D14Hours'].mean():.1f}")

            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1:
                st.plotly_chart(pie(df, "D6Age",
                    {1:"18–24",2:"25–34",3:"35–44",4:"45–54",5:"55+"},
                    "Driver age group"), use_container_width=True)
            with r1c2:
                st.plotly_chart(pie(df, "D7Sex",
                    {1:"Male",2:"Female",3:"LGBTQ+",4:"Prefer not to say"},
                    "Driver gender"), use_container_width=True)
            with r1c3:
                if "D15Years" in df.columns:
                    st.plotly_chart(pie(df, "D15Years",
                        {1:"<1 yr",2:"1–3 yrs",3:"3–5 yrs",4:"5–10 yrs",5:">10 yrs"},
                        "Years as driver"), use_container_width=True)

            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.plotly_chart(bar(df, "D8Edu",
                    {1:"< Jr. High",2:"Jr. High",3:"Sr. High",4:"Vocational",
                     5:"Higher Voc.",6:"Bachelor",7:"Master",8:"PhD"},
                    "Education level"), use_container_width=True)
            with r2c2:
                if "D12Day" in df.columns:
                    st.plotly_chart(bar(df, "D12Day",
                        {1:"Mon",2:"Tue",3:"Wed",4:"Thu",5:"Fri",6:"Sat",7:"Sun"},
                        "Busiest day of week"), use_container_width=True)

            if "A1" in df.columns:
                st.plotly_chart(bar(df, "A1",
                    {1:"Win",2:"App"},
                    "A1 · Respondent type confirmation"), use_container_width=True)

            if "C1" in df.columns:
                st.plotly_chart(bar(df, "C1",
                    {1:"Own",2:"Rent",3:"Installment",4:"Other"},
                    "C1 · Motorcycle ownership"), use_container_width=True)

            # EV interest (E1, E2)
            if "E1" in df.columns:
                st.markdown("### EV Adoption (Supply Side)")
                ec1, ec2 = st.columns(2)
                with ec1:
                    st.plotly_chart(bar(df, "E1",
                        {1:"Definitely yes",2:"Probably yes",3:"Unsure",
                         4:"Probably no",5:"Definitely no"},
                        "E1 · Would switch to EV motorcycle?"), use_container_width=True)
                with ec2:
                    if "E2" in df.columns:
                        st.plotly_chart(bar(df, "E2",
                            {1:"Definitely yes",2:"Probably yes",3:"Unsure",
                             4:"Probably no",5:"Definitely no"},
                            "E2 · Would rent EV motorcycle?"), use_container_width=True)

            if "D20_1" in df.columns:
                st.markdown("### D20 · Problems faced")
                d20_cols = ["D20_1","D20_2","D20_3","D20_4","D20_5No"]
                d20_labels = {
                    "D20_1":"Traffic/roads",
                    "D20_2":"Income instability",
                    "D20_3":"Maintenance cost",
                    "D20_4":"Competition",
                    "D20_5No":"No problems",
                }
                st.plotly_chart(
                    binary_bar(df, d20_cols, d20_labels, "Problems reported (# drivers)"),
                    use_container_width=True)
