from datetime import datetime
from time import time, sleep
import shutil
import os

class FileStructure():

	def __init__(self, path):
		self.path = path
		self.files = []
		self.folders = []
		self._get_files_and_folders()	#Exec on init


	def _get_files_and_folders(self):
		for item in os.listdir(self.path):
			if os.path.isdir(os.path.join(self.path, item)):
				self.folders.append(item)
			else:
				self.files.append(item)

	def get_files(self):
		return self.files
	
	def get_folders(self):
		return self.folders
	
	def get_path(self):
		return self.path
	
	def get_full_path(self, item):
		return os.path.join(self.path, item)
	
	def get_modif_time(self, item):
		return os.path.getmtime(self.get_full_path(item))




class Sync():

	def __init__(self, origin, destination, log_path):
		self.origin = FileStructure(origin)			# Origin folder as FileStructure object
		self.destination = FileStructure(destination)	# FileStructure object
		self.log_path = log_path
		self._sync()

	def _sync(self):

		def write_log(action, item_path):
			with open(self.log_path, 'a') as logfile:
				date_time = datetime.now().strftime('%d/%m/%Y_%H:%M:%S - ')
				logfile.write(date_time + action + item_path + '\n')

		# Check all the files
		for file in self.origin.get_files():
			file_path = self.destination.get_full_path(file)
			# If file not in destination folder, copy it
			if file not in self.destination.get_files():
				action = 'Copying: '
				print(action + file_path)
				write_log(action, file_path)
				shutil.copy2(self.origin.get_full_path(file), self.destination.get_path())
			
			# File in dest folder, check modification time
			elif self.origin.get_modif_time(file) > self.destination.get_modif_time(file):
				action = 'Updating: '
				print(action + file_path)
				write_log(action, file_path)
				shutil.copy2(self.origin.get_full_path(file), self.destination.get_path())

		# Check all the folders
		for folder in self.origin.get_folders():
			folder_path = self.destination.get_full_path(folder)

			# If folder not in destination, copy it
			if folder not in self.destination.get_folders():
				action = 'Copying: '
				print(action + folder_path)
				write_log(action, folder_path)
				shutil.copytree(self.origin.get_full_path(folder), self.destination.get_full_path(folder)) #copy2 by default
			
			# Folder in dest, call Sync() recursivly on that folder
			else:
				Sync(self.origin.get_full_path(folder), self.destination.get_full_path(folder), self.log_path)

		# Check for deleted files
		for file in self.destination.get_files():
			if file not in self.origin.get_files():
				file_path = self.destination.get_full_path(file)
				action = 'Deleting: '
				print(action + file_path)
				write_log(action, file_path)
				os.remove(file_path)

		# Check for deleted folders
		for folder in self.destination.get_folders():
			if folder not in self.origin.get_folders():
				folder_path = self.destination.get_full_path(folder)
				action = 'Deleting: '
				print(action, folder_path)
				shutil.rmtree(folder_path)

def main():

	# Ask folders paths and logfile path
	origin = str(input('Origin folder path: '))
	destination = str(input('Destination folder path: '))
	log_path = str(input('Logfile path: '))
	log_path = log_path + r'\logfile.txt'

	# Sync interval
	interval = float(input('Syncronization interval (in minutes): '))
	interval = interval * 60

	while True:
		start_time = time()
		Sync(origin, destination, log_path)
		sleep(interval - (time() - start_time) % interval)

if __name__ == '__main__':
	main()