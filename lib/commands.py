# TODO: Fix methods, change add params, and rename from parms

settings = {}
config = {}

class Commands():

  def __init__(self, _config):
    config = _config
    settings = config.get()

    commands = {}
    commands['createchat'] = { 'handler': self.CreateChat }
    commands['listchats'] = { 'handler': self.ListChats }
    commands['delchat'] = { 'handler': self.DelChat }
    commands['listworlds'] = { 'handler': self.ListWorlds }
    commands['botstatus'] = { 'handler': self.BotStatus }
    commands['botstats'] = { 'handler': self.BotStatus }
    commands['monitor'] = {
      'syntax': "MONITOR <server> <alliance or player name>\r\n\
               EXAMPLE: >monitor delta Disciples of Ares\r\n\
               Description: Adds an Alliance or Player to the BP and Conquest watch list for this chat room. \
               Repeat same command to remove monitor.\r\n\
               Related Commands: monitorghost, monitorlist",
      'handler': self.Monitor
    }
    commands['monitorghost'] = {
      'syntax': "MONITORGHOST <server> <ocean>\r\n\
               EXAMPLE: >monitorghost delta 55\r\n\
               Description: Adds an Ocean to the Ghost watch list for this chat room. \
               Repeat same command to remove monitor.\r\n\
               Related Commands: monitor, monitorlist",
      'handler': self.MonitorGhost
    }
    commands['monitorlist'] = { 'handler': self.MonitorList }
    commands['conquests'] = {
      'syntax': "CONQUESTS <server> <alliance name>\r\n \
              EXAMPLE: >conquests delta Disciples of ares\r\n \
              Description: Returns last 48 hours of conquests for given alliance",
      'handler': self.Conquests
    }
    commands['joinchat'] = {
      'permissions': 'admin',
      'syntax': "JOINCHAT <chat id>",
      'handler': self.JoinChat
    }
    commands['kick'] = {
      'permissions': 'admin',
      'syntax': "KICK <username>",
      'handler': self.Kick
    }
    commands['adduser'] = {
      'permissions': 'admin',
      'syntax': "ADD <username>",
      'handler': self.AddUser
    }
    commands['promote'] = {
      'permissions': 'admin',
      'handler': self.PromoteDemote
    }
    commands['demote'] = {
      'permissions': 'admin',
      'handler': self.PromoteDemote
    }
    commands['addop'] = {
      'permissions': 'admin',
      'handler': self.AddOp
    }
    commands['delop'] = {
      'permissions': 'admin',
      'handler': self.DelOp
    }
    commands['listops'] = {
      'permissions': 'admin',
      'handler': self.ListOps
    }
    commands['addworld'] = {
      'permissions': 'admin',
      'syntax': "ADDWORLD <world>",
      'handler': self.AddWorld
    }
    commands['delworld'] = {
      'permissions': 'admin',
      'syntax': "DELWORLD <world>",
      'handler': self.DelWorld
    }
    commands['setstatus'] = {
      'permissions': 'admin',
      'syntax': "SETSTATUS <status>",
      'handler': self.SetStatus
    }
    commands['broadcast'] = {
      'permissions': 'admin',
      'syntax': "BROADCAST <message>",
      'handler': self.Broadcast
    }

    self.commands = commands

  def get(self):
    return self.commands

  def CreateChat(self, skype, Message):
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
  
  def ListChats(self, skype, Message):
    chats = []

    for chat in settings['monitor']:
      if chat not in chats:
        chats.append('%s\r\n' % (chat))

    for chat in settings['monitorghost']:
      if chat not in chats:
        chats.append('%s\r\n' % (chat))
    SendMessage('Bot Chats: \r\n    %s' % ('    '.join(chats)))

  def JoinChat(self, skype, Message):
    if not len(parms):
      SendMessage('[*] Syntax: JOINCHAT <chat id>')

    else:
      member = skype.User(Message.FromHandle)
      chat = skype.Chat(parms.split()[0])
      chat.SendMessage('/add %s' % (Message.FromHandle))

  def Kick(self, skype, Message):
    if not len(parms):
      SendMessage('[*] Syntax: KICK <user name>')
    else:
      Message.Chat.Kick(parms.split()[0])

  def AddUser(self, skype, Message):
    if not len(parms):
      SendMessage('[*] Syntax: ADD <user name>')
    else:
      member = skype.User(parms.split()[0])
      Message.Chat.AddMembers(member)

  # TODO: Fix this
  def PromoteDemote(self, skype, Message):
    role = 'MASTER'
    if cmd == 'DEMOTE': role = 'USER'

    try:
      if not len(parms):
        SendMessage('/setrole %s %s' % (Message.FromHandle, role))
      elif len(parms.split()[0]):
        SendMessage('/setrole %s %s' % (parms.split()[0], role))
    except:
      pass

  def AddOp(self, skype, Message):
    if not len(parms):
      SendMessage('[*] Syntax: ADDOP <user name>')
    else:
      settings["botadmins"].append(parms.split()[0])
      config.save(settings)
      SendMessage('Added %s to bot admins.' % (parms.split()[0]))

  def DelOp(self, skype, Message):
    if not len(parms):
      SendMessage('[*] Syntax: DELOP <user name>')
    else:
      settings["botadmins"].remove(parms.split()[0])
      config.save(settings)
      SendMessage('Removed %s from bot admins.' % (parms.split()[0]))

  def ListOps(self, skype, Message):
    SendMessage('Bot Admins: %s' % (', '.join(settings["botadmins"])))

  def DelChat(self, skype, Message):
    for member in Message.Chat.Members:
      if member.Handle == skype.CurrentUserHandle: continue
      Message.Chat.Kick(member.Handle)
    Message.Chat.Leave()
    # Message.Chat.Disband() # does not work 403 error
  
  def AddWorld(self, skype, Message):
    if len(parms.split()) < 2:
      SendMessage('[*] Syntax: ADDWORLD <server> <name>')
    else:
      settings['urls'][parms.split()[1]] = ("http://%s.grepolis.com" % parms.split()[0])
      config.save(settings)
      SendMessage('World %s added with url %s' % (parms.split()[1], "http://%s.grepolis.com" % parms.split()[0]))

  def DelWorld(self, skype, Message):
    if len(parms.split()) < 1:
      SendMessage('[*] Syntax: DELWORLD <name>')
    else:
      if parms.split()[0] in settings['urls']:
        settings['urls'].pop(parms.split()[0], None)
        config.save(settings)
        SendMessage('Deleted world %s.' % (parms.split()[0]))

  def ListWorlds(self, skype, Message):
    SendMessage('Worlds: %s' % ', '.join(settings['urls'].keys()))

  def BotStatus(self, skype, Message):
    if not 'botstatus' in settings or not len(settings['botstatus']):
      bot_status = 'There are no updates at this time.'
    else:
      bot_status = settings['botstatus']
    
    SendMessage(bot_status) 

  # TODO: Fix this, references to functions not defined here
  def BotStats(self, skype, Message):
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

  def SetStatus(self, skype, Message):
    if len(parms.split()) < 1:
      SendMessage('[*] Syntax: SETSTATUS <status>')
    else:
      today = datetime.date.today().strftime('%m/%d/%Y')
      print parms
      settings['botstatus'] = '%s: %s\r\n' % (today, parms)
      config.save(settings)
      SendMessage('Updated bot status.')

  def Broadcast(self, skype, Message):
    bcast = ' '.join(parms.split()[0:])
    SendMessage('Broadcasting this message to %s Chats: %s ' % (len(settings["monitor"]), bcast))
    for chat in settings["monitor"]:
      skype.Chat(chat).SendMessage(bcast)

  # TODO: Fix this, references to functions not defined here
  def Monitor(self, skype, Message):
    activeservers = getactiveservers()
    found = []
    if len(parms.split()) < 1:
      SendMessage('[*] Syntax: MONITOR <server> <alliance or player name>\r\n EXAMPLE: >monitor delta Disciples of Ares\r\nDescription: Adds an Alliance or Player to the DefBP and Conquest watch list for this chat room. Repeat same command to remove monitor.\r\nRelated Commands: monitorlist')
    elif parms.split()[0].lower() not in settings['urls']:
      SendMessage('[*] Invalid or unsupported server.')
    else:
      server = str(parms.split()[0].lower())
      if server not in activeservers:     # if server is not in list of monitored servers, download world files.
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
      
      config.save(settings)

  # TODO: Fix this, references to functions not defined here
  def MonitorGhost(self, skype, Message):
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

      config.save(settings)

  # TODO: Fix this, references to functions not defined here
  def MonitorList(self, skype, Message):
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
            
            if id in serveralliances:  out = '%s    %s (%s)\r\n' %(out, serveralliances[id][0],server)
            
            if id in serverplayers:  out = '%s    %s (%s)\r\n' %(out, serverplayers[id][0],server)
        SendMessage(out)
      if Message.Chat.Name in settings['monitorghost'] and len(settings['monitorghost'][Message.Chat.Name]) > 0:
        out = []
        for server in settings['monitorghost'][Message.Chat.Name]:
          for ocean in settings['monitorghost'][Message.Chat.Name][server]:
            if len(out) == 0: out = 'Oceans Monitored in this Chat\r\n'
            out = '%s    Ocean %s (%s)\r\n' % (out, ocean, server)
        SendMessage(out)
  
  # TODO: Fix this, references to functions not defined here
  def Conquests(self, skype, Message):
    __CONLIMIT__ = 60*60*24*2               #Set the max age of conquest we will return
    if len(parms.split()) < 2:
      SendMessage('[*] Syntax: CONQUESTS <server> <alliance name>\r\n EXAMPLE: >conquests delta Disciples of ares\r\n Description: Returns last 48 hours of conquests for given alliance')
    elif parms.split()[0].lower() not in settings['urls']:
      SendMessage('[*] Invalid or unsupported server')
    else:
      server = parms.split()[0].lower()
      alli_test = ' '.join(parms.split()[1:]).lower().strip() 
      found = find_alliance(server,alli_test) 
      if found: 
        alli_id,alli_name = found[0],found[1]       # set Alli ID and Alli name of the Alliance we are checking
        servertowns = loadfile(server,"towns")
        serverplayers = loadfile(server,"players")
        serveralliances = loadfile(server,"alliances")
        conquests = loadfile(server,"conquers")
        members = alliance_members(server,alli_id)      
        count = 0
        out = '[*] Conquests Involving %s in the last 48 hours [*]\r\n' % ( alli_name)
        for conquer in conquests["conquers"]:                   # Look at each line in the conquests file
          
          town_id,c_time,winner,loser,winner_ally_id,loser_ally_id,town_points = conquer  #break them down into vars
          town_name = unquote_plus(servertowns[town_id][1])
          if int(c_time) + __CONLIMIT__ < int(time()): continue         # if the conquest is greater than 48 hours ago, move to the next one
          if winner in members:                         #if the winner is in the alliance we are checking.....
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
        out = '%s [*] %s Conquests.' % (out, count)
        SendMessage(out)
            
      else:
        SendMessage('[*] Cannot initiate. Alliance id/name not found.')       

