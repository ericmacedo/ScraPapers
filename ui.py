import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from typing import Tuple


class UI(ttk.Frame):
    __title: str = "ScraPapers"
    __file_types: Tuple[str] = (
        ('text files', '*.txt'),
        ('Tabular files', '*.tsv, *.csv'))

    def __init__(self, window: tk.Tk, width: int = 265, height: int = 350):
        self.__window = window
        self.__geometry = dict(width=width, height=height)

        self.__window.title(self.__title)
        self.__window.resizable(False, False)
        self.__window.geometry(
            f"{self.__geometry['width']}x{self.__geometry['height']}")

        # self.__window.iconbitmap("icon.ico")

        self.__initUI()

    def __initUI(self) -> None:
        # File selection
        # Label
        self.__file_label_var = tk.StringVar()
        self.__file_label = ttk.Label(
            self.__window, textvariable=self.__file_label_var)
        self.__file_label.grid(column=0, row=0, padx=10, pady=10, ipadx=20)
        self.__set_file_label(None)

        # Button
        self.__file_picker = ttk.Button(
            self.__window, text='Open File', command=self.__open_file_dialog)
        self.__file_picker.grid(column=1, row=0, padx=10, pady=10, ipadx=20)

        # Select field in tabular file
        self.__field_var = tk.StringVar()
        self.__field = ttk.Combobox(
            self.__window, textvariable=self.__field_var,
            values=[f"text {i}" for i in range(100)],
            state=tk.DISABLED)
        self.__field.grid(columnspan=2, row=1, padx=10, pady=10, sticky='we')

        # DOI number list
        self.__doi_list = tk.Listbox(self.__window)

        # Adding Listbox to the left
        # side of root window
        self.__doi_list.grid(row=2, columnspan=2, padx=10,
                             pady=10, sticky='we')

        # Insert elements into the listbox
        for values in range(100):
            self.__doi_list.insert(tk.END, values)

        # Override
        self.__override_var = tk.StringVar()
        self.__override = ttk.Checkbutton(
            self.__window, text='Override', variable=self.__override_var, onvalue=True, offvalue=False)
        self.__override.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        self.__scrape = ttk.Button(
            self.__window, text='Scrape', command=self.__start_scrape)
        self.__scrape.grid(column=1, row=3, padx=10, pady=10, sticky="e")

    def __open_file_dialog(self) -> None:
        filename = tk.filedialog.askopenfilenames(
            title='Open file',
            initialdir='/',
            filetypes=self.__file_types)

        self.__set_file_label(filename)

    def __set_file_label(self, filename: str):
        if not filename:
            filename = "No file selected"

        self.__file_label_var.set(filename)

    def __field_selected(self) -> None:
        pass

    def __start_scrape(self) -> None:
        pass


def main() -> None:
    # create the root window
    window = tk.Tk()
    ui = UI(window)
    window.mainloop()


if __name__ == "__main__":
    main()
