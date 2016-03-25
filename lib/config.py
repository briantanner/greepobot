import json, os, logging

class Config:
  __URLS__ = {
    'lamia':'http://us36.grepolis.com',
    'marathon':'http://us37.grepolis.com',
    'naxos':'http://us38.grepolis.com',
    'olympia':'http://us39.grepolis.com'
  }

  defaults = {
    "territorylimit": {},
    "rangelimit": {},
    "monitor": {},
    "monitorghost": {},
    "botadmins": ["dev.lance"],
    "last_scrape": {},
    "world_scrape": {},
    "ghost_scrape": {},
    "feedback": {},
    "urls": {}
  }

  def __init__(self, file):
    self.file = file
    self.dir = os.getcwd()
    self.settings = False
    
    Config.defaults["urls"] = Config.__URLS__

    if os.path.isfile(os.path.join(self.dir, file)): #Check for config file
      logging.info('Using config file: %s\%s' %(self.dir,file))
      with open(os.path.join(self.dir,file), 'r') as f:
        self.settings = json.load(f)
        
    elif os.path.isfile(os.path.join(self.dir,"backup", file+".bak")): #Check for Backup config file
      logging.critical('Config file not found, backup file is present in the backup directory. Something bad may have happened.')
      # print("ERROR: Unable to find bot config file in primary location: %s\%s" % (self.dir,file))
      # print("A backup file exists, recover or remove the backup config file and start the server again")
      self.settings = False 
      
    else: #Create new config file
      print Config.defaults
      with open(os.path.join(self.dir, file), 'w') as f:
        json.dump(Config.defaults, f)
        #f.write(str(defaultconfig))
      logging.info('Created bot config file %s\%s' %(self.dir,file))
      self.settings = Config.defaults

  def get(self):
    return self.settings

  def save(self, settings):
    self.settings = settings
    with open(os.path.join(self.dir, self.file), 'w') as f:
      json.dump(settings, f)
    return