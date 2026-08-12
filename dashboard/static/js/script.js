document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('scoring-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.loader');
    
    const resultsContainer = document.getElementById('results-container');
    const emptyState = resultsContainer.querySelector('.empty-state');
    const scoringCard = resultsContainer.querySelector('.scoring-card');
    
    // Result elements
    const riskScoreEl = document.getElementById('risk-score');
    const fraudProbEl = document.getElementById('fraud-prob');
    const riskLevelEl = document.getElementById('risk-level');
    const txIdEl = document.getElementById('result-tx-id');
    const decisionBadge = document.getElementById('decision-badge');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // UI Loading State
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        loader.style.display = 'block';
        
        try {
            const txIdInput = document.getElementById('tx_id').value.trim();
            const jsonInput = document.getElementById('features_json').value;
            
            // Parse JSON
            let features;
            try {
                features = JSON.parse(jsonInput);
            } catch (err) {
                alert("Invalid JSON payload. Please check your syntax.");
                throw err;
            }
            
            const payload = {
                features: features
            };
            if (txIdInput) {
                payload.transaction_id = txIdInput;
            }
            
            // API Call to Flask Proxy
            const response = await fetch('/score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                alert(`Error: ${result.error || 'Failed to score transaction'}`);
                return;
            }
            
            // Update UI
            resultsContainer.classList.remove('empty');
            emptyState.style.display = 'none';
            scoringCard.style.display = 'block';
            
            // Populate Data
            riskScoreEl.textContent = result.risk_score;
            fraudProbEl.textContent = (result.fraud_probability * 100).toFixed(2) + '%';
            riskLevelEl.textContent = result.risk_level.replace('_', ' ');
            txIdEl.textContent = result.transaction_id.substring(0, 8) + '...';
            
            // Update Badge Color based on decision
            decisionBadge.textContent = result.decision;
            decisionBadge.className = 'badge'; // reset
            if (result.decision === 'APPROVE') decisionBadge.classList.add('approve');
            else if (result.decision === 'REVIEW') decisionBadge.classList.add('review');
            else if (result.decision === 'DECLINE') decisionBadge.classList.add('decline');
            
        } catch (error) {
            console.error(error);
        } finally {
            // Restore UI
            submitBtn.disabled = false;
            btnText.style.display = 'block';
            loader.style.display = 'none';
        }
    });
});
