console.log("ready")
const URI = "http://127.0.0.1:8000/llm"

document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.querySelector(".dream-textarea");
    console.log("auto resize on")
    if (textarea) {
        textarea.style.overflow = "hidden";                         // Prevent scrollbar
        textarea.style.height = "auto";                             // Reset height initially
        textarea.style.height = textarea.scrollHeight + "px";       // Set height dynamically

        textarea.addEventListener("input", function () {
            this.style.height = "auto";                             // Reset height
            this.style.height = this.scrollHeight + "px";           // Set new height
        });
    }
});

document.querySelector(".dream-form").addEventListener("submit", async (event) => {
    event.preventDefault()

    let dreamInput = document.querySelector(".dream-textarea");
    if (!dreamInput) {
        console.error("Empty form submitted. KYS")
        return
    }

    let formData = new FormData();
    formData.append("dream", dreamInput.value);

    try {
        const response = await fetch(URI, {
            method: "POST",
            body: formData,
        });
        console.log("data exchanged")
        let jsonResponse = await response.json();

        console.log(jsonResponse);
        // document.querySelector(".response").textContent = `lmao: ${jsonResponse}`
    } catch (e) {
        console.error(e);
    }

})