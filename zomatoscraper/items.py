# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class ZomatoscraperItem(Item):
    # define the fields for your item here:
    name = Field()
    link = Field()
    address = Field()
    contact = Field()
    cuisines = Field()
    rating = Field()
    votes = Field()
    price_two = Field()
    price_two_comp = Field()
    price_beer = Field()
    geo_location_lat = Field()
    geo_location_long = Field()
    timetable = Field()
    facility = Field()
    featured_collections = Field()    
    known_for = Field()
    what_people_love_here = Field()
    event_date = Field()
    event_desc = Field()
    event_name = Field()

