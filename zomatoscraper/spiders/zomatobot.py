# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider
from zomatoscraper.items import ZomatoscraperItem
from bs4 import BeautifulSoup

class ZomatobotSpider(Spider):
    name = 'zomatobot'
    allowed_domains = ['www.zomato.com']
    start_urls = ['http://www.zomato.com/india',]

    def parse(self, response):

        """ This function parses a main page.
            @raises CloseSpider exception if the bandwidth of the response is very high
            @forloop loops the urls of the top cities in the response returned for the Request sent using urls in the start_urls
            @yields requests using urls parsed on the page and calls the parse_page() on every url
        """

        # self.logger.info('Parse function called on %s', response.url)

        if b'Bandwidth exceeded' in response.body:
            raise CloseSpider('bandwidth_exceeded')
        for href in response.xpath("//section/div[1]//*/a/@href").extract():
            page_url = str(href+"/restaurants?bar=1")
            yield Request(page_url, callback=self.parse_page)

    def parse_page(self, response):

        """ This function parses a restaurants page.
            @raises CloseSpider exception if the bandwidth of the response is very high
            @forloop loops the restaurants_urls in the response returned for the Request sent using urls requested by parse()
            @yields requests on job_urls parsed in the response and calls the parse_page()
            @forloop loops the urls in the response returned for the Request sent using urls requested by parse()
            @yields requests on next_page_urls parsed in the response and calls the parse_page()
        """

        # self.logger.info('Parse function called on %s', response.url)
        url = "https://www.zomato.com"

        if b'Bandwidth exceeded' in response.body:
            raise CloseSpider('bandwidth_exceeded')

        for res_url in response.xpath('//*[@data-result-type="ResCard_Name"]/@href').extract():
            yield Request(res_url, callback=self.parse_restaurant)

        for more_outlets_url in response.xpath('//*/a[contains(text(),"See all outlets")]/@href').extract():
            yield Request(url+more_outlets_url, callback=self.parse_page)

        for res_url in response.xpath('//*/a[contains(@class,"search_chain_bottom_snippet")]/@href').extract():
            yield Request(res_url, callback=self.parse_restaurant)

        for next_page_url in response.xpath('//*[contains(@title, "Next Page")]/@href').extract():
            yield Request(url+next_page_url, callback=self.parse_page)
            
    def parse_restaurant(self, response):
        """ This function parses a restaurant page.
            @raises CloseSpider exception if the bandwidth of the response is very high
            @url url of the response by the parse_page()
            @yields items 1
            @scrapes [address, contact, cuisines, event_date, event_desc, event_name, facility,
            featured_collections, geo_location,	known_for, name, price_beer, price_two, price_two_comp,
            rating, timetable, votes, what_people_love_here] of the restaurant.
        """
        item = ZomatoscraperItem()
        item['link'] = response.url
        try:
            name = response.xpath('//*/h1[contains(@class,"ui res-name mb0 header nowrap")]/a/text()').extract()
            item['name'] = name[0].strip()
        except:
            item['name'] = ''
        
        # Res Rating
        try:
            rating = response.xpath('//*/div[contains(@class,"rating-for")]/text()').extract()
            item['rating'] = rating[0].strip()
        except:
            item['rating'] = 'N'
        
        # Res Votes
        try:
            item['votes'] = response.xpath('//*[@itemprop="ratingCount"]/text()').extract()[0]
        except:
            item['votes'] = 'N'
        
        # Res Contact
        try:
            contact = response.xpath('//*[@class="tel"]/text()').extract()
            item['contact'] = ", ".join(contact).strip()
        except:
            item['contact'] = ''
        
        # Res Cuisine
        try:
            cuisines = response.xpath('//*[@class="res-info-cuisines clearfix"]//text()').extract()
            item['cuisines'] = "".join(cuisines).split(",")
        except:
            item['cuisines'] = ''
        
        # Res Geo Location
        try:
            geo_location = response.xpath('//*[@data-is-zomato="true"]/@data-url').extract()
            location = geo_location[0].split("center=")[1].split("&")[0].split(",")
            item['geo_location_lat'] = location[0]
            item['geo_location_long'] = location[1]
        except:
            item['geo_location_lat'] = 'undefined'
            item['geo_location_long'] = 'undefined'
        
        # Res Price for Two Computation
        try:
            price_two_comp = response.xpath('//*/div[contains(@class,"tooltip-w")]/@aria-label').extract()
            item['price_two_comp'] = " ".join(price_two_comp).replace("\n"," ").split(":")[1].split(".")[0].strip()
        except:
            item['price_two_comp'] = ""
        
        # Res Price for Two
        try:
            price_two = response.xpath('//div[@class="res-info-detail"]//span[@tabindex="0"]/text()').extract()
            item['price_two'] = " ".join(price_two).replace("\n"," ").split(" for two people")[0].strip().replace("\u20b9","")
        except:
            item['price_two'] = ""
        
        # Res Price Beer
        try:
            price_beer = response.xpath('//div[@class="res-info-detail"]//div[@class="mt5"]//text()').extract()
            item['price_beer'] = " ".join(price_beer).replace("\n"," ").strip().split()[0].replace("\u20b9","")
        except:
            item['price_beer'] = ""
        
        # Res Facility
        try:
            item['facility'] = response.xpath('//div[@class="res-info-feature-text"]/text()').extract()
        except:
            item['facility'] = ""
        
        # Res Feature Collections
        try:
            featured_collections = response.xpath('//div[@class="ln24"]//text()').extract()
            item['featured_collections'] = [s.strip() for s in "".join(featured_collections).split("\n")]
        except:
            item['featured_collections'] = []
            
        # Res Address
        try:
            address = response.xpath('//div[@class="resinfo-icon"]//text()').extract()
            item['address'] = "".join(address).strip()
        except:
            item['address'] = ""
        
        # Res Known for
        try:
            known_for = response.xpath('//div[contains(@class,"res-info-known-for-text")]//text()').extract()
            item['known_for'] = "".join(known_for).replace("\n","").strip()
        except:
            item['known_for'] = ''
            
        # Res People Love Here
        try:
            item['what_people_love_here'] = response.xpath('//div[contains(@class,"rv_highlights__wrapper mtop0")]//div[contains(@class,"grey-text")]/text()').extract()
        except:
            item['what_people_love_here']  = ''
        
        # Res Timetable
        item['timetable'] = []
        try:
            for sel in response.xpath('//div[contains(@id,"res-week-timetable")]//tr'):
                item['timetable'].append([sel.xpath('td[@class="pr10"]/text()').extract()[0],sel.xpath('td[@class="pl10"]/text()').extract()[0]])
        except:
            pass
        
        soup = BeautifulSoup(response.body, 'lxml')
        item['event_name'] = []
        try:
            for div in soup.find_all('div', attrs={'class': 'resbox-event'}):
                child_div = div.find("div", attrs={'class': 'grey-data-icon event_title default-section-title bold'})
                if child_div:
                    item['event_name'].append(child_div.get_text())
        except:
            pass
        
        item['event_desc'] = []
        try:
            for div in soup.find_all('div', attrs={'class': 'resbox-event'}):
                child_div = div.find("p", attrs={'class': 'event__desc mtop0'})
                if child_div:
                    item['event_desc'].append(child_div.text.strip())
        except:
            pass

        item['event_date'] = []        
        try:
            for div in soup.find_all('div', attrs={'class': 'resbox-event'}):
                child_div = div.find("div", attrs={'class': 'event_date grey-text pt5'})
                if child_div:
                    item['event_date'].append(child_div.text.strip())
        except:
            pass
            
        yield item