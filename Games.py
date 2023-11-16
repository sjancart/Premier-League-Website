from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timedelta
from Teams import team_instances as ti

# Variables
num_instances = 7
day_instances = []

class Game:
    
    # Finds the Team object that corrosponds with the team name given
    def findTeam(self, team):
        for i in range(len(ti)):
            if ti[i].name == team:
                team = ti[i]
                break
        return team

    def __init__(self, day, homeTeam, awayTeam, time, stream, venue):
        self.day = day
        self.time = time
        self.homeTeam = self.findTeam(homeTeam)
        self.awayTeam = self.findTeam(awayTeam)
        self.stream = stream
        self.venue = venue

class Games: 
    def getData(self, response):
        # We got a valid connection and return
        list_of_games = []
        if (response.status_code == 200):

            # Save the content of the website
            content = response.text

            # Set the parser to lxml
            soup = BeautifulSoup(content, 'html.parser')

            # Holds data for whole games table
            table = soup.find('div', class_='TableBase')
            
            # Checks to see if there were games found on the website page for that day
            if table is not None:

                # Holds data for every game on the website page
                gtable = table.find_all('tr', class_="TableBase-bodyTr")
            
                for i in range(len(gtable)):
                    
                    # Gets only the data needed from each game row
                    gtable[i] = re.findall(r'([\w\d:.]+(?: [\w\d\'&]+)*)',gtable[i].get_text())

                    # Checks if the game has a steaming service. If not, stream equals ''
                    if len(gtable[i]) < 5:
                        gtable[i].insert(3,'')
                    
                    # Checks if one of the teams is named "Wolverhampton" as they go by "Wolverhampton Wanderers" on the website webscraped by Teams.py
                    if gtable[i][0] == 'Wolverhampton':
                        gtable[i][0] = 'Wolverhampton Wanderers'
                    elif gtable[i][1] == 'Wolverhampton':
                        gtable[i][1] = 'Wolverhampton Wanderers'
                    
                    # Creates an object of Game and sets all variables
                    game = Game(today_date, gtable[i][0],gtable[i][1],gtable[i][2],gtable[i][3],gtable[i][4])
                    list_of_games.append(game)
            else:
                game = Game(today_date,'','','','','')
                list_of_games.append(game)
        else:
            # Any error code
            print(f"Error {response.status_code}")
        
        return list_of_games
    
    def __init__(self, response):
        self.match = []
        self.match = self.getData(response)

    def same_game_time (self, day_to_check, time_to_check):
        matching_games = []
        for i in range(len(self.match)):
            if self.match[i].day == day_to_check and self.match[i].time == time_to_check:
                matching_games.append(self.match[i])
        return matching_games

class Day:
    def addGame(self, response_games):
        g = Games(response_games)
        self.games = g
        return self.games

    def __init__(self, response_games, date):
        self.date = date
        self.games = self.addGame(response_games)

"""MAIN"""
for num in range(0, num_instances):
    today_date = datetime.now().date() + timedelta(days=num)
    today_date = re.sub('-','',str(today_date))

    game_website = 'https://www.cbssports.com/soccer/premier-league/schedule/'+str(today_date)+'/'
    response_games = requests.get(game_website)
    d = Day(response_games, today_date)
    day_instances.append(d)