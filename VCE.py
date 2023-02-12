from mail_actions import *

def main():
    """
    Main function that handles primary choices
    """

    if isLoginCredentialsPresent():

        SpeakText(
            "Choose and speak out the option number for the task you want to perform. Say 1 to send a mail. Say 2 to get your mailbox status. Say 3 to search a mail. Say 4 to get the last 3 mails. Say 5 to delete a mail."
        )

        choice = sayChoice()

        if choice == 1:
            composeMail()
        elif choice == 2:
            getMailBoxStatus()
        elif choice == 3:
            searchMail()
        elif choice == 4:
            getLatestMails()
        elif choice == 5:
            deleteMail()

    else:
        SpeakText("Both Email ID and Password should be present")


if __name__ == "__main__":
    main()
