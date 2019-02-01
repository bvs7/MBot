class MState:

  def __init__(self, id, mainComm, mafiaComm, lobbyComm, rules, roles, rec, MTimerClass=MTimer):
    
  def start_game(self):
       
  def vote(self, voter_id, votee_id):
    
  def mafia_target(self, p_id, target_option):
    
  def mafia_options(self):
		
  def target(self, p_id, target_option):
	
  def send_options(self,p_id,prompt=None):
      
  def try_reveal(self, p_id):

  def reveal(self,p):
		
  def revealTeam(self,p):
      
  def getPlayer(self, p):
			
  def setTimer(self, player_id):

  def unSetTimer(self, player_id):