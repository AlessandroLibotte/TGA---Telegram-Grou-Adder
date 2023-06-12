from pyrogram import Client
from pyrogram.errors import RPCError
from os import path, mkdir


class TGAsessions:

    def __init__(self):

        self.sessions_fname: str = ""

        return

    def get_session_fname(self, fname):

        self.sessions_fname = fname

        return

    def run(self):

        session_file = open(self.sessions_fname, "r")

        sessions_data = session_file.readlines()

        session_file.close()

        if path.isdir("Sessions/") is False:

            mkdir("Sessions")

        for s_data in sessions_data:

            s_data = s_data.strip('\n')
            s_data = s_data.split(' ')

            session = Client("Sessions/" + s_data[0], int(s_data[1]), s_data[2], phone_number=s_data[3])

            try:

                session.start()
                session.send_message("me", "This account session id is " + s_data[0])
                session.stop()
                print("Session number " + s_data[0] + " on phone number " + s_data[3] + " created !")

            except RPCError:

                print("Session number " + s_data[0] + " on phone number " + s_data[3] + " is banned. Removing...")

                out = open(self.sessions_fname, "w")

                for s in sessions_data:

                    if s[0] != s_data[0]:

                        out.write(' '.join(s) + '\n')

                out.close()

        return
