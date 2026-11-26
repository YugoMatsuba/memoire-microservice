import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import readAuthResponse from './readAuthResponse'

function useRegister() {
  const navigate = useNavigate()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState('')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    if (String(formData.get('password') ?? '').length < 16) {
      setMessage('Password must be at least 16 characters.')
      return
    }
    setIsSubmitting(true)
    setMessage('')

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.get('email'),
          password: formData.get('password'),
          username: formData.get('username'),
        }),
      })

      const username = await readAuthResponse(response)
      navigate('/welcome', { replace: true, state: { username } })
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Unable to register. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return { handleSubmit, isSubmitting, message }
}

export default useRegister
