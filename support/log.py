# Logger.py - Written by Fatalcenturion between the dates of (DD/MM/YYYY) 15/10/2019
# and /10/2019 for use with Sparky, the CodeForge official Discord bot
# Provided free of charge and free of warranty.

from enum import Enum
from time import gmtime, strftime
from colorama import Fore


class Logger(Enum):
    INFO = Fore.YELLOW + "INFO" + Fore.RESET + "    |  "
    OK = Fore.GREEN + "OK" + Fore.RESET + "      |  "
    VERBOSE = Fore.LIGHTBLUE_EX + "VERBOSE" + Fore.RESET + " |  "
    DEBUG = Fore.WHITE + "DEBUG" + Fore.RESET + "   |  "
    ERROR = Fore.RED + "ERROR" + Fore.RESET + "   |  "

    # Log the headers of the log table (optional, just makes it look neater)
    @staticmethod
    def log_headers():
        print("       Timestamp       | Log Type |        Source       |  Content\n"
              "  ---------------------+----------+---------------------+-------------------------------------")

    # Log output to console, handle variations if custom=True
    @staticmethod
    def log(tag, content="===============================", source="Client", custom=False,
            rgb=["110", "110", "110", False]):
        if type(tag) is Logger:
            text = "  \x1b[38;2;120;171;70m" + strftime("%Y-%m-%d %H:%M:%S",
                                                        gmtime()) + "\x1b[0m  |  " + tag.value + Logger.format_source(
                source) + content
            print(text)
        else:
            if custom:
                if isinstance(rgb, list):
                    text = "  \x1b[38;2;120;171;70m" + strftime("%Y-%m-%d %H:%M:%S",
                                                                gmtime()) + "\x1b[0m  |  " + Logger.custom(rgb,
                                                                                                           tag) + content
                    print(text)
            else:
                text = "  \x1b[38;2;120;171;70m" + strftime("%Y-%m-%d %H:%M:%S",
                                                            gmtime()) + "\x1b[0m  |            " + content
                print(text)

    # Log a custom "spacer" with centered text up to 30 chars long
    @staticmethod
    def log_titled_spacer(content="===============================", filler=" "):
        spacer = ""

        while (len(spacer) + len(content) + len(spacer)) < 30:
            spacer += filler
        spacebar = "==" + spacer + content + spacer + "=="
        text = "  \x1b[38;2;120;171;70m" + strftime("%Y-%m-%d %H:%M:%S",
                                                    gmtime()) + "\x1b[0m  |          |                     |  " + spacebar
        print(text)

    # Snip and slice the source tag until it formatted properly for logging
    @staticmethod
    def format_source(source):
        if source != "Client":
            source = source.name
        if len(source) > 12:
            # Split the content at the 10th character and square brace
            source = "[" + source[0:11] + '...]'
        else:
            # Square brace the content
            source = "[" + source + ']'
        spacer = ""
        # Align logs properly by adding spaces
        while (len(spacer) * 2 + len(source)) < 18:
            spacer += " "
        return spacer + "\x1b[1;35m" + source + "\x1b[0m" + spacer + " |  "

    # Perform custom logging
    @staticmethod
    def custom(rgb, tag):
        if len(tag) < 10:
            if rgb[3] & rgb[3] is True:
                content = "\x1b[48;2;" + rgb[0] + ";" + rgb[1] + ";" + rgb[2] + "m\x1b[38;2;0;0;0m" + tag + "\x1b[0m"
            else:
                content = "\x1b[48;2;" + rgb[0] + ";" + rgb[1] + ";" + rgb[2] + "m" + tag + "\x1b[0m"
            spacer = ""
            while (len(spacer) + len(tag)) < 9:
                spacer += " "
            return content + spacer
        else:
            return ""
