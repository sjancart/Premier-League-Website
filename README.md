# Premier-League-Website

This project is to create a website to see the most interesting Premier League soccer games for the week. 
The website (https://staticwebsitefootball.s3.amazonaws.com/index.html) is a static website and is hosted on AWS S3.
The main programs running this project are Teams.py, Games.py, and Main.py and do the following.

Teams.py - Webscrapes the website 'https://www.premierleague.com/tables' for all stats on each of the 20 teams in the premier
           league using the dependencies Beautifulsoup4 and requests. This data is stored in the 'Team' class and is referenced 
           in Games.py and Main.py

Games.py - Webscrapes the website 'https://www.cbssports.com/soccer/premier-league/schedule/(date)' for all games for the next 7 days.
           The date is in the format of year, month, day(ex. November 25, 2023 -> 20231125). The data for a specific game is stored in
           the class 'Game'. A list containing a days worth of 'Game' objects is stored in the class 'Games', which is then held in the 
           class 'Day'. 

Main.py -  Creates a schedule for the games by day, time, and most interesting game to watch based off of collective ranks of the 
           two teams playing each other. For example, on November 25, 2023, at 10:00 am, there are five games going on, 
           -
           1. (17)  Newcastle United (Rank: 7) vs Chelsea (Rank: 10)
           2. (23)  Nottingham Forest (Rank: 15) vs Brighton & Hove Albion (Rank: 8)
           5. (36)  Sheffield United (Rank: 19) vs Bournemouth (Rank: 17)
           4. (31)  Luton Town (Rank: 18) vs Crystal Palace (Rank: 13)
           3. (29)  Burnley (Rank: 20) vs West Ham United (Rank: 9)
           -
           Newcastle United and Chelsea have a rank collective total of 17 and all other games have a collective total over 17, this game is 
           the most interesting to watch. If there is no conflicting game at a certain time, then that game is ranked first to watch. 
           Manchester City VS Liverpool is at 7:30 am with no other games at that time for the day, so this game is automatically the most 
           interesting game to watch at that time. Main.py also gets the 'index.html' from the hosted S3 bucket and writes new data into it
           to update the website.

Folders 'beautifulsoup4-4.12.2.dist-info', 'bs4', 'soupsieve', and 'soupsieve-2.5.dist-info' hold dependency beautifulsoup4

Folder 'cdk_folder' holds the cdk environment

Folders 'pip' and 'pip-23.3.1.dist-info' hold dependency pip

Folder 'requests-layer' holds the dependencies for request

Files '_virtualenv.pth', '_virtualenv.py', and 'pip-23.3.1.virtualenv' handle the python virtual environment

Folder 'requests-layer.zip' holds the zipped verison of the folder 'requests-layer', and is made into a layer by the CDK for AWS use

Folder 'web-scraper.zip' holds the files neccessary for the lambda function to run when createded by the CDK

Screenshot of the website with the lambda function updating as if it was on November 24, 2023:
![image](https://github.com/sjancart/Premier-League-Website/assets/149748778/92eb6a33-567c-403c-9f98-25a29020e545)

Architecture Diagram of the AWS portion of the project:
![image](https://github.com/sjancart/Premier-League-Website/assets/149748778/c2a04147-b2a1-4ebb-8c88-f225fe08546d)
