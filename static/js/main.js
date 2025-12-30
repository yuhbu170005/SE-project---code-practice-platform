/**
 * main.js - Global scripts for LiteCode
 */

console.log("LiteCode App Loaded");

// Hàm hỗ trợ chuyển Tab trong trang Problem Detail
// (Được gọi từ onclick trong HTML)
function switchTab(tabName) {
  const btnCase = document.getElementById("btn-case");
  const btnResult = document.getElementById("btn-result");
  const content = document.getElementById("tab-content");

  if (!btnCase || !btnResult || !content) return;

  if (tabName === "case1") {
    btnCase.classList.add("active");
    btnResult.classList.remove("active");
    // Nội dung mẫu (Sau này có thể lấy từ biến server)
    content.innerHTML =
      "<strong>Example Input:</strong><br>nums = [2,7,11,15], target = 9";
  } else {
    btnCase.classList.remove("active");
    btnResult.classList.add("active");
    content.innerHTML =
      '<em>No result available yet. Click "Run" to test.</em>';
  }
}

// Bạn có thể thêm các logic chung khác ở đây
// Ví dụ: Tự động tắt Alert sau 5 giây (chỉ các alert có class alert-dismissible)
document.addEventListener("DOMContentLoaded", () => {
  const alerts = document.querySelectorAll(".alert.alert-dismissible");
  if (alerts.length > 0) {
    setTimeout(() => {
      alerts.forEach((el) => (el.style.display = "none"));
    }, 5000); // 5 giây
  }
});
