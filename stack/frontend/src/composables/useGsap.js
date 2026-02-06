import { gsap } from 'gsap'

// Module-level singleton: design token defaults (resolved once, shared across components)
let _defaults = null

function resolveDefaults() {
  if (_defaults) return _defaults
  const style = getComputedStyle(document.documentElement)
  const get = (name) => style.getPropertyValue(name).trim()

  _defaults = {
    durationPanel: parseFloat(get('--duration-panel')) || 0.4,
    durationPill: parseFloat(get('--duration-pill')) || 0.2,
    durationDrawer: parseFloat(get('--duration-drawer')) || 0.3,
    easePanel: get('--ease-panel') || 'power2.out',
    easePill: get('--ease-pill') || 'power1.inOut',
  }
  return _defaults
}

/**
 * GSAP composable for Vue 3 Composition API.
 *
 * Thin wrapper — provides the gsap instance, resolved design token defaults,
 * and behavior helpers. Does NOT manage gsap.context() — components own that
 * using the standard GSAP + Vue pattern.
 *
 * Usage in components:
 *   const { gsap, defaults, slideTo, resizeTo } = useGsap()
 *
 *   let ctx
 *   onMounted(() => {
 *     ctx = gsap.context(() => { }, containerRef.value)
 *   })
 *   onUnmounted(() => ctx?.revert())
 *
 *   // In watchers/handlers — ctx.add() auto-collects animations:
 *   ctx.add(() => { resizeTo([...], opts) })
 */
export function useGsap() {
  const defaults = new Proxy({}, {
    get(_, prop) {
      return (_defaults || resolveDefaults())[prop]
    }
  })

  /** Choreographed horizontal slide with backdrop. Call inside ctx.add() for cleanup. */
  function slideTo(el, backdropEl, open, { fromLeft = false } = {}) {
    const d = _defaults || resolveDefaults()
    const offScreen = fromLeft ? '-100%' : '100%'
    const tl = gsap.timeline({
      defaults: { duration: d.durationDrawer, ease: d.easePanel }
    })

    if (open) {
      tl.set(el, { display: 'block' })
        .fromTo(backdropEl, { opacity: 0 }, { opacity: 1, duration: d.durationDrawer * 0.5 })
        .fromTo(el, { x: offScreen }, { x: '0%' }, '<')
    } else {
      tl.to(el, { x: offScreen })
        .to(backdropEl, { opacity: 0, duration: d.durationDrawer * 0.5 }, '<')
        .set(el, { display: 'none' })
    }

    return tl
  }

  /** Choreographed flex-basis resize. Call inside ctx.add() for cleanup. */
  function resizeTo(targets, opts = {}) {
    const d = _defaults || resolveDefaults()
    const tl = gsap.timeline({
      defaults: { ease: d.easePanel }
    })

    // Instant setup at position 0
    if (opts.overlayEl) tl.set(opts.overlayEl, { display: 'block', opacity: 1 }, 0)
    targets.forEach(({ el }) => tl.set(el, { overflow: 'hidden' }, 0))

    // Animate flex-basis with explicit fromTo
    targets.forEach(({ el, from, to }) => {
      const startVal = from || getComputedStyle(el).flexBasis
      tl.fromTo(el, { flexBasis: startVal }, { flexBasis: to, duration: d.durationPanel }, 0)
    })

    // Fade scrub panel
    if (opts.fadeEl) {
      tl.to(opts.fadeEl, {
        opacity: opts.fadeOut ? 0 : 1,
        duration: d.durationPanel * 0.6,
      }, opts.fadeOut ? 0 : d.durationPanel * 0.4)
    }

    // Cleanup after animation
    tl.call(() => targets.forEach(({ el }) => { el.style.overflow = '' }))

    if (opts.overlayEl) {
      tl.to(opts.overlayEl, { opacity: 0, duration: 0.1 })
        .set(opts.overlayEl, { display: 'none' })
    }

    return tl
  }

  return { gsap, defaults, slideTo, resizeTo }
}
