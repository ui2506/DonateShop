let textIndex = 0;
    
const messages = [
    "А ты не бойся!",
    "Пора победить страхи! >:3",
    "Ну я серьезно... Мы получаем только ваш SteamId",
    "ДА ЖМИ УЖЕ НА КНОПКУ!",
    "Я обиделся. >:("
];

function changeText() {
    const link = document.getElementById('sceary');
    if (textIndex < messages.length) {
        link.innerHTML = messages[textIndex];
        textIndex++;
    }
}

window.onload = () => {
    const link = document.getElementById('sceary');
    link.addEventListener('click', changeText);
};