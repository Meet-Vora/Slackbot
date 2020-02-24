import bot_server
import bot
import Sheet
import Shepherd

from flask import make_response

def on_deck_command(slack_event):
    """
    takes in 4 teams in the form [b1#, b2#, g1#, g2#], and will then post to
    slack that those 4 teams are the next 4 up. Also changes the next match in
    the sheet to have those teams.
    """

    #generic return messages
    message = "success"
    error_message = "error"

    #small amount of input sanitization
    text = slack_event.get("text")
    text = text.replace('#','')
    text = text.replace(' ','')
    text = text.replace('b','')
    text = text.replace('g','')
    text = text.replace('B','')
    text = text.replace('G','')

    #find the arguments in the input
    start,end = 0,0
    try:
        start = text.index('[')
        end = text.index(']')
    except:
        bot.send_plain_message(error_message+'1')
        return
    #make sure that the brackets are correct
    if start >= end:
        bot.send_plain_message(error_message+'2')
        return
    text = text[start+1:end]
    teams = text.split(",")
    #make sure that exactly 4 arguments were given
    if len(teams) != 4:
        bot.send_plain_message(error_message+'3')
        return
    try:
        #make sure that the teams given are ints
        teams = [int(t) for t in teams]
    except:
        bot.send_plain_message(error_message+'4')
        return

    #get the names of the teams
    names = [Sheet.name_from_num(i) for i in teams]
    #get the correct row
    row = Sheet.get_row_of_match(Shepherd.match_number) + 1
    #get the data already in that row
    data = Sheet.get_row("Match Database", row)
    #change the data
    data[3], data[5], data[7], data[9] = names[0], names[1], names[2], names[3]
    #set the data back into the sheet
    Sheet.set_row("Match Database", row, data)

    #send a message to slack
    bot.team_numbers_on_deck(*teams)

    #retun our success message
    bot.send_plain_message(message)
    return


if __name__ == '__main__':
    #This corresponds to the sheet named "1"
    Sheet.SPREADSHEET_ID = '1pmBAG8iiPxyPT2KtsKGCDI6PIMpYwPW5bJNtW-cqeVw'
    bot_server.add_function('/on-deck', on_deck_command)
    bot_server.app.run(threaded=True)
