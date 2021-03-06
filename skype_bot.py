import json, os, logging, gzip, Skype4Py, operator, math, socket, datetime
from urllib import urlretrieve,unquote_plus
from urllib2 import Request,urlopen
from time import time, ctime, sleep
currdir = os.getcwd()
cfgfile = 'bot.cfg' #the file where we store defpochs/conqeusts and other info
datadir = 'data_files' # directory where we store world data files.
logging.basicConfig(filename='skype_bot.log',level=logging.DEBUG, format='%(asctime)s %(message)s')
skype = Skype4Py.skype.Skype()
timeout = 30
settings = {}
socket.setdefaulttimeout(timeout)

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
defaultconfig = {"territorylimit": {}, "rangelimit": {}, "monitor": {}, "monitorghost": {}, "botadmins": ["dev.lance"], "last_scrape":{}, "world_scrape":{}, "ghost_scrape":{}, "feedback":{}, "urls":__URLS__}

def cfgcheck():   
	
	if os.path.isfile(os.path.join(currdir,cfgfile)): #Check for config file
		#logging.info('Using config file: %s\%s' %(currdir,cfgfile))
		with open(os.path.join(currdir,cfgfile), 'r') as f:
			status = json.load(f)
			
	elif os.path.isfile(os.path.join(currdir,"backup",cfgfile+".bak")): #Check for Backup config file
		#logging.critical('Config file not found, backup file is present in the backup directory. Something bad may have happened.')
		print("ERROR: Unable to find bot config file in primary location: %s\%s" % (currdir,cfgfile))
		print("A backup file exists, recover or remove the backup config file and start the server again")
		status = False 
		
	else: #Create new config file
		with open(os.path.join(currdir,cfgfile), 'w') as f:
			json.dump(defaultconfig, f)
			#f.write(str(defaultconfig))
		#logging.info('Created bot config file %s\%s' %(currdir,cfgfile))
		status = defaultconfig
	
	return status

def cfgsave(settings):  ## save config file with current settings data
	with open(os.path.join(currdir,cfgfile), 'w') as f:
		json.dump(settings, f)
	status = True
	return status


def loadfile(server,datatype):  ### open gzip world file and read into memory
	if not os.path.exists(currdir+"/"+datadir): os.makedirs(currdir+"/"+datadir)
	if not os.path.exists(os.path.join((currdir+"/"+datadir),server+"-"+datatype+".txt.gz")): getworlddata(server, settings['urls'][server], datatype)
	
		
	localfile = os.path.join((currdir+"/"+datadir),server+"-"+datatype+".txt.gz")
	datafile = {}
	if datatype == "conquers": datafile[datatype] = []
	try:
		f = gzip.open(localfile, 'rb')
		# with gzip.open(localfile, 'rb') as f:
		for line in f:
			
			if datatype == "conquers":
				if len(line.split(',')) < 7: #### some times the conquest file would have a line with just 4 items and the script would dump.  Need to handle cleaner
					print ("Skipping line becaue too short")
					continue	
				datafile[datatype].append((line.split(',')[0], line.split(',')[1], line.split(',')[2], line.split(',')[3], line.split(',')[4], line.split(',')[5], line.split(',')[6].strip() ))
			elif len(line.split(',')) == 7:
				datafile[line.split(',')[0]] = ()
				datafile[line.split(',')[0]] = (line.split(',')[1], line.split(',')[2], line.split(',')[3], line.split(',')[4], line.split(',')[5], line.split(',')[6].strip() )
			elif len(line.split(',')) == 6:
				datafile[line.split(',')[0]] = ()
				datafile[line.split(',')[0]] = (unquote_plus(line.split(',')[1]), line.split(',')[2], line.split(',')[3], line.split(',')[4], line.split(',')[5].strip() )
			elif len(line.split(',')) == 5:
				datafile[line.split(',')[0]] = ()
				datafile[line.split(',')[0]] = (line.split(',')[1], line.split(',')[2], line.split(',')[3], line.split(',')[4].strip() )
			elif len(line.split(',')) == 3:
				datafile[line.split(',')[1]] = ()
				datafile[line.split(',')[1]] = (line.split(',')[2].strip() )
	except EnvironmentError:
		
		#logging.warn("Unable to open file %s " % (localfile))
		print (("Unable to open file %s ") % (localfile))
		getworlddata(server, settings['urls'][server], datatype)
	
	return datafile

def getactiveservers():
	activeservers = []
	for chat in settings['monitor']:
				for server in settings['monitor'][chat]:
					if server not in activeservers: activeservers.append(str(server))
	for chat in settings["monitorghost"]:
		for server in settings["monitorghost"][chat]:
			if server not in activeservers: activeservers.append(str(server))
	return activeservers
	
def getworlddata(server, url, datatype):
	try:
		if datatype == "all":
			urlretrieve('%s/data/%s.txt.gz' % (url,"players"),'%s/%s/%s-%s.txt.gz' % (currdir,datadir,server,"players"))
			urlretrieve('%s/data/%s.txt.gz' % (url,"alliances"),'%s/%s/%s-%s.txt.gz' % (currdir,datadir,server,"alliances"))
			urlretrieve('%s/data/%s.txt.gz' % (url,"towns"),'%s/%s/%s-%s.txt.gz' % (currdir,datadir,server,"towns"))
			urlretrieve('%s/data/%s.txt.gz' % (url,"islands"),'%s/%s/%s-%s.txt.gz' % (currdir,datadir,server,"islands"))
			urlretrieve('%s/data/%s.txt.gz' % (url,"player_kills_def"),'%s/%s/%s-%s.txt.gz' % (currdir,datadir,server,"player_kills_def"))
			urlretrieve('%s/data/%s.txt.gz' % (url,"player_kills_att"),'%s/%s/%s-%s.txt.gz' % (currdir,datadir,server,"player_kills_att"))
			urlretrieve('%s/data/%s.txt.gz' % (url,"conquers"),'%s/%s/%s-%s.txt.gz' % (currdir,datadir,server,"conquers"))
			
			
			if server not in settings["world_scrape"]: settings["world_scrape"][server] = []
			settings["world_scrape"][server] = (int(time()))
			cfgsave(settings)
		else: urlretrieve('%s/data/%s.txt.gz' % (url,datatype),'%s/%s/%s-%s.txt.gz' % (currdir,datadir,server,datatype))
			  
	except ValueError, e:
		print "[ValueError] Problem Downloading World File."
		print e
		pass
	except socket.error, e:
		print "[SocketError] Connection error: %s" % e
		pass
	except IOError, e:
		print "[IOError] Problem Downloading World File."
		print e
		pass
	except Exception, e:
		print "[Exception] Problem Downloaidng World File."
		print e
		pass
def changecheck(url,datatype):
	try:
		req = Request('%s/data/%s.txt.gz' % (url,datatype))
		req.get_method = lambda : 'HEAD'
		url_handle = urlopen(req)
		size = url_handle.info().getheaders("Content-Length")[0]
		url_handle.close()
		return size
	except Exception:
		pass
		#print "Something happened! Error code" % (err.code)
	except URLError, err:
		print "Some other error happened:" % (err.reason)
def alliance_members(server,alli_id):
	players = loadfile(server,"players")
	members = []
	for player in players:
		if not players[player][1]:continue
		if alli_id == players[player][1]: members.append(player)
	return members

def alliance_name(server, alli_id, default=None ):
	retval = []
	alliances = loadfile(server,"alliances")
	for alliance in alliances: 
		if alli_id == alliance: retval = unquote_plus(alliances[alliance][0])
	return retval

def find_player(server,playername, default=None):
	retval = []
	
	players = loadfile(server,"players")
	for player in players:
		if playername.lower() == unquote_plus(players[player][0].lower().strip()):
			retval = [player,unquote_plus(players[player][0]),players[player][1],players[player][2],players[player][3],players[player][4]]
	return retval

def find_alliance(server,alliname, default=None):
	retval = []
	#getworlddata(server,__URLS__[server],"alliances")
	alliances = loadfile(server,"alliances")
	for alliance in alliances:
		if alliname == unquote_plus(alliances[alliance][0].lower().strip()): 
			retval = [alliance,alliances[alliance][0],alliances[alliance][1],alliances[alliance][2],alliances[alliance][3],alliances[alliance][4]]
	return retval
	
def find_towns(server,pid):
	retval = []
	towns = loadfile(server, "towns")
	for town in towns:
		if towns[town][0] == pid: retval.append(towns[town])
	return retval
	
def find_island(server,x,y):
	islands = loadfile(server, "islands")
	for isle in islands:
		if x == islands[isle][0] and y == islands[isle][1]:
			island = isle
	return island
	
def square(x):
	return x * x

def town_in_ocean(town,ocean):
	town_ocean = int('%s%s' % (str(town[2][0]),str(town[3][0])))
	return town_ocean == ocean

def towns_by_ocean(towns,ocean):
	rettowns = {}
	for id in towns:
		town = towns[id]
		if town_in_ocean(town,ocean):
			rettowns[id] = town
	return rettowns

def player_towns_by_ocean(towns,ocean):
	rettowns = {}
	for id in towns:
		town = towns[id]
		if town_in_ocean(town,ocean) and len(town[0]) > 0:
			rettowns[id] = town
	return rettowns

def ghosts_by_ocean(towns,ocean):
	rettowns = {}
	for id in towns:
		town = towns[id]
		if town_in_ocean(town,ocean) and not len(town[0]):
			rettowns[id] = town
	return rettowns

def promote(chat, member_name): # not currently working
	print chat.MemberObjects
	for member in chat.Members:
		print member
		if member.Handle == member_name:
			print member.Role
			member.Role = Skype4Py.chatMemberRoleMaster
	return

def message_status(Message, Status):
	if Status not in ('SENT','RECEIVED') or len(Message.Body) < 2: return
	if Message.Body[0] not in ('>','!'): return
	cmd = Message.Body.split()[0][1:].upper()
	parms = '' if len(Message.Body.split()) < 2 else ' '.join(Message.Body.split()[1:])
	#logging.info('Command: %s => %s (parms: %s)' % (Message.FromHandle,cmd,parms))
	print ('Command: %s => %s (parms: %s)' % (Message.FromHandle,cmd,parms))
	SendMessage = Message.Chat.SendMessage

	if cmd in ( 'HELP','COMMANDS', '?' ):
		SendMessage('[*] Available commands: BOTSTATUS, CONQUESTS, EASYMONEY, FEEDBACK, HELP, LISTALLI, MONITOR, MONITORGHOST, MONITORLIST, NEARGHOST, NEARPLAYER, NEARALLI, PLAYER, RANGELIMIT, TOWNS, TERRITORY, TOPRANK, LISTWORLDS')

	elif cmd in ( 'CREATECHAT', ):
		try:
			botname = 'test.grepo'
			if skype.CurrentUser.Handle == 'test.grepo': botname = 'us.grepo'

			chat = skype.CreateChatWith(Message.FromHandle, botname)
			chat.SendMessage('.')
			sleep(1)

			chat.SendMessage('/setrole %s %s' % (Message.FromHandle, "MASTER"))
			chat.Kick(botname)
		except:
			pass
	
	elif cmd in ( 'LISTCHATS', ):
		if Message.FromHandle not in settings["botadmins"]: return
		chats = []
		for chat in settings['monitor']:
			if chat not in chats:
				chats.append('%s\r\n' % (chat))
		for chat in settings['monitorghost']:
			if chat not in chats:
				chats.append('%s\r\n' % (chat))
		SendMessage('Bot Chats: \r\n    %s' % ('    '.join(chats)))


	elif cmd in ( 'JOINCHAT', ):
		if Message.FromHandle not in settings["botadmins"]: return
		if not len(parms):
			SendMessage('[*] Syntax: JOINCHAT <chat id>')
		else:
			member = skype.User(Message.FromHandle)
			chat = skype.Chat(parms.split()[0])
			chat.SendMessage('/add %s' % (Message.FromHandle))

	elif cmd in ( 'KICK', ):
		if Message.FromHandle not in settings["botadmins"]: return
		if not len(parms):
			SendMessage('[*] Syntax: KICK <user name>')
		else:
			Message.Chat.Kick(parms.split()[0])

	elif cmd in ( 'ADD', ):
		if Message.FromHandle not in settings["botadmins"]: return
		if not len(parms):
			SendMessage('[*] Syntax: ADD <user name>')
		else:
			member = skype.User(parms.split()[0])
			Message.Chat.AddMembers(member)

	elif cmd in ( 'PROMOTE', 'DEMOTE', ):
		if Message.FromHandle not in settings["botadmins"]: return

		role = 'MASTER'
		if cmd == 'DEMOTE': role = 'USER'

		try:
			if not len(parms):
				SendMessage('/setrole %s %s' % (Message.FromHandle, role))
			elif len(parms.split()[0]):
				SendMessage('/setrole %s %s' % (parms.split()[0], role))
		except:
			pass

	elif cmd in ( 'ADDOP', ):
		if Message.FromHandle not in settings["botadmins"]: return
		if not len(parms):
			SendMessage('[*] Syntax: ADDOP <user name>')
		else:
			settings["botadmins"].append(parms.split()[0])
			cfgsave(settings)
			SendMessage('Added %s to bot admins.' % (parms.split()[0]))

	elif cmd in ( 'DELOP', ):
		if Message.FromHandle not in settings["botadmins"]: return
		if not len(parms):
			SendMessage('[*] Syntax: DELOP <user name>')
		else:
			settings["botadmins"].remove(parms.split()[0])
			cfgsave(settings)
			SendMessage('Removed %s from bot admins.' % (parms.split()[0]))

	elif cmd in ( 'LISTOPS', ):
		if Message.FromHandle not in settings["botadmins"]: return
		SendMessage('Bot Admins: %s' % (', '.join(settings["botadmins"])))

	elif cmd in ( 'DELCHAT', ):
		for member in Message.Chat.Members:
			if member.Handle == skype.CurrentUserHandle: continue
			Message.Chat.Kick(member.Handle)
		Message.Chat.Leave()
		# Message.Chat.Disband() # does not work 403 error
	
	elif cmd in ( 'ADDWORLD', ):
		if Message.FromHandle not in settings["botadmins"]: return
		if len(parms.split()) < 2:
			SendMessage('[*] Syntax: ADDWORLD <server> <name>')
		else:
			settings['urls'][parms.split()[1]] = ("http://%s.grepolis.com" % parms.split()[0])
			cfgsave(settings)
			SendMessage('World %s added with url %s' % (parms.split()[1], "http://%s.grepolis.com" % parms.split()[0]))

	elif cmd in ( 'DELWORLD', ):
		if Message.FromHandle not in settings["botadmins"]: return
		if len(parms.split()) < 1:
			SendMessage('[*] Syntax: DELWORLD <name>')
		else:
			if parms.split()[0] in settings['urls']:
				settings['urls'].pop(parms.split()[0], None)
				cfgsave(settings)
				SendMessage('Deleted world %s.' % (parms.split()[0]))

	elif cmd in ( 'LISTWORLDS', ):
		SendMessage('Worlds: %s' % ', '.join(settings['urls'].keys()))

	elif cmd in ( 'BOTSTATUS',  ):
		if not 'botstatus' in settings or not len(settings['botstatus']):
			bot_status = 'There are no updates at this time.'
		else:
			bot_status = settings['botstatus']
		
		SendMessage(bot_status) 

	elif cmd in ( 'SETSTATUS', ):
		if Message.FromHandle not in settings["botadmins"]: return
		if len(parms.split()) < 1:
			SendMessage('[*] Syntax: SETSTATUS <status>')
		else:
			today = datetime.date.today().strftime('%m/%d/%Y')
			print parms
			settings['botstatus'] = '%s: %s\r\n' % (today, parms)
			cfgsave(settings)
			SendMessage('Updated bot status.')

	elif cmd in ( 'BROADCAST',):  #### Need to fix this when no params are given it crashes. Add help as well.  Also need to fix chat room removal first.  Bot should cleanup chat rooms that do not have any monitors from its list.
		if Message.FromHandle not in settings["botadmins"]: SendMessage('Broadcast permission denied')
		elif Message.FromHandle in settings["botadmins"]:
			bcast = ' '.join(parms.split()[0:])
			SendMessage('Broadcasting this message to %s Chats: %s ' % (len(settings["monitor"]), bcast))
			for chat in settings["monitor"]:
				skype.Chat(chat).SendMessage(bcast)
				
	elif cmd in ( 'FEEDBACK', ):
			if "feedback" not in settings: settings["feedback"] = {}
			if len(parms.split()) < 1: SendMessage('Have a suggestion for a new command or feature? Let the BotMaster know using the feedback command.\r\n Example: >feedback Can we get a command that does ...')
			elif len(parms.split()) < 5: SendMessage('That\'s not very much to say, can you elaborate?')
			else:
				if Message.FromHandle not in settings["feedback"]: settings["feedback"][Message.FromHandle] = []
				
				if len(settings["feedback"][Message.FromHandle]) > 6 : SendMessage('Sorry %s, Too Many Feedback Messages submitted. Please try again later' % (Message.FromHandle))
				
				elif len(settings["feedback"][Message.FromHandle]) < 6 : 
					SendMessage('Thank you %s for your message it has been logged ' % (Message.FromHandle))
					settings["feedback"][Message.FromHandle].append(' '.join(parms.split()[0:]))
					cfgsave(settings)

	elif cmd in ('MONITORGHOST',):
		activeservers = getactiveservers()
		if len(parms.split()) < 2:
			SendMessage('[*] Syntax: MONITORGHOST <server> <ocean>')
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Inavlid or unsupported server')
		elif not parms.split()[1].isdigit() or int(parms.split()[1]) < 1 or int(parms.split()[1]) > 99:
			SendMessage('[*] Invalid ocean')
		else:
			server = parms.split()[0].lower()
			ocean = int(parms.split()[1])
			if server not in activeservers:
				getworlddata(server,settings['urls'][server],"all")
				townsize = changecheck(settings['urls'][server],"towns")
				if server not in settings["ghost_scrape"]: settings["ghost_scrape"][server] = []
				settings["ghost_scrape"][server] = ((townsize, int(time())))
			
			if Message.Chat.Name in settings["monitorghost"]:
				if server in settings["monitorghost"][Message.Chat.Name]:
					if ocean in settings["monitorghost"][Message.Chat.Name][server]:
						settings["monitorghost"][Message.Chat.Name][server].remove(ocean)
						SendMessage('[*] Monitor Disabled for this channel.')
					else:
						settings["monitorghost"][Message.Chat.Name][server].append(ocean)
						SendMessage('[*] Monitor Enabled for this channel. Repeat this command to disable.')
				else:
					settings["monitorghost"][Message.Chat.Name][server] = []
					settings["monitorghost"][Message.Chat.Name][server].append(ocean)

					SendMessage('[*] Monitor Enabled for this channel. Repeat this command to disable.')
			else:
				settings["monitorghost"][Message.Chat.Name] = {}
				settings["monitorghost"][Message.Chat.Name][server] = []
				settings["monitorghost"][Message.Chat.Name][server].append(ocean)

				SendMessage('[*] Monitor Enabled for this channel. Repeat this command to disable.')

			cfgsave(settings)

	elif cmd in ('MONITOR',):
		activeservers = getactiveservers()
		found = []
		if len(parms.split()) < 1:
			SendMessage('[*] Syntax: MONITOR <server> <alliance or player name>\r\n EXAMPLE: >monitor delta Disciples of Ares\r\nDescription: Adds an Alliance or Player to the DefBP and Conquest watch list for this chat room. Repeat same command to remove monitor.\r\nRelated Commands: monitorlist')
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid or unsupported server.')
		else:
			server = str(parms.split()[0].lower())
			if server not in activeservers: 		# if server is not in list of monitored servers, download world files.
				getworlddata(server,settings['urls'][server],"all")
				attsize = changecheck(settings['urls'][server],'player_kills_att')
				defsize = changecheck(settings['urls'][server],'player_kills_def')									
				consize = changecheck(settings['urls'][server],'conquers')
				if server not in settings["last_scrape"]: settings["last_scrape"][server] = []
				settings["last_scrape"][server] = ((attsize, defsize, consize, int(time())))
				if server not in settings["world_scrape"]: settings["world_scrape"][server] = []
				settings["world_scrape"][server] = ((int(time())))
				
			alliplayer = str(' '.join(parms.split()[1:]).lower().strip())
			if find_alliance(server, alliplayer): found = find_alliance(server, alliplayer)[0]			
			if found: pass
			elif find_player(server,alliplayer):
				found = find_player(server,alliplayer)[0]
			else:
				SendMessage('[*] Alliance or Player Not Found.')	
			if found: 
				if Message.Chat.Name in settings['monitor']:
					if server in settings['monitor'][Message.Chat.Name]:
						if found in settings['monitor'][Message.Chat.Name][server]:
							settings['monitor'][Message.Chat.Name][server].remove(found)
							SendMessage('[*] Monitor Disabled for this channel.')
						else:
							settings['monitor'][Message.Chat.Name][server].append(found)
							SendMessage('[*] Monitor Enabled for this channel. Repeat this command to disable.')		
					else:
						settings['monitor'][Message.Chat.Name][server] = []
						settings['monitor'][Message.Chat.Name][server].append(found)
						
						SendMessage('[*] Monitor Enabled for this channel. Repeat this command to disable.')	
				else:
					settings['monitor'][Message.Chat.Name] = {}
					settings['monitor'][Message.Chat.Name][server] = []
					settings['monitor'][Message.Chat.Name][server].append(found)
					SendMessage('[*] Monitor Enabled for this channel. Repeat this command to disable.')
			
			cfgsave(settings)
	elif cmd in ('MONITORLIST',):
		if len(parms.split()) == 1:
			if parms.split()[0].lower() == "help" or parms.split()[0].lower() == '?':
				SendMessage('[*] Syntax: MONITORLIST \r\nLists Alliances or Players being monitored for this chat.\r\nUse MONITOR command to add/remove')
		else:
			if Message.Chat.Name not in settings['monitor']:
				print("Not in Settings")
				SendMessage('No Alliances or Players currently monitored')
			elif len(settings['monitor'][Message.Chat.Name]) == 0:
				print(" LEngth was zero")
				SendMessage('No Alliances or Players currently monitored')
			else:
				out = []
				for server in settings['monitor'][Message.Chat.Name]:
					for id in settings['monitor'][Message.Chat.Name][server]:
						serverplayers = loadfile(server,"players")
						serveralliances = loadfile(server,"alliances")
						if len(out) == 0: out = 'Alliances/Players Monitored in this Chat\r\n'
						
						if id in serveralliances:  out = '%s		%s (%s)\r\n' %(out, serveralliances[id][0],server)
						
						if id in serverplayers:  out = '%s		%s (%s)\r\n' %(out, serverplayers[id][0],server)
				SendMessage(out)
			if Message.Chat.Name in settings['monitorghost'] and len(settings['monitorghost'][Message.Chat.Name]) > 0:
			  out = []
			  for server in settings['monitorghost'][Message.Chat.Name]:
			    for ocean in settings['monitorghost'][Message.Chat.Name][server]:
			      if len(out) == 0: out = 'Oceans Monitored in this Chat\r\n'
			      out = '%s    Ocean %s (%s)\r\n' % (out, ocean, server)
			  SendMessage(out)
				
	elif cmd in ('PLAYER',):
		bbcode = False
		if len(parms.split()) < 2:
				SendMessage('[*] Syntax: PLAYER <server> {bbcode} <player name/id>    **bbcode is optional\r\n Example: >player delta bbcode fortyfour \r\n Description: Returns players points, number of towns and rank')
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid or unsupported server')
		elif parms.split()[1] == 'bbcode': bbcode = True
		
		server = parms.split()[0].lower()
		if bbcode == True: player = find_player(server,' '.join(parms.split()[2:]))
		else: player = find_player(server,' '.join(parms.split()[1:]))
		if len(player) > 0:
			pid,pname,paid,points,rank,towns = player
			if player[2]:
				paname = alliance_name(server,paid)
				if bbcode == True: SendMessage('[*] [player]%s[/player] ([ally]%s[/ally]): %s points, %s town(s), rank %s' % (pname,paname,points,towns,rank))
				else:SendMessage('[*] %s (%s): %s points, %s town(s), rank %s' % (pname,paname,points,towns,rank))
			else:
				if bbcode == True: SendMessage('[*] [player]%s[/player]: %s points, %s town(s), rank %s' % (pname,points,towns,rank))
				else:SendMessage('[*] %s: %s points, %s town(s), rank %s' % (pname,points,towns,rank))
		else:
			SendMessage('[*] No match found for that player.')
	
	elif cmd in ('CONQUESTS',):
		__CONLIMIT__ = 60*60*24*2								#Set the max age of conquest we will return
		if len(parms.split()) < 2:
			SendMessage('[*] Syntax: CONQUESTS <server> <alliance name>\r\n EXAMPLE: >conquests delta Disciples of ares\r\n Description: Returns last 48 hours of conquests for given alliance')
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid or unsupported server')
		else:
			server = parms.split()[0].lower()
			alli_test = ' '.join(parms.split()[1:]).lower().strip()	
			found = find_alliance(server,alli_test)	
			if found:	
				alli_id,alli_name = found[0],found[1]				# set Alli ID and Alli name of the Alliance we are checking
				servertowns = loadfile(server,"towns")
				serverplayers = loadfile(server,"players")
				serveralliances = loadfile(server,"alliances")
				conquests = loadfile(server,"conquers")
				members = alliance_members(server,alli_id)			
				count = 0
				out = '[*] Conquests Involving %s in the last 48 hours [*]\r\n' % ( alli_name)
				for conquer in conquests["conquers"]:										# Look at each line in the conquests file
					
					town_id,c_time,winner,loser,winner_ally_id,loser_ally_id,town_points = conquer  #break them down into vars
					town_name = unquote_plus(servertowns[town_id][1])
					if int(c_time) + __CONLIMIT__ < int(time()): continue					# if the conquest is greater than 48 hours ago, move to the next one
					if winner in members:													#if the winner is in the alliance we are checking.....
						count += 1
						loser_name = serverplayers[loser][0] if loser in serverplayers else 'Ghost Town'
						if loser_ally_id: loser_ally_name = alliance_name(server, loser_ally_id)
						else: loser_ally_name = 'NO ALLIANCE' 
						if not loser_ally_name: loser_ally_name = 'NO ALLIANCE' 
						out = '%s    %s(%s) conquered %s (%s)\r\n' % (out,serverplayers[winner][0],alli_name,town_name,loser_name)
					if loser in members:
						count += 1
						winner_alli_name = alliance_name(server,winner_ally_id) if winner_ally_id else 'NO ALLIANCE'
						out='%s    %s (%s) was conquered by %s (%s)\r\n' % (out,town_name,serverplayers[loser][0],serverplayers[winner][0],winner_alli_name)
				out = '%s	[*] %s Conquests.' % (out, count)
				SendMessage(out)
						
			else:
				SendMessage('[*] Cannot initiate. Alliance id/name not found.')				

		
	elif cmd in ('TOWNS',):
		bbcode = False
		if len(parms.split()) < 2:
			SendMessage('[*] Syntax: TOWNS <server> {bbcode} <player name>   *bbcode is optional\r\n Example: >towns delta bbcode fortyfour\r\n Description: Returns town names, coordinates and points for a given player')
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid or unsupported server.')
		else:
			if parms.split()[1] == 'bbcode': bbcode = True
			server = parms.split()[0].lower()
			serverplayers = loadfile(server,"players")
			serveralliances = loadfile(server,"alliances")
			if bbcode == True: 
				player = find_player(server,' '.join(parms.split()[2:]))
			else:
				player = find_player(server,' '.join(parms.split()[1:]))	
			
			if len(player) > 0:
				pid,pname,paid,points,rank,cities = player
				paname = alliance_name(server,str(paid))
				towns = find_towns(server,pid)
				if bbcode == True:
					out = '[b]%d towns for[/b] [player]%s[/player] ([ally]%s[/ally]):\r\n' % (len(towns),pname,paname)
					out = '%s [table][**]Town[||]Island[||]Points[/**]' % (out)
					bracount = 11
				else: out = '[*] %d town(s) for %s (%s):\r\n' % (len(towns),pname,paname)	
				if bbcode == True: 
					for town in towns:
						if bracount >= 492: 
							out = ('%s [/table]\r\n**500 CHARACTER LIMIT CUT POST HERE***\r\n [table]'  %(out))	
							bracount = 0
						islandid = find_island(server,town[2],town[3])
						towninfo = '[*][town]%s[/town][|][island]%s[/island][|]%s[/*]' % (unquote_plus(str(town[1])),islandid,town[5])
						bracount +=8	
						out = '%s %s \r\n' %(out,towninfo)
				if bbcode == False:
					for n,town in enumerate(towns):
						towninfo = '%s (%sx%s) %s points' % (unquote_plus(town[1]),town[3],town[4],town[5])
						out = '{0}    {1:0>#{2}}: {3}\r\n'.format(out,n+1,len(str(len(towns))),towninfo)
				if bbcode == True: out = '%s [/table]' % (out)		
				SendMessage(out)
			else:
				SendMessage('[*] No match found for that player.')		
	
	
	elif cmd in ('TERRITORYLIMIT',):
		if parms == '':
			if Message.Chat.Name not in settings['territorylimit']: settings['territorylimit'][Message.Chat.Name] = 5
			territorylimit = settings['territorylimit'][Message.Chat.Name]
			SendMessage('[*] Current Territory Limit: %s%s' % (str(territorylimit) if territorylimit > 0 else 'ALL','%'))
		elif parms.isdigit() or parms.upper() == 'ALL':
			limit = int(parms) if parms.isdigit() else 0
			if limit > 100: limit = 100
			settings['territorylimit'][Message.Chat.Name] = limit
			SendMessage('[*] Territory Limit Updated: %d%s' % (settings['territorylimit'][Message.Chat.Name],'%'))
			cfgsave(settings)
		else:
			SendMessage('[*] Syntax: TERRITORYLIMIT <percent|ALL>')
	elif cmd in ('RANGELIMIT',):
		
		if parms == '':
			if Message.Chat.Name not in settings['rangelimit']: settings['rangelimit'][Message.Chat.Name] = 30
			rangelimit = settings['rangelimit'][Message.Chat.Name]
			SendMessage('[*] Current Range Limit: %s\r\n *Rangelimit used by TERRITORY command' % (str(rangelimit) if rangelimit > 0 else 'ALL',))
		elif parms.isdigit() or parms.upper() == 'ALL':
			limit = int(parms) if parms.isdigit() else 0
			if limit > 999: limit = 999
			settings['rangelimit'][Message.Chat.Name] = limit
			SendMessage('[*] Range Limit Updated: %d\r\n *Rangelimit used by TERRITORY command' % (settings['rangelimit'][Message.Chat.Name]))
			cfgsave(settings)
		else:
			SendMessage('[*] Syntax: RANGELIMIT <distance|ALL>')
	
	elif cmd in ('ISLANDS',):
		bbcode = False
		if len(parms.split()) < 2:
			SendMessage('[*] Syntax: ISLANDS <server> {bbcode} <player name>  *bbcode is optional\r\n EXAMPLE: >islands delta bbcode fortyfour\r\n Description: Groups players towns by islands')
			SendMessage('	')
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid server : %s' % (parms.split()[0]))
		elif parms.split()[1] == 'bbcode': bbcode = True
		
		server = parms.split()[0].lower()
		if bbcode == True: 
			player = find_player(server,' '.join(parms.split()[2:]))
		else:
			player = find_player(server,' '.join(parms.split()[1:]))	

		if len(player) > 0:
			
			pid,pname,paid,points,rank,towns = player
			paname = alliance_name(server,str(paid))
			towns = find_towns(server,pid)
			sorted_towns = sorted(towns, key=operator.itemgetter(5))
			out = '[*] %d town(s) for %s (%s):\r\n' % (len(towns),pname,paname)	
			if bbcode == True: 
				for n,town in enumerate(towns):
					towninfo = '[town]%s[/town] (%sx%s) %s points' % (unquote_plus(town[1]),town[2],town[3],town[5])
					out = '{0}    {1:0>#{2}}: {3}\r\n'.format(out,n+1,len(str(len(towns))),sorted_towns)
					bracount = 11
			else:
				for n,town in enumerate(towns):
					towninfo = '%s (%sx%s) %s points' % (unquote_plus(town[1]),town[2],town[3],town[5])
					out = '{0}    {1:0>#{2}}: {3}\r\n'.format(out,n+1,len(str(len(towns))),towninfo)
			SendMessage(out)
		else:
			SendMessage('[*] No match found for that player.')
	
	elif cmd in ('EASYMONEY',):
	
		if len(parms.split()) < 2 or not parms.split()[1].isdigit() or not parms.split()[2].isdigit():
			SendMessage('[*] Syntax: %s <server> <min town points> <max alliance points> [ocean]\r\n EXAMPLE: >easymoney delta 9000 500000 63\r\n Description: Returns towns of a certain point size from alliances of a certain point size for a certain ocean' % (cmd,))
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid or unsupported server')
		elif not parms.split()[3].lower().isdigit() or len(list(parms.split()[3].lower())) != 2: SendMessage('[*] Invalid Ocean Number')
		else:
			server = parms.split()[0].lower()
			ocean =  int(parms.split()[3])
			serverplayers = loadfile(server,"players")
			serveralliances = loadfile(server,"alliances")
			towns = loadfile(server,"towns")
			target_alliances = {}
			for alliance in serveralliances:
				if int(serveralliances[alliance][1]) <= int(parms.split()[2]):
					target_alliances[alliance] = serveralliances[alliance]
			members = {}
			target_towns = {}
			for town in towns:
				if int(towns[town][5]) >= int(parms.split()[1]) and towns[town][0] in serverplayers and serverplayers[towns[town][0]][1] in target_alliances:
					town_ocean = int('%s%s' % (str(towns[town][2][0]),str(towns[town][3][0])))
					if ocean > 0 and town_ocean != ocean: continue
					if serverplayers[towns[town][0]][1] not in target_towns: target_towns[serverplayers[towns[town][0]][1]] = []
					target_towns[serverplayers[towns[town][0]][1]].append(towns[town])
			alli_points = {}
			for alliance in target_towns: alli_points[alliance] = target_alliances[alliance][3]
			sorted_allis = sorted(alli_points.iteritems(),key=operator.itemgetter(1))
			out = '[*] %d alliance%s with <= %s points:\r\n' % (len(target_towns),'s' if len(target_towns) != 1 else '',parms.split()[2])
			for alliance_tuple in sorted_allis:
				alliance,alli_points = alliance_tuple
				out = '%s    %s town%s for alliance "%s" (%s points):\r\n' % (out,len(target_towns[alliance]),'s' if len(target_towns[alliance]) != 1 else '',target_alliances[alliance][0],target_alliances[alliance][1])
				town_points = {}
				for town in target_towns[alliance]: town_points[town] = town[5]
				sorted_towns = sorted(town_points.iteritems(),key=operator.itemgetter(1))
				sorted_towns.reverse()
				for n,town_tuple in enumerate(sorted_towns):
					town,points = town_tuple
					towninfo = '%s @ %sx%s (owner: %s) (points: %s)' % (unquote_plus(town[1]),town[2],town[3],serverplayers[town[0]][0],town[5])
					out = '{0}        {1:0>#{2}}: {3}\r\n'.format(out,n+1,len(str(len(sorted_towns))),towninfo)
			SendMessage(out)

	elif cmd in ('NEARGHOST',):
		
		if len(parms.split()) < 3 or len(parms.split()[1].lower().split('x')) != 2 or not parms.split()[1].split('x')[0].isdigit() or not parms.split()[1].split('x')[1].isdigit() or not parms.split()[2].isdigit() :
			SendMessage('[*] Syntax: NEARGHOST <server> <coords> <min points>\r\n Example >nearghost delta 604x384 5000\r\n Description: Returns list of Ghost Towns of certain points near a coordinate')
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid or unsupported server.')
		else:
			server = parms.split()[0].lower()
			x1,y1 = int(parms.split()[1].lower().split('x')[0]),int(parms.split()[1].lower().split('x')[1])
			mpoints = parms.split()[2]
			towns = loadfile(server, "towns")
			towndistance = {}
			for town in towns:
				if len(towns[town][0]) == 0:
					d =  math.sqrt((square(int(int(towns[town][2]) - x1))) + (square(int(int(towns[town][3]) - y1))))
					if d < 78 and int(towns[town][5]) > int(mpoints): towndistance[towns[town]] = d
			sorted_d = sorted(towndistance.iteritems(),key=operator.itemgetter(1))
			out = '[*] %d Ghost town(s) near %sx%s with points greater than %s:\r\n' % (len(sorted_d),x1,y1, mpoints)
			for n,town_tuple in enumerate(sorted_d):
				town,distance = town_tuple
				towninfo = '%s (%sx%s) (%s points) (%d away)' % (unquote_plus(town[1]),town[2],town[3],town[5],distance)
				out = '{0}   {1:0>#{2}}: {3}\r\n'.format(out,n+1,len(str(len(sorted_d))),towninfo)
			SendMessage(out)	

	elif cmd in ('LISTALLI',):
		bbcode = False
		if len(parms.split()) < 3:
			SendMessage('[*] Syntax: LISTALLI <server> {bbcode} <ocean[,ocean[,...]]> <alliance id/name>\r\nEXAMPLE: >listalli delta 73 Disciples of Ares\r\nDescription: Returns the towns for an alliiance in specific oceans')
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid or unsupported server.')
					
		else:
			server = parms.split()[0].lower()
			serverplayers = loadfile(server,"players")
			serveralliances = loadfile(server,"alliances")
			towns = loadfile(server, "towns")
			server = parms.split()[0].lower()
			if parms.split()[1] == 'bbcode': bbcode = True
			if bbcode:alli_test = ' '.join(parms.split()[3:]).lower().strip()
			else: alli_test = ' '.join(parms.split()[2:]).lower().strip()
			found = find_alliance(server,alli_test)
			if found:
				oceans = []
				out = ''
				alli_id,alli_name = found[0],found[1]
				members = {}
				for player in serverplayers:
					if serverplayers[player][1] == alli_id: members[player] = serverplayers[player]
				for ocean in parms.split()[2].split(',') if bbcode else parms.split()[1].split(',') :
					if ocean.isdigit():
						ocean_members = []
						for town in towns:
							if towns[town][0] in members and members[towns[town][0]] not in ocean_members and '%s%s' % (towns[town][2][0],towns[town][3][0]) == ocean:
								ocean_members.append(members[towns[town][0]])
						ocean_members = sorted(ocean_members,key=lambda x: x[4],reverse=True)
						if  bbcode: out = '%s[b]%d %s member%s in ocean %s:[b]\r\n' % (out+'\r\n' if out else '',len(ocean_members),alli_name,'s' if len(ocean_members) != 1 else '',ocean)						
						else: out = '%s%d %s member%s in ocean %s:\r\n' % (out+'\r\n' if out else '',len(ocean_members),alli_name,'s' if len(ocean_members) != 1 else '',ocean)
						for n,member in enumerate(ocean_members):
							if bbcode:
								memberinfo = '[player]%s[/player] (%s points) (%s town%s) (rank %s)' % (member[0],member[2],member[4],'' if member[4] == 1 else 's',member[3])
								out = '{0}    {1:0>#{2}}: {3}\r\n'.format(out,n+1,len(str(len(ocean_members))),memberinfo)
							else:
								memberinfo = '%s (%s points) (%s town%s) (rank %s)' % (member[0],member[2],member[4],'' if member[4] == 1 else 's',member[3])
								out = '{0}    {1:0>#{2}}: {3}\r\n'.format(out,n+1,len(str(len(ocean_members))),memberinfo)
				SendMessage(out)
			else:
				SendMessage('[*] Alliance name/id not found.')
				
	elif cmd in ('NEARPLAYER',):
		if len(parms.split()) < 3 or len(parms.split()[1].lower().split('x')) != 2 or not parms.split()[1].lower().split('x')[0].isdigit() or not parms.split()[1].lower().split('x')[1].isdigit():
			SendMessage('[*] Syntax: NEARPLAYER <server> <coords> <player>\r\n Example: NEARPLAYER delta 604x384 fortyfour\r\n Description: Returns the towns of a player nearest to coordinates')
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid or unsupported server.')
		else:
			server = parms.split()[0].lower()
			player = find_player(server,' '.join(parms.split()[2:]))
			x1,y1 = int(parms.split()[1].lower().split('x')[0]),int(parms.split()[1].lower().split('x')[1])
			if len(player) > 0:
				pid,pname,paid,points,rank,towns = player
				paname = alliance_name(server,str(paid))
				towns = find_towns(server,pid)	
				towndistance = {}
				for town in towns:
					d =  math.sqrt((square(int(town[2]) - int(x1))) + (square(int(town[3]) - int(y1))))
					towndistance[town] = d
				sorted_d = sorted(towndistance.iteritems(),key=operator.itemgetter(1))
				out = '[*] %s town(s) for %s (%s):\r\n' % (len(towns),pname,paname)
				for n,town_tuple in enumerate(sorted_d):
					town,distance = town_tuple
					towninfo = '%s (%sx%s => %s) (%d away)' % (unquote_plus(town[1]),town[2],town[3],parms.split()[1].lower(),distance)
					out = '{0}    {1:0>#{2}}: {3}\r\n'.format(out,n+1,len(str(len(towns))),towninfo)
				SendMessage(out)
			else:
				SendMessage('[*] No match found for that player.')				
				
				
	elif cmd in ('NEARALLI',):
		bbcode = False
		clear = True
		
		if len(parms.split()) < 3:
			SendMessage('[*] Syntax: NEARALLI <server> {bbcode} <coords> <point limit> <alliance>    **bbcode is optional\r\nExample: >nearalli delta bbcode 624x298 100000 The Forgotten Pheonix\r\n Description: Returns the towns of a certain size for alliances nearest a coordinate.')

			clear = False
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid or unsupported server.')
			clear = False
		elif parms.split()[1] == 'bbcode':bbcode = True
		
		elif bbcode == True:
			if len(parms.split()) < 4 or len(parms.split()[2].lower().split('x')) != 2 or not parms.split()[2].lower().split('x')[0].isdigit() or len(parms.split()[2].lower().split('x')[0]) != 3 or len(parms.split()[2].lower().split('x')[1]) != 3 or not parms.split()[2].lower().split('x')[1].isdigit() or not parms.split()[3]:
				SendMessage('1[*] Syntax: NEARALLI <server> {bbcode} <coords> <point limit> <alliance>    **bbcode is optional')
				SendMessage('	Example: >nearalli delta bbcode 624x298 100000 The Forgotten Pheonix')
				clear = False
		elif bbcode == False:	
			if len(parms.split()) < 3 or len(parms.split()[1].lower().split('x')) != 2 or not parms.split()[1].lower().split('x')[0].isdigit() or len(parms.split()[1].lower().split('x')[0]) != 3 or len(parms.split()[1].lower().split('x')[1]) != 3 or not parms.split()[1].lower().split('x')[1].isdigit() or not parms.split()[2].isdigit():
				SendMessage('1[*] Syntax: NEARALLI <server> {bbcode} <coords> <point limit> <alliance>    **bbcode is optional')
				SendMessage('	Example: >nearalli delta 624x298 100000 The Forgotten Pheonix')
				clear = False
		
		if clear == True:	
			server = parms.split()[0].lower()
			
			if bbcode == True: x1,y1 = int(parms.split()[2].lower().split('x')[0]),int(parms.split()[2].lower().split('x')[1])
			else: x1,y1 = int(parms.split()[1].lower().split('x')[0]),int(parms.split()[1].lower().split('x')[1])
			if bbcode == True: alli_test = ' '.join(parms.split()[4:]).lower().strip()
			else: alli_test = ' '.join(parms.split()[3:]).lower().strip()
			found = find_alliance(server,alli_test)
			
			if len(found) > 0:
				if Message.Chat.Name not in settings['rangelimit']: settings['rangelimit'][Message.Chat.Name] = 30
				limit = settings['rangelimit'][Message.Chat.Name]
				alli_id,alli_name = found[0],found[1]
				towns = loadfile(server, "towns")
				players = loadfile(server, "players")
				# alliances = loadfile(server, "alliances")
				members = alliance_members(server, alli_id)
				allitowns = []
				for town in towns:
					if bbcode == True: 
						if towns[town][0] in members and int(towns[town][5]) >= int(parms.split()[3]):
							allitowns.append(towns[town])
					else: 
						if towns[town][0] in members and int(towns[town][5]) >= int(parms.split()[2]):
							allitowns.append(towns[town])
				towndistance = {}
				for town in allitowns:
					d =  int(math.sqrt((square(int(town[2]) - int(x1))) + (square(int(town[3]) - int(y1)))))
					if d <= limit or limit == 0: towndistance[town] = d
				sorted_d = sorted(towndistance.iteritems(),key=operator.itemgetter(1))
				if bbcode == True: out = '[*] %d town%s (>=%s points) for [ally]%s[/ally] (Range: %s):\r\n' % (len(towndistance),'' if len(towndistance) == 1 else 's',parms.split()[3],alliance_name(server, alli_id),'ALL' if limit == 0 else str(limit))
				else: out = '[*] %d town%s (>=%s points) for %s (Range: %s):\r\n' % (len(towndistance),'' if len(towndistance) == 1 else 's',parms.split()[2],alliance_name(server, alli_id),'ALL' if limit == 0 else str(limit))
				
				if bbcode == True:
					for n,town_tuple in enumerate(sorted_d):
						town,distance = town_tuple
						towninfo = '([player]%s[/player]) [town]%s[/town] @ %sx%s (%s points) (%s away)' % (players[town[0]][0],unquote_plus(town[1]),town[2],town[3],town[5],distance)
						out = '{0}    {1:0>#{2}}: {3}\r\n'.format(out,n+1,len(str(len(towndistance))),towninfo)
				else:
					for n,town_tuple in enumerate(sorted_d):
						town,distance = town_tuple
						towninfo = '(%s) %s @ %sx%s (%s points) (%s away)' % (players[town[0]][0],unquote_plus(town[1]),town[2],town[3],town[5],distance)
						out = '{0}    {1:0>#{2}}: {3}\r\n'.format(out,n+1,len(str(len(towndistance))),towninfo)
								
				SendMessage(out)	
			else:
				SendMessage('[*] Cannot initiate. Alliance name not found.')		
	
	elif cmd in ('TERRITORY',):

		if len(parms.split()) < 2:
			SendMessage('[*] Syntax: TERRITORY <server> <alliance id/name>\r\n EXAMPLE: >territory delta Disciples of Ares\r\n Description: Returns a breakdown of oceans an alliance resides in')
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid or unsupported server.')
		else:
			server = parms.split()[0].lower()
			alli_test = ' '.join(parms.split()[1:]).lower().strip()
			found = find_alliance(server,alli_test)
			#if len(found) > 1:
			#	print('TERRITORY command returned %d results.' % (len(found),))
			if found:
				#if Message.Chat.Name not in settings['rangelimit']: settings['rangelimit'][Message.Chat.Name] = 30
				#limit = settings['rangelimit'][Message.Chat.Name]
				alli_id,alli_name = found[0],found[1]
				members = alliance_members(server,alli_id)
				oceans = {}
				towns = loadfile(server, "towns")
				# town_db = {}
				for town in towns:
					if towns[town][0] not in members: continue
					x,y,points = towns[town][2],towns[town][3],towns[town][5]
					ocean = '%s%s' % (x[0],y[0])
					if ocean not in oceans:
						oceans[ocean] = {}
						oceans[ocean]['points'] = 0
						oceans[ocean]['towns'] = 0
					if points.isdigit():
						oceans[ocean]['points'] += int(points)
						oceans[ocean]['towns'] += 1
				total = 0
				sortlist = []
				for ocean in oceans:
					total += oceans[ocean]['points']
					sortlist.append((oceans[ocean]['points'],ocean))
				sortlist.sort()
				sortlist.reverse()
				out = '[*] Territory Summary for %s (%d points)\r\n' % (alli_name,total)
				for points,ocean in sortlist:
					percent = round((float(points)/float(total))*100.0,2)
					#if int(percent) < limit: continue
					out = '%s    Ocean %s: %d points (%s%s) %d town%s\r\n' % (out,ocean,points,str(percent),'%',oceans[ocean]['towns'],'' if oceans[ocean]['towns'] == 1 else 's')
				SendMessage(out)
			else:
				SendMessage('[*] Cannot initiate. Alliance id/name not found.')	
		
				
	elif cmd in ('TOPRANK',):
		bbcode = False
		if len(parms.split()) < 3:
			SendMessage('[*] Syntax: toprank <server> {bbcode} <limit> <Alliance id>  *bbcode is optional\r\n EXAMPLE: >toprank delta 20 disciples of ares\r\n Description: Returns the X amount top Defenders, Attackers and Fighters for a specific alliance ')
		elif parms.split()[0].lower() not in settings['urls']:
			SendMessage('[*] Invalid or unsupported server')
		elif parms.split()[1].lower() == 'bbcode' and not parms.split()[2].lower().isdigit():
			SendMessage('[*] No Limit Specified. Need a max player limit to return')
		elif parms.split()[1].lower() != 'bbcode' and not parms.split()[1].isdigit():
			SendMessage('[*] No Limit Specified. Need a max player limit to return')
		else:
			server = parms.split()[0].lower()
			if parms.split()[1] == 'bbcode': bbcode = True
			if bbcode == True: 
				alli_test = ' '.join(parms.split()[3:]).lower().strip()
				limit = parms.split()[2]
			else:
				alli_test = ' '.join(parms.split()[2:]).lower().strip()
				limit = parms.split()[1]
			found = find_alliance(server,alli_test)
			if found:
				alli_id,alli_name = found[0],found[1]
				amembers = alliance_members(server,alli_id)
				players = loadfile(server, "players")
				defranks = loadfile(server, "player_kills_def")
				attranks = loadfile(server, "player_kills_att")
				atkmembers = {}
				defmembers = {}
				for player in defranks:
					if player in amembers: defmembers[player] = int(defranks[player])
					
				if bbcode == True: 
					out = '[b]Top Defenders for [u][ally]%s[/ally][/u][/b]\r\n' % (alli_name)
				else:
					out = 'Top Defenders for %s\r\n' % (alli_name)
				sorted_d = sorted(defmembers.iteritems(), key=operator.itemgetter(1))	
				sorted_d.reverse()
				for n,dplayer in enumerate(sorted_d[0:int(limit)]):
					if bbcode == True: 
						rankinfo = ') [player]%s[/player] - [i]%s[/i]' % (players[dplayer[0]][0],dplayer[1])
					else:
						rankinfo = ') %s - %s' % (players[dplayer[0]][0],dplayer[1])
					out = '{0}\t\t\t\t{1}{2}\r\n'.format(out,n+1,rankinfo)

				for player in attranks:
					if player in amembers: atkmembers[player] = int(attranks[player])
				if bbcode == True: 
					out = '%s [b]Top Attackers for [u][ally]%s[/ally][/u][/b]\r\n' % (out, alli_name)
				else:
					out = '%s Top Attackers for %s\r\n' % (out, alli_name)
				sorted_a = sorted(atkmembers.iteritems(), key=operator.itemgetter(1))	
				sorted_a.reverse()
				for n,player in enumerate(sorted_a[0:int(limit)]):				
					if bbcode == True: 
						rankinfo = ') [player]%s[/player] - [i]%s[/i]' % (players[player[0]][0],player[1])
					else:
						rankinfo = ') %s - %s' % (players[player[0]][0],player[1])
					out = '{0}\t\t\t\t{1}{2}\r\n'.format(out,n+1,rankinfo)
				member_data = {}
				for player in amembers:
					if player not in attranks:continue 
					if player not in defranks:continue
					member_data[player] = (int(defranks[player]) + int(attranks[player]))				
				sorted_x = sorted(member_data.iteritems(), key=operator.itemgetter(1))	
				sorted_x.reverse()
				if bbcode == True:out = '%s [b]Top Fighters for [u][ally]%s[/ally][/u][/b]\r\n' % (out, alli_name)
				else: out = '%s Top Fighters for %s\r\n' % (out, alli_name)
				for n,player in enumerate(sorted_x[0:int(limit)]):
					if bbcode == True:rankinfo = ') [player]%s[/player] - [i]%s[/i]' % (players[player[0]][0],player[1])
					else: rankinfo = ') %s - %s' % (players[player[0]][0],player[1])
					out = '{0}\t\t\t\t{1}{2}\r\n'.format(out,n+1,rankinfo)
				SendMessage(out)
			else: SendMessage(" Unable to find alliance %s" % (alli_test))
	
	elif cmd in ('BOTSTATS',):
		alliplays = []
		contacts = skype.Friends.Count
		chats = len(settings['monitor'])
		chats = chats + len(settings['monitorghost'])
		servers = len(getactiveservers())
		oceans = 0
		for chat in settings['monitor']:
			for server in settings['monitor'][chat]:
				for item in settings['monitor'][chat][server]:
					if len(item) > 0 and item not in alliplays: alliplays.append(item)
		for chat in settings['monitorghost']:
			for server in settings['monitorghost'][chat]:
				oceans += len(server)
		SendMessage('I have %s contacts and am in %s active chat rooms monitoring %s alliances and players, and %s oceans on %s Grepolis servers.' % (contacts, chats, len(alliplays), oceans, servers))


	
	else:
		SendMessage('Unrecognized command: %s' % (cmd))

def main():
	global settings
	activeservers = []
	settings = cfgcheck()
	skype.Attach()
	print('Skype attached.')
	print(skype.CurrentUser.FullName)
	skype.OnMessageStatus = message_status
	nextscrape = 0
	worldfilecheck = 0
	allimembercheck = 0
	attcheck = False
	defcheck = False
	concheck = False
	towncheck = False
	delchat = []
	
	if 'urls' not in settings:
		settings['urls'] = __URLS__
		cfgsave(settings)
	
	while True:
		if nextscrape <= int(time()): 		##Is it time to check for updated world defbp and conq files?
			dout = []
			cout = []
			print ("[%s] Starting Monitor Check" % (ctime()))
			activeservers = getactiveservers()

			for server in activeservers:														#Check server by server....
				print("[%s] - %s" % (ctime(),server))
				servertowns = loadfile(server,"towns")
				serverplayers = loadfile(server,"players")
				serveralliances = loadfile(server,"alliances")
				attsize = changecheck(settings['urls'][server],'player_kills_att')
				defsize = changecheck(settings['urls'][server],'player_kills_def')									#get the current size of the file on the grepolis server.
				consize = changecheck(settings['urls'][server],'conquers')									#get the current size of the file on the grepolis server.
				
				if not server in settings["ghost_scrape"]: settings["ghost_scrape"][server] = [0,int(time())]
				if server in settings["ghost_scrape"]:
					townsize = changecheck(settings['urls'][server],'towns')
					if townsize != settings["ghost_scrape"][server][0]:
						towncheck = True
					if towncheck:
						checklist = {}
						currtowns = loadfile(server,"towns")
						getworlddata(server,settings['urls'][server],"towns")
						newtowns = loadfile(server,"towns")
						for chat in settings["monitorghost"]:
							try:
								if skype.Chat(chat).MyStatus != "SUBSCRIBED":
									if chat not in delchat:
										print("Adding Chat %s to delete list because of Status: %s" % (skype.Chat(chat).FriendlyName, skype.Chat(chat).MyStatus))
										delchat.append(chat)
									continue
							except Exception:
								pass
							if chat not in checklist:
								checklist[chat] = []
							if server not in settings["monitorghost"][chat]: continue
							for item in settings["monitorghost"][chat][server]:
								checklist[chat].append(item)

						for chat in checklist:
							toutlist = {}
							toutlist[chat] = {}
							toutlist[chat]["towns"] = {}

							for ocean in checklist[chat]:
								if not ocean in toutlist[chat]["towns"]: toutlist[chat]["towns"][ocean] = []
								playertowns = player_towns_by_ocean(currtowns,ocean)
								ghosttowns = ghosts_by_ocean(newtowns,ocean)
								for id in ghosttowns:
									ghost = ghosttowns[id]
									if id in playertowns:
										playertown = playertowns[id]
										if playertown[0] in serverplayers:
											player = serverplayers[playertown[0]][0]
										else: player = 'Unknown'
										ghostocean = int('%s%s' % (str(ghost[2][0]),str(ghost[3][0])))
										# toutlist[chat]["towns"][ghostocean].append('%s (%s) -> %s (%s) %s pts' % (unquote_plus(ghost[1]),player[0],unquote_plus(ghost[1]),'Ghost',ghost[5]))
										toutlist[chat]["towns"][ghostocean].append('%s (%s) -> %s (%s) [town]%s[/town] %s pts' % (unquote_plus(ghost[1]),player,unquote_plus(ghost[1]),'Ghost',id,ghost[5]))

							if toutlist[chat]["towns"]:
								tout = []
								for chat in toutlist:
									for ocean in toutlist[chat]["towns"]:
										if len(toutlist[chat]["towns"][ocean]) == 0: continue
										if len(tout) == 0: 
											tout = unicode('(tumbleweed) Ghost Alerts!\r\n')
										tout = '%s    Ocean %s (%s)\r\n' % (tout,ocean,server)

										for alert in toutlist[chat]["towns"][ocean]:
											if len(tout) == 0: 
												tout = unicode('(tumbleweed) Ghost Alerts!\r\n')
												tout = '%s    Ocean %s (%s)\r\n' % (tout,ocean,server)

											tout = '%s        %s\r\n' % (tout,alert,)

											if len(tout) > 6000:
												try:
													newchat = skype.Chat(chat)
													newchat.SendMessage(tout)
													tout = []
												except Exception:
													print('unable to send message to %s' % (skype.Chat))
								if len(tout) > 0:
									try:
										newchat = skype.Chat(chat)
										newchat.SendMessage(tout)
									except Exception:
										print('unable to send message to %s' % (skype.Chat))
					towncheck = False
					settings["ghost_scrape"][server] = ((townsize,int(time())))

				if not server in settings["last_scrape"]: settings["last_scrape"][server] = [0,0,int(time())]
				if attsize != settings["last_scrape"][server][0]:
					attcheck = True

				if defsize != settings["last_scrape"][server][1]: 
					defcheck = True
					#print ("[%s] Found updated Def file for %s" % (ctime(), server)) #Remarked to save console window space
				
				if consize != settings["last_scrape"][server][2]: 
					concheck = True
					#print ("[%s] Found updated Conquest file for %s" % (ctime(), server)) #Remarked to save console window space
				
				if defcheck or concheck or attcheck:
					checklist = {}
					if attcheck:

						acurrstats = loadfile(server,"player_kills_att")
						getworlddata(server,settings['urls'][server],"player_kills_att")
						anewstats = loadfile(server,"player_kills_att")
					if defcheck: 
						
						dcurrstats = loadfile(server,"player_kills_def")																	#load the current file into mem before download
						getworlddata(server,settings['urls'][server],"player_kills_def")															#download file from server
						dnewstats = loadfile(server,"player_kills_def")																	#load updated file into memory
					if concheck:
						
						ccurrstats = loadfile(server,"conquers")
						getworlddata(server,settings['urls'][server],"conquers")
						cnewstats = loadfile(server,"conquers")
						delta = list(set(cnewstats["conquers"]) - set(ccurrstats["conquers"]))
																												#clear out our checklist
					for chat in settings["monitor"]:
						
						try:
							if skype.Chat(chat).MyStatus != "SUBSCRIBED": 
								if chat not in delchat: 
									print("Adding Chat %s to delete list because of Status: %s" % (skype.Chat(chat).FriendlyName, skype.Chat(chat).MyStatus))
									delchat.append(chat)							
								continue
						except Exception:
							pass
							#print (("Unable to do things with chat %s ") % (chat))   ####FIX THIS WE HAVE A big list of chats here.
						if chat not in checklist: 
							checklist[chat] = []										#Add chat to temp checklist only once... i know lame.
						if server not in settings["monitor"][chat]: continue
						for item in settings["monitor"][chat][server]: 
							checklist[chat].append(item)								#if alliance or player is on server being checked, add them to list
					
					for chat in checklist:
						player2check = []
						aoutlist = {}
						doutlist = {}
						coutlist = {}
						alli2check = {}
						aoutlist[chat] = {}
						aoutlist[chat]["alliances"] = {}
						aoutlist[chat]["players"] = []
						doutlist[chat] = {}
						doutlist[chat]["alliances"] = {}
						doutlist[chat]["players"] = []
						coutlist[chat] = {}
						coutlist[chat]["alliances"] = {}
						coutlist[chat]["players"] = []
						
						for id in checklist[chat]:
							if id in serverplayers: 
								player2check.append(id)
							elif id in serveralliances: 
								alli2check[id] = alliance_members(server,str(id))
							#else: print("%s not found in alliances or players list for %s" % (id, server))### NEED TO ADD STATEMENT TO DROP ID from settings
							
						if alli2check:
							for alliance in alli2check:
								if not alliance in aoutlist[chat]["alliances"]: aoutlist[chat]["alliances"][alliance] = []
								if not alliance in doutlist[chat]["alliances"]: doutlist[chat]["alliances"][alliance] = []
								if not alliance in coutlist[chat]["alliances"]: coutlist[chat]["alliances"][alliance] = []
								for member in alli2check[alliance]:
									if attcheck:
										if member not in anewstats: continue
										if member not in acurrstats: continue
										if acurrstats[member] != anewstats[member]:
											aoutlist[chat]["alliances"][alliance].append('%s: %s(+%s)' % (serverplayers[member][0], anewstats[member], (int(anewstats[member]) - int(acurrstats[member]))))
									if defcheck:
										if member not in dnewstats: continue
										if member not in dcurrstats: continue
										if dcurrstats[member] != dnewstats[member]:
											doutlist[chat]["alliances"][alliance].append('%s: %s(+%s)' % (serverplayers[member][0], dnewstats[member], (int(dnewstats[member]) - int(dcurrstats[member]))))
									if concheck:
										for conquest in delta:
											# if conquest[4] == conquest[5]:			COME BACK TO THIS, TRYING TO SUPRESS MULTIPLE ENTRIES FOR INTRA ALLIANCE CONQUER
												# player_name = serverplayers[conquest[3]][0]			#otherwise get the players name
												# alli_name = alliance_name(server,conquest[5])			#Assign players alliance name
												# coutlist[chat]["alliances"][alliance].append('+%s(%s) conquered %s (%s)' % (serverplayers[conquest[2]][0],alliance_name(server,str(conquest[4])),player_name,alli_name))
												# continue
											if member == conquest[2]:					# Does this Alliance member match the victor?
												if not conquest[3]: player_name = "Ghost"				# Assign Ghost if player does not exist anymore
												else:
													player_name = serverplayers[conquest[3]][0]			#otherwise get the players name
												town_name = unquote_plus(servertowns[conquest[0]][1])
												coutlist[chat]["alliances"][alliance].append('%s(%s) conquered %s (%s)' % (serverplayers[conquest[2]][0],alliance_name(server,str(conquest[4])),town_name,player_name))
											if member == conquest[3]:
												town_name = unquote_plus(servertowns[conquest[0]][1])
												coutlist[chat]["alliances"][alliance].append('%s (%s) was conquered by %s (%s)' % (town_name,serverplayers[conquest[3]][0],serverplayers[conquest[2]][0],alliance_name(server,str(conquest[4]))))
									
					
						if player2check:
							doutlist[chat]["players"] = []
							for player in player2check:
								if attcheck:
									if str(player) not in acurrstats or anewstats: continue
									if acurrstats[str(player)] != anewstats[str(player)]:
										aoutlist[chat]["players"].append('%s: %d(+%s)' % (serverplayers[player][0], int(anewstats[player]), (int(anewstats[player]) - int(acurrstats[player]))))
								if defcheck:
									if str(player) not in dcurrstats or dnewstats: continue
									if dcurrstats[str(player)] != dnewstats[str(player)]:
										doutlist[chat]["players"].append('%s: %d(+%s)' % (serverplayers[player][0], int(dnewstats[player]), (int(dnewstats[player]) - int(dcurrstats[player]))))
								if concheck:
									for conquest in delta:
										if player == conquest[2]: 
											if not conquest[3]: player_name = "Ghost"
											else: player_name = serverplayers[conquest[3]][0]
											town_name = unquote_plus(servertowns[conquest[0]][1])
											coutlist[chat]["players"].append('%s(%s) conquered %s (%s)' % (serverplayers[conquest[2]][0],alliance_name(server,str(conquest[4])),town_name,player_name))
										if player == conquest[3]: coutlist[chat]["players"].append('%s (%s) was conquered by %s (%s)' % (town_name,serverplayers[conquest[3]][0],serverplayers[conquest[2]][0],alliance_name(server,str(conquest[4]))))
								
						if aoutlist[chat]["alliances"] or aoutlist[chat]["players"]:
						
							aout = []
							for chat in aoutlist:
								for alliance in aoutlist[chat]["alliances"]:
									if len(aoutlist[chat]["alliances"][alliance]) == 0:continue
									if len(aout) == 0: aout = unicode('(punch) ABP Alerts!\r\n')
									aout = '%s    %s (%s):\r\n' % (aout, alliance_name(server,str(alliance)),server)
									
									for alert in aoutlist[chat]["alliances"][alliance]:
										aout = '%s        %s\r\n' % (aout,alert,)
								for player in aoutlist[chat]["players"]:
									if len(aoutlist[chat]["players"]) == 0:continue
									if len(aout) == 0: aout = unicode('(punch) ABP Alerts!\r\n')
									#for alert in doutlist[chat]["players"]:
									aout = '%s        %s\r\n' % (aout,player,)	
										
								if len(aout) > 0:
									try:
										newchat = skype.Chat(chat)
										newchat.SendMessage(aout)
									except Exception:
										print ('unable to send message to %s' % (skype.Chat))			
								
						if doutlist[chat]["alliances"] or doutlist[chat]["players"]:
						
							dout = []
							for chat in doutlist:
								for alliance in doutlist[chat]["alliances"]:
									if len(doutlist[chat]["alliances"][alliance]) == 0:continue
									if len(dout) == 0: dout = unicode('(ninja) DBP Alerts!\r\n')
									dout = '%s    %s (%s):\r\n' % (dout, alliance_name(server,str(alliance)),server)
									
									for alert in doutlist[chat]["alliances"][alliance]:
										dout = '%s        %s\r\n' % (dout,alert,)
								for player in doutlist[chat]["players"]:
									if len(doutlist[chat]["players"]) == 0:continue
									if len(dout) == 0: dout = unicode('(ninja) DBP Alerts!\r\n')
									#for alert in doutlist[chat]["players"]:
									dout = '%s        %s\r\n' % (dout,player,)	
										
								if len(dout) > 0:
									try:
										newchat = skype.Chat(chat)
										newchat.SendMessage(dout)
									except Exception:
										print ('unable to send message to %s' % (skype.Chat))
									
						if coutlist[chat]["alliances"] or coutlist[chat]["players"]:
							cout = []
							for chat in coutlist:
								
								for alliance in coutlist[chat]["alliances"]:
									if len(coutlist[chat]["alliances"][alliance]) == 0: continue
									if len(cout) == 0: cout = unicode('(bandit) Conquest Alerts!\r\n')
									if len(coutlist[chat]["alliances"][alliance]) == 1: cout = '%s    1 Conquest by %s\r\n' % (cout, alliance_name(server,str(alliance)))
									else: cout = '%s    %s Conquests by %s (%s)\r\n' % (cout, len(coutlist[chat]["alliances"][alliance]),alliance_name(server,str(alliance)),server)

									for alert in coutlist[chat]["alliances"][alliance]:
										cout = '%s        %s\r\n' % (cout,alert,)
								
								for player in coutlist[chat]["players"]:
									if len(coutlist[chat]["players"]) == 0: continue
									if len(cout) == 0: cout = unicode(' (bandit) Conquest Alerts!\r\n')
									for alert in coutlist[chat]["players"]:
										cout = '%s        %s\r\n' % (cout,alert,)				
										
								if len(cout) > 0:
									try:
										newchat = skype.Chat(chat)
										newchat.SendMessage(cout)
									except Exception:
										print ('unable to send message to %s' % (skype.Chat))
					
					attcheck = False
					defcheck = False
					concheck = False
					settings["last_scrape"][server] = ((attsize, defsize, consize, int(time())))
					
					
				
				#else: print("No Updated World Files Found")
				if delchat: 
						for chat in delchat:
							print ("Deleting Chatroom %s from Monitor because no longer subscribed" % (skype.Chat(chat).FriendlyName))
							del settings["monitor"][chat]
				cfgsave(settings)
				delchat = []
			print ("[%s] Check Complete" % (ctime()))
			nextscrape = int(time()) + (60*5)		
		
		if worldfilecheck <= int(time()):
			print (" [%s] Begining World File Check" % (ctime()))
			#for server in settings["world_scrape"]:
			for server in getactiveservers():
				#print ("[WORLDFILECHECK][%s][%s]: Checking if %s is less than or equal to now" % (ctime(),server, settings["world_scrape"][server]))
				if server not in settings["world_scrape"]: settings["world_scrape"][server] = (int(time()) + (60 * 60 * 2))
				if settings["world_scrape"][server] <= int(time()):
					print ("Scraping world files for %s" % (server))
					try:
						getworlddata(server,settings['urls'][server],"all")
					except Exception:
						print ('unable to get world files for %s' % (server))
					settings["world_scrape"][server] = (int(time()) + (60 * 60 * 2))
					cfgsave(settings)
			print (" [%s] World File Check Complete" % (ctime()))
			worldfilecheck = int(time()) + (60 * 20)
		
		if allimembercheck <= int(time()):
			print("[%s] Beginning Alliance Member Check" % (ctime()))
			activeservers = getactiveservers()
			for server in activeservers:
				print("%s - %s" % (ctime(),server))
				serverplayers = loadfile(server,"players")
				serveralliances = loadfile(server,"alliances")
				alliances = {}
				newalliances = {}
				for player in serverplayers:
					if not serverplayers[player][1]: continue
					if not serverplayers[player][1] in alliances: alliances[serverplayers[player][1]] = [] 
					alliances[serverplayers[player][1]].append(player)
				getworlddata(server,settings['urls'][server],"players")
				newserverplayers = loadfile(server,"players")
				for player in newserverplayers:
					
					if not newserverplayers[player][1]: continue
					if not newserverplayers[player][1] in newalliances: newalliances[newserverplayers[player][1]] = [] 
					newalliances[newserverplayers[player][1]].append(player)
					
				
				for chat in settings["monitor"]:
					try:
						if skype.Chat(chat).MyStatus != "SUBSCRIBED": 
							if chat not in delchat:
								print("Adding Chat %s to delete list because of Status: %s" % (skype.Chat(chat).FriendlyName, skype.Chat(chat).MyStatus))
								delchat.append(chat)
							continue
					except Exception:
							pass
							#print (("Unable to do things with chat %s ") % (chat))
					if server in settings["monitor"][chat]:
						for entry in settings["monitor"][chat][server]:
							
							out = []
							if entry in newalliances:
								remdelta = set(alliances[entry]).difference(newalliances[entry])
								adddelta = set(newalliances[entry]).difference(alliances[entry])

								if len(remdelta) >0 or len(adddelta) >0:
									out= ("(handshake) Alliance Member Change: (%s) \r\n" % (server))
								if len(adddelta) >0:
									for player in adddelta:
										out = ("%s		 Player %s joined %s\r\n" % (out, newserverplayers[player][0], alliance_name(server, entry)))
								if len(remdelta) >0:
									for player in remdelta:
										out = ("%s		 Player %s left %s\r\n" % (out,serverplayers[player][0],alliance_name(server, entry)))
								if len(out) > 0:
									try:
										newchat = skype.Chat(chat)
										newchat.SendMessage(out)
									except Exception:
										print ('unable to send message to %s' % (skype.Chat))
			
			if delchat: 
				for chat in delchat:
					print ("Deleting Chatroom %s from Monitor because no longer subscribed" % (skype.Chat(chat).FriendlyName))
					del settings["monitor"][chat]
			delchat = []
			cfgsave(settings)
			print("[%s] Alliance Member Check Complete" % (ctime()))				
			allimembercheck = int(time()) + (60 * 60)				

		sleep(.01)

	
if __name__ == '__main__':
	main()
