//console.log(document.cookie)
///window.onload = () => adjustDialogHeight();

function toggleAdditionalButtons() {
    var additionalButtonsContainer = document.getElementById("additional-buttons-container");
    additionalButtonsContainer.style.display = (additionalButtonsContainer.style.display === "none") ? "block" : "none";
}

function redirectToPage(url) {
    window.location.href = url;
}

function submitForm() {
    var formData = new FormData();
    console.log("oooooooooooooooooooooooooooooooooooooooooooooooooooo")
    formData.append("image", document.getElementById("image").files[0], document.getElementById("image").files[0].name);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload");
    xhr.send(formData);
    xhr.onload = function () {
        if (xhr.status === 200) {
            console.log(xhr.responseText);
            ws = new WebSocket(`ws://${window.location.host}/ws/` + xhr.responseText.replace(/"/g, ''));
            ws.onmessage = checkResponce
        }
    };
}

function checkResponce(event) {
    var message = event.data
    var zip_path = message.split(';')[0]
    var mask = message.split(';')[1]
    var form = document.getElementById("save-archive");

    var img = document.createElement("img");
    img.src = mask;
    img.style.width = "99%";
    img.style.height = "99%";
    document.getElementById("history").style.display = "none";
    document.getElementById("done").style.display = "block";
    document.getElementById("save-archive").style.display = "block";
    document.getElementById("dialog-window").appendChild(img);
    document.getElementById("dialog-content").style.display = "none";
    // document.querySelector('#container').appendChild(img)

    var objects = message.split(';')[2]
    window.alert(objects)

    form.addEventListener("click", function (checker) {
        const save = document.createElement("a");
        save.href = zip_path;
        save.download = "archive.zip"

        document.body.appendChild(save)
        save.click()
        document.body.removeChild(save)
    });
}


// Определение сценариев и соответствующих сообщений
var scenarios = {
    scenario1: "Текст для сценария 1",
    scenario2: "Текст для сценария 2",
    scenario3: "Текст для сценария 3"
};

// Функция для отображения окна диалога с заданным текстом
function showTextOnClick(param) {

    var uploadPhoto = document.getElementById("upload-form")
    var dialogContent = document.getElementById("dialog-content");
    var historyForm = document.getElementById("history")
    var favouritesBtn = document.getElementById("check-favourites")
    var imageupload = document.getElementById("image-upload")
    var instructionBtn = document.getElementById("instruction")
    var historyBtn = document.getElementById("check-history")
    var back = document.getElementById("back")
    var allTimeHistory = document.getElementById("redirectHistory")

    switch (param) {

        case "wait":
            uploadPhoto.style.display = "block";

            historyForm.style.display = "none";
            favouritesBtn.style.display = "none";
            imageupload.style.display = "none";
            instructionBtn.style.display = "none";
            historyBtn.style.display = "none";
            back.style.display = "block";

            dialogContent.textContent = "Для наилучшего результата необходимо изображение в хорошем качестве с объектами на контрастном фоне, желательно в условиях дневной освещённости";
            break;
        case"image":
            uploadPhoto.style.display = "none";

            historyForm.style.display = "none";
            favouritesBtn.style.display = "none";
            imageupload.style.display = "none";
            instructionBtn.style.display = "none";
            historyBtn.style.display = "none";
            back.style.display = "block";

            var textArray = [
                ".",
                "..",
                "...",
                "....",
                "....."

            ];
            var textIndex = 0;
            var intervalId;

        function updateText() {
            dialogContent.textContent = textArray[textIndex];
            dialogContent.style.fontSize = "100px"; // Добавляем стиль шрифта
            textIndex = (textIndex + 1) % textArray.length;
        }

            intervalId = setInterval(updateText, 1000);

            //dialogContent.textContent = "Пожалуйста, подождите. Идёт обработка изображения..."
            break

        case "history":
            uploadPhoto.style.display = "none";

            historyForm.style.display = "block";
            back.style.display = "block";
            allTimeHistory.style.display = "block";

            dialogContent.textContent = "Ваша история";
            break;
        case "favourites":
            uploadPhoto.style.display = "none";

            historyForm.style.display = "none"

            dialogContent.textContent = "Ваши избранные";
            break;
        case "instructions":
            uploadPhoto.style.display = "none";

            historyForm.style.display = "none"
            back.style.display = "block"

            dialogContent.textContent = "Я обучен распознаванию порядка 25 различных объектов. Для удовлетворительного результата нужна фотография в хорошем качестве, на контрастном для объектов фоне, желательно снимать близко к объектам.";
            break;
        case "back":
            uploadPhoto.style.display = "none";

            historyForm.style.display = "none"
            back.style.display = "none";
            favouritesBtn.style.display = "block";
            imageupload.style.display = "block";
            instructionBtn.style.display = "block";
            historyBtn.style.display = "block";
            allTimeHistory.style.display = "none"

            dialogContent.innerHTML = "Привет!<br>Загрузи фотографию с объектами, которые обычно лежат на твоем столе, и узнай сколько предметов одной категории на ней присутствует";

            break;

        default:
            historyForm.style.display = "none"
            uploadPhoto.style.display = "none";
            text = "Вы сломали бота(";
    }

    console.log(text); // Вывод текста в консоль (можно заменить на другую логику)
}

// Пример вызова функции для отображения сценария 1


// Функция для показа инструкции
function showInstructions() {
    var message = "Я обучен распознаванию порядка 25 различных объектов.\n\n" +
        "Для удовлетворительного результата нужна фотография в хорошем качестве, " +
        "на контрастном для объектов фоне, желательно снимать близко к объектам.";

    window.alert(message);
}


// Функция для отображения/скрытия меню
function toggleMenu() {
    var menu = document.getElementById("menu");
    menu.style.display = (menu.style.display === "block") ? "none" : "block";
    //showDialog("scenario1");
}

// Функция для показа/сокрытия функционала по куки
// function cookieCheck() {
//     let cookies = document.cookie;
//     var menu = document.getElementById("menu");
//     if (cookies === "" || cookies.search('token=[a-zA-Z0-9]{64}') === -1) {
//         return
//     }
//     document.getElementById("menu-button").style.display = "block"
//     document.getElementById("telegram").style.display = "none"
//     document.getElementById("container").style.display = "block"
//     checkBalance()
// }

// Функция для получения куки с указанным именем
function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

// Функция для проверки и отображения баланса
async function checkBalance() {
    let cookies = getCookie("tg_uid")
    let response = await fetch(`/tglogin/${cookies}`).then(x => x.text());
    document.getElementById("balance").textContent = response;
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
    //
    // // Пример вызова функции displayImages с фиктивными данными
    // var fakeLeftImages = ["Daco_4925781.png", "Daco_4925781.png"]; // Фиктивные URL-адреса фотографий слева
    // var fakeRightImages = ["Daco_4925781.png", "Daco_4925781.png"]; // Фиктивные URL-адреса фотографий справа
    // displayImages(fakeLeftImages, fakeRightImages);
}

// // Функция для отправки формы и получения ответа с бэкенда
// function submitForm() {
//     var form = document.getElementById("upload-form");
//     var formData = new FormData(form);
//
//     // Код для отправки формы на бэкенд и получения ответа
//     // ...
//
//     // Пример вызова функции handleResponse с фиктивным ответом
//     var fakeResponse = {hasArchive: true}; // Фиктивный ответ с бэкенда
//     handleResponse(fakeResponse);
// }

// Инициализация формы
var form = document.getElementById("upload-form");
form.addEventListener("submit", function (event) {
    event.preventDefault();
    submitForm();
});


