document.getElementById("listingForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const form = e.target;
  const actionUrl = form.dataset.url;
  const redirectUrl = form.dataset.redirect;
  const responseMsg = document.getElementById("responseMessage");

  // Use FormData to handle both text and files
  const formData = new FormData();

  formData.append("title", document.getElementById("listingTitle").value);
  formData.append("creator", document.getElementById("listingCreator").value);
  formData.append("price", document.getElementById("listingPrice").value);
  formData.append("condition", document.getElementById("condition").value);
  formData.append("description", document.getElementById("description").value);

  const fileInput = document.getElementById("imageUpload");
  if (fileInput.files[0]) {
    formData.append("imageUpload", fileInput.files[0]);
  }

  try {
    const response = await fetch(actionUrl, {
      method: "POST",
      // IMPORTANT: Do NOT set Content-Type header when sending FormData.
      // The browser will set it automatically with the correct boundary.
      body: formData,
    });

    if (response.ok) {
      window.location.href = redirectUrl;
    } else {
      const result = await response.json();
      responseMsg.style.color = "red";
      responseMsg.innerText = "Error: " + (result.error || "Unknown error");
    }
  } catch (error) {
    console.error("Fetch error:", error);
    responseMsg.innerText = "Connection error. Please try again.";
  }
});
