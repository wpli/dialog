# User profile: contains information about keywords, contacts, and
# other data
class tbh_user_profile_t():
    def __init__( self, user_id=0 ):
        self.user_id = None
        self.keywords = None
        self.contacts = None
        self.load_user_info( user_id )

    def load_user_info( self, user_id ):
        if user_id == 0:
            self.user_id = user_id
            self.keywords = [ 'chair', \
                                  'wheelchair', \
                                  'hal', \
                                  'computer' ]
        
            self.contacts = { 'tech_support': 
            
if __name__ == '__main__':
    user_profile = tbh_user_profile_t()
    print user_profile.user_id
    print user_profile.keywords
    print user_profile.contacts
