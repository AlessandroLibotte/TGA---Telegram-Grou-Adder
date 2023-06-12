import colorama as cr
from pynput import keyboard
import os
from time import sleep
from random import randint

from lib.TGAmain import TGAgTg, TGAmlTg
from lib.TGAsessions import TGAsessions
from lib.TGAscraper import TGAscraper


class TGAtty:

    def __init__(self):

        cr.just_fix_windows_console()

        self.listener = keyboard.Listener(on_press=self._handler)
        self.listener.start()

        self.last_mode = ""
        self.config_fname = ""

        self.session_fname = ""
        self.paused_sessions = []
        self.mltg = TGAmlTg()
        self.gtg = TGAgTg()

        self.cursor = 1
        self.update = True
        self.menu_length = (8, 3, 3, 5, 4)
        self.page = 0
        self.menu = 0
        self.error = False

    def _main_page(self):

        print("\nWelcome to TGA - Telegram Group Adder (version 8.0)")

        print("\nMain Menu:" +
              "\n\n\t" + ("\033[47;30mRun last config\033[0m" if self.cursor == 1 else "Run last config") +
              "\n\n\t" + ("\033[47;30mLoad Config\033[0m" if self.cursor == 2 else "Load config") +
              "\n\n\t" + ("\033[47;30mSet Sessions File\033[0m" if self.cursor == 3 else "Set Sessions File") +
              "\n\n\t" + ("\033[47;30mCreate Sessions\033[0m" if self.cursor == 4 else "Create Sessions") +
              "\n\n\t" + ("\033[47;30mPause Sessions\033[0m" if self.cursor == 5 else "Pause Sessions") +
              "\n\n\t" + ("\033[47;30mGroup to Group Add\033[0m" if self.cursor == 6 else "Group to Group Add") +
              "\n\n\t" + ("\033[47;30mMember List to Group Add\033[0m" if self.cursor == 7 else "Member List to Group Add") +
              "\n\n\t" + ("\033[47;30mExit\033[0m" if self.cursor == 8 else "Exit"))

    def _run_last(self):

        if self._load_config():
            if self.last_mode == "gtg":
                self._gtg_run()
            elif self.last_mode == "mltg":
                self._mltg_run()

        self._reset_menu_page()

        return

    def _load_config_page(self):

        self._flush_input()

        _in = input("\nInsert the name of the desired configuration file to load"
                    "\nCurrent Configuration Filename: " +
                    (self.config_fname if self.config_fname != "" else "None") +
                    ". Type 'b' to bo back.\n\n: ")

        if _in != 'b':
            self.config_fname = _in
            self._load_config(self.config_fname)

        self._reset_menu_page()

        return

    def _set_session_fname_page(self):

        self._flush_input()

        _in = input("\nInsert the name of the desired sessions file to use"
                    "\nCurrent Session Filename: " +
                    (self.session_fname if self.session_fname != "" else "None") +
                    ". Type 'b' to bo back.\n\n: ")

        if _in != 'b':
            self.session_fname = _in

        self._reset_menu_page()

        return

    def _go_to_sessions_fname_not_set_page(self):

        self.menu = 5
        self.page = 1
        self.update = True

    def _create_sessions_page(self):

        if not self._check_requirements(1):
            self._go_to_sessions_fname_not_set_page()
            return

        print("\nCreating sessions\n")

        session_creator = TGAsessions()
        session_creator.get_session_fname(self.session_fname)
        session_creator.run()

        self._reset_menu_page()
        return

    def _pause_sessions_page(self):

        if not self._check_requirements(1):
            self._go_to_sessions_fname_not_set_page()
            return

        self._flush_input()

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

        self._reset_menu_page()
        return

    def _go_to_gtg_menu(self):

        if self._check_requirements(1):
            self.menu = 1
            self._reset_menu_page()
        else:
            self.menu = 5
            self.page = 1
            self.update = True

        return

    def _gtg_menu_page(self):

        print("\nGroup to Group Add - Menu:"
              "\n\n\t" + ("\033[47;30mRun\033[0m" if self.cursor == 1 else "Run") +
              "\n\n\t" + ("\033[47;30mSettings\033[0m" if self.cursor == 2 else "Settings") +
              "\n\n\t" + ("\033[47;30mBack\033[0m" if self.cursor == 3 else "Back"))

    def _go_to_gtg_missing_param_page(self):

        self.menu = 5
        self.page = 2
        self.update = True

    def _gtg_run(self):

        if not self._check_requirements(2):
            self._go_to_gtg_missing_param_page()
            return

        self._save_config(0)

        self._reset_menu_page()

    def _go_to_gtg_settings(self):

        self.menu = 2
        self._reset_menu_page()

        return

    def _gtg_settings_menu_page(self):

        print("\nGroup to Group Add - Settings:"
              "\n\n\t" + ("\033[47;30mSet Source Group\033[0m" if self.cursor == 1 else "Set Source Group") +
              "\n\n\t" + ("\033[47;30mSet Destination Group\033[0m" if self.cursor == 2 else "Set Destination Group") +
              "\n\n\t" + ("\033[47;30mBack\033[0m" if self.cursor == 3 else "Back"))

    def _gtg_set_source_group(self):

        self._flush_input()

        _in = input("\nInsert the id of the source group to use"
                    "\nCurrent Source Group: " +
                    (self.gtg.source_group if self.gtg.source_group != "" else "None") +
                    ". Type 'b' to bo back.\n\n: ")
        if _in != "b":
            self.gtg.set_source_group(_in)

        self._reset_menu_page()

    def _gtg_set_destination_group(self):

        self._flush_input()

        _in = input("\nInsert the id of the destination group to use"
                    "\nCurrent Destination Group: " +
                    (self.gtg.destination_group if self.gtg.destination_group != "" else "None") +
                    ". Type 'b' to bo back.\n\n: ")
        if _in != "b":
            self.gtg.set_destination_group(_in)

        self._reset_menu_page()

    def _go_to_mltg_menu(self):

        if self._check_requirements(1):
            self.menu = 3
            self._reset_menu_page()
        else:
            self.menu = 5
            self.page = 1
            self.update = True

        return

    def _mltg_menu_page(self):

        print("\nMember List to Group Add - Menu:"
              "\n\n\t" + ("\033[47;30mRun\033[0m" if self.cursor == 1 else "Run") +
              "\n\n\t" + ("\033[47;30mScrape Users from Group\033[0m" if self.cursor == 2 else "Scrape Users from Group") +
              "\n\n\t" + ("\033[47;30mSettings\033[0m" if self.cursor == 3 else "Settings") +
              "\n\n\t" + ("\033[47;30mSave config\033[0m" if self.cursor == 4 else "Save config") +
              "\n\n\t" + ("\033[47;30mBack\033[0m" if self.cursor == 5 else "Back"))

    def _go_to_mltg_missing_param_page(self):

        self.menu = 5
        self.page = 3
        self.update = True

    def _mltg_run(self):

        if not self._check_requirements(3):
            self._go_to_mltg_missing_param_page()
            return

        self._save_config(1)

        self.mltg.set_session_fname(self.session_fname)
        self.mltg.set_paused_sessions(self.paused_sessions)

        while True:

            self.mltg.quit = False

            self.mltg.load_sessions()

            if not self.mltg.run():

                break

            else:

                print("Pausing adding routine for 24/26h\n")
                sleep(randint(86400, 93600))

    def _mltg_scrape(self):

        self._flush_input()

        source_group = input("\nProvide a group id to scrape the users from.\n\n: ")

        print("\nScraping Members\n")

        member_scraper = TGAscraper()

        member_scraper.get_session_fname(self.session_fname)
        member_scraper.get_source_group(source_group)

        member_scraper.run()

        self.mltg.set_members_fname("Members.txt")

        self.page = 0
        self.update = True

    def _go_to_mltg_settings(self):

        self.menu = 4
        self._reset_menu_page()

    def _mltg_settings_menu_page(self):

        print("\nMember List to Group Add - Settings:"
              "\n\n\t" + ("\033[47;30mSet timer\033[0m" if self.cursor == 1 else "Set timer") +
              "\n\n\t" + ("\033[47;30mSet Member List File\033[0m" if self.cursor == 2 else "Set Member List File") +
              "\n\n\t" + ("\033[47;30mSet Destination Group\033[0m" if self.cursor == 3 else "Set Destination Group") +
              "\n\n\t" + ("\033[47;30mBack\033[0m" if self.cursor == 4 else "Back"))

    def _set_timer_page(self):

        self._flush_input()

        _in = input("\nInsert minimum time delay and maximum time delay separated by space (es: 40 70)"
                    "\nCurrent Time Delay: " + str(self.mltg.timer[0]) + " " + str(self.mltg.timer[1]) + "."
                    " Type 'b' to bo back.\n\n: ").split(
                    " ")

        if _in != ["b"] and _in != ['']:
            self.mltg.set_timer(_in)

        self._reset_menu_page()

    def _set_memberlist_fname_page(self):

        self._flush_input()

        _in = input("\nInsert the name of the desired member list file to use"
                    "\nCurrent Member List Filename: " +
                    (self.mltg.members_fname if self.mltg.members_fname != "" else "None") +
                    ". Type 'b' to bo back.\n\n: ")
        if _in != "b":
            self.mltg.set_members_fname(_in)

        self._reset_menu_page()

    def _set_dest_group_page(self):

        self._flush_input()

        _in = input("\nInsert the id of the destination group to use"
                    "\nCurrent Destination Group: " +
                    (self.mltg.destination_group if self.mltg.destination_group != "" else "None") +
                    ". Type 'b' to bo back.\n\n: ")
        if _in != "b":
            self.mltg.set_destination_group(_in)

        self._reset_menu_page()

    def _save_config_page(self):

        if not self._check_requirements(3):
            self._go_to_mltg_missing_param_page()
            return

        self._flush_input()

        _in = input("\nInsert the name of the file to save the configuration into. Type 'b' to bo back.\n\n: ")

        if _in != 'b':
            self._save_config(_in)
            self.config_fname = _in

        self._reset_menu_page()

    def _go_to_main_menu(self):

        self.menu = 0
        self._reset_menu_page()

    def _quit(self):

        self.listener.stop()
        exit(0)

    def _reset_menu_page(self):

        self.cursor = 1
        self.page = 0
        self.update = True

    def _check_requirements(self, layer):

        if layer == 1:
            if self.session_fname != "":
                return True
            else:
                return False
        elif layer == 2:
            if self.gtg.source_group != "" and self.gtg.destination_group != "":
                return True
            else:
                return False
        elif layer == 3:
            if self.mltg.members_fname != "" and self.mltg.destination_group != "":
                return True
            else:
                return False
        else:
            return False

    def _handler(self, key):

        if key == keyboard.Key.down:
            if self.cursor < self.menu_length[self.menu]:
                self.cursor += 1

        elif key == keyboard.Key.up:
            if self.cursor > 1:
                self.cursor -= 1

        elif key == keyboard.Key.enter:
            if self.error is False:
                self.page = self.cursor
            self.error = False

        self.update = True

        return

    @staticmethod
    def _flush_input():

        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()

    @staticmethod
    def _cls():
        os.system("cls")

    def _save_config(self, mode, config_fname="last_config.conf"):

        print("\nSaving configuration...")

        with open(config_fname, 'w') as file:
            file.write(("gtg" if mode == 0 else "mltg") + "\n")
            file.write(self.session_fname + "\n")
            [file.write(i + " ") for i in self.paused_sessions]
            file.write("\n")
            if mode == 0:
                file.write(self.gtg.source_group)
                file.write(self.gtg.destination_group)
            elif mode == 1:
                [file.write(str(i) + " ") for i in self.mltg.timer]
                file.write("\n")
                file.write(self.mltg.members_fname + "\n")
                file.write(self.mltg.destination_group)

    def _load_config(self, config_fname="last_config.conf"):

        try:
            file = open(config_fname, "r")
        except FileNotFoundError:
            return False
        else:

            get_line = lambda line: line.strip("\n").split(" ")

            params = [get_line(line)[0] if len(get_line(line)) <= 1 else get_line(line) for line in file.readlines()]

            self.last_mode = params[0]
            self.session_fname = params[1]
            self.paused_sessions = params[2][:-1]

            if self.last_mode == 'gtg':
                self.gtg.set_source_group(params[3])
                self.gtg.set_destination_group(params[4])
            elif self.last_mode == "mltg":
                self.mltg.set_timer(params[3][:-1])
                self.mltg.set_members_fname(params[4])
                self.mltg.set_destination_group(params[5])

            return True

    def _sessions_fname_not_set_page(self):

        print("You must set a session file before accessing other features")

        self.menu = 0
        self.cursor = 1
        self.page = 0
        self.error = True

        return

    def _gtg_missing_param_page(self):

        print("You must set a Source Group and a Destination Group before running the program")

        self.menu = 1
        self.cursor = 1
        self.page = 0
        self.error = True

        return

    def _mltg_missing_param_page(self):

        print("You must set a Member List file and a Destination Group before running the program")

        self.menu = 3
        self.cursor = 1
        self.page = 0
        self.error = True

        return

    def main_loop(self):

        sort_main_menu_page = {
            0: self._main_page,
            1: self._run_last,
            2: self._load_config_page,
            3: self._set_session_fname_page,
            4: self._create_sessions_page,
            5: self._pause_sessions_page,
            6: self._go_to_gtg_menu,
            7: self._go_to_mltg_menu,
            8: self._quit,
        }

        sort_gtg_menu_page = {
            0: self._gtg_menu_page,
            1: self._gtg_run,
            2: self._go_to_gtg_settings,
            3: self._go_to_main_menu
        }

        sort_gtg_settings_menu_page = {
            0: self._gtg_settings_menu_page,
            1: self._gtg_set_source_group,
            2: self._gtg_set_destination_group,
            3: self._go_to_gtg_menu
        }

        sort_mltg_menu_page = {
            0: self._mltg_menu_page,
            1: self._mltg_run,
            2: self._mltg_scrape,
            3: self._go_to_mltg_settings,
            4: self._save_config_page,
            5: self._go_to_main_menu,
        }

        sort_mltg_settings_menu_page = {
            0: self._mltg_settings_menu_page,
            1: self._set_timer_page,
            2: self._set_memberlist_fname_page,
            3: self._set_dest_group_page,
            4: self._go_to_mltg_menu
        }

        sort_error_page = {
            1: self._sessions_fname_not_set_page,
            2: self._gtg_missing_param_page,
            3: self._mltg_missing_param_page
        }

        sort_menu = {
            0: sort_main_menu_page,
            1: sort_gtg_menu_page,
            2: sort_gtg_settings_menu_page,
            3: sort_mltg_menu_page,
            4: sort_mltg_settings_menu_page,
            5: sort_error_page
        }

        while True:

            if self.update is True:

                self._cls()

                self.update = False

                sort_menu[self.menu][self.page]()


if __name__ == '__main__':

    menu = TGAtty()

    menu.main_loop()
