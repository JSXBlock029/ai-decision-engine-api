/**
 * Waitlist Form Handler
 * Updates the landing page to use backend API
 */

async function handleWaitlistSubmit(event) {
    event.preventDefault();
    const email = document.getElementById('emailInput').value;
    const name = document.getElementById('nameInput')?.value || '';
    const messageEl = document.getElementById('formMessage');
    
    // Show loading state
    const submitButton = event.target.querySelector('.submit-button');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Joining...';
    submitButton.disabled = true;
    
    try {
        // Send to backend API
        const response = await fetch('http://localhost:8001/waitlist/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                name: name || null,
                company: null
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageEl.textContent = `✅ Thanks! You're #${data.position} on the waitlist. We'll notify you when we launch!`;
            messageEl.style.display = 'block';
            messageEl.style.color = 'white';
            
            // Reset form
            document.getElementById('waitlistForm').reset();
        } else {
            throw new Error(data.detail || 'Failed to join waitlist');
        }
    } catch (error) {
        console.error('Waitlist error:', error);
        messageEl.textContent = `⚠️ ${error.message}. Please try again.`;
        messageEl.style.display = 'block';
        messageEl.style.color = '#ffeb3b';
    } finally {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }
}

// Update the form to use this handler
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('waitlistForm');
    if (form) {
        form.addEventListener('submit', handleWaitlistSubmit);
    }
});

