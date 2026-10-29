/**
 * Customer Cargo Booking & Manifest Management Client Services
 */
const CustomerService = {
    // Execute a booking for a targeted trip
    bookTrip: async function(tripId, bookingDetails = {}, triggerBtn = null) {
        if (triggerBtn) {
            window.HaulPool.setButtonLoading(triggerBtn, true, 'Confirming Booking...');
        }

        const payload = {
            trip_id: tripId,
            description: bookingDetails.description || 'General Merchandise Cargo',
            weight: parseFloat(bookingDetails.weight || 1.0),
            pickup: bookingDetails.pickup || '',
            dropoff: bookingDetails.dropoff || '',
            amount: floatOrZero(bookingDetails.amount)
        };

        try {
            const response = await fetch('/customer/api/book', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || 'Booking could not be processed');

            window.HaulPool.showToast(result.message || 'Booking Confirmed!');
            setTimeout(() => {
                window.location.href = '/customer/dashboard';
            }, 800);

        } catch (err) {
            window.HaulPool.showToast(err.message, true);
        } finally {
            if (triggerBtn) window.HaulPool.setButtonLoading(triggerBtn, false);
        }
    },

    // Update customer contact / profile info
    updateProfile: async function(event, formElement) {
        event.preventDefault();
        const submitBtn = formElement.querySelector('button[type="submit"]');

        const payload = {
            phone: formElement.querySelector('#custPhone')?.value || '',
            address: formElement.querySelector('#custAddress')?.value || '',
            company_name: formElement.querySelector('#custCompany')?.value || '',
            gst_number: formElement.querySelector('#custGst')?.value || ''
        };

        window.HaulPool.setButtonLoading(submitBtn, true, 'Saving Profile...');

        try {
            const response = await fetch('/customer/api/profile', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || 'Failed to update profile');

            window.HaulPool.showToast('Profile updated successfully!');
            setTimeout(() => { window.location.reload(); }, 600);
        } catch (err) {
            window.HaulPool.showToast(err.message, true);
        } finally {
            window.HaulPool.setButtonLoading(submitBtn, false);
        }
    }
};

function floatOrZero(val) {
    const f = parseFloat(val);
    return isNaN(f) ? 0 : f;
}

window.CustomerService = CustomerService;
