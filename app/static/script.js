//console.log(document.cookie)
window.onload = () => cookieCheck()

function toggleAdditionalButtons() {
    var additionalButtonsContainer = document.getElementById("additional-buttons-container");
    additionalButtonsContainer.style.display = (additionalButtonsContainer.style.display === "none") ? "block" : "none";
}

// Функция для отображения/скрытия меню
function toggleMenu() {
    var menu = document.getElementById("menu");
    menu.style.display = (menu.style.display === "block") ? "none" : "block";
}

// Функция для показа/сокрытия функционала по куки
function cookieCheck() {
    let cookies = document.cookie;
    var menu = document.getElementById("menu");
    if (cookies === "" || cookies.search('token=[a-zA-Z0-9]{64}') === -1) {
        return
    }
    document.getElementById("menu-button").style.display = "block"
    document.getElementById("telegram").style.display = "none"
    document.getElementById("container").style.display = "block"
    checkBalance()
}

// Функция для получения куки с указанным именем
function getCookie(name) {
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

// Функция для проверки и отображения баланса
async function checkBalance(){
    let cookies = getCookie("tg_uid")
    let response = await fetch(`/tglogin/${cookies}`).then(x=>x.text());
    document.getElementById("balance").textContent=response;
}

// Функция для пополнения токенов
function reloadTokensVeronika() {
    // Переадресация на профиль в Telegram
    window.location.href = " https://t.me/+79243652878";
    toggleAdditionalButtons()
}
function reloadTokensDmitry() {
    // Переадресация на профиль в Telegram
    window.location.href = "https://t.me/Jiraffeck";
    toggleAdditionalButtons()
}
function reloadTokensIlya() {
    // Переадресация на профиль в Telegram
    window.location.href = "https://t.me/nortrow";
    toggleAdditionalButtons()
}
function reloadTokensDanil() {
    // Переадресация на профиль в Telegram
    window.location.href = "https://t.me/IvanGroznyiA";
    toggleAdditionalButtons()
}


// Функция для выхода из аккаунта
function logout() {
    const cookies = document.cookie.split(";");

    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i];
        const eqPos = cookie.indexOf("=");
        const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
        location.reload()
    }
}

// Функция для отображения/скрытия кнопки "Скачать архив"
function toggleDownloadButton(show) {
    var downloadButton = document.getElementById("download-link");
    if (show) {
        downloadButton.style.display = "block";
    } else {
        downloadButton.style.display = "none";
    }
}

// Функция для отображения фотографий слева и справа
function displayImages(leftImages, rightImages) {
    var leftContainer = document.getElementById("left-images-container");
    var rightContainer = document.getElementById("right-images-container");

    // Очистка контейнеров перед отображением новых фотографий
    leftContainer.innerHTML = "";
    rightContainer.innerHTML = "";

    // Отображение фотографий слева
    leftImages.forEach(function (imageUrl) {
        var imageContainer = document.createElement("div");
        imageContainer.className = "image-container";
        var image = document.createElement("img");
        image.src = imageUrl;
        imageContainer.appendChild(image);
        leftContainer.appendChild(imageContainer);
    });

    // Отображение фотографий справа
    rightImages.forEach(function (imageUrl) {
        var imageContainer = document.createElement("div");
        imageContainer.className = "image-container";
        var image = document.createElement("img");
        image.src = imageUrl;
        imageContainer.appendChild(image);
        rightContainer.appendChild(imageContainer);
    });
}

// Функция для обработки ответа с бэкенда
function handleResponse(response) {
    // Проверка условия для отображения кнопки "Скачать архив"
    var showDownloadButton = response.hasArchive; // Ваше условие для отображения кнопки "Скачать архив" на основе полученного ответа
    toggleDownloadButton(showDownloadButton);

    // Пример вызова функции displayImages с фиктивными данными
    var fakeLeftImages = ["Daco_4925781.png", "Daco_4925781.png"]; // Фиктивные URL-адреса фотографий слева
    var fakeRightImages = ["Daco_4925781.png", "Daco_4925781.png"]; // Фиктивные URL-адреса фотографий справа
    displayImages(fakeLeftImages, fakeRightImages);
}

// Функция для отправки формы и получения ответа с бэкенда
function submitForm() {
    var form = document.getElementById("upload-form");
    var formData = new FormData(form);

    // Код для отправки формы на бэкенд и получения ответа
    // ...

    // Пример вызова функции handleResponse с фиктивным ответом
    var fakeResponse = {hasArchive: true}; // Фиктивный ответ с бэкенда
    handleResponse(fakeResponse);
}

// Инициализация формы
var form = document.getElementById("upload-form");
form.addEventListener("submit", function (event) {
    event.preventDefault();
    submitForm();
});


