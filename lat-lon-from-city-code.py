from pyowm.owm import OWM
owm = OWM('6d9a5322c06c0fc360ad96f1d2fc5c27')
reg = owm.city_id_registry()
CITY = 'Katy'
REG = 'TX'
TINT_COLOR = (0, 0, 0)  # Black
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
print(f'{CITY} {REG} lat {lat} lon {lon}')
