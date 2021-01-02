import sys
import requests
import irc.bot
import json
import os.path

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        self.counters = {'awa' : 0
        }

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)
        
    def on_welcome(self, c, e):

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            full_cmd = e.arguments[0].split(' ')
            cmd = full_cmd[0][1:]
            self.do_command(e, cmd, full_cmd)
        return

    def do_command(self, e, cmd, full_cmd):

        # Initialize request-relevant variables
        c = self.connection
        url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
        headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()


        # Poll the API to get current game.
        if cmd == "game":
            message = r['display_name'] + ' esta streamando ' + r['game']
            c.privmsg(self.channel, message)

        # Poll the API the get the current status of the stream
        elif cmd == "contato":
            message = '___________________________________________________ ___Twitter : ____ twitter.com/pedro_dsz _________ __Instagram : __ instagr.am/pedro.dsz ___________'
            c.privmsg(self.channel, message)

        # Awa counter 
        elif cmd == "awa":
            self.counters['awa'] += 1
            message = f'O Pedro bebeu {self.counters["awa"]} aguas hoje!'
            c.privmsg(self.channel, message)

        elif cmd == "awa_c":
            message = f'O Pedro bebeu {self.counters["awa"]} aguas hoje!'
            c.privmsg(self.channel, message)

        elif cmd == "so":
            try:
                message = f'Olhe o canal do {full_cmd[1]}, só ir em twitch.tv/{full_cmd[1][1:]}'
            except:
                message = f'Insira um nome valido!'
            c.privmsg(self.channel, message)

        elif cmd == "comandos":
            message = f'Comandos disponiveis: game, awa, awa_c, so, comandos'
            c.privmsg(self.channel, message)

        # The command was not recognized
        else:
            c.privmsg(self.channel, "Use !comandos para ver os comandos.")

def main():

    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

    with open('credentials.json') as json_file:
        config = json.load(json_file)
        username = config["username"]
        client_id = config["client_id"]
        token = config["token"]
        channel = config["channel"]

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()
