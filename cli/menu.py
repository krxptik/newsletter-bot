from datetime import datetime
import os
import math
import time

STATE_LIST = 1
STATE_ARTICLE_MENU = 2
STATE_DETAILS = 3
STATE_SELECTED_MENU = 4

class Article:
    def __init__(self, title):
        self.title = title
        self.pub_date = datetime.now()
        self.link = "https://example.com"
        self.tags = ["P2SA"]
        self.summary = "This is a summary."

def clear_terminal():
    # Windows (cmd or PowerShell) uses 'cls', Unix/Linux/macOS uses 'clear'
    os.system('cls' if os.name == 'nt' else 'clear')

def truncate(text, width):
    return text[:width-1] + "…" if len(text) > width else text

def display_list(articles, selected, page, max_page):
    clear_terminal()
    print("Available articles:".ljust(30) + "Selected")
    print(("="*25).ljust(30) + ("="*20))

    for i in range((page-1)*5, page*5):
        article_text, selected_text = "", ""
        if i < len(articles):
            article_title = articles[i].title
            article_text = (
                f"({i+1})".ljust(5) +
                truncate(article_title, 20).ljust(25)
            )
        if i < len(selected):
            selected_title = selected[i].title
            selected_text = (
                f"({chr(ord('A') + i)})".ljust(5) +
                truncate(selected_title, 20)
            )
        print(article_text + selected_text)
    
    print(f"Page {page} of {max_page}\n")
    
def display_list_options():
    text = (
        "Options:\n"
        "* Enter an article no.\n"
        "* Enter 'next' or 'prev' to navigate the list\n"
        "* Enter 'done' to create the newsletter\n"
        "> "
    )
    return input(text)

def display_article_menu(title):
    text = (
        f"You have selected {title}. Would you like to:\n"
        "(1) View the article's details (tags, summary, and link)\n"
        "(2) Put the article in the newsletter\n"
        "(3) Go back\n"
        "> "
    )

    response = input(text)
    if not response.isdigit():
        return False
    
    return int(response)

def display_selected_menu(title):
    text = (
        f"You have selected {title}. Would you like to:\n"
        "(1) View the article's details (tags, summary, and link)\n"
        "(2) Remove the article from the newsletter\n"
        "(3) Go back\n"
        "> "
    )

    response = input(text)
    if not response.isdigit():
        return False
    
    return int(response)

def display_details(article):
    pub_date = article.pub_date.strftime('%d/%m/%Y') if article.pub_date else 'None'
    print(
        f"Title: {article.title}\n"
        f"Date: {pub_date}\n"
        f"Link: {article.link}\n"
        f"Tags: {article.tags}\n"
        f"Summary: {article.summary}\n"
    )
    input("Enter any key to go back.\n> ")
    return 

def display_confirm(selected):
    clear_terminal()
    print("You have selected:")
    for i in range(len(selected)):
        text = (
            f"({i+1})".ljust(5) +
            f"{selected[i].title}"
        )
        print(text)
    return input("\nProceed to generate the newsletter? (Y/N)\n> ")



def menu(articles):
    state = STATE_LIST
    page = 1
    max_page = math.ceil(len(articles)/5)
    selection = None
    article_menu = True
    selected = []

    while True:
        if state == STATE_LIST:
            display_list(articles, selected, page, max_page)
            option = display_list_options()
            
            if option == 'next':
                if page+1 <= max_page:
                    page += 1
            elif option == 'prev':
                if page > 1:
                    page -= 1
            elif option == 'done':
                if not selected:
                    clear_terminal()
                    print('You have not selected any articles.')
                    print('Returning to main menu in 3 seconds...')
                    time.sleep(3)
                    continue
                option = display_confirm(selected)
                if option.upper() == 'Y':
                    clear_terminal()
                    return selected
                else:
                    continue
            elif option.isdigit():
                state = STATE_ARTICLE_MENU
                selection = int(option)-1
            elif option.isalpha() and len(option)==1:
                selection = ord(option)-ord('A')
                if selection > len(selected):
                    continue
                state = STATE_SELECTED_MENU
            else:
                continue

        elif state == STATE_ARTICLE_MENU:
            clear_terminal()
            article = articles[selection]
            option = display_article_menu(article.title)
            
            if option == False:
                continue

            if option == 1:
                state = STATE_DETAILS
                article_menu = True
            elif option == 2:
                state = STATE_LIST
                selected.append(articles.pop(selection))
            elif option == 3:
                state = STATE_LIST

        elif state == STATE_SELECTED_MENU:
            clear_terminal()
            article = selected[selection]
            option = display_selected_menu(article.title)

            if option == False:
                continue

            if option == 1:
                state = STATE_DETAILS
                article_menu = False
            elif option == 2:
                state = STATE_LIST
                articles.append(selected.pop(selection))
            elif option == 3:
                state = STATE_LIST

        elif state == STATE_DETAILS:
            clear_terminal()
            article = articles[selection] if article_menu else selected[selection]
            display_details(article)
            state = STATE_ARTICLE_MENU if article_menu else STATE_SELECTED_MENU
            
# state 1: articles list + options
# state 2: article menu
# state 3: article details

if __name__ == '__main__':
    # Mock articles for testing
    articles = [Article(f"Article {i}") for i in range(1, 20)]
    selected = menu(articles)

    print("Selected articles:")
    if selected:
        for a in selected:
            print(a.title)
