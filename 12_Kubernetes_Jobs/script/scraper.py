import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import os
import sys

def get_city_config():
    """Get city configuration from environment variables"""
    city = os.getenv('CITY', 'warszawa')
    pages = int(os.getenv('PAGES', '12'))
    delay = float(os.getenv('DELAY', '1.0'))
    output_dir = os.getenv('OUTPUT_DIR', '/data')
    
    return {
        'city': city,
        'pages': pages,
        'delay': delay,
        'output_dir': output_dir
    }

def scrape_city(city, pages, delay, output_dir):
    """Scrape offers for a specific city"""
    base_url = f"https://adresowo.pl/mieszkania/{city}/_l{{}}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    print(f"🏙️ Starting scrape for {city}")
    
    # Step 1: Gather offer URLs
    offer_urls = []
    for page in range(1, pages + 1):
        url = base_url.format(page)
        print(f"📄 Scraping page {page}/{pages}")
        
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            items = soup.select('section.search-results__item')
            
            for item in items:
                data_url = item.get('data-url')
                if data_url:
                    offer_urls.append(f'https://adresowo.pl{data_url}')
            
            time.sleep(delay)  # Be nice to the server
            
        except Exception as e:
            print(f"❌ Error scraping page {page}: {e}")
            continue
    
    # Remove duplicates
    offer_urls = list(dict.fromkeys(offer_urls))
    print(f"🔍 Found {len(offer_urls)} unique offer URLs")
    
    if not offer_urls:
        print("❌ No offers found")
        return
    
    # Step 2: Scrape offer details
    results = []
    for i, url in enumerate(offer_urls, 1):
        print(f"🏠 Scraping offer {i}/{len(offer_urls)}")
        
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            price = currency = url_offer = address = description = None
            num_images = None
            
            # JSON-LD data
            for script in soup.select('script[type="application/ld+json"]'):
                try:
                    data = json.loads(script.string)
                except Exception:
                    continue
                    
                if isinstance(data, dict) and data.get('@type') == 'Offer':
                    price = data.get('price')
                    currency = data.get('priceCurrency')
                    url_offer = data.get('url', url)
                
                graph = data.get('@graph') if isinstance(data, dict) else None
                if graph:
                    for node in graph:
                        if node.get('@type') == 'Place':
                            address = node.get('address', {}).get('streetAddress')
                            description = node.get('description')
                            break
            
            # Image count from inline JS
            js_text = soup.find(string=lambda t: t and 're.numberOfImages' in t)
            if js_text:
                try:
                    num_images = int(js_text.split('=')[1].split(';')[0].strip())
                except Exception:
                    num_images = None
            
            results.append({
                'offer_url': url_offer or url,
                'price': price,
                'currency': currency,
                'num_images': num_images,
                'street_address': address,
                'description': description,
                'city': city
            })
            
            time.sleep(delay)  # Be nice to the server
            
        except Exception as e:
            print(f"❌ Error scraping offer {url}: {e}")
            continue
    
    # Step 3: Save to CSV
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"adresowo_offers_{city}.csv")
    
    if results:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"✅ Data saved to {output_file}")
        print(f"📊 Total offers scraped: {len(results)}")
    else:
        print("❌ No results to save")

def main():
    """Main function"""
    config = get_city_config()
    print(f"🚀 Starting scraper with config: {config}")
    
    try:
        scrape_city(
            city=config['city'],
            pages=config['pages'],
            delay=config['delay'],
            output_dir=config['output_dir']
        )
        print("✅ Scraping completed successfully")
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()