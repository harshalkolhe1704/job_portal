// Initial Load
document.addEventListener("DOMContentLoaded", async () => {
    console.log("Admin Dashboard initializing...");
    if (!isLoggedIn()) {
        console.warn("User not logged in, redirecting to login...");
        window.location.href = 'login.html';
        return;
    }

    if (getUserRole() !== 'admin') {
        console.error("Access denied: User is not an admin. Role:", getUserRole());
        window.location.href = 'login.html';
        return;
    }

    window.initAdminDashboard = async () => {
        try {
            console.log("Fetching admin data...");
            await Promise.all([
                loadStats(),
                loadUsers(),
                loadJobs()
            ]);
            console.log("Admin Dashboard data loaded successfully.");
        } catch (err) {
            console.error("Critical error loading Admin Dashboard:", err);
            alert("Failed to load dashboard data. Check console for details.");
        }
    };

    await initAdminDashboard();
});

async function loadStats() {
    try {
        const stats = await apiCall("/admin/stats");
        document.getElementById("totalUsers").innerText = stats.total_users;
        document.getElementById("totalJobs").innerText = stats.total_jobs;
        document.getElementById("totalApps").innerText = stats.total_applications;
    } catch (e) {
        console.error(e);
    }
}

async function loadUsers() {
    try {
        const users = await apiCall("/admin/users");
        const container = document.getElementById("usersList");
        container.innerHTML = "";

        if (users.length === 0) {
            container.innerHTML = "<div style='padding: 2rem; text-align: center; color: var(--gray);'>No users found.</div>";
            return;
        }

        users.forEach(user => {
            const row = document.createElement("div");
            row.className = "admin-list-row";
            const initial = user.email.charAt(0).toUpperCase();

            row.innerHTML = `
                <div class="user-info-main">
                    <div class="user-initial-circle">${initial}</div>
                    <div>
                        <div style="font-weight: 600; color: var(--dark);">${user.email}</div>
                        <div style="font-size: 0.75rem; color: var(--gray); display: flex; gap: 0.5rem; align-items: center; margin-top: 0.2rem;">
                            <span class="badge" style="background: #e2e8f0; color: #475569; padding: 0.1rem 0.4rem;">${user.role}</span>
                            <span>ID: ${user.id}</span>
                        </div>
                    </div>
                </div>
                <button onclick="deleteUser(${user.id})" class="btn btn-secondary" 
                    style="color: var(--danger); border-color: #fee2e2; font-size: 0.75rem; padding: 0.35rem 0.75rem;">
                    Remove
                </button>
            `;
            container.appendChild(row);
        });
    } catch (e) {
        console.error(e);
        document.getElementById("usersList").innerHTML = "<div style='padding: 2rem; color: var(--danger);'>Error loading users.</div>";
    }
}

async function loadJobs() {
    try {
        const jobs = await apiCall("/admin/jobs");
        const container = document.getElementById("jobsList");
        container.innerHTML = "";

        if (jobs.length === 0) {
            container.innerHTML = "<div style='padding: 2rem; text-align: center; color: var(--gray);'>No active jobs.</div>";
            return;
        }

        jobs.forEach(job => {
            const row = document.createElement("div");
            row.className = "admin-list-row";

            row.innerHTML = `
                <div>
                    <div style="font-weight: 600; color: var(--dark);">${job.title}</div>
                    <div style="font-size: 0.75rem; color: var(--gray); margin-top: 0.2rem;">
                        <span style="color: var(--primary); font-weight: 500;">${job.company_name}</span>
                    </div>
                </div>
                <button onclick="deleteJob(${job.id})" class="btn btn-secondary" 
                    style="color: var(--danger); border-color: #fee2e2; font-size: 0.75rem; padding: 0.35rem 0.75rem;">
                    Delete
                </button>
            `;
            container.appendChild(row);
        });
    } catch (e) {
        console.error(e);
        document.getElementById("jobsList").innerHTML = "<div style='padding: 2rem; color: var(--danger);'>Error loading jobs.</div>";
    }
}

async function deleteUser(userId) {
    if (!confirm("Are you sure? This will delete all their data.")) return;
    try {
        await apiCall(`/admin/users/${userId}`, "DELETE");
        loadUsers();
        loadStats(); // Refresh stats
    } catch (e) {
        alert(e.message);
    }
}

async function deleteJob(jobId) {
    if (!confirm("Are you sure?")) return;
    try {
        await apiCall(`/admin/jobs/${jobId}`, "DELETE");
        loadJobs();
        loadStats();
    } catch (e) {
        alert(e.message);
    }
}
