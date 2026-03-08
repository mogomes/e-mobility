(function () {
  const maps = document.querySelectorAll('.map-box');
  if (!maps.length || typeof L === 'undefined') {
    return;
  }

  maps.forEach((element) => {
    const raw = element.dataset.mapPoints || '[]';
    let points = [];
    try {
      points = JSON.parse(raw);
    } catch (error) {
      points = [];
    }

    const fallback = [47.3769, 8.5417];
    const center = points.length ? [points[0].latitude, points[0].longitude] : fallback;
    const map = L.map(element).setView(center, 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap-Mitwirkende',
    }).addTo(map);

    points.forEach((point) => {
      const marker = L.marker([point.latitude, point.longitude]).addTo(map);
      marker.bindPopup(`
        <strong>${point.name}</strong><br>
        Kennung: ${point.public_id}<br>
        Status: ${point.status}<br>
        Akku: ${point.battery_level}%
      `);
    });
  });
})();
