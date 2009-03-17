from google.appengine.ext import db
from google.appengine.ext import search

from lib import slugify

class NewsItem(search.SearchableModel):
    "Represents an piece of content"
    title = db.StringProperty(required=True)
    slug = db.StringProperty()
    content = db.TextProperty(required=True)
    external_url = db.LinkProperty(required=True)
    internal_url = db.StringProperty()
    # we store the date automatically so we can filter the list
    publish_date = db.DateTimeProperty(auto_now_add=True)
    tags = db.StringListProperty()
    
    def get_url(self):
        return "/%s/%s/" % (self.publish_date.strftime("%Y/%m/%d"), self.slug)	    
    
    def put(self):
        self.slug = slugify(unicode(self.title))
        self.internal_url = self.get_url()        
        for tag in self.tags:
            obj = Tag(
                name=tag,
                title=self.title,
                url=self.internal_url,
            )
            obj.put()
        
        super(NewsItem, self).put()
        
    def delete(self):
        tags = Tag.all()
        tags.filter('url =', self.internal_url)
        for tag in tags:
            tag.delete()
        super(NewsItem, self).delete()
        
class Tag(db.Model):
    name = db.StringProperty(required=True)
    url = db.StringProperty(required=True)
    title = db.StringProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    
class Content(db.Model):
    path = db.StringProperty(required=True)
    ident = db.StringProperty(required=True)
    value = db.TextProperty(required=True)