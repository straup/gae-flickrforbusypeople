from google.appengine.ext import db
from ffbp.Tables import dbSettings

def get_settings_for_user (nsid, auto_create=True) :

    gql = "SELECT * FROM dbSettings WHERE nsid = :1"
    res = db.GqlQuery(gql, nsid)

    settings = res.get()
    
    if settings :
        return settings

    if auto_create :
        return create_settings_for_user(nsid)

    return False

def create_settings_for_user (nsid) :

    settings = dbSettings()
    settings.nsid = nsid
    settings.search_in_contacts_filter = 'all'
    settings.put()

    return settings

def search_in_contacts_filter (nsid, context='all') :

    settings = get_settings_for_user(nsid)
    settings.search_in_contacts_filter = context
    settings.put()

def embiggen_photos (nsid, bool=True) :

    settings = get_settings_for_user(nsid)
    settings.embiggen_photos = bool
    settings.put()
