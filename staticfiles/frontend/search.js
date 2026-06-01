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
  if (!data || data.results.length === 0) {
    jobList.innerHTML = '<p>No jobs match your search.</p>';
    paginationControls.innerHTML = '';
    return;
  }

  data.results.forEach((job) => {
    const clone = template.content.cloneNode(true);
    clone.querySelector('.job-title').textContent = job.title;
    clone.querySelector('.job-company').textContent = job.company;
    clone.querySelector('.job-location').textContent = job.location;
    clone.querySelector('.job-summary').textContent = job.summary;
    const logoImage = clone.querySelector('.logo-image');
    const logoInitials = clone.querySelector('.logo-initials');
    if (job.logo) {
      logoImage.src = job.logo;
      logoImage.classList.add('visible');
      logoInitials.textContent = '';
    } else {
      logoImage.classList.remove('visible');
      logoInitials.textContent = getCompanyInitials(job.company);
    }

    const tagsContainer = clone.querySelector('.job-tags');
    tagsContainer.innerHTML = '';
    getJobTags(job).forEach((tag) => {
      const badge = document.createElement('span');
      badge.className = 'job-tag';
      badge.textContent = tag;
      tagsContainer.appendChild(badge);
    });

    const salaryText = job.salary_range || 'Premium members only. Upgrade to view salary details.';
    const salaryElement = clone.querySelector('.job-salary');
    salaryElement.textContent = salaryText;
    if (salaryText.toLowerCase().includes('premium')) {
      salaryElement.classList.add('job-locked');
    }

    const applicationContainer = clone.querySelector('.job-application');
    applicationContainer.innerHTML = '';
    if (job.application_link && job.application_link.startsWith('http')) {
      const applyButton = document.createElement('a');
      applyButton.href = job.application_link;
      applyButton.target = '_blank';
      applyButton.rel = 'noopener noreferrer';
      applyButton.className = 'apply-button';
      applyButton.textContent = 'Apply now';
      applicationContainer.appendChild(applyButton);
    } else {
      const lockedMessage = document.createElement('span');
      lockedMessage.className = 'job-locked';
      lockedMessage.textContent = job.application_link || 'Premium members only. Upgrade to access application details.';
      applicationContainer.appendChild(lockedMessage);

      const upgradeLink = document.createElement('a');
      upgradeLink.href = '/upgrade/';
      upgradeLink.className = 'apply-button apply-upgrade';
      upgradeLink.textContent = 'Upgrade Now';
      applicationContainer.appendChild(upgradeLink);
    }

    jobList.appendChild(clone);
  });

  renderPagination(data);
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
