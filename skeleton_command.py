import bot_server
import bot
import Sheet
import Shepherd
import random

from flask import make_response

#TODO change all the "command" to the actual name of your command!
def randomize_matches(slack_event):
	# get input from slack
	text = slack_event.get("text")
	text = text.replace('#','')
	text = text.replace(' ','')
	text = text.replace(',',' ')

	# parse input and cast into int
	start, end = text.split()
	start, end = int(start), int(end)

	def get_data(start_row, end_row):
		each_row =[]
		prev_all_rows = all_rows = []
		counter = 0
		temp_start = start_row

		if start_row < end_row and end_row < 100 and start_row >= 1:
			for num in range(start_row + 1, end_row + 2):
				each_row = Sheet.get_row('Match Database', num)
				all_rows += [each_row]
			
			prev_all_rows = all_rows
			random.shuffle(all_rows)
			
			# makes sure the random.shuffle() method doesn't return the same list
			if prev_all_rows == all_rows:
				random.shuffle(all_rows)
			
			# changes the match numbers back to their original order
			for num in range(len(all_rows)):
				all_rows[num][0] = temp_start
				temp_start += 1

			for num in range(start_row + 1, end_row + 2):
				Sheet.set_row('Match Database', num, all_rows[counter])
				counter += 1

	return get_data(start, end)

 
if __name__ == '__main__':
    Sheet.SPREADSHEET_ID = '10JhC9BtpA4J-HivDTkkjpCVBLOrXIEcczChFhvbT8mQ'
    bot_server.add_function('/randomize_matches', randomize_matches)
    bot_server.app.run(threaded=True)



