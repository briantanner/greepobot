import json, os, logging

class Config:
  __URLS__ = {
    'alpha':'http://us1.grepolis.com',
    'beta':'http://us2.grepolis.com',
    'gamma':'http://us3.grepolis.com',
    'delta':'http://us4.grepolis.com',
    'epsilon':'http://us6.grepolis.com',
    'zeta':'http://us7.grepolis.com',
    'eta':'http://us8.grepolis.com',
    'theta':'http://us9.grepolis.com',
    'iota':'http://us10.grepolis.com',
    'kappa':'http://us11.grepolis.com',
    'lambda':'http://us12.grepolis.com',
    'mu':'http://us13.grepolis.com',
    'nu':'http://us14.grepolis.com',
    'xi':'http://us15.grepolis.com',
    'omicron':'http://us16.grepolis.com',
    'pi':'http://us17.grepolis.com',
    'rho':'http://us18.grepolis.com',
    'sigma':'http://us19.grepolis.com',
    'tau':'http://us20.grepolis.com',
    'upsilon':'http://us21.grepolis.com',
    'phi':'http://us22.grepolis.com',
    'chi':'http://us23.grepolis.com',
    'psi':'http://us24.grepolis.com',
    'omega':'http://us25.grepolis.com',
    'athens':'http://us26.grepolis.com',
    'byzantium':'http://us27.grepolis.com',
    'corinth':'http://us28.grepolis.com',
    'delphi':'http://us29.grepolis.com',
    'ephesus':'http://us30.grepolis.com',
    'gythium':'http://us31.grepolis.com',
    'heraklion':'http://us32.grepolis.com',
    'ithaca':'http://us33.grepolis.com',
    'juktas':'http://us34.grepolis.com',
    'knossos':'http://us35.grepolis.com',
    'lamia':'http://us36.grepolis.com',
    'marathon':'http://us37.grepolis.com',
    'naxos':'http://us38.grepolis.com',
    'olympia':'http://us39.grepolis.com'
  }

  default = {
    "territorylimit": {},
    "rangelimit": {},
    "monitor": {},
    "monitorghost": {},
    "botadmins": ["dev.lance"],
    "last_scrape": {},
    "world_scrape": {},
    "ghost_scrape": {},
    "feedback": {},
    "urls": Config.__URLS__
  }

  def __init__(self, file):
    currdir = os.getcwd()
    settings = False

    if os.path.isfile(os.path.join(currdir, file)): #Check for config file
      logging.info('Using config file: %s\%s' %(currdir,file))
      with open(os.path.join(currdir,file), 'r') as f:
        settings = json.load(f)
        
    elif os.path.isfile(os.path.join(currdir,"backup", file+".bak")): #Check for Backup config file
      logging.critical('Config file not found, backup file is present in the backup directory. Something bad may have happened.')
      # print("ERROR: Unable to find bot config file in primary location: %s\%s" % (currdir,file))
      # print("A backup file exists, recover or remove the backup config file and start the server again")
      settings = False 
      
    else: #Create new config file
      with open(os.path.join(currdir, file), 'w') as f:
        json.dump(defaultconfig, f)
        #f.write(str(defaultconfig))
      logging.info('Created bot config file %s\%s' %(currdir,file))
      settings = Config.default

    return settings

  def save(self, settings):
    with open(os.path.join(currdir,cfgfile), 'w') as f:
      json.dump(settings, f)
    return True


