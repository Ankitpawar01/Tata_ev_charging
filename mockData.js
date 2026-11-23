/**
 * Tata Power EV Charging Network Expansion & Revenue Analytics
 * Data Engine & Calculations Module — Indian EV Infrastructure Analytics
 * Complete Indian Footprint: 28 States & 5 major UTs (70 Cities)
 */

(function () {
  const regions = {
    "North": ["Delhi", "Uttar Pradesh", "Haryana", "Punjab", "Uttarakhand", "Himachal Pradesh", "Jammu & Kashmir", "Ladakh", "Chandigarh"],
    "West": ["Maharashtra", "Gujarat", "Rajasthan", "Goa"],
    "South": ["Karnataka", "Tamil Nadu", "Telangana", "Kerala", "Andhra Pradesh", "Puducherry"],
    "East": ["West Bengal", "Bihar", "Odisha", "Jharkhand", "Assam", "Sikkim", "Tripura", "Meghalaya", "Manipur", "Mizoram", "Nagaland", "Arunachal Pradesh"],
    "Central": ["Madhya Pradesh", "Chhattisgarh"]
  };

  const states = Object.keys(regions).reduce((acc, reg) => {
    return acc.concat(regions[reg]);
  }, []);

  // Base configurations for 70 cities across 33 states/UTs
  const baseCities = [
    // Maharashtra
    { city: "Mumbai", state: "Maharashtra", region: "West", evCount: 18500, stations: 110, demandFactor: 1.25, avgCost: 1500000 },
    { city: "Pune", state: "Maharashtra", region: "West", evCount: 9200, stations: 48, demandFactor: 1.15, avgCost: 1200000 },
    { city: "Nagpur", state: "Maharashtra", region: "West", evCount: 3100, stations: 12, demandFactor: 0.90, avgCost: 1100000 },
    { city: "Nashik", state: "Maharashtra", region: "West", evCount: 2200, stations: 8, demandFactor: 0.85, avgCost: 1000000 },
    { city: "Thane", state: "Maharashtra", region: "West", evCount: 4500, stations: 20, demandFactor: 1.10, avgCost: 1200000 },
    
    // Delhi
    { city: "New Delhi", state: "Delhi", region: "North", evCount: 22000, stations: 140, demandFactor: 1.30, avgCost: 1600000 },
    { city: "Dwarka", state: "Delhi", region: "North", evCount: 6800, stations: 32, demandFactor: 1.05, avgCost: 1200000 },
    { city: "Rohini", state: "Delhi", region: "North", evCount: 5200, stations: 24, demandFactor: 0.95, avgCost: 1200000 },
    { city: "Saket", state: "Delhi", region: "North", evCount: 4800, stations: 28, demandFactor: 1.12, avgCost: 1400000 },

    // Karnataka
    { city: "Bengaluru", state: "Karnataka", region: "South", evCount: 24500, stations: 155, demandFactor: 1.35, avgCost: 1600000 },
    { city: "Mysuru", state: "Karnataka", region: "South", evCount: 2800, stations: 15, demandFactor: 0.95, avgCost: 1100000 },
    { city: "Hubli", state: "Karnataka", region: "South", evCount: 1600, stations: 6, demandFactor: 0.80, avgCost: 1000000 },
    { city: "Mangaluru", state: "Karnataka", region: "South", evCount: 1900, stations: 8, demandFactor: 0.90, avgCost: 1100000 },

    // Tamil Nadu
    { city: "Chennai", state: "Tamil Nadu", region: "South", evCount: 14000, stations: 82, demandFactor: 1.20, avgCost: 1400000 },
    { city: "Coimbatore", state: "Tamil Nadu", region: "South", evCount: 4800, stations: 22, demandFactor: 1.05, avgCost: 1150000 },
    { city: "Madurai", state: "Tamil Nadu", region: "South", evCount: 2100, stations: 8, demandFactor: 0.88, avgCost: 1000000 },
    { city: "Salem", state: "Tamil Nadu", region: "South", evCount: 1700, stations: 6, demandFactor: 0.80, avgCost: 1000000 },

    // Telangana
    { city: "Hyderabad", state: "Telangana", region: "South", evCount: 16800, stations: 98, demandFactor: 1.28, avgCost: 1500000 },
    { city: "Warangal", state: "Telangana", region: "South", evCount: 2200, stations: 7, demandFactor: 0.85, avgCost: 1000000 },
    { city: "Nizamabad", state: "Telangana", region: "South", evCount: 1100, stations: 3, demandFactor: 0.75, avgCost: 950000 },

    // Uttar Pradesh
    { city: "Lucknow", state: "Uttar Pradesh", region: "North", evCount: 7500, stations: 35, demandFactor: 1.00, avgCost: 1200000 },
    { city: "Noida", state: "Uttar Pradesh", region: "North", evCount: 8900, stations: 52, demandFactor: 1.18, avgCost: 1300000 },
    { city: "Ghaziabad", state: "Uttar Pradesh", region: "North", evCount: 6100, stations: 26, demandFactor: 0.98, avgCost: 1200000 },
    { city: "Kanpur", state: "Uttar Pradesh", region: "North", evCount: 3900, stations: 14, demandFactor: 0.90, avgCost: 1100000 },
    { city: "Varanasi", state: "Uttar Pradesh", region: "North", evCount: 2800, stations: 9, demandFactor: 0.88, avgCost: 1050000 },

    // Gujarat
    { city: "Ahmedabad", state: "Gujarat", region: "West", evCount: 11500, stations: 64, demandFactor: 1.15, avgCost: 1350000 },
    { city: "Surat", state: "Gujarat", region: "West", evCount: 7800, stations: 38, demandFactor: 1.10, avgCost: 1300000 },
    { city: "Vadodara", state: "Gujarat", region: "West", evCount: 3400, stations: 15, demandFactor: 0.92, avgCost: 1100000 },
    { city: "Rajkot", state: "Gujarat", region: "West", evCount: 2600, stations: 10, demandFactor: 0.85, avgCost: 1000000 },

    // West Bengal
    { city: "Kolkata", state: "West Bengal", region: "East", evCount: 10200, stations: 45, demandFactor: 1.10, avgCost: 1300000 },
    { city: "Howrah", state: "West Bengal", region: "East", evCount: 2400, stations: 8, demandFactor: 0.85, avgCost: 1050000 },
    { city: "Siliguri", state: "West Bengal", region: "East", evCount: 1500, stations: 4, demandFactor: 0.80, avgCost: 950000 },

    // Rajasthan
    { city: "Jaipur", state: "Rajasthan", region: "West", evCount: 6500, stations: 28, demandFactor: 1.02, avgCost: 1150000 },
    { city: "Jodhpur", state: "Rajasthan", region: "West", evCount: 2300, stations: 9, demandFactor: 0.86, avgCost: 1000000 },
    { city: "Udaipur", state: "Rajasthan", region: "West", evCount: 1800, stations: 7, demandFactor: 0.92, avgCost: 1050000 },

    // Madhya Pradesh
    { city: "Indore", state: "Madhya Pradesh", region: "Central", evCount: 7100, stations: 26, demandFactor: 1.12, avgCost: 1200000 },
    { city: "Bhopal", state: "Madhya Pradesh", region: "Central", evCount: 4600, stations: 18, demandFactor: 0.96, avgCost: 1100000 },
    { city: "Jabalpur", state: "Madhya Pradesh", region: "Central", evCount: 1900, stations: 6, demandFactor: 0.82, avgCost: 1000000 },

    // Kerala
    { city: "Kochi", state: "Kerala", region: "South", evCount: 5400, stations: 28, demandFactor: 1.08, avgCost: 1250000 },
    { city: "Thiruvananthapuram", state: "Kerala", region: "South", evCount: 3100, stations: 14, demandFactor: 0.94, avgCost: 1150000 },
    { city: "Kozhikode", state: "Kerala", region: "South", evCount: 2200, stations: 8, demandFactor: 0.88, avgCost: 1050000 },

    // Haryana
    { city: "Gurgaon", state: "Haryana", region: "North", evCount: 12400, stations: 72, demandFactor: 1.28, avgCost: 1550000 },
    { city: "Faridabad", state: "Haryana", region: "North", evCount: 4200, stations: 16, demandFactor: 0.92, avgCost: 1150000 },
    { city: "Panipat", state: "Haryana", region: "North", evCount: 1500, stations: 4, demandFactor: 0.78, avgCost: 950000 },

    // Punjab
    { city: "Ludhiana", state: "Punjab", region: "North", evCount: 3800, stations: 12, demandFactor: 0.90, avgCost: 1100000 },
    { city: "Amritsar", state: "Punjab", region: "North", evCount: 2700, stations: 8, demandFactor: 0.84, avgCost: 1000000 },
    { city: "Jalandhar", state: "Punjab", region: "North", evCount: 2100, stations: 6, demandFactor: 0.80, avgCost: 1000000 },

    // Andhra Pradesh
    { city: "Visakhapatnam", state: "Andhra Pradesh", region: "South", evCount: 4900, stations: 20, demandFactor: 1.05, avgCost: 1200000 },
    { city: "Vijayawada", state: "Andhra Pradesh", region: "South", evCount: 3300, stations: 11, demandFactor: 0.92, avgCost: 1100000 },

    // Bihar
    { city: "Patna", state: "Bihar", region: "East", evCount: 3600, stations: 10, demandFactor: 0.88, avgCost: 1050000 },
    { city: "Gaya", state: "Bihar", region: "East", evCount: 1200, stations: 3, demandFactor: 0.72, avgCost: 900000 },

    // Odisha (New State)
    { city: "Bhubaneswar", state: "Odisha", region: "East", evCount: 4100, stations: 15, demandFactor: 1.02, avgCost: 1150000 },
    { city: "Cuttack", state: "Odisha", region: "East", evCount: 2200, stations: 6, demandFactor: 0.85, avgCost: 1000000 },

    // Jharkhand (New State)
    { city: "Ranchi", state: "Jharkhand", region: "East", evCount: 3200, stations: 12, demandFactor: 0.95, avgCost: 1100000 },
    { city: "Jamshedpur", state: "Jharkhand", region: "East", evCount: 3900, stations: 14, demandFactor: 1.00, avgCost: 1200000 },
    { city: "Dhanbad", state: "Jharkhand", region: "East", evCount: 1800, stations: 4, demandFactor: 0.80, avgCost: 1000000 },

    // Chhattisgarh (New State)
    { city: "Raipur", state: "Chhattisgarh", region: "Central", evCount: 3500, stations: 11, demandFactor: 0.96, avgCost: 1150000 },
    { city: "Bilaspur", state: "Chhattisgarh", region: "Central", evCount: 1700, stations: 5, demandFactor: 0.80, avgCost: 1000000 },

    // Uttarakhand (New State)
    { city: "Dehradun", state: "Uttarakhand", region: "North", evCount: 2900, stations: 10, demandFactor: 0.94, avgCost: 1100000 },
    { city: "Haridwar", state: "Uttarakhand", region: "North", evCount: 2100, stations: 7, demandFactor: 0.90, avgCost: 1050000 },

    // Himachal Pradesh (New State)
    { city: "Shimla", state: "Himachal Pradesh", region: "North", evCount: 1400, stations: 6, demandFactor: 0.86, avgCost: 1050000 },
    { city: "Dharamshala", state: "Himachal Pradesh", region: "North", evCount: 950, stations: 3, demandFactor: 0.80, avgCost: 1000000 },

    // Jammu & Kashmir (New UT)
    { city: "Srinagar", state: "Jammu & Kashmir", region: "North", evCount: 2100, stations: 5, demandFactor: 0.82, avgCost: 1100000 },
    { city: "Jammu", state: "Jammu & Kashmir", region: "North", evCount: 1800, stations: 6, demandFactor: 0.85, avgCost: 1050000 },

    // Ladakh (New UT)
    { city: "Leh", state: "Ladakh", region: "North", evCount: 350, stations: 2, demandFactor: 0.70, avgCost: 1150000 },

    // Goa (New State)
    { city: "Panaji", state: "Goa", region: "West", evCount: 2400, stations: 16, demandFactor: 1.15, avgCost: 1200000 },
    { city: "Margao", state: "Goa", region: "West", evCount: 1500, stations: 8, demandFactor: 1.00, avgCost: 1100000 },

    // Assam (New State)
    { city: "Guwahati", state: "Assam", region: "East", evCount: 4200, stations: 18, demandFactor: 1.08, avgCost: 1200000 },
    { city: "Dibrugarh", state: "Assam", region: "East", evCount: 1100, stations: 4, demandFactor: 0.82, avgCost: 1000000 },

    // Tripura (New State)
    { city: "Agartala", state: "Tripura", region: "East", evCount: 1300, stations: 4, demandFactor: 0.85, avgCost: 1000000 },

    // Meghalaya (New State)
    { city: "Shillong", state: "Meghalaya", region: "East", evCount: 1600, stations: 6, demandFactor: 0.90, avgCost: 1050000 },

    // Manipur (New State)
    { city: "Imphal", state: "Manipur", region: "East", evCount: 980, stations: 3, demandFactor: 0.80, avgCost: 1000000 },

    // Mizoram (New State)
    { city: "Aizawl", state: "Mizoram", region: "East", evCount: 750, stations: 2, demandFactor: 0.75, avgCost: 1000000 },

    // Nagaland (New State)
    { city: "Kohima", state: "Nagaland", region: "East", evCount: 820, stations: 2, demandFactor: 0.78, avgCost: 1000000 },
    { city: "Dimapur", state: "Nagaland", region: "East", evCount: 1200, stations: 4, demandFactor: 0.82, avgCost: 1000000 },

    // Sikkim (New State)
    { city: "Gangtok", state: "Sikkim", region: "East", evCount: 650, stations: 3, demandFactor: 0.80, avgCost: 1050000 },

    // Arunachal Pradesh (New State)
    { city: "Itanagar", state: "Arunachal Pradesh", region: "East", evCount: 780, stations: 2, demandFactor: 0.75, avgCost: 1000000 },

    // Chandigarh (New UT)
    { city: "Chandigarh", state: "Chandigarh", region: "North", evCount: 4200, stations: 22, demandFactor: 1.12, avgCost: 1300000 },

    // Puducherry (New UT)
    { city: "Puducherry", state: "Puducherry", region: "South", evCount: 1800, stations: 9, demandFactor: 0.96, avgCost: 1100000 },

    // Additional High-Demand Corridors & Emerging Tier-2 Hubs
    { city: "Mumbai-Pune Expressway", state: "Maharashtra", region: "West", evCount: 6400, stations: 26, demandFactor: 1.40, avgCost: 1600000 },
    { city: "Aurangabad", state: "Maharashtra", region: "West", evCount: 2600, stations: 10, demandFactor: 0.88, avgCost: 1050000 },
    { city: "Kolhapur", state: "Maharashtra", region: "West", evCount: 2100, stations: 7, demandFactor: 0.85, avgCost: 1000000 },
    { city: "Agra", state: "Uttar Pradesh", region: "North", evCount: 4200, stations: 16, demandFactor: 1.05, avgCost: 1200000 },
    { city: "Meerut", state: "Uttar Pradesh", region: "North", evCount: 3400, stations: 12, demandFactor: 0.92, avgCost: 1100000 },
    { city: "Mathura", state: "Uttar Pradesh", region: "North", evCount: 2200, stations: 8, demandFactor: 0.90, avgCost: 1050000 },
    { city: "Yamuna Expressway Corridor", state: "Uttar Pradesh", region: "North", evCount: 4500, stations: 18, demandFactor: 1.35, avgCost: 1500000 },
    { city: "Delhi-Jaipur Highway Corridor", state: "Rajasthan", region: "North", evCount: 5400, stations: 22, demandFactor: 1.35, avgCost: 1550000 },
    { city: "Kota", state: "Rajasthan", region: "West", evCount: 2800, stations: 9, demandFactor: 0.86, avgCost: 1000000 },
    { city: "Ajmer", state: "Rajasthan", region: "West", evCount: 2100, stations: 7, demandFactor: 0.85, avgCost: 1000000 },
    { city: "Gwalior", state: "Madhya Pradesh", region: "Central", evCount: 2500, stations: 8, demandFactor: 0.86, avgCost: 1050000 },
    { city: "Ujjain", state: "Madhya Pradesh", region: "Central", evCount: 1900, stations: 6, demandFactor: 0.88, avgCost: 1000000 },
    { city: "Bengaluru-Mysuru Expressway", state: "Karnataka", region: "South", evCount: 4800, stations: 19, demandFactor: 1.30, avgCost: 1500000 },
    { city: "Tiruchirappalli", state: "Tamil Nadu", region: "South", evCount: 2600, stations: 10, demandFactor: 0.90, avgCost: 1050000 },
    { city: "Tirupati", state: "Andhra Pradesh", region: "South", evCount: 2900, stations: 11, demandFactor: 0.98, avgCost: 1100000 },
    { city: "Guntur", state: "Andhra Pradesh", region: "South", evCount: 2300, stations: 8, demandFactor: 0.88, avgCost: 1000000 },
    { city: "Rourkela", state: "Odisha", region: "East", evCount: 1900, stations: 6, demandFactor: 0.84, avgCost: 1000000 },
    { city: "Bokaro", state: "Jharkhand", region: "East", evCount: 1700, stations: 5, demandFactor: 0.82, avgCost: 1000000 },
    { city: "Karnal", state: "Haryana", region: "North", evCount: 2100, stations: 8, demandFactor: 0.90, avgCost: 1050000 },
    { city: "Rohtak", state: "Haryana", region: "North", evCount: 1800, stations: 6, demandFactor: 0.85, avgCost: 1000000 },
    { city: "Bhatinda", state: "Punjab", region: "North", evCount: 1600, stations: 5, demandFactor: 0.80, avgCost: 950000 }
  ];

  // Comprehensive 24-Month Dataset (Full Years 2025 & 2026)
  const months = [
    "January 2025", "February 2025", "March 2025", "April 2025", "May 2025", "June 2025",
    "July 2025", "August 2025", "September 2025", "October 2025", "November 2025", "December 2025",
    "January 2026", "February 2026", "March 2026", "April 2026", "May 2026", "June 2026",
    "July 2026", "August 2026", "September 2026", "October 2026", "November 2026", "December 2026"
  ];

  // Progressive growth rates over 24 months
  const monthlyRates = [
    0.65, 0.68, 0.71, 0.74, 0.78, 0.82,
    0.86, 0.90, 0.93, 0.96, 0.98, 1.00,
    1.03, 1.07, 1.11, 1.15, 1.19, 1.23,
    1.27, 1.31, 1.35, 1.39, 1.43, 1.47
  ];

  const records = [];

  // Generate 24 months of rich telemetry entries
  months.forEach((month, mIdx) => {
    const rate = monthlyRates[mIdx];
    baseCities.forEach((bc) => {
      // 1. Calculate realistic EV growth
      const currentEv = Math.round(bc.evCount * rate);
      
      // 2. Existing stations remain mostly flat with slight expansion
      let currentStations = bc.stations;
      if (mIdx >= 2) currentStations += Math.round(bc.stations * 0.03 * (mIdx - 1)); // slight expansion over time
      
      // 3. Recommended/Optimal stations is based on EV density (approx 1 station per 100 EVs for optimal coverage)
      const optimalStationsCount = Math.ceil(currentEv / 100);
      
      // 4. Infrastructure Gap calculation
      const infraGap = Math.max(0, optimalStationsCount - currentStations);
      
      // 5. Utilization and Sessions (affected by demand factor and seasonality)
      // Base average sessions per station per month is ~220
      const baseSessionsPerStation = 210 + Math.sin(mIdx * 0.5) * 15;
      const calculatedSessions = currentStations > 0 
        ? Math.round(currentStations * baseSessionsPerStation * bc.demandFactor * (0.95 + Math.random() * 0.1))
        : Math.round(currentEv * 0.05); // low sessions if zero public stations but local charging exists
        
      // Avg session length = 1.6 hours
      const totalChargingHours = calculatedSessions * 1.6;
      const totalCapacityHours = (currentStations || 1) * 24 * 30;
      let utilization = (totalChargingHours / totalCapacityHours) * 100;
      if (utilization > 92) utilization = 92 - Math.random() * 3; // cap realistic utilization
      if (utilization < 15) utilization = 15 + Math.random() * 5;
      utilization = parseFloat(utilization.toFixed(1));

      // 6. Financial Calculations (in INR)
      const avgRevenuePerSession = 320; // ₹320 per session
      const capExCost = bc.avgCost; // Average Cost per charger setup
      const monthlyOpEx = currentStations * 18000; // OpEx is ~₹18,000 per station monthly
      const monthlyRevenue = calculatedSessions * avgRevenuePerSession;
      const expectedProfit = monthlyRevenue - monthlyOpEx;
      
      // Annualized ROI = (Monthly Profit * 12) / Total CapEx (scaled for current stations)
      const totalCapExVal = Math.max(1, currentStations) * capExCost;
      let roi = ((expectedProfit * 12) / totalCapExVal) * 100;
      if (currentStations === 0) roi = 0;
      roi = parseFloat(roi.toFixed(1));

      records.push({
        date: month,
        city: bc.city,
        state: bc.state,
        region: bc.region,
        evCount: currentEv,
        stations: currentStations,
        sessions: calculatedSessions,
        utilization: utilization,
        installationCost: totalCapExVal,
        revenue: Math.round(monthlyRevenue),
        profit: Math.round(expectedProfit),
        roi: roi,
        infraGap: infraGap,
        optimalStations: optimalStationsCount,
        singleStationCapEx: capExCost
      });
    });
  });

  // Calculate recommendation priorities based on weights
  function calculateRecommendations(recordsForMonth, weights = { evDensity: 0.25, demand: 0.25, infraGap: 0.25, roi: 0.25 }) {
    // Normalization factors
    const maxEv = Math.max(...recordsForMonth.map(r => r.evCount));
    const maxSessions = Math.max(...recordsForMonth.map(r => r.sessions));
    const maxGap = Math.max(...recordsForMonth.map(r => r.infraGap));
    const maxRoi = Math.max(...recordsForMonth.map(r => r.roi));

    return recordsForMonth.map(r => {
      const normEv = r.evCount / (maxEv || 1);
      const normSessions = r.sessions / (maxSessions || 1);
      const normGap = r.infraGap / (maxGap || 1);
      const normRoi = r.roi / (maxRoi || 1);

      // Score weighted average (0 - 100)
      const scoreRaw = (
        normEv * weights.evDensity +
        normSessions * weights.demand +
        normGap * weights.infraGap +
        normRoi * weights.roi
      ) * 100;

      const priorityScore = Math.round(Math.min(100, Math.max(0, scoreRaw)));

      let priorityClass = "Low";
      if (priorityScore >= 75) priorityClass = "Critical";
      else if (priorityScore >= 50) priorityClass = "High";
      else if (priorityScore >= 30) priorityClass = "Medium";

      // Dynamically generate the reasoning string
      let reasoning = "";
      if (priorityClass === "Critical" || priorityClass === "High") {
        reasoning = `${r.city} exhibits critical expansion priority due to high EV concentration (${r.evCount.toLocaleString()} EVs), an infrastructure gap of ${r.infraGap} optimal stations, and a strong projected ROI of ${r.roi}%.`;
      } else if (priorityClass === "Medium") {
        reasoning = `${r.city} offers steady medium-priority growth. Current station utilization is stable at ${r.utilization}%, presenting moderate ROI opportunities of ${r.roi}% for target charger infills.`;
      } else {
        reasoning = `${r.city} shows lower deployment urgency. Existing stations coverage is sufficient (Gap: ${r.infraGap}), and current local market density does not justify new CapEx commitments.`;
      }

      return {
        city: r.city,
        state: r.state,
        region: r.region,
        evCount: r.evCount,
        stations: r.stations,
        sessions: r.sessions,
        utilization: r.utilization,
        infraGap: r.infraGap,
        expectedRevenue: Math.round(r.singleStationCapEx * 0.28), // Est Revenue for 1 new station
        installationCost: r.singleStationCapEx,
        roi: r.roi,
        priorityScore,
        priorityClass,
        reasoning
      };
    }).sort((a, b) => b.priorityScore - a.priorityScore);
  }

  // Export to window for global access in HTML React app
  window.EV_ANALYTICS_DATA = {
    regions: Object.keys(regions),
    states,
    months,
    records,
    calculateRecommendations
  };
})();
