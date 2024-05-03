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


def getTeam_Events(team: str, year = None):

    """
    Gets the events that a team has particcipated in for a given year
    If no year is provided it gives every event that a team has ever participated in
    """

    if year != None:
        api_url = f'https://www.thebluealliance.com/api/v3/team/frc{team}/events/{year}'
    else:
        api_url = f'https://www.thebluealliance.com/api/v3/team/frc{team}/events'

    try:
        response = requests.get(api_url, headers={'X-TBA-Auth-Key': api_key})
        return response.json()
    except requests.exceptions.RequestException as e:
        return ("Error getting team events!")
    


def getTeam_Matches(team: str, event: str):

    """
    Gets the team's matches for a given event
    """
    
    api_url = f'https://www.thebluealliance.com/api/v3/team/frc{team}/event/{event}/matches'
    
    try:
        response = requests.get(api_url, headers={'X-TBA-Auth-Key': api_key})
        return response.json()
    except requests.exceptions.RequestException as e:
        return ("Error getting matches for event!")
    
def getEvent_Matches(event: str):
    
    """
    Gets all matches for a given event
    """

    api_url = f'https://www.thebluealliance.com/api/v3/event/{event}/matches'

    try:
        response = requests.get(api_url, headers={'X-TBA-Auth-Key': api_key})
        return response.json()
    except requests.exceptions.RequestException as e:
        return ('Error getting matches for event!')
    


def getTeam_MatchKeys(team: str, event: str):

    """
    Gets only the match keys, a little faster and less data
    Used to check if the match has already been stored
    """

    api_url = f'https://www.thebluealliance.com/api/v3/team/frc{team}/event/{event}/matches/keys'

    try:
        response = requests.get(api_url, headers={'X-TBA-Auth-Key': api_key})
        return response.json()
    except requests.exceptions.RequestException as e:
        return ('Error getting match keys for event!')



def getMatch(match: str):

    """
    Gets data for a single match by key
    """

    api_url = f'https://www.thebluealliance.com/api/v3/match/{match}/simple'

    try:
        response = requests.get(api_url, headers={'X-TBA-Auth-Key': api_key})
        return response.json()

    except requests.exceptions.RequestException as e:
        return ('Error getting match data for key!')
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
    