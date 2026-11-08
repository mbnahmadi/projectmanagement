const monthMap = {
    Jan: '01', Feb: '02', Mar: '03', Apr: '04', May: '05', Jun: '06',
    Jul: '07', Aug: '08', Sep: '09', Oct: '10', Nov: '11', Dec: '12'
  };
  
  let allPoints = [];  // ذخیره همه داده‌ها برای فیلتر بعدی
  let chart = null;
  
  function renderChart(filteredPoints) {
    if (chart) chart.destroy();
  
    const options = {
      chart: {
        height: 380,
        width: "100%",
        type: "area",
        zoom: { enabled: true },
        animations: { initialAnimation: { enabled: false } }
      },
      series: [{
        name: 'total activity days',
        data: filteredPoints   // [['2021-08-01', 7], ...]
      }],
      xaxis: {
        type: 'datetime',
        // floating: true,
        labels: {
          datetimeUTC: false,
          
        },
      },
      tooltip: {
        x: { format: 'yyyy MMM' } // فقط نمایش زیبا در tooltip
      }
    };
  
    chart = new ApexCharts(document.querySelector("#chart"), options);
    chart.render();
  }
  
  // بارگذاری اولیه داده‌ها
  fetch('http://127.0.0.1:8000/projects/days-per-month/all/')
    .then(response => response.json())
    .then(apidata => {
      allPoints = [];
      apidata.forEach(yearObj => {
        yearObj.data.forEach(item => {
          const monthNum = monthMap[item.month];
          const date = `${yearObj.year}-${monthNum}-01`; // مثل: 2021-08-01
          allPoints.push([date, item.days]);
        });
      });
  
      renderChart(allPoints);
    })
    .catch(error => console.error('Error fetching data:', error));
  
  // فیلتر بازه زمانی
  document.getElementById('applyRange').addEventListener('click', () => {
    const start = document.getElementById('startDate').value;
    const end = document.getElementById('endDate').value;
  
    const filtered = allPoints.filter(([date]) => {
      return (!start || date >= start) && (!end || date <= end);
    });
  
    renderChart(filtered);
  });