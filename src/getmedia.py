"""Download and maintain media from Youtube, Twitter, Instagram."""


import sys
import os
import shutil
import re
from abc import ABCMeta
import instaloader
from instaloader import Post
from youtube_dl import YoutubeDL
from multiprocessing import Pool

# Constant variables
IS_INSTA_PATTERN = re.compile(r'instagram\.com/p/')
INSTA_SHORTCODE_PATTERN = re.compile(r'/p/(.+)/')
TEMP_FILE_NAME = 'Temporary'
TEMP_YT_NAME = 'Temporary/youtube'
TEMP_INSTA_NAME = 'Temporary/instagram'
PERM_FILE_NAME = 'Permanent'


def block_print():
    """Toggle block all print statements in script."""
    sys.stdout = open(os.devnull, 'w')


def enable_print():
    """Toggle enable all print statements in script."""
    sys.stdout = sys.__stdout__


class Media(metaclass=ABCMeta):
    """An abstract Base class to acquire and maintain media from internet."""

    def __init__(self):
        """Construct method."""
        self.CWD = re.sub(
                      '\\\\',  # pattern
                      '/',     # replace
                      os.getcwd()  # string
                      )

    def download_insta(self, path, url):
        """Download Instagram media from given URL and save to given Path."""
        shortCode = INSTA_SHORTCODE_PATTERN.search(url).group(1)

        instance = instaloader.Instaloader(
                                           download_video_thumbnails=False,
                                           compress_json=False,
                                           save_metadata=False,
                                           post_metadata_txt_pattern='',
                                           dirname_pattern=path
                                            )

        post = Post.from_shortcode(instance.context, shortCode)
        instance.download_post(post, target='')

    def download_youtube(self, path, url):
        """Download Youtube and Twitter media from given URL and save to given Path."""
        optionsYT = {
                     'format': 'best',
                     'outtmpl': '{}/%(title)s'.format(path)+'.mp4',
                     'noplaylist': True,
                     'extract-audio': True,
                     }

        with YoutubeDL(optionsYT) as ydl:
            block_print()
            ydl.download([url])
            enable_print()

    def process_media(self, pathYT, pathIG, *url):
        """Input URLs to respected methods and save them in given paths."""
        listOfURLs = list({*url})  # Avoid repetitions
        IG = []
        YT = []

        # Assign each URL to its respective method
        for URL in listOfURLs:
            if IS_INSTA_PATTERN.search(URL):
                IG.append([pathIG, URL])
            else:
                YT.append([pathYT, URL])

        # If there is only one URL, do not initiate Pool for YT
        if len(YT) > 1:
            with Pool() as pool:
                pool.starmap(self.download_youtube, YT)
        elif len(YT) == 1:
            self.download_youtube(YT[0][0], YT[0][1])

        # If there is only one URL, do not initiate Pool for IG
        if len(IG) > 1:
            with Pool() as pool:
                pool.starmap(self.download_insta, IG)
        elif len(IG) == 1:
            self.download_insta(IG[0][0], IG[0][1])

    def dir_create(self, folderName):
        """Check if directory exist, create it if it does not."""
        path = self.CWD + '/' + folderName

        if os.path.isdir(path) is False:
            os.makedirs(folderName)
        return path


class SentMedia(Media):
    """Download and remove media inside ``with`` statement.

    Works with Youtube, Twitter and Instagram
    """

    def __init__(self):
        """Construct method."""
        super().__init__()
        self.tempFolder = self.dir_create(TEMP_FILE_NAME)

    def __enter__(self):
        """Create YT and IG files under ``self.tempFolder`` directory."""
        self.tempYT = self.dir_create(TEMP_YT_NAME)
        self.tempIG = self.dir_create(TEMP_INSTA_NAME)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Remove YT and IG files under ``self.tempFolder`` directory."""
        shutil.rmtree(self.tempYT)
        shutil.rmtree(self.tempIG)

    def send_media(self, *url):
        """Abstract class functionality to temporarily download media to one command."""
        self.process_media(self.tempYT, self.tempIG, *url)


class SavedMedia(Media):
    """Download and maintain media."""

    def __init__(self):
        """Construct method."""
        super().__init__()
        self.permFolder = self.dir_create(PERM_FILE_NAME)

    def save_media(self, cmd, *url):
        """Abstract class functionality to permanently download media."""
        commandFolder = self.get_command_path(cmd)
        self.process_media(commandFolder, commandFolder, *url)

        return self.show_media_names(cmd)

    def show_media_names(self, cmd):
        """Get titles of media related to command."""
        commandFolder = self.get_command_path(cmd)

        if os.path.isdir(commandFolder):

            mediaNamesList = os.listdir(commandFolder)
            return mediaNamesList

        return [
                'There is no media '
                'linked with the command:'
                ' \' {} \''.format(cmd)
                ]

    def show_media(self, cmd):
        """Get absolute directory path of media related to cmd."""
        commandFolder = self.get_command_path(cmd)

        if os.path.isdir(commandFolder):

            show_mediaList = []
            names = os.listdir(commandFolder)

            for i in range(len(names)):
                show_mediaList.append(commandFolder
                                     + '/'
                                     + names[i]
                                     )

            return show_mediaList

        return [
                'There is no media linked '
                'with the command \' {} \''.format(cmd)
                ]

    def show_media(self, cmd):
        """Delete saved media related to command."""
        commandFolder = self.get_command_path(cmd)

        if os.path.isdir(commandFolder):
            deletedMediaList = self.show_media_names(cmd)
            shutil.rmtree(commandFolder)
            return deletedMediaList

        return [
                'There are no media linked '
                'with the command \' {} \''.format(cmd)
                ]

    def get_command_path(self, cmd):
        """Get the path of command folder."""
        commandFolder = self.permFolder + '/' + cmd
        return commandFolder
