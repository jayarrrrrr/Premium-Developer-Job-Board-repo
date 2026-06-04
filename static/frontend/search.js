const jobList = document.querySelector('#job-list');
const paginationControls = document.querySelector('#pagination-controls');
const searchForm = document.querySelector('#search-form');
const searchInput = document.querySelector('#search-input');
const locationInput = document.querySelector('#location-input');
const template = document.querySelector('#job-card-template');

console.log('[search.js] DOM elements resolved:', {
  jobList,
  paginationControls,
  searchForm,
  searchInput,
  locationInput,
  template,
});

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
  console.log('[search.js] fetchJobs: requesting', url);
  const response = await fetch(url, { credentials: 'same-origin' });
  console.log('[search.js] fetchJobs: response status', response.status, response.ok);
  if (!response.ok) {
    jobList.innerHTML = '<p>Unable to load jobs at this time.</p>';
    return null;
  }
  const data = await response.json();
  console.log('[search.js] fetchJobs: data received', data);
  return data;
}

function updateUrl(params) {
  const query = buildQuery(params);
  const newUrl = `${window.location.pathname}?${query}`;
  window.history.replaceState({}, '', newUrl);
}

function getCompanyInitials(company) {
  try {
    const name = (company || 'C').toString();
    return name
      .split(' ')
      .map((word) => word[0] || '')
      .slice(0, 2)
      .join('')
      .toUpperCase() || 'C';
  } catch (e) {
    console.warn('[search.js] getCompanyInitials: error processing initials', e);
    return 'C';
  }
}

function getJobTags(job) {
  const tags = []; 
  try {
    const title = (job?.title || '').toLowerCase();
    const location = (job?.location || '').toLowerCase();
    if (title.includes('remote') || location.includes('remote')) tags.push('Remote');
    if (title.includes('senior')) tags.push('Senior');
    if (title.includes('backend') || title.includes('api')) tags.push('Backend');
    if (title.includes('django')) tags.push('Django');
    if (title.includes('python')) tags.push('Python');
    if (title.includes('react')) tags.push('React');
    if (!tags.length) tags.push('Full-Time');
  } catch (e) {
    console.warn('[search.js] getJobTags: error processing tags, using defaults', e);
    tags.push('Full-Time');
  }
  return [...new Set(tags)].slice(0, 6);
}

function renderJobs(data) {
  console.log('[search.js] renderJobs: called with data', data);

  if (!jobList) {
    console.error('[search.js] renderJobs: #job-list element not found in DOM');
    return;
  }
  if (!paginationControls) {
    console.error('[search.js] renderJobs: #pagination-controls element not found in DOM');
    return;
  }
  if (!template) {
    console.error('[search.js] renderJobs: #job-card-template element not found in DOM');
    return;
  }

  jobList.innerHTML = '';

  if (!data || !Array.isArray(data.results)) {
    console.warn('[search.js] renderJobs: data is missing or results is not an array', data);
    jobList.innerHTML = '<div class="card-modern" style="text-align: center; padding: 3rem 2rem;"><p class="eyebrow">No results</p><h2>Unable to load jobs at this time.</h2></div>';
    paginationControls.innerHTML = '';
    return;
  }

  if (data.results.length === 0) {
    console.log('[search.js] renderJobs: no jobs matched the query');
    jobList.innerHTML = '<div class="card-modern" style="text-align: center; padding: 3rem 2rem;"><p class="eyebrow">No results</p><h2>No jobs match your search.</h2><p class="hero-text">Try adjusting your search terms or filters.</p></div>';
    paginationControls.innerHTML = '';
    return;
  }

  console.log('[search.js] renderJobs: rendering', data.results.length, 'of', data.count, 'total jobs');

  let successCount = 0;
  let errorCount = 0;

  data.results.forEach((job, index) => {
    if (!job || !job.id) {
      console.error('[search.js] renderJobs: job object is invalid at index', index, job);
      errorCount++;
      return;
    }

    try {
      const clone = template.content ? document.importNode(template.content, true) : template.cloneNode(true);
      
      // Helper to safely set text content
      const setSafeText = (selector, value, defaultValue = 'N/A') => {
        try {
          const el = clone.querySelector(selector);
          if (el) {
            el.textContent = value || defaultValue;
            return true;
          }
          console.warn(`[search.js] renderJobs: Missing selector ${selector} for job ${job.id}`);
          return false;
        } catch (e) {
          console.error(`[search.js] renderJobs: Error setting ${selector}:`, e);
          return false;
        }
      };

      // Helper to safely set attribute
      const setSafeAttr = (selector, attrName, value) => {
        try {
          const el = clone.querySelector(selector);
          if (el) {
            el[attrName] = value;
            return true;
          }
          return false;
        } catch (e) {
          console.error(`[search.js] renderJobs: Error setting ${attrName} on ${selector}:`, e);
          return false;
        }
      };

      // Generic safe setter for textContent to avoid null reference errors
      const safeSetText = (el, value, defaultValue = '') => {
        try {
          if (!el) return false;
          if (typeof el.textContent === 'undefined') return false;
          el.textContent = value || defaultValue;
          return true;
        } catch (e) {
          console.warn('[search.js] safeSetText: could not set textContent', e, el);
          return false;
        }
      };

      // Set all required fields
      const titleOk = setSafeText('.job-title', job.title, 'Untitled Position');
      const companyOk = setSafeText('.company-name', job.company, 'Unknown Company');
      const summaryOk = setSafeText('.job-summary', job.summary, 'Exciting opportunity to join our team.');
      const locationOk = setSafeText('.location-badge', job.location, 'Remote');
      const employmentOk = setSafeText('.badge-type', job.employment_type, 'Full-Time');
      const salaryOk = setSafeText('.job-salary', job.salary_range, 'Competitive');

      // Handle logo
      try {
        const logoImage = clone.querySelector('.company-logo');
        const logoInitial = clone.querySelector('.company-initial');
        if (logoImage) {
          if (job.logo) {
            logoImage.src = job.logo;
            logoImage.style.display = 'block';
            if (logoInitial) {
              logoInitial.style.display = 'none';
            }
          } else {
            logoImage.style.display = 'none';
            if (logoInitial) {
              logoInitial.style.display = 'block';
              safeSetText(logoInitial, getCompanyInitials(job.company || 'Unknown'));
            }
          }
        }
      } catch (e) {
        console.warn('[search.js] renderJobs: Error handling logo for job', job.id, e);
      }

      // Handle remote badge
      try {
        const badgeRemote = clone.querySelector('.badge-remote');
        if (badgeRemote) {
          const isRemote = job.location && job.location.toLowerCase().includes('remote');
          safeSetText(badgeRemote, isRemote ? 'Remote' : 'On-site');
        }
      } catch (e) {
        console.warn('[search.js] renderJobs: Error setting remote badge for job', job.id, e);
      }

      // Handle skill chips
      try {
        const skillsContainer = clone.querySelector('.skills-chips');
        if (skillsContainer) {
          skillsContainer.innerHTML = '';
          getJobTags(job).forEach((tag) => {
            const chip = document.createElement('span');
            chip.className = 'skill-chip';
            safeSetText(chip, tag);
            skillsContainer.appendChild(chip);
          });
        }
      } catch (e) {
        console.warn('[search.js] renderJobs: Error handling skills for job', job.id, e);
      }

      // Handle apply button
      try {
        const applyBtn = clone.querySelector('.btn-card-apply');
        if (applyBtn) {
          if (job.application_link && job.application_link.startsWith('http')) {
            applyBtn.href = job.application_link;
            safeSetText(applyBtn, 'Apply now');
            applyBtn.target = '_blank';
            applyBtn.rel = 'noopener noreferrer';
          } else {
            applyBtn.href = '/upgrade/';
            safeSetText(applyBtn, 'Premium to apply');
            applyBtn.style.opacity = '0.6';
          }
        }
      } catch (e) {
        console.warn('[search.js] renderJobs: Error handling apply button for job', job.id, e);
      }

      // Handle save button
      try {
        const saveBtn = clone.querySelector('.card-save-btn');
        if (saveBtn) {
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
                saveBtn.classList.toggle('saved', result.saved);
                const svg = saveBtn.querySelector('svg path');
                if (svg) {
                  if (result.saved) {
                    svg.style.fill = 'currentColor';
                    saveBtn.setAttribute('data-saved', 'true');
                  } else {
                    svg.style.fill = 'none';
                    saveBtn.removeAttribute('data-saved');
                  }
                }
              } else if (response.status === 401) {
                window.location.href = '/login/';
              }
            } catch (error) {
              console.error('[search.js] saveBtn click: error saving job', job.id, error);
            }
          });
        }
      } catch (e) {
        console.warn('[search.js] renderJobs: Error handling save button for job', job.id, e);
      }

      // Only log critical missing fields
      if (!titleOk || !companyOk) {
        console.error(`[search.js] renderJobs: Critical fields missing for job ${job.id}`);
        errorCount++;
        return;
      }

      jobList.appendChild(clone);
      successCount++;
    } catch (error) {
      console.error(`[search.js] renderJobs: Fatal error rendering job ${job.id}:`, error, job);
      errorCount++;
    }
  });

  console.log(`[search.js] renderJobs: Rendered ${successCount} jobs successfully, ${errorCount} errors`);
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
    safeSetText(link, text);
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
