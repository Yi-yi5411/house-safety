// Shim for Vue to provide internal APIs that uni-app incorrectly imports
import * as Vue from './node_modules/vue/dist/vue.runtime.esm-bundler.js'

// isInSSRComponentSetup - always false in non-SSR uni-app context
export const isInSSRComponentSetup = false

// injectHook - simplified polyfill
export function injectHook(type, hook, target) {
  if (target) {
    const hooks = target[type] || (target[type] = [])
    hooks.push(hook)
  } else {
    const instance = Vue.getCurrentInstance()
    if (instance) {
      const hooks = instance[type] || (instance[type] = [])
      hooks.push(hook)
    }
  }
}

export default Vue
export * from './node_modules/vue/dist/vue.runtime.esm-bundler.js'
