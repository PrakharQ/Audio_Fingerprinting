#!/usr/bin/python
import os
import sys
import libs
import time
import libs.fingerprint as fingerprint
from termcolor import colored
from libs.reader_file import FileReader
from libs.db_sqlite import SqliteDatabase
from libs.config import get_config

if __name__ == '__main__':

      # fingerprint all files in a directory

      for filename in os.listdir("advertisements/"):
        config = get_config()
        if filename.endswith(".mp3"):
         if(os.path.getsize("advertisements/"+filename)<>346L):
          file_name="advertisement_data/fingerprints1.db"
          db = SqliteDatabase(file_name)
          reader = FileReader("advertisements/" + filename)
          audio = reader.parse_audio()

          song = db.get_song_by_filehash(audio['file_hash'])
          song_id = db.add_song(filename, audio['file_hash'])

          msg = ' * %s %s: %s' % (
            colored('id=%s', 'white', attrs=['dark']),       # id
            colored('channels=%d', 'white', attrs=['dark']), # channels
            colored('%s', 'white', attrs=['bold'])           # filename
          )
          print msg % (song_id, len(audio['channels']), filename)

          if song:
            hash_count = db.get_song_hashes_count(song_id)

            if hash_count > 0:
              msg = '   Already exists (%d hashes), skip' % hash_count
              print colored(msg, 'red')

              continue

          print colored('   New Audio File, Going to Analyze!..', 'green')

          hashes = set()
          channel_amount = len(audio['channels'])

          for channeln, channel in enumerate(audio['channels']):
            msg = '   Fingerprinting channel %d/%d'
            print colored(msg, attrs=['dark']) % (channeln+1, channel_amount)

            channel_hashes = fingerprint.fingerprint(channel, Fs=audio['Fs'], plots=config['fingerprint.show_plots'])
            channel_hashes = set(channel_hashes)

            msg = '   Finished Channel %d/%d, got %d hashes'
            print colored(msg, attrs=['dark']) % (
              channeln+1, channel_amount, len(channel_hashes)
            )

            hashes |= channel_hashes

          msg = '   Finished Fingerprinting, got %d unique hashes'

          values = []
          for hash, offset in hashes:
            values.append((song_id, hash, offset))

          msg = '   storing %d hashes in db' % len(values)
          print colored(msg, 'green')

          db.store_fingerprints(values)

      print('end')
