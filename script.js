const form = document.getElementById("gen-form");
const statusEl = document.getElementById("status");
const multiComparison = document.getElementById("multi-comparison");
const uploadBox = document.getElementById("upload-box");
const imagesInput = document.getElementById("images");
const promptEl = document.getElementById("prompt");
const charCount = document.getElementById("char-count");
const fileList = document.getElementById("file-list");

// Clickable upload zone
uploadBox.addEventListener("click", () => imagesInput.click());

// Show selected file names
imagesInput.addEventListener("change", () => {
  const files = Array.from(imagesInput.files || []);
  if (!files.length) {
    fileList.textContent = "";
    return;
  }
  const names = files.slice(0, 5).map(f => f.name).join(", ");
  fileList.textContent = `Selected: ${names}`;
});

// Live character count
promptEl.addEventListener("input", () => {
  charCount.textContent = `${promptEl.value.length}/1000`;
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  statusEl.textContent = "Generating... please wait";
  multiComparison.innerHTML = "";

  const formData = new FormData(form);

  // Optional: map aspect ratio to size hint (UI only)
  const aspect = document.getElementById("aspect").value;
  const sizeSelect = document.getElementById("size").value;
  // You could adjust size based on aspect if you add more sizes.

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
        title.textContent = `Image ${i + 1}`;
        block.appendChild(title);

        const row = document.createElement("div");
        row.className = "comp-row";

        // Before cell
        const beforeCell = document.createElement("div");
        beforeCell.className = "comp-cell";
        const beforeLabel = document.createElement("h4");
        beforeLabel.textContent = "Before";
        beforeCell.appendChild(beforeLabel);

        if (item.original && imagesInput.files[i]) {
          const beforeImg = document.createElement("img");
          beforeImg.src = URL.createObjectURL(imagesInput.files[i]);
          beforeImg.onload = () => beforeImg.classList.add("loaded");
          beforeCell.appendChild(beforeImg);
        }

        // After cell
        const afterCell = document.createElement("div");
        afterCell.className = "comp-cell";
        const afterLabel = document.createElement("h4");
        afterLabel.textContent = "After";
        afterCell.appendChild(afterLabel);

        if (item.outputs) {
          // Show the first output by default
          const afterImg = document.createElement("img");
          afterImg.src = item.outputs[0];
          afterImg.onload = () => afterImg.classList.add("loaded");
          afterCell.appendChild(afterImg);

          const downloadBtn = document.createElement("a");
          downloadBtn.href = item.outputs[0];
          downloadBtn.download = `transformed_${i + 1}.png`;
          downloadBtn.textContent = "Download";
          downloadBtn.className = "download-btn";
          afterCell.appendChild(downloadBtn);
        }

        row.appendChild(beforeCell);
        row.appendChild(afterCell);
        block.appendChild(row);
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
