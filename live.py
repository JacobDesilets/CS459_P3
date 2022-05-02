import tkinter as tk


# https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback/40618152#40618152
class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + '_orig'
        self.tk.call('rename', self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        if command in ('insert', 'delete', 'replace'):
            self.event_generate('<<TextModified>>')

        return result


root = tk.Tk()
label = tk.Label(root, anchor='w')
text = CustomText(root, width=40, height=4)

label.pack(side='bottom', fill='x')
text.pack(side='top', fill='both', expand=True)


def on_text_change(event):
    txt = event.widget.get('1.0', 'end-1c')
    label.configure(text=txt)


text.bind('<<TextModified>>', on_text_change)

root.mainloop()
