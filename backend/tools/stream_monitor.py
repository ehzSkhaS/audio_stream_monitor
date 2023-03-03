import os
import csv
import time
import threading
from datetime import datetime

'''GLOBAL'''
source_name = []
source_place = []
source_ip = []
source_url = []
headers = ['state', 'volume', 'timestamp']
abs_path = os.getcwd() + '/backend/'
'''GLOBAL'''


def data_load():
  '''
    load the source data
    from which gather the information
    to process
  '''
  try:
    with open(abs_path + 'tools/data.csv', newline = '') as source_data:
      for row in csv.DictReader(source_data):    
        source_name.append(row['\ufeffname'])
        source_place.append(row['place'])
        source_ip.append(row['ip'])
        source_url.append('https://icecast.teveo.cu/' + row['url'])
  except IOError as error:
    print(error)
  

def create_folder_structure():
  '''
    create the report folder
    for each radio station
    and one for the icecast server
  '''
  try:
    # os.makedirs(abs_path + 'reports/_ICECAST', exist_ok = True)
    for n in source_name:
      os.makedirs(abs_path + 'reports/' + n, exist_ok = True)
  except OSError as error:
    print(error)
  

def _create_report_file(today_file):
  '''
    create the a report file
    with the name as the date
    of the errors     
  '''
  try:
    with open(today_file, 'w', newline='', encoding='utf-8') as meta_data:
      writer = csv.DictWriter(meta_data, fieldnames=headers)
      writer.writeheader()      
      return today_file
  except OSError as error:
    print(error)
    
    
def _error_report(index, state = 'Down', volume = 'None'):
  '''
    if the report file doesn't exist,
    then calls the create_report_file() func,
    else adds a record of the error to the existing one
  '''
  from os.path import exists
  today_file = abs_path + 'reports/' + source_name[index] + '/' + datetime.today().strftime('%Y-%m-%d') + '.csv'
  if not exists(today_file):
    _create_report_file(today_file)
  
  try:
    with open(today_file, 'a', newline = '', encoding = 'utf-8') as error_data:
      now = datetime.now().strftime('%I: %M: %S %p')
      writer = csv.DictWriter(error_data, fieldnames = headers)
      writer.writerow({'state': state, 'volume': volume, 'timestamp': now})
  except OSError as error:
    print(error)


def _ffmpeg_volume_filter(index):
  '''
    uses the ffmpeg system audio filter: volumedetect
    to capture the data to a file
  '''
  record_file_path_terminal = abs_path + 'reports/' + source_name[index].replace(' ', '\ ') + '/_volumedetect_last_record.log'
  
  try:    
    os.system(
      "ffmpeg -hide_banner -re -i " + 
      source_url[index] + 
      " -y -filter:a volumedetect -vn -sn -dn -f null -t 10 /dev/null 2>" + 
      record_file_path_terminal
    )
  except OSError as error:
    print(error)


def _station_state(index):
  '''
    check the file captured by volumedetect filter
    to determine if there is an audio stream
  '''
  record_file_path_python = abs_path + 'reports/' + source_name[index] + '/_volumedetect_last_record.log'
  
  try:
    with open(record_file_path_python, 'r', newline = '', encoding = 'utf-8') as target_data:
      search_for = ('HTTP error 404',)
      station_state = "Up"
      for row in target_data.readlines():
        
        # station state #
        state = row.find(search_for[0])        
        if state != -1:
          station_state = "Down"
        # station state #
        
      return station_state
  except IOError as error:
    print(error)
  

def _station_volume(index):
  '''
    measure the volume levels of the audio stream
    and create a categorical qualification
  '''
  record_file_path_python = abs_path + 'reports/' + source_name[index] + '/_volumedetect_last_record.log' 
  
  try:
    with open(record_file_path_python, 'r', newline = '', encoding = 'utf-8') as target_data:
      search_for = ('mean_volume',)
      mean_value = "None"
      for row in target_data.readlines():
        
        # mean volume #
        mean = row.find(search_for[0])
        if mean != -1:
          mean_value = float(row[mean + 13:-4])
          if mean_value > -10:
            mean_value = "High"
          elif mean_value > -20:
            mean_value = "Normal"
          elif mean_value > -30:
            mean_value = "Low"
          elif mean_value > -40:
            mean_value = "Too Low"
          else:
            mean_value = "Silence"
        # mean volume #

      return mean_value
  except IOError as error:
    print(error)


def apply_filters(index):
  '''
    callback function to apply
    filters per thread
  '''
  _ffmpeg_volume_filter(index)  
  station_state = _station_state(index)
  station_volume = _station_volume(index)
  print(source_name[index], ' ', station_state, ' ', station_volume)
  
  if station_state == "Up":
    if station_volume != "Normal":
      _error_report(index, state=station_state, volume=station_volume)
  else:
      _error_report(index)


def main():
  data_load()
  create_folder_structure()
  while 1:
    for n in range(16):
      n_thread = threading.Thread(target=apply_filters, args=(n,))
      n_thread.start()
    time.sleep(12)
    for n in range(17, 32):
      n_thread = threading.Thread(target=apply_filters, args=(n,))
      n_thread.start()
    time.sleep(12)
    for n in range(33, 48):
      n_thread = threading.Thread(target=apply_filters, args=(n,))
      n_thread.start()
    time.sleep(12)
    for n in range(49, 64):
      n_thread = threading.Thread(target=apply_filters, args=(n,))
      n_thread.start()
    time.sleep(12)
    for n in range(65, 80):
      n_thread = threading.Thread(target=apply_filters, args=(n,))
      n_thread.start()
    time.sleep(12)
    for n in range(81, 97):
      n_thread = threading.Thread(target=apply_filters, args=(n,))
      n_thread.start()
    time.sleep(12)


if __name__ == "__main__":
  main()
