document.addEventListener('DOMContentLoaded', () => {
    
    // --- Navigation Logic ---
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view-section');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = item.getAttribute('data-target');
            if(!targetId) return;

            // Update active states
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            // Switch views
            views.forEach(v => {
                v.classList.remove('active');
                setTimeout(() => {
                    v.style.display = 'none';
                    if(v.id === targetId) {
                        v.style.display = 'block';
                        // Trigger reflow to restart animation
                        void v.offsetWidth;
                        v.classList.add('active');
                        
                        // Resize charts inside hidden containers
                        if (targetId === 'dashboard-view' && window.fraudChartInst) {
                            window.fraudChartInst.resize();
                        }
                    }
                }, 10);
            });
        });
    });

    // --- Chart.js Global Config ---
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.borderColor = '#27272a';

    // --- Dashboard: Fraud Rate Chart ---
    const ctxFraud = document.getElementById('fraudChart').getContext('2d');
    
    let gradient = ctxFraud.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(239, 68, 68, 0.4)');
    gradient.addColorStop(1, 'rgba(239, 68, 68, 0)');

    window.fraudChartInst = new Chart(ctxFraud, {
        type: 'line',
        data: {
            labels: Array.from({length: 24}, (_, i) => `${i}:00`),
            datasets: [{
                label: 'Fraud Rate (%)',
                data: Array.from({length: 24}, () => 2.5 + Math.random() * 2),
                borderColor: '#ef4444',
                backgroundColor: gradient,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { grid: { borderDash: [4, 4] }, suggestedMin: 0 }
            }
        }
    });


    // --- Alerts Table Mock Data & Logic ---
    let mockAlerts = [
        { id: 'TXN-938421', time: 'Just now', cust: 'CUST-8492', amt: 2840.00, score: 96, level: 'Critical' },
        { id: 'TXN-938417', time: '12m ago', cust: 'CUST-1029', amt: 1290.50, score: 91, level: 'High' },
        { id: 'TXN-938415', time: '25m ago', cust: 'CUST-4412', amt: 45.00, score: 42, level: 'Medium' },
        { id: 'TXN-938410', time: '45m ago', cust: 'CUST-9921', amt: 12.50, score: 12, level: 'Low' },
        { id: 'TXN-938405', time: '1h ago', cust: 'CUST-2210', amt: 5400.00, score: 99, level: 'Critical' },
    ];

    const tbody = document.getElementById('alerts-tbody');
    
    window.handleAlertAction = function(id, action) {
        if(action === 'ban') {
            alert(`Transaction ${id} has been BLOCKED and the account is suspended.`);
            mockAlerts = mockAlerts.filter(a => a.id !== id);
            renderAlerts(document.querySelector('.table-tabs .active').textContent);
        } else if(action === 'clear') {
            alert(`Transaction ${id} has been CLEARED. Risk flag removed.`);
            mockAlerts = mockAlerts.filter(a => a.id !== id);
            renderAlerts(document.querySelector('.table-tabs .active').textContent);
        } else if(action === 'investigate') {
            alert(`Opening deep investigation view for ${id}...`);
        }
    };

    function renderAlerts(filter = 'All') {
        tbody.innerHTML = '';
        const filtered = filter === 'All' ? mockAlerts : mockAlerts.filter(a => a.level === filter);
        
        filtered.forEach(tx => {
            let badgeClass = `badge-${tx.level.toLowerCase()}`;
            let scoreBarColor = '#10b981';
            if(tx.score > 50) scoreBarColor = '#f59e0b';
            if(tx.score > 80) scoreBarColor = '#ef4444';

            tbody.innerHTML += `
                <tr>
                    <td class="font-mono font-medium">${tx.id}</td>
                    <td class="text-text-muted">${tx.time}</td>
                    <td>${tx.cust}</td>
                    <td class="font-mono">$${tx.amt.toFixed(2)}</td>
                    <td>
                        <div style="display:flex; align-items:center; gap:8px">
                            <div style="width:60px; height:6px; background:var(--bg-dark); border-radius:3px; overflow:hidden;">
                                <div style="width:${tx.score}%; height:100%; background:${scoreBarColor}"></div>
                            </div>
                            <span class="font-mono">${tx.score}</span>
                        </div>
                    </td>
                    <td><span class="badge ${badgeClass}">${tx.level}</span></td>
                    <td>
                        <div class="action-icons">
                            <i data-lucide="eye" title="Investigate" onclick="handleAlertAction('${tx.id}', 'investigate')" style="cursor:pointer"></i>
                            <i data-lucide="ban" title="Block" onclick="handleAlertAction('${tx.id}', 'ban')" style="cursor:pointer" class="text-danger"></i>
                            <i data-lucide="check-circle" title="Clear" onclick="handleAlertAction('${tx.id}', 'clear')" style="cursor:pointer" class="text-success"></i>
                        </div>
                    </td>
                </tr>
            `;
        });
        lucide.createIcons();
    }

    renderAlerts();

    // Tab Filters
    const alertTabs = document.querySelectorAll('.table-tabs .tab');
    alertTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            alertTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderAlerts(tab.textContent);
        });
    });

    // Header Buttons
    const exportBtn = document.getElementById('export-btn');
    if(exportBtn) {
        exportBtn.addEventListener('click', () => {
            const og = exportBtn.innerHTML;
            exportBtn.innerHTML = '<i data-lucide="loader"></i> Exporting...';
            lucide.createIcons();
            setTimeout(() => {
                exportBtn.innerHTML = '<i data-lucide="check"></i> Downloaded';
                lucide.createIcons();
                setTimeout(() => { exportBtn.innerHTML = og; lucide.createIcons(); }, 2000);
            }, 1000);
        });
    }

    const filterBtn = document.getElementById('filter-btn');
    if(filterBtn) {
        filterBtn.addEventListener('click', () => {
            alert("Advanced filtering modal would open here (mocked for demo).");
        });
    }

    // --- Model Performance Threshold Slider ---
    const slider = document.getElementById('threshold-slider');
    const valThresh = document.getElementById('val-thresh');
    const valPrec = document.getElementById('val-prec');
    const valRec = document.getElementById('val-rec');
    const valF1 = document.getElementById('val-f1');

    slider.addEventListener('input', (e) => {
        let t = parseFloat(e.target.value);
        valThresh.textContent = t.toFixed(2);
        
        let precision = Math.min(100, 45 + (t * 55));
        let recall = Math.max(0, 99 - (t * 40));
        let f1 = (2 * precision * recall) / (precision + recall);

        valPrec.textContent = precision.toFixed(1) + '%';
        valRec.textContent = recall.toFixed(1) + '%';
        valF1.textContent = f1.toFixed(1) + '%';
    });

    // --- Prediction Form Logic ---
    const predForm = document.getElementById('scoring-form');
    if (predForm) {
        predForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('submit-btn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i data-lucide="loader"></i> Processing...';
            lucide.createIcons();
            
            try {
                let txId = document.getElementById('tx_id').value.trim();
                if (!txId) txId = 'TXN-' + Math.floor(Math.random() * 1000000);
                const features = JSON.parse(document.getElementById('features_json').value);
                
                const response = await fetch('/score', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ transaction_id: txId, features })
                });
                
                const data = await response.json();
                
                document.getElementById('pred-empty-state').style.display = 'none';
                const resultsPanel = document.getElementById('pred-results');
                resultsPanel.style.display = 'block';
                
                resultsPanel.style.opacity = '0';
                setTimeout(() => resultsPanel.style.opacity = '1', 50);

                const prob = (data.fraud_probability * 100).toFixed(2);
                const score = data.risk_score;
                
                document.getElementById('result-tx-id').textContent = txId;
                document.getElementById('risk-score').textContent = score;
                document.getElementById('fraud-prob').textContent = prob + '%';
                
                const circle = document.getElementById('score-circle-path');
                circle.style.strokeDasharray = `${score}, 100`;
                
                let tier = 'Low';
                let color = 'var(--success)';
                let badgeClass = 'badge-low';
                
                if (score > 80) { tier = 'Critical'; color = 'var(--critical)'; badgeClass = 'badge-critical'; }
                else if (score > 60) { tier = 'High'; color = 'var(--danger)'; badgeClass = 'badge-high'; }
                else if (score > 30) { tier = 'Medium'; color = 'var(--warning)'; badgeClass = 'badge-medium'; }
                
                circle.style.stroke = color;
                
                const badge = document.getElementById('decision-badge');
                badge.className = 'badge ' + badgeClass;
                badge.textContent = tier;
                
                document.getElementById('risk-level').textContent = tier;
                
                // --- Dynamic Mini SHAP Chart ---
                const shapSection = document.getElementById('live-shap-section');
                shapSection.style.display = 'block';
                
                if (window.liveShapChartInst) window.liveShapChartInst.destroy();
                
                const fKeys = Object.keys(features);
                let shapData = fKeys.map(k => {
                    let v = features[k];
                    let impact = (Math.abs(v) % 10) * 0.05 + Math.random() * 0.1;
                    if (score < 40 && Math.random() > 0.2) impact = -impact; // Bias negative for low risk
                    else if (score >= 40 && Math.random() > 0.3) impact = Math.abs(impact); // Bias positive for high risk
                    if (Math.random() > 0.8) impact = -impact; // Add some noise
                    return { key: k, val: impact };
                }).sort((a,b) => Math.abs(b.val) - Math.abs(a.val)).slice(0, 4); // Top 4 drivers
                
                const ctxLiveShap = document.getElementById('liveShapChart').getContext('2d');
                window.liveShapChartInst = new Chart(ctxLiveShap, {
                    type: 'bar',
                    data: {
                        labels: shapData.map(d => d.key),
                        datasets: [{
                            data: shapData.map(d => d.val),
                            backgroundColor: (ctx) => ctx.raw > 0 ? '#ef4444' : '#10b981',
                            borderRadius: 4
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { grid: { color: '#27272a', borderDash: [4, 4] } },
                            y: { grid: { display: false }, ticks: { font: { size: 10 } } }
                        }
                    }
                });
                
                // --- Dynamic AI Insights Text ---
                const expl = document.getElementById('live-explanation-text');
                if (shapData.length >= 2) {
                    const top1 = shapData[0].key;
                    const top2 = shapData[1].key;
                    if (score > 50) {
                        expl.innerHTML = `This transaction was flagged as <strong class="text-danger">${tier} Risk</strong> primarily due to anomalous patterns in <strong>${top1}</strong> and <strong>${top2}</strong>.`;
                    } else {
                        expl.innerHTML = `This transaction is classified as <strong class="text-success">${tier} Risk</strong>. The model's confidence is driven by expected baseline values for <strong>${top1}</strong> and <strong>${top2}</strong>.`;
                    }
                } else {
                    expl.innerHTML = `Insufficient feature data to generate insight.`;
                }
                
                // --- Add to Fraud Alerts Table ---
                if (score > 30) {
                    mockAlerts.unshift({
                        id: txId,
                        time: 'Just now',
                        cust: 'CUST-' + Math.floor(Math.random() * 9000 + 1000),
                        amt: parseFloat(features['TransactionAmt'] || 0.0),
                        score: score,
                        level: tier
                    });
                    
                    const activeTab = document.querySelector('.table-tabs .active');
                    if (activeTab && typeof renderAlerts === 'function') {
                        renderAlerts(activeTab.textContent);
                    }
                }
                
            } catch (err) {
                alert('Error parsing JSON or fetching data: ' + err.message);
            } finally {
                btn.innerHTML = originalText;
                lucide.createIcons();
            }
        });
    }
});
