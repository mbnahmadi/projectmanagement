// projects.js - Projects filter and report
let lastReportData = null;

const filterForm = document.getElementById('filter-form');

filterForm.addEventListener('submit', function(e) {
    e.preventDefault();

    let company_name = document.getElementById('company').value;
    let location_name = document.getElementById('location').value;
    let start = document.getElementById('start-date').value;
    let end = document.getElementById('end-date').value;

    let query = new URLSearchParams();
    if (company_name) query.append('company_name', company_name);
    if (location_name) query.append('location_name', location_name);
    if (start) query.append('start', start);
    if (end) query.append('end', end);

    fetch('/projects/company-location-daterange/?' + query.toString())
    .then(res => res.json())
    .then(data => {
        lastReportData = data; 
        markersLayer.clearLayers();

        data.forEach(company => {  
            company.detail.forEach(location => {  
                if (location.geometry.type === 'Point'){
                    let lat = location.geometry.coordinates[1];  
                    let lon = location.geometry.coordinates[0];  
               
                    let icon = location.is_active_now ? activeIcon : inactiveIcon;

                    let popupContent = `
                        <div style="direction: ltr; text-align: left; font-family: sans-serif; font-size:16px">
                            <b style="color:#00008B">Company: </b><b style="color:#3b3b3b">${company.company_name}</b><br>
                            <b style="color:#00008B">Location: </b><b style="color:#3b3b3b">${location.location_name}</b><br>
                            <b style="color:#00008B">format: </b><b style="color:#3b3b3b">${location.days_format} - ${location.project_format}</b><br>
                            <b style="color:#00008B">start date: </b><b style="color:#3b3b3b">${location.start_date}</b><br> 
                            <b style="color:#00008B">end date: </b><b style="color:#3b3b3b">
                                ${location.is_active_now ? '-' : `${location.end_date}` }
                            </b><br>
                            <b style="color:#00008B">status: </b><b style="color:${location.is_active_now ? 'green' : 'red'}">
                                ${location.is_active_now ? 'Active' : 'Inactive'}
                            </b><br>
                            ${location.is_active_now 
                                ? `<button class="download-btn" data-id="${location.pk}" style="margin-top:5px;background:#d9534f;color:white;border:none;padding:5px 10px;border-radius:5px;">download latest PDF</button>` 
                                : ''}
                        </div>
                    `;

                    let popupOptions = {
                        autoClose: true,       
                        closeOnClick: true,    
                        closeButton: true      
                    };

                    let marker = L.marker([lat, lon], {icon: icon});
                    marker.bindPopup(popupContent, popupOptions);
                    markersLayer.addLayer(marker);
                } else if (location.geometry.type === 'LineString'){
                    let latlngs2 = location.geometry.coordinates.map(c => [c[1], c[0]]);
                    let polyline2 = L.polyline(latlngs2, { color: location.is_active_now ? 'green' : 'red' });

                    let popupContent = `
                        <div style="direction: ltr; text-align: left; font-family: sans-serif; font-size:16px">
                            <b style="color:#00008B">Company: </b><b style="color:#3b3b3b">${company.company_name}</b><br>
                            <b style="color:#00008B">Location: </b><b style="color:#3b3b3b">${location.location_name}</b><br>
                            <b style="color:#00008B">format: </b><b style="color:#3b3b3b">${location.days_format} - ${location.project_format}</b><br>
                            <b style="color:#00008B">start date: </b><b style="color:#3b3b3b">${location.start_date}</b><br> 
                            <b style="color:#00008B">end date: </b><b style="color:#3b3b3b">
                                ${location.is_active_now ? '-' : `${location.end_date}` }
                            </b><br>
                            <b style="color:#00008B">status: </b><b style="color:${location.is_active_now ? 'green' : 'red'}">
                                ${location.is_active_now ? 'Active' : 'Inactive'}
                            </b><br>
                            ${location.is_active_now 
                                ? `<button class="download-btn" data-id="${location.pk}" style="margin-top:5px;background:#d9534f;color:white;border:none;padding:5px 10px;border-radius:5px;">download latest PDF</button>` 
                                : ''}
                        </div>
                    `;

                    let popupOptions = {
                        autoClose: true,       
                        closeOnClick: true,    
                        closeButton: true      
                    };

                    polyline2.bindPopup(popupContent, popupOptions);
                    markersLayer.addLayer(polyline2);
                }
            });
        });
    });
});

document.getElementById("report").addEventListener("click", function() {
    if (!lastReportData) {
      alert("No report data available. Please run filter first!");
      return;
    }
    
    let tbody = document.getElementById("reportTableBody");
    tbody.innerHTML = "";
  
    lastReportData.forEach(company => {
      company.detail.forEach((location) => {
        let tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="border px-4 py-2">${company.company_name}</td>
          <td class="border px-4 py-2">${location.location_name}</td>
          <td class="border px-4 py-2">${location.start_date}</td>
          <td class="border px-4 py-2">${location.end_date ?? '-'}</td>
          <td class="border px-4 py-2">${location.days_format} - ${location.project_format}</td>
          <td class="border px-4 py-2" style="color:${location.is_active_now ? 'green':'red'}">
            ${location.is_active_now ? 'Active' : 'Inactive'}
          </td>
          <td class="border px-4 py-2">${location.active_days}</td>
        `;
        tbody.appendChild(tr);
      });
      
      let summaryTr = document.createElement("tr");
      summaryTr.innerHTML = `
          <td class="border px-4 py-2 font-bold text-right" style="background-color: #D0FFBC" colspan="7">summary</td>
          <td class="border px-4 py-2 font-bold" style="background-color: #D0FFBC">${company.total_days}</td>
          <td class="border px-4 py-2 font-bold" style="background-color: #D0FFBC">${company.total_location}</td>
      `;
      tbody.appendChild(summaryTr);
    });
    // document.getElementById("map").classList.add("hidden"); // Uncomment if needed
    document.getElementById("reportModal").classList.remove("hidden");
  });

  document.getElementById("closeModal").addEventListener("click", function() {
    document.getElementById("reportModal").classList.add("hidden");
    // document.getElementById("map").classList.remove("hidden");
});