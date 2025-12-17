const visibilityButton = document.getElementById("visibility_button");
if (visibilityButton) {
    visibilityButton.addEventListener("click", async () => {
        await fetch(dataContainer.dataset.urlChangeImageVisibility, {method: "PATCH"});
        refreshPage();
    });
}
const deleteButton = document.getElementById("delete_button");
if (deleteButton) {
    deleteButton.addEventListener("click", async () => {
        if (confirm("Are you sure you want to delete this image?")) {
            await fetch(dataContainer.dataset.urlDeleteImage, {method: "DELETE"});
            redirectTo(dataContainer.dataset.urlGetMePage);
        }
    });
}

const deleteLikeButton = document.getElementById("delete_like_button");
if (deleteLikeButton) {
    deleteLikeButton.addEventListener("click", async () => {
        const response = await fetch(dataContainer.dataset.urlDeleteLike, {method: "DELETE"});
        if (response.ok)
            refreshPage();
    });
}
const placeLikeButton = document.getElementById("place_like_button");
if (placeLikeButton) {
    placeLikeButton.addEventListener("click", async () => {
        if (dataContainer.dataset.loggedIn) {
            const body = JSON.stringify({
                to_image_id: dataContainer.dataset.imageId
            });
            const response = await fetch(dataContainer.dataset.urlPlaceLike, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: body
            });
            if (response.ok)
                refreshPage();
        } else {
            redirectTo(dataContainer.dataset.urlLoginUserPage);
        }
    });
}