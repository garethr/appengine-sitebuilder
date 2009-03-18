import re
import unicodedata

END_BODY = re.compile(r'</body.*?>', re.I|re.S)
    
def slugify(value):
    "Slugify a string, to make it URL friendly."

    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+','-',value)

def add_to_end(self, html, extra_html):
    "Adds extra_html to the end of the html page (before </body>)"
    match = END_BODY.search(html)
    if not match:
        return html + extra_html
    else:
        return html[:match.start()] + extra_html + html[match.start():]
