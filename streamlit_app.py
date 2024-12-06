```python
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Biopolymer Company Finder")

st.title("🔬 Biopolymer Company Finder")
st.write("Search for companies working on biopolymers and sustainable materials")

# Simple search interface
search_term = st.selectbox(
    "What type of companies are you looking for?",
    [
        "Biopolymer manufacturers",
        "Biodegradable plastic companies",
        "Sustainable packaging companies",
        "Compostable materials manufacturers"
    ]
)

country = st.text_input("Enter country (optional)")

if st.button("Search"):
    with st.spinner("Searching..."):
        # Form search query
        query = f"{search_term}"
        if country:
            query += f" {country}"
            
        try:
            # Basic web search
            url = f"https://duckduckgo.com/html/?q={query}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                # Extract first 5 results
                for result in soup.find_all('div', class_='result')[:5]:
                    title = result.find('a').text
                    link = result.find('a')['href']
                    description = result.find('div', class_='result__snippet').text
                    
                    results.append({
                        "Company": title,
                        "Website": link,
                        "Description": description
                    })
                
                if results:
                    st.success(f"Found {len(results)} companies")
                    df = pd.DataFrame(results)
                    st.dataframe(df)
                    
                    # Add download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download Results",
                        csv,
                        "biopolymer_companies.csv",
                        "text/csv"
                    )
                else:
                    st.warning("No results found. Try different search terms.")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
```
