async function req(path, { userId, ...opts } = {}) {
  const headers = { ...(opts.headers || {}) }
  if (userId) headers['X-User-Id'] = String(userId)
  const res = await fetch(path, { ...opts, headers })
  if (!res.ok) {
    let msg = `Request failed (${res.status})`
    try {
      const body = await res.json()
      if (typeof body.detail === 'string') msg = body.detail
    } catch {
      /* keep default message */
    }
    throw new Error(msg)
  }
  if (res.status === 204) return null
  return res.json()
}

export const getUsers = () => req('/api/users')

export const getFollowing = (userId) => req('/api/users/me/following', { userId })

export const follow = (userId, targetId) =>
  req(`/api/follows/${targetId}`, { method: 'POST', userId })

export const unfollow = (userId, targetId) =>
  req(`/api/follows/${targetId}`, { method: 'DELETE', userId })

export const getFeed = (userId) => req('/api/feed', { userId })

export function createPost(userId, text, imageFile) {
  const form = new FormData()
  form.append('text', text)
  if (imageFile) form.append('image', imageFile)
  return req('/api/posts', { method: 'POST', userId, body: form })
}
