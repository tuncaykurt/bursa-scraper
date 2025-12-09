# Selectors for scraping

## Information

latest listings url: https://www.sahibinden.com/satilik/bursa

example listing url structure: https://www.sahibinden.com/ilan/{listing_title}-{listing_id}/detay

in latest listing url table selector which includes items: "#searchResultsTable > tbody"

inside tbody, bunch of tr tags with class of ".searchResultsItem"

in .searchResultsItem we can get <a> link tag that forwards to listing details page: "td.searchResultsTitleValue > a.classifiedTitle"

in detail page here is the information and selectors:

title: "#classifiedDetail > div.classifiedDetail > div.classifiedDetailTitle > h1"

price: "#classifiedDetail > div.classifiedDetail > div.classifiedDetailContent > div.classifiedInfo > h3 > span"

province: "#classifiedDetail > div.classifiedDetail > div.classifiedDetailContent > div.classifiedInfo > h2 > a:nth-child(1)"

area: "#classifiedDetail > div.classifiedDetail > div.classifiedDetailContent > div.classifiedInfo > h2 > a:nth-child(3)"

neighborhood: "#classifiedDetail > div.classifiedDetail > div.classifiedDetailContent > div.classifiedInfo > h2 > a:nth-child(5)"

date: "#classifiedDetail > div.classifiedDetail > div.classifiedDetailContent > div.classifiedInfo > ul > li:nth-child(2) > span"

desc: There is also a <div id="classifiedDescription"> which contains multiple <p>, <b>, <font>, <div>, etc. I want to extract only the clean text content (no HTML, no <br>, no image URLs). Just concatenate the text into one string.

also for other attributes about listing details: I want to scrape real estate listing details from a page. Each attribute is inside a <ul class="classifiedInfoList"> with multiple <li> elements. In every <li>, the label is inside a <strong> tag (like "İlan No", "İlan Tarihi", "m² (Brüt)", etc.), and the corresponding value is inside a <span>.

listing owner informations:  If it’s an individual user (<div class="classifiedUserContent">): Get the user’s name from the hidden CSS content: property inside <style> in .username-info-area. Get phone numbers from <ul id="phoneInfoPart">, where <strong> is the phone type (e.g. Cep) and the real number is in <span data-content>.

If it’s an agent/real estate office (<div class="user-info-module">): Get the agency/store name from .user-info-store-name a. Get the agent’s personal name from .user-info-agent h3. Get phone type/number pairs from .user-info-phones .dl-group (<dt> = type, <dd> = number).
