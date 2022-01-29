#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8


import tkinter as tk
from tkinter import messagebox as mb
from tkinter.ttk import Combobox
from math import *
import cmath
from typing import Union
import webbrowser
import sqlite3


# CONSTANTS
WIDTH = 500
HEIGHT = 768
FONT = 'Enrique'
WEBSITE_ADDRESS = 'http://f0578134.xsph.ru/'
LANGUAGE_DATABASE_WAY = 'languages.db'
SAFE_START = {'+', '-', '*', '/', '.', '('}
SAFE_END = {'+', '-', '*', '/', '.', ')', '^'}
OPERATIONS = {'+', '-', '^', '/', '*'}
CHR_TO_CLEAR = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'}
COLOR_ON_FOCUS = {
    'operator': '#FFC94A',
    'digit': '#62E1DF',
    'const_symbol': '#21AEAC',
    'trigonometric_function': '#E8A52F',
    'bracket_or_dot': '#6E98D1',
    'clear': '#FFA500',
    'calculate': '#DF663D'
}
DEFAULT_COLORS = {
    'operator': '#FFE4B5',
    'digit': '#A6EEED',
    'const_symbol': '#2CD7D4',
    'trigonometric_function': '#F1C16C',
    'bracket_or_dot': '#AAC3E4',
    'clear': '#FFBA00',
    'calculate': '#E9967A'
}

# LANGUAGES CONSTANTS
LANGUAGES = []  # HAS TO BE TUPLE, NOT LIST! (REALISED BELOW)
TITLE = {}
INFINITY = {}
NOT_EXISTS = {}
DOC_BUTTON_TEXT = {}
WEBSITE_BUTTON_TEXT = {}
DOCUMENTATION = {}
INPUT_ERROR = {}
ACC_TEXT = {}
CALC_BUTTON_TEXT = {}
CALC_CLEAR_BUTTON_TEXT = {}


with sqlite3.connect(LANGUAGE_DATABASE_WAY) as db:
    cursor = db.cursor()

    # Fill LANGUAGES
    cursor.execute("SELECT * FROM LANGUAGES;")
    db_languages = cursor.fetchall()
    for db_language in db_languages:
        LANGUAGES.append(db_language[1])
    LANGUAGES = tuple(LANGUAGES)

    def var_to_name(var):
        dict_vars = dict(globals().items())
        var_string = None
        for name in dict_vars.keys():
            if dict_vars[name] is var:
                var_string = name
                break
        return var_string

    def fill_language_constant(constant: dict):
        cursor.execute(f"SELECT * FROM {var_to_name(constant)};")
        data = cursor.fetchall()
        t_index = 0
        for elem in data:
            constant[LANGUAGES[t_index]] = elem[1]
            t_index += 1

    fill_language_constant(TITLE)
    fill_language_constant(INFINITY)
    fill_language_constant(NOT_EXISTS)
    fill_language_constant(DOC_BUTTON_TEXT)
    fill_language_constant(WEBSITE_BUTTON_TEXT)
    fill_language_constant(DOCUMENTATION)
    fill_language_constant(INPUT_ERROR)
    fill_language_constant(ACC_TEXT)
    fill_language_constant(CALC_BUTTON_TEXT)
    fill_language_constant(CALC_CLEAR_BUTTON_TEXT)


# Buttons
class HoverButton(tk.Button):
    """ Allow you to process the hover on the button.
    """
    def __init__(self, master, _type, **kw):
        tk.Button.__init__(self, master=master, **kw)
        self.hover_background = COLOR_ON_FOCUS[_type]
        self.default_background = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self['background'] = self.hover_background

    def on_leave(self, event):
        self['background'] = self.default_background


class onclick_bind_combobox(Combobox):
    """ Allow you to process the click on the combobox.
    """
    def __init__(self, master, **kw):
        Combobox.__init__(self, master=master, **kw)
        self.bind("<<ComboboxSelected>>", self.change_lang)

    def change_lang(self, event):
        """ Сhanges the application language.
        """
        global cur_lang
        cur_lang = languages_box.get()

        box.title(TITLE[cur_lang])
        doc_button['text'] = DOC_BUTTON_TEXT[cur_lang]
        website_button['text'] = WEBSITE_BUTTON_TEXT[cur_lang]
        acc_text['text'] = ACC_TEXT[cur_lang]
        buttons[26]['text'] = CALC_CLEAR_BUTTON_TEXT[cur_lang]
        buttons[27]['text'] = CALC_BUTTON_TEXT[cur_lang]

        a = str(screen.get())

        screen['state'] = "normal"
        for key in NOT_EXISTS:
            if NOT_EXISTS[key] == a:
                screen.delete(0, 'end')
                screen.insert(0, NOT_EXISTS[cur_lang])
        screen['state'] = "readonly"


def create_symbol_btn(i: int, text: str, _type: str) -> tk.Button:
    btn = HoverButton(
        calc_input,
        _type=_type,
        text=text,
        command=lambda: add_digit(text),
        bd=1,
        relief='solid',
        font=f'{FONT} 30',
        bg=DEFAULT_COLORS[_type],
    )
    if _type == 'trigonometric_function':
        btn['font'] = f'{FONT} 25'
        btn['command'] = lambda: add_digit(text + '(')

    btn.grid(row=i // 5, column=i % 5, stick='nesw', padx=3, pady=3)

    return btn


def create_operation_btn(i: int, text: str,  _type: str = 'operator') -> tk.Button:
    btn = HoverButton(
        calc_input,
        _type=_type,
        text=text,
        command=lambda: add_operation(text),
        bd=1,
        relief='solid',
        font=f'{FONT} 30',
        bg=DEFAULT_COLORS[_type],
    )

    btn.grid(row=i // 5, column=i % 5, stick='nesw', padx=3, pady=3)

    return btn


# Button commands
def show_doc():
    """ Show documentation.
    """

    doc_window = tk.Tk()
    doc_window.title(DOC_BUTTON_TEXT[cur_lang])
    doc_window.geometry(f"{1000}x{740}")

    doc_frame = tk.Frame(doc_window)
    doc_frame.place(relwidth=1, relheight=1)

    doc_label = tk.Label(doc_frame, text=DOCUMENTATION[cur_lang], justify='left')
    doc_label.pack()
    # mb.showinfo(message=DOCUMENTATION[cur_lang])


def open_website():
    """ Opens website of the program
    """
    webbrowser.open_new(WEBSITE_ADDRESS)


def add_digit(digit: str):
    """ Add a digit/constant symbol/trigonometric function to the screen.
    """
    global clear_mod

    if clear_mod and digit in CHR_TO_CLEAR:
        new_value = digit
    else:
        new_value = screen.get() + digit

    screen['state'] = "normal"
    screen.delete(0, 'end')
    screen.insert(0, new_value)
    screen['state'] = "readonly"
    clear_mod = False


def add_operation(operation: str):
    """ Add an operator to the screen.
    """
    global clear_mod

    value = str(screen.get())

    screen['state'] = "normal"
    if value == '':
        screen.insert(0, operation)
    elif clear_mod:
        screen.delete(0, 'end')
        screen.insert(0, operation)
    else:
        if value[-1] in OPERATIONS:
            value = value[:-1]
        screen.delete(0, 'end')
        screen.insert(0, value+operation)
    screen['state'] = "readonly"

    clear_mod = False


def backspace():
    """ Program the backspace function.
    """
    string = screen.get()
    n = len(string)
    if n == 0:
        return

    screen['state'] = "normal"
    if string.endswith('tg'):
        screen.delete(0, 'end')
        screen.insert(0, string[0: n - 2])

    elif string.endswith(('sin', 'cos', 'ctg')):
        screen.delete(0, 'end')
        screen.insert(0, string[0: n - 3])

    else:
        screen.delete(0, 'end')
        screen.insert(0, string[0: n - 1])
    screen['state'] = "readonly"


def clear_screen():
    """ Clear the screen.
    """
    screen['state'] = "normal"
    screen.delete(0, 'end')
    screen['state'] = "readonly"


# Calculation
def pre_calculate():
    """ Performs arithmetic conversions before extracting the root.
    """
    global clear_mod
    raw_number = str(screen.get())
    new_raw_number = ''

    n = len(raw_number)

    i = 0
    while i < n:
        if raw_number[i] == '^':
            new_raw_number += '**'

        elif raw_number[i] == 'i':
            if i > 0 and raw_number[i-1] not in SAFE_START and new_raw_number != '' and new_raw_number[-1] != '*':
                new_raw_number += '*'
            new_raw_number += '1j'
            if i < n-1 and raw_number[i+1] not in SAFE_END:
                new_raw_number += '*'

        elif raw_number[i] == 'π':
            if i > 0 and raw_number[i-1] not in SAFE_START and new_raw_number != '' and new_raw_number[-1] != '*':
                new_raw_number += '*'
            new_raw_number += 'pi'
            if i < n-1 and raw_number[i+1] not in SAFE_END:
                new_raw_number += '*'

        elif raw_number[i] == 'e':
            if i > 0 and raw_number[i-1] not in SAFE_START and new_raw_number != '' and new_raw_number[-1] != '*':
                new_raw_number += '*'
            new_raw_number += 'e'
            if i < n-1 and raw_number[i+1] not in SAFE_END:
                new_raw_number += '*'

        elif raw_number[i:i + 3] == 'sin':
            if i > 0 and raw_number[i - 1] not in SAFE_START and raw_number[i-1] != '(':
                new_raw_number += '*'
            new_raw_number += 'my_sin'
            i += 2

        elif raw_number[i:i+3] == 'cos':
            if i > 0 and raw_number[i-1] not in SAFE_START and new_raw_number != '' and new_raw_number[-1] != '*':
                new_raw_number += '*'
            new_raw_number += 'my_cos'
            i += 2

        elif raw_number[i:i+3] == 'ctg':
            if i > 0 and raw_number[i-1] not in SAFE_START and new_raw_number != '' and new_raw_number[-1] != '*':
                new_raw_number += '*'
            new_raw_number += 'my_ctg'
            i += 2

        elif raw_number[i:i+2] == 'tg':
            if i > 0 and raw_number[i-1] not in SAFE_START and new_raw_number != '' and new_raw_number[-1] != '*':
                new_raw_number += '*'
            new_raw_number += 'my_tg'
            i += 1

        else:
            new_raw_number += raw_number[i]

        i += 1

    new_raw_number = new_raw_number.replace(')(', ')*(')

    try:
        root(eval(new_raw_number), point=acc_scale.get())
        clear_mod = True
    except SyntaxError:
        mb.showerror(message=INPUT_ERROR[cur_lang])
    except NameError:
        mb.showerror(message=INPUT_ERROR[cur_lang])
    except TypeError:
        mb.showerror(message=INPUT_ERROR[cur_lang])
    except OverflowError:
        mb.showerror(message=INFINITY[cur_lang])
    except ZeroDivisionError:
        screen['state'] = "normal"
        screen.delete(0, 'end')
        screen.insert(0, NOT_EXISTS[cur_lang])
        screen['state'] = "readonly"
        clear_mod = True


def my_tg(x: Union[int, float, complex]) -> Union[int, float, complex]:
    """ Calculates the tangent of a float/integer/complex number.
    If calculation is not possible, initiates a ZeroDivisionError.
    """
    if type(x) == complex:
        return cmath.tan(x)
    if abs(x) > 1570796325.2241:
        raise OverflowError
    if x > pi:
        x %= pi
    elif x < -pi:
        x = -(x % pi)
    if 1.570796326 <= x <= 1.570796327 or -1.570796327 <= x <= -1.570796326:
        raise ZeroDivisionError
    return tan(x)


def my_ctg(x: Union[int, float, complex]) -> Union[int, float, complex]:
    """ Calculates the cotangent  of a float/integer/complex number.
    If calculation is not possible, initiates a ZeroDivisionError.
    """
    if type(x) == complex:
        return 1 / cmath.tan(x)
    if abs(x) > 3141561.2376632574:
        raise OverflowError
    if x > pi:
        x %= pi
    elif x < -pi:
        x = -(x % pi)
    if 3.141592652 <= x <= 3.141592654 or -0.0000000002 <= x <= 0.0000000002:
        raise ZeroDivisionError
    return 1/tan(x)


def my_sin(x: Union[int, float, complex]) -> Union[int, float, complex]:
    """ Calculates the sinus of a float/integer/complex number.
    """
    if type(x) == complex:
        return cmath.sin(x)
    return sin(x)


def my_cos(x: Union[int, float, complex]) -> Union[int, float, complex]:
    """ Calculates the cosinus of a float/integer/complex number.
    """
    if type(x) == complex:
        return cmath.cos(x)
    return cos(x)


def change_e(x: Union[float]) -> Union[str]:
    """ Replaces "e+" with "E" in big number and rounds it to the desired digit after the decimal point
    """
    if 'e' not in str(x):
        return str(x)

    point = acc_scale.get()
    string_x = str(x)
    e_pos = string_x.find('e')
    to_round = float(string_x[0:e_pos])
    to_round = round(to_round, point)
    if point == 0:
        to_round = int(to_round)
    minus = ''
    if string_x[e_pos+1] == '-':
        minus = '-'

    return str(to_round) + 'E' + minus + string_x[e_pos+2:]


def root(num: Union[int, float, complex], point: int):
    """ Extracts the root of a number.
    """
    global clear_mod

    if (type(num) == int or type(num) == float) and abs(num) <= 1e-9:
        rooted = 0
    elif (type(num) == int or type(num) == float) and num < 0:
        rooted = ((-num) ** 0.5)*1j
    else:
        rooted = num**0.5

    if type(rooted) == complex and abs(rooted.real) <= 1e-9:
        rooted = rooted.imag*1j
    if type(rooted) == complex and abs(rooted.imag) <= 1e-9:
        rooted = rooted.real

    if rooted == 0:
        screen['state'] = "normal"
        screen.delete(0, 'end')
        screen.insert(0, 0)
        screen['state'] = "readonly"
        return

    if 'e' in str(rooted):
        clear_mod = 2
        if type(rooted) == complex:
            if rooted.real == 0:
                output = '±' + change_e(rooted.imag) + '*i'
            else:
                rooted_imag = change_e(rooted.imag)
                if rooted_imag[0] != '-':
                    rooted_imag = '+' + rooted_imag
                output = f'±({change_e(rooted.real)}{rooted_imag}*i)'
        else:
            output = '±' + change_e(rooted)

        screen['state'] = "normal"
        screen.delete(0, 'end')
        screen.insert(0, output)
        screen['state'] = "readonly"

        return

    if type(rooted) == complex:
        output = round(rooted.real, point) + round(rooted.imag, point) * 1j
        output = str(output).replace('j', 'i')
        output = '±' + output
    else:
        output = '±' + str(round(rooted, point))

    screen['state'] = "normal"
    screen.delete(0, 'end')
    screen.insert(0, output)
    screen['state'] = "readonly"


# Variables
cur_lang = LANGUAGES[0]
clear_mod = False

# Creating a window
box = tk.Tk()
box.title(TITLE[cur_lang])
box.resizable(width=False, height=False)
box.geometry(f"{WIDTH}x{HEIGHT}")

frame = tk.Frame(box)
frame.place(relwidth=1, relheight=1)

# Switching languages

languages_box = onclick_bind_combobox(frame, values=LANGUAGES, state='readonly')
languages_box.place(width=100, height=25, y=5, x=5)
languages_box.current(0)

# Documentation button
doc_button = tk.Button(text=DOC_BUTTON_TEXT[cur_lang], command=show_doc, bd=1, relief='solid', bg='#AAA', fg='#FFF')
doc_button.place(width=80, height=25, y=5, x=WIDTH - 85)

# Website button
website_button = tk.Button(text=WEBSITE_BUTTON_TEXT[cur_lang], command=open_website, bd=1, relief='solid', bg='#AAA',
                           fg='#FFF')
website_button.place(width=80, height=25, y=5, x=WIDTH - 170)

# Accuracy slider
acc_text = tk.Label(frame, text=ACC_TEXT[cur_lang])
acc_text.place(width=60, height=20, x=5, y=50)
acc_scale = tk.Scale(frame, from_=0, to=16, orient=tk.HORIZONTAL)
acc_scale.place(width=WIDTH - 70, height=50, x=65, y=30)

# Screen
screen = tk.Entry(frame, font=f'{FONT} 38', justify='right', state='readonly')
screen.place(relwidth=1, height=90, y=80)

scroll_X = tk.Scrollbar(screen, command=screen.xview, orient=tk.HORIZONTAL)
scroll_X.pack(side=tk.BOTTOM, fill=tk.X)
screen['xscrollcommand'] = scroll_X.set

# Buttons grid
calc_input = tk.Canvas(frame)
calc_input.place(width=WIDTH - 10, height=HEIGHT - 180, x=5, y=175)
for i in range(6):
    calc_input.grid_columnconfigure(i, minsize=98)
    calc_input.grid_rowconfigure(i, minsize=98)

# Buttons
buttons = [
    create_operation_btn(0, '+', 'operator'),
    create_operation_btn(1, '-', 'operator'),
    create_operation_btn(2, '*', 'operator'),
    create_operation_btn(3, '/', 'operator'),
    create_operation_btn(4, '^', 'operator'),

    create_symbol_btn(5, '7',  'digit'),
    create_symbol_btn(6, '8',  'digit'),
    create_symbol_btn(7, '9',  'digit'),
    create_symbol_btn(10, '4', 'digit'),
    create_symbol_btn(11, '5', 'digit'),
    create_symbol_btn(12, '6', 'digit'),
    create_symbol_btn(15, '1', 'digit'),
    create_symbol_btn(16, '2', 'digit'),
    create_symbol_btn(17, '3', 'digit'),
    create_symbol_btn(20, '0', 'digit'),

    create_symbol_btn(8, 'π',  'const_symbol'),
    create_symbol_btn(13, 'e', 'const_symbol'),
    create_symbol_btn(18, 'i', 'const_symbol'),

    create_symbol_btn(9,  'sin', 'trigonometric_function'),
    create_symbol_btn(14, 'cos', 'trigonometric_function'),
    create_symbol_btn(19, 'tg',  'trigonometric_function'),
    create_symbol_btn(24, 'ctg', 'trigonometric_function'),

    create_symbol_btn(21, '.', 'bracket_or_dot'),
    create_symbol_btn(22, '(', 'bracket_or_dot'),
    create_symbol_btn(23, ')', 'bracket_or_dot'),
]

# Backspace button
buttons.append(
    HoverButton(
        calc_input,
        _type='clear',
        text='←',
        command=backspace,
        bd=1,
        relief='solid',
        font=f'{FONT} 25',
        bg=DEFAULT_COLORS['clear']
    )
)
buttons[25].grid(row=5, column=0, stick='nesw', padx=3, pady=3)

# Clear button
buttons.append(
    HoverButton(
        calc_input,
        _type='clear',
        text=CALC_CLEAR_BUTTON_TEXT[cur_lang],
        command=clear_screen,
        bd=1,
        relief='solid',
        font=f'{FONT} 25',
        bg=DEFAULT_COLORS['clear']
    )
)
buttons[26].grid(row=5, column=1, columnspan=2, stick='nesw', padx=3, pady=3)

# Calculate button
buttons.append(
    HoverButton(
        calc_input,
        _type='calculate',
        text=CALC_BUTTON_TEXT[cur_lang],
        command=pre_calculate,
        bd=1,
        relief='solid',
        font=f'{FONT} 24',
        bg=DEFAULT_COLORS['calculate']
    )
)
buttons[27].grid(row=5, column=3, columnspan=2, stick='nesw', padx=3, pady=3)


if __name__ == '__main__':
    frame.mainloop()
