if (item.outputs && item.outputs.length > 0) {
  const afterImg = document.createElement("img");
  afterImg.src = item.outputs[0];
  afterImg.alt = "Transformed image";
  afterImg.style.maxWidth = "100%";
  afterImg.onload = () => console.log("✅ Image loaded:", afterImg.src);
  afterCell.appendChild(afterImg);

  // Add download button
  const downloadBtn = document.createElement("a");
  downloadBtn.href = item.outputs[0];
  downloadBtn.download = `transformed_${i + 1}.png`;
  downloadBtn.textContent = "Download";
  downloadBtn.className = "download-btn";
  afterCell.appendChild(downloadBtn);
} else {
  const errorMsg = document.createElement("p");
  errorMsg.textContent = "⚠️ No image returned from backend";
  errorMsg.style.color = "#f66";
  afterCell.appendChild(errorMsg);
}
