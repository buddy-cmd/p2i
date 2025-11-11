const form = document.getElementById("gen-form");
const statusEl = document.getElementById("status");
const multiComparison = document.getElementById("multi-comparison");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  statusEl.textContent = "Generating... please wait";
  multiComparison.innerHTML = "";

  const formData = new FormData(form);

  try {
    const res = await fetch("https://p2i.onrender.com/generate", {
      method: "POST",
      body: formData
    });
    const data = await res.json();

    if (data.results) {
      data.results.forEach((item, i) => {
        const block = document.createElement("div");
        block.className = "comp-block";

        const title = document.createElement("h3");
        title.textContent = `Image ${i+1}`;
        block.appendChild(title);

        // Before image
        if (item.original) {
          const before = document.createElement("img");
          before.src = URL.createObjectURL(form.images.files[i]);
          before.onload = () => before.classList.add("loaded");
          block.appendChild(before);
        }

        // After image + download button
        if (item.outputs) {
          const after = document.createElement("img");
          after.src = item.outputs[0];
          after.onload = () => after.classList.add("loaded");
          block.appendChild(after);

          const downloadBtn = document.createElement("a");
          downloadBtn.href = item.outputs[0];
          downloadBtn.download = `transformed_${i+1}.png`;
          downloadBtn.textContent = "Download";
          downloadBtn.className = "download-btn";
          block.appendChild(downloadBtn);
        }

        multiComparison.appendChild(block);
      });
      statusEl.textContent = "Transformation complete!";
    } else {
      statusEl.textContent = data.error || "No images returned";
    }
  } catch (err) {
    statusEl.textContent = "Error: " + err.message;
  }
});
