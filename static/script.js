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





