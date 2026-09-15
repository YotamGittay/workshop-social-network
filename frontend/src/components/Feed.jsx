function ago(iso) {
  const seconds = (Date.now() - new Date(iso).getTime()) / 1000
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

export default function Feed({ posts }) {
  return (
    <div className="panel">
      <h2>Your feed (last 10)</h2>
      {posts.length === 0 ? (
        <p className="hint">No posts yet — follow someone on the left, or wait for the next poll.</p>
      ) : (
        <ul className="feed">
          {posts.map((p) => (
            <li key={p.id} className="post">
              <div className="post-head">
                <strong>{p.author.display_name}</strong>
                <small>
                  @{p.author.username} · {ago(p.created_at)}
                </small>
              </div>
              <p className="post-text">{p.text}</p>
              {p.image_url && <img className="post-image" src={p.image_url} alt="post attachment" />}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
