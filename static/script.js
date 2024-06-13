function initBar(id, maxValue) {
    document.getElementById(id).style.width = "100%";
    document.getElementById(id + "Title").innerText = maxValue;
}

function updateBar(id, maxValue, operator) {
    const fraction = (100 / maxValue);
    const barItself = document.getElementById(id);
    const numerator = document.getElementById(id + "Title");

    if (operator === "sub") {
        // subtract to numerator
        const number = numerator.innerText;

        // subtract to bar
        const barWidth = barItself.style.width;
        const result = (parseInt(barWidth) - fraction)

        if (result >= 0) {
            numerator.innerText = (parseInt(number) - 1);
            barItself.style.width = (result + "%");
        }

    }
    else {
        // add to numerator
        const number = numerator.innerText;

        // add to bar
        const barWidth = barItself.style.width;
        const result = (parseInt(barWidth) + fraction)

        if (result <= 100) {
            numerator.innerText = (parseInt(number) + 1);
            barItself.style.width = (result + "%");
        }
    }

    const colorValue = parseInt(barItself.style.width);

    if (colorValue > 50) {
        barItself.style.backgroundColor = '#4caf50'; // Green
    } else if (colorValue > 25) {
        barItself.style.backgroundColor = '#ffeb3b'; // Yellow
    } else {
        barItself.style.backgroundColor = '#f44336'; // Red
    }

}

function openDice(ID, insideID) {
    const div = document.getElementById(ID);
    const inside = document.getElementById(insideID);

    if (div.className === "floatDice0") {
        div.className = "floatDice1";
        inside.style.display = "block";

    }
    else {
        div.className = "floatDice0";
        inside.style.display = "none";
    }
}

function getRandomIntInclusive(min, max) {
    const minCeiled = Math.ceil(min);
    const maxFloored = Math.floor(max);
    return Math.floor(Math.random() * (maxFloored - minCeiled + 1) + minCeiled); // The maximum is inclusive and the minimum is inclusive
}


function d20(dID, s, r, max) {
    const dice = document.getElementById(dID);
    const sum = document.getElementById(s);
    const result = document.getElementById(r);

    dice.innerText = getRandomIntInclusive(1, max);
}


function updater(dice, sum, result) {
    const diceInput = document.getElementById(dice);
    const diceSum = document.getElementById(sum);
    const diceResult = document.getElementById(result);

    diceResult.value = (parseInt(diceInput.innerText) + parseInt(diceSum.value))
}





