export default async function readAuthResponse(response: Response) {
  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const detail = data?.detail
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map((error: { msg: string }) => error.msg).join(' ')
        : 'Unable to complete the request. Please try again.'
    throw new Error(message)
  }

  if (typeof data?.user?.username !== 'string') {
    throw new Error('Unexpected server response. Please try again.')
  }

  return data.user.username as string
}
