const API_BASE = '/api';

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API_BASE}${path}`, opts);
  const data = await res.json();
  if (!res.ok) throw { status: res.status, data };
  return data;
}

export const api = {
  createArticle: (name) => request('POST', '/articles/create/', { name }),
  getArticle: (name) => request('GET', `/articles/${encodeURIComponent(name)}/`),
  myArticles: () => request('GET', '/articles/mine/'),
  searchArticles: (query) => request('GET', `/articles/search/?q=${encodeURIComponent(query)}`),
  getVersion: (name) => request('GET', `/versions/${encodeURIComponent(name)}/`),
  createVersionFromVersion: (sourceVersionName, newVersionName) =>
    request('POST', '/versions/create/', {
      source_version_name: sourceVersionName,
      new_version_name: newVersionName,
    }),
  createEmptyVersion: (articleName, versionName) =>
    request('POST', '/versions/create-empty/', {
      article_name: articleName,
      version_name: versionName,
    }),
  updateVersion: (versionName, content) =>
    request('PATCH', `/versions/${encodeURIComponent(versionName)}/update/`, { content }),
  publishVersion: (versionName) =>
    request('POST', `/versions/${encodeURIComponent(versionName)}/publish/`),
  vote: (articleName, value) =>
    request('POST', '/vote/', { article_name: articleName, value }),
  requestPublish: (versionName) =>
    request('POST', '/publish-requests/create/', { version_name: versionName }),
  listPublishRequests: (articleName) =>
    request('GET', `/publish-requests/article/${encodeURIComponent(articleName)}/`),
  myPublishRequests: (articleName) =>
    request('GET', `/publish-requests/mine/${encodeURIComponent(articleName)}/`),
  approvePublishRequest: (pk) =>
    request('POST', `/publish-requests/${pk}/approve/`),
  rejectPublishRequest: (pk) =>
    request('POST', `/publish-requests/${pk}/reject/`),
  newestArticles: () => request('GET', '/articles/newest/'),
  topRatedArticles: () => request('GET', '/articles/top-rated/'),
  topArticlesByTag: () => request('GET', '/articles/top-by-tag/'),
  wikiContent: async (query) => {
    const res = await fetch(`/wiki/content/?q=${encodeURIComponent(query)}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
    });
    const data = await res.json();
    if (!res.ok) throw { status: res.status, data };
    return data;
  },
};
