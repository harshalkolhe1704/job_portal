// Initial Load
document.addEventListener("DOMContentLoaded", async () => {
    if (!isLoggedIn() || getUserRole() !== 'seeker') {
        window.location.href = 'login.html';
        return;
    }

    await loadProfile();
    await loadJobs();
    await loadApplications();
});

async function loadProfile() {
    try {
        const user = await apiCall("/auth/me");
        const profile = await apiCall("/seeker/profile");

        const displayName = profile.full_name || user.email;
        document.getElementById("userName").innerText = displayName;

        // Update Avatar
        const avatarChar = (profile.full_name || user.email || "?").charAt(0).toUpperCase();
        document.getElementById("userAvatar").innerText = avatarChar;

        const form = document.getElementById("profileForm");
        form.full_name.value = profile.full_name || "";
        form.resume_link.value = profile.resume_link || "";
        form.skills.value = profile.skills || "";
        form.education.value = profile.education || "";
        form.experience.value = profile.experience || "";
    } catch (e) {
        console.error(e);
    }
}

function openProfileModal() {
    document.getElementById("profileModal").style.display = "flex";
}

function closeProfileModal() {
    document.getElementById("profileModal").style.display = "none";
}

async function handleUpdateProfile(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    try {
        await apiCall("/seeker/profile", "PUT", data);
        alert("Profile updated successfully!");
        closeProfileModal();
        await loadProfile(); // Refresh display name and avatar
    } catch (e) {
        alert(e.message);
    }
}

async function loadJobs() {
    const title = document.getElementById("searchTitle").value;
    const location = document.getElementById("searchLocation").value;

    let query = "?";
    if (title) query += `title=${title}&`;
    if (location) query += `location=${location}`;

    try {
        const jobs = await apiCall(`/seeker/jobs${query}`);
        const container = document.getElementById("jobsList");
        container.innerHTML = "";

        if (jobs.length === 0) {
            container.innerHTML = "<p>No jobs found.</p>";
            return;
        }

        jobs.forEach(job => {
            const card = document.createElement("div");
            card.className = "card";
            card.innerHTML = `
                <h3>${job.title}</h3>
                <p class="text-sm text-muted">${job.company_name} • ${job.location}</p>
                <div style="margin: 1rem 0;">
                    <span class="badge" style="background: #f1f5f9; color: #475569;">${job.job_type}</span>
                    <span class="badge" style="background: #f1f5f9; color: #475569;">${job.salary_range}</span>
                </div>
                <p style="margin-bottom: 1rem;">${job.description.substring(0, 100)}...</p>
                <button onclick="applyForJob(${job.id})" class="btn btn-primary" style="width: 100%;">Apply Now</button>
            `;
            container.appendChild(card);
        });
    } catch (e) {
        console.error(e);
    }
}

async function loadApplications() {
    try {
        const apps = await apiCall("/seeker/applications");
        const container = document.getElementById("applicationsList");
        container.innerHTML = "";

        if (apps.length === 0) {
            container.innerHTML = "<p>No applications yet.</p>";
            return;
        }

        apps.forEach(app => {
            let badgeClass = "badge-applied";
            if (app.status === "Accepted") badgeClass = "badge-accepted";
            if (app.status === "Rejected") badgeClass = "badge-rejected";

            const div = document.createElement("div");
            div.className = "card";
            div.style.padding = "1rem";
            div.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>${app.job_title}</strong>
                    <span class="badge ${badgeClass}">${app.status}</span>
                </div>
                <p class="text-sm text-muted" style="margin-top: 0.5rem;">Applied: ${new Date(app.applied_at).toLocaleDateString()}</p>
            `;
            container.appendChild(div);
        });
    } catch (e) {
        console.error(e);
    }
}

async function applyForJob(jobId) {
    if (!confirm("Confirm apply?")) return;
    try {
        await apiCall(`/seeker/apply/${jobId}`, "POST");
        alert("Applied successfully!");
        loadApplications();
    } catch (e) {
        alert(e.message);
    }
}
