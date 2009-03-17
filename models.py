from google.appengine.ext import db

from lib import slugify

class NewsItem(db.Model):
    "Represents an piece of content"
    title = db.StringProperty(required=True)
    slug = db.StringProperty()
    content = db.StringProperty(required=True)
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
        tags.delete()
        super(NewsItem, self).delete()
        
class Tag(db.Model):
    name = db.StringProperty(required=True)
    url = db.StringProperty(required=True)
    title = db.StringProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)