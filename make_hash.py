#!/usr/bin/python
import os
import sys
import libs
import libs.fingerprint as fingerprint
import argparse
import datetime
from argparse import RawTextHelpFormatter
from itertools import izip_longest
from termcolor import colored
from libs.config import get_config
from libs.reader_microphone import MicrophoneReader
from libs.visualiser_console import VisualiserConsole as visual_peak
from libs.visualiser_plot import VisualiserPlot as visual_plot


if __name__ == '__main__':
  config = get_config()


  time= datetime.datetime.now()
  filename=time.strftime("%M")+".txt"
  parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
  parser.add_argument('-s', '--seconds', nargs='?')
  args = parser.parse_args()

  if not args.seconds:
    parser.print_help()
    sys.exit(0)

  seconds = int(args.seconds)

  chunksize = 2**12  # 4096
  channels = 2#int(config['channels']) # 1=mono, 2=stereo

  record_forever = False
  visualise_console = bool(config['mic.visualise_console'])
  visualise_plot = bool(config['mic.visualise_plot'])

  reader = MicrophoneReader(None)

  reader.start_recording(seconds=seconds,
    chunksize=chunksize,
    channels=channels)

  msg = ' * started recording..'
  print colored(msg, attrs=['dark'])

  while True:
    bufferSize = int(reader.rate / reader.chunksize * seconds)

    for i in range(0, bufferSize):
      nums = reader.process_recording()

      if visualise_console:
        msg = colored('   %05d', attrs=['dark']) + colored(' %s', 'green')
        print msg  % visual_peak.calc(nums)
      else:
        msg = '   processing %d of %d..' % (i, bufferSize)
        print colored(msg, attrs=['dark'])

    if not record_forever: break

  if visualise_plot:
    data = reader.get_recorded_data()[0]
    visual_plot.show(data)

  reader.stop_recording()

  msg = ' * recording has been stopped'
  print colored(msg, attrs=['dark'])



  def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return (filter(None, values) for values
            in izip_longest(fillvalue=fillvalue, *args))

  data = reader.get_recorded_data()

  msg = ' * recorded %d samples'
  print colored(msg, attrs=['dark']) % len(data[0])

  # reader.save_recorded('test.wav')


  Fs = fingerprint.DEFAULT_FS
  channel_amount = len(data)

  result = set()
  matches = []

  def find_matches(samples, Fs=fingerprint.DEFAULT_FS):
    hashes = fingerprint.fingerprint(samples, Fs=Fs)
    hashes=list(hashes)
    #filename=raw_input()
    with open("house_data/"+filename, 'w') as fp:
        fp.write('\n'.join('%s %s' % x for x in hashes))

  for channeln, channel in enumerate(data):
    # TODO: Remove prints or change them into optional logging.
    msg = '   fingerprinting channel %d/%d'
    print colored(msg, attrs=['dark']) % (channeln+1, channel_amount)

    find_matches(channel)

    msg = '   finished channel %d/%d, got %d hashes'
    print colored(msg, attrs=['dark']) % (
      channeln+1, channel_amount, len(matches)
    )
