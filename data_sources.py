import json
import pandas as pd


class JSONDataSource:
    def __init__(self, file_path):
        self._cache = {}
        self.json = self._read_json_file(file_path)
        self.post_processing()

    @staticmethod
    def _read_json_file(path):
        with open(path) as file:
            return json.load(file)

    def post_processing(self):
        raise NotImplementedError()

    def __getitem__(self, item):
        return self._cache.get(item)


class Regions(JSONDataSource):
    def __init__(self):
        super().__init__('data/system_regions.json')

    def post_processing(self):
        self._cache = {int(item['region_id']): item['name']
                       for item in self.json['data']['regions']}


class Stations(JSONDataSource):
    def __init__(self):
        super().__init__('data/station_information.json')

    def post_processing(self):
        self._cache = {item['station_id']: item for item in self.json['data']['stations']}

    @property
    def station_ids(self):
        return self._cache.keys()

    @property
    def all(self):
        return self._cache.values()

    def to_dataframe(self):
        data = {int(station_id): {
            'station_region_id': str(station['region_id']),
            'station_capacity': str(station['capacity']),
            'station_has_kiosk': station['has_kiosk'],
        } for station_id, station in self._cache.items()}
        return pd.DataFrame.from_dict(data, orient='index')


class Trips:
    def __init__(self, file_path):
        self.data_frame = pd.read_csv(file_path)
        self.post_processing()

    def post_processing(self):
        self.data_frame = self.data_frame.rename(columns={
            'tripduration': 'trip_duration',
            'starttime': 'start_time',
            'bikeid': 'bike_id',
            'usertype': 'user_type',
            'start station id': 'start_station_id',
            'birth year': 'birth_year',
            'start station name': 'start_station_name',
            'end station name': 'end_station_name',
        })
        self.data_frame = self.data_frame.drop(columns=[
            'stoptime',
            'start station latitude',
            'start station longitude',
            'end station id',
            'end station latitude',
            'end station longitude'
        ])
        self.data_frame['start_time'] = pd.to_datetime(self.data_frame['start_time'])

    @property
    def first_trip_start_time(self):
        if self.data_frame.shape[0] == 0:
            return None
        else:
            return self.data_frame['start_time'].iloc[0]
