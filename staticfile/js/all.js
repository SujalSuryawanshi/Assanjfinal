// Slider 1 Drag Functionality
const slider1 = document.querySelector('.slider1 .slides1');
let isDragging1 = false;
let startPos1 = 0;
let currentTranslate1 = 0;
let prevTranslate1 = 0;

slider1.addEventListener('touchstart', (e) => {
  isDragging1 = true;
  startPos1 = e.touches[0].clientX;
});

slider1.addEventListener('touchmove', (e) => {
  if (!isDragging1) return;
  const currentPosition = e.touches[0].clientX;
  currentTranslate1 = prevTranslate1 + (currentPosition - startPos1);
  slider1.style.transform = `translateX(${currentTranslate1}px)`;
});

slider1.addEventListener('touchend', () => {
  isDragging1 = false;

  // Snap to closest slide
  const slides = document.querySelectorAll('.slider1 .slide1');
  const slideWidth = slides[0].offsetWidth;
  const totalSlides = slides.length;

  let closestIndex = Math.round(-currentTranslate1 / slideWidth);
  closestIndex = Math.max(0, Math.min(totalSlides - 1, closestIndex));

  currentTranslate1 = -closestIndex * slideWidth;
  prevTranslate1 = currentTranslate1;

  slider1.style.transform = `translateX(${currentTranslate1}px)`;
  slider1.style.transition = 'transform 0.3s ease-in-out'; // Smooth snap
});

// Reset transition on touchstart
slider1.addEventListener('touchstart', () => {
  slider1.style.transition = 'none';
});

// Slider 2 Drag Functionality
const slider2 = document.querySelector('.slider2 .slides2');
let isDragging2 = false;
let startPos2 = 0;
let currentTranslate2 = 0;
let prevTranslate2 = 0;

slider2.addEventListener('touchstart', (e) => {
  isDragging2 = true;
  startPos2 = e.touches[0].clientX;
});

slider2.addEventListener('touchmove', (e) => {
  if (!isDragging2) return;
  const currentPosition = e.touches[0].clientX;
  currentTranslate2 = prevTranslate2 + (currentPosition - startPos2);
  slider2.style.transform = `translateX(${currentTranslate2}px)`;
});

slider2.addEventListener('touchend', () => {
  isDragging2 = false;

  // Snap to closest slide
  const slides = document.querySelectorAll('.slider2 .slide2');
  const slideWidth = slides[0].offsetWidth;
  const totalSlides = slides.length;

  let closestIndex = Math.round(-currentTranslate2 / slideWidth);
  closestIndex = Math.max(0, Math.min(totalSlides - 1, closestIndex));

  currentTranslate2 = -closestIndex * slideWidth;
  prevTranslate2 = currentTranslate2;

  slider2.style.transform = `translateX(${currentTranslate2}px)`;
  slider2.style.transition = 'transform 0.3s ease-in-out'; // Smooth snap
});

// Reset transition on touchstart
slider2.addEventListener('touchstart', () => {
  slider2.style.transition = 'none';
});
