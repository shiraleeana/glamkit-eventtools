#Exhibition
#ExhibitionSponsor
#ExhibitionPhoto
#ExhibitionVideo

from django.db import models
from datetime import timedelta
from events.models.venues import Venue
from settings import MARKUP_HELP
from podcasts.models import Channel
from grappelli.fields import PositionField
# from product.models import Product
from generic.models import Sponsor
from lumpypages.models import LumpyPage
from events.models.venues import ExternalLocation
from datetime import date
from django.db.models import signals
from staticgenerator import quick_delete

EVENT_STATUS = (

    ('draft', 'draft'),
    ('published', 'published'),
    ('removed', 'removed'),
)

CENTAMAN = 'https://ticketing.ag.nsw.gov.au/'

SIZE     = (
    (1, 'major'),
    (2, 'regular'),
    (3, 'minor'),
)

LOGO_SIZE     = (
    (1, 'large'),
    (2, 'medium'),
    (3, 'small'),
)

class SponsorshipType(models.Model):
    singular = models.CharField(max_length=50)
    plural = models.CharField(max_length=50)
    rank = models.IntegerField()
    logo_size = models.IntegerField(choices=LOGO_SIZE)

    class Meta:
        ordering = ['rank']
        app_label = "events"
    
    def __unicode__(self):
        return self.singular
        
class Exhibition(models.Model):
    """
    Represents an exhibtion
    """
    title = models.CharField(max_length = 255)
    size = models.IntegerField(max_length=1, choices=SIZE, default=2)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(help_text=MARKUP_HELP)
    pullquote = models.TextField(blank=True)
    pullquote_attribution = models.CharField(max_length=255, blank=True)
    venue = models.ForeignKey(Venue, blank=True, null=True)
    status = models.CharField("status", choices=EVENT_STATUS, default="draft", max_length=10)
    slug = models.SlugField()
    start = models.DateField()
    end = models.DateField()
    acknowledgements = models.TextField(blank=True, help_text=MARKUP_HELP)
    full_width_banner = models.BooleanField()
    poster_image = models.ImageField(upload_to="exhibition_images/canonical/")
    poster_image_detail = models.ImageField(upload_to="exhibition_images/canonical-detail/", help_text="Must be 725x380 pixels.")
    poster_image_caption = models.TextField()
    poster_image_attribution = models.TextField(blank=True, help_text="Photo attributions begin with 'Photo: '")
    start_promoting = models.DateField(null=True, blank=True, help_text="Determines when the exhibition gets displayed in 'coming soon' listings. If left blank, will default to six weeks before start.") # maybe let status do this manually?
    link_to_centaman = models.BooleanField()
    catalogue_pdf = models.URLField(blank=True)
    adult_price = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)
    concession_price = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)
    family_price = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)
    school_price = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)
    season_ticket_price = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)
    audio_tour = models.ForeignKey(Channel, blank=True, null=True)
    sponsors = models.ManyToManyField(Sponsor, through='ExhibitionSponsor')
    pages = models.ManyToManyField(LumpyPage, blank=True)
    
    def save(self):
        if not self.start_promoting:
            self.start_promoting = self.start - timedelta(days=42)
        super(Exhibition, self).save()          

    def ticket_sales(self):
        return CENTAMAN if self.link_to_centaman else None
    
    def started(self):
        return self.start <= date.today()
    
    def __unicode__(self):
        return self.title
        
    def main_competition(self):
        try:
            return self.competitionyear_set.all()[0]
        except:
            return None 

    def winners(self):
        from prizes.models import PrizeEntry, Prize
        items=[]
        for competition in self.competitionyear_set.all():
#            prizes = Prize.objects.filter(hide_from_archibald=False, competition=competition.competition)
            prizes = competition.competition.prize_set.filter(exhibition_page_order__lt=3)
            for p in prizes:
                try:
                    item = PrizeEntry.objects.get(year=competition.year, competition=competition.competition, prizes=p)
                    item.link_text = "%s Winner" % p.name
                    if not item.poster_image:
                        item.poster_image = competition.poster_image
                except:
                    if p.url_override:
                        item = p
                        item.link_text = "%s Winner" % p.name
                    else:
                        item = competition
                        item.link_text = "%s Finalists" % p.name
                items.append(item)
        return items
                    
#     @models.permalink
    def get_absolute_url(self):
        return '/'

    class Meta:
        ordering = ('title',)
        app_label = "events"
        
def purge_exhibition(sender, instance, **kwargs):
    quick_delete(instance)

signals.post_save.connect(purge_exhibition, sender=Exhibition)

class SponsorRelationshipBase(models.Model):
    sponsor = models.ForeignKey(Sponsor)
    sponsortype = models.ForeignKey(SponsorshipType, verbose_name="Type")
    annotation = models.CharField(max_length=255, blank=True)

    class Meta:
        app_label = "events"
        abstract = True
        
    def __unicode__(self):
        return u"%s - %s" % (self.sponsortype, self.sponsor)

    def logo(self):
        return {
            1: self.sponsor.large_logo,
            2: self.sponsor.medium_logo,
            3: self.sponsor.small_logo,
        }[self.sponsortype.logo_size]

class ExhibitionSponsor(SponsorRelationshipBase):
    exhibition = models.ForeignKey(Exhibition)

    class Meta(SponsorRelationshipBase.Meta):
        verbose_name = "Exhibition sponsor"
        verbose_name_plural = "Exhibition sponsors"        

class ExhibitionPhoto(models.Model):
    image = models.ImageField(upload_to="exhibition_images/additional/")
    caption = models.TextField()
    exhibition = models.ForeignKey(Exhibition)
    date_added = models.DateTimeField(auto_now_add=True)
    attribution = models.TextField(blank=True, help_text="Photo attributions begin with 'Photo: '")
    during_exhibition = models.BooleanField("Only display during exhibition")
    order = PositionField(unique_for_field='exhibition')
        
    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = "Exhibition photo"
        verbose_name_plural = "Exhibition photos"
        app_label = "events"
        
    def __unicode__(self):
        return self.caption

    def __str__(self):
        return self.__unicode__()

class ExhibitionVideo(models.Model):
    title = models.CharField(max_length=255)
    exhibition = models.ForeignKey(Exhibition)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    order = PositionField(unique_for_field='exhibition')
    poster_image = models.ImageField(upload_to='exhibition_videos')
    
    class Meta:
        app_label = "events"
    
    def __unicode__(self):
        return self.title

class RegionalTour(models.Model):
    exhibition = models.ForeignKey(Exhibition)
    sponsors = models.ManyToManyField(Sponsor, through='RegionalTourSponsor')
    
    class Meta:
        app_label = "events"

    def __unicode__(self):
        return "%s Regional Tour" % self.exhibition

class RegionalTourLocation(models.Model):
    tour = models.ForeignKey(RegionalTour)
    location = models.ForeignKey(ExternalLocation)
    start = models.DateField()
    end = models.DateField()

    class Meta:
        app_label = "events"
        ordering = ['start','end']

    def __unicode__(self):
        return "%s - %s" % (self.location, self.tour)
    
class RegionalTourSponsor(SponsorRelationshipBase):
    regionaltour = models.ForeignKey(RegionalTour)

    class Meta(SponsorRelationshipBase.Meta):
        verbose_name = "Regional Tour sponsor"
        verbose_name_plural = "Regional Tour sponsors"