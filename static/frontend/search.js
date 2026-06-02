const jobList = document.querySelector('#job-list');
const paginationControls = document.querySelector('#pagination-controls');
const searchForm = document.querySelector('#search-form');
const searchInput = document.querySelector('#search-input');
const locationInput = document.querySelector('#location-input');
const template = document.querySelector('#job-card-template');

function buildQuery(params) {
  const searchParams = new URLSearchParams();
  if (params.search) searchParams.set('search', params.search);
  if (params.location) searchParams.set('location', params.location);
  if (params.page) searchParams.set('page', params.page);
  return searchParams.toString();
}

async function fetchJobs(params) {
  const query = buildQuery(params);
  const url = `/api/jobs/?${query}`;
  const response = await fetch(url, { credentials: 'same-origin' });
  if (!response.ok) {
    jobList.innerHTML = '<p>Unable to load jobs at this time.</p>';
    return null;
  }
  return response.json();
}

function updateUrl(params) {
  const query = buildQuery(params);
  const newUrl = `${window.location.pathname}?${query}`;
  window.history.replaceState({}, '', newUrl);
}

function getCompanyInitials(company) {
  return company
    .split(' ')
    .map((word) => word[0] || '')
    .slice(0, 2)
    .join('')
    .toUpperCase();
}

function getJobTags(job) {
  const tags = []; 
  const title = job.title.toLowerCase();
  const location = job.location.toLowerCase();
  if (title.includes('remote') || location.includes('remote')) tags.push('Remote');
  if (title.includes('senior')) tags.push('Senior');
  if (title.includes('backend') || title.includes('api')) tags.push('Backend');
  if (title.includes('django')) tags.push('Django');
  if (title.includes('python')) tags.push('Python');
  if (title.includes('react')) tags.push('React');
  if (!tags.length) tags.push('Full-Time');
  return [...new Set(tags)].slice(0, 6);
}

function renderJobs(data) {
  jobList.innerHTML = '';
  console.debug('Job list API response', data);
  if (!data || !Array.isArray(data.results)) {
    jobList.innerHTML = '<div class="card-modern" style="text-align: center; padding: 3rem 2rem;"><p class="eyebrow">No results</p><h2>Unable to load jobs at this time.</h2></div>';
    paginationControls.innerHTML = '';
    return;
  }

  if (data.results.length === 0) {
    jobList.innerHTML = '<div class="card-modern" style="text-align: center; padding: 3rem 2rem;"><p class="eyebrow">No results</p><h2>No jobs match your search.</h2><p class="hero-text">Try adjusting your search terms or filters.</p></div>';
    paginationControls.innerHTML = '';
    return;
  }

  console.debug('Jobs returned', data.count, 'results', data.results.length);
  data.results.forEach((job) => {
    const clone = template.content.cloneNode(true);
    
    // Update job title and company info
    clone.querySelector('.job-title').textContent = job.title;
    clone.querySelector('.company-name').textContent = job.company;
    
    // Update company logo
    const logoImage = clone.querySelector('.company-logo');
    const logoInitial = clone.querySelector('.company-initial');
    if (job.logo) {
      logoImage.src = job.logo;
      logoImage.style.display = 'block';
      logoInitial.style.display = 'none';
    } else {
      logoImage.style.display = 'none';
      logoInitial.style.display = 'block';
      logoInitial.textContent = getCompanyInitials(job.company);
    }
    
    // Update job location
    const locationBadge = clone.querySelector('.location-badge');
    if (locationBadge) {
      locationBadge.textContent = job.location || 'Remote';
    }

    // Update job summary
    clone.querySelector('.job-summary').textContent = job.summary || 'Exciting opportunity to join a growing team.';
    
    // Update employment badges
    const badgeType = clone.querySelector('.badge-type');
    const badgeRemote = clone.querySelector('.badge-remote');
    badgeType.textContent = job.employment_type || 'Full-Time';
    badgeRemote.textContent = job.location?.toLowerCase().includes('remote') ? 'Remote' : 'On-site';
    
    // Update skill chips
    const skillsContainer = clone.querySelector('.skills-chips');
    skillsContainer.innerHTML = '';
    getJobTags(job).forEach((tag) => {
      const chip = document.createElement('span');
      chip.className = 'skill-chip';
      chip.textContent = tag;
      skillsContainer.appendChild(chip);
    });

    // Update salary display
    const salaryText = job.salary_range || '$Competitive';
    const salaryElement = clone.querySelector('.job-salary');
    salaryElement.textContent = salaryText;

    // Update apply button
    const applyBtn = clone.querySelector('.btn-card-apply');
    if (job.application_link && job.application_link.startsWith('http')) {
      applyBtn.href = job.application_link;
      applyBtn.textContent = 'Apply now';
      applyBtn.target = '_blank';
      applyBtn.rel = 'noopener noreferrer';
    } else {
      applyBtn.href = '/upgrade/';
      applyBtn.textContent = 'Premium to apply';
      applyBtn.style.opacity = '0.6';
    }

    // Add save button functionality
    const saveBtn = clone.querySelector('.card-save-btn');
    saveBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      try {
        const response = await fetch(`/api/jobs/job/${job.id}/save/`, {
          method: 'POST',
          credentials: 'same-origin',
          headers: { 'X-CSRFToken': getCookie('csrftoken') },
        });

        if (response.ok) {
          const result = await response.json();
          // Toggle saved state in UI
          saveBtn.classList.toggle('saved', result.saved);
          const svg = saveBtn.querySelector('svg path');
          if (result.saved) {
            svg.style.fill = 'currentColor';
            saveBtn.setAttribute('data-saved', 'true');
          } else {
            svg.style.fill = 'none';
            saveBtn.removeAttribute('data-saved');
          }
        } else if (response.status === 401) {
          window.location.href = '/login/';
        }
      } catch (error) {
        console.error('Error saving job:', error);
      }
    });

    jobList.appendChild(clone);
  });

  renderPagination(data);
}

// Utility function to get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function renderPagination(data) {
  paginationControls.innerHTML = '';
  const page = Number(data.page || 1);
  const totalPages = Math.max(1, Math.ceil(data.count / (data.page_size || 10)));

  const addPageLink = (text, targetPage, disabled = false, active = false) => {
    const link = document.createElement('a');
    link.href = '#';
    link.className = 'page-link';
    if (disabled) link.classList.add('disabled');
    if (active) link.classList.add('active');
    link.textContent = text;
    if (!disabled) {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        const params = getSearchParams();
        params.page = targetPage;
        updateUrl(params);
        loadJobs(params);
      });
    }
    paginationControls.appendChild(link);
  };

  addPageLink('← Previous', Math.max(1, page - 1), page === 1);

  for (let current = 1; current <= totalPages; current += 1) {
    addPageLink(current, current, false, current === page);
  }

  addPageLink('Next →', Math.min(totalPages, page + 1), page === totalPages);
}

function getSearchParams() {
  return {
    search: searchInput.value.trim(),
    location: locationInput.value.trim(),
    page: new URLSearchParams(window.location.search).get('page') || 1,
  };
}

async function loadJobs(params) {
  const data = await fetchJobs(params);
  renderJobs(data);
}

function populateFields() {
  const urlParams = new URLSearchParams(window.location.search);
  searchInput.value = urlParams.get('search') || '';
  locationInput.value = urlParams.get('location') || '';
}

searchForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const params = getSearchParams();
  params.page = 1;
  updateUrl(params);
  await loadJobs(params);
});

window.addEventListener('DOMContentLoaded', async () => {
  populateFields();
  const params = getSearchParams();
  await loadJobs(params);
});
