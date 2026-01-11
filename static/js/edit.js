// edit.js - Script for edit problem page

let testCases = [];

function getJsonEditor() {
  return document.getElementById('test-cases-json-editor');
}

// Load test cases into JSON editor
function loadTestCasesIntoEditor() {
  const jsonEditor = getJsonEditor();
  if (!jsonEditor) return;
  const cleanTestCases = testCases.map(tc => ({
    input: tc.input || '',
    expected_output: tc.expected_output || '',
    is_sample: tc.is_sample || false,
    is_hidden: tc.is_hidden || false
  }));
  jsonEditor.value = JSON.stringify(cleanTestCases, null, 2);
}

// Format JSON
function formatJsonTestCases() {
  const jsonEditor = getJsonEditor();
  if (!jsonEditor) return;
  const messageDiv = document.getElementById('json-validation-message');
  const jsonText = jsonEditor.value.trim();
  
  messageDiv.innerHTML = '';

  if (!jsonText) {
    messageDiv.innerHTML = '<span style="color: #dc3545;">✗ Empty JSON</span>';
    return;
  }

  try {
    const parsed = JSON.parse(jsonText);
    jsonEditor.value = JSON.stringify(parsed, null, 2);
    messageDiv.innerHTML = '<span style="color: #28a745;">✓ JSON formatted successfully</span>';
    setTimeout(() => messageDiv.innerHTML = '', 2000);
  } catch (e) {
    messageDiv.innerHTML = `<span style="color: #dc3545;">✗ Invalid JSON: ${e.message}</span>`;
  }
}

// Validate JSON
function validateJsonTestCases() {
  const jsonEditor = getJsonEditor();
  if (!jsonEditor) return;
  const messageDiv = document.getElementById('json-validation-message');
  const jsonText = jsonEditor.value.trim();
  
  messageDiv.innerHTML = '';

  if (!jsonText) {
    messageDiv.innerHTML = '<span style="color: #dc3545;">✗ Empty JSON</span>';
    return;
  }

  try {
    const parsed = JSON.parse(jsonText);

    if (!Array.isArray(parsed)) {
      messageDiv.innerHTML = '<span style="color: #dc3545;">✗ Must be a JSON array</span>';
      return;
    }

    if (parsed.length === 0) {
      messageDiv.innerHTML = '<span style="color: #dc3545;">✗ Array is empty</span>';
      return;
    }

    let validCount = 0;
    let issues = [];

    parsed.forEach((tc, index) => {
      if (typeof tc !== 'object' || tc === null) {
        issues.push(`Item ${index}: Not an object`);
        return;
      }

      if (tc.input === undefined || tc.input === null) {
        issues.push(`Item ${index}: Missing "input"`);
        return;
      }

      if (tc.expected_output === undefined || tc.expected_output === null) {
        issues.push(`Item ${index}: Missing "expected_output"`);
        return;
      }

      validCount++;
    });

    if (validCount === 0) {
      messageDiv.innerHTML = `<span style="color: #dc3545;">✗ No valid test cases. Issues: ${issues.join(', ')}</span>`;
      return;
    }

    let msg = `<span style="color: #28a745;">✓ Valid: ${validCount} test case${validCount > 1 ? 's' : ''}`;
    if (issues.length > 0) {
      msg += ` (${issues.length} invalid items skipped)`;
    }
    msg += '</span>';
    messageDiv.innerHTML = msg;
    setTimeout(() => messageDiv.innerHTML = '', 3000);
  } catch (e) {
    messageDiv.innerHTML = `<span style="color: #dc3545;">✗ Invalid JSON: ${e.message}</span>`;
  }
}

// Validation function
function validateForm() {
  const title = document.getElementById('title').value.trim();
  const slug = document.getElementById('slug').value.trim();
  const description = document.getElementById('description').value.trim();
  const difficulty = document.getElementById('difficulty').value;
  const jsonEditor = getJsonEditor();
  const jsonText = jsonEditor ? jsonEditor.value.trim() : '';

  // Title validation
  if (!title) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Please enter a problem title'
    });
    return false;
  }

  if (title.length < 3 || title.length > 200) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Title must be between 3 and 200 characters'
    });
    return false;
  }

  // Slug validation
  if (!slug) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Please enter a problem slug'
    });
    return false;
  }

  if (slug.length < 3 || slug.length > 100) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Slug must be between 3 and 100 characters'
    });
    return false;
  }

  if (!/^[a-z0-9-]+$/.test(slug)) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Slug can only contain lowercase letters, numbers, and hyphens'
    });
    return false;
  }

  // Description validation
  if (!description) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Please enter a problem description'
    });
    return false;
  }

  if (description.length < 10) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Description must be at least 10 characters'
    });
    return false;
  }

  // Difficulty validation
  if (!difficulty) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Please select a difficulty level'
    });
    return false;
  }

  // Test cases validation
  if (!jsonText) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: 'Test cases JSON is required'
    });
    return false;
  }

  try {
    const parsed = JSON.parse(jsonText);
    if (!Array.isArray(parsed) || parsed.length === 0) {
      Swal.fire({
        icon: 'warning',
        title: 'Validation Error',
        text: 'Test cases must be a non-empty JSON array'
      });
      return false;
    }
    return true;
  } catch (e) {
    Swal.fire({
      icon: 'warning',
      title: 'Validation Error',
      text: `Invalid test cases JSON: ${e.message}`
    });
    return false;
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('form');
  const jsonEditor = getJsonEditor();
  
  // Load test cases from data attribute
  const testCasesData = document.getElementById('test-cases-data');
  console.log('=== TEST CASES DEBUG ===');
  console.log('testCasesData element:', testCasesData);
  
  if (testCasesData) {
    const rawData = testCasesData.textContent;
    console.log('Raw data from textContent:', rawData);
    
    try {
      testCases = JSON.parse(rawData || '[]');
      console.log('Parsed test cases:', testCases);
      console.log('Test cases length:', testCases.length);
    } catch (e) {
      console.error('Error parsing test cases:', e);
      testCases = [];
    }
  } else {
    console.log('test-cases-data element NOT FOUND');
  }
  
  // Load test cases into editor on page load
  if (jsonEditor) {
    console.log('JSON editor found');
    if (testCases.length > 0) {
      console.log('Loading test cases into editor...');
      loadTestCasesIntoEditor();
    } else {
      console.log('No test cases to load (array is empty)');
    }
  } else {
    console.log('JSON editor NOT FOUND');
  }
  
  if (form && jsonEditor) {
    // Form submission
    form.addEventListener('submit', async function(e) {
      e.preventDefault();

      // Validate form
      if (!validateForm()) {
        return;
      }

      const jsonText = jsonEditor.value.trim();
      const parsed = JSON.parse(jsonText);
      const cleanTestCases = parsed.map(tc => ({
        input: tc.input || '',
        expected_output: tc.expected_output || '',
        is_sample: tc.is_sample === true,
        is_hidden: tc.is_hidden !== false
      }));

      document.getElementById('test_cases_json').value = JSON.stringify(cleanTestCases);

      // Show loading state
      Swal.fire({
        title: 'Updating Problem',
        text: 'Please wait...',
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        }
      });

      try {
        const formData = new FormData(this);
        const response = await fetch(this.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        const data = await response.json();

        if (response.ok && data.success) {
          Swal.fire({
            icon: 'success',
            title: 'Success',
            text: data.message || 'Problem updated successfully!',
            showConfirmButton: false,
            timer: 1500
          }).then(() => {
            window.location.href = '/problems';
          });
        } else {
          Swal.fire({
            icon: 'error',
            title: 'Validation Error',
            html: `<div style="text-align: left; white-space: pre-wrap; word-wrap: break-word;">${data.message || 'Failed to update problem. Please check your inputs.'}</div>`,
            confirmButtonText: 'OK'
          });
        }
      } catch (error) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: `An error occurred: ${error.message}`
        });
      }
    });

    // Initialize editor on page load
    loadTestCasesIntoEditor();
  }
});

