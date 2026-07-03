import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import path from 'path'

export default defineConfig(({ command, mode }) => {
  const isH5 = process.env.UNI_PLATFORM === 'h5' || !process.env.UNI_PLATFORM

  return {
    plugins: [uni()],
    resolve: {
      alias: isH5 ? {
        vue: path.resolve(__dirname, 'vue-shim.js')
      } : {}
    },
    css: {
      postcss: {
        plugins: []
      }
    }
  }
})
