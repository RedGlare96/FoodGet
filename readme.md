# GrabFood Scraper
Scraper for the GrabFood website. Enters address as per input and scrapes Latitude and Longitude of the results without leaving the domain

# Install instructions
1. Clone repository
2. Create Python venv
3. Install libraries using the command `pip install -r requirments.txt`
4. [Install Epic browser](https://www.mediafire.com/file/enmuh6ndt2iozkw/epic-bin.zip/file) (Download and extract)
5. [Install cookie with pre-configured VPN settings](https://www.mediafire.com/file/bu2tej14r1g251u/epic-proxies.zip/file) (Download and extract)
6. Change the value of the variable 'add' to any required address
7. Change the value of the variable 'pagination' to set a finite number of clicks to the 'load more' button. Set to a very high number such as 100 if you want it to continue until the button is gone.
8. Run `foodget.py`

# Attempt to streamline scraping process
Currently, the script opens each restaurant in a new tab and gets the data from the cached internal api response Nextjs leaves behind from Redux. Opening this page will cause a 429 error to come up on the page. To alleviate this, the script keeps refreshing the page, increasing wait time between refresh attempts in every 3 unsuccessful attempts. The browser will never be blocked because Cloudfront is unable to properly fingerprint the browser due to the patched version of chromedriver being used and Epic browser reporting a fake value each time a canvas fingerprint attempt is detected. 

This is currently the most reliable way to get the latitude and longitude of all restaurants in a location but it is very slow due to extensive refreshing required. However if I had access to more encrypted proxies, I could open each result with a fresh proxy and eliminate this issue altogether. 

In the branch **nextjs-redux** in this repository, an attempt was made to access the cached api response of all results in the results' page itself but the developers of the site have streamlined this process by using nextjs' Server Side Rendering (ssr) flow which updates the page by directly making API calls to the server and does not cache the data anywhere. The only way to get cached data is by refreshing the page and this gives data of only the first 8 results. There is no way to coax the Next Js engine to cache all the results since the workflow just does not work this way 
