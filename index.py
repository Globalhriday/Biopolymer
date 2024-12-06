import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from datetime import datetime
import re
from urllib.parse import urljoin

class BiopolymerResearchScraper:
    def __init__(self, delay=2):
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.organizations = []
        
    def search_organizations(self, max_pages=5):
        """
        Search for organizations using multiple search queries and sources
        """
        search_queries = [
            "biopolymer research companies",
            "bioplastic manufacturers",
            "compostable plastic research organizations",
            "biodegradable polymer companies",
            "sustainable plastic research institutes",
            "biopolymer research institutes India"
        ]
        
        for query in search_queries:
            self._search_google(query, max_pages)
            self._search_linkedin_companies(query, max_pages)
            time.sleep(self.delay)
    
    def _search_google(self, query, max_pages):
        """
        Search using Google's search engine
        """
        base_url = f"https://www.google.com/search?q={query}"
        
        try:
            for page in range(max_pages):
                response = requests.get(
                    f"{base_url}&start={page*10}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    self._parse_google_results(response.text)
                time.sleep(self.delay)
        except Exception as e:
            print(f"Error in Google search: {str(e)}")
    
    def _search_linkedin_companies(self, query, max_pages):
        """
        Search companies on LinkedIn
        Note: This is a simplified version. Real LinkedIn scraping would require authentication
        """
        base_url = f"https://www.linkedin.com/company/search?keywords={query}"
        # Implementation would depend on LinkedIn's API access or authentication method
        pass
    
    def _parse_google_results(self, html_content):
        """
        Parse Google search results and extract organization information
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        results = soup.find_all('div', class_='g')
        
        for result in results:
            try:
                title = result.find('h3').text
                url = result.find('a')['href']
                snippet = result.find('div', class_='VwiC3b').text
                
                # Check if it's likely a research organization
                if self._is_research_organization(title, snippet):
                    self._extract_organization_details(url)
            except:
                continue
    
    def _is_research_organization(self, title, snippet):
        """
        Check if the result is likely a research organization
        """
        keywords = [
            'research', 'biopolymer', 'bioplastic', 'laboratory',
            'institute', 'R&D', 'development', 'sustainable',
            'biodegradable', 'compostable', 'manufacturer'
        ]
        
        text = (title + ' ' + snippet).lower()
        return any(keyword in text for keyword in keywords)
    
    def _extract_organization_details(self, url):
        """
        Extract detailed information about an organization from its website
        """
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract organization details
            org_info = {
                'name': self._extract_text(soup, ['h1', '.company-name', '.org-name']),
                'website': url,
                'address': self._extract_address(soup),
                'email': self._extract_email(soup),
                'phone': self._extract_phone(soup),
                'contact_person': self._extract_contact_person(soup),
                'description': self._extract_text(soup, ['.about', '.description', '#about']),
                'research_areas': self._extract_research_areas(soup),
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
            
            # Only add if we found meaningful information
            if org_info['name'] and (org_info['email'] or org_info['phone']):
                self.organizations.append(org_info)
                
        except Exception as e:
            print(f"Error extracting organization details from {url}: {str(e)}")
    
    def _extract_text(self, soup, selectors):
        """Extract text using multiple possible selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.text.strip()
        return None
    
    def _extract_email(self, soup):
        """Extract email addresses from the page"""
        text = soup.get_text()
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return '; '.join(set(emails)) if emails else None
    
    def _extract_phone(self, soup):
        """Extract phone numbers from the page"""
        text = soup.get_text()
        phones = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
        return '; '.join(set(phones)) if phones else None
    
    def _extract_address(self, soup):
        """Extract physical address"""
        address_selectors = [
            '.address',
            '[itemprop="address"]',
            '.contact-address',
            '#address'
        ]
        return self._extract_text(soup, address_selectors)
    
    def _extract_contact_person(self, soup):
        """Extract contact person information"""
        person_selectors = [
            '.contact-person',
            '.team-lead',
            '.director',
            '.head-research'
        ]
        return self._extract_text(soup, person_selectors)
    
    def _extract_research_areas(self, soup):
        """Extract research areas related to biopolymers"""
        text = soup.get_text().lower()
        research_keywords = [
            'biopolymer', 'bioplastic', 'biodegradable',
            'compostable', 'sustainable materials', 'green polymers'
        ]
        found_areas = [k for k in research_keywords if k in text]
        return '; '.join(found_areas) if found_areas else None
    
    def save_results(self, filename='biopolymer_research_organizations.csv'):
        """Save results to CSV file"""
        df = pd.DataFrame(self.organizations)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Results saved to {filename}")
        
        # Also save as JSON for better data preservation
        with open(filename.replace('.csv', '.json'), 'w', encoding='utf-8') as f:
            json.dump(self.organizations, f, ensure_ascii=False, indent=2)
    
    def filter_results(self, country=None, research_area=None):
        """Filter results by country or research area"""
        filtered = self.organizations
        
        if country:
            filtered = [
                org for org in filtered
                if country.lower() in (org['address'] or '').lower()
            ]
            
        if research_area:
            filtered = [
                org for org in filtered
                if research_area.lower() in (org['research_areas'] or '').lower()
            ]
            
        return filtered

# Example usage
if __name__ == "__main__":
    # Initialize scraper
    scraper = BiopolymerResearchScraper(delay=3)
    
    # Search for organizations
    scraper.search_organizations(max_pages=3)
    
    # Filter for Indian organizations
    indian_orgs = scraper.filter_results(country='India')
    
    # Save all results
    scraper.save_results()
