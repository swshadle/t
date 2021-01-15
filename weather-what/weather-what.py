#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import time
import random
import sys
from font_fredoka_one import FredokaOne
from inky.auto import auto
# from inky import InkyWHAT
from PIL import Image, ImageDraw, ImageFont
from pyowm import OWM
from secrets import OWM_API_KEY
from datetime import datetime
import pytz
import numpy as np
from font_source_serif_pro import SourceSerifProSemibold
from font_source_sans_pro import SourceSansProSemibold
from profanityfilter import ProfanityFilter
from twitter_news import get_breaking_news
from twitter_what import hash_display
try:
    import wikiquotes
except ImportError:
    assert False, """This script requires the wikiquotes module.

Install with:
    sudo apt install python-lxml
    sudo pip install wikiquotes
"""
#     sys.exit(1)

"""
To run this example on Python 2.x you should:
    sudo apt install python-lxml
    sudo pip install geocoder requests font-fredoka-one beautifulsoup4=4.6.3

On Python 3.x:
    sudo apt install python3-lxml
    sudo pip3 install geocoder requests font-fredoka-one beautifulsoup4
"""

pf = ProfanityFilter()

global prev_tweet_id
prev_tweet_id = None

# print("""Inky pHAT: Weather
# 
# Displays weather information for Katy, Texas
# 
# """)

# Get the current path
PATH = os.path.dirname(__file__)

# Set up the display
try:
    inky_display = auto(ask_user=True, verbose=True)
#     inky_display = InkyWHAT('red')
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

colours = (inky_display.RED, inky_display.BLACK, inky_display.WHITE)
colour_names = (inky_display.colour, "black", "white")
clear_img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))

w, h = inky_display.resolution
# print("{}x{} display".format(w, h))

inky_display.set_border(inky_display.RED)

# Details to customise your weather display
# Get Open Weather Map data
owm = OWM(OWM_API_KEY)
mgr = owm.weather_manager()
reg = owm.city_id_registry()
CITY = 'Katy'
REG = 'TX'
list_of_locations = reg.locations_for(CITY, country=REG)
# print(f'list {list_of_locations}')
if len(list_of_locations):
    city = list_of_locations[0]
    lat = city.lat   # 55.75222
    lon = city.lon   # 37.615555
else:
    CITY = ''
    REG = ''
    lat = 29.785789
    lon = -95.824402

font_quote = 16
border = 50

author_font = ImageFont.truetype(SourceSerifProSemibold, font_quote+2)
quote_font = ImageFont.truetype(SourceSansProSemibold, font_quote)

# A list of famous people to search for quotes from
# on https://en.wikiquote.org. Change them to your
# favorite people, if you like!

people = [
#    "Ada Lovelace",
   "Carl Sagan",
#    "Charles Darwin",
##    "Dorothy Hodgkin",
#     "Edith Clarke",
#     "Grace Hopper",
#     "Hedy Lamarr",
##    "Isaac Newton",
#     "James Clerk Maxwell",
#     "Margaret Hamilton",
#    "Marie Curie",
#     "Michael Faraday",
#   "Niels Bohr",
#    "Nikola Tesla",
#    "Rosalind Franklin",
#    "Albert Einstein",
   "Stephen Hawking",
#    "Douglas Adams",
##     "Frank Herbert",
    "Neil deGrasse Tyson",
##     "Johannes Kepler",
#     "Christopher Hitchens",
#     "Richard Dawkins"
#     "Matt Dillahunty",
    "Sam Harris",
    "Mark Twain",
    "Samuel Clements",
#     "Walt Whitman",
    "Oscar Wilde",
#    "Stephen Fry",
]

def reflow_quote(quote, width, font):
    words = quote.split(" ")
    reflowed = ''
    line_length = 0

    for i in range(len(words)):
        word = words[i] + " "
        word_length = font.getsize(word)[0]
        line_length += word_length

        if line_length < width - font.getsize('\"')[0]:
            reflowed += word
        else:
            line_length = word_length
            reflowed = reflowed[:-1] + "\n  " + word

    reflowed = '"' + reflowed.rstrip().replace('\"', '\'', -1) + '"'

    return reflowed

def get_quote(max_height):
    below_max_length = False

# Only pick a quote that will fit in our defined area
# once rendered in the font and size defined.
    attempts = 0
    while not below_max_length:
        attempts = attempts + 1
        person = random.choice(people)           # Pick a random person from our list
        quote = wikiquotes.random_quote(person, "english")

        reflowed = reflow_quote(quote, inky_display.WIDTH-border, quote_font)
        p_w, p_h = quote_font.getsize(reflowed)  # Width and height of quote
        p_h = p_h * (reflowed.count("\n") + 1)   # Multiply through by number of lines

        if p_h <= max_height and not pf.is_profane(quote):
#             print(f'quote is {p_h}<={max_height}')
            below_max_length = True              # The quote fits! Break out of the loop.
        elif attempts >= 50:
            print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} quote is too long but we tried {attempts} times. quote is {p_h}>{max_height}')
            print(reflowed + "\n" + '-' + person)
            return ('', '', -1) # failure
        else:
            continue
#     print(reflowed + "\n" + person)
    return (person, reflowed, p_h)

while True:
    try:
        one_call = mgr.one_call(lon=lon, lat=lat, exclude='minutely,hourly', units='imperial')
        w = one_call.current
    except: # catch all exceptions
        print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} error {sys.exc_info()}')
    else:
        img = Image.open(os.path.join(PATH, "/home/pi/Pimoroni/inky/examples/phat/resources/empty-backdrop.png")).resize(inky_display.resolution)
        now = datetime.now()
        weekday = now.isoweekday()
        status = w.detailed_status
        temp = str(np.around(w.temperature()['temp'], 1))
        feels_like = str(int(np.around(w.temperature()['feels_like'], 0)))
        now_timestamp = now.replace().timestamp()
        if now_timestamp < w.sunrise_time(): # early morning, pre-sunrise
            sunrise = w.sunrise_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')
            sunset = w.sunset_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')
        elif now_timestamp < w.sunset_time(): # daytime
            sunset = w.sunset_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')
            sunrise = one_call.forecast_daily[1].sunrise_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')
        else: # evening, post-sunset
            sunrise = one_call.forecast_daily[1].sunrise_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')
            sunset = one_call.forecast_daily[1].sunset_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')
        forecast = one_call.forecast_daily[1].detailed_status
        forecast_high = int(np.around(one_call.forecast_daily[1].temperature()['max'], 0))
        forecast_low = int(np.around(one_call.forecast_daily[1].temperature()['min'], 0))
        forecast_morning = int(np.around(one_call.forecast_daily[1].temperature().get('feels_like_morn', None), 0))
    #     if weekday in (5, 6): # today is Fri or Sat so add forecast for Mon
    #         msg = msg + f" Monday: {one_call.forecast_daily[3 if weekday==5 else 2].detailed_status}" \
    #         f" high {int(np.around(one_call.forecast_daily[3 if weekday==5 else 2].temperature()['max'], 0))}" + \
    #         chr(248) + f"F low {int(np.around(one_call.forecast_daily[3 if weekday==5 else 2].temperature()['min'], 0))}" + chr(248) + f"F"
#         data = one_call.current.reference_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%b %d %H:%M:%S')
        data = one_call.current.reference_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')
    # try:
    #     msg
    # except NameError:
    #     msg = time.strftime("%a %b %d %Y")

    # Create a new canvas to draw on
#     img = Image.open(os.path.join(PATH, "examples/phat/resources/empty-backdrop.png")).resize(inky_display.resolution)
        draw = ImageDraw.Draw(img)

    # Load our icon files and generate masks
    # for icon in glob.glob(os.path.join(PATH, "resources/icon-*.png")):
    #     icon_name = icon.split("icon-")[1].replace(".png", "")
    #     icon_image = Image.open(icon)
    #     icons[icon_name] = icon_image
    #     masks[icon_name] = create_mask(icon_image)

    # Load the FredokaOne font
        font = ImageFont.truetype(FredokaOne, 22)

        # Draw lines to frame the weather data
        # draw.line((69, 36, 69, 81))       # Vertical line
        # draw.line((31, 35, 184, 35))      # Horizontal top line
        # draw.line((69, 58, 174, 58))      # Horizontal middle line
        draw.line((169, 58, 169, 58), 2)  # Red seaweed pixel :D

        # Write text with weather values to the canvas
        date_time = time.strftime("%a %b %d %Y")

        draw.text((38, 0), date_time, inky_display.WHITE, font=font)
        draw.text((260, 0), f'{CITY} {REG}', inky_display.WHITE, font=font)

        # draw.text((72, 34), "T", inky_display.WHITE, font=font)
        # draw.text((92, 34), u"{}°".format(temperature), inky_display.WHITE if temperature < WARNING_TEMP else inky_display.RED, font=font)
        draw.text((70, 25), f"{status} {temp}°F", inky_display.WHITE, font=font)
        # draw.text((72, 58), "P", inky_display.WHITE, font=font)
        draw.text((70, 50), f"feels like {feels_like}°F as of {data}", inky_display.WHITE, font=font)
        draw.text((70, 75), f"sunrise {sunrise} sunset {sunset}", inky_display.WHITE, font=font)
        draw.text((70, 100), f"tomorrow: {forecast}", inky_display.WHITE, font=font)
        draw.text((70, 125), f"high {forecast_high}°F low {forecast_low}°F", inky_display.WHITE, font=font)
        draw.text((70, 150), f"morning feels like {forecast_morning}°F", inky_display.WHITE, font=font)
#         draw.text((85, 175), f"", inky_display.WHITE, font=font)
        author, quote, quote_h = get_quote(inky_display.HEIGHT - 200)
        # x- and y-coordinates for the top left of the quote
        author_x = 90
        author_y = 180

        # x- and y-coordinates for the top left of the author
        quote_x = border
        quote_y = author_y + 25
        
        if quote_h != -1:
#             draw.rectangle(((quote_x, # llx
#                              quote_y + quote_h), # lly
#                             (inky_display.WIDTH - border, # urx
#                              quote_y)), # ury
#                            fill=inky_display.BLACK)
#             draw.multiline_text((author_x+1, author_y+1), author, fill=inky_display.RED, font=author_font, align="left")
#             draw.multiline_text((author_x, author_y), author, fill=inky_display.WHITE, font=author_font, align="left")
#             draw.multiline_text((quote_x, quote_y), quote, fill=inky_display.WHITE, font=quote_font, align="left")
            author_y = inky_display.HEIGHT-quote_h - 25
            quote_y = inky_display.HEIGHT-quote_h
            quote_w, quote_h = quote_font.getsize(quote)
            draw.rectangle(((quote_x, # llx
                             inky_display.HEIGHT), # lly
                            (quote_x + quote_w, # urx
                             quote_y)), # ury
                           fill=inky_display.BLACK)
            author_w, author_h = author_font.getsize(author)
            draw.rectangle(((author_x, # llx
                             author_y + author_h), # lly
                            (author_x + author_w, # urx
                             author_y)), # ury
                           fill=inky_display.BLACK)

            draw.multiline_text((author_x+1, author_y+1), author, fill=inky_display.RED, font=author_font, align="left")
            draw.multiline_text((author_x, author_y), author, fill=inky_display.WHITE, font=author_font, align="left")
            draw.multiline_text((quote_x, quote_y), quote, fill=inky_display.WHITE, font=quote_font, align="left")

    # Draw the current weather icon over the backdrop
    # if weather_icon is not None:
    #     img.paste(icons[weather_icon], (28, 36), masks[weather_icon])

    # else:
    #     draw.text((28, 36), "?", inky_display.RED, font=font)

    # Display the weather data on Inky pHAT
        inky_display.set_image(img)
        inky_display.show()

        print(f'{one_call.current.reference_time(timeformat="date").astimezone(pytz.timezone("America/Chicago")).strftime("%a %b %d %Y %H:%M:%S")}', f'{author}:', quote.replace("\n ", "") if len(quote)<75 else quote[:75].replace("\n ", ""))
        time.sleep(60-datetime.now().second+1)
        while datetime.now().minute % 15:
#             global prev_tweet_id
#             print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S idle")}')
            tweet, user, tweet_id = get_breaking_news(30)
            
            if tweet_id and tweet_id != prev_tweet_id:
                print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} {user}: {tweet if len(tweet)<75 else tweet[:75]}')
                hash_display(tweet, user)
                prev_tweet_id = tweet_id
                time.sleep(60-datetime.now().second)
                break
            else:
                print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S no news is good news")}')
                time.sleep(60-datetime.now().second)

# cleaning cycle
#         for j, c in enumerate(colours):
#             print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} cleaning {colour_names[j]}')
#             inky_display.set_border(c)
#             for x in range(inky_display.WIDTH):
#                 for y in range(inky_display.HEIGHT):
#                     clear_img.putpixel((x, y), c)
#             inky_display.set_image(clear_img)
#             inky_display.show()
#             time.sleep(1)
#         print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} cleaning complete')
