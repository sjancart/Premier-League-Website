import json
import boto3
import time
from datetime import datetime, timedelta

def disable_cloudfront_distribution():
    cloudfront_client = boto3.client('cloudfront')
    cname = 'www.premierwatchlist.net'
    # List all CloudFront distributions
    distributions = cloudfront_client.list_distributions()
    try:
        # Iterate through all distributions
        for distribution in distributions['DistributionList']['Items']:
            
            if 'Aliases' in distribution and 'Items' in distribution['Aliases']:
                
                # Check if the CNAME is in the distribution's aliases
                if cname in distribution['Aliases']['Items']:
                    
                    # Get the Id and configuration of the distribution
                    distribution_id = distribution['Id']
                    distribution_config = cloudfront_client.get_distribution_config(Id=distribution_id)
                    
                    status = distribution_config.get('Status')
                    if status not in ['Deployed', 'Disabled']:
                        
                        # Disable the distribution
                        distribution_config['DistributionConfig']['Enabled'] = False
        
                        etag = distribution_config['ETag']
                        
                        # Update the distribution with 'disabled'
                        cloudfront_client.update_distribution(
                            DistributionConfig=distribution_config['DistributionConfig'],
                            Id=distribution_id,
                            IfMatch=etag
                        )
                        
                        print(f"Disabled distribution: {distribution_id}")
                    else:
                        print("Already Disabled")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return distribution_id

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

# Adds the header cell to the table to define what each stat means
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

# Adds stats of the teams to the table
def create_cell(content, team, color):
    tab = '\n\t\t\t'
    content += ('\n\t\t<tr>')
    content += (tab + '<td style="background-color: '+color+'"><img src="'+team.name+'.png"> </td>')              # Adds the team logo
    content += (tab + '<td style="background-color: '+color+'">'+team.name+'</td>')                               # Adds the team name
    content += (tab + '<td style="background-color: '+color+'">'+team.rank+'</td>')                               # Adds the team rank
    content += (tab + '<td style="background-color: '+color+'">'+team.pl+'</td>')                                 # Adds the number of games the team has played
    content += (tab + '<td style="background-color: '+color+'">'+team.w+'</td>')                                  # Adds the number of games the team won
    content += (tab + '<td style="background-color: '+color+'">'+team.d+'</td>')                                  # Adds the number of games the team drawn
    content += (tab + '<td style="background-color: '+color+'">'+team.l+'</td>')                                  # Adds the number of games the team lost
    content += (tab + '<td style="background-color: '+color+'">'+team.gf+'</td>')                                 # Adds the number of goals the team has made
    content += (tab + '<td style="background-color: '+color+'">'+team.ga+'</td>')                                 # Adds the number of goals the team has conceded stat
    content += (tab + '<td style="background-color: '+color+'">'+team.gd+'</td>')                                 # Adds the difference between GF and GA
    content += (tab + '<td style="background-color: '+color+'">'+team.pts+'</td>')                                # Adds the number of points the team has
    content += ('\n\t\t</tr>')
    return content
    
def edit_index(schedule):

    # Make an S3 client
    s3_client = boto3.client('s3')
    
    # Define the bucket name
    bucket_name = 'www.premierwatchlist.net'
    
    # Define the file name
    file = 'index.html'                                                                         # Holds the name of the file creating the stat website
    currentDate = ''                                                                            # Holds the date of the current game
    currentTime = ''                                                                            # Holds the time of the current game
    time_colors = ['Blue', '#5dade2', '#85c1e9', '#a9cce3', '#d0e8f2', '#abebc6', 'Green']      # Holds the color of the time tables
    rank_colors = ['Gold', 'Silver', 'rgb(205, 127, 50)']                                       # Holds the top 1, 2, and 3 ranked game of the time's colors (gold, silver, bronze)
    time_color_count = 0                                                                        # Increments the color being used in time_colors
    rank_color_count = 0                                                                        # Increments the color being used in rank_colors
    
    # Rewrite the content of the file by iterating through the schedule
    content = '<html xmlns="http://www.w3.org/1999/whtml" >\n<head>\n\t<title>Premier League Schedule</title>\n</head>\n<body>\n\t<h1>Premier League Games</h1>'
    content += f'\n\t<h5>Lasted Updated:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</h5>\n\t<h5>Game Dates:{datetime.now().date()} - {(datetime.now() + timedelta(days=6)).date()}</h5>'
    # Add the Day, Time, Home Teams (logo pic), and Away Teams(logo pic) to index.html
    for i in range(len(schedule)):
        
        if (schedule[i].homeTeam != ''):
            
            # Checks if this game is on a new day then the last game
            if schedule[i].day != currentDate:
                formattedDate = formatDate(schedule[i].day)
                content += ('\n\t<h2>'+str(formattedDate)+'</h2>')                              # Adds the Date to the file
                currentDate = schedule[i].day
                rank_color_count = 0
            
            content += ('\n\t<table style="background-color: ' + time_colors[time_color_count] + '">')   # Adds the table header
            
            # Checks if this game is at a new time then the last game
            if schedule[i].time != currentTime:
                content += ('<td><h3>'+str(schedule[i].time)+'</h3></td>')                      # Adds the time
                currentTime = schedule[i].time
                time_color_count = 0
                rank_color_count = 0
            
            # Checks if the game is in the top 3 games to watch for the time in the day
            if rank_color_count <= 2:
                content = create_head(content, rank_colors[rank_color_count])                                      # Adds the head of the teams stats
                content = create_cell(content, schedule[i].homeTeam, rank_colors[rank_color_count])                # Adds a cell to the table for home team
                content = create_cell(content, schedule[i].awayTeam, rank_colors[rank_color_count])                # Adds a cell to the table for away team
            
            # If it is not in the top 3, background is white
            else:
                content = create_head(content, 'white')                                                   # Adds the head of the teams stats
                content = create_cell(content, schedule[i].homeTeam, 'white')                             # Adds a cell to the table for home team
                content = create_cell(content, schedule[i].awayTeam, 'white')                             # Adds a cell to the table for away team
            
            content += ('\n\t</table>')                          # Closes the table section
            
            currentDate = schedule[i].day                                                       # Update the current date
            rank_color_count += 1                                # Update to go to the next rank color
            time_color_count += 1                               # Update to go to the next time color
    
    if 'table' not in content:
        content += "\n\t<h1>There are no games scheduled for the next 7 days.</h1>"
    
    # End body and html sections
    content += "\n</body>\n</html>"
    
    # Send the new index.html to the bucket
    s3_client.put_object(Bucket=bucket_name, Key=file, Body=content, ContentType='text/html')
                
def delete_cloudfront_distribution(cloudfront_client, id):
    while True:
        try:
            distribution = cloudfront_client.get_distribution(Id=id)
            etag = distribution['ETag']
            status = distribution['Distribution']['Status']
            
            if status == 'Deployed':
                response = cloudfront_client.delete_distribution(Id=id, IfMatch=etag)
                print(f"Deleted CloudFront distribution with ID: {id}")
                print(response)
                break
            else:
                time.sleep(30)
    
        except cloudfront_client.exceptions.NoSuchDistribution as e:
            print(f"CloudFront distribution with ID {id} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

def create_cloudfront_distribution(id):
    
    cloudfront_client = boto3.client('cloudfront', region_name='us-east-1')
    
    # Delete the previous distribution
    delete_cloudfront_distribution(cloudfront_client, id)
    
    # Make a new distribution
    distribution_config = {
        'CallerReference': f'PL-{time.time()}',
        'Aliases': {
            'Quantity': 1,
            'Items': ['www.premierwatchlist.net']
        },
        'DefaultRootObject': 'index.html',
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': 'premierwatchlist-s3-origin',
                    'DomainName': 'www.premierwatchlist.net.s3.amazonaws.com',
                    'S3OriginConfig': {
                        'OriginAccessIdentity': ''
                    }
                }
            ]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': 'premierwatchlist-s3-origin',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'DefaultTTL': 86400,
            'MinTTL': 3600,
            'MaxTTL': 31536000,
            'ForwardedValues': {
                'QueryString': True,
                'Cookies': {
                    'Forward': 'all'
                }
            }
        },
        'ViewerCertificate': {
            'ACMCertificateArn': 'arn:aws:acm:us-east-1:595338072969:certificate/edf46da3-641e-48f0-b061-f1d1274d8509',
            'SSLSupportMethod': 'sni-only'
        },
        'Comment': 'Premier League website distribution',
        'Enabled': True,
    }

    response = cloudfront_client.create_distribution(DistributionConfig=distribution_config)
    
    # Get the domain name for updating the Route 53 Records
    distribution_domain_name = response['Distribution']['DomainName']

    print(response)
    return distribution_domain_name

def update_route53_records(domain_name, hosted_zone_id, record_name):
    # Create a Route 53 client
    route53_client = boto3.client('route53')

   # Get the existing record set
    response = route53_client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        StartRecordName=record_name,
        StartRecordType='A',
        MaxItems='1'
    )

    # Extract the existing record set details if available
    existing_record_set = response['ResourceRecordSets'][0] if 'ResourceRecordSets' in response else None
    print(existing_record_set)

    if existing_record_set:
        # Update the existing record set
        existing_record_set['AliasTarget']['DNSName'] = domain_name

        # Create a change batch to update the record set
        change_batch = {
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': existing_record_set
                },
            ]
        }

    # Update the record set
    try:
        route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch=change_batch
        )
        print(f"Updated Route 53 record set for {record_name} with CloudFront distribution domain: {domain_name}")
    
    except route53_client.exceptions.InvalidChangeBatch as e:
        print(f"Error: {e}")
