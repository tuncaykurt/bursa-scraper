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
║                        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━                            ║
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
        await page.wait_for_timeout(1500)  # Slightly reduced wait time

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
            # Get all text content and clean it up
            description_text = await desc_element.text_content()
            if description_text:
                # Clean up the text: remove extra whitespace, newlines, etc.
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
                        # Extract content between quotes
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

    proxies = {
        'http': proxy_config['server'],
        'https': proxy_config['server']
    }

    # Add authentication if provided
    if proxy_config.get('username') and proxy_config.get('password'):
        import urllib.parse
        parsed = urllib.parse.urlparse(proxy_config['server'])
        auth_server = f"{parsed.scheme}://{proxy_config['username']}:{proxy_config['password']}@{parsed.netloc}"
        proxies = {
            'http': auth_server,
            'https': auth_server
        }

    # Retry loop for proxy connection
    for attempt in range(1, max_retries + 1):
        try:
            # Test with a simple HTTP request and get IP
            response = requests.get('http://httpbin.org/ip',
                                    proxies=proxies, timeout=10)
            if response.status_code == 200:
                proxy_ip = response.json().get('origin', 'Unknown')

                # Get country information from ip-api.com
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
    """Main scraping function that can be called from webhook"""
    scraped_listings = []

    # Track start time
    start_time = time.time()

    # Test proxy connectivity if proxy is provided
    if proxy:
        print(f"Testing proxy connectivity for {proxy.get('server')}...")
        is_working, message, country_info = test_proxy_connectivity(proxy)
        if not is_working:
            raise Exception(f"Proxy validation failed: {message}")
        else:
            print(f"Proxy test successful: {message}")
            if country_info:
                print(f"🌍 Proxy Location: {country_info}")

    # Prepare browser options - keep stable for captcha solving
    browser_options = {
        'headless': True,
        'geoip': True,
        'humanize': False,
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

            # Add authentication if provided
            if proxy.get('username') and proxy.get('password'):
                browser_options['proxy']['username'] = proxy['username']
                browser_options['proxy']['password'] = proxy['password']

            print(f"Camoufox will use proxy: {proxy['server']}")

    async with AsyncCamoufox(**browser_options) as browser:
        page = await browser.new_page()

        # Navigate to the BURSA listings page
        await page.goto("https://www.sahibinden.com/satilik-daire/bursa")

        # Handle multiple captcha attempts
        max_captcha_attempts = 3
        for attempt in range(max_captcha_attempts):
            # Try to solve captcha
            success = await solve_captcha(page, captcha_type='cloudflare', challenge_type='interstitial')

            if success:
                await page.wait_for_timeout(5000)

                # Check if we're on the actual listings page or still on captcha
                try:
                    await page.wait_for_selector("#searchResultsTable", timeout=10000)
                    break
                except:
                    continue
            else:
                if attempt < max_captcha_attempts - 1:
                    await page.wait_for_timeout(2000)
                    continue
                else:
                    await page.wait_for_timeout(30000)
                    break

        # Find all listing links using the selector from SELECTORS.md
        try:
            # Wait for the search results table to load
            await page.wait_for_selector("#searchResultsTable > tbody", timeout=30000)

            # Get all listing links
            listing_links = await page.query_selector_all("td.searchResultsTitleValue > a.classifiedTitle")

            if not listing_links:
                return []

            # Extract href attributes from the links
            listing_urls = []
            # Limit based on the parameter
            for link in listing_links[:limit]:
                href = await link.get_attribute("href")
                if href:
                    full_url = urllib.parse.urljoin(
                        "https://www.sahibinden.com", href)
                    listing_urls.append(full_url)

            # Scrape each listing sequentially (more stable)
            for listing_url in listing_urls:
                listing_data = await scrape_listing_details(page, listing_url)

                if listing_data:
                    scraped_listings.append(listing_data)

                # Small delay between requests
                await page.wait_for_timeout(1000)  # Reduced from 2000

        except Exception:
            return []

    # Calculate and print statistics
    end_time = time.time()
    total_time = end_time - start_time

    # Calculate total data size (approximate JSON size)
    import json
    total_data_bytes = len(json.dumps(scraped_listings).encode('utf-8'))
    total_data_kb = total_data_bytes / 1024
    total_data_mb = total_data_kb / 1024

    # Print statistics
    print(f"\n{'='*80}")
    print(f"✅ Scraping completed successfully!")
    print(f"📊 Total listings scraped: {len(scraped_listings)}")
    print(
        f"⏱️  Time spent: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")

    if total_data_mb >= 1:
        print(
            f"💾 Data consumed: {total_data_mb:.2f} MB ({total_data_kb:.2f} KB)")
    else:
        print(
            f"💾 Data consumed: {total_data_kb:.2f} KB ({total_data_bytes} bytes)")

    if len(scraped_listings) > 0:
        avg_time_per_listing = total_time / len(scraped_listings)
        print(
            f"⚡ Average time per listing: {avg_time_per_listing:.2f} seconds")

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
