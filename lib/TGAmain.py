from random import randint
from pyrogram import Client
from time import sleep
import asyncio


class TGA:

    def __init__(self):

        self.sessions_fname: str = ""  # Name of the file containing session details

        self.sessions: list[Client] = []  # List containing the session client objects

        self.sessions_id: list[str] = []

        self.paused_sessions: list[int] = []  # List containing the paused sessions ids

        self.destination_group: str = ""  # Destination Group id

        self.quit: bool = False

        return

    def exit(self):

        self.quit = True

        return

    def set_session_fname(self, fname):

        self.sessions_fname = fname

        return

    def set_destination_group(self, gname):

        self.destination_group = gname

        return

    def set_paused_sessions(self, ps):

        self.paused_sessions = ps

    def load_sessions(self):

        sessions_file = open(self.sessions_fname, "r")
        lines = sessions_file.readlines()
        sessions_file.close()

        for s in lines:
            s = s.strip("\n")
            s = s.split(" ")

            if s[0] not in self.paused_sessions:
                self.sessions.append(Client("Sessions/" + str(s[0]), int(s[1]), str(s[2]), phone_number=str(s[3])))
                self.sessions_id.append(s[0])
                print(f"Loaded session {str(s[0])} ({str(s[3])})")
            else:
                print(f"Skipped session {str(s[0])} ({str(s[3])})")

        print()

        return

    def start_sessions(self):

        if len(self.sessions) > 0:

            for index, session in enumerate(self.sessions):
                session.start()
                print(f"Started session {self.sessions_id[index]}")

            print("\nSessions successfully started.\n")

            return True

        else:

            print("!WARNING![W01] No session to start.")

            return False

    def stop_sessions(self):

        if len(self.sessions) > 0:

            for index, session in enumerate(self.sessions):
                session.stop()
                print(f"Stopped session {self.sessions_id[index]}")

            print("\nSessions successfully stopped.\n")

        return

    def join_group(self, group: str):

        print(f"Joining group @{group}...\n")

        for index, session in enumerate(self.sessions):

            try:

                session.join_chat(group)

                print(f"Session {self.sessions_id[index]} joined.")

            except Exception as ex:

                print(f"!ERROR![E01] Session {index} failed to join. Exception: {ex.__class__.__name__}")

        return


class TGAgTg(TGA):

    def __init__(self):

        super().__init__()

        self.source_group: str = ""  # Source Group id

        return

    def set_source_group(self, gname):

        self.source_group = gname

        return

    def run(self):

        members = self.sessions[randint(0, len(self.sessions))].get_chat_members(self.source_group)

        for index, member in enumerate(members):

            session = self.sessions[index % len(self.sessions)]

            try:

                user_name = member.user.username
                session.add_chat_members(self.destination_group, user_name)

            except Exception as ex:

                print("!ERROR![E02] Failed to add " + str(member.user.username) + " to group " + self.destination_group + ". Exception: " + ex.__class__.__name__)

            else:

                print("Added " + str(user_name) + "\t DONE")

        return


class TGAmlTg(TGA):

    def __init__(self):

        super().__init__()

        self.members_fname: str = ""  # Name of the member list file

        self.timer: list[int, int] = [40, 70]  # List containing the minimum and maximum time delay

        return

    def set_members_fname(self, fname):

        self.members_fname = fname

        return

    def set_timer(self, times):

        self.timer = [int(t) for t in times]

    @staticmethod
    def _remove_member(member):

        m = None
        with open("Members.txt", "r") as f:
            m = f.readlines()
            f.close()
        with open("Members.txt", "w") as f:
            for line in m:
                if line.strip("\n") != member:
                    f.write(line)
            f.close()

    def run(self):

        members_file = open(self.members_fname, "r")

        member_list = members_file.readlines()

        members_file.close()

        print("Awaiting session connection...\n")

        if not self.start_sessions():

            return False

        self.join_group(self.destination_group)

        print("Done!\n")
        print("Starting adding routine...\n")

        for index, member in enumerate(member_list):

            if self.quit is True:

                print("Stopping Adding Routine...\n")

                break

            if len(self.sessions) < 1:

                print("All sessions suspended for this run.")
                self.quit = True

                continue

            member = member.strip("\n")

            added = False
            skip = False

            for i in range(5):
            
                if len(self.sessions) < 1:
                
                    break

                active_session = (index + i) % len(self.sessions)

                session = self.sessions[active_session]

                print(f"Addition attempt {i+1} for member {member} with Session {self.sessions_id[active_session]} ({self.sessions[active_session].phone_number})\n")

                try:

                    session.add_chat_members(self.destination_group, member)

                except Exception as ex:

                    status = ex.__class__.__name__

                    def __user_not_mutual_contact():
                        print(f"!WARNING![W02] Session {self.sessions_id[active_session]} ({self.sessions[active_session].phone_number})"
                              f" Failed to add user number {index}: {member}\t{status}")
                        print("Skipping and removing user")

                        return True

                    def __user_privacy_restrict():
                        print(f"!WARNING![W03] Session {self.sessions_id[active_session]} ({self.sessions[active_session].phone_number})"
                              f" Failed to add user number {index}: {member}\t{status}")
                        print("Skipping and removing user")

                        return True

                    def __user_banned_in_channel():

                        print(f"!WARNING![W04] Session {self.sessions_id[active_session]} ({self.sessions[active_session].phone_number})"
                              f" Failed to add user number {index}: {member}\t{status}")
                        print("Remove this session from the session file")

                        return True

                    def __connection_error():

                        print("!!ERROR!![E03] Connection error. Retrying in 15s...")

                        sleep(15)

                        return False

                    def __flood_wait():

                        print(f"!WARNING![W05] Session {self.sessions_id[active_session]} ({self.sessions[active_session].phone_number})"
                              f" Failed to add user number {index}: {member}\t{status}")

                        print(f"Session {self.sessions_id[active_session]} suspended for this run")

                        self.sessions[active_session].stop()
                        self.sessions.pop(active_session)

                        return False

                    def __peer_flood():

                        print(f"!WARNING![W06] Session {self.sessions_id[active_session]} ({self.sessions[active_session].phone_number})"
                              f" Failed to add user number {index}: {member}\t{status}")

                        print(f"Session {self.sessions_id[active_session]} suspended for this run")

                        self.sessions[active_session].stop()
                        self.sessions.pop(active_session)

                        return False

                    sort_ex = {
                        "UserNotMutualContact": __user_not_mutual_contact,
                        "UserPrivacyRestrict": __user_privacy_restrict,
                        "UserBannedInChannel": __user_banned_in_channel,
                        "ConnectionError": __connection_error,
                        "FloodWait": __flood_wait,
                        "PeerFlood": __peer_flood,
                    }

                    if status in sort_ex.keys():

                        skip = sort_ex[status]()

                    else:

                        print(f"!WARNING![W07] Session {self.sessions_id[active_session]} ({self.sessions[active_session].phone_number})"
                              f" Failed to add user number {index}: {member}\t{status}")

                        self._remove_member(member)

                    added = False

                else:

                    self._remove_member(member)

                    print(f"!DONE! Session {self.sessions_id[active_session]} ({self.sessions[active_session].phone_number})"
                          f" Successfully added user number {index}: {member}")

                    added = True

                print()

                if added is True or skip is True:

                    break

            sleep(randint(self.timer[0], self.timer[1]))

        self.stop_sessions()

        return True
