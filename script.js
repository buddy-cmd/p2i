document.getElementById("generateForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData();
  formData.append("prompt", document.getElementById("prompt").value);
  formData.append("model", document.getElementById("model").value);
  formData.append("aspect_ratio", document.getElementById("aspect").value);
  formData.append("outputs", document.getElementById("outputs").value);

  const imageFile = document.getElementById("imageUpload").files[0];
  if (imageFile) formData.append("image", imageFile);

  const response = await fetch("http://localhost:8000/generate", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  const results = document.getElementById("results");
  results.innerHTML = "";

  if (data.images) {
    data.images.forEach((imgUrl) => {
      const img = document.createElement("img");
      img.src = imgUrl;
      img.alt = "Generated Image";
      img.style.width = "100%";
      results.appendChild(img);
    });
  } else {
    results.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
  }
});
