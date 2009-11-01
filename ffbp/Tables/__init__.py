from google.appengine.ext import db

class dbSettings (db.Model) :

    nsid = db.StringProperty()
    search_in_contacts_filter = db.StringProperty()
    embiggen_photos = db.BooleanProperty()
