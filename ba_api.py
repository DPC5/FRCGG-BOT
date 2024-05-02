import requests
import json

with open('config/config.json') as f:
    json = json.load(f)
    api_key = json['Ba_API_KEY']


#Gets the status of the blue alliance website
#Mainly used to just get the current season
def getStatus():
    api_url = "https://www.thebluealliance.com/api/v3/status"

    try:
        response = requests.get(api_url)
        return response.json()
    except requests.exceptions.RequestException as e:
        return("Error getting status!")

#Gets a team including all of thier general stats
def getTeam(team: str):

    api_url = f'https://www.thebluealliance.com/api/v3/team/frc{team}'
    
    try:
        response = requests.get(api_url, headers={'X-TBA-Auth-Key': api_key})
        return response.json()
    except requests.exceptions.RequestException as e:
        return ("Error getting team!")


#Gets the events that a team has participated in for a given year
#If no year is called then it will list every event that team has participated in
def getTeam_Events(team: str, year = None):

    if year != None:
        api_url = f'https://www.thebluealliance.com/api/v3/team/frc{team}/events/{year}'
    else:
        api_url = f'https://www.thebluealliance.com/api/v3/team/frc{team}/events'

    try:
        response = requests.get(api_url, headers={'X-TBA-Auth-Key': api_key})
        return response.json()
    except requests.exceptions.RequestException as e:
        return ("Error getting team events!")
    

#Gets the team's matches for a given event
def getTeam_Matches(team: str, event: str):

    api_url = f'https://www.thebluealliance.com/api/v3/team/frc{team}/event/{event}/matches'
    
    try:
        response = requests.get(api_url, headers={'X-TBA-Auth-Key': api_key})
        return response.json()
    except requests.exceptions.RequestException as e:
        return ("Error getting matches for event!")
    
def getEvent_Matches(event: str):
    
    api_url = f'https://www.thebluealliance.com/api/v3/event/{event}/matches'

    try:
        response = requests.get(api_url, headers={'X-TBA-Auth-Key': api_key})
        return response.json()
    except requests.exceptions.RequestException as e:
        return ('Error getting matches for event!')


#Gets all stats for a year for a team
#Returns winrate for that year, average score
def getYear_Stats(team: str, year: int):

    api_url = f'https://www.thebluealliance.com/api/v3/team/frc{team}/matches/{year}/simple'

    try:
        response = requests.get(api_url, headers={'X-TBA-Auth-Key': api_key})
        matches = response.json()
        score = 0
        wins = 0
        games = 0
        for dic in matches:
            games += 1
            if f'frc{team}' in dic['alliances']['blue']['team_keys']:
                alliance = 'blue'
            else:
                alliance = 'red'
            if alliance == dic['winning_alliance']:
                wins += 1
            score += dic['alliances'][alliance]['score']
        return {
            'winRate': wins / games,
            'score': score / games
        }

    except requests.exceptions.RequestException as e:
        return ("Error getting yearly stats!")
    
# print (getYear_Stats('5736',2024))

#gets a team's icon for that year
#returning a base64
def getIcon(team: str, year: int):

    api_url = f'https://www.thebluealliance.com/api/v3/team/frc{team}/media/{year}'

    try:
        response = requests.get(api_url, headers={'X-TBA-Auth-Key': api_key})
        response = response.json()
        return response[0]['details']['base64Image']
    except requests.exceptions.RequestException as e:
        return ("Error getting icon!")
    