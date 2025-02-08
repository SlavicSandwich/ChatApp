import curses
import threading

import ui


class Main:
    def __init__(self):
        self.running_gui = False
        self.running_client = False
        self.running_server = False

    def start_gui(self):
        self.process_gui = threading.Thread(target=curses.wrapper(self.run_gui))
        self.process_gui.start()

    def quit(self):
        self.running_gui = False
        self.process_gui.join()

    def run_gui(self, stdscr):
        self.gui = ui.ChatApp(stdscr)
        self.gui.win_draw_global()
        self.running_gui = True

        while self.running_gui:
            user_input = stdscr.getch()
            if user_input == curses.KEY_RESIZE:
                self.gui.handle_resize()

            elif 32 <= user_input <= 126:
                self.gui.handle_character_input(user_input)

            elif user_input == curses.KEY_UP and not self.gui.shows_first_message:
                self.gui.chat_scroll_index += 1
                self.gui.win_draw_semi()

            elif user_input == curses.KEY_DOWN:
                if self.gui.chat_scroll_index > 0:
                    self.gui.chat_scroll_index -= 1
                    self.gui.win_draw_semi()

            elif user_input == curses.KEY_ENTER or user_input == 10 or user_input == 13:
                user_message = self.gui.get_user_input().strip()
                self.gui.handle_enter()
                if user_message.startswith("/"):
                    self.user_command(user_message)
                    continue
                if user_message == "":
                    continue
                else:
                    #send message logic
                    self.gui.new_message("You", user_message)
            elif user_input == curses.KEY_BACKSPACE or user_input == 127 or user_input == 8:
                self.gui.handle_backspace()

    def user_command(self, command_string: str):
        command = list(command_string.strip().split())
        key_word = command[0]

        try:
            if key_word == "/quit":
                self.quit()

            elif key_word == "/server":
                if self.running_server:
                    self.gui.console_message("You are already running a server")

                elif self.running_client:
                    self.gui.console_message("You are already joined as a client")

                else:
                    self.start_server(command)

            elif key_word == "/client":
                if self.running_server:
                    self.gui.console_message("You are already running a server")

                elif self.running_client:
                    self.gui.console_message("You are already joined as a client")

                else:
                    self.start_client(command)

            elif key_word == "/bottom":
                self.gui.scroll_bottom()

            elif key_word == "/clear":
                self.gui.clear()

            else:
                self.gui.console_message("Dunno what that is.")

        except Exception as e:
            self.gui.console_message(f"You got that error {e}")


    def start_server(self, command: list[str]):
        self.running_server = True
        pass

    def start_client(self, command: list[str]):
        self.running_client = True
        pass


if __name__ == "__main__":
    main = Main()
    main.start_gui()