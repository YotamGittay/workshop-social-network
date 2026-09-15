import { useCallback, useEffect, useState } from 'react'
import * as api from './api'
import UserList from './components/UserList'
import NewPost from './components/NewPost'
import Feed from './components/Feed'

export default function App() {
  const [users, setUsers] = useState([])
  const [meId, setMeId] = useState(() => Number(localStorage.getItem('meId')) || null)
  const [following, setFollowing] = useState([])
  const [feed, setFeed] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getUsers().then(setUsers).catch((e) => setError(e.message))
  }, [])

  const refresh = useCallback(() => {
    if (!meId) return
    Promise.all([api.getFollowing(meId), api.getFeed(meId)])
      .then(([followingUsers, posts]) => {
        setFollowing(followingUsers)
        setFeed(posts)
        setError(null)
      })
      .catch((e) => setError(e.message))
  }, [meId])

  useEffect(() => {
    refresh()
    const timer = setInterval(refresh, 5000)
    return () => clearInterval(timer)
  }, [refresh])

  function pickUser(id) {
    setMeId(id)
    localStorage.setItem('meId', String(id))
  }

  async function toggleFollow(targetId, isFollowing) {
    try {
      if (isFollowing) {
        await api.unfollow(meId, targetId)
      } else {
        await api.follow(meId, targetId)
      }
      refresh()
    } catch (e) {
      setError(e.message)
    }
  }

  const me = users.find((u) => u.id === meId) || null

  return (
    <div className="app">
      <header className="topbar">
        <h1>Workshop Social</h1>
        <label className="switcher">
          Posting as{' '}
          <select value={meId || ''} onChange={(e) => pickUser(Number(e.target.value))}>
            <option value="" disabled>
              pick a user…
            </option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.display_name} (@{u.username})
              </option>
            ))}
          </select>
        </label>
      </header>

      {error && <div className="error">{error}</div>}

      {!me ? (
        <p className="hint">Pick who you are (top right) to see your feed.</p>
      ) : (
        <div className="layout">
          <aside>
            <UserList
              users={users}
              meId={meId}
              followingIds={new Set(following.map((u) => u.id))}
              onToggle={toggleFollow}
            />
          </aside>
          <main>
            <NewPost meId={meId} onPosted={refresh} onError={setError} />
            <Feed posts={feed} />
          </main>
        </div>
      )}
    </div>
  )
}
