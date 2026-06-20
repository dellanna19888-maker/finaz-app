import { describe, it, expect } from 'vitest'
import { evaluate, assess, mapCountryToJurisdiction } from '../src/compliance/gateway'

describe('mapCountryToJurisdiction', () => {
  it('mappt EU/EWR-Länder auf EU', () => {
    expect(mapCountryToJurisdiction('DE')).toBe('EU')
    expect(mapCountryToJurisdiction('fr')).toBe('EU')
    expect(mapCountryToJurisdiction('NO')).toBe('EU') // EWR
  })
  it('mappt UK/US und Unbekanntes', () => {
    expect(mapCountryToJurisdiction('GB')).toBe('UK')
    expect(mapCountryToJurisdiction('UK')).toBe('UK')
    expect(mapCountryToJurisdiction('US')).toBe('US')
    expect(mapCountryToJurisdiction('JP')).toBe('DEFAULT')
    expect(mapCountryToJurisdiction(null)).toBe('DEFAULT')
  })
})

describe('assess', () => {
  it('erkennt PII (E-Mail/IBAN)', () => {
    const r = assess('chat', 'Schreib an max@example.com, IBAN DE89370400440532013000')
    expect(r.findings).toContain('PII_PRESENT')
    expect(r.pii).toContain('email')
    expect(r.pii).toContain('iban')
  })
  it('erkennt verbotene Praktiken und besondere Kategorien', () => {
    expect(assess('chat', 'Massenüberwachung der Bürger').findings).toContain('PROHIBITED_PRACTICE')
    expect(assess('chat', 'Diagnose einer Krankheit des Patienten').findings).toContain('SPECIAL_CATEGORY')
  })
  it('markiert übermäßige Datenmenge oberhalb von maxChars', () => {
    expect(assess('chat', 'x'.repeat(50), 10).findings).toContain('EXCESSIVE_DATA')
  })
})

describe('evaluate', () => {
  it('sauberer Text → PASS', () => {
    const ev = evaluate({ action: 'chat', text: 'Gib mir 5 Video-Ideen.', jurisdiction: 'EU' })
    expect(ev.status).toBe('PASS')
    expect(ev.originalStatus).toBe('PASS')
  })

  it('PII → WARN (Autorisierung erforderlich)', () => {
    const ev = evaluate({ action: 'chat', text: 'Kontakt: max@example.com', jurisdiction: 'EU' })
    expect(ev.originalStatus).toBe('WARN')
    expect(ev.status).toBe('WARN')
    expect(ev.humanAuthorized).toBe(false)
  })

  it('WARN + consent → effektiv PASS, aber originalStatus bleibt WARN', () => {
    const ev = evaluate({ action: 'chat', text: 'Kontakt: max@example.com', jurisdiction: 'EU', consent: true })
    expect(ev.originalStatus).toBe('WARN')
    expect(ev.status).toBe('PASS')
    expect(ev.humanAuthorized).toBe(true)
  })

  it('verbotene Praktik → BLOCK (auch mit consent)', () => {
    const ev = evaluate({ action: 'chat', text: 'Social Scoring der Nutzer', jurisdiction: 'EU', consent: true })
    expect(ev.status).toBe('BLOCK')
    expect(ev.humanAuthorized).toBe(false)
  })

  it('unbekannte Jurisdiktion fällt auf restriktives DEFAULT-Profil zurück', () => {
    const ev = evaluate({ action: 'chat', text: 'max@example.com', jurisdiction: 'ATLANTIS' })
    expect(ev.jurisdiction).toBe('ATLANTIS')
    expect(ev.rulesetLabel).toContain('DSGVO')
    expect(ev.originalStatus).toBe('WARN')
  })
})
