from tkinter import *


misspList = []
misspFile = "data/missp.txt"
with open(misspFile) as file:
    #missp = file.read().splitlines()
    missp = file.read().split('$')
for i in range(len(missp)):
    misspList.append(missp[i].split())


word = ""


def key_down(e):
    #global key
    #key = e.keycode
    #print(str(e).find('state'))
    spacebar = False
    global word

    if str(e).find('char') > -1:
        idx = str(e).find('char') + 6
        chr = str(e)[idx]
        word += chr
        print(chr, end="")

        # space bar = end of the word -> do correction & prediction
        if chr == " ":
            spacebar = True
            correctStr = correction(word[:-1])
            print(correctStr, end=" ")
            word = ""
        else:
            spacebar = False

    #print(word, end="")

# Spell Checker
def correction(text):
    correctionList = []
    print()
    for i in range(len(misspList)):
        #print(misspList[i])
        #print(text in misspList[i])
        if text in misspList[i] and text != misspList[i][0]:
            correctionList.append(misspList[i][0])
    if correctionList:
        print('Did you mean:', correctionList)
        #print(correctionList)
        num = int(input("Type # to change or -1 to finish correction: "))
        if num == -1:
            return text
        else:
            return correctionList[num - 1]
    return text

main = Tk()
main.title("Key Press")
main.bind("<KeyPress>", key_down)

main.mainloop()