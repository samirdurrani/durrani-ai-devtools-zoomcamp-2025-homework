// Configuration constants for the application

// Backend API configuration
// Change these values to match your backend server
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'

// Supported programming languages
// Each language has a name, id (used by Monaco editor), and default code template
export const LANGUAGES = [
  {
    id: 'javascript',
    name: 'JavaScript',
    defaultCode: '// Welcome to the coding interview platform!\n// JavaScript runs directly in your browser\n\nfunction solution() {\n  // Your code here\n  console.log("Hello, World!");\n  \n  // Try some computations\n  const numbers = [1, 2, 3, 4, 5];\n  const sum = numbers.reduce((a, b) => a + b, 0);\n  console.log("Sum:", sum);\n}\n\nsolution();',
    canRunInBrowser: true,
    executionEngine: 'native',
  },
  {
    id: 'typescript',
    name: 'TypeScript',
    defaultCode: '// Welcome to the coding interview platform!\n// TypeScript is compiled to JavaScript in your browser\n\ninterface Person {\n  name: string;\n  age: number;\n}\n\nfunction greet(person: Person): void {\n  console.log(`Hello, ${person.name}!`);\n  console.log(`You are ${person.age} years old.`);\n}\n\nconst user: Person = {\n  name: "Alice",\n  age: 25\n};\n\ngreet(user);',
    canRunInBrowser: true,
    executionEngine: 'typescript-compiler',
  },
  {
    id: 'python',
    name: 'Python',
    defaultCode: '# Welcome to the coding interview platform!\n# Python runs via Pyodide WebAssembly in your browser\n\ndef solution():\n    # Your code here\n    print("Hello, World!")\n    \n    # Try some Python features\n    numbers = [1, 2, 3, 4, 5]\n    total = sum(numbers)\n    print(f"Sum: {total}")\n    \n    # List comprehension\n    squares = [x**2 for x in numbers]\n    print(f"Squares: {squares}")\n\nsolution()',
    canRunInBrowser: true,
    executionEngine: 'pyodide',
    loadingMessage: 'Loading Python environment (Pyodide)... This may take a few seconds on first run.',
  },
  {
    id: 'html',
    name: 'HTML',
    defaultCode: '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Hello World</title>\n    <style>\n        body {\n            font-family: Arial, sans-serif;\n            display: flex;\n            justify-content: center;\n            align-items: center;\n            height: 100vh;\n            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n        }\n        .container {\n            text-align: center;\n            color: white;\n        }\n    </style>\n</head>\n<body>\n    <div class="container">\n        <h1>Hello, World!</h1>\n        <p>Welcome to the coding interview platform!</p>\n    </div>\n</body>\n</html>',
    canRunInBrowser: true,
    executionEngine: 'html-preview',
  },
  {
    id: 'css',
    name: 'CSS',
    defaultCode: '/* CSS Validation and Preview */\n/* Write your CSS rules here */\n\nbody {\n    font-family: "Segoe UI", Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n    background: #f0f0f0;\n}\n\n.container {\n    max-width: 1200px;\n    margin: 0 auto;\n    padding: 20px;\n    background: white;\n    border-radius: 8px;\n    box-shadow: 0 2px 10px rgba(0,0,0,0.1);\n}\n\nh1 {\n    color: #333;\n    border-bottom: 2px solid #007acc;\n    padding-bottom: 10px;\n}\n\n.button {\n    display: inline-block;\n    padding: 10px 20px;\n    background: #007acc;\n    color: white;\n    border: none;\n    border-radius: 4px;\n    cursor: pointer;\n    transition: background 0.3s;\n}\n\n.button:hover {\n    background: #005a9e;\n}',
    canRunInBrowser: true,
    executionEngine: 'css-validator',
  },
  {
    id: 'java',
    name: 'Java',
    defaultCode: '// Java code cannot run directly in the browser\n// This is for syntax highlighting and collaboration only\n\npublic class Main {\n    public static void main(String[] args) {\n        // Your code here\n        System.out.println("Hello, World!");\n        \n        // Example: Calculate factorial\n        int n = 5;\n        int factorial = calculateFactorial(n);\n        System.out.println("Factorial of " + n + " is: " + factorial);\n    }\n    \n    public static int calculateFactorial(int n) {\n        if (n <= 1) return 1;\n        return n * calculateFactorial(n - 1);\n    }\n}',
    canRunInBrowser: false,
    executionEngine: 'not-supported',
    note: 'Java requires server-side compilation',
  },
  {
    id: 'cpp',
    name: 'C++',
    defaultCode: '// C++ code cannot run directly in the browser\n// This is for syntax highlighting and collaboration only\n\n#include <iostream>\n#include <vector>\nusing namespace std;\n\nint main() {\n    // Your code here\n    cout << "Hello, World!" << endl;\n    \n    // Example: Find prime numbers\n    vector<int> primes;\n    for (int i = 2; i <= 20; i++) {\n        bool isPrime = true;\n        for (int j = 2; j * j <= i; j++) {\n            if (i % j == 0) {\n                isPrime = false;\n                break;\n            }\n        }\n        if (isPrime) primes.push_back(i);\n    }\n    \n    cout << "Prime numbers up to 20: ";\n    for (int prime : primes) {\n        cout << prime << " ";\n    }\n    cout << endl;\n    \n    return 0;\n}',
    canRunInBrowser: false,
    executionEngine: 'not-supported',
    note: 'C++ requires server-side compilation',
  },
  {
    id: 'go',
    name: 'Go',
    defaultCode: '// Go code cannot run directly in the browser\n// This is for syntax highlighting and collaboration only\n\npackage main\n\nimport "fmt"\n\nfunc main() {\n    // Your code here\n    fmt.Println("Hello, World!")\n    \n    // Example: Fibonacci sequence\n    n := 10\n    fmt.Printf("First %d Fibonacci numbers:\\n", n)\n    for i := 0; i < n; i++ {\n        fmt.Printf("%d ", fibonacci(i))\n    }\n    fmt.Println()\n}\n\nfunc fibonacci(n int) int {\n    if n <= 1 {\n        return n\n    }\n    return fibonacci(n-1) + fibonacci(n-2)\n}',
    canRunInBrowser: false,
    executionEngine: 'not-supported',
    note: 'Go requires server-side compilation',
  },
  {
    id: 'rust',
    name: 'Rust',
    defaultCode: '// Rust code cannot run directly in the browser\n// This is for syntax highlighting and collaboration only\n\nfn main() {\n    // Your code here\n    println!("Hello, World!");\n    \n    // Example: Calculate sum of squares\n    let numbers = vec![1, 2, 3, 4, 5];\n    let sum_of_squares: i32 = numbers\n        .iter()\n        .map(|x| x * x)\n        .sum();\n    \n    println!("Sum of squares: {}", sum_of_squares);\n    \n    // Pattern matching example\n    let x = 5;\n    match x {\n        1 => println!("One"),\n        2 => println!("Two"),\n        3..=5 => println!("Three to five"),\n        _ => println!("Something else"),\n    }\n}',
    canRunInBrowser: false,
    executionEngine: 'not-supported',
    note: 'Rust requires server-side compilation',
  },
]

// WebSocket event types
export const WS_EVENTS = {
  JOIN_SESSION: 'join_session',
  LEAVE_SESSION: 'leave_session',
  CODE_UPDATE: 'code_update',
  LANGUAGE_CHANGE: 'language_change',
  EXECUTE_CODE: 'execute_code',
  EXECUTION_RESULT: 'execution_result',
  USER_JOINED: 'user_joined',
  USER_LEFT: 'user_left',
  SESSION_STATE: 'session_state',
  ERROR: 'error',
}