const username = document.getElementById("username");
const password = document.getElementById("password");
const button = document.getElementById("login_button");

button.addEventListener("click", async () => {
    if (!username.value.trim() || !password.value.trim()) {
        showErrorText("Please fill in all fields");
        return;
    }

    const body = JSON.stringify({
        username: username.value,
        password: password.value
    });

    try {
        const response = await fetch(dataContainer.dataset.urlLoginUser, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: body
        });

        if (response.ok) {
            redirectTo(dataContainer.dataset.urlHomePage);
        } else {
            const result = await response.json();
            showErrorText(result.detail);
        }
    } catch (error) {
        showErrorText("An error occurred. Please try again.");
    }
});