"""
Compare the number with the original random number and return the number of A abd B.
"""

"""
Rules:
Instructions: 
This is a two-player chat system-based guessing number game. 
In this game, you and your opponent will take turns to enter numbers (no repetitions like 8848) 
and try to figure out a random 4-digit number based on the clues that the server gives. 
The first player who gets the correct number wins the game. 

The clues: 
The clues will be strings which are in the format of “? A, ? B”, (? is an integer between 0 and 4) which indicates how well your guessing is. 

One “B” indicates that you have one number correct but its position is wrong; 
one “A” indicates that you have both the value of the number and the position of the number correct. 

For example, if the correct number is 1234 and your guess is 4321, 
you have four numbers correct but none of the positions are correct, 
so the server will return “0A, 4B”. 
Else if your guess is 1243, you have four numbers with right values but only two numbers with the right position, now the server will return “2A, 2B”. 

From these clues you will be able to figure out what is the number as the game continues. 

Now you can type in your answers and begin the game.

"""
import random


def redundant(num):
    for i in range(len(num)):
        if num[i] in num[i + 1:]:
            return True
    return False

class Game:
    def __init__(self):
        self.integer = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    def generate_number(self):
        guess = []
        for i in range(4):
            j = len(self.integer)
            a = random.randint(0, j - 1)
            guess.append(self.integer[a])
            self.integer.pop(a)
        return guess


    def compare_number(self, client_number,N):
        n = []
        for p in range(len(str(client_number))):
            n.append(str(client_number)[p])
        sum_a = 0
        sum_ab = 0
        for i in range(4):
            if int(n[i]) == N[i]:
                sum_a += 1
        for j in n:
            if int(j) in N:
                sum_ab += 1
        sum_b = sum_ab - sum_a
        return sum_a, sum_b

    def redundant(self, num):
        for i in range(len(num)):
            if num[i] in num[i+1:]:
                return True
        return False


    def play(self):
        N = self.generate_number()
        while True:
            num = input('Please enter a number: ')
            if num.isdigit():
                if len(num) == 4:
                    if self.redundant(num):
                        print('You make a mistake. Try it again. ')
                    else:
                        a, b = self.compare_number(num, N)
                        if a == 4:
                            print('You are right.')
                            break
                        else:
                            print("There are", a, "A and", b, "B.")
                else:
                    print('You make a mistake. Try it again. ')
            else:
                print('You make a mistake. Try it again. ')

def main():
    game = Game()
    game.play()
if __name__ == "__main__":
    main()
