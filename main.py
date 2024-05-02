import sb_api as sb
import ba_api as ba
import discord
from discord.ext import commands
from discord import app_commands
import json
import math
import base64
import asyncio

year = 2024
guild = 1021925711344320603

def read(fileN: str):
    with open(fileN) as f:
        js = json.load(f)
        return js
    
token = read('config/config.json')['Token']



# extra calculations

def sigmoid(x, k=1, x0=0.5):
    return 1 / (1 + math.exp(-k * (x - x0)))


#NOTES
#I really dont want to use EPA for calculating ELO because I feel that its basically a loop so ill figure something else out
#I plan on using OPR to calculate ELO or maybe as a way to classify teams as either offensive or defensive
#Another problem I have with this calculation is that unlike EPA this ELO is mainly by year, meaning that If not enough games are played there will be no elo
#I could fix this by saving ELO in a global json, which really isnt bad, and then using this to compare for teams when there isnt enough data to get from
#Using EPA kind of fixes this
#Right now ELO is just an artifical adjustment of EPA to make it more accurate to recent games

def calcELO(team: str, year: int):
    search = sb.search(int(team))
    sb_year = sb.get_yr(int(team), year)
    wr = search['Win Rate']
    epaTotal = search['EPA']
    epaCurrent = sb_year['epa_end']
    score = ba.getYear_Stats(team, year)['score']
    rank = sb_year['total_epa_rank']
    percent = sb_year['total_epa_percentile']
    wr_bonus = 1
    years = year - int(search['Rookie'])

    if wr > 0.50:
        wr_bonus = 1 + sigmoid(wr, k=2)



    ELO = (epaCurrent + score) * wr_bonus * (1+percent)

    return ELO

#All i did was compare the two total elo
#THe percent is basically meningless all i did was if the elo of the other team is 2x the other one, they should win %100
#I could improve this by maybe trying a neural network
#The easiest way to improve this would be to compare average elo depending on the game, some games its harder for one team to carry, while others one team can just stomp

def calcWin(red: int, blue: int):

    if blue > red:
        winner = "Blue Alliance"
    elif red == blue:
        winner = "Coin Flip"
    else:
        winner = "Red Alliance"
    if (max(red, blue))/(min(red, blue))*50 > 100:
        chance = 100
    else:
        chance = (max(red, blue))/(min(red, blue))*50
    calc = {
        "winner": winner,
        "chance": round(chance,2)
    }
    return calc

#TODO
#Make the prediction generator just make predictions for every match at an event
#After the predictions are made store it in a json
#Then pull the games that the requested team have played in
#If I want to make it a little more optimized I will make it so that it only generates the games that a team has played in that event
#Storing that data in the json, and appending any more calls
#If i need to make another call to a team I will have to see if those games are already stored in the json, if not generate them


def generatePredictions(event: str):
    ret = []
    matches = ba.getEvent_Matches(event)
    year = int(event[:4])
    for match in matches:
        blueTeams = []
        blueTeamELO = []
        redTeams = []
        redTeamELO = []
        for team in match['alliances']['blue']['team_keys']:
            blueTeams.append(team[3:])
            blueTeamELO.append(round(calcELO(team[3:],year),2))
        for team in match['alliances']['red']['team_keys']:
            redTeams.append(team[3:])
            redTeamELO.append(round(calcELO(team[3:],year),2))
        dic = {
            'match': match['key'],
            'blueTeams': blueTeams,
            'blueTeamELO': blueTeamELO,
            'redTeams': redTeams,
            'redTeamELO': redTeamELO,
            'prediction': calcWin(sum(redTeamELO), sum(blueTeamELO))
        }
        print (f"PREDICTION DONE FOR {match['key']}\n")
        ret.append(dic)
    if ret != []:
        with open(f"data/{event}_predictions.json", 'w') as w:
            json.dump(ret, w, indent=4)
            print (f"Data written to data/{event}_predictions.json")
        return ret
    else:
        return None

# generatePredictions('2024nyli2')


def grabGames(team_number:str, event:str):
    ret = []
    try:
        data = json.load(open(f"data/{event}_predictions.json"))
        print (f'File found at data/{event}_predictions.json')
        for match in data:
            if (f'{team_number}' in match['blueTeams']) or (f'{team_number}' in match['redTeams']):
                ret.append(match)
        return ret
    except:
        print (f'No data found for {team_number} at {event} trying to generate predictions!')
        generatePredictions(event)
        print ('Re running function!')
        grabGames(team_number, event)


# print (grabGames('5736', '2024nyli2'))



#Bot Stuff

client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)


training = True

@client.event
async def on_ready():
    asyncio.create_task(update_activity())
    await tree.sync(guild=discord.Object(id=guild))
    print(f'Logged in as {client.user}')


async def update_activity():
    while True:
        data = read('data/stats.json')
        acc = int(data['Right']/(data['Total'])*100)
        if training:
            activity = f"Training {int(data['Total'])} matches..."
        else:
            activity = f"{int(data['Total'])} predictions at {acc}%"
        await client.change_presence(activity=discord.CustomActivity(name=f'{activity}'))
        await asyncio.sleep(30)

@tree.command(
    name="lookup",
    description="Look up a FRC team!",
    guild=discord.Object(id=guild)
)
async def lookup(interaction, team_number: int):

    base = ba.getIcon(str(team_number), year)

    url = f'https://www.thebluealliance.com/team/{team_number}'
    icon = f'icon.png'
    search = sb.search(team_number)
    misc = sb.get_yr(team_number, year)
    elo = ba.calcELO(str(team_number), year)


    embed=discord.Embed(title=" ", color=0x0000ff)
    embed.set_author(name=f"{team_number} ({round(misc['total_epa_percentile']*100)} percentile)", url=url)
    embed.add_field(name="Name", value=search['Nickname'], inline=True)
    embed.add_field(name="Rookie", value=search['Rookie'], inline=True)
    embed.add_field(name="Rank", value=misc['total_epa_rank'], inline=True)
    embed.add_field(name="Current EPA", value=misc['epa_end'], inline=True)
    embed.add_field(name="ELO", value=round(elo,2), inline=True)
    embed.add_field(name="Win/Loss", value=f"{round(int(search['Win Rate']*100))}%", inline=True)
    print(f'Lookup sent for team {team_number}')
    await interaction.response.send_message(embed=embed)


@tree.command(
    name='help',
    description="Get a list of commands!",
    guild=discord.Object(id=guild)
)
async def help(interaction):
    embed = discord.Embed(title="Commands",
                      colour=0x00f56a)
    embed.set_author(name="Help")

    embed.add_field(name="/lookup (team #)",
                    value="This command provides basic stats for a team. Including EPA,ELO,Rank, and more.",
                    inline=False)
    embed.add_field(name="/predict (team #) **(not done)**",
                    value="This command will predict all unplayed matches for a team.",
                    inline=False)
    embed.add_field(name="/fantasy (red1 #, red2 #, red3 #, blue1 #, blue2 #, blue3 #) **(not done)**",
                    value="Predict a hypothetical match between any 6 teams.",
                    inline=False)
    embed.add_field(name="/follow (team #) **(not done)**",
                    value="Follow a team to get updates on upcoming matches, unfollow with /unfollow",
                    inline=False)
    embed.add_field(name="/frcguessr **(not done)**",
                    value="A mini game where you have to guess the robot, game piece, or field element",
                    inline=False)

    embed.set_footer(text="Version 1.0")

    await interaction.response.send_message(embed=embed)


#embed for predicted matches, possibly make it so you can follow a team and have it auto show the next match
@tree.command(
    name='predict',
    description='Predict all matches for a team at a given event',
    guild=discord.Object(id=guild)
)
async def predict(interaction, team_number: int, event: str):
    print ('Predict Command Recieved')
    channel = interaction.channel


    try:
        matches = grabGames(team_number, event)

        for match in matches:
            embed = discord.Embed(title=f"Winner ({match['prediction']['winner']}) (%{match['prediction']['chance']})",
                                colour=0xf500d4, url=f"https://www.statbotics.io/match/{match['match']}")

            embed.set_author(name=f"{match['match']}",
                            url=f"https://www.thebluealliance.com/match/{match['match']}",
                            icon_url="https://www.thebluealliance.com/images/tba_lamp.svg")

            for team_color in ['red', 'blue']:
                team = match[f'{team_color}Teams']
                team_elo = match[f'{team_color}TeamELO']
        
                for i in range(3):
                    embed.add_field(
                        name=f"{team[i]}",
                        value=f"{team_elo[i]} ELO",
                        inline=True
                    )
            
            await channel.send(embed=embed)
    except:
        await channel.send(f'{team_number} has not played in {event}')

client.run(token)
