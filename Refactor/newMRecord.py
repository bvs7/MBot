# Try to include everything needed so no extra info needs to be saved

class MRecord:
  
  def create(self, id, players, roleDict):
    raise NotImplementedError()

  def start(self):
    raise NotImplementedError()

  def vote(self, voter_id, votee_id, day):
    """Voter and votee are player objects"""
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
