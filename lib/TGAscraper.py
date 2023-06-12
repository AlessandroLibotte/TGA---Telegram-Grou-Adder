from pyrogram import Client
from random import randint


class TGAscraper:

    def __init__(self):

        self.sessions_fname: str = ""
        self.source_group: str = ""

        return

    def get_session_fname(self, fname):

        self.sessions_fname = fname

        return

    def get_source_group(self, group):

        self.source_group = group

        return

    def run(self):

        sessions_file = open(self.sessions_fname, "r")

        sessions_data = sessions_file.readlines()

        sessions_file.close()

        s_data = sessions_data[randint(0, len(sessions_data)-1)].strip('\n').split(' ')

        session = Client("Sessions/" + s_data[0], s_data[1], s_data[2], phone_number=s_data[3])

        session.start()

        session.join_chat(self.source_group)

        members = session.get_chat_members(self.source_group)

        members_file = open("Members.txt", "a")

        for member in members:

            username = str(member.user.username)

            if username != "None":

                members_file.write(username + '\n')

                print("Added member " + username + " to members list.")

        members_file.close()

        session.stop()

        return
