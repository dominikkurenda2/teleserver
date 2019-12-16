import alsaaudio
import base64
from datetime import datetime
from io import BytesIO
import pyscreenshot as ImageGrab
from subprocess import call
import webbrowser
from Xlib.error import DisplayNameError
import yaml

from tools.common import UPLOAD_DIRECTORY

try:
    from pynput.keyboard import Controller
    x_display = True
except DisplayNameError:
    print("Couldn't find connected DISPLAY. Keyboard input is disabled.")
    x_display = False


URL_SCHEMES = ('file://',
               'ftp://',
               'gopher://',
               'hdl://',
               'http://',
               'https://',
               'imap://',
               'mailto://',
               'mms://',
               'news://',
               'nntp://',
               'prospero://',
               'rsync://',
               'rtsp://',
               'rtspu://',
               'sftp://',
               'shttp://',
               'sip://',
               'sips://',
               'snews://',
               'svn://',
               'svn+ssh://',
               'telnet://',
               'wais://',
               'ws://',
               'wss://')


def url_parser(url):
    """Parse url.
    If URL does not contain any of url schemas at the beginning
    then add https:// at the beginning.

    :param url: URL to parse
    :type url: str

    :return: Parsed URL
    :rtype: str
    """
    if url.startswith(URL_SCHEMES):
        return url
    else:
        return 'https://' + url


def close():
    """Close web browser
    """
    call(["pkill", "chrome"])


def web_open(url):
    """Open URL in web browser

    :param url: URL to open
    :type url: str
    """
    webbrowser.open(url_parser(url), new=0)


def poweroff():
    """Power off the machine
    """
    call(['systemctl', 'poweroff', '-i'])


def reboot():
    """Reboot the machine
    """
    call(['systemctl', 'reboot', '-i'])


def screenshot():
    """Make a screenshot
    """
    date = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    call(['gnome-screenshot',
          '-f',
          '{dir}/{date}'
          .format(dir=UPLOAD_DIRECTORY,
                  date=date)])


def mute():
    """Mute the machine
    """
    vol = alsaaudio.Mixer()
    vol.setvolume(0)


def volume(volume):
    """Set volume level on the machine

    :param volume: Volume level
    :type volume: int
    """
    vol = alsaaudio.Mixer()
    vol.setvolume(volume)


def xdotool_key(keys):
    """Call xdotool with specific keys

    :param keys: Keys to call
    :type keys: str
    """
    call(['xdotool', 'key', keys])


def type_keyboard(word):
    """Type specific word with spoofed keyboard

    :param word: Word to enter
    :param word: str
    """
    if x_display:
        keyboard = Controller()
        keyboard.type(word)
        del keyboard
    else:
        pass


def get_volume():
    """Get current level of volume

    :return: Volume level
    :rtype: int
    """
    vol = alsaaudio.Mixer()
    value = vol.getvolume()
    return value[0]


def get_screen():
    """Get current snapshot of machine's screen

    :return: Screen's snapshot
    :rtype: base64.bytes
    """
    screen = ImageGrab.grab()
    buffered_screen = BytesIO()
    screen.save(buffered_screen, format='JPEG')
    return base64.b64encode(buffered_screen.getvalue()).decode('utf-8')


def url_history(url):
    """ Saves casted url in file

    """

    with open('/var/lib/teleserver/app/config_teleserver.yml', 'r') as file:
        urls = yaml.load(file, Loader=yaml.FullLoader)
        urls_to_hist = urls.get("urls")
        urls_config = urls.get("url_config")

    if urls_to_hist is not None:
        if len(urls_to_hist) < urls_config:
            urls_to_hist.append(urls_to_hist[len(urls_to_hist) - 1])
            for x in range(len(urls_to_hist)-1, -1, -1):
                urls_to_hist[x] = urls_to_hist[x-1]
        else:
            if len(urls_to_hist) > urls_config:
                del urls_to_hist[urls_config:len(urls_to_hist)]
            for x in range((urls_config-1), -1, -1):
                urls_to_hist[x] = urls_to_hist[x-1]
        urls_to_hist[0] = url
    else:
        urls_to_hist = []
        urls_to_hist.append(url)

    with open('/var/lib/teleserver/app/config_teleserver.yml', 'w') as file:
        yaml.dump(dict(urls=urls_to_hist, url_config=urls_config), file)


def get_url_history():
    """Get array of casted urls

    :return: Array of urls
    :rtype: array
    """
    with open('/var/lib/teleserver/app/config_teleserver.yml') as file:
        urls = yaml.load(file, Loader=yaml.FullLoader)
        urls_hist = urls.get("urls")
    return urls_hist
