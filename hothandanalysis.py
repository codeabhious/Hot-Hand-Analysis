import pandas as pd
import random
import numpy as np
import string
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid")
import plotly.plotly as plotly
import plotly.graph_objs as go
import plotly.tools as tls
tls.set_credentials_file(username='abhious', api_key='1Tdwg7pmZUvqlMJhNEgD')
plotly.sign_in(username='abhious',api_key='1Tdwg7pmZUvqlMJhNEgD')
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
    for item in range(len(nba['SHOT_CLOCK'])): #fill in N/A values
        if np.isnan(nba['SHOT_CLOCK'][item]):
            nba['SHOT_CLOCK'][item] = float(nba['GAME_CLOCK'][item][3:])            
    drops = ['FINAL_MARGIN','SHOT_RESULT','SHOT_NUMBER','player_id','CLOSEST_DEFENDER_PLAYER_ID'] #columns to get rid of 
    nba.drop(drops,axis=1,inplace=True) #get rid of these columns
    return nba

fp = "C:\\Users\\Abhijit\\Downloads\\shot_logs.csv\\shotlogs.csv"    # testing out handle_data function
x = handle_data(fp)
##print(x)

# Basic Visualization of Player's Shot distribution
def shotdist(data,player):
    copy = data[['SHOT_DIST', 'player_name']] #keep distance and player name
    g = sns.FacetGrid(copy, col="player_name")
    g.map(sns.distplot, "SHOT_DIST") #plot distance and player name
    layout = go.Layout(barmode='overlay')
    for p in player:
        individual = data.loc[data['player_name'] == p]
        y = individual['SHOT_DIST']
        x = individual.loc[individual['PTS'] != 0]
        x = x['SHOT_DIST']
        trace = go.Histogram(x=x, opacity = .75, name = 'Shots Made', autobinx = False, xbins = dict(start = 0, end = 45, size = 5))
        trace0 = go.Histogram( x = y, opacity = .1, name = 'Shots Attempted', autobinx = False, xbins =dict(start = 0, end = 45, size = 5) )
        data_1 = [trace,trace0]
        fig = go.Figure(data=data_1, layout=layout)
        fig['layout'].update(height=600, width=600, title= p + ' Shot Distribution')
        plotly.plot(fig)
    sns.plt.show(g)
    return None


#shotdist(x,['stephen curry', 'james harden', 'chris paul', 'kyrie irving', 'russell westbrook'])

### Basic Visualization of Player's 3 pt. and 2 pt. Binning
def behindthearc(data,player):
    copy = data[['PTS_TYPE', 'player_name']] #keep 2/3 and player name
    g = sns.FacetGrid(copy, col="player_name")
    g.map(sns.distplot, "PTS_TYPE") #plot distance and player name
    sns.plt.subplots_adjust(top=0.9)
    g.fig.suptitle('Shot Attempt Bin')
    copy2 = data[['PTS','player_name']]
    copy2 = copy2.loc[copy2['PTS'] != 0]
    f = sns.FacetGrid(copy2,col='player_name')
    f.map(sns.distplot,'PTS')
    sns.plt.subplots_adjust(top=0.9)
    f.fig.suptitle('Shot Made Bin')
    sns.plt.show(f)
    sns.plt.show(g)
    return None
#behindthearc(x,['stephen curry', 'james harden', 'chris paul', 'kyrie irving', 'russell westbrook']) #just testing out the behindthearc binning
def shootingPercentageVsTeam(data,playerlist):
    j = data
    teams = list(set(j['MATCHUP'].apply(lambda x: x[len(x)-3:len(x)+1])))#make team names more readable #get list of teams
    data['MATCHUP'] = data['MATCHUP'].apply(lambda x: x[len(x)-3:len(x)+1])
    copy = data[['MATCHUP','LOCATION','player_name','PTS','PTS_TYPE']] #make copy of data 
    #print(teams)
    players = playerlist #get list of players
    c = ['2 PT. Shooting Percentage','3 PT. Shooting Percentage','Overall Shooting Percentage', 'Team'] #columns of seaborn plot
    for player in players: #produce a plot for each player
        stats = pd.DataFrame(columns = c) #empty dataframe for each player
        individual = copy.loc[copy['player_name']==player]#isolate data for specific player
        for team in teams: #do it for all the teams
            tdata = individual.loc[individual['MATCHUP'] == team] #matchup data for each specific team
            if not tdata.empty: #calculate the necessary values to compute the shooting percentages
                overallshots = float(len(tdata['PTS']))
                overallmade = float(len(tdata.loc[tdata['PTS'] != 0]))
                overall2shots = float(len(tdata.loc[tdata['PTS_TYPE']==2]))
                overall2shotsmade = float(len(tdata.loc[tdata['PTS']==2]))
                overall3shots = float(len(tdata.loc[tdata['PTS_TYPE']==3]))
                overall3shotsmade = float(len(tdata.loc[tdata['PTS']==3]))
                pcg3 = overall3shotsmade/overall3shots
                pcg2 = overall2shotsmade/overall2shots
                opcg = overallmade/overallshots
                stats = pd.concat([stats,pd.DataFrame([[pcg2,pcg3,opcg,team]],columns = c)]) #add the new data into the data frame
        copystats = pd.melt(stats,id_vars = 'Team', var_name = 'Percentage Type', value_name = 'Shooting Percentage') #melt the data set
        sns.factorplot(x='Team', y='Shooting Percentage', hue='Percentage Type', data=copystats, kind='bar') #seaborn yeet
        sns.plt.title(player + ' Shooting Percentage vs. Team')
        sns.plt.show()                         
    return stats
#shootingPercentageVsTeam(x,['stephen curry']) #testing the shooting percentage vs team
def shootingPercentageVsMonth(data,player):
    j = data #the data
    #months = list(set(j['MATCHUP'].apply(lambda x: x[0:3]))) # get the months
    months = ['OCT','NOV','DEC','JAN','FEB','MAR']
    data['MATCHUP'] = data['MATCHUP'].apply(lambda x: x[0:3]) #change the columns of matchup to be readable
    copy = data[['MATCHUP','LOCATION','player_name','PTS','PTS_TYPE']] #copy the data
    c = ['2 PT. Shooting Percentage','3 PT. Shooting Percentage','Overall Shooting Percentage', 'Month'] #columns of seaborn plot
    for player in player:
        stats = pd.DataFrame(columns = c) #empty dataframe for each player
        individual = copy.loc[copy['player_name']==player]#isolate data for specific player
        for month in months: #do it for all the teams
            tdata = individual.loc[individual['MATCHUP'] == month] #matchup data for each specific team
            if not tdata.empty: #calculate the necessary values to compute the shooting percentages
                overallshots = float(len(tdata['PTS']))
                overallmade = float(len(tdata.loc[tdata['PTS'] != 0]))
                overall2shots = float(len(tdata.loc[tdata['PTS_TYPE']==2]))
                overall2shotsmade = float(len(tdata.loc[tdata['PTS']==2]))
                overall3shots = float(len(tdata.loc[tdata['PTS_TYPE']==3]))
                overall3shotsmade = float(len(tdata.loc[tdata['PTS']==3]))
                pcg3 = overall3shotsmade/overall3shots
                pcg2 = overall2shotsmade/overall2shots
                opcg = overallmade/overallshots
                stats = pd.concat([stats,pd.DataFrame([[pcg2,pcg3,opcg,month]],columns = c)]) #add the new data into the data frame
        copystats = pd.melt(stats,id_vars = 'Month', var_name = 'Percentage Type', value_name = 'Shooting Percentage') #melt the data set
        sns.pointplot(x='Month', y='Shooting Percentage', hue='Percentage Type', data=copystats) #seaborn yeet
        sns.plt.title(player + ' Shooting Percentage vs. Month')
        sns.plt.show()                         
    return stats
#shootingPercentageVsMonth(x,['kyrie irving']) #testing the above function
def playerHeatMap(data,player,ifplayer):
    #this function returns a heatmap with the following:
    #x - axis: shot location
    # y- axis: defender location
    #the "heat" themselves will be the percentage made
    if ifplayer:
        playerdata = data.loc[data['player_name']==player] #get only the necessary data for the player
    else:
        playerdata = data
    playerdatacopy = playerdata.copy() #deep copy
    playerdatacopy = playerdatacopy[['FGM','SHOT_DIST','CLOSE_DEF_DIST']]#get only the necessary columns
    playerdatacopy = playerdatacopy.apply(lambda x: round(x))
    bins = 10
    res = playerdatacopy.groupby([pd.cut(playerdatacopy['SHOT_DIST'],bins),pd.cut(playerdatacopy['CLOSE_DEF_DIST'],bins)])['FGM'].mean().unstack()
    sns.heatmap(res,annot = True)
    if ifplayer:
        sns.plt.title(player + ': ' + 'Defender Distance vs. Shot Distance HeatMap')
    else:
        sns.plt.title('League Wide: Defender Distance vs. Shot Distance HeatMap')
    sns.plt.show()
    return None

#playerHeatMap(x,'stephen curry',True)
def pcgNShots(data,player,n):
    #this function seeks to identify the field goal percentage of a certain player after they have made "n" shots
    playerdata = data.loc[data['player_name']==player] #get data for specific player
    games = set(playerdata['GAME_ID']) # get all the games played by player
    #shooting streak of 1, 2, 3 affecting the next shot
    pcggame = []   #create an empty list for adding each percentage in each game for one made shot, two made shots, etc.
    
    for game in games:
        sgame = playerdata.loc[playerdata['GAME_ID']==game] #look at all shots in a specific game
        shotlist = list(sgame['FGM']) #all the shots for this game
        nshots = [] #shot list after n make(s)
        start = 0
        end = start + n #start and end index for search
        
        while end < len(shotlist):
            if sum(shotlist[start:end]) == n:
                nshots.append(shotlist[end]) #append the result of the shot after the nth make
            end += 1 #update the search region
            start += 1 #update search region
        if len(nshots) > 0:
            pcggame.append(float(sum(nshots))/float(len(nshots)))
    return np.mean(pcggame)

#k = pcgNShots(x,'stephen curry',4)
#print(k)
#playerlist = ['klay thompson','kyle korver','danny green','stephen curry']
playerlist = []
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
def HotHand(data,playerlist,n,league):
    #n is a list of 1...n of shots made
    #player list is a list of players to visualize
    hothand = pd.DataFrame(columns = ['Player','Streak','FG %'])
    for player in league:
        if player in playerlist:
            for streak in n:
                fg = pcgNShots(data,player,streak)
                df1 = pd.DataFrame({'Player': [player], 'Streak': [streak], 'FG %': [fg]})
                hothand = pd.concat([df1,hothand])
        else: #calculate league average
            for streak in n:
                fg = pcgNShots(data,player,streak)
                df2 = pd.DataFrame({'Player': ['League Avg'], 'Streak': [streak],'FG %' : [fg]})
                hothand = pd.concat([df2,hothand])
    
    totals = pd.DataFrame(columns = ['Player','Streak','FG %']) #new data frame for totals 
    for i in n:
        l = hothand.loc[hothand['Player']=='League Avg']
        l = l.loc[l['Streak']==i]
        df3 = pd.DataFrame({'Player': ['League Avg'],'Streak': [i], 'FG %' : [np.mean(l['FG %'])]}) #calculate league averages
        totals = pd.concat([df3,totals])
    hothand.drop(['League Avg'])
    hothand = pd.concat([totals,hothand])
    sns.pointplot(x = 'Streak', y = 'FG %', hue = 'Player',data = hothand,ci = None)
    sns.plt.suptitle('Hot Hand Analysis')
    sns.plt.show()
    return None

#HotHand(x,playerlist,n,league)
#print(k)
def shotDistNShots(data,player,n):
    #this function seeks to identify the average shot distance of a certain player after they have made "n" shots
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
            if sum(iterlist[start:end]) == n:
                
                shotdistgame.append(shotlist['SHOT_DIST'].as_matrix()[end]) #append the distance of the shot after the nth make    
            end += 1 #update the search region
            start += 1 #update search region
        
    return np.mean(shotdistgame)
    
#k = shotDistNShots(x,'stephen curry',4)
#print(k)

def shotDistHotHand(data,playerlist,n,league):
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
    sns.plt.suptitle('Hot Hand Analysis')
    sns.plt.show()
    return None
    
#shotDistHotHand(x,playerlist,n,league)    

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
            if sum(iterlist[start:end]) == n:
                
                defdistgame.append(shotlist['CLOSE_DEF_DIST'].as_matrix()[end]) #append the distance of the shot after the nth make    
            end += 1 #update the search region
            start += 1 #update search region
        
    return np.mean(defdistgame)

def defDistHotHand(data,playerlist,n,league):
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
    sns.plt.suptitle('Hot Hand Analysis')
    sns.plt.show()
    return None    
        
#defDistHotHand(x,playerlist,n,league)        
def defDribNShots(data,player,n):
    #this function seeks to identify the average defender distance of a certain player after they have made "n" shots
    playerdata = data.loc[data['player_name']==player] #get data for specific player
    games = set(playerdata['GAME_ID']) # get all the games played by player
    #shooting streak of 1, 2, 3 affecting the next shot
    dribgame = []   #create an empty list for adding each def distance in each game for one made shot, two made shots, etc.
    for game in games:
        sgame = playerdata.loc[playerdata['GAME_ID']==game] #look at all shots in a specific game
        shotlist = sgame[['FGM','DRIBBLES']]#all the shots for this game, in a data frame with fgm
        start = 0
        end = start + n #start and end index for search
        iterlist = list(shotlist['FGM'])
        
        while end < len(iterlist):           
            if sum(iterlist[start:end]) == n:
                
                dribgame.append(shotlist['DRIBBLES'].as_matrix()[end]) #append the distance of the shot after the nth make    
            end += 1 #update the search region
            start += 1 #update search region
        
    return np.mean(dribgame)
def defDribHotHand(data,playerlist,n,league):
    hothand = pd.DataFrame(columns = ['Player','Streak','Defender Distance'])
    for player in league:
        if player in playerlist:
            for streak in n:
                ct = defDribNShots(data,player,streak)
                df1 = pd.DataFrame({'Player': [player], 'Streak': [streak], 'Dribbles': [ct]})
                hothand = pd.concat([df1,hothand])
        else: #calculate league average
            for streak in n:
                fg = defDribNShots(data,player,streak)
                df2 = pd.DataFrame({'Player': ['League Avg'], 'Streak': [streak],'Dribbles' : [fg]})
                hothand = pd.concat([df2,hothand])
    
    totals = pd.DataFrame(columns = ['Player','Streak','Dribbles']) #new data frame for totals 
    for i in n:
        l = hothand.loc[hothand['Player']=='League Avg']
        l = l.loc[l['Streak']==i]
        df3 = pd.DataFrame({'Player': ['League Avg'],'Streak': [i], 'Dribbles' : [np.mean(l['Dribbles'])]}) #calculate league averages
        totals = pd.concat([df3,totals])
    hothand.drop(['League Avg'])
    hothand = pd.concat([totals,hothand])
    sns.pointplot(x = 'Streak', y = 'Dribbles', hue = 'Player',data = hothand,ci=None)
    sns.plt.suptitle('Hot Hand Analysis')
    sns.plt.show()
    return None 
       
#defDribHotHand(x,playerlist,n,league)
def homeNShots(data,player,n,location):
    #this function seeks to identify the field goal percentage of a certain player after they have made "n" shots
    playerdata = data.loc[data['player_name']==player] #get data for specific player
    games = set(playerdata['GAME_ID']) # get all the games played by player
    #shooting streak of 1, 2, 3 affecting the next shot
    pcggame = []   #create an empty list for adding each percentage in each game for one made shot, two made shots, etc.
    
    for game in games:
        sgame = playerdata.loc[playerdata['GAME_ID']==game]#look at all shots in a specific game
        sgame = sgame.loc[sgame['LOCATION'] == location]
        shotlist = list(sgame['FGM']) #all the shots for this game
        nshots = [] #shot list after n make(s)
        start = 0
        end = start + n #start and end index for search
        
        while end < len(shotlist):
            if sum(shotlist[start:end]) == n:
                nshots.append(shotlist[end]) #append the result of the shot after the nth make
            end += 1 #update the search region
            start += 1 #update search region
        if len(nshots) > 0:
            pcggame.append(float(sum(nshots))/float(len(nshots)))
    return np.mean(pcggame)
def homeHotHand(data,player,n,league,location):
    #n is a list of 1...n of shots made
    #player list is a list of players to visualize
    hothand = pd.DataFrame(columns = ['Player','Streak','FG %'])
    for player in league:
        if player in playerlist:
            for streak in n:
                fg = homeNShots(data,player,streak,location)
                df1 = pd.DataFrame({'Player': [player], 'Streak': [streak], 'FG %': [fg]})
                hothand = pd.concat([df1,hothand])
        else: #calculate league average
            for streak in n:
                fg = homeNShots(data,player,streak,location)
                df2 = pd.DataFrame({'Player': ['League Avg'], 'Streak': [streak],'FG %' : [fg]})
                hothand = pd.concat([df2,hothand])
    
    totals = pd.DataFrame(columns = ['Player','Streak','FG %']) #new data frame for totals 
    for i in n:
        l = hothand.loc[hothand['Player']=='League Avg']
        l = l.loc[l['Streak']==i]
        df3 = pd.DataFrame({'Player': ['League Avg'],'Streak': [i], 'FG %' : [np.mean(l['FG %'])]}) #calculate league averages
        totals = pd.concat([df3,totals])
    hothand.drop(['League Avg'])
    hothand = pd.concat([totals,hothand])
    sns.pointplot(x = 'Streak', y = 'FG %', hue = 'Player',data = hothand, ci = None)
    
    sns.plt.suptitle(location + ': ' +'Hot Hand Analysis')
    sns.plt.show()
    return None

#homeHotHand(x,playerlist,n,league,'H')

