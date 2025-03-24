console.log("ready")
const URI = "http://127.0.0.1:8000/llm"

let dreamInput = document.querySelector(".dream-textarea");
let responseDiv = document.querySelector(".response");
let loadingArea = document.querySelector(".loader");
let submitButton = document.querySelector(".submit-button")

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


function toTitleCase(str) {
    return str.replace(/_/g, ' ')                               // Convert snake_case to spaces
              .replace(/([a-z])([A-Z])/g, '$1 $2')              // Convert camelCase to spaces
              .replace(/\b\w/g, char => char.toUpperCase());    // Capitalize first letter of each word
}

function generateHTML(data, container) {
    Object.entries(data).forEach(([key, value]) => {

        let heading = document.createElement("div");

        if (key.toLowerCase() == "text" || key.toLowerCase() == "title") {
            let gap = document.createElement("div");
            gap.classList.add("gap");
        } else {
            heading.textContent = toTitleCase(key);
        }
        heading.classList.add("response-heading");
        container.appendChild(heading);

        if (typeof value === "object" && !Array.isArray(value)) {
            // `value` is another object, and not an array

            // heading.classList.add("heading-sub");
            let subContainer = document.createElement("div");
            subContainer.classList.add("response-heading-sub");
            generateHTML(value, subContainer);
            container.appendChild(subContainer);

        } else if (Array.isArray(value)) {
            let listContainer = document.createElement("div");
            value.forEach((item, index) => {
                let listItem = document.createElement("div");
                generateHTML(item, listItem);
                listContainer.appendChild(listItem);
            });
            container.appendChild(listContainer);

        } else {
            let paragraph = document.createElement("p");
            paragraph.textContent = value;
            container.appendChild(paragraph);
        }
    });
}

document.querySelector(".dream-form").addEventListener("submit", async (event) => {
    event.preventDefault()

    if (!dreamInput.value) {
        console.error("Empty form submitted. KYS");
        return;
    }

    responseDiv.innerHTML = "";
    console.log("nuked");
    loadingArea.classList.remove("invisible");

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

        let archetype = jsonResponse.archetype;
        let descriptiveContent = jsonResponse.descriptive_content;

        generateHTML(descriptiveContent, responseDiv);
        loadingArea.classList.add("invisible")

    } catch (e) {
        console.error(e);
    }
})

submitButton.addEventListener("mouseover", () => {
    if (!dreamInput.value) {
        submitButton.style.cursor = "not-allowed";
    } else {
        submitButton.style.cursor = "pointer";
    }
});
