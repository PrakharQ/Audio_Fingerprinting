#!/usr/bin/python
import os
import numpy
import sys
import libs
import libs.fingerprint as fingerprint
import argparse
from scipy.io.wavfile import read
from argparse import RawTextHelpFormatter
from itertools import izip_longest
from termcolor import colored
from libs.reader_file import FileReader
from libs.config import get_config
from libs.reader_microphone import MicrophoneReader
from libs.visualiser_console import VisualiserConsole as visual_peak
from libs.visualiser_plot import VisualiserPlot as visual_plot
from libs.db_sqlite import SqliteDatabase
# from libs.db_mongo import MongoDatabase

if __name__ == '__main__':
  for filename in os.listdir("house_data/"):
    if filename.endswith(".txt"):
      file_name="house_data/"+filename
      config = get_config()

      db = SqliteDatabase("20_mins/"+filename[0]+filename[1]+"/fingerprints2.db")

      parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
      parser.add_argument('-s', '--seconds', nargs='?')
      args = parser.parse_args()

      # if not args.seconds:
      #   parser.print_help()
      #   sys.exit(0)

      #seconds = int(args.seconds)

      chunksize = 2**12  # 4096
      channels = 2#int(config['channels']) # 1=mono, 2=stereo

      record_forever = False
      visualise_console = bool(config['mic.visualise_console'])
      visualise_plot = bool(config['mic.visualise_plot'])


      def grouper(iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return (filter(None, values) for values
                in izip_longest(fillvalue=fillvalue, *args))




      # reader.save_recorded('test.wav')


      Fs = fingerprint.DEFAULT_FS


      result = set()
      matches = []

      def return_matches(hashes):
        mapper = {}
        for hash, offset in hashes:
          mapper[hash.upper()] = offset
        values = mapper.keys()

        for split_values in grouper(values, 1000):
          # @todo move to db related files
          query = """
            SELECT upper(hash), song_fk, offset
            FROM fingerprints
            WHERE upper(hash) IN (%s)
          """
          query = query % ', '.join('?' * len(split_values))

          x = db.executeAll(query, split_values)
          matches_found = len(x)

          #if matches_found > 0:
           # msg = '   ** Found %d hash matches'
            #print colored(msg, 'green') % matches_found
            
          #else:
           # msg = '   ** No matches found '
            #print colored(msg, 'red') 
            

          for hash, sid, offset in x:
            # (sid, db_offset - song_sampled_offset)
            yield (sid, offset - mapper[hash])

      #filename=raw_input()
      with open(file_name,'r') as f:
          hashes=[tuple([i.split(' ')[0],int(i.split(' ')[1])]) for i in f]
      matches.extend(return_matches(hashes))


      def align_matches(matches):
        diff_counter = {}
        largest = 0
        largest_count = 0
        song_id = -1

        for tup in matches:
          sid, diff = tup

          if diff not in diff_counter:
            diff_counter[diff] = {}

          if sid not in diff_counter[diff]:
            diff_counter[diff][sid] = 0

          diff_counter[diff][sid] += 1

          if diff_counter[diff][sid] > largest_count:
            largest = diff
            largest_count = diff_counter[diff][sid]
            song_id = sid

        songM = db.get_song_by_id(song_id)

        nseconds = round(float(largest) / fingerprint.DEFAULT_FS *
                         fingerprint.DEFAULT_WINDOW_SIZE *
                         fingerprint.DEFAULT_OVERLAP_RATIO, 5)

        return {
            "SONG_ID" : song_id,
            "SONG_NAME" : songM[1],
            "CONFIDENCE" : largest_count,
            "OFFSET" : int(largest),
            "OFFSET_SECS" : nseconds
        }

      total_matches_found = len(matches)

      print ''

      if total_matches_found > 0:
        msg = ' ** Totally found %d hash matches'
        print colored(msg, 'green') % total_matches_found

        song = align_matches(matches)

        msg = ' => song: %s (id=%d)\n'
        #msg += '    offset: %d (%d secs)\n'
        #msg += '    confidence: %d'

        print colored(msg, 'white') % (
          song['SONG_NAME'], song['SONG_ID']
          #song['OFFSET'], song['OFFSET_SECS'],
          #song['CONFIDENCE']    
        )
      else:
        msg = '   ** No matches found at all'
        print colored(msg, 'red')
      
      
      
      
      #code for advertisement recognition
      db = SqliteDatabase("advertisement_data/fingerprints1.db")

      parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
      parser.add_argument('-s', '--seconds', nargs='?')
      args = parser.parse_args()

      # if not args.seconds:
      #   parser.print_help()
      #   sys.exit(0)

      #seconds = int(args.seconds)

      chunksize = 2**12  # 4096
      channels = 2#int(config['channels']) # 1=mono, 2=stereo

      record_forever = False
      visualise_console = bool(config['mic.visualise_console'])
      visualise_plot = bool(config['mic.visualise_plot'])
      
      
      
      Fs = fingerprint.DEFAULT_FS


      result = set()
      matches = []
      
      with open(file_name,'r') as f:
          hashes=[tuple([i.split(' ')[0],int(i.split(' ')[1])]) for i in f]
      matches.extend(return_matches(hashes))
      
      
      total_matches_found = len(matches)

      print ''
      song = align_matches(matches)
      if total_matches_found > 0 and song['CONFIDENCE']>5:
        msg = '   ** Totally found %d hash matches'
        print colored(msg, 'green') % total_matches_found

        

        msg = ' => Advertisement: %s (id=%d)\n'
        #msg += '    offset: %d (%d secs)\n'
        #msg += '    confidence: %d'

        print colored(msg, 'white') % (
          song['SONG_NAME'], song['SONG_ID'],
          #song['OFFSET'], song['OFFSET_SECS'],
          #song['CONFIDENCE']    
        )
      else:
        msg = 'No Advertisement match'
        print colored(msg, 'red')
      
