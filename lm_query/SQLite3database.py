# Copyright 2019 Zhaozhen Liang
import sqlite3
import sys

class Database:
	"""Handling SQLite3 database"""
	def __init__(self, databaseFile):
		self.databaseFile = databaseFile
		self.connect()

	def connect(self):
		"""Connect to database"""
		try:
			# connection to database
			self.connection = sqlite3.connect(self.databaseFile)
			# cursor
			self.cursor = self.connection.cursor()
			#check if successfully connected to database
			if not self.connection or not self.cursor:
				#display error msge
				raise ValueError("failed to connect to {}", self.databaseFile)
		except Exception as e:
			print(str(e))
			sys.exit(1)

	def close(self):
		"""Close connection"""
		try:
			self.connection.close()
		except Exception as e:
			print(str(e))
			sys.exit(1)

	def execute(self, SQLstatements):
		"""
		Input: SQL statments string to be executed
		"""
		try:
			self.cursor.executescript(SQLstatements)
		except Exception as e:
			print(str(e))
			sys.exit(1)

	def getConnection(self):
		return self.connection

	def getCursor(self):
		return self.cursor

	def commit(self):
		try:
			self.connection.commit()
		except Exception as e:
			print(str(e))
			sys.exit(1)

	def initInsertString(self):
		self.InsertString = ""

	def addInsertString(self, SQLstring):
		self.InsertString += SQLstring

	def getInsertString(self):
		return self.InsertString

	def addBeginTransactionString(self):
		self.InsertString += "BEGIN TRANSACTION; "

	def addCommitString(self):
		self.InsertString += " COMMIT;"

	def fetchall(self):
		return self.cursor.fetchall()
	
	def fetchone(self):
		return self.cursor.fetchone()
