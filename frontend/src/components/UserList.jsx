export default function UserList({ users, meId, followingIds, onToggle }) {
  return (
    <div className="panel">
      <h2>People</h2>
      <ul className="user-list">
        {users.map((u) => {
          if (u.id === meId) {
            return (
              <li key={u.id} className="user-row me">
                <span>
                  {u.display_name} <em>(you)</em>
                </span>
              </li>
            )
          }
          const isFollowing = followingIds.has(u.id)
          return (
            <li key={u.id} className="user-row">
              <span>
                {u.display_name}
                <small>@{u.username}</small>
              </span>
              <button
                className={isFollowing ? 'btn secondary' : 'btn'}
                onClick={() => onToggle(u.id, isFollowing)}
              >
                {isFollowing ? 'Unfollow' : 'Follow'}
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
