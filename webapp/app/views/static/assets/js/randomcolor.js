function generateRandomHexColor() {
    // Erzeugt eine zufällige Zahl zwischen 0 und 16777215 (dezimal für 0xFFFFFF)
    const randomInt = Math.floor(Math.random() * 16777215);
    // Wandelt die Zahl in eine Hexadezimaldarstellung um und fügt nötigenfalls führende Nullen hinzu
    const hexColor = '#' + randomInt.toString(16).padStart(6, '0');
    return hexColor;
}
// Funktion, die beim Laden der Seite ausgeführt wird
function setRandomColor() {
    // Generiert eine zufällige Hex-Farbe
    const randomColor = generateRandomHexColor();
    // Findet das Element mit der ID 'colorpicker'
    const colorPickerElement = document.getElementById('colorpicker');
    // Setzt den Wert des Elements auf die generierte Farbe
    if (colorPickerElement) {
        colorPickerElement.value = randomColor;
    }
}

// Fügt einen Event-Listener hinzu, der die setRandomColor-Funktion beim Laden der Seite ausführt
window.addEventListener('load', setRandomColor);