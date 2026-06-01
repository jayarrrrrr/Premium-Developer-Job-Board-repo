(function(){
  const toggle = document.querySelector('.profile-toggle');
  const dropdown = document.querySelector('.profile-dropdown');

  if (!toggle || !dropdown) return;

  function openDropdown() {
    dropdown.setAttribute('data-open','true');
    toggle.setAttribute('aria-expanded','true');
  }
  function closeDropdown() {
    dropdown.setAttribute('data-open','false');
    toggle.setAttribute('aria-expanded','false');
  }

  toggle.addEventListener('click', function(e){
    const isOpen = dropdown.getAttribute('data-open') === 'true';
    if (isOpen) closeDropdown(); else openDropdown();
  });

  // Close on outside click
  document.addEventListener('click', function(e){
    if (!dropdown.contains(e.target) && !toggle.contains(e.target)) {
      closeDropdown();
    }
  });

  // Close on ESC
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape') closeDropdown(); });

  // Highlight active menu item by matching current path
  try {
    const items = dropdown.querySelectorAll('.dropdown-item');
    const path = window.location.pathname.replace(/\/+$/,'');
    items.forEach(a=>{
      try{
        const href = a.getAttribute('href') || (a.querySelector('form a') && a.querySelector('form a').getAttribute('href'));
        if (!href) return;
        const hrefPath = new URL(href, window.location.origin).pathname.replace(/\/+$/,'');
        if (hrefPath === path) a.classList.add('active');
      }catch(e){}
    });
  } catch(e){/* ignore */}

})();
