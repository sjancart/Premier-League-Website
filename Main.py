from Teams import team_instances as ti
from Games import day_instances as di
import Aws

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

def rank(di):
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

def lambda_handler(event, context):
    
    hosted_zone_id = 'Z0402118S674EV25HLOF'
    record_name_1 = 'www.premierwatchlist.net'
    record_name_2 = 'premierwatchlist.net'
    
    # Creates a schedule in the order of games to watch
    schedule = rank(di)

    # Edits the static website with the new schedule
    Aws.edit_index(schedule)
    
    id = Aws.disable_cloudfront_distribution()
    
    domain_name = Aws.create_cloudfront_distribution(id)

    Aws.update_route53_records(domain_name, hosted_zone_id, record_name_1)

    Aws.update_route53_records(domain_name, hosted_zone_id, record_name_2)
    
    return {
        'statusCode': 200,
        'body': 'S3 Static Website Updated Successfully!'
    }