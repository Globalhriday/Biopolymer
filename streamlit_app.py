import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import re

class MobileResearchFinder:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15'
        }
        self.results = []

    def search(self, query, country=None, max_results=10):
        """Simplified search function for mobile use"""
        base_url = f"https://duckduckgo.com/html/?q={query}"
        if country:
            base_url += f"+{country}"
            
        try:
            response = requests.get(base_url, headers=self.headers)
            if response.status_code == 200:
                self._parse_results(response.text, max_results)
        except Exception as e:
            st.error(f"Search error: {str(e)}")
    
    def _parse_results(self, html, max_results):
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find_all('div', class_='result')
        
        for result in results[:max_results]:
            try:
                title = result.find('h2').text.strip()
                url = result.find('a')['href']
                description = result.find('div', class_='snippet').text.strip()
                
                if self._is_relevant(title, description):
                    self._get_contact_info(url, title, description)
            except:
                continue
    
    def _is_relevant(self, title, description):
        keywords = ['biopolymer', 'bioplastic', 'biodegradable', 'compostable', 
                   'research', 'polymer', 'sustainable', 'manufacturer']
        text = (title + ' ' + description).lower()
        return any(keyword in text for keyword in keywords)
    
    def _get_contact_info(self, url, title, description):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            
            # Extract email and phone
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            phones = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
            
            self.results.append({
                'name': title,
                'website': url,
                'description': description,
                'email': '; '.join(set(emails[:3])) if emails else 'Not found',
                'phone': '; '.join(set(phones[:3])) if phones else 'Not found',
                'found_on': datetime.now().strftime('%Y-%m-%d')
            })
            
        except Exception as e:
            st.warning(f"Couldn't fetch details for {url}")

def main():
    st.set_page_config(page_title="Biopolymer Research Finder", layout="wide")
    
    st.title("🔬 Biopolymer Research Organization Finder")
    st.write("Find companies and organizations working on biopolymers, bioplastics, and compostable materials")
    
    # Search interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_type = st.selectbox(
            "What are you looking for?",
            ["Biopolymer Research Companies", 
             "Bioplastic Manufacturers",
             "Compostable Materials Research",
             "Sustainable Packaging Companies"]
        )
    
    with col2:
        country = st.text_input("Country (optional)", "")
    
    max_results = st.slider("Maximum number of results", 5, 20, 10)
    
    if st.button("🔎 Search", type="primary"):
        with st.spinner("Searching... This may take a minute..."):
            finder = MobileResearchFinder()
            finder.search(search_type, country, max_results)
            
            if finder.results:
                # Display results
                st.success(f"Found {len(finder.results)} organizations")
                
                for org in finder.results:
                    with st.expander(f"📍 {org['name']}"):
                        st.write("**Website:**", org['website'])
                        st.write("**Description:**", org['description'])
                        st.write("**Contact Email:**", org['email'])
                        st.write("**Phone:**", org['phone'])
                
                # Convert to DataFrame for download
                df = pd.DataFrame(finder.results)
                st.download_button(
                    "📥 Download Results (CSV)",
                    df.to_csv(index=False).encode('utf-8'),
                    "biopolymer_research_organizations.csv",
                    "text/csv",
                    key='download-csv'
                )
            else:
                st.warning("No results found. Try different search terms or country.")

if __name__ == "__main__":
    main()