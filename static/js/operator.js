/**
 * Transport Operator Studio & Route Management Client Services
 */
const OperatorService = {
    // Post new route/trip
    publishTrip: async function(event, formElement) {
        event.preventDefault();
        const submitBtn = formElement.querySelector('button[type="submit"]') || formElement.querySelector('.btn-submit');
        
        const payload = {
            start: formElement.querySelector('#startLocation, input[name="start"]').value.strip ? formElement.querySelector('#startLocation, input[name="start"]').value.trim() : '',
            end: formElement.querySelector('#endLocation, input[name="end"]').value.strip ? formElement.querySelector('#endLocation, input[name="end"]').value.trim() : '',
            rate: parseFloat(formElement.querySelector('#askingRate, input[name="rate"]').value || 0),
            capacity: parseInt(formElement.querySelector('#capacity, input[name="capacity"]').value || 100),
            weight: parseFloat(formElement.querySelector('#weight, input[name="weight"]').value || 10.0),
            vehicle_type: formElement.querySelector('#vehicleType, select[name="vehicle_type"]')?.value || '53 Dry Van',
            cargo_type: formElement.querySelector('#cargoType, input[name="cargo_type"]')?.value || 'General Freight',
            departure: formElement.querySelector('#departureTime, input[name="departure"]')?.value || new Date().toISOString(),
            arrival: formElement.querySelector('#arrivalTime, input[name="arrival"]')?.value || new Date(Date.now() + 86400000).toISOString(),
            description: formElement.querySelector('#description, textarea[name="description"]')?.value || ''
        };

        if (!payload.start || !payload.end) {
            window.HaulPool.showToast('Please provide both Origin and Destination.', true);
            return;
        }

        window.HaulPool.setButtonLoading(submitBtn, true, 'Publishing Route...');

        try {
            const response = await fetch('/operator/api/trips', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || 'Failed to publish route');

            window.HaulPool.showToast(result.message || 'Route published successfully!');
            setTimeout(() => {
                window.location.href = '/operator/dashboard';
            }, 800);

        } catch (err) {
            window.HaulPool.showToast(err.message, true);
        } finally {
            window.HaulPool.setButtonLoading(submitBtn, false);
        }
    },

    // Update status of an active trip
    updateTripStatus: async function(tripId, newStatus, selectOrBtn) {
        try {
            const response = await fetch(`/operator/api/trips/${tripId}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || 'Failed to update status');

            window.HaulPool.showToast(result.message);
            setTimeout(() => { window.location.reload(); }, 600);
        } catch (err) {
            window.HaulPool.showToast(err.message, true);
        }
    }
};

window.OperatorService = OperatorService;
