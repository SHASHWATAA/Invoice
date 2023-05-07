from pandas import DataFrame as df
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import smtplib
import datetime
import webbrowser


def getstarttime(argsSplit):
    startPMflag = False

    # manipulate startime
    starttime = argsSplit[1]

    # check if startime is in PM. needed to calculate total hour further
    if "p" in starttime:
        startPMflag = True
        starttime = starttime.replace("p", "")

    if not starttime.isdigit():
        print(" start time nai wrong halis babu extra alphabet bhayo. pheri try gar")
        return "continue"

    if len(starttime) == 1 or len(starttime) == 2:
        starttime = "0" + str(starttime)
        starttime = int(starttime[-2:])

    elif len(starttime) == 3 or len(starttime) == 4:
        starttime = "0" + str(starttime)
        starttime = (starttime[-4:])
        temphour = starttime[0:2]
        tempmin = int(starttime[-2:]) / 60
        tempstarttime = int(temphour) + tempmin
        starttime = tempstarttime
    else:
        print(" start time nai wrong halis babu. pheri try gar")
        return "continue"

    if startPMflag and str(starttime)[0:2] != "12":
        starttime = starttime + 12

    return starttime


def getendtime(argsSplit):
    endAMflag = False

    # manipulate startime
    endtime = argsSplit[2]

    # check if startime is in AM. needed to calculate total hour further
    if "a" in endtime:
        endAMflag = True
        endtime = endtime.replace("a", "")

    if not endtime.isdigit():
        print(" end time nai wrong halis babu extra alphabet bhayo. pheri try gar")
        return "continue"

    if len(endtime) == 1 or len(endtime) == 2:
        endtime = "0" + str(endtime)
        endtime = int(endtime[-2:])

    elif len(endtime) == 3 or len(endtime) == 4:
        endtime = "0" + str(endtime)
        endtime = (endtime[-4:])
        temphour = endtime[0:2]
        tempmin = int(endtime[-2:]) / 60
        tempendtime = int(temphour) + tempmin
        endtime = tempendtime
    else:
        print(" start time nai wrong halis babu. pheri try gar")
        return "continue"

    if not endAMflag and endtime < 12:
        endtime = endtime + 12

    return endtime


def parsechanges(defaultTime):
    args = ""

    while args != "clear":
        args = input("enter changes: ")
        # print(args)

        # break when you see dd don't need to check anything else
        if args == "clear" or args == "dd":
            break

        # check if help is asked
        if args == "help":
            print("""
example: 	_ _ (DAY) 			_ _ _ _ (START TIME) 			_ _ _ _ (END TIME)

		 	mo -> Monday		915		(for 9:15 start)		0515 	(for 05:15 end)
		 	tu -> Tuesday		10		(for 10 start)			05 		(for 5 end)
		 	we -> Wednesday		1p		(for 1pm start)			11a 	(for 11am end )
		 	th -> Thursday		115p	(for 1:15 pm start)
		 	fr -> Friday
		 	sa -> Saturday
		 	su -> Sunday

				""")
            continue

        argsSplit = args.split(" ")

        # check syntax
        if len(argsSplit) != 3 and len(argsSplit) != 2:
            print("invalid input. Syntax ('day' 'start time' 'end time'). input help for examples.")
            continue

        if len(argsSplit[0]) != 3:
            print("invalid day input. Syntax ('day' 'start time' 'end time'). input help for examples.")
            continue

        starttime = getstarttime(argsSplit)

        if starttime == "continue":
            continue

        # print (starttime)

        endtime = getendtime(argsSplit)
        # print (endtime)

        # change appropriate day's time
        if argsSplit[0] == 'mon':
            defaultTime[0] = (starttime, endtime)
        if argsSplit[0] == 'tue':
            defaultTime[1] = (starttime, endtime)
        if argsSplit[0] == 'wed':
            defaultTime[2] = (starttime, endtime)
        if argsSplit[0] == 'thu':
            defaultTime[3] = (starttime, endtime)
        if argsSplit[0] == 'fri':
            defaultTime[4] = (starttime, endtime)
        if argsSplit[0] == 'sat':
            defaultTime[5] = (starttime, endtime)
        if argsSplit[0] == 'sun':
            defaultTime[6] = (starttime, endtime)

    # print(defaultTime)

    return defaultTime


def weektype(defaultTime):
    errorflag = True

    while errorflag == True:
        errorflag = False
        weektype = input("""
1. Non-Market
2. Market
3. Weird
Select week: """)
        try:
            weektype = int(weektype)
        except ValueError:
            print("error. Wront input. Try again.")
            errorflag = True
            continue;

        if weektype == 1:
            defaultTime[6] = 0
            defaultTime[5] = 0
        elif weektype == 2:
            defaultTime[2] = 0
            defaultTime[3] = 0
        elif weektype == 3:
            offdays = input("type days off seperated by space: ")
            argsSplit = offdays.split(" ")
            for args in argsSplit:
                # change appropriate day's time
                if args == 'mon':
                    defaultTime[0] = 0
                if args == 'tue':
                    defaultTime[1] = 0
                if args == 'wed':
                    defaultTime[2] = 0
                if args == 'thu':
                    defaultTime[3] = 0
                if args == 'fri':
                    defaultTime[4] = 0
                if args == 'sat':
                    defaultTime[5] = 0
                if args == 'sun':
                    defaultTime[6] = 0
        else:
            print("error. Wront input. Try again.")
            errorflag = True

        return defaultTime


def createtable(times):
    headings = ['Day', 'Time Started', 'Time Ended', 'Break', 'Hours']
    day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hlog = []
    count = 0
    for time in times:
        if time != 0:
            if count == 5 or count == 6:
                breakh = 0
            else:
                breakh = 0.5

            hours = time[1] - time[0] - breakh

            if hours < 7.5:
                hours = hours + 0.5
                breakh = 0

            log = (day[count], time[0], time[1], breakh, hours)
            hlog.append(log)

        count = count + 1

    print(hlog)
    table = df.from_records(hlog, columns=headings)
    return table


def send_email(DATA, sum):
    # me == my email address
    # you == recipient's email address
    me = "shashwat221@gmail.com"
    you = "shashwat221@gmail.com"

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Hours for last week"
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).
    text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = "<html><head></head><body>" + DATA.to_html() + "<br><b> Total hours: " + str(sum) + "</b></body></html>"

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login('shashwat221@gmail.com', 'adsbshiflcpiikfm')
    mail.sendmail(me, you, msg.as_string())
    mail.quit()


if __name__ == '__main__':
    x = datetime.datetime.now()
    date = x.strftime("%Y-%m-%d")
    link = "https://www.google.com/maps/timeline?pb=!1m2!1m1!1s" + date
    webbrowser.open(link, new=0, autoraise=True)

    defaultTime = [(9, 17), (9, 17), (9, 12.25), (9, 12.25), (9, 17), (7.5, 14.5), (7.5, 16.5)]

    defaultTime = weektype(defaultTime)

    times = parsechanges(defaultTime)

    table = createtable(times)
    sum = table['Hours'].sum()
    # table

    send_email(table, sum)
