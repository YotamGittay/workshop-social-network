import { useState } from 'react'
import * as api from '../api'

export default function NewPost({ meId, onPosted, onError }) {
  const [text, setText] = useState('')
  const [image, setImage] = useState(null)
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    if (!text.trim()) return
    setBusy(true)
    try {
      await api.createPost(meId, text, image)
      setText('')
      setImage(null)
      e.target.reset()
      onPosted()
    } catch (err) {
      onError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="panel new-post" onSubmit={submit}>
      <textarea
        placeholder="What's happening?"
        value={text}
        maxLength={1000}
        onChange={(e) => setText(e.target.value)}
      />
      <div className="new-post-actions">
        <input
          type="file"
          accept="image/jpeg,image/png,image/gif,image/webp"
          onChange={(e) => setImage(e.target.files[0] || null)}
        />
        <button className="btn" type="submit" disabled={busy || !text.trim()}>
          {busy ? 'Posting…' : 'Post'}
        </button>
      </div>
    </form>
  )
}
