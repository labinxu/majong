import sys, time

cards = [1,2,3,4,5,6,7,8,9]
def play_card():
    print(' '.join([str(i) for i in cards]))
    r = input('action: ')
    cards.remove(int(r))
    print(' '.join([str(i) for i in cards]))

play_card()
