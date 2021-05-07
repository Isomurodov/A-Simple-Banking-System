import random
import sqlite3

conn = sqlite3.connect('card.s3db')
c = conn.cursor()
c.execute(''' CREATE TABLE IF NOT EXISTS card
                (id INTEGER,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0)''')
conn.commit()


def num_generator():
    global card_num
    global nums
    for _ in range(9):
        value = random.randint(0, 9)
        card_num += str(value)
    luhn(card_num)
    if card_num not in nums:
        nums.append(card_num)
        return card_num
    else:
        return num_generator()


def pin_generator():
    global pin
    global pins
    for _ in range(4):
        value = random.randint(0, 9)
        pin += str(value)
    if pin not in pins:
        pins.append(pin)
        return pin
    else:
        return pin_generator()


def luhn(x):
    global card_num
    ans = []
    for i in range(15):
        if i % 2 == 0:
            if int(x[i]) * 2 > 9:
                ans.append(int(x[i]) * 2 - 9)
            else:
                ans.append(int(x[i]) * 2)
        else:
            ans.append(int(x[i]))
    for i in range(10):
        if (sum(ans) + i) % 10 == 0:
            if x == card_num:
                x += str(i)
                card_num = x
                return x
            else:
                if str(i) == x[-1]:
                    return True
                else: return False


menu = """1. Create an account
2. Log into account
0. Exit"""

menu_log = """1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit"""

create_message = """Your card has been created
Your card number:
{num}
Your card PIN:
{pinn}"""

cards = {}
pins = []
nums = []
main = True
card_num = '400000'
pin = ''

# Start
while True:
    print('\n')

    # main menu
    if main:
        print(menu)
        a = int(input())
        # create account
        if a == 1:
            id_num = len(c.fetchall()) + 1
            values = (id_num, num_generator(), pin_generator())
            cards[values[1]] = {'pin': values[2], 'balance': 0}
            c.execute("INSERT INTO card (id, number, pin) VALUES (?, ?, ?)", values)
            conn.commit()
            print(create_message.format(num=card_num, pinn=pin))
        # log in
        elif a == 2:
            enter_num = input('Enter your card number:\n')
            enter_pin = input('Enter your PIN:\n')
            if (enter_num in cards) and (enter_pin == cards[str(enter_num)]['pin']):
                main = False
                print('You have successfully logged in!\n')
                continue
            else:
                print('Wrong card number or PIN!\n')
        # exit
        else:
            print('Bye!')
            break

            # menu after login
    else:
        print(menu_log, '\n')
        a = int(input())
        if a == 1:
            print('Balance: ', cards[str(enter_num)]['balance'], '\n')
        elif a == 2:
            income = int(input('Enter income:\n'))
            cards[enter_num]['balance'] += income
            tupl_income = (income, enter_num)
            c.execute("UPDATE card SET balance = balance + ? WHERE number = ? ", tupl_income)
            conn.commit()
            print('Income was added!\n')
        elif a == 3:
            print('Enter card number:')
            rcvr = input()
            if luhn(rcvr):
                if rcvr in cards:
                    if rcvr == enter_num: print('You can\'t transfer money to the same account!')
                    print('Enter how much money you want to transfer:')
                    amount = int(input())
                    if amount <= cards[enter_num]['balance']:
                        cards[enter_num]['balance'] -= amount
                        cards[rcvr]['balance'] += amount
                        tupl_sender = (amount, enter_num)
                        tupl_rcvr = (amount, rcvr)
                        c.execute("UPDATE card SET balance = balance - ? WHERE number = ? ", tupl_sender)
                        conn.commit()
                        c.execute("UPDATE card SET balance = balance + ? WHERE number = ? ", tupl_rcvr)
                        conn.commit()
                        print('Success!\n')
                    else:
                        print('Not enough money!\n')
                else:
                    print('Such a card does not exist.\n')
            else:
                print('Probably you made a mistake in the card number. Please try again!\n')
        elif a == 4:
            tupl = (enter_num,)
            c.execute("DELETE FROM card WHERE number=?", tupl)
            conn.commit()
            cards.pop(enter_num)
            print('The account has been closed!\n')
            main = True
        elif a == 5:
            print('You have successfully logged out!\n')
            main = True
        else:
            print('Bye!')
            break
    card_num = '400000'
    pin = ''
conn.close()
