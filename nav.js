// ── K8 GUIDE — Shared Navigation ─────────────────────────────────────────
// Edit this file to update the nav across ALL pages at once.
// To add a new dropdown item, add a new <li> inside the relevant dropdown-menu.
// To add a new top-level nav item, add a new <a> or <li class="nav-dropdown"> in the nav-links ul.

(function () {
  const NAV_HTML = `
<a href="index.html" class="nav-logo">K8<span>GUIDE</span></a>
<ul class="nav-links">
  <li class="nav-dropdown">
    <a href="characters.html">Characters ▾</a>
    <ul class="dropdown-menu">
      <li><a href="characters.html">Character Roster</a></li>
      <li><a href="weapons.html">Weapons &amp; Best Users</a></li>
    </ul>
  </li>
  <a href="beginner.html">Beginner</a>
  <li class="nav-dropdown">
    <a href="gameguide.html">Game Guide ▾</a>
    <ul class="dropdown-menu">
      <li><a href="gameguide.html">Game Guide</a></li>
      <li><a href="limited.html">Limited Characters</a></li>
    </ul>
  </li>
  <a href="combat.html">Combat</a>
  <a href="socials.html">Socials</a>
</ul>`;

  // Inject nav
  const nav = document.getElementById('main-nav');
  if (nav) nav.innerHTML = NAV_HTML;

  // Highlight active page
  const current = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('#main-nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    if (href === current) {
      link.classList.add('active');
      // If inside a dropdown, also highlight the parent
      const dropdown = link.closest('.nav-dropdown');
      if (dropdown) dropdown.querySelector(':scope > a').classList.add('active');
    }
  });
})();
