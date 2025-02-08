import curses
import math
from curses import wrapper
import threading
import time


class Message:
    def __init__(self, sender_name: str, message: str):
        self.sender_name = sender_name
        self.message = message
        self.total_length = len(f"{self.sender_name}: {self.message}")


class ChatApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.user_input_message = ""
        self.relative_input_cursor_x = 0
        self.cursor_x = 3
        self.user_input_offset = 0
        self.chat_scroll_index = 0
        self.chatbox_messages = []

        self.screen_height = 0
        self.screen_width = 0
        self.input_field_border = None
        self.input_field = None
        self.chatbox_border = None
        self.chatbox = None

    def calc_lines_needed(self, text_length, chatbox_width):
        return math.ceil(text_length / chatbox_width)

    def get_user_input(self):
        return self.user_input_message

    def dimensions_changed(self):
        new_height, new_width = self.stdscr.getmaxyx()
        if self.screen_width != new_width or self.screen_height != new_height:
            return True
        return False

    def update_dimensions(self):
        self.screen_height, self.screen_width = self.stdscr.getmaxyx()

    def update_window_dimensions(self):
        input_field_height = 1
        input_field_width = self.screen_width - 5
        chatbox_height = self.screen_height - 5
        chatbox_width = self.screen_width - 3

        input_field_border_hwyx = (input_field_height + 2, input_field_width + 3, chatbox_height + 2, 1)
        input_field_hwyx = (input_field_height, input_field_width, chatbox_height + 3, 3)
        self.input_field_border = curses.newwin(*input_field_border_hwyx)
        self.input_field = curses.newwin(*input_field_hwyx)

        chatbox_border_hwyx = (chatbox_height + 2, chatbox_width + 2, 0, 0)
        chatbox_hwyx = (chatbox_height, chatbox_width, 1, 1)
        self.chatbox_border = curses.newwin(*chatbox_border_hwyx)
        self.chatbox = curses.newwin(*chatbox_hwyx)

    def win_draw_chatbox(self):
        self.chatbox.erase()
        chatbox_height = self.screen_height - 5
        chatbox_width = self.screen_width - 3

        temp_lines_offset = sum([self.calc_lines_needed(msg.total_length, chatbox_width) for msg in self.chatbox_messages])
        if temp_lines_offset <= chatbox_height:
            cursor_y = 0
            for msg in self.chatbox_messages:
                try:
                    complete_message = f"{msg.sender_name}: {msg.message}"
                    self.chatbox.addstr(cursor_y, 0, complete_message)
                    cursor_y = self.chatbox.getyx()[0] + 1
                except:
                    pass

        else:
            total_lines_offset = 0
            for i in range(min(chatbox_height, len(self.chatbox_messages))):
                try:
                    recent_message = self.chatbox_messages[len(self.chatbox_messages) - i - 1 - self.chat_scroll_index]
                    total_lines_offset += self.calc_lines_needed(recent_message.total_length, chatbox_width)
                    complete_message = f"{recent_message.sender_name}: {recent_message.message}"
                    self.chatbox.addstr(chatbox_height - total_lines_offset, 0, complete_message)
                except:
                    continue
        self.chatbox_border.border()
        self.chatbox_border.refresh()
        self.chatbox.refresh()

    def win_draw_input_field(self):
        self.input_field.erase()
        self.input_field_border.border()

        input_field_width = self.screen_width - 5
        user_input_display = self.user_input_message[
                             self.user_input_offset:input_field_width + self.user_input_offset - 1]
        if len(user_input_display) > input_field_width:
            curses.beep()

        self.input_field.addstr(0, 0, user_input_display, curses.color_pair(1))

        self.input_field_border.addch(1, 1, ">")
        self.input_field_border.refresh()
        self.input_field.refresh()

    def win_draw_global(self):
        self.stdscr.erase()

        if self.dimensions_changed():
            self.update_dimensions()
            try:
                self.update_window_dimensions()
            except:
                curses.beep()

        try:
            self.stdscr.refresh()
            self.win_draw_chatbox()
            self.win_draw_input_field()
        except:
            curses.beep()

    def win_draw_semi(self):
        self.win_draw_chatbox()
        self.win_draw_input_field()

    def remove_char_input(self):
        string1 = self.user_input_message[:self.relative_input_cursor_x]
        string2 = self.user_input_message[self.relative_input_cursor_x+ 1:]
        self.user_input_message = string1 + string2

    def handle_character_input(self, user_input):
        self.user_input_message += chr(user_input)
        self.update_dimensions()
        if self.input_field.getyx()[1] == self.screen_width - 6:
            self.user_input_offset += 1
        self.win_draw_input_field()
        self.relative_input_cursor_x += 1

    def handle_backspace(self):
        if self.relative_input_cursor_x != 0:
            if self.user_input_offset > 0:
                self.user_input_offset -= 1
            self.relative_input_cursor_x -= 1
            self.remove_char_input()
            self.win_draw_input_field()
        else:
            curses.beep()

    def handle_enter(self):
        self.user_input_message = ""
        self.relative_input_cursor_x = 0
        self.user_input_offset = 0

    def new_message(self, sender_name, message):
        object = Message(sender_name, message)
        self.chatbox_messages.append(object)
        self.win_draw_semi()

    def handle_resize(self):
        self.win_draw_global()
        input_field_width = self.screen_width - 5
        if len(self.user_input_message) >= input_field_width:
            self.user_input_offset = len(self.user_input_message) - (input_field_width - 1)
            self.relative_input_cursor_x = len(self.user_input_message)
            self.win_draw_input_field()
        else:
            self.user_input_offset = 0



