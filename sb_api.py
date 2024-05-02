import statbotics
import ba_api as ba

#Overall goal for this file is going to be to combine data from both BA and SB
#Using this data I plan to make my own ELO system similar to EPA however I plan to make it take into account, Defensive playing, or being carried
#Possibly in the future even allowing it to take into accout SOS 


sb = statbotics.Statbotics()
current_season = '2024'

#General search function that returns basic data for a team
#Uses ba also
def search(team: int):
    dat = sb.get_team(team)
    misc = ba.getTeam(str(team))


    ret = {
        'Name': misc['name'],
        'Nickname': misc['nickname'],
        'Rookie': misc['rookie_year'],
        'Number': team,
        'EPA': dat['norm_epa'],
        'Win Rate': dat['full_winrate'],
        'Country': dat['country'],
        'Active': dat['active'],
        'State': misc['state_prov']
    }


    return ret



#gets specific data for a team per year
def get_yr(team: int, year: int):
    return sb.get_team_year(team, year)


