```python
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
```