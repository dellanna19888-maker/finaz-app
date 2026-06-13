<template>
  <nav class="navbar">
    <div class="brand">
      <span class="brand-icon">💰</span>
      <span class="brand-name">FinazApp</span>
    </div>
    <div class="nav-links">
      <RouterLink to="/" class="nav-link">Dashboard</RouterLink>
      <RouterLink to="/transactions" class="nav-link">Transaktionen</RouterLink>
      <RouterLink to="/budget" class="nav-link">Budget</RouterLink>
      <RouterLink to="/reports" class="nav-link">Berichte</RouterLink>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 60px;
  background: #1a1a2e;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.brand-icon { font-size: 1.5rem; }
.brand-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: 0.02em;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

.nav-link {
  padding: 0.4rem 1rem;
  border-radius: 6px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.nav-link:hover { color: #e2e8f0; background: rgba(255,255,255,0.05); }
.nav-link.router-link-active { color: #60a5fa; background: rgba(96,165,250,0.1); }
</style>
