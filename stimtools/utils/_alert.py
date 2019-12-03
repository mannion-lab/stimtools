import ctypes


def windows_alert_box(msg, style=0):
    """Pop up an alert box on Windows.

    From https://stackoverflow.com/questions/2963263/how-can-i-create-a-simple-message-box-in-python

    Styles:
    0 : OK
    1 : OK | Cancel
    2 : Abort | Retry | Ignore
    3 : Yes | No | Cancel
    4 : Yes | No
    5 : Retry | No 
    6 : Cancel | Try Again | Continue
    """

    response = ctypes.windll.user32.MessageBoxW(0, msg, "Alert", style)

    return response