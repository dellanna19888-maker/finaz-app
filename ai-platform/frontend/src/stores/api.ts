const BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'API-Fehler')
  }
  return res.json() as Promise<T>
}

export const api = {
  chat: {
    send: (messages: Array<{role: string; content: string}>, domain = 'general') =>
      request('/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages, domain }),
      }),
    domains: () => request<{ domains: Array<{id:string;name:string;icon:string}> }>('/chat/domains'),
  },

  text: {
    classify: (text: string, labels?: string[], domain = 'general', multi_label = false) =>
      request('/classify/text/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, labels, domain, multi_label }),
      }),
    sentiment: (text: string) =>
      request(`/classify/text/sentiment?text=${encodeURIComponent(text)}`, { method: 'POST' }),
    labels: (domain: string) =>
      request<{ domain: string; labels: string[] }>(`/classify/text/labels/${domain}`),
  },

  image: {
    classify: (file: File, domain = 'general', customLabels?: string) => {
      const form = new FormData()
      form.append('file', file)
      form.append('domain', domain)
      if (customLabels) form.append('custom_labels', customLabels)
      return request('/classify/image/', { method: 'POST', body: form })
    },
  },

  documents: {
    upload: (file: File) => {
      const form = new FormData()
      form.append('file', file)
      return request('/documents/upload', { method: 'POST', body: form })
    },
    summarize: (docId: string) =>
      request(`/documents/summarize/${docId}`, { method: 'POST' }),
    qa: (documentId: string, question: string) =>
      request('/documents/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_id: documentId, question }),
      }),
  },

  training: {
    start: (config: object, trainingData: File) => {
      const form = new FormData()
      form.append('config_json', JSON.stringify(config))
      form.append('training_data', trainingData)
      return request('/training/start', { method: 'POST', body: form })
    },
    jobs: () => request<{ jobs: any[] }>('/training/jobs'),
    job: (jobId: string) => request(`/training/jobs/${jobId}`),
    deleteJob: (jobId: string) =>
      request(`/training/jobs/${jobId}`, { method: 'DELETE' }),
    models: () => request<{ models: any }>('/training/models'),
    dataFormat: () => request('/training/data-format'),
  },

  models: {
    list: () => request<{ pretrained: any[]; custom: any[]; total: number }>('/models/'),
    get: (id: string) => request(`/models/${id}`),
  },
}
