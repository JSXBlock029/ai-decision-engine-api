// Update landing page to connect to backend API
// Replace the handleWaitlistSubmit function in index.html with this version

async function handleWaitlistSubmit(event) {
    event.preventDefault();
    const email = document.getElementById('emailInput').value;
    const messageEl = document.getElementById('formMessage');
    const submitButton = document.querySelector('.submit-button');
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.textContent = 'Adding...';
    messageEl.style.display = 'none';
    
    try {
        // In production, use: https://waitlist.api.example.com/waitlist
        // For development, use: http://localhost:8001/waitlist
        const API_URL = 'http://localhost:8001/waitlist';
        
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageEl.textContent = `✅ Thanks ${data.email}! You're #${data.position} on the waitlist. We'll notify you when we launch!`;
            messageEl.style.display = 'block';
            messageEl.style.color = 'white';
            document.getElementById('waitlistForm').reset();
            
            // Log success
            console.log('Waitlist signup successful:', data);
        } else {
            throw new Error(data.detail || 'Failed to add to waitlist');
        }
    } catch (error) {
        messageEl.textContent = `❌ Error: ${error.message}. Please try again.`;
        messageEl.style.display = 'block';
        messageEl.style.color = '#ffcccc';
        console.error('Waitlist signup error:', error);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Join Waitlist';
    }
}

