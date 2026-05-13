document.getElementById("listingForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  // Grab the URL from the form's data attribute (we will set this in Step 2)
  const form = e.target;
  const actionUrl = form.dataset.url;
  const redirectUrl = form.dataset.redirect;

  const payload = {
    title: document.getElementById("title").value,
    creator: document.getElementById("creator").value,
    price: parseFloat(document.getElementById("price").value),
    condition: document.getElementById("condition").value,
    description: document.getElementById("description").value,
  };

  try {
    const response = await fetch(actionUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      window.location.href = redirectUrl;
    } else {
      const result = await response.json();
      document.getElementById("responseMessage").innerText =
        "Error: " + (result.error || "Unknown error");
    }
  } catch (error) {
    console.error("Fetch error:", error);
    document.getElementById("responseMessage").innerText = "Connection error.";
  }
});
