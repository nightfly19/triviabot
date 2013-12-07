import sqlite3 as db
import sys
import re

class Question():
    def __init__(self, category, question, answer, db):
        self.category = category
        self.question = question
        self.answer = answer
        self.db = db
        pass

    def asked(self):
        query = "update or ignore questions set asked = asked + 1 where question = ? and answer = ?;"
        temp = self.db._one_from_query(query, (self.question, self.answer))
        self.db.commit()
        return temp

    def answered(self):
        query = "update or ignore questions set answered = answered + 1 where question = ? and answer = ?;"
        temp = self.db._one_from_query(query, (self.question, self.answer))
        self.db.commit()
        return temp

class Questions():
    def __init__(self, db_filename):
        self.__db_filename = db_filename
        self.db = db.connect(self.__db_filename)
        cur = self.db.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS questions (prikey INTEGER PRIMARY KEY ASC AUTOINCREMENT, category CHAR not null, question CHAR unique not null, answer CHAR not null, asked INT DEFAULT 0, answered INT DEFAULT 0);')
        cur.execute('CREATE INDEX IF NOT EXISTS questions_category ON questions (category);')
        cur.execute('CREATE INDEX IF NOT EXISTS questions_answer ON questions (answer);')
        cur.execute('CREATE INDEX IF NOT EXISTS questions_asked ON questions (asked);')
        cur.execute('CREATE INDEX IF NOT EXISTS questions_answered ON questions (answered);')
        self.commit()
        
    def add(self, category, question, answer):
        query = "insert or ignore into questions (category, question, answer) values (?, ?, ?);"
        cur = self.db.cursor()
        temp = cur.execute(query, (category, question, answer))
        cur.close()
        return temp

    def import_file(self, question_file):
        raw = open(question_file,'r')
        for line in raw:
            self.add(*re.match('^([^:]+):\s+([^`]+)`(\S+)',line).groups())
        self.db.commit()

    def _one_from_query(self, query, args=()):
        cur = self.db.cursor()
        cur.execute(query, args)
        temp = cur.fetchone()
        cur.close()
        return temp
        
    def random(self):
        query = 'select category, question, answer from questions order by random() asc limit 1'
        return Question(*(self._one_from_query(query) + (self,)))

    def good_random(self):
        query = 'select * from questions order by answered asc, asked asc, random() asc limit 1'
        return Question(*(self._one_from_query(query) + (self,)))

    def commit(self):
        self.db.commit()

    def close(self):
        self.commit()
