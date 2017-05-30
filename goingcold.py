import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid")
pd.options.mode.chained_assignment = None

def handle_data(fp):
    #fp is the filepath on the computer
    #this function returns the data set which is needed to analyze steph curry's shot tendencies as well as other pg's
    #we make the data frame more readable by converting closest defender name to "first last" instead of "last, first"
    #we take the shot clock to be the game clock whenever the game clock is under 24 sec
    nba = pd.read_csv(fp)  #open the file 
    nba['CLOSEST_DEFENDER'] = nba['CLOSEST_DEFENDER'].apply(lambda x: x.lower())    #lower case everything
    nba['CLOSEST_DEFENDER'] = nba['CLOSEST_DEFENDER'].apply(lambda x: x.split(', ')) #make like the first name
    nba['CLOSEST_DEFENDER'] = nba['CLOSEST_DEFENDER'].apply(lambda x: x[1] + ' ' + x[0] if len(x) == 2 else None) #make like first name
    nba['Minutes Elapsed'] = nba['GAME_CLOCK'].apply(lambda x: x.replace(":",""))
    nba['Minutes Elapsed'] = nba['Minutes Elapsed'].apply(lambda x: 12 - float(x[0:2])*1 + float(x[3:5])/60 if len(x) == 4 else 12 - float(x[0]) + float(x[2:4])/60)
    nba['Minutes Elapsed'] = 12*(nba['PERIOD']-1) + nba['Minutes Elapsed']
    for item in range(len(nba['SHOT_CLOCK'])): #fill in N/A values
        if np.isnan(nba['SHOT_CLOCK'][item]):
            nba['SHOT_CLOCK'][item] = float(nba['GAME_CLOCK'][item][3:])            
    drops = ['FINAL_MARGIN','SHOT_RESULT','SHOT_NUMBER','player_id','CLOSEST_DEFENDER_PLAYER_ID'] #columns to get rid of 
    nba.drop(drops,axis=1,inplace=True) #get rid of these columns
    return nba

fp = "C:\\Users\\Abhijit\\Downloads\\shot_logs.csv\\shotlogs.csv"    # testing out handle_data function
x = handle_data(fp)
#print(x)

def pcgNShots(data,player,n):
    #this function seeks to identify the field goal percentage of a certain player after they have missed "n" shots
    playerdata = data.loc[data['player_name']==player] #get data for specific player
    games = set(playerdata['GAME_ID']) # get all the games played by player
    #shooting miss- streak of 1, 2, 3 affecting the next shot
    pcggame = []   #create an empty list for adding each percentage in each game for one missed shot, two missed shots, etc.
    
    for game in games:
        sgame = playerdata.loc[playerdata['GAME_ID']==game] #look at all shots in a specific game
        shotlist = list(2*sgame['FGM'] - 1) #all the shots for this game
        nshots = [] #shot list after n miss(s)
        start = 0
        end = start + n #start and end index for search
        
        while end < len(shotlist):
            if sum(shotlist[start:end]) == -n:
                nshots.append(.5*(shotlist[end] + 1)) #append the result of the shot after the nth miss
            end += 1 #update the search region
            start += 1 #update search region
        if len(nshots) > 0:
            pcggame.append(1 - (float(sum(nshots))/float(len(nshots))))
        #print(nshots)
    return np.mean(pcggame)

#k = pcgNShots(x,'stephen curry',5)
#print(k)
playerlist = ['stephen curry','james harden','lebron james','russell westbrook','jamal crawford','damian lillard']
#playerlist = []
#playerlist = ['dwight howard','al horford','blake griffin','marc gasol','tim duncan','pau gasol','lamarcus aldridge']
league = list(['jimmy butler','james harden','kyrie irving','andrew wiggins','lebron james',
               'john wall','trevor ariza','carmelo anthony','victor oladipo','damian lillard',
               'ty lawson','rudy gay','joe johnson','chris paul','tobias harris','darren collison'
               'eric bledsoe','kobe bryant','kyle lowry','russell westbrook','gordon hayward',
               'kemba walker','tyreke evans','goran dragic','monta ellis','wesley matthews',
               'luol deng','nicolas batum','kevin martin','bradley beal','chandler parsons','alec burks'
               'eric gordon','stephen curry','jrue holiday','brandon knight','kyle korver','arron afflalo',
               'klay thompson','draymond green','mike conley','dwyane wade','kawhi leonard','wilson chandler',
               'avery bradley','ricky rubio','jeff green','giannis antetokounmpo','deron williams',
               'jj redick','courtney lee','jeff teague','elfrid payton','jose calderon',
               'khris middleton','trey burke','derrick rose','matt barnes','rajon rondo','dirk nowitzki',
               'mario chalmers','george hill','jabari parker','reggie jackson','brandon jennings','harrison barnes','tony parker',
               'evan turner','dion waiters', 'marcus smart','andre iguodala','jamal crawford',
               'cj miles','tony allen','corey brewer','lance stephenson','jeremy lin','isaiah thomas','lou williams'])
n = list(range(1,7))
def ColdHand(data,playerlist,n,league):
    #n is a list of 1...n of shots missed
    #player list is a list of players to visualize
    hothand = pd.DataFrame(columns = ['Player','Streak','Prob. of Missing'])
    for player in league:
        if player in playerlist:
            for streak in n:
                fg = pcgNShots(data,player,streak)
                df1 = pd.DataFrame({'Player': [player], 'Streak': [streak], 'Prob. of Missing': [fg]})
                hothand = pd.concat([df1,hothand])
        else: #calculate league average
            for streak in n:
                fg = pcgNShots(data,player,streak)
                df2 = pd.DataFrame({'Player': ['League Avg'], 'Streak': [streak],'Prob. of Missing' : [fg]})
                hothand = pd.concat([df2,hothand])
    
    totals = pd.DataFrame(columns = ['Player','Streak','Prob. of Missing']) #new data frame for totals 
    for i in n:
        l = hothand.loc[hothand['Player']=='League Avg']
        l = l.loc[l['Streak']==i]
        df3 = pd.DataFrame({'Player': ['League Avg'],'Streak': [i], 'Prob. of Missing' : [np.mean(l['Prob. of Missing'])]}) #calculate league averages
        totals = pd.concat([df3,totals])
    hothand.drop(['League Avg'])
    hothand = pd.concat([totals,hothand])
    sns.pointplot(x = 'Streak', y = 'Prob. of Missing', hue = 'Player',data = hothand,ci = None)
    sns.plt.suptitle('Cold Hand Analysis')
    sns.plt.show()
    return None

#ColdHand(x,playerlist,n,league)
#print(k)
def shotDistNShots(data,player,n):
    #this function seeks to identify the average shot distance of a certain player after they have missed "n" shots
    playerdata = data.loc[data['player_name']==player] #get data for specific player
    games = set(playerdata['GAME_ID']) # get all the games played by player
    #shooting streak of 1, 2, 3 affecting the next shot
    shotdistgame = []   #create an empty list for adding each shot distance in each game for one made shot, two made shots, etc.
    for game in games:
        sgame = playerdata.loc[playerdata['GAME_ID']==game] #look at all shots in a specific game
        shotlist = sgame[['FGM','SHOT_DIST']]#all the shots for this game, in a data frame with fgm
        start = 0
        end = start + n #start and end index for search
        iterlist = list(shotlist['FGM'])
        
        while end < len(iterlist):           
            if sum(iterlist[start:end]) == 0:
                
                shotdistgame.append(shotlist['SHOT_DIST'].as_matrix()[end]) #append the distance of the shot after the nth miss    
            end += 1 #update the search region
            start += 1 #update search region
        
    return np.mean(shotdistgame)
    
#k = shotDistNShots(x,'stephen curry',4)
#print(k)

def shotDistColdHand(data,playerlist,n,league):
    hothand = pd.DataFrame(columns = ['Player','Streak','Shot Distance'])
    for player in league:
        if player in playerlist:
            for streak in n:
                sd = shotDistNShots(data,player,streak)
                df1 = pd.DataFrame({'Player': [player], 'Streak': [streak], 'Shot Distance': [sd]})
                hothand = pd.concat([df1,hothand])
        else: #calculate league average
            for streak in n:
                fg = shotDistNShots(data,player,streak)
                df2 = pd.DataFrame({'Player': ['League Avg'], 'Streak': [streak],'Shot Distance' : [fg]})
                hothand = pd.concat([df2,hothand])
    
    totals = pd.DataFrame(columns = ['Player','Streak','Shot Distance']) #new data frame for totals 
    for i in n:
        l = hothand.loc[hothand['Player']=='League Avg']
        l = l.loc[l['Streak']==i]
        df3 = pd.DataFrame({'Player': ['League Avg'],'Streak': [i], 'Shot Distance' : [np.mean(l['Shot Distance'])]}) #calculate league averages
        totals = pd.concat([df3,totals])
    hothand.drop(['League Avg'])
    hothand = pd.concat([totals,hothand])
    sns.pointplot(x = 'Streak', y = 'Shot Distance', hue = 'Player',data = hothand,ci = None)
    sns.plt.suptitle('Cold Hand Analysis')
    sns.plt.show()
    return None
    
#shotDistColdHand(x,playerlist,n,league)    

def defDistNShots(data,player,n):
    #this function seeks to identify the average defender distance of a certain player after they have made "n" shots
    playerdata = data.loc[data['player_name']==player] #get data for specific player
    games = set(playerdata['GAME_ID']) # get all the games played by player
    #shooting streak of 1, 2, 3 affecting the next shot
    defdistgame = []   #create an empty list for adding each def distance in each game for one made shot, two made shots, etc.
    for game in games:
        sgame = playerdata.loc[playerdata['GAME_ID']==game] #look at all shots in a specific game
        shotlist = sgame[['FGM','CLOSE_DEF_DIST']]#all the shots for this game, in a data frame with fgm
        start = 0
        end = start + n #start and end index for search
        iterlist = list(shotlist['FGM'])
        
        while end < len(iterlist):           
            if sum(iterlist[start:end]) == 0:
                
                defdistgame.append(shotlist['CLOSE_DEF_DIST'].as_matrix()[end]) #append the distance of the shot after the nth make    
            end += 1 #update the search region
            start += 1 #update search region
        
    return np.mean(defdistgame)

def defDistColdHand(data,playerlist,n,league):
    hothand = pd.DataFrame(columns = ['Player','Streak','Defender Distance'])
    for player in league:
        if player in playerlist:
            for streak in n:
                dd = defDistNShots(data,player,streak)
                df1 = pd.DataFrame({'Player': [player], 'Streak': [streak], 'Defender Distance': [dd]})
                hothand = pd.concat([df1,hothand])
        else: #calculate league average
            for streak in n:
                fg = defDistNShots(data,player,streak)
                df2 = pd.DataFrame({'Player': ['League Avg'], 'Streak': [streak],'Defender Distance' : [fg]})
                hothand = pd.concat([df2,hothand])
    
    totals = pd.DataFrame(columns = ['Player','Streak','Defender Distance']) #new data frame for totals 
    for i in n:
        l = hothand.loc[hothand['Player']=='League Avg']
        l = l.loc[l['Streak']==i]
        df3 = pd.DataFrame({'Player': ['League Avg'],'Streak': [i], 'Defender Distance' : [np.mean(l['Defender Distance'])]}) #calculate league averages
        totals = pd.concat([df3,totals])
    hothand.drop(['League Avg'])
    hothand = pd.concat([totals,hothand])
    sns.pointplot(x = 'Streak', y = 'Defender Distance', hue = 'Player',data = hothand,ci = None)
    sns.plt.suptitle('Cold Hand Analysis')
    sns.plt.show()
    return None    
        
#defDistColdHand(x,playerlist,n,league)        

def FreqNShots(data,player,n):
    #this function determines the shot frequency after a player has missed n shots
    playerdata = data.loc[data['player_name']==player] #get data for specific player
    games = set(playerdata['GAME_ID']) # get all the games played by player
    #shooting streak of 1, 2, 3 affecting the next shot
    freqgame = []   #create an empty list for adding each def distance in each game for one made shot, two made shots, etc.
    for game in games:
        sgame = playerdata.loc[playerdata['GAME_ID']==game] #look at all shots in a specific game
        shotlist = sgame[['FGM','Minutes Elapsed']]#all the shots for this game, in a data frame with fgm
        start = 0
        end = start + n #start and end index for search
        iterlist = list(shotlist['FGM'])        
        while end < len(iterlist):           
            if sum(iterlist[start:end]) == 0:                
                freqgame.append(shotlist['Minutes Elapsed'].as_matrix()[end]-shotlist['Minutes Elapsed'].as_matrix()[end-1]) #append the difference in shot time after the nth make    
            end += 1 #update the search region
            start += 1 #update search region
        
    return np.mean(freqgame)
#m = FreqNShots(x,'stephen curry',1)
#print(m)
def FreqColdHand(data,playerlist,n,league):
    hothand = pd.DataFrame(columns = ['Player','Streak','Minutes Elapsed'])
    for player in league:
        if player in playerlist:
            for streak in n:
                dd = FreqNShots(data,player,streak)
                df1 = pd.DataFrame({'Player': [player], 'Streak': [streak], 'Minutes Elapsed': [dd]})
                hothand = pd.concat([df1,hothand])
        else: #calculate league average
            for streak in n:
                fg = FreqNShots(data,player,streak)
                df2 = pd.DataFrame({'Player': ['League Avg'], 'Streak': [streak],'Minutes Elapsed' : [fg]})
                hothand = pd.concat([df2,hothand])
    
    totals = pd.DataFrame(columns = ['Player','Streak','Minutes Elapsed']) #new data frame for totals 
    for i in n:
        l = hothand.loc[hothand['Player']=='League Avg']
        l = l.loc[l['Streak']==i]
        df3 = pd.DataFrame({'Player': ['League Avg'],'Streak': [i], 'Minutes Elapsed' : [np.mean(l['Minutes Elapsed'])]}) #calculate league averages
        totals = pd.concat([df3,totals])
    hothand.drop(['League Avg'])
    hothand = pd.concat([totals,hothand])
    sns.pointplot(x = 'Streak', y = 'Minutes Elapsed', hue = 'Player',data = hothand,ci = None)
    sns.plt.suptitle('Cold Hand Analysis')
    sns.plt.show()
    return None
#FreqColdHand(x,playerlist,n,league)
def TOPNShots(data,player,n):
    #this function determines the shot frequency after a player has missed n shots
    playerdata = data.loc[data['player_name']==player] #get data for specific player
    games = set(playerdata['GAME_ID']) # get all the games played by player
    #shooting streak of 1, 2, 3 affecting the next shot
    freqgame = []   #create an empty list for adding each def distance in each game for one made shot, two made shots, etc.
    for game in games:
        sgame = playerdata.loc[playerdata['GAME_ID']==game] #look at all shots in a specific game
        shotlist = sgame[['FGM','TOUCH_TIME']]#all the shots for this game, in a data frame with fgm
        start = 0
        end = start + n #start and end index for search
        iterlist = list(shotlist['FGM'])        
        while end < len(iterlist):           
            if sum(iterlist[start:end]) == 0:                
                freqgame.append(shotlist['TOUCH_TIME'].as_matrix()[end]) #append the difference in shot time after the nth make    
            end += 1 #update the search region
            start += 1 #update search region
        
    return np.mean(freqgame)

def TouchColdHand(data,playerlist,n,league):
    hothand = pd.DataFrame(columns = ['Player','Streak','Minutes Elapsed'])
    for player in league:
        if player in playerlist:
            for streak in n:
                dd = TOPNShots(data,player,streak)
                df1 = pd.DataFrame({'Player': [player], 'Streak': [streak], 'TOUCH_TIME': [dd]})
                hothand = pd.concat([df1,hothand])
        else: #calculate league average
            for streak in n:
                fg = TOPNShots(data,player,streak)
                df2 = pd.DataFrame({'Player': ['League Avg'], 'Streak': [streak],'TOUCH_TIME' : [fg]})
                hothand = pd.concat([df2,hothand])
    
    totals = pd.DataFrame(columns = ['Player','Streak','TOUCH_TIME']) #new data frame for totals 
    for i in n:
        l = hothand.loc[hothand['Player']=='League Avg']
        l = l.loc[l['Streak']==i]
        df3 = pd.DataFrame({'Player': ['League Avg'],'Streak': [i], 'TOUCH_TIME' : [np.mean(l['TOUCH_TIME'])]}) #calculate league averages
        totals = pd.concat([df3,totals])
    hothand.drop(['League Avg'])
    hothand = pd.concat([totals,hothand])
    sns.pointplot(x = 'Streak', y = 'TOUCH_TIME', hue = 'Player',data = hothand,ci = None)
    sns.plt.suptitle('Cold Hand Analysis')
    sns.plt.show()
    return None
TouchColdHand(x,playerlist,n,league)
