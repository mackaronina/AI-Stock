const logoutButton = document.getElementById("logout_button");
logoutButton.addEventListener("click", async () => {
    await fetch(dataContainer.dataset.urlLogoutUser, {method: "POST"});
    redirectTo(dataContainer.dataset.urlHomePage);
});

const deleteButton = document.getElementById("delete_button");
deleteButton.addEventListener("click", async () => {
    if (confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
        await fetch(dataContainer.dataset.urlDeleteUser, {method: "DELETE"});
        redirectTo(dataContainer.dataset.urlHomePage);
    }
});