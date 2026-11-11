export interface SSEEvent {
  event: string
  data: string
}

// Read complete SSE events, independent of network chunk and newline boundaries.
export async function readSSE(
  stream: ReadableStream<Uint8Array>,
  onEvent: (event: SSEEvent) => boolean | void,
): Promise<void> {
  const reader = stream.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let eventName = ''
  let data: string[] = []
  let stopped = false
  let ended = false

  function dispatch() {
    if (data.length > 0) {
      stopped = onEvent({ event: eventName || 'message', data: data.join('\n') }) === false
    }
    eventName = ''
    data = []
  }

  function processLine(line: string) {
    if (line === '') {
      dispatch()
      return
    }
    if (line.startsWith(':')) return
    const colon = line.indexOf(':')
    const field = colon === -1 ? line : line.slice(0, colon)
    let value = colon === -1 ? '' : line.slice(colon + 1)
    if (value.startsWith(' ')) value = value.slice(1)
    if (field === 'data') data.push(value)
    if (field === 'event') eventName = value
  }

  function processBuffer(final = false) {
    while (!stopped) {
      const index = buffer.search(/[\r\n]/)
      if (index === -1) break
      // A CRLF separator may itself be split across network chunks.
      if (!final && buffer[index] === '\r' && index === buffer.length - 1) break
      const separatorLength = buffer[index] === '\r' && buffer[index + 1] === '\n' ? 2 : 1
      const line = buffer.slice(0, index)
      buffer = buffer.slice(index + separatorLength)
      processLine(line)
    }
    if (final && !stopped) {
      if (buffer) processLine(buffer)
      buffer = ''
      dispatch()
    }
  }

  try {
    while (!stopped) {
      const { done, value } = await reader.read()
      if (done) {
        ended = true
        buffer += decoder.decode()
        processBuffer(true)
        break
      }
      buffer += decoder.decode(value, { stream: true })
      processBuffer()
    }
  } finally {
    if (!ended) await reader.cancel().catch(() => {})
    reader.releaseLock()
  }
}
