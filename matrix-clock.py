#!/usr/bin/env python
import time
from datetime import datetime

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT

from pyowm import OWM
from datetime import datetime
import pytz
import numpy as np

owm = OWM('6d9a5322c06c0fc360ad96f1d2fc5c27')
mgr = owm.weather_manager()

# observation = mgr.weather_at_place('Katy,US')
# w = observation.weather


def minute_change(device):
    '''When we reach a minute change, animate it.'''
    hours = datetime.now().strftime('%H')
    minutes = datetime.now().strftime('%M')
    h = int(hours)
    h_ones = h % 10
    h_tens = h // 10 % 10
    m = int(minutes)
    m_ones = m % 10
    m_tens = m // 10 % 10

    if m_ones == 9:
        if m_tens != 5: # change 2 digits (original behavior)
            digits = 2
        else:
            if h_ones in (3, 9): # change 4 digits
                digits = 4
            else: # change 3 digits
                digits = 3
    else: # change 1 digit
        digits = 1

    def helper(current_y):
        with canvas(device) as draw:
            if digits == 1:
                text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
                text(draw, (15, 1), ":", fill="white", font=proportional(TINY_FONT))
                text(draw, (17, 1), str(m_tens), fill="white", font=proportional(CP437_FONT))
                text(draw, (25 if m_tens in (0, 4) else 24, current_y), str(m_ones), fill="white", font=proportional(CP437_FONT))
            if digits == 2:
                text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
                text(draw, (15, 1), ":", fill="white", font=proportional(TINY_FONT))
                text(draw, (17, current_y), minutes, fill="white", font=proportional(CP437_FONT))
            if digits == 3:
                text(draw, (0, 1), str(h_tens), fill="white", font=proportional(CP437_FONT))
                text(draw, (8 if h_tens == 0 else 7, current_y), str(h_ones), fill="white", font=proportional(CP437_FONT))
                text(draw, (15, 1), ":", fill="white", font=proportional(TINY_FONT))
                text(draw, (17, current_y), minutes, fill="white", font=proportional(CP437_FONT))
            if digits == 4:
                text(draw, (0, current_y), hours, fill="white", font=proportional(CP437_FONT))
                text(draw, (15, 1), ":", fill="white", font=proportional(TINY_FONT))
                text(draw, (17, current_y), minutes, fill="white", font=proportional(CP437_FONT))
        time.sleep(0.1)

    for current_y in range(1, 9):
        helper(current_y)
#     time.sleep(0.25)
    seconds = datetime.now().second
#     print(seconds, '!')
    while seconds>50:
        seconds = datetime.now().second
#     print(seconds)
    hours = datetime.now().strftime('%H')
    minutes = datetime.now().strftime('%M')
    h = int(hours)
    h_ones = h % 10
    h_tens = h // 10 % 10
    m = int(minutes)
    m_ones = m % 10
    m_tens = m // 10 % 10
    for current_y in range(-5, 1): # range(9, 1, -1):
        helper(current_y)

def animation(device, from_y, to_y):
    '''Animate the whole thing, moving it into/out of the abyss.'''
    hourstime = datetime.now().strftime('%H')
    mintime = datetime.now().strftime('%M')
    current_y = from_y
    while current_y != to_y:
        with canvas(device) as draw:
            text(draw, (0, current_y), hourstime, fill="white", font=proportional(CP437_FONT))
            text(draw, (15, current_y), ":", fill="white", font=proportional(TINY_FONT))
            text(draw, (17, current_y), mintime, fill="white", font=proportional(CP437_FONT))
        time.sleep(0.1)
        current_y += 1 if to_y > from_y else -1

def main():
    # Setup for Banggood version of 4 x 8x8 LED Matrix (https://bit.ly/2Gywazb)
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=90, blocks_arranged_in_reverse_order=True)
    device.contrast(16)

    # The time ascends from the abyss...
    animation(device, 8, 1)
    global one_call
    global w
    toggle = False  # Toggle the second indicator every second
    while True:
        toggle = not toggle
        now = datetime.now()
        m = now.minute
        s = now.second
        weekday = now.isoweekday()
#         if sec == 59:
        if s == 10:
            # Half-way through each minute, display the complete date, current weather and forecast
            if m%2 == 0: # get fresh weather data every other minute
                msg = time.strftime("%a %b %d %Y")
                try:
                    one_call = mgr.one_call(lon=-95.824402, lat=29.785789, exclude='minutely,hourly', units='imperial')
                    w = one_call.current
                except ConfigurationNotFoundError as e:
                    msg = msg + " " + str(e)
                    print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} error', e)
                except ConfigurationParseError as e:
                    msg = msg + " " + str(e)
                    print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} error', e)
                except TimeoutError as e:
                    msg = msg + " " + str(e)
                    print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} error', e)
                except InvalidSSLCertificateError as e:
                    msg = msg + " " + str(e)
                    print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} error', e)
                except APIResponseError as e:
                    msg = msg + " " + str(e)
                    print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} error', e)
                except NotFoundError as e:
                    msg = msg + " " + str(e)
                    print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} error', e)
                except UnauthorizedError as e:
                    msg = msg + " " + str(e)
                    print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} error', e)
                except ParseAPIResponseError as e:
                    msg = msg + " " + str(e)
                    print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} error', e)
                except PyOWMError as e:
                    msg = msg + " " + str(e)
                    print(f'{datetime.now().strftime("%a %b %d %Y %H:%M:%S")} error', e)
                else:
                    msg = msg + " " + w.detailed_status + " " + \
                          str(np.around(w.temperature()['temp'], 1)) + chr(248) + \
                          "F feels like " + str(int(np.around(w.temperature()['feels_like'], 0))) + \
                          chr(248) + "F"
                    now_timestamp = now.replace().timestamp()
                    if now_timestamp < w.sunrise_time(): # early morning, pre-sunrise
                        device.contrast(0)
                        msg = msg + f" sunrise {w.sunrise_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')} " \
                              f"sunset {w.sunset_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')}"
                    elif now_timestamp < w.sunset_time(): # daytime
                        device.contrast(16)
                        msg = msg + f" sunset {w.sunset_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')} " \
                              f"sunrise {one_call.forecast_daily[1].sunrise_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')}"
                    else: # evening, post-sunset
                        device.contrast(0)
                        msg = msg + f" sunrise {one_call.forecast_daily[1].sunrise_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')} " \
                              f"sunset {one_call.forecast_daily[1].sunset_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%H:%M')}"
                    msg = msg + f" forecast: {one_call.forecast_daily[1].detailed_status}" \
                        f" high {int(np.around(one_call.forecast_daily[1].temperature()['max'], 0))}" + \
                        chr(248) + f"F low {int(np.around(one_call.forecast_daily[1].temperature()['min'], 0))}" + \
                        chr(248) + f"F morning feels like {int(np.around(one_call.forecast_daily[1].temperature().get('feels_like_morn', None), 0))}" + chr(248) + "F"
                    if weekday in (5, 6): # today is Fri or Sat so add forecast for Mon
                        msg = msg + f" Monday: {one_call.forecast_daily[3 if weekday==5 else 2].detailed_status}" \
                        f" high {int(np.around(one_call.forecast_daily[3 if weekday==5 else 2].temperature()['max'], 0))}" + \
                        chr(248) + f"F low {int(np.around(one_call.forecast_daily[3 if weekday==5 else 2].temperature()['min'], 0))}" + chr(248) + f"F"
        #             msg = msg + f" data as of {one_call.current.reference_time(timeformat='date').astimezone(pytz.timezone('America/Chicago')).strftime('%b %d %H:%M:%S')}"
            try:
                msg
            except NameError:
                msg = time.strftime("%a %b %d %Y")
            # animate the time display into and out of the abyss
            animation(device, 1, 8)
            show_message(device, msg, fill="white", font=proportional(CP437_FONT))
            animation(device, 8, 1)
        elif s == 59:
            # animate the minute change
            minute_change(device)
        else:
            # Do the following twice a second (so the seconds' indicator blips).
            # I'd optimize if I had to - but what's the point?
            # Even my Raspberry PI2 can do this at 4% of a single one of the 4 cores!
            hours = datetime.now().strftime('%H')
            minutes = datetime.now().strftime('%M')
            with canvas(device) as draw:
                text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
                text(draw, (15, 1), ":" if toggle else " ", fill="white", font=proportional(TINY_FONT))
                text(draw, (17, 1), minutes, fill="white", font=proportional(CP437_FONT))
            time.sleep(0.5)


if __name__ == "__main__":
    main()