import json, os, logging, gzip, Skype4Py, operator, math, socket, datetime
from urllib import urlretrieve,unquote_plus
from urllib2 import Request,urlopen
from time import time, ctime, sleep
from lib.config import Config
from lib.commands import Commands
currdir = os.getcwd()
cfgfile = 'bot.cfg' #the file where we store defpochs/conqeusts and other info
datadir = 'data_files' # directory where we store world data files.
logging.basicConfig(filename='skype_bot.log',level=logging.DEBUG, format='%(asctime)s %(message)s')
skype = Skype4Py.skype.Skype()
timeout = 30
settings = {}
commands = {}
config = Config(cfgfile)
socket.setdefaulttimeout(timeout)

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
			config.save(settings)
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

	if commands[cmd]:
		commands[cmd].handler(skype, Message)

	else:
		SendMessage('Unrecognized command: %s' % (cmd))

def main():
	global settings
	activeservers = []
	settings = config.get()
	commands = Commands(config)
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
		config.save(settings)
	
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
				config.save(settings)
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
					config.save(settings)
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
			config.save(settings)
			print("[%s] Alliance Member Check Complete" % (ctime()))				
			allimembercheck = int(time()) + (60 * 60)				

		sleep(.01)

	
if __name__ == '__main__':
	main()
