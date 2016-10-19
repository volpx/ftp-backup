def gui():
    try:
        from dialog import Dialog#used for gui interaction
    except ImportError:
        print('Please install pythondialog to use the gui :(')
        print('You can run: pip install pythondialog')
        exit(-1)
