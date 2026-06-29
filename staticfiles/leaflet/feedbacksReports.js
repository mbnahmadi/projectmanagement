// Feedback filter and report
let lastReportDatafb = null;

const filterFormfb = document.getElementById('filter-form-fb');

filterFormfb.addEventListener('submit', function(e) {
    e.preventDefault();

    let company_name= document.getElementById('company-fb').value; // Adjust ID if different
    let location_name = document.getElementById('location-fb').value; // Adjust ID if different
    let start = document.getElementById('start-date-fb').value; // Adjust ID if different
    let end = document.getElementById('end-date-fb').value; // Adjust ID if different

    let query = new URLSearchParams();
    if (company_name) query.append('company_name', company_name);
    if (location_name) query.append('location_name', location_name);
    if (start) query.append('start', start);
    if (end) query.append('end', end);

    fetch('/feedback/feedback-custom-filter/?' + query.toString()) //
    .then(res => res.json())
    .then(data => {
        lastReportDatafb = data; 
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
                            
                            <button class="feedback-btn" data-id="${location.pk}" style="margin-top:5px;background:#FFD32C;color:white;border:none;padding:5px 10px;border-radius:5px;">feed back</button>
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
                            ${location.has_feedback 
                                ? `<button class="feedback-btn" data-id="${location.pk}" style="margin-top:5px;background:#FFD32C;color:white;border:none;padding:5px 10px;border-radius:5px;">feed back</button>` 
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
const modal = document.getElementById("totalreporfeedbacktModal");
const closeBtn = document.getElementById("closeModaltotalfb");
const container = document.getElementById("totalreportfeedbackVerticalContainer");
const reportBtn = document.getElementById("report-fb");

reportBtn.addEventListener("click", function() {
    if (!lastReportDatafb) {
        alert("No report data available. Please run filter first!");
        return;
    }

    container.innerHTML = "";

    lastReportDatafb.forEach(company => {
        company.detail.forEach(location => {
            (location.feedbacks || []).forEach(feedback => {
                console.log(feedback)
                let table = document.createElement("table");
                table.className = "w-full border border-gray-300 rounded-lg overflow-hidden mb-6";

                table.innerHTML = `
                    <tr class=" bg-red-200">
                        <th class="border text-center" colspan="2">main detail for ${company.company_name} -  ${location.location_name}</th>
                    </tr>
                    <tbody>
                        <tr class="bg-gray-100">
                            <th class="border px-4 py-2 w-40 text-left">Company</th>
                            <td class="border px-4 py-2">${company.company_name}</td>
                        </tr>
                        <tr>
                            <th class="border px-4 py-2 text-left">Location</th>
                            <td class="border px-4 py-2">${location.location_name}</td>
                        </tr>
                        <tr class="bg-gray-100">
                            <th class="border px-4 py-2 text-left">format</th>
                            <td class="border px-4 py-2">${location.days_format} - ${location.project_format}</td>
                        </tr>
                        <tr>
                            <th class="border px-4 py-2 text-left">Start</th>
                            <td class="border px-4 py-2">${location.start_date}</td>
                        </tr>
                        <tr class="bg-gray-100">
                            <th class="border px-4 py-2 text-left">End</th>
                            <td class="border px-4 py-2">${location.end_date ?? '-'}</td>
                        </tr>
                        <tr>
                            <th class="border px-4 py-2 text-left">Status</th>
                            <td class="border px-4 py-2" style="color:${location.is_active_now ? 'green':'red'}">
                                ${location.is_active_now ? 'Active' : 'Inactive'}
                            </td>
                        </tr>

                        <!-- اطلاعات feedback -->
                        <tr class=" bg-gray-400">
                            <th class="border text-center" colspan="2">feed back</th>
                        </tr>
                        <tr>
                            <th class="border px-4 py-2 text-left">Name</th>
                            <td class="border px-4 py-2">${feedback.name}</td>
                        </tr>
                        <tr class="bg-gray-100">
                            <th class="border px-4 py-2 text-left">Phone</th>
                            <td class="border px-4 py-2">${feedback.phone_number}</td>
                        </tr>
                        <tr>
                            <th class="border px-4 py-2 text-left">Through</th>
                            <td class="border px-4 py-2">${feedback.through}</td>
                        </tr>
                        <tr class="bg-gray-100">
                            <th class="border px-4 py-2 text-left">Date</th>
                            <td class="border px-4 py-2">${feedback.date}</td>
                        </tr>
                        <tr>
                            <th class="border px-4 py-2 text-left">Message</th>
                            <td class="border px-4 py-2 whitespace-pre-wrap break-words">${feedback.message}</td>
                        </tr>
                        <tr class="bg-gray-100">
                            <th class="border px-4 py-2 text-left">Attachments</th>
                            <td class="border px-4 py-2">
                                ${(feedback.attachments || []).map(a => `<a href="${a.file}" target="_blank" class="text-blue-600 underline">Download</a>`).join(' ')}
                            </td>
                        </tr>
                        ${(feedback.response || []).map(res =>
                            `<tr class=" bg-gray-400">
                            <th class="border text-center" colspan="2">feed back response</th>
                        </tr>
                        <tr>
                            <th class="border px-4 py-2 text-left">Through</th>
                            <td class="border px-4 py-2">${res.through}</td>
                        </tr>
                            <tr class="bg-gray-100">
                            <th class="border px-4 py-2 text-left">Date</th>
                            <td class="border px-4 py-2">${res.date}</td>
                        </tr>
                        <tr>
                            <th class="border px-4 py-2 text-left">Message</th>
                            <td class="border px-4 py-2 whitespace-pre-wrap break-words">${res.message}</td>
                        </tr>
                        <tr class="bg-gray-100">
                            <th class="border px-4 py-2 text-left">ISO Form</th>
                            <td class="border px-4 py-2">
                                ${res.iso_form ? `<a href="${res.iso_form}" target="_blank" class="text-blue-600 underline">Download</a>` : ''}
                            </td>
                        </tr>
                        
                        `
                    )}
                    
                    <br><br><br>

                    </tbody>
                `;

                container.appendChild(table);
            });
        });
    });

    modal.classList.remove("hidden");
});

closeBtn.addEventListener("click", function() {
    modal.classList.add("hidden");
    container.innerHTML = ""; 
});

modal.addEventListener("click", function(e) {
    if (e.target === modal) {
        modal.classList.add("hidden");
        container.innerHTML = ""; 
    }
});
