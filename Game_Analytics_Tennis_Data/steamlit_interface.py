
import streamlit as st
import plotly.express as px
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Connection of database.

engine = create_engine("postgresql://postgres:12345678@localhost:5432/sports")

# Convert the sql table into data frame.

competitors = pd.read_sql("SELECT * FROM competitors_table", engine)
rankings = pd.read_sql("SELECT * FROM competitor_ranking_table", engine)

# Drop the duplicate and the dataframe.

rankings_unique = rankings.drop_duplicates(subset=['competitor_id'], keep='first')
merged_df = competitors.merge(rankings_unique, on="competitor_id", how="left", validate="many_to_one")


st.title("🎾Tennis Analytics Dashboard")            # Main title for dashboard
st.markdown("---")

st.sidebar.title("🧭 Dashboard Controls")           # Sidebar title
st.sidebar.markdown("---")

st.sidebar.subheader("Search Competitor")
name = st.sidebar.text_input("Enter competitor name:")

rank_range = st.sidebar.slider("Select Rank Range",1,500,(1, 50))

st.sidebar.subheader("Filter")
selector = st.sidebar.radio("Select the option:", ['Filtered Competitors','Competitor details viewer',
                            'Country Analysis','Leader boards'])



col1, col2, col3 ,col4 = st.columns(4)

col1.metric("Total Competitors",len(competitors))

col2.metric("Total Countries",competitors['country_code'].nunique())

col3.metric("Highest Points",rankings['points'].max())

col4.metric("Lowest points",rankings['points'].min())


def filtered_competitors():
   
   st.subheader("Filter Rakings 📈")                  # for slider and filter.

   filtered = merged_df[(merged_df['rank'] >= rank_range[0]) &(merged_df['rank'] <= rank_range[1])]

   st.dataframe(filtered,width='stretch')


def competitor_details():
   if name:

      result = merged_df[merged_df['name'].str.contains(name, case=False)]

      results = result[['name','rank','movement','competitions_played',
                        'country']].reset_index(drop=True)
                                                               # For competitor details.  
      st.dataframe(results,width='stretch')

      st.subheader("🎯 Filtered by Name")

   else:
      st.subheader(":red[Enter Competitor Names !]")



def country_analysis():
    st.subheader("🌍 Country Analysis")

                                                             # Group by country.
    country_stats = merged_df.groupby("country").agg(
        competitors=("competitor_id", "count"),
        Average_points=("points", "mean")).reset_index()

                                                             # Show dataframe.
    st.dataframe(country_stats,width='stretch')

                                                             
    fig = px.bar(country_stats,
           x="country",y="competitors",
           title="Number of Competitors by Country",         # Plot: Competitors by Country (Bar Chart).
           color="competitors", text="competitors")
    
    fig.update_layout(xaxis_title="Country", yaxis_title="Number of Competitors")
    
    st.plotly_chart(fig, width='stretch')


def leaderboard():
    st.subheader("🏅 Top Ranked Competitors")                  # Top 10 rank holder.

    top_ranked = merged_df.sort_values(by="rank").head(10)[["name", 
                 "rank", "country"]].reset_index(drop=True)
    
    st.dataframe(top_ranked, width='stretch')

    st.subheader("🚀 Competitor With High Points")              # Top 10 high points.
    
    top_points = merged_df.sort_values(by="points", ascending=False).head(10)[["name",
                 "points", "country"]].reset_index(drop=True)

    st.dataframe(top_points, width='stretch')
   

if selector == 'Filtered Competitors':
   filtered_competitors()
elif selector == 'Country Analysis':
   country_analysis()
elif selector == 'Leader boards':
   leaderboard()
else:     
   competitor_details()