// Register Form Handler
async function handleRegister(event) {
    event.preventDefault();
    const btn = event.target.querySelector("button");
    const originalText = btn.innerText;
    btn.innerText = "Loading...";
    btn.disabled = true;

    try {
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());

        // Pass basic profile info based on role
        if (data.role === 'seeker') {
            data.full_name = data.name_or_company;
        } else if (data.role === 'employer') {
            data.company_name = data.name_or_company;
        }

        delete data.name_or_company; // cleanup

        const response = await apiCall("/auth/register", "POST", data);
        console.log("Registered:", response);
        alert("Registration successful! Please login.");
        window.location.href = "login.html";
    } catch (error) {
        alert(error.message);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

// Login Form Handler
async function handleLogin(event) {
    event.preventDefault();
    const btn = event.target.querySelector("button");
    const originalText = btn.innerText;
    btn.innerText = "Loading...";
    btn.disabled = true;

    try {
        const formData = new FormData(event.target);
        // OAuth2PasswordRequestForm expects username/password as form-data, not JSON typically, 
        // but our apiCalls sends JSON. 
        // Wait, backend: login(form_data: OAuth2PasswordRequestForm = Depends())
        // This requires application/x-www-form-urlencoded

        const urlEncodedData = new URLSearchParams();
        urlEncodedData.append("username", formData.get("email"));
        urlEncodedData.append("password", formData.get("password"));

        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: urlEncodedData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Login failed");
        }

        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", data.role);

        window.location.href = `dashboard_${data.role}.html`;
    } catch (error) {
        alert(error.message);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}
