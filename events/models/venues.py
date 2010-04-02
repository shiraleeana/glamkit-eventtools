#Place
#Venue
#ExternalLocation
#VenuePhoto
from django.db import models
from countries.models import Country
from datetime import datetime, timedelta
from grappelli.fields import PositionField
from settings import MARKUP_HELP

PLACE_TYPES = (
    ('level', 'level'),
    ('gallery', 'gallery'),
    ('room', 'room'),
    ('position', 'position'),
)

class Place(models.Model):
    """
    Represents a place in the gallery
    
    # Create a new place tree
    >>> building = Place(name="Art Gallery of New South Wales", vernon_id=1)
    >>> level = Place(name="Ground Floor", vernon_id=2, parent=building)
    
    # Find the parent
    >>> level.parent.name
    "Art Gallery of New South Wales"
    >>> str(level.parent_venue())
    'None'
    
    """
    name = models.CharField(max_length=200)
    vernon_id = models.IntegerField(blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name="places")
    type = models.CharField(choices = PLACE_TYPES, max_length=20, blank=True)
    tree = models.CharField(max_length=200,blank=True)
    
    def __unicode__(self):
        return self.name
        
    def parent_venue(self):
        place = self
        venue = None
        while not venue:
            try:
                venue = place.venue
            except Venue.DoesNotExist:
                place = place.parent
            except AttributeError:
                break
        return venue
    
#     def import_csv(self, file):
#         """
#         Imports data from a CSV file exported from Vernon
#         
#         To import, run the following at the Django shell
#         > from events.models import Place
#         > x = Place()
#         > x.import_csv('pathetofile.csv')
#         """
#         import csv
#             # First delete all the objects before inserting
#         Place.objects.all().delete()
#             # create a reader to get the data from the file
#         reader = csv.reader(open(file))
#         count = 0    
#         for v_id, tree, public, page in reader:
#             if public == "P":
#                 treepath = tree.split('/')
#                 parent = None
#                 if len(treepath) > 1:
#                     parent = Place.objects.get(tree='/'.join(treepath[:-1]))
#                 if page =="Y":
#                     object = Venue(vernon_id=v_id, name=treepath[-1], parent=parent, tree=tree)
#                     print "XXX added venue - %s" % tree
#                 else:
#                     object = Place(vernon_id=v_id, name=treepath[-1], parent=parent, tree=tree)
#                     print "added place - %s" % tree
#                 object.save()
#         del reader
        
    def get_venue(self):
        """
        Returns the closest parent Venue for this Place
        """
        try:
            return self.venue
        except Venue.DoesNotExist:
            return self.parent_venue()

    def get_places(self):
        """
        Returns a list of Places contained within this Place
        """
        places = []
        for p in self.places.all():
            places.append(p)
            places.extend(p.get_places())
        return places
        
    class Meta:
        app_label = "events"


class Venue(Place):
    """
    Represents a place in the gallery that has its own web page	

    # Create a new place tree
    >>> building = Venue.objects.create(name="Art Gallery of New South Wales", vernon_id=1, slug="agnsw")
    >>> level = Venue.objects.create(name="Ground Floor", vernon_id=2, parent=building, slug="ground_floor")
    >>> gallery = Venue.objects.create(name="Dummy Gallery", vernon_id=3, parent=level, slug="dummy")
    >>> room = Place.objects.create(name="First Room", vernon_id=4, parent=gallery)
    >>> wall = Place.objects.create(name="North Wall", vernon_id=5, parent=room)
    >>> wall.parent.name
    'First Room'
    
    >>> str(wall.parent_venue())
    'Dummy Gallery'
    
    >>> gallery.get_absolute_url()
    "/venues/dummy/"
    
    >>> wall.get_absolute_url()
    "/venues/dummy/"
    
    >>> x = Place.objects.get(vernon_id = 3)
    >>> x.get_absolute_url()
    "/venues/dummy/"
    
    """
    slug = models.SlugField()
    directions = models.TextField(blank=True, help_text=MARKUP_HELP)
    accessible_directions = models.TextField(blank=True, help_text=MARKUP_HELP)
    hireable = models.BooleanField()
    description = models.TextField(blank=True, help_text=MARKUP_HELP)
    floorplan_coordinates = models.CharField(max_length=255, blank=True)
        
    def __unicode__(self):
        return "%s - %s" % (self.name, self.parent)        
                
    @models.permalink
    def get_absolute_url(self):
        return ('events.views.venue', (), {'slug': self.slug})
        
    class Meta:
        app_label = "events"
        ordering = ['name', 'vernon_id']


LOCATION_ACCURACY = (
    ('country', 'country'),
    ('region', 'region'),
    ('city / town', 'city / town'),
    ('suburb', 'suburb'),
    ('street address', 'street address'),
)

class ExternalLocation(models.Model):
    """
    A geographical location
    """
    location = models.CharField(max_length=200, blank=True, help_text = "This field is not made public, but can be used to search Google Maps")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    name = models.CharField(max_length=200, help_text = "as displayed on site")
    zoomlevel = models.IntegerField(max_length=2, blank=True, null=True)
    accuracy = models.CharField(max_length=20, choices=LOCATION_ACCURACY, blank=True)
    url = models.URLField(blank=True)
    street_address = models.CharField(max_length=200, blank=True)
    locality = models.CharField(max_length=200, blank=True)
    region = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=5, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    telephone = models.CharField(max_length=12, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'External location'
        verbose_name_plural = 'External locations'
        app_label = "events"
        
class VenuePhoto(models.Model):
    image = models.ImageField(upload_to="exhibition_images/additional/")
    caption = models.TextField(blank=True)
    venue = models.ForeignKey(Venue)
    date_added = models.DateTimeField(auto_now_add=True)
    attribution = models.TextField(blank=True, help_text="Photo attributions begin with 'Photo: '")
    order = PositionField(unique_for_field='venue')
    
    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = "Venue photo"
        verbose_name_plural = "Venue photos"

    def __unicode__(self):
        return u"%s - %s" % (self.caption, self.image)

    def __str__(self):
        return self.__unicode__()

    class Meta:
        app_label = "events"
