from APIApp import APIApp
import ffbp

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

        embiggen = 0;

        if self.user.settings.embiggen_photos :
            embiggen = 1;
            
        return self.api_ok({'photos' : rsp['photos'], 'embiggen' : embiggen})
        
