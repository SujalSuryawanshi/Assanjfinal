// index.html slider // Category slider // staller slider

document.addEventListener("DOMContentLoaded", function () {
  const sliders = {};

  document.querySelectorAll(".slider").forEach(slider => {
      const category = slider.id.replace("Slider", ""); // Extract category name
      sliders[category] = {
          index: 0,
          container: slider,
          startX: 0,
          isSwiping: false
      };

      // Attach touch event listeners for swiping
      slider.addEventListener("touchstart", function (e) { startSwipe(e, category); });
      slider.addEventListener("touchmove", function (e) { moveSwipe(e, category); });
      slider.addEventListener("touchend", function (e) { endSwipe(e, category); });
  });

  function updateSlidePosition(category) {
      const slider = sliders[category].container;
      const slides = slider.querySelectorAll(".slide");
      if (slides.length === 0) return;

      const slideWidth = slides[0].clientWidth;
      slider.style.transition = "transform 0.3s ease-in-out";
      slider.style.transform = `translateX(-${slideWidth * sliders[category].index}px)`;
  }

  function startSwipe(e, category) {
      sliders[category].startX = e.touches[0].clientX;
      sliders[category].isSwiping = true;
  }

  function moveSwipe(e, category) {
      if (!sliders[category].isSwiping) return;
      const currentX = e.touches[0].clientX;
      const diff = sliders[category].startX - currentX;

      if (Math.abs(diff) > 50) {  // Minimum swipe threshold
          if (diff > 0) {
              nextSlide(category);
          } else {
              prevSlide(category);
          }
          sliders[category].isSwiping = false;
      }
  }

  function endSwipe(e, category) {
      sliders[category].isSwiping = false;
  }

  function nextSlide(category) {
      const slider = sliders[category].container;
      const totalSlides = slider.querySelectorAll(".slide").length;
      if (totalSlides === 0) return;

      sliders[category].index = (sliders[category].index + 1) % totalSlides;
      updateSlidePosition(category);
  }

  function prevSlide(category) {
      const slider = sliders[category].container;
      const totalSlides = slider.querySelectorAll(".slide").length;
      if (totalSlides === 0) return;

      sliders[category].index = (sliders[category].index - 1 + totalSlides) % totalSlides;
      updateSlidePosition(category);
  }

  // Resize fix to maintain correct position
  window.addEventListener("resize", function () {
      Object.keys(sliders).forEach(updateSlidePosition);
  });
});




// Profile slide // arrow slider //

document.addEventListener("DOMContentLoaded", function () {
  const sliders = {
      'popular': { index: 0, container: document.getElementById('popularSlider') },
      'all': { index: 0, container: document.getElementById('allSlider') }
  };

  function updateSlidePosition(sliderKey) {
      const slider = sliders[sliderKey].container;
      const slideWidth = slider.querySelector('.slide').clientWidth;
      slider.style.transform = `translateX(-${slideWidth * sliders[sliderKey].index}px)`;
  }

  window.nextSlide = function (sliderKey) {
      const slider = sliders[sliderKey].container;
      const totalSlides = slider.querySelectorAll('.slide').length;

      sliders[sliderKey].index = (sliders[sliderKey].index + 1) % totalSlides;
      updateSlidePosition(sliderKey);
  }

  window.prevSlide = function (sliderKey) {
      const slider = sliders[sliderKey].container;
      const totalSlides = slider.querySelectorAll('.slide').length;

      sliders[sliderKey].index = (sliders[sliderKey].index - 1 + totalSlides) % totalSlides;
      updateSlidePosition(sliderKey);
  }

  window.addEventListener("resize", function () {
      updateSlidePosition('popular');
      updateSlidePosition('all');
  });
});



// Add to cart // Add items // 
function toggleCart(itemId) {
    const button = document.getElementById(`cart-btn-${itemId}`);
    const action = button.textContent.trim() === "Add to Cart" ? "add" : "remove";

    fetch(`/cart/${action}/${itemId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.textContent = action === "add" ? "Remove from Cart" : "Add to Cart";
        } else {
            alert("Failed to update cart.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the cart.');
    });
}

function toggleCart(itemId) {
    fetch(`/add-to-cart/${itemId}/`, {  // Use correct URL from urls.py
        method: "POST",
        headers: {
            "X-CSRFToken": "{{ csrf_token }}",  // Ensure CSRF protection
            "Content-Type": "application/json"
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let btn = document.getElementById(`cart-btn-${itemId}`);
            if (data.in_cart) {
                btn.textContent = "Remove from Cart";
                btn.classList.remove("btn-success");
                btn.classList.add("btn-danger");
            } else {
                btn.textContent = "Add to Cart";
                btn.classList.remove("btn-danger");
                btn.classList.add("btn-success");
            }
        }
    });
}



// Update location // location index.html // button update // 
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  }

  function updateLocation() {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      function (position) {
        let latitude = position.coords.latitude;
        let longitude = position.coords.longitude;
        console.log("Retrieved location:", latitude, longitude);

        let stallIdElement = document.getElementById("stall-id");
        if (!stallIdElement) {
          console.error("Error: stall ID input field is missing.");
          alert("Error: Stall ID input field not found on the page.");
          return;
        }

        let stallId = stallIdElement.value;
        if (!stallId) {
          console.error("Error: stallId is empty.");
          alert("Please enter a valid stall ID.");
          return;
        }

        fetch(`/update-location/${stallId}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken()
          },
          body: `latitude=${latitude}&longitude=${longitude}`
        })
        .then(response => {
          if (!response.ok) {
            return response.json().then(errData => {
              console.error("Server error:", response.status, errData);
              throw new Error(`Failed to update location: ${response.status} - ${JSON.stringify(errData)}`);
            });
          }
          return response.json();
        })
        .then(data => {
          console.log("Location updated:", data);
          if (data.success) {
            alert("Location updated successfully!");

            // Update the displayed latitude and longitude on the page
            let latElement = document.getElementById("lat");
            let lngElement = document.getElementById("lng");
            if (latElement && lngElement) {
              latElement.innerText = latitude.toFixed(6); // Update with retrieved latitude
              lngElement.innerText = longitude.toFixed(6); // Update with retrieved longitude

              // Update the Google Maps link
              let mapsBtn = document.getElementById("openMapsBtn");
              if (mapsBtn) {
                mapsBtn.href = `https://www.google.com/maps?q=${latitude},${longitude}`;
                mapsBtn.style.display = "inline-block"; // Make sure the button is visible
              }
            }

            // Update the marker on the map if the map is initialized
            if (typeof map !== 'undefined' && typeof marker !== 'undefined') {
              const newLatLng = { lat: latitude, lng: longitude };
              marker.setPosition(newLatLng);
              map.setCenter(newLatLng);
            } else {
              console.warn("Map object or marker is not initialized yet. Location updated in data but not on the map.");
              // Optionally, you could re-initialize the map here if needed
              // initMap();
            }

          } else {
            alert(`Failed to update location: ${data.error || 'Unknown error'}`);
          }
        })
        .catch(error => {
          console.error("Error:", error);
          alert("Failed to update location. Please try again.");
        });
      },
      function (error) {
        let errorMessage = "Failed to retrieve location: ";
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage += "User denied the request for Geolocation.";
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage += "Location information is unavailable.";
            break;
          case error.TIMEOUT:
            errorMessage += "The request to get user location timed out.";
            break;
          case error.UNKNOWN_ERROR:
            errorMessage += "An unknown error occurred.";
            break;
        }
        alert(errorMessage);
        console.error("Failed to retrieve location:", error);
      }
    );
  }


// Map Markers // Map display // Map 

    let map;
    let marker;
  
    function initMap() {
      var latElement = document.getElementById("lat");
      var lngElement = document.getElementById("lng");
  
      if (!latElement || !lngElement) {
        console.error("Latitude or Longitude elements not found in the DOM.");
        return;
      }
  
      var lat = parseFloat(latElement.innerText.trim());
      var lng = parseFloat(lngElement.innerText.trim());
  
      if (isNaN(lat) || isNaN(lng)) {
        console.warn("Invalid latitude/longitude values. Defaulting to (0,0).");
        lat = 0;
        lng = 0;
      }
  
      const myLatLng = { lat: lat, lng: lng };
      map = new google.maps.Map(document.getElementById("map"), {
        zoom: 15,
        center: myLatLng
      });
  
      marker = new google.maps.Marker({
        position: myLatLng,
        map: map,
        title: "{{ stall.name }}"
      });
    }
  
    document.addEventListener("DOMContentLoaded", function () {
      let lat = document.getElementById("lat").innerText.trim();
      let lng = document.getElementById("lng").innerText.trim();
      let mapsBtn = document.getElementById("openMapsBtn");
  
      if (lat && lng && lat !== "0" && lng !== "0") {
        mapsBtn.href = `https://www.google.com/maps?q=${{ lat }},{{ lng }}`;
      } else {
        mapsBtn.style.display = "none"; // Hide the button if location is not available
      }
    });


  
// Update quantity // Remove // Add item // remove item 
function updateQuantity(cartItemId, change) {
    fetch(`/cart/update-quantity/${cartItemId}/${change}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`quantity-${cartItemId}`).innerText = data.quantity;
            document.getElementById(`total-${cartItemId}`).innerText = data.total_price;
            document.getElementById('cart-total').innerText = data.cart_total;
        }
    })
    .catch(error => console.error('Error:', error));
}

function removeFromCart(cartItemId) {
    fetch(`/cart/remove/${cartItemId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`cart-item-${cartItemId}`).remove();
            document.getElementById('cart-total').innerText = data.cart_total;
        }
    })
    .catch(error => console.error('Error:', error));
}


// Order udate // owner order // process // pending // completed
function updateOrderStatus(orderId, status) {
    fetch(`/order/update-status/${orderId}/${status}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`status-${orderId}`).innerText = data.status;
            alert(`Order ${data.order_number} status updated to ${data.status}`);
            
            // Remove order from the list if it's marked as 'done'
            if (data.status === 'done') {
                document.getElementById(`order-${orderId}`).remove();
            }
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the order status.');
    });
}


// Cart PAge // CArt // QR //
function generateQR(totalAmount, upiOwner) {
    let upiId = upiOwner;
    let amount = totalAmount;
    
    console.log("Debug: Total Amount =", totalAmount);

    if (amount <= 0) {
        alert("Invalid amount! Please check your cart.");
        return;
    }

    let upiUrl = `upi://pay?pa=${upiId}&pn=StallOwner&am=${amount}&cu=INR`;
    let qrCodeUrl = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" + encodeURIComponent(upiUrl);

    document.getElementById("upi-qr").src = qrCodeUrl;
    document.getElementById("upi-qr").style.display = "block";
    
    checkPaymentStatus();
}

function checkPaymentStatus(transactionId) {
    fetch(`/verify_payment?transaction_id=${transactionId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("✅ Payment verified, creating order...");
            createOrder();
        } else {
            console.error("❌ Payment verification failed!");
            alert("Payment verification failed. Please contact support.");
        }
    })
    .catch(error => console.error("❌ Error verifying payment:", error));
}

function createOrder() {
    fetch("/create_order", { method: "POST" })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("✅ Order created successfully!");
            alert("Your order has been placed!");
            document.getElementById("qr-code").style.display = "none";  // Hide QR
        } else {
            console.error("❌ Order creation failed:", data.error);
            alert("Order creation failed. Please contact support.");
        }
    })
    .catch(error => console.error("❌ Error creating order:", error));
}


function notifyStallOwner() {
    fetch('/notify-stall-owner/', {
        method: "POST",
        headers: { "X-CSRFToken": "{{ csrf_token }}", "Content-Type": "application/json" },
        body: JSON.stringify({ cart_id: "{{ cart.id }}", stall_owner: "{{ cart.related.owner.upi_id }}" })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "NOTIFICATION_SENT") {
            alert("Stall owner has been notified!");
        }
    });
}


// Edit map // pin update // pin drag // 
function initMap() {
    // Get latitude & longitude from hidden fields
    var latField = document.getElementById('latitude');
    var lngField = document.getElementById('longitude');

    var lat = parseFloat(latField.value);
    var lng = parseFloat(lngField.value);

    // Use a default location if coordinates are missing (Pune, India)
    if (isNaN(lat) || isNaN(lng)) {
        lat = 18.5204;
        lng = 73.8567;
        latField.value = lat;
        lngField.value = lng;
    }

    // Initialize the map
    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: lat, lng: lng },
        zoom: 15
    });

    // Add a draggable marker
    var marker = new google.maps.Marker({
        position: { lat: lat, lng: lng },
        map: map,
        draggable: true
    });

    // Update hidden fields when marker is moved
    google.maps.event.addListener(marker, 'dragend', function (event) {
        latField.value = event.latLng.lat();
        lngField.value = event.latLng.lng();

        // Update UI with new values
        document.getElementById('lat_display').innerText = event.latLng.lat();
        document.getElementById('lng_display').innerText = event.latLng.lng();
        
        console.log("Updated Latitude:", latField.value, "Updated Longitude:", lngField.value);
    });
}   

