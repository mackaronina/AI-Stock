function redirectTo(url) {
    window.location.href = url;
}

function showErrorText(text) {
    const errorAlert = document.getElementById("error_alert");
    errorAlert.innerText = text;
    errorAlert.classList.remove("d-none");
    setTimeout(() => errorAlert.classList.add("d-none"), 5000);
}

function refreshPage() {
    window.location.reload();
}

const dataContainer = document.getElementById("data-container");

if (!dataContainer.dataset.loggedIn) {
    fetch(dataContainer.dataset.urlRefreshTokens, {
        method: "POST",
    }).then(response => {
        if (response.ok) {
            refreshPage();
        }
    });
}