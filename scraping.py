# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt


# ths function initializes the browser, creates a data dictionary and ends the WebDriver and return the scraped data
def scrape_all():
    # Initiate headless driver for deployment
    # Set up splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # When we were testing our code in Jupyter, headless was set as False so we could see the scraping in action. 
    # Now that we are deploying our code into a usable web app, we don't need to watch the script work, hence its True

    # This line of code tells Python that we'll be using our mars_news function to pull this data.
    news_title, news_paragraph = mars_news(browser)


    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
        # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # convert the browser html to soup object 
    html = browser.html
    news_soup = soup(html, 'html.parser')

     # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # In this line of code, we chained .find onto our previously assigned variable, slide_elem. 
        # When we do this, we're saying, "This variable holds a ton of information, so look inside of that 
        # information to find this specific data." 
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        #news_title

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
        #news_p

    except AttributeError:
        return None, None

    return news_title, news_p
    

### Featured Images

def featured_image(browser): 
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button. [1] clicks second button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        # An img tag is nested within this HTML, so we've included it.
        # .get('src') pulls the link to the image.
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        #img_url_rel

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    #img_url
    
    return img_url

# The main container is the <table /> tag. Inside the table is <tbody />, which is the body of the table
# —the headers, columns, and rows. <tr /> is the tag for each table row. 
# Within that tag, the table data is stored in <td /> tags. This is where the columns are established.
# Instead of scraping each row, or the data in each <td />, 
# we're going to scrape the entire table with Pandas' .read_html() function.

### Mars facts
def mars_facts():
try: 
    #[0] to read the first item on the list 
    # use 'read_html" to scrape the facts table into a dataframe
    df = pd.read_html('https://galaxyfacts-mars.com')[0]
# BaseException is a little bit of a catchall, raised when any of the built-in exceptions are encountered and 
# it won't handle any user-defined exceptions. 
except BaseException: 
    return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    #df

    # Pandas can easily convert our DataFrame back into HTML-ready code using the .to_html() function
    #df.to_html()
    return df.to_html()

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
