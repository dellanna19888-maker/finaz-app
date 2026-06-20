import { describe, it, expect } from 'vitest'
import { parseActions, stripActions, actionLabel } from '../src/lib/actions'

const withBlock = [
  'Klar, ich lege das an.',
  '```action',
  '{"tool":"add_income","args":{"amount":800,"category":"Sponsoring"}}',
  '```',
].join('\n')

describe('parseActions', () => {
  it('extrahiert einen gültigen Aktionsblock', () => {
    const acts = parseActions(withBlock)
    expect(acts).toHaveLength(1)
    expect(acts[0].tool).toBe('add_income')
    expect(acts[0].args.amount).toBe(800)
  })

  it('ignoriert ungültiges JSON im Block', () => {
    const acts = parseActions('```action\n{not json}\n```')
    expect(acts).toHaveLength(0)
  })

  it('liefert leeres Array ohne Block', () => {
    expect(parseActions('Nur Text, keine Aktion.')).toHaveLength(0)
  })
})

describe('stripActions', () => {
  it('entfernt den Aktionsblock aus dem Anzeigetext', () => {
    const out = stripActions(withBlock)
    expect(out).toContain('Klar, ich lege das an.')
    expect(out).not.toContain('add_income')
    expect(out).not.toContain('```')
  })
})

describe('actionLabel', () => {
  it('beschriftet Finanz-Aktionen verständlich', () => {
    expect(actionLabel({ tool: 'add_income', args: { amount: 800, category: 'Sponsoring' } })).toContain('Einnahme buchen')
    expect(actionLabel({ tool: 'add_expense', args: { amount: 200 } })).toContain('Ausgabe buchen')
    expect(actionLabel({ tool: 'delete_transaction', args: { id: 'f1' } })).toContain('f1')
  })
  it('normalisiert negative Beträge zu positiv', () => {
    expect(actionLabel({ tool: 'add_expense', args: { amount: -50 } })).toContain('50')
  })
  it('beschriftet Content-Aktionen', () => {
    expect(actionLabel({ tool: 'add_task', args: { title: 'Neues Video' } })).toContain('Neues Video')
  })
})
