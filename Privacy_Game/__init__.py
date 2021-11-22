

from otree.api import *
c = cu

doc = '\na.k.a. Keynesian beauty contest.\nPlayers all guess a number; whoever guesses closest to\n2/3 of the average wins.\nSee https://en.wikipedia.org/wiki/Guess_2/3_of_the_average\n'
class Constants(BaseConstants):
    name_in_url = 'Privacy_Game'
    players_per_group = None
    num_rounds = 2
    question_stack = ('Are you attracted to anyone in the game?', 'Have you ever been arrested?', 'Can you imagine pursuing a political career?')
    num_players = 2
    instructions_template = 'Privacy_Game/instructions.html'


class Subsession(BaseSubsession):
    player_ranking = models.IntegerField()
def display_question(group):
    session = group.session
    import random
    random.shuffle(session.quesstion_bank)
    while(session.quesstion_bank[0] in session.used_questions):
        random.shuffle(session.quesstion_bank)
    
    
    group.current_question = session.quesstion_bank[0]
    session.used_questions.append(session.quesstion_bank[0])
    print(group.current_question)

def calculate_rewards(group):
    pass
    
    
    
def get_total_yes(group):
    pass
def update_player_ranking(group):
    pass
def consolidate_question_list(group):
    import copy
    import random
    
    questions = copy.deepcopy(Constants.question_stack)
    additional_questions = []
    
    for player in group.get_players():
        if player.participant.is_dropout == False:
            additional_questions.append(player.participant.vars["added_questions"])
    
    consolidated_list = list(questions) + additional_questions
    #print(consolidated_list)
    
    random.shuffle(consolidated_list)
    #print(consolidated_list)
    pick_from = [i for i in range(len(consolidated_list))]
    
    order_of_questions = []
    for i in range(len(consolidated_list)):
        pick = random.choice(pick_from)
        if pick not in order_of_questions:
            order_of_questions.append(pick)
        #pick_from.pop(pick)
    
    for player in group.get_players():
        player.participant.vars["list_questions"] = consolidated_list
        player.participant.vars["order_of_questions"] = order_of_questions
    
    
    
    
    #print("pick",pick)
    
    #print("additional",additional_questions)
    #print("consolidated",consolidated_list)
class Group(BaseGroup):
    current_question = models.StringField()
    total_yeses = models.IntegerField()

def my_function(player):
    pass
class Player(BasePlayer):
    id_inGroup = models.IntegerField(label='Please enter the ID given by the host')
    answer = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], label='')
    rewards = models.IntegerField()
    name = models.StringField()
    host = models.BooleanField()
    my_field = models.StringField()
    enter_question = models.LongStringField(blank=True, label='Enter question you would like to ask the group')
    guess = models.IntegerField(label='', max=Constants.players_per_group, min=0)

class Wait_page_1(WaitPage):
    after_all_players_arrive = consolidate_question_list
class Answer_Question_Page(Page):
    form_model = 'player'
    form_fields = ['answer']
    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.is_dropout==False

    @staticmethod
    def vars_for_template(player):
        participant = player.participant
        #import random
        
        
        display_question_lis = player.participant.vars["list_questions"]
        
        #question_num = player.participant.vars["order_of_questions"]
        
        
        #print(display_question_lis)
        #print(player.round_number-1)
        
        
        #display_question = display_question_lis[question_num[player.round_number-1]]
        display_question = display_question_lis[0]
        #print(player.participant.vars["order_of_questions"])
        #player.participant.vars["order_of_questions"].pop(0)
        #print(player.participant.vars["order_of_questions"])
        
        player.participant.vars["list_questions"].pop(0)
        return dict([('question', display_question)])

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        participant.vars["answer"] = player.answer
    

        
class Wait_page_2(WaitPage):
    after_all_players_arrive = get_total_yes

class Guess_page(Page):
    form_model = 'player'
    form_fields = ['guess']

    @staticmethod
    def is_displayed(player):
        participant = player.participant
        return participant.is_dropout==False

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        participant.vars["guess"] = player.guess
        print("guess saved", player.guess)

        
class Wait_page_3(WaitPage):
    #after_all_players_arrive = calculate_rewards

    @staticmethod
    def after_all_players_arrive(group: Group):
        session = group.session
        subsession = group.subsession
        #group = player.group
        yeses = 0

        #save answers on participant
        for player in group.get_players():
            if  player.participant.is_dropout == False and player.participant.vars["answer"] == True:
                yeses += 1
    
        print("yeses",yeses)
        for player in group.get_players():
            player.participant.vars["yeses"] = yeses

        
        #setting round rewards here
        for player in group.get_players():
            if yeses == player.participant.vars["guess"]:
                player.participant.vars["round_rewards"] = 3
            elif yeses == (player.participant.vars["guess"] +1 ) or (yeses == player.participant.vars["guess"] -1):
                player.participant.vars["round_rewards"] = 1
            else:
                player.participant.vars["round_rewards"] = 0
                
       
        #updating overall points
        for player in group.get_players():
            if subsession.round_number == 1:
                player.participant.vars["overall_points"]  = 0
            player.participant.vars["overall_points"]  = player.participant.vars["overall_points"] + player.participant.vars["round_rewards"]
            print("points overall:",player.participant.vars["overall_points"])
    
        print("getting here")

        #calculating ranking
        ranking_id = []
        ranking_points = []

        ind = 0
        for player in group.get_players():
            print("p",player)
            if ind == 0:
                ranking_id.append(player.id_in_group)
                ranking_points.append(player.participant.vars["overall_points"])
            else:
                ind2 = 0
                while True:
                    print(ranking_points)
                    print("p",player, "ind2", ind2)
                    if player.participant.vars["overall_points"] > ranking_points[ind2]:
                        ranking_id.insert(ind2,player.id_in_group)
                        ranking_points.insert(ind2, player.participant.vars["overall_points"])
                        break
                    elif ind2+1 >= len(ranking_points):
                        ranking_id.append(player.id_in_group)
                        ranking_points.append(player.participant.vars["overall_points"])
                        break
                    ind2 +=1
                        
            ind +=1

        print("ranking points",ranking_points)
        print("ranking id",ranking_id)
        for player in group.get_players():
            player.participant.vars["ranking points"] = ranking_points
            player.participant.vars["ranking_id"] = ranking_id
        #after_all_players_arrive = calculate_rewards 
    #pass


class Round_results(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        session = player.session
        subsession = player.subsession
        participant = player.participant
        return participant.is_dropout==False and subsession.round_number < Constants.num_rounds

    @staticmethod
    def vars_for_template(player):
        #group = player.group

        ranking_points = player.participant.vars["ranking points"] 
        ranking_id = player.participant.vars["ranking_id"]
        print("ranking points",ranking_points)
        print(Constants.players_per_group)
        return dict(ranking_id= ranking_id, ranking_points= ranking_points, players_per_group = Constants.num_players)


   

class Final_results(Page):
    form_model = 'player'
    @staticmethod
    def is_displayed(player):
        session = player.session
        subsession = player.subsession
        return subsession.round_number == Constants.num_rounds

    @staticmethod
    def vars_for_template(player):
        #group = player.group

        ranking_points = player.participant.vars["ranking points"] 
        ranking_id = player.participant.vars["ranking_id"]
        print("ranking points",ranking_points)
        print(Constants.players_per_group)
        return dict(ranking_id= ranking_id, ranking_points= ranking_points, players_per_group = Constants.num_players)



page_sequence = [Wait_page_1, Answer_Question_Page, Wait_page_2, Guess_page, Wait_page_3, Round_results, Final_results]

