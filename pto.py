from imap_tools import MailBox, AND
from datetime import datetime, timedelta
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
	msg_date = msg.date
	subject = msg.subject.lower().replace("1/2 pto", "pto")
	match = re.search(" .{1,2}\/.{1,2} ", subject)

	if match:
		return match.group(0).strip()

	if "today" in subject:
		return msg_date.strftime("%#m/%d")
		
	if "tomorrow" in subject:
		return (msg_date + timedelta(days=1)).strftime("%#m/%d")

	return msg_date.strftime("%#m/%d")


# get list of email subjects from INBOX folder
with MailBox('imap.gmail.com').login(username, password, initial_folder='[Gmail]/Sent Mail') as mailbox:
	for msg in mailbox.fetch(AND(subject='PTO', sent_date_gte=first_day, sent_date_lt=last_day)):
		if any(phrase in msg.subject for phrase in subject_blacklist_phrases):
			continue

		date_str = msg.date_str
		subject = msg.subject
		pto_amount = 0
		outcome = ""
		found_date = GetDateFromMsg(msg)
		messages.append(msg)


		if any(half_day_phrase in subject.lower() for half_day_phrase in half_day_phrases):
			outcome = "Half day"
			pto_amount = 0.5

		if "&" in msg.subject:
			amount = len(msg.subject.split("&"))
			pto_amount += amount
			outcome = f"{amount} days"

		if not pto_amount:
			pto_amount = 1
			outcome = "1 day"
			
		if any(cancel_pto_phrase in subject.lower() for cancel_pto_phrase in cancel_pto_phrases):
			pto_amount = 0
			outcome = f"Cancel PTO"

		if found_date in pto_map:
			pto_map[found_date]["pto_amount"] = pto_amount
			pto_map[found_date]["reasons"].append(subject)
		else:
			pto_map[found_date] = {
				"pto_amount": pto_amount,
				"reasons": [subject],
			}

		print()
		print(f"Date:     {date_str}")
		print(f"Subject:  {subject}")
		print(f"Outcome:  {outcome} for {found_date}")
			

print()

for date, pto_info in pto_map.items():
	used_pto += pto_info["pto_amount"]
	print("Date:", date, " Amount:", pto_info["pto_amount"], " Reasons:", ", ".join([f'"{reason}"' for reason in pto_info["reasons"]] ) )


print()
print(f"Found {len(messages)} messages")
print()
print(f"Total PTO: {total_pto}")
print(f"Used PTO: {used_pto}")
print(f"PTO left: {total_pto - used_pto}")

input("\nPress enter to exit...")
