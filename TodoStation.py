#!/usr/bin/python
# This is the Notation Station!

# TODO:
# 1. add note
# 2. remove note
# 3. view note (by date, priority)
# 4. edit note
# 5. commandline syntax NotationStation --add, --delete, --edit, --view

# INSTALLATION NOTES
# 1. Download and install CocoaDialog.
# 2. Set USER CONFIG options below:

# USER CONFIG
DEFAULT_PRIORITY = 0
DATABASE_PATH = '/Users/matt/CodingProjects/TodoStation/storage.db'
COCOADIALOG_PATH = '/Applications/CocoaDialog.app/Contents/MacOS/CocoaDialog'
LINE2_WIDTH = 20

# For displaying data
LINE1_WIDTH = LINE2_WIDTH+(LINE2_WIDTH/3)
space2 = ""
space1 = ""
for e in range(LINE2_WIDTH/4):
	space2 = space2 + " "
for e in range(LINE1_WIDTH/4+2):
	space1 = space1+ " "
# import dependencies
import sqlite3,subprocess,sys,string,datetime,os

class Notes:
	connection = None
	cursor = None
	
	def __init__(self,database=DATABASE_PATH):
		self.connection = sqlite3.connect(database)
		self.cursor = self.connection.cursor()
	
	def close(self):
		self.cursor.close()
		
	def add(self,text='',priority=DEFAULT_PRIORITY,datedue=''):
		dtnow = datetime.datetime.now().isoformat(' ')
		query = "INSERT INTO notes (text,datetime,priority,datedue) VALUES (\"%s\",\"%s\",%i,\"%s\")" %(text,dtnow,priority,datedue)
		self.cursor.execute(query)
		self.connection.commit()
		
	def remove(self,id):
		pass
		
	def edit(self,id,text):
		query = "UPDATE notes SET text=\"%s\"  WHERE id=%s" %(text,id)
		self.cursor.execute(query)
		self.connection.commit()
		
	def view(self,query=""):
		if query == "": # view all
			query = "SELECT * FROM notes ORDER BY datedue ASC"
			self.cursor.execute(query)
		else: # view by parameters
			query = "SELECT * FROM notes WHERE %s ORDER BY datedue ASC" %(query)
			self.cursor.execute(query)
		notes = self.cursor.fetchall()
		# show notes
		# for note display: lines, and output
		line2 = ""
		line1 = ""
		for num in range(LINE2_WIDTH):
			line2 = line2+"="
		for num in range(LINE1_WIDTH):
			line1 = line1+"-"
		previousdate = ""
		tempdt = ""
		outputstring = ""
		for note in notes:
			#read date and time
			date =  str(note[1])[:10]
			time = str(note[1])[11:][:5]
			dt = note[1][:16]
			#get day of week from datedue
			datedue = note[4]
			datedt = datetime.datetime.strptime(datedue,"%Y-%m-%d")
			weekday = datedt.weekday()
			weekdays = ["Mon","Tues","Wed","Thurs","Fri","Sat","Sun"]
			weekday = weekdays[weekday]
			# get today's date
			todaydate = str(datetime.datetime.now())[:10]
			# if note due after today or today, display it
			if datedue >= todaydate:
				if date != previousdate: # its a new day
					# echo "\033[1;36mWoot\033[m"    prints blue
					# echo "\033[1;32mWoot\033[m" -- prints green
					outputstring = outputstring+line2+"\n"
					weekdate = "Due on "+weekday+", "+datedue[5:]
					outputstring = outputstring+"\033[1;36m"+weekdate+"\033[m \033[0;38\033[m"+"\n"
					
					outputstring = outputstring+line2+space2+str(note[0])+"\n"
					previousdate = date
				else:	
					outputstring = outputstring+line1+space1+str(note[0])+"\n"
				outputstring = outputstring+note[2]+"\n"
		print outputstring
	
	# helper functions
	def getactiveids(self):
		query = "SELECT id FROM notes ORDER BY datedue ASC"
		self.cursor.execute(query)
		idset = self.cursor.fetchall()
		ids = []
		for num in idset:
			ids.append(num[0])
		return ids
	
	def getnotetext(self,id):
		query = "SELECT text FROM notes WHERE id=%s" %(id)
		self.cursor.execute(query)
		text = self.cursor.fetchone()
		return text

class TodoStation:
	Notes = None
	
	def __init__(self):
		#inititalize database:
		self.Notes = Notes()
		# read input from command line
		function = sys.argv[1]
		# run function with parameters
		if function == "add":
			self.addnote()
		elif function == "edit":
			self.editnote()
		elif function == "remove":
			self.removenote()
		elif function == "prioritize":
			self.prioritizenote()
		elif function == "view":
			self.Notes.view()
		self.Notes.close()
		
	def addnote(self):
		text = subprocess.Popen([COCOADIALOG_PATH,"textbox","--button1","Save","--button2","Cancel","--editable","-float","--title","New To Do Item"],stdout=subprocess.PIPE).communicate()[0]
		if text[0] == "1":
			# get due date #
			# get days of week for upcoming 2 weeks
			tday = str(datetime.datetime.now())[:10]
			today = datetime.datetime.now().weekday()
			weekdays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
			week = []
			nextweek = []
			for each in range(14):
				if each < 7: # in current week
					if today+each < 7:
						week.append(weekdays[today+each])
					else:
						week.append(weekdays[(today+each)-7])
				else:
					for day in week:
						nextweek.append("Next "+day)
					week = week+nextweek
					break
			duedateprocess = [COCOADIALOG_PATH,"dropdown","--title","Todo By","--text","Due on","--button1","Ok","--button2","Cancel","--items"]
			duedateprocess = duedateprocess+week
			dd = subprocess.Popen(duedateprocess,stdout=subprocess.PIPE).communicate()[0]
			# get date of selected duedate
			rawduedate = int(str(tday)[8:])+int(dd[2:])
			print rawduedate
			if len(str(rawduedate)) == 1:
				rawduedate = "0"+str(rawduedate)
			newduedate = str(tday)[:8]+str(rawduedate)
			
			if dd[0] == "1": # ok selected
				self.Notes.add(string.strip(text[1:]),datedue=newduedate)
			elif dd[0] == "2": # cancel selected
				self.Notes.add(string.strip(text[1:]))
		
	def editnote(self):
		# get all note ids currently displayed	
		process = [COCOADIALOG_PATH,"dropdown","--title","Edit Note","--text","Choose Note id","--button1","Ok","--button2","Cancel","--items"]
		activeids = self.Notes.getactiveids()
		for id in activeids:
			process.append(str(id))
		choice = subprocess.Popen(process,stdout=subprocess.PIPE).communicate()[0]
		noteid = activeids[int(choice[1:])]
		# get note text
		# display text field for editing note
		notetext = self.Notes.getnotetext(noteid)
		text = subprocess.Popen([COCOADIALOG_PATH,"textbox","--button1","Save","--button2","Cancel","--editable","-float","--title","Edit To Do Item","--text","%s" %(notetext)],stdout=subprocess.PIPE).communicate()[0]
		if text[0] == "1": # save new text
			newtext = text[2:]
			self.Notes.edit(id,text)
		#self.Notes.edit(id)
		
	def removenote(self):
		pass
	
	def prioritizenote(self):
		pass
		
TodoStation()