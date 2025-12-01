DROP DATABASE IF EXISTS coding_practice_system;

CREATE DATABASE IF NOT EXISTS coding_practice_system;
USE coding_practice_system;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    total_solved INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

CREATE TABLE tags (
    tag_id INT PRIMARY KEY AUTO_INCREMENT,
    tag_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    INDEX idx_tag_name (tag_name)
);

CREATE TABLE problems (
    problem_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    difficulty ENUM('Easy', 'Medium', 'Hard') NOT NULL,
    time_limit INT DEFAULT 1000,
    memory_limit INT DEFAULT 256,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_difficulty (difficulty),
    INDEX idx_slug (slug)
);

CREATE TABLE problem_tags (
    problem_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (problem_id, tag_id),
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE,
    INDEX idx_problem_id (problem_id),
    INDEX idx_tag_id (tag_id)
);

CREATE TABLE test_cases (
    test_case_id INT PRIMARY KEY AUTO_INCREMENT,
    problem_id INT NOT NULL,
    input TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_sample BOOLEAN DEFAULT FALSE,
    is_hidden BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE,
    INDEX idx_problem_id (problem_id)
);

CREATE TABLE submissions (
    submission_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    problem_id INT NOT NULL,
    code TEXT NOT NULL,
    language VARCHAR(20) NOT NULL,
    status ENUM('Pending', 'Accepted', 'Wrong Answer', 'Time Limit Exceeded', 
                'Memory Limit Exceeded', 'Runtime Error', 'Compilation Error') DEFAULT 'Pending',
    execution_time INT,
    memory_used INT,
    test_cases_passed INT DEFAULT 0,
    total_test_cases INT DEFAULT 0,
    submitted_at DATETIME NULL DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_problem_id (problem_id),
    INDEX idx_status (status),
    INDEX idx_submitted_at (submitted_at)
);

CREATE TABLE user_problems (
    user_id INT NOT NULL,
    problem_id INT NOT NULL,
    status ENUM('Not Attempted', 'Attempted', 'Solved') DEFAULT 'Not Attempted',
    attempts INT DEFAULT 0,
    best_submission_id INT NULL,
    first_solved_at TIMESTAMP NULL,
    last_attempted_at TIMESTAMP NULL,
    PRIMARY KEY (user_id, problem_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE,
    FOREIGN KEY (best_submission_id) REFERENCES submissions(submission_id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_problem_id (problem_id),
    INDEX idx_status (status)
);

-- Insert sample data
INSERT INTO users (user_id, username, email, password_hash, full_name, total_solved, created_at)
VALUES
(1, 'alice123', 'alice@example.com', 'hash1', 'Alice Nguyen', 12, CURRENT_TIMESTAMP),
(2, 'bobdev', 'bob@example.com', 'hash2', 'Bob Tran', 5, CURRENT_TIMESTAMP),
(3, 'charlie', 'charlie@example.com', 'hash3', 'Charlie Le', 20, CURRENT_TIMESTAMP),
(4, 'daisy01', 'daisy@example.com', 'hash4', 'Daisy Pham', 8, CURRENT_TIMESTAMP),
(5, 'ericpro', 'eric@example.com', 'hash5', 'Eric Bui', 0, CURRENT_TIMESTAMP);

INSERT INTO tags (tag_id, tag_name, description)
VALUES
(1, 'Array', 'Operations on arrays'),
(2, 'String', 'Handling text data'),
(3, 'Math', 'Mathematical logic and formulas'),
(4, 'DP', 'Dynamic Programming'),
(5, 'Graph', 'Graph algorithms'),
(6, 'Sorting', 'Sorting and searching techniques');

INSERT INTO problems (problem_id, title, slug, description, difficulty, time_limit, memory_limit, created_at, updated_at)
VALUES
(1, 'Two Sum', 'two-sum', 'Find two numbers that add up to target.', 'Easy', 1000, 256, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'Valid Parentheses', 'valid-parentheses', 'Check if parentheses are valid.', 'Easy', 1000, 256, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(3, 'Longest Substring Without Repeat', 'longest-substring', 'Find longest substring with unique chars.', 'Medium', 1000, 256, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(4, 'Climbing Stairs', 'climbing-stairs', 'Count number of ways to climb stairs.', 'Easy', 1000, 256, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(5, 'Dijkstra Shortest Path', 'dijkstra-path', 'Compute shortest path in graph.', 'Hard', 1000, 256, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO problem_tags (problem_id, tag_id)
VALUES
(1, 1),
(1, 6),
(2, 2),
(3, 2),
(3, 1),
(4, 3),
(5, 5),
(5, 3);

INSERT INTO test_cases (test_case_id, problem_id, input, expected_output, is_sample, is_hidden, created_at)
VALUES
(1, 1, 'nums=[2,7,11,15], target=9', '[0,1]', TRUE, FALSE, CURRENT_TIMESTAMP),
(2, 2, 's="()[]{}"', 'true', TRUE, FALSE, CURRENT_TIMESTAMP),
(3, 3, 's="abcabcbb"', '3', TRUE, FALSE, CURRENT_TIMESTAMP),
(4, 4, 'n=3', '3', TRUE, FALSE, CURRENT_TIMESTAMP),
(5, 5, 'graph example', '0→3', TRUE, TRUE, CURRENT_TIMESTAMP);

INSERT INTO submissions (submission_id, user_id, problem_id, code, language, status, execution_time, memory_used, test_cases_passed, total_test_cases, submitted_at)
VALUES
(1, 1, 1, 'code1', 'Python', 'Accepted', 12, 1024, 1, 1, CURRENT_TIMESTAMP),
(2, 2, 1, 'code2', 'Java', 'Wrong Answer', 20, 2048, 0, 1, CURRENT_TIMESTAMP),
(3, 3, 3, 'code3', 'Python', 'Accepted', 34, 1500, 1, 1, CURRENT_TIMESTAMP),
(4, 4, 2, 'code4', 'C++', 'Runtime Error', 0, 0, 0, 1, CURRENT_TIMESTAMP),
(5, 5, 5, 'code5', 'Python', 'Time Limit Exceeded', 1000, 3000, 0, 1, CURRENT_TIMESTAMP);

INSERT INTO user_problems (user_id, problem_id, status, attempts, best_submission_id, first_solved_at, last_attempted_at)
VALUES
(1, 1, 'Solved', 2, 1, NULL, NULL),
(2, 1, 'Attempted', 1, 2, NULL, NULL),
(3, 3, 'Solved', 3, 3, NULL, NULL),
(4, 2, 'Attempted', 1, 4, NULL, NULL),
(5, 5, 'Attempted', 2, 5, NULL, NULL);
