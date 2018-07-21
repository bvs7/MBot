

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


class TestMRecord(MRecord):

  def __init__(self, pattern):
    """ pattern is a list of strings representing which events should occur """
    self.pattern = pattern
    self.log = ""

  def create(self, id, players):
    expected = self.pattern.pop(0)
    actual = "CREATE {} {}".format(id, " ".join([str(p) for p in players]))
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def start(self):
    expected = self.pattern.pop(0)
    actual = "START"
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def vote(self, voter, votee):
    expected = self.pattern.pop(0)
    actual = "VOTE {} {}".format(voter, votee)
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def mafia_target(self, target):
    expected = self.pattern.pop(0)
    actual = "MAFIA_TARGET {}".format(target)
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def target(self, player, target):
    expected = self.pattern.pop(0)
    actual = "TARGET {} {}".format(player, target)
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def reveal(self, player):
    expected = self.pattern.pop(0)
    actual = "REVEAL {}".format(player)
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def nokill(self):
    expected = self.pattern.pop(0)
    actual = "NOKILL"
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def kill(self, player):
    expected = self.pattern.pop(0)
    actual = "KILL {}".format(player)
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def day(self):
    expected = self.pattern.pop(0)
    actual = "DAY"
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def night(self):
    expected = self.pattern.pop(0)
    actual = "NIGHT"
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def investigate(self, cop, target):
    expected = self.pattern.pop(0)
    actual = "INVESTIGATE {} {}".format(cop,target)
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def save(self, doctor, target):
    expected = self.pattern.pop(0)
    actual = "SAVE {} {}".format(doctor, target)
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def town_wins(self):
    expected = self.pattern.pop(0)
    actual = "TOWN_WINS"
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def mafia_wins(self):
    expected = self.pattern.pop(0)
    actual = "MAFIA_WINS"
    self.log += actual + "\n"
    assert expected == actual, "{}\n{}".format(expected,actual)

  def archive(self):
    print(self.log)

  
  