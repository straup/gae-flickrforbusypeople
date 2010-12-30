from config import config

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
    contacts_crumb = self.generate_crumb(self.user, 'method=contacts')
    self.assign('search_crumb', search_crumb)
    self.assign('contacts_crumb', contacts_crumb)

    contacts_30m = self.get_contacts('30m', [])
    contacts_2h = self.get_contacts('2h', contacts_30m['filter'])
    contacts_4h = self.get_contacts('4h', contacts_2h['filter'])
    contacts_8h = self.get_contacts('8h', contacts_4h['filter'])

    slices = []
    slices.append(contacts_30m)
    slices.append(contacts_2h)
    slices.append(contacts_4h)
    slices.append(contacts_8h)

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
    elif duration == '8h' :
        hours = 8
    else :
        duration = 1
        hours = 1

    offset = 60 * 60 * hours
    dt = int(time.time() - offset)

    if config['ffbp_deferred_loading'] :
      return {'contacts' : [], 'filter' : filter, 'error' : None, 'defer' : 1, 'offset' : dt, 'duration' : duration, 'count' : 0 }

    contacts_filter = self.user.settings.search_in_contacts_filter

    # TO DO: Backet times, so 30 minutes becomes 0-30 minutes
    # and 2hr becomes 30-120 minutes and so on. This requires
    # changes in the Flickr API itself.

    args = {
        'auth_token' : self.user.token,
        'date_lastupload' : dt,
        'filter' : contacts_filter,
    }

    rsp = self.api_call('flickr.contacts.getListRecentlyUploaded', args)

    contacts = []
    new_filter = filter

    if not rsp or rsp['stat'] != 'ok' :

        error = 'Hrm. Something went wrong calling the Flickr API...'

        if rsp :
            error = rsp['message']

        return {'contacts' : contacts, 'filter' : new_filter, 'error' : error, 'offset' : dt, 'duration' : duration, 'count' : 0 }

    if rsp['contacts']['total'] == 0 :
        return {'contacts' : contacts, 'filter' : new_filter, 'error' : None, 'offset' : dt, 'duration' : duration, 'count' : 0 }

    for c in rsp['contacts']['contact'] :

        if c['nsid'] in filter :
            continue

        icon = self.flickr_get_buddyicon(c['nsid'])

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

        #
        
        filter = self.request.get('filter')

        ffbp.Settings.search_in_contacts_filter(self.user.nsid, filter)

        #
        
        embiggen = self.request.get('embiggen')        

        if not filter in ('all', 'ff') :
            self.assign('error', 'invalid_filter')
            self.display('settings.html')
            return

        if embiggen == 'yes' :
          ffbp.Settings.embiggen_photos(self.user.nsid, True)
        else :
          ffbp.Settings.embiggen_photos(self.user.nsid, False)        

        #

        self.redirect('/')
