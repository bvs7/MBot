

class MRecord:
  
  def create(self, id, players):
    raise NotImplementedError()

  def start(self):
    raise NotImplementedError()

  def vote(self, voter, votee):
    raise NotImplementedError()

  def mafia_target(self, target):
    raise NotImplementedError()

  def target(self, player, target):
    raise NotImplementedError()

  def reveal(self, player):
    raise NotImplementedError()

  def nokill(self):
    raise NotImplementedError()

  def kill(self, player):
    raise NotImplementedError()

  def day(self):
    raise NotImplementedError()

  def night(self):
    raise NotImplementedError()

  def investigate(self, cop, target):
    raise NotImplementedError()

  def save(self, doctor, target):
    raise NotImplementedError()

  def town_wins(self):
    raise NotImplementedError()

  def mafia_wins(self):
    raise NotImplementedError()

  def archive(self):
    raise NotImplementedError()

class FileMRecord(MRecord):
  """Saves recorded info to a file"""

  def __init__(self, record_filename):
    """Create a record system that works on the given record folder"""
    self.record_filename = record_filename
    self.log = ""

  def create(self, id, players):
    actual = "CREATE {} {}".format(id, " ".join([str(p) for p in players]))
    self.log += actual + "\n"

  def start(self):
    self.log += "START\n"

  def vote(self, voter, votee):
    actual = "VOTE {} {}".format(voter, votee)
    self.log += actual + "\n"

  def mafia_target(self, target):
    actual = "MAFIA_TARGET {}".format(target)
    self.log += actual + "\n"

  def target(self, player, target):
    actual = "TARGET {} {}".format(player, target)
    self.log += actual + "\n"

  def reveal(self, player):
    actual = "REVEAL {}".format(player)
    self.log += actual + "\n"

  def nokill(self):
    self.log += "NOKILL\n"

  def kill(self, player):
    actual = "KILL {}".format(player)
    self.log += actual + "\n"

  def day(self):
    self.log += "DAY\n"

  def night(self):
    self.log += "NIGHT\n"

  def investigate(self, cop, target):
    actual = "INVESTIGATE {} {}".format(cop,target)
    self.log += actual + "\n"

  def save(self, doctor, target):
    actual = "SAVE {} {}".format(doctor, target)
    self.log += actual + "\n"

  def town_wins(self):
    self.log += "TOWN_WINS\n"

  def mafia_wins(self):
    self.log += "MAFIA_WINS\n"

  def archive(self):
    record_file = open(self.record_filename, "a")
    record_file.write(self.log.strip())
    self.log = ""
    record_file.close()


class TestMRecord(MRecord):

  def __init__(self, pattern):
    """ pattern is a list of strings representing which events should occur """
    self.pattern = pattern
    self.line = 0
    self.log = ""

  def create(self, id, players):
    expected = self.get_next_pattern()
    actual = "CREATE {} {}".format(id, " ".join([str(p) for p in players]))
    self.test_check(expected,actual)

  def start(self):
    expected = self.get_next_pattern()
    actual = "START"
    self.test_check(expected,actual)

  def vote(self, voter, votee):
    expected = self.get_next_pattern()
    actual = "VOTE {} {}".format(voter, votee)
    self.test_check(expected,actual)

  def mafia_target(self, target):
    expected = self.get_next_pattern()
    actual = "MAFIA_TARGET {}".format(target)
    self.test_check(expected,actual)

  def target(self, player, target):
    expected = self.get_next_pattern()
    actual = "TARGET {} {}".format(player, target)
    self.test_check(expected,actual)

  def reveal(self, player):
    expected = self.get_next_pattern()
    actual = "REVEAL {}".format(player)
    self.test_check(expected,actual)

  def nokill(self):
    expected = self.get_next_pattern()
    actual = "NOKILL"
    self.test_check(expected,actual)

  def kill(self, player):
    expected = self.get_next_pattern()
    actual = "KILL {}".format(player)
    self.test_check(expected,actual)

  def day(self):
    expected = self.get_next_pattern()
    actual = "DAY"
    self.test_check(expected,actual)

  def night(self):
    expected = self.get_next_pattern()
    actual = "NIGHT"
    self.test_check(expected,actual)

  def investigate(self, cop, target):
    expected = self.get_next_pattern()
    actual = "INVESTIGATE {} {}".format(cop,target)
    self.test_check(expected,actual)

  def save(self, doctor, target):
    expected = self.get_next_pattern()
    actual = "SAVE {} {}".format(doctor, target)
    self.test_check(expected,actual)

  def town_wins(self):
    expected = self.get_next_pattern()
    actual = "TOWN_WINS"
    self.test_check(expected,actual)

  def mafia_wins(self):
    expected = self.get_next_pattern()
    actual = "MAFIA_WINS"
    self.test_check(expected,actual)

  def test_check(self, expected, actual):
    print("	{:3d}|".format(self.line)+actual,end='')
    assert expected == actual, "{}\n{}".format(expected,actual)
    print(u"\u2713")

  def get_next_pattern(self):
    expected = self.pattern.pop(0)
    self.line += 1
    while expected.strip() == "" or expected.strip()[0] == '#':
      print(expected)
      expected = self.pattern.pop(0)
      self.line += 1
    return expected

  def archive(self):
    pass

  
  