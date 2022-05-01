var misspList = [];
var changeWord = [];

function getMissp() {
    var raw = new XMLHttpRequest();
    raw.open("GET", "../data/missp.txt", true);
    raw.onreadystatechange = function() {
        if (raw.readyState === 4) {
            var allText = raw.responseText.split('$');
            for (var i = 0; i < allText.length; i++) {
                recommend = allText[i].split('\n').slice(0, -1);
                misspList.push(recommend);
            }
        }
    }
    raw.send();
}

async function checkFile() {
    var input = document.getElementById('inputText').files[0];
    var text = await input.text();

    var original = document.getElementById('original');
    original.textContent = text;
    original.style.border = "1px solid black";

    checkError(text);
    //console.log(text);
}

function checkError(text) {
    var recommend = document.getElementById('recommend');

    var originalWords = text.split(' ');
    var changedWords = originalWords; // words without '(', ')', '.', '!', ...

    for (var i = 0; i < originalWords.length; i++) {
        word = originalWords[i];
        wordLen = word.length;

        if (word[0] === '(') {
            word = word.slice(1, -1);
        }
        else if (word[wordLen - 1] === '.' || word[wordLen - 1] === ',' || word[wordLen - 1] === '!') {
            word = word.slice(0, -1);
        }
        changedWords[i] = word;
    }

    for (var i = 0; i < changedWords.length; i++) {
        var checkWord = changedWords[i];
        var recommendList = [];
        for (var j = 0; j < misspList.length; j++) {
            if (misspList[j].includes(checkWord) && misspList[j][0] !== checkWord) {
                recommendList.push(misspList[j][0])
            }
        }

        // elliminate redundancies
        recommendList = new Set(recommendList);
        recommendList = [...recommendList];

        if (recommendList.length > 0) {
            // redundancy check
            var redundance = false;
            changeWord.forEach((e) => {
                if (checkWord === e) {
                    redundance = true;
                    return false;
                }
            });
            if (redundance !== true) {
                var addHTML = "<b>" + checkWord + "</b> - " + recommendList + '<br>';
                recommend.innerHTML += addHTML;
                changeWord.push(checkWord);
            }
        }
    }
    console.log(changeWord);
    highlightWord(changeWord, text);
}

function highlightWord(wordList, original) {
    var originalHTML = document.getElementById('original');
    var finalHTML = '';

    var original = original.split(" ");

    original.forEach((e) => {
        var word = e;
        var wordLen = word.length;
        var caseNum;

        if (word[wordLen - 1] === '.') {
            word = word.slice(0, -1);
            caseNum = 1;
        }
        else if (word[wordLen - 1] === ',') {
            word = word.slice(0, -1);
            caseNum = 2;
        }
        else if (word[wordLen - 1] === '!') {
            word = word.slice(0, -1);
            caseNum = 3;
        }

        var addHTML;

        // if the word should be highlighted
        if (wordList.includes(word)) {
            if (caseNum === 1) {
                addHTML = " <a id='highlight'>" + word + "</a>. ";
            }
            else if (caseNum === 2) {
                addHTML = " <a id='highlight'>" + word + "</a>, ";
            }
            else if (caseNum === 3) {
                addHTML = " <a id='highlight'>" + word + "</a>! ";
            }
            else {
                addHTML = " <a id='highlight'>" + word + "</a> ";
            }
        } else {
            if (caseNum === 1) {
                addHTML = " " + word + ". ";
            }
            else if (caseNum === 2) {
                addHTML = " " + word + ", ";
            }
            else if (caseNum === 3) {
                addHTML = " " + word + "! ";
            }
            else {
                addHTML = " " + word + " ";
            }
        }
        finalHTML += addHTML;
    })

    originalHTML.innerHTML = finalHTML;
}

getMissp();