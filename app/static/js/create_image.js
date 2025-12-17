const prompt = document.getElementById("prompt");
const button = document.getElementById("create_button");

function disableButton() {
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';
    button.disabled = true;
}

function enableButton() {
    button.innerHTML = '<i class="bi bi-stars"></i> Generate Image';
    button.disabled = false;
}

button.addEventListener("click", async () => {
    if (!prompt.value.trim()) {
        showErrorText("Please enter a prompt");
        return;
    }

    disableButton();
    const body = JSON.stringify({
        prompt: prompt.value
    });

    try {
        const response = await fetch(dataContainer.dataset.urlCreateImage, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: body
        });

        if (response.ok) {
            const result = await response.json();
            redirectTo(result.image_url);
        } else {
            const result = await response.json();
            showErrorText(result.detail);
            enableButton();
        }
    } catch (error) {
        showErrorText("An error occurred. Please try again.");
        enableButton();
    }
});