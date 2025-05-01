import curses
import socket
import threading
from argparse import ArgumentParser

import client
import server
import ui

#/client -i localhost -p 5050 -ps 123 -n biba
#/client -i localhost -p 5050 -ps 123 -n biba1


class Main:
    def __init__(self):
        self.running_gui = False
        self.running_client = False
        self.running_server = False

    def setup_parser(self):
        parser = ArgumentParser(
            description="To parse agruments needed for establishing connection."
        )
        return parser

    def setup_server_parser(self) -> ArgumentParser:
        parser = self.setup_parser()
        parser.add_argument(
            "-p",
            "--port",
            type=int,
            default=5050,
        )
        return parser

    def setup_client_parser(self) -> ArgumentParser:
        parser = self.setup_parser()
        parser.add_argument(
            "-n",
            "--username",
            type=str,
            required=True
        )
        parser.add_argument(
            "-ps",
            "--password",
            type=str,
            required=True
        )
        parser.add_argument(
            "-p",
            "--port",
            type=int,
            required=True
        )
        parser.add_argument(
            "-i",
            "--ip",
            type=str,
            required=True
        )
        return parser

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
                    if self.running_server:
                        pass
                    elif self.running_client:
                        self.client.send_message(user_message)
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
                    self.start_server(command[1:])

            elif key_word == "/client":
                if self.running_server:
                    self.gui.console_message("You are already running a server")

                elif self.running_client:
                    self.gui.console_message("You are already joined as a client")

                else:
                    self.start_client(command[1:])

            elif key_word == "/bottom":
                self.gui.scroll_bottom()

            elif key_word == "/clear":
                self.gui.clear()

            else:
                self.gui.console_message("Dunno what that is.")

        except Exception as e:
            self.gui.console_message(f"You got that error {e}")


    def start_server(self, command: list[str]):
        args = None
        try:
            args = self.setup_server_parser().parse_args(command)

        except Exception as e:
            self.gui.console_message(f"{e}")
            return

        if server.is_port_available(args.port):
            self.server = server.Server(args.port)
            self.process_server = threading.Thread(target=self.server.run_server)
            self.running_server = True
            self.process_server.start()
            self.gui.console_message("Running as Server")

        else:
            self.gui.console_message("Port is unavailable")


    def start_client(self, command: list[str]):
        args = None
        try:
            args = self.setup_client_parser().parse_args(command)
            self.gui.console_message(f"{args}")

        except Exception as e:
            self.gui.console_message(f"{e}")
            return

        self.client = client.Client(args.ip, args.port, args.username, args.password, self.gui)

        try:
            self.client.start_connection()
        except:
            self.gui.console_message(f"Unable to setup connection with {args.ip}:{args.port}")
            return

        self.process_client = threading.Thread(target=self.client.run_client)
        self.running_client = True
        self.process_client.start()
        self.gui.console_message("Running as Client")


if __name__ == "__main__":
    print(socket.gethostname())
    main = Main()
    main.start_gui()