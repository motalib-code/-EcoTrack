// ============================================
// EcoTrack — Carbon Footprint Awareness Platform
// Main Application JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initThemeToggle();
    initHeroAnimations();
    initCalculator();
    initDashboard();
    initChartLoader();
    applyImageLazyAttributes();
    initScrollAnimations();
    initCounterAnimations();
});

// ============================================
// NAVIGATION
// ============================================
function initNavigation() {
    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.getElementById('nav-links');

    // Scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Mobile toggle
    navToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        navToggle.classList.toggle('active');
    });

    // Close mobile menu on link click
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            navToggle.classList.remove('active');
        });
    });

    // Active link tracking
    const sections = document.querySelectorAll('section[id]');
    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY + 100;
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            const navLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
            if (navLink) {
                if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                    navLink.classList.add('active');
                } else {
                    navLink.classList.remove('active');
                }
            }
        });
    });
}

// ============================================
// HERO ANIMATIONS
// ============================================
function initHeroAnimations() {
    createParticles();
    animateHeroStats();
}

function createParticles() {
    const container = document.getElementById('hero-particles');
    if (!container) return;

    const particleCount = 50;
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 4 + 1}px;
            height: ${Math.random() * 4 + 1}px;
            background: rgba(0, 212, 170, ${Math.random() * 0.5 + 0.1});
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: particleFloat ${Math.random() * 10 + 10}s ease-in-out infinite;
            animation-delay: ${Math.random() * 5}s;
        `;
        container.appendChild(particle);
    }

    // Add particle animation keyframes
    const style = document.createElement('style');
    style.textContent = `
        @keyframes particleFloat {
            0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.3; }
            25% { transform: translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px) scale(1.5); opacity: 0.6; }
            50% { transform: translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px) scale(1); opacity: 0.4; }
            75% { transform: translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px) scale(1.3); opacity: 0.5; }
        }
    `;
    document.head.appendChild(style);
}

function animateHeroStats() {
    const statNumbers = document.querySelectorAll('.hero-stat-number');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.getAttribute('data-target'));
                animateNumber(entry.target, 0, target, 2000);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(stat => observer.observe(stat));
}

function animateNumber(element, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeProgress = 1 - Math.pow(1 - progress, 3); // Ease out cubic
        const current = Math.round(start + range * easeProgress);
        element.textContent = current.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// ============================================
// CALCULATOR
// ============================================
function initCalculator() {
    // Tab switching
    const tabs = document.querySelectorAll('.calc-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetPanel = tab.getAttribute('data-tab');

            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            document.querySelectorAll('.calc-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            document.getElementById(`panel-${targetPanel}`).classList.add('active');
        });
    });

    // Range slider value display
    initRangeSliders();
}

function initRangeSliders() {
    const rangeInputs = [
        { id: 'car-km', suffix: ' km' },
        { id: 'public-transport', suffix: ' hrs' },
        { id: 'flights', suffix: '' },
        { id: 'local-food', suffix: '%' },
        { id: 'streaming', suffix: ' hrs' }
    ];

    rangeInputs.forEach(({ id, suffix }) => {
        const input = document.getElementById(id);
        const display = document.getElementById(`${id}-value`);
        if (input && display) {
            input.addEventListener('input', () => {
                display.textContent = input.value + suffix;
                updateSliderTrack(input);
            });
            updateSliderTrack(input);
        }
    });
}

function updateSliderTrack(slider) {
    const min = parseFloat(slider.min);
    const max = parseFloat(slider.max);
    const value = parseFloat(slider.value);
    const percentage = ((value - min) / (max - min)) * 100;
    slider.style.setProperty('--slider-progress', `${percentage}%`);
}

// ============================================
// CARBON FOOTPRINT CALCULATION
// ============================================
function calculateFootprint() {
    const btn = document.getElementById('calculate-btn');
    btn.classList.add('loading');
    btn.innerHTML = '<span class="spinner"></span><span>Calculating...</span>';

    // Simulate calculation delay for UX
    setTimeout(() => {
        const results = computeEmissions();
        displayResults(results);
        updateDashboardFromResults(results);
        updateInsightsFromResults(results);

        btn.classList.remove('loading');
        btn.innerHTML = '<span>Recalculate</span><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>';
    }, 1500);
}

function computeEmissions() {
    // Transport emissions (kg CO₂ per month)
    const carKm = parseFloat(document.getElementById('car-km').value) || 0;
    const carType = document.getElementById('car-type').value;
    const publicTransport = parseFloat(document.getElementById('public-transport').value) || 0;
    const flights = parseFloat(document.getElementById('flights').value) || 0;

    const carFactors = {
        'petrol': 0.21,
        'diesel': 0.27,
        'hybrid': 0.12,
        'electric': 0.05,
        'none': 0
    };

    const transportEmissions = (carKm * 4.33 * (carFactors[carType] || 0)) +
        (publicTransport * 4.33 * 0.089) +
        (flights * 255 / 12); // Monthly avg from yearly flights

    // Energy emissions
    const electricity = parseFloat(document.getElementById('electricity').value) || 0;
    const gasBill = parseFloat(document.getElementById('gas-bill').value) || 0;
    const renewable = document.getElementById('renewable').value;
    const heating = document.getElementById('heating').value;

    const renewableFactors = { 'none': 1, 'partial': 0.7, 'mostly': 0.3, 'full': 0.05 };
    const heatingFactors = { 'gas': 1, 'electric': 0.8, 'oil': 1.3, 'heatpump': 0.3, 'wood': 0.6 };

    const energyEmissions = ((electricity * 0.92) + (gasBill * 2.1)) *
        (renewableFactors[renewable] || 1) *
        (heatingFactors[heating] || 1);

    // Food emissions
    const diet = document.getElementById('diet').value;
    const foodWaste = document.getElementById('food-waste').value;
    const localFood = parseFloat(document.getElementById('local-food').value) || 0;

    const dietFactors = {
        'heavy-meat': 250,
        'medium-meat': 180,
        'low-meat': 130,
        'pescatarian': 110,
        'vegetarian': 85,
        'vegan': 60
    };

    const wasteFactors = { 'high': 1.3, 'medium': 1.1, 'low': 1, 'none': 0.9 };
    const localFactor = 1 - (localFood / 100) * 0.3;

    const foodEmissions = (dietFactors[diet] || 180) * (wasteFactors[foodWaste] || 1) * localFactor;

    // Lifestyle emissions
    const shopping = parseFloat(document.getElementById('shopping').value) || 0;
    const recycling = document.getElementById('recycling').value;
    const streaming = parseFloat(document.getElementById('streaming').value) || 0;
    const waterUsage = document.getElementById('water-usage').value;

    const recyclingFactors = { 'none': 1.2, 'some': 1, 'most': 0.8, 'all': 0.6 };
    const waterFactors = { 'high': 1.3, 'average': 1, 'conscious': 0.7, 'minimal': 0.5 };

    const lifestyleEmissions = (shopping * 0.5 * (recyclingFactors[recycling] || 1)) +
        (streaming * 30 * 0.036) +
        (waterFactors[waterUsage] || 1) * 20;

    const total = transportEmissions + energyEmissions + foodEmissions + lifestyleEmissions;

    return {
        transport: Math.round(transportEmissions),
        energy: Math.round(energyEmissions),
        food: Math.round(foodEmissions),
        lifestyle: Math.round(lifestyleEmissions),
        total: Math.round(total)
    };
}

function displayResults(results) {
    const placeholder = document.getElementById('results-placeholder');
    const content = document.getElementById('results-content');

    placeholder.classList.add('hidden');
    content.classList.remove('hidden');

    // Animate total
    const totalEl = document.getElementById('result-total');
    animateNumber(totalEl, 0, results.total, 1500);

    // Circular progress (based on 1000kg being maximum/worst)
    const percentage = Math.min((results.total / 1000) * 100, 100);
    const circularEl = document.getElementById('circular-progress');
    setTimeout(() => {
        circularEl.style.setProperty('--progress', `${percentage * 3.6}deg`);
    }, 100);

    // Rating badge
    const ratingBadge = document.getElementById('rating-badge');
    const rating = getRating(results.total);
    ratingBadge.textContent = rating.label;
    ratingBadge.className = `rating-badge rating-${rating.class}`;

    // Breakdown bars
    const maxCategory = Math.max(results.transport, results.energy, results.food, results.lifestyle);

    const breakdowns = [
        { id: 'transport', value: results.transport },
        { id: 'energy', value: results.energy },
        { id: 'food', value: results.food },
        { id: 'lifestyle', value: results.lifestyle }
    ];

    breakdowns.forEach(({ id, value }) => {
        const valueEl = document.getElementById(`breakdown-${id}`);
        const fillEl = document.getElementById(`fill-${id}`);
        valueEl.textContent = `${value} kg`;
        const fillPercent = maxCategory > 0 ? (value / maxCategory) * 100 : 0;
        setTimeout(() => {
            fillEl.style.width = `${fillPercent}%`;
        }, 300);
    });

    // Comparison text
    const compText = document.getElementById('comparison-text');
    const globalAvg = 400; // kg CO₂/month global average approximation
    if (results.total < globalAvg * 0.7) {
        compText.innerHTML = `🌟 <strong>Excellent!</strong> Your footprint is ${Math.round((1 - results.total / globalAvg) * 100)}% below the global average. Keep it up!`;
    } else if (results.total < globalAvg) {
        compText.innerHTML = `👍 <strong>Good job!</strong> Your footprint is ${Math.round((1 - results.total / globalAvg) * 100)}% below the global average. Small changes can make it even better.`;
    } else {
        compText.innerHTML = `⚠️ Your footprint is ${Math.round((results.total / globalAvg - 1) * 100)}% above the global average. Check out our recommendations to reduce it!`;
    }

    // Smooth scroll to results on mobile
    if (window.innerWidth < 768) {
        document.getElementById('calculator-results').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function getRating(total) {
    if (total < 150) return { label: '🌟 Excellent', class: 'excellent' };
    if (total < 250) return { label: '✅ Good', class: 'good' };
    if (total < 400) return { label: '⚡ Average', class: 'average' };
    if (total < 600) return { label: '⚠️ High', class: 'high' };
    return { label: '🔴 Very High', class: 'very-high' };
}

// ============================================
// DASHBOARD
// ============================================
function initDashboard() {
    // Set initial demo values with animation
    const demoData = {
        transport: 145,
        energy: 198,
        food: 167,
        total: 510
    };

    setTimeout(() => {
        animateNumber(document.getElementById('stat-transport-value'), 0, demoData.transport, 2000);
        animateNumber(document.getElementById('stat-energy-value'), 0, demoData.energy, 2000);
        animateNumber(document.getElementById('stat-food-value'), 0, demoData.food, 2000);
        animateNumber(document.getElementById('stat-total-value'), 0, demoData.total, 2500);
    }, 500);
}

function updateDashboardFromResults(results) {
    animateNumber(document.getElementById('stat-transport-value'), 0, results.transport, 1500);
    animateNumber(document.getElementById('stat-energy-value'), 0, results.energy, 1500);
    animateNumber(document.getElementById('stat-food-value'), 0, results.food, 1500);
    animateNumber(document.getElementById('stat-total-value'), 0, results.total, 2000);

    // Update charts
    updateCharts(results);
}

// ============================================
// INSIGHTS
// ============================================
function updateInsightsFromResults(results) {
    const maxPossible = { transport: 500, energy: 400, food: 300, lifestyle: 300 };

    const scores = {
        transport: Math.max(0, Math.round(100 - (results.transport / maxPossible.transport) * 100)),
        energy: Math.max(0, Math.round(100 - (results.energy / maxPossible.energy) * 100)),
        food: Math.max(0, Math.round(100 - (results.food / maxPossible.food) * 100)),
        lifestyle: Math.max(0, Math.round(100 - (results.lifestyle / maxPossible.lifestyle) * 100))
    };

    // Update scores
    Object.keys(scores).forEach(key => {
        const scoreEl = document.getElementById(`score-${key}`);
        if (scoreEl) {
            animateNumber(scoreEl, 0, scores[key], 1500);
        }

        // Update progress bar
        const card = document.getElementById(`insight-${key}`);
        if (card) {
            const progressFill = card.querySelector('.progress-fill');
            if (progressFill) {
                progressFill.style.setProperty('--progress', `${scores[key]}%`);
            }
        }
    });

    // Update insight descriptions
    updateInsightDescriptions(results, scores);

    // Update overall score
    const overallScore = Math.round((scores.transport + scores.energy + scores.food + scores.lifestyle) / 4);
    animateNumber(document.getElementById('overall-score'), 0, overallScore, 2000);

    const overallProgress = document.getElementById('overall-progress');
    if (overallProgress) {
        overallProgress.style.setProperty('--progress', `${overallScore * 3.6}deg`);
    }

    // Update overall description
    const overallDesc = document.getElementById('overall-desc');
    if (overallScore >= 80) {
        overallDesc.textContent = "Outstanding! You're a sustainability champion! Your lifestyle choices are significantly reducing your environmental impact. Keep inspiring others! 🌟";
    } else if (overallScore >= 60) {
        overallDesc.textContent = "You're making good progress! With a few targeted changes in energy and diet, you could reduce your carbon footprint by up to 30%. Keep up the great work! 🌿";
    } else if (overallScore >= 40) {
        overallDesc.textContent = "There's room for improvement. Focus on the categories with lower scores first — small changes in transportation and energy can make a big difference! 💪";
    } else {
        overallDesc.textContent = "Time to take action! Your carbon footprint is significantly above average. Check out our recommendations — even small daily changes can dramatically reduce your impact. 🌍";
    }
}

function updateInsightDescriptions(results, scores) {
    const descriptions = {
        transport: scores.transport >= 70
            ? "Great job keeping your transport emissions low! Consider walking or cycling for short trips to maintain this excellent score."
            : scores.transport >= 40
                ? "Your driving habits contribute moderately to emissions. Consider carpooling or using public transit 2 more days per week."
                : "Transport is your biggest challenge. Try remote work days, carpooling, or switching to an electric vehicle.",
        energy: scores.energy >= 70
            ? "Your energy usage is efficient! Consider switching to 100% renewable energy for an even better score."
            : scores.energy >= 40
                ? "Your energy usage is above average. Switching to LED bulbs and smart thermostats could reduce consumption by 25%."
                : "Your energy consumption is high. Prioritize insulation, energy-efficient appliances, and renewable energy sources.",
        food: scores.food >= 70
            ? "Excellent dietary choices! Your plant-forward diet significantly reduces your carbon footprint."
            : scores.food >= 40
                ? "Reducing red meat by one meal per week could save approximately 50 kg of CO₂ per month. Try plant-based alternatives!"
                : "Your food choices have a significant carbon impact. Consider gradually shifting to more plant-based meals and reducing food waste.",
        lifestyle: scores.lifestyle >= 70
            ? "Great recycling habits! Consider reducing fast fashion purchases and choosing second-hand items when possible."
            : scores.lifestyle >= 40
                ? "You can improve by reducing shopping, increasing recycling, and being more mindful of water consumption."
                : "Focus on reducing consumption, recycling more, and choosing sustainable products. Every small action counts!"
    };

    Object.keys(descriptions).forEach(key => {
        const card = document.getElementById(`insight-${key}`);
        if (card) {
            const desc = card.querySelector('.insight-desc');
            if (desc) desc.textContent = descriptions[key];
        }
    });
}

// ============================================
// CHARTS
// ============================================
let breakdownChart = null;
let trendChart = null;
let ChartConstructor = null;
let chartInitPromise = null;
let pendingChartResults = null;

function initChartLoader() {
    const dashboardSection = document.getElementById('dashboard');
    if (!dashboardSection) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                initializeChartsWhenNeeded();
                observer.disconnect();
            }
        });
    }, { rootMargin: '250px 0px', threshold: 0.1 });

    observer.observe(dashboardSection);
}

async function initializeChartsWhenNeeded() {
    if (breakdownChart || trendChart) return;
    if (!chartInitPromise) {
        chartInitPromise = (async () => {
            try {
                await loadChartLibrary();
                initCharts();
                if (pendingChartResults) {
                    applyChartUpdates(pendingChartResults);
                }
            } catch (error) {
                console.error('Unable to load chart library:', error);
            } finally {
                chartInitPromise = null;
            }
        })();
    }

    await chartInitPromise;
}

async function loadChartLibrary() {
    if (ChartConstructor) return;

    const chartModule = await import('https://cdn.jsdelivr.net/npm/chart.js@4.4.0/+esm');
    ChartConstructor = chartModule.Chart;
}

function initCharts() {
    if (!ChartConstructor) return;

    ChartConstructor.defaults.color = '#94a3b8';
    ChartConstructor.defaults.font.family = 'Inter, sans-serif';
    ChartConstructor.defaults.plugins.legend.labels.padding = 16;
    ChartConstructor.defaults.plugins.legend.labels.usePointStyle = true;

    // Breakdown Doughnut Chart
    const breakdownCtx = document.getElementById('chart-breakdown');
    if (breakdownCtx) {
        breakdownChart = new ChartConstructor(breakdownCtx, {
            type: 'doughnut',
            data: {
                labels: ['Transport', 'Energy', 'Food', 'Lifestyle'],
                datasets: [{
                    data: [145, 198, 167, 70],
                    backgroundColor: [
                        'rgba(0, 212, 170, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(45, 212, 191, 0.8)',
                        'rgba(167, 139, 250, 0.8)'
                    ],
                    borderColor: [
                        'rgba(0, 212, 170, 1)',
                        'rgba(245, 158, 11, 1)',
                        'rgba(45, 212, 191, 1)',
                        'rgba(167, 139, 250, 1)'
                    ],
                    borderWidth: 2,
                    hoverOffset: 12,
                    spacing: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: { size: 13, weight: '500' }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(19, 28, 24, 0.95)',
                        titleFont: { size: 14, weight: '600' },
                        bodyFont: { size: 13 },
                        padding: 12,
                        borderColor: 'rgba(0, 212, 170, 0.3)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: (context) => ` ${context.label}: ${context.parsed} kg CO₂`
                        }
                    }
                }
            }
        });
    }

    // Trend Line Chart
    const trendCtx = document.getElementById('chart-trend');
    if (trendCtx) {
        const gradient = trendCtx.getContext('2d').createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(0, 212, 170, 0.3)');
        gradient.addColorStop(1, 'rgba(0, 212, 170, 0)');

        trendChart = new ChartConstructor(trendCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Total CO₂ (kg)',
                    data: [620, 580, 550, 530, 510, 480],
                    fill: true,
                    backgroundColor: gradient,
                    borderColor: 'rgba(0, 212, 170, 1)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgba(0, 212, 170, 1)',
                    pointBorderColor: '#131c18',
                    pointBorderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 9,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(148, 163, 184, 0.08)',
                            drawBorder: false
                        },
                        ticks: { font: { size: 12, weight: '500' } }
                    },
                    y: {
                        grid: {
                            color: 'rgba(148, 163, 184, 0.08)',
                            drawBorder: false
                        },
                        ticks: {
                            font: { size: 12, weight: '500' },
                            callback: (val) => val + ' kg'
                        },
                        beginAtZero: false
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(19, 28, 24, 0.95)',
                        titleFont: { size: 14, weight: '600' },
                        bodyFont: { size: 13 },
                        padding: 12,
                        borderColor: 'rgba(0, 212, 170, 0.3)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: (context) => ` ${context.parsed.y} kg CO₂`
                        }
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                }
            }
        });
    }
}

function updateCharts(results) {
    pendingChartResults = results;

    if (!breakdownChart && !trendChart) {
        initializeChartsWhenNeeded();
        return;
    }

    applyChartUpdates(results);
}

function applyChartUpdates(results) {
    if (breakdownChart) {
        breakdownChart.data.datasets[0].data = [
            results.transport,
            results.energy,
            results.food,
            results.lifestyle
        ];
        breakdownChart.update('active');
    }

    if (trendChart) {
        // Push current total to trend and shift
        const data = trendChart.data.datasets[0].data;
        data.push(results.total);
        if (data.length > 6) data.shift();

        const labels = trendChart.data.labels;
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const currentMonth = new Date().getMonth();
        labels.push(months[currentMonth]);
        if (labels.length > 6) labels.shift();

        trendChart.update('active');
    }
}

// ============================================
// SCROLL ANIMATIONS
// ============================================
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll(
        '.stat-card, .chart-card, .insight-card, .rec-card, .overall-score-card, .section-header'
    );

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animate-in');
                }, index * 100);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    animatedElements.forEach(el => {
        el.classList.add('animate-prepare');
        observer.observe(el);
    });
}

// ============================================
// COUNTER ANIMATIONS (for Insight scores)
// ============================================
function initCounterAnimations() {
    const scoreElements = document.querySelectorAll('.score-value');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.textContent);
                animateNumber(entry.target, 0, target, 1500);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    scoreElements.forEach(el => observer.observe(el));

    // Overall circular progress
    const overallProgress = document.getElementById('overall-progress');
    if (overallProgress) {
        const overallObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const score = parseInt(document.getElementById('overall-score').textContent) || 69;
                    overallProgress.style.setProperty('--progress', `${score * 3.6}deg`);
                    overallObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });
        overallObserver.observe(overallProgress);
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function applyImageLazyAttributes() {
    document.querySelectorAll('img').forEach(img => {
        img.setAttribute('loading', 'lazy');
        img.setAttribute('decoding', 'async');
    });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Make calculateFootprint available globally
window.calculateFootprint = calculateFootprint;

// ============================================
// THEME TOGGLE
// ============================================
function initThemeToggle() {
    const toggleBtn = document.getElementById('theme-toggle');
    const iconLight = document.querySelector('.theme-icon-light');
    const iconDark = document.querySelector('.theme-icon-dark');
    
    if (!toggleBtn) return;
    
    const savedTheme = localStorage.getItem('eco-theme');
    const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
    
    if (savedTheme === 'light' || (!savedTheme && prefersLight)) {
        document.documentElement.setAttribute('data-theme', 'light');
        iconLight.style.display = 'none';
        iconDark.style.display = 'inline';
    } else {
        document.documentElement.removeAttribute('data-theme');
        iconLight.style.display = 'inline';
        iconDark.style.display = 'none';
    }
    
    toggleBtn.addEventListener('click', () => {
        const isLight = document.documentElement.getAttribute('data-theme') === 'light';
        
        if (isLight) {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('eco-theme', 'dark');
            iconLight.style.display = 'inline';
            iconDark.style.display = 'none';
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('eco-theme', 'light');
            iconLight.style.display = 'none';
            iconDark.style.display = 'inline';
        }
    });
}
