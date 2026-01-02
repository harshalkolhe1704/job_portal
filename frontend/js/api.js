const API_URL = "http://127.0.0.1:8000";

async function apiCall(endpoint, method = "GET", data = null) {
    const headers = {
        "Content-Type": "application/json"
    };
    
    const token = localStorage.getItem("token");
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const config = {
        method,
        headers,
    };

    if (data) {
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, config);
        
        if (response.status === 401) {
            // Unauthorized - clear token and redirect unless on login page
            if (token && !window.location.href.includes("login.html")) {
                localStorage.removeItem("token");
                localStorage.removeItem("role");
                window.location.href = "login.html";
            }
        }

        const json = await response.json();
        
        if (!response.ok) {
            throw new Error(json.detail || "Something went wrong");
        }
        
        return json;
    } catch (error) {
        console.error("API Error:", error);
        throw error; // Rethrow to handle in UI
    }
}

function isLoggedIn() {
    return !!localStorage.getItem("token");
}

function getUserRole() {
    return localStorage.getItem("role");
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "index.html";
}
