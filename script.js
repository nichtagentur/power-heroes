// EUROPE'S POWER HEROES — minimal interactivity

// Reveal hero panels as they scroll into view
const observer = new IntersectionObserver(entries => {
  for (const e of entries) {
    if (e.isIntersecting) {
      e.target.classList.add('in-view');
      observer.unobserve(e.target);
    }
  }
}, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.hero').forEach(el => observer.observe(el));

// Share / mailto fallback
const shareBtn = document.getElementById('shareBtn');
if (shareBtn) {
  shareBtn.addEventListener('click', async () => {
    const shareData = {
      title: "Europe's Power Heroes",
      text: "Eight champions. One mission: power Europe without burning it down.",
      url: location.href,
    };
    if (navigator.share) {
      try { await navigator.share(shareData); }
      catch (err) { fallback(); }
    } else {
      fallback();
    }
  });
}

function fallback() {
  // Open mailto with the page URL pre-filled
  const subject = encodeURIComponent("Europe's Power Heroes");
  const body = encodeURIComponent(
    "Found this — eight characters explaining how Europe is rewiring itself.\n\n" +
    location.href + "\n\n" +
    "Pick one of the four CTAs at the bottom and join the team."
  );
  location.href = `mailto:?subject=${subject}&body=${body}`;
}
