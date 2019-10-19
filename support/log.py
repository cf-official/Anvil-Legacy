# Logger.py - Written by Fatalcenturion between the dates of (DD/MM/YYYY) 15/10/2019
# and /10/2019 for use with Sparky, the CodeForge official Discord bot
# Provided free of charge and free of warranty.

from enum import Enum
from time import gmtime, strftime

# Temporary import
from colorama import Fore
from colorama import Back

class Logger(Enum):
    # FG white, BG Blue
    #INFO = "\x1b[48;2;0;0;255mINFO\x1b[0m     "
    INFO = Fore.YELLOW+"INFO"+Fore.RESET+"     "
    # FG black, BG green
    #OK = "\x1b[48;2;0;255;0m\x1b[38;2;0;0;0mOK\x1b[0m       "
    OK = Fore.GREEN+"OK"+Fore.RESET+"       "
    # FG ?, BG ?
    #VERBOSE = "\x1b[48;2;128;128;128mVERBOSE\x1b[0m  "
    VERBOSE = Fore.LIGHTBLUE_EX+"VERBOSE"+Fore.RESET+"  "
    # FG ?, BG ?
    #DEBUG = "\x1b[48;2;240;230;140m\x1b[38;2;0;0;0mDEBUG\x1b[0m    "
    DEBUG = Fore.WHITE+"DEBUG"+Fore.RESET+"    "
    # FG white, BG red
    #ERROR = "\x1b[48;2;255;0;0mERROR\x1b[0m    "
    ERROR = Fore.RED+"ERROR"+Fore.RESET+"    "

    # Log output to console, handle variations if custom=True
    @staticmethod
    def log(tag, content, source="Client", custom=False, rgb=["110", "110", "110", False]):
        if type(tag) is Logger:
            #text = "  \x1b[38;2;120;171;70m"+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"\x1b[0m  |  "+tag.value + format_source(source) + content
            text = "  \x1b[38;2;120;171;70m"+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"\x1b[0m  |  "+tag.value + Logger.format_source(source) + content
            print(text)
        else:
            if custom:
                if isinstance(rgb, list):
                    #text = "  \x1b[38;2;120;171;70m"+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"\x1b[0m  |  "+Logger.custom(rgb, tag) + content
                    text = "  \x1b[38;2;120;171;70m"+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"\x1b[0m  |  "+Logger.custom(rgb, tag) + content
                    print(text)
            else:
                #text = "  \x1b[38;2;120;171;70m"+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"\x1b[0m  |            " + content
                text = "  \x1b[38;2;120;171;70m"+strftime("%Y-%m-%d %H:%M:%S", gmtime())+"\x1b[0m  |            " + content
                print(text)

    #snip and slice the source tag until it formatted properly for logging
    @staticmethod
    def format_source(content):
        if len(content) > 10:
            content = "[" + content[0:9] + '...]' #split the content at the 10th character and square brace
        else:
            content = "[" + content + ']' # square brace the content
        spacer = ""
        while (len(spacer)+len(content)) < 19:
            spacer += " " #add a single space to the spacer to allow the logs full alignment
        return "\x1b[1;35m"+content+"\x1b[0m"+spacer

    # Perform custom logging
    @staticmethod
    def custom(rgb, tag):
        if len(tag) < 10:
            if rgb[3] & rgb[3] is True:
                content = "\x1b[48;2;" + rgb[0] + ";" + rgb[1] + ";" + rgb[2] + "m\x1b[38;2;0;0;0m" + tag + "\x1b[0m"
            else:
                content = "\x1b[48;2;" + rgb[0] + ";" + rgb[1] + ";" + rgb[2] + "m" + tag + "\x1b[0m"
            spacer = ""
            while (len(spacer)+len(tag)) < 9:
                spacer += " "
            return content+spacer
        else:
            return ""
