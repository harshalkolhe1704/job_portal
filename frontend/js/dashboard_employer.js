// Initial Load
document.addEventListener("DOMContentLoaded", async () => {
    if (!isLoggedIn() || getUserRole() !== 'employer') {
        window.location.href = 'login.html';
        return;
    }
    await loadProfile();
    await loadMyJobs();
});

async function loadProfile() {
    try {
        const user = await apiCall("/auth/me");
        const profile = await apiCall("/employer/profile");

        const displayName = profile.company_name || user.email;
        document.getElementById("userName").innerText = displayName;

        // Update Avatar
        const avatarChar = (profile.company_name || user.email || "?").charAt(0).toUpperCase();
        document.getElementById("userAvatar").innerText = avatarChar;

        const form = document.getElementById("profileForm");
        form.company_name.value = profile.company_name || "";
        form.location.value = profile.location || "";
        form.website.value = profile.website || "";
        form.company_description.value = profile.company_description || "";
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
        await apiCall("/employer/profile", "PUT", data);
        alert("Company profile updated successfully!");
        closeProfileModal();
        await loadProfile(); // Refresh
    } catch (e) {
        alert(e.message);
    }
}

async function handlePostJob(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    // Convert empty strings to null for optional backend fields
    for (let key in data) {
        if (data[key] === "") data[key] = null;
    }

    try {
        await apiCall("/employer/jobs", "POST", data);
        alert("Job posted!");
        event.target.reset();
        loadMyJobs();
    } catch (e) {
        alert(e.message);
    }
}

let myJobs = []; // Global registry to avoid JSON.stringify issues in HTML attributes

async function loadMyJobs() {
    try {
        myJobs = await apiCall("/employer/jobs");
        const container = document.getElementById("jobsList");
        container.innerHTML = "";

        if (myJobs.length === 0) {
            container.innerHTML = "<p>No jobs posted yet.</p>";
            return;
        }

        myJobs.forEach(job => {
            const card = document.createElement("div");
            card.className = "card";
            const postedDate = new Date(job.posted_at).toLocaleDateString();
            const closingDate = job.closing_date ? new Date(job.closing_date).toLocaleDateString() : "No deadline";

            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="margin-bottom: 0.25rem;">${job.title}</h3>
                        <p class="text-sm text-muted">${job.location} • ${job.job_type}</p>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <button onclick="openEditModalById(${job.id})" class="btn btn-secondary" style="font-size: 0.8rem; padding: 0.4rem 0.8rem;">Edit</button>
                        <button onclick="deleteJob(${job.id})" class="btn btn-secondary" style="color: var(--danger); border-color: var(--danger); font-size: 0.8rem; padding: 0.4rem 0.8rem;">Delete</button>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding: 0.75rem; background: #f8fafc; border-radius: 0.5rem; display: flex; gap: 2rem;">
                    <div><span class="text-xs text-muted">POSTED</span><br><b class="text-sm">${postedDate}</b></div>
                    <div><span class="text-xs text-muted">CLOSING</span><br><b class="text-sm">${closingDate}</b></div>
                </div>
                <div style="margin-top: 1rem;">
                    <button onclick="viewApplicants(${job.id})" class="btn btn-primary" style="width: 100%;">View Applicants</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (e) {
        console.error(e);
    }
}

function openEditModalById(jobId) {
    const job = myJobs.find(j => j.id === jobId);
    if (!job) return;

    document.getElementById("editJobId").value = job.id;
    const form = document.getElementById("editJobForm");
    form.title.value = job.title;
    form.location.value = job.location;
    form.job_type.value = job.job_type;
    form.salary_range.value = job.salary_range;
    form.description.value = job.description;

    if (job.closing_date) {
        form.closing_date.value = job.closing_date.split('T')[0];
    } else {
        form.closing_date.value = "";
    }

    document.getElementById("editJobModal").style.display = "flex";
}

function closeEditModal() {
    document.getElementById("editJobId").value = "";
    document.getElementById("editJobModal").style.display = "none";
}

async function handleUpdateJob(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const id = formData.get("id");
    const data = Object.fromEntries(formData.entries());
    delete data.id;

    // Convert empty strings to null for the backend
    for (let key in data) {
        if (data[key] === "") data[key] = null;
    }

    try {
        await apiCall(`/employer/jobs/${id}`, "PUT", data);
        alert("Job updated successfully!");
        closeEditModal();
        loadMyJobs();
    } catch (e) {
        alert(e.message);
    }
}

async function deleteJob(jobId) {
    if (!confirm("Delete this job post?")) return;
    try {
        await apiCall(`/employer/jobs/${jobId}`, "DELETE");
        loadMyJobs();
    } catch (e) {
        alert(e.message);
    }
}

async function viewApplicants(jobId) {
    const modal = document.getElementById("applicantsModal");
    const container = document.getElementById("applicantsList");
    container.innerHTML = "Loading...";
    modal.style.display = "flex";

    try {
        const apps = await apiCall(`/employer/jobs/${jobId}/applicants`);
        container.innerHTML = "";

        if (apps.length === 0) {
            container.innerHTML = "<p class='text-center py-4'>No applicants yet for this position.</p>";
            return;
        }

        apps.forEach(app => {
            const div = document.createElement("div");
            div.className = "card";
            div.style.padding = "1.5rem";
            div.style.border = "1px solid #e2e8f0";

            div.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <div>
                        <h4 style="font-size: 1.1rem; margin-bottom: 0.25rem;">${app.seeker_name}</h4>
                        <p class="text-sm text-muted">${app.seeker_email}</p>
                    </div>
                    <span class="badge ${app.status === 'Accepted' ? 'badge-accepted' : app.status === 'Rejected' ? 'badge-rejected' : 'badge-applied'}">${app.status}</span>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
                    <div>
                        <p class="text-xs text-muted">SKILLS</p>
                        <p class="text-sm">${app.seeker_skills || 'Not specified'}</p>
                    </div>
                    <div>
                        <p class="text-xs text-muted">EDUCATION</p>
                        <p class="text-sm">${app.seeker_education || 'Not specified'}</p>
                    </div>
                    <div style="grid-column: span 2;">
                        <p class="text-xs text-muted">EXPERIENCE</p>
                        <p class="text-sm" style="white-space: pre-wrap;">${app.seeker_experience || 'Not specified'}</p>
                    </div>
                    <div style="grid-column: span 2;">
                        <p class="text-xs text-muted">RESUME / LINKEDIN</p>
                        ${app.seeker_resume_link ? `<a href="${app.seeker_resume_link}" target="_blank" class="text-sm" style="color: var(--primary);">View Resume</a>` : '<p class="text-sm">Not provided</p>'}
                    </div>
                </div>

                <div style="display: flex; gap: 1rem; border-top: 1px solid #f1f5f9; pt-1rem; padding-top: 1rem;">
                    <button onclick="updateStatus(${app.id}, 'Accepted')" class="btn btn-primary" style="flex: 1; background: #22c55e; border: none;">Accept Applicant</button>
                    <button onclick="updateStatus(${app.id}, 'Rejected')" class="btn btn-secondary" style="flex: 1; color: var(--danger); border-color: var(--danger);">Reject Applicant</button>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (e) {
        container.innerHTML = "Error loading applicants.";
    }
}

async function updateStatus(appId, status) {
    if (!confirm(`Are you sure you want to ${status.toLowerCase()} this applicant?`)) return;
    try {
        await apiCall(`/employer/applications/${appId}/status?status=${status}`, "PUT");
        alert(`Application ${status.toLowerCase()}ed successfully`);
        // We don't close modal, just refresh the list to show new status
        // Extract jobId from current modal or just reload if we can. 
        // For simplicity, let's close and let them open again if they want, or refresh.
        // Actually, let's just close to avoid complex state tracking for now.
        closeModal();
    } catch (e) {
        alert(e.message);
    }
}

function closeModal() {
    document.getElementById("applicantsModal").style.display = "none";
}
