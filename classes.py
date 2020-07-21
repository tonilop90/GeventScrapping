
class Hotel(object):
    """ Class with the data we are going to scrapp from booking"""
    def __init__(self, name, lat: float, lng: float,
                 total_comments: int, city: str,
                 comments_by_country: dict):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.total_comments = total_comments
        self.city = city
        self.comments_by_country = comments_by_country

    def to_dict(self):
        return {
            'name': self.name,
            'lat': self.lat,
            'lng': self.lng,
            'total_comments': self.total_comments,
            'city': self.city,
            'comments_by_country': self.comments_by_country
        }
