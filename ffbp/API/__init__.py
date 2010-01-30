from APIApp import APIApp
import ffbp

import time
import md5

import logging

class Dispatch (ffbp.Request, APIApp) :

    def __init__ (self):
        ffbp.Request.__init__(self)
        APIApp.__init__(self)

    def post (self) :

        if not self.check_logged_in(self.min_perms) :
            self.api_error(403)
            return

        method = self.request.get('method')
        format = self.request.get('format')

        if format and not format in self.valid_formats :
            self.api_error(999, 'Not a valid format')
            return

        if format :
            self.format = format

        if method == 'search' :
            return self.__search()

        elif method == 'contacts' :
            return self.__contacts()

        else :
            self.api_error(404, 'Invalid method')
            return

    def ensure_crumb (self, path) :

        if not self.validate_crumb(self.user, path, self.request.get('crumb')) :
            self.api_error(400, 'Invalid crumb')
            return False

        return True

    def __search (self) :

        required = ('crumb', 'user_id', 'min_upload_date')

        if not self.ensure_args(required) :
            return

        if not self.ensure_crumb('method=search') :
            return

        method = 'flickr.photos.search'

        args = {
            'auth_token' : self.user.token,
            'user_id' : self.request.get('user_id'),
            'min_upload_date' : self.request.get('min_upload_date'),
            'extras' : 'owner_name',
            }

        rsp = self.api_call(method, args)

        if not rsp :
            return self.api_error()

        if rsp['stat'] != 'ok' :
            return self.api_error()

        self.check_useragent()

        embiggen = 0
        mobile = 0

        if self.user.settings.embiggen_photos:
            embiggen = 1

        if self.browser['mobile']:
            mobile = 1

        return self.api_ok({'photos' : rsp['photos'], 'embiggen' : embiggen, 'mobile': mobile})

    def __contacts (self) :

        required = ('crumb', 'offset')

        if not self.ensure_args(required) :
            return

        if not self.ensure_crumb('method=contacts') :
            return

        duration = self.request.get('offset')

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

        contacts_filter = self.user.settings.search_in_contacts_filter

        args = {
            'auth_token' : self.user.token,
            'date_lastupload' : dt,
            'filter' : contacts_filter,
            }

        rsp = self.api_call('flickr.contacts.getListRecentlyUploaded', args)

        contacts = []

        foo = None

        if not rsp or rsp['stat'] != 'ok' :

            code = 999
            error = 'Hrm. Something went wrong calling the Flickr API...'

            if rsp :
                code = rsp['code']
                error = rsp['message']

            self.api_error(code, error)
            return

        elif rsp['contacts']['total'] == 0 :
            foo = {'contacts' : contacts, 'error' : None, 'offset' : dt, 'duration' : duration, 'count' : 0 }

        else :
            for c in rsp['contacts']['contact'] :

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

            foo =  {'contacts' : contacts, 'error' : None, 'offset' : dt, 'duration' : duration, 'count' : len(contacts) }

        return self.api_ok(foo)
