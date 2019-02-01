# Try to include everything needed so no extra info needs to be saved

class MRecord:
  
  def create(self, id, players, roleDict):
    raise NotImplementedError()

  def start(self):
    raise NotImplementedError()

  def vote(self, voter_id, votee_id, day):
    raise NotImplementedError()

  def mafia_target(self, p_id, target_id, night):
    raise NotImplementedError()

  def target(self, p_id, target_id, night):
    raise NotImplementedError()

  def reveal(self, p_id, day, distracted):
    raise NotImplementedError()

  def elect(self, voter_ids, target_id, day, roles):
    raise NotImplementedError()

  def murder(self, mafia_ids, target_id, night, successful, roles):
    raise NotImplementedError()

  def day(self):
    raise NotImplementedError()

  def night(self):
    raise NotImplementedError()

  def end(self, winner, phase, day):
    raise NotImplementedError()

  def archive(self):
    raise NotImplementedError()

class PrintMRecord:
  
  def create(self, g_id, players, roleDict):
    print("CREATE {}".format(g_id))

  def start(self):
    print("START")

  def vote(self, voter_id, votee_id, day):
    print("VOTE {} {}".format(voter_id, votee_id))

  def mafia_target(self, p_id, target_id, night):
    print("MTARGET {} {}".format(p_id, target_id))

  def target(self, p_id, target_id, night):
    print("TARGET {} {}".format(p_id, target_id))

  def reveal(self, p_id, day, distracted):
    print("REVEAL {} {}".format(p_id, distracted))

  def elect(self, voter_ids, target_id, day, roles):
    print("ELECT {}".format(target_id))

  def murder(self, mafia_ids, target_id, night, successful, roles):
    print("MURDER {} {}".format(target_id, 'success' if successful else 'failure'))

  def day(self):
    print("DAY")

  def night(self):
    print("NIGHT")

  def end(self, winner, phase, day):
    print("END {} {} {}".format(winner, phase, day))

  def archive(self):
    print("archive")

class TestMRecord(MRecord):

  def __init__(self, pattern):
    """ pattern is a list of strings representing which events should occur

    A line that is "*" will accept any one line
    A line that is "***" will accept lines until the following line appears
    "*" and "***" lines shouldn't be adjacent
    """
    self.active = True
    self.log = "Start\n"
    self.pattern_pairs = []
    self.line = 0
    line_nbr = 1
    for line in pattern:
      raw_line = line
      line = line.split('#')[0]
      line = line.strip()
      pair = (line,line_nbr,raw_line)
      if not (line == "" or line[0] == '#'):
        self.pattern_pairs.append(pair)
      line_nbr += 1

    if len(self.pattern_pairs) > 0:
      self.next_line = self.pattern_pairs[0]
      self.curr_line = None
    else:
      # Exception?
      pass

  def __next_line(self):

    self.line += 1

    if len(self.pattern_pairs) > self.line:
      self.next_line = self.pattern_pairs[self.line]
    else:
      self.next_line = None
    if len(self.pattern_pairs) > self.line-1:
      self.curr_line = self.pattern_pairs[self.line-1]  
    else:
      self.curr_line = None

  def __compare(self, line):

    if self.next_line == None and not self.curr_line == "***":
      self.log += "ERROR: Extra generated line: {}\n".format(line)
      return
    if (not self.next_line == None and 
        (line == self.next_line[0] or 
         '*' == self.next_line[0])):
      self.log += "Matched line {}: {}{}\n".format(
        self.next_line[1],
        '('+self.next_line[2]+') ' if self.next_line[0] == '*' else '',
        line
      )
      self.__next_line()
    else:
      if self.next_line[0] == '***':
        self.__next_line()
      if self.curr_line != None and self.curr_line[0] == '***':
        self.log += "Matched line {}: ({}) {}\n".format(
          self.curr_line[1], self.curr_line[2], line
        )
        return
      # Line doesn't match. log and continue?
      self.log += "ERROR: Mismatched line {}: ({}) {}\n".format(
        self.next_line[1], self.next_line[2], line
      )
      self.__next_line()

  def create(self, g_id, players, roleDict):
    self.__compare(
      "CREATE {}".format(g_id)
    )

  def start(self):
    self.__compare(
      "START"
    )

  def vote(self, voter_id, votee_id, day):
    self.__compare(
      "VOTE {} {}".format(voter_id, votee_id)
    )

  def mafia_target(self, p_id, target_id, night):
    self.__compare(
      "MTARGET {} {}".format(p_id, target_id)
    )

  def target(self, p_id, target_id, night):
    self.__compare(
      "TARGET {} {}".format(p_id, target_id)
    )

  def reveal(self, p_id, day, distracted):
    self.__compare(
      "REVEAL {} {}".format(p_id, distracted)
    )

  def elect(self, voter_ids, target_id, day, roles):
    self.__compare(
      "ELECT {}".format(target_id)
    )

  def murder(self, mafia_ids, target_id, night, successful, roles):
    self.__compare(
      "MURDER {} {}".format(target_id, 'success' if successful else 'failure')
    )

  def day(self):
    self.__compare(
      "DAY"
    )

  def night(self):
    self.__compare(
      "NIGHT"
    )

  def end(self, winner, phase, day):
    self.__compare(
      "END {} {} {}".format(winner, phase, day)
    )

  def archive(self):
    if not self.next_line == None:
      while not self.next_line == None:
        self.log += "ERROR: Remaining line {}: {}\n".format(
          self.next_line[1], self.next_line[2]
        )
        self.__next_line()
    self.active = False
