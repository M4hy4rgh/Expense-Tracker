"""
This is a money management application that allows users to track their income and expenses.
The application will allow users to add new transactions and incomes, view their total expenses,
view their spending by category, and view their total profit.

The application will store the data in a SQLite database. The database will have three tables:
1) categories: This table will store the list of categories that the user can select from when adding a new transaction.
2) transactions: This table will store the list of transactions that the user has added.
3) incomes: This table will store the list of incomes that the user has added.

The Application is developed by:

    1) Mahyar Ghasemi Khah

"""
import re
import sqlite3
from prettytable import PrettyTable
from datetime import datetime


class MoneyManager:
    def __init__(self):
        self.conn = sqlite3.connect('money.db')
        self.c = self.conn.cursor()
        self.create_tables()
        self.run()

    def create_tables(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS categories(name text PRIMARY KEY)''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS transactions
                          (id integer PRIMARY KEY, 
                          category text, 
                          amount real, 
                          description text,
                          "date" DATE)''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS incomes
                          (id integer PRIMARY KEY,
                           amount real,
                           description text,
                           "date" DATE)''')

        default_categories = ['Rent', 'Food', 'Clothing', 'Utilities', 'Entertainment', 'Grocery Shopping',
                              'Tuition Fee']
        for category in default_categories:
            self.c.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))

        self.conn.commit()

    def new_transaction(self):
        # Display the list of categories and allow the user to select a category or add a new one
        self.c.execute('SELECT name FROM categories')
        categories = [row[0] for row in self.c.fetchall()]
        categories.append('Add a new category')
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")

        userInputCategory = input("Please choose an option: ")
        while not userInputCategory.isdigit() or int(userInputCategory) not in range(1, len(categories) + 1):
            print("You have entered an invalid input!")
            userInputCategory = input("Please choose a valid option: ")
        category = categories[int(userInputCategory) - 1]

        if category == 'Add a new category':
            new_category = input("Please enter the name of the new category: ")
            self.c.execute('INSERT INTO categories (name) VALUES (?)', (new_category,))
            self.conn.commit()
            print(f"New category '{new_category}' has been added!")
            category = new_category

        # Get the transaction amount, description, and date from the user
        amount = input("Please enter the amount of the transaction:")
        while not amount.replace('.', '', 1).isdigit():
            amount = input("Invalid amount! Please enter a valid amount: ")
        amount = float(amount)

        description = input("Description (optional): ")
        while not re.match(r'^[A-Za-z\s]*$', description):
            description = input("Invalid description! Please enter a valid description: ")

        date_str = input("Date (DD-MM-YYYY): ")
        while True:
            try:
                date = datetime.strptime(date_str, '%d-%m-%Y').date().strftime('%d-%m-%Y')
                break
            except ValueError:
                date_str = input("Invalid date format! Please enter date in the format of 'DD-MM-YYYY': ")

        # Add the new transaction to the selected category's list of transactions
        self.c.execute('INSERT INTO transactions (category, amount, description, date) VALUES (?, ?, ?, ?)',
                       (category, amount, description, date))
        self.conn.commit()

        print(f"The transaction has been added to {category}!")

        # Ask the user if they want to go back to the main menu
        user_input = input("Press 'y' to go back to the main menu and 'n' to add another transaction: ")
        while user_input.lower() not in ['y', 'n']:
            user_input = input("Invalid input. Enter a valid Input: ")

        if user_input.lower() == 'y':
            self.run()
        else:
            self.new_transaction()

    def new_income(self):
        incomeAmt = input("Please enter the amount of your income: ")
        while not incomeAmt.replace('.', '', 1).isdigit():
            incomeAmt = input("Invalid amount! Please enter a valid amount: ")
        incomeAmt = float(incomeAmt)

        income_description = input("Description (optional): ")
        while not re.match(r'^[A-Za-z\s]*$', income_description):
            income_description = input("Invalid description! Please enter a valid description: ")

        income_date = input("Please enter the date of your income (DD-MM-YYYY): ")
        while True:
            try:
                income_date = datetime.strptime(income_date, '%d-%m-%Y').date().strftime('%d-%m-%Y')
                break
            except ValueError:
                income_date = input("Invalid date format! Please enter date in the format of 'DD-MM-YYYY': ")

        self.c.execute('INSERT INTO incomes (amount, description, date) VALUES (?, ?, ?)',
                       (incomeAmt, income_description, income_date,))
        self.conn.commit()

        print(f"The income of ${incomeAmt:,.2f} has been added!")

        user_input = input("Press 'y' to go back to the main menu and 'n' to add another transaction: ")
        while user_input.lower() not in ['y', 'n']:
            user_input = input("Invalid input. Enter a valid Input: ")

        if user_input.lower() == 'y':
            self.run()
        else:
            self.new_income()

    def view_total_expenses(self):
        self.c.execute('SELECT category, amount, description, "date"  FROM transactions')
        result = self.c.fetchall()
        total_expenses = 0
        table = PrettyTable(['Category', 'Amount', 'Description', 'Date'])
        for row in result:
            category, amount, description, date = row
            table.add_row([category, f"${amount:,.2f}", description, date])
            total_expenses += amount

        table.add_row(['--------------', '--------------', '--------------', '--------------'])
        table.add_row(['Total', f"${total_expenses:,.2f}", '', ''])
        print('+-------------------------------------------------------------------+')
        print("|{:^67}|".format("Transaction"))
        print(table)

        user_input = input("Press 'y' to go back to the main menu: ")
        while user_input.lower() != 'y':
            user_input = input("Invalid input. Enter a valid Input: ")

        self.run()

    def view_spending_by_category(self):
        self.c.execute('SELECT category, SUM(amount) FROM transactions GROUP BY category')
        result = self.c.fetchall()
        table = PrettyTable(['Category', 'Total Spending'])
        for row in result:
            category, category_spending = row
            table.add_row([category, f"${category_spending:,.2f}"])
        # print('+--------------------------------+')
        # print("|{:^32}|".format("Transaction"))
        # make the commented code above dynamic with the width of the table


        print(table)


        user_input = input("Press 'y' to go back to the main menu: ")
        while user_input.lower() != 'y':
            user_input = input("Invalid input. Enter a valid Input: ")

        self.run()

    def view_income(self):
        self.c.execute('SELECT SUM(amount) FROM incomes')
        result = self.c.fetchone()
        total_income = result[0] if result[0] else 0

        self.c.execute('SELECT id, amount, description, "date" FROM incomes')
        results = self.c.fetchall()
        table = PrettyTable(['ID', 'Amount', 'Description', 'Date'])
        for row in results:
            id, amount, description, date = row
            table.add_row([id, f"${amount:,.2f}", description, date])
        table.add_row(['--------------', '--------------', '--------------', '--------------'])
        table.add_row(['Total', f"${total_income:,.2f}", '', ''])
        print('+---------------------------------------------------------------------+')
        print("|{:^69}|".format("INCOME"))
        print(table)

        user_input = input("Press 'y' to go back to the main menu: ")
        while user_input.lower() != 'y':
            user_input = input("Invalid input. Enter a valid Input: ")

        self.run()

    def view_total_profit(self):
        self.c.execute('SELECT SUM(amount) FROM incomes')
        result = self.c.fetchone()
        total_income = result[0] if result[0] else 0

        self.c.execute('SELECT SUM(amount) FROM transactions')
        result = self.c.fetchone()
        total_expenses = result[0] if result[0] else 0

        total_profit = total_income - total_expenses

        debt = 0.0
        if total_profit < 0:
            debt = total_profit * -1
            total_profit = 0

        table = PrettyTable(['Total Income', 'Total Expenses', 'Total Profit', 'Total Debt'])
        table.add_row([f"${total_income:,.2f}", f"${total_expenses:,.2f}", f"${total_profit:,.2f}", f"${debt:,.2f}"])
        print('+-----------------------------------------------------------+')
        print("|{:^59}|".format("PROFIT"))
        print(table)

        user_input = input("Press 'y' to go back to the main menu: ")
        while user_input.lower() != 'y':
            user_input = input("Invalid input. Enter a valid Input: ")

        self.run()

    def run(self):
        menu_options = [
            "Add A New Transaction",
            "Add A New Income",
            "View Total Expenses",
            "View Expenses By Category",
            "View Total Income",
            "View Total Profit / Debt",
            "Exit"
        ]

        print((' ' * 13) + ('* ' * 26))
        print(' ' * 17 + 'Hello, welcome to your personal Money Manager')
        print(' ' * 21 + 'Choose an option from the menu below')
        print((' ' * 13) + ('* ' * 26))
        print((' ' * 13) + '*    ' + '-' * 40 + '     *')
        print((' ' * 13) + '*    |' + ' ' * 18 + 'MENU' + ' ' * 16 + '|     *')
        print((' ' * 13) + '*    ' + '-' * 40 + '     *')

        for i, option in enumerate(menu_options, start=1):
            print(f'{" " * 12} *    |  {i}) {option: <33}|     *')

        print((' ' * 13) + '*    ' + '-' * 40 + '     *')
        print((' ' * 13) + ('* ' * 26))

        userInput = input("\nPlease choose an option: ")
        while not userInput.isdigit() or int(userInput) not in range(1, 8):
            print("You have entered an invalid input!")
            userInput = input("Please choose a valid option: ")
        option = int(userInput)

        match option:
            case 1:
                self.new_transaction()
            case 2:
                self.new_income()
            case 3:
                self.view_total_expenses()
            case 4:
                self.view_spending_by_category()
            case 5:
                self.view_income()
            case 6:
                self.view_total_profit()
            case 7:
                print("\nThank you for using Money Manager. Goodbye!")
                exit()


if __name__ == '__main__':
    MoneyManager()
