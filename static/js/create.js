// create.js - Script for create problem page

let testCases = [];

function addTestCase() {
  const id = Date.now();
  testCases.push({
    id,
    input: "",
    expected_output: "",
    is_sample: false,
    is_hidden: false,
  });
  renderTestCases();
}

function removeTestCase(id) {
  testCases = testCases.filter((tc) => tc.id !== id);
  renderTestCases();
}

function updateTestCase(id, field, value) {
  const tc = testCases.find((tc) => tc.id === id);
  if (tc) tc[field] = value;
}

function renderTestCases() {
  const container = document.getElementById("test-cases-container");
  container.innerHTML = testCases
    .map(
      (tc, index) => `
    <div style="border: 1px solid #ccc; border-radius: 6px; padding: 15px; margin-bottom: 10px; background: white;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <strong>Test Case ${index + 1}</strong>
        <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeTestCase(${
          tc.id
        })">
          <i class="fas fa-trash"></i>
        </button>
      </div>
      <div style="margin-bottom: 10px;">
        <label style="font-size: 13px; font-weight: 600; color: #555;">Input:</label>
        <textarea class="form-control" rows="2" placeholder="Ex: [2,7,11,15]\\n9" onchange="updateTestCase(${
          tc.id
        }, 'input', this.value)" style="font-family: monospace; font-size: 12px;">${
        tc.input
      }</textarea>
      </div>
      <div style="margin-bottom: 10px;">
        <label style="font-size: 13px; font-weight: 600; color: #555;">Expected Output:</label>
        <textarea class="form-control" rows="2" placeholder="Ex: [0,1]" onchange="updateTestCase(${
          tc.id
        }, 'expected_output', this.value)" style="font-family: monospace; font-size: 12px;">${
        tc.expected_output
      }</textarea>
      </div>
      <div style="display: flex; gap: 15px;">
        <label style="font-size: 13px;">
          <input type="checkbox" ${
            tc.is_sample ? "checked" : ""
          } onchange="updateTestCase(${tc.id}, 'is_sample', this.checked)"> 
          <span style="margin-left: 5px;">Is Sample (show in description)</span>
        </label>
        <label style="font-size: 13px;">
          <input type="checkbox" ${
            tc.is_hidden ? "checked" : ""
          } onchange="updateTestCase(${tc.id}, 'is_hidden', this.checked)"> 
          <span style="margin-left: 5px;">Is Hidden (for grading only)</span>
        </label>
      </div>
    </div>
  `
    )
    .join("");
}

function toggleJsonImport() {
  const section = document.getElementById("json-import-section");
  section.style.display = section.style.display === "none" ? "block" : "none";
  if (section.style.display === "block") {
    document.getElementById("json-import-textarea").focus();
  }
}

function importTestCasesFromJson() {
  const textarea = document.getElementById("json-import-textarea");
  const messageDiv = document.getElementById("import-message");
  const jsonText = textarea.value.trim();

  messageDiv.innerHTML = "";

  if (!jsonText) {
    messageDiv.innerHTML =
      '<span style="color: #dc3545;">❌ Please paste JSON array</span>';
    return;
  }

  try {
    const importedCases = JSON.parse(jsonText);

    if (!Array.isArray(importedCases)) {
      messageDiv.innerHTML =
        '<span style="color: #dc3545;">❌ JSON must be an array</span>';
      return;
    }

    if (importedCases.length === 0) {
      messageDiv.innerHTML =
        '<span style="color: #dc3545;">❌ Array is empty</span>';
      return;
    }

    let validCount = 0;
    importedCases.forEach((tc) => {
      if (tc.input !== undefined && tc.expected_output !== undefined) {
        testCases.push({
          id: Date.now() + Math.random(),
          input: tc.input || "",
          expected_output: tc.expected_output || "",
          is_sample: tc.is_sample || false,
          is_hidden: tc.is_hidden !== false, // default to true
        });
        validCount++;
      }
    });

    if (validCount === 0) {
      messageDiv.innerHTML =
        '<span style="color: #dc3545;">❌ No valid test cases found</span>';
      return;
    }

    renderTestCases();
    textarea.value = "";
    toggleJsonImport();
    messageDiv.innerHTML = `<span style="color: #28a745;">✓ Imported ${validCount} test case${
      validCount > 1 ? "s" : ""
    }</span>`;
    setTimeout(() => {
      messageDiv.innerHTML = "";
    }, 3000);
  } catch (e) {
    messageDiv.innerHTML = `<span style="color: #dc3545;">❌ Invalid JSON: ${e.message}</span>`;
  }
}

// Validation function
function validateForm() {
  const title = document.getElementById("title").value.trim();
  const slug = document.getElementById("slug").value.trim();
  const description = document.getElementById("description").value.trim();
  const difficulty = document.getElementById("difficulty").value;

  // Title validation (3+ chars)
  if (!title) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Please enter a problem title",
    });
    return false;
  }

  if (title.length < 3) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Title must be at least 3 characters",
    });
    return false;
  }

  if (title.length > 200) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Title must not exceed 200 characters",
    });
    return false;
  }

  // Slug validation (3+ chars, lowercase/numbers/hyphens only)
  if (!slug) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Please enter a problem slug",
    });
    return false;
  }

  if (slug.length < 3) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Slug must be at least 3 characters",
    });
    return false;
  }

  if (slug.length > 100) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Slug must not exceed 100 characters",
    });
    return false;
  }

  // Slug format validation (only lowercase, numbers, and hyphens)
  if (!/^[a-z0-9-]+$/.test(slug)) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Slug can only contain lowercase letters, numbers, and hyphens",
    });
    return false;
  }

  if (slug.startsWith("-") || slug.endsWith("-")) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Slug cannot start or end with a hyphen",
    });
    return false;
  }

  // Description validation (10+ chars)
  if (!description) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Please enter a problem description",
    });
    return false;
  }

  if (description.length < 10) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Description must be at least 10 characters",
    });
    return false;
  }

  if (description.length > 50000) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Description is too long (max 50,000 characters)",
    });
    return false;
  }

  // Difficulty validation
  if (!difficulty) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Please select a difficulty level",
    });
    return false;
  }

  // Test cases validation
  if (testCases.length === 0) {
    Swal.fire({
      icon: "warning",
      title: "Validation Error",
      text: "Please add at least one test case",
    });
    return false;
  }

  // Check if all test cases have input and output
  for (let i = 0; i < testCases.length; i++) {
    if (!testCases[i].input.trim()) {
      Swal.fire({
        icon: "warning",
        title: "Validation Error",
        text: `Test case ${i + 1}: Input is required`,
      });
      return false;
    }
    if (!testCases[i].expected_output.trim()) {
      Swal.fire({
        icon: "warning",
        title: "Validation Error",
        text: `Test case ${i + 1}: Expected output is required`,
      });
      return false;
    }
  }

  return true;
}

// Initialize
document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      // Validate form
      if (!validateForm()) {
        return;
      }

      // Prepare test cases
      const cleanTestCases = testCases.map((tc) => ({
        input: tc.input,
        expected_output: tc.expected_output,
        is_sample: tc.is_sample,
        is_hidden: tc.is_hidden,
      }));
      document.getElementById("test_cases_json").value =
        JSON.stringify(cleanTestCases);

      // Show loading state
      Swal.fire({
        title: "Creating Problem",
        text: "Please wait...",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      try {
        const formData = new FormData(this);
        const response = await fetch("/problems/create", {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        });

        const data = await response.json();

        if (response.ok && data.success) {
          Swal.fire({
            icon: "success",
            title: "Success",
            text: data.message || "Problem created successfully!",
            showConfirmButton: false,
            timer: 1500,
          }).then(() => {
            window.location.href = "/problems";
          });
        } else {
          Swal.fire({
            icon: "error",
            title: "Validation Error",
            html: `<div style="text-align: left; white-space: pre-wrap; word-wrap: break-word;">${
              data.message ||
              "Failed to create problem. Please check your inputs."
            }</div>`,
            confirmButtonText: "OK",
          });
        }
      } catch (error) {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: `An error occurred: ${error.message}`,
        });
      }
    });
  }

  addTestCase();
});

