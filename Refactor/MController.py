
# Has a function for every possible command
# Each command fn has a standard form
# These commands form an interface that controls the overall operation of the app

# command(group_id, message_id, member_id, data)

# group_id is the id of the group that the message was sent to.
# member_id is the id of the player who sent the message
# message_id is the id of the message sent
# data will contain any other necessary information for the command to process.

# The server program will process requests and port them into the correct command fn


class MController

  

  def command(self, keyword, group_id, message_id, member_id, data):
    if keyword in self.commands:
      self.commands[keyword](group_id, message_id, member_id, data)
    

  def start_command(self, group_id, message_id, member_id, data):
    
    
  def in_command(self, group_id, message_id, member_id, data):

  def out_command(self, group_id, message_id, member_id, data):
    
  def watch_command(self, group_id, message_id, member_id, data):
    
  def rule_command(self, group_id, message_id, member_id, data):
    
  def stats_command(self, group_id, message_id, member_id, data):

  def vote_command(self, group_id, message_id, member_id, data):
    
  def status_command(self, group_id, message_id, member_id, data):
    
  def help_command(self, group_id, message_id, member_id, data):
    
  def timer_command(self, group_id, message_id, member_id, data):
    
  def leave_command(self, group_id, message_id, member_id, data):
    
  def target_command(self, group_id, message_id, member_id, data):

  def options_command(self, group_id, message_id, member_id, data):

  def reveal_command(self, group_id, message_id, member_id, data):
    
    
    
    