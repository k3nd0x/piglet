function generateRandomHexColor() {
    const randomInt = Math.floor(Math.random() * 16777215);
    const hexColor = '#' + randomInt.toString(16).padStart(6, '0');
    return hexColor;
}
function setRandomColor() {
    const randomColor = generateRandomHexColor();
    const colorPickerElement = document.getElementById('colorpicker');
    if (colorPickerElement) {
        colorPickerElement.value = randomColor;
    }
}
window.addEventListener('load', setRandomColor);