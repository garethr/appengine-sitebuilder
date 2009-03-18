from google.appengine.ext import db
from google.appengine.ext import search

from lib import slugify

class Page(search.SearchableModel):
    "Represents an piece of content"
    title = db.StringProperty(required=True)
    slug = db.StringProperty()
    content = db.TextProperty(required=True)
    external_url = db.LinkProperty()
    internal_url = db.StringProperty()
    publish_date = db.DateTimeProperty(auto_now_add=True)
    tags = db.StringListProperty()
        
    def put(self):
        self.slug = slugify(unicode(self.title))
        if not self.internal_url:
            self.internal_url = "/%s/%s/" % (self.publish_date.strftime("%Y/%m/%d"), self.slug)	    
        for tag in self.tags:
            obj = Tag(
                name=tag,
                title=self.title,
                url=self.internal_url,
            )
            obj.put()
        
        super(Page, self).put()
        
    def delete(self):
        tags = Tag.all()
        tags.filter('url =', self.internal_url)
        for tag in tags:
            tag.delete()
        super(Page, self).delete()
        
class Tag(db.Model):
    name = db.StringProperty(required=True)
    url = db.StringProperty(required=True)
    title = db.StringProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
        
class Content(db.Model):
    path = db.StringProperty(required=True)
    ident = db.StringProperty(required=True)
    value = db.TextProperty(required=True)