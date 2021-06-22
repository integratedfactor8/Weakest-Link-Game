import os
import sys
import random
import math
import csv
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextNode

CWD = os.getcwd()

# settings

n_players = 9
n_cpus = 8
diff = 1
no_vote_strongest = True

DIFF_NAMES = ("Beginner", "Intermediate", "Advanced", "Expert", "Master") # same for names of difficulties



def secs_to_mins(secs):
    """Converts an number of seconds to a string in the form
    mins:secs"""

    mins_and_secs = divmod(secs, 60)
    str_mins_secs = [str(i) for i in mins_and_secs] # converts to list and string
    if len(str_mins_secs[1]) < 2: # if adds a zero to the seconds if it is 1 digit (eg 4 becomes 04)
        str_mins_secs[1] = "0" + str_mins_secs[1]

    return ":".join(str_mins_secs) # puts in that format with :


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        properties = WindowProperties()
        properties.setSize(1280, 720) # default size
        properties.setTitle("The Weakest Link") # name of window
        self.win.requestProperties(properties)
        self.disableMouse() # stops mouse moving camera
        self.setBackgroundColor(0,0,0) # sets background to black
        self.cbank = 0 # total banked for the round
        self.round = 9-n_players # round to start on
        self.roundmod = 9-n_players # what is subtracted so first round is always displayed as round 1

        self.no_vote_strongest = no_vote_strongest
            
        self.total = 0 # total banked
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.starting_player = 0
        self.toskip = False
        self.autostart = True
        self.sortedplayers = list(players)
        self.round_ongoing = False
        self.sd = False # if sudden death is active
        self.editing_settings = False
        
        #loading files
        
        self.target_sfx = self.loader.loadSfx(CWD+"/music/target-new.ogg")
        self.vbreak = self.loader.loadSfx(CWD+"/music/voting-break-new.ogg")
        self.vloop = self.loader.loadSfx(CWD+"/music/voting-loop-new.ogg")
        self.exitsfx = self.loader.loadSfx(CWD+"/music/exit-new.ogg")
        self.introsfx = self.loader.loadSfx(CWD+"/music/intro-new.ogg")
        self.expsfx = self.loader.loadSfx(CWD+"/music/explain-new.ogg")
        self.nexpsfx = self.loader.loadSfx(CWD+"/music/explain_after_round-new.ogg")
        self.ffirst = self.loader.loadSfx(CWD+"/music/final-intro-new.ogg")
        self.finalloop = self.loader.loadSfx(CWD+"/music/final-loop-new.ogg")
        self.finishsfx = self.loader.loadSfx(CWD+"/music/finish-new.ogg")
        #self.final_end = self.loader.loadSfx(CWD+"/music/final-finish.ogg")
        #self.sdsfx_s = self.loader.loadSfx(CWD+"/music/sd-start.ogg")
        self.sdsfx_l = self.loader.loadSfx(CWD+"/music/sd-loop-new.ogg")
        self.chain_img = OnscreenImage(image=CWD+"/images/chain_n.png", pos=(-1.5,0,0.15), scale=(0.25, 0, 0.83))
        self.chain_img.hide()
        self.arrow = OnscreenImage(image=CWD+"/images/arrow.png", pos=(-1.1,0,-0.62), scale=(0.1, 0, 0.05))
        self.arrow.hide()
        self.finalloop.setLoop(True)
        self.sdsfx_l.setLoop(True)
        self.vloop.setLoop(True)

        # loads questions
        
        QUESTSION_PATH = CWD+"/data/questions.csv"
        self.ALL_QUESTIONS = list(csv.reader(open(QUESTSION_PATH), delimiter=';'))
        self.ALL_QUESTIONS = [x for x in self.ALL_QUESTIONS if x[0][0] != "#"]
        self.cquestions = random.sample(self.ALL_QUESTIONS, len(self.ALL_QUESTIONS))
        

        self.chain_values = [0, 20, 50, 100, 200, 300, 450, 600, 800, 1000]
        self.arrow_zpositions = [-0.62, -0.43, -0.24, -0.05, 0.14, 0.33, 0.52, 0.71, 0.89, 0.95]
        self.chainlv = 0
    


        self.taskMgr.add(self.start_intro)
        self.taskMgr.add(self.stop_intro)


        






    def start_intro(self, task):
        self.introsfx.play()
        self.intropic = OnscreenImage(image=CWD+"/images/start_img.png", pos=(0,0,0))

        self.toskip = False
        self.skipbutton = DirectButton(text="Click to start", scale=0.1, command=self.skip_intro)
        self.autostart_button = DirectButton(text="Autostart: OFF", scale=0.1, command=self.toggle_autostart, pos=(-1.4,0,0.6))
        self.settings_button = DirectButton(text="Settings", scale=0.1, pos=(-1.4,0,-0.8), command=self.show_settings)
        self.autostart = True
        self.autostart_button.setText("Autostart: ON") # it is set after so the size of the button will fit AUTOSTART OFF despite the default being on
        self.skipbutton.setPos(-1.4,0,0.8)
        
        
        return task.done


    def skip_intro(self):
        self.toskip = True

    def show_settings(self):
        # getting rid of main menu stuff
        self.editing_settings = True
        self.intropic.destroy()
        self.introsfx.stop()
        self.autostart_button.destroy()
        self.skipbutton.destroy()
        self.settings_button.destroy()
        self.vloop.play()
        self.s_text = OnscreenText(text="Changing Settings", pos=(0,0.8), scale=0.15, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)
    
        self.main_menu_button = DirectButton(text="Main Menu", scale=0.1, command=self.end_settings, pos=(-1.4,0,0.8))

        # changing number of players
        self.change_player_text = OnscreenText(text="Number of players: "+str(n_players), pos=(-1.25,0.55), scale=0.1, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)
        self.add_player_button = DirectButton(text="+1", scale=0.1, command=self.add_player, pos=(-0.65,0,0.55))
        self.minus_player_button = DirectButton(text="-1", scale=0.1, command=self.minus_player, pos=(-0.45,0,0.55))

        # changing number of cpus
        self.change_cpu_text = OnscreenText(text="Number of CPUs: "+str(n_cpus), pos=(-1.25,0.4), scale=0.1, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)
        self.add_cpu_button = DirectButton(text="+1", scale=0.1, command=self.add_cpu, pos=(-0.65,0,0.4))
        self.minus_cpu_button = DirectButton(text="-1", scale=0.1, command=self.minus_cpu, pos=(-0.45,0,0.4))

        # change cpu difficulty

        self.diff_text = OnscreenText(text="Difficulty: "+str(DIFF_NAMES[diff]), pos=(-1.25,0.25), scale=0.1, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)
        self.diff_down_b = DirectButton(text="Easier", scale=0.08, command=self.diff_down, pos=(-0.58,0,0.25))
        self.diff_up_b = DirectButton(text="Harder", scale=0.08, command=self.diff_up, pos=(-0.3,0,0.25))

        # change no vote strongest
        if no_vote_strongest is True:
            nvs_value = "Disallowed"
        else:
            nvs_value = "Allowed"
        self.nvs_text = OnscreenText(text="Voting for strongest: "+nvs_value, pos=(-1.02,0.1), scale=0.1, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)
        self.nvs_toggle_b = DirectButton(text="Toggle", scale=0.08, command=self.nvs_toggle, pos=(-0.1,0,0.1))

        
        
        

    def end_settings(self):
        global players
        # getting rid of settings stuff
        self.vloop.stop()
        self.main_menu_button.destroy()
        self.minus_player_button.destroy()
        self.add_player_button.destroy()
        self.s_text.destroy()
        self.change_player_text.destroy()
        self.minus_cpu_button.destroy()
        self.add_cpu_button.destroy()
        self.change_cpu_text.destroy()
        self.diff_text.destroy()
        self.diff_down_b.destroy()
        self.diff_up_b.destroy()
        self.nvs_toggle_b.destroy()
        self.nvs_text.destroy()
        
        self.editing_settings = False


        # re adds players to reflect settings change

        players = []
        for number in range (1, n_cpus+1): # adding cpus
            players.append(Player(number, True, diff))

        for number in range(1, (n_players-n_cpus)+1): # adding players
            players.append(Player(number, False))
            

        random.shuffle(players) # shuffles the player order

        # changing values to reflect new player list

        self.sortedplayers = list(players)
        self.round = 9-n_players # round to start on
        self.roundmod = 9-n_players # what is subtracted so first round is always displayed as round 1
        
        self.taskMgr.add(self.start_intro)
        self.taskMgr.add(self.stop_intro)



    # settings commands start here

    def add_player(self):
        global n_players

        n_players = n_players+1

        if n_players > 9:
            n_players = 9
            return # doesn't change

        self.change_player_text.setText("Number of players: "+str(n_players))

        # add more here

    def minus_player(self):
        global n_players, n_cpus

        n_players = n_players-1

        if n_players < 2:
            n_players = 2
            return # doesn't change

        if n_players < n_cpus:
            n_cpus = n_players
            self.change_cpu_text.setText("Number of CPUs: "+str(n_cpus))

        self.change_player_text.setText("Number of players: "+str(n_players))



    def add_cpu(self):
        global n_cpus

        n_cpus = n_cpus+1

        if n_cpus > n_players:
            n_cpus = n_players
            return # doesn't change

        self.change_cpu_text.setText("Number of CPUs: "+str(n_cpus))


    def minus_cpu(self):
        global n_cpus

        n_cpus = n_cpus-1

        if n_cpus < 0:
            n_cpus = 0
            return # doesn't change

        self.change_cpu_text.setText("Number of CPUs: "+str(n_cpus))


    def diff_up(self):
        """ Increases CPU difficulty """

        global diff

        diff = diff+1

        if diff > 4:
            diff = 4
            return # no change


        self.diff_text.setText("Difficulty: "+str(DIFF_NAMES[diff]))



    def diff_down(self):
        """ Decreases CPU difficulty """

        global diff

        diff = diff-1

        if diff < 0:
            diff = 0
            return # no change


        self.diff_text.setText("Difficulty: "+str(DIFF_NAMES[diff]))


    def nvs_toggle(self):
        """ Toggles no_vote_strongest on of off """

        global no_vote_strongest

        if no_vote_strongest is True:
            no_vote_strongest = False
            self.nvs_text.setText("Voting for strongest: Allowed")

        else:
            no_vote_strongest = True
            self.nvs_text.setText("Voting for strongest: Disallowed")

        self.no_vote_strongest = no_vote_strongest

        

        

        



    # settings commands end here
        
        

    def toggle_autostart(self):
        if self.autostart is True:
            self.autostart = False
            self.autostart_button.setText("Autostart: OFF")
        else:
            self.autostart = True
            self.autostart_button.setText("Autostart: ON")

        
    def stop_intro(self, task):
        if self.introsfx.status() == self.introsfx.PLAYING and not self.toskip:
            return task.cont

        elif self.autostart is False and self.toskip is False:
            return task.cont

        elif self.editing_settings is True:
            return task.done

        self.introsfx.stop()

        # destroying intro things     
        self.intropic.destroy()
        self.skipbutton.destroy()
        self.autostart_button.destroy()
        self.settings_button.destroy()
        
        self.taskMgr.add(self.start_explain)
        
        return task.done


    def start_explain(self, task):
        self.chain_img.show()
        self.arrow.show()
        self.expsfx.play()
        self.taskMgr.add(self.stop_explain)
        self.playertext = OnscreenText(text="Here are the players: ", pos=(0.15,0.9), scale=0.07, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)
        self.playerlisttext = OnscreenText(text=", ".join([str(x) for x in players]), pos=(0.15,0.8), scale=0.08, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)

        if self.round == 7:
            self.rtime = 90

        else:
            self.rtime = 180 - 10*self.round

        self.explaination = ("The goal is to try and get 1000 in the bank, the fastest way \n to do this is  by creating a chain of 9 correct answers. \n If you answer incorrectly, you "
                             + "lose everything \n in the chain, but if you click bank before the \n question is asked then you keep everything in the \n chain but must start a new chain. \n \n"
                             + "After each round, everyone votes for someone to be eliminated \n as the weakest link. \n \n The first round lasts "+str(self.rtime)+" seconds, \n we will start with the first player"
                             + " in the random order: \n that's you, "+str(players[0])+". \n\n Let's play, the weakest link.")
        
        self.explaintext = OnscreenText(text=self.explaination, pos=(0.15,0.6), scale=0.08, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)
        
        self.banktext = OnscreenText(text="Bank: "+str(self.cbank), pos=(-1.45,-0.9), scale=0.13, fg=(1, 1, 1, 1), align=TextNode.ACenter, mayChange=1)

        self.taskMgr.doMethodLater(2, self.add_bank_demo, "bank_demo")


    def stop_explain(self, task):
        if self.expsfx.status() == self.expsfx.PLAYING:
            return task.cont

        self.playertext.destroy()
        self.explaintext.destroy()
        self.playerlisttext.destroy()

        self.cbank = 0
        self.chainlv = 0

        self.arrow.setPos((-1.1, 0, -0.62))

        self.banktext.setText("Bank: "+str(self.cbank))

        self.taskMgr.add(self.start_questions, "question_task")


        
        return task.done


    def add_bank_demo(self, task):
        if self.round_ongoing is True:
            return task.done
        
        if self.chainlv == 9:
            self.bank()
            return task.done 
        self.chainlv = self.chainlv+1
        self.arrow.setPos((-1.1, 0, self.arrow_zpositions[self.chainlv]))
        return task.again


    def bank(self):
        
        if self.chainlv > 9:
            tobank = 1000

        else:
            tobank = self.chain_values[self.chainlv]

        self.chainlv = 0
        self.arrow.setPos((-1.1,0,-0.62))
        
        if self.cbank + tobank >= 1000:
            self.cbank = 1000

        else:
            self.cbank = self.cbank + tobank


        self.banktext.setText("Bank: "+str(self.cbank))

        if self.round_ongoing is True:
            self.bank_button.setText("Banked!")
            self.bank_button["state"] = DGG.DISABLED
            self.player_asked.r_bank =  self.player_asked.r_bank+tobank

        return


    def stop_questions(self, task):
        if task.time < self.rtime and self.cbank < 1000:
            self.clock_text.setText("Clock: "+secs_to_mins(math.ceil(self.rtime-task.time)))
            return task.cont

        
        self.round_ongoing = False


        if self.answering is True:
            self.player_asked.r_time = self.player_asked.r_time + (globalClock.getFrameTime() - self.q_start_time)

        if self.cbank == 1000:
            self.target_sfx.play()
            self.rmusic.stop()

        self.taskMgr.remove("ask_questions")
        self.taskMgr.remove("bankchance")
        if self.round == 7:
            self.total = self.total + 3*self.cbank
        else:
            self.total = self.total + self.cbank
        self.player_asked_text.destroy()
        self.question_text.destroy()
        self.bank_button.destroy()
        self.clock_text.destroy()
        self.chainlv = 0
        self.arrow.setPos((-1.1,0,-0.62))
        for button in self.buttons:
            button.destroy()



        for player in players: # determining a score for weakest/strongest link
            thiscorrect = player.correct
            thisincorrect = player.incorrect

            #potential alternative taking into account time to answer and amount banked

            #thiscorrect = thiscorrect + player.r_bank/200 # every 200 banked counts as 1 correct answer
            #thisincorrect = thisincorrect + player.r_time/20 # every 20 sec taken to answer counts as 1 incorrect answer

            try:
                correct_rate = thiscorrect/(thiscorrect+thisincorrect)
            except ZeroDivisionError:
                correct_rate = 0

            player.r_score = correct_rate

    

        self.sortedplayers = sorted(self.sortedplayers, reverse=True, key=lambda x: x.r_time)
        self.sortedplayers = sorted(self.sortedplayers, key=lambda x: x.r_bank)
        self.sortedplayers = sorted(self.sortedplayers, key=lambda x: x.r_score)

##        self.sortedplayers.sort(reverse=True, key=lambda x: x.r_time)
##        self.sortedplayers.sort(key=lambda x: x.r_bank)
##        self.sortedplayers.sort(key=lambda x: x.r_score)

        # sorts based on time, then amount banked, then amount correct in case of a draw



        self.sstrongestlink = self.sortedplayers[-1]
        self.sweakestlink = self.sortedplayers[0]


        self.taskMgr.add(self.after_questions)
        
        return task.done
        


        
    def start_questions(self, task):
        self.r_start_time = globalClock.getFrameTime()
        self.rmusic = self.loader.loadSfx(CWD+"/music/r"+str(self.round)+"-new.ogg")
        self.rmusic.play()

        self.clock_text = OnscreenText(text="Clock: 180", pos=(0.1,-0.8), scale=0.12, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)

        self.cplayer = self.starting_player


        if self.round == 7:
            self.rtime = 90

        else:
            self.rtime = 180 - 10*self.round


        for player in players: # clearing players' previous round stats
            player.correct = 0
            player.r_time = 0
            player.incorrect = 0
            player.r_score = 0
            player.m_banked = 0
            player.votes = 0

        self.round_ongoing = True
        self.player_asked = players[self.cplayer]
        self.player_asked_text = OnscreenText(text="", pos=(0.1,0.8), scale=0.12, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)
        self.question_text = OnscreenText(text="", pos=(0.1,0.5), scale=0.1, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1, wordwrap=22)
        self.bank_button = DirectButton(text="__Bank__", scale=0.1, textMayChange=1, text_align=TextNode.ACenter, state=DGG.DISABLED, command=self.bank, pos=(0.1,0,-0.1))
        self.bank_button.hide()
        self.buttons = []
        self.buttons.append(DirectButton(text="Nothing to show yet, no potential answer", scale=0.1, textMayChange=1, text_align=TextNode.ACenter))
        #frameColor=(0,0,0,0)
        self.buttons[0].setPos((0.1,0,0.1))
        self.buttons.append(DirectButton(text="Nothing to show yet, no potential answer", scale=0.1, textMayChange=1, text_align=TextNode.ACenter))
        self.buttons[1].setPos((0.1,0,-0.1))
        self.buttons.append(DirectButton(text="Nothing to show yet, no potential answer", scale=0.1, textMayChange=1, text_align=TextNode.ACenter))
        self.buttons[2].setPos((0.1,0,-0.3))

        self.taskMgr.add(self.ask_questions, "ask_questions")

        self.taskMgr.add(self.stop_questions)

        return task.done
        


    def ask_questions(self, task):

        #self.cbank = 1000 #debug to skip questions

        self.answering = True
        self.q_start_time = globalClock.getFrameTime()
 
        self.bank_button.hide() # disable banking

        if len(self.cquestions) == 0:
            self.cquestions = random.sample(self.ALL_QUESTIONS, len(self.ALL_QUESTIONS))
            
        full_question = self.cquestions.pop()

        this_question = full_question[0]

        self.player_asked_text.setText("Current Player: "+str(players[self.cplayer]))

        self.question_text.setText(this_question)
        
        c_button = random.randint(0, 2)

        c_answer = full_question[1]
        
        wrong_answers = full_question[2:]
        
        random.shuffle(wrong_answers)

        if self.player_asked.cpu is True: # allows clicking if player is not cpu only
            for button in self.buttons:
                button["state"] = DGG.DISABLED
                button.show()



            delay = random.uniform(self.player_asked.mintime, self.player_asked.maxtime)
            self.taskMgr.doMethodLater(delay, self.cpu_answer, "cpu_answer", extraArgs=[False], appendTask=True)

        else:
            for button in self.buttons:
                button["state"] = DGG.NORMAL
                button.show()

            
        self.buttons[c_button].setText(c_answer)  
        self.buttons[c_button]["command"] = self.correct

        for x in range(len(self.buttons)):
            if x == c_button:
                continue

            self.buttons[x]["command"] = self.incorrect
            self.buttons[x].setText(wrong_answers.pop())

        return task.done
        




    def correct(self):
        if self.round_ongoing is False:
            return
        
        if self.chainlv < 9:
            self.chainlv = self.chainlv + 1

        self.arrow.setPos((-1.1, 0, self.arrow_zpositions[self.chainlv]))

        self.correct_answers = self.correct_answers+1

        self.player_asked.correct = self.player_asked.correct+1

        self.cplayer = self.cplayer+1
        if self.cplayer > len(players)-1:
            self.cplayer = 0


        self.player_asked.r_time = self.player_asked.r_time + (globalClock.getFrameTime() - self.q_start_time)

        self.player_asked = players[self.cplayer]

        self.taskMgr.add(self.bankchance, "bankchance")



    def incorrect(self):
        if self.round_ongoing is False:
            return

        self.player_asked.incorrect = self.player_asked.incorrect+1
        
        self.chainlv = 0

        self.arrow.setPos((-1.1, 0, -0.62))

        self.incorrect_answers = self.incorrect_answers+1

        
        self.cplayer = self.cplayer+1
        if self.cplayer > len(players)-1:
            self.cplayer = 0


        self.player_asked.r_time = self.player_asked.r_time + (globalClock.getFrameTime() - self.q_start_time)

        self.player_asked = players[self.cplayer]


        self.taskMgr.add(self.ask_questions)


    def cpu_answer(self, final, task):
        # final is if it is the final or not
        
        if self.player_asked.answer_correct() is True:
            
            if final is True:
                self.fcorrect()
            else:
                self.correct()

        else:
            
            if final is True:
                self.fincorrect()
            else:
                self.incorrect()

        return task.done


    def bankchance(self, task):
        self.answering = False
        self.player_asked_text.setText("Current Player: "+str(self.player_asked))
        for button in self.buttons:
            button.hide()
            button["state"] = DGG.DISABLED

        self.bank_button.show()

        self.bank_button["state"] = DGG.DISABLED
        
        self.question_text.setText("Click to bank.")

        self.bank_button.setText("Bank?")

        if self.player_asked.cpu is False:
            self.bank_button["state"] = DGG.NORMAL

        else:
            if self.player_asked.should_bank(self.chainlv, self.chain_values, self.correct_answers, self.incorrect_answers, self.rtime-(globalClock.getFrameTime()-self.r_start_time), self.cbank):
                self.bank()

        self.taskMgr.doMethodLater(1, self.ask_questions, "ask_questions")

        return task.done



    def after_questions(self, task):
        if self.rmusic.status() == self.rmusic.PLAYING or self.target_sfx.status() == self.target_sfx.PLAYING:
            return task.cont

        global players

        if len(players) > 2:
            self.chain_img.hide()
            self.arrow.hide()
            self.banktext.hide()
            self.vloop.setLoop(True)
            self.vloop.play()

            if self.cbank == 1000:
                
                end_contents = "You have reached your 1000 target."
                
            else:
                end_contents = "Time is up, you managed to bank "+str(self.cbank)+"."

            n_contents = ("\n\n That will be added to your total, giving you a total of "+str(self.total)+"\n\n"
                          + "However, one player must be eliminated. \n\n It's time to vote off, the weakest link.")
            
            t_contents = end_contents + n_contents
            self.after_text = OnscreenText(text=t_contents, pos=(0,0.35), scale=0.1, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)

            self.s_text = OnscreenText(text="End of round "+str(self.round - self.roundmod + 1), pos=(0,0.8), scale=0.15, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)


            self.taskMgr.doMethodLater(10, self.start_voting, "start_voting")


        else:
            self.chain_img.hide()
            self.arrow.hide()
            self.banktext.hide()
            self.ffirst.play()
            self.s_text = OnscreenText(text="End of round "+str(self.round - self.roundmod + 1), pos=(0,0.8), scale=0.15, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)

            if self.cbank == 1000:
                
                end_contents = "You have reached your 1000 target."
                
            else:
                end_contents = "Time is up, you managed to bank "+str(self.cbank)+"."
                
            n_contents = ("\n\n That will be trebled, giving you a final amount of "+str(self.total)+"\n\n"
                          + "Now you'll play against each other. \n\n" + ", ".join([str(player) for player in players])+", let's play the weakest link."
                          + "\n\n" +str(self.sstrongestlink)+ ", as the strongest link last round you will go first.")
            
            t_contents = end_contents + n_contents
            self.after_text = OnscreenText(text=t_contents, pos=(0,0.45), scale=0.1, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)

            self.taskMgr.doMethodLater(self.ffirst.length(), self.start_final, "start_final")
            

            


    def start_voting(self,task):
        
        self.after_text.destroy()
        self.s_text.setText("Currently voting...")
        self.vbreak.play()
        self.vloop.stop()
        self.taskMgr.doMethodLater(1, self.restartloop, "restartloop")
        self.cplayer = 0
        self.player_asked = players[self.cplayer]
        self.vote_text = OnscreenText(text="CPU 9 is voting", pos=(0,0.6), scale=0.1, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)
        self.vote_text.hide()
        self.vote_buttons = []

        for z in range(3): #creates a grid of buttons 
            for x in range(3):
                self.vote_buttons.append(DirectButton(text="CPU 9", scale=0.1, textMayChange=1, state=DGG.DISABLED, command=self.vote_for, text_align=TextNode.ACenter, pos=(-0.3+(0.3*x), 0, 0.2-(z*0.2))))


        for button in self.vote_buttons:
            button.hide()


        self.taskMgr.add(self.vote)

        return task.done


    def restartloop(self,task):
        
        self.vloop.play()
        return task.done

    def vote(self, task):
        if self.player_asked.cpu is True: # cpus autovote
            t = self.player_asked.who_to_vote_for(self.sortedplayers)
            self.vote_for(t)
            return task.done
        
        self.vote_text.setText(str(self.player_asked)+" is voting")
        self.vote_text.show()
        for x in range(len(players)):
            thisplayer = players[x]
            if thisplayer == self.player_asked or (thisplayer == self.sstrongestlink and self.no_vote_strongest is True):
                self.vote_buttons[x]["frameColor"] = (0.5,0.5,0.5,1)
                self.vote_buttons[x]["state"] = DGG.DISABLED
            else:
                self.vote_buttons[x]["frameColor"] = (1,1,1,1)
                self.vote_buttons[x]["state"] = DGG.NORMAL
            self.vote_buttons[x].setText(str(thisplayer))
            self.vote_buttons[x]["extraArgs"] = [thisplayer]
            
##            if self.player_asked.cpu is True:
##                self.vote_buttons[x]["state"] = DGG.DISABLED
##                t = self.player_asked.who_to_vote_for(self.sortedplayers)
##                self.vote_for(t)
##                return task.done

            self.vote_buttons[x].show()

        return task.done
            


    def vote_for(self, target):
        target.votes = target.votes + 1
        self.player_asked.voted = target
        self.cplayer = self.cplayer+1
        if self.cplayer > len(players) - 1:
            #voting over
            self.taskMgr.add(self.after_vote)
            return

        self.player_asked = players[self.cplayer]
        
        self.taskMgr.add(self.vote)


    def after_vote(self, task):
        for button in self.vote_buttons:
            button.destroy()

        self.s_text.destroy()
        self.vbreak.stop()
        self.vbreak.play()
        self.vloop.stop()
        self.taskMgr.remove("restartloop")
        self.taskMgr.doMethodLater(1, self.restartloop, "restartloop")
        self.vote_text.destroy()

        self.after_vote_text = OnscreenText(text="Voting over: it's time to reveal who you think is the weakest link:\n Who everyone voted for:", pos=(0,0.85), scale=0.12, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)

        votetext = ", ".join([str(player) + ": "+str(player.voted) for player in players])

        self.vote_reveal_text = OnscreenText(text=votetext, pos=(0,0.5), scale=0.1, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0, wordwrap = 30)

        most = -1 
        self.weakest = []
        for player in players: # finding the player(s) with the most votes
            if player.votes > most:
                most = player.votes
                self.weakest = []
                self.weakest.append(player)
            elif player.votes == most:
                self.weakest.append(player)



        if len(self.weakest) == 1:
            
            self.weakest_link = self.weakest[0]
            self.outcome_text = OnscreenText(text=("The statistical weakest link is: "+str(self.sweakestlink) + "\nThe statistical strongest link is: "+str(self.sstrongestlink)
                                                   + "\n\nIt's the votes that count, and \n the player with the most votes is "+str(self.weakest_link)), pos=(0,0), scale=0.15, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)
            
            self.taskMgr.doMethodLater(18, self.vote_off, "vote_off", extraArgs=[False], appendTask=True)



        else:
            self.outcome_text = OnscreenText(text="We have a draw.\n With the votes tied, the strongest link must vote, \n that's you, "+str(self.sstrongestlink), pos=(0,0), scale=0.15, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)

            self.taskMgr.doMethodLater(13, self.vote_tiebreak, "tiebreaking")

            
        return task.done


    def vote_off(self, from_draw, task):
        global players

        players.remove(self.weakest_link)
        self.sortedplayers.remove(self.weakest_link)
        if not from_draw:
            self.vote_reveal_text.destroy()
            self.after_vote_text.destroy()
            self.outcome_text.destroy()

        else:
            for button in self.vote_buttons:
                button.destroy()
            self.vote_text.destroy()
            self.s_text.destroy()


        self.s_text = OnscreenText(text="Weakest Link Revealed:", pos=(0,0.8), scale=0.15, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)

        self.weakest_text = OnscreenText(text=str(self.weakest_link)+", You are the weakest link.\n Goodbye.", pos=(0,0), scale=0.15, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)

        self.exitsfx.play()
        self.vloop.stop()

        self.taskMgr.add(self.new_round_explain)

        return task.done

        
        


    def vote_tiebreak(self, task):

        # destroying old stuff
        self.outcome_text.destroy()
        self.vote_reveal_text.destroy()
        self.after_vote_text.destroy()

        
        if self.sstrongestlink.cpu is True: # cpu autovote
            t = self.sstrongestlink.who_to_vote_for(self.weakest)
            self.vote_for_draw(t)
            return task.done
        
        # strongest link decides when there is a tie
        self.s_text = OnscreenText(text="Strongest link deciding...", pos=(0,0.8), scale=0.15, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)
        self.vote_text = OnscreenText(text=str(self.sstrongestlink)+" is voting...", pos=(0,0.6), scale=0.1, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)
        
        self.vote_buttons = []
        for z in range(3): #creates a grid of buttons 
            for x in range(3):
                self.vote_buttons.append(DirectButton(text="CPU 9", scale=0.1, textMayChange=1, state=DGG.DISABLED, command=self.vote_for_draw, text_align=TextNode.ACenter, pos=(-0.3+(0.3*x), 0, 0.2-(z*0.2))))


        for x in self.vote_buttons:
            x.hide()

        for x in range(len(self.weakest)):
            thisplayer = self.weakest[x]
            if thisplayer == self.sstrongestlink:
                self.vote_buttons[x]["frameColor"] = (0.5,0.5,0.5,1)
                self.vote_buttons[x]["state"] = DGG.DISABLED
            else:
                self.vote_buttons[x]["state"] = DGG.NORMAL
                self.vote_buttons[x]["frameColor"] = (1,1,1,1)
                
            self.vote_buttons[x].setText(str(thisplayer))
            self.vote_buttons[x]["extraArgs"] = [thisplayer]
            
##            if self.sstrongestlink.cpu is True:
##                self.vote_buttons[x]["state"] = DGG.DISABLED
##                t = self.player_asked.who_to_vote_for(self.weakest)
##                self.vote_for_draw(t)
##                return task.done
            
            self.vote_buttons[x].show()

        return task.done


    def vote_for_draw(self, target):
        # votes off the target at once, used for a draw
        
        self.weakest_link = target
        self.taskMgr.add(self.vote_off, "vote_off", extraArgs=[True], appendTask=True)



    def new_round_explain(self, task):
        if self.exitsfx.status() == self.exitsfx.PLAYING:
            return task.cont

        self.s_text.destroy()
        self.weakest_text.destroy()
        self.starting_player = players.index(self.sortedplayers[-1])
        self.cbank = 0
        self.chainlv = 0
        self.arrow.setPos((-1.1, 0, -0.62))
        self.round = self.round+1
        self.chain_img.show()
        self.banktext.setText("Bank: 0")
        self.banktext.show()
        self.arrow.show()
        self.nexpsfx.play()
        self.taskMgr.add(self.new_stop_explain)
        if self.round == 7:
            timestr = "This round is only 90 seconds.\nWhatever you win will be trebled.\n"
        else:
            timestr = "There's 10 seconds coming off the time.\nFirst question is for 20 points\n"
        self.explaination = ("Round "+str(self.round - self.roundmod + 1) + " in the bank: "+str(self.total)+"\n" + timestr
                             +"We will start with the strongest link \n from last round, that's you "+str(self.sortedplayers[-1])+"."
                             + "\n\nLet's play, the weakest link.")
        
        self.explaintext = OnscreenText(text=self.explaination, pos=(0.15,0.35), scale=0.12, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)


        return task.done


    def new_stop_explain(self, task):
        if self.nexpsfx.status() == self.nexpsfx.PLAYING:
            return task.cont

        self.explaintext.destroy()

        self.taskMgr.add(self.start_questions, "question_task")


    def playsound(self, sound, task):

        sound.play()

        return task.done

    def start_final(self, task):
        self.cplayer = players.index(self.sstrongestlink)
        self.player_asked = players[self.cplayer]

        otherplayer = self.cplayer+1

        if otherplayer > len(players)-1:
            otherplayer = 0

        otherplayer = players[otherplayer]

        self.finalloop.play()

        #self.taskMgr.doMethodLater(self.finals.length()-0.01, self.playsound, "loop_end", extraArgs=[self.finalloop], appendTask=True)
        
        self.player_asked.final_text = OnscreenText(text=str(self.player_asked)+": "+", ".join(self.player_asked.final_list), pos=(0,-0.6), scale=0.2, fg=(0.5, 0.5, 1, 1), frame=(1,1,1,1), align=TextNode.ACenter, mayChange=1)

        otherplayer.final_text = OnscreenText(text=str(otherplayer)+": "+", ".join(self.player_asked.final_list), pos=(0,-0.9), scale=0.2, fg=(0.5, 0.5, 1, 1), frame=(1,1,1,1), align=TextNode.ACenter, mayChange=1)
        
        self.s_text.destroy()
        self.after_text.destroy()


        self.player_asked_text = OnscreenText(text="", pos=(0,0.85), scale=0.12, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1)
        self.question_text = OnscreenText(text="", pos=(0,0.55), scale=0.1, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=1, wordwrap=30)
        self.buttons = []
        self.buttons.append(DirectButton(text="Nothing to show yet, no potential answer", scale=0.1, textMayChange=1, text_align=TextNode.ACenter))
        self.buttons[0].setPos((0,0,0.15))
        self.buttons.append(DirectButton(text="Nothing to show yet, no potential answer", scale=0.1, textMayChange=1, text_align=TextNode.ACenter))
        self.buttons[1].setPos((0,0,-0.05))
        self.buttons.append(DirectButton(text="Nothing to show yet, no potential answer", scale=0.1, textMayChange=1, text_align=TextNode.ACenter))
        self.buttons[2].setPos((0,0,-0.25))


        
        self.taskMgr.add(self.ask_final)

        return task.done


    def ask_final(self, task):


        #checks to see if someone cannot win

        thisplayer = self.player_asked
        otherplayer = self.cplayer+1
        if otherplayer > len(players)-1:
            otherplayer = 0
        otherplayer = players[otherplayer]
        
        if thisplayer.final_score+(5-thisplayer.finalqans) < otherplayer.final_score:
            #otherplayer auto wins
            self.final_winner = otherplayer
            self.taskMgr.add(self.final_over)
            #print(otherplayer, "wins")
            return task.done
        
        elif otherplayer.final_score+(5-otherplayer.finalqans) < thisplayer.final_score:
            #thisplayer auto wins
            self.final_winner = thisplayer
            self.taskMgr.add(self.final_over)
            #print(thisplayer, "wins")
            return task.done

        # this also will check if anyone wins at the end since 5-finalqans will be 0
        # checks if sudden death should occur

        if thisplayer.finalqans == 5 and otherplayer.finalqans == 5 and thisplayer.final_score == otherplayer.final_score:
            self.taskMgr.add(self.sd_intro)
            return task.done
    
        if len(self.cquestions) == 0:
            self.cquestions = random.sample(self.ALL_QUESTIONS, len(self.ALL_QUESTIONS))
            
        full_question = self.cquestions.pop()

        this_question = full_question[0]

        self.player_asked_text.setText("Current Player: "+str(players[self.cplayer]))

        self.question_text.setText(this_question)
        
        c_button = random.randint(0, 2)

        c_answer = full_question[1]
        
        wrong_answers = full_question[2:]
        
        random.shuffle(wrong_answers)

        if self.player_asked.cpu is True: # allows clicking if player is not cpu only
            for button in self.buttons:
                button["state"] = DGG.DISABLED
                
            delay = random.uniform(self.player_asked.mintime, self.player_asked.maxtime)
            self.taskMgr.doMethodLater(delay, self.cpu_answer, "cpu_answer", extraArgs=[True], appendTask=True)

        else:
            for button in self.buttons:
                button["state"] = DGG.NORMAL

            
        self.buttons[c_button].setText(c_answer)  
        self.buttons[c_button]["command"] = self.fcorrect

        for x in range(len(self.buttons)):
            if x == c_button:
                continue

            self.buttons[x]["command"] = self.fincorrect
            self.buttons[x].setText(wrong_answers.pop())

        return task.done



    def fcorrect(self):
        if not self.sd:
            #print("correct", self.player_asked, self.player_asked.final_score, self.player_asked.finalqans, self.player_asked.final_list)
            self.player_asked.final_list[self.player_asked.finalqans] = "+"
            self.player_asked.final_text.setText(str(self.player_asked)+": "+", ".join(self.player_asked.final_list))
            self.player_asked.final_score = self.player_asked.final_score+1
            self.player_asked.finalqans = self.player_asked.finalqans + 1 # self.player_asked.finalqans is how many questions the player has answered in the final
            
            self.cplayer = self.cplayer+1 # next player
            if self.cplayer > len(players)-1:
                self.cplayer = 0
            self.player_asked = players[self.cplayer]

            self.taskMgr.add(self.ask_final)

        else: # if sd
            self.player_asked.final_list[0] = "+"
            self.player_asked.final_text.setText(str(self.player_asked)+": "+", ".join(self.player_asked.final_list))
            self.player_asked.sdcorrect = True

            self.cplayer = self.cplayer+1 # next player
            if self.cplayer > len(players)-1:
                self.cplayer = 0
            self.player_asked = players[self.cplayer]

            self.taskMgr.add(self.ask_sd)
            

        
    




    def fincorrect(self):
        if not self.sd:
            self.player_asked.final_list[self.player_asked.finalqans] = "-"
            self.player_asked.final_text.setText(str(self.player_asked)+": "+", ".join(self.player_asked.final_list))
            self.player_asked.finalqans = self.player_asked.finalqans + 1 # self.player_asked.finalqans is how many questions the player has answered in the final
            
            self.cplayer = self.cplayer+1
            if self.cplayer > len(players)-1:
                self.cplayer = 0
            self.player_asked = players[self.cplayer]

            self.taskMgr.add(self.ask_final)

        else: # if sd
            self.player_asked.final_list[0] = "-"
            self.player_asked.final_text.setText(str(self.player_asked)+": "+", ".join(self.player_asked.final_list))
            self.player_asked.sdcorrect = False

            self.cplayer = self.cplayer+1 # next player
            if self.cplayer > len(players)-1:
                self.cplayer = 0
            self.player_asked = players[self.cplayer]

            self.taskMgr.add(self.ask_sd)
            



    def final_over(self, task):
        # play sounds

        # destroying old things
        #self.sdsfx_s.stop()
        self.sdsfx_l.stop()
        self.finalloop.stop()
        #self.finals.stop()
        self.player_asked_text.destroy()
        self.question_text.destroy()
        for b in self.buttons:
            b.destroy()
        
        self.finishsfx.play()
        #self.taskMgr.doMethodLater(self.final_end.length()-0.903, self.playsound, "finish", extraArgs=[self.finishsfx], appendTask=True)


        self.s_text = OnscreenText(text="Strongest Link Revealed", pos=(0,0.8), scale=0.15, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)
        
        players.remove(self.final_winner) ; otherplayer = players[0] # the losing player
        
        textcontents = (str(self.final_winner)+", that means you are today's strongest link and you win "+str(self.total)+" points.\n\n"
                        + str(otherplayer)+", you leave with nothing.\n\n Join us again on the weakest link, goodbye.")
        
        self.over_text = OnscreenText(text=textcontents, pos=(0,0.45), scale=0.13, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0, wordwrap=23)

        self.taskMgr.add(self.endprogram)
        
        return task.done


    def sd_intro(self, task):
        # destroying old things
        self.sd = True
        self.player_asked_text.hide()
        self.question_text.hide()
        for b in self.buttons:
            b.hide()

        self.s_text = OnscreenText(text="Scores are drawn", pos=(0,0.8), scale=0.15, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)

        self.sdexplain_text = OnscreenText(text=("After 5 questions each your scores are the same.\n\n"+
                                                 "That means we will go to sudden death\nuntil there is a winner.\n\n"+
                                                 ", ".join([str(player) for player in players])+", let's play sudden death."), pos=(0,0.5), scale=0.15, fg=(0.5, 0.5, 1, 1), align=TextNode.ACenter, mayChange=0)

        self.taskMgr.doMethodLater(8, self.start_sd, "start_sd")

        return task.done


    def start_sd(self, task):
        for player in players:
            player.final_list = ["1"]
            player.final_text.setText(str(player)+": "+", ".join(player.final_list))

        self.s_text.destroy() # destroying sd explain stuff
        self.sdexplain_text.destroy()

        self.finalloop.stop() # stops old music
        
        self.sdsfx_l.play() # starts new music
        
        #self.taskMgr.doMethodLater(self.sdsfx_s.length()-0.01, self.playsound, "loop_end", extraArgs=[self.sdsfx_l], appendTask=True)

        self.player_asked_text.show() # shows question stuff
        self.question_text.show()
        for b in self.buttons:
            b.show()

        self.cplayer = players.index(self.sstrongestlink)
        self.player_asked = players[self.cplayer]

        self.taskMgr.add(self.ask_sd)

        return task.done



    def ask_sd(self, task): # asks questions during sudden death

        thisplayer = self.player_asked
        otherplayer = self.cplayer+1
        if otherplayer > len(players)-1:
            otherplayer = 0
        otherplayer = players[otherplayer]

        # checks if someone should win

        if thisplayer.sdcorrect is not None and otherplayer.sdcorrect is not None: # if both players have had a turn
            if thisplayer.sdcorrect is True and otherplayer.sdcorrect is False:
                self.final_winner = thisplayer
                self.taskMgr.add(self.final_over)
                #print(thisplayer, "wins")
                return task.done

            elif thisplayer.sdcorrect is False and otherplayer.sdcorrect is True:
                self.final_winner = otherplayer
                self.taskMgr.add(self.final_over)
                #print(otherplayer, "wins")
                return task.done

            else: # there is no winner (both right or both wrong)
                # resets sudden death
                for player in players:
                    player.final_list = ["1"]
                    player.final_text.setText(str(player)+": "+", ".join(player.final_list))
                    player.sdcorrect = None

                
                
        
        if len(self.cquestions) == 0:
            self.cquestions = random.sample(self.ALL_QUESTIONS, len(self.ALL_QUESTIONS))
            
        full_question = self.cquestions.pop()

        this_question = full_question[0]

        self.player_asked_text.setText("Current Player: "+str(players[self.cplayer]))

        self.question_text.setText(this_question)
        
        c_button = random.randint(0, 2)

        c_answer = full_question[1]
        
        wrong_answers = full_question[2:]
        
        random.shuffle(wrong_answers)

        if self.player_asked.cpu is True: # allows clicking if player is not cpu only
            for button in self.buttons:
                button["state"] = DGG.DISABLED
                
            delay = random.uniform(self.player_asked.mintime, self.player_asked.maxtime)
            self.taskMgr.doMethodLater(delay, self.cpu_answer, "cpu_answer", extraArgs=[True], appendTask=True)

        else:
            for button in self.buttons:
                button["state"] = DGG.NORMAL

            
        self.buttons[c_button].setText(c_answer)  
        self.buttons[c_button]["command"] = self.fcorrect

        for x in range(len(self.buttons)):
            if x == c_button:
                # stops if it is the correct button (as it has already been set)
                continue

            self.buttons[x]["command"] = self.fincorrect
            self.buttons[x].setText(wrong_answers.pop())

        return task.done



    def endprogram(self, task): # quits the program
        if self.finishsfx.status() == self.finishsfx.PLAYING:
            return task.cont


        base.destroy() # closes program
        sys.exit()

        return task.done
        

    
        
        

        
        


        
        
        

            
        
        

        
        



    

    

        
        


        
                

            
        
            







        

    





class Player:
    def __init__(self, number, cpu, cpu_diff=None):
        self.number = number
        self.cpu = cpu
        self.diff = cpu_diff
        self.r_score = 0
        self.r_time = 0
        self.correct = 0
        self.incorrect = 0
        self.r_bank = 0
        self.voted = None
        self.votes = 0
        self.final_list = ["1", "2", "3", "4", "5"]
        self.final_score = 0
        self.finalqans = 0
        self.sdcorrect = None

        if self.diff is not None:
            DIFF_MINTIMES = (7, 6, 5, 4, 2) # a tuple of minimum times for each difficulty (0-4) 5 in total
            DIFF_MAXTIMES = (15, 12, 9, 7, 5) # same for maxtimes
            DIFF_CHANCES = (0.7, 0.77, 0.85, 0.93, 0.98) # same for chances

                
            self.mintime = DIFF_MINTIMES[self.diff]
            self.maxtime = DIFF_MAXTIMES[self.diff]
            self.chance = DIFF_CHANCES[self.diff]
            self.diff_name = DIFF_NAMES[self.diff]

        else:
            self.mintime = None
            self.maxtime = None
            self.chance = None
            self.diff_name = None


    def __str__(self):
        if self.cpu is True:
            ptype = "CPU"
        else:
            ptype = "P"

        return ptype+" "+str(self.number)


    def should_bank(self, chainlv, chain_values, correct_answers, incorrect_answers, timeleft, cbank):
        if self.cpu is False: # has to be a cpu
            return None
        
        t_answers = correct_answers + incorrect_answers
        if t_answers == 0: 
            return False
        if chainlv == 0:
            return False
        elif chainlv == 9: # always banks if at max chainlv (1000)
            return True

        if chain_values[chainlv] + cbank >= 1000: # banks if doing so reaches target
            return True
        
        if timeleft < self.maxtime: # banks if not enough time to definately answer the question
            return True



        try:
            p_correct = (correct_answers/t_answers)**chainlv # an estimate for probability of the next question
            #  being answered correctly

        except ZeroDivisionError:
            return False

        p_incorrect = 1-p_correct # same except for incorrect


        #print(p_correct)

        togain = chain_values[chainlv+1] - chain_values[chainlv] # how much to gain from
        # answering it correctly

        tolose = chain_values[chainlv] # how much to lose from answering wrong

        avg_gain = togain*p_correct - tolose*p_incorrect # average gain

        #print(avg_gain)
        
        if avg_gain > 0:
            return False
        else:
            return True


    def answer_correct(self):
        chance = self.chance

        chance = int(chance*1000) # answer correctly based on chance dependant on difficulty

        rand = random.randint(0,999)
        if rand < chance:
            return True

        else:
            return False


    def who_to_vote_for(self, sortedplayers):

        #return self.debug_vote_for() #debug, forces a draw (everyone has 1 vote)

        chance = 900 # x/1000 chance to vote for weakest, else then next weakest with same chance
        # then repeat

        this_sortedplayers = list(sortedplayers)
        this_sortedplayers.pop() # no voting for strongest link
        try:
            this_sortedplayers.remove(self) # cannot vote for self
        except ValueError:
            pass

        while True:
            cindex = 0 # the current index, 0 is weakest
            rand = random.randint(0, 999)
            if rand < chance:
                return this_sortedplayers[cindex]
            
            else:
                cindex = cindex + 1
                if cindex > len(this_sortedplayers)-1:
                    return this_sortedplayers[-1]


    def debug_vote_for(self):
        # gives a draw always if everyone votes this way, testing draws
        global players

        myindex = players.index(self)

        t_index = myindex+1

        if t_index > len(players)-1:
            t_index = 0

        return players[t_index]

        
                
        

        

        

        

        

        



players = []
for number in range (1, n_cpus+1): # adding cpus
    players.append(Player(number, True, diff))

for number in range(1, (n_players-n_cpus)+1): # adding players
    players.append(Player(number, False))
    

random.shuffle(players) # shuffles the player order 








        


        
# runs the app

app = MyApp()
try:
    
    app.run()
    
finally:
    
    try:
        base.destroy() # closes program if there is an error
        
    except Exception:
        pass
