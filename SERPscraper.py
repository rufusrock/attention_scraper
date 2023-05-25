from pandas import concat, DataFrame
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def scrape(browser):
    search_results = WebDriverWait(browser, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
    carousels = browser.find_elements(By.CSS_SELECTOR, "span[data-component-type='s-searchgrid-carousel']")
    video_elements = browser.find_elements(By.CSS_SELECTOR, "div[class='a-section sbv-video aok-relative sbv-vertical-center-within-parent']")
    banner_elements = browser.find_elements(By.CSS_SELECTOR, "div[class='s-result-item s-widget s-widget-spacing-large AdHolder s-flex-full-width']")
    other_ads = browser.find_elements(By.CSS_SELECTOR, "div[id='ad']")
    
    #resultsdf = DataFrame(columns=["ProductName", "Ad", "Rating","NoOfReviews","ListingType", "SectionHeading","URL","Price","SaveCoupon","BundlesAvailable","LimitedTimeDeal","AmazonsChoice","BestSeller","Prime","AmazonBrand","EcoFriendly","SmallBusiness","ElementWidth", "ElementHeight", "ElementArea","YCoord","XCoord","HTMLWidth", "HTMLHeight","ViewPortWidth","ViewPortHeight"])

    results_data = []

    for result in search_results:
        results_data.append(search_result_scrape(browser, result))

    for carousel in carousels: 
        results_data.append(carousel_widget_scrape(browser, carousel))
        results_data = results_data + carousel_results_scrape(browser, carousel)

    for banner in banner_elements:
        results_data.append(banner_scrape(browser, banner))

    for video in video_elements:
        results_data.append(video_scrape(browser, video))
        
    for ad in other_ads:
        results_data.append(scrape_other_ad(browser, ad))

    df = DataFrame(results_data)

    return df

def find_element(search_result, locator):
    try:
        return search_result.find_element(*locator)
    except NoSuchElementException:
        return None
    
def search_result_scrape(browser, result):
    sponsored_span_text = find_element(result, (By.CSS_SELECTOR, "span[class='puis-label-popover-default']"))
    if sponsored_span_text:
        sponsored = True
    else:
        sponsored = False

    name_element = find_element(result, (By.CSS_SELECTOR, "span[class='a-size-medium a-color-base a-text-normal']"))
    name = ""
    if name_element:
        name = name_element.get_attribute("innerHTML")
    else:
        name_element = find_element(result,  (By.CSS_SELECTOR, "span.a-size-base-plus.a-color-base.a-text-normal"))
        if name_element:
            name = name_element.get_attribute("innerHTML")

    price_element = find_element(result, (By.CSS_SELECTOR, "span.a-offscreen"))
    if price_element:
        price = price_element.get_attribute("innerHTML")
    else:
        price = "No Price Found"

    rating_list = find_element(result, (By.CSS_SELECTOR, "span[class='a-icon-alt']"))
    if rating_list:
        ratings = rating_list.get_attribute("innerHTML").split(" ")
        for string in ratings:
            if "." in string:
                rating = string
                break
    else:
        rating = "No Rating Found"
    
    amazon_banner_element = find_element(result, (By.CSS_SELECTOR, "span[class='a-color-state.puis-light-weight-text']"))
    if amazon_banner_element:
        amazon_banner = True
    else:
        amazon_banner = False
        sponsored_from_element = find_element(result, (By.CSS_SELECTOR, "span[class='a-size-micro a-color-secondary']"))
        if sponsored_from_element and "Featured from our brands" in sponsored_from_element.get_attribute("innerHTML"):
            amazon_banner = True

    prime_logo_element = find_element(result, (By.CSS_SELECTOR, "i.a-icon.a-icon-prime.a-icon-medium"))
    if prime_logo_element:
        prime_logo = True
    else:
        prime_logo = False

    icon_element = find_element(result, (By.CSS_SELECTOR, "span.a-badge-label-inner.a-text-ellipsis"))
    if icon_element:
        first_text_element = icon_element.find_element(By.CSS_SELECTOR, "span[class='a-badge-text']").get_attribute("innerHTML")
        if "Best" in first_text_element:
            best_seller = True
            amazons_choice = False
        elif "Amazon's" in first_text_element:
            best_seller = False
            amazons_choice = True
        else:
            best_seller = False
            amazons_choice = False
    else:
        best_seller = False
        amazons_choice = False

    limited_time_deal_element = find_element(result, (By.CSS_SELECTOR, "span[data-a-badge-color='sx-lightning-deal-red']"))
    if limited_time_deal_element and limited_time_deal_element.find_element(By.CSS_SELECTOR, "span[class='a-badge-text']").get_attribute("innerHTML") == "Limited time deal":
            limited_time_deal = True
    else:
        limited_time_deal = False

    save_coupon_element = find_element(result, (By.CSS_SELECTOR, "span[class='a-size-base s-highlighted-text-padding aok-inline-block s-coupon-highlight-color']"))
    if save_coupon_element and "Save" in save_coupon_element.get_attribute("innerHTML"):
        save_string = save_coupon_element.get_attribute("innerHTML").split(" ")
        for part in save_string:
            if "$" in part or "%" in part:
                save_coupon = part
                break
    else:
        save_coupon = ""

    labels = result.find_elements(By.CSS_SELECTOR, "a[class='a-link-normal s-underline-text s-underline-link-text s-link-style']")
    if labels:
        small_business = False
        for label in labels:
            if label.get_attribute("src") == "https://m.media-amazon.com/images/I/111mHoVK0kL._SS200_.png":
                small_business = True
                break

    images = result.find_elements(By.CSS_SELECTOR,"img[class='s-image']")
    eco_friendly = False
    small_business = False
    if images:
        for image in images:
            if image.get_attribute("src") == "https://m.media-amazon.com/images/I/216-OX9rBaL._SS200_.png":
                eco_friendly = True
            elif image.get_attribute("src") == "https://m.media-amazon.com/images/I/111mHoVK0kL._SS200_.png":
                small_business = True

    
    links = result.find_elements(By.CSS_SELECTOR, "a[class='a-link-normal s-underline-text s-underline-link-text s-link-style']")
    bundles = False
    if links:
        for link in links:
            if "Bundles" in link.text:
                bundles = True
                break

    href = find_element(result, (By.CSS_SELECTOR, "a[class='a-link-normal s-no-outline']"))
    if href:
        href = href.get_attribute("href")
        if "amazon.com" in href:
            url = href
        else:
            url = "https://www.amazon.com" + href
    else:
        url = "URL Not Found"

    no_of_reviews_element = find_element(result, (By.CSS_SELECTOR, "span.a-size-base.s-underline-text"))
    if no_of_reviews_element:
        no_of_reviews = no_of_reviews_element.text.replace(",", "").replace("(","").replace(")","")
    else:
        no_of_reviews = "No Reviews Found"

    element_width, element_height, element_area, screen_x_dimension, screen_y_dimension, element_y_coord, element_x_coord, body_x_dimension, body_y_dimension = get_size_stats(browser, result)

    return {
            "ProductName":name,
            "Ad":sponsored,
            "Rating":rating,
            "NoOfReviews":no_of_reviews,
            "ListingType":"Result",
            "SectionHeading":"Results",
            "URL":url,
            "Price":price, 
            "SaveCoupon":save_coupon,
            "BundlesAvailable":bundles,
            "LimitedTimeDeal":limited_time_deal,
            "AmazonsChoice":amazons_choice,
            "BestSeller":best_seller,
            "Prime":prime_logo,
            "AmazonBrand":amazon_banner,
            "EcoFriendly":eco_friendly,
            "SmallBusiness":small_business,
            "ElementWidth":element_width,
            "ElementHeight":element_height,
            "ElementArea":element_area,
            "YCoord":element_y_coord,
            "XCoord":element_x_coord,
            "HTMLWidth":body_x_dimension,
            "HTMLHeight":body_y_dimension,
            "ViewPortWidth":screen_x_dimension,
            "ViewPortHeight":screen_y_dimension,
        } 

def carousel_widget_scrape(browser, carousel_widget):
    element_width, element_height, element_area, screen_x_dimension, screen_y_dimension, element_y_coord, element_x_coord, html_x_dimension, html_y_dimension = get_size_stats(browser, carousel_widget)
    listing_type = "Carousel Widget"
    sponsored = False
    section_heading = carousel_widget.find_element(By.XPATH, ".//preceding::span[contains(@class,'a-size-medium-plus') and contains(@class,'a-color-base')][1]").get_attribute("innerHTML")
    try:
        sponsored_tag = carousel_widget.find_element(By.XPATH, "(.//preceding::span[contains(@class,'aok-inline-block') and contains(@class, 's-widget-sponsored-label-text')])[1]")
    except NoSuchElementException:
        sponsored_tag = None
        sponsored = False

    if sponsored_tag:
        if "Sponsored" in sponsored_tag.get_attribute("innerHTML"):
            sponsored = True

    return {
        "ListingType":listing_type,
        "Ad":sponsored,
        "SectionHeading":section_heading,
        "ElementWidth":element_width,
        "ElementHeight":element_height,
        "ElementArea":element_area,
        "YCoord":element_y_coord,
        "XCoord":element_x_coord,
        "HTMLWidth":html_x_dimension,
        "HTMLHeight":html_y_dimension,
        "ViewPortWidth":screen_x_dimension,
        "ViewPortHeight":screen_y_dimension,
    } 

def carousel_results_scrape(browser, carousel):
    carousel_data = []

    sponsored = False
    listing_type = "Carousel Result"
    section_heading = carousel.find_element(By.XPATH, ".//preceding::span[contains(@class,'a-size-medium-plus') and contains(@class,'a-color-base')][1]").get_attribute("innerHTML")
    try:
        sponsored_tag = carousel.find_element(By.XPATH, "(.//preceding::span[contains(@class,'aok-inline-block') and contains(@class, 's-widget-sponsored-label-text')])[1]")
    except NoSuchElementException:
        sponsored_tag = None
        sponsored = False

    if sponsored_tag:
        if "Sponsored" in sponsored_tag.get_attribute("innerHTML"):
            sponsored = True

    carousel_results = carousel.find_elements(By.CSS_SELECTOR, "li[class^='a-carousel-card']")
    for result in carousel_results:
        resultdict = search_result_scrape(browser, result)
        resultdict["Ad"] = sponsored
        resultdict["SectionHeading"] = section_heading
        resultdict["ListingType"] = listing_type
        carousel_data.append(resultdict)

    return carousel_data

def banner_scrape(browser, banner):
    urls = banner.find_elements(By.TAG_NAME, "a")
    for url in urls:
        class_name = url.get_attribute("class")
        if class_name and class_name.startswith("a-link-normal"):
            href = url.get_attribute("href")
            break

    ad = True
    listing_type = "Banner"
    element_width, element_height, element_area, screen_x_dimension, screen_y_dimension, element_y_coord, element_x_coord, body_x_dimension, body_y_dimension = get_size_stats(browser, banner)
    return {
        "URL":href,
        "Ad":ad,
        "ListingType":listing_type,
        "ElementWidth":element_width,
        "ElementHeight":element_height,
        "ElementArea":element_area,
        "YCoord":element_y_coord,
        "XCoord":element_x_coord,
        "HTMLWidth":body_x_dimension,
        "HTMLHeight":body_y_dimension,
        "ViewPortWidth":screen_x_dimension,
        "ViewPortHeight":screen_y_dimension,
    }

def video_scrape(browser, video):
    urls = video.find_elements(By.TAG_NAME, "a")
    for url in urls:
        class_name = url.get_attribute("class")
        if class_name and class_name.startswith("a-link-normal"):
            href = url.get_attribute("href")
            break
    ad = True
    listing_type = "Video"
    parent_element = video.find_element(By.XPATH, ".//ancestor::div[@class='sg-col-inner'][1]")
    element_width, element_height, element_area, screen_x_dimension, screen_y_dimension, element_y_coord, element_x_coord, body_x_dimension, body_y_dimension = get_size_stats(browser, parent_element)
    return {
        "URL":href,
        "Ad":ad,
        "ListingType":listing_type,
        "ElementWidth":element_width,
        "ElementHeight":element_height,
        "ElementArea":element_area,
        "YCoord":element_y_coord,
        "XCoord":element_x_coord,
        "HTMLWidth":body_x_dimension,
        "HTMLHeight":body_y_dimension,
        "ViewPortWidth":screen_x_dimension,
        "ViewPortHeight":screen_y_dimension,
    }

def scrape_other_ad(browser,other_ad):
    a_element = other_ad.find_element(By.XPAHT, ".//a[contains(@class, 'ad-link')]")
    url = a_element.get_attribute("href")
    ad = True
    listing_type = "Other Ad"
    element_width, element_height, element_area, screen_x_dimension, screen_y_dimension, element_y_coord, element_x_coord, body_x_dimension, body_y_dimension = get_size_stats(browser, other_ad)
    return {
        "URL":url,
        "Ad":ad,
        "ListingType":listing_type,
        "ElementWidth":element_width,
        "ElementHeight":element_height,
        "ElementArea":element_area,
        "YCoord":element_y_coord,
        "XCoord":element_x_coord,
        "HTMLWidth":body_x_dimension,
        "HTMLHeight":body_y_dimension,
        "ViewPortWidth":screen_x_dimension,
        "ViewPortHeight":screen_y_dimension,
    }

def get_size_stats(browser, element):
    if element.is_displayed() == True:
        element_width = element.size["width"]
        element_height = element.size["height"]
        element_area = element.size["width"] * element.size["height"]
        element_y_coord = element.location["y"]
        element_x_coord = element.location["x"]
        screen_x_dimension = browser.get_window_size()["width"]
        screen_y_dimension = browser.get_window_size()["height"]
        html_x_dimension = browser.find_element(By.TAG_NAME, "body").size["width"] 
        html_y_dimension = browser.find_element(By.TAG_NAME, "body").size["height"]
        return element_width, element_height, element_area, screen_x_dimension, screen_y_dimension, element_y_coord, element_x_coord, html_x_dimension, html_y_dimension
    else:
        return "Not Visible","Not Visible","Not Visible","Not Visible","Not Visible","Not Visible","Not Visible","Not Visible","Not Visible"
        