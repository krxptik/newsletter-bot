import pyfiglet

def banner():
    print("=========================")
    text = "ellie!"
    banner = pyfiglet.figlet_format(text)
    print(banner[:-1])
    print("=========================")
    print("\nRunning v0.1.1.\n")