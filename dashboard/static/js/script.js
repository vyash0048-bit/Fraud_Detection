document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('scoring-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.scanning-loader');
    
    const resultsContainer = document.getElementById('results-container');
    const emptyState = resultsContainer.querySelector('.empty-state');
    const scoringCard = resultsContainer.querySelector('.scoring-card');
    
    // Result elements
    const riskScoreEl = document.getElementById('risk-score');
    const scoreCircle = document.getElementById('score-circle');
    const fraudProbEl = document.getElementById('fraud-prob');
    const riskLevelEl = document.getElementById('risk-level');
    const txIdEl = document.getElementById('result-tx-id');
    const decisionBadge = document.getElementById('decision-badge');

    // KPI Elements
    const kpiMetrics = document.getElementById('header-metrics');
    const kpiAuc = document.getElementById('kpi-auc');
    const kpiBrier = document.getElementById('kpi-brier');
    const kpiPrecision = document.getElementById('kpi-precision');

    // Log Element
    const logBody = document.getElementById('log-body');
    const txHistory = [];

    // Load Metrics on start
    async function loadMetrics() {
        try {
            const res = await fetch('/metrics');
            if (res.ok) {
                const data = await res.json();
                if (!data.error) {
                    kpiAuc.textContent = data.roc_auc.toFixed(3);
                    kpiBrier.textContent = data.brier_score_calibrated.toFixed(3);
                    kpiPrecision.textContent = data.precision_at_best.toFixed(3);
                    kpiMetrics.style.opacity = 1;
                }
            }
        } catch (e) {
            console.warn("Metrics not available yet.");
        }
    }
    loadMetrics();

    function updateLogTable(result, amount) {
        txHistory.unshift({ ...result, amount });
        if (txHistory.length > 5) txHistory.pop(); // keep last 5
        
        logBody.innerHTML = txHistory.map(tx => {
            let badgeClass = 'pending';
            if (tx.decision === 'APPROVE') badgeClass = 'approve';
            if (tx.decision === 'REVIEW') badgeClass = 'review';
            if (tx.decision === 'DECLINE') badgeClass = 'decline';
            
            return `
                <tr>
                    <td class="mono">${tx.transaction_id.substring(0,8)}...</td>
                    <td>$${amount ? amount.toFixed(2) : '0.00'}</td>
                    <td class="mono">${(tx.fraud_probability * 100).toFixed(2)}%</td>
                    <td class="mono">${tx.risk_score}</td>
                    <td><span class="badge ${badgeClass}">${tx.decision}</span></td>
                </tr>
            `;
        }).join('');
    }

    // Count Up Animation
    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        loader.style.display = 'flex';
        
        try {
            const txIdInput = document.getElementById('tx_id').value.trim();
            const jsonInput = document.getElementById('features_json').value;
            
            let features;
            try {
                features = JSON.parse(jsonInput);
            } catch (err) {
                alert("Invalid JSON payload. Please check your syntax.");
                throw err;
            }
            
            const payload = { features: features };
            if (txIdInput) payload.transaction_id = txIdInput;
            
            await new Promise(r => setTimeout(r, 600)); // aesthetic delay
            
            const response = await fetch('/score', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                alert(`Error: ${result.error || 'Failed to score transaction'}`);
                return;
            }
            
            // Show Results
            resultsContainer.classList.remove('empty');
            emptyState.style.display = 'none';
            scoringCard.style.display = 'flex';
            
            // Score Animation
            const targetScore = result.risk_score;
            animateValue(riskScoreEl, 0, targetScore, 1000);
            
            // SVG Gauge Animation
            scoreCircle.setAttribute('stroke-dasharray', `${targetScore}, 100`);
            
            let strokeColor = '#10b981'; // Green
            if (result.decision === 'REVIEW') strokeColor = '#f59e0b'; // Yellow
            if (result.decision === 'DECLINE') strokeColor = '#ef4444'; // Red
            scoreCircle.style.stroke = strokeColor;
            
            // Update Text
            fraudProbEl.textContent = (result.fraud_probability * 100).toFixed(2) + '%';
            riskLevelEl.textContent = result.risk_level.replace('_', ' ');
            txIdEl.textContent = result.transaction_id.length > 15 ? 
                result.transaction_id.substring(0, 15) + '...' : result.transaction_id;
            
            // Badge
            decisionBadge.textContent = result.decision;
            decisionBadge.className = 'badge'; // reset
            if (result.decision === 'APPROVE') decisionBadge.classList.add('approve');
            else if (result.decision === 'REVIEW') decisionBadge.classList.add('review');
            else if (result.decision === 'DECLINE') decisionBadge.classList.add('decline');
            
            // Update Log
            updateLogTable(result, features.TransactionAmt || features.transaction_amount || 0);
            
        } catch (error) {
            console.error(error);
        } finally {
            submitBtn.disabled = false;
            btnText.style.display = 'block';
            loader.style.display = 'none';
        }
    });
});
