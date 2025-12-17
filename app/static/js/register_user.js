const username = document.getElementById("username");
const email = document.getElementById("email");
const password = document.getElementById("password");
const confirm_password = document.getElementById("confirm_password");
const button = document.getElementById("signup_button");

button.addEventListener("click", async () => {
    if (!username.value.trim() || !email.value.trim() ||
        !password.value.trim() || !confirm_password.value.trim()) {
        showErrorText("Please fill in all fields");
        return;
    }

    const body = JSON.stringify({
        username: username.value,
        email: email.value,
        password: password.value,
        confirm_password: confirm_password.value
    });

    try {
        const response = await fetch(dataContainer.dataset.urlRegisterUser, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: body
        });

        if (response.ok) {
            await fetch(dataContainer.dataset.urlLoginUser, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: body
            });
            redirectTo(dataContainer.dataset.urlHomePage);
        } else {
            const result = await response.json();
            showErrorText(result.detail);
        }
    } catch (error) {
        showErrorText("An error occurred. Please try again.");
    }
});