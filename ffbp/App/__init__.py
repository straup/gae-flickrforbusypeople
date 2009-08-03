import ffbp
import ffbp.Settings

from google.appengine.api import memcache

import time
import logging
import md5

class Main (ffbp.Request) :

  def get (self):

    if not self.check_logged_in(self.min_perms) :
        self.display("main_logged_out.html")
        return

    search_crumb = self.generate_crumb(self.user, 'method=search')
    self.assign('search_crumb', search_crumb)
    
    contacts_30m = self.get_contacts('30m', [])
    contacts_2h = self.get_contacts('2h', contacts_30m['filter'])
    contacts_4h = self.get_contacts('4h', contacts_2h['filter'])
    
    slices = []
    slices.append(contacts_30m)
    slices.append(contacts_2h)
    slices.append(contacts_4h)

    self.assign('slices', slices)
    self.display("main_logged_in.html")
    return

  def get_contacts (self, duration=1, filter=[]) :

    if duration == '30m' :
        hours = .5
    elif duration == '2h' :
        hours = 2
    elif duration == '4h' :
        hours = 4
    else :
        duration = 1
        hours = 1
        
    offset = 60 * 60 * hours
    dt = int(time.time() - offset)

    contacts_filter = self.user.settings.search_in_contacts_filter
    
    args = {
        'auth_token' : self.user.token,
        'date_lastupload' : dt,
        'filter' : contacts_filter,
    }

    rsp = self.api_call('flickr.contacts.getListRecentlyUploaded', args)
    
    contacts = []
    new_filter = filter
    
    if not rsp or rsp['stat'] != 'ok' :

        error = 'INVISIBLE ERRORCAT HISSES AT YOU'

        if rsp :
            error = rsp['message']
            
        return {'contacts' : contacts, 'filter' : new_filter, 'error' : error, 'offset' : dt, 'duration' : duration, 'count' : 0 }
    
    if rsp['contacts']['total'] == 0 :
        return {'contacts' : contacts, 'filter' : new_filter, 'error' : None, 'offset' : dt, 'duration' : duration, 'count' : 0 }
    
    for c in rsp['contacts']['contact'] :

        if c['nsid'] in filter :
            continue
        
        args = {
            'user_id' : c['nsid'],
            'method' : 'flickr.photos.search',
            'auth_token' : self.user.token,
            'min_upload_date' : dt,
            }

        icon = self.get_buddyicon(c['nsid'])

        hex = md5.new(c['nsid']).hexdigest()
        short_hex = hex[0:6]

        user = {
            'username' : c['username'],
            'nsid' : c['nsid'],
            'nsid_hex' : hex,
            'nsid_short_hex' : short_hex,
            'count' : c['photos_uploaded'],
            'buddyicon' : icon,
        }
        
        contacts.append(user)
        new_filter.append(c['nsid'])
        
    return {'contacts' : contacts, 'filter' : new_filter, 'error' : None, 'offset' : dt, 'duration' : duration, 'count' : len(contacts) }

  def get_user (self, nsid) :

      memkey = "people_getinfo_%s" % nsid
      cache = memcache.get(memkey)
      
      if cache :
          return cache

      rsp = self.api_call('flickr.people.getInfo', {'user_id' : nsid, 'auth_token' : self.user.token})
      
      if not rsp or rsp['stat'] != 'ok' :
          return

      ttl = 60 * 60 * 24 * 14
      
      memcache.add(memkey, rsp['person'], ttl)
      return rsp['person']

  def get_buddyicon (self, nsid) :
      
      user = self.get_user(nsid)
      
      if user['iconserver'] == 0 :
        return 'http://www.flickr.com/images/buddyicon.jpg'
      
      return "http://farm%s.static.flickr.com/%s/buddyicons/%s.jpg" % (user['iconfarm'], user['iconserver'], nsid)

class Settings (ffbp.Request) :

    def get (self) :

        if not self.check_logged_in(self.min_perms) :
            self.do_flickr_auth(self.min_perms)
            return

        settings_crumb = self.generate_crumb(self.user, 'method=settings')
        self.assign('settings_crumb', settings_crumb)

        self.display('settings.html')
        return
    
    def post (self) :
    
        if not self.check_logged_in(self.min_perms) :
            self.do_flickr_auth(self.min_perms)
            return

        if not self.validate_crumb(self.user, 'method=settings', self.request.get('crumb')) :
            self.assign('error', 'invalid_crumb')
            self.display('settings.html')
            return

        filter = self.request.get('filter')

        if not filter in ('all', 'ff') :
            self.assign('error', 'invalid_filter')
            self.display('settings.html')
            return
        
        ffbp.Settings.search_in_contacts_filter(self.user.nsid, filter)

        self.redirect('/')
