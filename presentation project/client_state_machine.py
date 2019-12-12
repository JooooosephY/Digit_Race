"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
import game as gm

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.play_game = False
        self.accept = False
        self.answering = False
        self.respond = False
        self.answer = False

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    # print(poem)
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                # If you are in the game.
                if self.play_game is True:
                    # If it's your turn to answer
                    if self.answer is True:
                        # If your answer are all digits
                        if my_msg.isdigit():
                            # if the length of your answer is 4.
                            if len(my_msg) == 4:
                                if gm.redundant(my_msg):
                                    self.out_msg += 'You make a mistake. Try it again.'
                                # If there is no repetition
                                else:
                                    mysend(self.s, json.dumps({"action": "exchange", "from": "[" + self.me + "]", "message": my_msg}))
                                    mysend(self.s, json.dumps({"action": "guessing", "from": "[" + self.me + "]", "message": my_msg}))
                                    self.answer = False
                            else:
                                self.out_msg += 'You make a mistake. Try it again.'
                        else:
                            self.out_msg += 'You make a mistake. Try it again.'
                    elif my_msg == "quit":
                        mysend(self.s,json.dumps({"action": "guessing", "from": "[" + self.me + "]", "message": my_msg}))
                        self.answer = False
                        self.play_game = False
                else:
                    # respond to the invitation
                    if self.answering is True and self.respond is False:
                        if my_msg == 'Yes' or my_msg == 'yes' or my_msg == 'YES':
                            self.accept = True
                            self.respond = True
                            self.answering = False
                            self.play_game = True
                            self.answer = False
                            mysend(self.s, json.dumps({"action":"accept_invitation", "from":"[" + self.me + "]", "message":'Yes'}))
                            self.out_msg += "Let's start!\n"
                            self.out_msg += '\n'
                            self.out_msg += "Instructions: \n This is a two-player chat system-based guessing number game. \nIn this game, you and your opponent will take turns and try to figure out a random 4-digit number based on the clues that the server gives (no repetitions like 8848). \nThe first player who gets the correct number wins the game. \n\nThe clues: \nThe clues will be strings which are in the format of “? A, ? B”, (? is an integer between 0 and 4) which indicates how well your guessing is. \n\nOne “B” indicates that you have one number correct but its position is wrong; \none “A” indicates that you have both the value of the number and the position of the number correct.\n \nFor example, if the correct number is 1234 and your guess is 4321, \nyou have four numbers correct but none of the positions are correct,\n so the server will return “0A, 4B”. \nElse if your guess is 1243, \nyou have four numbers with right values but only two numbers with the right position, now the server will return “2A, 2B”. \n\nFrom these clues you will be able to figure out what is the number as the game continues. \n\nNow you can type in your answers and begin the game. \n\n"
                            self.out_msg += "You will start until your opponent have started. \n"
                        elif my_msg == 'No' or my_msg == 'no' or my_msg == 'NO':
                            self.accept = False
                            self.respond = True
                            self.answer = False
                            mysend(self.s, json.dumps({"action":"accept_invitation", "from":"[" + self.me + "]", "message":'No'}))
                        else:
                            self.out_msg += 'You should respond the invitation.'
                    # 正常聊天
                    else:
                        mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                        if my_msg == 'bye':
                            self.disconnect()
                            self.state = S_LOGGEDIN
                            self.peer = ''

                        # 想玩游戏
                        elif my_msg == 'game':
                            mysend(self.s, json.dumps({"action":"game", "from":"[" + self.me + "]", "message":my_msg}))
                            rst = json.loads(myrecv(self.s))["results"]
                            if rst == "incapable":
                                self.out_msg += 'The number of the group members is larger than 2.\nYou cannot send the invitation'
                            else:
                                self.out_msg += "You've sent the invitation."




            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                #peer 发来游戏请求
                elif peer_msg["action"] == "game":
                    self.out_msg += "Your friend wants to invite you to play the game.\n"
                    self.out_msg += "Do you want to accept the invitation?\n"
                    self.out_msg += "Please answer Yes or No"
                    self.answering = True
                    self.respond = False
                # peer 是否接受请求
                elif peer_msg['action'] == 'accept_invitation':
                    if peer_msg['accept'] == 'No':
                        self.answer = False
                        self.out_msg += 'Your friend reject your invitation'
                    elif peer_msg['accept'] == 'Yes':
                        self.play_game = True
                        self.answer = True
                        self.out_msg += "Let's start!\n\n"
                        self.out_msg += "Instructions: \n This is a two-player chat system-based guessing number game. \nIn this game, you and your opponent will take turns and try to figure out a random \n 4-digit number based on the clues that the server gives (no repetitions like 8848). \nThe first player who gets the correct number wins the game. \n\nThe clues: \nThe clues will be strings which are in the format of “? A, ? B”, \n (? is an integer between 0 and 4) which indicates how well your guessing is. \n\nOne “B” indicates that you have one number correct but its position is wrong; \none “A” indicates that you have both the value of the number and the position of the number correct.\n \nFor example, if the correct number is 1234 and your guess is 4321, \nyou have four numbers correct but none of the positions are correct,\n so the server will return “0A, 4B”. \nElse if your guess is 1243, \nyou have four numbers with right values but only two numbers with the right position, now the server will return “2A, 2B”. \n\nFrom these clues you will be able to figure out what is the number as the game continues. \n\nNow you can type in your answers and begin the game. \n\n"
                        self.out_msg += "Player [" + self.me + "] you can start the game first.\n"
                # 猜数字阶段
                elif peer_msg['action'] == 'guessing':
                    if peer_msg['condition'] == 'continue':
                        self.out_msg += peer_msg['results']
                        if peer_msg['from'] != "[" + str(self.me) + "]":
                            self.answer = True
                    # End the game
                    elif peer_msg['condition'] == 'end':
                        self.play_game = False
                        self.answer = False
                        self.out_msg += peer_msg['results']
                else:
                    self.out_msg += peer_msg["from"] + peer_msg["message"]


            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
