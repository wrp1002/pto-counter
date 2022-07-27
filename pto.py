from imap_tools import MailBox, AND
from datetime import datetime
import re

username = ""
password = ""

total_pto = 18
used_pto = 0

current_year = datetime.now().year
first_day = datetime(current_year, 1, 1).date()
last_day = datetime(current_year, 12, 31).date()

subject_blacklist_phrases = {
	"Re:"
}

half_day_phrases = {
	"1/2 pto",
	"half",
}

cancel_pto_phrases = {
	"not pto",
}

messages = []
pto_map = {}

def GetDateFromMsg(msg):
	date = msg.date
	subject = msg.subject.lower().replace("1/2 pto", "pto")
	match = re.search(" .{1,2}\/.{1,2} ", subject)
	print(match)


# get list of email subjects from INBOX folder
with MailBox('imap.gmail.com').login(username, password, initial_folder='[Gmail]/Sent Mail') as mailbox:
	for msg in mailbox.fetch(AND(subject='PTO', sent_date_gte=first_day, sent_date_lt=last_day)):
		if any(phrase in msg.subject for phrase in subject_blacklist_phrases):
			continue

		date_str = msg.date_str
		subject = msg.subject
		pto_amount = 0

		GetDateFromMsg(msg)

		print(msg.date)
		print(f"\nDate:     {date_str}")
		print(f"Subject:  {subject}")
		messages.append(msg)


		if any(half_day_phrase in msg.subject.lower() for half_day_phrase in half_day_phrases):
			print("Half day")
			pto_amount = 0.5

		if "&" in msg.subject:
			amount = len(msg.subject.split("&"))
			pto_amount += amount
			print(f"{amount} days")

		if not pto_amount:
			pto_amount = 1
			print("1 day")
			
		pto_map[date_str] = {
			
		}
			
		used_pto += pto_amount


print()
print(f"Found {len(messages)} messages")
print()
print(f"Total PTO: {total_pto}")
print(f"Used PTO: {used_pto}")
print(f"PTO left: {total_pto - used_pto}")

input("\nPress enter to exit...")
