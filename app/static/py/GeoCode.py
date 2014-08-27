import sys
from json import loads as JSONLoad;

def GeoCode(address):
    from urllib2 import urlopen as UrlOpen;
    from urllib import quote as Quote;
    ###
    # Encode query string into URL
    ###
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&sensor=false&key=********'.format(Quote(address));
    ###
    # Call API and extract JSON
    ###
    print 'Calling Google Maps API for ' + address;
    #PrintNow('Calling Google Maps API for `{:s}` ... '.format(address), end = '');
    json = UrlOpen(url).read();
    json = JSONLoad(json.decode('utf-8'));
    ###
    # Extract longitude and latitude
    ###
    if json.get('status') == 'ZERO_RESULTS':
        latitude, longitude = None, None;
        ###
        print 'address is not found'
        #PrintNow('it was not found');
    else:
        latitude, longitude = (value for key, value in sorted(json.get('results')[0].get('geometry').get('location').items()));
        ###
        print('it is located at {:f}/{:f}'.format(longitude, latitude));
    ###
    return (longitude, latitude);


'''
if __name__ == "__main__":
    addr = sys.argv[1]
    PrintNow(addr)
    GeoCode(addr)
'''
