// Base map setup and Quick access functions

let map = L.map("map").setView([35, 50], 5);
// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
L.tileLayer("/static/tiles/{z}/{x}/{y}.png", {
  maxZoom: 9,
  minZoom: 1,
}).addTo(map);
let markersLayer = L.markerClusterGroup().addTo(map);

let activeIcon = L.icon({
  iconUrl: "/static/images/location/green.png",
  iconSize: [15, 15],
});
let inactiveIcon = L.icon({
  iconUrl: "/static/images/location/red.png",
  iconSize: [15, 15],
});
let download = "/static/images/icon/download.png";

function loadLocations(url) {
  fetch(url)
    .then((res) => res.json())
    .then((data) => {
      markersLayer.clearLayers();

      data.features.forEach((f) => {
        const geom = f.geometry;
        const props = f.properties;
        let icon = props.is_active_now ? activeIcon : inactiveIcon;

        let popupContent = `
                    <div style="direction:ltr;text-align:left;font-family:sans-serif;font-size:16px">
                        <b style="color:#00008B">Company: </b><b>${props.company_name}</b><br>
                        <b style="color:#00008B">Location: </b><b>${props.location_name}</b><br>
                        <b style="color:#00008B">Format: </b><b>${props.days_format} - ${props.project_format}</b><br>
                        <b style="color:#00008B">Start: </b><b>${props.start_date}</b><br>
                        <b style="color:#00008B">End: </b><b>${props.end_date ?? "-"}</b><br>
                        <b style="color:#00008B">Status: </b>
                        <b style="color:${props.is_active_now ? "green" : "red"}">
                            ${props.is_active_now ? "Active" : "Inactive"}
                        </b><br>
                        ${
                          props.is_active_now
                            ? `<button class="download-btn" data-id="${props.pk}" style="margin-top:5px;background:#d9534f;color:white;border:none;padding:5px 10px;border-radius:5px;">download latest PDF</button>`
                            : ""
                        }
                        ${
                          props.has_feedback
                            ? `<button class="feedback-btn" data-id="${props.pk}" style="margin-top:5px;background:#FFD32C;color:white;border:none;padding:5px 10px;border-radius:5px;">feed back</button>`
                            : ""
                        }
                    </div>
                `;

        let popupOptions = {
          autoClose: true,
          closeOnClick: true,
          closeButton: true,
        };

        if (geom.type === "Point") {
          let marker = L.marker([geom.coordinates[1], geom.coordinates[0]], {
            icon,
          });
          marker.bindPopup(popupContent, popupOptions);
          markersLayer.addLayer(marker);
        } else if (geom.type === "LineString") {
          let latlngs = geom.coordinates.map((c) => [c[1], c[0]]);
          let polyline = L.polyline(latlngs, {
            color: props.is_active_now ? "green" : "red",
          });
          let centroid = latlngs[Math.floor(latlngs.length / 2)];
          let marker = L.marker(centroid, { icon });

          polyline.bindPopup(popupContent, popupOptions);
          marker.bindPopup(popupContent, popupOptions);

          markersLayer.addLayer(polyline);
          markersLayer.addLayer(marker);
        }
      });
    });
}

map.on("popupopen", function (e) {
  const btn = e.popup._contentNode.querySelector(".download-btn");
  if (btn) {
    btn.addEventListener("click", function (ev) {
      ev.stopPropagation();
      const pk = btn.getAttribute("data-id");
      window.location.href = `/projects/download-pdf/${pk}/`;
    });
  }
});
// map.on('popupopen', function (e) {
//     const btn = e.popup._contentNode.querySelector('.feedback-btn');
//     if (btn) {
//         btn.addEventListener('click', function(ev) {
//             ev.stopPropagation();
//             const pk = btn.getAttribute('data-id');
//             window.location.href = `/feedback/locations-feedback/${pk}/`;
//         });
//     }
// });

map.on("popupopen", function (e) {
  const btn = e.popup._contentNode.querySelector(".feedback-btn");
  if (btn) {
    btn.addEventListener("click", function (ev) {
      ev.stopPropagation();
      const pk = btn.getAttribute("data-id");

      fetch(`/feedback/locations-feedback/${pk}/`)
        .then((res) => res.json())
        .then((data) => {
          let container = document.getElementById(
            "reportfeedbackVerticalContainer",
          );
          container.innerHTML = "";

          data.forEach((location) => {
            location.feedbacks.forEach((feedback) => {
              let table = document.createElement("table");
              table.className =
                "w-full border border-gray-300 rounded-lg overflow-hidden mb-6";

              table.innerHTML = `
                                <tbody>
                                    <tr class=" bg-gray-400">
                                        <th class="border text-center" colspan="2">MAIN DETAIL</th>
                                    </tr>
                                    <tr class="bg-gray-100">
                                        <th class="border px-4 py-2 w-40 text-left">Company</th>
                                        <td class="border px-4 py-2">${location.company_name}</td>
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
                                        <td class="border px-4 py-2">${location.end_date ?? "-"}</td>
                                    </tr>
                                    <tr>
                                        <th class="border px-4 py-2 text-left">Status</th>
                                        <td class="border px-4 py-2" style="color:${location.is_active_now ? "green" : "red"}">
                                            ${location.is_active_now ? "Active" : "Inactive"}
                                        </td>
                                    </tr>
                                    <tr class=" bg-gray-400">
                                        <th class="border text-center" colspan="2">FEED BACK</th>
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
                                            ${feedback.attachments.map((a) => `<a href="${a.file}" target="_blank" class="text-blue-600 underline">Download | </a>`).join(" ")}
                                        </td>
                                    </tr>

                                    ${
                                      feedback.response
                                        ? `
                                    <tr class=" bg-gray-400">
                                        <th class="border text-center" colspan="2">FEED BACK RESPONSE</th>
                                    </tr>
                                    <tr>
                                        <th class="border px-4 py-2 text-left">Through</th>
                                        <td class="border px-4 py-2">${feedback.response.through}</td>
                                    </tr>
                                    <tr class="bg-gray-100">
                                        <th class="border px-4 py-2 text-left">Date</th>
                                        <td class="border px-4 py-2">${feedback.response.date}</td>
                                    </tr>
                                    <tr>
                                        <th class="border px-4 py-2 text-left">Message</th>
                                        <td class="border px-4 py-2 whitespace-pre-wrap break-words">${feedback.response.message}</td>
                                    </tr>
                                    <tr class="bg-gray-100">
                                        <th class="border px-4 py-2 text-left">Attachments</th>
                                        <td class="border px-4 py-2">
                                            ${feedback.response.iso_form ? `<a href="${feedback.response.iso_form}" target="_blank" class="text-blue-600 underline">Download</a>` : ""}
                                        </td>
                                    </tr>
                                    `
                                        : ""
                                    }
                                </tbody>
                            `;

              container.appendChild(table);
            });
          });

          document
            .getElementById("reporfeedbacktModal")
            .classList.remove("hidden");
        })
        .catch((err) => {
          console.error(err);
          alert("error to get data.");
        });
    });
  }
});

document.getElementById("closeModalfb").addEventListener("click", function () {
  document.getElementById("reporfeedbacktModal").classList.add("hidden");
});

document
  .getElementById("active-locations-btn")
  .addEventListener("click", function () {
    loadLocations("/projects/get-active-locations/");
  });
document
  .getElementById("all-locations-btn")
  .addEventListener("click", function () {
    loadLocations("/projects/get-all-locations/");
  });
document
  .getElementById("all-routes-btn")
  .addEventListener("click", function () {
    loadLocations("/projects/get-all-routes/");
  });
document
  .getElementById("has-feedback-locations-btn")
  .addEventListener("click", function () {
    loadLocations("/projects/get-all-locations_has_feedback/");
  });

// ------------ calculate distance ----------------

// define obj
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

// set draw control to obj
const drawControl = new L.Control.Draw({
  edit: {
    featureGroup: drawnItems,
  },
  draw: {
    polygon: true,
    polyline: true,
    rectangle: true,
    circle: false,
    marker: true,
  },
});

// add draw controls to map / toolbar appears on the map.
map.addControl(drawControl);

// When a user finishes drawing something, Leaflet emits events. Without this, drawings vanish into the void.
let totalDistancePopup = null;
let segmentTooltips = [];

map.on(L.Draw.Event.CREATED, function (e) {
  const layer = e.layer;

  if (!(layer instanceof L.Polyline)) return;

  // clear leftovers (important if user draws again)
  clearSegmentTooltips();
  clearTotalPopup();

  const latlngs = layer.getLatLngs();

  let total = 0;

  latlngs.slice(1).forEach((point, i) => {
    const prev = latlngs[i];
    const dist = map.distance(prev, point) / 1000;
    total += dist;

    // segment tooltip
    const mid = L.latLng(
      (prev.lat + point.lat) / 2,
      (prev.lng + point.lng) / 2,
    );

    const tt = L.tooltip({
      permanent: true,
      direction: "center",
      className: "segment-distance",
    })
      .setLatLng(mid)
      .setContent(`${dist.toFixed(1)} km`)
      .addTo(map);

    segmentTooltips.push(tt);
  });

  // popup at last vertex
  const lastPoint = latlngs[latlngs.length - 1];

  totalDistancePopup = L.popup({
    closeButton: false,
    autoClose: false,
    className: "total-distance",
  })
    .setLatLng(lastPoint)
    .setContent(`Total distance: ${total.toFixed(2)} km`)
    .openOn(map);

  drawnItems.addLayer(layer);
});

function clearSegmentTooltips() {
  segmentTooltips.forEach((t) => map.removeLayer(t));
  segmentTooltips.length = 0;
}

function clearTotalPopup() {
  if (totalDistancePopup) {
    map.removeLayer(totalDistancePopup);
    totalDistancePopup = null;
  }
}

map.on("draw:deleted", function () {
  clearSegmentTooltips();
  clearTotalPopup();
});
// map.on(L.Draw.Event.CREATED, function (e) {
//     const layer = e.layer;

//     if (layer instanceof L.Polyline) {
//       const lengthInMeters = layer.getLatLngs()
//         .reduce((sum, point, i, arr) =>
//           i === 0 ? 0 : sum + map.distance(arr[i - 1], point)
//         , 0);

//       console.log('sum', lengthInMeters/1000);
//     }

//     drawnItems.addLayer(layer);
//   });

// map.on('draw:drawvertex', function (e) {
//     const markers = e.layers.getLayers();
//     const last = markers[markers.length - 1];
//     const prev = markers[markers.length - 2];

//     if (prev && last) {
//         console.log('distance from the last point', map.distance(prev.getLatLng(), last.getLatLng())/1000);
//     }
// });

//////////////////////////////////////
// let
//     _firstLatLng, //holding first marker latitude and longitude
//     _secondLatLng,//holding second marker latitude and longitude
//     _polyline,    //holding polyline object
//     merkerA= null,
//     markerB = null;

// map.on('click', function(e) {
//     if (!_firstLatLng) {
//         _firstLatLng = e.latlng;
//         markerA = L.marker(_firstLatLng).addTo(map).bindPopup('Point A<br/>' + e.latlng).openPopup();

//     }else if (!_secondLatLng) {
//         //get second point latitude and longitude
//         _secondLatLng = e.latlng;

//         //create second marker and add popup
//         markerB = L.marker(_secondLatLng).addTo(map).bindPopup('Point B<br/>' + e.latlng).openPopup();

//         //draw a line between two points
//         _polyline = L.polyline([_firstLatLng, _secondLatLng], {
//             color: 'blue'
//         });

//         //add the line to the map
//         _polyline.addTo(map);

//         //get the distance between two points
//         let _length = map.distance(_firstLatLng, _secondLatLng);

//         //display the result
//         document.getElementById('length').innerHTML = _length;

//     }

// })
