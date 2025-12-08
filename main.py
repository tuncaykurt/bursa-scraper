from camoufox import AsyncCamoufox
import asyncio
from camoufox_captcha import solve_captcha
import urllib.parse
import time
import sys
import re
import requests


def print_banner():
    """Print a cool ASCII banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🏠 SAHIBINDEN SCRAPER 🏠                           ║
║                        ━━━━━━━━━━━━━━━━━━━━━━━━━━━                            ║
║                    Powered by Camoufox & Claude Code                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print("\033[96m" + banner + "\033[0m")


async def animated_loading(text, duration=2):
    """Show animated loading with spinning wheel"""
    spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end_time = time.time() + duration

    while time.time() < end_time:
        for char in spinner_chars:
            sys.stdout.write(f"\r\033[93m{char} {text}\033[0m")
            sys.stdout.flush()
            await asyncio.sleep(0.1)

    sys.stdout.write(f"\r\033[92m✓ {text}\033[0m\n")
    sys.stdout.flush()


def print_progress_bar(current, total, width=50):
    """Print a cool progress bar"""
    percent = current / total
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    print(f"\033[94m[{bar}] {current}/{total} ({percent:.1%})\033[0m")


def print_section_header(title):
    """Print a fancy section header"""
    print(f"\n\033[95m{'='*80}\033[0m")
    print(f"\033[95m{title.center(80)}\033[0m")
    print(f"\033[95m{'='*80}\033[0m\n")


def print_listing_info(i, listing_data):
    """Print listing information with fancy formatting"""
    print(
        f"\n\033[96m┌─── 📋 LISTING {i} ───────────────────────────────────────────────────────┐\033[0m")

    fields = [
        ("🏷️  Title", listing_data['title']),
        ("💰 Price", listing_data['price']),
        ("🌍 Province", listing_data['province']),
        ("📍 Area", listing_data['area']),
        ("🏘️  Neighborhood", listing_data['neighborhood']),
        ("📅 Date", listing_data['date']),
        ("📝 Description", listing_data['description']),
        ("👥 Owner Type", listing_data['owner_type']),
        ("👤 Owner Name", listing_data['owner_name']),
        ("📞 Owner Phone", listing_data['owner_phone']),
        ("🔗 URL", listing_data['url'])
    ]

    # Add store name for agent listings
    if listing_data['owner_type'] == 'Agent' and listing_data['store_name'] != 'N/A':
        fields.insert(-1, ("🏢 Store/Agency", listing_data['store_name']))

    for label, value in fields:
        if len(value) > 60:
            value = value[:57] + "..."
        print(f"\033[96m│\033[0m {label:<15} \033[97m{value}\033[0m")

    # Print additional attributes if they exist
    if 'attributes' in listing_data and listing_data['attributes']:
        print(f"\033[96m│\033[0m")
        print(f"\033[96m│\033[0m \033[93m📊 Additional Details:\033[0m")
        for attr_label, attr_value in listing_data['attributes'].items():
            if len(attr_value) > 55:
                attr_value = attr_value[:52] + "..."
            print(
                f"\033[96m│\033[0m   {attr_label:<12} \033[97m{attr_value}\033[0m")

    print(f"\033[96m└──────────────────────────────────────────────────────────────────────────────┘\033[0m")


async def scrape_listing_details(page, listing_url):
    """Scrape details from a single listing page"""
    try:
        # Increased timeout for proxy
        await page.goto(listing_url, timeout=60000)
        await page.wait_for_timeout(1500)

        # Extract all the required information using the selectors
        title_element = await page.query_selector("#classifiedDetail > div.classifiedDetail > div.classifiedDetailTitle > h1")
        title = await title_element.text_content() if title_element else "N/A"

        price_element = await page.query_selector("#classifiedDetail > div.classifiedDetail > div.classifiedDetailContent > div.classifiedInfo > h3 > span")
        price = await price_element.text_content() if price_element else "N/A"

        province_element = await page.query_selector("#classifiedDetail > div.classifiedDetail > div.classifiedDetailContent > div.classifiedInfo > h2 > a:nth-child(1)")
        province = await province_element.text_content() if province_element else "N/A"

        area_element = await page.query_selector("#classifiedDetail > div.classifiedDetail > div.classifiedDetailContent > div.classifiedInfo > h2 > a:nth-child(3)")
        area = await area_element.text_content() if area_element else "N/A"

        neighborhood_element = await page.query_selector("#classifiedDetail > div.classifiedDetail > div.classifiedDetailContent > div.classifiedInfo > h2 > a:nth-child(5)")
        neighborhood = await neighborhood_element.text_content() if neighborhood_element else "N/A"

        date_element = await page.query_selector("#classifiedDetail > div.classifiedDetail > div.classifiedDetailContent > div.classifiedInfo > ul > li:nth-child(2) > span")
        date = await date_element.text_content() if date_element else "N/A"

        # Extract clean text content from the entire classifiedDescription div
        desc_element = await page.query_selector("#classifiedDescription")
        description = "N/A"
        if desc_element:
            description_text = await desc_element.text_content()
            if description_text:
                description = " ".join(description_text.strip().split())
            else:
                description = "N/A"

        # Check if it's an individual user or agent/real estate office
        individual_user_container = await page.query_selector(".classifiedUserContent")
        agent_container = await page.query_selector(".user-info-module")

        owner_name = "N/A"
        owner_phone = "N/A"
        owner_type = "N/A"
        store_name = "N/A"

        if individual_user_container:
            # Individual user listing
            owner_type = "Individual"

            # Get username from CSS content property in style tag
            try:
                style_element = await page.query_selector(".username-info-area style")
                if style_element:
                    style_content = await style_element.text_content()
                    if style_content and 'content:' in style_content:
                        match = re.search(
                            r'content:\s*["\']([^"\']+)["\']', style_content)
                        if match:
                            owner_name = match.group(1).strip()
            except:
                pass

            # Get phone numbers from phoneInfoPart
            phone_list = []
            phone_items = await page.query_selector_all("#phoneInfoPart li")

            for item in phone_items:
                phone_type_element = await item.query_selector("strong")
                phone_number_element = await item.query_selector("span[data-content]")

                if phone_type_element and phone_number_element:
                    phone_type = await phone_type_element.text_content()
                    phone_number = await phone_number_element.get_attribute("data-content")
                    if phone_type and phone_number:
                        phone_list.append(
                            f"{phone_type.strip()}: {phone_number.strip()}")

            owner_phone = " | ".join(phone_list) if phone_list else "N/A"

        elif agent_container:
            # Agent/real estate office listing
            owner_type = "Agent"

            # Get store/agency name
            store_name_element = await page.query_selector(".user-info-store-name a")
            if store_name_element:
                store_name = await store_name_element.text_content()
                store_name = store_name.strip() if store_name else "N/A"

            # Get agent's personal name
            agent_name_element = await page.query_selector(".user-info-agent h3")
            if agent_name_element:
                owner_name = await agent_name_element.text_content()
                owner_name = owner_name.strip() if owner_name else "N/A"

            # Get phone numbers from dl-group divs
            phone_list = []
            phone_groups = await page.query_selector_all(".user-info-phones .dl-group")

            for group in phone_groups:
                phone_type_element = await group.query_selector("dt")
                phone_number_element = await group.query_selector("dd")

                if phone_type_element and phone_number_element:
                    phone_type = await phone_type_element.text_content()
                    phone_number = await phone_number_element.text_content()
                    if phone_type and phone_number:
                        phone_list.append(
                            f"{phone_type.strip()}: {phone_number.strip()}")

            owner_phone = " | ".join(phone_list) if phone_list else "N/A"

        # Scrape additional listing attributes from classifiedInfoList
        listing_attributes = {}
        classified_info_lists = await page.query_selector_all("ul.classifiedInfoList")

        for info_list in classified_info_lists:
            list_items = await info_list.query_selector_all("li")

            for item in list_items:
                label_element = await item.query_selector("strong")
                value_element = await item.query_selector("span")

                if label_element and value_element:
                    label = await label_element.text_content()
                    value = await value_element.text_content()

                    if label and value:
                        listing_attributes[label.strip()] = value.strip()

        return {
            "url": listing_url,
            "title": title.strip() if title != "N/A" else "N/A",
            "price": price.strip() if price != "N/A" else "N/A",
            "province": province.strip() if province != "N/A" else "N/A",
            "area": area.strip() if area != "N/A" else "N/A",
            "neighborhood": neighborhood.strip() if neighborhood != "N/A" else "N/A",
            "date": date.strip() if date != "N/A" else "N/A",
            "description": description.strip() if description != "N/A" else "N/A",
            "owner_type": owner_type,
            "owner_name": owner_name,
            "owner_phone": owner_phone,
            "store_name": store_name,
            "attributes": listing_attributes
        }
    except Exception as e:
        print(f"Error scraping {listing_url}: {str(e)}")
        return None


def test_proxy_connectivity(proxy_config, max_retries=3, retry_delay=2):
    """Test if proxy is working by making a simple HTTP request with retry logic"""
    if not proxy_config or not proxy_config.get('server'):
        return True, "No proxy configured", None

    # New format has auth embedded in URL
    proxy_url = proxy_config['server']
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }

    # Retry loop for proxy connection
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get('http://httpbin.org/ip',
                                    proxies=proxies, timeout=10)
            if response.status_code == 200:
                proxy_ip = response.json().get('origin', 'Unknown')

                try:
                    geo_response = requests.get(
                        f'http://ip-api.com/json/{proxy_ip}', timeout=10)
                    if geo_response.status_code == 200:
                        geo_data = geo_response.json()
                        country = geo_data.get('country', 'Unknown')
                        country_code = geo_data.get('countryCode', 'Unknown')
                        city = geo_data.get('city', 'Unknown')
                        region = geo_data.get('regionName', 'Unknown')

                        location_info = f"{city}, {region}, {country} ({country_code})"
                        return True, f"Proxy working. IP: {proxy_ip}", location_info
                    else:
                        return True, f"Proxy working. IP: {proxy_ip}", "Country lookup failed"
                except:
                    return True, f"Proxy working. IP: {proxy_ip}", "Country lookup failed"
            else:
                return False, f"Proxy returned status code: {response.status_code}", None

        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, ConnectionResetError) as e:
            if attempt < max_retries:
                print(
                    f"Proxy connection attempt {attempt}/{max_retries} failed, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                continue
            else:
                return False, f"Proxy connection failed after {max_retries} attempts: {str(e)}", None
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                print(
                    f"Proxy timeout attempt {attempt}/{max_retries}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                continue
            else:
                return False, f"Proxy connection timed out after {max_retries} attempts", None
        except Exception as e:
            if attempt < max_retries:
                print(
                    f"Proxy test attempt {attempt}/{max_retries} failed, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                continue
            else:
                return False, f"Proxy test error after {max_retries} attempts: {str(e)}", None

    return False, "Proxy test failed for unknown reason", None


async def run_scraper(limit=5, proxy=None):
    """
    Main scraping function - scrapes BURSA only, all listings
    
    Args:
        limit: Number of listings to scrape
        proxy: Proxy configuration (optional)
    """
    scraped_listings = []

    # Track start time
    start_time = time.time()

    # Test proxy connectivity if proxy is provided
    if proxy:
        print(f"🌐 Using proxy: {proxy.get('server')}")
        print("⚠️  Skipping proxy validation - will test during scraping")
        # Skip validation, let Playwright/Camoufox handle it

    # Prepare browser options with better fingerprinting
    browser_options = {
        'headless': True,
        'geoip': True,
        'humanize': True,  # Changed to True for better behavior
        'i_know_what_im_doing': True,
        'config': {'forceScopeAccess': True},
        'disable_coop': True,
        'args': [
            '--disable-dev-shm-usage',
            '--no-sandbox'
        ]
    }

    # Add proxy configuration if provided
    if proxy:
        if proxy.get('server'):
            browser_options['proxy'] = {
                'server': proxy['server']
            }

            if proxy.get('username') and proxy.get('password'):
                browser_options['proxy']['username'] = proxy['username']
                browser_options['proxy']['password'] = proxy['password']

            print(f"Camoufox will use proxy: {proxy['server']}")

    async with AsyncCamoufox(**browser_options) as browser:
        # Create context with Turkish locale
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='tr-TR',
            timezone_id='Europe/Istanbul',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()

        # Simple Bursa URL - NO FILTERS
        bursa_url = "https://www.sahibinden.com/satilik-daire/bursa"
        
        print(f"\n🔍 Scraping ALL listings from Bursa: {bursa_url}\n")

        # Navigate to Bursa listings page
        await page.goto(bursa_url, wait_until='networkidle')
        print(f"📍 Navigated to: {page.url}")

        # Handle captcha with increased wait times
        max_captcha_attempts = 3
        for attempt in range(max_captcha_attempts):
            success = await solve_captcha(page, captcha_type='cloudflare', challenge_type='interstitial')

            if success:
                print("✅ Cloudflare captcha solved, waiting for page to load...")
                await page.wait_for_timeout(15000)  # Increased from 5000 to 15000

                # Check current URL
                current_url = page.url
                print(f"📍 Current URL after captcha: {current_url}")
                
                # If redirected to login, try to go back to listings
                if 'login' in current_url:
                    print("⚠️  Redirected to login page, attempting to navigate back...")
                    await page.goto(bursa_url, wait_until='networkidle')
                    await page.wait_for_timeout(5000)
                    current_url = page.url
                    print(f"📍 URL after navigation: {current_url}")

                try:
                    await page.wait_for_selector("#searchResultsTable", timeout=10000)
                    print("✅ Search results table found!")
                    break
                except:
                    print("⚠️  Search results table not found yet, continuing...")
                    continue
            else:
                if attempt < max_captcha_attempts - 1:
                    print(f"⚠️  Captcha attempt {attempt + 1} failed, retrying...")
                    await page.wait_for_timeout(2000)
                    continue
                else:
                    print("⚠️  All captcha attempts exhausted, waiting longer...")
                    await page.wait_for_timeout(30000)
                    break

        # Find all listing links - UPDATED SELECTOR WITH DEBUG
        try:
            # Wait for the search results table to load
            print("⏳ Waiting for search results table...")
            
            # Check if we're still on login page
            current_url = page.url
            if 'login' in current_url:
                print(f"❌ Still on login page: {current_url}")
                print("⚠️  Sahibinden.com requires authentication from your location/IP")
                return []
            
            await page.wait_for_selector("#searchResultsTable > tbody", timeout=30000)
            print("✅ Search results table loaded")

            # Get all listing rows - FIXED SELECTOR
            print("🔍 Looking for listing rows...")
            listing_rows = await page.query_selector_all("tr.searchResultsItem")

            if not listing_rows:
                print("⚠️  No listing rows found!")
                
                # DEBUG: Let's see what's on the page
                page_html = await page.content()
                print(f"📄 Page HTML length: {len(page_html)} characters")
                print(f"📄 First 1000 chars: {page_html[:1000]}")
                
                # Try alternative selectors
                print("🔍 Trying alternative selectors...")
                alt_rows = await page.query_selector_all("tr[data-id]")
                print(f"📊 Found {len(alt_rows)} rows with data-id attribute")
                
                alt_rows2 = await page.query_selector_all(".searchResultsItem")
                print(f"📊 Found {len(alt_rows2)} rows with searchResultsItem class")
                
                return []

            print(f"✅ Found {len(listing_rows)} total listings on page")

            # Extract href attributes from the links
            listing_urls = []
            for row in listing_rows[:limit]:
                link = await row.query_selector("td.searchResultsTitleValue a")
                if link:
                    href = await link.get_attribute("href")
                    if href:
                        full_url = urllib.parse.urljoin("https://www.sahibinden.com", href)
                        listing_urls.append(full_url)

            print(f"✅ Will scrape {len(listing_urls)} listings")

            # Scrape each listing sequentially
            for i, listing_url in enumerate(listing_urls, 1):
                print(f"🔄 Scraping {i}/{len(listing_urls)}: {listing_url}")
                listing_data = await scrape_listing_details(page, listing_url)

                if listing_data:
                    scraped_listings.append(listing_data)
                    print(f"✅ Successfully scraped listing {i}")
                else:
                    print(f"❌ Failed to scrape listing {i}")

                # Small delay between requests
                await page.wait_for_timeout(1000)

        except Exception as e:
            print(f"❌ CRITICAL ERROR: {str(e)}")
            import traceback
            print(f"📋 Full traceback:")
            print(traceback.format_exc())
            
            # Try to get page info
            try:
                page_url = page.url
                print(f"🌐 Current URL: {page_url}")
                page_html = await page.content()
                print(f"📄 Page HTML length: {len(page_html)} characters")
            except:
                pass
                
            return []

    # Calculate statistics
    end_time = time.time()
    total_time = end_time - start_time

    import json
    total_data_bytes = len(json.dumps(scraped_listings).encode('utf-8'))
    total_data_kb = total_data_bytes / 1024
    total_data_mb = total_data_kb / 1024

    # Print statistics
    print(f"\n{'='*80}")
    print(f"✅ Scraping completed successfully!")
    print(f"📊 Total listings scraped: {len(scraped_listings)}")
    print(f"⏱️  Time spent: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")

    if total_data_mb >= 1:
        print(f"💾 Data consumed: {total_data_mb:.2f} MB ({total_data_kb:.2f} KB)")
    else:
        print(f"💾 Data consumed: {total_data_kb:.2f} KB ({total_data_bytes} bytes)")

    if len(scraped_listings) > 0:
        avg_time_per_listing = total_time / len(scraped_listings)
        print(f"⚡ Average time per listing: {avg_time_per_listing:.2f} seconds")

    print(f"{'='*80}\n")

    return scraped_listings


async def main():
    """CLI entry point"""
    print_banner()
    listings = await run_scraper(5)

    # Print listings for CLI usage
    for i, listing_data in enumerate(listings, 1):
        print_listing_info(i, listing_data)

if __name__ == "__main__":
    asyncio.run(main())
