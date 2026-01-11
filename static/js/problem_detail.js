// problem_detail.js - Script for problem detail page

// UI Logic
function switchResultTab(tabName) {
    document.querySelectorAll('.panel-tab').forEach(btn => btn.classList.remove('active'));
    if (tabName === 'testcase') {
        document.querySelector('.panel-tab:first-child').classList.add('active');
        document.getElementById('view-testcase').classList.remove('d-none');
        document.getElementById('view-result').classList.add('d-none');
    } else {
        document.getElementById('tab-result').classList.add('active');
        document.getElementById('view-testcase').classList.add('d-none');
        document.getElementById('view-result').classList.remove('d-none');
    }
}

function showCase(index) {
    document.querySelectorAll('.case-btn').forEach(b => {
        b.classList.remove('active', 'border-primary', 'text-primary');
    });
    document.getElementById('btn-case-' + index).classList.add('active', 'border-primary', 'text-primary');
    document.querySelectorAll('[id^="case-content-"]').forEach(d => d.classList.add('d-none'));
    document.getElementById('case-content-' + index).classList.remove('d-none');
}

// Initialize Monaco Editor and setup event listeners
function initProblemDetail() {
    const problemIdEl = document.getElementById('problem-data');
    const outputDiv = document.getElementById('result-output');
    
    if (!problemIdEl || !outputDiv) return;
    
    const problemId = parseInt(problemIdEl.dataset.problemId);
    const functionName = problemIdEl.dataset.functionName || 'solve';
    let starterCodeData = null;
    try {
        const starterCodeStr = problemIdEl.dataset.starterCode || '';
        if (starterCodeStr) {
            starterCodeData = JSON.parse(starterCodeStr);
        }
    } catch (e) {
        console.error('Error parsing starter code:', e);
        starterCodeData = null;
    }

    // Map giữa value của thẻ select và ID ngôn ngữ của Monaco Editor
    const monacoLanguages = {
        'python': 'python',
        'java': 'java',
        'cpp': 'cpp',
        'javascript': 'javascript'
    };

    // Fallback templates nếu không có trong database - sử dụng function name động
    const defaultTemplates = {
        'python': `class Solution:\n    def ${functionName}(self, input_str):\n        # Your code here\n        pass`,
        'java': `class Solution {\n    public void ${functionName}(String input) {\n        // Your code here\n    }\n}`,
        'cpp': `class Solution {\npublic:\n    void ${functionName}(string input) {\n        // Your code here\n    }\n};`,
        'javascript': `class Solution {\n    ${functionName}(input) {\n        // Your code here\n    }\n}`
    };

    // Monaco
    require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.36.1/min/vs' }});
    require(['vs/editor/editor.main'], function() {
        // Check if it's multi-language object or single string
        let initialCode = "";
        if (typeof starterCodeData === 'object' && starterCodeData !== null && Object.keys(starterCodeData).length > 0) {
            // Multi-language: use python as default
            initialCode = starterCodeData['python'] || defaultTemplates['python'];
            window.starterCodes = starterCodeData; // Store for language switching
        } else {
            // Single string or empty
            initialCode = (typeof starterCodeData === 'string' && starterCodeData) ? starterCodeData : defaultTemplates['python'];
            window.starterCodes = null;
        }

        window.editor = monaco.editor.create(document.getElementById('monaco-editor'), {
            value: initialCode,
            language: 'python',
            theme: 'vs-light',
            automaticLayout: true,
            minimap: { enabled: false },
            fontSize: 14,
            scrollBeyondLastLine: false
        });

        // Initialize Bootstrap tooltips
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

        // Bắt sự kiện khi thay đổi dropdown
        document.getElementById('language-select').addEventListener('change', function() {
            const selectedLang = this.value;

            // Lấy ID ngôn ngữ cho Monaco
            const monacoMode = monacoLanguages[selectedLang] || 'python';

            // Lấy code mẫu: ưu tiên từ database, fallback về default
            let templateCode = "";
            if (window.starterCodes && window.starterCodes[selectedLang]) {
                templateCode = window.starterCodes[selectedLang];
            } else {
                templateCode = defaultTemplates[selectedLang] || "";
            }

            // CẬP NHẬT EDITOR:
            // A. Đổi syntax highlighting (màu sắc code)
            monaco.editor.setModelLanguage(window.editor.getModel(), monacoMode);

            // B. Đổi nội dung code thành code mẫu mới
            window.editor.setValue(templateCode);
        });

        // Run Code
        document.getElementById('btn-run').addEventListener('click', async () => {
            switchResultTab('result');
            outputDiv.innerHTML = '<div class="text-center mt-4 text-primary"><div class="spinner-border spinner-border-sm me-2"></div>Running...</div>';

            const code = window.editor.getValue();
            const language = document.getElementById('language-select').value || 'python';
            try {
                const res = await fetch('/api/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ code: code, problem_id: problemId, language: language })
                });
                const data = await res.json();

                let html = '';
                if (data.final_status === 'Accepted') {
                    html += `<div class="alert alert-success d-flex align-items-center py-2 mb-3">
                                <i class="fas fa-check-circle me-2 fs-4"></i><strong>Accepted</strong>
                             </div>`;
                } else {
                    html += `<div class="alert alert-danger d-flex align-items-center py-2 mb-3">
                                <i class="fas fa-times-circle me-2 fs-4"></i><strong>${data.final_status}</strong>
                             </div>`;
                }

                if (data.results) {
                    data.results.forEach(r => {
                        const isPass = r.status === 'Passed';
                        const cardClass = isPass ? 'pass' : 'fail';
                        const icon = isPass ? 'check' : 'times';

                        html += `<div class="result-card ${cardClass}">
                                    <div class="result-header">
                                        <span><i class="fas fa-${icon} me-2"></i> Case ${r.case}</span>
                                        <span>${r.status}</span>
                                    </div>`;
                        if (!isPass) {
                            html += `<div class="result-detail">
                                        <div class="mb-1"><span class="label-text">Input:</span> ${r.input || 'N/A'}</div>
                                        <div class="mb-1"><span class="label-text">Expect:</span> <span class="text-success">${r.expected || 'N/A'}</span></div>
                                        <div><span class="label-text">Actual:</span> <span class="text-danger">${r.actual || r.error || 'Error'}</span></div>
                                     </div>`;
                        }
                        html += `</div>`;
                    });
                }
                outputDiv.innerHTML = html;
            } catch (e) { 
                outputDiv.innerHTML = `<div class="alert alert-danger">Error: ${e.message}</div>`; 
            }
        });

        // Submit
        document.getElementById('btn-submit').addEventListener('click', async () => {
            switchResultTab('result');
            outputDiv.innerHTML = '<div class="text-center mt-4 text-warning"><div class="spinner-border spinner-border-sm me-2"></div>Submitting...</div>';

            const code = window.editor.getValue();
            try {
                const language = document.getElementById('language-select').value || 'python';
                const res = await fetch('/api/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ code: code, problem_id: problemId, language: language })
                });
                const data = await res.json();

                let html = `<div class="d-flex flex-column align-items-center justify-content-center h-100">`;
                if (data.final_status === 'Accepted') {
                    html += `<i class="fas fa-trophy text-warning mb-3" style="font-size: 4rem;"></i>`;
                    html += `<h2 class="text-success">Accepted</h2>`;
                    html += `<p class="text-secondary mb-2">All test cases passed! (${data.test_cases_passed}/${data.total_test_cases})</p>`;
                    if(data.execution_time) html += `<p class="text-muted mb-1"><i class="fas fa-clock me-1"></i>Time: ${data.execution_time.toFixed(2)}ms</p>`;
                    if(data.memory_used) html += `<p class="text-muted mb-2"><i class="fas fa-memory me-1"></i>Memory: ${(data.memory_used / 1024).toFixed(2)}MB</p>`;
                    if(data.submission_id) html += `<a href="/submission/${data.submission_id}" class="btn btn-sm btn-outline-primary mt-2"><i class="fas fa-history me-1"></i>View Submission</a>`;
                } else {
                    html += `<i class="fas fa-times-circle text-danger mb-3" style="font-size: 4rem;"></i>`;
                    html += `<h2 class="text-danger">${data.final_status}</h2>`;
                    html += `<p class="text-secondary mb-2">Test cases passed: ${data.test_cases_passed}/${data.total_test_cases}</p>`;

                    // Hiển thị chi tiết test case fail
                    if(data.failed_case_detail) {
                        html += `<div class="result-detail mt-3 p-3 border rounded bg-light text-start w-75">`;
                        if(data.failed_case_detail.input !== undefined) {
                            html += `<div class="mb-2"><span class="label-text fw-bold">Input:</span> <pre class="d-inline mb-0">${data.failed_case_detail.input || 'N/A'}</pre></div>`;
                        }
                        if(data.failed_case_detail.expected_output !== undefined) {
                            html += `<div class="mb-2"><span class="label-text fw-bold">Expected:</span> <span class="text-success"><pre class="d-inline mb-0">${data.failed_case_detail.expected_output}</pre></span></div>`;
                            html += `<div class="mb-2"><span class="label-text fw-bold">Actual:</span> <span class="text-danger"><pre class="d-inline mb-0">${data.failed_case_detail.actual_output || 'N/A'}</pre></span></div>`;
                        }
                        if(data.failed_case_detail.error !== undefined) {
                            html += `<div class="mb-2"><span class="label-text fw-bold">Error:</span> <span class="text-danger">${data.failed_case_detail.error}</span></div>`;
                        }
                        if(data.failed_case_detail.time_used !== undefined) {
                            html += `<div class="mb-2"><span class="label-text fw-bold">Time Used:</span> ${data.failed_case_detail.time_used.toFixed(2)}ms / ${data.failed_case_detail.time_limit}ms</div>`;
                        }
                        if(data.failed_case_detail.memory_used !== undefined) {
                            html += `<div class="mb-2"><span class="label-text fw-bold">Memory Used:</span> ${data.failed_case_detail.memory_used.toFixed(2)}MB / ${data.failed_case_detail.memory_limit}MB</div>`;
                        }
                        html += `</div>`;
                    }

                    if(data.execution_time) html += `<p class="text-muted mb-1 mt-3"><i class="fas fa-clock me-1"></i>Time: ${data.execution_time.toFixed(2)}ms</p>`;
                    if(data.memory_used) html += `<p class="text-muted mb-2"><i class="fas fa-memory me-1"></i>Memory: ${(data.memory_used / 1024).toFixed(2)}MB</p>`;
                    if(data.submission_id) html += `<a href="/submission/${data.submission_id}" class="btn btn-sm btn-outline-primary mt-2"><i class="fas fa-history me-1"></i>View Submission</a>`;
                }
                html += `</div>`;
                outputDiv.innerHTML = html;
            } catch (e) { 
                outputDiv.innerHTML = `<div class="alert alert-danger">Error: ${e.message}</div>`; 
            }
        });
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initProblemDetail);
} else {
    initProblemDetail();
}

