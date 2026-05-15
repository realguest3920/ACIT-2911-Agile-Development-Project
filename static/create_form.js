document.getElementById("imageUpload").addEventListener("change", function () {
  const fileName = this.files[0]?.name;
  const label = document.getElementById("fileName");
  if (fileName) {
    label.textContent = fileName;
    label.style.display = "block";
  }
});
