from bs4 import BeautifulSoup
import requests
import re

# Variables
team_website = 'https://www.premierleague.com/tables'               # Define website to datascrape for teams
num_instances = 20                                                  # Defines how many teams are in the league
team_instances = []                                                 # Holds the instances of teams

class Team:
    def getData(self, response, num):
        if (response.status_code == 200):
            # We got a valid connection and return
            # Save the content of the website
            content = response.text

            # Set the parser to lxml
            soup = BeautifulSoup(content, 'html.parser')

            # Holds data for whole team table
            table = soup.find('div', class_="league-table__all-tables-container allTablesContainer")

            # Holds data for first place team
            team1 = table.find('tr', {'data-position':f'{num}'})

            # Get total points of team
            # firstPlace.append(team1.find('td', class_="league-table__points points").get_text())
            self.pts = team1.find('td', class_="league-table__points points").text

            # Get PL, W, D, and L
            # firstPlace.append(team1)
            stats = team1.find_all('td', class_="")
            self.pl = re.sub(r'\D', '', stats[0].text)
            self.w = re.sub(r'\D', '', stats[1].text)
            self.d = re.sub(r'\D', '', stats[2].text)
            self.l = re.sub(r'\D', '', stats[3].text)
            self.gd = re.sub(r'\D', '', stats[4].text)
            
            extra_stats = team1.find_all('td', class_="hideSmall")
            self.gf = re.sub(r'\D', '', extra_stats[0].text)
            self.ga = re.sub(r'\D', '', extra_stats[1].text)

            # Get values held in data_collection
            self.rank = team1["data-position"]
            self.name = team1["data-filtered-table-row-name"]

        elif (response.status_code == 404):
            # 404 NOT FOUND
            print(f"Error {response.status_code}: Resource you were looking for was not found")
        else:
            # Any error code
            print(f"Error {response.status_code}")
    
    def __init__(self, response, num, name='', rank='', pl='', w='', d='', l='', gf='', ga='', gd='', pts=''):
        self.num = num
        self.getData(response, num)
    
"""MAIN"""
# Get data from website for teams
response_teams = requests.get(team_website)

# Creates instances for each team and increments num 
for num in range(1, num_instances + 1):
    team = Team(response_teams, num=num)
    team_instances.append(team)
