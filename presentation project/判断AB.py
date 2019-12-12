"""
Compare the number with the original random number and return the number of A abd B.
"""
import random


def generate_number():
    integer = [0,1,2,3,4,5,6,7,8,9]
    guess = []
    for i in range(4):
        j = len(integer)
        a = random.randint(0,j-1)
        guess.append(integer[a])
        integer.pop(a)
    return guess

def compare_number(client_number):
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
            
def main():
    while True:
        num = input('Please enter a number: ')
        if len(num) == 4:
            a,b = compare_number(num)
            if a == 4:
                print('You are right.')
                break
            else:
                print("There are", a ,"A and",b,"B.")
        else:
            print('You make a mistake. Try it again. ')
            
if __name__ == "__main__":
    N = generate_number()
    main()
