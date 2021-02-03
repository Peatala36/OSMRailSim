import srtm
import json
import numpy as np
import infrastruktur

# constants
EARTH_RADIUS = 6371e3 # meters

class rohdaten:
    def __init__(self):
        pass

    def prs_load(self, path):
        # input: path = string
        # output: prs_data = dict{'lat':list[float], 'lon':list[float], 'ele':list[float]}
        
        prs_data = {'lat':[], 'lon':[], 'ele':[]}
        
        with open(path, "r") as file:
            m = json.load(file)
            file.close()
            ele = srtm.get_data()

            for way in m["features"]:
                for coord in way["geometry"]["coordinates"]:
                    prs_data['lat'].append(coord[0])
                    prs_data['lon'].append(coord[1])
                    prs_data['ele'].append(ele.get_elevation(coord[0], coord[1]))
        return prs_data

    def prs_remove_duplicate(self, prs_data):
        # input: prs_data = dict{'lat':list[float], 'lon':list[float], 'ele':list[float]}
        # ouput: prs_data_nodup = dict{'lat':list[float], 'lon':list[float], 'ele':list[float]}

        prs_dist = self.prs_calculate_distance(prs_data)

        i_dist = np.concatenate(([0], np.nonzero(prs_dist)[0]))

        if not len(prs_dist) == len(i_dist):
            print('Removed {} duplicate trackpoint(s)'.format(len(prs_dist)-len(i_dist)))

        prs_data_nodup = prs_data.copy()

        for k in ('lat', 'lon', 'ele'):
            prs_data_nodup[k] = [prs_data[k][i] for i in i_dist] if prs_data[k] else None

        return prs_data_nodup
        

    def prs_calculate_distance(self, prs_data):
        # input: prs_data = dict{'lat':list[float], 'lon':list[float], 'ele':list[float]}
        # output: prs_dist = numpy.ndarray[float]

        prs_dist = np.zeros(len(prs_data['lat']))

        for i in range(len(prs_dist)-1):
            lat1 = np.radians(prs_data['lat'][i])
            lon1 = np.radians(prs_data['lon'][i])
            lat2 = np.radians(prs_data['lat'][i+1])
            lon2 = np.radians(prs_data['lon'][i+1])

            delta_lat = lat2-lat1
            delta_lon = lon2-lon1

            c = 2.0*np.arcsin(np.sqrt(np.sin(delta_lat/2.0)**2+np.cos(lat1)*np.cos(lat2)*np.sin(delta_lon/2.0)**2))
            dist_latlon = EARTH_RADIUS*c # great-circle distance
            prs_dist[i+1] = dist_latlon

        return prs_dist

    def prs_interpolate(self, prs_data, res, deg = 1):
        if not type(deg) is int:
            raise TypeError('deg must be int')
        if not 1 <= deg <= 5:
            raise ValueError('deg must be in [1-5]')
        if not len(prs_data['lat']) > deg:
            raise ValueError('number of data points must be > deg')

        _prs_data = prs_remove_dublicate(prs_data)
        _prs_dist = prs_calculate_distance(_prs_data)

        
            
