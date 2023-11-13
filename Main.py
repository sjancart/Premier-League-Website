from Teams import team_instances as ti
from Games import day_instances as di
import json
import boto3

# All installed libraries
#   pip install beautifulsoup4
#   pip install requests


def sort (conflicts):
    # Recursive Function that quick sorts the original arrays by setting the pivot to the middle index,
    # then splitting the array into 3 arrays, which hold the indexes that are less that, 
    # greater then, or equal to the pivot. Those arrays also get sorted recurively and so on, 
    # until there is only 1 index in the array. Then the recursion goes back up the chain with combined,
    # in order, arrays
    
    if len(conflicts) <= 1:
        return conflicts
    
    pivot = int(conflicts[len(conflicts) // 2].homeTeam.rank) + int(conflicts[len(conflicts) // 2].awayTeam.rank)   # Choose the pivot element as the middle
    left = [x for x in conflicts if (int(x.homeTeam.rank) + int(x.awayTeam.rank)) < pivot]                          # Indexes that are smaller than the pivot
    middle = [x for x in conflicts if (int(x.homeTeam.rank) + int(x.awayTeam.rank)) == pivot]                       # Indexes that are equal to the pivot
    right = [x for x in conflicts if (int(x.homeTeam.rank) + int(x.awayTeam.rank)) > pivot]                         # Indexes that are greater than the pivot
    array = sort(left) + middle + sort(right)
    
    return array

def rank(ti,di):
    schedule = []           # Holds the games in date order, time order, then ranked order if conflicts
    conflicts = []          # Holds the games with conflicting times in a day
    sortedConflicts = []    # Holds the sorted games with conflicts              
    k=0                     # Interates through the games in a day

    # Goes through every day in the week
    for i in range(0,7):

        # Set k to 0, if not, while loop does not start at the beginning of the list 
        k=0
        
        # Checks if the day does not have any matches, if so, add to schedule immediately
        if di[i].games.match[0].time == '':
            schedule.append(di[i].games.match[0])
        
        # If the day does have matches, see how many
        else:

            # Loops until all matches of the day are gone through
            while k < len(di[i].games.match):

                # Checks to see if there are any games in the day at the same time
                conflicts = di[i].games.same_game_time(di[i].games.match[k].day, di[i].games.match[k].time)
                
                # If there is only 1 index in conflicts, there are no conflicts (1 = the game that was being compared)
                if len(conflicts) == 1:

                    # Add the game right to the schedule, increment (k) to the next game
                    schedule.append(di[i].games.match[k])
                    k+=1
                
                # There is a game or more that is at the same time as the game being compared
                else:

                    # Put the games into order of rank (lowest to highest accumlative rank of home and away team)
                    sortedConflicts = sort(conflicts)
                    
                    # Add the sorted conflict games to the schedule
                    for m in range(len(sortedConflicts)):
                        schedule.append(sortedConflicts[m])
                    
                    # Increment (k) to the next game that was not at the conflicted time
                    k+=len(sortedConflicts)
    return schedule

def formatDate(date):
    formattedDate = ''  # Holds the newly formatted day (ex. January 1, 2000)
    year = date[:4]     # Parse the year from the date
    month = date[4:6]   # Parse the month from the date
    day = date[6:]      # Parse the day from the date
    
    match(month):
        case '01':
            formattedDate = "January "
        case '02':
            formattedDate = "February "
        case '03':
            formattedDate = "March "
        case '04':
            formattedDate = "April "
        case '05':
            formattedDate = "May "
        case '06':
            formattedDate = "June "
        case '07':
            formattedDate = "July "
        case '08':
            formattedDate = "August "
        case '09':
            formattedDate = "September "
        case '10':
            formattedDate = "October "
        case '11':
            formattedDate = "November "
        case '12':
            formattedDate = "December "
        case _:
            formattedDate = month + " "

    formattedDate += (day + ', ')
    formattedDate += year

    return formattedDate

def create_head(content, color):
    tab = '\n\t\t\t'
    content += ('\n\t\t<tr>')
    content += (tab + '<td></td>')
    content += (tab + '<td></td>')
    content += (tab + '<td style="background-color: '+color+'">Rank</td>')
    content += (tab + '<td style="background-color: '+color+'">Played</td>')
    content += (tab + '<td style="background-color: '+color+'">Won</td>')
    content += (tab + '<td style="background-color: '+color+'">Drawn</td>')
    content += (tab + '<td style="background-color: '+color+'">Lost</td>')
    content += (tab + '<td style="background-color: '+color+'">GF</td>')
    content += (tab + '<td style="background-color: '+color+'">GA</td>')
    content += (tab + '<td style="background-color: '+color+'">GD</td>')
    content += (tab + '<td style="background-color: '+color+'">Points</td>')
    content += ('\n\t\t</tr>')
    return content 

def create_cell(content, team, color):
    tab = '\n\t\t\t'
    content += ('\n\t\t<tr>')
    content += (tab + '<td style="background-color: '+color+'"><img src="'+team.name+'.png"> </td>')              # Adds the team logo
    content += (tab + '<td style="background-color: '+color+'">'+team.name+'</td>')                               # Adds the team name
    content += (tab + '<td style="background-color: '+color+'">'+team.rank+'</td>')                               # Adds the team rank
    content += (tab + '<td style="background-color: '+color+'">'+team.pl+'</td>')                                 # Adds the team Played
    content += (tab + '<td style="background-color: '+color+'">'+team.w+'</td>')                                  # Adds the team Won
    content += (tab + '<td style="background-color: '+color+'">'+team.d+'</td>')                                  # Adds the team Drawn
    content += (tab + '<td style="background-color: '+color+'">'+team.l+'</td>')                                  # Adds the team Lost
    content += (tab + '<td style="background-color: '+color+'">'+team.gf+'</td>')                                 # Adds the team GF
    content += (tab + '<td style="background-color: '+color+'">'+team.ga+'</td>')                                 # Adds the team GA
    content += (tab + '<td style="background-color: '+color+'">'+team.gd+'</td>')                                 # Adds the team GD
    content += (tab + '<td style="background-color: '+color+'">'+team.pts+'</td>')                                # Adds the team Points
    content += ('\n\t\t</tr>')
    return content

def edit_index(schedule):
    # Make an S3 client
    s3_client = boto3.client('s3')
    
    # Define the bucket name
    bucket_name = 'staticwebsitefootball'
    
    # Define the file name
    file = 'index.html'
    currentDate = ''
    currentTime = ''
    # time_colors = ['Orange', 'Salmon', 'Tomato', 'Coral', 'Khaki', 'LemonChiffon', 'PeachPuff']  # Holds the color of the time tables
    time_colors = ['Blue', '#5dade2', '#85c1e9', '#a9cce3', '#d0e8f2', '#abebc6', 'Green']  # Holds the color of the time tables
    rank_colors = ['Gold', 'Silver', 'rgb(205, 127, 50)']                                        # Holds the top 1, 2, and 3 ranked game of the time's colors (gold, silver, bronze)
    count_1 = 0
    count_2 = 0
    
    # Rewrite the content of the file by iterating through the schedule
    content = '<html xmlns="http://www.w3.org/1999/whtml" >\n<head>\n\t<title>Premier League Schedule</title>\n</head>\n<body>\n\t<h1>Premier League Rank</h1>'

    # Add the Day, Time, Home Teams (logo pic), and Away Teams(logo pic) to index.html
    for i in range(len(schedule)):
        
        if (schedule[i].homeTeam != ''):
            
            if schedule[i].day != currentDate:
                formattedDate = formatDate(schedule[i].day)
                content += ('\n\t<h2>'+str(formattedDate)+'</h2>')                              # Adds the Date
                currentDate = schedule[i].day
                count_2 = 0

            content += ('\n\t<table style="background-color: ' + time_colors[count_1] + '">')  # Adds the table header
            
            if schedule[i].time != currentTime:
                content += ('<td><h3>'+str(schedule[i].time)+'</h3></td>')                      # Adds the time
                currentTime = schedule[i].time
                count_1 = 0
                count_2 = 0
            
                                                                 
            
            # Checks if the game is in the top 3 games to watch for the time in the day
            if count_2 <= 2:
                content = create_head(content, rank_colors[count_2])                                                          # Adds the head of the teams stats
                content = create_cell(content, schedule[i].homeTeam, rank_colors[count_2])                # Adds a cell to the table
                content = create_cell(content, schedule[i].awayTeam, rank_colors[count_2])                # Adds a cell to the table
            else:
                content = create_head(content, 'white')                                                            # Adds the head of the teams stats
                content = create_cell(content, schedule[i].homeTeam, 'white')                               # Adds a cell to the table
                content = create_cell(content, schedule[i].awayTeam, 'white')                               # Adds a cell to the table
            
            content += ('\n\t</table>')
            
            currentDate = schedule[i].day                                                       # Update the current date
            count_2 += 1
        count_1 += 1   
    # End body and html sections
    content += "\n</body>\n</html>"
    
    # Send the new index.html to the bucket
    s3_client.put_object(Bucket=bucket_name, Key=file, Body=content, ContentType='text/html')
    
def lambda_handler(event, context):
    schedule = rank(ti,di)
    edit_index(schedule)
    
    return {
        'statusCode': 200,
        'body': 'S3 Static Website Updated Successfully!'
    }