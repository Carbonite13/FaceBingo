document.addEventListener('DOMContentLoaded', () => {
    const modal = document.querySelector('#profile-modal'),
    form = document.querySelector('#profile-form'),
    saved = JSON.parse(localStorage.getItem('facebingo_profile') || 'null');
    if (!saved) modal.classList.add('active');
    else {
        profileName.value = saved.name || '';
        profileBio.value = saved.bio || '';
    }
    form.addEventListener('submit', async e => {
        e.preventDefault();
        const profile = {
            name: profileName.value.trim(),
            bio: profileBio.value.trim()
        };
        if (!profile.name) return; 
        localStorage.setItem('facebingo_profile', JSON.stringify(profile)); 
        document.cookie = `facebingo_profile=${encodeURIComponent(JSON.stringify(profile))};path=/;SameSite=Lax`; 
        modal.classList.remove('active'); 
        try { 
            const r = await fetch('/api/register', {
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify(profile) 
            });

            if (r.ok) { 
                const stored = await r.json(); 
                localStorage.setItem('facebingo_profile', JSON.stringify(stored)); 
            } 
        } catch { 
            console.log('Error in registering profile');
        }
    });
});
