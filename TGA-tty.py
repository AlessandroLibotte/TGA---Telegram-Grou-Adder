import random
import time

from lib.TGAmain import TGAgTg, TGAmlTg
from lib.TGAsessions import TGAsessions
from lib.TGAscraper import TGAscraper


class TGAtty:

    def __init__(self):

        self.page_id = 0

        self.paused_sessions: list = []
        self.session_fname: str = ""

        self.gtg = TGAgTg()
        self.mltg = TGAmlTg()

        self._sort_menu_page = {
            0: self._main_page,
            1: self._set_session_fname,
            2: self._create_sessions,
            3: self._pause_sessions,
            4: self._gtg_menu,
            5: self._mltg_menu,
            6: self._gtg_settings_page,
            7: self._mltg_scrape,
            8: self._mltg_settings_page,
            99: exit
        }

        self._sort_run = {
            5: self._gtg_run,
            6: self._mltg_run
        }

        self._sort_settings_submenu_page = {
            7: self._gtg_settings_source,
            8: self._gtg_settings_destination,
            9: self._mltg_settings_timer,
            10: self._mltg_settings_mlfname,
            11: self._mltg_settings_destination,
        }

        self._load_config()

        return

    def _load_config(self):

        try:
            file = open("config.conf", "r")
        except FileNotFoundError:
            return
        else:

            get_line = lambda line: line.strip("\n").split(" ")

            params = [get_line(line)[0] if len(get_line(line)) <= 1 else get_line(line) for line in file.readlines()]

            self.session_fname = params[1]
            self.paused_sessions = params[2][:-1]
            self.mltg.set_timer(params[3][:-1])
            self.mltg.set_members_fname(params[4])
            self.mltg.set_destination_group(params[5])

    def _check_requirements(self, i):

        if i:

            if self.page_id < 2:

                return True

            if self.session_fname == "":

                print("\nYou must set a session filename before accessing other features.")

                return False

            return True

        else:

            if self.page_id == 5:

                if self.gtg.destination_group == "":

                    print("\nYou must set a destination group before starting the adding routine")

                    return False

                if self.gtg.source_group == "":

                    print("\nYou must set a source group before starting the adding routine")

                    return False

            if self.page_id == 6:

                if self.mltg.members_fname == "":

                    print("\nYou must set a member list file before starting the adding routine.")

                    return False

                if self.mltg.destination_group == "":

                    print("\nYou must set a destination group before starting the adding routine")

                    return False

            return True

    def menu(self):

        print("\nWelcome to TGA - Telegram Group Adder (version 7.4)")

        _old_i = []

        while True:

            if len(_old_i) < 3:

                if len(_old_i) == 2 and _old_i[-1] == 1:

                    if self._check_requirements(0) is True:

                        _sm = self._sort_run[self.page_id]() if self.page_id in self._sort_run.keys() else False

                    else:

                        _sm = False

                else:

                    if len(_old_i) == 1 and self.page_id > 5 and self.page_id != 99:

                        _sm = False

                    else:

                        if self._check_requirements(1) is True:

                            _sm = self._sort_menu_page[self.page_id]() if self.page_id in self._sort_menu_page.keys() else False

                        else:

                            _sm = False

            else:

                _sm = self._sort_settings_submenu_page[self.page_id]() if self.page_id in self._sort_settings_submenu_page.keys() else False

            if _sm is True:

                _i = input("\n\n: ")

                if _i.isdigit() is True:

                    _i = int(_i)

                    if _i != 0:

                        self.page_id = self.page_id + _i

                        _old_i.append(_i)

                    else:

                        self.page_id = self.page_id - _old_i[-1]

                        _old_i.pop(-1)

            else:

                self.page_id -= _old_i[-1]

                _old_i.pop(-1)

    @staticmethod
    def _main_page():

        print("\nMain Menu:"
              "\n\n\t1) Set Sessions File"
              "\n\n\t2) Create Sessions"
              "\n\n\t3) Pause Sessions"
              "\n\n\t4) Group to Group Add"
              "\n\n\t5) Member List to Group Add"
              "\n\n\t99) Exit")

        return True

    def _create_sessions(self):

        print("\nCreating sessions\n")

        session_creator = TGAsessions()
        session_creator.get_session_fname(self.session_fname)
        session_creator.run()

        return False

    def _pause_sessions(self):

        print("\nInsert session ids separated by space to pause (es: 3 6 9)\nCurrently Paused Session: ", end='')
        if len(self.paused_sessions) != 0:
            [print(i, end=' ') for i in self.paused_sessions]
        else:
            print("None", end=' ')
        print(". Leave empty to activate all. Type 'b' to bo back.")

        _in = input("\n: ").split(" ")

        if _in != ["b"]:
            self.paused_sessions = _in
        if _in == ['']:
            self.paused_sessions = []

        return False

    def _set_session_fname(self):

        _in = input("\nInsert the name of the desired sessions file to use"
                    "\nCurrent Session Filename: " +
                    (self.session_fname if self.session_fname != "" else "None") +
                    ". Type 'b' to bo back.\n\n: ")
        if _in != "b":
            self.session_fname = _in

        return False

    @staticmethod
    def _gtg_menu():

        print("\nGroup to Group Add - Menu:"
              "\n\n\t1) Run"
              "\n\n\t2) Settings"
              "\n\n\t0) Back")

        return True

    @staticmethod
    def _gtg_run(self):

        print("\nStarting Group to Group Add")

        return False

    @staticmethod
    def _gtg_settings_page():

        print("\nGroup to Group Add - Settings:"
              "\n\n\t1) Set Source Group"
              "\n\n\t2) Set Destination Group"
              "\n\n\t0) Back")

        return True

    def _gtg_settings_source(self):

        _in = input("\nInsert the id of the source group to use"
                    "\nCurrent Source Group: " +
                    (self.gtg.source_group if self.gtg.source_group != "" else "None") +
                    ". Type 'b' to bo back.\n\n: ")
        if _in != "b":
            self.gtg.set_source_group(_in)

        return False

    def _gtg_settings_destination(self):

        _in = input("\nInsert the id of the destination group to use"
                    "\nCurrent Destination Group: " +
                    (self.gtg.destination_group if self.gtg.destination_group != "" else "None") +
                    ". Type 'b' to bo back.\n\n: ")
        if _in != "b":
            self.gtg.set_destination_group(_in)

        return False

    @staticmethod
    def _mltg_menu():

        print("\nMember List to Group Add - Menu:"
              "\n\n\t1) Run"
              "\n\n\t2) Scrape Users from Group"
              "\n\n\t3) Settings"
              "\n\n\t0) Back")

        return True

    def _mltg_run(self):

        self._save_config()

        self.mltg.set_session_fname(self.session_fname)
        self.mltg.set_paused_sessions(self.paused_sessions)

        while True:

            self.mltg.quit = False

            self.mltg.load_sessions()

            if not self.mltg.run():

                break

            else:

                print("Pausing adding routine for 24/26h\n")
                time.sleep(random.randint(86400, 93600))

        return False

    def _mltg_scrape(self):

        source_group = input("\nProvide a group id to scrape the users from.\n\n: ")

        print("\nScraping Members\n")

        member_scraper = TGAscraper()

        member_scraper.get_session_fname(self.session_fname)
        member_scraper.get_source_group(source_group)

        member_scraper.run()

        self.mltg.set_members_fname("Members.txt")

        return False

    @staticmethod
    def _mltg_settings_page():

        print("\nMember List to Group Add - Settings:"
              "\n\n\t1) Set timer"
              "\n\n\t2) Set Member List File"
              "\n\n\t3) Set Destination Group"
              "\n\n\t0) Back")

        return True

    def _mltg_settings_timer(self):

        _in = input("\nInsert minimum time delay and maximum time delay separated by space (es: 40 70)"
                    "\nCurrent Time Delay: " + str(self.mltg.timer[0]) + " " + str(self.mltg.timer[1]) + "."
                    " Type 'b' to bo back.\n\n: ").split(" ")
        if _in != ["b"]:
            self.mltg.set_timer(_in)

        return False

    def _mltg_settings_mlfname(self):

        _in = input("\nInsert the name of the desired member list file to use"
                    "\nCurrent Member List Filename: " +
                    (self.mltg.members_fname if self.mltg.members_fname != "" else "None") +
                    ". Type 'b' to bo back.\n\n: ")
        if _in != "b":
            self.mltg.set_members_fname(_in)

        return False

    def _mltg_settings_destination(self):

        _in = input("\nInsert the id of the destination group to use"
                    "\nCurrent Destination Group: " +
                    (self.mltg.destination_group if self.mltg.destination_group != "" else "None") +
                    ". Type 'b' to bo back.\n\n: ")
        if _in != "b":
            self.mltg.set_destination_group(_in)

        return False

    def _save_config(self):

        print("\nSaving configuration...")

        with open("config.conf", 'w') as file:
            file.write("mltg" + "\n")
            file.write(self.session_fname + "\n")
            [file.write(i + " ") for i in self.paused_sessions]
            file.write("\n")
            [file.write(str(i) + " ") for i in self.mltg.timer]
            file.write("\n")
            file.write(self.mltg.members_fname + "\n")
            file.write(self.mltg.destination_group)

        print("\nStarting Member List to Group Add\n")


def main():

    process = TGAtty()

    process.menu()

    return


if __name__ == "__main__":

    main()
