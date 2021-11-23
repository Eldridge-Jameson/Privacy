from otree.api import *
c = cu

doc = ''
class Constants(BaseConstants):
    name_in_url = 'Privacy_Initialization'
    players_per_group = None
    num_rounds = 1
    questions = ('Are you attracted to anyone in the room?', 'Have you ever been arrested?', 'Can you imagine pursuing a political career?')

class Subsession(BaseSubsession):
    pass
def displayQuestion(group):
    import random
    import copy
    
    questions = copy.deepcopy(Constants.question_stack)
    #now append the players questions here
    
    #then suffle
    random.shuffle(questions)
    #group.current_question = questions[0]
    
class Group(BaseGroup):
    answer_yeses = models.IntegerField(initial=0)
    number_of_players = models.IntegerField(initial=0)

def set_name(group):
    for p in group.get_players():
        participant = p.participant
        participant.username = p.name


def determine_host(player):
    session = player.session
    if player.host == True:
        session.host = player.id_in_group
def determine_valid_id(player):
    session = player.session
    group = player.group
    participant = player.participant
    p_host= group.get_player_by_id(session.host)
    session.invalid_Ids =[]
    if(participant.id_in_session == session.host):
        participant.is_dropout = False
    elif player.id_InGroup != p_host.host_Id:
        session.invalid_Ids.append(player.id_in_group)
        participant.is_dropout= True
    else:
        participant.is_dropout=False

class Player(BasePlayer):
    id_InGroup = models.IntegerField()
    name = models.StringField(label='Enter your name')
    host = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], initial=False, label=' ')
    host_Id = models.IntegerField()
    enter_question = models.LongStringField(blank=True, label='Enter a question you would like to ask the group here:')
    is_dropout = models.BooleanField(initial=False)

class Welcome_Page(Page):
    form_model = 'player'
    form_fields = ['host','name']
    @staticmethod
    def before_next_page(player, timeout_happened):
        import random
        num = random.randint(0,189753)
        player.host_Id = num
        determine_host(player)
class Host_Session(Page):
    form_model = 'player'
    @staticmethod
    def is_displayed(player):
        return player.host==True
    @staticmethod
    def before_next_page(player, timeout_happened):
        determine_valid_id(player)
class Join_session(Page):
    form_model = 'player'
    form_fields = ['id_InGroup']
    @staticmethod
    def is_displayed(player):
        return player.host==False
    @staticmethod
    def before_next_page(player, timeout_happened):
        determine_valid_id(player)
class Invalid_id(Page):
    form_model = 'player'
    form_fields = ['id_InGroup']
    @staticmethod
    def is_displayed(player):
        session = player.session
        group = player.group
        check = player.id_in_group in session.invalid_Ids
        return check
    @staticmethod
    def before_next_page(player, timeout_happened):
        determine_valid_id(player)
class Invalid_ID_dropout(Page):
    form_model = 'player'
    timeout_seconds = 10
    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.is_dropout
class WaitPage1(WaitPage):
    body_text = 'Waiting for all the players to join'
    after_all_players_arrive = set_name

class Write_Questions(Page):
    form_model = 'player'
    form_fields = ['enter_question']
    @staticmethod
    def is_displayed(player):
        group = player.group
        participant = player.participant
        return participant.is_dropout==False
    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        participant.vars["added_questions"] = player.enter_question
        
        
page_sequence = [Welcome_Page, Host_Session, Join_session, Invalid_id, Invalid_ID_dropout, WaitPage1, Write_Questions]
