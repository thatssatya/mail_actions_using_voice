import smtplib
import email
import imaplib
from email.header import decode_header
from utils import *

def sendMail(sendTo, msg):
    """
    To send a mail

    Args:
        sendTo (list): List of mail targets
        msg (str): Message
    """
    mail = smtplib.SMTP("smtp.gmail.com", 587)  # host and port
    # Hostname to send for this command defaults to the FQDN of the local host.
    mail.ehlo()
    mail.starttls()  # security connection
    mail.login(EMAIL_ID, PASSWORD)  # login part
    for person in sendTo:
        mail.sendmail(EMAIL_ID, person, msg)  # send part
        print("Mail sent successfully to " + person)
    mail.close()


def composeMail():
    """
    Compose and create a Mail

    Returns:
        None: None
    """
    SpeakText(
        "Mention the gmail ID of the persons to whom you want to send a mail. Email IDs should be separated with the word, AND."
    )

    receivers = speech_to_text()
    receivers = receivers.replace("at the rate", "@")
    emails = receivers.split(" and ")
    index = 0
    for email in emails:
        emails[index] = email.replace(" ", "")
        index += 1

    SpeakText(
        "The mail will be send to "
        + (" and ".join([str(elem) for elem in emails]))
        + ". Confirm by saying YES or NO."
    )

    confirmMailList = confirmChoice()

    if confirmMailList.lower() != "yes":
        SpeakText("Operation cancelled by the user")
        return None

    SpeakText("Say your message")
    msg = speech_to_text()

    SpeakText("You said  " + msg + ". Confirm by saying YES or NO.")
    # confirmMailBody = speech_to_text()

    confirmMailBody = confirmChoice()

    if confirmMailBody.lower() == "yes":
        SpeakText("Message sent")
        sendMail(emails, msg)
    else:
        SpeakText("Operation cancelled by the user")
        return None


def getMailBoxStatus():
    """
    Get mail counts of all folders in the mailbox
    """
    # host and port (ssl security)
    M = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    M.login(EMAIL_ID, PASSWORD)  # login

    for i in M.list()[1]:
        l = i.decode().split(' "/" ')
        if l[1] == '"[Gmail]"':
            continue

        stat, total = M.select(f"{l[1]}")
        l[1] = l[1][1:-1]
        messages = int(total[0])
        if l[1] == "INBOX":
            SpeakText(l[1] + " has " + str(messages) + " messages.")
        else:
            SpeakText(l[1].split("/")[-1] + " has " + str(messages) + " messages.")

    M.close()
    M.logout()

def searchMail():
    """
    Search mails by subject / author mail ID

    Returns:
        None: None
    """
    M = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    M.login(EMAIL_ID, PASSWORD)

    mailBoxTarget = "INBOX"
    SpeakText(
        "Where do you want to search ? Say 1 for Inbox. Say 2 for Sent Mailbox. Say 3 for Drafts. Say 4 for important mails. Say 5 for Spam. Say 6 for Starred Mails. Say 7 for Bin."
    )
    cmb = speech_to_text()
    if cmb == "1" or cmb.lower() == "one":
        mailBoxTarget = "INBOX"
        SpeakText("Inbox selected.")
    elif cmb == "2" or cmb.lower() == "two" or cmb.lower() == "tu":
        mailBoxTarget = '"[Gmail]/Sent Mail"'
        SpeakText("Sent Mailbox selected.")
    elif cmb == "3" or cmb.lower() == "three":
        mailBoxTarget = '"[Gmail]/Drafts"'
        SpeakText("Drafts selected.")
    elif cmb == "4" or cmb.lower() == "four":
        mailBoxTarget = '"[Gmail]/Important"'
        SpeakText("Important Mails selected.")
    elif cmb == "5" or cmb.lower() == "five":
        mailBoxTarget = '"[Gmail]/Spam"'
        SpeakText("Spam selected.")
    elif cmb == "6" or cmb.lower() == "six":
        mailBoxTarget = '"[Gmail]/Starred"'
        SpeakText("Starred Mails selected.")
    elif cmb == "7" or cmb.lower() == "seven":
        mailBoxTarget = '"[Gmail]/Bin"'
        SpeakText("Bin selected.")
    else:
        SpeakText("Wrong choice. Hence, default option Inbox wil be selected.")

    M.select(mailBoxTarget)

    SpeakText(
        "Say 1 to search mails from a specific sender. Say 2 to search mail with respect to the subject of the mail."
    )
    mailSearchChoice = speech_to_text()
    if mailSearchChoice == "1" or mailSearchChoice.lower() == "one":
        SpeakText("Please mention the sender email ID you want to search.")
        searchSub = speech_to_text()
        searchSub = searchSub.replace("at the rate", "@")
        searchSub = searchSub.replace(" ", "")
        status, messages = M.search(None, f'FROM "{searchSub}"')
    elif (
        mailSearchChoice == "2"
        or mailSearchChoice.lower() == "two"
        or mailSearchChoice.lower() == "tu"
    ):
        SpeakText("Please mention the subject of the mail you want to search.")
        searchSub = speech_to_text()
        status, messages = M.search(None, f'SUBJECT "{searchSub}"')
    else:
        SpeakText(
            "Wrong choice. Performing default operation. Please mention the subject of the mail you want to search."
        )
        searchSub = speech_to_text()
        status, messages = M.search(None, f'SUBJECT "{searchSub}"')

    if str(messages[0]) == "b''":
        SpeakText(f"Mail not found in {mailBoxTarget}.")
        return None

    msgCount = 1
    for i in messages:
        SpeakText(f"Message {msgCount}:")
        res, msg = M.fetch(i, "(RFC822)")  # fetch the email message by ID
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(
                    response[1]
                )  # parse a bytes email into a message object

                subject, encoding = decode_header(msg["Subject"])[
                    0
                ]  # decode the email subject
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding)  # if it's a bytes, decode to str

                From, encoding = decode_header(msg.get("From"))[
                    0
                ]  # decode email sender
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                SpeakText("Subject: " + subject)
                FromArr = From.split()
                FromName = " ".join(namechar for namechar in FromArr[0:-1])
                SpeakText("From: " + FromName)
                SpeakText("Sender mail: " + FromArr[-1])

                # MULTIPART
                if msg.is_multipart():
                    for part in msg.walk():  # iterate over email parts
                        content_type = (
                            part.get_content_type()
                        )  # extract content type of email
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(
                                decode=True
                            ).decode()  # get the email body
                        except:
                            pass

                        # PLAIN TEXT MAIL
                        if (
                            content_type == "text/plain"
                            and "attachment" not in content_disposition
                        ):
                            SpeakText(
                                "Do you want to listen to the text content of the mail ? Please say YES or NO."
                            )
                            talkMSG1 = speech_to_text()
                            if "yes" in talkMSG1.lower():
                                SpeakText("The mail body contains the following:")
                                SpeakText(body)
                            else:
                                SpeakText("You chose NO")

                        # MAIL WITH ATTACHMENT
                        elif "attachment" in content_disposition:
                            SpeakText(
                                "The mail contains attachment, the contents of which will be saved in respective folders with it's name similar to that of subject of the mail"
                            )
                            filename = part.get_filename()  # download attachment
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    os.mkdir(
                                        folder_name
                                    )  # make a folder for this email (named after the subject)
                                filepath = os.path.join(folder_name, filename)
                                open(filepath, "wb").write(
                                    part.get_payload(decode=True)
                                )  # download attachment and save it

                # NOT MULTIPART
                else:
                    content_type = (
                        msg.get_content_type()
                    )  # extract content type of email
                    body = msg.get_payload(decode=True).decode()  # get the email body
                    if content_type == "text/plain":
                        SpeakText(
                            "Do you want to listen to the text content of the mail ? Please say YES or NO."
                        )
                        talkMSG2 = speech_to_text()
                        if "yes" in talkMSG2.lower():
                            SpeakText("The mail body contains the following:")
                            SpeakText(body)
                        else:
                            SpeakText("You chose NO")

                # HTML CONTENTS
                if content_type == "text/html":
                    SpeakText(
                        "The mail contains an HTML part, the contents of which will be saved in respective folders with it's name similar to that of subject of the mail. You can view the html files in any browser, simply by clicking on them."
                    )
                    # if it's HTML, create a new HTML file
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        os.mkdir(
                            folder_name
                        )  # make a folder for this email (named after the subject)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    open(filepath, "w").write(body)

                    # webbrowser.open(filepath)     # open in the default browser

                SpeakText(f"\nEnd of message {msgCount}:")
                msgCount += 1
                print("=" * 100)

    M.close()
    M.logout()


def getLatestMails():
    """
    Get latest mails from folders in mailbox (Defaults to 3 Inbox mails)
    """
    mailBoxTarget = "INBOX"
    SpeakText(
        "Choose the folder name to get the latest mails. Say 1 for Inbox. Say 2 for Sent Mailbox. Say 3 for Drafts. Say 4 for important mails. Say 5 for Spam. Say 6 for Starred Mails. Say 7 for Bin."
    )
    cmb = speech_to_text()
    if cmb == "1" or cmb.lower() == "one":
        mailBoxTarget = "INBOX"
        SpeakText("Inbox selected.")
    elif cmb == "2" or cmb.lower() == "two" or cmb.lower() == "tu":
        mailBoxTarget = '"[Gmail]/Sent Mail"'
        SpeakText("Sent Mailbox selected.")
    elif cmb == "3" or cmb.lower() == "three":
        mailBoxTarget = '"[Gmail]/Drafts"'
        SpeakText("Drafts selected.")
    elif cmb == "4" or cmb.lower() == "four":
        mailBoxTarget = '"[Gmail]/Important"'
        SpeakText("Important Mails selected.")
    elif cmb == "5" or cmb.lower() == "five":
        mailBoxTarget = '"[Gmail]/Spam"'
        SpeakText("Spam selected.")
    elif cmb == "6" or cmb.lower() == "six":
        mailBoxTarget = '"[Gmail]/Starred"'
        SpeakText("Starred Mails selected.")
    elif cmb == "7" or cmb.lower() == "seven":
        mailBoxTarget = '"[Gmail]/Bin"'
        SpeakText("Bin selected.")
    else:
        SpeakText("Wrong choice. Hence, default option Inbox wil be selected.")

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL_ID, PASSWORD)

    status, messages = imap.select(mailBoxTarget)

    messages = int(messages[0])

    if messages == 0:
        SpeakText("Selected MailBox is empty.")
        return None
    elif messages == 1:
        N = 1  # number of top emails to fetch
    elif messages == 2:
        N = 2  # number of top emails to fetch
    else:
        N = 3  # number of top emails to fetch

    msgCount = 1
    for i in range(messages, messages - N, -1):
        SpeakText(f"Message {msgCount}:")
        res, msg = imap.fetch(str(i), "(RFC822)")  # fetch the email message by ID
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(
                    response[1]
                )  # parse a bytes email into a message object

                subject, encoding = decode_header(msg["Subject"])[
                    0
                ]  # decode the email subject
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding)  # if it's a bytes, decode to str

                From, encoding = decode_header(msg.get("From"))[
                    0
                ]  # decode email sender
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                SpeakText("Subject: " + subject)
                FromArr = From.split()
                FromName = " ".join(namechar for namechar in FromArr[0:-1])
                SpeakText("From: " + FromName)
                SpeakText("Sender mail: " + FromArr[-1])
                SpeakText("The mail says or contains the following:")

                # MULTIPART
                if msg.is_multipart():
                    for part in msg.walk():  # iterate over email parts
                        content_type = (
                            part.get_content_type()
                        )  # extract content type of email
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(
                                decode=True
                            ).decode()  # get the email body
                        except:
                            pass

                        # PLAIN TEXT MAIL
                        if (
                            content_type == "text/plain"
                            and "attachment" not in content_disposition
                        ):
                            SpeakText(
                                "Do you want to listen to the text content of the mail ? Please say YES or NO."
                            )
                            talkMSG1 = speech_to_text()
                            if "yes" in talkMSG1.lower():
                                SpeakText("The mail body contains the following:")
                                SpeakText(body)
                            else:
                                SpeakText("You chose NO")

                        # MAIL WITH ATTACHMENT
                        elif "attachment" in content_disposition:
                            SpeakText(
                                "The mail contains attachment, the contents of which will be saved in respective folders with it's name similar to that of subject of the mail"
                            )
                            filename = part.get_filename()  # download attachment
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    os.mkdir(
                                        folder_name
                                    )  # make a folder for this email (named after the subject)
                                filepath = os.path.join(folder_name, filename)
                                open(filepath, "wb").write(
                                    part.get_payload(decode=True)
                                )  # download attachment and save it

                # NOT MULTIPART
                else:
                    content_type = (
                        msg.get_content_type()
                    )  # extract content type of email
                    body = msg.get_payload(decode=True).decode()  # get the email body
                    if content_type == "text/plain":
                        SpeakText(
                            "Do you want to listen to the text content of the mail ? Please say YES or NO."
                        )
                        talkMSG2 = speech_to_text()
                        if "yes" in talkMSG2.lower():
                            SpeakText("The mail body contains the following:")
                            SpeakText(body)
                        else:
                            SpeakText("You chose NO")

                # HTML CONTENTS
                if content_type == "text/html":
                    SpeakText(
                        "The mail contains an HTML part, the contents of which will be saved in respective folders with it's name similar to that of subject of the mail. You can view the html files in any browser, simply by clicking on them."
                    )
                    # if it's HTML, create a new HTML file
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        os.mkdir(
                            folder_name
                        )  # make a folder for this email (named after the subject)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    open(filepath, "w").write(body)

                    # webbrowser.open(filepath)     # open in the default browser

                SpeakText(f"\nEnd of message {msgCount}:")
                msgCount += 1
                print("=" * 100)
    imap.close()
    imap.logout()


def deleteMail():
    M = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    M.login(EMAIL_ID, PASSWORD)

    mailBoxTarget = "INBOX"
    SpeakText(
        "From where do you want to delete the mail ? Say 1 for Inbox. Say 2 for Sent Mailbox. Say 3 for Drafts. Say 4 for important mails. Say 5 for Spam. Say 6 for Starred Mails. Say 7 for Bin."
    )
    cmb = speech_to_text()
    if cmb == "1" or cmb.lower() == "one":
        mailBoxTarget = "INBOX"
        SpeakText("Inbox selected.")
    elif cmb == "2" or cmb.lower() == "two" or cmb.lower() == "tu":
        mailBoxTarget = '"[Gmail]/Sent Mail"'
        SpeakText("Sent Mailbox selected.")
    elif cmb == "3" or cmb.lower() == "three":
        mailBoxTarget = '"[Gmail]/Drafts"'
        SpeakText("Drafts selected.")
    elif cmb == "4" or cmb.lower() == "four":
        mailBoxTarget = '"[Gmail]/Important"'
        SpeakText("Important Mails selected.")
    elif cmb == "5" or cmb.lower() == "five":
        mailBoxTarget = '"[Gmail]/Spam"'
        SpeakText("Spam selected.")
    elif cmb == "6" or cmb.lower() == "six":
        mailBoxTarget = '"[Gmail]/Starred"'
        SpeakText("Starred Mails selected.")
    elif cmb == "7" or cmb.lower() == "seven":
        mailBoxTarget = '"[Gmail]/Bin"'
        SpeakText("Bin selected.")
    else:
        SpeakText("Wrong choice. Hence, default option Inbox wil be selected.")

    M.select(mailBoxTarget)

    SpeakText(
        "Say 1 to delete mail from a specific sender. Say 2 to delete mail with respect to the subject of the mail.  "
    )
    mailSearchChoice = speech_to_text()
    if mailSearchChoice == "1" or mailSearchChoice.lower() == "one":
        SpeakText("Please mention the sender email ID you want to Delete.")
        searchSub = speech_to_text()
        searchSub = searchSub.replace("at the rate", "@")
        searchSub = searchSub.replace(" ", "")
        status, messages = M.search(None, f'FROM "{searchSub}"')
    elif (
        mailSearchChoice == "2"
        or mailSearchChoice.lower() == "two"
        or mailSearchChoice.lower() == "tu"
    ):
        SpeakText("Please mention the subject of the mail you want to Delete.")
        searchSub = speech_to_text()
        status, messages = M.search(None, f'SUBJECT "{searchSub}"')
    else:
        SpeakText(
            "Wrong choice. Performing default operation. Please mention the subject of the mail you want to Delete."
        )
        searchSub = speech_to_text()
        status, messages = M.search(None, f'SUBJECT "{searchSub}"')

    if str(messages[0]) == "b''":
        SpeakText(f"Mail not found in {mailBoxTarget}.")
        return None

    messages = messages[0].split(b" ")

    for mail in messages:
        _, msg = M.fetch(mail, "(RFC822)")
        # you can delete the for loop for performance if you have a long list of emails
        # because it is only for printing the SUBJECT of target email to delete
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    # if it's a bytes type, decode to str
                    subject = subject.decode()
                print("Deleting", subject)
                SpeakText("Mail subject saying " + subject + " is deleted")
        # mark the mail as deleted
        M.store(mail, "+FLAGS", "\\Deleted")

    M.expunge()
    M.close()
    M.logout()
